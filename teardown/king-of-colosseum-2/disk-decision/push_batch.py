#!/usr/bin/env python3
"""KoC2 raw landing — git push pipeline (no-checkout, blob:none clone).

Pushes large binary payloads into western-heart branch muse/koc2-raw WITHOUT
materializing copies on disk:
  - small files: git hash-object -w in place (bulk via --stdin-paths)
  - big files (>PIECE_SIZE): streamed in pieces straight into git objects
    via `git hash-object -w --stdin` (pieces never exist as files)
  - index built with read-tree + update-index --index-info, committed with
    commit-tree, pushed, verified via ls-tree SHA comparison, then loose
    objects are deleted to reclaim disk.

Usage: python3 push_batch.py <batch-spec.json>
Batch spec:
  {
    "name": "B0-m3-small",
    "message": "commit message",
    "max_bytes": 900000000,          # hard cap on input bytes for this batch
    "files": [{"src": "/abs", "dst": "repo/path"}, ...],
    "dirs":  [{"src": "/abs/dir", "dst": "repo/prefix"}, ...],
    "split_files": [{"src": "/abs", "dst_dir": "repo/dir", "dst_name": "Name.iso",
                     "pieces": [0,1,2] | "all",
                     "sha256": "<whole-file sha256, required if manifest>",
                     "manifest": true | false}],
    "manifest_files": [{"dst": "repo/path.json", "content": {...}}]
  }
Outputs: <workdir>/batches/<name>.report.json + appends to ledger.jsonl
"""
import hashlib
import json
import os
import subprocess
import sys
import time

WORKDIR = os.path.expanduser("~/workspace/koc2-disk-decision")
CLONE = os.path.join(WORKDIR, "wh-size-probe")
BRANCH = "muse/koc2-raw"
BASE_BRANCH = "muse/koc2"  # first batch parents onto this; later batches onto BRANCH
PIECE_SIZE = 99_000_000
GIT_ENV = dict(os.environ, GIT_NO_LAZY_FETCH="1",
               GIT_CONFIG_COUNT="1",
               GIT_CONFIG_KEY_0="credential.helper",
               GIT_CONFIG_VALUE_0="store --file /home/hatch/.git-credentials-bannon")


def git(*args, input_data=None, cwd=None):
    r = subprocess.run(["git", "-C", cwd or CLONE, *args],
                       input=input_data, capture_output=True, env=GIT_ENV)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args[:4])} failed: "
                           f"{r.stderr.decode(errors='replace')[:800]}")
    return r.stdout


def git_lines(*args, **kw):
    return git(*args, **kw).decode().splitlines()


def hash_one(path):
    return git("hash-object", "-w", path).decode().strip()


def hash_many(paths):
    """Bulk-hash a list of absolute paths. Returns {path: sha}."""
    inp = ("\n".join(paths) + "\n").encode()
    out = git("hash-object", "-w", "--stdin-paths", input_data=inp).decode().splitlines()
    if len(out) != len(paths):
        raise RuntimeError(f"hash_many: got {len(out)} shas for {len(paths)} files")
    return dict(zip(paths, out))


def hash_pieces(path, wanted):
    """Stream a big file in PIECE_SIZE chunks, hashing each wanted piece.
    Returns {piece_index: (sha, size)}. Chunks not wanted are skipped
    (seek) without hashing."""
    total = os.path.getsize(path)
    npieces = (total + PIECE_SIZE - 1) // PIECE_SIZE
    wanted = set(wanted)
    result = {}
    with open(path, "rb") as f:
        for i in range(npieces):
            size = min(PIECE_SIZE, total - i * PIECE_SIZE)
            if i in wanted:
                data = f.read(size)
                p = subprocess.run(["git", "-C", CLONE, "hash-object", "-w", "--stdin"],
                                   input=data, capture_output=True, env=GIT_ENV)
                if p.returncode != 0:
                    raise RuntimeError(f"hash piece {i} of {path}: "
                                       f"{p.stderr.decode(errors='replace')[:400]}")
                result[i] = (p.stdout.decode().strip(), size)
            else:
                f.seek(size, os.SEEK_CUR)
    return result, total, npieces


def load_base_tree(base):
    """Load the base commit's full tree as {path: (mode, type, sha)}.
    Trees only — no blob access, safe in a blob:none clone."""
    out = git("ls-tree", "-r", "-z", base)
    entries = {}
    for rec in out.split(b"\0"):
        if not rec:
            continue
        meta, path = rec.split(b"\t", 1)
        mode, typ, sha = meta.decode().split()
        entries[path.decode()] = (mode, typ, sha)
    return entries


def build_trees(all_entries):
    """Build the full new tree hierarchy bottom-up with mktree --missing
    (never touches blob contents, so it works in a blob:none clone even
    after previously-pushed blobs were deleted locally).
    all_entries: {full_path: (mode, type, sha)}. Returns root tree sha."""
    # Organize into dirs: dirpath -> {name: (mode, type, sha)} and subdirs
    files = {}   # dirpath -> {name: (mode, type, sha)}
    subdirs = {}  # dirpath -> set(subdir names)
    for path, (mode, typ, sha) in all_entries.items():
        if "/" in path:
            d, name = path.rsplit("/", 1)
        else:
            d, name = "", path
        files.setdefault(d, {})[name] = (mode, typ, sha)
        # register all ancestor dirs
        parts = d.split("/") if d else []
        for i in range(len(parts)):
            parent = "/".join(parts[:i])
            subdirs.setdefault(parent, set()).add(parts[i])

    def mktree_for(d):
        items = []  # (sort_key, mode, type, sha, name)
        for name, (mode, typ, sha) in files.get(d, {}).items():
            items.append((name, mode, typ, sha, name))
        for sub in subdirs.get(d, set()):
            subpath = f"{d}/{sub}" if d else sub
            tsha = mktree_for(subpath)
            items.append((sub + "/", "040000", "tree", tsha, sub))
        items.sort(key=lambda x: x[0])
        inp = "".join(f"{mode} {typ} {sha}\t{name}\n"
                      for _, mode, typ, sha, name in items)
        return git("mktree", "--missing",
                   input_data=inp.encode()).decode().strip()

    return mktree_for("")


def ls_tree(treeish):
    """Non-recursive listing: {name: (mode, type, sha)}. Trees only."""
    out = git("ls-tree", "-z", treeish)
    entries = {}
    for rec in out.split(b"\0"):
        if not rec:
            continue
        meta, name = rec.split(b"\t", 1)
        mode, typ, sha = meta.decode().split()
        entries[name.decode()] = (mode, typ, sha)
    return entries


def build_trees_incremental(base, new_entries):
    """Rebuild ONLY the directories touched by new_entries, reusing the
    existing subtree SHAs everywhere else. new_entries: {path: (mode, type,
    sha)}. Returns the new root tree SHA. Fast even on an 86K-entry tree."""
    changes = {}
    for path, (mode, typ, sha) in new_entries.items():
        d, name = path.rsplit("/", 1) if "/" in path else ("", path)
        changes.setdefault(d, {})[name] = (mode, typ, sha)

    def rebuild(tree_sha, dirpath):
        existing = ls_tree(tree_sha) if tree_sha else {}
        touched_subs = set()
        for chdir in changes:
            if chdir == dirpath:
                continue
            if dirpath == "":
                touched_subs.add(chdir.split("/")[0])
            elif chdir.startswith(dirpath + "/"):
                touched_subs.add(chdir[len(dirpath) + 1:].split("/")[0])
        merged = dict(existing)
        for name, (mode, typ, sha) in changes.get(dirpath, {}).items():
            if name in merged and merged[name][1] == "tree":
                raise RuntimeError(f"path collision: {dirpath}/{name} "
                                   f"is a dir in base, file in batch")
            merged[name] = (mode, typ, sha)
        for sub in touched_subs:
            subpath = f"{dirpath}/{sub}" if dirpath else sub
            old = existing.get(sub)
            if old is not None and old[1] != "tree":
                raise RuntimeError(f"path collision: {subpath} is a "
                                   f"file in base, dir in batch")
            new_sub_sha = rebuild(old[2] if old else None, subpath)
            merged[sub] = ("040000", "tree", new_sub_sha)
        items = []
        for name, (mode, typ, sha) in merged.items():
            key = name + "/" if typ == "tree" else name
            items.append((key, mode, typ, sha, name))
        items.sort(key=lambda x: x[0])
        inp = "".join(f"{mode} {typ} {sha}\t{name}\n"
                      for _, mode, typ, sha, name in items)
        return git("mktree", "--missing",
                   input_data=inp.encode()).decode().strip()

    base_tree = git("rev-parse", f"{base}^{{tree}}").decode().strip()
    return rebuild(base_tree, "")


def main():
    spec_path = sys.argv[1]
    spec = json.load(open(spec_path))
    name = spec["name"]
    t0 = time.time()
    report = {"name": name, "entries": [], "started": t0}

    # --- size budget check (before touching disk) ---
    total_in = 0
    for f in spec.get("files", []):
        total_in += os.path.getsize(f["src"])
    for d in spec.get("dirs", []):
        dps = []
        for root, _, files in os.walk(d["src"]):
            for fn in files:
                p = os.path.join(root, fn)
                if os.path.getsize(p) <= PIECE_SIZE:
                    dps.append(p)
        if "shard" in d:
            i, n = d["shard"]
            dps = sorted(dps)
            chunk = (len(dps) + n - 1) // n
            dps = dps[i * chunk:(i + 1) * chunk]
        for p in dps:
            total_in += os.path.getsize(p)
    for s in spec.get("split_files", []):
        sz = os.path.getsize(s["src"])
        if s.get("pieces") == "all":
            total_in += sz
        else:
            total_in += sum(min(PIECE_SIZE, sz - i * PIECE_SIZE)
                            for i in s["pieces"])
    report["input_bytes"] = total_in
    if total_in > spec.get("max_bytes", 900_000_000):
        print(f"REFUSED: batch input {total_in} exceeds cap "
              f"{spec.get('max_bytes')}", file=sys.stderr)
        sys.exit(2)

    # --- resolve base commit ---
    try:
        git("fetch", "origin", BRANCH, "--no-tags")
    except RuntimeError:
        pass  # branch may not exist yet (first batch)
    try:
        base = git("rev-parse", f"origin/{BRANCH}").decode().strip()
    except RuntimeError:
        base = git("rev-parse", f"origin/{BASE_BRANCH}").decode().strip()
    report["base"] = base
    print(f"[{name}] base={base[:10]} input={total_in/1e6:.1f} MB")

    new_entries = {}  # repo_path -> (mode, type, sha)
    created_blobs = []  # shas to delete after push

    # --- plain files ---
    for f in spec.get("files", []):
        sha = hash_one(f["src"])
        new_entries[f["dst"]] = ("100644", "blob", sha)
        created_blobs.append(sha)
        report["entries"].append({"dst": f["dst"], "sha": sha,
                                  "size": os.path.getsize(f["src"])})

    # --- whole dirs (bulk) ---
    for d in spec.get("dirs", []):
        paths = []
        for root, _, files in os.walk(d["src"]):
            for fn in sorted(files):
                p = os.path.join(root, fn)
                if os.path.getsize(p) > PIECE_SIZE:
                    # oversized: must be a split_file entry, never hashed whole
                    print(f"[{name}] SKIP oversized in dir: {p}")
                    continue
                paths.append(p)
        if "shard" in d:
            i, n = d["shard"]
            paths = sorted(paths)
            chunk = (len(paths) + n - 1) // n
            paths = paths[i * chunk:(i + 1) * chunk]
            print(f"[{name}] dir shard {i}/{n}: {len(paths)} files")
        mapping = hash_many(paths)
        for p in paths:
            rel = os.path.relpath(p, d["src"])
            dst = f"{d['dst']}/{rel}"
            sha = mapping[p]
            new_entries[dst] = ("100644", "blob", sha)
            created_blobs.append(sha)
            report["entries"].append({"dst": dst, "sha": sha,
                                      "size": os.path.getsize(p)})
        print(f"[{name}] dir {d['src']}: {len(paths)} files hashed")

    # --- split files ---
    for s in spec.get("split_files", []):
        sz = os.path.getsize(s["src"])
        npieces = (sz + PIECE_SIZE - 1) // PIECE_SIZE
        wanted = list(range(npieces)) if s.get("pieces") == "all" else s["pieces"]
        pieces, total, _ = hash_pieces(s["src"], wanted)
        for i in sorted(pieces):
            sha, psize = pieces[i]
            dst = f"{s['dst_dir']}/{s['dst_name']}.part{i:03d}"
            new_entries[dst] = ("100644", "blob", sha)
            created_blobs.append(sha)
            report["entries"].append({"dst": dst, "sha": sha, "size": psize,
                                      "split_of": s["dst_name"], "piece": i})
        print(f"[{name}] split {s['dst_name']}: pieces {wanted} "
              f"of {npieces} hashed")
        if s.get("manifest"):
            manifest = {
                "original": s.get("original_name", s["dst_name"]),
                "size": total,
                "sha256": s["sha256"],
                "piece_size": PIECE_SIZE,
                "piece_count": npieces,
                "pieces": [f"{s['dst_name']}.part{i:03d}" for i in range(npieces)],
                "reassemble": f"cat {s['dst_name']}.part* > {s['dst_name']}",
            }
            blob = subprocess.run(
                ["git", "-C", CLONE, "hash-object", "-w", "--stdin"],
                input=json.dumps(manifest, indent=1).encode(),
                capture_output=True, env=GIT_ENV)
            msha = blob.stdout.decode().strip()
            mdst = f"{s['dst_dir']}/{s['dst_name']}.manifest.json"
            new_entries[mdst] = ("100644", "blob", msha)
            created_blobs.append(msha)
            report["entries"].append({"dst": mdst, "sha": msha,
                                      "size": len(json.dumps(manifest))})

    # --- inline manifest/text files ---
    for m in spec.get("manifest_files", []):
        content = m["content"]
        if not isinstance(content, str):
            content = json.dumps(content, indent=1)
        blob = subprocess.run(
            ["git", "-C", CLONE, "hash-object", "-w", "--stdin"],
            input=content.encode(), capture_output=True, env=GIT_ENV)
        sha = blob.stdout.decode().strip()
        new_entries[m["dst"]] = ("100644", "blob", sha)
        created_blobs.append(sha)
        report["entries"].append({"dst": m["dst"], "sha": sha,
                                  "size": len(content)})

    # --- commit (incremental mktree: no index, no blob reads) ---
    tree = build_trees_incremental(base, new_entries)
    commit = git("commit-tree", tree, "-p", base, "-m",
                 spec["message"]).decode().strip()
    report["commit"] = commit
    report["tree"] = tree
    print(f"[{name}] commit={commit[:10]} entries={len(new_entries)}")

    # --- push with retries ---
    pushed = False
    for attempt in range(1, 4):
        r = subprocess.run(["git", "-C", CLONE, "push", "origin",
                            f"{commit}:refs/heads/{BRANCH}"],
                           capture_output=True, env=GIT_ENV)
        if r.returncode == 0:
            pushed = True
            print(f"[{name}] push OK (attempt {attempt})")
            break
        print(f"[{name}] push attempt {attempt} failed: "
              f"{r.stderr.decode(errors='replace')[:500]}")
        time.sleep(20 * attempt)
    if not pushed:
        report["push"] = "FAILED"
        save_report(name, report)
        sys.exit(3)

    # --- verify via fresh fetch + ls-tree SHA comparison ---
    git("fetch", "origin", BRANCH, "--no-tags")
    remote = {}
    for line in git_lines("ls-tree", "-r", f"origin/{BRANCH}", "--",
                          "raw/", "teardown/king-of-colosseum-2/tools/",
                          "teardown/king-of-colosseum-2/work/"):
        # "<mode> blob <sha>\t<path>"
        meta, path = line.split("\t", 1)
        remote[path] = meta.split()[2]
    missing, wrong = [], []
    for e in report["entries"]:
        if e["dst"] not in remote:
            missing.append(e["dst"])
        elif remote[e["dst"]] != e["sha"]:
            wrong.append(e["dst"])
    report["verify"] = {"checked": len(report["entries"]),
                        "missing": missing, "wrong_sha": wrong}
    if missing or wrong:
        print(f"[{name}] VERIFY FAILED missing={len(missing)} "
              f"wrong={len(wrong)}", file=sys.stderr)
        save_report(name, report)
        sys.exit(4)
    print(f"[{name}] verified {len(report['entries'])} blobs on origin")

    # --- reclaim disk: delete the loose objects we just pushed ---
    freed = 0
    for sha in set(created_blobs):
        p = os.path.join(CLONE, ".git", "objects", sha[:2], sha[2:])
        if os.path.exists(p):
            freed += os.path.getsize(p)
            os.remove(p)
    report["objects_deleted_bytes"] = freed
    report["elapsed_s"] = round(time.time() - t0, 1)
    save_report(name, report)
    print(f"[{name}] done in {report['elapsed_s']}s, "
          f"reclaimed {freed/1e6:.1f} MB of loose objects")


def save_report(name, report):
    d = os.path.join(WORKDIR, "batches")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f"{name}.report.json"), "w") as f:
        json.dump(report, f, indent=1)
    with open(os.path.join(WORKDIR, "ledger.jsonl"), "a") as f:
        f.write(json.dumps({"name": name, "commit": report.get("commit"),
                            "entries": len(report["entries"]),
                            "input_bytes": report.get("input_bytes"),
                            "verify": report.get("verify")}) + "\n")


if __name__ == "__main__":
    main()

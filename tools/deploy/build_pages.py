#!/usr/bin/env python3
"""tools/deploy/build_pages.py — build the GitHub Pages site (gh-pages) from a committed ref.

Owner 2026-10-22: "Make sure the version at the url is updating with all this ... the one I'm playing"
(https://mhvnsnt.github.io/western-heart/). Same deploy method as the earlier gh-pages deploys
(main's full game/ tree + every repo file the runtime references), made repeatable:

  * reads files from a COMMITTED git ref (default origin/main) — never from the working tree;
  * roots: game/**, customization/creation-suite-ui/**, packages/creation-suite/{src,ui,ui2}/**;
  * reference closure: every quoted path in those js/mjs/html/css/json files (and, recursively, in
    any text file it pulls in) that resolves to a file in the ref — tried relative to the file, to
    each page base (game/, customization/creation-suite-ui/, packages/creation-suite/ui2/) and to
    the repo root — with a runtime file extension; docs/proof/, teardown/ and tools/ are skipped;
  * writes the files into OUT (a gh-pages checkout) and NEVER deletes anything there;
  * prints the file list, sizes and a manifest (OUT/deploy-manifest.json).

    python3 tools/deploy/build_pages.py --ref origin/main --out /path/to/gh-pages-checkout
Then in OUT: git add <the listed files> && git commit && git push (fast-forward, no force).

Plumbing mode (EXPERIMENTAL, not yet used for a real deploy; no checkout, no large downloads):
    python3 tools/deploy/build_pages.py --ref origin/main --onto origin/gh-pages [--push]
builds the new gh-pages commit straight from git objects: the current gh-pages tree, plus every
closure file pointed at the SAME blob it has on the source ref (git update-index --cacheinfo), plus
deploy-manifest.json. Entries are only added or updated, never removed. The model blobs already
exist on GitHub (they are main's), so a push sends trees + one commit; in a blob:none partial
clone only the text files the closure scan reads are fetched.
"""
import argparse
import json
import os
import posixpath
import re
import subprocess
import sys

ROOTS = ("game/", "customization/creation-suite-ui/", "packages/creation-suite/src/",
         "packages/creation-suite/ui/", "packages/creation-suite/ui2/",
         # fetched by path built at runtime (game/js/customization-consumer.js:191
         # `customization/profiles/${fighter.char.id}.json`) — no literal to follow
         "customization/profiles/")
BASES = ("game/", "customization/creation-suite-ui/", "packages/creation-suite/ui2/", "")
TEXT = (".js", ".mjs", ".html", ".css", ".json")
RUNTIME = TEXT + (".glb", ".gltf", ".bin", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".ktx2",
                  ".obj", ".mtl", ".mp3", ".ogg", ".wav", ".m4a", ".mp4", ".webm", ".ttf", ".otf",
                  ".woff", ".woff2", ".txt", ".csv", ".tga", ".dds")
SKIP = ("docs/proof/", "teardown/", "tools/", ".github/", "node_modules/")
# Deployed, but their references are not followed by default: the suite's roster-attires.json lists
# every attire model in roster/ (2.0 GB, 2026-10-22) — following it would put the site at 3.7 GB
# (GitHub Pages' documented limit is 1 GB; the live site already runs at 2.3 GB). --follow-all
# overrides; a follow-up deploy can add those models once the main deploy is confirmed live.
NO_FOLLOW = ("customization/creation-suite-ui/data/roster-attires.json",)
STR = re.compile(r"""["'`]([^"'`\s<>{}$|*?]+\.[A-Za-z0-9]{2,5})(?:[?#][^"'`\s]*)?["'`]""")


def git(*args, binary=False):
    r = subprocess.run(["git", *args], capture_output=True)
    if r.returncode:
        sys.exit(r.stderr.decode()[:2000])
    return r.stdout if binary else r.stdout.decode()


def tree_sizes(sha):
    """{path: size} for every blob in `sha`, WITHOUT lazily fetching blobs.

    In a --filter=blob:none clone, `git ls-tree -l` downloads every missing
    blob one request at a time (the whole 5+ GB repo, >25 min). Instead:
    batch-fetch only the text blobs the closure scan reads (one request per
    500), and read the other sizes from the local object store; blobs that
    aren't local report size 0 (only used for the printed totals)."""
    oid = {}
    for line in git("ls-tree", "-r", sha).splitlines():
        meta, path = line.split("\t", 1)
        parts = meta.split()
        if parts[1] == "blob":
            oid[path] = parts[2]
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1")

    def check(oids):
        r = subprocess.run(["git", "cat-file", "--batch-check"], input="\n".join(oids) + "\n",
                           capture_output=True, text=True, env=env)
        out = {}
        for l in r.stdout.splitlines():
            f = l.split()
            out[f[0]] = int(f[2]) if len(f) == 3 and f[1] == "blob" else None
        return out

    text = sorted({o for p, o in oid.items() if p.endswith(TEXT)})
    missing = [o for o, n in check(text).items() if n is None]
    for i in range(0, len(missing), 500):
        subprocess.run(["git", "-c", "fetch.negotiationAlgorithm=noop", "fetch", "-q", "--no-tags",
                        "--no-write-fetch-head", "--filter=blob:none", "origin", *missing[i:i + 500]])
    got = check(sorted(set(oid.values())))
    unknown = sum(1 for n in got.values() if n is None)
    if unknown:
        print(f"note: {unknown} blobs not fetched locally; their sizes count as 0 in totals")
    return {p: (got.get(o) or 0) for p, o in oid.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--out", default=None)
    ap.add_argument("--onto", default=None, help="plumbing mode: parent gh-pages ref (e.g. origin/gh-pages)")
    ap.add_argument("--branch", default="gh-pages")
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--follow-all", action="store_true")
    ap.add_argument("--cook", action="store_true",
                    help="plumbing mode: also add cooked <x>.web.glb sidecars + cooked-manifest.json "
                         "(tools/deploy/cook_assets.py; docs/tech/ASSET-PIPELINE-2026.md). Originals stay.")
    ap.add_argument("--cook-mirror", default="https://mhvnsnt.github.io/western-heart/",
                    help="where to download original GLBs from in parallel (each verified against its git blob "
                         "SHA; falls back to git cat-file)")
    a = ap.parse_args()
    sha = git("rev-parse", a.ref).strip()
    sizes = tree_sizes(sha)
    files = set(p for p in sizes if p.startswith(ROOTS))
    queue = [p for p in files if p.endswith(TEXT)]
    seen_text = set(queue)
    while queue:
        p = queue.pop()
        if p in NO_FOLLOW and not a.follow_all:
            continue
        try:
            txt = git("cat-file", "-p", f"{sha}:{p}")
        except SystemExit:
            continue
        here = posixpath.dirname(p)
        for m in STR.finditer(txt):
            ref = m.group(1)
            if "://" in ref or ref.startswith("//") or not ref.lower().endswith(RUNTIME):
                continue
            for base in (here,) + BASES:
                cand = posixpath.normpath(posixpath.join(base, ref.lstrip("/") if ref.startswith("/") else ref))
                if cand in sizes and not cand.startswith(SKIP):
                    if cand not in files:
                        files.add(cand)
                        if cand.endswith(TEXT) and cand not in seen_text:
                            seen_text.add(cand)
                            queue.append(cand)
                    break
    files = sorted(files)
    total = sum(sizes[f] for f in files)
    by_top = {}
    for f in files:
        top = f.split("/", 1)[0]
        by_top[top] = by_top.get(top, 0) + sizes[f]
    print(f"ref {a.ref} = {sha}: {len(files)} files, {total/1e6:.1f} MB")
    for t, s in sorted(by_top.items(), key=lambda x: -x[1]):
        print(f"  {t:16s} {s/1e6:9.1f} MB")
    big = [f for f in files if sizes[f] > 95e6]
    if big:
        print("over 95 MB (GitHub per-file limit is 100 MB):", big)
    if a.dry_run:
        return
    if a.onto:
        return plumbing(a, sha, files, sizes, total)
    for f in files:
        dst = os.path.join(a.out, f)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        data = git("cat-file", "blob", f"{sha}:{f}", binary=True)
        if os.path.exists(dst):
            with open(dst, "rb") as fh:
                if fh.read() == data:
                    continue
        with open(dst, "wb") as fh:
            fh.write(data)
    man = {"format": "wh-pages-deploy/1", "ref": a.ref, "commit": sha, "files": len(files),
           "bytes": total, "tool": "tools/deploy/build_pages.py"}
    with open(os.path.join(a.out, "deploy-manifest.json"), "w") as fh:
        json.dump(man, fh, indent=1)
    with open(os.path.join(a.out, ".deploy-files.txt"), "w") as fh:
        fh.write("\n".join(files) + "\n")
    print("written; file list:", os.path.join(a.out, ".deploy-files.txt"))


def cook_into_index(a, sha, files, blob, g):
    """Add cooked sidecars to the temp index. Returns the cooked-manifest blob id."""
    import hashlib
    import urllib.request
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import cook_assets
    src_dir = os.path.join(os.path.expanduser("~/.cache/wh-cook"), "src")
    os.makedirs(src_dir, exist_ok=True)

    def read(path, obj):
        p = os.path.join(src_dir, obj)
        if os.path.exists(p):
            return open(p, "rb").read()
        data = None
        try:
            with urllib.request.urlopen(a.cook_mirror + urllib.request.quote(path), timeout=300) as r:
                data = r.read()
            if cook_assets.git_blob_sha(data) != obj:
                data = None  # mirror is older/newer than the ref
        except Exception:
            data = None
        if data is None:
            data = git("cat-file", "blob", obj, binary=True)
        open(p, "wb").write(data)
        return data

    items = [(f, blob[f][1]) for f in files if f.lower().endswith(".glb") and not f.endswith(".web.glb")]
    print(f"cooking {len(items)} GLBs")
    entries, outputs = cook_assets.cook_all(items, read, jobs=int(os.environ.get("WH_COOK_JOBS", "4")))
    lines = []
    for cp, data in outputs.items():
        obj = g("hash-object", "-w", "--stdin", inp=data).strip()
        lines.append(f"100644 {obj}\t{cp}")
    cm = cook_assets.manifest(entries, sha)
    mobj = g("hash-object", "-w", "--stdin", inp=json.dumps(cm, indent=1).encode()).strip()
    lines.append(f"100644 {mobj}\tcooked-manifest.json")
    g("update-index", "--add", "--index-info", inp=("\n".join(lines) + "\n").encode())
    print(f"cooked {cm['cooked_models']}/{cm['models']} models: {cm['bytes_original']/1e6:.0f} MB -> "
          f"{cm['bytes_served']/1e6:.0f} MB served")
    return mobj[:12]


def plumbing(a, sha, files, sizes, total):
    import tempfile
    blob = {}
    for line in git("ls-tree", "-r", sha, "--", *sorted({f.split("/", 1)[0] for f in files})).splitlines():
        meta, path = line.split("\t", 1)
        mode, kind, obj = meta.split()
        if kind == "blob":
            blob[path] = (mode, obj)
    parent = git("rev-parse", a.onto).strip()
    idx = tempfile.mktemp(prefix="wh-pages-index-")
    env = dict(os.environ, GIT_INDEX_FILE=idx)
    def g(*args, inp=None):
        r = subprocess.run(["git", *args], capture_output=True, env=env, input=inp)
        if r.returncode:
            sys.exit(r.stderr.decode()[:2000])
        return r.stdout.decode()
    g("read-tree", parent)
    before = {l.split("\t", 1)[1]: l.split()[1] for l in g("ls-files", "-s").splitlines()}
    lines, changed = [], 0
    for f in files:
        mode, obj = blob[f]
        if before.get(f) != obj:
            changed += 1
        lines.append(f"{mode} {obj}\t{f}")
    g("update-index", "--index-info", inp=("\n".join(lines) + "\n").encode())
    man_d = {"format": "wh-pages-deploy/1", "ref": a.ref, "commit": sha, "files": len(files),
             "bytes": total, "tool": "tools/deploy/build_pages.py"}
    if a.cook:
        man_d["cooked"] = cook_into_index(a, sha, files, blob, g)
    man = json.dumps(man_d, indent=1).encode()
    mobj = g("hash-object", "-w", "--stdin", inp=man).strip()
    g("update-index", "--add", "--cacheinfo", f"100644,{mobj},deploy-manifest.json")
    after = set(l.split("\t", 1)[1] for l in g("ls-files", "-s").splitlines())
    missing = set(before) - after
    if missing:
        sys.exit(f"refusing: {len(missing)} entries would be removed")
    tree = g("write-tree").strip()
    if tree == git("rev-parse", parent + "^{tree}").strip():
        print("gh-pages already matches", a.ref, "- nothing to deploy")
        os.remove(idx)
        return
    msg = (f"Deploy: western-heart from {a.ref} @ {sha[:9]} (tools/deploy/build_pages.py)\n\n"
           f"{changed} files added or updated ({len(files)} in the deploy set, {total/1e6:.0f} MB); "
           f"0 removed.\n")
    commit = g("-c", "user.name=wh-deploy", "-c", "user.email=noreply@github.com",
               "commit-tree", tree, "-p", parent, inp=msg.encode()).strip()
    os.remove(idx)
    print("new", a.branch, "commit", commit, f"({changed} files changed vs {a.onto})")
    if a.push:
        r = subprocess.run(["git", "push", "origin", f"{commit}:refs/heads/{a.branch}"], capture_output=True, text=True)
        print(r.stdout, r.stderr)
        if r.returncode:
            sys.exit("push failed")


if __name__ == "__main__":
    main()

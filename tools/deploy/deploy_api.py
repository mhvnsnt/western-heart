#!/usr/bin/env python3
"""deploy_api.py — deploy the Pages shell via the GitHub Git Data API.

No local git, no clone, no home writes: everything runs through `gh api`
and a scratch dir (default: a fresh dir under the system temp area).
This is the scripted form of REPUBLISH.md section 2 — the same route that
shipped live 32607e2b -> main 847a0aa4 on 2026-11-08 (deploy commit
60a0c5f8, manifest 847a0aa4, verified live). It replicates
tools/deploy/deploy_delta.py exactly (same ROOTS, same T7/small add rules,
same 1 GiB CAP), then adds the module-graph check the delta tool runs on
the assembled tree.

Usage:
    python3 tools/deploy/deploy_api.py [--main <sha>] [--live-tip <sha>]
        [--branch gh-pages-m1-20261029] [--scratch DIR] [--push]

Without --push this is a dry run: it computes the delta, materializes the
assembled tree's code files, runs the module-graph check, creates the
manifest blob, tree and commit — and stops before patching the ref
(the commit is left dangling). With --push it re-checks the live tip and
PATCHes the branch ref with force:false; a 422 means another lane
deployed first — stop, recompute, never force.

Deploys are add/update-only. Nothing is ever removed from the deploy
branch, and it is never force-pushed.
"""
import argparse
import base64
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile

REPO = "mhvnsnt/western-heart"
BRANCH = "gh-pages-m1-20261029"
ROOTS = ("game", "customization", "packages", "roster")
ROOT_PREFIXES = tuple(r + "/" for r in ROOTS)
SMALL_ADD_PREFIXES = ("customization/creation-suite-ui/", "customization/templates/",
                      "game/js/", "game/data/", "game/css/")
SMALL_EXT = (".js", ".mjs", ".json", ".css", ".html")
SMALL_MAX, SMALL_TOTAL = 256 * 1024, 2_500_000
CAP = 1_073_741_824
CODE_EXT = (".js", ".mjs", ".html", ".json", ".css")


def gh(*args, inp=None):
    r = subprocess.run(["gh", "api"] + list(args),
                       input=inp, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"gh api {' '.join(args)} failed:\n{r.stderr.strip()[:500]}")
    return r.stdout


def gh_json(*args, inp=None):
    return json.loads(gh(*args, inp=inp))


def fetch_tree(ref, root):
    """Recursive tree for one root (game, customization, packages, roster,
    assets) at a ref; returns {path: (sha, size, mode)} with root prefix."""
    d = gh_json(f"repos/{REPO}/git/trees/{ref}:{root}?recursive=1")
    assert not d.get("truncated"), f"tree {ref}:{root} truncated"
    return {f"{root}/{e['path']}": (e["sha"], e.get("size", 0) or 0, e["mode"])
            for e in d["tree"] if e["type"] == "blob"}


def fetch_blob_text(sha):
    r = gh_json(f"repos/{REPO}/git/blobs/{sha}")
    return base64.b64decode("".join(r["content"].split())).decode("utf-8", "replace")


def compute_delta(live, main, t3anims):
    """Same rules as tools/deploy/deploy_delta.py. Returns (upd, add, gone)."""
    upd = sorted(p for p in live if p in main and p.startswith(ROOT_PREFIXES)
                 and live[p][0] != main[p][0])
    blk = re.search(r"export const T7_STANCES = \{(.*?)\n\};", t3anims, re.S)
    dirs = sorted(set(re.findall(r"dir:\s*'(assets/anim/t7/[\w-]+/)'",
                                 blk.group(1)))) if blk else []
    want = ["game/" + d + f for d in dirs for f in ("skeleton.json", "stance.json")]
    mblk = re.search(r"export const T7_MOVES = \{(.*?)\n\};", t3anims, re.S)
    mdirs = sorted(set(re.findall(r"dir:\s*'(assets/anim/t7/[\w-]+/)'",
                                  mblk.group(1)))) if mblk else []
    want += ["game/" + d + "skeleton.json" for d in mdirs]
    add = sorted(p for p in want if p in main and p not in live)
    # Own-slot T7 generic banks (t3anims.js 'assets/anim/t3/t7_*/'): t3anims loads banks with a plain
    # local fetch (no remote fallback), so the shell must carry them or own-slot fighters lose their
    # bank on Pages (2026-11-10: 13 banks, 256 files, 10.1 MB, shipped in deploy 0969a76e).
    bdirs = sorted(set(re.findall(r"'(assets/anim/t3/t7_[\w-]+/)'", t3anims)))
    add += sorted(p for p in main for d in bdirs if p.startswith("game/" + d) and p not in live)
    budget = SMALL_TOTAL
    for p in sorted(p for p in main if p not in live
                    and p.startswith(SMALL_ADD_PREFIXES)
                    and p.endswith(SMALL_EXT) and "/tests/" not in p
                    and "/proof" not in p and main[p][1] <= SMALL_MAX):
        if main[p][1] <= budget and p not in add:
            add.append(p)
            budget -= main[p][1]
    add = sorted(set(add))
    gone = sorted(p for p in live if p not in main)
    return upd, add, gone


def materialize(assembled, checker, scratch):
    """Fetch every CODE file of the assembled tree via the blobs API
    (skipping files already on disk at the right size), then run the
    module-graph check against the materialized dir.
    Returns the checker's CompletedProcess (caller reads its stdout)."""
    code = sorted(p for p, (_, sz, _) in assembled.items()
                  if p.endswith(CODE_EXT))
    print(f"assembled code files: {len(code)}")
    adir = os.path.join(scratch, "assembled")
    ok, skipped, fail = 0, 0, []
    for i, p in enumerate(code):
        sha, sz, _ = assembled[p]
        dst = os.path.join(adir, p)
        if os.path.exists(dst) and os.path.getsize(dst) == sz:
            skipped += 1
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        r = subprocess.run(["gh", "api", f"repos/{REPO}/git/blobs/{sha}",
                            "--jq", ".content"], capture_output=True, text=True)
        if r.returncode or not r.stdout.strip():
            fail.append(p)
            continue
        try:
            data = base64.b64decode("".join(r.stdout.split()))
        except Exception as e:
            fail.append(f"{p} (b64: {e})")
            continue
        with open(dst, "wb") as f:
            f.write(data)
        ok += 1
        if (i + 1) % 200 == 0:
            print(f"  {i + 1}/{len(code)} fetched...")
    print(f"materialized: fetched {ok}, skipped {skipped}, failed {len(fail)}")
    if fail:
        raise SystemExit(f"FAILED to fetch blobs: {fail[:10]}")
    r = subprocess.run([sys.executable, checker, adir],
                       capture_output=True, text=True)
    print(r.stdout.strip())
    return r  # caller parses MISSING MODULE lines from r.stdout


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--main", help="main commit SHA (default: current main tip)")
    ap.add_argument("--live-tip", help="deploy branch tip SHA (default: current tip)")
    ap.add_argument("--branch", default=BRANCH)
    ap.add_argument("--scratch", help="scratch dir (default: fresh tmp dir)")
    ap.add_argument("--push", action="store_true",
                    help="actually PATCH the branch ref (default: dry run)")
    args = ap.parse_args()

    main_sha = args.main or gh_json(
        f"repos/{REPO}/git/refs/heads/main")["object"]["sha"]
    live_tip = args.live_tip or gh_json(
        f"repos/{REPO}/git/refs/heads/{args.branch}")["object"]["sha"]
    print(f"main: {main_sha[:8]}  live tip: {live_tip[:8]}  branch: {args.branch}")
    scratch = args.scratch or tempfile.mkdtemp(prefix="deploy-api-")
    os.makedirs(scratch, exist_ok=True)
    print(f"scratch: {scratch}")

    # 1. Trees.
    live, main = {}, {}
    for root in ROOTS:
        live.update(fetch_tree(live_tip, root))
        main.update(fetch_tree(main_sha, root))
    live_assets = fetch_tree(live_tip, "assets")
    top = gh_json(f"repos/{REPO}/git/trees/{live_tip}")["tree"]
    root_blobs = {e["path"]: (e["sha"], e.get("size", 0) or 0, e["mode"])
                  for e in top if e["type"] == "blob"}
    live_total = (sum(v[1] for v in live.values())
                  + sum(v[1] for v in live_assets.values())
                  + sum(v[1] for v in root_blobs.values()))
    print(f"live blobs in ROOTS: {len(live)}  live total bytes: {live_total}")

    # 2. Delta (deploy_delta.py rules).
    t3anims = fetch_blob_text(main["game/js/t3anims.js"][0])
    upd, add, gone = compute_delta(live, main, t3anims)
    new_total = (live_total - sum(live[p][1] for p in upd)
                 + sum(main[p][1] for p in upd) + sum(main[p][1] for p in add))
    print(f"updated: {len(upd)}  added: {len(add)}  "
          f"on-live-gone-from-main: {len(gone)} (stays — add/update-only)")
    for p in gone[:20]:
        print(f"  GONE-FROM-MAIN (stays on live): {p}")
    print(f"new total w/o manifest change: {new_total}  cap: {CAP}  "
          f"headroom: {CAP - new_total}")
    if new_total > CAP:
        raise SystemExit("REFUSING: new tree over the 1 GiB cap")
    json.dump({"upd": upd, "add": add, "gone": gone, "live_total": live_total,
               "new_total_wo_manifest": new_total},
              open(os.path.join(scratch, "delta.json"), "w"), indent=1)

    # 3. Module-graph check on the assembled tree.
    assembled = dict(live)
    for p in upd + add:
        assembled[p] = main[p]
    # Root index.html only (the checker starts at game/index.html; the live
    # deploy-manifest.json is not code the graph reads).
    if "index.html" in root_blobs:
        assembled["index.html"] = root_blobs["index.html"]
    assembled["game/index.html"] = main["game/index.html"]
    # The module-graph checker lives under tools/ (outside the deploy
    # ROOTS), so fetch it from main via the contents API.
    checker = os.path.join(scratch, "check_module_graph.py")
    if not os.path.exists(checker):
        c = gh_json(f"repos/{REPO}/contents/tools/deploy/check_module_graph.py"
                    f"?ref={main_sha}")
        with open(checker, "w") as f:
            f.write(base64.b64decode("".join(c["content"].split())).decode())
    for _attempt in range(3):
        check = materialize(assembled, checker, scratch)
        if check.returncode == 0:
            break
        # Missing static-module targets that exist on main get added,
        # then re-check; anything else is a hard refuse.
        missing = re.findall(r"MISSING MODULE \(static\): .* -> (\S+)",
                             check.stdout)
        addable = [m for m in missing if m in main and m not in assembled]
        if not addable:
            raise SystemExit("module-graph check FAILED (hard missing) — "
                             f"refusing; missing: {missing[:10]}")
        print(f"adding missing modules from main: {addable}")
        for p in addable:
            assembled[p] = main[p]
            add.append(p)
    else:
        raise SystemExit("module-graph check did not pass after 3 attempts")

    # 4. Manifest blob.
    man = json.loads(fetch_blob_text(root_blobs["deploy-manifest.json"][0]))
    man_bytes_old = root_blobs["deploy-manifest.json"][1]
    man.update({
        "commit": main_sha,
        "files": man["files"] + len(add),
        "bytes": 0,
        "built": datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "tool": "tools/deploy/deploy_api.py (Git Data API route, REPUBLISH.md section 2)",
        "delta_note": (f"Delta deploy (API route, REPUBLISH.md section 2 logic) "
                       f"live {live_tip[:8]} -> main {main_sha[:8]}: "
                       f"{len(upd)} updated, {len(add)} added, 0 removed; "
                       f"module graph checked."),
    })
    for _ in range(3):
        body = json.dumps(man, indent=1) + "\n"
        man["bytes"] = new_total - man_bytes_old + len(body.encode())
        if len((json.dumps(man, indent=1) + "\n").encode()) == len(body.encode()):
            break
    body = json.dumps(man, indent=1) + "\n"
    print(f"manifest: files={man['files']} bytes={man['bytes']} "
          f"built={man['built']}")
    assert man["bytes"] <= CAP, "manifest total over cap"
    blob = gh_json("repos/" + REPO + "/git/blobs", "--method", "POST",
                   "-f", f"content={base64.b64encode(body.encode()).decode()}",
                   "-f", "encoding=base64")
    man_sha = blob["sha"]
    print(f"manifest blob: {man_sha}")

    # 5. Tree (base_tree = live tip) + verification before any ref change.
    changed = sorted(set(upd) | set(add))
    entries = [{"path": p, "mode": main[p][2], "type": "blob", "sha": main[p][0]}
               for p in changed]
    entries.append({"path": "deploy-manifest.json", "mode": "100644",
                    "type": "blob", "sha": man_sha})
    payload = json.dumps({"base_tree": live_tip, "tree": entries})
    tree = gh_json(f"repos/{REPO}/git/trees", "--method", "POST",
                   "--input", "-", inp=payload)
    new_tree_sha = tree["sha"]
    print(f"new tree: {new_tree_sha}")
    total = 0
    for root in list(ROOTS) + ["assets"]:
        d = gh_json(f"repos/{REPO}/git/trees/{new_tree_sha}:{root}?recursive=1")
        assert not d.get("truncated")
        total += sum(e.get("size", 0) or 0 for e in d["tree"] if e["type"] == "blob")
    top_new = gh_json(f"repos/{REPO}/git/trees/{new_tree_sha}")["tree"]
    total += sum(e.get("size", 0) or 0 for e in top_new if e["type"] == "blob")
    print(f"verified new tree total: {total} (manifest claimed {man['bytes']})")
    assert total == man["bytes"], "total mismatch"
    assert total <= CAP, "new tree over cap"
    new_paths = set()
    for root in ROOTS:
        d = gh_json(f"repos/{REPO}/git/trees/{new_tree_sha}:{root}?recursive=1")
        new_paths |= {f"{root}/{e['path']}" for e in d["tree"] if e["type"] == "blob"}
    removed = sorted(set(live) - new_paths)
    print(f"removed: {len(removed)}")
    assert not removed, f"refusing: would remove {removed[:10]}"

    # 6. Commit.
    msg = (f"Pages shell deploy: main {main_sha[:8]} - {len(upd)} updated, "
           f"{len(add)} added, 0 removed\n\n{man['delta_note']}\n"
           f"Module graph checked (tools/deploy/check_module_graph.py on the "
           f"assembled tree). Fast-forward only.\n")
    payload = json.dumps({"message": msg, "tree": new_tree_sha,
                          "parents": [live_tip]})
    commit = gh_json(f"repos/{REPO}/git/commits", "--method", "POST",
                     "--input", "-", inp=payload)
    print(f"new commit: {commit['sha']}")
    if not args.push:
        print("dry run: commit created (dangling), ref NOT patched. "
              "Re-run with --push.")
        return 0

    # 7. Patch the ref (fast-forward only).
    tip = gh_json(f"repos/{REPO}/git/refs/heads/{args.branch}")
    print(f"live tip before patch: {tip['object']['sha'][:8]}")
    assert tip["object"]["sha"] == live_tip, "live tip moved — stop, recompute"
    payload = json.dumps({"sha": commit["sha"], "force": False})
    gh(f"repos/{REPO}/git/refs/heads/{args.branch}", "--method", "PATCH",
       "--input", "-", inp=payload)
    print(f"PATCHED ref {args.branch} -> {commit['sha'][:8]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

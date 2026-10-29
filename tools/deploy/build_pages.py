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

Shell-only mode (owner decision 2026-10-26, "Split it: Pages shell + GLBs on R2"):
GitHub Pages caps a published site at 1 GB; the full deploy set is ~5,969 MB, so the full
set can never ship on Pages. --shell-only deploys the playable shell only — all code/UI/text
plus the bundled fighters/stage in SHELL_BUNDLED_MODELS — and leaves every other .glb/.gltf
out of the deploy. Excluded models load at runtime from the remote asset base
(see game/js/asset-config.js). Nothing is cut from the game, only from the deploy.
    python3 tools/deploy/build_pages.py --ref origin/main --dry-run --shell-only

Itch.io mode (owner decision 2026-10-27, itch-trim lane): --itch builds the same
shell, trimmed further to fit itch.io's HTML5 caps (<=1,000 files, <=500 MB extracted,
<=200 MB per file, filenames <=240 chars). Only the bundled fighters' data ships
(movesets/anim/voices/portraits for demonio, pantera, awa-pop, baek), a 4-track music
subset, and the PNGs those screens use; everything else loads from the remote asset
base exactly like the Pages shell does. The build FAILS (exit 1, nothing written)
if the trimmed set is over any hard itch cap. Soft targets are <=900 files and
<=450 MB, so a small drift does not break itch.
    python3 tools/deploy/build_pages.py --ref origin/main --itch --out <dir>
    cd <dir> && zip -r ../wh-itch-trimmed.zip . -x deploy-manifest.json .deploy-files.txt
Each cut rule in itch_drop_reason() carries the runtime evidence for why the file
is safe to drop (referrer map + the loader that would have fetched it). Nothing is
cut from the game, only from this deploy.
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
# Shell-only deploy (owner decision 2026-10-26: split hosting, Pages shell + GLBs on R2).
# --shell-only ships these models on Pages; every other .glb/.gltf in the closure is
# excluded from the deploy and loads at runtime from the remote asset base
# (game/js/asset-config.js). Picks are the small canon fighters from the verified
# play-verify pair plus two tiny ones, so the shell still plays out of the box:
#   demonio 8.8 MB, pantera 7.6 MB, awa-pop 0.4 MB, baek 0.4 MB (~17 MB total).
# Stages ship as .obj/.png atlases (small); no stage GLB is bundled.
SHELL_BUNDLED_MODELS = (
    "game/assets/models/demonio.glb",
    "game/assets/models/pantera.glb",
    "game/assets/models/awa-pop.glb",
    "game/assets/models/baek.glb",
)
# In shell-only mode a single file over this size never belongs in the shell:
# the remote base serves it instead. 25 MiB matches the Cloudflare Pages
# per-file cap, so the same shell could also deploy there unchanged.
SHELL_MAX_FILE_BYTES = 25 * 1024 * 1024
# Models named in SHELL_BUNDLED_MODELS may exceed the 25 MiB soft cap up to
# GitHub Pages' hard 100 MB per-file limit (Milestone 1 core 8, 2026-10-29).
PAGES_MAX_FILE_BYTES = 100 * 1000 * 1000
# Itch.io HTML5 caps (verified live 2026-10-25/26, agent-ops PR #161):
# <=1,000 files, <=500 MB extracted, <=200 MB per file, filenames <=240 chars.
# --itch trims the shell-only set to the bundled fighters' playable scope.
# Soft targets (<=900 files, <=450 MB) leave margin so a small drift in main
# does not break the itch upload.
ITCH_MAX_FILES = 1000
ITCH_MAX_BYTES = 500 * 1024 * 1024
ITCH_MAX_FILE_BYTES = 200 * 1024 * 1024
ITCH_MAX_NAME = 240
ITCH_TARGET_FILES = 900
ITCH_TARGET_BYTES = 450 * 1024 * 1024
# Bundled fighters (game/js/asset-config.js SHELL_BUNDLED_MODELS). The itch
# build plays these four only; everything else loads from the remote base.
ITCH_BUNDLED_MOVESETS = ("awapop", "baek", "baek-master-white", "demonio",
                         "demonio-bloodline-ember", "demonio-human",
                         "demonio-winged", "pantera")
# Anim banks for the bundled fighters, from the moveset index (anim_bank):
# demonio -> jin, pantera -> king_on_pantera_leoman, awapop -> nina, baek -> bryan.
ITCH_BUNDLED_ANIM_BANKS = ("jin", "king_on_pantera_leoman", "nina", "bryan")
# Music subset: the mode tracks (title -> menu -> select -> battle). The
# music engine (game/js/music.js) filters pickTrack to what exists and
# _fallback() covers an empty pool, never throws; CI runs menu-touch-e2e
# with game/assets/music excluded entirely.
ITCH_MUSIC = ("title-meditation", "menu-deliberate", "select-exhilarate",
              "battle-volatile")
# Fight models the bundled fighters ACTUALLY load — these ship in the itch
# build even though the shell-only filter excludes them (non-bundled .glb,
# three of them over the 25 MB shell cap). The split's SHELL_BUNDLED_MODELS
# names the BASE glbs, but the fight loads the fighters' ATTIRE models:
#   demonio -> demonio-a1 (roster model, attires.js ATTIRE_VARIANTS list
#     head; the BASE demonio.glb "rendered the wrong body on select"),
#     plus its transform targets demonio-winged + demonio-human, which
#     startFight preloads (createInstance is sync) — a demonio fight
#     fails to start without all three.
#   awa-pop -> awa-pop-attire2 (roster model; the bundled awa-pop.glb is
#     the base the pane falls back to, not the fight model).
#   pantera -> pantera (bundled game/assets/models/pantera.glb) for the
#     fight; leomon is the select-pane attire, bundled so the panes stop
#     retrying a missing model.
#   baek -> baek (bundled) for the fight; no forms, no attire override.
# Without these five the itch build's demonio/awa-pop fights fail exactly
# as they do on the Pages shell today (same gap — a split follow-up, not
# this lane: the Pages shell has no remote base yet either). Sizes from
# the R2 manifest: demonio-a1 27.5 MB, winged 18.1 MB, human 27.4 MB,
# awa-pop-attire2 28.7 MB, leomon 4.2 MB (106.0 MB total).
ITCH_BUNDLED_MODELS = (
    "roster/demonio/attires/attire1/model.glb",
    "roster/demonio/attires/winged-devil/model-rigged.glb",
    "roster/demonio/attires/human/model-rerig.glb",
    "roster/awa-pop/attires/attire2/model-rigged.glb",
    "roster/pantera/attires/leomon/model.glb",
)


def itch_drop_reason(f):
    """Reason to drop f from the itch build, or None to keep it.

    Every rule was verified against the runtime code on 2026-10-27 (referrer
    map over the shell text files + the loader that would fetch the file).
    Paths are repo-root-relative, as compute_deploy_files() returns them.
    """
    if f.startswith("customization/parts-converted/") and not f.endswith(".json"):
        return "parts-converted media"
    if f.startswith("customization/parts/") and not f.endswith(".json"):
        return "parts media"
    if f.startswith("customization/decal-library/"):
        return "decal-library (customization only)"
    if f.startswith("customization/reskin-library/"):
        return "reskin-library (customization only)"
    if f.startswith("customization/creation-suite-ui/demo/"):
        return "suite demo mp4"
    if f.startswith("game/assets/movesets/"):
        name = f.rsplit("/", 1)[-1]
        if name in ("index.json", "t3_input_tables.json", "ur-native-index.json"):
            return None
        sub = f[len("game/assets/movesets/"):]
        if name.endswith(".json") and "/" not in sub and name[:-5] in ITCH_BUNDLED_MOVESETS:
            return None
        return "non-bundled moveset"
    if f.startswith("game/assets/anim/t3/"):
        rest = f[len("game/assets/anim/t3/"):]
        if "/" not in rest:
            return None  # top-level classification/reaction JSONs
        if rest.split("/", 1)[0] in ITCH_BUNDLED_ANIM_BANKS:
            return None
        return "non-bundled anim bank"
    if f.startswith(("game/assets/anim/ur-general-", "game/assets/anim/t7/",
                     "game/assets/anim/made/", "game/assets/anim/oss/")):
        return "unused anim"
    if f.startswith("game/assets/music/"):
        return None if f.rsplit("/", 1)[-1][:-4] in ITCH_MUSIC else "non-kept music"
    if f.startswith("game/assets/sounds/"):
        # game/js/voice.js playSound(bankId) has zero callers repo-wide;
        # fight voices come from game/assets/voices/ via the voice manifests.
        return "sound-bank (no callers)"
    if f.startswith("game/assets/archive/"):
        return "archive"
    if f.startswith("game/assets/voices/"):
        return None if f.split("/")[3] in ("demonio", "pantera") else "non-bundled voices"
    if f.startswith("game/assets/portraits/"):
        # select-screen.js portraitHTML has an onerror fallback to a
        # procedural SVG + monogram, so a missing portrait never breaks a card.
        return None if f.rsplit("/", 1)[-1][:-4] in ITCH_BUNDLED_MOVESETS else "non-bundled portrait"
    if f.startswith("game/ui-wh/portraits/zui_"):
        return "zui ui portraits"
    if f.startswith("game/assets/stages/thumbs/"):
        # stages.js falls back to the palette swatch when a thumb is absent.
        return "stage thumbs"
    if f.startswith("game/assets/models/renders/"):
        return "model renders"
    if f.startswith(("game/assets/poses/", "assets/poses/")):
        # Referenced only by game/ui-wh/roster.js (art cards); the fight
        # never loads them. (Top-level assets/ is the repo-root mirror the
        # roster file reaches via ../../assets/poses/.)
        return "poses (poselab only)"
    if f.startswith("game/data/t7-frame-data/"):
        # t7Frame() has no callers in the fight path; the loader is lazy.
        return "t7 frame data"
    if f.startswith("game/data/movesets/"):
        return "data/movesets"
    if f.startswith("game/data/moveset-library/"):
        # game/js/moveset-library.js has no importer; frame-tables.js mentions
        # it only in a comment. The fight's frame data is t8_frame_tables.json.
        return "moveset-library (no importer)"
    if f.startswith("game/data/voices/"):
        return None if f.rsplit("/", 1)[-1][:-5] in ("awapop", "baek-master-white", "demonio", "pantera") else "non-bundled voice manifest"
    if f.startswith("game/tests/"):
        return "tests"
    if f.startswith("docs/"):
        return "docs"
    if f.startswith("game/assets/") and f.endswith("_moves.json"):
        return "legacy *_moves.json"
    if f.startswith("game/assets/accessories/"):
        return "accessories docs"
    if f.startswith("game/assets/stages/eastern-mind/ai-pass/"):
        return "ai-pass compare images"
    if f.startswith("game/assets/stages/eastern-mind/") and f.endswith("/pano.png"):
        # Stage defs name pano-wh.png; the pano loader has no pano.png fallback.
        return "superseded pano.png"
    if f.startswith("game/assets/stages/sunra/preview/"):
        return "sunra preview media"
    return None
REPO = os.environ.get("WH_REPO", "mhvnsnt/western-heart")
STR = re.compile(r"""["'`]([^"'`\s<>{}$|*?]+\.[A-Za-z0-9]{2,5})(?:[?#][^"'`\s]*)?["'`]""")


def git(*args, binary=False):
    r = subprocess.run(["git", *args], capture_output=True)
    if r.returncode:
        sys.exit(r.stderr.decode()[:2000])
    return r.stdout if binary else r.stdout.decode()


def blob_sizes(sha):
    """Sizes for every blob WITHOUT lazy-fetching it. `git ls-tree -l` in a blob:none partial clone
    downloads every blob one at a time (60k+ round trips = the old >10 min hang). Present blobs are
    sized locally (GIT_NO_LAZY_FETCH); missing ones via the GitHub trees API per top-level dir."""
    oids = {}
    # -z: NUL-separated, never C-quoted. Without it, filenames with non-ASCII
    # bytes (e.g. customization/parts/wmxix mojibake names, on main since
    # 2026-10-26) come back "..." quoted and break every later lookup —
    # the script died on `rev-parse <sha>:"customization` before this fix.
    for line in git("ls-tree", "-r", "-z", sha).split("\0"):
        if not line:
            continue
        meta, path = line.split("\t", 1)
        mode, kind, obj = meta.split()
        if kind == "blob":
            oids[path] = obj
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1")
    uniq = sorted(set(oids.values()))
    r = subprocess.run(["git", "cat-file", "--batch-check=%(objectname) %(objectsize)"], input="\n".join(uniq) + "\n",
                       capture_output=True, text=True, env=env)
    by_oid = {}
    for l in r.stdout.splitlines():
        a, b = l.split(" ", 1)
        if b != "missing":
            by_oid[a] = int(b)
    need = {o for o in uniq if o not in by_oid}
    if need:
        def walk(path, depth=0):
            # The trees API truncates big recursive listings (~100k entries /
            # 7 MB); when it does, descend one level and list each subtree.
            try:
                t = git("rev-parse", f"{sha}:{path}").strip()
                d = None
                for _ in range(4):  # the API call is retried: a flaky fetch must not zero sizes
                    out = subprocess.run(["gh", "api", f"repos/{REPO}/git/trees/{t}?recursive=1"],
                                         capture_output=True, text=True)
                    if out.returncode == 0:
                        d = json.loads(out.stdout)
                        break
                if d is None:
                    return
            except Exception:
                return
            for e in d.get("tree", []):
                if e.get("type") == "blob":
                    by_oid[e["sha"]] = e.get("size", 0)
            if d.get("truncated") and depth < 4:
                for e in d.get("tree", []):
                    if e.get("type") == "tree" and "/" not in e["path"]:
                        walk(f"{path}/{e['path']}", depth + 1)
        for top in sorted({p.split("/", 1)[0] for p, o in oids.items() if o in need and "/" in p}):
            walk(top)
    unknown = sum(1 for o in uniq if o not in by_oid)
    if unknown:
        print(f"note: {unknown} blob sizes unknown (API truncated); counted as 0 MB in the report")
    return {p: by_oid.get(o, 0) for p, o in oids.items()}, oids


def prefetch_text(oids):
    """One batched fetch of every runtime text blob the closure scan may read (was one lazy fetch per file)."""
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1")
    want = sorted({o for p, o in oids.items() if p.endswith(TEXT) and not p.startswith(SKIP)})
    r = subprocess.run(["git", "cat-file", "--batch-check=%(objectname) %(objecttype)"], input="\n".join(want) + "\n",
                       capture_output=True, text=True, env=env)
    miss = [l.split()[0] for l in r.stdout.splitlines() if l.endswith(" missing")]
    for i in range(0, len(miss), 2000):
        subprocess.run(["git", "-c", "fetch.negotiationAlgorithm=noop", "fetch", "-q", "--no-tags",
                        "--no-write-fetch-head", "--filter=blob:none", "origin", *miss[i:i + 2000]])
    if miss:
        print(f"prefetched {len(miss)} text blobs in {(len(miss) + 1999) // 2000} batch(es)")


def shell_bundled_models(sha):
    """Bundled-model allowlist, read from game/js/asset-config.js on the same
    ref — that file is the single source of truth, so the deploy script and
    the loader can never drift apart. Falls back to SHELL_BUNDLED_MODELS
    (with a warning) if the file or the list cannot be read."""
    try:
        txt = git("cat-file", "-p", f"{sha}:game/js/asset-config.js")
        m = re.search(r"SHELL_BUNDLED_MODELS\s*=\s*\[([^\]]*)\]", txt)
        if m:
            found = tuple(re.findall(r"'([^']+)'", m.group(1)))
            if found:
                return found
    except SystemExit:
        pass
    print("warning: could not read SHELL_BUNDLED_MODELS from game/js/asset-config.js; using built-in list")
    return SHELL_BUNDLED_MODELS


def compute_deploy_files(sha, sizes, oids, follow_all=False, shell_only=False,
                         itch_only=False, itch_reasons=None):
    """Reference closure over ROOTS, as a sorted file list.

    Shared by main() and tools/deploy/r2-upload-manifest.py so the R2 manifest
    and the deploy set can never drift apart: one closure, two consumers.
    shell_only=True applies the split-hosting filter (see SHELL_BUNDLED_MODELS)
    and returns (files, excluded) where excluded is the sorted list of files
    dropped from the shell (they load from the remote asset base at runtime).
    itch_only=True implies shell_only and then applies the itch trim
    (see itch_drop_reason); when itch_reasons is a dict it is filled with
    {dropped path: reason} for the itch-trimmed files.
    """
    files = set(p for p in sizes if p.startswith(ROOTS))
    queue = [p for p in files if p.endswith(TEXT)]
    seen_text = set(queue)
    while queue:
        p = queue.pop()
        if p in NO_FOLLOW and not follow_all:
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
    if itch_only:
        shell_only = True
    if not shell_only:
        return files, []
    bundled = shell_bundled_models(sha)
    excluded = []
    kept = []
    for f in files:
        if f.lower().endswith((".glb", ".gltf")) and f not in bundled:
            excluded.append(f)
        elif sizes[f] > (PAGES_MAX_FILE_BYTES if f in bundled else SHELL_MAX_FILE_BYTES):
            excluded.append(f)
        else:
            kept.append(f)
    if not itch_only:
        return kept, sorted(excluded)
    # The bundled fighters' fight models (ITCH_BUNDLED_MODELS) were just
    # excluded by the shell filter (non-bundled .glb, three over the 25 MB
    # shell cap) — put them back: the fight loads these, not the BASE glbs.
    # They must be in the reference closure (assets.js MODEL_URLS names
    # them); if one is missing from the ref, that is a loud failure, not
    # a silent skip — the itch build cannot play without it.
    missing = [f for f in ITCH_BUNDLED_MODELS if f not in sizes]
    if missing:
        sys.exit(f"itch: bundled fight model(s) missing from {sha}: {missing}")
    for f in ITCH_BUNDLED_MODELS:
        if f in excluded:
            excluded.remove(f)
        if f not in kept:
            # In the closure (assets.js MODEL_URLS names it) in practice;
            # added from the ref directly if the closure ever misses it.
            kept.append(f)
    itch_kept = []
    for f in kept:
        reason = itch_drop_reason(f)
        if reason is None:
            itch_kept.append(f)
        else:
            excluded.append(f)
            if itch_reasons is not None:
                itch_reasons[f] = reason
    return itch_kept, sorted(excluded)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--out", default=None)
    ap.add_argument("--onto", default=None, help="plumbing mode: parent gh-pages ref (e.g. origin/gh-pages)")
    ap.add_argument("--branch", default="gh-pages")
    ap.add_argument("--orphan", action="store_true",
                    help="plumbing mode with no parent: a fresh deploy commit on --branch "
                         "holding ONLY the deploy set (new branch; nothing is deleted anywhere)")
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--follow-all", action="store_true")
    ap.add_argument("--shell-only", action="store_true",
                    help="deploy the playable shell only (owner decision 2026-10-26: "
                         "Pages shell + GLBs on R2); all other .glb/.gltf load at "
                         "runtime from the remote asset base (game/js/asset-config.js)")
    ap.add_argument("--itch", action="store_true",
                    help="itch.io HTML5 build: the shell-only set trimmed to the bundled "
                         "fighters (see itch_drop_reason); fails if over itch.io's hard "
                         "caps (1,000 files / 500 MB extracted / 200 MB per file)")
    a = ap.parse_args()
    if a.itch:
        a.shell_only = True
    sha = git("rev-parse", a.ref).strip()
    sizes, oids = blob_sizes(sha)
    prefetch_text(oids)
    itch_reasons = {} if a.itch else None
    files, excluded = compute_deploy_files(sha, sizes, oids, a.follow_all, a.shell_only,
                                           a.itch, itch_reasons)
    total = sum(sizes[f] for f in files)
    by_top = {}
    for f in files:
        top = f.split("/", 1)[0]
        by_top[top] = by_top.get(top, 0) + sizes[f]
    mode = "itch" if a.itch else ("shell-only" if a.shell_only else "full")
    print(f"ref {a.ref} = {sha}: {len(files)} files, {total/1e6:.1f} MB ({mode})")
    for t, s in sorted(by_top.items(), key=lambda x: -x[1]):
        print(f"  {t:16s} {s/1e6:9.1f} MB")
    if excluded:
        ex_bytes = sum(sizes[f] for f in excluded)
        ex_glb = [f for f in excluded if f.lower().endswith((".glb", ".gltf"))]
        print(f"{mode}: excluded {len(excluded)} files, {ex_bytes/1e6:.1f} MB "
              f"({len(ex_glb)} models -> remote asset base)")
    big = [f for f in files if sizes[f] > 95e6]
    if big:
        print("over 95 MB (GitHub per-file limit is 100 MB):", big)
    if total > 1e9:
        print(f"WARNING: deploy set {total/1e6:.0f} MB exceeds the GitHub Pages 1 GB published-site limit")
    if a.itch:
        largest = max(((sizes[f], f) for f in files), default=(0, ""))
        longest = max(((len(f), f) for f in files), default=(0, ""))
        print(f"itch caps: {len(files)}/{ITCH_MAX_FILES} files, {total/1e6:.1f}/{ITCH_MAX_BYTES/1e6:.0f} MB "
              f"extracted, largest {largest[0]/1e6:.2f} MB ({largest[1]}), "
              f"longest name {longest[0]}/{ITCH_MAX_NAME} chars")
        over = []
        if len(files) > ITCH_MAX_FILES:
            over.append(f"{len(files)} files > {ITCH_MAX_FILES}")
        if total > ITCH_MAX_BYTES:
            over.append(f"{total/1e6:.1f} MB > {ITCH_MAX_BYTES/1e6:.0f} MB")
        if largest[0] > ITCH_MAX_FILE_BYTES:
            over.append(f"largest file {largest[0]/1e6:.1f} MB > {ITCH_MAX_FILE_BYTES/1e6:.0f} MB")
        if longest[0] > ITCH_MAX_NAME:
            over.append(f"filename {longest[0]} chars > {ITCH_MAX_NAME}: {longest[1]}")
        if over:
            sys.exit("ITCH CAPS FAILED: " + "; ".join(over) + " — trim further, nothing written")
        print("itch caps: PASS" +
              ("" if len(files) <= ITCH_TARGET_FILES and total <= ITCH_TARGET_BYTES else
               f" (note: over soft targets {ITCH_TARGET_FILES} files / {ITCH_TARGET_BYTES/1e6:.0f} MB)"))
        from collections import Counter
        print("itch trim (dropped from shell):")
        for reason, n in sorted(Counter(itch_reasons.values()).items(), key=lambda x: -x[1]):
            print(f"  {n:5d}  {reason}")
    if a.dry_run:
        return
    if a.onto or a.orphan:
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
           "bytes": total, "built": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "tool": "tools/deploy/build_pages.py", "mode": mode}
    if excluded:
        man["excluded_files"] = len(excluded)
        man["excluded_bytes"] = sum(sizes[f] for f in excluded)
    if a.itch:
        from collections import Counter
        man["itch_trim"] = {"dropped_files": len(itch_reasons),
                            "dropped_bytes": sum(sizes[f] for f in itch_reasons),
                            "by_reason": dict(sorted(Counter(itch_reasons.values()).items(),
                                                    key=lambda x: -x[1])),
                            "caps": {"max_files": ITCH_MAX_FILES, "max_bytes": ITCH_MAX_BYTES,
                                     "max_file_bytes": ITCH_MAX_FILE_BYTES, "max_name": ITCH_MAX_NAME}}
    with open(os.path.join(a.out, "deploy-manifest.json"), "w") as fh:
        json.dump(man, fh, indent=1)
    with open(os.path.join(a.out, ".deploy-files.txt"), "w") as fh:
        fh.write("\n".join(files) + "\n")
    print("written; file list:", os.path.join(a.out, ".deploy-files.txt"))


def plumbing(a, sha, files, sizes, total):
    import tempfile
    blob = {}
    for line in git("ls-tree", "-r", "-z", sha, "--", *sorted({f.split("/", 1)[0] for f in files})).split("\0"):
        if not line:
            continue
        meta, path = line.split("\t", 1)
        mode, kind, obj = meta.split()
        if kind == "blob":
            blob[path] = (mode, obj)
    parent = None if a.orphan else git("rev-parse", a.onto).strip()
    idx = tempfile.mktemp(prefix="wh-pages-index-")
    env = dict(os.environ, GIT_INDEX_FILE=idx)
    def g(*args, inp=None):
        r = subprocess.run(["git", *args], capture_output=True, env=env, input=inp)
        if r.returncode:
            sys.exit(r.stderr.decode()[:2000])
        return r.stdout.decode()
    if parent:
        g("read-tree", parent)
    else:
        g("read-tree", "--empty")
    before = {l.split("\t", 1)[1]: l.split()[1] for l in g("ls-files", "-s", "-z").split("\0") if l}
    lines, changed = [], 0
    for f in files:
        mode, obj = blob[f]
        if before.get(f) != obj:
            changed += 1
        lines.append(f"{mode} {obj}\t{f}")
    g("update-index", "--index-info", inp=("\n".join(lines) + "\n").encode())
    man = json.dumps({"format": "wh-pages-deploy/1", "ref": a.ref, "commit": sha, "files": len(files),
                      "bytes": total, "tool": "tools/deploy/build_pages.py",
                      "mode": "itch" if a.itch else ("shell-only" if a.shell_only else "full")}, indent=1).encode()
    mobj = g("hash-object", "-w", "--stdin", inp=man).strip()
    g("update-index", "--add", "--cacheinfo", f"100644,{mobj},deploy-manifest.json")
    after = set(l.split("\t", 1)[1] for l in g("ls-files", "-s", "-z").split("\0") if l)
    missing = set(before) - after
    if missing:
        sys.exit(f"refusing: {len(missing)} entries would be removed")
    tree = g("write-tree").strip()
    if parent and tree == git("rev-parse", parent + "^{tree}").strip():
        print("gh-pages already matches", a.ref, "- nothing to deploy")
        os.remove(idx)
        return
    msg = (f"Deploy: western-heart from {a.ref} @ {sha[:9]} (tools/deploy/build_pages.py)\n\n"
           f"{changed} files added or updated ({len(files)} in the deploy set, {total/1e6:.0f} MB"
           f"{', shell-only' if a.shell_only else ''}); "
           f"0 removed.\n")
    commit = g("-c", "user.name=wh-deploy", "-c", "user.email=noreply@github.com",
               "commit-tree", tree, *(["-p", parent] if parent else []), inp=msg.encode()).strip()
    os.remove(idx)
    print("new", a.branch, "commit", commit, f"({changed} files changed vs {a.onto})")
    if a.push:
        r = subprocess.run(["git", "push", "origin", f"{commit}:refs/heads/{a.branch}"], capture_output=True, text=True)
        print(r.stdout, r.stderr)
        if r.returncode:
            sys.exit("push failed")


if __name__ == "__main__":
    main()

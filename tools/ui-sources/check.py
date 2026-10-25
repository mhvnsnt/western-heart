#!/usr/bin/env python3
"""ui_sources gate (owner law t123u, Oct 23 2026: no hand-made menus).

Usage: check.py BASE_REF HEAD_REF   (git refs/SHAs; reads blobs via git, no checkout needed)

Rules (enforced against the manifest game/ui_sources.json at HEAD):
 1. Every <section id="screen-*"> in game/index.html has a manifest entry.
 2. A screen that is NEW in this PR, or whose <section> markup CHANGED, or that
    owns (manifest "files") a file CHANGED in this PR, must cite >=1 teardown
    source: a path that exists at HEAD under teardown/, or
    "gre:<path>" that exists in mhvnsnt/game-reverse-engineering (checked
    offline against tools/ui-sources/gre_paths.txt if present, else format-only).
    Status "legacy-unsourced" is only allowed for untouched screens.
 3. Any other change to a UI file (UI_GLOBS) must come with a manifest entry
    listing that file under a sourced screen.
Exit 1 with a list of violations; 0 otherwise.
"""
import json, re, subprocess, sys, fnmatch

UI_GLOBS = ["game/index.html", "game/*.css", "game/js/*menu*.js", "game/js/*-screen.js",
            "game/js/*-ui.js", "game/js/ui-*.js", "game/ui/*", "game/ui/**",
            "packages/creation-suite/src/*ui*", "packages/creation-suite/*.html"]
MANIFEST = "game/ui_sources.json"

def git(*a, ok=False):
    r = subprocess.run(["git", *a], capture_output=True, text=True)
    if r.returncode and not ok: sys.exit(f"git {' '.join(a)} failed: {r.stderr}")
    return r.stdout if r.returncode == 0 else None

def show(ref, path): return git("show", f"{ref}:{path}", ok=True)

def sections(html):
    out = {}
    if not html: return out
    for m in re.finditer(r'<section\s+id="(screen-[a-z0-9-]+)"', html):
        start = m.start(); depth = 0; i = start
        for t in re.finditer(r'<(/?)section\b', html[start:]):
            depth += -1 if t.group(1) else 1
            if depth == 0: i = start + t.end(); break
        out[m.group(1)] = html[start:i]
    return out

def is_ui(p): return any(fnmatch.fnmatch(p, g) for g in UI_GLOBS)

def main(base, head):
    raw = show(head, MANIFEST)
    if raw is None: sys.exit(f"FAIL: {MANIFEST} missing at {head}")
    man = json.loads(raw)["screens"]
    fork = (git("merge-base", base, head, ok=True) or base).strip()
    changed = [l for l in git("diff", "--name-only", fork, head).splitlines()]
    hs, bs = sections(show(head, "game/index.html")), sections(show(fork, "game/index.html"))
    gre = set()
    try: gre = set(open("tools/ui-sources/gre_paths.txt").read().split())
    except OSError: pass
    def valid(src):
        if src.startswith("gre:"): return (src[4:] in gre) if gre else bool(src[4:])
        return src.startswith("teardown/") and git("cat-file", "-e", f"{head}:{src}", ok=True) is not None
    errs, touched = [], set()
    for sid in hs:
        if sid not in man: errs.append(f"{sid}: no entry in {MANIFEST}")
        if sid not in bs or hs[sid] != bs[sid]: touched.add(sid)
    owner = {}
    for sid, e in man.items():
        for f in e.get("files", []): owner.setdefault(f, []).append(sid)
    for f in changed:
        if f == MANIFEST or not is_ui(f) or f == "game/index.html": continue
        if f in owner: touched.update(owner[f])
        else: errs.append(f"{f}: UI file changed but not listed under any screen's \"files\" in {MANIFEST}")
    for sid in sorted(touched):
        e = man.get(sid)
        if not e: continue
        srcs = e.get("sources", [])
        bad = [s for s in srcs if not valid(s)]
        if not srcs or e.get("status") == "legacy-unsourced":
            errs.append(f"{sid}: changed/new but has no teardown source (status={e.get('status')}). Hand-made menus are banned (AGENTS.md).")
        elif bad: errs.append(f"{sid}: source(s) not found: {bad}")
    print(f"ui_sources: {len(hs)} screens, {len(touched)} touched: {sorted(touched)}")
    if errs:
        print("FAIL:\n  " + "\n  ".join(errs)); sys.exit(1)
    print("PASS")

if __name__ == "__main__": main(*sys.argv[1:3])

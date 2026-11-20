#!/usr/bin/env python3
"""check_module_graph.py — verify a Western Heart tree's ES module graph
is complete: every module the shell can import actually exists in the tree.

Why this exists (2026-10-30 regression): a delta deploy shipped the new
game/js/fighter.js without game/js/step-plan-bank.js, which fighter.js
imports. The module 404'd, the dynamic import of fighter.js rejected,
and EVERY fight bounced back to the stage screen ("Failed to load
fighters: Failed to fetch dynamically imported module ...") until a
follow-up deploy added the missing file. A browser caches a failed
module in its module map for the life of the page, so players who hit
the broken window stayed broken until they reloaded by hand.

Run this against the assembled deploy tree (or a checkout of the
gh-pages-m1-20261029 branch) before/after every deploy:

    python3 tools/deploy/check_module_graph.py [TREE_ROOT]

TREE_ROOT defaults to the current directory. The walk starts at
<TREE_ROOT>/game/index.html: its importmap and module <script> entries
seed a transitive scan of import / export-from / dynamic-import string
specifiers. Relative specifiers resolve against the importing file;
bare specifiers resolve through the importmap. Non-literal dynamic
imports (template strings, variables) cannot be resolved statically
and are skipped.

Severity: a missing target of a STATIC import in a first-party file is
a hard failure (exit 1) — that is the failure class that bricks the
whole module graph. Missing DYNAMIC imports (call sites in this
codebase guard them by design), unmapped bare specifiers, and anything
inside a vendor/ tree are warnings: printed, but the exit code stays 0.
"""
import json
import os
import re
import sys

IMPORTMAP_RE = re.compile(r'<script[^>]+type="importmap"[^>]*>(.*?)</script>', re.S)
SCRIPT_SRC_RE = re.compile(r'<script[^>]+type="module"[^>]+src="([^"]+)"', re.S)
STATIC_RE = re.compile(r"""(?:import|export)\s+(?:[^'"]*?\s+from\s+)?['"]([^'"]+)['"]""")
DYNAMIC_RE = re.compile(r"""import\s*\(\s*['"]([^'"]+)['"]\s*\)""")


def strip_comments(src):
    """Remove /* */ blocks and // line comments so specifiers quoted in
    docs (e.g. a usage example in a header comment) are not mistaken for
    real imports. Line-comment stripping skips '//' right after ':' so
    URLs inside strings survive."""
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    out = []
    for line in src.splitlines():
        i = line.find("//")
        while i != -1 and i > 0 and line[i - 1] == ":":
            i = line.find("//", i + 2)
        out.append(line if i == -1 else line[:i])
    return "\n".join(out)


def load_importmap(html_path):
    with open(html_path, encoding="utf-8", errors="replace") as f:
        html = f.read()
    entries = SCRIPT_SRC_RE.findall(html)
    mapping = {}
    m = IMPORTMAP_RE.search(html)
    if m:
        try:
            mapping = json.loads(m.group(1)).get("imports", {})
        except json.JSONDecodeError as e:
            print(f"ERROR: importmap in {html_path} is not valid JSON: {e}")
            sys.exit(2)
    return entries, mapping


def resolve(spec, importer_dir, html_dir, mapping):
    """Return the tree-relative path a specifier resolves to, or None if
    it is a bare specifier with no importmap entry."""
    if spec.startswith("./") or spec.startswith("../"):
        return os.path.normpath(os.path.join(importer_dir, spec))
    # Bare specifier: longest importmap key match (exact or '/' prefix).
    best = None
    for key, target in mapping.items():
        if key.endswith("/") and spec.startswith(key):
            cand = target + spec[len(key):]
            if best is None or len(key) > len(best[0]):
                best = (key, cand)
        elif spec == key:
            return os.path.normpath(os.path.join(html_dir, target))
    if best:
        return os.path.normpath(os.path.join(html_dir, best[1]))
    return None


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    html_path = os.path.join(root, "game", "index.html")
    if not os.path.exists(html_path):
        print(f"ERROR: {html_path} not found — TREE_ROOT must be the tree root containing game/")
        return 2
    html_dir = os.path.join(root, "game")
    entries, mapping = load_importmap(html_path)

    queue = []
    for e in entries:
        p = os.path.normpath(os.path.join(html_dir, e))
        queue.append(p)
    seen = set()
    hard = []  # static import in a first-party file -> target missing (the 2026-10-30 break class)
    warn = []  # dynamic import missing, unmapped bare specifier, or anything from a vendor tree
    scanned = 0
    while queue:
        path = queue.pop()
        if path in seen:
            continue
        seen.add(path)
        if not os.path.exists(path):
            hard.append(("<entry>", os.path.relpath(path, root), os.path.relpath(path, root), "static"))
            continue
        if not path.endswith((".js", ".mjs")):
            continue
        scanned += 1
        with open(path, encoding="utf-8", errors="replace") as f:
            src = strip_comments(f.read())
        importer_dir = os.path.dirname(path)
        rel = os.path.relpath(path, root)
        in_vendor = "/vendor/" in path.replace(os.sep, "/")
        for rx, kind in ((STATIC_RE, "static"), (DYNAMIC_RE, "dynamic")):
            for spec in rx.findall(src):
                resolved = resolve(spec, importer_dir, html_dir, mapping)
                if resolved is None:
                    warn.append((rel, spec, "(no importmap entry)", kind))
                    continue
                if not os.path.exists(resolved):
                    item = (rel, spec, os.path.relpath(resolved, root), kind)
                    if kind == "static" and not in_vendor:
                        hard.append(item)
                    else:
                        warn.append(item)
                else:
                    queue.append(resolved)

    for importer, spec, resolved, kind in sorted(set(warn)):
        print(f"WARN ({kind}): {importer} imports '{spec}' -> {resolved} (unresolved; guarded/vendor/dynamic — not a hard failure)")
    for importer, spec, resolved, kind in sorted(set(hard)):
        print(f"MISSING MODULE ({kind}): {importer} imports '{spec}' -> {resolved} (not in tree)")
    if hard:
        print(f"FAIL: {len(set(hard))} hard unresolved module reference(s), {len(set(warn))} warning(s); {scanned} files scanned from {len(entries)} entry point(s)")
        return 1
    print(f"OK: module graph complete — {scanned} files scanned, {len(seen)} modules resolved, 0 hard missing, {len(set(warn))} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

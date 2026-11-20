#!/usr/bin/env python3
"""Model wiring audit for Western Heart (worker-9 wire-up pass, 2026-10-22).

Authoritative on-disk vs wired map:
  - on-disk models: every .glb under roster/*/attires/ on MAIN
    (via --manifest tree dump, or by walking a local clone dir)
  - wired: keys of MODEL_URLS in game/js/assets.js + ATTIRE_VARIANTS
    ladders in game/js/attires.js + fighter model keys in game/js/roster-full.js

Usage:
  wire-audit.py --manifest /tmp/tree.json --assets game/js/assets.js \\
      --attires game/js/attires.js --rosterfull game/js/roster-full.js
  wire-audit.py --root ~/workspace/fix3/wireaudit ...

A GLB is WIRED when its repo path matches a MODEL_URLS value (after
normalizing '../' prefixes). A wired key is REACHABLE when it appears in
some fighter's ATTIRE_VARIANTS ladder or as a fighter's base model key.
"""
import argparse, json, os, re, sys

MODEL_URLS_RE = re.compile(r"^\s*['\"]?([\w\-/]+)['\"]?\s*:\s*['\"]([^'\"]+)['\"]", re.M)
FIGHTER_RE = re.compile(r"^\s*(?:id|model)\s*:\s*['\"]([^'\"]+)['\"]", re.M)
LADDER_KEY_RE = re.compile(r"^\s*['\"]?([\w\-]+)['\"]?\s*:\s*\[", re.M)
LADDER_MODEL_RE = re.compile(r"\{\s*model\s*:\s*['\"]([^'\"]+)['\"]")


def parse_model_urls(text):
    """Extract the MODEL_URLS object literal, then key->url pairs."""
    m = re.search(r"export const MODEL_URLS\s*=\s*\{", text)
    assert m, "MODEL_URLS not found"
    start = m.end() - 1
    depth, i = 0, start
    while True:
        c = text[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                break
        i += 1
    body = text[start:i + 1]
    pairs = {}
    for km in MODEL_URLS_RE.finditer(body):
        key, url = km.group(1), km.group(2)
        if key in ('import', 'export'):
            continue
        pairs[key] = url
    return pairs


def norm_url(url):
    u = url.strip()
    if u.startswith('../'):
        return u[3:]
    return u


def parse_ladders(text):
    m = re.search(r"export const ATTIRE_VARIANTS\s*=\s*\{", text)
    assert m, "ATTIRE_VARIANTS not found"
    start = m.end() - 1
    depth, i = 0, start
    while True:
        c = text[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                break
        i += 1
    body = text[start:i + 1]
    ladders, cur = {}, None
    for line in body.splitlines():
        km = LADDER_KEY_RE.match(line)
        if km and '[' in line:
            cur = km.group(1)
            ladders[cur] = []
            continue
        if cur:
            mm = LADDER_MODEL_RE.search(line)
            if mm:
                ladders[cur].append(mm.group(1))
    return ladders


def parse_roster_full(text):
    """Best-effort: id -> model for fighter entries.

    Entries look like:  { id: 'rin', name: 'RIN', ..., model: 'steve-fox', ... }
    mostly on one line, sometimes spanning lines inside the same {...}.
    """
    fighters = {}
    # find each top-level { ... } entry of FULL_ROSTER by brace depth
    m = re.search(r"FULL_ROSTER\s*=\s*\[", text)
    assert m, "FULL_ROSTER not found"
    i = m.end()
    while i < len(text):
        if text[i] == '{':
            depth, j = 1, i + 1
            while depth and j < len(text):
                if text[j] == '{':
                    depth += 1
                elif text[j] == '}':
                    depth -= 1
                j += 1
            block = text[i:j]
            im = re.search(r"\bid\s*:\s*['\"]([^'\"]+)['\"]", block)
            mm = re.search(r"\bmodel\s*:\s*['\"]([^'\"]+)['\"]", block)
            if im and mm:
                fighters[im.group(1)] = mm.group(1)
            i = j
        else:
            i += 1
    return fighters


def ondisk_from_manifest(manifest):
    d = json.load(open(manifest))
    out = []
    for t in d['tree']:
        p = t['path']
        if (t['type'] == 'blob' and p.startswith('roster/')
                and '/attires/' in p and p.lower().endswith('.glb')):
            out.append((p, t.get('size', 0)))
    return sorted(out)


def ondisk_from_root(root):
    out = []
    rdir = os.path.join(root, 'roster')
    for dirpath, _dn, fn in os.walk(rdir):
        if '/attires/' not in dirpath.replace(os.sep, '/'):
            continue
        for f in fn:
            if f.lower().endswith('.glb'):
                full = os.path.join(dirpath, f)
                rel = os.path.relpath(full, root).replace(os.sep, '/')
                out.append((rel, os.path.getsize(full)))
    return sorted(out)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--manifest', help='github trees recursive JSON (authoritative)')
    ap.add_argument('--root', help='local clone root to walk')
    ap.add_argument('--assets', required=True)
    ap.add_argument('--attires', required=True)
    ap.add_argument('--rosterfull', required=True)
    a = ap.parse_args()

    if a.manifest:
        ondisk = ondisk_from_manifest(a.manifest)
        print(f"on-disk source: manifest ({len(ondisk)} GLBs under roster/*/attires/)")
    else:
        ondisk = ondisk_from_root(a.root or '.')
        print(f"on-disk source: walk of {a.root or '.'} ({len(ondisk)} GLBs)")

    model_urls = parse_model_urls(open(a.assets).read())
    ladders = parse_ladders(open(a.attires).read())
    fighters = parse_roster_full(open(a.rosterfull).read())
    print(f"MODEL_URLS keys: {len(model_urls)}")
    print(f"ladder fighters: {len(ladders)}")
    print(f"roster-full entries: {len(fighters)}")

    wired_path_to_keys = {}
    for key, url in model_urls.items():
        wired_path_to_keys.setdefault(norm_url(url), []).append(key)

    reachable_keys = set()
    for _f, keys in ladders.items():
        reachable_keys.update(keys)
    reachable_keys.update(fighters.values())

    wired, unwired = [], []
    for path, size in ondisk:
        if path in wired_path_to_keys:
            keys = wired_path_to_keys[path]
            reach = [k for k in keys if k in reachable_keys]
            wired.append((path, size, keys, bool(reach)))
        else:
            unwired.append((path, size))

    print("\n================ WIRED (on-disk, in MODEL_URLS) ================")
    unreach = 0
    for path, size, keys, reach in wired:
        flag = "" if reach else "  <-- KEY NOT IN ANY LADDER/ROSTER (dead key)"
        if not reach:
            unreach += 1
        print(f"  [{size/1e6:6.1f}MB] {path}\n           keys={keys}{flag}")

    print(f"\n================ UNWIRED ({len(unwired)}) ================")
    for path, size in unwired:
        print(f"  [{size/1e6:6.1f}MB] {path}")

    # wired keys whose path no longer exists on disk (dangling)
    ondisk_set = {p for p, _s in ondisk}
    dangling = [(k, u) for k, u in model_urls.items()
                if u.startswith('../roster') and norm_url(u) not in ondisk_set]
    print(f"\n================ DANGLING KEYS ({len(dangling)}) ================")
    for k, u in dangling:
        print(f"  {k} -> {u}")

    print("\n================ SUMMARY ================")
    print(f"on-disk GLBs: {len(ondisk)} | wired: {len(wired)} | unwired: {len(unwired)} | "
          f"wired-but-unreachable: {unreach} | dangling keys: {len(dangling)}")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

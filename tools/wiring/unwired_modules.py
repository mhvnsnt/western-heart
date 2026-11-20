#!/usr/bin/env python3
"""tools/wiring/unwired_modules.py — which game modules are BUILT but never loaded (owner 2026-11-01: "a lot of things
are there that aren't fully wired up ... get everything 100% complete").

Walks the module graph from every HTML page's scripts (game/index.html first) through static imports, dynamic
import('./x.js'), integration.js tryInit('name', './x.js') loads and new URL('./x.js') references, then lists every
game/js module no page reaches, with the first line of its header (what it is), and which other pages reach it.

    python3 tools/wiring/unwired_modules.py            # table
    python3 tools/wiring/unwired_modules.py --json     # machine-readable
"""
import json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EDGE = [re.compile(r"""(?:from|import)\s*\(?\s*['"](\.{1,2}/[^'"]+)['"]"""),
        re.compile(r"""tryInit\(\s*['"][^'"]+['"]\s*,\s*['"](\.{1,2}/[^'"]+)['"]"""),
        re.compile(r"""new URL\(\s*['"](\.{1,2}/[^'"]+\.m?js)['"]"""), re.compile(r"""['"](\./[\w\-/]+\.m?js)['"]""")]


def page_entries(html_path):
    s = open(html_path, encoding='utf8', errors='replace').read()
    base = os.path.dirname(html_path)
    out = set()
    for m in re.finditer(r'<script[^>]*src="([^"]+)"', s):
        if not m.group(1).startswith('http'): out.add(os.path.normpath(os.path.join(base, m.group(1))))
    for r in EDGE:
        for m in r.finditer(s): out.add(os.path.normpath(os.path.join(base, m.group(1))))
    return out


def reach(entries):
    seen, stack = set(), list(entries)
    while stack:
        p = stack.pop()
        if p in seen or not os.path.isfile(p): seen.add(p); continue
        seen.add(p)
        s = open(p, encoding='utf8', errors='replace').read()
        for r in EDGE:
            for m in r.finditer(s):
                q = os.path.normpath(os.path.join(os.path.dirname(p), m.group(1)))
                if q not in seen: stack.append(q)
    return seen


def header(p):
    s = open(p, encoding='utf8', errors='replace').read(1500)
    m = re.search(r'/\*+\s*(?:=+\s*)?(.*?)\n', s) or re.search(r'//\s*(.*?)\n', s)
    return (m.group(1) if m else '').strip()[:120]


def main():
    os.chdir(REPO)
    mods = sorted(os.path.normpath(os.path.join(r, f)) for r, _, fs in os.walk('game/js') if '/vendor' not in r
                  for f in fs if f.endswith(('.js', '.mjs')))
    game = reach(page_entries('game/index.html'))
    pages = [os.path.normpath(os.path.join(r, f)) for top in ('game', 'packages', 'tools', 'docs') for r, _, fs in os.walk(top)
             if 'node_modules' not in r and '/vendor' not in r for f in fs if f.endswith('.html') and f != 'index.html' or
             (f == 'index.html' and r != 'game')]
    other = {pg: reach(page_entries(pg)) for pg in pages}
    tests = reach({os.path.normpath(os.path.join(r, f)) for r, _, fs in os.walk('test') for f in fs if f.endswith('.mjs')})
    rows = []
    for p in mods:
        if p in game: continue
        rows.append({'module': p, 'what': header(p), 'other_pages': sorted(pg for pg, s in other.items() if p in s),
                     'tested': p in tests})
    if '--json' in sys.argv:
        print(json.dumps({'modules': len(mods), 'loaded_by_game': len(mods) - len(rows), 'unwired': rows}, indent=1)); return
    print('%d game/js modules; %d loaded by the game; %d NOT loaded by the game\n' % (len(mods), len(mods) - len(rows), len(rows)))
    for r in rows:
        print('%-44s %-6s %-70s %s' % (r['module'][8:], 'test' if r['tested'] else '', r['what'][:70], ', '.join(r['other_pages'])[:60]))


if __name__ == '__main__':
    main()

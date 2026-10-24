#!/usr/bin/env python3
"""Build game/data/t8_frame_tables.json from docs/t7t8-reference/frame-data-t8-full/*.json
(wavu.wiki, CC0-1.0). Per character, keyed by full input string (parent chain joined):
  s   startup frame (first number of iNN)
  blk on-block frame advantage   hit on-hit   ch on-counter-hit (null = same as hit)
  ko  hit/ch is a knockdown/launch ('a','d','c' suffix)
  brk throw break input ('1','2','1+2','1|2','none')   tgt hit level string (h/m/l/t...)
Output is additive. Runtime reads it in game/js/frame-tables.js."""
import json, glob, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'docs/t7t8-reference/frame-data-t8-full')
OUT = os.path.join(ROOT, 'game/data/t8_frame_tables.json')
num = lambda v: (lambda m: int(m.group(0)) if m else None)(re.search(r'[+-]?\d+', v or ''))
def adv(v):
    if not v: return None, False
    v = v.split('(')[0].strip().lstrip(',')
    return num(v), bool(re.search(r'\d+\s*[adc]', v)) or v.lower().startswith(('launch', 'k'))
def brk(n):
    n = n or ''
    if re.search(r'Unbreakable|Cannot throw break', n): return 'none'
    m = re.search(r'Throw break:?\s*(1\+2|1 or 2|1|2)', n)
    return (m.group(1).replace(' or ', '|')) if m else None
out = {'source': 'wavu.wiki via docs/t7t8-reference/frame-data-t8-full', 'license': 'CC0-1.0 (wavu.wiki)',
       'generator': 'tools/frame-data/build_t8_frame_tables.py', 'chars': {}}
for f in sorted(glob.glob(os.path.join(SRC, '*.json'))):
    d = json.load(open(f)); key = os.path.basename(f)[:-5].replace('-', '_')
    byid, rows = {m['id']: m for m in d['moves']}, {}
    for m in d['moves']:
        chain, p, guard = [m.get('input') or ''], m.get('parent'), 0
        while p and p in byid and guard < 12:
            chain.insert(0, byid[p].get('input') or ''); p = byid[p].get('parent'); guard += 1
        inp = ''.join(chain).strip().lstrip(',')
        b, _ = adv(m.get('block')); h, hk = adv(m.get('hit')); c, ck = adv(m.get('ch'))
        tgt = (m.get('target') or '').split(',')[-1].strip()
        row = {'s': num((m.get('startup') or '').split(',')[-1]), 'blk': b, 'hit': h, 'ch': c,
               'ko': bool(hk or ck), 'tgt': tgt or None}
        bk = brk(m.get('notes'))
        if bk or tgt.startswith('t'):
            # no note: Tekken default by button (1+3 -> 1, 2+4 -> 2, else 1+2)
            row['brk'] = bk or ('1' if inp.endswith('1+3') else '2' if inp.endswith('2+4') else '1+2')
        if inp and inp not in rows: rows[inp] = {k: v for k, v in row.items() if v not in (None, False)}
    out['chars'][key] = rows
json.dump(out, open(OUT, 'w'), separators=(',', ':'))
print(OUT, sum(len(v) for v in out['chars'].values()), 'moves', len(out['chars']), 'chars')

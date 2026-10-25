#!/usr/bin/env python3
"""Build game/data/hit_tables.json — wavu T8 active frames for the hit-contact lane.

  t8[char][input] = [active_frames, reach_m]   (wavu.wiki T8, CC0: docs/t7t8-reference/frame-data-t8-full)

Owner law: T5-T8 data first, T3 last resort. wavu gives startup "i10" (first active frame),
recovery "r19" (frames after the last active one) and total "29", so for a move started from
neutral (no parent): active = tot - (startup - 1) - recv  (Bryan 1+2: i17~18 r27 t45 -> 2, its
i17~18 range). A string continuation's tot counts from the string's first press, so it only gets
an active count from an explicit "iA~B" range (B - A + 1). Counts outside 1..12 are dropped
(holds, multi-hit totals). reach = wavu's range field when present (metres, T8).

Usage: python3 tools/hit-contact/build_hit_tables.py      (rewrites game/data/hit_tables.json)
Runtime: game/js/hit-tables.js (t8ActiveOf), read by fighter.js getRealMove.
"""
import json, glob, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
T8 = os.path.join(ROOT, 'docs/t7t8-reference/frame-data-t8-full')
OUT = os.path.join(ROOT, 'game/data/hit_tables.json')


def num(v):
    m = re.search(r'\d+', v or '')
    return int(m.group(0)) if m else None


def active_of(m):
    st = (m.get('startup') or '').split(',')[-1]
    rng = re.search(r'i(\d+)\s*~\s*(\d+)', st)
    s, r, t = num(st), num(m.get('recv')), num(m.get('tot'))
    if not m.get('parent') and s and r is not None and t:
        a = t - (s - 1) - r
        if 1 <= a <= 12:
            return a
    if rng:
        a = int(rng.group(2)) - int(rng.group(1)) + 1
        if 1 <= a <= 6:
            return a
    return None


def main():
    out = {'source': 'wavu.wiki T8 frame data (CC0-1.0) via docs/t7t8-reference/frame-data-t8-full',
           'generator': 'tools/hit-contact/build_hit_tables.py', 'fields': {'t8': '[active_frames, reach_m]'},
           't8': {}}
    n = 0
    for f in sorted(glob.glob(os.path.join(T8, '*.json'))):
        d = json.load(open(f))
        key = os.path.basename(f)[:-5].replace('-', '_')
        byid = {m['id']: m for m in d['moves']}
        rows = {}
        for m in d['moves']:
            chain, p, guard = [m.get('input') or ''], m.get('parent'), 0
            while p and p in byid and guard < 12:
                chain.insert(0, byid[p].get('input') or ''); p = byid[p].get('parent'); guard += 1
            inp = ''.join(chain).replace('​', '').strip().lstrip(',')
            a = active_of(m)
            try:
                reach = float(m['reach']) if m.get('reach') else None
            except ValueError:
                reach = None
            if inp and (a or reach) and inp not in rows:
                rows[inp] = [a, reach]
                n += 1
        out['t8'][key] = rows
    json.dump(out, open(OUT, 'w'), separators=(',', ':'))
    print(OUT, n, 'moves', len(out['t8']), 'chars')


if __name__ == '__main__':
    main()

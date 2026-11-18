#!/usr/bin/env python3
"""Gate: diff this lane's joins vs the shipped joins (WH PR #1557)."""
import json, os, sys

MINE = os.path.expanduser('~/workspace/_fill3-ttt2-20261106/work/joins')
SHIP = os.path.expanduser('~/workspace/_ttt2-motion-20261103/join-cont/out')

for name, mine_fn, ship_fn in (('roger', 'roger-join.json', 'roger-join.json'),
                               ('jun', 'jun_kazama-join.json', 'jun-join.json'),
                               ('unknown', 'unknown-join.json', 'unknown-join.json')):
    mine = json.load(open(os.path.join(MINE, mine_fn)))
    ship = json.load(open(os.path.join(SHIP, ship_fn)))
    m = {r['i']: r for r in mine['records']}
    s = {r['i']: r for r in ship['records']}
    only_m = sorted(set(m) - set(s))
    only_s = sorted(set(s) - set(m))
    diff = [i for i in sorted(set(m) & set(s))
            if (m[i]['name'], m[i]['anim'], m[i]['ref']) != (s[i]['name'], s[i]['anim'], s[i]['ref'])]
    print(f"{name}: mine={len(m)} shipped={len(s)} only_mine={len(only_m)} only_shipped={len(only_s)} field_diffs={len(diff)}")
    for i in only_s[:10]:
        print('  shipped-only i=%s: %s' % (i, s[i]))
    for i in only_m[:10]:
        print('  mine-only    i=%s: %s' % (i, m[i]))
    for i in diff[:10]:
        print('  diff i=%s: mine=%s shipped=%s' % (i, m[i], s[i]))

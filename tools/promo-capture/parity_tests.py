#!/usr/bin/env python3
"""parity_tests.py: build the Pantera-vs-King-T7 parity test list from King's moves pack (no hand list).
Every distinct neutral input of a damaging pack move (single inputs + 2-3 step strings whose every prefix has exactly
one pack move), with the expected clip + T7 damage + motbin move per hit. Stance-prefixed rows (BT/FC/SS/WS) and
throws (1+3 / 2+4) are left out (they need a set-up state / take the throw path).
usage: python3 tools/promo-capture/parity_tests.py game/assets/anim/t7/king/moves.pack.json > parity-tests.json"""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'anim'))
from t7_pack_graph_fill import norm_input, norm_string  # noqa: E402
STEP = re.compile(r'^(?:(d/f|d/b|u/f|u/b|f|b|d|u)\+)?([1-4](?:\+[1-4])*)$')
p = json.load(open(sys.argv[1]))
by_in, by_str = {}, {}
for k, m in p['moves'].items():
    ni, ns = norm_input(m['input']), norm_string(m['input'])
    if ni: by_in.setdefault(ni, []).append(k)
    if ns: by_str.setdefault(ns, []).append(k)
tests = []
for ni, ks in sorted(by_in.items()):
    m = p['moves'][ks[0]]
    if not (m.get('damage') or 0) > 0 or ni in ('1+3', '2+4') or not STEP.match(ni): continue
    tests.append({'input': ni, 'steps': [ni], 'expect': [[m['clip'], m['damage'], m['motbin_move']]]})
for ns, ks in sorted(by_str.items()):
    st = ns.split(',')
    if len(ks) > 1 or len(st) > 3 or not all(STEP.match(x) for x in st): continue
    exp = []
    for i in range(len(st)):
        cand = by_in.get(st[0]) if i == 0 else by_str.get(','.join(st[:i + 1]))
        if not cand or (i and len(cand) != 1): exp = None; break
        m = p['moves'][cand[0]]; exp.append([m['clip'], m.get('damage'), m['motbin_move']])
    if exp: tests.append({'input': ns, 'steps': st, 'expect': exp})
json.dump(tests, sys.stdout)

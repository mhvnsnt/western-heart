#!/usr/bin/env python3
"""parity_tests.py: build the Pantera-vs-King-T7 parity test list from King's moves pack (no hand list).
Every distinct damaging pack input: neutral singles + 2-3 step strings whose every prefix has exactly
one pack move, and stance-prefixed rows (BT/FC/SS/WS) with a `setup` field so the harness can enter
that state first. Throws (1+3 / 2+4) stay out (they take the throw path).
usage: python3 tools/promo-capture/parity_tests.py game/assets/anim/t7/king/moves.pack.json > parity-tests.json"""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'anim'))
from t7_pack_graph_fill import norm_input, norm_string  # noqa: E402
STEP = re.compile(r'^(?:(d/f|d/b|u/f|u/b|f|b|d|u)\+)?([1-4](?:\+[1-4])*)$')
STANCE = re.compile(r'^(bt|fc|ss|ws)\.(.+)$', re.I)
p = json.load(open(sys.argv[1]))
by_in, by_str = {}, {}
stance_by = {}  # canonical 'BT.1' / 'WS.2,2' -> pack key
for k, m in p['moves'].items():
    ni, ns = norm_input(m['input']), norm_string(m['input'])
    if ni: by_in.setdefault(ni, []).append(k)
    if ns: by_str.setdefault(ns, []).append(k)
    raw = re.sub(r'\s+', '', str(m.get('input') or ''))
    sm = STANCE.match(raw)
    if not sm: continue
    setup = sm.group(1).upper()
    steps = []
    ok = True
    for part in sm.group(2).split(','):
        n = norm_input(part)
        if not n or not STEP.match(n):
            ok = False
            break
        steps.append(n)
    if ok and steps:
        stance_by.setdefault(f"{setup}.{','.join(steps)}", []).append(k)
tests = []
for ni, ks in sorted(by_in.items()):
    m = p['moves'][ks[0]]
    if not (m.get('damage') or 0) > 0 or ni in ('1+3', '2+4') or not STEP.match(ni): continue
    tests.append({'input': ni, 'setup': None, 'steps': [ni], 'expect': [[m['clip'], m['damage'], m['motbin_move']]]})
for ns, ks in sorted(by_str.items()):
    st = ns.split(',')
    if len(ks) > 1 or len(st) > 3 or not all(STEP.match(x) for x in st): continue
    exp = []
    for i in range(len(st)):
        cand = by_in.get(st[0]) if i == 0 else by_str.get(','.join(st[:i + 1]))
        if not cand or (i and len(cand) != 1): exp = None; break
        m = p['moves'][cand[0]]; exp.append([m['clip'], m.get('damage'), m['motbin_move']])
    if exp: tests.append({'input': ns, 'setup': None, 'steps': st, 'expect': exp})
for inp, ks in sorted(stance_by.items(), key=lambda kv: kv[0]):
    setup, rest = inp.split('.', 1)
    steps = rest.split(',')
    m0 = p['moves'][ks[0]]
    if not (m0.get('damage') or 0) > 0: continue
    if len(steps) == 1:
        tests.append({'input': inp, 'setup': setup, 'steps': steps, 'expect': [[m0['clip'], m0['damage'], m0['motbin_move']]]})
        continue
    if len(steps) > 3: continue
    exp = []
    for i in range(len(steps)):
        pref = f"{setup}.{','.join(steps[:i + 1])}"
        cand = stance_by.get(pref)
        if not cand:
            exp = None
            break
        # WS.2,2 and ws2,2 (etc.) are the same pack move under two keys
        triples = {(p['moves'][c]['clip'], p['moves'][c].get('damage'), p['moves'][c]['motbin_move']) for c in cand}
        if len(triples) != 1:
            exp = None
            break
        m = p['moves'][cand[0]]
        exp.append([m['clip'], m.get('damage'), m['motbin_move']])
    if exp:
        tests.append({'input': inp, 'setup': setup, 'steps': steps, 'expect': exp})
json.dump(tests, sys.stdout)

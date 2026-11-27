#!/usr/bin/env python3
"""parity_report.py <rowsDir> <parity-tests.json>: PASS when every expected King T7 clip played, no T3 clip played,
and the per-hit damage list equals the T7 damage list (each hit within 0.05)."""
import json, glob, sys
rows = {}
for f in sorted(glob.glob(sys.argv[1] + '/rows-*.jsonl')):
    for l in open(f):
        r = json.loads(l); rows[r['input']] = r
tests = json.load(open(sys.argv[2]))
out, npass = [], 0
for t in tests:
    r = rows.get(t['input'])
    if not r: out.append((t['input'], 'NOT RUN', '', '')); continue
    played = [c.replace('t7_pantera_', '').split('@')[0] for c in r['clips']]
    exp_clips = [e[0] for e in t['expect']]; exp_dmg = [e[1] for e in t['expect']]
    miss = [c for c in exp_clips if c not in played]; t3 = [c for c in played if c.startswith('t3_') and not c.startswith('t3_t7_')]  # t3_t7_* = King T7 locomotion in the T3 bank
    dmg_ok = len(r['hits']) == len(exp_dmg) and all(abs(a - b) <= 0.05 for a, b in zip(r['hits'], exp_dmg))
    ok = not miss and not t3 and dmg_ok; npass += ok
    why = [] if ok else ([f'missing clip {miss}'] if miss else []) + ([f'T3 {t3}'] if t3 else []) + ([] if dmg_ok else [f'hits {r["hits"]} vs T7 {exp_dmg}'])
    out.append((t['input'], 'PASS' if ok else 'FAIL', ' -> '.join(e[2] for e in t['expect']), '; '.join(why)))
print(f'# Pantera vs King T7 parity: {npass}/{len(tests)} PASS\n')
print('| input | result | King T7 move(s) | why |\n|---|---|---|---|')
for o in out: print('| ' + ' | '.join(o) + ' |')

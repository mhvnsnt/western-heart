#!/usr/bin/env python3
"""Promote step-plan steps whose row is proven by the fighter's own data.

Why this exists: tools/input-verify/input_coverage_probe.mjs found string
slots that fire but play no animation. Their string_step_plans steps were
recorded "unmapped" (row: null), and the engine's playability gate
(game/js/step-plan-bank.js, Path A) plays a step only when status is
'verified' with a finite row — so those steps play nothing.

Evidence rule (no guessing): a step is promoted ONLY when two independent
places in the same moveset agree on the row —
  1. the step plan's candidate_row, and
  2. the prefix move's own record (its name cites the row, e.g.
     "(T3 king r233)", or a t3_row/row field).
The row must also exist in the bound bank's rows.pack.json. A prefix whose
sources disagree is a conflict, not evidence (Pantera's f+2: the record
cites row 230 while a verified plan step plays 111 — left alone). Steps
with no candidate stay unmapped and are printed.

Adjudication vetoes (--veto prefix=row, repeatable): a step whose pairing
the repo's own strike/throw test (test/attack-anim.test.mjs, "no strike
plays a throw row") rejects is NOT promoted, however well the moveset's
own records agree — the bank's hit classification (hit_frames.json: rows
415 / 417 carry the throw flag) conflicts with the slots' strike nature,
and the engine's runtime gate rejects the pairing too. Pantera's vetoed
pairs, found by running that test against the promoted file:
  1+3,1=415, 2+4,1=417
They stay unmapped until the conflict is adjudicated. (The engine's grab
classification is deeper than any single record field, so vetoes are
taken from the test's verdict, never guessed from fields.)

Usage:
  promote_step_plans.py <moveset.json> <bank-rows.pack.json> <coverage.json> [--veto prefix=row ...] [--apply]

coverage.json is a probe report; only its TPOSE rows are considered.
Without --apply the tool only prints what it would change.
"""
import json, re, sys

def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 2
    ms_path, pack_path, cov_path = sys.argv[1:4]
    apply = '--apply' in sys.argv
    vetoes = set()
    for i, a in enumerate(sys.argv):
        if a == '--veto' and i + 1 < len(sys.argv):
            pfx, _, row = sys.argv[i + 1].rpartition('=')
            vetoes.add((pfx, int(row)))
    ms = json.load(open(ms_path))

    pack = json.load(open(pack_path))
    pack_rows = set()
    def collect(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if re.fullmatch(r'\d+', str(k)):
                    pack_rows.add(int(k))
                collect(v)
    collect(pack)

    plans = ms['string_step_plans']['plans']
    moves = ms.get('moves', {})
    slots = ms.get('slots', {})

    def move_row(key):
        m = moves.get(key) or slots.get(key) or {}
        if isinstance(m, dict):
            for f in ('t3_row', 'row'):
                if m.get(f):
                    return int(m[f])
            mm = re.search(r'\(T3 \w+ r(\d+)\)', m.get('name') or '')
            if mm:
                return int(mm.group(1))
        return None

    cov = json.load(open(cov_path))
    tpose = [(r['n'], r.get('moveKey')) for r in cov['rows'] if r['outcome'] == 'TPOSE']
    note = ('promoted 2026-11-01: row confirmed by the prefix move\'s own record '
            'in this same moveset (probe docs/movesets/PANTERA-INPUT-COVERAGE-2026-11-01.md)')
    touched = {}
    for n, mk in tpose:
        plan = plans.get(n) or (plans.get(mk) if mk else None)
        if not plan:
            print(f'{n}: no step plan — left as-is')
            continue
        for s in plan['steps']:
            if s.get('status') == 'verified' and s.get('row'):
                continue
            cand = s.get('candidate_row')
            prow = move_row(s['prefix'])
            if cand and (s['prefix'], int(cand)) in vetoes:
                print(f'{n}: step {s["prefix"]} VETOED (adjudicated strike/throw conflict, row {cand}); stays {s.get("status")}')
                continue
            if cand and prow and int(cand) == prow and int(cand) in pack_rows:
                print(f'{n}: step {s["prefix"]} {s.get("status")} -> verified row {cand}')
                if apply:
                    s['row'] = int(cand)
                    s['status'] = 'verified'
                    s.setdefault('reasons', []).append(note)
                    touched[n] = touched.get(n, 0) + 1
            else:
                print(f'{n}: step {s["prefix"]} stays {s.get("status")} (candidate={cand}, prefix record row={prow})')
    print('plans touched:', len(touched))
    if apply:
        with open(ms_path, 'w') as f:
            json.dump(ms, f, indent=1, ensure_ascii=False)
        print('wrote', ms_path)
    return 0

if __name__ == '__main__':
    sys.exit(main())

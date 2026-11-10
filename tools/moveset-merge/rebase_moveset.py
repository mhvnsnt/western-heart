#!/usr/bin/env python3
"""tools/moveset-merge/rebase_moveset.py — rebase a fighter's moveset onto its declared base, dropping other characters.

Why (2026-11-10, owner on Gyou): "Gyou isn't supposed to have hwoarang guard? Someone else has hwoarangs moves ...
gyou has someone else's moves" / "Gyou was probably Paul Phoenix and fire attacks". On 2026-10-23 the owner set it
("he can have Paul Phoenix moves mixed with like flame attacks or whatever") and a lane built exactly that file,
game/assets/movesets/gyou-spirit-body.json: Paul Phoenix's bank-derived moves plus the user-requested flame layer
(`flame_attacks`). It was never wired: the game loads <id>.json, and gyou.json stayed a MIX (declared base Paul, 133
Paul rows, but 723 Hwoarang rows (Tobi's base) and 145 Jin rows; docs/MOVESET-PATTERN-AUDIT-2026-10-24.md:
"Gyou -- NEEDS-DECISION (owner)").

The rebased file is the BASE file (here the Paul + flame moveset) with, carried over from the OLD file:
  * every move whose own source names the kept character (--keep, matched on merge_source / t7_source / source /
    t3_source, case-insensitive), added fill-only (a key or input slot the base already has is never replaced);
  * the fighter's OWN signature rows (name contains --own-mark, default '[WH SIGNATURE]': Gyou's Cannot Stop and
    Everywhere Already carry no source key), with priority: a base move they displace stays in the file under
    '<key>~base' (unslotted), so nothing is lost;
  * the fighter's own canon (canon_moves / canon_wiring) and the kept character's motbin block (t7_motbin) when it
    names that character;
  * stance_after / hit_words entries only for moves that exist in the result.
Everything else in the OLD file (other characters' rows, their specials, their stance transitions) is dropped and
counted in the `rebase` provenance block. The OLD file is archived byte-for-byte first (--archive).

    python3 tools/moveset-merge/rebase_moveset.py --old game/assets/movesets/gyou.json \\
        --base game/assets/movesets/gyou-spirit-body.json --keep paul --fighter gyou --display GYOU \\
        --archive docs/archive/movesets/gyou-pre-paul-rebase-2026-11-10.json --out game/assets/movesets/gyou.json
"""
import argparse
import collections
import copy
import json
import os
import shutil
import sys

SRC_KEYS = ('merge_source', 't7_source', 'source', 't3_source')


def move_source(m):
    for k in SRC_KEYS:
        v = m.get(k)
        if v:
            return str(v)
    return ''


def family(src):
    s = src.lower()
    if ':' in s:
        parts = s.split(':')
        who = parts[1] if len(parts) > 1 else parts[0]
        return parts[0] + ':' + who.split('_')[0].split('-')[0]
    return s


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--old', required=True)
    ap.add_argument('--base', required=True)
    ap.add_argument('--keep', required=True, help='character whose rows in OLD are carried over (e.g. paul)')
    ap.add_argument('--fighter', required=True)
    ap.add_argument('--display', required=True)
    ap.add_argument('--archive', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--owner-quote', action='append', default=[])
    ap.add_argument('--own-mark', default='[WH SIGNATURE]')
    a = ap.parse_args()
    keep = a.keep.lower()
    old = json.load(open(a.old))
    base = json.load(open(a.base))
    os.makedirs(os.path.dirname(a.archive), exist_ok=True)
    shutil.copyfile(a.old, a.archive)

    new = copy.deepcopy(base)
    new['fighter'], new['display'] = a.fighter, a.display
    moves, slots = new.setdefault('moves', {}), new.setdefault('slots', {})
    carried, dropped = [], collections.Counter()
    own = []
    for k, m in (old.get('moves') or {}).items():
        src = move_source(m)
        if a.own_mark and a.own_mark in str(m.get('name') or ''):
            if k in moves:
                moves[k + '~base'] = moves[k]
            moves[k] = copy.deepcopy(m)
            slots[m.get('input') or k] = k
            own.append(k)
            continue
        if keep in src.lower():
            if k in moves:
                dropped['kept-character row already in base (key)'] += 1
                continue
            mm = copy.deepcopy(m)
            if isinstance(mm.get('name'), str) and old.get('display') and mm['name'].startswith(old['display']):
                mm['name'] = a.display + mm['name'][len(old['display']):]
            moves[k] = mm
            inp = m.get('input') or k
            if inp not in slots:
                slots[inp] = k
            carried.append(k)
        else:
            dropped[family(src) or '(no source)'] += 1
    for key in ('canon_moves', 'canon_wiring'):
        if key in old:
            new[key] = copy.deepcopy(old[key])
    tm = old.get('t7_motbin')
    if isinstance(tm, dict) and keep in str(tm.get('character_name', '')).lower():
        new['t7_motbin'] = copy.deepcopy(tm)
    for key in ('stance_after', 'hit_words'):
        merged = dict(new.get(key) or {})
        for k, v in (old.get(key) or {}).items():
            if k in moves and k not in merged:
                merged[k] = v
        if merged:
            new[key] = merged
    # a slot must point at a move that exists
    bad = [i for i, k in slots.items() if k not in moves]
    for i in bad:
        slots.pop(i)
    new['rebase'] = {
        'date': '2026-11-10', 'tool': 'tools/moveset-merge/rebase_moveset.py',
        'owner': a.owner_quote,
        'base_file': os.path.basename(a.base), 'old_file_archived_as': a.archive,
        'kept_character': keep, 'carried_from_old': len(carried), 'own_signatures_kept': own,
        'dropped_from_old_by_source': dict(dropped.most_common()),
        'slots_dropped_dangling': len(bad),
        'result_moves': len(moves), 'result_slots': len(slots),
    }
    with open(a.out, 'w') as f:
        json.dump(new, f, indent=1, ensure_ascii=False)
        f.write('\n')
    print(json.dumps(new['rebase'], indent=1))


if __name__ == '__main__':
    sys.exit(main())

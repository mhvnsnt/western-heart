#!/usr/bin/env python3
"""restore_quarantine_fields.py — make the #988 (Option B) T8 restoration keep the NEWEST move data.

The #1039 mega-batch moved 630 moves of the 8 T7 fighters into each file's `t8_quarantine_20261024`
section (verbatim copies of the live entries at that moment). #988 put them back into `moves`, but from
its own older branch data, which predates later work on main:
  - MOD damage wiring (#1000): Pantera JGS.1/2/3/4/df+4 came back at 0 damage (quarantine: 28/20/31/54/40);
  - combat systems (#1045): db+1+2,3+4 lost powerCrush + powerCrush_source;
  - Pantera strings fix (#1007): JGS.3,2+3 went back to an unblockable throw although the newer entry
    records "Fixed to T7 strike 2026-10-24 (docs/research/PANTERA-STRING-AUDIT-2026-10-24.md)";
  - input_lp labels, t3_row / t3_source fields.
#988's own contribution to those entries is the `anim_t3` mapping (the only other field it adds is a
throw_break that belongs to the reverted throw reading).

So each restored move becomes: the quarantine entry (newest data, verbatim, its key order) + #988's
`anim_t3`. Moves whose live entry already equals that are left untouched. The quarantine section itself is
never modified. Nothing is deleted.

Usage:  python3 tools/moveset-merge/restore_quarantine_fields.py [--check] [fighter ...]
        (default fighters: the 8 T7 fighters; --check reports without writing)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECTION = 't8_quarantine_20261024'
FIGHTERS = ['burger', 'demonio', 'diablo', 'kinpo', 'pantera', 'phantom', 'scimitar', 'skull']
KEEP_FROM_LIVE = ('anim_t3',)


def dump(obj, ascii_only):
    return json.dumps(obj, indent=2, ensure_ascii=ascii_only) + '\n'


def main(argv):
    check = '--check' in argv
    names = [a for a in argv if not a.startswith('--')] or FIGHTERS
    total = 0
    for name in names:
        path = ROOT / 'game' / 'assets' / 'movesets' / f'{name}.json'
        raw = path.read_text(encoding='utf-8')
        data = json.loads(raw)
        ascii_only = raw.isascii()
        if dump(data, ascii_only) != raw:
            print(f'{name}: SKIP (re-serialising does not reproduce the file byte-for-byte; refusing to rewrite)')
            continue
        quarantine = data.get(SECTION) or {}
        moves = data.get('moves') or {}
        changed = []
        for key, qv in quarantine.items():
            live = moves.get(key)
            if not isinstance(qv, dict) or not isinstance(live, dict):
                continue
            new = dict(qv)
            for fld in KEEP_FROM_LIVE:
                if fld in live:
                    new[fld] = live[fld]
            if new != live:
                lost = sorted(f for f in live if f not in new)
                moves[key] = new
                changed.append((key, lost))
        total += len(changed)
        print(f'{name}: {len(changed)} restored moves brought to the newest data' + (' (check only)' if check else ''))
        for key, lost in changed:
            print(f'    {key}' + (f'   (dropped live-only fields: {", ".join(lost)})' if lost else ''))
        if changed and not check:
            path.write_text(dump(data, ascii_only), encoding='utf-8')
    print(f'TOTAL {total}')


if __name__ == '__main__':
    main(sys.argv[1:])

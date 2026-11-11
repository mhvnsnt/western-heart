#!/usr/bin/env python3
"""tools/moveset-merge/t7_throw_slot_fix.py: give an input back to its base's own real T7 strike, where the slot table
fires a throw that has no clip of its own.

Why (2026-11-11, seen in the game by eye): Gyou's f+2 slot fires the T8 row 'Phoenix Hook, Tiger Claw' (hit level
'h,t', a hit-throw). merge_sources ranks a T8 base row above a T7 base row ("signature > T8 base > T7 base > ..."),
so the T8 row won the slot. For a strike that order is harmless: the game plays the T7 move pack's clip through its
input fallback (t3anims.js t7MoveClip) and only the frame data comes from the T8 row. A throw never takes a strike
clip (fighter.js: "a throw keeps the throw path"), and a T8 throw has no clip. So the game showed a Tekken 3 throw
stand-in ('match': Paul's T3 throw attempt, a 3.3 m running leap) instead of Paul's f+2. Meanwhile Paul's own T7 f+2
row ('f+2~t7.paul', exact T7 frame data) has its real clip in the pack. Owner standing order: work from the top-level
sources (T7/T5), judged by eye.

Rule: a slot is re-pointed ONLY when all of these hold:
  * its row is a throw or hit-throw (isGrab / throw / move_class 'throw' / last hit level 't') from T8
    (merge_source 't8:...');
  * the fighter's T7 move pack (T7_MOVES in game/js/t3anims.js) maps that same input to a row of the same moveset;
  * that pack row is a strike: the pack never holds throws.
The slot then fires the pack row. The T8 row stays in the file under its own key; nothing is removed. Only the
file is written back in its own byte layout, so the diff is only the changed slot lines plus a 't7_throw_slot_fix'
block that records each change.

    python3 tools/moveset-merge/t7_throw_slot_fix.py                 # report every T7-pack fighter; exit 1 if any
    python3 tools/moveset-merge/t7_throw_slot_fix.py --only gyou --write
"""
import argparse
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def t7_moves_table():
    s = open(os.path.join(REPO, 'game/js/t3anims.js'), encoding='utf-8').read()
    body = re.search(r'export const T7_MOVES = \{([\s\S]*?)\n\};', s).group(1)
    return {fid: (d, pk or 'moves.pack.json') for fid, d, pk in
            re.findall(r"^\s+([a-z0-9_-]+): \{ bank: '[a-z0-9_]+', dir: '([^']+)'(?:, pack: '([^']+)')? \}", body, re.M)}


def is_t8_throw(m):
    lvl = str(m.get('hit_level') or '').split(',')[-1].strip().lower()
    grab = m.get('isGrab') or m.get('throw') or m.get('move_class') == 'throw' or lvl.startswith('t')
    return bool(grab) and str(m.get('merge_source') or '').startswith('t8:')


def findings(fid, pack_path):
    msf = os.path.join(REPO, 'game/assets/movesets/%s.json' % fid)
    if not os.path.exists(msf) or not os.path.exists(pack_path):
        return None, []
    raw = open(msf, encoding='utf-8').read()
    ms = json.loads(raw)
    pack = json.load(open(pack_path, encoding='utf-8'))
    by_input = {}
    for k, v in pack['moves'].items():
        by_input.setdefault(v.get('input'), k)
    out = []
    for n, k in (ms.get('slots') or {}).items():
        m = ms['moves'].get(k) or {}
        t7 = by_input.get(n)
        if not t7 or t7 == k or t7 not in ms['moves'] or not is_t8_throw(m):
            continue
        out.append({'slot': n, 'from': k, 'from_name': m.get('name'), 'from_hit_level': m.get('hit_level'),
                    'to': t7, 'to_motbin': pack['moves'][t7].get('motbin_move'), 'to_clip': pack['moves'][t7].get('clip')})
    return (msf, raw, ms), out


def same_format(data, raw):
    """(indent, ensure_ascii, trailing) that reproduce the file byte for byte, so a rewrite keeps its layout."""
    for ind in (2, 1, 4):
        for ea in (True, False):
            for nl in ('\n', ''):
                if json.dumps(data, indent=ind, ensure_ascii=ea) + nl == raw:
                    return ind, ea, nl
    raise SystemExit('cannot reproduce the file layout byte for byte; refusing to rewrite it')


def rewrite(msf, raw, ms, changes, note):
    """Re-point the slots and append a provenance block, written back in the file's own layout (the diff is only
    the changed slot lines and the new block)."""
    ind, ea, nl = same_format(ms, raw)
    if 't7_throw_slot_fix' in ms:
        raise SystemExit('%s already has a t7_throw_slot_fix block; extend this tool before running it twice' % msf)
    for c in changes:
        assert ms['slots'][c['slot']] == c['from']
        ms['slots'][c['slot']] = c['to']
    ms['t7_throw_slot_fix'] = {'date': '2026-11-11', 'tool': 'tools/moveset-merge/t7_throw_slot_fix.py', 'why': note,
                               'reslotted': changes}
    open(msf, 'w', encoding='utf-8').write(json.dumps(ms, indent=ind, ensure_ascii=ea) + nl)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--only', default='')
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args()
    only = {x for x in a.only.split(',') if x}
    note = ('a T8 throw/hit-throw held this input but has no clip (the game showed a T3 throw stand-in); the '
            "fighter's own T7 strike on the same input has its real clip in the T7 move pack")
    total = 0
    for fid, (d, pk) in sorted(t7_moves_table().items()):
        if only and fid not in only:
            continue
        ctx, out = findings(fid, os.path.join(REPO, 'game', d, pk))
        for c in out:
            total += 1
            print('%-12s slot %-10s %s (%s, %s) -> %s (%s, %s)' % (fid, c['slot'], c['from'], c['from_name'],
                  c['from_hit_level'], c['to'], c['to_motbin'], c['to_clip']))
        if out and a.write:
            rewrite(*ctx, out, note)
            print('  wrote', os.path.relpath(ctx[0], REPO))
    if not a.write and total:
        sys.exit(1)


if __name__ == '__main__':
    main()

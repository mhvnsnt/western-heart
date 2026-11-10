#!/usr/bin/env python3
"""t7_generic_slots.py: resolve each Tekken 7 base's OWN generic-action moves (walk / dash / crouch / jump / sidestep /
block / hit / KO, plus its 1 / 3 / 4 attacks) from its motbin, for tools/anim/t7_generic_bank_bake.py --slots.

Why (2026-11-10, owner: "negativo should have only had t7 data from negan"): the T7-stance fighters still play walk,
block, hit and KO from Tekken 3 banks. t7_generic_bank_bake.py bakes those slots from the base's own T7 clips, but its
fixed name templates ('<P>_sWALKF', ...) miss bases whose moves are named differently (Negan walks with the shared
'sWALK_00F'; King has no 'Kg_sWALKB'). Read-only; nothing is guessed:

  * walk / dash / crouch / jump / sidestep: the base's neutral stance (<P>_sKAM00_) cancel list, group cancels expanded
    (t7_move_resolve.Motbin), entries with NO button: direction f 0x40 / b 0x10 -> walks, d 0x4 -> stand-to-crouch,
    u 0x100 / u/f 0x200 / u/b 0x80 -> jumps, special 0x8001 / 0x8002 -> dash / backdash, 0x8003 / 0x8004 ->
    sidesteps. Several entries per direction are requirement-gated variants (turn-arounds, rage, side): the
    unconditional one (requirements index 0) wins, then the first in priority order whose name is the engine's state
    family for that slot (sWALK / sDASH / st2cr / sJUMP / sSTEP).
  * block / hit / launched / KO / crouch-hold: the engine's shared state names (sGrd_YC00G, sDm_Aokimid00,
    sDw_AIR00_, Fall_sKAM, cKAM__00_), else the base's own state of that family.
  * light / medium / heavy / grab: the moves the fighter's REAL T7 move pack already maps to inputs 1 / 3 / 4 by exact
    frame data (game/assets/anim/t7/<dir>/moves*.pack.json, tools/anim/t7_move_resolve.py), so the bank's attack
    slots are the same moves the game already plays for those buttons.

    python3 tools/anim/t7_generic_slots.py <GRE>/teardown/tekken7-steam/tkdata/mothead <code> [<pack.json>] > slots.json

Resolved plans for the 13 T7-stance bases are committed in tools/anim/t7_generic_slots/<code>.json (2026-11-10):
kin hei bry bob xia yos hwo kum pan jul lee lar nsa, 16-19 slots each (hei: no plain '4' row in his pack; bob: no
move pack yet, so his 1/3/4 slots stay on his bound bank). kum/pan have no sGrd_YC00G; their block falls back to their
own first sGrd_ state (sGrd_AokihR18) -- judge it by eye before wiring. Bake each with
    T7_EXE=<exe> python3 tools/anim/t7_generic_bank_bake.py --code <code> --slots tools/anim/t7_generic_slots/<code>.json \
        --fighter <id> --character '<name> (Tekken 7)' --mothead <GRE>/.../mothead --mannequin <blend> --helper <py> \
        --blender <blender> --out-dir game/assets/anim/t3/<bank>/
Hands: each base's motbin also carries a hand block (Negan: MOTA block 1, 113 clips, 0x64, 19 bones = one T7 hand:
FingerBase/Middle/Ring/Pinky roots + 3 joints x 5 fingers) and a face block (block 2, 43 clips, 116 bones). The game's
clips carry 21 body joints only, which is why every fighter's hands stay flat.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t7_move_resolve import Motbin  # noqa: E402

DIR_SLOTS = [('t3_walk_fwd', 0x40, r'sWALK'), ('t3_walk_back', 0x10, r'sWALK'), ('t3_crouch', 0x4, r'st2cr'),
             ('t3_jump_up', 0x100, r'sJUMP'), ('t3_jump_fwd', 0x200, r'sJUMP'), ('t3_jump_back', 0x80, r'sJUMP'),
             ('t3_dash_fwd', 0x8001, r'sDASH'), ('t3_backdash', 0x8002, r'sDASH'),
             ('t3_sidestep_a', 0x8003, r'sSTEP'), ('t3_sidestep_b', 0x8004, r'sSTEP')]
STATE_SLOTS = [('t3_block', 'sGrd_YC00G', r'^(\w+_)?sGrd_'), ('t3_hit', 'sDm_Aokimid00', r'^(\w+_)?sDm_'),
               ('t3_hit_launch', 'sDw_AIR00_', r'^(\w+_)?sDw_AIR'), ('t3_ko', 'Fall_sKAM', r'^(\w+_)?Fall_s'),
               ('t3_crouch_hold', 'cKAM__00_', r'^(\w+_)?cKAM')]
INPUT_SLOTS = [('t3_light', '1'), ('t3_medium', '3'), ('t3_heavy', '4')]


def resolve(mothead, code, pack=None):
    mb = Motbin(mothead, code)
    st = mb.stance()
    by_name = {m['name']: m for m in mb.moves}
    cancels = [(d, b & 0xFF, mid, req) for d, b, mid, req in mb.expanded_cancels(st) if mid < len(mb.moves)]
    out = {'code': code, 'stance': st['name'], 'slots': {}, 'unresolved': []}

    def put(slot, name, how):
        m = by_name[name]
        c = mb.clip(m)
        out['slots'][slot] = {'move': name, 'anim': m['anim'], 'how': how, 'bank': c['bank'], 'clip': c['clip'],
                              'fmt': c['fmt']}

    out['slots']['t3_neutral'] = None
    put('t3_neutral', st['name'], 'stance')
    for slot, d, fam in DIR_SLOTS:
        cand = [(req, mb.moves[mid]['name']) for dd, btn, mid, req in cancels if dd == d and btn == 0]
        pick = next((n for r, n in cand if r == 0 and re.search(fam, n)), None) or \
            next((n for r, n in cand if re.search(fam, n)), None)
        if slot in ('t3_sidestep_a', 't3_sidestep_b'):  # L / R by name, whichever command carries them
            want = 'L' if slot.endswith('_a') else 'R'
            allss = [n for dd, btn, mid, req in cancels for n in [mb.moves[mid]['name']]
                     if dd in (0x8003, 0x8004) and btn == 0 and re.search(r'sSTEP.*' + want + r'$', n)]
            pick = allss[0] if allss else pick
        if pick:
            put(slot, pick, 'stance cancel %s' % hex(d))
        else:
            out['unresolved'].append(slot)
    for slot, name, fam in STATE_SLOTS:
        if name in by_name:
            put(slot, name, 'engine state')
            continue
        alt = [m['name'] for m in mb.moves if re.search(fam, m['name'])]
        if alt:
            put(slot, alt[0], 'own state family %s' % fam)
        else:
            out['unresolved'].append(slot)
    if pack:
        pk = json.load(open(pack))
        by_input = {}
        for key, mv in (pk.get('moves') or {}).items():
            inp = str(mv.get('input') or '').strip()
            name = mv.get('motbin_move')
            if name and inp and inp not in by_input:
                by_input[inp] = name
        for slot, inp in INPUT_SLOTS:
            name = by_input.get(inp)
            if name in by_name:
                put(slot, name, 'move pack input %s' % inp)
            else:
                out['unresolved'].append(slot)
    return out


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    json.dump(resolve(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None), sys.stdout, indent=1)
    print()

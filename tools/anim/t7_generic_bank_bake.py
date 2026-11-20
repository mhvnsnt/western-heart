#!/usr/bin/env python3
"""t7_generic_bank_bake.py: bake a Tekken 7 character's OWN generic-action clips into a wh-anim/1 bank dir
(game/assets/anim/t3/<bank>/), one tools/anim/t7_c8_stance_bake.py run per T3_CLIP_DEFS slot.

Why this exists (2026-11-03, SmutBase T7 bank production): fighters whose base debuted after Tekken 3
(Pond <- the T7 'frv' source set, Ryusan <- the T7 'dnc' source set) had no bank at all — fighter.js
bankIdFor returned null, _bindT3 returned early, and neither their T7 stance nor their T7 move pack
could ever load. docs/anim/RAVEN-ANIM-GAP-20261023.md sets the doctrine: a fighter is never animated
with another character's clips, so the bank is built from the character's OWN T7 motbin state moves,
decoded through the same proven path as the move packs (0x64 clips converted by the game's own sampler
via tools/anim/t7_anim64_to_c8.py when T7_EXE is set; Blender + TekkenMannequin + TekkenAnimHelper).

Slot -> motbin move basis (the engine's own state names in the character's motbin table; the stance
move's cancel list wires the same targets — e.g. direction 0x40 from Nj_sKAM00_ -> Nj_sWALKF,
0x8001 -> Nj_sDASHF, both printed by tools/anim/t7_move_resolve.py's Motbin class):
  t3_neutral     the character's kamae move (<code> stance, *_sKAM00_)
  t3_light       the character's own '1' move      t3_medium  the character's own '3' move
  t3_heavy       the character's own '4' move      t3_grab    the stance-wired B2 throw (Thrmv_B2_00;
                 the 'dnc' table names the same move Thrmv_B2_00i — same Tco_ntukami anim — pass --grab)
  t3_block       sGrd_YC00G (standing guard state) t3_hit     sDm_Aokimid00 (standing mid damage)
  t3_hit_launch  sDw_AIR00_ (airborne down state)  t3_ko      Fall_sKAM (fall from kamae to down)
  t3_walk_fwd    <P>_sWALKF   t3_walk_back <P>_sWALKB   t3_dash_fwd <P>_sDASHF   t3_backdash <P>_sDASHB
  t3_crouch      the character's stand-to-crouch move (*_st2cr*)   t3_crouch_hold cKAM__00_ (crouch kamae)
  t3_jump_up     sJUMP_00_    t3_jump_fwd  sJUMP_00F   t3_jump_back sJUMP_00B (the motbin points all
                 three at the same clip — that is the game's own assignment, baked as-is)
  t3_sidestep_a  sSTEP_01L    t3_sidestep_b sSTEP_01R
NOT baked: t3_stance (intro, SHOW) and t3_win_rp (win, SHOW) — no body-clip candidate exists in either
motbin table (the only WIN-named entry is a facial animation); the loader tolerates the missing files
and the gap is logged in the lane handoff, per the SHOW-ANIMATION LOCK.

usage: T7_EXE=<exe> python3 tools/anim/t7_generic_bank_bake.py --code frv --fighter pond --prefix Nj \
         --stance Nj_sKAM00_ --basic1 Nj_lp002 --basic3 Nj_lk00 --basic4 Nj_rk00 --crouch Nj_st2cr00_ \
         --character 'T7 source set frv (frv.json)' --mothead <GRE>/teardown/tekken7-steam/tkdata/mothead \
         --mannequin TekkenMannequin_no_ik.blend --helper TekkenAnimHelper.py --blender blender \
         --out-dir game/assets/anim/t3/raven
Re-running is safe: slots whose file already exists in --out-dir are skipped.
"""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from t7_move_resolve import Motbin  # noqa: E402

SLOTS = {
    't3_neutral': '{stance}', 't3_light': '{basic1}', 't3_medium': '{basic3}', 't3_heavy': '{basic4}',
    't3_grab': '{grab}', 't3_block': 'sGrd_YC00G', 't3_hit': 'sDm_Aokimid00',
    't3_hit_launch': 'sDw_AIR00_', 't3_ko': 'Fall_sKAM',
    't3_walk_fwd': '{P}_sWALKF', 't3_walk_back': '{P}_sWALKB', 't3_dash_fwd': '{P}_sDASHF',
    't3_backdash': '{P}_sDASHB', 't3_crouch': '{crouch}', 't3_crouch_hold': 'cKAM__00_',
    't3_jump_up': 'sJUMP_00_', 't3_jump_fwd': 'sJUMP_00F', 't3_jump_back': 'sJUMP_00B',
    't3_sidestep_a': 'sSTEP_01L', 't3_sidestep_b': 'sSTEP_01R',
}
ARC = {'rotsm': 'mask/{code}rotsm.arc', 'motbin': 'bin/{code}mot.bin', 'common': 'mask/common.arc'}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for a in ('--code', '--fighter', '--character', '--mothead', '--mannequin', '--helper', '--blender', '--out-dir'):
        ap.add_argument(a, required=True)
    # Name templates (the 2026-11-03 path), or --slots: a tools/anim/t7_generic_slots.py JSON that names each slot's
    # move from the base's own stance cancel table (2026-11-10: Negan walks with the shared sWALK_00F, King has no
    # Kg_sWALKB, so the templates miss them).
    for a in ('--prefix', '--stance', '--basic1', '--basic3', '--basic4', '--crouch'):
        ap.add_argument(a)
    ap.add_argument('--grab', default='Thrmv_B2_00')
    ap.add_argument('--slots', help='slot -> move JSON from tools/anim/t7_generic_slots.py (replaces the templates)')
    a = ap.parse_args()
    mb = Motbin(a.mothead, a.code)
    by_name = {m['name']: m for m in mb.moves}
    os.makedirs(a.out_dir, exist_ok=True)
    if a.slots:
        plan = {slot: (v or {}).get('move') for slot, v in json.load(open(a.slots))['slots'].items()}
    else:
        missing = [o for o in ('prefix', 'stance', 'basic1', 'basic3', 'basic4', 'crouch') if getattr(a, o) is None]
        if missing:
            ap.error('without --slots these are required: ' + ', '.join('--' + m for m in missing))
        fmt = dict(P=a.prefix, stance=a.stance, basic1=a.basic1, basic3=a.basic3, basic4=a.basic4, crouch=a.crouch,
                   grab=a.grab)
        plan = {slot: tmpl.format(**fmt) for slot, tmpl in SLOTS.items()}
    for slot, name in plan.items():
        m = by_name.get(name)
        if m is None:
            print('SKIP %s: move %s not in %s motbin' % (slot, name, a.code)); continue
        c = mb.clip(m)
        if c['fmt'] not in ('0x64', '0xC8'):
            print('SKIP %s: %s fmt %s' % (slot, name, c['fmt'])); continue
        out = os.path.join(a.out_dir, slot + '.json')
        if os.path.exists(out):
            print('EXISTS %s' % slot); continue
        arc = os.path.join(a.mothead, ARC[c['bank']].format(code=a.code))
        cmd = [sys.executable, os.path.join(HERE, 't7_c8_stance_bake.py'),
               '--arc', arc, '--clip', str(c['clip']), '--anim', m['anim'], '--moves', name,
               '--character', a.character, '--fighter', a.fighter,
               '--mannequin', a.mannequin, '--helper', a.helper, '--blender', a.blender,
               '--out-dir', a.out_dir, '--name', slot]
        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode:
            sys.exit('FAIL %s (%s %s#%s):\n%s\n%s' % (slot, name, c['bank'], c['clip'], p.stdout[-800:], p.stderr[-800:]))
        print('OK %s: %s -> %s [%s#%s %s] %s' % (slot, name, m['anim'], c['bank'], c['clip'], c['fmt'], p.stdout.strip()))
    print('BANK_BAKE_DONE', a.code, a.out_dir)


if __name__ == '__main__':
    main()

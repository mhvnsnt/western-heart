#!/usr/bin/env python3
"""t7_move_bake.py: bake a fighter's REAL Tekken 7 per-move clips (the rows tools/anim/t7_move_resolve.py mapped
exactly) into one pack the game loads: game/assets/anim/t7/<base>/moves.pack.json.

Each clip goes through tools/anim/t7_c8_stance_bake.py, the same community 0xC8 path as the stances
(Kiloutre's applyRotationFromAnimdata on Koenji's TekkenMannequin, FK self-check). 0xC8 clips bake directly; 0x64
clips (every attack) bake too when T7_EXE points at TekkenGame-Win64-Shipping.exe: tools/anim/t7_anim64_to_c8.py turns
them into 0xC8 values with the game's own sampler (docs/anim/T7-0x64-FRAME-RESEARCH-2026-10-30.md).

Kept out on purpose (they keep their current animation):
  - rows whose T7 hit level lists more than one hit: the second hit can live in a follow-up motbin move, so one
    clip could show only half the move;
  - throws (moveset isGrab / throw, or a T7 throw hit level): throws have their own pair animation path.
Each clip carries root_motion_fwd_m (forward travel per frame from the raw T7 root channel, metres).
Every clip is tagged FIGHT (SHOW-ANIMATION LOCK, docs/anim/NEGAN-ANIM-GAP-20261023.md): these are the moves' own
animations, never win/intro/taunt clips.

usage: python3 tools/anim/t7_move_bake.py --resolve resolve.json --mothead <GRE>/.../tkdata/mothead --code nsa \\
         --moveset game/assets/movesets/negativo.json --fighter negativo --character 'Negan (Tekken 7)' \\
         --mannequin TekkenMannequin_no_ik.blend --helper TekkenAnimHelper.py --blender blender \\
         --out-dir game/assets/anim/t7/negan
"""
import argparse, hashlib, json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import t7_c8_stance_bake as B  # noqa: E402  (decode_c8: raw 0xC8 frames)


def safe(name):
    return re.sub(r'[^A-Za-z0-9_]+', '_', name).strip('_')


def main():
    ap = argparse.ArgumentParser()
    for a in ('--resolve', '--mothead', '--code', '--moveset', '--fighter', '--character', '--mannequin', '--helper',
              '--blender', '--out-dir'):
        ap.add_argument(a, required=True)
    args = ap.parse_args()
    res = json.load(open(args.resolve))
    moveset = json.load(open(args.moveset))['moves']
    G = args.mothead.rstrip('/') + '/'
    keep, skipped = {}, {}
    for key, r in res['rows'].items():
        if r.get('status') != 'mapped': continue
        row = moveset.get(key) or {}
        if r.get('fmt') != '0xC8' and not (r.get('fmt') == '0x64' and os.environ.get('T7_EXE')):
            skipped[key] = 'clip is %s (0x64 needs T7_EXE for the game-sampler conversion)' % r.get('fmt'); continue
        levels = [x for x in str(row.get('t7_hit_level') or '').split(',') if x.strip()]
        if len(levels) > 1: skipped[key] = 'multi-hit (%s): one clip could show only the first hit' % row.get('t7_hit_level'); continue
        if row.get('isGrab') or row.get('throw') or re.match(r'\s*t', str(row.get('t7_hit_level') or ''), re.I):
            skipped[key] = 'throw: own pair-animation path'; continue
        keep[key] = r
    clips, moves = {}, {}
    with tempfile.TemporaryDirectory() as td:
        for key, r in keep.items():
            cname = safe(r['anim'])
            if cname not in clips:
                arc = G + r['file']
                cmd = [sys.executable, os.path.join(HERE, 't7_c8_stance_bake.py'), '--arc', arc, '--clip', str(r['clip']),
                       '--anim', r['anim'], '--moves', r['motbin_move'], '--character', args.character, '--fighter', args.fighter,
                       '--mannequin', args.mannequin, '--helper', args.helper, '--blender', args.blender,
                       '--out-dir', td, '--name', cname]
                p = subprocess.run(cmd, capture_output=True, text=True)
                if p.returncode: raise SystemExit('bake failed for %s (%s):\n%s' % (key, r['anim'], p.stderr[-2000:]))
                data = json.load(open(os.path.join(td, cname + '.json')))
                if not (data.get('fk_selfcheck_max_m', 1) <= 1e-5): raise SystemExit('%s: FK self-check %r' % (cname, data.get('fk_selfcheck_max_m')))
                data['loop'] = False
                data['anim_set'] = 'FIGHT'
                # Root motion from the RAW T7 root channel (slot 0, mm; forward = +z in both clip formats: King's
                # 0x64 jab root z 21 -> 555 -> 458 mm). The applier's posed hips track (root_t) carries this travel
                # 90 deg off the body's facing (T7 z lands on glTF x), so the game must not read travel from
                # root_t for these clips. Lateral travel is left at 0 until its sign is proven on a sidestep clip.
                raw = B.decode_c8(arc, r['clip'])
                z0 = raw[0][2]
                data['root_motion_fwd_m'] = [round((f[2] - z0) / 1000.0, 5) for f in raw]
                if len(data['root_motion_fwd_m']) != len(data['root_t']):
                    raise SystemExit('%s: root motion has %d frames, clip %d' % (cname, len(data['root_motion_fwd_m']), len(data['root_t'])))
                clips[cname] = data
                print('baked %-30s %3d frames  FK %.6f m  (%s)' % (cname, len(data['root_t']), data['fk_selfcheck_max_m'], key))
            moves[key] = {'clip': cname, 'input': r['input'], 't7_command': r.get('t7_command'), 'motbin_move': r['motbin_move'],
                          'motbin_id': r['motbin_id'], 'active_frames': r['active_frames'],
                          'verified': 'input path from %s + exact T7 frame data (damage %s, first active frame %s)' % (
                              res['stance'], r['damage'], r['startup'])}
        skel = json.load(open(os.path.join(td, 'skeleton.json')))
    os.makedirs(args.out_dir, exist_ok=True)
    sk_path = os.path.join(args.out_dir, 'skeleton.json')
    if os.path.exists(sk_path) and json.load(open(sk_path)) != skel:
        raise SystemExit('%s differs from the bake skeleton: the moves must share the stance skeleton' % sk_path)
    if not os.path.exists(sk_path): json.dump(skel, open(sk_path, 'w'))
    mot = G + 'json/' + next(n for n in ('%smot.json' % args.code, '%s.json' % args.code) if os.path.exists(G + 'json/' + n))
    pack = {'format': 'wh-t7-moves/1', 'fps': 60, 'fighter': args.fighter, 'character': args.character, 'anim_set': 'FIGHT',
            'skeleton': 'skeleton.json',
            'source': {'motbin': os.path.relpath(mot, G.rsplit('teardown/', 1)[0]) + ' (private GRE repo)',
                       'motbin_sha256': hashlib.sha256(open(mot, 'rb').read()).hexdigest(),
                       'resolver': 'tools/anim/t7_move_resolve.py', 'baker': 'tools/anim/t7_c8_stance_bake.py (per clip)'},
            'skipped': skipped, 'moves': moves, 'clips': clips}
    out = os.path.join(args.out_dir, 'moves.pack.json')
    json.dump(pack, open(out, 'w'), separators=(',', ':'))
    print('wrote %s: %d moves, %d clips, %d skipped, %.0f KB' % (out, len(moves), len(clips), len(skipped), os.path.getsize(out) / 1024))


if __name__ == '__main__':
    main()

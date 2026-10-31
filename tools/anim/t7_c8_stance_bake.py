#!/usr/bin/env python3
"""t7_c8_stance_bake.py: bake a real Tekken 7 0xC8 clip (e.g. King's standing stance) into the game's bank format.

Output (into --out-dir, e.g. game/assets/anim/t7/king/):
  skeleton.json  wh-anim-skel/1: the T7 rest pose (Koenji's TekkenMannequin), identity rest rotations, glTF space
                 (meters, Y up, faces +Z, character left = +X), joints named like every bank skeleton
  stance.json    wh-anim/1: per-joint LOCAL quaternions + root_t per frame (60 fps), with full provenance
game/js/t3anims.js (T7_STANCES / applyT7Stance) retargets it onto a fighter rig exactly like a T3 bank clip.

Pipeline (nothing authored, nothing guessed):
  1. decode the 0xC8 clip (raw float frames) from <code>rotsm.arc, MOTA block 0, clip index --clip;
  2. Blender (headless) poses the mannequin with Kiloutre's applyRotationFromAnimdata, the community path that applies
     T7 0xC8 frames (tools/anim/t7_bl_pose.py), and dumps every joint's world rotation + position;
  3. converts to canonical space: rest via C = (x, z, -y) (the mannequin's T-pose faces -Y), posed via
     C2 = (y, z, x) (the T7 fight frame faces +X, left +Y); world delta G = C2 . R_posed . R_rest^T . C^T;
     local = G(parent)^-1 . G(child). Self-check: FK of the written skeleton with these rotations must reproduce the
     posed T7 joint positions (max error printed; the King stance bake measured 0.000000 m).

Inputs you fetch once (raw game files stay in the private GRE repo; third-party tools are not vendored here):
  --arc        GRE teardown/tekken7-steam/tkdata/mothead/mask/<code>rotsm.arc
  --mannequin  TekkenMannequin_no_ik.blend by Koenji: https://mega.nz/folder/05pBGLAL#XPHcsgK2tBxT3RLMbZPaFw
               (the model Kiloutre's tools are written for; any MEGA client, e.g. npm megajs)
  --helper     TekkenAnimHelper.py from https://github.com/Kiloutre/BlenderTekkenDirect
               at commit bebb3d8bc5c4c2c58778ac6af4f87f3dc80062b1
  --blender    Blender 4.x executable

  python3 tools/anim/t7_c8_stance_bake.py --arc <GRE>/.../kinrotsm.arc --clip 132 --anim 'nakg_kg2kam(DVD)' \\
     --moves Kg_sKAM00_,Kg_KAM,Kg_sKAM_WAIT --character 'King (Tekken 7)' --fighter pantera \\
     --mannequin TekkenMannequin_no_ik.blend --helper BlenderTekkenDirect/TekkenAnimHelper.py \\
     --blender blender-4.0.2-linux-x64/blender --out-dir game/assets/anim/t7/king
"""
import argparse, hashlib, json, math, os, re, struct, subprocess, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from t7_anim64 import mota_anims  # noqa: E402

HELPER_COMMIT = 'bebb3d8bc5c4c2c58778ac6af4f87f3dc80062b1'
C = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float)    # mannequin rest (faces -Y, Z up) -> canonical
C2 = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], float)    # T7 fight frame (faces +X, left +Y, Z up) -> canonical
# canonical joint -> (T7 bone, canonical parent). Hips = the T7 lower body (Hip); Spine = T7 Spine1 (upper body).
MAP = [('Hips', 'Hip', None), ('Spine', 'Spine1', 'Hips'), ('Chest', 'Spine2', 'Spine'), ('Neck', 'Neck', 'Chest'),
       ('Head', 'Head', 'Neck')]
for _side, _t in (('Left', 'L'), ('Right', 'R')):
    MAP += [(_side + 'Shoulder', _t + '_Shoulder', 'Chest'), (_side + 'Arm', _t + '_Arm', _side + 'Shoulder'),
            (_side + 'ForeArm', _t + '_ForeArm', _side + 'Arm'), (_side + 'Hand', _t + '_Hand', _side + 'ForeArm'),
            (_side + 'UpLeg', _t + '_UpLeg', 'Hips'), (_side + 'Leg', _t + '_Leg', _side + 'UpLeg'),
            (_side + 'Foot', _t + '_Foot', _side + 'Leg'), (_side + 'ToeBase', _t + '_Toe', _side + 'Foot')]


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def decode_c8(arc, idx):
    d = open(arc, 'rb').read()
    m0 = re.search(b'MOTA', d).start()
    o = m0 + mota_anims(d, m0)[idx]
    t = d[o + 1] if d[o] == 0 else d[o]
    if t != 0xC8:
        sys.exit('clip %d is format %#x, not 0xC8 (0x64 clips need the joint frame first: '
                 'docs/anim/T7-0x64-FRAME-RESEARCH-2026-10-30.md)' % (idx, t))
    e = '<' if d[o] != 0 else '>'
    nb = struct.unpack_from(e + 'H', d, o + 2)[0]
    n = struct.unpack_from(e + 'I', d, o + 4)[0]
    if nb < 23:
        sys.exit('clip %d has %d bones, not a 23-bone body clip' % (idx, nb))
    p = o + 8 + 4 * nb
    return [list(struct.unpack_from(e + '%df' % (3 * nb), d, p + 12 * nb * k))[:69] for k in range(n)]


def mat_to_quat(m):
    t = np.trace(m)
    if t > 0:
        s = math.sqrt(t + 1.0) * 2
        w, x, y, z = 0.25 * s, (m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = math.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2
        w, x, y, z = (m[2, 1] - m[1, 2]) / s, 0.25 * s, (m[0, 1] + m[1, 0]) / s, (m[0, 2] + m[2, 0]) / s
    elif m[1, 1] > m[2, 2]:
        s = math.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2
        w, x, y, z = (m[0, 2] - m[2, 0]) / s, (m[0, 1] + m[1, 0]) / s, 0.25 * s, (m[1, 2] + m[2, 1]) / s
    else:
        s = math.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2
        w, x, y, z = (m[1, 0] - m[0, 1]) / s, (m[0, 2] + m[2, 0]) / s, (m[1, 2] + m[2, 1]) / s, 0.25 * s
    q = np.array([x, y, z, w])
    return q / np.linalg.norm(q)


def orth(m):
    u, _, vt = np.linalg.svd(np.array(m, float))
    r = u @ vt
    return r if np.linalg.det(r) > 0 else u @ np.diag([1, 1, -1]) @ vt


def convert(posed, provenance, mannequin_meta):
    rest_pos = {c: C @ np.array(posed['rest'][t]['head']) for c, t, _ in MAP}
    rest_rot = {c: orth(posed['rest'][t]['rot']) for c, t, _ in MAP}
    rot = {c: [] for c, _, _ in MAP}
    root_t, worst = [], 0.0
    for fr in posed['frames']:
        G = {c: C2 @ orth(fr[t]['rot']) @ rest_rot[c].T @ C.T for c, t, _ in MAP}
        pos = {c: C2 @ np.array(fr[t]['head']) for c, t, _ in MAP}
        fk = {}
        for c, _, p in MAP:
            loc = G[c] if p is None else G[p].T @ G[c]
            q = mat_to_quat(loc)
            if rot[c] and float(np.dot(q, rot[c][-1])) < 0:
                q = -q  # sign continuity for clean interpolation
            rot[c].append([round(float(v), 6) for v in q])
            fk[c] = pos['Hips'] if p is None else fk[p] + G[p] @ (rest_pos[c] - rest_pos[p])
            worst = max(worst, float(np.linalg.norm(fk[c] - pos[c])))
        root_t.append([round(float(v), 6) for v in pos['Hips']])
    skel = {'format': 'wh-anim-skel/1', 'tool': 'tools/anim/t7_c8_stance_bake.py',
            'note': 'Rest pose of the Tekken 7 skeleton (Koenji TekkenMannequin) the T7 clips here were converted on. '
                    'All joint rest rotations are identity; rest = world joint positions (glTF space, meters, faces +Z, '
                    'character left = +X).',
            'source_skeleton': mannequin_meta, 'root': 'Hips', 'root_rest_y': round(float(rest_pos['Hips'][1]), 6),
            'joints': [{'name': c, 'parent': p, 'rest': [round(float(v), 6) for v in rest_pos[c]]} for c, _, p in MAP],
            'foot_tip': {}}
    clip = {'format': 'wh-anim/1', 'fps': 60.0, 'anim_set': 'FIGHT', 'bones': [c for c, _, _ in MAP],
            'rot_xyzw': rot, 'root_t': root_t, 'source': 'REAL Tekken 7 motion (0xC8, raw float frames)',
            **provenance, 'fk_selfcheck_max_m': round(worst, 6)}
    return skel, clip, worst


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--arc', required=True)
    ap.add_argument('--clip', type=int, required=True)
    ap.add_argument('--anim', required=True, help='T7 animation name of the clip (from the motbin, e.g. nakg_kg2kam(DVD))')
    ap.add_argument('--moves', default='', help='comma list of T7 moves that play this clip')
    ap.add_argument('--character', required=True)
    ap.add_argument('--fighter', required=True, help='Western Heart fighter id the clip is baked for')
    ap.add_argument('--mannequin', required=True)
    ap.add_argument('--helper', required=True)
    ap.add_argument('--blender', required=True)
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--name', default='stance', help='output clip file name (without .json)')
    a = ap.parse_args()

    frames = decode_c8(a.arc, a.clip)
    with tempfile.TemporaryDirectory() as tmp:
        fpath, ppath = os.path.join(tmp, 'frames.json'), os.path.join(tmp, 'posed.json')
        json.dump({'frames': frames}, open(fpath, 'w'))
        r = subprocess.run([a.blender, '-b', a.mannequin, '--python', os.path.join(HERE, 't7_bl_pose.py'), '--',
                            a.helper, fpath, ppath], capture_output=True, text=True)
        if r.returncode or not os.path.exists(ppath):
            sys.exit('blender failed:\n' + r.stdout[-3000:] + r.stderr[-3000:])
        posed = json.load(open(ppath))
    mannequin_meta = {'file': os.path.basename(a.mannequin), 'by': 'Koenji', 'sha256': sha256(a.mannequin),
                      'url': 'https://mega.nz/folder/05pBGLAL#XPHcsgK2tBxT3RLMbZPaFw'}
    provenance = {'character': a.character, 'for_fighter': a.fighter, 'loop': True,
                  't7_source': {'file': 'teardown/tekken7-steam/tkdata/mothead/mask/' + os.path.basename(a.arc) +
                                ' (private GRE repo)', 'sha256': sha256(a.arc), 'mota_block': 0, 'clip': a.clip,
                                'anim': a.anim, 'format': '0xC8', 'frames': len(frames),
                                'moves': [m for m in a.moves.split(',') if m]},
                  'applier': {'function': 'applyRotationFromAnimdata', 'repo': 'https://github.com/Kiloutre/BlenderTekkenDirect',
                              'commit': HELPER_COMMIT, 'file': 'TekkenAnimHelper.py', 'sha256': sha256(a.helper)}}
    skel, clip, worst = convert(posed, provenance, mannequin_meta)
    if worst > 1e-3:
        sys.exit('FK self-check failed: %.6f m (the conversion does not reproduce the posed joints)' % worst)
    os.makedirs(a.out_dir, exist_ok=True)
    json.dump(skel, open(os.path.join(a.out_dir, 'skeleton.json'), 'w'), indent=1)
    json.dump(clip, open(os.path.join(a.out_dir, a.name + '.json'), 'w'), separators=(',', ':'))
    print('baked %d frames, %d joints -> %s (FK self-check max %.6f m)' % (len(frames), len(MAP), a.out_dir, worst))


if __name__ == '__main__':
    main()

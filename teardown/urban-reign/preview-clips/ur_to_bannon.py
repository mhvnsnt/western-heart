#!/usr/bin/env python3
"""ur_to_bannon.py — Urban Reign decoded motion banks -> preview-clip JSONs.

Converts the staged general banks (ur-general-normal / ur-general-30frame /
ur-general-weapon: clips.json + rows.pack.json + skeleton.json) into the
VPW2 v1.3 / KoC2 v1.2 converter-clip format:
  {dur, keys: [{t, root: [x, z], pose: {joint: [x, y, z]}}], _ur: {...}}
in the clip frame (x=forward, y=up, z=left, meters), 60 fps.

FK convention (PROVEN 2026-11-21, see BONE_MAP.md):
  * packed quats are q_bindlocal(glb-parent) x q_euler; the euler delta is
    recovered as qe = qbind_glb^-1 x q_packed. Validated to 0.002 deg RMS:
    the recovered root qe matches eul2mat(root position) exactly (the packer
    fed the root POSITION track through the Euler path, so the packed root
    quat is garbage and is discarded — the root keeps its bind rotation).
  * FK runs over the GAME hierarchy (PARENT_GAME), with bind-local rotations
    from the char001 GLB inverse-bind matrices (W = inv(IBM)) and Bannon
    REST bone offsets (the preview plays on the Bannon rig; the driver
    requires clip/rig segment ratios ~1.00, so the converter uses the
    target rig's proportions — same as the VPW2/KoC2 converters).
  * GLB -> clip axis map: clip = (glb_x, -glb_z, -glb_y).
  * Proven: 791/829 general-bank motions FK into a sane stance at frame 0
    (pelvis 0.90, head ~1.65, ankles ~0.12); the ur_m001 stance reads as a
    textbook fighting guard (lead left hand forward, rear right back).

Root motion: root_t (GLB) -> clip root [x, z] + pelvis height. 136/829
clips have a CORRUPT root decode in the staging (frame-to-frame jumps of
0.5-11.6 m — physically impossible; the type-14 range decode fails for
those tracks). For those, the root is zeroed (motion plays in place) and
the clip is flagged root_corrupt=true in _ur. Rotations are unaffected.

Per-frame pair lift (VPW2-style): lift = max(0, -min_y) over non-tip
joints, applied to all pose y, so feet never sink below the floor on a
flat stage. For a two-person pair, use --pair to share the lift.

NO BONE LIMITING: every joint the UR motion drives moves in the output —
both spine joints, both clavicles, wrists (TE), ankles (ASHI), toes
(TSUMASAKI). UR has no finger bones (mitten hands) and no separate
forearm joint (UDE->TE spans elbow->wrist): ha/fi are rigid extensions
of the wrist (curl ~0, honest), chest shares MUNE2's rotation (same as
VPW2's spineMid+chest sharing UpperBody).

Usage:
  python3 ur_to_bannon.py --bank <bankdir> --out <clipsdir> [--only m001,m002]
  python3 ur_to_bannon.py --pair <clipA.json> <clipB.json> --out <dir>
    (pair mode re-lifts two already-converted clips with a shared lift)
"""
import argparse
import base64
import json
import math
import os
import struct
import sys

import numpy as np

GLB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'wh/teardown/urban-reign/models/char001/char001.glb')

PARENT_GAME = {12: None, 0: 12, 1: 0, 2: 1, 3: 2, 4: 1, 5: 4, 6: 5, 7: 6,
               8: 1, 9: 8, 10: 9, 11: 10, 13: 12, 14: 13, 15: 14, 16: 15,
               17: 12, 18: 17, 19: 18, 20: 19}
BODY_ORDER = [12, 0, 13, 17, 1, 14, 18, 2, 4, 8, 15, 19, 3, 5, 9, 16, 20,
              6, 10, 7, 11]
# GLB -> clip axis map: clip = (gx, -gz, -gy)
A_MAP = np.array([[1, 0, 0], [0, 0, -1], [0, -1, 0]], float)

# REST pose: loaded from rest_mixamo.json (build_rest.py measurement of the
# BANNON_repaired.glb Mixamo rig) — NOT the VPW2 file's hardcoded REST.
# The hardcoded REST (pelvis 0.90) gave clip/rig ratios 1.57-2.35 against
# the Bannon GLB (the squash defect class); the measured Mixamo REST
# (pelvis 1.085) gives ratios ~1.00. Loaded at FK init; see --rest.
REST = None


def load_rest(path):
    d = json.load(open(path))
    need = set(UR2REST.values()) | {a for _, _, a in VIRTUAL}
    rest = {j: [float(v) for v in d[j]] for j in need}
    return rest
# UR GLB node -> clip joint (position anchor). Chain A (4-7, 13-16) is
# anatomical LEFT (verified: shL lands at +z = left in the FK stance).
UR2REST = {12: 'pelvis', 0: 'spineLow', 1: 'spineMid', 2: 'neck', 3: 'head',
           4: 'clavL', 5: 'shL', 6: 'elL', 7: 'wrL',
           8: 'clavR', 9: 'shR', 10: 'elR', 11: 'wrR',
           13: 'hipL', 14: 'knL', 15: 'ankL', 16: 'toL',
           17: 'hipR', 18: 'knR', 19: 'ankR', 20: 'toR'}
# Virtual joints: (name, parent UR node, REST anchor joint for the offset)
VIRTUAL = [('chest', 1, 'chest'),
           ('haL', 7, 'haL'), ('fiL', 7, 'fiL'),
           ('haR', 11, 'haR'), ('fiR', 11, 'fiR'),
           ('ftL', 15, 'ftL'), ('ftR', 19, 'ftR')]
# joints excluded from the lift computation (tips must not lift the pair)
TIP_JOINTS = {'fiL', 'fiR', 'toL', 'toR'}
ROOT_JUMP_MAX = 0.5  # m/frame at 60fps; above this the root decode is corrupt


def load_bind(glb_path):
    """W rotations + qbind_glb from the char001 GLB (read as data)."""
    data = open(glb_path, 'rb').read()
    ln = struct.unpack('<I', data[12:16])[0]
    g = json.loads(data[20:20 + ln])
    off = 20 + ln
    bln = struct.unpack('<I', data[off:off + 4])[0]
    binx = data[off + 8:off + 8 + bln]

    def acc(ai):
        a = g['accessors'][ai]
        bv = g['bufferViews'][a['bufferView']]
        o = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
        ct = {5126: '<f4', 5123: '<u2', 5125: '<u4', 5121: '<u1'}[
            a['componentType']]
        nc = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[
            a['type']]
        arr = np.frombuffer(binx, dtype=ct, count=a['count'] * nc, offset=o)
        return arr.reshape(a['count'], nc) if nc > 1 else arr

    skin = g['skins'][0]
    ibm = [np.array(m).reshape(4, 4).T
           for m in acc(skin['inverseBindMatrices'])]
    W = {ji: np.linalg.inv(ibm[k]) for k, ji in enumerate(skin['joints'])}
    glb_parent = {}
    for i, n in enumerate(g['nodes']):
        for c in n.get('children', []):
            glb_parent[c] = i
    W_R = {ji: W[ji][:3, :3] for ji in range(21)}
    LB_game_R = {}
    for ji in range(21):
        par = PARENT_GAME.get(ji)
        LB_game_R[ji] = W_R[ji] if par is None else (
            np.linalg.inv(W[par]) @ W[ji])[:3, :3]
    LB_glb = {}
    for ji in range(21):
        par = glb_parent.get(ji)
        LB_glb[ji] = W[ji].copy() if par is None else (
            np.linalg.inv(W[par]) @ W[ji])
    qbind_glb = {ji: mat2quat(LB_glb[ji][:3, :3]) for ji in range(21)}
    return W_R, LB_game_R, qbind_glb


def mat2quat(R):
    t = np.trace(R)
    if t > 0:
        s = np.sqrt(t + 1.0) * 2
        return np.array([0.25 * s, (R[2, 1] - R[1, 2]) / s,
                         (R[0, 2] - R[2, 0]) / s, (R[1, 0] - R[0, 1]) / s])
    i = int(np.argmax(np.diag(R)))
    if i == 0:
        s = np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2]) * 2
        return np.array([(R[2, 1] - R[1, 2]) / s, 0.25 * s,
                         (R[0, 1] + R[1, 0]) / s, (R[0, 2] + R[2, 0]) / s])
    if i == 1:
        s = np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2]) * 2
        return np.array([(R[0, 2] - R[2, 0]) / s, (R[0, 1] + R[1, 0]) / s,
                         0.25 * s, (R[1, 2] + R[2, 1]) / s])
    s = np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1]) * 2
    return np.array([(R[1, 0] - R[0, 1]) / s, (R[0, 2] + R[2, 0]) / s,
                     (R[1, 2] + R[2, 1]) / s, 0.25 * s])


def qmul_vec(a, b):
    """Hamilton product, vectorized over leading dims. Quats are (w,x,y,z)."""
    w1, x1, y1, z1 = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    w2, x2, y2, z2 = b[..., 0], b[..., 1], b[..., 2], b[..., 3]
    return np.stack([w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
                     w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                     w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
                     w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2], axis=-1)


def q2R_vec(q):
    q = q / np.linalg.norm(q, axis=-1, keepdims=True)
    w, x, y, z = q[..., 0], q[..., 1], q[..., 2], q[..., 3]
    R = np.empty(q.shape[:-1] + (3, 3))
    R[..., 0, 0] = 1 - 2 * (y * y + z * z)
    R[..., 0, 1] = 2 * (x * y - z * w)
    R[..., 0, 2] = 2 * (x * z + y * w)
    R[..., 1, 0] = 2 * (x * y + z * w)
    R[..., 1, 1] = 1 - 2 * (x * x + z * z)
    R[..., 1, 2] = 2 * (y * z - x * w)
    R[..., 2, 0] = 2 * (x * z - y * w)
    R[..., 2, 1] = 2 * (y * z + x * w)
    R[..., 2, 2] = 1 - 2 * (x * x + y * y)
    return R


def decode_rows(b64, n_frames):
    """base64 i16 xyzw -> (F, 21, 4) float quats in (w, x, y, z)."""
    raw = base64.b64decode(b64)
    vals = np.frombuffer(raw, dtype='<i2').astype(np.float64) / 32767.0
    vals = vals.reshape(n_frames, 21, 4)
    return np.stack([vals[..., 3], vals[..., 0], vals[..., 1], vals[..., 2]],
                    axis=-1)


class FK:
    def __init__(self, glb_path=GLB_PATH, rest_path=None):
        if rest_path is None:
            rest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     'rest_mixamo.json')
        rest = load_rest(rest_path)
        self.rest = rest
        W_R, LB_game_R, qbind_glb = load_bind(glb_path)
        self.W_R = W_R
        self.LB_game_R = LB_game_R
        self.qbind_inv = np.stack([
            np.array([qbind_glb[n][0], -qbind_glb[n][1],
                      -qbind_glb[n][2], -qbind_glb[n][3]])
            for n in range(21)])
        Ai = A_MAP.T
        rest_glb = {j: Ai @ np.array(v) for j, v in rest.items()}
        self.rest_glb = rest_glb
        # local offsets in the parent's bind frame (GLB space)
        self.off_local = {}
        for n in range(21):
            par = PARENT_GAME.get(n)
            if par is None:
                continue
            d = rest_glb[UR2REST[n]] - rest_glb[UR2REST[par]]
            self.off_local[n] = W_R[par].T @ d
        self.virt_off = {}
        for name, par_node, anchor in VIRTUAL:
            d = rest_glb[anchor] - rest_glb[UR2REST[par_node]]
            self.virt_off[name] = (par_node, W_R[par_node].T @ d)

    def run(self, q_packed, root_t):
        """q_packed: (F, 21, 4) wxyz; root_t: (F, 3) GLB-space.
        Returns dict joint -> (F, 3) clip-space WORLD positions and
        root_clip (F, 3)."""
        F = q_packed.shape[0]
        qe = qmul_vec(self.qbind_inv[None, :, :], q_packed)
        Re = q2R_vec(qe)  # (F, 21, 3, 3)
        Rw = {}
        P = {}
        for n in BODY_ORDER:
            par = PARENT_GAME.get(n)
            if n == 12:
                Rw[n] = np.broadcast_to(self.W_R[12], (F, 3, 3)).copy()
                P[n] = (self.rest_glb['pelvis'][None, :] + root_t)
            else:
                Rw[n] = Rw[par] @ self.LB_game_R[n][None, :, :] @ Re[:, n]
                P[n] = P[par] + np.einsum('fij,j->fi', Rw[par],
                                          self.off_local[n])
        out = {}
        for n in range(21):
            out[UR2REST[n]] = P[n] @ A_MAP.T
        for name, (par_node, off) in self.virt_off.items():
            Pv = P[par_node] + np.einsum('fij,j->fi', Rw[par_node], off)
            out[name] = Pv @ A_MAP.T
        root_clip = root_t @ A_MAP.T
        return out, root_clip


def lift_per_frame(poses):
    """poses: dict joint -> (F, 3) world positions. Returns (F,) lift."""
    F = next(iter(poses.values())).shape[0]
    lo = np.full(F, np.inf)
    for j, arr in poses.items():
        if j in TIP_JOINTS:
            continue
        lo = np.minimum(lo, arr[:, 1])
    return np.maximum(0.0, -lo)


def build_clip(fk, name, meta, pack, bank_name, ur_name, pair_lift=None):
    frames = meta['frames']
    q_packed = decode_rows(pack['rows'][name], frames)
    root_t = np.array(pack['root_t'][name], dtype=float)
    # corrupt-root detection: physically impossible frame-to-frame jump
    jumps = np.abs(np.diff(root_t, axis=0)).max(axis=1) if frames > 1 else [0]
    max_jump = float(jumps.max()) if len(jumps) else 0.0
    root_corrupt = max_jump > ROOT_JUMP_MAX
    if root_corrupt:
        root_t = np.zeros_like(root_t)
    poses, root_clip = fk.run(q_packed, root_t)
    lift = lift_per_frame(poses) if pair_lift is None else pair_lift
    keys = []
    for f in range(frames):
        rx, rz = float(root_clip[f, 0]), float(root_clip[f, 2])
        pose = {}
        for j, arr in poses.items():
            pose[j] = [round(float(arr[f, 0] - rx), 4),
                       round(float(arr[f, 1] + lift[f]), 4),
                       round(float(arr[f, 2] - rz), 4)]
        # pelvis is root-relative: x/z exactly 0
        pose['pelvis'][0] = 0.0
        pose['pelvis'][2] = 0.0
        keys.append({'t': round(f / 60.0, 4),
                     'root': [round(rx, 4), round(rz, 4)],
                     'pose': pose})
    clip = {'dur': round(frames / 60.0, 4), 'keys': keys,
            '_ur': {'source_bank': bank_name, 'motion': meta['motion'],
                    'clip': name, 'ur_name': ur_name,
                    'root_corrupt': root_corrupt,
                    'root_max_jump_m': round(max_jump, 3),
                    'frames': frames, 'fps': 60,
                    'lift': [round(float(v), 4) for v in lift],
                    'converter': 'ur_to_bannon.py (FK H1, rest_mixamo)'}}
    return clip


def load_names():
    """(bank, motion) -> ur_name from the name-bridge cross-bank hits."""
    import glob as gb
    base = '/home/hatch/workspace/wrestling-full-pull/other-games/urban-reign'
    names = {}
    for f in sorted(gb.glob(f'{base}/motion-names/name-bridge-*-proven.json')):
        d = json.load(open(f))
        for p in d.get('provenPairs', []):
            if 'alsoIn' in p:
                a = p['alsoIn']
                names[(a['bank'], a['motion'])] = p['name']
        for r in d.get('unprovenRecords', []):
            for h in r.get('crossBankHits', []):
                names[(h['bank'], h['bankMotion'])] = r['name']
    return names


BANK_SHORT = {'ur-general-normal': 'general_normal',
              'ur-general-30frame': 'general_30frame',
              'ur-general-weapon': 'general_weapon'}


def convert_bank(bank_dir, out_dir, only=None, force=False, rest_path=None):
    bank_name = os.path.basename(bank_dir.rstrip('/'))
    short = BANK_SHORT.get(bank_name, bank_name)
    clips = json.load(open(f'{bank_dir}/clips.json'))['clips']
    pack = json.load(open(f'{bank_dir}/rows.pack.json'))
    names = load_names()
    fk = FK(rest_path=rest_path)
    os.makedirs(out_dir, exist_ok=True)
    manifest_path = os.path.join(out_dir, f'MANIFEST-{short}.json')
    manifest = {}
    if os.path.exists(manifest_path):
        manifest = json.load(open(manifest_path))
    done = skipped = corrupt = 0
    for meta in clips:
        name = meta['name']
        if only and name not in only:
            continue
        out_path = os.path.join(out_dir, f'ur_{short}_{name}.json')
        if os.path.exists(out_path) and not force:
            skipped += 1
            continue
        ur_name = names.get((short, meta['motion']))
        clip = build_clip(fk, name, meta, pack, bank_name, ur_name)
        with open(out_path, 'w') as f:
            json.dump(clip, f, separators=(',', ':'))
        manifest[name] = {'file': os.path.basename(out_path),
                          'frames': meta['frames'],
                          'ur_name': ur_name,
                          'root_corrupt': clip['_ur']['root_corrupt'],
                          'root_max_jump_m': clip['_ur']['root_max_jump_m']}
        done += 1
        corrupt += 1 if clip['_ur']['root_corrupt'] else 0
        if done % 100 == 0:
            print(f'  {bank_name}: {done} converted, {corrupt} corrupt-root')
    json.dump(manifest, open(manifest_path, 'w'), indent=1)
    print(f'{bank_name}: {done} converted ({corrupt} root-corrupt), '
          f'{skipped} skipped (already present)')
    return done, corrupt, skipped


def pair_relist(clip_a_path, clip_b_path, out_dir, recv_offset_fwd=0.65):
    """Re-lift a P1/P2 pair with a SHARED per-frame lift, and stage the
    receiver at recv_offset_fwd meters in front of the attacker at t=0
    (the two motions are authored independently; the starting grapple
    distance is not in the data — 0.65 m is the driver's fallback)."""
    a = json.load(open(clip_a_path))
    b = json.load(open(clip_b_path))
    n = max(len(a['keys']), len(b['keys']))

    def world_unlifted(clip, f):
        # world positions with the clip's own baked lift stripped
        k = clip['keys'][min(f, len(clip['keys']) - 1)]
        own = clip['_ur']['lift'][min(f, len(clip['_ur']['lift']) - 1)]
        rx, rz = k['root']
        return {j: np.array([v[0] + rx, v[1] - own, v[2] + rz])
                for j, v in k['pose'].items()}

    lift = np.zeros(n)
    for f in range(n):
        lo = np.inf
        for clip in (a, b):
            for j, v in world_unlifted(clip, f).items():
                if j not in TIP_JOINTS:
                    lo = min(lo, v[1])
        lift[f] = max(0.0, -lo)
    # strip each clip's own lift, then apply the shared lift
    for clip, is_recv in ((a, False), (b, True)):
        own = clip['_ur']['lift']
        for f, k in enumerate(clip['keys']):
            shared = lift[min(f, n - 1)]
            dy = shared - own[f]
            for j in k['pose']:
                k['pose'][j][1] = round(k['pose'][j][1] + dy, 4)
            if is_recv:
                k['root'][0] = round(k['root'][0] + recv_offset_fwd, 4)
        clip['_ur']['lift'] = [round(float(lift[min(f, n - 1)]), 4)
                               for f in range(len(clip['keys']))]
        clip['_ur']['pair_lift_shared'] = True
        if is_recv:
            clip['_ur']['recv_offset_fwd_m'] = recv_offset_fwd
    os.makedirs(out_dir, exist_ok=True)
    pa = os.path.join(out_dir, os.path.basename(clip_a_path))
    pb = os.path.join(out_dir, os.path.basename(clip_b_path))
    json.dump(a, open(pa, 'w'), separators=(',', ':'))
    json.dump(b, open(pb, 'w'), separators=(',', ':'))
    print(f'pair re-lifted: {pa} + {pb} (shared lift, '
          f'recv offset +{recv_offset_fwd}m fwd)')
    return pa, pb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bank', help='bank dir (clips.json + rows.pack.json)')
    ap.add_argument('--out', required=True)
    ap.add_argument('--only', help='comma-separated clip names, e.g. ur_m001')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--pair', nargs=2, metavar=('P1', 'P2'),
                    help='pair mode: re-lift two clips with shared lift')
    ap.add_argument('--recv-offset', type=float, default=0.65)
    ap.add_argument('--rest', default=None,
                    help='REST JSON (default: workdir rest_mixamo.json)')
    args = ap.parse_args()
    if args.pair:
        pair_relist(args.pair[0], args.pair[1], args.out, args.recv_offset)
        return
    only = set(args.only.split(',')) if args.only else None
    convert_bank(args.bank, args.out, only=only, force=args.force,
                 rest_path=args.rest)


if __name__ == '__main__':
    main()

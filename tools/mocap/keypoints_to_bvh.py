#!/usr/bin/env python3
"""Stage 2 of the WH mocap pipeline: wh-keypoints/1 JSON -> BVH.

[WIRED] Runs on CPU, no GPU needed. Tested end-to-end on synthetic keypoints
(see tests/test_pipeline.py).

Reads the canonical keypoint schema produced by tools/mocap/video_to_keypoints.py
(wh-keypoints/1) and writes a standard BVH file whose joint names match the
game's canonical clip bone set (T3_BONES in game/js/t3anims.js), so the output
flows through the same retarget (retargetT3Clips) as the Tekken 3 banks.

Method (v1, heuristic):
  - Per-frame joint positions -> metric space (Y-up, meters), hips-centered.
  - Missing detections are linearly interpolated; light moving-average smoothing.
  - World orientation per bone from keypoint geometry:
      pelvis/torso/head : orthonormal frame from hip axis + torso up axis
      limb bones        : shortest-arc swing from rest direction to current
                          bone direction (NO TWIST in v1)
  - Local rotations = parentWorld^-1 * world; written as ZXY euler (degrees).
  - Root carries translation; Root rotation is identity, pelvis orientation
    lives on Hips (mirrors the T3 bank convention of separate Root/Hips).

Conventions:
  - Output faces +Z, character left = +X (same declaration as the T3 banks'
    skeleton.json notes; retargetT3Clips and bankFacing rely on it).
  - Euler order ZXY: R = Rz(z) * Rx(x) * Ry(y), degrees. Stated in the BVH
    header comment. tools/mocap/bvh_to_wh_anim.py round-trips this exactly;
    re-export from Blender if another DCC needs a different order.
  - MediaPipe z-sign: --z-sign -1 (default) maps MediaPipe's
    "smaller z = closer to camera" to +Z forward. If gate_check.py reports
    the bank faces -Z on real footage, re-run with --z-sign 1.

Limitations (honest): no twist estimation, rigid torso/head in v1, foot
contact not enforced (expect some foot slide). The GPU 3D-lifting path
(MotionBERT/WHAM -> SMPL -> BVH, see README.md) is the quality upgrade.
"""
import argparse
import json
import math

import numpy as np

# ----------------------------------------------------------------------------
# Canonical WH bone set (== T3_BONES in game/js/t3anims.js)
# ----------------------------------------------------------------------------
BONES = [
    'Root', 'Hips', 'Spine', 'Chest', 'Neck', 'Head',
    'LeftShoulder', 'LeftArm', 'LeftForeArm', 'LeftHand',
    'RightShoulder', 'RightArm', 'RightForeArm', 'RightHand',
    'LeftUpLeg', 'LeftLeg', 'LeftFoot', 'LeftToeBase',
    'RightUpLeg', 'RightLeg', 'RightFoot', 'RightToeBase',
]
PARENTS = {
    'Root': None,
    'Hips': 'Root',
    'Spine': 'Hips', 'Chest': 'Spine', 'Neck': 'Chest', 'Head': 'Neck',
    'LeftShoulder': 'Chest', 'LeftArm': 'LeftShoulder',
    'LeftForeArm': 'LeftArm', 'LeftHand': 'LeftForeArm',
    'RightShoulder': 'Chest', 'RightArm': 'RightShoulder',
    'RightForeArm': 'RightArm', 'RightHand': 'RightForeArm',
    'LeftUpLeg': 'Hips', 'LeftLeg': 'LeftUpLeg',
    'LeftFoot': 'LeftLeg', 'LeftToeBase': 'LeftFoot',
    'RightUpLeg': 'Hips', 'RightLeg': 'RightUpLeg',
    'RightFoot': 'RightLeg', 'RightToeBase': 'RightFoot',
}
CHILDREN = {b: [] for b in BONES}
for _b, _p in PARENTS.items():
    if _p:
        CHILDREN[_p].append(_b)

# Generic T-pose rest, meters, faces +Z, character left = +X.
# (Only the DIRECTIONS matter for the swing computation; the retarget maps
#  source rest dirs -> target rest dirs, exactly like the T3 banks.)
REST = {
    'Root':         (0.00, 0.98, 0.00),
    'Hips':         (0.00, 0.98, 0.00),
    'Spine':        (0.00, 1.12, 0.00),
    'Chest':        (0.00, 1.28, 0.00),
    'Neck':         (0.00, 1.42, 0.00),
    'Head':         (0.00, 1.54, 0.00),
    'LeftShoulder': (0.06, 1.40, 0.00),
    'LeftArm':      (0.21, 1.40, 0.00),
    'LeftForeArm':  (0.47, 1.40, 0.00),
    'LeftHand':     (0.67, 1.40, 0.00),
    'RightShoulder': (-0.06, 1.40, 0.00),
    'RightArm':     (-0.21, 1.40, 0.00),
    'RightForeArm': (-0.47, 1.40, 0.00),
    'RightHand':    (-0.67, 1.40, 0.00),
    'LeftUpLeg':    (0.10, 0.96, 0.00),
    'LeftLeg':      (0.10, 0.52, 0.00),
    'LeftFoot':     (0.10, 0.10, 0.00),
    'LeftToeBase':  (0.10, 0.06, 0.17),
    'RightUpLeg':   (-0.10, 0.96, 0.00),
    'RightLeg':     (-0.10, 0.52, 0.00),
    'RightFoot':    (-0.10, 0.10, 0.00),
    'RightToeBase': (-0.10, 0.06, 0.17),
}
REST_DIRS = {}
for _b in BONES:
    _p = PARENTS[_b]
    if _p is None:
        REST_DIRS[_b] = np.zeros(3)
    else:
        _d = np.array(REST[_b]) - np.array(REST[_p])
        _n = np.linalg.norm(_d)
        REST_DIRS[_b] = _d / _n if _n > 1e-9 else np.zeros(3)

END_SITES = {  # leaf bones -> end-site offset (rest dir * small length)
    'Head': (0.00, 0.14, 0.00),
    'LeftHand': (0.10, 0.00, 0.00), 'RightHand': (-0.10, 0.00, 0.00),
    'LeftToeBase': (0.00, 0.00, 0.08), 'RightToeBase': (0.00, 0.00, 0.08),
}

# ----------------------------------------------------------------------------
# Quaternion / euler math (xyzw convention, matching wh-anim/1 rot_xyzw)
# ----------------------------------------------------------------------------
def q_mul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return np.array([
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    ])


def q_conj(q):
    return np.array([-q[0], -q[1], -q[2], q[3]])


def q_norm(q):
    n = np.linalg.norm(q)
    return q / n if n > 1e-12 else np.array([0.0, 0.0, 0.0, 1.0])


def q_identity():
    return np.array([0.0, 0.0, 0.0, 1.0])


def q_from_axis_angle(axis, angle):
    axis = np.asarray(axis, dtype=float)
    n = np.linalg.norm(axis)
    if n < 1e-12:
        return q_identity()
    axis = axis / n
    s = math.sin(angle / 2.0)
    return np.array([axis[0] * s, axis[1] * s, axis[2] * s, math.cos(angle / 2.0)])


def swing(a, b):
    """Shortest-arc quaternion rotating unit vector a onto unit vector b."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-9 or nb < 1e-9:
        return q_identity()
    a, b = a / na, b / nb
    d = float(np.dot(a, b))
    if d >= 1.0 - 1e-9:
        return q_identity()
    if d <= -1.0 + 1e-9:
        # 180 deg: pick any orthogonal axis
        ax = np.cross(a, np.array([1.0, 0.0, 0.0]))
        if np.linalg.norm(ax) < 1e-6:
            ax = np.cross(a, np.array([0.0, 1.0, 0.0]))
        return q_from_axis_angle(ax, math.pi)
    c = np.cross(a, b)
    return q_norm(np.array([c[0], c[1], c[2], 1.0 + d]))


def mat_to_quat(m):
    t = m[0, 0] + m[1, 1] + m[2, 2]
    if t > 0:
        s = math.sqrt(t + 1.0) * 2.0
        w = 0.25 * s
        x = (m[2, 1] - m[1, 2]) / s
        y = (m[0, 2] - m[2, 0]) / s
        z = (m[1, 0] - m[0, 1]) / s
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = math.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2.0
        w = (m[2, 1] - m[1, 2]) / s
        x = 0.25 * s
        y = (m[0, 1] + m[1, 0]) / s
        z = (m[0, 2] + m[2, 0]) / s
    elif m[1, 1] > m[2, 2]:
        s = math.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2.0
        w = (m[0, 2] - m[2, 0]) / s
        x = (m[0, 1] + m[1, 0]) / s
        y = 0.25 * s
        z = (m[1, 2] + m[2, 1]) / s
    else:
        s = math.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2.0
        w = (m[1, 0] - m[0, 1]) / s
        x = (m[0, 2] + m[2, 0]) / s
        y = (m[1, 2] + m[2, 1]) / s
        z = 0.25 * s
    return q_norm(np.array([x, y, z, w]))


def quat_to_mat(q):
    x, y, z, w = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def quat_to_euler_zxy(q):
    """-> (z, x, y) radians with R = Rz(z) @ Rx(x) @ Ry(y)."""
    R = quat_to_mat(q_norm(q))
    # R[2][1] = sin(x); R[2][0] = -cos(x) sin(y); R[2][2] = cos(x) cos(y)
    # R[0][1] = -sin(z) cos(x); R[1][1] = cos(z) cos(x)
    sx = max(-1.0, min(1.0, R[2, 1]))
    x = math.asin(sx)
    if abs(math.cos(x)) > 1e-6:
        y = math.atan2(-R[2, 0], R[2, 2])
        z = math.atan2(-R[0, 1], R[1, 1])
    else:  # gimbal: fold into z
        y = 0.0
        z = math.atan2(R[1, 0], R[0, 0])
    return (z, x, y)


def euler_zxy_to_quat(z, x, y):
    qz = q_from_axis_angle((0, 0, 1), z)
    qx = q_from_axis_angle((1, 0, 0), x)
    qy = q_from_axis_angle((0, 1, 0), y)
    return q_norm(q_mul(qz, q_mul(qx, qy)))


# ----------------------------------------------------------------------------
# Keypoint handling
# ----------------------------------------------------------------------------
def mid(a, b):
    return (np.asarray(a, dtype=float) + np.asarray(b, dtype=float)) / 2.0


def load_keypoints(path):
    with open(path) as f:
        data = json.load(f)
    if data.get('format') != 'wh-keypoints/1':
        raise ValueError(f'{path}: expected format wh-keypoints/1, got {data.get("format")}')
    return data


def frames_to_metric(data, z_sign=-1.0):
    """Per-frame dict of canonical joint -> np.array(3) in meters, Y-up.

    MediaPipe-style input: x right (0..1), y down (0..1), z toward camera.
    Output: character-centric meters, faces +Z, character left = +X, Y up.
    Scale: torso (hips->shoulders) normalized to 0.50 m.
    """
    out = []
    for fr in data['frames']:
        pos = fr.get('pos', {})
        P = {}
        for name, xyz in pos.items():
            x, y, z = xyz
            P[name] = np.array([x, -y, z_sign * z], dtype=float)
        out.append({'t': fr.get('t', 0.0), 'detected': bool(fr.get('detected'))
                    and 'left_hip' in P and 'right_hip' in P, 'P': P})
    # metric normalization per frame (detected frames only)
    for fr in out:
        if not fr['detected']:
            continue
        P = fr['P']
        hips = mid(P['left_hip'], P['right_hip'])
        if 'left_shoulder' in P and 'right_shoulder' in P:
            chest = mid(P['left_shoulder'], P['right_shoulder'])
        else:
            chest = hips + np.array([0.0, 0.5, 0.0])
        torso = np.linalg.norm(chest - hips)
        s = 0.50 / torso if torso > 1e-9 else 1.0
        fr['P'] = {k: (v - hips) * s for k, v in P.items()}
        fr['hips'] = np.zeros(3)
    return out


def interpolate_missing(frames, joint_names):
    """Linear interpolation of joint positions across undetected frames."""
    n = len(frames)
    for jn in joint_names:
        # collect known samples
        known = [(i, fr['P'][jn]) for i, fr in enumerate(frames)
                 if fr['detected'] and jn in fr['P']]
        if not known:
            continue
        for i, fr in enumerate(frames):
            if fr['detected'] and jn in fr['P']:
                continue
            # find bracketing known frames
            prev = next((k for k in reversed(range(len(known))) if known[k][0] <= i), None)
            nxt = next((k for k in range(len(known)) if known[k][0] >= i), None)
            if prev is None:
                fr['P'][jn] = known[0][1].copy()
            elif nxt is None:
                fr['P'][jn] = known[-1][1].copy()
            else:
                i0, p0 = known[prev]
                i1, p1 = known[nxt]
                a = 0.0 if i1 == i0 else (i - i0) / (i1 - i0)
                fr['P'][jn] = (1 - a) * p0 + a * p1
            fr['detected'] = fr['detected']  # keep original flag
    # mark frames usable if they now have the core joints
    core = ['left_hip', 'right_hip', 'left_shoulder', 'right_shoulder']
    for fr in frames:
        fr['usable'] = all(c in fr['P'] for c in core)
    return frames


def smooth(frames, window=3):
    if window <= 1:
        return frames
    n = len(frames)
    joints = set()
    for fr in frames:
        joints.update(fr['P'].keys())
    half = window // 2
    smoothed = []
    for i, fr in enumerate(frames):
        P = {}
        for jn in joints:
            acc = np.zeros(3)
            cnt = 0
            for k in range(max(0, i - half), min(n, i + half + 1)):
                if jn in frames[k]['P']:
                    acc += frames[k]['P'][jn]
                    cnt += 1
            P[jn] = acc / cnt if cnt else fr['P'].get(jn, np.zeros(3))
        smoothed.append({'t': fr['t'], 'detected': fr['detected'],
                         'usable': fr.get('usable', False), 'P': P})
    return smoothed


# ----------------------------------------------------------------------------
# Bone world orientations from keypoint geometry
# ----------------------------------------------------------------------------
def bone_anchors(P):
    """Map WH bone -> world joint position from keypoints."""
    def req(n):
        return P[n]
    hips = mid(req('left_hip'), req('right_hip'))
    chest = mid(req('left_shoulder'), req('right_shoulder')) \
        if 'left_shoulder' in P and 'right_shoulder' in P else hips + np.array([0, 0.5, 0])
    nose = P.get('nose', chest + np.array([0, 0.24, 0.02]))
    neck = chest + (nose - chest) * 0.45
    A = {}
    A['Root'] = hips
    A['Hips'] = hips
    A['Spine'] = hips + (chest - hips) * 0.35
    A['Chest'] = hips + (chest - hips) * 0.70
    A['Neck'] = neck
    A['Head'] = nose
    for side, s in (('Left', 'left'), ('Right', 'right')):
        sh = P.get(f'{s}_shoulder', chest)
        el = P.get(f'{s}_elbow', sh + np.array([0.25 if side == 'Left' else -0.25, -0.05, 0]))
        wr = P.get(f'{s}_wrist', el)
        idx = P.get(f'{s}_index', wr)
        hip = P.get(f'{s}_hip', hips)
        knee = P.get(f'{s}_knee', hip + np.array([0, -0.45, 0]))
        ank = P.get(f'{s}_ankle', knee + np.array([0, -0.45, 0]))
        toe = P.get(f'{s}_foot_index', ank + np.array([0, -0.02, 0.12]))
        A[f'{side}Shoulder'] = sh
        A[f'{side}Arm'] = el
        A[f'{side}ForeArm'] = wr
        A[f'{side}Hand'] = idx
        A[f'{side}UpLeg'] = hip
        A[f'{side}Leg'] = knee
        A[f'{side}Foot'] = ank
        A[f'{side}ToeBase'] = toe
    return A


def world_orientations(A):
    """Desired WORLD orientation per bone (quats, xyzw)."""
    W = {}
    # pelvis orientation from the keypoint-derived anchors
    xl = A['LeftUpLeg'] - A['RightUpLeg']
    n = np.linalg.norm(xl)
    x = xl / n if n > 1e-9 else np.array([1.0, 0.0, 0.0])
    yup = A['Chest'] - A['Hips']
    n = np.linalg.norm(yup)
    yup = yup / n if n > 1e-9 else np.array([0.0, 1.0, 0.0])
    z = np.cross(x, yup)
    n = np.linalg.norm(z)
    z = z / n if n > 1e-9 else np.array([0.0, 0.0, 1.0])
    y = np.cross(z, x)
    y = y / (np.linalg.norm(y) or 1.0)
    pelvis_q = mat_to_quat(np.column_stack([x, y, z]))

    W['Root'] = q_identity()
    W['Hips'] = pelvis_q
    for b in ('Spine', 'Chest', 'Neck', 'Head', 'LeftShoulder', 'RightShoulder'):
        W[b] = pelvis_q  # v1: rigid torso/head (documented limitation)

    for side in ('Left', 'Right'):
        # arm chain: bone vector = child anchor - own anchor
        for bone, cname in ((f'{side}Arm', f'{side}ForeArm'),
                            (f'{side}ForeArm', f'{side}Hand')):
            d = A[cname] - A[bone]
            W[bone] = swing(REST_DIRS[bone], d) if np.linalg.norm(d) > 1e-9 else q_identity()
        W[f'{side}Hand'] = W[f'{side}ForeArm']  # rigid hand in v1
        for bone, cname in ((f'{side}UpLeg', f'{side}Leg'),
                            (f'{side}Leg', f'{side}Foot'),
                            (f'{side}Foot', f'{side}ToeBase')):
            d = A[cname] - A[bone]
            W[bone] = swing(REST_DIRS[bone], d) if np.linalg.norm(d) > 1e-9 else q_identity()
        W[f'{side}ToeBase'] = W[f'{side}Foot']
    return W


def local_rotations(W):
    """World -> local (parent-relative) quats, hierarchy order."""
    L = {}
    for b in BONES:
        p = PARENTS[b]
        if p is None:
            L[b] = q_norm(W[b])
        else:
            L[b] = q_norm(q_mul(q_conj(q_norm(W[p])), q_norm(W[b])))
        L[b] = L[b] / (np.linalg.norm(L[b]) or 1.0)
    return L


# ----------------------------------------------------------------------------
# BVH writer
# ----------------------------------------------------------------------------
def write_bvh(path, frames_data, fps):
    n = len(frames_data)
    lines = []
    lines.append('# WH mocap BVH. Euler order ZXY (R = Rz*Rx*Ry), degrees.')
    lines.append('# Faces +Z, character left = +X, Y-up, meters.')
    lines.append('# Generated by tools/mocap/keypoints_to_bvh.py (heuristic v1).')
    lines.append('HIERARCHY')

    def emit(bone, depth):
        ind = '    ' * (depth + 1)
        tag = 'ROOT' if PARENTS[bone] is None else 'JOINT'
        lines.append(f'{ind}{tag} {bone}')
        lines.append(f'{ind}' + '{')
        off = (np.array(REST[bone]) - np.array(REST[PARENTS[bone]])) \
            if PARENTS[bone] else np.array(REST[bone])
        lines.append(f'{ind}    OFFSET {off[0]:.6f} {off[1]:.6f} {off[2]:.6f}')
        if PARENTS[bone] is None:
            lines.append(f'{ind}    CHANNELS 6 Xposition Yposition Zposition '
                         'Zrotation Xrotation Yrotation')
        else:
            lines.append(f'{ind}    CHANNELS 3 Zrotation Xrotation Yrotation')
        for ch in CHILDREN[bone]:
            emit(ch, depth + 1)
        if bone in END_SITES:
            e = END_SITES[bone]
            lines.append(f'{ind}    End Site')
            lines.append(f'{ind}    ' + '{')
            lines.append(f'{ind}        OFFSET {e[0]:.6f} {e[1]:.6f} {e[2]:.6f}')
            lines.append(f'{ind}    ' + '}')
        lines.append(f'{ind}' + '}')

    emit('Root', 0)
    lines.append('MOTION')
    lines.append(f'Frames: {n}')
    lines.append(f'Frame Time: {1.0 / fps:.9f}')
    for fr in frames_data:
        vals = []
        p = fr['root_pos']
        vals += [p[0], p[1], p[2]]
        for b in BONES:
            z, x, y = quat_to_euler_zxy(fr['local'][b])
            vals += [math.degrees(z), math.degrees(x), math.degrees(y)]
        lines.append(' '.join(f'{v:.4f}' for v in vals))
    with open(path, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    return path


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def convert(kp_path, bvh_path, fps=30.0, z_sign=-1.0, smooth_window=3):
    data = load_keypoints(kp_path)
    fps = float(data.get('fps', fps))
    frames = frames_to_metric(data, z_sign=z_sign)
    if not any(fr['detected'] for fr in frames):
        raise ValueError('no detected frames in keypoints file; nothing to convert')
    joint_names = set()
    for fr in frames:
        joint_names.update(fr['P'].keys())
    for core in ('left_hip', 'right_hip'):
        if not any(core in fr['P'] for fr in frames if fr['detected']):
            raise ValueError(
                f'core joint {core!r} never detected; need hips visible '
                f'(single performer, full body in frame)')
    frames = interpolate_missing(frames, joint_names)
    frames = smooth(frames, window=smooth_window)

    out = []
    root0 = None
    for fr in frames:
        A = bone_anchors(fr['P'])
        W = world_orientations(A)
        L = local_rotations(W)
        root = A['Root'].copy()
        if root0 is None:
            root0 = root.copy()
        # keep absolute height (hip height), x/z relative to first frame
        root_pos = np.array([root[0] - root0[0], root[1], root[2] - root0[2]])
        out.append({'t': fr['t'], 'root_pos': root_pos, 'local': L,
                    'anchors': A})
    write_bvh(bvh_path, out, fps)
    detected = sum(1 for fr in frames if fr['detected'])
    print(f'wrote {bvh_path}: {len(out)} frames @ {fps} fps '
          f'({detected}/{len(frames)} detected, rest interpolated)')
    return bvh_path, out


def main(argv=None):
    ap = argparse.ArgumentParser(description='wh-keypoints/1 JSON -> BVH [WIRED, CPU]')
    ap.add_argument('keypoints', help='input wh-keypoints/1 JSON')
    ap.add_argument('bvh', help='output .bvh path')
    ap.add_argument('--fps', type=float, default=30.0)
    ap.add_argument('--z-sign', type=float, default=-1.0,
                    help='sign applied to MediaPipe z (default -1: toward-camera -> +Z)')
    ap.add_argument('--smooth', type=int, default=3,
                    help='moving-average window (frames); 1 = off')
    a = ap.parse_args(argv)
    convert(a.keypoints, a.bvh, fps=a.fps, z_sign=a.z_sign,
            smooth_window=a.smooth)


if __name__ == '__main__':
    main()

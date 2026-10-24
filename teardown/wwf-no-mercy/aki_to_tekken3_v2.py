#!/usr/bin/env python3
"""AKI (No Mercy) -> Tekken 3 retarget v2.

REGENERATED from the CORRECTED animation bank (NTSC_U_11 offsets:
FileTable 0x16C31D8, FirstFile 0x1BD150). v1 was built on the misaligned
NTSC_U_10 bank and is deprecated.

Loads from animations/clips/*.npy (int16, shape [nframes, 26, 3]).
Joint order per manifest.json. PR joints: [pivot_x, rot_s8, pivot_z].
OM/MV joints: [x, y, z].

Pipeline:
1. Load NPY clip. Extract s8 rotations from PR joints (channel 1).
2. Map AKI joints -> Tekken 3 FK Euler joints.
3. Overlay: tekken(t) = stance0 + (aki(t) - mean(aki)) on X channel.
4. Root: OverallMovement -> Tekken root (scaled).
5. Output JSON.

Usage: python3 aki_to_tekken3_v2.py [fileid_hex] [out_json]
"""
import struct, sys, math, json, os
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
CLIPDIR = os.path.join(BASE, 'animations', 'clips')

FID = sys.argv[1] if len(sys.argv) > 1 else '339A'
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BASE, 'aki_to_tekken3_v2.json')

# Joint indices from manifest.json
J = {
    'Pelvis': 0, 'OverallMovement': 1, 'LowerAb': 2, 'UpperBody': 4,
    'Neck': 6, 'Head': 7,
    'LowerLeftLeg': 8, 'UpperLeftLeg': 9, 'LowerRightLeg': 17, 'UpperRightLeg': 18,
    'LowerLeftArm': 14, 'UpperLeftArm': 15, 'LowerRightArm': 21, 'UpperRightArm': 24,
}

CH_NAMES = (['root_x', 'root_y', 'root_z']
            + [f'ik{i}_{a}' for i in range(4) for a in 'xyz']
            + [f'swivel{i}' for i in range(4)]
            + [f'joint{i}_{a}' for i in range(10) for a in 'xyz'])
assert len(CH_NAMES) == 49

AKI_TO_T3 = {
    'Pelvis': 'joint0',
    'LowerAb': 'joint1', 'UpperBody': 'joint1',
    'Neck': 'joint3', 'Head': 'joint3',
    'UpperRightArm': 'joint4', 'UpperLeftArm': 'joint5',
    'LowerRightArm': 'joint6', 'LowerLeftArm': 'joint7',
    'UpperRightLeg': 'joint8', 'UpperLeftLeg': 'joint9',
    'LowerRightLeg': 'joint8', 'LowerLeftLeg': 'joint9',
}

# Load clip
clip_path = os.path.join(CLIPDIR, f'anim_{FID}.npy')
clip = np.load(clip_path)  # (nframes, 26, 3)
n = clip.shape[0]
print(f"AKI clip {FID}: {n} frames from CORRECTED bank")

# Load Tekken 3 King stance
T3DIR = os.path.expanduser('~/workspace/game-reverse-engineering/tekken3')
stance = json.load(open(os.path.join(T3DIR, 'models/king95/king95_stance0_pose.json')))
base_pose = np.array([stance['pose_channels'][c] for c in CH_NAMES], dtype=float)

# Extract s8 rotations (channel 1 of PR joints)
series = {}
for aki_joint, t3_joint in AKI_TO_T3.items():
    ji = J[aki_joint]
    vals = clip[:, ji, 1].astype(float)  # s8 rotation
    series.setdefault(t3_joint, []).append(vals)

# Root movement
root_vals = clip[:, J['OverallMovement'], :].astype(float)

S8_TO_T3 = 65536.0 / 360.0

poses = []
for fi in range(n):
    p = base_pose.copy()
    for t3_joint, vlist in series.items():
        v = np.mean(vlist, axis=0)
        delta = (v - v.mean()) * S8_TO_T3
        idx = CH_NAMES.index(t3_joint + '_x')
        p[idx] = np.clip(p[idx] + delta[fi], -32768, 32767)
    for j, ax in enumerate('xyz'):
        idx = CH_NAMES.index(f'root_{ax}')
        rv = root_vals[:, j]
        delta = (rv - rv.mean()) * 0.5
        p[idx] = np.clip(p[idx] + delta[fi], -32768, 32767)
    poses.append([int(round(x)) for x in p])

# Verification: correlation of source vs retarget
print("\nVerification (source-vs-retarget correlations):")
for aki_joint, t3_joint in [('Pelvis', 'joint0'), ('UpperBody', 'joint1'),
                             ('UpperRightArm', 'joint4'), ('Head', 'joint3')]:
    ji = J[aki_joint]
    src = clip[:, ji, 1].astype(float)
    src_c = src - src.mean()
    idx = CH_NAMES.index(t3_joint + '_x')
    dst = np.array([p[idx] for p in poses], dtype=float)
    dst_c = dst - dst.mean()
    corr = np.corrcoef(src_c, dst_c)[0, 1] if np.std(src_c) > 0 and np.std(dst_c) > 0 else 0
    print(f"  {aki_joint} -> {t3_joint}: {corr:+.3f}")

out = {
    'schema': 'aki->tekken3 retarget v2 (CORRECTED bank, NTSC_U_11)',
    'source_file': f'No Mercy anim {FID}',
    'source_frames': n,
    'source_bank': 'animations/clips/ (FileTable 0x16C31D8, NTSC_U_11)',
    'tekken_model': 'tekken3/models/king95 (King, BNS record 95)',
    'joint_map': AKI_TO_T3,
    'note': 'v1 (aki_to_tekken3_v1.json) was built on misaligned NTSC_U_10 bank; use v2.',
    'poses': poses,
}
json.dump(out, open(OUT, 'w'))
print(f"\nWrote {OUT}: {n} poses")

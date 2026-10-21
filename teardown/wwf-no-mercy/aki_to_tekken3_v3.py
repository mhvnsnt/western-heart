#!/usr/bin/env python3
"""AKI (No Mercy) -> Tekken 3 retarget v3.

Extends aki_to_tekken3_v2.py (same joint map, same stance overlay, same
root handling) with one measured correction and batch support:

* **s8 unwrap (NEW in v3)**: the AKI rotation channel is an angle modulo
  256 units (256 = 360 deg) stored as s8. Clips whose joints rotate past
  +-127 wrap mid-clip (measured: system clip 0x2DDA pelvis reads
  105, 121, 121, -103, 121, -103 — smooth only modulo 256). v2 averaged
  and overlaid the wrapped values, injecting phantom ~224 deg swings.
  v3 unwraps each joint series (period 256) before the overlay.
  Measured effect on MK-1240 (Rock Bottom, anim 0x37FA) through the
  bit-exact PoseBuildMatrices port (usa_tables.pose_to_slot_rotations):
  mean slot rotation delta 53.5 -> 25.8 deg/frame (real T3 King stance
  stream: 2.4). The remaining gap is NOT noise — it is the known v1/v2
  scope limit: T3 arm/leg segments are IK-driven (PoseBuildMatrices
  overwrites slots 4,5,8,9,12,13,15,16 from IK target channels), so
  limb motion needs AKI FK -> T3 IK targets, which requires the AKI
  player-code FK. See AKI-TEKKEN3-RETARGET.md (v3 section) and
  docs/anim/AKI-BAKE-ROCK-2026-10-21.md before consuming these poses
  as playable clips.

* Stance pose is read from this repo (teardown/tekken3/models/king95/
  king95_stance0_pose.json) instead of the old game-reverse-engineering
  path v2 used.

Usage:
  python3 aki_to_tekken3_v3.py                  # the CornerStone Rock set
  python3 aki_to_tekken3_v3.py 37FA [out.json]   # one clip by file id
"""
import json, os, sys
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(BASE, '..', '..'))
CLIPDIR = os.path.join(BASE, 'animations', 'clips')
STANCE = os.path.join(REPO, 'teardown', 'tekken3', 'models', 'king95',
                      'king95_stance0_pose.json')
OUTDIR = os.path.join(BASE, 'aki-rock-v3')

# The CornerStone Rock set: mat-kings MK id -> No Mercy file id.
# (moveset-library/movesets/mat-kings-move-database.json; wired from
# game/assets/movesets/ryuji-rock.json, anim_ref mk:MK-####.)
ROCK_SET = {
    'MK-1240': '37FA',  # Rock Bottom (P1)
    'MK-2843': '3E3D',  # People's Elbow (P1, grounded)
    'MK-3473': '40B3',  # People's Elbow (running)
    'MK-4353': '4423',  # Rock Taunt 01 (primary taunt ref)
    'MK-4347': '441D',  # Rock Taunt 02
    'MK-4354': '4424',  # Rock Taunt 03
    'MK-4233': '43AB',  # Rock Entry Way taunt
    'MK-4269': '43CF',  # Rock In The Ring taunt
    'MK-1885': '3A7F',  # Rock Spinebuster
    'MK-3120': '3F52',  # Rock Stomp
    'MK-3659': '416D',  # Rock Spinning DDT
}

# Joint indices from animations/manifest.json
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

S8_TO_T3 = 65536.0 / 360.0


def convert(fid):
    """One AKI clip -> v3 pose dict (49-channel s16 pose vectors)."""
    clip = np.load(os.path.join(CLIPDIR, f'anim_{fid}.npy'))  # (nframes, 26, 3)
    n = clip.shape[0]
    stance = json.load(open(STANCE))
    base_pose = np.array([stance['pose_channels'][c] for c in CH_NAMES], dtype=float)

    # s8 rotations (channel 1 of PR joints), unwrapped modulo 256.
    series = {}
    for aki_joint, t3_joint in AKI_TO_T3.items():
        vals = clip[:, J[aki_joint], 1].astype(float)
        vals = np.unwrap(vals, period=256.0)
        series.setdefault(t3_joint, []).append(vals)

    root_vals = clip[:, J['OverallMovement'], :].astype(float)

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

    # Verification: correlation of (unwrapped) source vs retarget channel.
    corr = {}
    for aki_joint, t3_joint in [('Pelvis', 'joint0'), ('UpperBody', 'joint1'),
                                ('UpperRightArm', 'joint4'), ('Head', 'joint3')]:
        src = np.unwrap(clip[:, J[aki_joint], 1].astype(float), period=256.0)
        src_c = src - src.mean()
        idx = CH_NAMES.index(t3_joint + '_x')
        dst = np.array([p[idx] for p in poses], dtype=float)
        dst_c = dst - dst.mean()
        corr[f'{aki_joint}->{t3_joint}'] = (
            round(float(np.corrcoef(src_c, dst_c)[0, 1]), 3)
            if np.std(src_c) > 0 and np.std(dst_c) > 0 else 0.0)

    return {
        'schema': 'aki->tekken3 retarget v3 (CORRECTED bank NTSC_U_11 + s8 unwrap)',
        'source_file': f'No Mercy anim {fid}',
        'source_frames': n,
        'source_bank': 'animations/clips/ (FileTable 0x16C31D8, NTSC_U_11)',
        'tekken_model': 'tekken3/models/king95 (King, BNS record 95)',
        'joint_map': AKI_TO_T3,
        'unwrap': 'per-joint s8 series unwrapped modulo 256 before overlay (v3 fix)',
        'verification_channel_correlations': corr,
        'poses': poses,
    }


def main():
    if len(sys.argv) > 1:
        fid = sys.argv[1].upper()
        out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BASE, f'aki_to_tekken3_v3_{fid}.json')
        res = convert(fid)
        json.dump(res, open(out, 'w'))
        print(f'{fid}: {res["source_frames"]} poses -> {out}  corr={res["verification_channel_correlations"]}')
        return
    os.makedirs(OUTDIR, exist_ok=True)
    for mk, fid in ROCK_SET.items():
        res = convert(fid)
        res['mat_kings_id'] = mk
        out = os.path.join(OUTDIR, f'{mk.lower()}-anim_{fid}.json')
        json.dump(res, open(out, 'w'))
        print(f'{mk} anim_{fid}: {res["source_frames"]} poses -> {out}  corr={res["verification_channel_correlations"]}')


if __name__ == '__main__':
    main()

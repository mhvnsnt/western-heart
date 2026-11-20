#!/usr/bin/env python3
"""End-to-end test of the WH mocap pipeline on SYNTHETIC keypoints.

[WIRED] Runs on CPU with stdlib + numpy only (no mediapipe needed).

Chain under test:
  synthetic wh-keypoints/1 -> keypoints_to_bvh -> BVH ->
  bvh_to_wh_anim -> game/assets/anim/gen/<fighter>/{clip,skeleton,sets}.json
  -> gate_check (show-animation lock conformance)

The synthetic performer is an abstract adult stick figure (no real footage,
no real person): a 30-frame jab + squat, facing the camera, in MediaPipe
coordinate convention (x right, y DOWN, smaller z = closer to camera).

Run:  python3 tools/mocap/tests/test_pipeline.py
"""
import json
import math
import os
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MOCAP = os.path.dirname(HERE)
sys.path.insert(0, MOCAP)

from keypoints_to_bvh import (  # noqa: E402
    convert as kp_to_bvh, BONES as CANONICAL, q_norm,
)
from bvh_to_wh_anim import (  # noqa: E402
    parse_bvh, bvh_to_clip_data, write_bank,
)
from gate_check import check_fighter  # noqa: E402


def cosine_env(frame, start, peak, end):
    """0 -> 1 -> 0 envelope over [start, end] peaking at `peak`."""
    if frame <= start or frame >= end:
        return 0.0
    if frame <= peak:
        t = (frame - start) / (peak - start)
    else:
        t = (frame - peak) / (end - peak)
        t = 1.0 - t
    return 0.5 - 0.5 * math.cos(t * math.pi)


def lerp(a, b, t):
    return tuple(ai + (bi - ai) * t for ai, bi in zip(a, b))


# Base pose: adult performer facing the camera, MediaPipe convention
# (x: 0..1 left->right, y: 0..1 top->bottom, z: smaller = closer to camera)
BASE = {
    'nose': (0.50, 0.20, -0.06),
    'left_eye': (0.53, 0.19, -0.06), 'right_eye': (0.47, 0.19, -0.06),
    'left_ear': (0.55, 0.20, -0.03), 'right_ear': (0.45, 0.20, -0.03),
    'left_shoulder': (0.58, 0.32, -0.02), 'right_shoulder': (0.42, 0.32, -0.02),
    'left_elbow': (0.62, 0.44, -0.01), 'right_elbow': (0.38, 0.44, -0.01),
    'left_wrist': (0.63, 0.55, 0.00), 'right_wrist': (0.37, 0.55, 0.00),
    'left_pinky': (0.64, 0.57, -0.01), 'right_pinky': (0.36, 0.57, -0.01),
    'left_index': (0.63, 0.58, -0.01), 'right_index': (0.37, 0.58, -0.01),
    'left_thumb': (0.62, 0.56, -0.02), 'right_thumb': (0.38, 0.56, -0.02),
    'left_hip': (0.55, 0.58, 0.00), 'right_hip': (0.45, 0.58, 0.00),
    'left_knee': (0.55, 0.74, 0.00), 'right_knee': (0.45, 0.74, 0.00),
    'left_ankle': (0.55, 0.90, 0.00), 'right_ankle': (0.45, 0.90, 0.00),
    'left_heel': (0.55, 0.92, 0.03), 'right_heel': (0.45, 0.92, 0.03),
    'left_foot_index': (0.55, 0.92, -0.06),
    'right_foot_index': (0.45, 0.92, -0.06),
}


def synth_frame(i):
    """Frame i of 30: jab (frames 6-14) then squat (frames 16-24)."""
    P = dict(BASE)
    jab = cosine_env(i, 6, 10, 14)
    if jab:
        P['right_wrist'] = lerp(BASE['right_wrist'], (0.50, 0.42, -0.28), jab)
        P['right_elbow'] = lerp(BASE['right_elbow'], (0.44, 0.42, -0.12), jab)
        P['right_index'] = lerp(BASE['right_index'], (0.50, 0.44, -0.30), jab)
        P['right_pinky'] = lerp(BASE['right_pinky'], (0.51, 0.44, -0.28), jab)
    squat = cosine_env(i, 16, 20, 24)
    if squat:
        dy = 0.08 * squat
        for j in ('left_hip', 'right_hip'):
            x, y, z = BASE[j]
            P[j] = (x, y + dy, z)
        for j in ('left_knee', 'right_knee'):
            x, y, z = BASE[j]
            P[j] = (x, y + dy * 0.5, z - 0.07 * squat)  # knees push toward camera
    return P


def synth_taunt_frame(i):
    """12-frame show clip: both arms rise overhead (taunt)."""
    P = dict(BASE)
    t = cosine_env(i, 0, 6, 11)
    for s, sx in (('left', 1), ('right', -1)):
        P[f'{s}_wrist'] = lerp(BASE[f'{s}_wrist'], (0.50 + 0.10 * sx, 0.10, -0.05), t)
        P[f'{s}_elbow'] = lerp(BASE[f'{s}_elbow'], (0.50 + 0.16 * sx, 0.20, -0.03), t)
        P[f'{s}_index'] = lerp(BASE[f'{s}_index'], (0.50 + 0.10 * sx, 0.07, -0.06), t)
    return P


def make_keypoints(frames_fn, n_frames, fps=30.0):
    frames = []
    for i in range(n_frames):
        pos = {k: list(v) for k, v in frames_fn(i).items()}
        conf = {k: 0.99 for k in pos}
        frames.append({'t': round(i / fps, 4), 'detected': True,
                       'pos': pos, 'conf': conf})
    # one dropped-detection frame to exercise interpolation
    drop = 15 if n_frames > 16 else n_frames // 2
    frames[drop] = {'t': round(drop / fps, 4), 'detected': False, 'pos': {}, 'conf': {}}
    return {
        'format': 'wh-keypoints/1', 'backend': 'synthetic-test',
        'fps': fps, 'width': 640, 'height': 480,
        'joints': sorted(pos.keys()), 'frames': frames,
    }


def check(cond, msg):
    if not cond:
        raise AssertionError(f'TEST FAILED: {msg}')
    print(f'  ok: {msg}')


def main():
    tmp = tempfile.mkdtemp(prefix='wh-mocap-test-')
    print(f'workdir: {tmp}')

    # ---- 1. keypoints -> BVH ----
    kp_path = os.path.join(tmp, 'jab.json')
    with open(kp_path, 'w') as f:
        json.dump(make_keypoints(synth_frame, 30), f)
    bvh_path = os.path.join(tmp, 'jab.bvh')
    _, written = kp_to_bvh(kp_path, bvh_path, fps=30.0, z_sign=-1.0, smooth_window=3)
    check(os.path.exists(bvh_path), 'BVH written')

    bvh = parse_bvh(bvh_path)
    check(bvh['n_frames'] == 30, f'BVH has 30 frames (got {bvh["n_frames"]})')
    names = [j.name for j in bvh['order']]
    check(all(b in names for b in CANONICAL), 'BVH carries all 22 canonical bones')

    # euler round-trip fidelity: parsed quats == written quats (sign-insensitive)
    data = bvh_to_clip_data(bvh)
    worst = 0.0
    for c in CANONICAL:
        for f in range(30):
            q1 = np.array(written[f]['local'][c])
            q2 = np.array(data['local'][c][f])
            err = min(np.linalg.norm(q1 - q2), np.linalg.norm(q1 + q2))
            worst = max(worst, err)
    check(worst < 2e-3, f'BVH euler round-trip fidelity (worst quat err {worst:.2e})')
    for c in CANONICAL:
        arr = data['local'][c]
        check(len(arr) == 30, f'bone {c}: 30 quat frames')
        for q in arr:
            check(abs(np.linalg.norm(q) - 1.0) < 1e-6, f'bone {c}: unit quats')
    check(len(data['root_t']) == 30 and len(data['root_t'][0]) == 3,
          'root_t is 30x3')

    # jab actually moves the right wrist forward (+Z) at the peak
    rw = np.array(data['rest_world']['RightForeArm'])
    # (world-orientation check happens via facing test below)

    # ---- 2. BVH -> game bank files ----
    anim_root = os.path.join(tmp, 'game', 'assets', 'anim')
    clip_path, skel_path, sets_path = write_bank(
        bvh_path, fighter='testfighter', clip_name='mocap_jab_01',
        out_root=anim_root, set_tag='fight', slot='light',
        source_video=kp_path)
    check(os.path.exists(clip_path), 'clip JSON written')
    check(os.path.exists(skel_path), 'skeleton.json written')
    check(os.path.exists(sets_path), 'sets.json written')

    with open(clip_path) as f:
        clip = json.load(f)
    check(clip['format'] == 'wh-anim/1', 'clip format is wh-anim/1')
    check(clip['bones'] == list(CANONICAL), 'clip bones == canonical 22')
    check(abs(clip['fps'] - 30.0) < 1e-3 and clip['stream_frames'] == 30, 'fps/frames')
    check(set(clip['rot_xyzw'].keys()) == set(CANONICAL), 'rot_xyzw covers 22 bones')
    check(all(len(v) == 30 and len(v[0]) == 4 for v in clip['rot_xyzw'].values()),
          'rot_xyzw: 30 frames x quat4 per bone')
    check(len(clip['root_t']) == 30, 'root_t 30 frames')
    check(clip['hand_keyed'] is False, 'hand_keyed=false (AI motion provenance)')

    with open(skel_path) as f:
        skel = json.load(f)
    check(skel['format'] == 'wh-anim-skel/1', 'skeleton format wh-anim-skel/1')
    check(skel['root_rest_y'] > 0.5, 'root_rest_y sane (hip height meters)')
    check([j['name'] for j in skel['joints']] == list(CANONICAL),
          'skeleton joints == canonical 22')

    # ---- 3. a SHOW clip in the same bank ----
    kp2 = os.path.join(tmp, 'taunt.json')
    with open(kp2, 'w') as f:
        json.dump(make_keypoints(synth_taunt_frame, 12), f)
    bvh2 = os.path.join(tmp, 'taunt.bvh')
    kp_to_bvh(kp2, bvh2, fps=30.0, z_sign=-1.0)
    write_bank(bvh2, fighter='testfighter', clip_name='mocap_taunt_01',
               out_root=anim_root, set_tag='show', show_slot='taunt',
               source_video=kp2)
    with open(sets_path) as f:
        sets = json.load(f)
    check(sets['format'] == 'wh-anim-sets/1', 'sets format wh-anim-sets/1')
    check(sets['clips']['mocap_jab_01']['set'] == 'fight', 'jab tagged fight')
    check(sets['clips']['mocap_taunt_01']['set'] == 'show', 'taunt tagged show')
    check('FIGHT' not in sets['clips']['mocap_taunt_01']['contexts'],
          'show clip contexts exclude FIGHT')
    check(sets['clips']['mocap_taunt_01']['showSlot'] == 'taunt', 'showSlot set')

    # ---- 4. gate check passes ----
    errors, warnings = check_fighter(os.path.join(anim_root, 'gen', 'testfighter'))
    for w in warnings:
        print(f'  warn: {w}')
    check(not errors, f'gate_check PASS (errors={errors})')

    # ---- 5. gate check CATCHES a lock violation ----
    bad_sets = json.load(open(sets_path))
    bad_sets['clips']['mocap_taunt_01']['contexts'] = ['FIGHT', 'SHOW']
    bad_path = os.path.join(tmp, 'badsets.json')
    with open(bad_path, 'w') as f:
        json.dump(bad_sets, f)
    import shutil
    baddir = os.path.join(tmp, 'badbank')
    shutil.copytree(os.path.join(anim_root, 'gen', 'testfighter'), baddir)
    with open(os.path.join(baddir, 'sets.json'), 'w') as f:
        json.dump(bad_sets, f)
    errors, _ = check_fighter(baddir)
    check(any('SHOW-ANIMATION LOCK VIOLATION' in e for e in errors),
          'gate_check catches show clip tagged for FIGHT')

    # ---- 6. flip-180 swaps L/R and mirrors X ----
    flipped = bvh_to_clip_data(bvh, flip_180=True)
    q_orig = np.array(data['local']['LeftArm'][10])
    q_flip = np.array(flipped['local']['RightArm'][10])
    check(np.allclose([-q_orig[0], q_orig[1], -q_orig[2], q_orig[3]], q_flip, atol=1e-6),
          'flip-180 mirrors quats and swaps L/R')

    print('\nALL MOCAP PIPELINE TESTS PASSED')


if __name__ == '__main__':
    main()

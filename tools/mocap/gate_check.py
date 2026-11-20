#!/usr/bin/env python3
"""Offline conformance check for generated animation banks.

[WIRED] Runs on CPU, no GPU needed. Pure stdlib (+numpy for the facing check).

Mirrors the runtime rules in game/js/anim-gate.js (the owner-mandated
SHOW-ANIMATION LOCK, 2026-10-23) and the facing check in bankFacing():

  1. sets.json parses as wh-anim-sets/1.
  2. Every clip entry has set in {"fight", "show"}.
  3. A "show" clip MUST NOT list FIGHT in contexts, and must name a showSlot.
     (anim-gate.js: show_to_fight may never allow FIGHT.)
  4. Every clip file exists, parses as wh-anim/1, and carries the bones the
     retarget needs (retargetT3Clips delta list).
  5. All rot_xyzw quaternions are unit length (tolerance 1e-3); frame counts
     are consistent across bones and match stream_frames and root_t.
  6. Facing sanity (bankFacing twin): knees bend toward +Z on average, i.e.
     the bank really faces +Z / character-left = +X as skeleton.json claims.
     Warns (does not fail) if the bank looks turned; fix with
     bvh_to_wh_anim.py --flip-180.

Exit 0 = PASS, 1 = FAIL. Intended for CI on every gen/ bank change.
Usage: gate_check.py game/assets/anim/gen/<fighter>
"""
import json
import math
import os
import sys

import numpy as np

REQUIRED_BY_RETARGET = [
    'Hips', 'Chest', 'Head',
    'LeftShoulder', 'LeftArm', 'LeftForeArm', 'LeftHand',
    'RightShoulder', 'RightArm', 'RightForeArm', 'RightHand',
    'LeftUpLeg', 'LeftLeg', 'LeftFoot',
    'RightUpLeg', 'RightLeg', 'RightFoot',
]

CTX = {'FIGHT', 'INTRO_OUTRO', 'CUTSCENE', 'SHOW'}


def fail(msg, errors):
    errors.append(msg)


def check_fighter(fighter_dir):
    errors, warnings = [], []
    sets_path = os.path.join(fighter_dir, 'sets.json')
    if not os.path.exists(sets_path):
        return [f'missing sets.json in {fighter_dir}'], []
    with open(sets_path) as f:
        sets = json.load(f)
    if sets.get('format') != 'wh-anim-sets/1':
        fail(f'sets.json: bad format {sets.get("format")!r} (want wh-anim-sets/1)', errors)

    skel_path = os.path.join(fighter_dir, 'skeleton.json')
    skel = None
    if os.path.exists(skel_path):
        with open(skel_path) as f:
            skel = json.load(f)
        if skel.get('format') != 'wh-anim-skel/1':
            fail('skeleton.json: bad format (want wh-anim-skel/1)', errors)
    else:
        warnings.append('no skeleton.json (retarget needs it to map rest dirs)')

    clips = sets.get('clips', {})
    if not clips:
        warnings.append('sets.json lists no clips')
    for name, entry in clips.items():
        set_tag = entry.get('set')
        if set_tag not in ('fight', 'show'):
            fail(f'{name}: set must be fight|show, got {set_tag!r}', errors)
            continue
        contexts = entry.get('contexts', [])
        bad = [c for c in contexts if c not in CTX]
        if bad:
            fail(f'{name}: unknown contexts {bad}', errors)
        # THE lock: show clips may never be tagged for FIGHT
        if set_tag == 'show':
            if 'FIGHT' in contexts:
                fail(f'{name}: SHOW-ANIMATION LOCK VIOLATION: show clip lists FIGHT context', errors)
            if not entry.get('showSlot'):
                fail(f'{name}: show clip needs a showSlot', errors)
        clip_path = os.path.join(fighter_dir, entry.get('file', ''))
        if not os.path.exists(clip_path):
            fail(f'{name}: clip file missing: {entry.get("file")}', errors)
            continue
        with open(clip_path) as f:
            clip = json.load(f)
        if clip.get('format') != 'wh-anim/1':
            fail(f'{name}: bad clip format {clip.get("format")!r}', errors)
            continue
        rot = clip.get('rot_xyzw', {})
        missing = [b for b in REQUIRED_BY_RETARGET if b not in rot]
        if missing:
            fail(f'{name}: clip missing retarget bones {missing}', errors)
        n = clip.get('stream_frames', 0)
        for b, arr in rot.items():
            if len(arr) != n:
                fail(f'{name}: bone {b} has {len(arr)} frames, stream_frames={n}', errors)
            for q in arr:
                if abs(math.sqrt(sum(v * v for v in q)) - 1.0) > 1e-3:
                    fail(f'{name}: bone {b} has non-unit quaternion', errors)
                    break
        rt = clip.get('root_t', [])
        if len(rt) != n:
            fail(f'{name}: root_t has {len(rt)} frames, stream_frames={n}', errors)

    # facing sanity across all fight clips (bankFacing twin)
    if skel:
        fwd = facing_report(fighter_dir, sets, skel)
        if fwd is not None:
            if fwd < 0:
                warnings.append(
                    f'facing check: knees bend toward -Z (mean {fwd:.3f}); bank looks '
                    f'TURNED 180 deg. Re-run bvh_to_wh_anim.py --flip-180.')
            else:
                print(f'facing check: OK (knees forward, mean {fwd:.3f})')
    return errors, warnings


def facing_report(fighter_dir, sets, skel):
    """Mean forward component of knee offset from hip-ankle midline (>0 = +Z)."""
    P = {j['name']: np.array(j['rest']) for j in skel['joints']}
    par = {j['name']: j['parent'] for j in skel['joints']}
    order = [j['name'] for j in skel['joints']]

    def qmul(a, b):
        ax, ay, az, aw = a
        bx, by, bz, bw = b
        return np.array([aw * bx + ax * bw + ay * bz - az * by,
                         aw * by - ax * bz + ay * bw + az * bx,
                         aw * bz + ax * by - ay * bx + az * bw,
                         aw * bw - ax * bx - ay * by - az * bz])

    def qrot(q, v):
        x, y, z, w = q
        tx, ty, tz = 2 * (y * v[2] - z * v[1]), 2 * (z * v[0] - x * v[2]), 2 * (x * v[1] - y * v[0])
        return np.array([v[0] + w * tx + (y * tz - z * ty),
                         v[1] + w * ty + (z * tx - x * tz),
                         v[2] + w * tz + (x * ty - y * tx)])

    fwd_sum, samples = 0.0, 0
    for name, entry in sets.get('clips', {}).items():
        if entry.get('set') != 'fight':
            continue
        with open(os.path.join(fighter_dir, entry['file'])) as f:
            clip = json.load(f)
        rot = clip['rot_xyzw']
        n = max((len(v) for v in rot.values()), default=0)
        for fi in range(n):
            G, X = {}, {}
            for j in order:
                r = rot.get(j)
                q = np.array(r[min(fi, len(r) - 1)]) if r else np.array([0, 0, 0, 1])
                p = par[j]
                if p and p in G:
                    G[j] = qmul(G[p], q)
                    o = qrot(G[p], P[j] - P[p])
                    X[j] = X[p] + o
                else:
                    G[j] = q
                    X[j] = P[j].copy()
            if 'Hips' not in G:
                continue
            hx = qrot(G['Hips'], np.array([1.0, 0.0, 0.0]))
            fx, fz = -hx[2], hx[0]
            fl = math.hypot(fx, fz)
            if fl < 1e-6:
                continue
            fx, fz = fx / fl, fz / fl
            for s in ('Left', 'Right'):
                try:
                    a, k, e = X[f'{s}UpLeg'], X[f'{s}Leg'], X[f'{s}Foot']
                except KeyError:
                    continue
                ox, oz = k[0] - (a[0] + e[0]) / 2, k[2] - (a[2] + e[2]) / 2
                fwd_sum += ox * fx + oz * fz
                samples += 1
    return (fwd_sum / samples) if samples else None


def main(argv=None):
    ap = __import__('argparse').ArgumentParser(
        description='offline anim-gate conformance for a gen/ fighter bank [WIRED, CPU]')
    ap.add_argument('fighter_dir', help='e.g. game/assets/anim/gen/law')
    a = ap.parse_args(argv)
    errors, warnings = check_fighter(a.fighter_dir)
    for w in warnings:
        print(f'WARN: {w}')
    if errors:
        print(f'FAIL: {len(errors)} error(s):')
        for e in errors:
            print(f'  - {e}')
        return 1
    print(f'PASS: {a.fighter_dir}')
    return 0


if __name__ == '__main__':
    sys.exit(main())

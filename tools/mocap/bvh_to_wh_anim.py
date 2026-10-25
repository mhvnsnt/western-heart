#!/usr/bin/env python3
"""Stage 3 of the WH mocap pipeline: BVH -> game animation bank files.

[WIRED] Runs on CPU, no GPU needed. Tested end-to-end on synthetic data
(see tests/test_pipeline.py).

Reads a BVH (ours from keypoints_to_bvh.py, or any standard BVH via
--bone-map) and writes the game's animation bank layout for one fighter:

  game/assets/anim/gen/<fighter>/
    <clip>.json      # wh-anim/1 clip (bones + rot_xyzw quats + root_t)
    skeleton.json    # wh-anim-skel/1 rest pose (created once, reused)
    sets.json        # wh-anim-sets/1 FIGHT/SHOW set tags (merged)

The clip format matches what game/js/t3anims.js jsonToClip() reads:
  - format "wh-anim/1", fps, stream_frames
  - bones: the 22 canonical names (== T3_BONES)
  - rot_xyzw: { bone: [[x,y,z,w], ...] } per frame, quaternions
  - root_t: [[x,y,z], ...] per frame, meters (kept for lateralDx etc.;
    the game drives in-fight positioning itself, same as T3 banks)

SHOW-ANIMATION LOCK (owner law 2026-10-23): generated clips are tagged in
sets.json as "fight" or "show". The runtime gate is game/js/anim-gate.js:
a clip tagged show may NEVER play in FIGHT context. tools/mocap/gate_check.py
enforces the same rules offline. A show move enters a fighter's moveset only
with the owner's explicit approval (it is NOT automatic).

Facing: input is assumed to face +Z (character left = +X), the same
declaration as the T3 banks. Use --flip-180 if your BVH faces -Z (applies
the same (x,y,z)->(-x,y,-z) + L/R swap the game uses for turned banks).
"""
import argparse
import datetime
import hashlib
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keypoints_to_bvh import (  # noqa: E402
    BONES, PARENTS, CHILDREN, REST, q_norm, q_conj, q_mul,
    euler_zxy_to_quat, mat_to_quat,
)

CANONICAL = list(BONES)
# bones the retarget's delta() pass reads (game/js/t3anims.js retargetT3Clips)
REQUIRED_BY_RETARGET = [
    'Hips', 'Chest', 'Head',
    'LeftShoulder', 'LeftArm', 'LeftForeArm', 'LeftHand',
    'RightShoulder', 'RightArm', 'RightForeArm', 'RightHand',
    'LeftUpLeg', 'LeftLeg', 'LeftFoot',
    'RightUpLeg', 'RightLeg', 'RightFoot',
]


# ----------------------------------------------------------------------------
# Minimal BVH parser (hierarchy + motion; euler orders from CHANNELS tokens)
# ----------------------------------------------------------------------------
class BvhJoint:
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.offset = np.zeros(3)
        self.channels = []  # e.g. ['Xposition','Yposition','Zposition',
                            #        'Zrotation','Xrotation','Yrotation']
        self.children = []


def parse_bvh(path):
    with open(path) as f:
        raw = f.read()
    toks = []
    for line in raw.splitlines():
        line = line.split('#')[0]
        toks += line.replace('{', ' { ').replace('}', ' } ').split()
    i = [0]

    def take():
        v = toks[i[0]]
        i[0] += 1
        return v

    def expect(v):
        t = take()
        assert t == v, f'BVH parse: expected {v!r}, got {t!r}'

    joints = []

    def parse_joint(parent):
        tag = take()  # ROOT or JOINT
        assert tag in ('ROOT', 'JOINT'), f'bad joint tag {tag!r}'
        name = take()
        j = BvhJoint(name, parent)
        joints.append(j)
        expect('{')
        while True:
            t = take()
            if t == '}':
                break
            elif t == 'OFFSET':
                j.offset = np.array([float(take()), float(take()), float(take())])
            elif t == 'CHANNELS':
                n = int(take())
                j.channels = [take() for _ in range(n)]
            elif t == 'JOINT':
                i[0] -= 1  # push back; parse_joint re-reads tag
                child = parse_joint(j)
                j.children.append(child)
            elif t == 'End':
                site = take()
                assert site == 'Site', f'bad End Site: {site!r}'
                expect('{')
                while take() != '}':
                    pass
            else:
                raise ValueError(f'BVH parse: unexpected token {t!r}')
        return j

    root = None
    # skip to HIERARCHY
    while take() != 'HIERARCHY':
        pass
    root = parse_joint(None)
    expect('MOTION')
    assert take() == 'Frames:'
    n_frames = int(take())
    assert take() == 'Frame'
    assert take() == 'Time:'
    frame_time = float(take())

    # channel layout in file order (depth-first)
    order = []

    def walk(j):
        order.append(j)
        for c in j.children:
            walk(c)
    walk(root)
    per_frame = sum(len(j.channels) for j in order)
    values = []
    for _ in range(n_frames):
        row = [float(take()) for _ in range(per_frame)]
        values.append(row)
    return {'root': root, 'joints': joints, 'order': order,
            'n_frames': n_frames, 'fps': 1.0 / frame_time,
            'motion': values}




def euler_channels_to_quat(channels, vals):
    """Rebuild a local quat from one joint's channel values.

    Rotation composition follows the file's channel order as INTRINSIC
    rotations: for [Zrotation, Xrotation, Yrotation] the matrix is
    R = Rz*Rx*Ry (matching what keypoints_to_bvh.py writes; also stated in
    the BVH header comment). Position channels are consumed and ignored.
    """
    from keypoints_to_bvh import q_from_axis_angle
    rots = []
    it = iter(vals)
    for ch in channels:
        v = next(it)
        if ch == 'Xposition' or ch == 'Yposition' or ch == 'Zposition':
            continue
        rad = math.radians(v)
        if ch == 'Xrotation':
            rots.append(q_from_axis_angle((1, 0, 0), rad))
        elif ch == 'Yrotation':
            rots.append(q_from_axis_angle((0, 1, 0), rad))
        elif ch == 'Zrotation':
            rots.append(q_from_axis_angle((0, 0, 1), rad))
        else:
            raise ValueError(f'unknown channel {ch!r}')
    q = np.array([0.0, 0.0, 0.0, 1.0])
    for r in rots:
        q = q_mul(q, r)  # intrinsic order: q = qz*qx*qy -> R = Rz*Rx*Ry
    return q_norm(q)


def bvh_to_clip_data(bvh, bone_map=None, flip_180=False):
    order = bvh['order']
    name_of = {j.name: j for j in order}
    # map file joint names -> canonical bone names
    f2c = {}
    if bone_map:
        with open(bone_map) as f:
            bm = json.load(f)
        for canon, src in bm.items():
            f2c[src] = canon
    else:
        for j in order:
            if j.name in CANONICAL:
                f2c[j.name] = j.name
    missing = [c for c in CANONICAL if c not in f2c.values()]
    if missing:
        raise ValueError(f'BVH is missing canonical bones: {missing} '
                         f'(supply --bone-map for foreign rigs)')

    c2f = {c: f for f, c in f2c.items()}
    n = bvh['n_frames']
    # per-frame local quats keyed by canonical bone
    local = {c: [] for c in CANONICAL}
    root_t = []
    for row in bvh['motion']:
        p = 0
        frame_q = {}
        root_pos = None
        for j in order:
            nc = len(j.channels)
            vals = row[p:p + nc]
            p += nc
            pos_vals = []
            q = euler_channels_to_quat(j.channels, vals)
            k = 0
            for ch in j.channels:
                if ch in ('Xposition', 'Yposition', 'Zposition'):
                    pos_vals.append(vals[k])
                k += 1
            frame_q[j.name] = q
            if j.parent is None and pos_vals:
                root_pos = pos_vals
        for c in CANONICAL:
            local[c].append(frame_q[c2f[c]])
        root_t.append(root_pos if root_pos else [0.0, 0.0, 0.0])

    # world rest positions from offsets (for skeleton.json)
    rest_world = {}

    def walk(j, acc):
        rest_world[j.name] = acc + j.offset
        for c in j.children:
            walk(c, rest_world[j.name])
    walk(bvh['root'], np.zeros(3))

    if flip_180:
        # (x,y,z) -> (-x,y,-z); quat (x,y,z,w) -> (-x,y,-z,w); swap L/R names
        def swap(n):
            return n.replace('Left', '\x00').replace('Right', 'Left').replace('\x00', 'Right')
        new_local = {}
        for c in CANONICAL:
            nc = swap(c)
            new_local[nc] = [[-q[0], q[1], -q[2], q[3]] for q in local[c]]
        local = new_local
        root_t = [[-t[0], t[1], -t[2]] for t in root_t]
        rest_world = {swap(k): np.array([-v[0], v[1], -v[2]])
                      for k, v in rest_world.items()}

    return {'local': local, 'root_t': root_t, 'rest_world': rest_world,
            'fps': bvh['fps'], 'n_frames': n}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def write_bank(bvh_path, fighter, clip_name, out_root, set_tag='fight',
               contexts=None, slot=None, show_slot=None, source_video=None,
               flip_180=False, bone_map=None, fps_override=0.0):
    bvh = parse_bvh(bvh_path)
    data = bvh_to_clip_data(bvh, bone_map=bone_map, flip_180=flip_180)
    n = data['n_frames']
    fps = float(fps_override) if fps_override else float(data['fps'])

    fighter_dir = os.path.join(out_root, 'gen', fighter)
    os.makedirs(fighter_dir, exist_ok=True)

    # ---- clip JSON (wh-anim/1) ----
    rot = {}
    for c in CANONICAL:
        rot[c] = [[float(q[0]), float(q[1]), float(q[2]), float(q[3])]
                  for q in data['local'][c]]
    clip = {
        'format': 'wh-anim/1',
        'source': ('AI mocap from reference video '
                   + (source_video or bvh_path)),
        'bank': f'gen/mocap/{fighter}',
        'slot': clip_name,
        'fps': fps,
        'stream_frames': n,
        'hand_keyed': False,
        'bones': list(CANONICAL),
        'rot_xyzw': rot,
        'root_t': [[float(v) for v in t] for t in data['root_t']],
        'tool': 'tools/mocap/bvh_to_wh_anim.py (BVH -> wh-anim/1)',
        'sha256': {
            'source_bvh': sha256_file(bvh_path),
            **({'source_video': sha256_file(source_video)}
               if source_video and os.path.exists(source_video) else {}),
        },
        'note': ('AI-generated motion from reference footage. Heuristic v1 '
                 '(no twist, rigid torso); physics cleanup via Cascadeur/open '
                 'alternatives pending (see tools/mocap/README.md).'),
    }
    clip_path = os.path.join(fighter_dir, f'{clip_name}.json')
    with open(clip_path, 'w') as f:
        json.dump(clip, f)

    # ---- skeleton.json (wh-anim-skel/1), written once ----
    skel_path = os.path.join(fighter_dir, 'skeleton.json')
    if not os.path.exists(skel_path):
        rw = data['rest_world']
        # canonical parents; rest = world joint positions
        joints = []
        for c in CANONICAL:
            joints.append({
                'name': c,
                'parent': PARENTS[c],
                'rest': [float(v) for v in rw[c]],
            })
        # foot_tip: toe positions (fallback: rest + forward)
        def tip(side):
            k = f'{side}ToeBase'
            return [float(v) for v in rw[k]] if k in rw else [0.1, 0.06, 0.17]
        skel = {
            'format': 'wh-anim-skel/1',
            'source': f'gen/mocap/{fighter} rest pose (BVH offsets, meters)',
            'tool': 'tools/mocap/bvh_to_wh_anim.py',
            'note': ('Rest pose of the rig the bank\'s clips were baked onto. '
                     'All joint rest rotations are identity; rest = world joint '
                     'positions (meters, faces +Z, character left = +X).'),
            'root': 'Root',
            'root_rest_y': float(rw['Hips'][1]),
            'joints': joints,
            'foot_tip': {'LeftFoot': tip('Left'), 'RightFoot': tip('Right')},
        }
        with open(skel_path, 'w') as f:
            json.dump(skel, f, indent=1)

    # ---- sets.json (wh-anim-sets/1), merged ----
    sets_path = os.path.join(fighter_dir, 'sets.json')
    if os.path.exists(sets_path):
        with open(sets_path) as f:
            sets = json.load(f)
    else:
        sets = {
            'format': 'wh-anim-sets/1',
            'fighter': fighter,
            'bank': f'gen/mocap/{fighter}',
            'tool': 'tools/mocap/bvh_to_wh_anim.py',
            'note': ('FIGHT/SHOW set tags. Runtime gate: game/js/anim-gate.js. '
                     'A "show" clip must NEVER list FIGHT in contexts '
                     '(tools/mocap/gate_check.py enforces). A show move enters '
                     'a fighter moveset only with explicit owner approval.'),
            'clips': {},
        }
    if set_tag not in ('fight', 'show'):
        raise ValueError("set_tag must be 'fight' or 'show'")
    if contexts is None:
        contexts = ['FIGHT'] if set_tag == 'fight' else ['INTRO_OUTRO', 'CUTSCENE', 'SHOW']
    entry = {
        'file': f'{clip_name}.json',
        'set': set_tag,
        'contexts': contexts,
        'slot': slot or clip_name,
        'source': clip['source'],
        'tool': clip['tool'],
        'sha256': clip['sha256'],
        'added': datetime.date.today().isoformat(),
    }
    if set_tag == 'show':
        entry['showSlot'] = show_slot or clip_name
    sets['clips'][clip_name] = entry
    with open(sets_path, 'w') as f:
        json.dump(sets, f, indent=1)

    print(f'wrote {clip_path} ({n} frames @ {fps} fps, set={set_tag})')
    print(f'skeleton: {skel_path} | sets: {sets_path}')
    return clip_path, skel_path, sets_path


def main(argv=None):
    ap = argparse.ArgumentParser(
        description='BVH -> wh-anim/1 bank files (clip + skeleton.json + sets.json) [WIRED, CPU]')
    ap.add_argument('bvh', help='input .bvh')
    ap.add_argument('--fighter', required=True, help='fighter id, e.g. law')
    ap.add_argument('--clip', required=True, help='clip name, e.g. mocap_jab_01')
    ap.add_argument('--out-root', required=True,
                    help='anim root to write under (game/assets/anim)')
    ap.add_argument('--set', dest='set_tag', default='fight', choices=['fight', 'show'],
                    help="anim-gate set tag (default: fight)")
    ap.add_argument('--contexts', default='',
                    help='comma-separated contexts (default: FIGHT for fight, INTRO_OUTRO,CUTSCENE,SHOW for show)')
    ap.add_argument('--slot', default='', help='moveset slot name (fight clips)')
    ap.add_argument('--show-slot', default='', help='show slot name (show clips)')
    ap.add_argument('--source-video', default='', help='original reference video (for provenance sha)')
    ap.add_argument('--flip-180', action='store_true', help='source faces -Z; turn to +Z')
    ap.add_argument('--bone-map', default='', help='JSON {canonical: source} name map for foreign BVHs')
    ap.add_argument('--fps', type=float, default=0.0, help='override fps (0 = from BVH)')
    a = ap.parse_args(argv)
    write_bank(
        a.bvh, a.fighter, a.clip, a.out_root, set_tag=a.set_tag,
        contexts=[c for c in a.contexts.split(',') if c] or None,
        slot=a.slot or None, show_slot=a.show_slot or None,
        source_video=a.source_video or None,
        flip_180=a.flip_180, bone_map=a.bone_map or None,
        fps_override=a.fps,
    )


if __name__ == '__main__':
    main()

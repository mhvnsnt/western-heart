#!/usr/bin/env python3
"""dw_curve_bake.py — bake decoded Devil Within motion curves into wh-anim/1
packs for Western Heart (game/assets/anim/dw/).

Converts the per-joint DW curves (teardown/tekken5/dw-motion-curves.json) into
the game's wh-anim/1 clip format + wh-anim-skel/1 skeleton, so the DW motion
retargets onto Mixamo-rigged fighters through the game's existing
retargetT3Clips path (the same shape as the T7 moves packs).

Method (cracked 2026-11-08, measured — see DW-DECODE-LOG.md §22):
- Rotation convention: LOCAL, R = Rz(t2)*Ry(t1)*Rx(t0), composed down the DW
  hierarchy. (The decode's stated R = Ry(t0)*Rx(t1)*Rz(t2) was WRONG.)
- FK model: bone 0 = root ground travel (Y 0); bone 1 (hips) is root-relative
  [0, height, 0]; limb endpoints (25-32) are stage-frame absolute; bone 8 is
  a fixed [-400,0,0] marker (excluded); bones 33/34 are frozen toes.
- Rest offsets (mm, parent-local): the authored bone lengths (arm 670 mm,
  leg 860 mm). See dw_fk.py.
- Canonical mapping (L/R measured — DW bone 11 is the character's RIGHT side,
  bone 15 the LEFT; the ±Z split is reversed from the first hypothesis):
  0 Root, 1 Hips, 3 Spine, 6 Chest, 11 RightShoulder, 15 LeftShoulder,
  12 RightArm, 16 LeftArm, 13 RightForeArm, 17 LeftForeArm, 14 RightHand,
  18 LeftHand, 19 RightUpLeg, 22 LeftUpLeg, 20 RightLeg, 23 LeftLeg,
  21 RightFoot, 24 LeftFoot, 4 Head, 33 RightToeBase, 34 LeftToeBase.
  Unmapped: 2 (lone spin/prop), 8 (marker), 9/10 (chest chain, unidentified).
- Emission: CONJUGATED deltas from the rest pose —
  E_c(k) = W_parent(ref) * local_c(k) * local_c(ref)^-1 * W_parent(ref)^-1 —
  so the composed world delta equals the true DW world delta
  W_c(k)*W_c(ref)^-1. (Absolute locals and plain deltas are both WRONG:
  round-trip worst errors 8.6 m and 1,677 mm respectively.)
- Bank-frame conjugation: the emitted locals are additionally conjugated by
  the facing rotation R_y, so the whole bank (rest positions, root_t AND
  rotations) lives in the bank frame. The facing is the PELVIS forward
  (W_3 at the reference frame 0) — 0.0 deg for the default reference clip
  (gym_ozb3_greaction2.dat). The earlier +7.5 deg rotation (from the
  bankFacing kneeDeg) was a misread and is NOT applied.
- Skeleton rest positions = FK positions at the reference frame 0 (metres,
  DW frame, rotated into the bank frame); root_rest_y = reference hips height.
- Head/Neck rest and ToeBase rest are NOT in the DW data (the head bone is
  rotation-only and co-located with the spine; the toe offsets are frozen).
  They are taken from the game's own canonical proportions at the same scale
  (the king bank: Chest->Head 0.4229 m, Chest->Neck 0.273 m, Hips->Chest
  0.1365 m; ToeBase = Foot + [0, -0.1, 0.153] m). Flagged as assumptions in
  the bake log. Without a real Head rest, the retarget's torso match breaks.
- Skipped-joint residual (a real limit of the 35->21 bone map): the canonical
  hierarchy skips DW joints 5 (Chest) and 7 (UpLeg). Their rotations are
  folded into the child's local, but the child's POSITION cannot be recovered
  from the parent's rotation alone — the residual is the skipped joint's
  rotation change x its offset (chest ~44-65 mm, upleg ~95-190 mm, up to
  200-400 mm at the foot during a big throw). This does NOT corrupt the
  retarget's joint rotations (G is correct); it only bounds the torso-match
  direction error by a few degrees. The render is the arbiter.

Usage:
  python3 dw_curve_bake.py --curves <dw-motion-curves.json> --out <dir>
      --set {pantera|warden|all} --ref <reference clip> --fighter <id>
"""
import argparse
import json
import math
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
# dw_fk.py lives with the decode tools (teardown/tekken5/tools/) when landed;
# fall back to the bake tool's own directory (a flat checkout).
for _p in (_HERE, os.path.join(_HERE, '..', '..', 'teardown', 'tekken5', 'tools')):
    if os.path.exists(os.path.join(_p, 'dw_fk.py')) and _p not in sys.path:
        sys.path.insert(0, os.path.abspath(_p))
from dw_fk import (
    PARENT35, OFFSET35, PARENT27, OFFSET27,
    quat_mul, quat_conj, quat_norm, quat_apply, quat_from_euler_deg,
    world_rotations, _rotation_at, _position_at,
)

# Canonical joint set (21, matching the king skeleton).
CANON = [
    ('Hips', None), ('Spine', 'Hips'), ('Chest', 'Spine'), ('Neck', 'Chest'),
    ('Head', 'Neck'),
    ('LeftShoulder', 'Chest'), ('LeftArm', 'LeftShoulder'),
    ('LeftForeArm', 'LeftArm'), ('LeftHand', 'LeftForeArm'),
    ('LeftUpLeg', 'Hips'), ('LeftLeg', 'LeftUpLeg'), ('LeftFoot', 'LeftLeg'),
    ('LeftToeBase', 'LeftFoot'),
    ('RightShoulder', 'Chest'), ('RightArm', 'RightShoulder'),
    ('RightForeArm', 'RightArm'), ('RightHand', 'RightForeArm'),
    ('RightUpLeg', 'Hips'), ('RightLeg', 'RightUpLeg'),
    ('RightFoot', 'RightLeg'), ('RightToeBase', 'RightFoot'),
]
CANON_PARENT = dict(CANON)

# DW bone -> canonical joint. L/R measured (bone 11 = RIGHT, bone 15 = LEFT).
# Each canonical joint is built from a DW world rotation W_<dw bone>.
# The toe bones differ by skeleton: 35-bone uses 33/34, 27-bone renumbers
# them 25/26 (the 27-bone skeleton is the 35-bone minus the 8 locators).
CANON_DW_BONE_35 = {
    'Hips': 3, 'Spine': 3, 'Chest': 6, 'Neck': 6, 'Head': 4,
    'LeftShoulder': 15, 'LeftArm': 16, 'LeftForeArm': 17, 'LeftHand': 18,
    'LeftUpLeg': 22, 'LeftLeg': 23, 'LeftFoot': 24, 'LeftToeBase': 34,
    'RightShoulder': 11, 'RightArm': 12, 'RightForeArm': 13, 'RightHand': 14,
    'RightUpLeg': 19, 'RightLeg': 20, 'RightFoot': 21, 'RightToeBase': 33,
}
CANON_DW_BONE_27 = dict(CANON_DW_BONE_35, LeftToeBase=26, RightToeBase=25)
CANON_DW_BONE = CANON_DW_BONE_35
# Canonical joint's parent DW bone (for the local computation):
# canonical local = W_parent_dw^-1 * W_joint_dw, where the parent's DW world
# rotation is the DW bone that maps to the canonical parent.
def canon_parent_dw(joint):
    p = CANON_PARENT[joint]
    return None if p is None else CANON_DW_BONE[p]

# DW bone that carries the canonical joint's LOCAL rotation directly.
# (For joints whose DW chain has a skipped joint — Chest skips 5, UpLeg skips
# 7 — the local is folded: the child's local absorbs the skipped joint's
# rotation, which the conjugated-delta emission handles exactly.)
CANON_LOCAL_DW = {
    'Hips': 1, 'Spine': 3, 'Chest': 6, 'Neck': 6, 'Head': 4,
    'LeftShoulder': 15, 'LeftArm': 16, 'LeftForeArm': 17, 'LeftHand': 18,
    'LeftUpLeg': 22, 'LeftLeg': 23, 'LeftFoot': 24, 'LeftToeBase': 34,
    'RightShoulder': 11, 'RightArm': 12, 'RightForeArm': 13, 'RightHand': 14,
    'RightUpLeg': 19, 'RightLeg': 20, 'RightFoot': 21, 'RightToeBase': 33,
}

# King-bank canonical proportions (metres) — the assumptions for Head/Neck/Toe.
KING_HIPS_CHEST = 0.1365
KING_CHEST_HEAD = 0.4229
KING_CHEST_NECK = 0.2730
KING_FOOT_DIR = (0.0, -0.1, 0.153)

# Pilot moves (Pantera). Only the two basic front throws are mapped — the
# other four nage clips are baked as data with the mapping owed, not guessed.
# The name "Soul Beam" is PROPOSED (Jay call #6) and is NOT used in code.
PANTERA_MOVES = {
    'surge':         {'clip': 'dwhadoh00', 'input': '1+2+3+4', 'dw_source': 'gym_dwhadoh00.dat',
                      'note': 'Surge Form beam (wave file).'},
    'surge-trigger': {'clip': 'ozhe_power', 'input': None, 'dw_source': 'gym_ozhe_power.dat',
                      'note': 'Soul Surge Bloom trigger — plays once when Surge Form starts. '
                              'ozhe_power (unmasked kit, 45f): grounded crouch-then-rise '
                              '(hips 620->1122 mm, ends 981 mm) — measured 2026-11-08 and '
                              'watched in-game the same day (crouch, gather, rise, feet on '
                              'the floor, no leap). Replaces dwup00 (leaps to 2.375 m, ends '
                              'prone — measured; kept as a decoded clip only, not a move).'},
    '1+3':           {'clip': 'ikdv_36_nage_f', 'input': '1+3', 'dw_source': 'gym_ikdv_36_nage_f.dat',
                      'note': 'Surge Form front throw 1+3 (Surge Kit donor, first pair).'},
    '2+4':           {'clip': 'ikdv_36_nage_y', 'input': '2+4', 'dw_source': 'gym_ikdv_36_nage_y.dat',
                      'note': 'Surge Form front throw 2+4 (Surge Kit donor, first pair).'},
}
PANTERA_UNMAPPED = ['gym_ikdv_b_nage_f.dat', 'gym_ikdv_b_nage_y.dat',
                    'gym_ikdv_ppp_nage_f.dat', 'gym_ikdv_ppp_nage_y.dat']
WARDEN_MOVES = {}  # kmb1 Warden kit — wiring hook is the HeartMind Warden boss
                   # in brawler.js; its fighter binding is a follow-up.

# Rollout kit sets (2026-11-08): one pack per DW group, baked the same way
# as the pilot. The packs are DATA (moves = {} — move mapping owed, not
# guessed) except Pantera's, which keeps the pilot's 4 mapped moves.
#   warden       <- kmb1  (39 clips, all 35-bone)
#   unmasked     <- ozb3  (29 wireable 35-bone; 7 x 4-bone teil1 appendage
#                          clips excluded — see kit_exclusions())
#   drowned-ogre <- kob2  (25 wireable 35-bone; 4 x 4-bone tail part-clips
#                          excluded)
#   wave-echo    <- oz_extra (5 clips, all 35-bone)
# The 27-bone singles (dw_nog00 / dw_raribxk / dw_rarixk / dwfkao00 /
# dwup_hei) are decoded but non-wireable per the bank (no kit assignment)
# and are NOT baked. The 78/111-bone init objects are 1-frame poses, not
# motion; the 12-bone djin clips are wing/feather appendage motion — none
# of them is fighter motion and none is bakeable with this 35/27-bone FK
# model. Each exclusion is measured and listed by kit_exclusions().
KIT_SETS = {
    'warden':       {'group': 'kmb1',     'fighter': 'warden',       'pack': 'moves.warden.pack.json'},
    'unmasked':     {'group': 'ozb3',     'fighter': 'unmasked',     'pack': 'moves.unmasked.pack.json'},
    'drowned-ogre': {'group': 'kob2',     'fighter': 'drowned-ogre', 'pack': 'moves.drowned-ogre.pack.json'},
    'wave-echo':    {'group': 'oz_extra', 'fighter': 'wave-echo',    'pack': 'moves.wave-echo.pack.json'},
}

def kit_clip_names(bank, group):
    """Sorted clip names (no gym_/.dat) of the wireable 35-bone clips in a
    DW group, from the motion bank. These are the bakeable clips of the
    group — the FK model covers 35-bone (and 27-bone) skeletons only."""
    out = []
    for c in bank.get('clips', []):
        if c.get('group') != group or not c.get('wireable') or c.get('bones') != 35:
            continue
        src = c.get('source_file', '')
        if src.startswith('gym_') and src.endswith('.dat'):
            out.append(src[4:-4])
    return sorted(set(out))

def kit_exclusions(bank, group):
    """(clip name, measured reason) for the decoded clips of a group that
    are NOT bakeable with this FK model. Reasons are measured from the
    bank + curves, never guessed."""
    out = []
    for c in bank.get('clips', []):
        if c.get('group') != group:
            continue
        src = c.get('source_file', '')
        name = src[4:-4] if src.startswith('gym_') and src.endswith('.dat') else src
        bones, frames = c.get('bones'), c.get('frames')
        status = str(c.get('status', ''))
        if c.get('wireable') and bones == 35:
            continue  # bakeable
        if status.startswith('MISSING'):
            reason = 'missing file — no data in TK5DATA2 (list reference only, no curves to bake)'
        elif bones in (78, 111, 96) and frames == 1:
            reason = f'{bones}-bone 1-frame init object (a pose, not motion)'
        elif bones == 4:
            reason = '4-bone appendage part-clip (tail/wave/horn/tornado/demo part 1 — not a full-body skeleton)'
        elif bones == 12:
            reason = '12-bone wing/feather appendage motion (not a full-body skeleton)'
        elif bones == 27 and not c.get('wireable'):
            reason = '27-bone, decoded but non-wireable per the bank (no kit assignment)'
        elif not c.get('wireable'):
            reason = 'decoded but non-wireable per the bank (no kit assignment)'
        else:
            reason = f'{bones}-bone, no FK model for this skeleton'
        out.append((name, reason))
    return sorted(out)

def rot_y_deg(deg):
    r = math.radians(deg)
    return (0.0, math.sin(r / 2), 0.0, math.cos(r / 2))

def vec_rot_y(v, deg):
    q = rot_y_deg(deg)
    return quat_apply(q, v)

def vec_add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])

def vec_scale(v, s):
    return (v[0] * s, v[1] * s, v[2] * s)

def load_curves(path):
    with open(path) as f:
        return json.load(f)

def reference_frame(curves, ref_name):
    """Rest pose + facing from the reference clip's frame 0.
    Returns (W_ref, P_ref, facing_deg) where W_ref is the DW world rotation
    of every bone at frame 0, P_ref the FK positions (mm, DW frame), and
    facing_deg the pelvis-forward yaw (deg, 0 = +Z)."""
    clip = next(c for c in curves['clips'] if c['source_file'] == ref_name)
    parent = PARENT35 if clip['bones'] == 35 else PARENT27
    offset = OFFSET35 if clip['bones'] == 35 else OFFSET27
    W = world_rotations(clip, 0, parent)
    p0 = _position_at(clip, 0, 0)
    h1 = _position_at(clip, 1, 0)
    P = {0: p0, 1: (p0[0] + h1[0], p0[1] + h1[1], p0[2] + h1[2])}
    depth = {}
    def dep(b):
        if b not in depth:
            pp = parent.get(b)
            depth[b] = 0 if pp is None else dep(pp) + 1
        return depth[b]
    for b in sorted(parent.keys(), key=lambda x: (dep(x), x)):
        if b in (0, 1):
            continue
        p = parent.get(b)
        if p is None:
            P[b] = (0.0, 0.0, 0.0)
            continue
        off = offset.get(b, (0.0, 0.0, 0.0))
        r = quat_apply(W[p], off)
        P[b] = (P[p][0] + r[0], P[p][1] + r[1], P[p][2] + r[2])
    # Facing = pelvis forward (W_3 at frame 0). The pelvis local frame has
    # +X along the spine (up), +/-Z left/right (shoulders), so the forward
    # is the local +Y axis. Its horizontal projection (X/Z) is the facing;
    # for the reference clip it is already +Z (0.0 deg). (Using the local
    # +X — the spine direction — gives a wrong 90 deg.)
    fwd = quat_apply(W[3], (0.0, 1.0, 0.0))
    facing = math.degrees(math.atan2(fwd[0], fwd[2]))
    return (W, P, facing, clip)

def canonical_world(clip, ki, parent, bone_map):
    """Canonical world rotations W_c(k) for every canonical joint at keyframe ki.
    W_c = the DW world rotation of the mapped DW bone. For the canonical
    hierarchy, W_Spine = W_3 (Spine local = identity, matching the T3 rig
    where Spine rest = Hips rest); W_Neck = W_Chest (Neck local identity).
    bone_map is CANON_DW_BONE_35 or CANON_DW_BONE_27 (toes renumber)."""
    Wdw = world_rotations(clip, ki, parent)
    Wc = {}
    for joint in CANON_PARENT:
        Wc[joint] = Wdw[bone_map[joint]]
    return Wc

def bake_clip(clip, W_ref, P_ref, facing_deg, parent, offset):
    """Bake one DW clip into a wh-anim/1 clip dict.
    Emits conjugated deltas from the rest pose, conjugated into the bank
    frame by the facing rotation R_y."""
    n_kf = clip['n_keyframes']
    step = clip['step']
    fps = 60 if step == 1 else 30
    bone_map = CANON_DW_BONE_35 if clip['bones'] == 35 else CANON_DW_BONE_27
    # Canonical world rotations at the reference frame (rest pose).
    # Rest world rotations come from the REFERENCE clip (shared rest pose),
    # not from this clip's frame 0 (27-bone clips start in different poses).
    # W_ref is the reference clip's DW world rotations at frame 0 (35-bone).
    Wc_ref = {j: W_ref[CANON_DW_BONE_35[j]] for j in CANON_PARENT}
    # Canonical parent world rotations at the reference frame.
    Wp_ref = {}
    for j in CANON_PARENT:
        p = CANON_PARENT[j]
        Wp_ref[j] = (0.0, 0.0, 0.0, 1.0) if p is None else Wc_ref[p]
    Ry = rot_y_deg(-facing_deg)
    rot_xyzw = {j: [] for j in CANON_PARENT}
    root_t = []
    for ki in range(n_kf):
        Wc = canonical_world(clip, ki, parent, bone_map)
        # Canonical parent world rotations at this keyframe.
        Wp = {}
        for j in CANON_PARENT:
            p = CANON_PARENT[j]
            Wp[j] = (0.0, 0.0, 0.0, 1.0) if p is None else Wc[p]
        for j in CANON_PARENT:
            # Conjugated delta: E = W_parent(ref) * local(k) * local(ref)^-1
            #   * W_parent(ref)^-1, where local(k) = W_parent(k)^-1 * W_c(k)
            #   and local(ref) = W_parent(ref)^-1 * W_c(ref).
            # This makes the composed G equal the true world delta
            # W_c(k)*W_c(ref)^-1 (verified by induction).
            local_k = quat_mul(quat_conj(Wp[j]), Wc[j])
            local_ref = quat_mul(quat_conj(Wp_ref[j]), Wc_ref[j])
            E = quat_mul(Wp_ref[j], quat_mul(local_k, quat_mul(quat_conj(local_ref), quat_conj(Wp_ref[j]))))
            # Bank-frame conjugation: E' = R_y * E * R_y^-1.
            E = quat_mul(Ry, quat_mul(E, quat_conj(Ry)))
            E = quat_norm(E)
            rot_xyzw[j].append([round(E[0], 6), round(E[1], 6), round(E[2], 6), round(E[3], 6)])
        # root_t = [pos_0.x, pos_1.y, pos_0.z] in metres, rotated into the bank frame.
        p0 = _position_at(clip, 0, ki)
        h1 = _position_at(clip, 1, ki)
        rt = (p0[0] / 1000.0, h1[1] / 1000.0, p0[2] / 1000.0)
        rt = vec_rot_y(rt, -facing_deg)
        root_t.append([round(rt[0], 6), round(rt[1], 6), round(rt[2], 6)])
    return {'fps': fps, 'rot_xyzw': rot_xyzw, 'root_t': root_t, 'n_keyframes': n_kf}

def bake_skeleton(W_ref, P_ref, facing_deg):
    """Skeleton.json rest positions = FK positions at the reference frame 0
    (metres, DW frame, rotated into the bank frame). Head/Neck/ToeBase are
    the king-bank proportions (flagged as assumptions)."""
    def to_bank(p_mm):
        v = (p_mm[0] / 1000.0, p_mm[1] / 1000.0, p_mm[2] / 1000.0)
        v = vec_rot_y(v, -facing_deg)
        return [round(v[0], 6), round(v[1], 6), round(v[2], 6)]
    dw_pos = {}
    for j in CANON_PARENT:
        dw_pos[j] = P_ref[CANON_DW_BONE[j]]
    # Scale: DW Hips->Chest vs king Hips->Chest.
    hips = dw_pos['Hips']
    chest = dw_pos['Chest']
    dw_hips_chest = math.sqrt(sum((chest[i] - hips[i]) ** 2 for i in range(3))) / 1000.0
    scale = dw_hips_chest / KING_HIPS_CHEST if KING_HIPS_CHEST else 1.0
    # Torso direction (Chest - Hips, normalised) for Head/Neck placement.
    td = [(chest[i] - hips[i]) / 1000.0 for i in range(3)]
    tl = math.sqrt(sum(x * x for x in td)) or 1.0
    td = [x / tl for x in td]
    head_h = KING_CHEST_HEAD * scale
    neck_h = KING_CHEST_NECK * scale
    chest_m = (chest[0] / 1000.0, chest[1] / 1000.0, chest[2] / 1000.0)
    neck = [chest_m[i] + td[i] * neck_h for i in range(3)]
    head = [chest_m[i] + td[i] * head_h for i in range(3)]
    rest = {}
    for j in CANON_PARENT:
        if j == 'Neck':
            rest[j] = [round(x, 6) for x in vec_rot_y(tuple(neck), -facing_deg)]
        elif j == 'Head':
            rest[j] = [round(x, 6) for x in vec_rot_y(tuple(head), -facing_deg)]
        elif j == 'LeftToeBase':
            f = dw_pos['LeftFoot']
            foot = (f[0] / 1000.0, f[1] / 1000.0, f[2] / 1000.0)
            toe = (foot[0] + KING_FOOT_DIR[0] * scale, foot[1] + KING_FOOT_DIR[1] * scale,
                   foot[2] + KING_FOOT_DIR[2] * scale)
            rest[j] = [round(x, 6) for x in vec_rot_y(toe, -facing_deg)]
        elif j == 'RightToeBase':
            f = dw_pos['RightFoot']
            foot = (f[0] / 1000.0, f[1] / 1000.0, f[2] / 1000.0)
            toe = (foot[0] + KING_FOOT_DIR[0] * scale, foot[1] + KING_FOOT_DIR[1] * scale,
                   foot[2] + KING_FOOT_DIR[2] * scale)
            rest[j] = [round(x, 6) for x in vec_rot_y(toe, -facing_deg)]
        else:
            rest[j] = to_bank(dw_pos[j])
    root_rest_y = round(P_ref[1][1] / 1000.0, 6)
    joints = [{'name': j, 'parent': CANON_PARENT[j], 'rest': rest[j]} for j, _ in CANON]
    return {
        'format': 'wh-anim-skel/1',
        'tool': 'dw_curve_bake.py (Devil Within curve retarget)',
        'note': ('Rest = FK positions at the reference clip frame 0 (guard stance). '
                 'Head/Neck rest and ToeBase rest are the game\'s own canonical proportions '
                 'at the same scale (king bank) — DW data has no positions for them. '
                 'All joint rest rotations are identity; rest = world joint positions '
                 '(glTF space, meters, faces +Z, character left = +X).'),
        'source_skeleton': 'tekken5-dw-35bone (27-bone clips share the same rest pose)',
        'root': 'Hips',
        'root_rest_y': root_rest_y,
        'joints': joints,
        'foot_tip': {},
    }, {'dw_hips_chest_m': round(dw_hips_chest, 6), 'scale_vs_king': round(scale, 6),
        'root_rest_y_m': root_rest_y}

def bake_set(data, byname, bank, W_ref, P_ref, facing, skel, skel_meta,
             set_name, moves, unmapped, clip_names, fighter, pack_name,
             exclusions, out, ref='gym_ozb3_greaction2.dat'):
    """Bake one set (a fighter pack or a kit data pack) into `out`.
    `moves` maps move keys to {clip, input, dw_source, note}; `unmapped`
    is the list of gym_*.dat source files baked as data; `exclusions`
    is the list of (clip, measured reason) NOT baked. Returns (n_clips,
    pack_path)."""
    clips = {}
    log_lines = []
    for cname in clip_names:
        src = 'gym_' + cname + '.dat'
        clip = byname.get(src)
        if clip is None:
            log_lines.append(f'  MISSING source file for clip {cname} ({src}) — skipped')
            continue
        parent = PARENT35 if clip['bones'] == 35 else PARENT27
        offset = OFFSET35 if clip['bones'] == 35 else OFFSET27
        baked = bake_clip(clip, W_ref, P_ref, facing, parent, offset)
        clips[cname] = {
            'format': 'wh-anim/1',
            'fps': baked['fps'],
            'anim_set': 'FIGHT',
            'bones': [j for j, _ in CANON],
            'rot_xyzw': baked['rot_xyzw'],
            'root_t': baked['root_t'],
            'source': src,
            'character': fighter,
            'for_fighter': fighter,
            'loop': False,
            'dw_source': src,
            'applier': 'dw_curve_bake.py',
        }
        log_lines.append(f"  {cname}: {clip['frames']}f step {clip['step']} "
                         f"({baked['n_keyframes']} kf @ {baked['fps']} fps, {clip['bones']} bones)")

    moves_out = {}
    for key, m in moves.items():
        moves_out[key] = {
            'clip': m['clip'],
            'input': m['input'],
            'dw_source': m['dw_source'],
            'active_frames': None,
            'verified': False,
        }
    pack = {
        'format': 'wh-dw-moves/1',
        'fps': 30,
        'fighter': fighter,
        'character': fighter,
        'anim_set': 'FIGHT',
        'skeleton': 'skeleton.json',
        'source': {'dw_curves': 'teardown/tekken5/dw-motion-curves.json',
                   'baker': 'dw_curve_bake.py'},
        'skipped': [{'clip': u.replace('gym_', '').replace('.dat', ''), 'reason': 'baked as data, move mapping owed — not guessed'}
                    for u in unmapped],
        'moves': moves_out,
        'clips': clips,
    }

    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'skeleton.json'), 'w') as f:
        json.dump(skel, f, indent=1)
    pack_path = os.path.join(out, pack_name)
    with open(pack_path, 'w') as f:
        json.dump(pack, f, indent=1)

    log = []
    log.append('# DW curve bake log')
    log.append('')
    log.append(f"Reference clip: {ref} (frame 0 rest pose). Facing (pelvis forward): {facing:.2f} deg from +Z.")
    log.append(f"root_rest_y: {skel_meta['root_rest_y_m']} m. DW Hips->Chest: {skel_meta['dw_hips_chest_m']} m (scale vs king: {skel_meta['scale_vs_king']}).")
    log.append('')
    log.append('## Assumptions (DW data has no positions for these)')
    log.append('- Head/Neck rest: king-bank proportions at the same scale (Chest->Head 0.4229 m, Chest->Neck 0.273 m).')
    log.append('- ToeBase rest: Foot + [0, -0.1, 0.153] m (king-bank foot direction).')
    log.append('- 27-bone clips share the 35-bone rest pose; their bone lengths are transferred, unverified until the watched render.')
    log.append('- Dropped bones (unmapped, documented): 2 (lone spin/prop), 8 (fixed marker), 9/10 (chest chain, nature unidentified).')
    log.append('')
    log.append('## Skipped-joint residual (real limit of the 35->21 bone map)')
    log.append('The canonical hierarchy skips DW joints 5 (Chest) and 7 (UpLeg). Their rotations are folded into the child local, but the child POSITION cannot be recovered from the parent rotation alone — the residual is the skipped joint rotation change x its offset (chest ~44-65 mm, upleg ~95-190 mm, up to 200-400 mm at the foot during a big throw). Joint rotations are correct; only the torso-match direction is bounded by a few degrees. The render is the arbiter.')
    log.append('')
    log.append('## Clips baked')
    log.extend(log_lines)
    log.append('')
    log.append('## Moves mapped')
    if moves:
        for key, m in moves.items():
            log.append(f"- {key}: {m['clip']} ({m['dw_source']}) — {m['note']}")
    else:
        log.append('- (none — this pack is DATA: every clip is baked, no move mapping is claimed. Mapping owed, not guessed.)')
    log.append('')
    log.append('## Unmapped (baked as data, mapping owed — not guessed)')
    for u in unmapped:
        log.append(f'- {u}')
    log.append('')
    log.append('## Excluded from this pack (measured — not bakeable with this FK model)')
    if exclusions:
        for name, reason in exclusions:
            log.append(f'- {name}: {reason}')
    else:
        log.append('- (none — every decoded clip of this group is baked)')
    log_name = 'DW-BAKE-LOG.md' if set_name == 'pantera' else f'DW-BAKE-LOG-{fighter}.md'
    with open(os.path.join(out, log_name), 'w') as f:
        f.write('\n'.join(log) + '\n')

    print(f'Baked {len(clips)} clips, {len(moves)} moves -> {out}')
    print(f'  skeleton.json (root_rest_y {skel_meta["root_rest_y_m"]} m, facing {facing:.2f} deg)')
    print(f'  {pack_name} ({os.path.getsize(pack_path)} B)')
    print(f'  {log_name}')
    return len(clips), pack_path


def pantera_unmapped(bank):
    """Pantera's unmapped clips: the pilot's 4 nage clips PLUS every
    remaining wireable 35-bone ikdv (Surge Kit) clip — the Surge Kit is
    Pantera's kit, so its clips live in his pack as data until a move
    mapping claims them. Returns gym_*.dat source filenames, sorted."""
    have = {m['clip'] for m in PANTERA_MOVES.values()}
    unmapped = list(PANTERA_UNMAPPED)
    for c in bank.get('clips', []):
        if c.get('group') != 'ikdv' or not c.get('wireable') or c.get('bones') != 35:
            continue
        src = c.get('source_file', '')
        if not src or src in unmapped:
            continue
        if src[4:-4] in have:
            continue
        unmapped.append(src)
    return sorted(unmapped)


def main():
    ap = argparse.ArgumentParser(description='Bake DW motion curves to wh-anim packs.')
    ap.add_argument('--curves', default='teardown/tekken5/dw-motion-curves.json')
    ap.add_argument('--bank', default='teardown/tekken5/dw-motion-bank.json')
    ap.add_argument('--out', default='game/assets/anim/dw')
    ap.add_argument('--set', choices=['pantera', 'warden', 'unmasked', 'drowned-ogre', 'wave-echo', 'all'],
                    default='pantera')
    ap.add_argument('--ref', default='gym_ozb3_greaction2.dat')
    ap.add_argument('--fighter', default=None,
                    help='fighter/kit id for the pack (defaults per set)')
    args = ap.parse_args()

    data = load_curves(args.curves)
    byname = {c['source_file']: c for c in data['clips']}
    with open(args.bank) as f:
        bank = json.load(f)
    W_ref, P_ref, facing, ref_clip = reference_frame(data, args.ref)
    skel, skel_meta = bake_skeleton(W_ref, P_ref, facing)

    sets = ['pantera', 'warden', 'unmasked', 'drowned-ogre', 'wave-echo'] if args.set == 'all' else [args.set]
    for set_name in sets:
        if set_name == 'pantera':
            moves = PANTERA_MOVES
            unmapped = pantera_unmapped(bank)
            clip_names = sorted({m['clip'] for m in moves.values()} |
                                {u.replace('gym_', '').replace('.dat', '') for u in unmapped})
            fighter = args.fighter or 'pantera'
            pack_name = 'moves.pantera.pack.json'
            exclusions = []
        else:
            spec = KIT_SETS[set_name]
            moves = {}
            names = kit_clip_names(bank, spec['group'])
            unmapped = ['gym_' + n + '.dat' for n in names]
            clip_names = names
            fighter = args.fighter or spec['fighter']
            pack_name = spec['pack']
            exclusions = kit_exclusions(bank, spec['group'])
        bake_set(data, byname, bank, W_ref, P_ref, facing, skel, skel_meta,
                 set_name, moves, unmapped, clip_names, fighter, pack_name,
                 exclusions, args.out, args.ref)

if __name__ == '__main__':
    main()

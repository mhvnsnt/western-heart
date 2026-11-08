# dw_fk.py — Devil Within FK model (shared module for the DW retarget bake).
#
# Cracked 2026-11-08 from teardown/tekken5/dw-motion-curves.json, measured on the
# pilot throws + ozb3/kmB1 clips. Rebuilt 2026-11-08 after a /tmp wipe.
# The model (all rotations are LOCAL, R = Rz(t2)*Ry(t1)*Rx(t0) applied to the
# parent-local frame; positions are mm, Y-up, stage frame):
#   bone 0 = root ground travel (Y always 0; travels metres in a throw clip).
#   bone 1 (hips) is root-relative [0, height, 0] — X/Z exactly 0 every frame;
#     pelvis sits directly above the root. Stage-frame pelvis = pos_0 + [0, h, 0].
#   limb endpoints (25-32) are stage-frame absolute; they track bone 0's travel.
#   bone 8 = FIXED marker [-400, 0, 0] every frame — not a joint; exclude.
#   bone 2 = lone chain [2], rotation ONLY on t1, sweeping -166..+176 deg —
#     affects no body joint's position; nature unidentified (candidate:
#     facing/spin/prop bone); unmapped, dropped, noted.
#   bones 33/34 = CONSTANT [-180, -180, 89.99] — frozen toe bones; offsets
#     unidentifiable (leaves, no position descendants).
#   bones 9/10 = 2-bone chain off bone 6 (chest), rotation-only, nature
#     unidentified (candidate: tail/wing/hair/cape chain); unmapped, dropped.
#   bones 4, 5, 7 carry large frame-0 rotations — rest locals are NOT identity;
#     the bake must emit deltas from a chosen rest pose.
#   bones 13/17/20/23 have t0=t1=0, only t2 varies — single-axis hinges.
#
# Rest offsets (mm, parent-local frame; identical across the throw clips tested
# — round numbers, the authored bone lengths). Arm 140+300+230 = 670 mm;
# leg 440+420 = 860 mm. Bones 3/5/7 are co-located ([0,0,0] each); their
# individual splits are gauge freedom — only the sum matters (it is 0).
# Bone 2/8/9/10/33/34 are not in this table (unmapped / marker / frozen).

import math

# parent of each bone in the 35-bone skeleton (None = root of the hierarchy)
PARENT35 = {
    0: None, 1: 0, 2: None, 3: 1, 4: 3, 5: 3, 6: 5, 7: 3,
    8: 0, 9: 6, 10: 9, 11: 6, 12: 11, 13: 25, 14: 13,
    15: 6, 16: 15, 17: 26, 18: 17,
    19: 7, 20: 29, 21: 20,
    22: 7, 23: 30, 24: 23,
    25: 12, 26: 16, 27: 14, 28: 18, 29: 19, 30: 22, 31: 21, 32: 24,
    33: 21, 34: 24,
}
# rest offset of each bone from its parent (mm, parent-local frame).
# Position bones (25-32) are locators co-located with their joints ([0,0,0]).
OFFSET35 = {
    1: (0.0, 0.0, 0.0), 3: (0.0, 0.0, 0.0), 4: (0.0, 0.0, 0.0),
    5: (0.0, 0.0, 0.0), 6: (130.0, 0.0, 0.0), 7: (0.0, 0.0, 0.0),
    11: (220.0, 0.0, -100.0), 12: (140.0, 0.0, 0.0), 13: (300.0, 0.0, 0.0),
    14: (230.0, 0.0, 0.0),
    15: (220.0, 0.0, 100.0), 16: (140.0, 0.0, 0.0), 17: (300.0, 0.0, 0.0),
    18: (230.0, 0.0, 0.0),
    19: (160.0, 0.0, -100.0), 20: (440.0, 0.0, 0.0), 21: (420.0, 0.0, 0.0),
    22: (160.0, 0.0, 100.0), 23: (440.0, 0.0, 0.0), 24: (420.0, 0.0, 0.0),
    25: (0.0, 0.0, 0.0), 26: (0.0, 0.0, 0.0), 27: (0.0, 0.0, 0.0),
    28: (0.0, 0.0, 0.0), 29: (0.0, 0.0, 0.0), 30: (0.0, 0.0, 0.0),
    31: (0.0, 0.0, 0.0), 32: (0.0, 0.0, 0.0),
}
# The 27-bone skeleton is the 35-bone skeleton minus the 8 locator bones
# (25-32), toes renumbered 33->25, 34->26. Chains match exactly after removal.
PARENT27 = {
    0: None, 1: 0, 2: None, 3: 1, 4: 3, 5: 3, 6: 5, 7: 3,
    8: 0, 9: 6, 10: 9, 11: 6, 12: 11, 13: 12, 14: 13,
    15: 6, 16: 15, 17: 16, 18: 17,
    19: 7, 20: 19, 21: 20,
    22: 7, 23: 22, 24: 23,
    25: 21, 26: 24,
}
OFFSET27 = {
    1: (0.0, 0.0, 0.0), 3: (0.0, 0.0, 0.0), 4: (0.0, 0.0, 0.0),
    5: (0.0, 0.0, 0.0), 6: (130.0, 0.0, 0.0), 7: (0.0, 0.0, 0.0),
    11: (220.0, 0.0, -100.0), 12: (140.0, 0.0, 0.0), 13: (300.0, 0.0, 0.0),
    14: (230.0, 0.0, 0.0),
    15: (220.0, 0.0, 100.0), 16: (140.0, 0.0, 0.0), 17: (300.0, 0.0, 0.0),
    18: (230.0, 0.0, 0.0),
    19: (160.0, 0.0, -100.0), 20: (440.0, 0.0, 0.0), 21: (420.0, 0.0, 0.0),
    22: (160.0, 0.0, 100.0), 23: (440.0, 0.0, 0.0), 24: (420.0, 0.0, 0.0),
}

def quat_mul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    )

def quat_conj(q):
    return (-q[0], -q[1], -q[2], q[3])

def quat_norm(q):
    n = math.sqrt(sum(c * c for c in q))
    return tuple(c / n for c in q) if n else (0.0, 0.0, 0.0, 1.0)

def quat_from_euler_deg(t0, t1, t2):
    """Local rotation R = Rz(t2)*Ry(t1)*Rx(t0) (the cracked DW convention)."""
    x0, y1, z2 = (math.radians(t0), math.radians(t1), math.radians(t2))
    qx = (math.sin(x0 / 2), 0.0, 0.0, math.cos(x0 / 2))
    qy = (0.0, math.sin(y1 / 2), 0.0, math.cos(y1 / 2))
    qz = (0.0, 0.0, math.sin(z2 / 2), math.cos(z2 / 2))
    return quat_norm(quat_mul(qz, quat_mul(qy, qx)))

def quat_apply(q, v):
    x, y, z, w = q
    vx, vy, vz = v
    tx = 2 * (y * vz - z * vy)
    ty = 2 * (z * vx - x * vz)
    tz = 2 * (x * vy - y * vx)
    return (vx + w * tx + y * tz - z * ty,
            vy + w * ty + z * tx - x * tz,
            vz + w * tz + x * ty - y * tx)

def quat_angle_deg(a, b):
    """Smallest rotation angle (deg) between two unit quats."""
    d = abs(sum(x * y for x, y in zip(quat_norm(a), quat_norm(b))))
    d = min(1.0, d)
    return 2 * math.degrees(math.acos(d))

def _rotation_at(clip, bone, frame_idx, bones):
    """Local rotation quat of `bone` at keyframe index `frame_idx` (Euler deg)."""
    for rec in clip['curves']:
        if rec['bone'] == bone and rec['channel'] == 'rotation_deg':
            keys = rec['keys']
            k = keys[min(frame_idx, len(keys) - 1)]
            return quat_from_euler_deg(k[0], k[1], k[2])
    return (0.0, 0.0, 0.0, 1.0)

def _position_at(clip, bone, frame_idx):
    for rec in clip['curves']:
        if rec['bone'] == bone and rec['channel'] == 'position_mm':
            keys = rec['keys']
            k = keys[min(frame_idx, len(keys) - 1)]
            return (k[0], k[1], k[2])
    return None

def world_rotations(clip, frame_idx, parent):
    """World rotation quat of every bone at a keyframe index (DW frame)."""
    W = {}
    order = sorted(parent.keys(), key=lambda b: (parent[b] is None, parent[b] or 0, b))
    # topological: parents before children (parents have smaller numbers except
    # bone 2's chain; sort by depth instead for safety)
    depth = {}
    def dep(b):
        if b not in depth:
            p = parent.get(b)
            depth[b] = 0 if p is None else dep(p) + 1
        return depth[b]
    order = sorted(parent.keys(), key=lambda b: (dep(b), b))
    for b in order:
        q = _rotation_at(clip, b, frame_idx, parent)
        p = parent.get(b)
        W[b] = q if p is None else quat_mul(W[p], q)
    return W

def fk_check(clip, parent, offset):
    """Forward-kinematics check: predict the recorded position channels from
    the rotation channels + the rest offsets; return (rms_mm, max_mm, n).
    Only bones that carry a position channel are measured."""
    pos_bones = sorted({rec['bone'] for rec in clip['curves'] if rec['channel'] == 'position_mm'})
    n_kf = clip['n_keyframes']
    errs = []
    for ki in range(n_kf):
        W = world_rotations(clip, ki, parent)
        # world positions: bone 0 is the stage-frame root (its own position
        # channel); bone 1 is root-relative [0, h, 0]; every other bone is
        # parent_pos + W_parent * offset.
        P = {}
        p0 = _position_at(clip, 0, ki)
        if p0 is None:
            continue
        P[0] = p0
        depth = {}
        def dep(b):
            if b not in depth:
                pp = parent.get(b)
                depth[b] = 0 if pp is None else dep(pp) + 1
            return depth[b]
        for b in sorted(parent.keys(), key=lambda x: (dep(x), x)):
            if b == 0:
                continue
            p = parent.get(b)
            if p is None:
                P[b] = (0.0, 0.0, 0.0)
                continue
            if b == 1:
                # hips: root-relative [0, height, 0]; height from its own channel
                h = _position_at(clip, 1, ki)
                P[1] = (P[0][0] + (h[0] if h else 0.0),
                        P[0][1] + (h[1] if h else 0.0),
                        P[0][2] + (h[2] if h else 0.0))
                continue
            off = offset.get(b, (0.0, 0.0, 0.0))
            rot = quat_apply(W[p], off)
            P[b] = (P[p][0] + rot[0], P[p][1] + rot[1], P[p][2] + rot[2])
        for b in pos_bones:
            if b in (0, 1, 8):
                continue  # 0/1 are the inputs; 8 is a fixed marker, not a joint
            rec = _position_at(clip, b, ki)
            if rec is None or b not in P:
                continue
            d = math.sqrt(sum((P[b][i] - rec[i]) ** 2 for i in range(3)))
            errs.append(d)
    if not errs:
        return (0.0, 0.0, 0)
    rms = math.sqrt(sum(e * e for e in errs) / len(errs))
    return (rms, max(errs), len(errs))

#!/usr/bin/env python3
"""YANM clip + YOBJ model -> animated glTF 2.0 (.glb) for WWE 2K19.

Usage: python3 yanm_to_gltf.py <model.yobj> <clip.yanm> <out.glb>
       [--fps 60] [--every N] [--no-morphs]

Embeds the YANM clip's Part A rotation tracks as a glTF animation
on the YOBJ skeleton (v2 bind pose: true rest orientations +
offsets). One rotation channel per animated joint; keyframes are
the clip's own keyframes (linear interpolation, quaternions kept
on one hemisphere so the +/-180-degree wrap slerps correctly).

Decode (validated 2026-11-19 by forward-kinematics stick figures
against the decoded skeleton -- identity mapping gives crumpled
impossible poses, this mapping gives coherent standing/kicking/
walking poses):
  * Part A record (v0, v1, v2, dt): v0/v1/v2 are signed-byte Euler
    angles, 1 unit = 360/256 degrees, wrapping at +/-180 degrees.
  * R_anim = Rx(v2) @ Ry(v0) @ Rz(v1) -- i.e. byte0 is the Y
    rotation, byte1 the Z rotation, byte2 the X rotation.
  * Joint local rotation = R_rest @ R_anim (R_rest = the YOBJ
    bone's rest orientation, Euler XYZ).
  * Elbow bones: bytes 0 and 2 are binary flags (-128 or 0), not
    rotations; -128 is treated as 0, leaving a clean 1-DOF hinge
    on byte1.
  * Leg twist: the leg bones' byte2 (local-X twist) carries a
    180-degree offset -- the stored values cluster near +/-180
    degrees, which points the feet backward; adding 180 degrees
    (mod 360) makes the feet point forward (validated on the
    toe-vs-hips facing metric over 3 clips: mean dot -0.27 raw,
    +0.25 with the offset). The offset is a v1 approximation:
    the exact mechanism (channel bias vs frame difference) is
    not yet understood, but the empirical result is clear, and
    the twist does not affect joint positions.
  * Frame count = majority vote of the per-part dt sums.

Known limits (see docs/YOBJ-YANM.md): no root motion (the J_Hips
Part B track is not decoded yet, so the figure animates in place);
no knee bend (knee data lives in the undeciphered StartingID 0x0001
blocks, so knees stay straight); Part B tracks are not applied;
frame rate is assumed 60 fps (2K19's simulation rate).
"""

import argparse
import math
import struct
import sys

from yobj import load as load_yobj
from yanm_decode import load as load_yanm
from yobj_to_gltf import (build_gltf, write_glb, euler_xyz_mat,
                          mat_to_gltf, mat_to_quat)

UNIT = math.radians(360.0 / 256.0)
ELBOWS = ("J_Elbow_L", "J_Elbow_R")
LEGS = ("J_Leg_L", "J_Leg_R")


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3))
             for j in range(3)] for i in range(3)]


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return [[1, 0, 0], [0, c, -s], [0, s, c]]


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]]


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def anim_matrix(v0, v1, v2):
    """YANM Part A values -> rotation matrix (file coords):
    R = Rx(v2) @ Ry(v0) @ Rz(v1)."""
    return matmul(rot_x(v2 * UNIT),
                  matmul(rot_y(v0 * UNIT), rot_z(v1 * UNIT)))


def quat_dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def unwrap_keys(keys):
    """Unwrap a keyframe track's values so consecutive keys differ
    by at most 128 units (the values wrap at +/-128 = +/-180
    degrees; linear interpolation across the wrap would swing
    through 0 degrees instead of staying near 180). Returns a new
    key list with unwrapped (possibly out-of-range) values."""
    out = []
    off = [0, 0, 0]
    prev = None
    for frame, v0, v1, v2 in keys:
        vals = [v0, v1, v2]
        if prev is not None:
            for c in range(3):
                while vals[c] + off[c] - prev[c] > 128:
                    off[c] -= 256
                while vals[c] + off[c] - prev[c] < -128:
                    off[c] += 256
        unwrapped = tuple(vals[c] + off[c] for c in range(3))
        out.append((frame,) + unwrapped)
        prev = unwrapped
    return out


def convert(yobj_path, yanm_path, out_path, fps=60, every=1,
            with_morphs=True):
    y = load_yobj(yobj_path)
    clip = load_yanm(yanm_path)
    name2idx = {b["name"]: b["index"] for b in y.bones}
    rest_mat = {}
    for b in y.bones:
        rest_mat[b["name"]] = euler_xyz_mat(*b["rest_euler"])

    gltf, b, _ = build_gltf(yobj_path, with_morphs=with_morphs)

    samplers = []
    channels = []
    n_frames = clip.frame_count
    frames = list(range(0, n_frames, every))
    if frames[-1] != n_frames - 1:
        frames.append(n_frames - 1)
    times = [f / fps for f in frames]

    # Time accessor (shared by all channels).
    tdata = struct.pack(f"<{len(times)}f", *times)
    tbv = b.add_data(tdata)
    tacc = b.add_accessor(tbv, 5126, len(times), "SCALAR",
                          [times[0]], [times[-1]])

    n_channels = 0
    for bone in clip.bones:
        name = bone["bone"]
        if not name or name not in name2idx or name not in rest_mat:
            continue
        keys = clip.track(bone, "part_a")
        if not keys:
            continue
        # Per-bone value fixes on the RAW keys, before unwrap/sample:
        # elbows: -128 flags -> 0; legs: twist channel +180 degrees.
        if name in ELBOWS:
            keys = [(f, 0.0 if v0 == -128 else v0, v1,
                     0.0 if v2 == -128 else v2)
                    for (f, v0, v1, v2) in keys]
        if name in LEGS:
            keys = [(f, v0, v1, ((v2 + 256) % 256) - 128)
                    for (f, v0, v1, v2) in keys]
        keys = unwrap_keys(keys)
        node = name2idx[name]
        rr = rest_mat[name]
        quats = []
        prev = None
        for f in frames:
            v0, v1, v2 = clip.sample(keys, f)
            rloc = matmul(rr, anim_matrix(v0, v1, v2))
            q = mat_to_quat(mat_to_gltf(rloc))
            if prev is not None and quat_dot(prev, q) < 0:
                q = tuple(-x for x in q)
            quats.append(q)
            prev = q
        qdata = struct.pack(f"<{len(quats) * 4}f",
                            *[c for q in quats for c in q])
        qbv = b.add_data(qdata)
        qacc = b.add_accessor(qbv, 5126, len(quats), "VEC4")
        samplers.append({"input": tacc, "interpolation": "LINEAR",
                         "output": qacc})
        channels.append({"sampler": len(samplers) - 1,
                         "target": {"node": node, "path": "rotation"}})
        n_channels += 1

    gltf["animations"] = [{"name": yanm_path.split("/")[-1],
                           "samplers": samplers,
                           "channels": channels}]
    write_glb(gltf, b, out_path)
    print(f"wrote {out_path}: {n_channels} rotation channels, "
          f"{len(frames)} keyframes, {n_frames} frames @ {fps} fps "
          f"({n_frames / fps:.2f} s)")


def main():
    ap = argparse.ArgumentParser(description="Convert a WWE 2K19 "
                                 "YANM clip + YOBJ model to an "
                                 "animated .glb.")
    ap.add_argument("yobj", help="input .yobj file")
    ap.add_argument("yanm", help="input .yanm clip")
    ap.add_argument("glb", help="output .glb file")
    ap.add_argument("--fps", type=int, default=60,
                    help="frames per second (default 60)")
    ap.add_argument("--every", type=int, default=1,
                    help="sample every Nth frame (default 1)")
    ap.add_argument("--no-morphs", action="store_true",
                    help="skip facial morph targets")
    args = ap.parse_args()
    convert(args.yobj, args.yanm, args.glb, fps=args.fps,
            every=args.every, with_morphs=not args.no_morphs)


if __name__ == "__main__":
    main()

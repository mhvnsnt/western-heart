#!/usr/bin/env python3
"""make_clips.py - generate the 6 standard gate clips as synthetic fixtures.

Track-1 (2026-10-14) finding: the 6 standard gate clips
(idle, walk, jab, kick, hit_react, knockdown) do NOT exist anywhere, so the
full rig_check gate could never PASS as shipped. These fixtures close that gap.

What they are: a canonical Mixamo-style 58-joint skeleton (mixamorig: names,
~1.8 m, feet on y=0, facing +Z) with 6 short procedural animations, one GLB
per clip. They are TEST FIXTURES for the gate (like unit-test data), not game
content: the gate measures the TARGET model's skin deformation (edge stretch
p99.9, ground contact, hinge flips) while these clips drive its bones, so only
plausible joint motion matters, not authored quality.

Poses are defined as keyframed euler angles (degrees, XYZ intrinsic) plus an
optional hips translation; written with LINEAR interpolation.
"""
import json, struct, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "clips", "standard")


def euler_to_quat(rx, ry, rz):
    rx, ry, rz = np.radians([rx, ry, rz])
    cx, sx = np.cos(rx / 2), np.sin(rx / 2)
    cy, sy = np.cos(ry / 2), np.sin(ry / 2)
    cz, sz = np.cos(rz / 2), np.sin(rz / 2)
    # XYZ intrinsic: q = qx * qy * qz
    qx = np.array([sx, 0, 0, cx])
    qy = np.array([0, sy, 0, cy])
    qz = np.array([0, 0, sz, cz])

    def mul(a, b):
        ax, ay, az, aw = a
        bx, by, bz, bw = b
        return np.array([aw * bx + ax * bw + ay * bz - az * by,
                         aw * by - ax * bz + ay * bw + az * bx,
                         aw * bz + ax * by - ay * bx + az * bw,
                         aw * bw - ax * bx - ay * by - az * bz])
    return mul(mul(qx, qy), qz)


# (name, parent, offset) -- parent is the index in this list; -1 = root
BONES = [
    ("mixamorig:Hips", -1, (0, 0.95, 0)),
    ("mixamorig:Spine", 0, (0, 0.12, 0)),
    ("mixamorig:Spine1", 1, (0, 0.12, 0)),
    ("mixamorig:Spine2", 2, (0, 0.12, 0)),
    ("mixamorig:Neck", 3, (0, 0.12, 0)),
    ("mixamorig:Head", 4, (0, 0.12, 0)),
    ("mixamorig:HeadTop_End", 5, (0, 0.10, 0)),
    ("mixamorig:LeftShoulder", 3, (0.17, 0.10, 0)),
    ("mixamorig:LeftArm", 7, (0.10, -0.03, 0)),
    ("mixamorig:LeftForeArm", 8, (0.27, -0.06, 0)),
    ("mixamorig:LeftHand", 9, (0.25, -0.02, 0)),
    ("mixamorig:RightShoulder", 3, (-0.17, 0.10, 0)),
    ("mixamorig:RightArm", 11, (-0.10, -0.03, 0)),
    ("mixamorig:RightForeArm", 12, (-0.27, -0.06, 0)),
    ("mixamorig:RightHand", 13, (-0.25, -0.02, 0)),
    ("mixamorig:LeftUpLeg", 0, (0.10, -0.08, 0)),
    ("mixamorig:LeftLeg", 15, (0, -0.43, 0)),
    ("mixamorig:LeftFoot", 16, (0, -0.43, 0)),
    ("mixamorig:LeftToeBase", 17, (0, -0.01, 0.13)),
    ("mixamorig:LeftToe_End", 18, (0, 0.0, 0.10)),
    ("mixamorig:RightUpLeg", 0, (-0.10, -0.08, 0)),
    ("mixamorig:RightLeg", 20, (0, -0.43, 0)),
    ("mixamorig:RightFoot", 21, (0, -0.43, 0)),
    ("mixamorig:RightToeBase", 22, (0, -0.01, 0.13)),
    ("mixamorig:RightToe_End", 23, (0, 0.0, 0.10)),
]
# finger stubs (static in fixtures; keep the joint count Mixamo-like)
FINGERS = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
for side, hand_idx in (("Left", 10), ("Right", 14)):
    fx = 0.06 if side == "Left" else -0.06
    for f in FINGERS:
        base = len(BONES)
        BONES.append((f"mixamorig:{side}Hand{f}1", hand_idx, (fx, -0.01, 0.02)))
        BONES.append((f"mixamorig:{side}Hand{f}2", base, (fx * 0.7, 0, 0.01)))
        BONES.append((f"mixamorig:{side}Hand{f}3", base + 1, (fx * 0.6, 0, 0.01)))

N = {b[0]: i for i, b in enumerate(BONES)}

# keyframes: list of (t, {bone_short: (rx,ry,rz)}, hips_dy)
idle = [
    (0.0, {"Spine": (2, 0, 0), "LeftArm": (0, 0, 3), "RightArm": (0, 0, -3)}, 0.005),
    (0.8, {"Spine": (-2, 0, 0), "LeftArm": (0, 0, -3), "RightArm": (0, 0, 3)}, -0.005),
    (1.6, {"Spine": (2, 0, 0), "LeftArm": (0, 0, 3), "RightArm": (0, 0, -3)}, 0.005),
]
walk = [
    (0.0, {"LeftUpLeg": (25, 0, 0), "RightUpLeg": (-25, 0, 0), "LeftLeg": (5, 0, 0),
           "RightLeg": (12, 0, 0), "LeftArm": (-18, 0, 0), "RightArm": (18, 0, 0)}, 0.0),
    (0.3, {"LeftUpLeg": (0, 0, 0), "RightUpLeg": (0, 0, 0), "LeftLeg": (8, 0, 0),
           "RightLeg": (8, 0, 0), "LeftArm": (0, 0, 0), "RightArm": (0, 0, 0)}, -0.02),
    (0.6, {"LeftUpLeg": (-25, 0, 0), "RightUpLeg": (25, 0, 0), "LeftLeg": (12, 0, 0),
           "RightLeg": (5, 0, 0), "LeftArm": (18, 0, 0), "RightArm": (-18, 0, 0)}, 0.0),
    (0.9, {"LeftUpLeg": (0, 0, 0), "RightUpLeg": (0, 0, 0), "LeftLeg": (8, 0, 0),
           "RightLeg": (8, 0, 0), "LeftArm": (0, 0, 0), "RightArm": (0, 0, 0)}, -0.02),
    (1.2, {"LeftUpLeg": (25, 0, 0), "RightUpLeg": (-25, 0, 0), "LeftLeg": (5, 0, 0),
           "RightLeg": (12, 0, 0), "LeftArm": (-18, 0, 0), "RightArm": (18, 0, 0)}, 0.0),
]
jab = [
    (0.0, {}, 0.0),
    (0.2, {"RightArm": (0, 40, 0), "RightForeArm": (-70, 0, 0), "Spine1": (0, 12, 0)}, 0.0),
    (0.45, {"RightArm": (0, 90, 0), "RightForeArm": (-5, 0, 0), "Spine1": (0, -12, 0)}, 0.01),
    (0.7, {"RightArm": (0, 40, 0), "RightForeArm": (-70, 0, 0), "Spine1": (0, 12, 0)}, 0.0),
    (0.9, {}, 0.0),
]
kick = [
    (0.0, {}, 0.0),
    (0.3, {"RightUpLeg": (-60, 0, 0), "RightLeg": (90, 0, 0), "LeftArm": (0, 0, 25)}, -0.03),
    (0.55, {"RightUpLeg": (-85, 0, 0), "RightLeg": (10, 0, 0), "LeftArm": (0, 0, 35),
            "Spine": (-8, 0, 0)}, -0.02),
    (0.8, {"RightUpLeg": (-60, 0, 0), "RightLeg": (90, 0, 0), "LeftArm": (0, 0, 25)}, -0.03),
    (1.0, {}, 0.0),
]
hit_react = [
    (0.0, {}, 0.0),
    (0.25, {"Spine": (18, 0, 0), "Spine1": (10, 0, 0), "Neck": (12, 0, 0), "Head": (8, 0, 0),
            "LeftArm": (0, 0, 20), "RightArm": (0, 0, -20)}, -0.015),
    (0.5, {"Spine": (8, 0, 0), "Neck": (5, 0, 0), "LeftArm": (0, 0, 10),
           "RightArm": (0, 0, -10)}, -0.005),
    (0.8, {}, 0.0),
]
# knockdown: crumple to a kneel, staying above the floor (fixture, not choreography)
knockdown = [
    (0.0, {}, 0.0),
    (0.4, {"Spine": (30, 0, 0), "Spine1": (12, 0, 0), "LeftUpLeg": (-25, 0, 0),
           "RightUpLeg": (-25, 0, 0), "LeftLeg": (40, 0, 0), "RightLeg": (40, 0, 0),
           "LeftArm": (0, 0, 30), "RightArm": (0, 0, -30)}, -0.30),
    (0.8, {"Spine": (45, 0, 0), "Spine1": (18, 0, 0), "Neck": (12, 0, 0),
           "LeftUpLeg": (-35, 0, 0), "RightUpLeg": (-35, 0, 0),
           "LeftLeg": (70, 0, 0), "RightLeg": (70, 0, 0),
           "LeftArm": (0, 0, 40), "RightArm": (0, 0, -40)}, -0.42),
    (1.2, {"Spine": (45, 0, 0), "Spine1": (18, 0, 0), "Neck": (12, 0, 0),
           "LeftUpLeg": (-35, 0, 0), "RightUpLeg": (-35, 0, 0),
           "LeftLeg": (70, 0, 0), "RightLeg": (70, 0, 0),
           "LeftArm": (0, 0, 40), "RightArm": (0, 0, -40)}, -0.42),
    (1.6, {"Spine": (45, 0, 0), "Spine1": (18, 0, 0), "Neck": (12, 0, 0),
           "LeftUpLeg": (-35, 0, 0), "RightUpLeg": (-35, 0, 0),
           "LeftLeg": (70, 0, 0), "RightLeg": (70, 0, 0),
           "LeftArm": (0, 0, 40), "RightArm": (0, 0, -40)}, -0.42),
]
CLIPS = {"idle": idle, "walk": walk, "jab": jab, "kick": kick,
         "hit_react": hit_react, "knockdown": knockdown}


def write_clip(name, kfs, out_path):
    nodes = []
    children = {i: [] for i in range(len(BONES))}
    for i, (bn, parent, off) in enumerate(BONES):
        if parent >= 0:
            children[parent].append(i)
    for i, (bn, parent, off) in enumerate(BONES):
        nodes.append({"name": bn, "translation": list(off),
                      "children": children[i]})

    blob = bytearray()
    accessors = []
    bufferViews = []

    def add(data, target=None):
        while len(blob) % 4:
            blob.append(0)
        bv = {"buffer": 0, "byteOffset": len(blob), "byteLength": len(data)}
        if target:
            bv["target"] = target
        blob.extend(bytes(data))
        bufferViews.append(bv)
        return len(bufferViews) - 1

    def acc(arr, ctype, gtype):
        arr = np.ascontiguousarray(arr, dtype=np.float32)
        a = {"bufferView": add(arr.tobytes()), "componentType": ctype,
             "count": arr.shape[0], "type": gtype}
        accessors.append(a)
        return len(accessors) - 1

    # collect animated bones
    bones = sorted({b for _, pose, _ in kfs for b in pose})
    times = np.array([t for t, _, _ in kfs], dtype=np.float32)
    time_acc = acc(times[:, None], 5126, "SCALAR")

    channels, samplers = [], []
    for b in bones:
        ni = N["mixamorig:" + b]
        quats = np.stack([euler_to_quat(*pose.get(b, (0, 0, 0))) for _, pose, _ in kfs])
        out_acc = acc(quats, 5126, "VEC4")
        samplers.append({"input": time_acc, "output": out_acc,
                         "interpolation": "LINEAR"})
        channels.append({"sampler": len(samplers) - 1,
                         "target": {"node": ni, "path": "rotation"}})
    # hips translation track
    hips_base = np.array(BONES[0][2], dtype=np.float32)
    trans = np.stack([hips_base + np.array([0, dy, 0]) for _, _, dy in kfs]).astype(np.float32)
    out_acc = acc(trans, 5126, "VEC3")
    samplers.append({"input": time_acc, "output": out_acc, "interpolation": "LINEAR"})
    channels.append({"sampler": len(samplers) - 1,
                     "target": {"node": 0, "path": "translation"}})

    j = {"asset": {"version": "2.0", "generator": "rig-repair make_clips.py v1 (test fixtures)"},
         "scene": 0, "scenes": [{"nodes": [0]}],
         "nodes": nodes,
         "animations": [{"name": name, "channels": channels, "samplers": samplers}],
         "accessors": accessors, "bufferViews": bufferViews,
         "buffers": [{"byteLength": len(blob)}]}
    jb = json.dumps(j, separators=(",", ":")).encode()
    jb += b" " * (-len(jb) % 4)
    with open(out_path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, 28 + len(jb) + len(blob)))
        f.write(struct.pack("<II", len(jb), 0x4E4F534A))
        f.write(jb)
        f.write(struct.pack("<II", len(blob), 0x004E4942))
        f.write(blob)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, kfs in CLIPS.items():
        p = os.path.join(OUT, name + ".glb")
        write_clip(name, kfs, p)
        print("wrote", p, os.path.getsize(p), "bytes")

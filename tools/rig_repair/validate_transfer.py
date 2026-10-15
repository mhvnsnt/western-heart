#!/usr/bin/env python3
"""Extreme-pose validation battery for case-2 weight transfers.

Pure numpy: skins the GLB's meshes under scripted joint rotations (on top of
the TPose clip base) and measures worst triangle-edge stretch per mesh per
pose, plus cuff-to-wrist tracking. No Blender needed.

Usage:
    python3 validate_transfer.py model.glb [--json report.json]

Gate: EVERY mesh < 2.5 max edge stretch in EVERY pose; cuffs stay attached.
Poses replicate the Blender proof renders (transfer proof renders use the same
joint euler overrides on the TPose_Character action base).
"""
import json
import struct
import sys

import numpy as np

# ---------------------------------------------------------------- GLB io

def load(p):
    b = open(p, "rb").read()
    n = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + n])
    o = 20 + n
    bl = struct.unpack("<I", b[o:o + 4])[0]
    return j, bytearray(b[o + 8:o + 8 + bl])


def view(j, binb, i):
    A = j["accessors"][i]
    bv = j["bufferViews"][A["bufferView"]]
    n = {"VEC4": 4, "VEC3": 3, "MAT4": 16, "SCALAR": 1}[A["type"]]
    dt = {5126: np.float32, 5121: np.uint8, 5123: np.uint16}[A["componentType"]]
    o = bv.get("byteOffset", 0) + A.get("byteOffset", 0)
    return np.frombuffer(bytes(binb[o:o + np.dtype(dt).itemsize * n * A["count"]]),
                         dt).reshape(A["count"], n).copy()


# ---------------------------------------------------------------- math

def euler_xyz_to_quat(e):
    x, y, z = e
    cx, sx = np.cos(x / 2), np.sin(x / 2)
    cy, sy = np.cos(y / 2), np.sin(y / 2)
    cz, sz = np.cos(z / 2), np.sin(z / 2)
    # XYZ intrinsic order
    w = cx * cy * cz - sx * sy * sz
    xq = sx * cy * cz + cx * sy * sz
    yq = cx * sy * cz - sx * cy * sz
    zq = cx * cy * sz + sx * sy * cz
    return np.array([xq, yq, zq, w])


def qm(q):
    x, y, z, w = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


# ---------------------------------------------------------------- poses
# joint euler (XYZ radians) overrides on the TPose clip base

POSES = {
    "S1_cuffs_raise": {
        "LeftArm": (2.0, 0, 0), "RightArm": (2.0, 0, 0)},
    "S2_logo_bend": {
        "Spine1": (0.45, 0, 0), "Spine2": (0.30, 0, 0)},
    "S3_pants_stance": {
        "LeftUpLeg": (0, 0, 0.6), "RightUpLeg": (0, 0, -0.6)},
    "X1_arms_overhead": {
        "LeftArm": (2.6, 0, 0), "RightArm": (2.6, 0, 0)},
    "X2_arms_crossed": {
        "LeftArm": (1.3, 0, 0.55), "RightArm": (1.3, 0, -0.55),
        "LeftForeArm": (0.2, 0, 0.9), "RightForeArm": (0.2, 0, -0.9)},
    "X3_crouch_wide": {
        "LeftUpLeg": (1.2, 0, 0.9), "RightUpLeg": (1.2, 0, -0.9),
        "LeftLeg": (-1.0, 0, 0), "RightLeg": (-1.0, 0, 0)},
    "X4_spine_bend_twist": {
        "Spine": (0.3, 0.25, 0), "Spine1": (0.3, 0.25, 0),
        "Spine2": (0.2, 0, 0)},
    "X5_wrestler": {
        "LeftArm": (2.6, 0, 0), "RightArm": (2.6, 0, 0),
        "Spine": (-0.2, 0, 0), "Spine1": (-0.2, 0, 0),
        "Spine2": (-0.1, 0, 0)},
}

ARM_POSES = ["S1_cuffs_raise", "X1_arms_overhead", "X5_wrestler"]
CUFF_SUBS = ["belt2", "buckles"]
WRIST_JOINTS = ["LeftHand", "RightHand"]


def main():
    path = sys.argv[1]
    j, b = load(path)
    N = j["nodes"]
    par = {c: i for i, n in enumerate(N) for c in n.get("children", [])}
    name2idx = {n.get("name"): i for i, n in enumerate(N) if n.get("name")}

    # TPose clip base transforms (frame 0)
    tpose = next(a for a in j["animations"] if a["name"] == "TPose")
    ch = {"rotation": {}, "translation": {}, "scale": {}}
    for c in tpose["channels"]:
        samp = tpose["samplers"][c["sampler"]]
        acc = j["accessors"][samp["output"]]
        if acc["type"] == "SCALAR":
            continue
        v = view(j, b, samp["output"])
        ch[c["target"]["path"]][c["target"]["node"]] = v[0]

    sk = j["skins"][0]
    ibm = view(j, b, sk["inverseBindMatrices"]).reshape(-1, 4, 4).transpose(0, 2, 1)
    joint_nodes = sk["joints"]  # joint index -> node index

    def pose_world(overrides):
        memo = {}

        def loc(i):
            n = N[i]
            R = ch["rotation"].get(i, np.array(n.get("rotation", [0, 0, 0, 1])))
            nm = n.get("name")
            if nm in overrides:
                R = euler_xyz_to_quat(overrides[nm])
            M = np.eye(4)
            M[:3, :3] = qm(R) @ np.diag(
                ch["scale"].get(i, np.array(n.get("scale", [1, 1, 1]))))
            M[:3, 3] = ch["translation"].get(i, np.array(n.get("translation", [0, 0, 0])))
            return M

        def W(i):
            if i not in memo:
                memo[i] = (W(par[i]) if i in par else np.eye(4)) @ loc(i)
            return memo[i]

        Mj = np.array([W(nd) @ ibm[k] for k, nd in enumerate(joint_nodes)])
        Wj = [W(nd) for nd in joint_nodes]
        return Mj, Wj

    # mesh inventory: node name -> list of (positions, joints, weights, indices, mesh_name)
    meshes = []
    for n in N:
        if "mesh" not in n:
            continue
        for pr in j["meshes"][n["mesh"]]["primitives"]:
            at = pr["attributes"]
            if "JOINTS_0" not in at or "indices" not in pr:
                continue
            P = view(j, b, at["POSITION"])[:, :3]
            J = view(j, b, at["JOINTS_0"]).astype(int)
            Wt = view(j, b, at["WEIGHTS_0"])
            A = j["accessors"][pr["indices"]]
            bv = j["bufferViews"][A["bufferView"]]
            dt = {5125: np.uint32, 5123: np.uint16, 5121: np.uint8}[A["componentType"]]
            o = bv.get("byteOffset", 0) + A.get("byteOffset", 0)
            I = np.frombuffer(bytes(b[o:o + np.dtype(dt).itemsize * A["count"]]),
                              dt).reshape(-1, 3)
            meshes.append({"node": n.get("name"), "P": P, "J": J, "W": Wt, "I": I})

    def skin(Mj, m):
        Ph = np.c_[m["P"], np.ones(len(m["P"]))]
        return np.einsum("vk,vkij,vj->vi", m["W"], Mj[m["J"]], Ph)[:, :3]

    def max_stretch(m, S):
        P, I = m["P"], m["I"]
        rs = []
        for e0, e1 in ((0, 1), (1, 2), (2, 0)):
            l0 = np.linalg.norm(P[I[:, e0]] - P[I[:, e1]], axis=1)
            l1 = np.linalg.norm(S[I[:, e0]] - S[I[:, e1]], axis=1)
            ok = l0 > 5e-3
            rs.append(l1[ok] / l0[ok])
        r = np.concatenate(rs)
        return float(r.max())

    wrist_idx = {w: joint_nodes.index(name2idx[w]) for w in WRIST_JOINTS}
    cuff_meshes = [m for m in meshes
                   if any(s in (m["node"] or "").lower() for s in CUFF_SUBS)]

    report = {"model": path, "poses": {}, "cuff_tracking": {}, "gate": 2.5}
    all_ok = True

    for pname, overrides in POSES.items():
        Mj, _Wj = pose_world(overrides)
        per_mesh = {}
        for m in meshes:
            s = max_stretch(m, skin(Mj, m))
            per_mesh[m["node"]] = round(s, 2)
            if s >= 2.5:
                all_ok = False
        report["poses"][pname] = per_mesh

    # cuff tracking through arm raises: max cuff-vert distance to nearest wrist
    for pname in ARM_POSES:
        Mj, Wj = pose_world(POSES[pname])
        wpos = {w: (Wj[wrist_idx[w]] @ np.array([0, 0, 0, 1]))[:3]
                for w in WRIST_JOINTS}
        worst = 0.0
        for m in cuff_meshes:
            S = skin(Mj, m)
            d = np.minimum(
                np.linalg.norm(S - wpos["LeftHand"], axis=1),
                np.linalg.norm(S - wpos["RightHand"], axis=1))
            worst = max(worst, float(d.max()))
        report["cuff_tracking"][pname] = round(worst, 3)
        if worst >= 0.20:
            all_ok = False

    report["pass"] = bool(all_ok)
    # worst offenders summary
    worst5 = []
    for pname, pm in report["poses"].items():
        for mn, s in pm.items():
            worst5.append((s, pname, mn))
    worst5.sort(reverse=True)
    report["worst_5"] = [(s, p, m) for s, p, m in worst5[:5]]

    out = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "--json" else None
    if "--json" in sys.argv:
        jp = sys.argv[sys.argv.index("--json") + 1]
        json.dump(report, open(jp, "w"), indent=1)
        print(f"report -> {jp}")

    print(f"MODEL {path}")
    for pname in POSES:
        pm = report["poses"][pname]
        w = max(pm.values())
        flag = "" if w < 2.5 else "  <-- FAIL"
        print(f"  {pname:22s} worst {w:6.2f}{flag}")
    print("cuff tracking (max vert->wrist m):",
          {k: v for k, v in report["cuff_tracking"].items()})
    print("GATE:", "PASS" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

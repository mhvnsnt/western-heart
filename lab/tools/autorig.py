#!/usr/bin/env python3
"""Non-destructive auto-rig for owner-made T-pose GLBs (Tripo exports) onto WH-Canonical-22.

Reads the original GLB (never modified), decodes it (gltf-transform dequantize/weld/simplify
done beforehand -> *_game.glb), orients it to Y-up / face +Z / feet on floor, scales to a
target height, places canonical joints from body landmarks, computes smooth skin weights
(inverse-distance to bone segments, top-4, normalised; tail/back verts -> Hips), and writes a
new skinned GLB with the textures + the canonical combat clips.
Usage: autorig.py in_game.glb out.glb --height 1.85 --face +x
"""
import argparse, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gltf_eval import Gltf
from gltf_write import GLB
import clips as CL

CANON = [b for b in json.load(open(Path(__file__).resolve().parents[1] / "skeleton/canonical_skeleton.json"))["bones"]]

def landmarks(P, H):
    """Joint positions for a T-pose humanoid (Y-up, faces +Z, feet y=0, centred)."""
    y = P[:, 1]; ax = np.abs(P[:, 0])
    span = ax.max()
    armband = P[(y > 0.70 * H) & (y < 0.90 * H)]
    arm_y = float(np.median(armband[np.abs(armband[:, 0]) > 0.6 * span][:, 1])) if len(armband) else 0.8 * H
    j = {}
    j["Root"] = [0, 0.53 * H, 0]; j["Hips"] = [0, 0.53 * H, 0]; j["Spine"] = [0, 0.62 * H, 0]; j["Chest"] = [0, 0.72 * H, 0]
    j["Neck"] = [0, 0.84 * H, 0]; j["Head"] = [0, 0.88 * H, 0]
    feet = P[y < 0.06 * H]
    for s, sx in (("Left", 1), ("Right", -1)):
        sh = 0.11 * H
        j[s + "Shoulder"] = [sx * 0.04 * H, arm_y, 0]
        j[s + "Arm"] = [sx * sh, arm_y, 0]
        j[s + "ForeArm"] = [sx * (sh + 0.47 * (span - sh)), arm_y, 0]
        j[s + "Hand"] = [sx * (sh + 0.85 * (span - sh)), arm_y, 0]
        side = feet[feet[:, 0] * sx > 0]
        fx = float(np.median(side[:, 0])) if len(side) else sx * 0.08 * H
        fz = float(np.median(side[:, 2])) if len(side) else 0
        j[s + "UpLeg"] = [sx * 0.09 * H * 0.6 + fx * 0.4, 0.50 * H, 0]
        j[s + "Leg"] = [fx, 0.28 * H, 0.01 * H]
        j[s + "Foot"] = [fx, 0.05 * H, fz - 0.02 * H]
        j[s + "ToeBase"] = [fx, 0.015 * H, fz + 0.07 * H]
    return {k: np.array(v, float) for k, v in j.items()}

def seg_dist(P, a, b):
    ab = b - a; t = np.clip(((P - a) @ ab) / max(ab @ ab, 1e-9), 0, 1)
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("out"); ap.add_argument("--height", type=float, default=1.85)
    ap.add_argument("--face", default="+x"); ap.add_argument("--source-note", default=""); ap.add_argument("--smooth", type=int, default=25)
    a = ap.parse_args()
    g = Gltf(a.src); W = g.world()
    ni = [i for i, n in enumerate(g.nodes) if "mesh" in n][0]
    pr = g.j["meshes"][g.nodes[ni]["mesh"]]["primitives"][0]
    P = g.acc(pr["attributes"]["POSITION"]).astype(float); P = (np.c_[P, np.ones(len(P))] @ W[ni].T)[:, :3]
    N = g.acc(pr["attributes"]["NORMAL"]).astype(float) @ W[ni][:3, :3].T
    UV = g.acc(pr["attributes"]["TEXCOORD_0"]).astype(np.float32); IDX = g.acc(pr["indices"])[:, 0].astype(np.uint32)
    rot = {"+x": np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]]), "-x": np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]]), "+z": np.eye(3), "-z": np.diag([-1, 1, -1])}[a.face]
    P = P @ rot.T; N = N @ rot.T
    P[:, 1] -= P[:, 1].min(); s = a.height / P[:, 1].max(); P *= s
    P[:, 0] -= (P[:, 0].max() + P[:, 0].min()) / 2; P[:, 2] -= np.median(P[P[:, 1] > 0.6 * a.height][:, 2])
    J = landmarks(P, a.height)
    names = [b["name"] for b in CANON]; parent = [names.index(b["parent"]) if b["parent"] else -1 for b in CANON]
    piv = np.array([J[n] for n in names])
    # bone segments: bone -> first child (leaf: short extension)
    D = np.full((len(P), len(names)), 1e9)
    for b, n in enumerate(names):
        if n == "Root": continue
        kids = [c for c in range(len(names)) if parent[c] == b]
        end = piv[kids[0]] if kids and n not in ("Hips",) else piv[b] + np.array([0, -0.0 if n != "Head" else 0.15 * a.height, 0])
        if n == "Hips": end = piv[names.index("Spine")]
        if n == "Head": end = piv[b] + [0, 0.12 * a.height, 0]
        if n.endswith("Hand"): end = piv[b] + (piv[b] - piv[parent[b]]) * 0.6
        if n.endswith("ToeBase"): end = piv[b] + [0, 0, 0.04 * a.height]
        D[:, b] = seg_dist(P, piv[b], end)
    # keep arms off torso and legs apart: lateral gating
    for b, n in enumerate(names):
        if "Left" in n and n.replace("Left", "") not in ("Shoulder",): D[P[:, 0] < -0.02 * a.height, b] = 1e9
        if "Right" in n and n.replace("Right", "") not in ("Shoulder",): D[P[:, 0] > 0.02 * a.height, b] = 1e9
    # tail / anything far behind the pelvis follows the hips
    tail = (P[:, 2] < -0.10 * a.height) & (P[:, 1] < 0.6 * a.height) & (P[:, 1] > 0.1 * a.height)
    D[tail, :] = 1e9; D[tail, names.index("Hips")] = 0.01
    Wf = 1.0 / np.maximum(D, 1e-3) ** 4; Wf[D > 1e8] = 0; Wf /= Wf.sum(1, keepdims=True)
    # arms never pull torso/mane verts; legs never pull above the pelvis
    for b, n in enumerate(names):
        if any(n.endswith(x) for x in ("Arm", "ForeArm", "Hand")) and not n.endswith("UpLeg"):
            ax_ = abs(piv[names.index(("Left" if "Left" in n else "Right") + "Arm")][0]); Wf[(np.abs(P[:, 0]) < ax_ + 0.03 * a.height) | (P[:, 2] < -0.08 * a.height), b] = 0
        if any(n.endswith(x) for x in ("UpLeg", "Leg", "Foot", "ToeBase")):
            Wf[P[:, 1] > piv[names.index("Hips")][1] + 0.03 * a.height, b] = 0
    Wf /= np.maximum(Wf.sum(1, keepdims=True), 1e-12)
    # Laplacian smoothing of weights over mesh adjacency (removes seams / armpit tearing)
    import scipy.sparse as sp
    tri = IDX.reshape(-1, 3); rows = np.concatenate([tri[:, 0], tri[:, 1], tri[:, 2], tri[:, 1], tri[:, 2], tri[:, 0]]); cols = np.concatenate([tri[:, 1], tri[:, 2], tri[:, 0], tri[:, 0], tri[:, 1], tri[:, 2]])
    A = sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(P), len(P))); A.data[:] = 1
    deg = np.asarray(A.sum(1)).ravel(); Dinv = sp.diags(1 / np.maximum(deg, 1))
    lock = tail
    for _ in range(a.smooth):
        Wn = 0.5 * Wf + 0.5 * (Dinv @ A @ Wf); Wn[lock] = Wf[lock]; Wf = Wn
    # continuous sparsification: subtract a constant floor (<=4 influences when tau>=0.2), renormalise
    tau = np.minimum(0.2, 0.5 * Wf.max(1, keepdims=True)); Ws = np.maximum(Wf - tau, 0); Wf = Ws / Ws.sum(1, keepdims=True)
    k = 4; order = np.argsort(-Wf, 1)[:, :k]; w = np.take_along_axis(Wf, order, 1); w /= w.sum(1, keepdims=True)
    # out
    out = GLB(); j = out.j
    # copy images/textures/material from source
    for im in g.j.get("images", []):
        bv = g.j["bufferViews"][im["bufferView"]]; data = g.bin[bv.get("byteOffset", 0):bv.get("byteOffset", 0) + bv["byteLength"]]
        j.setdefault("images", []).append({"bufferView": out._view(bytes(data)), "mimeType": im["mimeType"]})
    j["textures"] = [{"source": t["source"], **({"sampler": 0} if "sampler" in t else {})} for t in g.j.get("textures", [])]
    if g.j.get("samplers"): j["samplers"] = g.j["samplers"]
    mat = dict(g.j["materials"][0]); mat["name"] = "owner_original"; mat["doubleSided"] = True; j["materials"] = [mat]
    attrs = {"POSITION": out.acc(P.astype(np.float32), "VEC3", 34962, True), "NORMAL": out.acc((N / np.linalg.norm(N, axis=1, keepdims=True)).astype(np.float32), "VEC3", 34962),
             "TEXCOORD_0": out.acc(UV, "VEC2", 34962), "JOINTS_0": out.acc(order.astype(np.uint8), "VEC4", 34962), "WEIGHTS_0": out.acc(w.astype(np.float32), "VEC4", 34962)}
    j["meshes"] = [{"name": "body", "primitives": [{"attributes": attrs, "indices": out.acc(IDX, "SCALAR", 34963), "material": 0}]}]
    nodes = []
    for b, n in enumerate(names):
        loc = piv[b] - (piv[parent[b]] if parent[b] >= 0 else 0); nodes.append(out.node(name=n, translation=[float(x) for x in loc]))
    for b in range(len(names)):
        ch = [nodes[c] for c in range(len(names)) if parent[c] == b]
        if ch: j["nodes"][nodes[b]]["children"] = ch
    ibm = np.array([np.eye(4) for _ in names], np.float32)
    for b in range(len(names)): ibm[b][:3, 3] = -piv[b]
    j["skins"] = [{"name": "WH-Canonical-22", "joints": nodes, "skeleton": nodes[0], "inverseBindMatrices": out.acc(np.ascontiguousarray(ibm.transpose(0, 2, 1).reshape(-1, 16)), "MAT4")}]
    mn = out.node(name="body", mesh=0, skin=0); j["scenes"][0]["nodes"] = [out.node(name="Fighter", children=[nodes[0], mn])]
    rig = {"names": names, "parent": parent, "pivot": piv}
    j["animations"] = []
    for cn, clip in CL.build_all(rig).items():
        chs, smp = [], []
        for bi, (times, quats, trans) in clip.items():
            ta = out.acc(np.array(times, np.float32), "SCALAR", None, True)
            smp.append({"input": ta, "output": out.acc(np.array(quats, np.float32), "VEC4"), "interpolation": "LINEAR"}); chs.append({"sampler": len(smp) - 1, "target": {"node": nodes[bi], "path": "rotation"}})
            if trans is not None:
                smp.append({"input": ta, "output": out.acc(np.array(trans, np.float32), "VEC3"), "interpolation": "LINEAR"}); chs.append({"sampler": len(smp) - 1, "target": {"node": nodes[bi], "path": "translation"}})
        j["animations"].append({"name": cn, "channels": chs, "samplers": smp})
    j["extras"] = {"source": a.src, "provenance": "ORIGINAL (owner-made)", "note": a.source_note, "rig": "autorig.py landmarks + inverse-distance weights (non-destructive; original untouched)"}
    out.save(a.out); print(json.dumps({"verts": len(P), "tris": len(IDX) // 3, "bones": len(names), "height": a.height}))

if __name__ == "__main__":
    main()

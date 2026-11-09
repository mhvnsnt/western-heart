#!/usr/bin/env python3
"""Acceptance probe for a skinned GLB, replicating the metric definitions of
docs/handoffs/NIGHTWOLF-RERIG-REPORT-2026-11-07.md (PR #1692):

- dominant verts per bone: verts whose top skin weight (>0.5) is that bone
- arm segment distance: median distance from a bone's dominant verts to its
  bone segment (head->child head; for end bones, head->tail)
- height offset: |median y of dominant verts - joint y| for Arm/ForeArm bones
- face slab: verts with y in [1.44, 1.64] (at 1.67 m scale), share whose top
  weight is the Head bone
- stretch/crush check under poses is done in the render harness, not here.

Skinned world positions are computed through the skin bind matrices
(jointWorld @ inverseBindMatrix), per the report's method note.

Usage: probe_acceptance.py model.glb [--scale-band 1.44,1.64] > metrics.json
Requires: numpy. Decodes plain (uncompressed) glTF only; for meshopt files,
decode first with the repo codec.
"""
import argparse, json, struct, sys
import numpy as np


def load_glb(path):
    raw = open(path, "rb").read()
    assert raw[:4] == b"glTF", "not a GLB"
    jlen = struct.unpack("<I", raw[12:16])[0]
    gltf = json.loads(raw[20:20 + jlen])
    off = 20 + jlen
    blen = struct.unpack("<I", raw[off:off + 4])[0]
    buf = raw[off + 8:off + 8 + blen]
    return gltf, buf


def acc_data(gltf, buf, idx):
    acc = gltf["accessors"][idx]
    bv = gltf["bufferViews"][acc["bufferView"]]
    start = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    ncomp = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}[acc["type"]]
    dt = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8}[acc["componentType"]]
    count = acc["count"]
    stride = bv.get("byteStride")
    if stride and stride != ncomp * np.dtype(dt).itemsize:
        raw = np.frombuffer(buf, dtype=np.uint8, count=count * stride, offset=start)
        raw = raw.reshape(count, stride)[:, :ncomp * np.dtype(dt).itemsize]
        return np.ascontiguousarray(raw).view(dt).reshape(count, ncomp) if ncomp > 1 else np.ascontiguousarray(raw).view(dt).reshape(count)
    arr = np.frombuffer(buf, dtype=dt, count=count * ncomp, offset=start)
    return arr.reshape(count, ncomp) if ncomp > 1 else arr


def node_world(gltf, idx, cache):
    if idx in cache:
        return cache[idx]
    nd = gltf["nodes"][idx]
    m = np.eye(4)
    if "matrix" in nd:
        m = np.array(nd["matrix"], dtype=np.float64).reshape(4, 4).T
    else:
        t = np.array(nd.get("translation", [0, 0, 0]), dtype=np.float64)
        r = np.array(nd.get("rotation", [0, 0, 0, 1]), dtype=np.float64)
        s = np.array(nd.get("scale", [1, 1, 1]), dtype=np.float64)
        x, y, z, w = r
        R = np.array([
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
        m[:3, :3] = R * s
        m[:3, 3] = t
    parent = None
    for i, n in enumerate(gltf["nodes"]):
        if idx in n.get("children", []):
            parent = i
            break
    if parent is not None:
        m = node_world(gltf, parent, cache) @ m
    cache[idx] = m
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("glb")
    ap.add_argument("--band", default="1.44,1.64")
    a = ap.parse_args()
    lo, hi = (float(x) for x in a.band.split(","))
    gltf, buf = load_glb(a.glb)
    skin = gltf["skins"][0]
    joints = skin["joints"]
    names = [gltf["nodes"][j].get("name", f"joint{j}") for j in joints]
    ibms = acc_data(gltf, buf, skin["inverseBindMatrices"]).reshape(-1, 4, 4)
    ibms = np.transpose(ibms, (0, 2, 1))
    cache = {}
    jworld = np.stack([node_world(gltf, j, cache) for j in joints])
    bindm = jworld @ ibms  # per-joint skin bind matrix
    jpos = jworld[:, :3, 3]

    # gather skinned bind-pose verts across all skinned meshes
    allpos, alltop, allw = [], [], []
    for nd in gltf["nodes"]:
        if "mesh" not in nd or "skin" not in nd:
            continue
        for prim in gltf["meshes"][nd["mesh"]]["primitives"]:
            pos = acc_data(gltf, buf, prim["attributes"]["POSITION"]).astype(np.float64)
            j4 = acc_data(gltf, buf, prim["attributes"]["JOINTS_0"]).astype(int)
            w4 = acc_data(gltf, buf, prim["attributes"]["WEIGHTS_0"]).astype(np.float64)
            sk = np.zeros_like(pos)
            for k in range(4):
                m = bindm[j4[:, k]]
                sk += w4[:, k:k + 1] * (pos @ m[:, :3, :3].transpose(0, 2, 1) + m[:, :3, 3])
            allpos.append(sk)
            alltop.append(j4[np.arange(len(pos)), np.argmax(w4, axis=1)])
            allw.append(w4.max(axis=1))
    pos = np.concatenate(allpos)
    top = np.concatenate(alltop)
    topw = np.concatenate(allw)
    by_name = {n: i for i, n in enumerate(names)}

    def seg_dist(bi):
        head = jpos[bi]
        # child: the joint whose parent is bi (first found)
        child = None
        for cj, jn in enumerate(joints):
            p = None
            for i, n in enumerate(gltf["nodes"]):
                if jn in n.get("children", []):
                    p = i
                    break
            if p == joints[bi]:
                child = cj
                break
        tail = jpos[child] if child is not None else head + np.array([0, 0.1, 0])
        d = tail - head
        L2 = float(d @ d) or 1.0
        t = np.clip(((pos - head) @ d) / L2, 0, 1)
        proj = head + t[:, None] * d
        return np.linalg.norm(pos - proj, axis=1)

    out = {"file": a.glb, "n_verts": int(len(pos)), "n_joints": len(joints),
           "names": names, "bones": {}}
    for bn in ("LeftArm", "RightArm", "LeftForeArm", "RightForeArm",
               "LeftHand", "RightHand", "Head", "Neck"):
        if bn not in by_name:
            continue
        bi = by_name[bn]
        dom = (top == bi) & (topw > 0.5)
        entry = {"dominant_verts": int(dom.sum())}
        if dom.sum():
            sd = seg_dist(bi)
            entry["seg_median_m"] = float(np.median(sd[dom]))
            entry["height_offset_m"] = float(abs(np.median(pos[dom][:, 1]) - jpos[bi][1]))
        out["bones"][bn] = entry
    if "Head" in by_name:
        slab = (pos[:, 1] >= lo) & (pos[:, 1] <= hi)
        hb = by_name["Head"]
        out["face_slab"] = {"band": [lo, hi], "verts": int(slab.sum()),
                            "head_top_share": float((top[slab] == hb).mean()) if slab.sum() else None,
                            "head_dominant_share": float(((top[slab] == hb) & (topw[slab] > 0.5)).mean()) if slab.sum() else None}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Case-2 weight fix: copy skin weights from correctly-weighted body meshes onto
broken accessory meshes by nearest-vertex lookup. Fully automatic — no
hand-painted weights, no vertex edits, no Blender required.

The defect class: an accessory mesh (cuffs, logo, clothing panels) authored with
weights to the wrong bones (e.g. wrist cuffs 100% on Spine), so it detaches or
tears when the body moves. The fix copies the (joints, weights) of the nearest
vertex on the body mesh underneath it — the same nearest-vertex weight-copy
algorithm as Blender's Data Transfer modifier (the standard game-modding
approach), implemented directly on the glTF skin data.

Usage:
    python3 transfer_weights.py --in in.glb --out out.glb \
        --spec transfers.json --report report.json

transfers.json:
    {"transfers": [
        {"target": "belt2",  "sources": ["arms"]},
        {"target": "buckles","sources": ["arms"]},
        {"target": "logo",   "sources": ["torso"]},
        {"target": "pants",  "sources": ["torso", "thighs"]},
        {"target": "thighs", "sources": ["torso", "thighs"]}
    ]}
Mesh names match by case-insensitive substring against node names (exactly one
match required). Multiple sources are pooled: each target vertex copies from
whichever source vertex is closest, so boundary regions (pants hips, thigh
tops) pick up the right bones automatically.

All mesh nodes must share the same skin and identity node transforms (true for
this pipeline's exports); positions are compared directly.

Writes a NEW file; the input is never modified.
"""
import argparse
import json
import struct
import sys

import numpy as np


def load(p):
    b = open(p, "rb").read()
    n = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + n])
    o = 20 + n
    bl = struct.unpack("<I", b[o:o + 4])[0]
    return j, bytearray(b[o + 8:o + 8 + bl])


def save(p, j, binb):
    js = json.dumps(j, separators=(",", ":")).encode()
    js += b" " * (-len(js) % 4)
    binb = bytes(binb) + b"\0" * (-len(binb) % 4)
    out = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(binb))
    out += struct.pack("<II", len(js), 0x4E4F534A) + js
    out += struct.pack("<II", len(binb), 0x004E4942) + binb
    open(p, "wb").write(out)


_DT = {5126: np.float32, 5121: np.uint8, 5123: np.uint16, 5125: np.uint32}
_NT = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def view(j, binb, i):
    A = j["accessors"][i]
    bv = j["bufferViews"][A["bufferView"]]
    n = _NT[A["type"]]
    dt = _DT[A["componentType"]]
    o = bv.get("byteOffset", 0) + A.get("byteOffset", 0)
    return np.frombuffer(bytes(binb[o:o + np.dtype(dt).itemsize * n * A["count"]]),
                         dt).reshape(A["count"], n)


def write_back(j, binb, i, arr):
    """Overwrite accessor i's bytes with arr (same shape/dtype required)."""
    A = j["accessors"][i]
    bv = j["bufferViews"][A["bufferView"]]
    n = _NT[A["type"]]
    dt = _DT[A["componentType"]]
    assert arr.shape == (A["count"], n), f"shape {arr.shape} vs {(A['count'], n)}"
    assert arr.dtype == dt, f"dtype {arr.dtype} vs {dt}"
    o = bv.get("byteOffset", 0) + A.get("byteOffset", 0)
    raw = np.ascontiguousarray(arr, dtype=dt).tobytes()
    binb[o:o + len(raw)] = raw


def find_node(nodes, sub):
    cands = [nd for nd in nodes
             if "mesh" in nd and sub.lower() in (nd.get("name") or "").lower()]
    if len(cands) != 1:
        raise RuntimeError(
            f"mesh spec '{sub}' matched {len(cands)} nodes: "
            f"{[c.get('name') for c in cands]} (need exactly 1)")
    return cands[0]


def prim_of(j, node):
    prims = j["meshes"][node["mesh"]]["primitives"]
    skinned = [pr for pr in prims if "JOINTS_0" in pr["attributes"]]
    if len(skinned) != 1:
        raise RuntimeError(f"node {node.get('name')}: {len(skinned)} skinned prims")
    return skinned[0]


def indices_of(j, binb, pr):
    A = j["accessors"][pr["indices"]]
    bv = j["bufferViews"][A["bufferView"]]
    dt = {5125: np.uint32, 5123: np.uint16, 5121: np.uint8}[A["componentType"]]
    o = bv.get("byteOffset", 0) + A.get("byteOffset", 0)
    return np.frombuffer(bytes(binb[o:o + np.dtype(dt).itemsize * A["count"]]),
                         dt).reshape(-1, 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--knn", type=int, default=4,
                    help="nearest source verts to blend per target vert")
    ap.add_argument("--smooth", type=int, default=8,
                    help="laplacian smoothing iterations on the weight field")
    a = ap.parse_args()

    spec = json.load(open(a.spec))
    j, binb = load(a.inp)
    nodes = j["nodes"]
    report = {"input": a.inp, "output": a.out, "transfers": [],
              "knn": a.knn, "smooth_iters": a.smooth}

    for t in spec["transfers"]:
        tnode = find_node(nodes, t["target"])
        snodes = [find_node(nodes, s) for s in t["sources"]]
        tpr = prim_of(j, tnode)
        ta = tpr["attributes"]

        P_t = view(j, binb, ta["POSITION"])[:, :3].astype(np.float64)
        J_t = view(j, binb, ta["JOINTS_0"])
        W_t = view(j, binb, ta["WEIGHTS_0"])
        j_dt, w_dt = J_t.dtype, W_t.dtype
        I_t = indices_of(j, binb, tpr)

        # pool source verts
        sP, sJ, sW = [], [], []
        for sn in snodes:
            pr = prim_of(j, sn)
            sa = pr["attributes"]
            sP.append(view(j, binb, sa["POSITION"])[:, :3].astype(np.float64))
            sJ.append(view(j, binb, sa["JOINTS_0"]))
            sW.append(view(j, binb, sa["WEIGHTS_0"]))
        sP = np.concatenate(sP)
        sJ = np.concatenate(sJ).astype(np.int64)
        sW = np.concatenate(sW).astype(np.float64)

        # k-NN inverse-distance blend of source weight distributions
        nj = sJ.shape[1]
        newW_full = {}  # joint_idx -> weight array
        CH = 128
        k = min(a.knn, len(sP))
        for s0 in range(0, len(P_t), CH):
            c = P_t[s0:s0 + CH]
            d2 = ((c[:, None, :] - sP[None, :, :]) ** 2).sum(-1)
            nn = np.argpartition(d2, k - 1, axis=1)[:, :k]
            dist = np.sqrt(np.take_along_axis(d2, nn, axis=1))
            w = 1.0 / (dist + 1e-6)
            w /= w.sum(1, keepdims=True)
            sj = sJ[nn]          # (chunk, k, nj)
            sw = sW[nn]          # (chunk, k, nj)
            # accumulate joint->weight per target vert
            for ci in range(c.shape[0]):
                acc = {}
                for ki in range(k):
                    for ji in range(nj):
                        jidx = int(sj[ci, ki, ji])
                        wt = float(sw[ci, ki, ji]) * float(w[ci, ki])
                        if wt > 1e-9:
                            acc[jidx] = acc.get(jidx, 0.0) + wt
                # keep top 4 influences, renormalize
                items = sorted(acc.items(), key=lambda x: -x[1])[:4]
                tot = sum(v for _, v in items) or 1.0
                for jidx, wt in items:
                    newW_full.setdefault(jidx, np.zeros(len(P_t)))[s0 + ci] = wt / tot

        # densify to (verts, 4) JOINTS/WEIGHTS
        joints_sorted = sorted(newW_full.keys())
        jmap = {jj: ii for ii, jj in enumerate(joints_sorted)}
        dense = np.zeros((len(P_t), len(joints_sorted)))
        for jj, arr in newW_full.items():
            dense[:, jmap[jj]] = arr
        # per-vert top-4
        newJ = np.zeros((len(P_t), 4), dtype=np.int64)
        newW = np.zeros((len(P_t), 4))
        top4 = np.argpartition(-dense, min(4, dense.shape[1]) - 1, axis=1)[:, :4]
        for vi in range(len(P_t)):
            js = top4[vi]
            ws = dense[vi, js]
            o = np.argsort(-ws)
            js, ws = js[o], ws[o]
            newJ[vi, :len(js)] = np.array([joints_sorted[x] for x in js])
            newW[vi, :len(ws)] = ws / (ws.sum() or 1.0)

        # laplacian smooth the weight field over mesh topology
        if a.smooth > 0:
            adj = [set() for _ in range(len(P_t))]
            for tri in I_t:
                for e0, e1 in ((0, 1), (1, 2), (2, 0)):
                    adj[int(tri[e0])].add(int(tri[e1]))
                    adj[int(tri[e1])].add(int(tri[e0]))
            # smooth as joint-indexed dense field
            fld = np.zeros((len(P_t), len(joints_sorted)))
            for jj, ii in jmap.items():
                fld[:, ii] = newW_full[jj]
            for _ in range(a.smooth):
                nxt = fld.copy()
                for vi in range(len(P_t)):
                    nb = adj[vi]
                    if nb:
                        nxt[vi] = (fld[vi] + sum(fld[u] for u in nb)) / (1 + len(nb))
                fld = nxt
            # back to top-4 per vert
            for vi in range(len(P_t)):
                o = np.argpartition(-fld[vi], min(4, len(joints_sorted)) - 1)[:4]
                o = o[np.argsort(-fld[vi, o])]
                ws = fld[vi, o]
                ws = ws / (ws.sum() or 1.0)
                newJ[vi] = 0
                newW[vi] = 0
                for ii, (jj, ww) in enumerate(zip(o, ws)):
                    if ww > 1e-6 and ii < 4:
                        newJ[vi, ii] = joints_sorted[jj]
                        newW[vi, ii] = ww

        write_back(j, binb, ta["JOINTS_0"], newJ.astype(j_dt))
        write_back(j, binb, ta["WEIGHTS_0"], newW.astype(w_dt))

        # report resulting bone distribution
        uj, cnt = np.unique(newJ[newW > 1e-6], return_counts=True)
        # map joint index -> bone name via skin
        sk = j["skins"][0]
        jnames = [nodes[ni].get("name", f"j{ni}") for ni in sk["joints"]]
        top = sorted([(jnames[u], int(c)) for u, c in zip(uj, cnt)],
                     key=lambda x: -x[1])[:6]
        report["transfers"].append({
            "target": tnode.get("name"),
            "sources": [sn.get("name") for sn in snodes],
            "verts": int(len(P_t)),
            "result_top_bones": top,
        })
        print(f"TRANSFER {t['target']}: {len(P_t)} verts <- "
              f"{[sn.get('name') for sn in snodes]}; top bones {top}")

    save(a.out, j, binb)
    json.dump(report, open(a.report, "w"), indent=1)
    print(f"WROTE {a.out}")
    print(f"REPORT {a.report}")


if __name__ == "__main__":
    main()

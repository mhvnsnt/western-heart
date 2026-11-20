#!/usr/bin/env python3
"""Re-weight a garment primitive that was skinned rigidly to the spine, from the SAME model's
correctly skinned body parts (k-nearest-neighbour weight transfer in bind space).

Measured defect (2026-10-20, docs/handoffs/CLAUDE_TO_MUSE_FIXES_2026-10-20.md Fix 4c):
game/assets/models/steve-fox.glb and demonio.glb carry a `ModelShirt` primitive (2,246 verts,
sleeves out to |x| = 0.74 m) weighted 100% to Spine/Spine1, so the sleeves stay in a T-pose under
any animation. 16 roster fighters use this body.

Method (no hand painting, no new bones):
  donors  = the other skinned primitives of the same file chosen by --donors (material-name
            substrings), i.e. the bare arms, torso, neck and hands under the shirt
  target  = the primitive(s) whose material name matches --target
  for each target vertex: k nearest donor vertices (bind-space positions, cKDTree), inverse-
  distance blend of their (joint, weight) pairs, keep the 4 strongest, renormalize.
JOINTS_0/WEIGHTS_0 are rewritten in place (same accessors, same byte size); positions,
normals, UVs, materials, skeleton and animations are untouched. Writes a JSON report.

Usage:
  python3 tools/anim/repair_sleeve_weights.py game/assets/models/steve-fox.glb \
      --target ModelShirt --donors ModelArms,ModelTorso,ModelNeck,ModelHands,ModelGloves_Main
"""
import argparse, hashlib, json, struct, sys
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree

COMP = {5121: np.uint8, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NC = {"SCALAR": 1, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def load(path):
    b = bytearray(Path(path).read_bytes())
    n = struct.unpack("<I", b[12:16])[0]
    j = json.loads(bytes(b[20:20 + n]))
    return b, j, 20 + n + 8


def view(b, j, boff, i):
    a = j["accessors"][i]
    bv = j["bufferViews"][a["bufferView"]]
    dt = np.dtype(COMP[a["componentType"]])
    nc = NC[a["type"]]
    off = boff + bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = bv.get("byteStride", 0) or nc * dt.itemsize
    return a, dt, nc, off, stride


def read(b, j, boff, i):
    a, dt, nc, off, stride = view(b, j, boff, i)
    out = np.empty((a["count"], nc), dt)
    for k in range(a["count"]):
        out[k] = np.frombuffer(b, dt, nc, off + k * stride)
    return out


def write(b, j, boff, i, arr):
    a, dt, nc, off, stride = view(b, j, boff, i)
    arr = np.ascontiguousarray(arr.astype(dt))
    for k in range(a["count"]):
        b[off + k * stride: off + k * stride + nc * dt.itemsize] = arr[k].tobytes()
    if "min" in a or "max" in a:
        a["min"] = arr.min(0).tolist(); a["max"] = arr.max(0).tolist()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("glb")
    ap.add_argument("--target", required=True)
    ap.add_argument("--donors", required=True)
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--out", help="default: rewrite the input in place")
    a = ap.parse_args()
    src = Path(a.glb)
    before = hashlib.sha256(src.read_bytes()).hexdigest()
    b, j, boff = load(src)
    names = [j["nodes"][i]["name"] for i in j["skins"][0]["joints"]]
    mat = lambda pr: j["materials"][pr["material"]].get("name", "") if "material" in pr else ""
    donors_P, donors_J, donors_W, tgt = [], [], [], []
    want = [s for s in a.donors.split(",") if s]
    for mi, m in enumerate(j["meshes"]):
        for pi, pr in enumerate(m["primitives"]):
            at = pr["attributes"]
            if "JOINTS_0" not in at:
                continue
            mn = mat(pr)
            if a.target in mn:
                tgt.append((mi, pi, pr))
            elif any(w in mn for w in want):
                donors_P.append(read(b, j, boff, at["POSITION"]).astype(float))
                donors_J.append(read(b, j, boff, at["JOINTS_0"]).astype(int))
                donors_W.append(read(b, j, boff, at["WEIGHTS_0"]).astype(float))
    if not tgt or not donors_P:
        sys.exit(f"target prims {len(tgt)}, donor prims {len(donors_P)} — nothing to do")
    P = np.concatenate(donors_P); J = np.concatenate(donors_J); Wt = np.concatenate(donors_W)
    tree = cKDTree(P)
    report = {"file": str(src), "sha256_before": before, "target": a.target, "donors": want,
              "k": a.k, "donor_vertices": int(len(P)), "prims": []}
    for mi, pi, pr in tgt:
        at = pr["attributes"]
        pos = read(b, j, boff, at["POSITION"]).astype(float)
        j0 = read(b, j, boff, at["JOINTS_0"]).astype(int)
        w0 = read(b, j, boff, at["WEIGHTS_0"]).astype(float)
        d, idx = tree.query(pos, k=a.k)
        inv = 1.0 / np.maximum(d, 1e-5)
        newJ = np.zeros_like(j0); newW = np.zeros_like(w0)
        for v in range(len(pos)):
            acc = {}
            for c in range(a.k):
                di = idx[v, c]
                for jj, ww in zip(J[di], Wt[di]):
                    if ww > 0:
                        acc[jj] = acc.get(jj, 0.0) + ww * inv[v, c]
            top = sorted(acc.items(), key=lambda t: -t[1])[:4]
            s = sum(w for _, w in top) or 1.0
            for c, (jj, ww) in enumerate(top):
                newJ[v, c] = jj; newW[v, c] = ww / s
        dom_before = {names[x]: int((j0[np.arange(len(j0)), w0.argmax(1)] == x).sum()) for x in set(j0[np.arange(len(j0)), w0.argmax(1)])}
        dom_after = {}
        for x in newJ[np.arange(len(newJ)), newW.argmax(1)]:
            dom_after[names[x]] = dom_after.get(names[x], 0) + 1
        write(b, j, boff, at["JOINTS_0"], newJ)
        write(b, j, boff, at["WEIGHTS_0"], newW.astype(np.float32))
        report["prims"].append({"mesh": mi, "prim": pi, "material": mat(pr), "vertices": int(len(pos)),
                                "max_donor_dist_m": round(float(d[:, 0].max()), 4),
                                "dominant_before": dom_before, "dominant_after": dict(sorted(dom_after.items(), key=lambda t: -t[1]))})
    # JSON chunk may have grown/shrunk only via accessor min/max (WEIGHTS/JOINTS rarely carry them);
    # re-serialize it padded to the original length to keep the binary chunk offset identical.
    n0 = struct.unpack("<I", b[12:16])[0]
    js = json.dumps(j, separators=(",", ":")).encode()
    if len(js) > n0:
        sys.exit("JSON chunk grew; refusing to shift the binary chunk")
    b[20:20 + n0] = js + b" " * (n0 - len(js))
    dst = Path(a.out) if a.out else src
    dst.write_bytes(bytes(b))
    report["sha256_after"] = hashlib.sha256(dst.read_bytes()).hexdigest()
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()

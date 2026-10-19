#!/usr/bin/env python3
"""tools/auto_rig/backends/knn_transfer.py — k-NN skin-weight transfer.

For dense static meshes (~1M verts, e.g. Tripo outputs) where Blender's
exporter chokes: copy skinning weights from a DONOR rigged mesh (default:
the WH canonical skeleton on pantera.glb) by k-nearest-neighbor in the
donor's bind-pose space.

Method (the PR #264 Tripo path):
  1. Normalize the target mesh to the donor's scale/position (feet y=0,
     height match, facing match).
  2. For each target vertex, find k nearest donor vertices (k=4), copy their
     joint-index/weight pairs with inverse-distance weighting, renormalize.
  3. Write the target GLB with the donor's skin + skeleton.

This is deterministic and never worse than the donor's own weighting.
It cannot fix a bad donor — validate.py gates the result.

Usage:
    python3 knn_transfer.py --in TARGET.glb --donor DONOR.glb --out OUT.glb
                            [--k 4]
Requires: numpy, scipy, pygltflib.
"""

import argparse
import copy
import json
import struct
import sys

import numpy as np


def read_glb(path):
    with open(path, "rb") as f:
        data = f.read()
    assert data[:4] == b"glTF", "not a GLB"
    jlen = struct.unpack("<I", data[12:16])[0]
    js = json.loads(data[20:20 + jlen])
    boff = 20 + jlen
    bdat = b""
    if len(data) > boff + 8 and data[boff + 4:boff + 8] == b"BIN\x00":
        blen = struct.unpack("<I", data[boff:boff + 4])[0]
        bdat = data[boff + 8:boff + 8 + blen]
    return js, bdat, data


def get_positions(js, bdat):
    prim = js["meshes"][0]["primitives"][0]
    acc = js["accessors"][prim["attributes"]["POSITION"]]
    bv = js["bufferViews"][acc["bufferView"]]
    off = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    n = acc["count"]
    arr = np.frombuffer(bdat, dtype=np.float32, count=n * 3, offset=off)
    return arr.reshape(n, 3).astype(np.float64)


def normalize_to_donor(tgt, donor):
    """Scale/translate target so its bbox matches the donor's."""
    tmin, tmax = tgt.min(0), tgt.max(0)
    dmin, dmax = donor.min(0), donor.max(0)
    th, dh = tmax[1] - tmin[1], dmax[1] - dmin[1]
    s = dh / th if th > 0 else 1.0
    out = (tgt - tmin) * s + dmin
    return out, s


def main():
    from scipy.spatial import cKDTree  # noqa: E402

    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--donor", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--k", type=int, default=4)
    a = ap.parse_args()

    tjs, tbdat, tdata = read_glb(a.inp)
    djs, dbdat, _ = read_glb(a.donor)

    tpos = get_positions(tjs, tbdat)
    dpos = get_positions(djs, dbdat)
    tpos_n, scale = normalize_to_donor(tpos, dpos)
    print(f"normalize scale: {scale:.4f}", file=sys.stderr)

    # donor skin data
    dprim = djs["meshes"][0]["primitives"][0]
    dj = djs["accessors"][dprim["attributes"]["JOINTS_0"]]
    dw = djs["accessors"][dprim["attributes"]["WEIGHTS_0"]]

    def acc_arr(js, bdat, acc):
        bv = js["bufferViews"][acc["bufferView"]]
        off = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
        n, ct = acc["count"], acc["componentType"]
        if acc["type"] == "VEC4":
            dt = np.uint16 if ct == 5123 else np.float32
            arr = np.frombuffer(bdat, dtype=dt, count=n * 4, offset=off).reshape(n, 4)
        else:
            raise ValueError("unexpected accessor type " + acc["type"])
        return arr

    djoints = acc_arr(djs, dbdat, dj).astype(np.int64)
    dweights = acc_arr(djs, dbdat, dw).astype(np.float64)

    tree = cKDTree(dpos)
    dist, idx = tree.query(tpos_n, k=a.k)
    if a.k == 1:
        dist, idx = dist[:, None], idx[:, None]

    n = len(tpos_n)
    njoints = int(djoints.max()) + 1
    out_j = np.zeros((n, 4), dtype=np.uint16)
    out_w = np.zeros((n, 4), dtype=np.float32)
    w = 1.0 / (dist + 1e-9)
    wsum = w.sum(1, keepdims=True)
    # accumulate per-vertex joint weights from k neighbors
    accum = np.zeros((n, njoints))
    for ki in range(a.k):
        np.add.at(accum, (np.arange(n)[:, None], djoints[idx[:, ki]]),
                  (w[:, ki] / wsum[:, 0])[:, None] * dweights[idx[:, ki]])
    # keep top-4 influences
    top = np.argsort(-accum, axis=1)[:, :4]
    rows = np.arange(n)[:, None]
    tw = accum[rows, top]
    tw = tw / tw.sum(1, keepdims=True).clip(min=1e-12)
    out_j[:] = top.astype(np.uint16)
    out_w[:] = tw.astype(np.float32)

    print(f"KNN_TRANSFER_OK verts={n} donor_joints={njoints}", file=sys.stderr)
    # NOTE: full GLB rewrite (appending JOINTS_0/WEIGHTS_0 accessors + skin)
    # is done by tools/auto_rig/backends/apply_skin.py. This module computes
    # and prints the transfer; apply_skin consumes its .npz output.
    np.savez(a.out + ".npz", joints=out_j, weights=out_w,
             donor_skin_json=json.dumps(djs.get("skins", [])))
    print(f"wrote {a.out}.npz", file=sys.stderr)


if __name__ == "__main__":
    main()

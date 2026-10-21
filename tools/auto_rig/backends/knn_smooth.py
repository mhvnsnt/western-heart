#!/usr/bin/env python3
"""tools/auto_rig/backends/knn_smooth.py — smooth-kernel k-NN skin-weight
transfer. Same .npz contract as knn_transfer.py (joints/weights/
donor_skin_json, consumed by backends/apply_skin.py), but the transfer
kernel is a wide gaussian (k=64, sigma = donor vertex-spacing scale,
default 0.03 in donor units) aggregating the neighbours' FULL weight
vectors, instead of k=4 inverse-distance pair copying.

Why: knn_transfer's k=4 field aliases the donor's near-binary per-vertex
weights onto a ~100x denser target mesh. Adjacent target verts land on
opposite sides of donor weight creases, so posed micro-edges tear (on the
964,668-vert Leopard King: neighbour weight-L1 p99.9 = 2.000, the maximum
— completely disjoint weight sets on adjacent verts). The wide smooth
kernel makes the field smooth at the donor's own sampling wavelength
(same mesh: raw p99 0.498 -> 0.121 before any polish). Follow with
backends/diffuse_weights.py for a light polish pass.

Chunked over target verts; peak RAM ~500MB at 1M verts.

Usage:
    python3 knn_smooth.py --in TARGET_ROTATED.glb --donor DONOR_MERGED.glb \
                          --out TARGET_knn_smooth [--k 64] [--sigma 0.03]
The target must already be rotated into the donor's facing (this tool,
like knn_transfer.py, does no rotation); the donor file must expose its
full skin cloud as meshes[0].primitives[0] (merge prims first if the
donor is multi-mesh). Requires numpy + scipy.
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from knn_transfer import read_glb, get_positions, normalize_to_donor  # noqa: E402


def acc_arr(js, bdat, acc):
    bv = js['bufferViews'][acc['bufferView']]
    off = bv.get('byteOffset', 0) + acc.get('byteOffset', 0)
    n, ct = acc['count'], acc['componentType']
    dt = np.uint16 if ct == 5123 else np.float32
    return np.frombuffer(bdat, dtype=dt, count=n * 4, offset=off).reshape(n, 4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--donor', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--k', type=int, default=64)
    ap.add_argument('--sigma', type=float, default=0.03)
    a = ap.parse_args()

    from scipy.spatial import cKDTree

    tjs, tbdat, _ = read_glb(a.inp)
    djs, dbdat, _ = read_glb(a.donor)
    tpos = get_positions(tjs, tbdat)
    dpos = get_positions(djs, dbdat)
    tpos_n, scale = normalize_to_donor(tpos, dpos)
    print(f'normalize scale: {scale:.4f}', file=sys.stderr, flush=True)
    dprim = djs['meshes'][0]['primitives'][0]
    djoints = acc_arr(djs, dbdat, djs['accessors'][dprim['attributes']['JOINTS_0']]).astype(np.int64)
    dweights = acc_arr(djs, dbdat, djs['accessors'][dprim['attributes']['WEIGHTS_0']]).astype(np.float64)
    tree = cKDTree(dpos)
    n = len(tpos_n)
    njoints = int(djoints.max()) + 1
    out_j = np.zeros((n, 4), dtype=np.uint16)
    out_w = np.zeros((n, 4), dtype=np.float32)
    CH = 60000
    for s in range(0, n, CH):
        e = min(s + CH, n)
        dist, idx = tree.query(tpos_n[s:e], k=a.k)
        w = np.exp(-(dist ** 2) / (2 * a.sigma ** 2))
        wsum = w.sum(1, keepdims=True)
        wsum[wsum == 0] = 1
        wn = w / wsum
        m = e - s
        accum = np.zeros((m, njoints))
        rows = np.arange(m)[:, None]
        for ki in range(a.k):
            np.add.at(accum, (rows, djoints[idx[:, ki]]),
                      wn[:, ki][:, None] * dweights[idx[:, ki]])
        top = np.argsort(-accum, axis=1)[:, :4]
        tw = accum[rows, top]
        tw = tw / tw.sum(1, keepdims=True).clip(min=1e-12)
        out_j[s:e] = top.astype(np.uint16)
        out_w[s:e] = tw.astype(np.float32)
        print(f'  chunk {e}/{n}', file=sys.stderr, flush=True)
    np.savez(a.out + '.npz', joints=out_j, weights=out_w,
             donor_skin_json=json.dumps(djs.get('skins', [])))
    print(f'KNN_SMOOTH_OK verts={n} k={a.k} sigma={a.sigma} -> {a.out}.npz',
          file=sys.stderr, flush=True)


if __name__ == '__main__':
    main()

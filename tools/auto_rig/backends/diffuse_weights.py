#!/usr/bin/env python3
"""tools/auto_rig/backends/diffuse_weights.py — global Jacobi diffusion of
a skinned GLB's weight field over its full triangle-edge graph.

Skinning quality on dense meshes is governed by how continuous the weight
field is between NEIGHBOURING vertices: the per-edge weight L1 distance
(|w(u) - w(v)| summed over joints) is what stretches an edge when its two
endpoint bones separate. Transfer seams, hard donor part boundaries and
fitted accessory chains (e.g. apply_skin.py's tail override) all leave
L1 spikes — up to 2.000 (disjoint weight sets) — that read as tears in
poses even when every per-clip stretch gate passes (anim_check.py's
stretch check skips edges shorter than 0.5% of model height, which on a
~1M-vert mesh is ~99% of all edges). Diffusion is the principled polish:
repeated neighbour averaging (alpha=0.5) with NO intermediate top-4
truncation, so gradients widen instead of re-creasing.

Workflow (used for Pantera Leopard King, 2026-10-20/21):
    diffuse_weights.py --in model.glb --out work --passes 10
    diffuse_weights.py --in model.glb --out work --dense-in work.dense.npy \
                       --passes 10          # resume, banks every run
    (then bake work.joints.npy/work.weights.npy back into the GLB)

Prints the edge weight-L1 distribution before/after (median/p99/p99.9/
max). float32 with per-joint bincount segment sums; peak RAM < 700MB at
1M verts / 53 joints. Requires numpy.
"""
import argparse
import importlib.util
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_AUTO_RIG = os.path.dirname(_HERE)
sys.path.insert(0, _AUTO_RIG)
from validate import read_glb  # noqa: E402

_sp = importlib.util.spec_from_file_location('apply_skin', os.path.join(_HERE, 'apply_skin.py'))
_aps = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(_aps)

CH = 250_000


def unique_edges(idx):
    tris = idx.reshape(-1, 3)
    e = np.concatenate([tris[:, [0, 1]], tris[:, [1, 2]], tris[:, [2, 0]]])
    e = np.sort(e, axis=1)
    return np.unique(e, axis=0)


def edge_l1(D, edges):
    out = np.empty(len(edges), dtype=np.float64)
    for s in range(0, len(edges), CH):
        e = edges[s:s + CH]
        out[s:s + len(e)] = np.abs(D[e[:, 0]].astype(np.float64) - D[e[:, 1]]).sum(1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--passes', type=int, default=20)
    ap.add_argument('--alpha', type=float, default=0.5)
    ap.add_argument('--dense-in')
    a = ap.parse_args()

    js, bd = read_glb(a.inp)
    prim = js['meshes'][0]['primitives'][0]
    idx = _aps.acc_array(js, bd, prim['indices']).astype(np.int64)
    J = _aps.acc_array(js, bd, prim['attributes']['JOINTS_0']).astype(np.int64)
    W = _aps.acc_array(js, bd, prim['attributes']['WEIGHTS_0']).astype(np.float32)
    Jmax = int(J.max()) + 1
    n = len(W)
    if a.dense_in:
        D = np.load(a.dense_in).astype(np.float32)
        print('resumed from dense', a.dense_in, D.shape, flush=True)
    else:
        D = np.zeros((n, Jmax), dtype=np.float32)
        np.put_along_axis(D, J, W, axis=1)
    edges = unique_edges(idx)
    src = np.concatenate([edges[:, 0], edges[:, 1]])
    dst = np.concatenate([edges[:, 1], edges[:, 0]])
    deg = np.bincount(src, minlength=n).astype(np.float32)
    deg[deg == 0] = 1
    print('verts', n, 'joints', Jmax, 'directed edges', len(src), flush=True)
    d0 = edge_l1(D, edges)
    print('L1 BEFORE: median %.4f p99 %.4f p999 %.4f max %.3f' % (
        np.median(d0), np.percentile(d0, 99), np.percentile(d0, 99.9), d0.max()), flush=True)
    for p in range(a.passes):
        acc = np.empty((n, Jmax), dtype=np.float32)
        for k in range(Jmax):
            acc[:, k] = np.bincount(src, weights=D[dst, k].astype(np.float64),
                                    minlength=n).astype(np.float32)
        D = ((1 - a.alpha) * D + a.alpha * (acc / deg[:, None])).astype(np.float32)
        print('  pass', p + 1, 'done', flush=True)
    d1 = edge_l1(D, edges)
    print('L1 AFTER: median %.4f p99 %.4f p999 %.4f max %.3f' % (
        np.median(d1), np.percentile(d1, 99), np.percentile(d1, 99.9), d1.max()), flush=True)
    np.save(a.out + '.dense.npy', D)
    idx4 = np.argpartition(-D, 4, axis=1)[:, :4]
    w4 = np.take_along_axis(D, idx4, axis=1)
    order = np.argsort(-w4, axis=1)
    idx4 = np.take_along_axis(idx4, order, axis=1)
    w4 = np.take_along_axis(w4, order, axis=1)
    s = w4.sum(1, keepdims=True)
    s[s == 0] = 1
    w4 = w4 / s
    np.save(a.out + '.joints.npy', idx4.astype(np.uint16))
    np.save(a.out + '.weights.npy', w4.astype(np.float32))
    print('dumped', a.out, flush=True)


if __name__ == '__main__':
    main()

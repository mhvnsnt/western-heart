#!/usr/bin/env python3
"""tools/auto_rig/head_territory_clean.py — take a Head bone's weight off everything that is not head, and inpaint it.

Why (2026-11-10, Thor): the refit's head-territory step gave the Head bone everything above a horizontal cut at the
shoulder line. Between 1.32 m and 1.48 m every vertex out to the T-posed arms (|x| <= 0.70 m) was Head-dominant: his
traps, deltoids, upper arms and forearm bracers rode his head. When his hands went forward (his own Ganryu sumo
stance), the Head-weighted part of each bracer stayed behind and stretched into a fin; every head turn dragged his
shoulders. The same cut-by-height bug as the roster lane's Sha rebind (territory_weight_merge.py).

The head's real territory is measured, not cut: the head and helmet above --top-y within --r-top of the head's
vertical axis, and below it only the neck / jaw column (|x| <= --x-neck, --z-back <= z - head_z <= --z-front, above
--floor-y). Outside it the --joint weight is removed. A vertex that keeps most of its weight on other bones is
renormalized; one that was mostly Head is INPAINTED: harmonic interpolation of its neighbours' weights over the mesh
(triangle edges + UV-seam copies), the valid vertices held fixed and the Head channel held at zero, so the hole is
filled from the shoulder / arm / spine weights around it (the inpainting step of Robust Skin Weights Transfer,
Abdrashitov et al. 2023, on a plain neighbour Laplacian). Top-4 influences, continuous cut, renormalized.

Plain (decoded) GLB in and out (tools/anim/gltf_codec.mjs decode / encode). Measure with --profile first.

    python3 tools/auto_rig/head_territory_clean.py --in plain.glb --profile
    python3 tools/auto_rig/head_territory_clean.py --in plain.glb --out clean.glb --top-y 1.50 --r-top 0.28 \\
        --x-neck 0.16 --z-back -0.20 --z-front 0.25 --floor-y 1.30 [--report r.json]
"""
import argparse
import json
import os
import shutil
import struct
import sys

import numpy as np
import scipy.sparse as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import anim_check as ac  # noqa: E402

_NP = {5121: np.uint8, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}


def bind_positions(model, prim):
    bind = model.bind_world()
    B = bind[int(model.joint_nodes[0])] @ model.ibm[0]
    return (np.c_[prim['pos'], np.ones(len(prim['pos']))] @ B.T)[:, :3], bind


def adjacency(prim):
    n = len(prim['pos'])
    rows, cols = [], []
    if prim['idx'] is not None:
        t = prim['idx'].reshape(-1, 3)
        for a, b in ((0, 1), (1, 2), (2, 0)):
            rows += [t[:, a], t[:, b]]
            cols += [t[:, b], t[:, a]]
    key = np.round(prim['pos'] * 1e5).astype(np.int64)
    _, inv = np.unique(key, axis=0, return_inverse=True)
    order = np.argsort(inv, kind='stable')
    same = inv[order][1:] == inv[order][:-1]
    a, b = order[:-1][same], order[1:][same]
    rows += [a, b]
    cols += [b, a]
    r, c = np.concatenate(rows), np.concatenate(cols)
    A = sp.coo_matrix((np.ones(len(r)), (r, c)), shape=(n, n)).tocsr()
    A.data[:] = 1.0
    return A


def dense(prim, nj):
    W = np.zeros((len(prim['joints']), nj))
    for k in range(4):
        np.add.at(W, (np.arange(len(W)), prim['joints'][:, k]), prim['weights'][:, k])
    return W


def view(js, raw, boff, acc_i):
    acc = js['accessors'][acc_i]
    bv = js['bufferViews'][acc['bufferView']]
    dt = np.dtype(_NP[acc['componentType']]).newbyteorder('<')
    stride = bv.get('byteStride', 0) or 4 * dt.itemsize
    base = boff + bv.get('byteOffset', 0) + acc.get('byteOffset', 0)
    return np.ndarray(shape=(acc['count'], 4), dtype=dt, buffer=raw, offset=base, strides=(stride, dt.itemsize))


def territory(P, head, a):
    dz = P[:, 2] - head[2]
    rxz = np.hypot(P[:, 0] - head[0], dz)
    top = (P[:, 1] >= a.top_y) & (rxz <= a.r_top)
    neck = (P[:, 1] >= a.floor_y) & (P[:, 1] < a.top_y) & (np.abs(P[:, 0] - head[0]) <= a.x_neck) & \
        (dz >= a.z_back) & (dz <= a.z_front)
    return top | neck


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out')
    ap.add_argument('--joint', default='Head')
    ap.add_argument('--profile', action='store_true')
    ap.add_argument('--top-y', type=float, default=1.50)
    ap.add_argument('--r-top', type=float, default=0.28)
    ap.add_argument('--x-neck', type=float, default=0.16)
    ap.add_argument('--z-back', type=float, default=-0.20)
    ap.add_argument('--z-front', type=float, default=0.25)
    ap.add_argument('--floor-y', type=float, default=1.30)
    ap.add_argument('--inpaint-below', type=float, default=0.5,
                    help='inpaint a vertex whose non-Head weight is below this; renormalize the rest')
    ap.add_argument('--iters', type=int, default=200)
    ap.add_argument('--report')
    a = ap.parse_args()
    if not a.profile and not a.out:
        sys.exit('--out is required (or --profile)')
    if a.out and a.out != a.inp:
        shutil.copy(a.inp, a.out)
    model = ac.AnimModel(a.out or a.inp)
    names = [model.nodes[int(j)].get('name') for j in model.joint_nodes]
    hi = names.index(a.joint)
    rep = {'tool': 'tools/auto_rig/head_territory_clean.py', 'params': {k: v for k, v in vars(a).items()
                                                                     if k not in ('inp', 'out', 'report')}, 'prims': []}
    raw = bytearray(open(a.out or a.inp, 'rb').read())
    boff = 20 + struct.unpack_from('<I', raw, 12)[0] + 8
    js = model.js
    metas = [p['attributes'] for m in js['meshes'] for p in m['primitives']
             if 'JOINTS_0' in p.get('attributes', {}) and 'POSITION' in p.get('attributes', {})]
    for at, prim in zip(metas, model.prims):
        P, bind = bind_positions(model, prim)
        head = bind[int(model.joint_nodes[hi])][:3, 3]
        W = dense(prim, len(names))
        inside = territory(P, head, a)
        bad = (W[:, hi] > 1e-4) & ~inside
        if a.profile:
            for y0 in np.arange(round(P[:, 1].max(), 2), a.floor_y - 0.12, -0.04):
                b = (P[:, 1] >= y0 - 0.04) & (P[:, 1] < y0)
                if b.any():
                    print('y %.2f-%.2f verts %6d  Head-weighted %6d  outside territory %6d  max |x| of Head-dominant %.3f'
                          % (y0 - 0.04, y0, b.sum(), (b & (W[:, hi] > 0.02)).sum(), (b & bad).sum(),
                             np.abs(P[b & (W.argmax(1) == hi), 0] - head[0]).max() if (b & (W.argmax(1) == hi)).any() else 0))
            continue
        rest = W.copy()
        rest[:, hi] = 0.0
        mass = rest.sum(1)
        hole = bad & (mass < a.inpaint_below)
        renorm = bad & ~hole
        rest[renorm] /= mass[renorm, None]
        # harmonic inpainting of the holes from their neighbours (valid vertices fixed, Head channel zero)
        A = adjacency(prim)
        deg = np.asarray(A.sum(1)).ravel()
        deg[deg == 0] = 1
        Dinv = sp.diags(1.0 / deg)
        M = (Dinv @ A).tocsr()
        Wn = rest.copy()
        Wn[hole] = 0.0
        h_idx = np.nonzero(hole)[0]
        Mh = M[h_idx]
        for _ in range(a.iters):
            upd = Mh @ Wn
            s = upd.sum(1, keepdims=True)
            ok = s[:, 0] > 1e-9
            upd[ok] /= s[ok]
            upd[:, hi] = 0.0
            Wn[h_idx[ok]] = upd[ok]
        unfilled = hole & (Wn.sum(1) < 1e-6)
        Wn[unfilled] = rest[unfilled] / np.maximum(rest[unfilled].sum(1, keepdims=True), 1e-9)
        changed = np.nonzero(bad)[0]
        sub = Wn[changed]
        order = np.argsort(-sub, axis=1)[:, :5]
        top5 = np.take_along_axis(sub, order, 1)
        w4 = np.maximum(top5[:, :4] - top5[:, 4:5], 0.0)
        s = w4.sum(1, keepdims=True)
        zero = s[:, 0] <= 1e-9
        w4[zero] = top5[zero, :4]
        s = w4.sum(1, keepdims=True)
        w4 /= np.maximum(s, 1e-12)
        j4 = np.where(w4 > 0, order[:, :4], 0)
        jv = view(js, raw, boff, at['JOINTS_0'])
        wv = view(js, raw, boff, at['WEIGHTS_0'])
        if wv.dtype != np.float32:
            sys.exit('WEIGHTS_0 must be float (decode the GLB first)')
        jv[changed] = j4.astype(jv.dtype)
        wv[changed] = w4.astype(np.float32)
        newdom = np.array(names)[j4[np.arange(len(j4)), w4.argmax(1)]] if len(j4) else []
        u, c = np.unique(newdom, return_counts=True)
        rep['prims'].append({'verts': int(len(W)), 'head_weighted': int((W[:, hi] > 1e-4).sum()),
                             'outside_territory': int(bad.sum()), 'renormalized': int(renorm.sum()),
                             'inpainted': int(hole.sum()), 'unfilled_fallback': int(unfilled.sum()),
                             'new_dominant': dict(sorted(zip(u.tolist(), c.tolist()), key=lambda x: -x[1])[:8])})
    if a.profile:
        return
    open(a.out, 'wb').write(raw)
    txt = json.dumps(rep, indent=1)
    if a.report:
        open(a.report, 'w').write(txt + '\n')
    print(txt)


if __name__ == '__main__':
    main()

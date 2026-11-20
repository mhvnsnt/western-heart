#!/usr/bin/env python3
"""tools/auto_rig/territory_weight_merge.py — keep only the part of a weight repair that lies inside a bone's territory.

Why (2026-11-10, Sha): the roster wire-up lane's Sha repair (PR #1600 -> #1710, "head-territory rebind: dominant
shoulder/arm verts in head zone 926 -> 46") rebound 7,840 vertices. Judged by eye in the fight path, it did three
things at once:
  * hair 9-22 cm from the Head joint moved off the shoulder / arm bones onto Head / Spine2: her hair stays on her
    head instead of shattering into shards around a bare scalp (the fix);
  * 1,085 right-arm vertices 35-49 cm from the Head (the T-posed arm sits at head height) rebound to Head: in every
    pose the forearm stretched out to a hand left hanging where the T-pose had it (a regression);
  * neck pieces 2-8 cm from the Head moved from Head / Neck onto LeftShoulder (a regression).
This tool takes the BASE file's weights and accepts the repair's weights only inside the territory: within --radius of
the --joint at bind AND onto a dominant bone in --allow (the head / neck / upper-spine chain): the repair's intent,
without its spill. The decision is made per connected mesh island (a hair card, a bracelet; UV-seam copies joined),
on the island's changed vertices (median distance, majority dominant bone), so no island is cut in two: a per-vertex cut
left hair cards half on the head and half on an arm, stretched into lines. Same vertex order is required (a
weights-only repair; positions are checked).

Both inputs are PLAIN (decoded) GLBs (tools/anim/gltf_codec.mjs decode); the output is the base file with the accepted
JOINTS_0 / WEIGHTS_0 written in place.

    python3 tools/auto_rig/territory_weight_merge.py --base main-plain.glb --repair repaired-plain.glb --out merged.glb \\
        --joint Head --radius 0.30 --allow Head,Neck,Spine2,Spine1 [--report r.json]
"""
import argparse
import collections
import json
import os
import shutil
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import anim_check as ac  # noqa: E402

_NP = {5121: np.uint8, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
_NORM = {5121: 255.0, 5123: 65535.0}


def view(js, raw, boff, acc_i):
    acc = js['accessors'][acc_i]
    bv = js['bufferViews'][acc['bufferView']]
    dt = np.dtype(_NP[acc['componentType']]).newbyteorder('<')
    stride = bv.get('byteStride', 0) or 4 * dt.itemsize
    base = boff + bv.get('byteOffset', 0) + acc.get('byteOffset', 0)
    return np.ndarray(shape=(acc['count'], 4), dtype=dt, buffer=raw, offset=base, strides=(stride, dt.itemsize)), acc


def islands(prim):
    """Connected-component id per vertex (shared triangle edges + identical positions, i.e. UV-seam copies)."""
    n = len(prim['pos'])
    par = np.arange(n)

    def find(x):
        r = x
        while par[r] != r:
            r = par[r]
        while par[x] != r:
            par[x], x = r, par[x]
        return r

    pairs = []
    if prim['idx'] is not None:
        t = prim['idx'].reshape(-1, 3)
        pairs += [t[:, [0, 1]], t[:, [1, 2]]]
    key = np.round(prim['pos'] * 1e5).astype(np.int64)
    _, inv = np.unique(key, axis=0, return_inverse=True)
    order = np.argsort(inv, kind='stable')
    same = inv[order][1:] == inv[order][:-1]
    pairs.append(np.stack([order[:-1][same], order[1:][same]], 1))
    for a_, b_ in np.concatenate(pairs):
        ra, rb = find(int(a_)), find(int(b_))
        if ra != rb:
            par[ra] = rb
    return np.array([find(i) for i in range(n)])


def dense(prim, n):
    W = np.zeros((len(prim['joints']), n))
    for k in range(4):
        np.add.at(W, (np.arange(len(W)), prim['joints'][:, k]), prim['weights'][:, k])
    return W


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--base', required=True)
    ap.add_argument('--repair', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--joint', default='Head')
    ap.add_argument('--radius', type=float, default=0.30)
    ap.add_argument('--allow', default='Head,Neck,Spine2,Spine1')
    ap.add_argument('--report')
    a = ap.parse_args()
    allow = set(a.allow.split(','))
    shutil.copy(a.base, a.out)
    base, rep = ac.AnimModel(a.out), ac.AnimModel(a.repair)
    names = [base.nodes[int(j)].get('name') for j in base.joint_nodes]
    if names != [rep.nodes[int(j)].get('name') for j in rep.joint_nodes]:
        sys.exit('the two files have different skins')
    bind = base.bind_world()
    jpos = bind[int(base.joint_nodes[names.index(a.joint)])][:3, 3]
    B = bind[int(base.joint_nodes[0])] @ base.ibm[0]
    allow_i = np.array([names.index(n) for n in allow if n in names])
    raw = bytearray(open(a.out, 'rb').read())
    boff = 20 + struct.unpack_from('<I', raw, 12)[0] + 8
    js = base.js
    rjs = rep.js
    metas = [p['attributes'] for m in js['meshes'] for p in m['primitives']
             if 'JOINTS_0' in p.get('attributes', {}) and 'POSITION' in p.get('attributes', {})]
    out = {'tool': 'tools/auto_rig/territory_weight_merge.py', 'base': a.base, 'repair': a.repair, 'output': a.out,
           'joint': a.joint, 'radius': a.radius, 'allow': sorted(allow), 'prims': []}
    for at, pa, pb in zip(metas, base.prims, rep.prims):
        if len(pa['pos']) != len(pb['pos']) or np.abs(pa['pos'] - pb['pos']).max() > 1e-6:
            sys.exit('vertex positions differ: not a weights-only repair')
        Wa, Wb = dense(pa, len(names)), dense(pb, len(names))
        changed = np.abs(Wa - Wb).sum(1) > 1e-4
        P = (np.c_[pa['pos'], np.ones(len(pa['pos']))] @ B.T)[:, :3]
        dist = np.linalg.norm(P - jpos, axis=1)
        onto_v = np.isin(Wb.argmax(1), allow_i)
        comp = islands(pa)
        near = np.zeros(len(Wa), bool)
        onto = np.zeros(len(Wa), bool)
        for c in np.unique(comp[changed]):
            m = comp == c
            mc = m & changed
            near[m] = np.median(dist[mc]) <= a.radius
            onto[m] = onto_v[mc].mean() > 0.5
        accept = changed & near & onto
        jv, jacc = view(js, raw, boff, at['JOINTS_0'])
        wv, wacc = view(js, raw, boff, at['WEIGHTS_0'])
        idx = np.nonzero(accept)[0]
        if len(idx):
            jv[idx] = pb['joints'][idx].astype(jv.dtype)
            w = pb['weights'][idx]
            if wv.dtype == np.float32:
                wv[idx] = w.astype(np.float32)
            else:
                s = _NORM[wacc['componentType']]
                q = np.round(w * s)
                q[:, 0] += s - q.sum(1)  # keep the quantized sum exact
                wv[idx] = q.astype(wv.dtype)
        dom_a = collections.Counter(np.array(names)[Wa[idx].argmax(1)].tolist() if len(idx) else [])
        out['prims'].append({'verts': int(len(Wa)), 'changed_by_repair': int(changed.sum()), 'accepted': int(len(idx)),
                             'rejected_far': int((changed & ~near).sum()),
                             'rejected_not_onto_allowed': int((changed & near & ~onto).sum()),
                             'accepted_from': dict(dom_a.most_common(6))})
    open(a.out, 'wb').write(raw)
    t = {k: sum(p[k] for p in out['prims']) for k in ('changed_by_repair', 'accepted', 'rejected_far',
                                                       'rejected_not_onto_allowed')}
    out['totals'] = t
    txt = json.dumps(out, indent=1)
    if a.report:
        open(a.report, 'w').write(txt + '\n')
    print(json.dumps(t))


if __name__ == '__main__':
    main()

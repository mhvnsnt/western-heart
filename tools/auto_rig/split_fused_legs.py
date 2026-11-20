#!/usr/bin/env python3
"""tools/auto_rig/split_fused_legs.py — separate the legs of a mesh that was generated with them fused together.

Why (2026-11-10, Gyou): image-to-3D statics often come out with the legs touching or joined by a sheet (Gyou's flame
body: the legs touch from the feet to the crotch and flame sheets bridge them). Once rigged, every triangle that has a
vertex on the left leg and another on the right leg is stretched between the two legs by any stance wider than the
rest pose; on a high kick it becomes a fan of long triangles from the kicking foot to the standing foot. No weighting
fixes that: the triangle belongs to both legs. A modeller cuts the legs apart; this does the same cut on the rigged
mesh, deterministically: it removes exactly the triangles whose vertices are dominated (> --dominance of their weight)
by bones of OPPOSITE legs. Nothing else changes (vertices, weights, skeleton, materials, clips); the open seam sits on
the inner legs where they touched.

Input and output are PLAIN (decoded) GLBs (tools/anim/gltf_codec.mjs decode / encode), like the other auto_rig steps.

    python3 tools/auto_rig/split_fused_legs.py --in rigged.glb --out split.glb [--dominance 0.5] [--report r.json]
"""
import argparse
import json
import os
import shutil
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import anim_check as ac  # noqa: E402

_NP = {5121: np.uint8, 5123: np.uint16, 5125: np.uint32}
LEG_PARTS = ('UpLeg', 'Leg', 'Foot', 'Toe', 'thigh', 'shin', 'foot', 'toe')


def leg_side(name):
    n = name or ''
    if not any(k in n for k in LEG_PARTS):
        return 0
    if n.startswith('Left') or n.endswith('.L') or n.endswith('_L') or n.startswith('L_'):
        return 1
    if n.startswith('Right') or n.endswith('.R') or n.endswith('_R') or n.startswith('R_'):
        return 2
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--dominance', type=float, default=0.5)
    ap.add_argument('--report')
    a = ap.parse_args()
    if a.out != a.inp:
        shutil.copy(a.inp, a.out)
    model = ac.AnimModel(a.out)
    names = [model.nodes[int(j)].get('name') for j in model.joint_nodes]
    side = np.array([leg_side(n) for n in names])
    raw = bytearray(open(a.out, 'rb').read())
    boff = 20 + struct.unpack_from('<I', raw, 12)[0] + 8
    js = model.js
    prims = [p for m in js['meshes'] for p in m['primitives']
             if 'JOINTS_0' in p.get('attributes', {}) and 'POSITION' in p.get('attributes', {})]
    rep = {'tool': 'tools/auto_rig/split_fused_legs.py', 'input': a.inp, 'output': a.out, 'dominance': a.dominance,
           'prims': []}
    for p, pr in zip(prims, model.prims):
        if pr['idx'] is None or p.get('mode', 4) != 4:
            rep['prims'].append({'skipped': 'not an indexed triangle list'})
            continue
        J, W = pr['joints'], pr['weights']
        mL = (W * (side[J] == 1)).sum(1)
        mR = (W * (side[J] == 2)).sum(1)
        dom = np.where(mL > a.dominance, 1, np.where(mR > a.dominance, 2, 0))
        tri = pr['idx'].reshape(-1, 3)
        d = dom[tri]
        cross = (d == 1).any(1) & (d == 2).any(1)
        keep = tri[~cross].reshape(-1)
        acc = js['accessors'][p['indices']]
        bv = js['bufferViews'][acc['bufferView']]
        dt = np.dtype(_NP[acc['componentType']]).newbyteorder('<')
        base = boff + bv.get('byteOffset', 0) + acc.get('byteOffset', 0)
        view = np.ndarray(shape=(acc['count'],), dtype=dt, buffer=raw, offset=base)
        view[:len(keep)] = keep.astype(dt)
        acc['count'] = int(len(keep))
        rep['prims'].append({'triangles': int(len(tri)), 'removed_cross_leg': int(cross.sum())})
    # rewrite the JSON chunk with the new accessor counts (same BIN chunk)
    jtxt = json.dumps(js, separators=(',', ':')).encode()
    jtxt += b' ' * ((4 - len(jtxt) % 4) % 4)
    n_old = struct.unpack_from('<I', raw, 12)[0]
    bin_chunk = bytes(raw[20 + n_old:])
    out = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(jtxt) + len(bin_chunk)) + \
        struct.pack('<II', len(jtxt), 0x4E4F534A) + jtxt + bin_chunk
    open(a.out, 'wb').write(out)
    txt = json.dumps(rep, indent=1)
    if a.report:
        open(a.report, 'w').write(txt + '\n')
    print(txt)


if __name__ == '__main__':
    main()

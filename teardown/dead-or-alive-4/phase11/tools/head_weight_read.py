#!/usr/bin/env python3
"""Phase 11 Job 2: per-head skin-weight + joint-palette read.
For each chrtwo head package GLB: nodes (index, name, translation),
skin joint list (node indices in palette order), total skin weight mass
per palette entry (summed over all primitives/vertices), and raw
POSITION bounds. Decides origin convention: geometry weighted to the
head's local nodes vs the anchor-copy root nodes, and whether raw
geometry sits at local (~0) or body-world (~0.4-0.6) height."""
import json, struct, sys, os
import numpy as np

def load_glb(path):
    d = open(path, 'rb').read()
    jlen = struct.unpack_from('<I', d, 12)[0]
    g = json.loads(d[20:20 + jlen])
    off = 20 + jlen
    blen = struct.unpack_from('<I', d, off)[0]
    return g, d[off + 8: off + 8 + blen]

def acc(g, bin_, idx):
    a = g['accessors'][idx]
    bv = g['bufferViews'][a['bufferView']]
    start = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    ncomp = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]
    dt = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8}[a['componentType']]
    stride = bv.get('byteStride')
    raw = np.frombuffer(bin_, dtype=dt, offset=start, count=a['count'] * ncomp)
    if stride and stride != ncomp * np.dtype(dt).itemsize:
        raw = np.lib.stride_tricks.as_strided(
            np.frombuffer(bin_, dtype=np.uint8, offset=start),
            shape=(a['count'], ncomp), strides=(stride, np.dtype(dt).itemsize)).copy().ravel()
    return raw.reshape(a['count'], ncomp)

def analyze(path):
    g, bin_ = load_glb(path)
    nodes = g.get('nodes', [])
    skins = g.get('skins', [])
    joints = skins[0]['joints'] if skins else []
    mass = np.zeros(len(joints))
    pos_min = np.array([1e9] * 3); pos_max = np.array([-1e9] * 3)
    for m in g.get('meshes', []):
        for pr in m['primitives']:
            P = acc(g, bin_, pr['attributes']['POSITION']).astype(np.float64)
            pos_min = np.minimum(pos_min, P.min(axis=0)); pos_max = np.maximum(pos_max, P.max(axis=0))
            if 'JOINTS_0' in pr['attributes']:
                J = acc(g, bin_, pr['attributes']['JOINTS_0']).astype(np.int64)
                W = acc(g, bin_, pr['attributes']['WEIGHTS_0']).astype(np.float64)
                for k in range(4):
                    ok = J[:, k] < len(joints)
                    if (~ok).any():
                        assert W[~ok, k].max() == 0, 'nonzero weight on sentinel joint!'
                    np.add.at(mass, J[ok, k], W[ok, k])
    return g, nodes, joints, mass, pos_min, pos_max

HEADDIR = '/home/hatch/workspace/_doa4p2-scratch/p9/glb-chrtwo/extracted'
out = {}
for pkg in range(4, 46):
    p = os.path.join(HEADDIR, 'chrtwo-pkg%02d-skinned.glb' % pkg)
    if not os.path.exists(p):
        print('MISSING', p); continue
    g, nodes, joints, mass, pmin, pmax = analyze(p)
    top = sorted(range(len(joints)), key=lambda i: -mass[i])[:6]
    out['pkg%02d' % pkg] = {
        'nnodes': len(nodes), 'njoints': len(joints),
        'pos_min': [round(float(x), 3) for x in pmin], 'pos_max': [round(float(x), 3) for x in pmax],
        'top_joints': [(int(joints[i]), round(float(mass[i]), 1)) for i in top if mass[i] > 0],
        'total_mass': round(float(mass.sum()), 1),
        'node_translations': {str(i): [round(float(x), 3) for x in n.get('translation', [0, 0, 0])] for i, n in enumerate(nodes[:16])},
        'joint_nodes': [int(j) for j in joints],
    }
    o = out['pkg%02d' % pkg]
    print('pkg%02d nodes=%d joints=%d posY[%.3f..%.3f] posX[%.3f..%.3f] posZ[%.3f..%.3f] top=%s total=%.0f' % (
        pkg, o['nnodes'], o['njoints'], pmin[1], pmax[1], pmin[0], pmax[0], pmin[2], pmax[2],
        o['top_joints'], o['total_mass']))
json.dump(out, open('/home/hatch/workspace/_doa4p2-scratch/p11/head_weights.json', 'w'), indent=1)
print('wrote head_weights.json')

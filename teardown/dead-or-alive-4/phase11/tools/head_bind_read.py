#!/usr/bin/env python3
"""Phase 11 Job 2b: dominant-joint bind positions per head.
Bind world matrix of joint j = inverse(IBM_j). Report its translation
plus geometry Y extent relative to it, for floater/marginal/seated sets."""
import json, struct, os
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
    ncomp = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[a['type']]
    dt = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8}[a['componentType']]
    stride = bv.get('byteStride')
    raw = np.frombuffer(bin_, dtype=dt, offset=start, count=a['count'] * ncomp)
    if stride and stride != ncomp * np.dtype(dt).itemsize:
        raw = np.lib.stride_tricks.as_strided(
            np.frombuffer(bin_, dtype=np.uint8, offset=start),
            shape=(a['count'], ncomp), strides=(stride, np.dtype(dt).itemsize)).copy().ravel()
    return raw.reshape(a['count'], ncomp)

HEADDIR = '/home/hatch/workspace/_doa4p2-scratch/p9/glb-chrtwo/extracted'
FLOAT = {9, 18, 19, 20, 21, 25, 33}; MARG = {7}
SEATED = {4, 8, 11, 17, 29, 30, 34, 35, 41, 42, 44}
res = {}
for pkg in range(4, 46):
    p = os.path.join(HEADDIR, 'chrtwo-pkg%02d-skinned.glb' % pkg)
    g, bin_ = load_glb(p)
    sk = g['skins'][0]
    joints = sk['joints']
    ibm = acc(g, bin_, sk['inverseBindMatrices']).astype(np.float64).reshape(-1, 4, 4).transpose(0, 2, 1)  # column-major -> row
    bind = np.linalg.inv(ibm)
    mass = np.zeros(len(joints))
    pmin = np.array([1e9] * 3); pmax = np.array([-1e9] * 3)
    for m in g.get('meshes', []):
        for pr in m['primitives']:
            P = acc(g, bin_, pr['attributes']['POSITION']).astype(np.float64)
            ok = np.isfinite(P).all(axis=1) & (np.abs(P) < 10).all(axis=1)
            P = P[ok]
            pmin = np.minimum(pmin, P.min(axis=0)); pmax = np.maximum(pmax, P.max(axis=0))
            J = acc(g, bin_, pr['attributes']['JOINTS_0']).astype(np.int64)
            W = acc(g, bin_, pr['attributes']['WEIGHTS_0']).astype(np.float64)
            for k in range(4):
                okj = J[:, k] < len(joints)
                np.add.at(mass, J[okj, k], W[okj, k])
    dom = int(np.argmax(mass))
    bt = bind[dom][:3, 3]
    grp = 'FLOAT' if pkg in FLOAT else ('MARG' if pkg in MARG else ('SEATED' if pkg in SEATED else 'other'))
    res['pkg%02d' % pkg] = {'group': grp, 'dom_node': int(joints[dom]), 'dom_mass_frac': round(float(mass[dom] / mass.sum()), 3),
                            'bind_t': [round(float(x), 4) for x in bt], 'ymin': round(float(pmin[1]), 4), 'ymax': round(float(pmax[1]), 4),
                            'below_bind': round(float(bt[1] - pmin[1]), 4), 'above_bind': round(float(pmax[1] - bt[1]), 4),
                            'joint_bind': {str(int(joints[i])): [round(float(x), 3) for x in bind[i][:3, 3]] for i in range(len(joints))}}
    print('pkg%02d %-6s domNode=%2d frac=%.2f bindT=(%.3f,%.3f,%.3f) Y[%.3f..%.3f] below=%.3f above=%.3f' % (
        pkg, grp, joints[dom], mass[dom] / mass.sum(), bt[0], bt[1], bt[2], pmin[1], pmax[1], bt[1] - pmin[1], pmax[1] - bt[1]))
json.dump(res, open('/home/hatch/workspace/_doa4p2-scratch/p11/head_bind.json', 'w'), indent=1)
print('wrote head_bind.json')

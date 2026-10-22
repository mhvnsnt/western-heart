#!/usr/bin/env python3
"""Phase 11 Job 2c: TRUE skinned bind pose per head GLB.
v' = sum_j w_j * (World_j * IBM_j) * v, World from the GLB node
hierarchy. This is what a renderer shows at rest — the number the
composite placement must be based on."""
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

def node_local(n):
    if 'matrix' in n:
        return np.array(n['matrix'], dtype=np.float64).reshape(4, 4).T
    t = n.get('translation', [0, 0, 0]); r = n.get('rotation', [0, 0, 0, 1]); s = n.get('scale', [1, 1, 1])
    x, y, z, w = r
    R = np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w), 0],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w), 0],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y), 0],
        [0, 0, 0, 1]], dtype=np.float64)
    R[:3, :3] *= np.array(s)[None, :]
    R[:3, 3] = t
    return R

def analyze(path):
    g, bin_ = load_glb(path)
    nodes = g['nodes']
    parent = {}
    for i, n in enumerate(nodes):
        for c in n.get('children', []):
            parent[c] = i
    world = {}
    def W(i):
        if i not in world:
            L = node_local(nodes[i])
            world[i] = W(parent[i]) @ L if i in parent else L
        return world[i]
    sk = g['skins'][0]
    joints = sk['joints']
    ibm = acc(g, bin_, sk['inverseBindMatrices']).astype(np.float64).reshape(-1, 4, 4).transpose(0, 2, 1)
    M = [W(j) @ ibm[k] for k, j in enumerate(joints)]
    out_min = np.array([1e9] * 3); out_max = np.array([-1e9] * 3)
    for m in g.get('meshes', []):
        for pr in m['primitives']:
            P = acc(g, bin_, pr['attributes']['POSITION']).astype(np.float64)
            ok = np.isfinite(P).all(axis=1) & (np.abs(P) < 10).all(axis=1)
            P = P[ok]
            J = acc(g, bin_, pr['attributes']['JOINTS_0']).astype(np.int64)[ok]
            Wt = acc(g, bin_, pr['attributes']['WEIGHTS_0']).astype(np.float64)[ok]
            Ph = np.concatenate([P, np.ones((len(P), 1))], axis=1)
            acc_out = np.zeros((len(P), 3))
            for k in range(4):
                jj = J[:, k]; ww = Wt[:, k]
                valid = jj < len(joints)
                for jidx in np.unique(jj[valid]):
                    sel = valid & (jj == jidx)
                    acc_out[sel] += ww[sel, None] * (Ph[sel] @ M[jidx].T)[:, :3]
            out_min = np.minimum(out_min, acc_out.min(axis=0)); out_max = np.maximum(out_max, acc_out.max(axis=0))
    return out_min, out_max

HEADDIR = '/home/hatch/workspace/_doa4p2-scratch/p9/glb-chrtwo/extracted'
FLOAT = {9, 18, 19, 20, 21, 25, 33}; MARG = {7}
SEATED = {4, 8, 11, 17, 29, 30, 34, 35, 41, 42, 44}
res = {}
for pkg in range(4, 46):
    mn, mx = analyze(os.path.join(HEADDIR, 'chrtwo-pkg%02d-skinned.glb' % pkg))
    grp = 'FLOAT' if pkg in FLOAT else ('MARG' if pkg in MARG else ('SEATED' if pkg in SEATED else 'other'))
    res['pkg%02d' % pkg] = {'group': grp, 'skin_min': [round(float(x), 4) for x in mn], 'skin_max': [round(float(x), 4) for x in mx]}
    print('pkg%02d %-6s skinned Y[%.3f..%.3f] X[%.3f..%.3f] Z[%.3f..%.3f]' % (pkg, grp, mn[1], mx[1], mn[0], mx[0], mn[2], mx[2]))
json.dump(res, open('/home/hatch/workspace/_doa4p2-scratch/p11/head_skinbind.json', 'w'), indent=1)
print('wrote head_skinbind.json')

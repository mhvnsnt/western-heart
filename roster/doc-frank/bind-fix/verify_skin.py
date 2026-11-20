#!/usr/bin/env python3
"""Independent check: skin all vertices at bind pose in two GLBs, compare.
Also compares joint world positions and mesh vertex counts."""
import json, struct, sys
import numpy as np

def load(path):
    d = open(path, 'rb').read()
    ln = struct.unpack('<I', d[12:16])[0]
    js = json.loads(d[20:20+ln])
    off = 20 + ln
    bln, _ = struct.unpack('<I4s', d[off:off+8])
    return js, d[off+8:off+8+bln]

def acc_data(js, bin_data, idx):
    acc = js['accessors'][idx]
    bv = js['bufferViews'][acc['bufferView']]
    base = bv.get('byteOffset', 0) + acc.get('byteOffset', 0)
    ncomp = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[acc['type']]
    dt = {5126: '<f4', 5123: '<u2', 5125: '<u4', 5121: 'u1', 5122: '<i2', 5120: 'i1'}[acc['componentType']]
    itemsize = np.dtype(dt).itemsize * ncomp
    stride = bv.get('byteStride')
    if stride and stride != itemsize:
        raw = np.frombuffer(bin_data[base:base + stride * acc['count']], dtype='u1')
        raw = raw.reshape(acc['count'], stride)[:, :itemsize]
        arr = raw.copy().view(dt)
    else:
        n = acc['count'] * ncomp
        arr = np.frombuffer(bin_data[base:base + n * np.dtype(dt).itemsize], dtype=dt)
    return arr.reshape(acc['count'], ncomp) if ncomp > 1 else arr

def quat_mat(q):
    x, y, z, w = q
    return np.array([
        [1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w), 0],
        [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w), 0],
        [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y), 0],
        [0, 0, 0, 1]], float)

def local(n):
    T = np.eye(4)
    if 'translation' in n: T[:3, 3] = n['translation']
    R = quat_mat(n['rotation']) if 'rotation' in n else np.eye(4)
    S = np.diag([*(n.get('scale', [1, 1, 1])), 1.0])
    if 'matrix' in n:
        return np.array(n['matrix'], float).reshape((4, 4), order='F')
    return T @ R @ S

def worlds(js):
    nodes = js['nodes']
    w = {}
    def go(i, pw):
        w[i] = pw @ local(nodes[i])
        for c in nodes[i].get('children', []):
            go(c, w[i])
    for sc in js.get('scenes', []):
        for r in sc.get('nodes', []):
            go(r, np.eye(4))
    return w

def skinned_positions(path):
    js, bin_data = load(path)
    w = worlds(js)
    skin = js['skins'][0]
    joints = skin['joints']
    ibms = acc_data(js, bin_data, skin['inverseBindMatrices']).reshape(len(joints), 4, 4)
    ibms = np.array([m.T for m in ibms])  # frombuffer row-major -> transpose to col-major convention
    # acc_data reshaped (count,16) row-major view of column-major data: element (r,c) is at r*4+c in col-major storage = index c*4+r
    raw = acc_data(js, bin_data, skin['inverseBindMatrices'])
    ibms = np.array([raw[k].reshape((4, 4), order='F') for k in range(len(joints))])
    bone_mats = [w[j] @ ibms[k] for k, j in enumerate(joints)]
    out = []
    jpos = {js['nodes'][j].get('name'): w[j][:3, 3] for j in joints}
    for mesh in js['meshes']:
        for prim in mesh['primitives']:
            pos = acc_data(js, bin_data, prim['attributes']['POSITION']).astype(float)
            if 'JOINTS_0' not in prim['attributes']:
                out.append(pos)
                continue
            jidx = acc_data(js, bin_data, prim['attributes']['JOINTS_0']).astype(int)
            wts = acc_data(js, bin_data, prim['attributes']['WEIGHTS_0']).astype(float)
            v = np.concatenate([pos, np.ones((len(pos), 1))], axis=1)
            sk = np.zeros((len(pos), 4))
            for k in range(4):
                M = np.array([bone_mats[j] for j in jidx[:, k]])
                sk += wts[:, k:k+1] * np.einsum('nij,nj->ni', M, v)
            out.append(sk[:, :3])
    return np.concatenate(out), jpos

if __name__ == '__main__':
    a, ja = skinned_positions(sys.argv[1])
    b, jb = skinned_positions(sys.argv[2])
    print(f"verts: {len(a)} vs {len(b)}")
    assert len(a) == len(b)
    dev = np.abs(a - b).max()
    print(f"max skinned-vertex deviation at bind pose: {dev:.2e}")
    common = set(ja) & set(jb)
    pd = max(np.abs(ja[k] - jb[k]).max() for k in common)
    print(f"max joint world-position deviation ({len(common)} named joints): {pd:.2e}")

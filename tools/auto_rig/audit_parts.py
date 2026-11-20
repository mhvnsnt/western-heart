#!/usr/bin/env python3
"""audit_parts.py — per-part skinning audit for multi-skin GLBs.

The repo's tools/auto_rig/anim_check.py AnimModel applies skins[0]'s inverse bind
matrices to EVERY primitive. Multi-part exports (the 2026-10-23 "gamerig" files:
mina-ashido model-rerig, miruko model-rerig-textured, tsuyu model-rigged-textured)
give each part its OWN skin whose IBMs map that part's local frame into skeleton
space, so single-IBM skinning collapses/misplaces parts and the region metrics
come out garbage. three.js (the game) applies each SkinnedMesh's own skin. This
probe does the same: skin every primitive with the skin of the node that
references its mesh, then report height + rig_inspect region shares + seams.

Usage: audit_parts.py plain.glb [plain2.glb ...]   (meshopt files: decode first
with tools/anim/gltf_codec.mjs)"""
import json, struct, sys
import numpy as np

sys.path.insert(0, '/home/hatch/workspace/_smutbase6-fix-20261102/repo/tools/auto_rig')
sys.path.insert(0, '/home/hatch/workspace/_smutbase6-fix-20261102/repo/tools/auto_rig/backends')
import rig_inspect as R
from smooth_weights import _skin_fast

_COMP = {5120: ('b', 1), 5121: ('B', 1), 5122: ('h', 2), 5123: ('H', 2), 5125: ('I', 4), 5126: ('f', 4)}
_TN = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}

def read_glb(path):
    data = open(path, 'rb').read()
    assert data[:4] == b'glTF'
    jlen = struct.unpack('<I', data[12:16])[0]
    js = json.loads(data[20:20 + jlen])
    boff = 20 + jlen
    blen = struct.unpack('<I', data[boff:boff + 4])[0]
    return js, data[boff + 8:boff + 8 + blen]

def read_acc(js, bdat, idx):
    a = js['accessors'][idx]; bv = js['bufferViews'][a['bufferView']]
    fmt, sz = _COMP[a['componentType']]; n = _TN[a['type']]
    off = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    stride = bv.get('byteStride', 0) or n * sz
    count = a['count']
    raw = np.frombuffer(bdat, dtype=np.uint8, count=(count - 1) * stride + n * sz, offset=off)
    dt = np.dtype('<' + fmt)
    if stride == n * sz:
        arr = raw[:count * n * sz].view(dt).reshape(count, n).astype(np.float64)
    else:
        arr = np.zeros((count, n))
        for i in range(count):
            arr[i] = np.frombuffer(raw, dtype=dt, count=n, offset=i * stride)
    if a.get('normalized'):
        arr = arr / float({'b': 127, 'B': 255, 'h': 32767, 'H': 65535}[fmt])
    return arr

def node_local(n):
    if 'matrix' in n:
        return np.array(n['matrix'], dtype=np.float64).reshape(4, 4).T
    t = n.get('translation', [0, 0, 0]); r = n.get('rotation', [0, 0, 0, 1]); s = n.get('scale', [1, 1, 1])
    x, y, z, w = r
    Rm = np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                   [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                   [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
    m = np.eye(4); m[:3, :3] = Rm * np.array(s); m[:3, 3] = t
    return m

def audit(path):
    js, bdat = read_glb(path)
    nodes = js['nodes']
    parent = {}
    for i, nd in enumerate(nodes):
        for c in nd.get('children', []):
            parent[c] = i
    world = {}
    def getw(i):
        if i not in world:
            m = node_local(nodes[i])
            world[i] = (getw(parent[i]) @ m) if i in parent else m
        return world[i]
    # mesh index -> skin index (via nodes)
    mesh_skin = {}
    for nd in nodes:
        if 'mesh' in nd:
            mesh_skin[nd['mesh']] = nd.get('skin')
    skins = js.get('skins', [])
    # canonical joint order: skins[0] joints (all skins share it in these exports)
    canon = skins[0]['joints'] if skins else []
    names = [nodes[j].get('name', '') for j in canon]
    name_to_canon = {n: k for k, n in enumerate(names)}
    bind = {j: getw(j) for j in set(canon)}
    Ps, Js_, Ws, Ts = [], [], [], []
    voff = 0
    for mi, mesh in enumerate(js['meshes']):
        si = mesh_skin.get(mi)
        if si is None:
            continue
        skin = skins[si]
        ibm = read_acc(js, bdat, skin['inverseBindMatrices']).reshape(-1, 4, 4).transpose(0, 2, 1)
        # per-skin joint -> canonical index remap (by node id)
        remap = np.array([canon.index(j) for j in skin['joints']])
        bs_canon = np.zeros((len(canon), 4, 4))
        for k, j in enumerate(skin['joints']):
            bs_canon[remap[k]] = bind[j] @ ibm[k]
        for prim in mesh['primitives']:
            at = prim['attributes']
            if 'JOINTS_0' not in at:
                continue
            pos = read_acc(js, bdat, at['POSITION'])
            jn = read_acc(js, bdat, at['JOINTS_0']).astype(int)
            w = read_acc(js, bdat, at['WEIGHTS_0'])
            ws = w.sum(1, keepdims=True); ws[ws == 0] = 1
            w = w / ws
            jn = remap[jn]
            pr = {'pos': pos, 'joints': jn, 'weights': w}
            P = _skin_fast(bs_canon, pr, np.c_[pos, np.ones(len(pos))])
            idx = read_acc(js, bdat, prim['indices']).reshape(-1).astype(np.int64) if 'indices' in prim else np.arange(len(pos))
            Ps.append(P); Js_.append(jn); Ws.append(w); Ts.append(idx + voff)
            voff += len(pos)
    P = np.concatenate(Ps); Jn = np.concatenate(Js_); W = np.concatenate(Ws); T = np.concatenate(Ts)
    jp = {n: bind[j][:3, 3].astype(np.float64) for n, j in zip(names, canon)}
    # load_skinned-compatible normalization: face +Z via toes, ground y=0, Left on +X
    if all(k in jp for k in ('LeftFoot', 'LeftToeBase', 'RightFoot', 'RightToeBase')):
        fwd = (jp['LeftToeBase'] - jp['LeftFoot'] + jp['RightToeBase'] - jp['RightFoot'])[[0, 2]]
        ang = np.arctan2(fwd[0], fwd[1]); c, s = np.cos(-ang), np.sin(-ang)
        Rm = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        P = P @ Rm.T; jp = {n: Rm @ v for n, v in jp.items()}
    y0 = P[:, 1].min(); P[:, 1] -= y0
    jp = {n: v - np.array([0, y0, 0]) for n, v in jp.items()}
    if 'LeftArm' in jp and 'RightArm' in jp and jp['LeftArm'][0] < jp['RightArm'][0]:
        P[:, 0] *= -1; jp = {n: v * np.array([-1, 1, 1]) for n, v in jp.items()}
    print(f'== {path}')
    print(f'   skinned height: {P[:,1].max():.3f} m   verts: {len(P)}')
    for lab, n, sh in R.region_shares(P, Jn, W, names, jp):
        top = sorted(sh.items(), key=lambda kv: -kv[1])[:3]
        print(f'   {lab}: n={n} {[(k, round(v,3)) for k,v in top]}')
    print('   seams:', R.seam_stats(P, Jn, W, names))

for p in sys.argv[1:]:
    audit(p)

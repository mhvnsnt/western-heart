"""Minimal GLB reader/writer helpers for the lash-fix lane (numpy only)."""
import json, struct
import numpy as np

CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16,
      5125: np.uint32, 5126: np.float32}
NCOMP = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}

def load_glb(path):
    with open(path, 'rb') as f:
        data = f.read()
    assert data[:4] == b'glTF', path
    jlen = struct.unpack('<I', data[12:16])[0]
    gltf = json.loads(data[20:20 + jlen])
    off = 20 + jlen
    blen = struct.unpack('<I', data[off:off + 4])[0]
    binbuf = data[off + 8:off + 8 + blen]
    return gltf, binbuf, data

def accessor(gltf, binbuf, idx):
    a = gltf['accessors'][idx]
    if 'bufferView' not in a:
        return np.zeros((a['count'], NCOMP[a['type']]), dtype=np.float64)
    bv = gltf['bufferViews'][a['bufferView']]
    start = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    n = a['count'] * NCOMP[a['type']]
    dt = CT[a['componentType']]
    stride = bv.get('byteStride')
    if stride and stride != np.dtype(dt).itemsize * NCOMP[a['type']]:
        raw = np.frombuffer(binbuf, dtype=np.uint8, count=stride * a['count'], offset=start)
        raw = raw.reshape(a['count'], stride)[:, :np.dtype(dt).itemsize * NCOMP[a['type']]]
        arr = raw.copy().view(dt).reshape(a['count'], NCOMP[a['type']])
    else:
        arr = np.frombuffer(binbuf, dtype=dt, count=n, offset=start).reshape(a['count'], NCOMP[a['type']])
    return arr.astype(np.float64) if a['componentType'] == 5126 else arr

def node_world_mats(gltf):
    """World matrix per node (bind pose, from node TRS only)."""
    mats = {}
    def mat_of(n):
        if 'matrix' in n:
            return np.array(n['matrix'], dtype=np.float64).reshape(4, 4).T
        t = np.array(n.get('translation', [0, 0, 0]), dtype=np.float64)
        r = n.get('rotation', [0, 0, 0, 1])
        s = np.array(n.get('scale', [1, 1, 1]), dtype=np.float64)
        x, y, z, w = r
        R = np.array([
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
        M = np.eye(4); M[:3, :3] = R * s[None, :]; M[:3, 3] = t
        return M
    children = {}
    roots = []
    for i, n in enumerate(gltf.get('nodes', [])):
        for c in n.get('children', []):
            children[c] = i
    def world(i):
        if i in mats: return mats[i]
        M = mat_of(gltf['nodes'][i])
        if i in children: M = world(children[i]) @ M
        mats[i] = M
        return M
    for i in range(len(gltf.get('nodes', []))):
        world(i)
    return mats

def skinned_positions(gltf, binbuf, mesh_idx, morphs=None):
    """World-space skinned positions, bind pose. morphs={name:weight}."""
    morphs = morphs or {}
    mesh = gltf['meshes'][mesh_idx]
    skin = None; node_w = None
    mats = node_world_mats(gltf)
    for ni, n in enumerate(gltf.get('nodes', [])):
        if n.get('mesh') == mesh_idx:
            if 'skin' in n: skin = gltf['skins'][n['skin']]
            node_w = mats[ni]
            break
    out_prims = []
    for prim in mesh['primitives']:
        pos = accessor(gltf, binbuf, prim['attributes']['POSITION']).copy()
        if morphs and 'targets' in prim:
            names = mesh.get('extras', {}).get('targetNames', [])
            for mn, mw in morphs.items():
                if mn in names:
                    pos = pos + accessor(gltf, binbuf, prim['targets'][names.index(mn)]['POSITION']) * mw
        if skin is not None and 'JOINTS_0' in prim['attributes'] and 'WEIGHTS_0' in prim['attributes']:
            W = accessor(gltf, binbuf, prim['attributes']['WEIGHTS_0']).astype(np.float64)
            J = accessor(gltf, binbuf, prim['attributes']['JOINTS_0']).astype(int)
            ibm = accessor(gltf, binbuf, skin['inverseBindMatrices']).reshape(-1, 4, 4).transpose(0, 2, 1)
            joints = skin['joints']
            jm = np.stack([mats[j] @ ibm[k] for k, j in enumerate(joints)])
            Rj = jm[J][:, :, :3, :3]                       # (n,4,3,3)
            tj = jm[J][:, :, :3, 3]                        # (n,4,3)
            tp = np.einsum('njoi,ni->njo', Rj, pos) + tj   # (n,4,3)
            pos = np.einsum('nj,njk->nk', W, tp)
        elif node_w is not None:
            pos = pos @ node_w[:3, :3].T + node_w[:3, 3]
        idx = None
        if 'indices' in prim:
            idx = accessor(gltf, binbuf, prim['indices']).reshape(-1)
        out_prims.append({'pos': pos, 'idx': idx, 'mat': prim.get('material')})
    return out_prims

def prim_local(gltf, binbuf, mesh_idx, prim_idx, morphs=None):
    """Local (pre-skin) positions for one prim with morphs applied."""
    mesh = gltf['meshes'][mesh_idx]
    prim = mesh['primitives'][prim_idx]
    pos = accessor(gltf, binbuf, prim['attributes']['POSITION']).copy()
    if morphs and 'targets' in prim:
        names = mesh.get('extras', {}).get('targetNames', [])
        for mn, mw in morphs.items():
            if mn in names:
                pos = pos + accessor(gltf, binbuf, prim['targets'][names.index(mn)]['POSITION']) * mw
    idx = accessor(gltf, binbuf, prim['indices']).reshape(-1) if 'indices' in prim else None
    return pos, idx

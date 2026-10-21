#!/usr/bin/env python3
"""Round-2 placement round-trip verifier (no Blender needed).

Measures a baked GLB the way the game sees it:
  measure <glb>  -> JSON with, per part node (name starts "cs_"): world
  bbox + centroid; the Head joint world position; the base model's
  Head-dominant skinned verts world bbox + centroid (the head itself);
  Hips joint world position (for the up axis).

Skinned verts are evaluated properly: world = sum_i w_i * (jointWorld_i
* inverseBind_i) * v. Part nodes are bone children in the node tree, so
their world transforms compose down the tree.

Proof use: bake a record with placement P, measure; bake again with
P + delta, measure; the part centroid must move by exactly the bone-frame
delta (checked by cs-round2-proof.sh / the lane's proof notes).
"""
import json, struct, sys
import numpy as np

def load(path):
    with open(path, 'rb') as f:
        data = f.read()
    clen, _ = struct.unpack('<II', data[12:20])
    g = json.loads(data[20:20 + clen])
    off = 20 + clen
    blen, _ = struct.unpack('<II', data[off:off + 8])
    return g, data[off + 8:off + 8 + blen]

def acc(g, b, ai):
    a = g['accessors'][ai]
    bv = g['bufferViews'][a['bufferView']]
    start = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    ncomp = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[a['type']]
    dt = {5126: np.float32, 5123: np.uint16, 5125: np.uint32,
          5121: np.uint8, 5120: np.int8, 5122: np.int16}[a['componentType']]
    raw = np.frombuffer(b, dtype=dt, count=a['count'] * ncomp, offset=start)
    stride = bv.get('byteStride')
    if stride and stride != raw.dtype.itemsize * ncomp:
        raw = np.frombuffer(b, dtype=np.uint8, count=stride * a['count'], offset=start)
        raw = raw.reshape(a['count'], stride)[:, :raw.dtype.itemsize * ncomp].copy().view(dt)
    arr = raw.reshape(a['count'], ncomp) if ncomp > 1 else raw
    if a.get('normalized'):
        arr = arr.astype(np.float64) / float(np.iinfo(dt).max)
    return arr.astype(np.float64)

def node_local(n):
    if 'matrix' in n:
        return np.array(n['matrix'], dtype=float).reshape(4, 4).T
    T = np.eye(4); T[:3, 3] = n.get('translation', [0, 0, 0])
    x, y, z, w = n.get('rotation', [0, 0, 0, 1])
    R = np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w), 0],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w), 0],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y), 0],
        [0, 0, 0, 1]], dtype=float)
    S = np.diag([*n.get('scale', [1, 1, 1]), 1.0])
    return T @ R @ S

def measure(path):
    g, b = load(path)
    nodes = g['nodes']
    worlds = {}
    def walk(i, parent):
        w = parent @ node_local(nodes[i])
        worlds[i] = w
        for c in nodes[i].get('children', []):
            walk(c, w)
    for s in g.get('scenes', [{}])[0].get('nodes', []):
        walk(s, np.eye(4))
    out = {'parts': {}, 'joints': {}}
    skins = g.get('skins', [])
    joint_world = {}
    if skins:
        sk = skins[0]
        ibm = acc(g, b, sk['inverseBindMatrices']).reshape(-1, 4, 4)
        ibm = np.transpose(ibm, (0, 2, 1))
        for ji, jn in enumerate(sk['joints']):
            joint_world[jn] = worlds[jn] @ ibm[ji]
            nm = nodes[jn].get('name')
            if nm in ('Head', 'Hips', 'Neck'):
                out['joints'][nm] = worlds[jn][:3, 3].round(4).tolist()
    head_verts = []
    for ni, n in enumerate(nodes):
        if 'mesh' not in n:
            continue
        mesh = g['meshes'][n['mesh']]
        for prim in mesh['primitives']:
            pos = acc(g, b, prim['attributes']['POSITION'])
            if 'skin' in n and 'JOINTS_0' in prim['attributes']:
                J = acc(g, b, prim['attributes']['JOINTS_0']).astype(int)
                W = acc(g, b, prim['attributes']['WEIGHTS_0'])
                mats = np.stack([joint_world[j] for j in sk['joints']])
                posh = np.concatenate([pos, np.ones((len(pos), 1))], axis=1)
                vw = np.zeros_like(pos)
                for k in range(4):
                    mk = mats[J[:, k]]
                    vw += W[:, k:k + 1] * np.einsum('nij,nj->ni', mk[:, :3, :], posh)
                dom = J[np.arange(len(J)), W.argmax(1)]
                names = [nodes[j].get('name') for j in sk['joints']]
                hv = vw[[names[d] == 'Head' for d in dom]]
                if len(hv):
                    head_verts.append(hv)
            else:
                vw = (worlds[ni][:3, :3] @ pos.T).T + worlds[ni][:3, 3]
                if (n.get('name') or '').startswith('cs_'):
                    out['parts'][n['name']] = {
                        'bbox_min': vw.min(0).round(4).tolist(),
                        'bbox_max': vw.max(0).round(4).tolist(),
                        'centroid': vw.mean(0).round(4).tolist(),
                        'verts': len(vw),
                    }
    if head_verts:
        H = np.vstack(head_verts)
        out['head'] = {
            'bbox_min': H.min(0).round(4).tolist(),
            'bbox_max': H.max(0).round(4).tolist(),
            'centroid': H.mean(0).round(4).tolist(),
            'verts': len(H),
        }
    return out

if __name__ == '__main__':
    if sys.argv[1] == 'measure':
        print(json.dumps(measure(sys.argv[2]), indent=1))
    else:
        print(__doc__)
        sys.exit(1)

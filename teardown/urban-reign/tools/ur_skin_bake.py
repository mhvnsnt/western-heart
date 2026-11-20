#!/usr/bin/env python3
"""Bake one decoded motion into per-frame vertex positions via numpy skinning.

Joint world matrices: game hierarchy (H-index: motion bone b = GLB node
index b) composed from bind locals Lbind = W[parent]^-1 W[b] with the
rotation part replaced by the sampler Euler matrix; motion bone 0 is the
root position track (KOSHI, node 12) - its local translation is anchored
at bind plus the scaled game-space delta. Non-body joints ride their GLB
parents with bind locals. W = inv(IBM) from the GLB (game space = GLB
space; phase-1 skinning relations are exact in this space).
"""
import json, struct, sys
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/ur-phase2-work/tools')
from ur_gyu import Bank, load_tables

PARENT_GAME = {12: None, 0: 12, 1: 0, 2: 1, 3: 2, 4: 1, 5: 4, 6: 5, 7: 6,
               8: 1, 9: 8, 10: 9, 11: 10, 13: 12, 14: 13, 15: 14, 16: 15,
               17: 12, 18: 17, 19: 18, 20: 19}
MB2NODE = {0: 12, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8,
           10: 9, 11: 10, 12: 11, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17,
           18: 18, 19: 19, 20: 20}
BODY_ORDER = [12, 0, 13, 17, 1, 14, 18, 2, 4, 8, 15, 19, 3, 5, 9, 16, 20, 6, 10, 7, 11]
ROOT_SCALE = 0.4034  # caller applies sampler pos x 0.1 x char scale (FUN_002918xx)

def eul2mat(x, y, z, order):
    cx, sx, cy, sy, cz, sz = np.cos(x), np.sin(x), np.cos(y), np.sin(y), np.cos(z), np.sin(z)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]], float)
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], float)
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]], float)
    return {'RzRyRx': Rz @ Ry @ Rx, 'RxRyRz': Rx @ Ry @ Rz}[order]

def load_glb(p):
    data = open(p, 'rb').read()
    ln = struct.unpack('<I', data[12:16])[0]
    g = json.loads(data[20:20+ln])
    off = 20 + ln; bln = struct.unpack('<I', data[off:off+4])[0]
    binx = data[off+8:off+8+bln]
    def acc(ai):
        a = g['accessors'][ai]; bv = g['bufferViews'][a['bufferView']]
        o = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
        ct = {5126: '<f4', 5123: '<u2', 5125: '<u4', 5121: '<u1'}[a['componentType']]
        nc = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[a['type']]
        arr = np.frombuffer(binx, dtype=ct, count=a['count'] * nc, offset=o)
        return arr.reshape(a['count'], nc) if nc > 1 else arr
    skin = g['skins'][0]
    ibm = [np.array(m).reshape(4, 4).T for m in acc(skin['inverseBindMatrices'])]
    W = {ji: np.linalg.inv(ibm[k]) for k, ji in enumerate(skin['joints'])}
    parent = {}
    for i, n in enumerate(g['nodes']):
        for c in n.get('children', []): parent[c] = i
    mesh_node = [n for n in g['nodes'] if 'mesh' in n and 'skin' in n][0]
    pos_l, jts_l, wts_l, idx_l = [], [], [], []
    voff = 0
    for prim in g['meshes'][mesh_node['mesh']]['primitives']:
        pos_l.append(acc(prim['attributes']['POSITION']))
        jts_l.append(acc(prim['attributes']['JOINTS_0']))
        wts_l.append(acc(prim['attributes']['WEIGHTS_0']))
        idx = acc(prim['indices'])
        idx_l.append(idx.reshape(-1, 3) + voff)
        voff += len(pos_l[-1])
    return (g, skin, W, parent, np.vstack(pos_l), np.vstack(jts_l),
            np.vstack(wts_l), np.vstack(idx_l))

def sample(vals, fpk, frame):
    p = frame / fpk
    i = min(int(p), len(vals) - 1); fr = p - i
    j = min(i + 1, len(vals) - 1)
    return tuple(vals[i][c] * (1 - fr) + vals[j][c] * fr for c in range(3))

MODE = 'delta'
def bake(gyu, glb, mi, order, frames_wanted, out_npz):
    set1, set2 = load_tables('/home/hatch/workspace/ur-decode/work/SLUS_212.09')
    bank = Bank(gyu)
    trs = bank.tracks(mi)
    dec = [t.decode(bank.d, set1, set2) for t in trs]
    g, skin, W, glb_parent, pos, jts, wts, idx = load_glb(glb)
    joints = skin['joints']
    # bind locals under game hierarchy (body) / glb hierarchy (others)
    Lbind = {}
    for n in BODY_ORDER:
        par = PARENT_GAME[n]
        Lbind[n] = W[n].copy() if par is None else np.linalg.inv(W[par]) @ W[n]
    others = [ji for ji in joints if ji not in Lbind]
    # glb-topological order for others
    def depth(ji):
        d = 0
        while ji in glb_parent: d += 1; ji = glb_parent[ji]
        return d
    for ji in sorted(others, key=depth):
        par = glb_parent.get(ji)
        Lbind[ji] = W[ji].copy() if par is None else np.linalg.inv(W[par]) @ W[ji]
    root0 = sample(dec[0], trs[0].fpk, 0)
    out = {}
    for f in frames_wanted:
        JW = {}
        for n in BODY_ORDER:
            par = PARENT_GAME[n]
            mb = [k for k, v in MB2NODE.items() if v == n][0]
            L = Lbind[n].copy()
            if n == 12:
                rp = sample(dec[0], trs[0].fpk, f)
                delta = np.array([rp[c] - root0[c] for c in range(3)]) * ROOT_SCALE
                # game (x,y,z) -> GLB (x, z, -y)
                L[:3, 3] = Lbind[n][:3, 3] + np.array([delta[0], delta[2], -delta[1]])
            else:
                e = sample(dec[mb], trs[mb].fpk, f)
                R = np.eye(4); R[:3, :3] = eul2mat(e[0], e[1], e[2], order)
                if MODE == 'delta':
                    L = Lbind[n] @ R
                elif MODE == 'abs':
                    Rb = Lbind[n][:3, :3]
                    # polar decomposition rotation of bind 3x3
                    U, _, Vt = np.linalg.svd(Rb)
                    Rp = U @ Vt
                    if np.linalg.det(Rp) < 0: U[:, -1] *= -1; Rp = U @ Vt
                    Rd = np.eye(4); Rd[:3, :3] = np.linalg.inv(Rp) @ eul2mat(e[0], e[1], e[2], order)
                    L = Lbind[n] @ Rd
            JW[n] = L if par is None else JW[par] @ L
        for ji in sorted(others, key=depth):
            par = glb_parent.get(ji)
            JW[ji] = Lbind[ji].copy() if par is None else JW[par] @ Lbind[ji]
        sk = np.zeros_like(pos)
        for k, ji in enumerate(joints):
            M = JW[ji] @ np.linalg.inv(W[ji])
            m = (jts == k)
            for s in range(4):
                sel = m[:, s]
                sk[sel] += (pos[sel] @ M[:3, :3].T + M[:3, 3]) * wts[sel, s:s+1]
        out[f'f{f}'] = sk
    np.savez(out_npz, idx=idx, **out)
    print('baked', list(out.keys()), '->', out_npz)

if __name__ == '__main__':
    import ur_skin_bake as _m
    _m.MODE = sys.argv[7] if len(sys.argv) > 7 else 'delta'
    bake(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4],
         [int(x) for x in sys.argv[5].split(',')], sys.argv[6])

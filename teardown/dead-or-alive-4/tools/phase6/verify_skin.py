"""Spot-verify a phase-6 skinned GLB from the file's own data:
1) bind-pose recomputation must reproduce POSITION (skin math self-consistent);
2) bend one joint (rotate its world joint-matrix subtree about the joint pivot)
   and write a static bent GLB for rendered own-eyes comparison.
Usage: verify_skin.py in.glb joint_index angle_deg out_bent.glb
"""
import numpy as np, struct, json, sys

def load_glb(path):
    b = open(path, 'rb').read()
    assert b[:4] == b'glTF'
    jlen = struct.unpack('<I', b[12:16])[0]
    g = json.loads(b[20:20 + jlen])
    off = 20 + jlen
    blen = struct.unpack('<I', b[off:off + 4])[0]
    bin_ = b[off + 8:off + 8 + blen]
    return g, bin_

CT = {5126: ('f', 4), 5123: ('H', 2), 5125: ('I', 4), 5121: ('B', 1)}
def acc_data(g, bin_, ai):
    a = g['accessors'][ai]; v = g['bufferViews'][a['bufferView']]
    start = v.get('byteOffset', 0) + a.get('byteOffset', 0)
    fmt, sz = CT[a['componentType']]
    ncomp = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[a['type']]
    arr = np.frombuffer(bin_, dtype=fmt, count=a['count'] * ncomp, offset=start)
    return arr.reshape(a['count'], ncomp) if ncomp > 1 else arr

def trs(t, q, s):
    x, y, z, w = q
    R = np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]], dtype=np.float64)
    M = np.eye(4); M[:3, :3] = R * np.array(s)[None, :]; M[:3, 3] = t
    return M

def main():
    path, joint, deg, outp = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    g, bin_ = load_glb(path)
    nodes = g['nodes']
    children = {}
    allchild = set()
    for i, n in enumerate(nodes):
        for c in n.get('children', []):
            children[c] = i; allchild.add(c)
    worlds = [None] * len(nodes)
    def world(i):
        if worlds[i] is not None: return worlds[i]
        n = nodes[i]
        L = trs(n.get('translation', [0, 0, 0]), n.get('rotation', [0, 0, 0, 1]), n.get('scale', [1, 1, 1]))
        worlds[i] = L if i not in children else world(children[i]) @ L
        return worlds[i]
    for i in range(len(nodes)): world(i)
    skin = g['skins'][0]
    joints = skin['joints']
    ibm = acc_data(g, bin_, skin['inverseBindMatrices']).reshape(len(joints), 4, 4).transpose(0, 2, 1)
    # ibm stored column-major: reading as row-major gives transpose; transpose back above.
    jm = np.array([worlds[j] @ ibm[k] for k, j in enumerate(joints)])
    jidx = {node: k for k, node in enumerate(joints)}
    # subtree of target joint (in node space)
    sub = set()
    stack = [joints[joint]]
    childrenmap = {}
    for i, n in enumerate(nodes):
        for c in n.get('children', []): childrenmap.setdefault(i, []).append(c)
    while stack:
        x = stack.pop(); sub.add(x); stack += childrenmap.get(x, [])
    th = np.radians(deg); c, s = np.cos(th), np.sin(th)
    pivot = worlds[joints[joint]][:3, 3]
    R = np.eye(4); R[0, 0], R[0, 1], R[1, 0], R[1, 1] = c, -s, s, c
    B = np.eye(4); B[:3, 3] = pivot; Bm = B @ R @ np.linalg.inv(B)
    jm_bent = jm.copy()
    for node in sub:
        if node in jidx: jm_bent[jidx[node]] = Bm @ jm[jidx[node]]
    maxbind = 0.0; meshes_out = []
    for mi, mesh in enumerate(g['meshes']):
        prim = mesh['primitives'][0]
        P = acc_data(g, bin_, prim['attributes']['POSITION']).astype(np.float64)
        J = acc_data(g, bin_, prim['attributes']['JOINTS_0']).astype(int)
        W = acc_data(g, bin_, prim['attributes']['WEIGHTS_0']).astype(np.float64)
        def apply(jmats):
            out = np.zeros_like(P)
            Ph = np.c_[P, np.ones(len(P))]
            for k in range(4):
                sel = jmats[J[:, k]]  # (N,4,4) column-convention joint matrices
                out += W[:, k:k + 1] * np.einsum('nj,njk->nk', Ph, sel.transpose(0, 2, 1))[:, :3]
            return out
        bind = apply(jm)
        err = np.abs(bind - P).max()
        maxbind = max(maxbind, err)
        bent = apply(jm_bent)
        N = acc_data(g, bin_, prim['attributes']['NORMAL']).astype(np.float32) if 'NORMAL' in prim['attributes'] else None
        idx = acc_data(g, bin_, prim['indices']).astype(np.int64).reshape(-1, 3)
        meshes_out.append((mesh['name'], bent, N, None, idx, 0))
    print(f'bind repro max err: {maxbind:.6f}')
    sys.path.insert(0, '/home/hatch/workspace/_doa4p2-scratch/p5')
    from pkg_glb import write_glb
    write_glb(outp, meshes_out)
    disp = 0.0
    print('bent glb written', outp)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Phase 9: skinned bind-pose bounds of a GLB: pos' = sum_i w_i (JW_i . IBM_i) pos.
Tells where geometry actually lands in world space at bind (vs raw positions)."""
import json, struct, sys
import numpy as np

def load(path):
    d = open(path, 'rb').read()
    jl = struct.unpack('<I', d[12:16])[0]
    g = json.loads(d[20:20+jl]); off = 20+jl
    bl = struct.unpack('<I', d[off:off+4])[0]
    return g, d[off+8:off+8+bl]

def acc(g, bin_, idx):
    a = g['accessors'][idx]; bv = g['bufferViews'][a['bufferView']]
    st = bv.get('byteOffset',0)+a.get('byteOffset',0)
    nc = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
    dt = {5126:np.float32,5123:np.uint16,5125:np.uint32,5121:np.uint8}[a['componentType']]
    stride = bv.get('byteStride')
    raw = np.frombuffer(bin_, dtype=dt, count=a['count']*nc, offset=st)
    if stride and stride != nc*np.dtype(dt).itemsize:
        raw = np.lib.stride_tricks.as_strided(np.frombuffer(bin_, dtype=np.uint8, offset=st),
            shape=(a['count'], nc), strides=(stride, np.dtype(dt).itemsize)).copy().ravel()
    return raw.reshape(a['count'], nc)

def trs_m(node):
    if 'matrix' in node: return np.array(node['matrix'],dtype=np.float64).reshape(4,4).T
    t=node.get('translation',[0,0,0]); r=node.get('rotation',[0,0,0,1]); s=node.get('scale',[1,1,1])
    x,y,z,w=r
    R=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]],dtype=np.float64)
    M=np.eye(4); M[:3,:3]=R*np.array(s); M[:3,3]=t; return M

for path in sys.argv[1:]:
    g, bin_ = load(path)
    nodes = g['nodes']; parent = {}
    for i, n in enumerate(nodes):
        for c in n.get('children', []): parent[c] = i
    world = {}
    def W(i):
        if i in world: return world[i]
        M = trs_m(nodes[i])
        if i in parent: M = W(parent[i]) @ M
        world[i] = M; return M
    skin = g['skins'][0]
    joints = skin['joints']
    ibm = acc(g, bin_, skin['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1)
    skinm = np.stack([W(ni) @ ibm[k] for k, ni in enumerate(joints)])
    out = []
    for m in g['meshes']:
        for pr in m['primitives']:
            P = acc(g, bin_, pr['attributes']['POSITION']).astype(np.float64)
            if 'JOINTS_0' not in pr['attributes']:
                out.append(P); continue
            J = acc(g, bin_, pr['attributes']['JOINTS_0']).astype(int)
            Wt = acc(g, bin_, pr['attributes']['WEIGHTS_0']).astype(np.float64)
            Jc = np.clip(J, 0, len(joints)-1)
            Ph = np.concatenate([P, np.ones((len(P),1))], axis=1)
            acc_out = np.zeros((len(P),4))
            for k in range(4):
                acc_out += Wt[:,k:k+1] * (Ph @ skinm[Jc[:,k]].transpose(0,2,1)).diagonal(axis1=1,axis2=2) if False else Wt[:,k:k+1] * np.einsum('nij,nj->ni', skinm[Jc[:,k]], Ph)
            out.append(acc_out[:,:3])
    A = np.vstack(out)
    print(f"{path.split('/')[-1]}: skinned Y[{A[:,1].min():.3f},{A[:,1].max():.3f}] X[{A[:,0].min():.3f},{A[:,0].max():.3f}] Z[{A[:,2].min():.3f},{A[:,2].max():.3f}]")

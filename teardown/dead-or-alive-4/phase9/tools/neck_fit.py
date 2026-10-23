#!/usr/bin/env python3
"""Phase 9 Job 1c: neck-fit metric. GLB raw positions are bind-pose world
positions (jointWorld x IBM = I at bind). Body collar radius = max radial
XZ of body verts in the top Y band; head neck-stub radius = max radial XZ
of head verts near its base (local Y in [-0.02, 0.08], excluding the long
hair sheets by also reporting the 90th-percentile radius). Pairing evidence
= closest stub radius to collar radius. Usage: neck_fit.py body.glb head1.glb ..."""
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
    nc = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    dt = {5126:np.float32,5123:np.uint16,5125:np.uint32,5121:np.uint8}[a['componentType']]
    stride = bv.get('byteStride')
    raw = np.frombuffer(bin_, dtype=dt, count=a['count']*nc, offset=st)
    if stride and stride != nc*np.dtype(dt).itemsize:
        raw = np.lib.stride_tricks.as_strided(np.frombuffer(bin_, dtype=np.uint8, offset=st),
            shape=(a['count'], nc), strides=(stride, np.dtype(dt).itemsize)).copy().ravel()
    return raw.reshape(a['count'], nc)

def allpos(path):
    g, bin_ = load(path)
    P = []
    for m in g['meshes']:
        for pr in m['primitives']:
            P.append(acc(g, bin_, pr['attributes']['POSITION']))
    return np.vstack(P)

body = allpos(sys.argv[1])
top = body[body[:,1] > body[:,1].max()-0.04]
collar_r = np.percentile(np.hypot(top[:,0], top[:,2]), 95)
print(f"BODY collar: topY={body[:,1].max():.3f} collar_r95={collar_r:.4f} n_top={len(top)}")
for hp in sys.argv[2:]:
    H = allpos(hp)
    base = H[(H[:,1] > -0.02) & (H[:,1] < 0.08)]
    if len(base) == 0: base = H[H[:,1] < H[:,1].min()+0.05]
    r = np.hypot(base[:,0], base[:,2])
    print(f"{hp.split('/')[-1]}: stub_r95={np.percentile(r,95):.4f} stub_rmax={r.max():.4f} n_base={len(base)} yspan=[{H[:,1].min():.3f},{H[:,1].max():.3f}] diff={abs(np.percentile(r,95)-collar_r):.4f}")

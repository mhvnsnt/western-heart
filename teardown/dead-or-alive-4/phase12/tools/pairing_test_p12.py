#!/usr/bin/env python3
"""Phase 12 Job 2: PROVEN pairing test (phase-11 method) of the 8 unpaired
heads against every chrthree body. A pairing is PROVEN only when the head's
dominant-joint skin bind (inv-IBM translation) matches a body family head
anchor at Delta = 0.000 (phase-11 standard: pkg22 -> (0,0.477,-0.041),
pkg31 -> (0,0.525,-0.025)). Body anchors taken two ways per GLB:
 (i) node world translations in the head band (x~0, 0.35<y<0.80) — the body
     package's own copy of the head node;
 (ii) the body's skin joint binds (inv-IBM translations).
Origin-bound heads (dominant bind == (0,0,0)) carry NO family signal: a
Delta=0 against any body's root joint is vacuous and per phase-11 discipline
does NOT count as proof — reported as UNTESTABLE, never as paired.
"""
import json, struct, os, glob
import numpy as np

def load_glb(path):
    d=open(path,'rb').read()
    jlen=struct.unpack_from('<I', d, 12)[0]
    g=json.loads(d[20:20+jlen]); off=20+jlen
    blen=struct.unpack_from('<I', d, off)[0]
    return g, d[off+8:off+8+blen]

def acc(g, bin_, idx):
    a=g['accessors'][idx]; bv=g['bufferViews'][a['bufferView']]
    start=bv.get('byteOffset',0)+a.get('byteOffset',0)
    ncomp={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
    dt={5126:np.float32,5123:np.uint16,5125:np.uint32,5121:np.uint8}[a['componentType']]
    stride=bv.get('byteStride')
    raw=np.frombuffer(bin_, dtype=dt, offset=start, count=a['count']*ncomp)
    if stride and stride!=ncomp*np.dtype(dt).itemsize:
        raw=np.lib.stride_tricks.as_strided(np.frombuffer(bin_,dtype=np.uint8,offset=start),
            shape=(a['count'],ncomp), strides=(stride,np.dtype(dt).itemsize)).copy().ravel()
    return raw.reshape(a['count'], ncomp)

def node_local(n):
    if 'matrix' in n: return np.array(n['matrix'],dtype=np.float64).reshape(4,4).T
    t=n.get('translation',[0,0,0]); r=n.get('rotation',[0,0,0,1]); s=n.get('scale',[1,1,1])
    x,y,z,w=r
    R=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),0],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),0],
                [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y),0],[0,0,0,1]],dtype=np.float64)
    R[:3,:3]*=np.array(s)[None,:]; R[:3,3]=t; return R

def body_anchors(path):
    g,bin_=load_glb(path)
    nodes=g['nodes']; parent={}
    for i,n in enumerate(nodes):
        for c in n.get('children',[]): parent[c]=i
    world={}
    def W(i):
        if i not in world:
            L=node_local(nodes[i]); world[i]=W(parent[i])@L if i in parent else L
        return world[i]
    node_anchors=[]
    for i,n in enumerate(nodes):
        t=W(i)[:3,3]
        if abs(t[0])<=0.002 and 0.35<t[1]<0.80 and abs(t[2])<=0.08:
            node_anchors.append([round(float(x),4) for x in t])
    joint_binds=[]
    if g.get('skins'):
        sk=g['skins'][0]
        ibm=acc(g,bin_,sk['inverseBindMatrices']).astype(np.float64).reshape(-1,4,4).transpose(0,2,1)
        bind=np.linalg.inv(ibm)
        joint_binds=[[round(float(x),4) for x in bind[k][:3,3]] for k in range(len(sk['joints']))]
    return sorted(set(map(tuple,node_anchors))), joint_binds

hb=json.load(open('/home/hatch/workspace/_doa4p2-scratch/p11/head_bind.json'))
UNPAIRED=['pkg05','pkg06','pkg23','pkg24','pkg26','pkg27','pkg28','pkg32']
heads={h: hb[h]['bind_t'] for h in UNPAIRED}
print("unpaired head dominant binds:", heads)
EXTRACT=sorted(glob.glob('/home/hatch/workspace/_doa4p2-scratch/p12/chrthree/extracted/chrthree-pkg*-skinned.glb'))
print(f"{len(EXTRACT)} chrthree GLBs")
results={}
for p in EXTRACT:
    name=os.path.basename(p).replace('-skinned.glb','')
    na, jb = body_anchors(p)
    row={'node_anchors':[list(a) for a in na]}
    for h,bt in heads.items():
        bt=np.array(bt)
        if np.allclose(bt,[0,0,0]):
            row[h]='UNTESTABLE (bind at origin — no family signal)'
            continue
        cand=[np.array(a) for a in na]+[np.array(b) for b in jb]
        if not cand: row[h]='no anchors'; continue
        dmin=min(float(np.linalg.norm(c-bt)) for c in cand)
        row[h]=round(dmin,4)
    results[name]=row
    testable={h:v for h,v in row.items() if isinstance(v,float)}
    print(name, "anchors:", [list(a) for a in na], "minDelta:", testable)
json.dump(results, open('/home/hatch/workspace/_doa4p2-scratch/p12/pairing_chrthree.json','w'), indent=1)
print("wrote pairing_chrthree.json")
print("PROVEN pairings (Delta<=0.0005, testable heads only):",
      [(b,h,v) for b,r in results.items() for h,v in r.items() if isinstance(v,float) and v<=0.0005])

#!/usr/bin/env python3
"""Phase 9 Job 1a: audit a phase-6 skinned GLB for head geometry.
Reports: node list (skeleton), skin joints, per-mesh POSITION bounds,
and which joints each mesh's JOINTS_0 actually references (max weight
joint set) — specifically whether any vertex is weighted to a head/neck-top
joint and how high (max Y) geometry reaches vs the skeleton's top joint.
Usage: glb_head_audit.py file.glb [file2.glb ...]
"""
import json, struct, sys
import numpy as np

def load_glb(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'glTF'
    jlen = struct.unpack('<I', d[12:16])[0]
    gltf = json.loads(d[20:20+jlen])
    off = 20 + jlen
    blen = struct.unpack('<I', d[off:off+4])[0]
    bin_ = d[off+8:off+8+blen]
    return gltf, bin_

def acc(gltf, bin_, idx):
    a = gltf['accessors'][idx]
    bv = gltf['bufferViews'][a['bufferView']]
    start = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    ncomp = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    dt = {5126:np.float32,5123:np.uint16,5125:np.uint32,5121:np.uint8}[a['componentType']]
    stride = bv.get('byteStride')
    raw = np.frombuffer(bin_, dtype=dt, count=a['count']*ncomp, offset=start)
    if stride and stride != ncomp*np.dtype(dt).itemsize:
        raw = np.lib.stride_tricks.as_strided(
            np.frombuffer(bin_, dtype=np.uint8, offset=start),
            shape=(a['count'], ncomp), strides=(stride, np.dtype(dt).itemsize)).copy().ravel()
    return raw.reshape(a['count'], ncomp)

for path in sys.argv[1:]:
    gltf, bin_ = load_glb(path)
    nodes = gltf.get('nodes', [])
    skins = gltf.get('skins', [])
    print(f"== {path.split('/')[-1]}: nodes={len(nodes)} meshes={len(gltf.get('meshes',[]))} skins={len(skins)}")
    if skins:
        joints = skins[0]['joints']
        print(f"   skin joints={len(joints)}")
        # world Y of each joint from node translations along parent chain (bind pose approx: use translation only)
        names = [nodes[j].get('name','?') for j in joints]
        print("   joint names:", names)
    # geometry bounds overall and per joint usage
    allmax = -1e9; allmin = 1e9
    joint_used = set()
    top_meshes = []
    for mi, mesh in enumerate(gltf.get('meshes', [])):
        for prim in mesh['primitives']:
            pos = acc(gltf, bin_, prim['attributes']['POSITION'])
            allmax = max(allmax, float(pos[:,1].max())); allmin = min(allmin, float(pos[:,1].min()))
            if 'JOINTS_0' in prim['attributes']:
                j = acc(gltf, bin_, prim['attributes']['JOINTS_0'])
                w = acc(gltf, bin_, prim['attributes']['WEIGHTS_0'])
                used = set(int(x) for x in np.unique(j[w > 0.01]))
                joint_used |= used
                top_meshes.append((float(pos[:,1].max()), mi, sorted(used)))
    top_meshes.sort(reverse=True)
    print(f"   geometry Y range: [{allmin:.3f}, {allmax:.3f}]")
    print(f"   joints actually weighted (>0.01): {sorted(joint_used)}")
    print("   top-5 meshes by max Y (maxY, meshIdx, joints):")
    for t in top_meshes[:5]:
        print(f"     {t[0]:.3f} mesh{t[1]} joints={t[2]}")

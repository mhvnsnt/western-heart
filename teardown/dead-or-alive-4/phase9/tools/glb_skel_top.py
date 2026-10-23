#!/usr/bin/env python3
"""Phase 9: compute GLB joint world positions (bind pose, TRS chain) and
report the topmost joints — does the skeleton have a head joint, and where
does it sit vs the geometry top? Usage: glb_skel_top.py file.glb"""
import json, struct, sys
import numpy as np

def load_glb(path):
    d = open(path, 'rb').read()
    jlen = struct.unpack('<I', d[12:16])[0]
    gltf = json.loads(d[20:20+jlen])
    off = 20 + jlen
    blen = struct.unpack('<I', d[off:off+4])[0]
    return gltf, d[off+8:off+8+blen]

def trs_m(node):
    if 'matrix' in node:
        return np.array(node['matrix'], dtype=np.float64).reshape(4,4).T
    t = node.get('translation', [0,0,0]); r = node.get('rotation', [0,0,0,1]); s = node.get('scale', [1,1,1])
    x,y,z,w = r
    R = np.array([
        [1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
        [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
        [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]], dtype=np.float64)
    M = np.eye(4); M[:3,:3] = R * np.array(s); M[:3,3] = t
    return M

path = sys.argv[1]
gltf, bin_ = load_glb(path)
nodes = gltf['nodes']
parent = {}
for i, n in enumerate(nodes):
    for c in n.get('children', []):
        parent[c] = i
world = {}
def get_world(i):
    if i in world: return world[i]
    M = trs_m(nodes[i])
    if i in parent: M = get_world(parent[i]) @ M
    world[i] = M
    return M
joints = gltf['skins'][0]['joints']
rows = []
for ji, ni in enumerate(joints):
    W = get_world(ni)
    rows.append((float(W[1,3]), ji, ni, nodes[ni].get('name','?'), parent.get(ni)))
rows.sort(reverse=True)
print(f"{path.split('/')[-1]}: top joints by world Y:")
for y, ji, ni, nm, par in rows[:10]:
    print(f"  joint{ji} node{ni} ({nm}) Y={y:.3f} parentNode={par}")
print(f"  lowest joint Y={rows[-1][0]:.3f}; total joints={len(rows)}")

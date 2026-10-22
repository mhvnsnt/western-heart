#!/usr/bin/env python3
"""Phase 9 Job 1c: anchor matching. Head packages carry copies of their
owner's neck/head anchor bones at character-space positions in their Hie
skeleton. For each head GLB: anchor = mean of central joints (|x|<0.01)
with Y in [0.35,0.60]. For each body GLB: head joint = max-Y central joint
(|x|<0.01, z<0.05). Match = nearest anchor Y to body head-joint Y.
Usage: anchor_match.py bodies... -- heads..."""
import json, struct, sys
import numpy as np

def load(path):
    d = open(path, 'rb').read()
    jl = struct.unpack('<I', d[12:16])[0]
    return json.loads(d[20:20+jl])

def trs_m(node):
    if 'matrix' in node: return np.array(node['matrix'],dtype=np.float64).reshape(4,4).T
    t=node.get('translation',[0,0,0]); r=node.get('rotation',[0,0,0,1]); s=node.get('scale',[1,1,1])
    x,y,z,w=r
    R=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]],dtype=np.float64)
    M=np.eye(4); M[:3,:3]=R*np.array(s); M[:3,3]=t; return M

def joint_pos(path):
    g = load(path); nodes = g['nodes']; parent = {}
    for i, n in enumerate(nodes):
        for c in n.get('children', []): parent[c] = i
    world = {}
    def W(i):
        if i in world: return world[i]
        M = trs_m(nodes[i])
        if i in parent: M = W(parent[i]) @ M
        world[i] = M; return M
    return np.array([W(ni)[:3,3] for ni in g['skins'][0]['joints']])

sep = sys.argv.index('--')
bodies, heads = sys.argv[1:sep], sys.argv[sep+1:]
B = {}
for bp in bodies:
    J = joint_pos(bp)
    cen = J[(np.abs(J[:,0]) < 0.01) & (J[:,2] < 0.05)]
    B[bp.split('/')[-1]] = float(cen[:,1].max())
H = {}
for hp in heads:
    J = joint_pos(hp)
    cen = J[(np.abs(J[:,0]) < 0.01) & (J[:,1] > 0.35) & (J[:,1] < 0.60)]
    H[hp.split('/')[-1]] = float(cen[:,1].mean()) if len(cen) else float('nan')
print("BODY head-joint Y:")
for k, v in sorted(B.items(), key=lambda kv: kv[1]): print(f"  {k}: {v:.3f}")
print("HEAD anchor Y -> nearest bodies:")
for k, v in sorted(H.items(), key=lambda kv: kv[1]):
    near = sorted(B.items(), key=lambda kv: abs(kv[1]-v))[:3]
    print(f"  {k}: {v:.3f} -> " + ", ".join(f"{n}({abs(bv-v):.3f})" for n, bv in near))

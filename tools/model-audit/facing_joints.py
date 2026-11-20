"""Facing from joint layout

Toe direction, arm X sign and hand/head vertex offsets per model (mixamorig naming).
Usage: python3 tools/model-audit/facing_joints.py MODEL.glb [...]

Part of the 2026-10-20/21 Claude combat-animation audit (see tools/TOOLS-INDEX.md and
docs/handoffs/CLAUDE_TO_MUSE_FIXES_2026-10-20.md). Read-only: never writes to the models.
"""
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
import json,struct,sys,os,re
import numpy as np
sys.path.insert(0,str(REPO/'tools/anim'))
from t3_bank_skeleton import read_glb, accessor
def qm(q):
    x,y,z,w=q
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def analyze(path):
    from pathlib import Path
    j,blob=read_glb(Path(path)); N=j['nodes']
    par={c:i for i,nd in enumerate(N) for c in nd.get('children',[])}
    def local(i):
        nd=N[i]; M=np.eye(4); M[:3,:3]=qm(nd.get('rotation',[0,0,0,1]))@np.diag(nd.get('scale',[1,1,1])); M[:3,3]=nd.get('translation',[0,0,0]); return M
    def world(i): return (world(par[i]) if i in par else np.eye(4))@local(i)
    sk=j['skins'][0]; names=[re.sub(r'^mixamorig:?','',N[i]['name']) for i in sk['joints']]
    W={names[k]:world(i) for k,i in enumerate(sk['joints'])}
    P={k:v[:3,3] for k,v in W.items()}
    out={}
    for s in ['Left','Right']:
        if s+'Foot' in P and s+'ToeBase' in P: out[s+'toe_dir']=np.round(P[s+'ToeBase']-P[s+'Foot'],3).tolist()
    out['LeftArm_x']=round(float(P['LeftArm'][0]),3); out['RightArm_x']=round(float(P['RightArm'][0]),3)
    # mesh: where are vertices skinned to LeftArm/LeftHand (dominant)? in bind space via IBM
    ibm=accessor(j,blob,sk['inverseBindMatrices']).astype(float).reshape(-1,4,4).transpose(0,2,1)
    li=names.index('LeftHand'); ri=names.index('RightHand'); hi=names.index('Head')
    cen={}
    for m in j['meshes']:
        for pr in m['primitives']:
            at=pr['attributes']
            if 'JOINTS_0' not in at: continue
            pos=accessor(j,blob,at['POSITION']).astype(float); jt=accessor(j,blob,at['JOINTS_0']).astype(int); wt=accessor(j,blob,at['WEIGHTS_0']).astype(float)
            dom=jt[np.arange(len(jt)),wt.argmax(1)]
            for nm,idx in [('LeftHand',li),('RightHand',ri),('Head',hi)]:
                sel=dom==idx
                if sel.any(): cen.setdefault(nm,[]).append(pos[sel])
    # mesh positions are in mesh-node space; bind world of joint = inv(ibm) -> compare joint bind pos vs its vertex centroid in same (mesh) space
    for nm,idx in [('LeftHand',li),('RightHand',ri),('Head',hi)]:
        if nm in cen:
            c=np.concatenate(cen[nm]).mean(0); jb=np.linalg.inv(ibm[idx])[:3,3]
            out[nm+'_verts_vs_joint']=np.round(c-jb,3).tolist(); out[nm+'_bindpos']=np.round(jb,3).tolist()
    # head verts: face direction ~ head verts centroid offset z relative to joint
    return out
for p in sys.argv[1:]:
    print(p.split('/')[-1], analyze(p))

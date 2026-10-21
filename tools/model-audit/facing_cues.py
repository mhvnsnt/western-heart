"""Facing cues from skinned vertices

Head / thumb / torso vertex-centroid offsets relative to their joints in bind space - which
way the face and chest point. One of the cues behind game/assets/models/model-facing.json
(final facing decided from rest renders that were viewed).
Usage: python3 tools/model-audit/facing_cues.py MODEL.glb [...]

Part of the 2026-10-20/21 Claude combat-animation audit (see tools/TOOLS-INDEX.md and
docs/handoffs/CLAUDE_TO_MUSE_FIXES_2026-10-20.md). Read-only: never writes to the models.
"""
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
import json,sys,re,os
import numpy as np
from pathlib import Path
sys.path.insert(0,str(REPO/'tools/anim'))
from t3_bank_skeleton import read_glb, accessor
def canon(n):
    return re.sub(r'_\d+$','',re.sub(r'^mixamorig:?','',n))
def run(path):
    j,blob=read_glb(Path(path)); N=j['nodes']; sk=j['skins'][0]
    names=[canon(N[i]['name']) for i in sk['joints']]
    idx={n:k for k,n in enumerate(names)}
    ibm=accessor(j,blob,sk['inverseBindMatrices']).astype(float).reshape(-1,4,4).transpose(0,2,1)
    B=[np.linalg.inv(m)[:3,3] for m in ibm]
    V={}
    for m in j['meshes']:
        for pr in m['primitives']:
            at=pr['attributes']
            if 'JOINTS_0' not in at: continue
            pos=accessor(j,blob,at['POSITION']).astype(float); jt=accessor(j,blob,at['JOINTS_0']).astype(int); wt=accessor(j,blob,at['WEIGHTS_0']).astype(float)
            dom=jt[np.arange(len(jt)),wt.argmax(1)]
            for k in set(dom.tolist()):
                V.setdefault(k,[]).append(pos[dom==k])
    V={k:np.concatenate(v) for k,v in V.items()}
    out={}
    h=idx.get('Head')
    if h in V:
        hv=V[h]; out['head_cent_dz']=round(float(hv[:,2].mean()-B[h][2]),3); out['head_zmax']=round(float(hv[:,2].max()-B[h][2]),3); out['head_zmin']=round(float(hv[:,2].min()-B[h][2]),3)
    for s in ['Left']:
        t=idx.get(s+'HandThumb1'); hd=idx.get(s+'Hand')
        if t is not None and hd is not None: out['thumb_dz']=round(float(B[t][2]-B[hd][2]),3)
    # all mesh verts: bounding center z vs hips z
    allv=np.concatenate(list(V.values()))
    out['all_cz_minus_hips']=round(float(allv[:,2].mean()-B[idx['Hips']][2]),3)
    # chest: verts dominated by spine bones
    sp=[idx[n] for n in ['Spine','Spine1','Spine2'] if n in idx and idx[n] in V]
    if sp:
        cv=np.concatenate([V[k] for k in sp]); jz=np.mean([B[k][2] for k in sp]); out['torso_dz']=round(float(cv[:,2].mean()-jz),3)
    return out
for p in sys.argv[1:]:
    print(p.split('/')[-1], run(p))

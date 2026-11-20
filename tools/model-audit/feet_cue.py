"""Foot-direction facing cue

Foot->toe direction per side for each rig (first pass).
Usage: python3 tools/model-audit/feet_cue.py MODEL.glb [...]

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
    n=re.sub(r'^mixamorig:?','',n); n2=re.sub(r'_\d+$','',n)
    m=re.match(r'^Bip0*1 (L|R) Foot$',n2)
    if m: return ('Left' if m[1]=='L' else 'Right')+'Foot'
    m=re.match(r'^(L|R)_Foot$',n2)
    if m: return ('Left' if m[1]=='L' else 'Right')+'Foot'
    return n2
def run(path):
    j,blob=read_glb(Path(path)); N=j['nodes']; sk=j['skins'][0]
    names=[canon(N[i]['name']) for i in sk['joints']]; idx={n:k for k,n in enumerate(names)}
    ibm=accessor(j,blob,sk['inverseBindMatrices']).astype(float).reshape(-1,4,4).transpose(0,2,1)
    B=[np.linalg.inv(m)[:3,3] for m in ibm]
    P=[]
    for m in j['meshes']:
        for pr in m['primitives']:
            at=pr['attributes']
            if 'JOINTS_0' in at: P.append(accessor(j,blob,at['POSITION']).astype(float))
    P=np.concatenate(P)
    y0,y1=P[:,1].min(),P[:,1].max(); hgt=y1-y0
    low=P[P[:,1]<y0+0.06*hgt]
    res=[]
    for s in ['Left','Right']:
        a=B[idx[s+'Foot']]
        near=low[np.abs(low[:,0]-a[0])<0.12*hgt]
        if len(near)<10: continue
        fwd=near[:,2].max()-a[2]; back=a[2]-near[:,2].min()
        res.append((round(float(fwd),3),round(float(back),3)))
    score=sum(f-b for f,b in res)
    return f"feet(+z ext, -z ext)={res} => mesh faces {'+Z' if score>0.02 else ('-Z' if score<-0.02 else '??')}"
for p in sys.argv[1:]:
    try: print(f"{p.split('/')[-1][:34]:34s}", run(p))
    except Exception as e: print(p, 'ERR', e)

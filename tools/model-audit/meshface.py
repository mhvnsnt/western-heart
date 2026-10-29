"""Mesh facing from vertex distribution

Front/back asymmetry of the skinned mesh around the foot/arm joints (canonical names for
Mixamo, Bip01 and L_/R_ rigs).
Usage: python3 tools/model-audit/meshface.py MODEL.glb [...]

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
R=str(REPO)+'/'
def canon(n):
    n=re.sub(r'^mixamorig:?','',n); n=re.sub(r'_\d+$','',n)
    m=re.match(r'^Bip0*1 (L|R) (Foot|Toe0|UpperArm)$',n)
    if m: return ('Left' if m[1]=='L' else 'Right')+{'Foot':'Foot','Toe0':'ToeBase','UpperArm':'Arm'}[m[2]]
    m=re.match(r'^(L|R)_(Foot|Toe|Arm)$',n)
    if m: return ('Left' if m[1]=='L' else 'Right')+{'Foot':'Foot','Toe':'ToeBase','Arm':'Arm'}[m[2]]
    return n
def run(path):
    j,blob=read_glb(Path(path)); N=j['nodes']; sk=j['skins'][0]
    names=[canon(N[i]['name']) for i in sk['joints']]
    ibm=accessor(j,blob,sk['inverseBindMatrices']).astype(float).reshape(-1,4,4).transpose(0,2,1)
    bind=[np.linalg.inv(m) for m in ibm]
    idx={n:k for k,n in enumerate(names)}
    need=['LeftFoot','RightFoot','LeftArm','RightArm']
    if any(n not in idx for n in need): return 'missing bones'
    acc={'Left':[], 'Right':[]}
    for m in j['meshes']:
        for pr in m['primitives']:
            at=pr['attributes']
            if 'JOINTS_0' not in at: continue
            pos=accessor(j,blob,at['POSITION']).astype(float); jt=accessor(j,blob,at['JOINTS_0']).astype(int); wt=accessor(j,blob,at['WEIGHTS_0']).astype(float)
            dom=jt[np.arange(len(jt)),wt.argmax(1)]
            for s in ['Left','Right']:
                ids=[idx[s+'Foot']]+([idx[s+'ToeBase']] if s+'ToeBase' in idx else [])
                sel=np.isin(dom,ids)
                if sel.any(): acc[s].append(pos[sel])
    f=np.zeros(3)
    for s in ['Left','Right']:
        if acc[s]:
            c=np.concatenate(acc[s]).mean(0); f+=c-bind[idx[s+'Foot']][:3,3]
    f[1]=0; f/=np.linalg.norm(f)+1e-9
    left=np.cross([0,1,0],f)  # character left for forward f (Y up): f=+Z -> left=+X
    lr=bind[idx['LeftArm']][:3,3]-bind[idx['RightArm']][:3,3]
    toe = (bind[idx['LeftToeBase']][:3,3]-bind[idx['LeftFoot']][:3,3]) if 'LeftToeBase' in idx else None
    return f"mesh_fwd={np.round(f,2).tolist()} names_ok={'YES' if np.dot(lr,left)>0 else 'SWAPPED'} toejoint_z={None if toe is None else round(float(toe[2]),3)}"
src=open(R+'game/js/assets.js').read()
urls=dict(re.findall(r"^\s*'?([\w-]+)'?\s*:\s*'([^']+\.glb)'", src, re.M))
for m,u in list(urls.items()):
    p=os.path.normpath(R+'game/'+u)
    if not os.path.exists(p): continue
    b=open(p,'rb').read(20); 
    try:
        j,_=read_glb(Path(p))
        if not j.get('skins'): continue
        print(f"{m:26s}", run(p))
    except Exception as e: print(m,'ERR',e)
for p in ['lab/game/assets/pantera_leoman_t3real.glb',str(REPO/'lab/game/assets/t3_jin_t3real.glb')]:
    print(p.split('/')[-1], run(R+p))

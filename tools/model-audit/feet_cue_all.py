"""Foot-direction facing cue, all roster models

Second pass of feet_cue over every model URL in game/js/assets.js, Mixamo / Biped / L_R_
naming; this is the same cue assets.js feetFacingCue() uses as a fallback (|score| >= 0.05).
Usage: python3 tools/model-audit/feet_cue_all.py

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
VIS_NEG={'mariposa','mariposa-monarch','saku-ra-main','cape-jones','kiko-tanaka','kiko-tanaka_alt1','purple-rain-main','custom'}
def qm(q):
    x,y,z,w=q
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def canonFoot(n):
    n=re.sub(r'^mixamorig:?','',n); n2=re.sub(r'_\d+$','',n)
    for pat,side in [(r'^Bip0*1 (L|R) Foot$',None),(r'^(L|R)_Foot$',None)]:
        m=re.match(pat,n2)
        if m: return ('Left' if m[1]=='L' else 'Right')+'Foot'
    return n2
def world_verts(j,blob):
    N=j['nodes']; par={c:i for i,nd in enumerate(N) for c in nd.get('children',[])}
    def local(i):
        nd=N[i]; M=np.eye(4)
        if 'matrix' in nd: return np.array(nd['matrix']).reshape(4,4).T
        M[:3,:3]=qm(nd.get('rotation',[0,0,0,1]))@np.diag(nd.get('scale',[1,1,1])); M[:3,3]=nd.get('translation',[0,0,0]); return M
    def world(i): return (world(par[i]) if i in par else np.eye(4))@local(i)
    P=[]
    for i,nd in enumerate(N):
        if 'mesh' not in nd or 'skin' not in nd: continue
        for pr in j['meshes'][nd['mesh']]['primitives']:
            if 'JOINTS_0' not in pr['attributes']: continue
            p=accessor(j,blob,pr['attributes']['POSITION']).astype(float)
            P.append(p)  # skinned verts are in bind space = skeleton world (approx)
    return np.concatenate(P)
def run(path):
    j,blob=read_glb(Path(path)); N=j['nodes']; sk=j['skins'][0]
    names=[canonFoot(N[i]['name']) for i in sk['joints']]; idx={n:k for k,n in enumerate(names)}
    ibm=accessor(j,blob,sk['inverseBindMatrices']).astype(float).reshape(-1,4,4).transpose(0,2,1)
    B=[np.linalg.inv(m)[:3,3] for m in ibm]
    P=world_verts(j,blob)
    y0,y1=P[:,1].min(),P[:,1].max(); hgt=y1-y0
    low=P[P[:,1]<y0+0.05*hgt]
    sc=0; ok=0
    for s in ['Left','Right']:
        if s+'Foot' not in idx: continue
        a=B[idx[s+'Foot']]
        near=low[np.abs(low[:,0]-a[0])<0.06*hgt]
        if len(near)<10: continue
        fwd=np.percentile(near[:,2],99)-a[2]; back=a[2]-np.percentile(near[:,2],1)
        sc+= (fwd-back)/hgt; ok+=1
    return sc, ok, hgt
src=open(R+'game/js/assets.js').read()
urls=dict(re.findall(r"^\s*'?([\w-]+)'?\s*:\s*'([^']+\.glb)'", src, re.M))
ms=json.load(open(sys.argv[1] if len(sys.argv) > 1 else str(REPO/'tools/model-audit/data/skinned.json')))
bad=0
for m in ms:
    try: sc,ok,h=run(os.path.normpath(R+'game/'+urls[m]))
    except Exception as e: print(m,'ERR',e); continue
    pred='-Z' if sc< -0.01 else ('+Z' if sc>0.01 else '??')
    vis='-Z' if m in VIS_NEG else '+Z'
    flag='' if pred==vis else '  <-- MISMATCH'
    if flag: bad+=1
    print(f"{m:26s} score={sc:+.3f} feet={ok} h={h:.2f} pred={pred} visual={vis}{flag}")
print('mismatches',bad)

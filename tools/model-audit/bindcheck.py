"""Bind-pose vs node-rest check

For every skinned roster model: distance between each joint node's rest world position and
the position its inverse bind matrix expects. >5 cm means the mesh will jump/distort at rest.
Usage: python3 tools/model-audit/bindcheck.py [models.json]

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
def qm(q):
    x,y,z,w=q
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def run(p):
    j,blob=read_glb(Path(p)); N=j['nodes']; sk=j['skins'][0]
    par={c:i for i,nd in enumerate(N) for c in nd.get('children',[])}
    def local(i):
        nd=N[i]
        if 'matrix' in nd: return np.array(nd['matrix']).reshape(4,4).T
        M=np.eye(4); M[:3,:3]=qm(nd.get('rotation',[0,0,0,1]))@np.diag(nd.get('scale',[1,1,1])); M[:3,3]=nd.get('translation',[0,0,0]); return M
    def world(i): return (world(par[i]) if i in par else np.eye(4))@local(i)
    ibm=accessor(j,blob,sk['inverseBindMatrices']).astype(float).reshape(-1,4,4).transpose(0,2,1)
    # mesh node using the skin: its world matrix maps bind space
    meshnode=[i for i,nd in enumerate(N) if nd.get('skin')==0][0]
    Mw=world(meshnode)
    errs=[]
    for k,i in enumerate(sk['joints']):
        node_w=world(i)[:3,3]
        bind_w=(Mw@np.linalg.inv(ibm[k]))[:3,3]   # where the joint must be for the mesh to sit at rest
        errs.append(np.linalg.norm(node_w-bind_w))
    hips=[k for k,i in enumerate(sk['joints']) if re.sub(r'^mixamorig:?','',N[i]['name'])=='Hips']
    h=hips[0] if hips else 0
    return max(errs), float(np.median(errs)), (Mw@np.linalg.inv(ibm[h]))[:3,3].round(3).tolist(), world(sk['joints'][h])[:3,3].round(3).tolist()
src=open(R+'game/js/assets.js').read()
urls=dict(re.findall(r"^\s*'?([\w-]+)'?\s*:\s*'([^']+\.glb)'", src, re.M))
ms=json.load(open(sys.argv[1] if len(sys.argv) > 1 else str(REPO/'tools/model-audit/data/skinned.json')))
for m in ms:
    try:
        mx,md,hb,hn=run(os.path.normpath(R+'game/'+urls[m]))
        flag='  <-- node rest != bind' if mx>0.05 else ''
        print(f"{m:24s} max|node-bind|={mx:.3f} median={md:.3f} hips bind={hb} node={hn}{flag}")
    except Exception as e: print(m,'ERR',e)

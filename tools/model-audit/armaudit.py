"""Arm-region weight audit

Counts vertices far out along the T/A-pose arms whose DOMINANT bone is not an arm bone
(e.g. a shirt weighted to the spine -> sleeves stay frozen). This found the steve-fox/demonio
`ModelShirt` defect fixed by tools/anim/repair_sleeve_weights.py.
Usage: python3 tools/model-audit/armaudit.py [models.json]   (default data/skinned.json)

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
ARM=re.compile(r'(Shoulder|Arm|ForeArm|Hand|Thumb|Index|Middle|Ring|Pinky|Finger|Clavicle|UpperArm|Forearm|Elbow|Wrist)', re.I)
def run(path):
    j,blob=read_glb(Path(path)); N=j['nodes']; sk=j['skins'][0]
    names=[N[i]['name'] for i in sk['joints']]
    ibm=accessor(j,blob,sk['inverseBindMatrices']).astype(float).reshape(-1,4,4).transpose(0,2,1)
    B=np.array([np.linalg.inv(m)[:3,3] for m in ibm])
    # arm span: x of hand joints
    hand=[k for k,n in enumerate(names) if re.search(r'(Left|Right|L_|R_|L |R )Hand$|Hand_\d+$',re.sub(r'^mixamorig:?','',n))]
    if not hand: return None
    span=np.abs(B[hand,0]).max()
    bad=tot=0; worst=[]
    for mi,m in enumerate(j['meshes']):
        for pi,pr in enumerate(m['primitives']):
            at=pr['attributes']
            if 'JOINTS_0' not in at: continue
            pos=accessor(j,blob,at['POSITION']).astype(float); jt=accessor(j,blob,at['JOINTS_0']).astype(int); wt=accessor(j,blob,at['WEIGHTS_0']).astype(float)
            sel=np.abs(pos[:,0])>0.45*span   # well out along a T/A-pose arm
            if not sel.any(): continue
            dom=jt[np.arange(len(jt)),wt.argmax(1)][sel]
            nb=sum(1 for d in dom if not ARM.search(names[d]))
            bad+=nb; tot+=int(sel.sum())
            if nb>20: worst.append((m.get('name'),pi,nb,int(sel.sum())))
    return bad,tot,worst
src=open(R+'game/js/assets.js').read()
urls=dict(re.findall(r"^\s*'?([\w-]+)'?\s*:\s*'([^']+\.glb)'", src, re.M))
ms=json.load(open(sys.argv[1] if len(sys.argv) > 1 else str(REPO/'tools/model-audit/data/skinned.json')))
for m in ms:
    try: r=run(os.path.normpath(R+'game/'+urls[m]))
    except Exception as e: print(m,'ERR',e); continue
    if r is None: print(f'{m:24s} no hand bones'); continue
    bad,tot,worst=r
    print(f"{m:24s} arm-region verts on non-arm bones: {bad}/{tot} ({100*bad/max(tot,1):.0f}%) {worst[:3] if bad>50 else ''}")

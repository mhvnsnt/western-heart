"""Roster rig audit

Every model referenced by game/js/roster-full.js + assets.js: skinned or not, joint count,
chest bone, missing humanoid joints. Produced data/skinned.json / data/statics.json (the list
of unrigged Tripo statics that need GameRig).
Usage: python3 tools/model-audit/rigaudit.py

Part of the 2026-10-20/21 Claude combat-animation audit (see tools/TOOLS-INDEX.md and
docs/handoffs/CLAUDE_TO_MUSE_FIXES_2026-10-20.md). Read-only: never writes to the models.
"""
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
import json, re, struct, sys, os
R=str(REPO)
src=open(R+'/game/js/assets.js').read()
urls=dict(re.findall(r"^\s*'?([\w-]+)'?\s*:\s*'([^']+\.glb)'", src, re.M))
roster=open(R+'/game/js/roster-full.js').read()
rmodels=re.findall(r"id: '([^']+)'.*?model: '([^']+)'", roster)
def info(path):
    p=os.path.normpath(os.path.join(R,'game',path))
    if not os.path.exists(p): return 'MISSING FILE'
    b=open(p,'rb').read(32*1024*1024)
    if b[:4]!=b'glTF': return 'not glb'
    n=struct.unpack('<I',b[12:16])[0]; j=json.loads(b[20:20+n])
    skins=j.get('skins',[])
    if not skins: return f"UNSKINNED meshes={len(j.get('meshes',[]))}"
    N=j['nodes']; names=[N[i].get('name','') for i in skins[0]['joints']]
    st=[re.sub(r'^mixamorig:?','',x) for x in names]
    need=['Hips','Spine','Head','LeftArm','LeftForeArm','LeftHand','RightArm','RightForeArm','RightHand','LeftUpLeg','LeftLeg','LeftFoot','RightUpLeg','RightLeg','RightFoot']
    miss=[x for x in need if x not in st]
    chest='Spine2' if 'Spine2' in st else ('Chest' if 'Chest' in st else ('Spine1' if 'Spine1' in st else '-'))
    pref='mixamorig' if any(x.startswith('mixamorig') for x in names) else ''
    return f"skinned joints={len(names)} chest={chest} {pref} miss={miss}"
seen={}
for fid,m in rmodels:
    seen.setdefault(m,[]).append(fid)
for m,fids in seen.items():
    print(f"{m:28s} {','.join(fids)[:40]:40s} {info(urls.get(m,'??')) if m in urls else 'NO URL'}")
print('---- all attire models')
for m,u in urls.items():
    if m not in seen: print(f"{m:28s} {'':40s} {info(u)}")

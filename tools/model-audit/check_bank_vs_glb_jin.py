"""Bank clip vs source GLB (Jin)

First check that game/assets/anim/t3/jin clips equal the t3_jin_t3real.glb animation channels
(superseded by tools/anim/t3_bank_skeleton.py --check).

Part of the 2026-10-20/21 Claude combat-animation audit (see tools/TOOLS-INDEX.md and
docs/handoffs/CLAUDE_TO_MUSE_FIXES_2026-10-20.md). Read-only: never writes to the models.
"""
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
import json, sys, numpy as np, pygltflib
from scipy.spatial.transform import Rotation as R
g = pygltflib.GLTF2().load(str(REPO/'lab/game/assets/t3_jin_t3real.glb'))
blob = g.binary_blob()
def acc(i):
    a=g.accessors[i]; bv=g.bufferViews[a.bufferView]
    n={'SCALAR':1,'VEC3':3,'VEC4':4}[a.type]
    o=(bv.byteOffset or 0)+(a.byteOffset or 0)
    return np.frombuffer(blob[o:o+a.count*n*4],np.float32).reshape(a.count,n)
an=[a for a in g.animations if a.name=='t3_stance'][0]
tr={}
for ch in an.channels:
    s=an.samplers[ch.sampler]; tr[(g.nodes[ch.target.node].name,ch.target.path)]=acc(s.output)
print(sorted(tr.keys()))
d=json.load(open('game/assets/anim/t3/jin/t3_stance.json'))
q=lambda b,f: R.from_quat(d['rot_xyzw'][b][f])
f=10
for b in ['Hips','Chest','Head','LeftArm','LeftForeArm','RightUpLeg']:
    print(b,'glb',np.round(tr[(b,'rotation')][f],4),'json',np.round(d['rot_xyzw'][b][f],4))
# canonical chain compose
Gc = q('Root',f)*q('Hips',f)*q('Spine',f)*q('Chest',f)
print('json canonical G(Chest)', np.round(Gc.as_quat(),4), ' glb Chest(world)', np.round(tr[('Chest','rotation')][f],4))
Gh = Gc*q('Neck',f)*q('Head',f)
print('json canonical G(Head)', np.round(Gh.as_quat(),4), ' glb Chest*Head', np.round((R.from_quat(tr[('Chest','rotation')][f])*R.from_quat(tr[('Head','rotation')][f])).as_quat(),4))
print('root_t glb', tr.get(('Root','translation'),[None]*20)[f], 'json', d['root_t'][f])

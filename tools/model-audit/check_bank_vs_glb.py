"""Bank clip vs source GLB

Quaternion + root translation mismatch between a bank folder's t3_*.json clips and the GLB
they were exported from.
Usage: python3 tools/model-audit/check_bank_vs_glb.py SOURCE.glb game/assets/anim/t3/<bank>

Part of the 2026-10-20/21 Claude combat-animation audit (see tools/TOOLS-INDEX.md and
docs/handoffs/CLAUDE_TO_MUSE_FIXES_2026-10-20.md). Read-only: never writes to the models.
"""
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
import json, sys, numpy as np, pygltflib
glb, bankdir = sys.argv[1], sys.argv[2]
g = pygltflib.GLTF2().load(glb); blob = g.binary_blob()
def acc(i):
    a=g.accessors[i]; bv=g.bufferViews[a.bufferView]; n={'SCALAR':1,'VEC3':3,'VEC4':4}[a.type]
    o=(bv.byteOffset or 0)+(a.byteOffset or 0); return np.frombuffer(blob[o:o+a.count*n*4],np.float32).reshape(a.count,n)
for clip in ['t3_stance','t3_light','t3_ko']:
    an=[a for a in g.animations if a.name==clip]
    if not an: print(clip,'not in glb'); continue
    an=an[0]; tr={(g.nodes[c.target.node].name,c.target.path):acc(an.samplers[c.sampler].output) for c in an.channels}
    d=json.load(open(f'{bankdir}/{clip}.json'))
    err=0; n=0
    for b,arr in d['rot_xyzw'].items():
        if (b,'rotation') in tr:
            A=np.array(arr); B=tr[(b,'rotation')]
            m=min(len(A),len(B)); err=max(err, np.abs(np.abs((A[:m]*B[:m]).sum(1))-1).max()); n+=1
    rt=np.array(d['root_t']); RT=tr.get(('Root','translation'))
    print(clip, 'bones compared', n, 'max quat mismatch', round(float(err),6), 'root_t diff', None if RT is None else round(float(np.abs(rt[:len(RT)]-RT[:len(rt)]).max()),4), 'frames json/glb', len(rt), None if RT is None else len(RT))

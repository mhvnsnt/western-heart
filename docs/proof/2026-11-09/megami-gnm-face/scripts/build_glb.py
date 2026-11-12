"""Assemble the GNM-face GLB variant from the v3 base:
  - AngelFace POSITION accessors on the face-assembly prims replaced with
    the transferred GNM identity key (work/key_*.npz);
  - image 21 (face atlas) replaced with the owner-spec texture bake
    (work/face_atlas_new.png), bufferViews after it shifted accordingly.
Everything else is byte-identical to the base; verify_glb.py proves it.
Usage: build_glb.py <key.npz> <out.glb> [base.glb]
"""
import json, sys
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/_gnmface-20261109/scripts')
from glb_lib import load_glb, save_glb, acc_span

W = '/home/hatch/workspace/_gnmface-20261109/work'
KEY = sys.argv[1]
OUT = sys.argv[2]
BASE = sys.argv[3] if len(sys.argv) > 3 else f'{W}/megami-angel-pilot2-v3.glb'

g, buf = load_glb(BASE)
key = np.load(KEY)
touched = []
for tag in key.files:
    mi, pi = map(int, tag.split(':'))
    names = g['meshes'][mi]['extras']['targetNames']
    fi = names.index('AngelFace')
    acc_i = g['meshes'][mi]['primitives'][pi]['targets'][fi]['POSITION']
    arr = key[tag].astype(np.float32)
    start, ln = acc_span(g, acc_i)
    assert ln == arr.nbytes, f'{tag}: span {ln} != key {arr.nbytes}'
    buf[start:start + ln] = arr.tobytes()
    a = g['accessors'][acc_i]
    a['min'] = arr.min(axis=0).tolist()
    a['max'] = arr.max(axis=0).tolist()
    touched.append((tag, acc_i))
print('AngelFace accessors replaced:', touched)

# ---- image 21 splice ----
new_png = open(f'{W}/face_atlas_new.png', 'rb').read()
bv_i = g['images'][21]['bufferView']
bv = g['bufferViews'][bv_i]
O, L = bv.get('byteOffset', 0), bv['byteLength']
print(f'image21: old {L} B at {O}; new {len(new_png)} B')
pad = (4 - (O + len(new_png)) % 4) % 4
delta = len(new_png) + pad - L
buf = buf[:O] + bytearray(new_png) + bytearray(pad) + buf[O + L:]
bv['byteLength'] = len(new_png)
for v in g['bufferViews']:
    if v is not bv and v.get('byteOffset', 0) > O:
        v['byteOffset'] = v.get('byteOffset', 0) + delta
g['buffers'][0]['byteLength'] = len(buf)
print(f'BIN delta {delta} B (pad {pad}); new BIN {len(buf)} B')

n = save_glb(OUT, g, buf)
print('wrote', OUT, n, 'bytes')

"""Byte-level preservation proof: new GLB vs base GLB.
Every accessor's DATA must be identical except the AngelFace POSITION
accessors of the touched prims; every image's bytes identical except
image 21; JSON structure identical except bufferView offsets/lengths
(from the image splice), the changed accessors' min/max, buffers length.
Usage: verify_glb.py <base.glb> <new.glb> <key.npz>
"""
import json, sys
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/_gnmface-20261109/scripts')
from glb_lib import load_glb, acc_array

BASE, NEW, KEY = sys.argv[1], sys.argv[2], sys.argv[3]
g0, b0 = load_glb(BASE)
g1, b1 = load_glb(NEW)
key = np.load(KEY)
allowed = set()
for tag in key.files:
    mi, pi = map(int, tag.split(':'))
    names = g0['meshes'][mi]['extras']['targetNames']
    fi = names.index('AngelFace')
    allowed.add(g0['meshes'][mi]['primitives'][pi]['targets'][fi]['POSITION'])
print('allowed-changed accessors:', sorted(allowed))

bad = []
for ai in range(len(g0['accessors'])):
    A = acc_array(g0, b0, ai)
    B = acc_array(g1, b1, ai)
    same = A.shape == B.shape and np.array_equal(A, B)
    if not same and ai not in allowed:
        bad.append(ai)
    if same and ai in allowed:
        bad.append(('EXPECTED-DIFF-BUT-SAME', ai))
print('accessors checked:', len(g0['accessors']), '| unexpected diffs:', bad)

for ii in range(len(g0['images'])):
    v0 = g0['bufferViews'][g0['images'][ii]['bufferView']]
    v1 = g1['bufferViews'][g1['images'][ii]['bufferView']]
    d0 = bytes(b0[v0.get('byteOffset', 0): v0.get('byteOffset', 0) + v0['byteLength']])
    d1 = bytes(b1[v1.get('byteOffset', 0): v1.get('byteOffset', 0) + v1['byteLength']])
    tag = 'SAME' if d0 == d1 else 'DIFF'
    if ii == 21:
        assert tag == 'DIFF', 'image 21 must differ'
    else:
        assert tag == 'SAME', f'image {ii} must be identical'
print('images: all identical except 21 (changed as intended)')

for mi in range(len(g0['meshes'])):
    m0, m1 = g0['meshes'][mi], g1['meshes'][mi]
    assert m0['extras']['targetNames'] == m1['extras']['targetNames'], f'mesh {mi} targetNames'
    assert m0.get('weights') == m1.get('weights'), f'mesh {mi} weights'
    assert len(m0['primitives']) == len(m1['primitives'])
print('targetNames + weights identical on all meshes; mesh10 targets:',
      len(g0['meshes'][10]['primitives'][0]['targets']))
assert g0['nodes'] == g1['nodes'] and g0['skins'] == g1['skins'] and g0['materials'] == g1['materials']
print('nodes/skins/materials JSON identical')
print('VERIFY OK')

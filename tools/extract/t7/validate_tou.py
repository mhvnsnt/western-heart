#!/usr/bin/env python3
"""Validate tou-body.glb: structure, skin integrity, canonical bones, bounds."""
import json, struct, sys
import numpy as np

def load(p):
    d = open(p, 'rb').read()
    assert d[:4] == b'glTF', 'bad magic'
    ln = struct.unpack('<I', d[12:16])[0]
    return json.loads(d[20:20+ln]), d

def acc_data(g, blob, ai):
    a = g['accessors'][ai]
    bv = g['bufferViews'][a['bufferView']]
    bin_off = 12 + 8 + struct.unpack('<I', blob[12:16])[0] + 8
    off = bin_off + (bv.get('byteOffset', 0)) + (a.get('byteOffset', 0))
    ncomp = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[a['type']]
    dt = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8}[a['componentType']]
    return np.frombuffer(blob, dtype=dt, count=a['count'] * ncomp, offset=off).reshape(a['count'], ncomp)

def node_mat(n):
    t = np.array(n.get('translation', [0, 0, 0]), float)
    r = np.array(n.get('rotation', [0, 0, 0, 1]), float)
    s = np.array(n.get('scale', [1, 1, 1]), float)
    x, y, z, w = r
    R = np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                  [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                  [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
    M = np.eye(4); M[:3, :3] = R * s; M[:3, 3] = t
    return M

g, blob = load(sys.argv[1])
nodes = g['nodes']
names = [n.get('name') for n in nodes]
skin = g['skins'][0]
joints = skin['joints']
jnames = [names[j] for j in joints]
WH = ['Hips', 'Spine', 'Spine1', 'Spine2', 'Neck', 'Head', 'LeftShoulder', 'LeftArm',
      'LeftForeArm', 'LeftHand', 'LeftHandThumb1', 'LeftHandThumb2', 'LeftHandThumb3',
      'LeftHandIndex1', 'LeftHandIndex2', 'LeftHandIndex3', 'LeftHandMiddle1',
      'LeftHandMiddle2', 'LeftHandMiddle3', 'LeftHandRing1', 'LeftHandRing2',
      'LeftHandRing3', 'LeftHandPinky1', 'LeftHandPinky2', 'RightShoulder', 'RightArm',
      'RightForeArm', 'RightHand', 'RightHandThumb1', 'RightHandThumb2', 'RightHandThumb3',
      'RightHandIndex1', 'RightHandIndex2', 'RightHandIndex3', 'RightHandMiddle1',
      'RightHandMiddle2', 'RightHandMiddle3', 'RightHandRing1', 'RightHandRing2',
      'RightHandRing3', 'RightHandPinky1', 'RightHandPinky2', 'LeftUpLeg', 'LeftLeg',
      'LeftFoot', 'LeftToeBase', 'RightUpLeg', 'RightLeg', 'RightFoot', 'RightToeBase']
missing = [b for b in WH if b not in jnames]
print(f"joints {len(joints)}; WH canonical present {len(WH)-len(missing)}/{len(WH)}; missing: {missing}")

parent = {}
for i, n in enumerate(nodes):
    for c in n.get('children', []):
        parent[c] = i
def glob(i):
    chain = []
    while i is not None:
        chain.append(i); i = parent.get(i)
    M = np.eye(4)
    for i in reversed(chain):
        M = M @ node_mat(nodes[i])
    return M
ibms = acc_data(g, blob, skin['inverseBindMatrices']).reshape(-1, 4, 4)
err = 0.0
for k, j in enumerate(joints):
    ibm = ibms[k].T  # stored column-major
    err = max(err, float(np.abs(glob(j) @ ibm - np.eye(4)).max()))
print(f"IBM check: max |globalBind * IBM - I| = {err:.2e}")

mn = np.array([1e9]*3); mx = np.array([-1e9]*3)
bad_w = bad_j = 0
total_v = 0
for m in g['meshes']:
    for pr in m['primitives']:
        pos = acc_data(g, blob, pr['attributes']['POSITION'])
        mn = np.minimum(mn, pos.min(axis=0)); mx = np.maximum(mx, pos.max(axis=0))
        j = acc_data(g, blob, pr['attributes']['JOINTS_0']).astype(int)
        w = acc_data(g, blob, pr['attributes']['WEIGHTS_0'])
        bad_j += int((j >= len(joints)).sum())
        bad_w += int((np.abs(w.sum(axis=1) - 1) > 1e-3).sum())
        total_v += len(pos)
print(f"meshes {len(g['meshes'])} verts {total_v} bounds min {np.round(mn,3)} max {np.round(mx,3)} height {mx[1]-mn[1]:.3f}")
print(f"joint index overflows {bad_j}; verts with weight-sum != 1: {bad_w}")
mats = g['materials']
texd = sum(1 for m in mats if m.get('pbrMetallicRoughness', {}).get('baseColorTexture') is not None)
flat = [m['name'] for m in mats if m.get('pbrMetallicRoughness', {}).get('baseColorTexture') is None]
print(f"materials {len(mats)}: textured {texd}, flat {flat}")
print(f"images {len(g['images'])} textures {len(g['textures'])}")

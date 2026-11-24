"""Skin char001 at bind pose (standard glTF: pos' = sum w * IBM * pos,
node transforms are identity) and locate anatomical joints."""
import json, struct
import numpy as np

GLB = '/home/hatch/workspace/preview-clips/urban-reign/wh/teardown/urban-reign/models/char001/char001.glb'
data = open(GLB, 'rb').read()
ln = struct.unpack('<I', data[12:16])[0]
g = json.loads(data[20:20+ln])
off = 20 + ln; bln = struct.unpack('<I', data[off:off+4])[0]
binx = data[off+8:off+8+bln]
def acc(ai):
    a = g['accessors'][ai]; bv = g['bufferViews'][a['bufferView']]
    o = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    ct = {5126: '<f4', 5123: '<u2', 5125: '<u4', 5121: '<u1'}[a['componentType']]
    nc = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[a['type']]
    arr = np.frombuffer(binx, dtype=ct, count=a['count'] * nc, offset=o)
    return arr.reshape(a['count'], nc) if nc > 1 else arr
skin = g['skins'][0]
ibm = np.array([np.array(m).reshape(4,4).T for m in acc(skin['inverseBindMatrices'])])
mesh_node = [n for n in g['nodes'] if 'mesh' in n and 'skin' in n][0]
pos_l, jts_l, wts_l = [], [], []
for prim in g['meshes'][mesh_node['mesh']]['primitives']:
    pos_l.append(acc(prim['attributes']['POSITION']).astype(float))
    jts_l.append(acc(prim['attributes']['JOINTS_0']).astype(int))
    wts_l.append(acc(prim['attributes']['WEIGHTS_0']).astype(float))
pos = np.vstack(pos_l); jts = np.vstack(jts_l); wts = np.vstack(wts_l)
hom = np.concatenate([pos, np.ones((len(pos),1))], axis=1)
sk = np.zeros((len(pos),4))
for k in range(4):
    sk += wts[:,k:k+1] * np.einsum('nij,nj->ni', ibm[jts[:,k]], hom)
P = sk[:,:3]
print("assembled bind mesh: verts", len(P), "min", P.min(0).round(3), "max", P.max(0).round(3))
print("extents:", (P.max(0)-P.min(0)).round(3))
np.save('/home/hatch/workspace/preview-clips/urban-reign/bind_pos.npy', P)
np.save('/home/hatch/workspace/preview-clips/urban-reign/bind_jts.npy', jts)
np.save('/home/hatch/workspace/preview-clips/urban-reign/bind_wts.npy', wts)
# per-joint dominant-vert centroids in ASSEMBLED space
dom = jts[np.arange(len(P)), np.argmax(wts, axis=1)]
print("\nper-joint dominant centroid (assembled space):")
for ji in range(37):
    sel = dom == ji
    if sel.sum() == 0:
        continue
    c = P[sel].mean(0)
    print(f"  joint {ji:2d} ({g['nodes'][ji]['name']:8s}): n={sel.sum():4d} c=[{c[0]:+.3f}, {c[1]:+.3f}, {c[2]:+.3f}]")

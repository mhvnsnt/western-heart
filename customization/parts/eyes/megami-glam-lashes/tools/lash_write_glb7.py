"""Write the lash-fix GLBs:
  work/lashes_glam_megami.glb            standalone part (skin subset copied
                                         from the target: ancestor chains of
                                         the used joints + subset IBMs)
  work/megami-angel-gnmface-v2-lashfix.glb  target GLB + lash mesh on skin 0
  work/lashes_before_similarity.glb      PR #149 set carried across by ONE
                                         similarity transform (the BEFORE)
"""
import sys, json, struct
sys.path.insert(0, 'scripts')
import numpy as np
from lash_glb_lib import load_glb, accessor

lg = np.load('work/lashes_megami_geom7.npz', allow_pickle=True)
V, T, C, Nr, J, W = lg['V'], lg['T'], lg['C'], lg['N'], lg['J'], lg['W']
g, b, raw = load_glb('work/megami-angel-gnmface-v2.glb')

LASH_MAT = {"name": "lash_dark", "pbrMetallicRoughness": {
    "baseColorFactor": [1.0, 1.0, 1.0, 1.0], "metallicFactor": 0.0,
    "roughnessFactor": 0.85}, "doubleSided": True, "alphaMode": "BLEND"}

def pack(arrays):
    """arrays: list of (bytes, alignment) -> (bin, offsets)"""
    binbuf = bytearray(); offs = []
    for data, al in arrays:
        while len(binbuf) % al: binbuf.append(0)
        offs.append(len(binbuf)); binbuf += data
    while len(binbuf) % 4: binbuf.append(0)
    return bytes(binbuf), offs

def glb_bytes(gltf, binbuf):
    j = json.dumps(gltf, separators=(',', ':')).encode()
    while len(j) % 4: j += b' '
    total = 12 + 8 + len(j) + 8 + len(binbuf)
    out = bytearray(b'glTF'); out += struct.pack('<II', 2, total)
    out += struct.pack('<I', len(j)) + b'JSON' + j
    out += struct.pack('<I', len(binbuf)) + b'BIN\x00' + binbuf
    return bytes(out)

def geom_arrays(Jx):
    return [
        (V.astype(np.float32).tobytes(), 4),
        (Nr.astype(np.float32).tobytes(), 4),
        (C.astype(np.float32).tobytes(), 4),
        (Jx.astype(np.uint16).tobytes(), 2),
        (W.astype(np.float32).tobytes(), 4),
        (T.astype(np.uint32).tobytes(), 4)]

def geom_accessors(base_bv, base_acc, Jx):
    bvs, accs = [], []
    specs = [
        (0, 5126, 'VEC3', V), (1, 5126, 'VEC3', Nr), (2, 5126, 'VEC4', C),
        (3, 5123, 'VEC4', Jx), (4, 5126, 'VEC4', W), (5, 5125, 'SCALAR', T)]
    for k, (ai, ct, ty, arr) in enumerate(specs):
        bvs.append({"buffer": 0, "byteOffset": 0, "byteLength": arr.size * np.dtype(
            {5126: np.float32, 5123: np.uint16, 5125: np.uint32}[ct]).itemsize})
        # FIX (finisher): the index accessor's count must be the ELEMENT count
        # (T.size = 3 x triangle count). The v1/v2 writer used len(T) = triangle
        # count, silently truncating the draw to the first third of the indices
        # — the posx side only; the negx band never rasterized. (F-1 in report.)
        cnt = int(arr.size) if ty == 'SCALAR' else len(arr)
        a = {"bufferView": base_bv + k, "componentType": ct, "count": cnt, "type": ty}
        if ty == 'VEC3' and k == 0:
            a['min'] = V.min(0).tolist(); a['max'] = V.max(0).tolist()
        accs.append(a)
    return bvs, accs

USED = sorted(set(int(x) for row in J for x in row if True))
USED = sorted(set(int(x) for x in np.unique(J)))
print('used skin-joint slots:', USED, [g['nodes'][g['skins'][0]['joints'][u]].get('name') for u in USED])

# ---------------- standalone part ----------------
skin0 = g['skins'][0]
joint_nodes = [skin0['joints'][u] for u in USED]
# ancestors of joint nodes
parent = {}
for i, n in enumerate(g['nodes']):
    for c in n.get('children', []): parent[c] = i
include = set(joint_nodes)
for jn in joint_nodes:
    cur = jn
    while cur in parent:
        cur = parent[cur]; include.add(cur)
order = sorted(include)
remap = {old: new for new, old in enumerate(order)}
nodes = []
for old in order:
    n = dict(g['nodes'][old])
    if 'children' in n: n['children'] = [remap[c] for c in n['children'] if c in remap]
    n.pop('mesh', None); n.pop('skin', None)
    nodes.append(n)
ibm_all = accessor(g, b, skin0['inverseBindMatrices'])
ibm_sub = ibm_all.reshape(-1, 16)[USED]
Jremap = np.array([[USED.index(int(x)) for x in row] for row in J], dtype=np.uint16)
binbuf, offs = pack(geom_arrays(Jremap) + [(ibm_sub.astype(np.float32).tobytes(), 4)])
bvs, accs = geom_accessors(0, 0, Jremap)
for bv_, o in zip(bvs, offs): bv_['byteOffset'] = o
bvs.append({"buffer": 0, "byteOffset": offs[6], "byteLength": ibm_sub.size * 4})
accs.append({"bufferView": 6, "componentType": 5126, "count": len(USED), "type": "MAT4"})
mesh_node = len(nodes)
nodes.append({"name": "glam_lashes_megami", "mesh": 0, "skin": 0})
roots = [remap[o] for o in order if o not in parent or parent[o] not in include]
part = {"asset": {"version": "2.0", "generator": "lash-fix lane"},
        "scene": 0, "scenes": [{"nodes": roots + [mesh_node]}],
        "nodes": nodes,
        "meshes": [{"name": "glam_lashes_megami", "primitives": [{
            "attributes": {"POSITION": 0, "NORMAL": 1, "COLOR_0": 2, "JOINTS_0": 3, "WEIGHTS_0": 4},
            "indices": 5, "material": 0}]}],
        "materials": [LASH_MAT],
        "skins": [{"joints": [remap[j] for j in joint_nodes],
                   "inverseBindMatrices": 6,
                   "skeleton": roots[0] if roots else remap[joint_nodes[0]]}],
        "buffers": [{"byteLength": len(binbuf)}],
        "bufferViews": bvs, "accessors": accs}
open('work/lashes_glam_megami.glb', 'wb').write(glb_bytes(part, binbuf))
print('wrote work/lashes_glam_megami.glb')

# ---------------- merged build ----------------
g2 = json.loads(json.dumps(g))
old_bin = b
binbuf2, offs2 = pack(geom_arrays(J))
base_bv = len(g2['bufferViews']); base_acc = len(g2['accessors'])
bvs2, accs2 = geom_accessors(base_bv, base_acc, J)
for bv_, o in zip(bvs2, offs2): bv_['byteOffset'] = len(old_bin) + o
g2['bufferViews'] += bvs2; g2['accessors'] += accs2
g2['materials'].append(LASH_MAT)
mat_i = len(g2['materials']) - 1
g2['meshes'].append({"name": "glam_lashes_megami", "primitives": [{
    "attributes": {"POSITION": base_acc + 0, "NORMAL": base_acc + 1, "COLOR_0": base_acc + 2,
                   "JOINTS_0": base_acc + 3, "WEIGHTS_0": base_acc + 4},
    "indices": base_acc + 5, "material": mat_i}]})
g2['nodes'].append({"name": "GlamLashes", "mesh": len(g2['meshes']) - 1, "skin": 0})
g2['scenes'][0]['nodes'].append(len(g2['nodes']) - 1)
g2['buffers'][0]['byteLength'] = len(old_bin) + len(binbuf2)
open('work/megami-angel-gnmface-v2-lashfix.glb', 'wb').write(glb_bytes(g2, old_bin + binbuf2))
print('wrote work/megami-angel-gnmface-v2-lashfix.glb')

# ---------------- BEFORE: similarity carry-across ----------------
gg, bb, _ = load_glb('glam-src/lashes_glam.glb')
gv = accessor(gg, bb, gg['meshes'][0]['primitives'][0]['attributes']['POSITION'])
gt = accessor(gg, bb, gg['meshes'][0]['primitives'][0]['indices']).reshape(-1)
geo2 = np.load('work/lash_megami_geometry.npz', allow_pickle=True)
mid_meg = (geo2['posx_iris_c'] + geo2['negx_iris_c']) / 2
iod_meg = float(np.linalg.norm(geo2['posx_iris_c'] - geo2['negx_iris_c']))
IOD_GNM = 0.0639887937790898
s = iod_meg / IOD_GNM
mid_gnm = gv.mean(0)
Vb = mid_meg + s * (gv - mid_gnm)
binbuf3, offs3 = pack([(Vb.astype(np.float32).tobytes(), 4), (gt.astype(np.uint32).tobytes(), 4)])
before = {"asset": {"version": "2.0", "generator": "lash-fix BEFORE reproduction"},
          "scene": 0, "scenes": [{"nodes": [0]}],
          "nodes": [{"name": "glam_lashes_before", "mesh": 0}],
          "meshes": [{"name": "glam_lashes_before", "primitives": [{
              "attributes": {"POSITION": 0}, "indices": 1, "material": 0}]}],
          "materials": [{"name": "lash_dark", "pbrMetallicRoughness": {
              "baseColorFactor": [0.05, 0.05, 0.05, 1.0], "metallicFactor": 0.0,
              "roughnessFactor": 0.85}, "doubleSided": True}],
          "buffers": [{"byteLength": len(binbuf3)}],
          "bufferViews": [{"buffer": 0, "byteOffset": offs3[0], "byteLength": len(Vb) * 12},
                          {"buffer": 0, "byteOffset": offs3[1], "byteLength": len(gt) * 4}],
          "accessors": [{"bufferView": 0, "componentType": 5126, "count": len(Vb), "type": "VEC3",
                         "min": Vb.min(0).tolist(), "max": Vb.max(0).tolist()},
                        {"bufferView": 1, "componentType": 5125, "count": len(gt), "type": "SCALAR"}]}
open('work/lashes_before_similarity.glb', 'wb').write(glb_bytes(before, binbuf3))
per_eye = {}
for nm, sel in (('negx', Vb[:, 0] < mid_meg[0]), ('posx', Vb[:, 0] >= mid_meg[0])):
    per_eye[nm] = float(Vb[sel][:, 0].max() - Vb[sel][:, 0].min())
print(f'wrote work/lashes_before_similarity.glb  scale={s:.4f} iod_meg={iod_meg:.5f} per-eye span={per_eye}')

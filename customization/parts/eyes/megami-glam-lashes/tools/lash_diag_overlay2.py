"""V7 diagnostic build 2: markers at the NEW visible margin (cyan top /
yellow bot) on the base GLB — they should trace the visible edge of the
eyeball opening exactly. Plus red markers at the OLD loop for contrast."""
import sys, json, struct
sys.path.insert(0, 'scripts')
import numpy as np
from lash_glb_lib import load_glb

geo = np.load('work/lash_megami_geometry.npz', allow_pickle=True)
vis = np.load('work/lash_visible_margin.npz', allow_pickle=True)


def octa(P, r=0.00030):
    V, T = [], []
    for p in P:
        o = len(V)
        V += [p + [r, 0, 0], p - [r, 0, 0], p + [0, r, 0], p - [0, r, 0], p + [0, 0, r], p - [0, 0, r]]
        for a, b2, c in ((0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)):
            T.append([o + a, o + b2, o + c])
    return np.array(V), np.array(T)


def pack(arrays):
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


g, b, _ = load_glb('work/megami-angel-gnmface-v2.glb')
g2 = json.loads(json.dumps(g))
sets = [
    (np.vstack([vis['posx_top_pts'], vis['negx_top_pts']]), [0, 1, 1], 'MARK_newtop'),
    (np.vstack([vis['posx_bot_pts'], vis['negx_bot_pts']]), [1, 1, 0], 'MARK_newbot'),
    (np.vstack([geo['posx_top'], geo['negx_top']]), [1, 0, 0.1], 'MARK_oldtop'),
]
for P, rgb, name in sets:
    V, T = octa(P)
    binbuf, offs = pack([(V.astype(np.float32).tobytes(), 4),
                         (T.astype(np.uint32).tobytes(), 4)])
    base_bv = len(g2['bufferViews']); base_acc = len(g2['accessors'])
    g2['bufferViews'] += [
        {"buffer": 0, "byteOffset": len(b) + offs[0], "byteLength": V.size * 4},
        {"buffer": 0, "byteOffset": len(b) + offs[1], "byteLength": T.size * 4}]
    g2['accessors'] += [
        {"bufferView": base_bv, "componentType": 5126, "count": len(V), "type": "VEC3",
         "min": V.min(0).tolist(), "max": V.max(0).tolist()},
        {"bufferView": base_bv + 1, "componentType": 5125, "count": int(T.size), "type": "SCALAR"}]
    g2['materials'].append({"name": name, "pbrMetallicRoughness": {
        "baseColorFactor": rgb + [1.0], "metallicFactor": 0.0, "roughnessFactor": 0.4},
        "doubleSided": True})
    g2['meshes'].append({"name": name, "primitives": [{
        "attributes": {"POSITION": base_acc}, "indices": base_acc + 1,
        "material": len(g2['materials']) - 1}]})
    g2['nodes'].append({"name": name, "mesh": len(g2['meshes']) - 1})
    g2['scenes'][0]['nodes'].append(len(g2['nodes']) - 1)
    b = b + binbuf
g2['buffers'][0]['byteLength'] = len(b)
open('work/diag_markers2.glb', 'wb').write(glb_bytes(g2, b))
print('wrote work/diag_markers2.glb')

"""V7 diagnostic build: marker GLBs to identify the extracted margin loop
in SCREEN space. Appends octahedron markers to a GLB:
  RED  = extracted TOP arc (the 'margin' the lashes are rooted on)
  GREEN= extracted BOT arc
Variants:
  work/diag_markers_lash.glb  = lashfix(v6) GLB + markers
  work/diag_markers_nolash.glb= base GLB + markers only
Markers are UNSKINNED at the extracted AngelFace=1/AngelBody=1 world
coords (the stage renders exactly that state in bind pose)."""
import sys, json, struct
sys.path.insert(0, 'scripts')
import numpy as np
from lash_glb_lib import load_glb

geo = np.load('work/lash_megami_geometry.npz', allow_pickle=True)


def catmull(Pt, n_per=16):
    Pt = np.asarray(Pt, float)
    ext = np.vstack([Pt[0] + (Pt[0] - Pt[1]), Pt, Pt[-1] + (Pt[-1] - Pt[-2])])
    out = []
    for i in range(len(Pt) - 1):
        p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
        for t in np.linspace(0, 1, n_per, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(Pt[-1])
    return np.array(out)


def octa(P, r=0.00035):
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


def add_markers(src, dst):
    g, b, _ = load_glb(src)
    g2 = json.loads(json.dumps(g))
    tops = np.vstack([catmull(geo['posx_top']), catmull(geo['negx_top'])])
    bots = np.vstack([catmull(geo['posx_bot']), catmull(geo['negx_bot'])])
    for P, rgb, name in ((tops, [1, 0, 0.1], 'MARK_top'), (bots, [0, 1, 0.2], 'MARK_bot')):
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
    open(dst, 'wb').write(glb_bytes(g2, b))
    print('wrote', dst)


add_markers('work/megami-angel-gnmface-v2-lashfix.glb', 'work/diag_markers_lash.glb')
add_markers('work/megami-angel-gnmface-v2.glb', 'work/diag_markers_nolash.glb')

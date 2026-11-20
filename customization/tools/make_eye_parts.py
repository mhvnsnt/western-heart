#!/usr/bin/env python3
"""Build the Creation Suite eye mesh parts (owner law: eyes are real
placeable MESH parts, never painted decals).

Writes two small GLBs in glTF space (Y-up, +Z forward — the roster's
convention), origin at the part's natural anchor:
  customization/parts/eyes/eyeball.glb  origin = eyeball centre
  customization/parts/eyes/eyelash.glb  origin = the eyeball centre it
                                        sits on (lash arc above/front)
An eyeball is ~24 mm across: sclera sphere r=12 mm, iris disc r=5.5 mm
at the front pole, pupil r=2.8 mm. No textures — flat PBR colours, the
suite tints/places them like any other part.

Usage: python3 customization/tools/make_eye_parts.py
"""
import json, math, os, struct
import numpy as np

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'parts', 'eyes')

def sphere(r, seg=24, rings=16, squash_z=1.0):
    verts, idx = [], []
    for i in range(rings + 1):
        phi = math.pi * i / rings
        for j in range(seg + 1):
            th = 2 * math.pi * j / seg
            verts.append([r * math.sin(phi) * math.cos(th),
                          r * math.cos(phi),
                          r * squash_z * math.sin(phi) * math.sin(th)])
    for i in range(rings):
        for j in range(seg):
            a = i * (seg + 1) + j; b = a + seg + 1
            idx += [a, b, a + 1, b, b + 1, a + 1]
    return np.array(verts, dtype=np.float64), np.array(idx, dtype=np.uint32)

def disc(r, z, seg=24):
    verts = [[0.0, 0.0, z]]
    for j in range(seg):
        th = 2 * math.pi * j / seg
        verts.append([r * math.cos(th), r * math.sin(th), z])
    idx = []
    for j in range(seg):
        idx += [0, 1 + j, 1 + (j + 1) % seg]
    return np.array(verts, dtype=np.float64), np.array(idx, dtype=np.uint32)

def lash_band(r=0.0135, width=0.0045, arc=2.0, seg=20):
    """A curved strip hugging the top front of the eyeball."""
    verts, idx = [], []
    for i in range(seg + 1):
        th = math.pi / 2 + arc * (i / seg - 0.5)   # around the top
        for k in (-0.5, 0.5):
            rr = r + k * width
            verts.append([rr * math.cos(th), rr * math.sin(th) * 0.55 + 0.004,
                          r * 0.82])
    for i in range(seg):
        a = i * 2
        idx += [a, a + 2, a + 1, a + 2, a + 3, a + 1]
    return np.array(verts, dtype=np.float64), np.array(idx, dtype=np.uint32)

def normals_for(verts, idx):
    n = np.zeros_like(verts)
    for a, b, c in idx.reshape(-1, 3):
        fn = np.cross(verts[b] - verts[a], verts[c] - verts[a])
        n[a] += fn; n[b] += fn; n[c] += fn
    L = np.linalg.norm(n, axis=1, keepdims=True)
    return (n / np.maximum(L, 1e-9)).astype(np.float32)

def write_glb(path, meshes):
    """meshes: [(name, verts, idx, rgba)] — unlit-ish PBR flat colours."""
    blob = bytearray()
    views, accessors, gltf_meshes, materials = [], [], [], []
    def add_view(arr, target):
        nonlocal blob
        while len(blob) % 4:
            blob += b'\x00'
        off = len(blob)
        blob += arr.tobytes()
        views.append({'buffer': 0, 'byteOffset': off, 'byteLength': len(arr.tobytes()),
                      'target': target})
        return len(views) - 1
    def add_acc(view, comp, typ, count, mn=None, mx=None):
        a = {'bufferView': view, 'componentType': comp, 'type': typ, 'count': count}
        if mn is not None: a['min'] = mn
        if mx is not None: a['max'] = mx
        accessors.append(a)
        return len(accessors) - 1
    nodes = []
    for name, verts, idx, rgba in meshes:
        v32 = verts.astype(np.float32)
        nrm = normals_for(verts, idx)
        pv = add_view(v32, 34962)
        pa = add_acc(pv, 5126, 'VEC3', len(v32), v32.min(0).tolist(), v32.max(0).tolist())
        nv = add_view(nrm, 34962)
        na = add_acc(nv, 5126, 'VEC3', len(nrm))
        iv = add_view(idx.astype(np.uint32), 34963)
        ia = add_acc(iv, 5125, 'SCALAR', len(idx))
        materials.append({'name': f'{name}_mat', 'pbrMetallicRoughness': {
            'baseColorFactor': rgba, 'metallicFactor': 0.0, 'roughnessFactor': 0.35}})
        gltf_meshes.append({'name': name, 'primitives': [{
            'attributes': {'POSITION': pa, 'NORMAL': na}, 'indices': ia,
            'material': len(materials) - 1}]})
        nodes.append({'name': name, 'mesh': len(gltf_meshes) - 1})
    doc = {'asset': {'version': '2.0', 'generator': 'wh make_eye_parts.py'},
           'scene': 0, 'scenes': [{'nodes': list(range(len(nodes)))}],
           'nodes': nodes, 'meshes': gltf_meshes, 'materials': materials,
           'buffers': [{'byteLength': len(blob)}], 'bufferViews': views,
           'accessors': accessors}
    js = json.dumps(doc).encode()
    js += b' ' * ((4 - len(js) % 4) % 4)
    total = 12 + 8 + len(js) + 8 + len(blob)
    with open(path, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, total))
        f.write(struct.pack('<II', len(js), 0x4E4F534A)); f.write(js)
        f.write(struct.pack('<II', len(blob), 0x004E4942)); f.write(bytes(blob))
    print(f'wrote {path} ({total} B, {len(meshes)} meshes)')

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    sv, si = sphere(0.012)
    iv, ii = disc(0.0055, 0.0113)
    pv, pi = disc(0.0028, 0.0119)
    write_glb(os.path.join(OUT_DIR, 'eyeball.glb'), [
        ('EyeballSclera', sv, si, [0.96, 0.95, 0.93, 1.0]),
        ('EyeballIris', iv, ii, [0.23, 0.12, 0.05, 1.0]),
        ('EyeballPupil', pv, pi, [0.02, 0.02, 0.02, 1.0]),
    ])
    lv, li = lash_band()
    write_glb(os.path.join(OUT_DIR, 'eyelash.glb'), [
        ('Eyelash', lv, li, [0.03, 0.02, 0.02, 1.0]),
    ])

if __name__ == '__main__':
    main()

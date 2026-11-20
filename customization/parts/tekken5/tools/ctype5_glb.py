"""GLB writer for decoded ctype-5 (VIF 0x82) models (gap-closure W7d).

Conventions matched to the W7e costume GLBs in this catalog: raw source
coordinates (no axis conversion), UV V flipped to the glTF convention
(nudp2obj_uv.py does the same), the container's TIM2 picture 0 embedded
as the material's baseColorTexture (the only texture any of these
models' materials reference), vertex colors from the V4-8 section (RGBA,
PS2 alpha scale 0..128 -> 0..1). Normals are computed (smooth,
area-weighted) because the 0x82 packet carries no normal section.
Every decoded blob becomes one primitive; mesh groups are exported
faithfully as stored (in these models all groups of a model are
byte-identical repeated units - runtime placement transforms are not
stored in the NUDP).
"""
import struct, json, math, os


def write_glb(path, subs, png_bytes):
    bin_parts = []
    views = []
    accessors = []
    offset = 0

    def add_view(data, hint):
        nonlocal offset
        pad = (-offset) % 4
        if pad:
            bin_parts.append(b'\x00' * pad)
            offset += pad
        views.append((offset, len(data), hint))
        bin_parts.append(data)
        offset += len(data)
        return len(views) - 1

    def acc(view, ctype, typ, count, mn=None, mx=None):
        a = {'bufferView': view, 'componentType': ctype, 'type': typ, 'count': count}
        if mn is not None:
            a['min'] = mn
            a['max'] = mx
        accessors.append(a)
        return len(accessors) - 1

    prims = []
    total_v = total_f = 0
    for r in subs:
        pos, n, faces = r['pos'], r['n'], r['faces']
        nrm = [[0.0, 0.0, 0.0] for _ in range(n)]
        for a, b, c in faces:
            ux, uy, uz = (pos[b][i] - pos[a][i] for i in range(3))
            vx, vy, vz = (pos[c][i] - pos[a][i] for i in range(3))
            cx, cy, cz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
            for i in (a, b, c):
                nrm[i][0] += cx
                nrm[i][1] += cy
                nrm[i][2] += cz
        for v in nrm:
            l = math.sqrt(sum(x * x for x in v)) or 1.0
            v[0] /= l
            v[1] /= l
            v[2] /= l
        col = [(rr / 255.0, gg / 255.0, bb / 255.0, min(1.0, aa / 128.0))
               for rr, gg, bb, aa in r['col']]
        uv = [(u, 1.0 - v) for u, v in r['uv']]
        pa = acc(add_view(b''.join(struct.pack('<3f', *p) for p in pos), 34962),
                 5126, 'VEC3', n,
                 [min(p[i] for p in pos) for i in range(3)],
                 [max(p[i] for p in pos) for i in range(3)])
        na = acc(add_view(b''.join(struct.pack('<3f', *v) for v in nrm), 34962),
                 5126, 'VEC3', n)
        ca = acc(add_view(b''.join(struct.pack('<4f', *c) for c in col), 34962),
                 5126, 'VEC4', n)
        ta = acc(add_view(b''.join(struct.pack('<2f', *t) for t in uv), 34962),
                 5126, 'VEC2', n)
        ia = acc(add_view(b''.join(struct.pack('<3I', *f) for f in faces), 34963),
                 5125, 'SCALAR', len(faces) * 3)
        prims.append({'attributes': {'POSITION': pa, 'NORMAL': na,
                                      'COLOR_0': ca, 'TEXCOORD_0': ta},
                      'indices': ia, 'material': 0})
        total_v += n
        total_f += len(faces)
    img_view = add_view(png_bytes, 0)
    bchunk = b''.join(bin_parts)
    gltf = {
        'asset': {'version': '2.0',
                  'generator': 'W7d vif082.py + ctype5_glb.py (Tekken 5 VIF 0x82 decoder)'},
        'scene': 0, 'scenes': [{'nodes': [0]}], 'nodes': [{'mesh': 0}],
        'meshes': [{'name': os.path.basename(path)[:-4], 'primitives': prims}],
        'materials': [{'name': 'tex0',
                       'pbrMetallicRoughness': {'baseColorTexture': {'index': 0},
                                                'metallicFactor': 0.0,
                                                'roughnessFactor': 1.0},
                       'alphaMode': 'BLEND', 'doubleSided': True}],
        'textures': [{'source': 0, 'sampler': 0}],
        'images': [{'bufferView': img_view, 'mimeType': 'image/png'}],
        'samplers': [{'magFilter': 9729, 'minFilter': 9729,
                      'wrapS': 10497, 'wrapT': 10497}],
        'bufferViews': [{'buffer': 0, 'byteOffset': o, 'byteLength': l,
                         **({'target': t} if t else {})} for o, l, t in views],
        'accessors': accessors,
        'buffers': [{'byteLength': len(bchunk)}],
    }
    jchunk = json.dumps(gltf).encode()
    jchunk += b' ' * ((-len(jchunk)) % 4)
    bchunk += b'\x00' * ((-len(bchunk)) % 4)
    total = 12 + 8 + len(jchunk) + 8 + len(bchunk)
    with open(path, 'wb') as f:
        f.write(struct.pack('<4sII', b'glTF', 2, total))
        f.write(struct.pack('<II', len(jchunk), 0x4E4F534A))
        f.write(jchunk)
        f.write(struct.pack('<II', len(bchunk), 0x004E4942))
        f.write(bchunk)
    return total_v, total_f

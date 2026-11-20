#!/usr/bin/env python3
"""Phase 13 JOB 2: embed VXT textures into a phase-5 skinned fighter GLB.

Mapping (pointer-exact, see VXT-FORMAT.md):
  GLB mesh name g{gi}p{ii}[_r]  ->  VMX part record (group gi, index ii)
  part +0x0c                    ->  rec80 material record
  material +0x08                ->  primary VXT texture record
The texture PNG (DXT level 0, linear decode) is embedded in the GLB and
assigned as baseColorTexture. Geometry/skinning data is copied through
untouched; the tool verifies accessor counts are identical afterwards.
Usage: apply_textures.py <bundle.bin> <in.glb> <out.glb>
Prints a JSON report line.
"""
import struct, sys, json, io
sys.path.insert(0, '/home/hatch/workspace/scii-work/p13/work')
from vxt_decode import parse_vxt, decode_texture, FMT
from PIL import Image

def u16(d, o): return struct.unpack_from('<H', d, o)[0]
def u32(d, o): return struct.unpack_from('<I', d, o)[0]

def load_glb(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'glTF'
    ln = u32(d, 12)
    g = json.loads(d[20:20+ln])
    boff = 20 + ln
    bln = u32(d, boff)
    binchunk = d[boff+8:boff+8+bln]
    return g, bytearray(binchunk)

def save_glb(path, g, binchunk):
    js = json.dumps(g, separators=(',', ':')).encode()
    js += b' ' * ((4 - len(js) % 4) % 4)
    binchunk += b'\x00' * ((4 - len(binchunk) % 4) % 4)
    out = bytearray()
    out += b'glTF' + struct.pack('<2I', 2, 12 + 8 + len(js) + 8 + len(binchunk))
    out += struct.pack('<I', len(js)) + b'JSON' + js
    out += struct.pack('<I', len(binchunk)) + b'BIN\x00' + binchunk
    open(path, 'wb').write(out)

def accessor_counts(g):
    pos = idx = joints = 0
    for m in g['meshes']:
        for pr in m['primitives']:
            pos += g['accessors'][pr['attributes']['POSITION']]['count']
            if 'indices' in pr:
                idx += g['accessors'][pr['indices']]['count']
            if 'JOINTS_0' in pr['attributes']:
                joints += g['accessors'][pr['attributes']['JOINTS_0']]['count']
    skins = len(g.get('skins', []))
    njoints = len(g['skins'][0]['joints']) if skins else 0
    return dict(verts=pos, indices=idx, jointattr=joints, skins=skins, skinjoints=njoints)

def main():
    bundle_path, in_glb, out_glb = sys.argv[1:4]
    d = open(bundle_path, 'rb').read()
    V = d.find(b'VMX.')
    assert V >= 0 and d[V+4] == 4, 'vmx0 not found'
    vxt_rel = u32(d, V+0x18)
    vxt_base = V + vxt_rel
    assert d[vxt_base:vxt_base+4] == b'VXT.', 'VXT section missing'
    recs = parse_vxt(d, vxt_base)
    tex_rec_base = vxt_base + u32(d, vxt_base+0x0c)
    rec80_base = V + u32(d, V+0x1c)
    n80 = u16(d, V+0x14)
    pcounts = [u16(d, V+0x0C), u16(d, V+0x0E), u16(d, V+0x10)]
    pbase = [u32(d, V+0x2C), u32(d, V+0x30), u32(d, V+0x34)]

    def part_tex(gi, ii):
        """-> (tex_index or None, mat_index, note)"""
        rec = struct.unpack_from('<10I', d, V + pbase[gi] + ii*40)
        matptr = rec[3]
        if matptr == 0:
            return None, None, 'part has no material pointer'
        mi, rem = divmod(matptr - u32(d, V+0x1c), 80)
        if rem or not (0 <= mi < n80):
            return None, None, f'material pointer {matptr:#x} not in rec80 array'
        tp = u32(d, V + u32(d, V+0x1c) + mi*80 + 8)
        if tp == 0:
            return None, mi, 'material is color-only (texture ptr 0)'
        ti, rem = divmod(tp - vxt_rel - 0x14, 36)
        if rem or not (0 <= ti < len(recs)):
            return None, mi, f'texture pointer {tp:#x} not a VXT record'
        return ti, mi, 'ok'

    g, binchunk = load_glb(in_glb)
    before = accessor_counts(g)
    tex_png = {}   # tex idx -> image index
    tex_alpha = {} # tex idx -> (min alpha, max alpha)
    g.setdefault('images', []); g.setdefault('bufferViews', [])
    g.setdefault('textures', []); g.setdefault('materials', [])
    g.setdefault('samplers', [{'magFilter': 9729, 'minFilter': 9987,
                               'wrapS': 10497, 'wrapT': 10497}])
    mat_for_tex = {}
    per_mesh = []
    for m in g['meshes']:
        name = m['name']
        base = name[:-2] if name.endswith('_r') else name
        gi = int(base[1]); ii = int(base[3:5])
        ti, mi, note = part_tex(gi, ii)
        if ti is None:
            per_mesh.append((name, None, note)); continue
        if ti not in tex_png:
            img = decode_texture(d, vxt_base, recs[ti], unsw=False)
            amin, amax = int(img[:, :, 3].min()), int(img[:, :, 3].max())
            tex_alpha[ti] = (amin, amax)
            a = img[:, :, 3]
            # Alpha-mode rule (evidence in TEXTURED-MODELS.md): MASK only for
            # genuine cutout maps — real fully-transparent AND fully-opaque
            # populations. Texture sets whose alpha never reaches 255
            # (e.g. idx944 Spawn: every texture amax<=179, alpha is a
            # specular-style mask) ship OPAQUE or the body renders washed out.
            is_cutout = (amax == 255 and float((a <= 8).mean()) >= 0.01
                         and float((a >= 247).mean()) >= 0.05)
            buf = io.BytesIO(); Image.fromarray(img, 'RGBA').save(buf, 'PNG')
            png = buf.getvalue()
            off = len(binchunk); binchunk += png
            binchunk += b'\x00' * ((4 - len(binchunk) % 4) % 4)
            g['bufferViews'].append({'buffer': 0, 'byteOffset': off, 'byteLength': len(png)})
            g['images'].append({'bufferView': len(g['bufferViews'])-1,
                                'mimeType': 'image/png', 'name': f'vxt_tex{ti:02d}'})
            tex_png[ti] = len(g['images']) - 1
            g['textures'].append({'source': tex_png[ti], 'sampler': 0})
            mat = {'name': f'vxt_tex{ti:02d}_mat',
                   'pbrMetallicRoughness': {'baseColorTexture': {'index': len(g['textures'])-1},
                                            'metallicFactor': 0.0, 'roughnessFactor': 1.0}}
            if is_cutout:
                mat['alphaMode'] = 'MASK'; mat['alphaCutoff'] = 0.5
            mat['doubleSided'] = True
            g['materials'].append(mat)
            mat_for_tex[ti] = len(g['materials']) - 1
        for pr in m['primitives']:
            pr['material'] = mat_for_tex[ti]
        per_mesh.append((name, ti, 'ok'))
    g['buffers'][0]['byteLength'] = len(binchunk)
    save_glb(out_glb, g, binchunk)
    g2, _ = load_glb(out_glb)
    after = accessor_counts(g2)
    assert before == after, f'GEOMETRY CHANGED {before} -> {after}'
    rep = dict(glb=out_glb, counts=before, images=len(g2.get('images', [])),
               textures_used=sorted(tex_png.keys()),
               tex_alpha={str(k): v for k, v in sorted(tex_alpha.items())},
               meshes_total=len(per_mesh),
               meshes_textured=sum(1 for _n, t, _x in per_mesh if t is not None),
               meshes_untextured=[(n, x) for n, t, x in per_mesh if t is None],
               per_mesh=[(n, t) for n, t, _x in per_mesh])
    print(json.dumps(rep))

if __name__ == '__main__':
    main()

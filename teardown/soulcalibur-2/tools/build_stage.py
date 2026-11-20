#!/usr/bin/env python3
"""Phase 13 JOB 3: assemble a v404 stage VMX into a textured stage GLB.

Stage part layout (GRE PR #28, verified): per-part vertex stream at
part+0x14, end at part+0x24, stride 40 B (pos f32x3, normal f32x3,
color u8x4, uv f32x2, pad f32). Index stream u16 at part+0x10, count
at part+0x04. Positions are world-space (m003 floor plan verified from
raw positions). Face topology per part is chosen by the phase-3 parity
method: triangle-strip vs triangle-list scored by agreement between
geometric face normals and authored vertex normals; the winner is
recorded in the report (no guessed topology ships unmeasured).
Textures: same part+0x0c -> rec80 material -> +0x08 VXT record chain
as the fighters (VXT-FORMAT.md), embedded as PNG.
Usage: build_stage.py <stage.bin> <out.glb>  -> prints JSON report.
"""
import struct, sys, json, io, math
sys.path.insert(0, '/home/hatch/workspace/scii-work/p13/work')
from vxt_decode import parse_vxt, decode_texture
from PIL import Image
import numpy as np

def u16(d, o): return struct.unpack_from('<H', d, o)[0]
def u32(d, o): return struct.unpack_from('<I', d, o)[0]

def strip_to_tris(idx):
    tris = []
    for i in range(len(idx) - 2):
        a, b, c = idx[i], idx[i+1], idx[i+2]
        if a == b or b == c or a == c: continue
        if i % 2 == 1: a, c = c, a
        tris.append((a, b, c))
    return tris

def list_to_tris(idx):
    return [(idx[i], idx[i+1], idx[i+2]) for i in range(0, len(idx) - 2, 3)
            if len({idx[i], idx[i+1], idx[i+2]}) == 3]

def score(tris, P, N):
    if not tris: return 0.0
    tot, nn = 0.0, 0
    for a, b, c in tris:
        pa, pb, pc = P[a], P[b], P[c]
        ux, uy, uz = pb[0]-pa[0], pb[1]-pa[1], pb[2]-pa[2]
        vx, vy, vz = pc[0]-pa[0], pc[1]-pa[1], pc[2]-pa[2]
        gx, gy, gz = uy*vz-uz*vy, uz*vx-ux*vz, ux*vy-uy*vx
        gl = math.sqrt(gx*gx+gy*gy+gz*gz)
        if gl < 1e-12: continue
        gx, gy, gz = gx/gl, gy/gl, gz/gl
        mx = (N[a][0]+N[b][0]+N[c][0])/3; my = (N[a][1]+N[b][1]+N[c][1])/3; mz = (N[a][2]+N[b][2]+N[c][2])/3
        ml = math.sqrt(mx*mx+my*my+mz*mz)
        if ml < 1e-12: continue
        tot += (gx*mx + gy*my + gz*mz)/ml; nn += 1
    return tot/nn if nn else 0.0

def main():
    fn, out = sys.argv[1], sys.argv[2]
    d = open(fn, 'rb').read()
    V = d.find(b'VMX.')
    assert V >= 0, 'no VMX'
    vxt_rel = u32(d, V+0x18); vb = V + vxt_rel
    has_vxt = d[vb:vb+4] == b'VXT.'
    recs = parse_vxt(d, vb) if has_vxt else []
    rec80_base_rel = u32(d, V+0x1c); n80 = u16(d, V+0x14)
    pcounts = [u16(d, V+0x0C), u16(d, V+0x0E), u16(d, V+0x10)]
    pbase = [u32(d, V+0x2C), u32(d, V+0x30), u32(d, V+0x34)]

    def part_tex(gi, ii):
        rec = struct.unpack_from('<10I', d, V + pbase[gi] + ii*40)
        mp = rec[3]
        if mp == 0 or not has_vxt: return None
        mi, rem = divmod(mp - rec80_base_rel, 80)
        if rem or not (0 <= mi < n80): return None
        tp = u32(d, V + rec80_base_rel + mi*80 + 8)
        if tp == 0: return None
        ti, rem = divmod(tp - vxt_rel - 0x14, 36)
        if rem or not (0 <= ti < len(recs)): return None
        return ti

    binbuf = bytearray(); views = []; accs = []; meshes = []; nodes = []
    images = []; textures = []; materials = []
    mat_for_tex = {}
    part_reports = []
    total_v = total_t = 0

    def add_view(data, target=None):
        off = len(binbuf); binbuf.extend(data)
        binbuf.extend(b'\x00' * ((4 - len(binbuf) % 4) % 4))
        v = {'buffer': 0, 'byteOffset': off, 'byteLength': len(data)}
        if target: v['target'] = target
        views.append(v); return len(views) - 1

    def add_acc(view, ctype, atype, count, mn=None, mx=None):
        a = {'bufferView': view, 'componentType': ctype, 'type': atype, 'count': count}
        if mn is not None: a['min'] = mn
        if mx is not None: a['max'] = mx
        accs.append(a); return len(accs) - 1

    for gi in range(3):
        for ii in range(pcounts[gi]):
            rec = struct.unpack_from('<10I', d, V + pbase[gi] + ii*40)
            icnt, iptr, vptr, vend = rec[1], rec[4], rec[5], rec[9]
            span = vend - vptr
            if span <= 0 or span % 40 or icnt == 0:
                part_reports.append((f'g{gi}p{ii:02d}', 'skipped: bad span/count')); continue
            nv = span // 40
            P = []; N = []; UV = []; COL = []
            for k in range(nv):
                o = V + vptr + k*40
                x, y, z, nx, ny, nz = struct.unpack_from('<6f', d, o)
                col = u32(d, o + 24)
                uu, vv = struct.unpack_from('<2f', d, o + 28)
                P.append((x, y, z)); N.append((nx, ny, nz)); UV.append((uu, vv))
                COL.append(((col >> 16 & 255)/255, (col >> 8 & 255)/255, (col & 255)/255, (col >> 24 & 255)/255))
            idx = list(struct.unpack_from(f'<{icnt}H', d, V + iptr))
            if max(idx) >= nv:
                part_reports.append((f'g{gi}p{ii:02d}', f'skipped: index {max(idx)} >= nv {nv}')); continue
            ts = strip_to_tris(idx); tl = list_to_tris(idx)
            ss, sl = score(ts, P, N), score(tl, P, N)
            tris, topo = (ts, 'strip') if ss >= sl else (tl, 'list')
            flat = [i for t in tris for i in t]
            pa = add_acc(add_view(b''.join(struct.pack('<3f', *p) for p in P), 34962), 5126, 'VEC3', nv,
                         [min(p[k] for p in P) for k in range(3)], [max(p[k] for p in P) for k in range(3)])
            na = add_acc(add_view(b''.join(struct.pack('<3f', *n) for n in N), 34962), 5126, 'VEC3', nv)
            ta = add_acc(add_view(b''.join(struct.pack('<2f', *t) for t in UV), 34962), 5126, 'VEC2', nv)
            ca = add_acc(add_view(b''.join(struct.pack('<4f', *c) for c in COL), 34962), 5126, 'VEC4', nv)
            ia = add_acc(add_view(b''.join(struct.pack('<I', i) for i in flat), 34963), 5125, 'SCALAR', len(flat))
            prim = {'attributes': {'POSITION': pa, 'NORMAL': na, 'TEXCOORD_0': ta, 'COLOR_0': ca},
                    'indices': ia, 'mode': 4}
            ti = part_tex(gi, ii)
            if ti is not None:
                if ti not in mat_for_tex:
                    img = decode_texture(d, vb, recs[ti], unsw=False)
                    a = img[:, :, 3]
                    buf = io.BytesIO(); Image.fromarray(img, 'RGBA').save(buf, 'PNG')
                    png = buf.getvalue()
                    images.append({'bufferView': add_view(png), 'mimeType': 'image/png', 'name': f'vxt_tex{ti:02d}'})
                    textures.append({'source': len(images)-1, 'sampler': 0})
                    mat = {'name': f'vxt_tex{ti:02d}_mat',
                           'pbrMetallicRoughness': {'baseColorTexture': {'index': len(textures)-1},
                                                    'metallicFactor': 0.0, 'roughnessFactor': 1.0},
                           'doubleSided': True}
                    if (int(a.max()) == 255 and float((a <= 8).mean()) >= 0.01
                            and float((a >= 247).mean()) >= 0.05):
                        mat['alphaMode'] = 'MASK'; mat['alphaCutoff'] = 0.5
                    materials.append(mat); mat_for_tex[ti] = len(materials)-1
                prim['material'] = mat_for_tex[ti]
            meshes.append({'name': f'g{gi}p{ii:02d}', 'primitives': [prim]})
            nodes.append({'mesh': len(meshes)-1, 'name': f'g{gi}p{ii:02d}'})
            total_v += nv; total_t += len(tris)
            part_reports.append((f'g{gi}p{ii:02d}', f'{topo} strip={ss:.2f} list={sl:.2f} tex={ti}'))
    g = {'asset': {'version': '2.0', 'generator': 'scii phase13 build_stage.py'},
         'scene': 0, 'scenes': [{'nodes': list(range(len(nodes)))}], 'nodes': nodes,
         'meshes': meshes, 'accessors': accs, 'bufferViews': views,
         'buffers': [{'byteLength': len(binbuf)}],
         'samplers': [{'magFilter': 9729, 'minFilter': 9987, 'wrapS': 10497, 'wrapT': 10497}],
         'images': images, 'textures': textures, 'materials': materials}
    js = json.dumps(g, separators=(',', ':')).encode(); js += b' ' * ((4 - len(js) % 4) % 4)
    bb = bytes(binbuf); bb += b'\x00' * ((4 - len(bb) % 4) % 4)
    g['buffers'][0]['byteLength'] = len(bb)
    js = json.dumps(g, separators=(',', ':')).encode(); js += b' ' * ((4 - len(js) % 4) % 4)
    outb = bytearray()
    outb += b'glTF' + struct.pack('<2I', 2, 12 + 8 + len(js) + 8 + len(bb))
    outb += struct.pack('<I', len(js)) + b'JSON' + js
    outb += struct.pack('<I', len(bb)) + b'BIN\x00' + bb
    open(out, 'wb').write(outb)
    print(json.dumps({'stage': fn, 'verts': total_v, 'tris': total_t,
                      'parts': len(meshes), 'images': len(images),
                      'skipped': [p for p in part_reports if 'skipped' in p[1]],
                      'topo': {t: sum(1 for _n, r in part_reports if r.startswith(t)) for t in ('strip', 'list')}}))

if __name__ == '__main__':
    main()

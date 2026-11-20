#!/usr/bin/env python3
"""Phase 14 JOB 1: assemble VMX v2 (m000) and v3 (m120) stage VMXs into
textured stage GLBs, extending the phase-13 build_stage.py discipline.

Layouts (all measured this phase; see PHASE14-STAGE-LAYOUTS.md):
- v3 (m120): standard 40 B part records; vend field = 0xFFFFFFFF
  sentinel. Vertex count = maxidx+1; verified (iptr-vptr) == nv*40 + 8
  (8 spare bytes trail the vertex block, data starts AT vptr).
- v2 (m000): 36 B part records
  [type, icnt, nodeptr, matptr, iptr, vbase, s6, s7, s8].
  Parts share one vertex stream per node (58 streams / 265 parts);
  stream vertex count = max(maxidx)+1 over sharing parts; tiling
  verified: block span is exactly nv*40 or nv*40+8 for every stream.
  - type 0: interleaved 40 B stream at vbase (pos/nrm/col/uv at
    +0/+12/+24/+28), data starts AT vbase (unit-normal verified).
  - type 4 (3 parts, node 28): split streams — color+UV at vbase
    (12 B/vert: u32 color, f32x2 uv; colors all 0xFFFFFFFF, UVs in
    [0,1]); pos+normal at s6 (32 B/vert: pos f32x3 @+0, pad 1.0,
    normal f32x3 @+16, pad 1.0; normals 156/156 unit); s6==s7==s8
    byte-identical copies (asserted).
- VXT v1 (m000/m120): 32 B texture records
  [palptr, common, flags, dataoff, D3DFMT, w/h u16 pair @+0x14,
  mips @+0x18]. Size accounting: data offsets tile exactly by full
  mip chains over all 86 m000 records (verified). Material chain is
  the same rec80 +0x08 pointer chain, record stride 32.
  m120's VXT has 0 records; its single material is color-only.
Topology per part: strip-vs-list by normal agreement (phase-3 method),
winner recorded. Textures embedded via decode_texture (level 0).
Usage: build_stage2.py <stage.bin> <out.glb> -> JSON report.
"""
import struct, sys, json, io, math, bisect
sys.path.insert(0, '/home/hatch/workspace/scii-work/p13/work')
from vxt_decode import parse_vxt, decode_texture
from PIL import Image
import numpy as np

def u16(d, o): return struct.unpack_from('<H', d, o)[0]
def u32(d, o): return struct.unpack_from('<I', d, o)[0]

def parse_vxt_v1(buf, base):
    cnt = u16(buf, base + 8)
    rec0 = u32(buf, base + 0x0c)
    recs = []
    for i in range(cnt):
        r = base + rec0 + i * 32
        pal, _common, fl08, data, fmt = struct.unpack_from('<5I', buf, r)
        w, h = struct.unpack_from('<2H', buf, r + 0x14)
        mips = struct.unpack_from('<I', buf, r + 0x18)[0]
        recs.append(dict(idx=i, pal=pal, fl08=fl08, w=w, h=h, data=data,
                         fmt=fmt, mips=mips, flags=0))
    return recs

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
    ver = d[V+4]
    assert ver in (2, 3), f'VMX version {ver} not this tool'
    vxt_rel = u32(d, V+0x18); vb = V + vxt_rel
    has_vxt = d[vb:vb+4] == b'VXT.'
    vxt_ver = d[vb+4] if has_vxt else None
    recs = []
    rec_stride = 36
    if has_vxt:
        if vxt_ver == 1:
            recs = parse_vxt_v1(d, vb); rec_stride = 32
        else:
            recs = parse_vxt(d, vb); rec_stride = 36
    rec80_base_rel = u32(d, V+0x1c); n80 = u16(d, V+0x14)
    node_base = u32(d, V+0x24); nnodes = u16(d, V+0x0A)
    nodeM = []
    for i in range(nnodes):
        M = list(struct.unpack_from('<16f', d, V + node_base + i*400 + 0x10))
        nodeM.append(M)
    def place(P, N, ni):
        M = nodeM[ni]
        P2 = [(x*M[0]+y*M[4]+z*M[8]+M[12], x*M[1]+y*M[5]+z*M[9]+M[13], x*M[2]+y*M[6]+z*M[10]+M[14]) for (x, y, z) in P]
        N2 = []
        for (x, y, z) in N:
            nx, ny, nz = x*M[0]+y*M[4]+z*M[8], x*M[1]+y*M[5]+z*M[9], x*M[2]+y*M[6]+z*M[10]
            L = math.sqrt(nx*nx+ny*ny+nz*nz)
            N2.append((nx/L, ny/L, nz/L) if L > 1e-12 else (nx, ny, nz))
        return P2, N2
    pcounts = [u16(d, V+0x0C), u16(d, V+0x0E), u16(d, V+0x10)]
    pbase = [u32(d, V+0x2C), u32(d, V+0x30), u32(d, V+0x34)]

    # ---- collect raw parts ----
    raw = []  # dict per part
    if ver == 3:
        for gi in range(3):
            for ii in range(pcounts[gi]):
                r = struct.unpack_from('<10I', d, V + pbase[gi] + ii*40)
                raw.append(dict(gi=gi, ii=ii, typ=0, icnt=r[1], node=r[2],
                                mat=r[3], iptr=r[4], vptr=r[5], vend=r[9]))
    else:  # ver == 2, 36B records
        for gi in range(3):
            for ii in range(pcounts[gi]):
                r = struct.unpack_from('<9I', d, V + pbase[gi] + ii*36)
                raw.append(dict(gi=gi, ii=ii, typ=r[0], icnt=r[1], node=r[2],
                                mat=r[3], iptr=r[4], vptr=r[5],
                                s6=r[6], s7=r[7], s8=r[8]))

    for p in raw:
        idx = list(struct.unpack_from(f"<{p['icnt']}H", d, V + p['iptr'])) if p['icnt'] else []
        p['idx'] = idx
        p['maxidx'] = max(idx) if idx else -1

    checks = []
    if ver == 3:
        for p in raw:
            assert p['vend'] == 0xFFFFFFFF, f"v3 part vend {p['vend']:#x} not sentinel"
            nv = p['maxidx'] + 1
            span = p['iptr'] - p['vptr']
            assert span == nv*40 + 8, f"v3 span {span} != nv*40+8 {nv*40+8}"
            p['nv'] = nv
            checks.append(f"v3 g{p['gi']}p{p['ii']:02d}: nv={nv} span-check OK")
    else:
        # stream vertex counts from shared maxidx; tiling verification
        starts = sorted(set([p['vptr'] for p in raw] + [p['iptr'] for p in raw] + [vxt_rel]))
        from collections import defaultdict
        streams = defaultdict(list)
        for p in raw: streams[p['vptr']].append(p)
        for vb_, ps in sorted(streams.items()):
            nv = max(p['maxidx'] for p in ps) + 1
            for p in ps: p['nv'] = nv
            nxt = starts[bisect.bisect_right(starts, vb_)]
            span = nxt - vb_
            typ = ps[0]['typ']
            if typ == 0:
                assert span in (nv*40, nv*40+8), f"stream {vb_:#x} span {span} nv {nv}"
                checks.append(f"v2 stream {vb_:#x}: {len(ps)} parts nv={nv} span={span} (nv*40{'+8' if span==nv*40+8 else ''}) OK")
            else:
                # split-stream group: verify component sizes + copy identity
                p0 = ps[0]
                assert all(p['s6'] == p0['s6'] and p['s7'] == p0['s7'] and p['s8'] == p0['s8'] for p in ps)
                assert (p0['s6'] - vb_) == nv*12, 'aux stream size'
                assert (p0['s7'] - p0['s6']) == nv*32, 'pos/nrm stream size'
                b6 = d[V+p0['s6']:V+p0['s6']+nv*32]
                assert b6 == d[V+p0['s7']:V+p0['s7']+nv*32] == d[V+p0['s8']:V+p0['s8']+nv*32], 'pos/nrm copies differ'
                checks.append(f"v2 split stream {vb_:#x}: {len(ps)} type-4 parts nv={nv} aux=12B/v posnrm=32B/v x3 identical copies OK")

    def part_tex(p):
        mp = p['mat']
        if mp == 0 or not has_vxt or not recs: return None
        mi, rem = divmod(mp - rec80_base_rel, 80)
        if rem or not (0 <= mi < n80): return None
        tp = u32(d, V + rec80_base_rel + mi*80 + 8)
        if tp == 0: return None
        ti, rem = divmod(tp - vxt_rel - 0x14, rec_stride)
        if rem or not (0 <= ti < len(recs)): return None
        return ti

    def read_verts(p):
        nv = p['nv']; P = []; N = []; UV = []; COL = []
        if p['typ'] == 4:
            for k in range(nv):
                o = V + p['s6'] + k*32
                x, y, z = struct.unpack_from('<3f', d, o)
                nx, ny, nz = struct.unpack_from('<3f', d, o + 16)
                oa = V + p['vptr'] + k*12
                col = u32(d, oa)
                uu, vv = struct.unpack_from('<2f', d, oa + 4)
                P.append((x, y, z)); N.append((nx, ny, nz)); UV.append((uu, vv))
                COL.append(((col >> 16 & 255)/255, (col >> 8 & 255)/255, (col & 255)/255, (col >> 24 & 255)/255))
        else:
            for k in range(nv):
                o = V + p['vptr'] + k*40
                x, y, z, nx, ny, nz = struct.unpack_from('<6f', d, o)
                col = u32(d, o + 24)
                uu, vv = struct.unpack_from('<2f', d, o + 28)
                P.append((x, y, z)); N.append((nx, ny, nz)); UV.append((uu, vv))
                COL.append(((col >> 16 & 255)/255, (col >> 8 & 255)/255, (col & 255)/255, (col >> 24 & 255)/255))
        return P, N, UV, COL

    binbuf = bytearray(); views = []; accs = []; meshes = []; nodes = []
    images = []; textures = []; materials = []
    mat_for_tex = {}
    part_reports = []
    total_v = total_t = 0
    # shared streams: emit each stream's verts once per part (parts index
    # the shared stream directly; duplicating per part keeps the GLB
    # self-contained exactly like the v4 builder's per-part streams)

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

    for p in raw:
        if p['icnt'] == 0:
            part_reports.append((f"g{p['gi']}p{p['ii']:02d}", 'skipped: zero indices')); continue
        P, N, UV, COL = read_verts(p)
        if ver in (2, 3) and p['typ'] != 4:
            ni = (p['node'] - node_base) // 400
            if 0 <= ni < nnodes:
                P, N = place(P, N, ni)
        nv = p['nv']
        idx = p['idx']
        ts = strip_to_tris(idx); tl = list_to_tris(idx)
        ss, sl = score(ts, P, N), score(tl, P, N)
        tris, topo = (ts, 'strip') if ss >= sl else (tl, 'list')
        flat = [i for t in tris for i in t]
        pa = add_acc(add_view(b''.join(struct.pack('<3f', *q) for q in P), 34962), 5126, 'VEC3', nv,
                     [min(q[k] for q in P) for k in range(3)], [max(q[k] for q in P) for k in range(3)])
        na = add_acc(add_view(b''.join(struct.pack('<3f', *q) for q in N), 34962), 5126, 'VEC3', nv)
        ta = add_acc(add_view(b''.join(struct.pack('<2f', *q) for q in UV), 34962), 5126, 'VEC2', nv)
        ca = add_acc(add_view(b''.join(struct.pack('<4f', *q) for q in COL), 34962), 5126, 'VEC4', nv)
        ia = add_acc(add_view(b''.join(struct.pack('<I', i) for i in flat), 34963), 5125, 'SCALAR', len(flat))
        prim = {'attributes': {'POSITION': pa, 'NORMAL': na, 'TEXCOORD_0': ta, 'COLOR_0': ca},
                'indices': ia, 'mode': 4}
        ti = part_tex(p)
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
        meshes.append({'name': f"g{p['gi']}p{p['ii']:02d}", 'primitives': [prim]})
        nodes.append({'mesh': len(meshes)-1, 'name': f"g{p['gi']}p{p['ii']:02d}"})
        total_v += nv; total_t += len(tris)
        part_reports.append((f"g{p['gi']}p{p['ii']:02d}", f'{topo} strip={ss:.2f} list={sl:.2f} tex={ti} type={p["typ"]}'))

    g = {'asset': {'version': '2.0', 'generator': 'scii phase14 build_stage2.py'},
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
    print(json.dumps({'stage': fn, 'vmx_version': ver, 'verts': total_v, 'tris': total_t,
                      'parts': len(meshes), 'images': len(images),
                      'parts_source': len(raw),
                      'skipped': [x for x in part_reports if 'skipped' in x[1]],
                      'topo': {t: sum(1 for _n, r in part_reports if r.startswith(t)) for t in ('strip', 'list')},
                      'checks': checks}))

if __name__ == '__main__':
    main()

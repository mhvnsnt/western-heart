#!/usr/bin/env python3
"""
DOA4 Phase-4 assembler: GeoDecl vertex pools -> assembled character GLB.

Supersedes the phase-2/3 pool carving. Everything below is verified against
real package bytes (chrone pkg00 worked end to end; see
PHASE4-GEODECL-FINDINGS-2026-10-21.md for the evidence trail).

FORMAT FACTS (chrone pkg00 unless noted)
----------------------------------------
1. XPR2 directory records are 16 bytes (magic, f1, f2, f3). f1 is the
   XPR2-relative offset of a 20-byte descriptor (flags, addr, size, type, 0);
   type 0x10001=VBUF, 0x20001=IBUF, 0x30001=TX2D. f1 is NOT a data offset --
   the phase-2/3 misreading that produced the +/-3e38 spiked pools.
   (stg pkg00: every record's f3 = 8260, a package tag, not a vertex count.)
2. Vertex segments are NOT at descriptor-addr-derived file offsets (there is
   no single addr->file base; VBUF and IBUF bases differ). Segments are
   stored in replicated sets in GeoDecl order, each in a slot of
   align(vtx_count * stride, 0x1000). A candidate segment VERIFIES when,
   parsed at its decl's stride, >=99.5% of vertices have unit-length
   normals AND lie inside the object's ObjInfo bounds (segment bboxes
   share exact planes with the bounds). Positions are stored in model
   bind space -- the very space ObjInfo bounds describe. The Hie world
   matrices are the skinning skeleton, NOT bind placement (applying them
   pulls the assembled figure apart; verified by render).
3. GeoDecl record (sub-chunk inside ObjGeo at ObjGeo+0x28):
   +0x00 payload size, +0x04 = 1, +0x08 global decl index,
   +0x0c segment index count, +0x10 element count INCLUDING END,
   +0x14 segment vertex count, +0x18 stream (0/1/3), +0x20 flag.
   Elements at +0x30, 12 bytes each: (byte_offset, buffer_tag, packed_usage).
   buffer_tag in {0x2A23B9, 0x2C23A5} -- two global attribute planes A/B.
   packed_usage: hi u16 = D3D usage (0=POSITION, 1=BLENDWEIGHT, 3=NORMAL,
   5=TEXCOORD, 6=TANGENT), next byte = usage index. END = (0x00FF0000,
   0xFFFFFFFF, 0). Element sizes: POSITION/NORMAL/TANGENT = 12B,
   TEXCOORD = 8B, BLENDWEIGHT = 8B (2 floats) or 12B (3 floats), varying
   per decl; the segment validator arbitrates. The 16-byte record tail
   carries the VBUF descriptor counter (desc = counter + 1); which tail
   slot holds it rotates with the decl's element count.
4. IBUF file mapping (chrone pkg00): file = (addr & ~3) - 0x8C4000.
   Stream-3 index data is sequential triangle lists (0,1,2,FFFF,3,4,5,...);
   stream-1/0 data is genuine strip walks. Strip->decl pairing uses FULL
   vertex coverage first, geometry score second (the model reuses parts,
   so score-only pairing produces confident garbage). Confirmed pairs are
   listed in the findings doc.
5. BLENDWEIGHT (usage 1) is real skinning data: values in [0,1], per-vertex
   rows sum to 1.000; 20/68 chrone pkg00 decls carry it (2 or 3 influences).
   BLENDINDICES (usage 2) occurs in ZERO of the 68 decls -- the bone-index
   source is not in the vertex streams (G3 stays open on that evidence).
6. Exported triangles are winding-normalized against the file's vertex
   normals: garment pieces carry inner+outer surfaces with mixed winding
   (the game renders double-sided; glTF consumers shade single-sided).

USAGE
-----
    python3 doa4_decode3.py / doa4_assemble.py first (phase 3) to produce
    the assembly graph JSON for the package, then:
    python3 doa4_assemble2.py <package.bin> <graph.json> <out.glb>

<package.bin> contains the package span (data section through Hie end).
chrone pkg00: chrone.afs bytes [0, 0xF8C000), graph from doa4_assemble.py.
"""
import numpy as np, struct, json, sys

ELEM_SIZE = {0: 12, 3: 12, 6: 12, 5: 8, 2: 4}   # BLENDWEIGHT(1): try 8 and 12
IBUF_BASE_SUB = 0x8C4000                        # chrone pkg00


def u32(d, o):
    return struct.unpack('>I', d[o:o + 4])[0]


def parse_directory(d, xp):
    recs = []
    pos = xp
    while pos < len(d) - 16:
        magic = d[pos:pos + 4]
        if magic in (b'XPR2', b'USER', b'TX2D', b'VBUF', b'IBUF'):
            f1, f2, f3 = struct.unpack('>3I', d[pos + 4:pos + 16])
            recs.append((magic.decode(), f1))
            pos += 16
        elif magic == b'\x00\x00\x00\x00':
            pos += 16
        else:
            break
    return recs


def parse_decls(d, g):
    decls = []
    for obj in g['objects']:
        og = obj['objgeo']['offset']
        gd = og + obj['objgeo']['geodecl_off']
        gcnt = u32(d, gd + 0x14)
        gtab = u32(d, gd + 0x20)
        for i in range(gcnt):
            rec = gd + u32(d, gd + gtab + i * 4)
            nelem = u32(d, rec + 0x10)
            elems = [struct.unpack('>3I', d[rec + 0x30 + e * 12:rec + 0x30 + e * 12 + 12])
                     for e in range(nelem)]
            real = [(e[0], e[2] >> 16, (e[2] >> 8) & 0xFF) for e in elems
                    if e[1] != 0xFFFFFFFF]
            decls.append(dict(decl_id=u32(d, rec + 0x08), obj=obj['index'],
                              stream=u32(d, rec + 0x18), vtx=u32(d, rec + 0x14),
                              idx=u32(d, rec + 0x0c), elems=real))
    return decls


def strides(dd):
    out = set()
    for bw in (8, 12):
        sizes = dict(ELEM_SIZE); sizes[1] = bw
        out.add(max(boff + sizes.get(u, 4) for (boff, u, ui) in dd['elems']))
    return sorted(out)


def validate(d, off, dd, st, lo, hi):
    nv = dd['vtx']
    if off < 0 or off + nv * st > len(d):
        return 0.0
    raw = np.frombuffer(d[off:off + nv * st], dtype='>f4').astype(np.float32)
    A = raw.reshape(nv, st // 4)
    P = A[:, :3].astype(np.float64)
    if not np.isfinite(P).all():
        return 0.0
    inside = ((P >= lo - 0.02) & (P <= hi + 0.02)).all(axis=1).mean()
    if inside < 0.99:
        return float(inside)
    if st > 12:
        N = A[:, 3:6].astype(np.float64)
        nl = np.sqrt((N ** 2).sum(axis=1))
        return float(min(inside, (np.abs(nl - 1) < 0.06).mean()))
    return float(inside)


def find_segments(d, g, decls):
    bnds = {}
    for obj in g['objects']:
        b = obj['objinfo']
        c = np.array(b['bounds_center']); e = np.array(b['bounds_extents'])
        bnds[obj['index']] = (c - e, c + e)
    seg = {}
    for dd in decls:
        lo, hi = bnds[dd['obj']]
        for off in range(0x8000, len(d), 0x1000):
            for st in strides(dd):
                if validate(d, off, dd, st, lo, hi) >= 0.995:
                    seg[dd['decl_id']] = (off, st)
                    break
            if dd['decl_id'] in seg:
                break
    return seg


def strip_tris(s, nv):
    tris = []; run = []
    for v in s:
        if v == 0xFFFF:
            for i in range(len(run) - 2):
                a, b, c = run[i], run[i + 1], run[i + 2]
                if len({a, b, c}) == 3 and max(a, b, c) < nv:
                    tris.append((a, b, c) if i % 2 == 0 else (a, c, b))
            run = []
        else:
            run.append(int(v))
    for i in range(len(run) - 2):
        a, b, c = run[i], run[i + 1], run[i + 2]
        if len({a, b, c}) == 3 and max(a, b, c) < nv:
            tris.append((a, b, c) if i % 2 == 0 else (a, c, b))
    return tris


def seq_tris(idx, nv):
    tris = []; cnt = 0; i = 0
    while cnt + 2 < idx and i + 2 < nv:
        tris.append((i, i + 1, i + 2)); i += 3; cnt += 4
    return tris


def write_glb(path, meshes):
    binparts = []; views = []; accs = []; gltf_meshes = []; nodes = []

    def add_view(data_bytes, target):
        off = sum(len(p) for p in binparts)
        pad = (4 - len(data_bytes) % 4) % 4
        binparts.append(data_bytes + b'\x00' * pad)
        views.append({'buffer': 0, 'byteOffset': off,
                      'byteLength': len(data_bytes), 'target': target})
        return len(views) - 1

    def add_acc(view, comp, count, typ, mn=None, mx=None):
        a = {'bufferView': view, 'componentType': comp, 'count': count, 'type': typ}
        if mn is not None: a['min'] = mn
        if mx is not None: a['max'] = mx
        accs.append(a); return len(accs) - 1

    for (name, P, N, UV, T) in meshes:
        pos32 = P.astype(np.float32)
        pv = add_view(pos32.tobytes(), 34962)
        pa = add_acc(pv, 5126, len(pos32), 'VEC3',
                     pos32.min(axis=0).tolist(), pos32.max(axis=0).tolist())
        prim = {'attributes': {'POSITION': pa}}
        if N is not None:
            nv = add_view(N.astype(np.float32).tobytes(), 34962)
            prim['attributes']['NORMAL'] = add_acc(nv, 5126, len(N), 'VEC3')
        if UV is not None:
            uvv = add_view(UV.astype(np.float32).tobytes(), 34962)
            prim['attributes']['TEXCOORD_0'] = add_acc(uvv, 5126, len(UV), 'VEC2')
        idx32 = T.reshape(-1).astype(np.uint32)
        iv = add_view(idx32.tobytes(), 34963)
        prim['indices'] = add_acc(iv, 5125, len(idx32), 'SCALAR')
        prim['mode'] = 4
        gltf_meshes.append({'name': name, 'primitives': [prim]})
        nodes.append({'mesh': len(gltf_meshes) - 1, 'name': name})
    blob = b''.join(binparts)
    gltf = {'asset': {'version': '2.0', 'generator': 'doa4_assemble2 (phase 4)'},
            'scene': 0, 'scenes': [{'nodes': list(range(len(nodes)))}],
            'nodes': nodes, 'meshes': gltf_meshes,
            'buffers': [{'byteLength': len(blob)}],
            'bufferViews': views, 'accessors': accs}
    js = json.dumps(gltf).encode()
    js += b' ' * ((4 - len(js) % 4) % 4)
    out = struct.pack('<4sII', b'glTF', 2, 12 + 8 + len(js) + 8 + len(blob))
    out += struct.pack('<II', len(js), 0x4E4F534A) + js
    out += struct.pack('<II', len(blob), 0x004E4942) + blob
    open(path, 'wb').write(out)
    print('wrote', path, len(out), 'bytes')


def main():
    if len(sys.argv) != 5:
        raise SystemExit('usage: doa4_assemble2.py <package.bin> <graph.json> '
                         '<xpr2_offset> <out.glb>')
    d = open(sys.argv[1], 'rb').read()
    g = json.load(open(sys.argv[2]))
    xp = int(sys.argv[3], 0)
    out_path = sys.argv[4]
    recs = parse_directory(d, xp)

    def desc(f1):
        return struct.unpack('>5I', d[xp + f1:xp + f1 + 20])

    ibd = [desc(r[1]) for r in recs if r[0] == 'IBUF']

    def desc_full(di):
        w0, addr, size, typ, _ = ibd[di]
        f = (addr & ~3) - IBUF_BASE_SUB
        return np.frombuffer(d[f:f + size], dtype='>u2').astype(np.int64)

    decls = parse_decls(d, g)
    seg = find_segments(d, g, decls)
    print(f'segments located: {len(seg)}/{len(decls)}')

    def parse_seg(dd):
        off, st = seg[dd['decl_id']]
        nv = dd['vtx']
        raw = np.frombuffer(d[off:off + nv * st], dtype='>f4').astype(np.float32)
        A = raw.reshape(nv, st // 4)
        out = {}
        for (boff, usage, uidx) in dd['elems']:
            fo = boff // 4
            if usage == 0: out['pos'] = A[:, fo:fo + 3].astype(np.float64)
            elif usage == 3: out['nrm'] = A[:, fo:fo + 3].astype(np.float32)
            elif usage == 5: out[f'uv{uidx}'] = A[:, fo:fo + 2].astype(np.float32)
        return out

    def best_strip(dd, P):
        diag = np.linalg.norm(P.max(axis=0) - P.min(axis=0))
        idx = dd['idx']; best = None
        for di in range(len(ibd)):
            full = desc_full(di)
            if len(full) < idx: continue
            s = full[:idx]
            sv = s[s != 0xFFFF]
            if not len(sv) or int(sv.max()) >= dd['vtx']: continue
            vals = [int(v) for v in s if v != 0xFFFF]
            if vals == list(range(len(vals))): continue
            cov = len(set(sv.tolist())) / dd['vtx']
            if cov < 0.70: continue
            tris = strip_tris(s, dd['vtx'])
            if len(tris) < 3: continue
            T = P[np.array(tris)]
            e = (np.linalg.norm(T[:, 0] - T[:, 1], axis=1) +
                 np.linalg.norm(T[:, 1] - T[:, 2], axis=1) +
                 np.linalg.norm(T[:, 2] - T[:, 0], axis=1)) / 3
            sc = float(e.mean() / diag)
            key = (cov, -sc)
            if best is None or key > best[0]:
                best = (key, di, tris, cov, sc)
        return best

    meshes = []
    for dd in sorted(decls, key=lambda x: x['decl_id']):
        did = dd['decl_id']
        if did not in seg:
            print(f'decl{did} obj{dd["obj"]}: NO SEGMENT (omitted)')
            continue
        s = parse_seg(dd); P = s['pos']
        if dd['stream'] == 3:
            tris = seq_tris(dd['idx'], dd['vtx']); how = 'seq'
        else:
            b = best_strip(dd, P)
            if b is None:
                print(f'decl{did} obj{dd["obj"]}: NO STRIP (omitted)')
                continue
            tris = b[2]; how = f'desc#{b[1]} cov {b[3]:.2f} score {b[4]:.3f}'
        tris = np.array(tris, dtype=np.int64)
        if 'nrm' in s and len(tris):
            N = s['nrm'].astype(np.float64)
            v0, v1, v2 = P[tris[:, 0]], P[tris[:, 1]], P[tris[:, 2]]
            fn = np.cross(v1 - v0, v2 - v0)
            vn = N[tris[:, 0]] + N[tris[:, 1]] + N[tris[:, 2]]
            bad = (fn * vn).sum(axis=1) < 0
            tris[bad] = tris[bad][:, [0, 2, 1]]
        meshes.append((f"obj{dd['obj']}_decl{did}", P, s.get('nrm'),
                       s.get('uv0'), tris))
        print(f'decl{did} obj{dd["obj"]} s{dd["stream"]}: {len(tris)} tris {how}')
    write_glb(out_path, meshes)


if __name__ == '__main__':
    main()

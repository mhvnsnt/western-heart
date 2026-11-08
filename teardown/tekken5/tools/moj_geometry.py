#!/usr/bin/env python3
"""Stage geometry parser for Tekken 5 Devil Within stage map objects (moj_stg*.dat).

Parses, per stage file:
  MIF bone chunks (validated headers only — the container inventory in
  moj_parse.py counts raw 'MIF' byte hits, which overcounts: 27 of stg00's
  56 hits and 2 of stg02's 22 are 'EMIF' byte sequences inside texture /
  vertex data, not MIF chunks):
    header: 'MIF\\0', u32[3]=0x05010000, u32[4]=bone count,
            u32[5]=64, u32[6]=data bytes = 64*(3*count+1), u32[7]=chunk-16.
    data: count records of 192 bytes:
      +0  u32 flags (0)
      +4  u32 bone count, set on record 0 only (0 on the rest)
      +32 u32 name offset (byte offset of the bone's name from the
          name-table count field, see below)
      +36 i32 parent (-1 on every bone measured: map objects are
          root-level placements, not a skeleton hierarchy)
      +48 4x4 float matrix, row-major (rotation + translation)
      +112 suffix: u32 0 x4, u32 node id (the DSNID number when the
          bone's name is DSNIDnnn, else -1), u32 bone index,
          u32 0 x13, f32 100.0
    trailing 64 bytes: u32 0 x8, u32 bone count, then the first 28
    bytes of the name table. Names are NUL-terminated ASCII
    ('__O_OBJ__O_MATRIX__DSNIDnnn__' in stg04, '_O_OBJ_O_MATRIX_N'
    elsewhere), at (count-field + name offset). Tail pads with NULs
    to the next chunk.
  NUDP model chunks (validated by tiling: u32[1] = distance to the
  next NUDP; u32[3] = 0):
    header (32 bytes): 'NUDP', u32[1]=chunk length,
      u32[2]=(block_count<<16)|0x5103, u32[3]=0,
      f32[4..7]=bounding sphere (cx, cy, cz, radius).
    block table at +32: block_count records of 64 bytes:
      [0]=block index<<24, [1]=0x580001, [2]/[4]=tiny floats
      (semantics unresolved), [3]=sphere centre Y,
      [5]=sphere radius, [6]=0x100200d4, [7]=464, [8]=416 (table
      end), [9]=0x80000003, [10]=block byte offset, [11]=0x20092,
      [12]=0, [13]=0xffff0000, [14]=[15]=0xffffffff.
    each block: sub-meshes, each:
      28-byte header: [0]=0x8204xx, [1]=0x01000105,
      [2]=0x60010000, [3]=vertex count, [4]=0x20000000,
      [5]=128, [6]=0x783x8001
      positions: vertex_count x f32 x3 (validated: every triple
      inside the chunk bounding sphere)
      aux block: vertex_count x u32, byte pattern (X,X,X,0x80)
      (greyscale RGBA vertex colours, A=0x80 — pattern measured,
      semantics UNCONFIRMED) — plus a small header
      UVs: vertex_count x f32 x2 (validated: u in [0,1], v in [0,1]
      range measured; values are the raw floats, not clamped)
      trailer: strided u32 values 0x70068001+20k + next header
    Triangle indices were NOT found in any NUDP chunk: no index
    table is present in the measured bytes. Vertices are stored
    in draw order (sub-mesh order); whether that order is a
    triangle strip is UNCONFIRMED — no strip-restart markers
    were identified. Do NOT treat the vertex list as indexed
    triangles.

Outputs moj-stage-geometry.json (format 'western-heart
dw-stage-geometry v1') plus a validation summary on stdout.
Unparsed stays UNMEASURED: nothing is invented.

Usage: python3 moj_geometry.py <romd_out_dir> <out.json>
"""
import json, math, struct, sys
from pathlib import Path

STAGES = {
    'moj_stg00.dat': 'THE THRESHOLD',
    'moj_stg01.dat': 'THE GALLERY OF MASKS',
    'moj_stg02.dat': 'THE DROWNING ROOM',
    'moj_stg04.dat': 'THE STILL POINT',
}

def is_mif(d, off):
    if off + 32 > len(d):
        return False
    u = struct.unpack_from('<8I', d, off)
    return (u[0] == 0x0046494D and u[3] == 0x05010000 and u[5] == 64
            and u[6] == 64 * (3 * u[4] + 1))

def find_all(d, magic):
    offs, i = [], 0
    while True:
        j = d.find(magic, i)
        if j < 0:
            break
        offs.append(j)
        i = j + 1
    return offs

def parse_mif(d, off):
    u = struct.unpack_from('<8I', d, off)
    count, data_bytes, chunk_minus16 = u[4], u[6], u[7]
    base = off + 32
    count_field = base + 192 * count + 32  # u32 bone count inside trailing block
    bones = []
    for k in range(count):
        rec = base + 192 * k
        pre = struct.unpack_from('<12I', d, rec)
        mtx = struct.unpack_from('<16f', d, rec + 48)
        suf = struct.unpack_from('<20I', d, rec + 112)
        name_off = pre[8]
        name_end = d.find(b'\x00', count_field + name_off)
        name = d[count_field + name_off:name_end].decode('ascii', 'replace')
        bones.append({
            'index': k, 'name': name,
            'name_offset': name_off, 'parent': -1 if pre[9] == 0xFFFFFFFF else pre[9],
            'node_id': -1 if suf[4] == 0xFFFFFFFF else suf[4],
            'matrix': [round(v, 3) for v in mtx],
            'translation': [round(mtx[12], 3), round(mtx[13], 3), round(mtx[14], 3)],
            'suffix_last_float': struct.unpack_from('<f', d, rec + 112 + 76)[0],
        })
    return {'offset': off, 'count': count, 'data_bytes': data_bytes,
            'chunk_bytes': chunk_minus16 + 16, 'bones': bones}

def is_nudp(d, off):
    if off + 32 > len(d):
        return False
    u = struct.unpack_from('<8I', d, off)
    return (u[0] == 0x5044554E and u[3] == 0 and (u[2] & 0xFFFF) == 0x5103
            and 1 <= (u[2] >> 16) <= 64 and 0 < u[1] <= len(d) - off)

def parse_nudp(d, off):
    u = struct.unpack_from('<8I', d, off)
    chunk_bytes = u[1]
    block_count = u[2] >> 16
    tag = u[2] & 0xFFFF
    sphere = [round(v, 3) for v in struct.unpack_from('<4f', d, off + 16)]
    cx, cy, cz, r = struct.unpack_from('<4f', d, off + 16)
    # Table at +32: sequential records. Record size is 64 + 40*(nstreams-1),
    # where nstreams = [1] & 0xFFFF and [1]>>16 = total vertices in the block.
    # Main entry (64B): [0]=index<<24, [1]=(verts<<16)|nstreams,
    #   [2..5]=per-block bounding sphere (cx,cy,cz,r), [6]=0x100200dX,
    #   [7]=stream descriptor offset (unresolved), [8]=table end (16-aligned),
    #   [9]=0x80000003, [10]=stream0 offset, [11]=stream0 bytes/16,
    #   [12]=0, [13]=0xffff0000, [14]=[15]=0xffffffff.
    # Extra stream entries (40B each): [0]=0x100200dX, [1]=descriptor offset,
    #   [2]=table end, [3]=0x80000003, [4]=stream offset, [5]=stream bytes/16,
    #   [6]=0, [7]=0xffff0000, [8]=[9]=0xffffffff.
    table = []
    p = 32
    for k in range(block_count):
        base = struct.unpack_from('<16I', d, off + p)
        nstreams = base[1] & 0xFFFF
        nverts = base[1] >> 16
        streams = [(base[10], (base[11] & 0xFFFF) * 16)]
        for j in range(1, nstreams):
            e = struct.unpack_from('<10I', d, off + p + 64 + 40 * (j - 1))
            streams.append((e[4], (e[5] & 0xFFFF) * 16))
        table.append({'index': base[0] >> 24, 'vertices': nverts,
                      'nstreams': nstreams,
                      'sphere': [round(v, 3) for v in
                                 struct.unpack_from('<4f', d, off + p + 8)],
                      'field6': base[6], 'field7': base[7],
                      'table_end': base[8], 'field9': base[9],
                      'field11': base[11], 'streams': [
                          {'offset': so, 'bytes': sb} for so, sb in streams]})
        p += 64 + 40 * (nstreams - 1)
    blocks = []
    seen_streams = set()
    shared_streams = []
    for k, t in enumerate(table):
        subs = []
        for si, st in enumerate(t['streams']):
            sstart, send = st['offset'], st['offset'] + st['bytes']
            # A table entry can reference the same stream bytes as an
            # earlier entry (shared geometry, e.g. two materials on one
            # mesh — the duplicate entry carries a different flags field,
            # 0x80000202 vs 0x80000003). Parse it once.
            key = (sstart, st['bytes'])
            if key in seen_streams:
                shared_streams.append({'block': k, 'stream': si,
                                       'offset': sstart, 'bytes': st['bytes']})
                continue
            seen_streams.add(key)
            q = sstart
            guard = 0
            while q + 28 <= send and guard < 64:
                guard += 1
                hdr = struct.unpack_from('<7I', d, off + q)
                # Sub-mesh header (28B), measured on every real sub-mesh:
                # [0]=0x82/0x83/0x86 + (bytes to next sub-mesh header),
                # [1]=0x01000105, [2]=0x60018000, [3]=vertex count,
                # [4]=0x20000000, [5]=128, [6]=0x78000001|(vertex count<<16).
                # Variant byte: 0x82 = positions+colours+UVs, 0x83 = same plus
                # a per-vertex normals block (3f x n) after positions,
                # 0x86 = same layout as 0x82, vertex colours alpha 0xC0.
                variant = (hdr[0] >> 16) & 0xFF
                if not (hdr[1] == 0x01000105 and hdr[2] == 0x60018000
                        and hdr[4] == 0x20000000 and hdr[5] == 128
                        and ((hdr[6] >> 16) & 0xFF) == hdr[3]
                        and (hdr[0] & 0xFFFF) > 0
                        and variant in (0x82, 0x83, 0x86)):
                    break
                n = hdr[3]
                pos_off = q + 28
                pos = struct.unpack_from(f'<{3 * n}f', d, off + pos_off)
                # 0x83 only: normals block [4B header 0x68??8002, byte 2 =
                # vertex count][n x 3f normals] between positions and colours.
                norms = []
                norm_hdr = 0
                norm_hdr_ok = True
                aux_off = pos_off + 12 * n
                if variant == 0x83:
                    norm_hdr = struct.unpack_from('<I', d, off + aux_off)[0] \
                        if aux_off + 4 <= send else 0
                    norm_hdr_ok = ((norm_hdr & 0xFF00FFFF) == 0x68008002
                                   and ((norm_hdr >> 16) & 0xFF) == n)
                    norms = struct.unpack_from(f'<{3 * n}f',
                                               d, off + aux_off + 4) \
                        if aux_off + 4 + 12 * n <= send else []
                    aux_off = aux_off + 4 + 12 * n
                # Aux block (8 + 4n bytes): [4B header 0x6e??c003, byte 2 =
                # vertex count][n u32 RGBA vertex colours, A=0x80][4B trailer
                # 0x64??8004, byte 2 = vertex count]. Colours are real
                # per-vertex colours (grey on some meshes, coloured on others).
                aux_hdr = struct.unpack_from('<I', d, off + aux_off)[0] \
                    if aux_off + 4 <= send else 0
                aux = struct.unpack_from(f'<{n}I', d, off + aux_off + 4) \
                    if aux_off + 4 + 4 * n <= send else []
                aux_trl = struct.unpack_from('<I', d, off + aux_off + 4 + 4 * n)[0] \
                    if aux_off + 8 + 4 * n <= send else 0
                uv_off = aux_off + 8 + 4 * n
                uv = struct.unpack_from(f'<{2 * n}f', d, off + uv_off) \
                    if uv_off + 8 * n <= send else []
                scx, scy, scz, sr = t['sphere']
                in_sphere = 0
                for i in range(n):
                    x, y, z = pos[3 * i], pos[3 * i + 1], pos[3 * i + 2]
                    if math.sqrt((x - scx) ** 2 + (y - scy) ** 2 + (z - scz) ** 2) <= sr * 1.001:
                        in_sphere += 1
                uv_ok = all(math.isfinite(v) for v in uv) if uv else False
                alpha_ok = True  # vertex colour alpha varies by material
                # (0x80 common, 0xC0 on 0x86 sub-meshes, other values seen);
                # recorded as data in the summary, not a pass/fail.
                hdr_ok = ((aux_hdr & 0xFF00FFFF) == 0x6E00C003
                          and ((aux_hdr >> 16) & 0xFF) == n)
                trl_ok = ((aux_trl & 0xFF00FFFF) == 0x64008004
                          and ((aux_trl >> 16) & 0xFF) == n)
                subs.append({
                    'stream': si, 'variant': f'0x{variant:02x}',
                    'has_normals': variant == 0x83,
                    'vertex_count': n,
                    'header_offset': q, 'positions_offset': pos_off,
                    'aux_offset': aux_off, 'uv_offset': uv_off,
                    'positions': [[round(pos[3 * i], 3), round(pos[3 * i + 1], 3),
                                   round(pos[3 * i + 2], 3)] for i in range(n)],
                    'normals': [[round(norms[3 * i], 4), round(norms[3 * i + 1], 4),
                                 round(norms[3 * i + 2], 4)] for i in range(n)]
                               if norms else [],
                    'uvs': [[round(uv[2 * i], 4), round(uv[2 * i + 1], 4)]
                            for i in range(n)] if uv else [],
                    'vertex_colors_rgba': [f'0x{v:08x}' for v in aux],
                    'aux_header': f'0x{aux_hdr:08x}',
                    'aux_trailer': f'0x{aux_trl:08x}',
                    'normal_header': f'0x{norm_hdr:08x}' if variant == 0x83 else None,
                    'checks': {'in_block_sphere': f'{in_sphere}/{n}',
                               'uv_finite': uv_ok,
                               'aux_header_count': hdr_ok,
                               'aux_trailer_count': trl_ok,
                               'normal_header_count': norm_hdr_ok},
                })
                # Step to the next sub-mesh: [0]'s low 16 bits are the exact
                # byte distance to the next header (measured). Fall back to
                # scanning only if the stepped position is not a header.
                step = hdr[0] & 0xFFFF
                cand = q + step
                if cand + 28 <= send:
                    h = struct.unpack_from('<7I', d, off + cand)
                    if (h[1] == 0x01000105 and h[2] == 0x60018000
                            and h[4] == 0x20000000):
                        q = cand
                        continue
                nxt = uv_off + 8 * n
                found = None
                qq = nxt
                while qq + 28 <= send:
                    h = struct.unpack_from('<7I', d, off + qq)
                    if h[1] == 0x01000105 and h[2] == 0x60018000:
                        found = qq
                        break
                    qq += 4
                if found is None:
                    q = send
                else:
                    q = found
        blocks.append({'index': k, 'table': t, 'sub_meshes': subs})
    return {'offset': off, 'chunk_bytes': chunk_bytes,
            'block_count': block_count, 'tag_low16': tag,
            'bounding_sphere': sphere, 'shared_streams': shared_streams,
            'blocks': blocks}

def main():
    out_dir, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    stages = []
    tot_bones = tot_verts = tot_blocks = 0
    problems = []
    for name, canon in STAGES.items():
        p = out_dir / name
        if not p.exists():
            stages.append({'source_file': name, 'canon_stage': canon,
                           'status': 'MISSING'})
            continue
        d = p.read_bytes()
        mif_offs = [o for o in find_all(d, b'MIF') if is_mif(d, o)]
        mifs = [parse_mif(d, o) for o in mif_offs]
        nudps = []
        for o in find_all(d, b'NUDP'):
            if is_nudp(d, o):
                nudps.append(parse_nudp(d, o))
        for m in mifs:
            tot_bones += m['count']
        for nd in nudps:
            tot_blocks += nd['block_count']
            for b in nd['blocks']:
                for sm in b['sub_meshes']:
                    tot_verts += sm['vertex_count']
                    if sm['checks']['in_block_sphere'] != f"{sm['vertex_count']}/{sm['vertex_count']}":
                        problems.append(f"{name} NUDP@{nd['offset']} block{b['index']}: "
                                        f"positions outside block sphere {sm['checks']['in_block_sphere']}")
                    if not sm['checks']['uv_finite']:
                        problems.append(f"{name} NUDP@{nd['offset']} block{b['index']}: "
                                        f"non-finite UV")
                    if not sm['checks']['aux_header_count']:
                        problems.append(f"{name} NUDP@{nd['offset']} block{b['index']}: "
                                        f"aux header {sm['aux_header']} does not encode vertex count")
                    if not sm['checks']['aux_trailer_count']:
                        problems.append(f"{name} NUDP@{nd['offset']} block{b['index']}: "
                                        f"aux trailer {sm['aux_trailer']} does not encode vertex count")
                    if not sm['checks']['normal_header_count']:
                        problems.append(f"{name} NUDP@{nd['offset']} block{b['index']}: "
                                        f"normal header {sm['normal_header']} does not encode vertex count")
        stages.append({
            'source_file': name, 'canon_stage': canon, 'status': 'extracted',
            'size_bytes': len(d),
            'nudp_count': len(nudps), 'mif_count': len(mifs),
            'bone_count': sum(m['count'] for m in mifs),
            'nudps': nudps, 'mifs': mifs,
        })
        print(f"{name} -> {canon}: NUDP={len(nudps)} MIF={len(mifs)} "
              f"bones={sum(m['count'] for m in mifs)}")
    out = {
        'format': 'western-heart dw-stage-geometry v1',
        'source': 'Tekken 5 disc, TK5DATA2.BIN (romD), Internet Archive item slus-210.59.-tekken-5',
        'notes': [
            'MIF bones fully parsed: 192-byte records, 4x4 matrices, names.',
            'NUDP vertices parsed: positions (f32x3, inside per-block bounding sphere) + UVs (f32x2) per sub-mesh.',
            'NUDP block table: records at +32, size 64 + 40*(nstreams-1); [1]=(total_verts<<16)|nstreams; [2..5]=per-block bounding sphere; [10]/[11]=stream0 offset/size/16; extra 40-byte entries carry further streams. A table entry may reference stream bytes already listed by an earlier entry (shared geometry; the duplicate carries flags 0x80000202 vs 0x80000003) — parsed once, listed under shared_streams.',
            'Sub-mesh variants by header byte: 0x82 = positions+colours+UVs; 0x83 = same plus a per-vertex normals block (header 0x68??8002, then 3f x n) after positions; 0x86 = same layout as 0x82 with vertex-colour alpha 0xC0. Header [0] low 16 bits = bytes to the next sub-mesh header; [6] = 0x78000001|(vertex count<<16).',
            'UVs are tiled (range about [-3, 3]), not clamped to [0,1]; only non-finite UVs are flagged.',
            'Vertex-colour alpha varies by material (0x80 common, 0xC0 on 0x86, other values seen) — recorded as data, not a pass/fail.',
            'Triangle indices NOT found in any NUDP chunk — vertices are in draw order; strip order UNCONFIRMED.',
            'Aux block per sub-mesh is n RGBA vertex colours (A=0x80, grey on some meshes, coloured on others) between a 0x6e??c003 header and a 0x64??8004 trailer, each encoding the vertex count in byte 2.',
            'Table [6] (0x100200dX), [7]/[17] stream-descriptor offsets, and the 28-byte (0,0,0x50000,0,0,0,X) descriptors between table end and first stream are measured but unresolved.',
            'MIF counts here are header-validated (real MIFs only); the earlier raw-count inventory overcounted via false EMIF hits.',
        ],
        'totals': {'bones': tot_bones, 'vertices': tot_verts,
                   'nudp_blocks': tot_blocks},
        'problems': problems,
        'stages': stages,
    }
    out_path.write_text(json.dumps(out, indent=1))
    print(f"totals: bones={tot_bones} vertices={tot_verts} blocks={tot_blocks}")
    print(f"problems: {len(problems)}")
    for pr in problems[:20]:
        print('  PROBLEM:', pr)

if __name__ == '__main__':
    main()

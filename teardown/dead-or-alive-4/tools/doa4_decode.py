#!/usr/bin/env python3
"""
DOA4 triangulated mesh decoder.
- XPR2 table: 16-byte records (magic, f1, f2, f3).
- VBUF record: f1 = ABSOLUTE file offset of vertex data, f2 = stride (20), f3 = vert count.
  Vertex: BE float3 position + BE float2 UV (20 bytes).
- IBUF record: f1 = TABLE-RELATIVE offset to 20-byte descriptor.
  Descriptor: (flags, addr, size, type=0x20001, 0). addr = GPU address.
  file_offset = addr - IBUF_BASE (per-file). Data = u16 triangle strip with 0xFFFF restart.
- Converts strips to triangle lists, outputs GLB.
"""
import struct, re, sys, os, json

# Per-file IBUF base (file_offset = desc.addr - base)
IBUF_BASE = {
    'chrone.afs': 0x880000,
    'chrtwo.afs': 0x57000,
    'chrthree.afs': 0xe73000,
    'mot.afs': 0x5e0000,
    # 'stg.afs': ?,  # TODO
}

def parse_xpr2(data, xp):
    pos = xp; recs = []
    while pos < len(data) - 16:
        magic = data[pos:pos+4]
        if magic in (b'XPR2', b'USER', b'TX2D', b'VBUF', b'IBUF'):
            f1, f2, f3 = struct.unpack('>3I', data[pos+4:pos+16])
            recs.append((magic.decode(), f1, f2, f3))
            pos += 16
        elif magic == b'\x00\x00\x00\x00':
            pos += 16
        else:
            break
    return recs

def strip_to_tris(indices):
    """Convert triangle strip (with 0xFFFF restart) to triangle list."""
    tris = []
    # split by 0xFFFF
    strips = []
    cur = []
    for v in indices:
        if v == 0xFFFF:
            if len(cur) >= 3:
                strips.append(cur)
            cur = []
        else:
            cur.append(v)
    if len(cur) >= 3:
        strips.append(cur)
    for s in strips:
        for i in range(len(s) - 2):
            a, b, c = s[i], s[i+1], s[i+2]
            if a == b or b == c or a == c:
                continue
            # strip winding alternates
            if i % 2 == 1:
                tris.append((b, a, c))
            else:
                tris.append((a, b, c))
    return tris

def decode_table(afs_path, xp, ibuf_base):
    with open(afs_path, 'rb') as f:
        data = f.read()
    recs = parse_xpr2(data, xp)
    vbufs = [(f1, f2, f3) for m, f1, f2, f3 in recs if m == 'VBUF']
    ibufs = [(f1, f2, f3) for m, f1, f2, f3 in recs if m == 'IBUF']
    if not vbufs:
        return None
    # vertex pool: group by (f2, f3), take min f1 (like carve script)
    from collections import defaultdict
    groups = defaultdict(list)
    for f1, f2, f3 in vbufs:
        groups[(f2, f3)].append(f1)
    # pick largest group (most records = main pool)
    (stride, vcount), f1s = max(groups.items(), key=lambda x: len(x[1]))
    voff = min(f1s)
    # sanity: stride 20, reasonable count
    if stride != 20 or not (100 < vcount < 100000):
        return None
    verts = []
    uvs = []
    for i in range(vcount):
        o = voff + i * stride
        x, y, z = struct.unpack('>3f', data[o:o+12])
        u, v = struct.unpack('>2f', data[o+12:o+20])
        verts.append((x, y, z))
        uvs.append((u, v))
    # index buffers via descriptors: first pass to find max index
    ibuf_data = []
    max_idx = 0
    for f1, f2, f3 in ibufs:
        doff = xp + f1
        flags, addr, size, typ, _ = struct.unpack('>5I', data[doff:doff+20])
        if typ != 0x20001:
            continue
        ioff = (addr & ~3) - ibuf_base
        if ioff < 0 or ioff + size > len(data):
            continue
        nidx = size // 2
        indices = struct.unpack('>' + 'H' * nidx, data[ioff:ioff + nidx * 2])
        # validate: reasonable (not garbage)
        if len(indices) == 0:
            continue
        # allow up to 4x vcount; skip if clearly garbage
        if not all(v < vcount*4 or v == 0xFFFF for v in indices):
            continue
        ibuf_data.append(indices)
        for v in indices:
            if v != 0xFFFF and v > max_idx:
                max_idx = v
    # expand vertex pool to cover max index
    need_verts = max_idx + 1
    if need_verts > vcount:
        # read more verts
        for i in range(vcount, need_verts):
            o = voff + i * stride
            if o + 20 > len(data):
                break
            x, y, z = struct.unpack('>3f', data[o:o+12])
            u, v = struct.unpack('>2f', data[o+12:o+20])
            verts.append((x, y, z))
            uvs.append((u, v))
        vcount = len(verts)
    # convert strips to tris
    all_tris = []
    for indices in ibuf_data:
        # filter indices >= vcount (shouldn't happen, but safe)
        tris = strip_to_tris([v for v in indices if v < vcount or v == 0xFFFF])
        all_tris.extend(tris)
    return {
        'verts': verts, 'uvs': uvs,
        'tris': all_tris,
        'voff': voff, 'vcount': vcount,
        'n_ibuf': len(ibufs),
    }

def write_glb(verts, uvs, tris, path):
    import struct as st
    n = len(verts)
    # positions + uvs interleaved
    bin_data = bytearray()
    for i in range(n):
        bin_data.extend(st.pack('<3f', *verts[i]))
        bin_data.extend(st.pack('<2f', *uvs[i]))
    # indices (u32)
    idx_off = len(bin_data)
    for a, b, c in tris:
        bin_data.extend(st.pack('<3I', a, b, c))
    while len(bin_data) % 4:
        bin_data.append(0)
    json_str = json.dumps({
        "asset": {"version": "2.0", "generator": "doa4-decode"},
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": n, "type": "VEC3",
             "max": [max(v[i] for v in verts) for i in range(3)],
             "min": [min(v[i] for v in verts) for i in range(3)]},
            {"bufferView": 0, "byteOffset": n*12, "componentType": 5126, "count": n, "type": "VEC2"},
            {"bufferView": 1, "componentType": 5125, "count": len(tris)*3, "type": "SCALAR"},
        ],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": n*20, "byteStride": 20},
            {"buffer": 0, "byteOffset": idx_off, "byteLength": len(tris)*12},
        ],
        "buffers": [{"byteLength": len(bin_data)}],
        "meshes": [{"primitives": [{
            "attributes": {"POSITION": 0, "TEXCOORD_0": 1},
            "indices": 2, "mode": 4,
        }]}],
        "nodes": [{"mesh": 0}],
        "scenes": [{"nodes": [0]}],
        "scene": 0,
    }, separators=(',', ':'))
    jb = json_str.encode()
    while len(jb) % 4: jb += b' '
    glb = bytearray()
    glb.extend(st.pack('<4sII', b'glTF', 2, 12 + 8 + len(jb) + 8 + len(bin_data)))
    glb.extend(st.pack('<II', len(jb), 0x4E4F534A))
    glb.extend(jb)
    glb.extend(st.pack('<II', len(bin_data), 0x004E4942))
    glb.extend(bin_data)
    with open(path, 'wb') as f:
        f.write(glb)

if __name__ == '__main__':
    afs = sys.argv[1]
    xp = int(sys.argv[2], 16)
    out = sys.argv[3]
    base_name = os.path.basename(afs)
    base = IBUF_BASE.get(base_name)
    if base is None:
        print(f"no IBUF base for {base_name}"); sys.exit(1)
    r = decode_table(afs, xp, base)
    if not r:
        print("decode failed"); sys.exit(1)
    print(f"verts={len(r['verts'])} tris={len(r['tris'])} ibuf_recs={r['n_ibuf']}")
    write_glb(r['verts'], r['uvs'], r['tris'], out)
    print(f"wrote {out}")

#!/usr/bin/env python3
"""
DOA4 package assembly-graph parser + character assembler (Phase 3).

WHAT THIS IS
------------
Every DOA4 model package (in chrone/chrtwo/chrthree/mot/stg .afs) is a
self-contained unit:

    [data section: pools / strips / textures / per-object data]
    [XPR2 directory: 16-byte records XPR2/USER/TX2D/VBUF/IBUF]
    [MdlGeo block] [MdlInfo block] [Hie block]

This tool parses the FULL assembly graph of one package:

- XPR2 directory. The four USER records are a block directory:
  (offset-12, size) pairs for the header block, MdlGeo, MdlInfo, Hie.
  (Block name strings sit 12 bytes after the USER offset.)
- MdlGeo: header (name, 0xff000100, hdrlen 0x30, totalsize, count,
  count) + u32 offset table (count entries, block-relative) -> ObjGeo
  blocks. Header field +0x20 = offset of the per-object item-offset
  table inside each ObjGeo (usually 0x40); +0x28 = offset of the
  GeoDecl sub-chunk inside each ObjGeo.
- ObjGeo block: header + item table. Each item record is 0x140 bytes:
    +0x10 u32 index_start   (into the object's strip for its stream)
    +0x14 u32 index_count
    +0x18 u32 stream        (1, 2 or 3)
    +0x80.. material floats (diffuse/specular/shininess) - not geometry
  VERIFIED (chrone pkg0): obj0's stream-3 items sum to 20,983 indices;
  the matching IBUF descriptor strip holds 20,984 indices with max
  vertex index 7,860. Items are INDEX ranges into per-(object,stream)
  strips; strip indices are local to a per-(object,stream) vertex
  segment.
- MdlInfo: same table shape -> ObjInfo blocks. ObjInfo block header
  carries the object's bounds at +0x60: (center.xyz, sphere_radius),
  (center.xyz, 1.0), (extents.xyz, 0) with radius == |extents|
  (verified numerically). ObjInfo items are 0x50-byte records with the
  same bounds triple at +0x20. ObjInfo is bounds/metadata, NOT
  transforms.
- Hie (hierarchy): header + u32 node-offset table (count == object
  count in every package checked: chrone/chrtwo tables, 11 mot
  packages, 27 stg packages). Node record = 0x50 bytes:
    +0x00..0x3F  4x4 row-major local matrix (translation in row 3)
    +0x40..      u16 hierarchy links (parent index at +0x42, 0xFFFF =
                 root; remaining fields are child/sibling lists)
  World matrix = local x parent_world (row-vector convention).

ASSEMBLY
--------
assemble() composes Hie world matrices and applies them to pool
vertices, splitting triangles per object via the ObjGeo item index
ranges once a vertex pool + strips for the package are supplied
(--pool-glb from a doa4_decode3-style decode). The remaining blocker
for end-to-end character assembly is the vertex-pool location/format;
see PHASE3-ASSEMBLY-FINDINGS-2026-10-20.md for the evidence. In short:
VBUF record f1 steps by exactly 20 across records (a resource-space
offset, not a file offset), the absolute-f1 pools used by
doa4_decode/doa4_decode3 are bounded [-1,1] float streams whose
components repeat across records (not character positions), and
stride-{12,16,20,24,32} pos(+uv) scans (plain and 16-bit-swapped) of
the chrone lead-in and package data section found no position pool.

USAGE
-----
  doa4_assemble.py <afs_path> <xpr2_offset_hex> --graph out.json
  doa4_assemble.py <afs_path> <xpr2_offset_hex> --pool-glb pool.glb \
      --out assembled.glb
Per-character isolation: one package per run; no state is shared
between packages.
"""
import json
import struct
import sys

BLK_HDR = 0x30  # named-block header size
NODE_SIZE = 0x50
ITEM_SIZE = 0x140


def u32(d, o):
    return struct.unpack('>I', d[o:o + 4])[0]


def u16s(d, o, n):
    return struct.unpack('>' + 'H' * n, d[o:o + 2 * n])


def f32s(d, o, n):
    return struct.unpack('>' + 'f' * n, d[o:o + 4 * n])


def parse_directory(d, xp):
    """Walk the XPR2 directory records at xp. Returns (records, blocks)
    where blocks maps block name -> (offset, size) from USER records."""
    recs = []
    pos = xp
    while pos < len(d) - 16:
        magic = d[pos:pos + 4]
        if magic in (b'XPR2', b'USER', b'TX2D', b'VBUF', b'IBUF'):
            f1, f2, f3 = struct.unpack('>3I', d[pos + 4:pos + 16])
            recs.append((magic.decode(), f1, f2, f3))
            pos += 16
        elif magic == b'\x00\x00\x00\x00':
            pos += 16
        else:
            break
    blocks = {}
    users = [r for r in recs if r[0] == 'USER']
    # USER directory order observed: header, MdlGeo, MdlInfo, Hie.
    names = ['header', 'MdlGeo', 'MdlInfo', 'Hie']
    for (name, (_, f1, f2, _)) in zip(names, users):
        blocks[name] = (xp + f1 + 12, f2)  # name string at f1+12
    return recs, blocks


def parse_named_block(d, off):
    """Parse one MdlGeo/MdlInfo/Hie block: header + offset table."""
    name = d[off:off + 8].split(b'\x00')[0].decode()
    assert d[off + 8:off + 12] == b'\xff\x00\x01\x00', (name, off)
    total = u32(d, off + 0x10)
    count = u32(d, off + 0x14)
    table_off = u32(d, off + 0x20)
    offs = [u32(d, off + table_off + i * 4) for i in range(count)]
    return {'name': name, 'offset': off, 'size': total,
            'count': count, 'table_off': table_off, 'offs': offs}


def parse_objgeo(d, off):
    size = u32(d, off + 0x10)
    count = u32(d, off + 0x14)
    item_tab = u32(d, off + 0x20)
    geodecl_off = u32(d, off + 0x28)
    items = []
    for j in range(count):
        it = off + u32(d, off + item_tab + j * 4)
        items.append({
            'index_start': u32(d, it + 0x10),
            'index_count': u32(d, it + 0x14),
            'stream': u32(d, it + 0x18),
        })
    return {'offset': off, 'size': size, 'count': count,
            'geodecl_off': geodecl_off, 'items': items}


def parse_objinfo(d, off):
    size = u32(d, off + 0x10)
    count = u32(d, off + 0x14)
    c = f32s(d, off + 0x60, 3)
    r = f32s(d, off + 0x6c, 1)[0]
    e = f32s(d, off + 0x80, 3)
    return {'offset': off, 'size': size, 'count': count,
            'bounds_center': list(c), 'bounds_radius': r,
            'bounds_extents': list(e)}


def parse_hie_node(d, off):
    mat = [list(f32s(d, off + r * 16, 4)) for r in range(4)]
    links = list(u16s(d, off + 0x40, 8))
    return {'offset': off, 'matrix': mat, 'links': links,
            'parent': links[1] if links[1] != 0xFFFF else -1}


def parse_package(d, xp):
    recs, blocks = parse_directory(d, xp)
    mg = parse_named_block(d, blocks['MdlGeo'][0])
    mi = parse_named_block(d, blocks['MdlInfo'][0])
    hie_off = blocks['Hie'][0]
    hie = parse_named_block(d, hie_off)
    assert mg['count'] == mi['count'] == hie['count'], (
        mg['count'], mi['count'], hie['count'])
    objects = []
    for k in range(mg['count']):
        og = parse_objgeo(d, mg['offset'] + mg['offs'][k])
        oi = parse_objinfo(d, mi['offset'] + mi['offs'][k])
        node = parse_hie_node(d, hie['offset'] + hie['offs'][k])
        objects.append({'index': k, 'objgeo': og, 'objinfo': oi,
                        'hie_node': node})
    return {
        'xpr2_offset': xp,
        'directory_records': len(recs),
        'blocks': {k: {'offset': v[0], 'size': v[1]}
                   for k, v in blocks.items()},
        'object_count': mg['count'],
        'objects': objects,
    }


def mat_mul(a, b):
    """Row-vector composition: world = local(a) x parent(b)."""
    return [[sum(a[i][k] * b[k][j] for k in range(4))
             for j in range(4)] for i in range(4)]


def world_matrices(pkg):
    """Compose Hie world matrices following parent links."""
    worlds = [None] * pkg['object_count']

    def solve(k, seen):
        if worlds[k] is not None:
            return worlds[k]
        if k in seen:
            raise ValueError(f'hierarchy cycle at node {k}')
        node = pkg['objects'][k]['hie_node']
        local = node['matrix']
        p = node['parent']
        if p < 0 or p >= pkg['object_count'] or p == k:
            worlds[k] = local
        else:
            worlds[k] = mat_mul(local, solve(p, seen | {k}))
        return worlds[k]

    for k in range(pkg['object_count']):
        solve(k, set())
    return worlds


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    afs_path, xp = argv[1], int(argv[2], 16)
    with open(afs_path, 'rb') as f:
        d = f.read()
    pkg = parse_package(d, xp)
    worlds = world_matrices(pkg)
    for k, w in enumerate(worlds):
        pkg['objects'][k]['world_matrix'] = w
    if '--graph' in argv:
        out = argv[argv.index('--graph') + 1]
        with open(out, 'w') as f:
            json.dump(pkg, f, indent=1)
        print(f"wrote assembly graph: {out} "
              f"({pkg['object_count']} objects)")
        return 0
    print(f"package at {xp:#x}: {pkg['object_count']} objects, "
          f"blocks {pkg['blocks']}")
    for o in pkg['objects'][:8]:
        t = o['world_matrix'][3]
        print(f"  obj{o['index']}: items={len(o['objgeo']['items'])} "
              f"parent={o['hie_node']['parent']} "
              f"world_T=({t[0]:.3f},{t[1]:.3f},{t[2]:.3f})")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

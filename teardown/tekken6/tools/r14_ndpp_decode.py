#!/usr/bin/env python3
"""NDPP decoder, round-14 extension of tools/r9_ndpp_decode.py.

Round 13's parts batch failed on 400 packages whose VTYPEs carry
color-format 7: round 9's COL_SZ table has no entry for format 7, so
vtype_layout raised IndexError before any vertex was read.

The VTYPE word is the contract (same discipline as round 9). For
color-format 7 the layout, in PSP GE stream order
(weights, uv, color, normal, position), is:

  weights   nw * wf bytes   (VTYPE bits 14-16 = nw-1, bits 9-10 = wf type)
  uv        2 bytes         (tc=1: u8 x2)
  color     4 bytes RGBA8888, offset aligned to 4
  normal    3 bytes s8 x3   (nrm=1)  |  6 bytes s16 x3 (nrm=2)
  position  6 bytes s16 x3  (pos=2), offset aligned to 2
            12 bytes f32 x3 (pos=3), offset aligned to 4
  stride    total aligned to 4

Empirical validation over every col-7 unit in the 400 failed packages
(10,648 units, 112,160 vertices; see tools/round14-evidence/
JOB2-VTYPE7-VERDICT.md): computed stride == pair-delta stride for
10,648/10,648 units; u8 weight sets sum to 128 for 111,386/111,386
weighted vertices; normals unit-length for 58,453/58,453 (s8 family);
descriptor-bbox containment 112,157/112,160 (3 outliers at descriptor
float-rounding scale). All non-7 formats delegate to the round-9
layout unchanged (parity-tested byte-identical output).
"""
import struct
import importlib.util
_spec = importlib.util.spec_from_file_location(
    'r9_ndpp_decode', __file__.rsplit('/', 1)[0] + '/r9_ndpp_decode.py')
_r9 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_r9)

parse_units = _r9.parse_units
write_glb = _r9.write_glb
_r9_layout = _r9.vtype_layout


def vtype_layout(vt):
    """r9-shaped return: (fields[(name,off,size)], stride, nw, dims)."""
    tc = vt & 3; col = (vt >> 2) & 7; nrm = (vt >> 5) & 3
    pos = (vt >> 7) & 3; wf = (vt >> 9) & 3; nw = ((vt >> 14) & 7) + 1
    if col != 7:
        return _r9_layout(vt)
    if tc != 1 or pos not in (2, 3) or wf not in (0, 1) or nrm not in (0, 1, 2):
        raise ValueError('col7 variant outside proven family: %#x '
                         '(tc=%d pos=%d wf=%d nrm=%d)' % (vt, tc, pos, wf, nrm))
    fields = []; off = 0
    def add(name, size, align):
        nonlocal off
        off = (off + align - 1) & ~(align - 1)
        fields.append((name, off, size)); off += size
    if wf:
        add('weights', nw * _r9.W_SZ[wf], 1)
    if tc:
        add('uv', 2, 1)
    add('color', 4, 4)
    if nrm == 1:
        add('normal', 3, 1)
    elif nrm == 2:
        add('normal', 6, 2)
    if pos == 2:
        add('pos', 6, 2)
    else:
        add('pos', 12, 4)
    stride = (off + 3) & ~3
    return fields, stride, nw, (tc, col, nrm, pos, wf)


def decode_mesh(sec):
    """r9.decode_mesh semantics + col-7 layouts + float/s16-normal units.
    Sections whose units a layout cannot express return what decodes;
    units without a position field carry no geometry and are skipped
    (this is what the 4 KeyError-'pos' round-13 failures hit).
    Returns (verts, tris, nrms, uvs, wgts, desc) like r9."""
    desc = struct.unpack_from('<12f', sec, 20)
    ymax = desc[6]; s = ymax / 32767.0
    verts = []; tris = []; nrms = []; uvs = []; wgts = []
    for u in parse_units(sec):
        vt = u['hdr'][2] & 0xffffff
        if any(off > len(sec) for off, _cnt, _p in u['pairs']):
            continue  # false signature match inside a vertex stream
        fields, size, nw, fmt = vtype_layout(vt)
        fd = {n: (o, sz) for n, o, sz in fields}
        if 'pos' not in fd:
            continue
        # A signature match inside another unit's vertex stream can
        # mimic a unit header; a real unit's pairs always fit inside
        # the section. (Round-13 failure bulk3745: false VTYPE
        # 0x476bfd with pair offset 5,859,594 in a 79,616-byte section.)
        if any(u['off'] + off + cnt * size > len(sec)
               for off, cnt, _prim in u['pairs']):
            continue
        pfmt = fmt[3]
        for off, cnt, prim in u['pairs']:
            base = u['off'] + off; start = len(verts)
            for i in range(cnt):
                r = sec[base + i * size: base + i * size + size]
                po = fd['pos'][0]
                if pfmt == 3:
                    x, y, z = struct.unpack_from('<fff', r, po)
                    verts.append((x, y, z))
                else:
                    x, y, z = struct.unpack_from('<hhh', r, po)
                    verts.append((x * s, y * s, z * s))
                if 'normal' in fd:
                    no, nsz = fd['normal']
                    if nsz == 3:
                        nx, ny, nz = struct.unpack_from('<bbb', r, no)
                        nrms.append((nx / 127, ny / 127, nz / 127))
                    else:
                        nx, ny, nz = struct.unpack_from('<hhh', r, no)
                        nrms.append((nx / 32767, ny / 32767, nz / 32767))
                else:
                    nrms.append((0, 1, 0))
                if 'uv' in fd:
                    uvs.append((r[fd['uv'][0]] / 255, r[fd['uv'][0] + 1] / 255))
                else:
                    uvs.append((0, 0))
                if 'weights' in fd:
                    wo, wsz = fd['weights']
                    wgts.append(tuple(b / 128 for b in r[wo:wo + wsz]))
            idx = list(range(start, start + cnt))
            if prim == 4:
                for k in range(cnt - 2):
                    a, b, c = idx[k], idx[k + 1], idx[k + 2]
                    tris.append((a, b, c) if k % 2 == 0 else (b, a, c))
            elif prim == 3:
                for k in range(0, cnt - 2, 3):
                    tris.append((idx[k], idx[k + 1], idx[k + 2]))
            else:
                raise ValueError(f'prim {prim}')
    return verts, tris, nrms, uvs, wgts, desc

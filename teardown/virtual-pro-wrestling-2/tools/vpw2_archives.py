#!/usr/bin/env python3
"""VPW2 AkiArchive decode + arena assembly (v2).

Archive format: u32be count, count x u32be offsets (offset 0 = empty slot),
entries run to the next nonzero offset or EOF. (The decomp's akiarc tool
skips the last real entry when trailing slots are zero; this parser does not.)

Entry formats found in VPW2 (verified against the bytes, 2026-11-19):
- Arena "Models" archives: alternating index/vertex pairs, in EITHER order.
  * Index buffer: (u8, u8, u8, 0x00) triangle quads, optional FF FF FF FF
    terminator as the last quad.
  * Vertex buffer: F3DEX2 16-byte vertices (X/Y/Z s16, flag u16 == 0,
    U/V s16 S10.5 fixed point, RGBA u8).
  Pairing is verified per pair: max index < vertex count.
- Arena "Textures" archives: alternating (32-byte CI4 palette, texture).
  Texture entry: 8-byte header [u32 0x10][mirror u8][mirror u8][log2w u8]
  [log2h u8] + CI4 pixel data (2 px/byte). Decoded to PNG with the paired
  palette (RGBA5551).
- 0016 "lightning": AkiTexture entries (TEX magic, embedded palette).
- 0087 "Referee Johnny H frames": 32-byte palette + 8192-byte raw CI4
  frames, decoded as 128x128 (inferred: 8192 B CI4 = 16384 px).
- 0245-0249 pyro: 2048-byte raw I4 entries, decoded as 64x64 grayscale
  (inferred: 2048 B I4 = 4096 px).

UV note: arena vertex U/V are emitted in texel units (u/32, v/32) because
the per-piece texture assignment lives in game code, not in the archive.
The wiring lane normalizes per texture. Vertex colors go to .vc sidecars.

Usage: vpw2_archives.py
"""
import json
import os
import re
import struct
import sys
import zlib

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RAW = os.path.join(BASE, 'extracted', 'raw')
DB = ('/home/hatch/workspace/grok-declined-items/lane-jp-sourcing/pulls/'
      'VPWStudio/VPWStudio/VPWStudio/FileTableDB/VPW2.txt')


def load_db(path):
    db = {}
    for line in open(path, encoding='utf-8', errors='replace'):
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        m = re.match(r'([0-9A-Fa-f]{2,})=([^;]+);(.*)$', s)
        if m:
            db[int(m.group(1), 16)] = (m.group(2), m.group(3).strip())
    return db


def parse_archive(data):
    n = struct.unpack('>I', data[:4])[0]
    offs = list(struct.unpack('>%dI' % n, data[4:4 + 4 * n]))
    entries = []
    for i, o in enumerate(offs):
        if o == 0:
            continue
        nxt = len(data)
        for o2 in offs[i + 1:]:
            if o2 != 0:
                nxt = o2
                break
        entries.append((i, data[o:nxt]))
    return n, entries


def is_vertex_buf(d):
    if len(d) < 16 or len(d) % 16:
        return False
    for k in range(0, len(d), 16):
        x, y, z, fl = struct.unpack('>hhhh', d[k:k + 8])
        if fl != 0:
            return False
        if abs(x) > 30000 or abs(y) > 30000 or abs(z) > 30000:
            return False
    return True


def is_index_buf(d):
    if len(d) < 4 or len(d) % 4:
        return False
    nq = len(d) // 4
    for q in range(nq):
        b = d[q * 4:q * 4 + 4]
        if b == b'\xff\xff\xff\xff':
            return q == nq - 1  # terminator only valid last
        if b[3] != 0:
            return False
    return True


def parse_verts(d):
    verts = []
    for k in range(0, len(d), 16):
        x, y, z, _fl, u, v = struct.unpack('>hhhhhH', d[k:k + 12])
        r, g, b, a = d[k + 12:k + 16]
        verts.append((x, y, z, u, v, r, g, b, a))
    return verts


def parse_tris(d):
    tris = []
    for q in range(len(d) // 4):
        b = d[q * 4:q * 4 + 4]
        if b == b'\xff\xff\xff\xff':
            break
        tris.append((b[0], b[1], b[2]))
    return tris


def rgba5551(v):
    r = (v >> 11) & 0x1F
    g = (v >> 6) & 0x1F
    b = (v >> 1) & 0x1F
    a = 255 if (v & 1) else 0
    return ((r << 3) | (r >> 2), (g << 3) | (g >> 2),
            (b << 3) | (b >> 2), a)


def write_png(path, w, h, rgba):
    def chunk(t, d):
        c = t + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c))
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)
    rows = b''.join(b'\x00' + rgba[y * w * 4:(y + 1) * w * 4]
                    for y in range(h))
    png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
           chunk(b'IDAT', zlib.compress(rows, 6)) + chunk(b'IEND', b''))
    open(path, 'wb').write(png)


def write_gray_png(path, w, h, px):
    def chunk(t, d):
        c = t + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c))
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 0, 0, 0, 0)
    rows = b''.join(b'\x00' + bytes(px[y * w:(y + 1) * w]) for y in range(h))
    png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
           chunk(b'IDAT', zlib.compress(rows, 6)) + chunk(b'IEND', b''))
    open(path, 'wb').write(png)


def decode_ci4(px, w, h, pal):
    rgba = bytearray(w * h * 4)
    for i in range(w * h):
        byte = px[i // 2]
        ci = (byte >> 4) if i % 2 == 0 else (byte & 0xF)
        rgba[i * 4:i * 4 + 4] = bytes(pal[ci])
    return bytes(rgba)


def decode_akitex(d):
    w, h = struct.unpack('>HH', d[4:8])
    fmt = d[8]
    npal = struct.unpack('>H', d[10:12])[0]
    pal = [rgba5551(struct.unpack('>H', d[0x10 + i * 2:0x12 + i * 2])[0])
           for i in range(npal)]
    px = d[0x10 + npal * 2:]
    if fmt == 4:
        return w, h, decode_ci4(px, w, h, pal)
    if fmt == 8:
        rgba = bytearray(w * h * 4)
        for i in range(w * h):
            rgba[i * 4:i * 4 + 4] = bytes(pal[px[i]])
        return w, h, bytes(rgba)
    return None


def sanitize(s):
    s = re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_')
    return s[:80] or 'piece'


def main():
    db = load_db(DB)
    arcdir = os.path.join(BASE, 'extracted', 'archives')
    arenadir = os.path.join(BASE, 'extracted', 'arenas')
    texdir = os.path.join(BASE, 'extracted', 'arena-textures')
    os.makedirs(arenadir, exist_ok=True)
    os.makedirs(texdir, exist_ok=True)
    manifest = {'archives': {}, 'arenas': {}, 'arena_textures': {},
                'other': {}}
    arena_pieces = {}   # name -> list of (fid, idx, verts, tris)
    arena_points = {}   # name -> list of (fid, idx, verts) unpaired
    tex_count = 0
    for fid, (typ, label) in sorted(db.items()):
        if typ != 'AkiArchive':
            continue
        data = open(os.path.join(RAW, f'{fid:04X}.bin'), 'rb').read()
        n, entries = parse_archive(data)
        outdir = os.path.join(arcdir, f'{fid:04X}')
        os.makedirs(outdir, exist_ok=True)
        info = {'label': label, 'slots': n, 'entries': len(entries),
                'kinds': {}}
        m = re.match(r'\[?(.+?)\]? -? ?(Models|Textures.*)$', label)
        if m and 'Arena Select' in label:
            m = re.match(r'\[Arena Select\] (.+?) - (Models|Textures.*)', label)
        elif m:
            # e.g. '[Dome Road] Stage Models' -> name 'Dome Road Stage'
            m = re.match(r'\[(.+?)\] ?(.*?) ?(Models|Textures.*)$', label)
            if m:
                import types as _t
                class _M:
                    def __init__(s, g1, g2, g3): s._g = (g1.strip() + ' ' + g2.strip()).strip(), g3
                    def group(s, i): return s._g[i - 1]
                m = _M(m.group(1), m.group(2), m.group(3))
        kinds = {}
        # classify all entries first
        classified = []
        for idx, blob in entries:
            with open(os.path.join(outdir, f'{fid:04X}_{idx:02X}.bin'),
                      'wb') as f:
                f.write(blob)
            if blob[:4] == b'TEX\x00':
                kind = 'akitexture'
            elif len(blob) == 32 and (m and 'Textures' in m.group(2)
                                      or fid == 0x0087):
                kind = 'palette32'
            elif is_vertex_buf(blob):
                kind = 'vertex'
            elif is_index_buf(blob):
                kind = 'index'
            elif m and 'Textures' in m.group(2) and len(blob) > 8 \
                    and blob[0:3] == b'\x00\x00\x00' and blob[3] == 0x10:
                kind = 'arena_tex'
            elif fid in (0x0245, 0x0246, 0x0247, 0x0248, 0x0249):
                kind = 'i4_raw'
            else:
                kind = 'other'
            kinds[kind] = kinds.get(kind, 0) + 1
            classified.append((idx, blob, kind))
        info['kinds'] = kinds
        manifest['archives'][f'{fid:04X}'] = info
        # arena models: pair adjacent index/vertex entries (either order)
        if m and m.group(2) == 'Models':
            name = m.group(1)
            i = 0
            while i + 1 < len(classified):
                (i1, b1, k1), (i2, b2, k2) = classified[i], classified[i + 1]
                pair = None
                if k1 == 'index' and k2 == 'vertex':
                    pair = (parse_tris(b1), parse_verts(b2))
                elif k1 == 'vertex' and k2 == 'index':
                    pair = (parse_tris(b2), parse_verts(b1))
                if pair:
                    tris, verts = pair
                    mx = max((max(t) for t in tris), default=-1)
                    assert mx < len(verts), \
                        f'{fid:04X} pair {i1}/{i2}: maxidx {mx} >= {len(verts)}'
                    arena_pieces.setdefault(name, []).append(
                        (fid, i1, verts, tris))
                    i += 2
                else:
                    info.setdefault('unpaired', []).append([i1, k1])
                    if k1 == 'vertex':
                        arena_points.setdefault(name, []).append(
                            (fid, i1, parse_verts(b1)))
                    i += 1
            if i < len(classified):
                info.setdefault('unpaired', []).append(
                    [classified[i][0], classified[i][2]])
                if classified[i][2] == 'vertex':
                    arena_points.setdefault(name, []).append(
                        (fid, classified[i][0],
                         parse_verts(classified[i][1])))
        # arena textures: palette + texture pairs
        if m and m.group(2).startswith('Textures'):
            name = m.group(1)
            pals = [(idx, [rgba5551(struct.unpack(
                '>H', blob[j:j + 2])[0]) for j in range(0, 32, 2)])
                for idx, blob, kind in classified if kind == 'palette32']
            for idx, blob, kind in classified:
                if kind == 'arena_tex' and pals:
                    _pre = [p for p in pals if p[0] < idx]
                    _pal_idx, pal = (_pre[-1] if _pre else
                                     min(pals, key=lambda p: abs(p[0] - idx)))
                    lw, lh = blob[6], blob[7]
                    w, h = 1 << lw, 1 << lh
                    px = blob[8:]
                    if len(px) * 2 >= w * h:
                        rgba = decode_ci4(px, w, h, pal)
                        fn = f'{sanitize(name)}_{fid:04X}_{idx:02X}.png'
                        write_png(os.path.join(texdir, fn), w, h, rgba)
                        manifest['arena_textures'][fn] = {
                            'arena': name, 'fid': f'{fid:04X}',
                            'entry': idx, 'palette_entry': _pal_idx,
                            'w': w, 'h': h}
                        tex_count += 1
        # lightning AkiTextures
        if fid == 0x0016:
            for idx, blob, kind in classified:
                if kind == 'akitexture':
                    r = decode_akitex(blob)
                    if r:
                        w, h, rgba = r
                        fn = f'lightning_{fid:04X}_{idx:02X}.png'
                        write_png(os.path.join(texdir, fn), w, h, rgba)
                        manifest['arena_textures'][fn] = {
                            'arena': 'lightning', 'fid': f'{fid:04X}',
                            'entry': idx, 'w': w, 'h': h}
                        tex_count += 1
        # referee frames: palette + raw CI4 128x128
        if fid == 0x0087:
            pal = None
            for idx, blob, kind in classified:
                if kind == 'palette32':
                    pal = [rgba5551(struct.unpack(
                        '>H', blob[j:j + 2])[0]) for j in range(0, 32, 2)]
                elif pal is not None and len(blob) == 8192:
                    rgba = decode_ci4(blob, 128, 128, pal)
                    fn = f'referee_{idx:02X}.png'
                    write_png(os.path.join(texdir, fn), 128, 128, rgba)
                    manifest['arena_textures'][fn] = {
                        'arena': 'referee-frames', 'fid': '0087',
                        'entry': idx, 'w': 128, 'h': 128,
                        'dims': 'inferred 128x128'}
                    tex_count += 1
        # pyro I4 raw 64x64 grayscale
        if fid in (0x0245, 0x0246, 0x0247, 0x0248, 0x0249):
            for idx, blob, kind in classified:
                if kind == 'i4_raw' and len(blob) == 2048:
                    px = bytearray(4096)
                    for i in range(4096):
                        byte = blob[i // 2]
                        px[i] = ((byte >> 4) if i % 2 == 0
                                 else (byte & 0xF)) * 17
                    fn = f'pyro_{fid:04X}_{idx:02X}.png'
                    write_gray_png(os.path.join(texdir, fn), 64, 64, px)
                    manifest['arena_textures'][fn] = {
                        'arena': 'pyro', 'fid': f'{fid:04X}', 'entry': idx,
                        'w': 64, 'h': 64, 'dims': 'inferred 64x64 I4'}
                    tex_count += 1
    # assemble one OBJ per arena
    for name, pieces in sorted(arena_pieces.items()):
        out = os.path.join(arenadir, f'arena_{sanitize(name)}.obj')
        nv_total = 0
        vc_lines = []
        ntris = 0
        with open(out, 'w') as f:
            f.write('# Virtual Pro Wrestling 2 arena assembly by '
                    'vpw2_archives.py\n')
            f.write(f'# arena: {name}; F3DEX2 verts, texel-space UVs '
                    '(u/32, v/32); vertex colors in .vc\n')
            for fid, idx, verts, tris in pieces:
                f.write(f'g {fid:04X}_{idx:02X}\n')
                for (x, y, z, u, v, r, g, b, a) in verts:
                    f.write(f'v {x} {y} {z}\n')
                for (x, y, z, u, v, r, g, b, a) in verts:
                    f.write(f'vt {u / 32:.6f} {1.0 - v / 32:.6f}\n')
                    vc_lines.append(f'{r} {g} {b}')
                for (a, b, c) in tris:
                    f.write(f'f {a + 1 + nv_total}/{a + 1 + nv_total} '
                            f'{b + 1 + nv_total}/{b + 1 + nv_total} '
                            f'{c + 1 + nv_total}/{c + 1 + nv_total}\n')
                nv_total += len(verts)
                ntris += len(tris)
            for fid, idx, verts in arena_points.get(name, []):
                f.write(f'g {fid:04X}_{idx:02X}_points\n')
                f.write('# unpaired vertex buffer: no index buffer in archive; '
                        'points only, topology is implicit in game code\n')
                for (x, y, z, u, v, r, g, b, a) in verts:
                    f.write(f'v {x} {y} {z}\n')
                for (x, y, z, u, v, r, g, b, a) in verts:
                    f.write(f'vt {u / 32:.6f} {1.0 - v / 32:.6f}\n')
                    vc_lines.append(f'{r} {g} {b}')
                nv_total += len(verts)
        with open(out[:-4] + '.vc', 'w') as f:
            f.write('\n'.join(vc_lines) + '\n')
        manifest['arenas'][name] = {
            'obj': os.path.basename(out), 'pieces': len(pieces),
            'verts': nv_total, 'tris': ntris,
            'point_groups': len(arena_points.get(name, [])),
        }
    json.dump(manifest, open(os.path.join(arcdir, 'manifest.json'), 'w'),
              indent=1)
    print(f'{len(manifest["archives"])} archives decoded')
    print(f'{len(manifest["arenas"])} arenas: ' + ', '.join(
        f'{k} ({v["pieces"]} pcs, {v["verts"]} v, {v["tris"]} tris)'
        for k, v in manifest['arenas'].items()))
    print(f'{tex_count} archive textures decoded to PNG')
    unpaired = {k: v['unpaired'] for k, v in manifest['archives'].items()
                if 'unpaired' in v}
    if unpaired:
        print('UNPAIRED entries:', unpaired)


if __name__ == '__main__':
    main()

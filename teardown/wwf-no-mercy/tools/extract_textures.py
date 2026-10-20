#!/usr/bin/env python3
"""Bulk-extract WWF No Mercy textures to PNG.

Source: WWF No Mercy (USA) (Rev-A).z64
FileTable @0x16C31D8, FirstFile @0x1BD150 (= VPWStudio NoMercy_NTSC_U_11).
Texture list: every file labeled Ci4Texture / Ci8Texture / AkiTexture /
I4Texture in VPWStudio's FileTableDB (NoMercy.txt, MIT).

Formats (VPWStudio DataStructures/N64/*.cs, DataStructures/AKI/AkiTexture.cs):
- AkiTexture: "TEX\\0" magic, u16BE w/h, u8 fmt (4=CI4,8=CI8), u8 colorwidth,
  u16BE palcolors, RGBA5551 palette @0x10, pixels after. Embedded palette.
- CI8Texture / CI4Texture: 8-byte header (u8 w-1, u8 h-1, u16BE numpal,
  u8 hmirror, u8 vmirror, u8 wbitlen, u8 hbitlen), then raw indices
  (1 px/byte CI8, 2 px/byte CI4). Palette is EXTERNAL: the DB entry's
  "|p:XXXX" suffix names the palette file. NOTE: in the DB the two files of
  a pair are systematically type-swapped (the "Palette" entry holds the
  texture and vice versa) — this tool pairs empirically: the file with the
  dimension header is the texture, the 512-byte (CI8) / 32-byte (CI4) file
  is the RGBA5551 palette.
- I4Texture: raw 4bpp intensity, no header; dimensions from the DB label's
  "|w:W,h:H" suffix. Rendered grayscale.

Output:
  <outdir>/<category>/<name>_<fid>.png   (category from DB [bracket])
  <outdir>/manifest.json

Usage: extract_textures.py <filedb.txt> <outdir>
"""
import json, os, re, struct, sys, zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anim_extract import FileTable
from lzss import asmik_decode

ROM = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   '..', 'WWF No Mercy (USA) (Rev-A).z64')
TEX_TYPES = {'Ci4Texture', 'Ci8Texture', 'AkiTexture', 'I4Texture'}

def rgba5551(v):
    r = (v >> 11) & 0x1F; g = (v >> 6) & 0x1F; b = (v >> 1) & 0x1F
    a = 255 if (v & 1) else 0
    return ((r << 3) | (r >> 2), (g << 3) | (g >> 2), (b << 3) | (b >> 2), a)

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

def parse_aki_texture(raw):
    """TEX container -> (w, h, palette[(r,g,b,a)], indices) or None."""
    if raw[:4] != b'TEX\x00':
        return None
    w = struct.unpack('>H', raw[4:6])[0]
    h = struct.unpack('>H', raw[6:8])[0]
    fmt = raw[8]; cw = raw[9]
    npc = struct.unpack('>H', raw[10:12])[0]
    pal = [rgba5551(v) for v in struct.unpack('>' + 'H' * npc,
                                              raw[0x10:0x10 + npc * 2])]
    data = raw[0x10 + npc * cw:]
    if fmt == 0x04:
        px = bytearray(w * h)
        for i in range(0, w * h, 2):
            b = data[i // 2]
            px[i] = (b & 0xF0) >> 4
            px[i + 1] = b & 0x0F
    elif fmt == 0x08:
        px = data[:w * h]
    else:
        return None
    return w, h, pal, bytes(px)

def parse_ci_header(raw):
    """8-byte CI dim header -> (w, h) or None."""
    if len(raw) < 8:
        return None
    w, h = raw[0] + 1, raw[1] + 1
    return (w, h)

def load_db(path):
    entries = {}
    for l in open(path):
        s = l.strip()
        if not s or s.startswith('#'):
            continue
        m = re.match(r'(?:\d+:)?([0-9A-Fa-f]{2,})=([A-Za-z0-9_]+);(.*)$', s)
        if not m:
            continue
        fid, typ, rest = int(m.group(1), 16), m.group(2), m.group(3)
        entries[fid] = (typ, rest)
    return entries

def clean_label(label):
    label = re.sub(r'\|p:[0-9A-Fa-f]+', '', label)
    label = re.sub(r'\|w:\d+,h:\d+', '', label)
    label = re.sub(r'[^\w\- ]+', '', label).strip().replace(' ', '_')
    return label[:60] or 'texture'

def classify(dec):
    """Content-based classification. Returns (kind, w, h) or (palettesize,) or None.
    kind: 'tex' (TEX container), 'ci8', 'ci4', 'i4raw', 'pal8' (256c), 'pal4' (16c)."""
    if dec[:4] == b'TEX\x00':
        return ('tex',)
    wh = parse_ci_header(dec)
    if wh:
        w, h = wh
        if len(dec) == 8 + w * h:
            return ('ci8', w, h)
        if len(dec) == 8 + (w * h) // 2:
            return ('ci4', w, h)
    if len(dec) == 512:
        return ('pal8',)
    if len(dec) == 32:
        return ('pal4',)
    return None

def main():
    db_path, outdir = sys.argv[1], sys.argv[2]
    entries = load_db(db_path)
    data = open(ROM, 'rb').read()
    ft = FileTable(data)
    cache = {}

    def get(fid):
        if fid not in cache:
            raw, enc = ft.get(fid)
            cache[fid] = asmik_decode(raw) if enc else raw
        return cache[fid]

    # pass 1: classify everything; build palette pool
    info = {}
    for fid, (typ, rest) in entries.items():
        dec = get(fid)
        c = classify(dec)
        # I4 dims come from label
        if c is None:
            wm = re.search(r'\|w:(\d+),h:(\d+)', rest)
            if wm and len(dec) * 2 == int(wm.group(1)) * int(wm.group(2)):
                c = ('i4', int(wm.group(1)), int(wm.group(2)))
        info[fid] = (typ, rest, dec, c)

    pal_pool = {fid: v for fid, v in info.items()
                if v[3] in (('pal8',), ('pal4',))}

    # reverse |p: index: texture fid -> [palette fids pointing at it]
    rev_p = {}
    for pfid, (ptyp, prest, pdec, pc) in info.items():
        rpm = re.search(r'\|p:([0-9A-Fa-f]+)', prest)
        if rpm:
            rev_p.setdefault(int(rpm.group(1), 16), []).append(pfid)

    def find_palette(fid, need):
        """need: 256 or 16. 1) |p: link either direction; 2) neighbors."""
        rest = info[fid][1]
        cands = []
        pm = re.search(r'\|p:([0-9A-Fa-f]+)', rest)
        if pm:
            cands.append(int(pm.group(1), 16))
        cands += rev_p.get(fid, [])
        for d in range(1, 65):
            cands += [fid - d, fid + d]
        for c in cands:
            if c in pal_pool:
                pc = pal_pool[c][3]
                if (need == 256 and pc == ('pal8',)) or \
                   (need == 16 and pc == ('pal4',)):
                    return c
        return None

    manifest = {"textures": [], "skipped": []}
    n = 0
    for fid in sorted(info):
        typ, rest, dec, c = info[fid]
        if c is None or c[0] in ('pal8', 'pal4'):
            continue
        bm = re.match(r'\[([^\]]*)\]', rest)
        cat = (bm.group(1).strip().lower().replace(' ', '_')
               if bm else 'misc') or 'misc'
        name = clean_label(rest)
        sub = os.path.join(outdir, cat)
        os.makedirs(sub, exist_ok=True)
        fn = f"{name}_{fid:04X}.png"
        outp = os.path.join(sub, fn)
        done, kind = False, ''

        if c[0] == 'tex':
            t = parse_aki_texture(dec)
            if t:
                w, h, pal, px = t
                rgba = bytearray()
                for i in px:
                    rgba += bytes(pal[i] if i < len(pal) else (0, 0, 0, 0))
                write_png(outp, w, h, bytes(rgba))
                done, kind = True, 'akitexture'
        elif c[0] in ('ci8', 'ci4'):
            _, w, h = c
            need = 256 if c[0] == 'ci8' else 16
            pfid = find_palette(fid, need)
            if pfid is not None:
                pdec = pal_pool[pfid][2]
                pal = [rgba5551(v) for v in struct.unpack(
                    '>' + 'H' * need, pdec[:need * 2])]
                idx = dec[8:]
                if c[0] == 'ci4':
                    px = bytearray(w * h)
                    for i in range(0, w * h, 2):
                        b = idx[i // 2]
                        px[i] = (b & 0xF0) >> 4
                        px[i + 1] = b & 0x0F
                    px = bytes(px)
                else:
                    px = idx[:w * h]
                rgba = bytearray()
                for i in px:
                    rgba += bytes(pal[i] if i < len(pal) else (0, 0, 0, 0))
                write_png(outp, w, h, bytes(rgba))
                done, kind = True, c[0] + ' (nearest palette)'
            else:
                # no palette found: render indices as grayscale (reference)
                idx = dec[8:]
                if c[0] == 'ci4':
                    px = bytearray(w * h)
                    for i in range(0, w * h, 2):
                        b = idx[i // 2]
                        px[i] = ((b & 0xF0) >> 4) * 17
                        px[i + 1] = (b & 0x0F) * 17
                    px = bytes(px)
                else:
                    px = idx[:w * h]
                write_gray_png(outp, w, h, px)
                done, kind = True, c[0] + ' (grayscale, no palette)'
        elif c[0] == 'i4':
            _, w, h = c
            px = bytearray(w * h)
            for i in range(0, w * h, 2):
                b = dec[i // 2]
                px[i] = ((b & 0xF0) >> 4) * 17
                px[i + 1] = (b & 0x0F) * 17
            write_gray_png(outp, w, h, px)
            done, kind = True, 'i4'

        if done:
            n += 1
            manifest["textures"].append({
                "file": f"{cat}/{fn}", "file_id": hex(fid),
                "kind": kind, "label": rest,
            })
        else:
            manifest["skipped"].append({"file_id": hex(fid), "label": rest,
                                        "declen": len(dec),
                                        "class": c[0] if c else None})
    json.dump(manifest, open(os.path.join(outdir, 'manifest.json'), 'w'), indent=1)
    print(f"extracted {n} textures, {len(manifest['skipped'])} skipped")

if __name__ == '__main__':
    main()

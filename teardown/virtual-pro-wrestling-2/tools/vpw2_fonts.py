#!/usr/bin/env python3
"""VPW2 font extraction (VPWStudio AkiFont.cs format, AKI-Club, MIT).

- Large font (file 0x0001): 24x21 glyphs, 3-byte header + 63 bytes 1bpp
  per glyph, ends when header[2] == 0x0A. VPW2: 3,260 glyphs
  (3,260*66 + 3 terminator = 215,163 bytes = file size, exact).
- Small font (file 0x0002): 16x13 glyphs, 2-byte header + 26 bytes 1bpp
  per glyph, until EOF. VPW2: 3,264 glyphs (3,264*28 = 91,392, exact).
- Font characters (file 0x0003): u16 Shift_JIS code per glyph index.
  File is 6,508 bytes = 3,254 codes (6 fewer than the large font's 3,260
  glyphs; the last 6 glyphs have no mapped character).

Header fields (VPWStudio, partly unknown):
- Large: [0] leading spacing?, [1] character width?, [2] unknown (0?)
- Small: [0] unknown (always 0?), [1] high nibble = leading blank pixels,
  low nibble = character width?

Pixel: bit set = black, clear = white.

Usage: python3 vpw2_fonts.py   (run from vpw2/tools/)
Outputs: vpw2/extracted/fonts/{large,small}_font_atlas.png,
  {large,small}_font_headers.json, font_characters.json
"""
import json
import os
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
VPW2 = os.path.dirname(HERE)
RAW = os.path.join(VPW2, 'extracted', 'raw')
OUT = os.path.join(VPW2, 'extracted', 'fonts')


def write_gray_png(path, w, h, px):
    """px: bytes of grayscale values, row-major."""
    def chunk(t, d):
        c = t + d
        return (struct.pack('>I', len(d)) + c +
                struct.pack('>I', zlib.crc32(c)))
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 0, 0, 0, 0)
    rows = b''.join(b'\x00' + bytes(px[y * w:(y + 1) * w])
                    for y in range(h))
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) +
                           chunk(b'IDAT', zlib.compress(rows, 6)) +
                           chunk(b'IEND', b''))


def unpack_1bpp(data, w, h):
    """1bpp MSB-first -> list of 0 (white) / 255 (black) per pixel."""
    px = []
    for i in range(w * h):
        byte = data[i // 8]
        px.append(255 if (byte >> (7 - i % 8)) & 1 else 0)
    return px


def main():
    os.makedirs(OUT, exist_ok=True)

    # ---- large font ----
    blob = open(os.path.join(RAW, '0001.bin'), 'rb').read()
    char_bytes = (21 * 24) // 8  # 63
    headers, glyphs = [], []
    pos = 0
    while pos + 3 <= len(blob):
        hdr = blob[pos:pos + 3]
        if hdr[2] == 0x0A:
            pos += 3
            break
        headers.append({'lead': hdr[0], 'width': hdr[1], 'unknown': hdr[2]})
        glyphs.append(unpack_1bpp(blob[pos + 3:pos + 3 + char_bytes], 24, 21))
        pos += 3 + char_bytes
    assert pos == len(blob), f'large font: ended at {pos}, file {len(blob)}'
    assert len(glyphs) == 3260, f'large font: {len(glyphs)} glyphs'
    print(f'large font: {len(glyphs)} glyphs, terminator at {pos - 3:#x}')
    # atlas: 20 cols x 163 rows (VPWStudio LargeFontOutCols/Rows for VPW2)
    W, H = 24 * 20, 21 * 163
    atlas = bytearray([0] * (W * H))
    for gi, g in enumerate(glyphs):
        cx, cy = (gi % 20) * 24, (gi // 20) * 21
        for y in range(21):
            for x in range(24):
                atlas[(cy + y) * W + (cx + x)] = g[y * 24 + x]
    write_gray_png(os.path.join(OUT, 'large_font_atlas.png'), W, H, atlas)
    json.dump({'font': 'large', 'glyph_size': [24, 21], 'count': len(glyphs),
               'atlas': {'file': 'large_font_atlas.png', 'cols': 20,
                         'rows': 163, 'w': W, 'h': H},
               'header_fields': 'lead=?, width=?, unknown=? '
                                '(VPWStudio: [0] leading spacing?, '
                                '[1] character width?, [2] unknown)',
               'headers': headers},
              open(os.path.join(OUT, 'large_font_headers.json'), 'w'),
              indent=1)

    # ---- small font ----
    blob = open(os.path.join(RAW, '0002.bin'), 'rb').read()
    char_bytes = (13 * 16) // 8  # 26
    headers, glyphs = [], []
    pos = 0
    while pos < len(blob):
        hdr = blob[pos:pos + 2]
        headers.append({'unknown': hdr[0],
                        'lead': (hdr[1] & 0xF0) >> 4,
                        'width': hdr[1] & 0x0F})
        glyphs.append(unpack_1bpp(blob[pos + 2:pos + 2 + char_bytes], 16, 13))
        pos += 2 + char_bytes
    assert pos == len(blob), f'small font: ended at {pos}, file {len(blob)}'
    assert len(glyphs) == 3264, f'small font: {len(glyphs)} glyphs'
    print(f'small font: {len(glyphs)} glyphs')
    W, H = 16 * 64, 13 * 51
    atlas = bytearray([0] * (W * H))
    for gi, g in enumerate(glyphs):
        cx, cy = (gi % 64) * 16, (gi // 64) * 13
        for y in range(13):
            for x in range(16):
                atlas[(cy + y) * W + (cx + x)] = g[y * 16 + x]
    write_gray_png(os.path.join(OUT, 'small_font_atlas.png'), W, H, atlas)
    json.dump({'font': 'small', 'glyph_size': [16, 13], 'count': len(glyphs),
               'atlas': {'file': 'small_font_atlas.png', 'cols': 64,
                         'rows': 51, 'w': W, 'h': H},
               'header_fields': '[0] unknown (always 0?), [1] high nibble = '
                                'leading blank pixels, low nibble = width?',
               'headers': headers},
              open(os.path.join(OUT, 'small_font_headers.json'), 'w'),
              indent=1)

    # ---- font characters ----
    blob = open(os.path.join(RAW, '0003.bin'), 'rb').read()
    assert len(blob) == 6508, f'font chars len {len(blob)}'
    chars = []
    for i in range(len(blob) // 2):
        code = blob[i * 2:(i + 1) * 2]
        try:
            ch = code.decode('shift_jis')
        except UnicodeDecodeError:
            ch = None
        chars.append({'index': i, 'sjis': code.hex(), 'char': ch})
    mapped = sum(1 for c in chars if c['char'])
    print(f'font characters: {len(chars)} codes, {mapped} decode as Shift_JIS')
    json.dump({'source': 'file 0x0003, u16 Shift_JIS code per glyph index',
               'note': '3,254 codes vs 3,260 large / 3,264 small glyphs: '
                       'the last glyphs have no mapped character',
               'count': len(chars), 'characters': chars},
              open(os.path.join(OUT, 'font_characters.json'), 'w'),
              ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()

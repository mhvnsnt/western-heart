#!/usr/bin/env python3
"""EA SHPS texture decoding for Def Jam: Fight for NY `.ssh` files.

A decompressed `.ssh` (see eagl_refpack.py for the RefPack layer) is a
standard EA SHPS shape file with one image entry:

  0x00  "SHPS"
  0x04  u32 total size (== decompressed length)
  0x08  u32 entry count (1 in all FFNY samples)
  0x0C  entry: 4-char format code ("G359"), 4-char name, u32 data offset
  ...   "Buy ERTS" metal-bin attachment block up to the data offset

At the data offset, the image header (16 bytes, layout per the Q3R
ssh2tga documentation, Yagotzirck/Q3R_tools, itself based on the XeNTaX
SHPS research):

  +0  u32: low byte = image type (1 = paletted 4bpp, 2 = paletted 8bpp,
      4 = truecolor 24bpp, 5 = truecolor 32bpp); high 3 bytes =
      offset from this header to the next header (the palette header
      for paletted types)
  +4  u16 width, u16 height
  +8  8 bytes, zero in samples

Paletted 8bpp layout (proven on FFNY samples, byte-exact accounting:
128 header + 65536 pixels + 16 + 1024 palette + 336 trailer = 67024):

  +16                       pixel indices, PS2 GS-swizzled
  at header+nextHdrOffset:  palette header (16 bytes, first byte 0x21,
                            u32 at +4 = 0x0410 = 16 + 1024 in samples),
                            then 256 x RGBA palette entries (stored
                            linear, NOT palette-swizzled in FFNY files)
  after palette:            trailer containing the string
                            "EAGL240 metal bin attachment for runtime
                            texture management"

PS2 alpha is 0x00-0x80 (0x80 = opaque); decoded PNG alpha = min(255, a*2).

The 8bpp unswizzle is the standard PS2 GS layout permutation, as
implemented by ReverseBox (GPL-3.0, Bartlomiej Duda) in
reversebox/image/swizzling/swizzle_ps2.py; reimplemented here from the
published algorithm.
"""

from __future__ import annotations

import struct


class ShpsError(ValueError):
    pass


def unswizzle_ps2_8bit(data: bytes, width: int, height: int) -> bytes:
    """Undo the PS2 GS 8bpp texture swizzle (standard published layout)."""
    if len(data) < width * height:
        raise ShpsError("pixel data shorter than width*height")
    out = bytearray(width * height)
    for y in range(height):
        for x in range(width):
            block_location = (y & ~0xF) * width + (x & ~0xF) * 2
            swap_selector = (((y + 2) >> 2) & 0x1) * 4
            pos_y = (((y & ~3) >> 1) + (y & 1)) & 0x7
            column_location = pos_y * width * 2 + ((x + swap_selector) & 0x7) * 4
            byte_num = ((y >> 1) & 1) + ((x >> 2) & 2)
            out[y * width + x] = data[block_location + column_location + byte_num]
    return bytes(out)


def parse_shps(data: bytes) -> dict:
    """Parse a decompressed SHPS file. Returns dict with image fields:
    width, height, img_type, rgba (bytes, width*height*4, row-major,
    top row first as stored), palette_offset, pixel_offset."""
    if len(data) < 16 or data[:4] != b"SHPS":
        raise ShpsError("missing SHPS magic")
    total, count = struct.unpack("<II", data[4:12])
    if total != len(data):
        raise ShpsError(f"SHPS size field {total} != actual {len(data)}")
    if count < 1:
        raise ShpsError("SHPS entry count is zero")
    code = data[12:16]
    img_off = struct.unpack("<I", data[20:24])[0]
    if img_off + 16 > len(data):
        raise ShpsError("image data offset out of range")
    hdr = data[img_off:img_off + 16]
    type_and_next = struct.unpack("<I", hdr[0:4])[0]
    img_type = type_and_next & 0xFF
    next_hdr_off = type_and_next >> 8
    width, height = struct.unpack("<HH", hdr[4:8])
    if img_type != 2:
        raise ShpsError(
            f"unsupported SHPS image type {img_type} (only 2 = paletted "
            "8bpp is proven on FFNY samples)")
    pix_off = img_off + 16
    npix = width * height
    if pix_off + npix > len(data):
        raise ShpsError("pixel data overruns file")
    indices = unswizzle_ps2_8bit(data[pix_off:pix_off + npix], width, height)
    pal_hdr_off = img_off + next_hdr_off
    if pal_hdr_off + 16 + 1024 > len(data):
        raise ShpsError("palette header offset out of range")
    if data[pal_hdr_off] != 0x21:
        raise ShpsError(
            f"palette header marker is {data[pal_hdr_off]:#x}, expected 0x21")
    pal = data[pal_hdr_off + 16:pal_hdr_off + 16 + 1024]
    rgba = bytearray(npix * 4)
    for i, idx in enumerate(indices):
        r, g, b, a = pal[idx * 4:idx * 4 + 4]
        rgba[i * 4:i * 4 + 4] = bytes((r, g, b, min(255, a * 2)))
    return {
        "code": code.decode("latin1"),
        "width": width,
        "height": height,
        "img_type": img_type,
        "pixel_offset": pix_off,
        "palette_offset": pal_hdr_off + 16,
        "rgba": bytes(rgba),
    }


def write_png(path: str, width: int, height: int, rgba: bytes) -> None:
    """Write an RGBA PNG (pure python, deterministic)."""
    import zlib

    def chunk(typ: bytes, payload: bytes) -> bytes:
        c = struct.pack(">I", len(payload)) + typ + payload
        return c + struct.pack(">I", zlib.crc32(typ + payload) & 0xFFFFFFFF)

    rows = b"".join(
        b"\x00" + rgba[y * width * 4:(y + 1) * width * 4] for y in range(height))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", zlib.compress(rows, 9)))
        f.write(chunk(b"IEND", b""))


if __name__ == "__main__":
    import sys

    sys.path.insert(0, ".")
    from eagl_refpack import refpack_decompress, find_refpack_offset

    for path in sys.argv[1:]:
        raw = open(path, "rb").read()
        off = find_refpack_offset(raw)
        img = parse_shps(refpack_decompress(raw[off:]))
        print(f"{path}: {img['width']}x{img['height']} type={img['img_type']} "
              f"code={img['code']}")

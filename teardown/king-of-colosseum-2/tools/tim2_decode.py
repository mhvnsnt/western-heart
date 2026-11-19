#!/usr/bin/env python3
"""TIM2 -> PNG decoder (PS2 texture format, as used by King of Colosseum II).

TIM2 layout (little-endian):
  File header (16 B): magic "TIM2", version u8, format u8, pictures u16,
    reserved 8 B.
  Per picture (24 B header + optional extension): total_size u32,
    clut_size u32, image_size u32, header_size u16, clut_colors u16,
    pict_format u8, mipmap_count u8, clut_type u8, image_type u8,
    width u16, height u16.
    NOTE (KoC2 quirk, found 2026-11-19): the picture header does NOT
    always start at offset 16 — in KoC2's TIM2s it starts at 0x80 (a
    112-byte zero gap follows the file header), and header_size is 0x80
    (128), so the CLUT starts at picture_start + 128. The decoder scans
    for a consistent picture header instead of assuming offset 16.
    The pixel mode is derived from image_size / (width*height) (bytes
    per pixel) + CLUT presence, not from pict_format alone — KoC2's
    pict_format byte reads 0x01 on files that are plainly 8-bit indexed
    (128x128, 16384 image bytes, 256-color CLUT).
    pict_format low 3 bits (standard): 0=16-bit RGBA1555, 1=24-bit RGB,
    2=32-bit RGBA, 3=4-bit indexed, 4=8-bit indexed.
    clut_type: 0=none, 1=16-bit, 2=24-bit, 3=32-bit.
  Then CLUT data (clut_size B), then image data (image_size B).
  Mipmaps (mipmap_count > 1) are ignored: only the base image is decoded.

Usage: tim2_decode.py input.tim2 [output.png] [--all]
  --all decodes every picture in the file (output_0.png, output_1.png, ...).

Lane E (KoC2), 2026-11-19. Written from the public TIM2 spec; validated
against KoC2's decompressed .tim2 files (see TEARDOWN.md).
"""
import struct
import sys
from pathlib import Path

from PIL import Image


def _decode_16bit(px: int):
    # A1R5G5B5
    a = 255 if (px & 0x8000) else 0
    r = ((px >> 10) & 0x1F) * 255 // 31
    g = ((px >> 5) & 0x1F) * 255 // 31
    b = (px & 0x1F) * 255 // 31
    return (r, g, b, a)


def _decode_clut(data: bytes, clut_type: int, count: int):
    clut = []
    if clut_type == 1:  # 16-bit
        for i in range(count):
            clut.append(_decode_16bit(struct.unpack_from("<H", data, i * 2)[0]))
    elif clut_type == 2:  # 24-bit
        for i in range(count):
            b, g, r = data[i * 3 : i * 3 + 3]
            clut.append((r, g, b, 255))
    elif clut_type == 3:  # 32-bit
        for i in range(count):
            r, g, b, a = data[i * 4 : i * 4 + 4]
            clut.append((r, g, b, a))
    return clut


def decode_picture(buf: bytes, off: int):
    """Decode one TIM2 picture at offset off. Returns (Image, next_offset)."""
    (total_size, clut_size, image_size, header_size, clut_colors,
     pict_format, mipmap_count, clut_type, image_type,
     width, height) = struct.unpack_from("<IIIHHBBBBHH", buf, off)
    # Mode from bytes-per-pixel (KoC2's pict_format byte is unreliable):
    # bpp 1 + CLUT -> 8-bit indexed; 0.5 -> 4-bit; 2 -> 16-bit; 3 -> 24-bit;
    # 4 -> 32-bit. Falls back to pict_format when the size is ambiguous.
    px = width * height
    if px and image_size:
        bpp_num = image_size * 2 // px  # 2x bpp to keep 4-bit integral
        if bpp_num == 1:
            mode = 3
        elif bpp_num == 2:
            mode = 4 if clut_size else 0
        elif bpp_num == 4:
            mode = 0
        elif bpp_num == 6:
            mode = 1
        elif bpp_num == 8:
            mode = 2
        else:
            mode = pict_format & 0x07
    else:
        mode = pict_format & 0x07
    body = off + header_size
    clut = []
    if clut_size:
        clut = _decode_clut(buf[body : body + clut_size], clut_type, clut_colors)
    img_off = body + clut_size
    img_data = buf[img_off : img_off + image_size]

    pixels = []
    if mode == 0:  # 16-bit
        for i in range(width * height):
            pixels.append(_decode_16bit(struct.unpack_from("<H", img_data, i * 2)[0]))
    elif mode == 1:  # 24-bit BGR
        for i in range(width * height):
            b, g, r = img_data[i * 3 : i * 3 + 3]
            pixels.append((r, g, b, 255))
    elif mode == 2:  # 32-bit RGBA
        for i in range(width * height):
            r, g, b, a = img_data[i * 4 : i * 4 + 4]
            pixels.append((r, g, b, a))
    elif mode == 3:  # 4-bit indexed, low nibble first
        for i in range(width * height):
            byte = img_data[i // 2]
            idx = (byte & 0x0F) if i % 2 == 0 else (byte >> 4)
            pixels.append(clut[idx] if idx < len(clut) else (0, 0, 0, 0))
    elif mode == 4:  # 8-bit indexed
        for i in range(width * height):
            idx = img_data[i]
            pixels.append(clut[idx] if idx < len(clut) else (0, 0, 0, 0))
    else:
        raise ValueError(f"unsupported TIM2 pict_format mode {mode}")

    im = Image.new("RGBA", (width, height))
    im.putdata(pixels)
    return im, off + total_size


def find_picture(buf: bytes, start: int):
    """Find the next valid TIM2 picture header at or after `start`.

    A header is valid when total_size is nonzero, header_size is sane
    (24..512), width/height are nonzero, and off + total_size does not
    run past the end of the buffer. KoC2 pads the file header out to
    0x80, so the first picture usually starts there, not at 16.
    """
    off = start
    while off + 24 <= len(buf):
        (total_size, clut_size, image_size, header_size, clut_colors,
         pict_format, mipmap_count, clut_type, image_type,
         width, height) = struct.unpack_from("<IIIHHBBBBHH", buf, off)
        if (total_size > 0 and 24 <= header_size <= 512
                and width > 0 and height > 0
                and off + total_size <= len(buf)
                and header_size + clut_size + image_size <= total_size):
            return off
        off += 16
    raise ValueError("no valid TIM2 picture header found")


def decode_file(path: Path):
    buf = path.read_bytes()
    if buf[:4] != b"TIM2":
        raise ValueError(f"{path}: not a TIM2 file (magic {buf[:4]!r})")
    count = struct.unpack_from("<H", buf, 6)[0]
    images = []
    off = 16
    for _ in range(count):
        off = find_picture(buf, off)
        im, off = decode_picture(buf, off)
        images.append(im)
    return images


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    src = Path(argv[1])
    decode_all = "--all" in argv
    out = None
    for a in argv[2:]:
        if not a.startswith("--"):
            out = Path(a)
    images = decode_file(src)
    if decode_all or len(images) > 1:
        base = out or src.with_suffix("")
        for i, im in enumerate(images):
            p = Path(f"{base}_{i}.png")
            im.save(p)
            print(f"{p} {im.size[0]}x{im.size[1]}")
    else:
        p = out or src.with_suffix(".png")
        images[0].save(p)
        print(f"{p} {images[0].size[0]}x{images[0].size[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

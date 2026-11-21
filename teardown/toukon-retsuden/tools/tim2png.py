#!/usr/bin/env python3
"""Render a PS1 TIM texture to PNG (4/8/15/24bpp, with CLUT support).

Usage:
  python3 tim2png.py <in.tim> <out.png> [--pal N] [--scale N]
  python3 tim2png.py --dir <indir> <outdir> [--scale N]
"""
import struct
import sys
from pathlib import Path

from PIL import Image


def psx15_to_rgb(v):
    r = (v & 0x1F) << 3
    g = ((v >> 5) & 0x1F) << 3
    b = ((v >> 10) & 0x1F) << 3
    return (r | (r >> 5), g | (g >> 5), b | (b >> 5))


def parse_tim(data):
    """Return (pixels, width, height) as an RGB PIL image."""
    magic, flags = struct.unpack_from("<II", data, 0)
    assert magic == 0x10, f"not a TIM (magic {magic:#x})"
    bpp = flags & 0x3
    has_clut = bool(flags & 0x8)
    off = 8
    palettes = []
    if has_clut:
        clen, _cx, _cy, cw, ch = struct.unpack_from("<IHHHH", data, off)
        clut_data = data[off + 12:off + clen]
        ncolors = len(clut_data) // 2
        colors = [psx15_to_rgb(struct.unpack_from("<H", clut_data, i * 2)[0])
                  for i in range(ncolors)]
        per = 16 if bpp == 0 else 256
        palettes = [colors[i:i + per] for i in range(0, len(colors), per)]
        off += clen
    ilen, _ix, _iy, iw, ih = struct.unpack_from("<IHHHH", data, off)
    px = data[off + 12:off + ilen]
    if bpp == 0:      # 4bpp: stored width is in 16-bit words; real w = iw*4
        w, h = iw * 4, ih
        img = Image.new("RGB", (w, h))
        pix = img.load()
        for y in range(h):
            for x in range(w):
                byte = px[y * (w // 2) + x // 2]
                idx = (byte >> 4) if (x & 1) else (byte & 0xF)
                pix[x, y] = palettes[0][idx] if palettes else (idx * 17,) * 3
        return img
    if bpp == 1:      # 8bpp: real w = iw*2
        w, h = iw * 2, ih
        img = Image.new("RGB", (w, h))
        pix = img.load()
        for y in range(h):
            for x in range(w):
                idx = px[y * w + x]
                pix[x, y] = palettes[0][idx] if palettes else (idx,) * 3
        return img
    if bpp == 2:      # 15bpp direct
        w, h = iw, ih
        img = Image.new("RGB", (w, h))
        pix = img.load()
        for y in range(h):
            for x in range(w):
                v = struct.unpack_from("<H", px, (y * w + x) * 2)[0]
                pix[x, y] = psx15_to_rgb(v)
        return img
    # 24bpp direct
    w, h = iw * 3 // 2, ih
    img = Image.new("RGB", (w, h))
    pix = img.load()
    for y in range(h):
        for x in range(w):
            o = (y * w + x) * 3
            pix[x, y] = (px[o + 2], px[o + 1], px[o])
    return img


def render_one(src, dst, scale=1, pal=0):
    data = Path(src).read_bytes()
    img = parse_tim(data)
    if scale != 1:
        img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    img.save(dst)
    print(f"{src} -> {dst} ({img.width}x{img.height})")


if __name__ == "__main__":
    args = sys.argv[1:]
    scale = 1
    if "--scale" in args:
        i = args.index("--scale")
        scale = int(args[i + 1])
        del args[i:i + 2]
    if args[0] == "--dir":
        indir, outdir = Path(args[1]), Path(args[2])
        outdir.mkdir(parents=True, exist_ok=True)
        for f in sorted(indir.glob("*.bin")):
            try:
                render_one(f, outdir / (f.stem + ".png"), scale)
            except Exception as e:
                print(f"{f.name}: FAILED {e}")
    else:
        render_one(args[0], args[1], scale)

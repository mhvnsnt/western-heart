#!/usr/bin/env python3
"""Extract all TIM textures from tim-inventory.json.

For every texture in tim-inventory.json:
  - writes the raw .tim slice [offset, end_offset) from TEKKEN3.BNS
  - renders PNG previews (one per palette) using the CLUT data

Usage: python3 tim_extract.py [--force]
Only writes files that are missing unless --force is given.
"""
import json, os, sys, struct
from pathlib import Path
from PIL import Image

BASE = Path(__file__).resolve().parent.parent.parent
BNS = BASE / "disc/files/TEKKEN3/TEKKEN3.BNS"
OUT = BASE / "tim-output"
INV = BASE / "tim-inventory.json"


def psx_to_rgb(c):
    r = (c & 0x1F) * 255 // 31
    g = ((c >> 5) & 0x1F) * 255 // 31
    b = ((c >> 10) & 0x1F) * 255 // 31
    return r, g, b


def main():
    force = "--force" in sys.argv
    inv = json.load(open(INV))
    texs = inv["textures"]
    f = open(BNS, "rb")
    made_tim = made_png = skip = 0
    for t in texs:
        tn = t["suggested_tim_filename"]
        tp = OUT / tn
        if force or not tp.exists():
            f.seek(t["offset"])
            raw = f.read(t["size"])
            assert len(raw) == t["size"], (tn, len(raw), t["size"])
            assert raw[0] == 0x10, tn  # TIM magic
            tp.write_bytes(raw)
            made_tim += 1
        else:
            skip += 1
        # PNG previews
        cl = t["clut"]
        im = t["image"]
        bpp = t["bits_per_pixel"]
        f.seek(cl["source_data_offset"])
        clut_raw = f.read(cl["data_size"])
        n_colors = len(clut_raw) // 2
        colors = [psx_to_rgb(struct.unpack_from("<H", clut_raw, i * 2)[0]) for i in range(n_colors)]
        f.seek(im["source_data_offset"])
        img_raw = f.read(im["data_size"])
        w, h = t["pixel_width"], t["height"]
        n_pal = t["palette_count"]
        pal_size = n_colors // n_pal
        previews = t["suggested_preview_filenames"]
        assert len(previews) == n_pal, tn
        for pi, pv in enumerate(previews):
            pp = OUT / pv
            if pp.exists() and not force:
                continue
            pal = colors[pi * pal_size:(pi + 1) * pal_size]
            img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            px = img.load()
            if bpp == 4:
                idx = 0
                for y in range(h):
                    for x in range(0, w, 2):
                        b = img_raw[idx]; idx += 1
                        for dx, v in ((0, b & 0xF), (1, b >> 4)):
                            if x + dx < w:
                                r, g, bl = pal[v]
                                px[x + dx, y] = (r, g, bl, 0 if v == 0 else 255)
            elif bpp == 8:
                idx = 0
                for y in range(h):
                    for x in range(w):
                        v = img_raw[idx]; idx += 1
                        r, g, bl = pal[v]
                        px[x, y] = (r, g, bl, 0 if v == 0 else 255)
            else:
                raise ValueError((tn, bpp))
            img.save(pp)
            made_png += 1
    print(f"tim: wrote {made_tim}, png: wrote {made_png}, skipped {skip} (already present)")


if __name__ == "__main__":
    main()

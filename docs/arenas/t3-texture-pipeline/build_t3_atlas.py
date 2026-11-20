#!/usr/bin/env python3
"""Tekken 3 stage panorama texture-atlas pipeline (Lane E / ARENAS).

Reconstructs real textured panoramas for the 15 T3 fight stages.

Source data (all real teardown, no hand-authoring):
  - Panorama TMD records: TEKKEN3.BNS records 56..70 (geometry + per-corner
    texture keys <cba>_<tsb> + per-packet RGB, extracted by
    teardown/tekken3/tools/local/extract_stages.py).
  - Stage texture ARCs: TEKKEN3.BNS records 36..50. Each ARC is a chain of
    standard PSX TIM files. Every TIM carries its own VRAM destination
    (image DX/DY, CLUT x/y), so blitting the chain in order rebuilds the
    1024x512 index-VRAM exactly as the game uploaded it.

Decoding rules (PSX GPU):
  - TSB = texture page word: bits 0-3 page X (*64), bit 4 page Y (0/256),
    bits 5-6 semi-transparency, bits 7-8 texture mode (0 = 4-bit here).
    All 15 stages' panoramas use 4-bit textures (verified).
  - (u, v) are texel offsets from the page origin (u: 0..255, v: 0..255).
  - CBA = CLUT base: x = (cba & 0x3F) * 16, y = (cba >> 6) & 0x1FF.
  - PSX 15-bit color: R = (c & 31) << 3 etc. Textures are opaque
    (abr = 0 on every key observed) so index 0 decodes to CLUT[0], NOT
    forced transparent.

Output per stage <letter>:
  - game/assets/stages/t3/stg_<letter>_atlas.png — shelf-packed atlas of
    every unique (cba, tsb) texture rect referenced by the panorama.
  - game/assets/stages/t3/stg_<letter>_panorama.obj — regenerated with
    atlas-space UVs (same v-flip convention as before: vt_v = 1 - v/H)
    and per-vertex TMD colors appended to v lines (v x y z r g b).
  - <out>/contact_<letter>.png — contact sheet of every atlas cell for
    own-eyes verification before wiring into the game.

Usage:
    python3 build_t3_atlas.py --bns <TEKKEN3.BNS> --table <bns-table.pkl> \\
        --out <game/assets/stages/t3> --work <scratch dir>
"""

from __future__ import annotations

import argparse
import pickle
import struct
from pathlib import Path

from PIL import Image

STAGES = [
    (0, "a"), (1, "b"), (2, "c"), (3, "d"), (4, "e"), (5, "f"), (6, "g"),
    (7, "n"), (8, "i"), (9, "j"), (10, "k"), (11, "l"), (12, "m"),
    (13, "t"), (14, "u"),
]

TABLE, ROW_BYTES, OBJECTS = 0x0C, 0x1C, 36
PACKET_BYTES = {0x24: 20, 0x28: 8, 0x2C: 20}
ATLAS_COL_W = 2048  # atlas row width; cells are packed left-to-right


# ---------------- TMD panorama parse ----------------

def parse_tmd(tmd: bytes):
    """Return list of (key, x, y, z, u, v, r, g, b) corners; key=(cba, tsb)."""
    cell = 10 * struct.unpack_from("<I", tmd, 4)[0]
    count = struct.unpack_from("<I", tmd, 8)[0]
    assert count == OBJECTS, f"expected {OBJECTS} objects, got {count}"
    corners = []
    for index in range(OBJECTS):
        vert_off, vert_count, _, _, prim_off, prim_count, _ = struct.unpack_from(
            "<7I", tmd, TABLE + ROW_BYTES * index)
        verts = [struct.unpack_from("<3h", tmd, TABLE + vert_off + 8 * i)
                 for i in range(vert_count)]
        pos = TABLE + prim_off
        for _ in range(prim_count):
            r, g, b, code = tmd[pos:pos + 4]
            if code == 0x28:
                idx = tmd[pos + 4:pos + 8]
                uvs = [(0, 0)] * 4
                key = None
            else:
                u0, v0, cba = struct.unpack_from("<BBH", tmd, pos + 4)
                u1, v1, tsb = struct.unpack_from("<BBH", tmd, pos + 8)
                u2, v2, u3, v3 = tmd[pos + 12:pos + 16]
                idx = tmd[pos + 16:pos + 20] if code == 0x2C else tmd[pos + 16:pos + 19]
                uvs = [(u0, v0), (u1, v1), (u2, v2), (u3, v3)]
                key = (cba, tsb)
            quads = [(0, 1, 2)] if len(idx) == 3 else [(0, 1, 2), (1, 3, 2)]
            for tri in quads:
                for c in tri:
                    vi = idx[c]
                    x, y, z = verts[vi]
                    u, v = uvs[c]
                    corners.append((key, x, y, z, u, v, r / 128.0, g / 128.0, b / 128.0))
            pos += PACKET_BYTES[code]
    return cell, corners


# ---------------- TIM / VRAM ----------------

def psx_to_rgb(c: int):
    return ((c & 0x1F) << 3, ((c >> 5) & 0x1F) << 3, ((c >> 10) & 0x1F) << 3)


def parse_arc(arc: bytes):
    """Blit every TIM in the ARC into a 1024x512 index buffer.

    Returns (vram_indices, cluts) where vram_indices is a bytearray of
    1024*512 nibble indices and cluts maps (x, y) -> list of 16-bit colors.
    """
    vram = bytearray(1024 * 512)  # 4-bit indices, 0 = unset
    cluts: dict[tuple[int, int], list[int]] = {}
    off, n = 0, len(arc)
    parsed = 0
    while off + 12 <= n:
        if arc[off:off + 4] == b"\x10\x00\x00\x00" and arc[off + 4] in (0x08, 0x09, 0x0A):
            flags = arc[off + 4]
            p = off + 8
            if flags in (0x08, 0x09):  # CLUT section
                bnum, dx, dy, w, h = struct.unpack_from("<IHHHH", arc, p)
                if bnum > 100000 or dx > 1024 or dy > 512:
                    off += 4
                    continue
                ncol = (bnum - 12) // 2
                colors = list(struct.unpack_from(f"<{ncol}H", arc, p + 12))
                cluts[(dx, dy)] = colors
                p += bnum
            bnum, dx, dy, w, h = struct.unpack_from("<IHHHH", arc, p)
            if bnum > 4000000 or dx > 1024 or dy > 512:
                off += 4
                continue
            data = arc[p + 12:p + bnum]
            if flags == 0x08:  # 4-bit: 4 texels per 16-bit word
                pw = w * 4
                for row in range(h):
                    for colw in range(w):
                        if (row * w + colw) * 2 + 1 >= len(data):
                            break
                        word = data[(row * w + colw) * 2] | (data[(row * w + colw) * 2 + 1] << 8)
                        for k in range(4):
                            x, y = dx + colw * 4 + k, dy + row
                            if x < 1024 and y < 512:
                                vram[y * 1024 + x] = (word >> (k * 4)) & 0xF
            elif flags == 0x09:  # 8-bit: store raw byte (CLUT has 256 entries)
                for row in range(h):
                    for col in range(w):
                        if row * w + col >= len(data):
                            break
                        x, y = dx + col, dy + row
                        if x < 1024 and y < 512:
                            vram[y * 1024 + x] = data[row * w + col]
            parsed += 1
            off = p + bnum
        else:
            off += 4
    return vram, cluts, parsed


# ---------------- atlas build ----------------

def build_stage(letter, tmd, arc, out_dir: Path, work_dir: Path):
    cell, corners = parse_tmd(tmd)
    textured = [c for c in corners if c[0] is not None]
    vram, cluts, ntim = parse_arc(arc)

    # per-key uv extents
    ext: dict[tuple[int, int], list[int]] = {}
    for key, x, y, z, u, v, r, g, b in textured:
        e = ext.setdefault(key, [999, 0, 999, 0])
        e[0] = min(e[0], u); e[1] = max(e[1], u)
        e[2] = min(e[2], v); e[3] = max(e[3], v)

    cells = []  # (key, PIL image, w, h)
    missing_clut = 0
    import numpy as np
    vram_np = np.frombuffer(vram, dtype=np.uint8).reshape(512, 1024)
    for key in sorted(ext):
        cba, tsb = key
        page_x = (tsb & 0x0F) * 64
        page_y = 256 if (tsb & 0x10) else 0
        clut_x = (cba & 0x3F) * 16
        clut_y = (cba >> 6) & 0x1FF
        umin, umax, vmin, vmax = ext[key]
        w, h = umax - umin + 1, vmax - vmin + 1
        pal = cluts.get((clut_x, clut_y))
        if pal is None or len(pal) < 16:
            missing_clut += 1
            img = Image.new("RGBA", (w, h), (255, 0, 255, 255))
        else:
            pal_rgb = np.array([psx_to_rgb(c) for c in pal[:16]], dtype=np.uint8)
            idx = vram_np[page_y + vmin:page_y + vmax + 1, page_x + umin:page_x + umax + 1]
            rgb = pal_rgb[idx]  # (h, w, 3)
            rgba = np.dstack([rgb, np.full((h, w), 255, dtype=np.uint8)])
            img = Image.fromarray(rgba, "RGBA")
        cells.append((key, img, w, h))

    # shelf pack
    placements = []  # (key, img, ax, ay)
    x = y = row_h = 0
    for key, img, w, h in cells:
        if x + w > ATLAS_COL_W:
            y += row_h
            x, row_h = 0, 0
        placements.append((key, img, x, y))
        x += w
        row_h = max(row_h, h)
    atlas_h = y + row_h
    atlas = Image.new("RGBA", (ATLAS_COL_W, atlas_h), (0, 0, 0, 255))
    cell_origin = {}
    for key, img, ax, ay in placements:
        atlas.paste(img, (ax, ay))
        cell_origin[key] = (ax, ay)
    atlas_path = out_dir / f"stg_{letter}_atlas.png"
    atlas.save(atlas_path)

    # contact sheet for own-eyes verification (max ~48px tall thumbs in grid)
    thumbs = []
    for key, img, w, h in cells:
        th = img.copy()
        th.thumbnail((128, 128))
        thumbs.append((f"{key[0]:04x}_{key[1]:04x}", th))
    cols = 8
    tw, thh = 140, 150
    sheet = Image.new("RGB", (cols * tw, ((len(thumbs) + cols - 1) // cols) * thh), (20, 20, 20))
    from PIL import ImageDraw
    dr = ImageDraw.Draw(sheet)
    for i, (name, th) in enumerate(thumbs):
        ox, oy = (i % cols) * tw, (i // cols) * thh
        sheet.paste(th, (ox + (tw - th.width) // 2, oy + 4))
        dr.text((ox + 4, oy + thh - 14), name, fill=(200, 200, 200))
    sheet.save(work_dir / f"contact_{letter}.png")

    # regenerated OBJ: atlas-space UVs + TMD vertex colors
    obj_lines = [f"# Tekken 3 stg_{letter} panorama - TEXTURED atlas "
                 f"(game/assets/stages/t3/stg_{letter}_atlas.png).",
                 f"# UVs are atlas-space (v flipped: vt = 1 - v/H). "
                 f"v lines carry TMD vertex colors (r g b, PSX /128).",
                 f"# {len(corners)} verts, {len(corners)//3} tris, "
                 f"{len(cells)} atlas cells, {ntim} TIMs blitted."]
    remap = {}
    for key, x, y_, z, u, vv, r, g, b in corners:
        if key is None:
            uu, vvv = 0.0, 0.0
        else:
            ax, ay = cell_origin[key]
            umin = ext[key][0]; vmin = ext[key][2]
            uu = (ax + (u - umin)) / ATLAS_COL_W
            vvv = 1.0 - (ay + (vv - vmin)) / atlas_h
        remap_key = (x, y_, z, round(uu, 6), round(vvv, 6), round(r, 4), round(g, 4), round(b, 4))
        obj_lines.append(f"v {x} {y_} {z} {r:.4f} {g:.4f} {b:.4f}")
        obj_lines.append(f"vt {uu:.6f} {vvv:.6f}")
    nv = len(corners)
    for i in range(0, nv, 3):
        a, b_, c_ = i + 1, i + 2, i + 3
        obj_lines.append(f"f {a}/{a} {b_}/{b_} {c_}/{c_}")
    (out_dir / f"stg_{letter}_panorama.obj").write_text("\n".join(obj_lines) + "\n")

    return {
        "letter": letter, "verts": nv, "tris": nv // 3, "cells": len(cells),
        "tims": ntim, "atlas": (ATLAS_COL_W, atlas_h),
        "missing_clut": missing_clut,
        "atlas_bytes": atlas_path.stat().st_size,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bns", required=True)
    ap.add_argument("--table", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--stages", default=",".join(l for _, l in STAGES))
    args = ap.parse_args()

    table = pickle.load(open(args.table, "rb"))
    by_id = {t[0]: t for t in table}
    bns = open(args.bns, "rb")

    def get(rec):
        rid, sector, size = by_id[rec]
        bns.seek(sector * 2048)
        return bns.read(size)

    out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)
    work_dir = Path(args.work); work_dir.mkdir(parents=True, exist_ok=True)
    want = set(args.stages.split(","))

    report = []
    for number, letter in STAGES:
        if letter not in want:
            continue
        tmd = get(56 + number)
        arc = get(36 + number)
        info = build_stage(letter, tmd, arc, out_dir, work_dir)
        report.append(info)
        print(f"stage {letter}: {info['verts']}v/{info['tris']}t "
              f"{info['cells']} cells atlas {info['atlas'][0]}x{info['atlas'][1]} "
              f"{info['atlas_bytes']//1024}KB missing_clut={info['missing_clut']}")

    import json
    (work_dir / "atlas_report.json").write_text(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

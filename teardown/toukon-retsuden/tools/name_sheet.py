#!/usr/bin/env python3
"""Build the English name sheet for Toukon Retsuden (PAC_GAME_MES bpe01).

Harvests the block-caps glyphs from the US (Power Move Pro Wrestling)
name sheet, then renders the 16 NJPW full names condensed to fit the
128px row width. The US glyphs are ~10px wide; the longest NJPW name
(JYUSHIN THUNDER LYGER, 21 chars) needs ~6px/char, so glyphs are
downscaled 2:1 horizontally (OR-sampled to preserve strokes) and
rendered at variable ink width + 1px spacing, centered per row.

Output: a 128x256 4bpp TIM with the JP sheet's header/palette (index 0
= white, 1 = black background), ready to BPE-compress into slot 1 of
PAC_GAME_MES.

Usage:
  python3 name_sheet.py [--out <tim>] [--png <png>]
"""
import struct
import sys
from pathlib import Path

HERE = Path(__file__).parent
WORK = HERE.parent / "work"

US_NAMES = ["DA' JUDGE", "DANNY MCGEE", "COMMANDANT", "ZOMBIE",
            "CHAINGANG", "MALIBU MIKE", "LANCE", "THE EGYPTIAN",
            "AREA 51", "ORANGE", "EL TEMBLOR", "KING OG", "SPARROW",
            "LYGER", "GORGON", "SALLIE"]

# JP roster order (matches the JP sheet rows + EXE name order)
JP_NAMES = ["TATSUMI FUJINAMI", "RIKI CHOSYU", "KEIJI MUTOH",
            "MASAHIRO CHONO", "SHINYA HASHIMOTO", "HIROSHI HASE",
            "KENSUKE SASAKI", "SHIRO KOSHINAKA", "JYUSHIN THUNDER LYGER",
            "HIROYOSHI TENZAN", "KOHJI KANEMOTO", "SCOTT NORTON",
            "THE GREAT MUTA", "POWER WARRIOR", "KERO-CHAN",
            "TIGER HATTORI"]


def parse_tim_4bpp(data):
    """Return (header_bytes, clut_bytes, w, h, idx_grid, vram_xy)."""
    magic, flags = struct.unpack_from("<II", data, 0)
    assert magic == 0x10 and (flags & 3) == 0, "not a 4bpp TIM"
    assert flags & 8, "no CLUT"
    off = 8
    clen, cx, cy, cw, ch = struct.unpack_from("<IHHHH", data, off)
    clut = data[off:off + clen]
    off += clen
    ilen, ix, iy, iw, ih = struct.unpack_from("<IHHHH", data, off)
    px = data[off + 12:off + ilen]
    w, h = iw * 4, ih
    grid = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            byte = px[y * (w // 2) + x // 2]
            grid[y][x] = (byte >> 4) if (x & 1) else (byte & 0xF)
    header = data[:8]
    return header, clut, w, h, grid, (ix, iy)


def build_tim_4bpp(header, clut, w, h, grid, vram_xy):
    """Pack an index grid back into a 4bpp TIM with the given header/CLUT."""
    px = bytearray()
    for y in range(h):
        for x in range(0, w, 2):
            px.append((grid[y][x] & 0xF) | ((grid[y][x + 1] & 0xF) << 4))
    ilen = 12 + len(px)
    img_hdr = struct.pack("<IHHHH", ilen, vram_xy[0], vram_xy[1],
                          w // 4, h)
    return header + clut + img_hdr + bytes(px)


def harvest_glyphs(grid):
    """Segment the US sheet rows into per-character bitmaps.

    Returns dict char -> list of 10 row-bitmasks (ink = index 0).
    Glyph rows are y 2..11 within each 16px row.
    """
    glyphs = {}
    for row, name in enumerate(US_NAMES):
        y0 = row * 16 + 2
        # column ink profile for this row (10px tall)
        cols = []
        for x in range(128):
            ink = any(grid[y0 + dy][x] == 0 for dy in range(10))
            cols.append(ink)
        # segments = runs of ink columns separated by blank columns
        segs = []
        x = 0
        while x < 128:
            if not cols[x]:
                x += 1
                continue
            x0 = x
            while x < 128 and cols[x]:
                x += 1
            segs.append((x0, x))  # [x0, x)
        # If adjacent glyphs touch (no blank column between them) we
        # get fewer segments than characters: split the widest
        # segment at its narrowest ink column, one split at a time,
        # until the counts match.
        chars = [ch for ch in name if ch != " "]
        def col_ink(xx):
            return sum(1 for dy in range(10)
                       if grid[y0 + dy][xx] == 0)
        while len(segs) < len(chars):
            # widest segment
            wi = max(range(len(segs)), key=lambda i: segs[i][1] - segs[i][0])
            a, b = segs[wi]
            if b - a < 8:
                break  # nothing wide enough left to split
            mid_lo = a + (b - a) // 4
            mid_hi = b - (b - a) // 4
            best = min(range(mid_lo, mid_hi),
                       key=lambda xx: (col_ink(xx), abs(xx - (a + b) // 2)))
            segs[wi:wi + 1] = [(a, best), (best, b)]
        # map segments to characters: spaces produce a gap >= 3 blank
        # columns between segments; the name's non-space chars map
        # 1:1 to segments in order
        chars = [ch for ch in name if ch != " "]
        if len(segs) != len(chars):
            print(f"WARN row {row} {name!r}: {len(segs)} segs vs "
                  f"{len(chars)} chars", file=sys.stderr)
        for (x0, x1), ch in zip(segs, chars):
            if ch in glyphs:
                continue
            rows = []
            for dy in range(10):
                mask = 0
                for xx in range(x0, x1):
                    if grid[y0 + dy][xx] == 0:
                        mask |= 1 << (x1 - 1 - xx)
                rows.append(mask)
            glyphs[ch] = (x1 - x0, rows)
    return glyphs


def condense(mask_rows, width):
    """Downscale a glyph 2:1 horizontally (OR-sample column pairs)."""
    nw = (width + 1) // 2
    out = []
    for mask in mask_rows:
        nm = 0
        for j in range(nw):
            # source columns 2j and 2j+1 (bit positions from the left)
            b = 0
            for k in (0, 1):
                src_col = 2 * j + k
                if src_col < width:
                    bit = (mask >> (width - 1 - src_col)) & 1
                    b |= bit
            if b:
                nm |= 1 << (nw - 1 - j)
        out.append(nm)
    # trim blank side columns
    while nw > 1 and all((m >> (nw - 1)) & 1 == 0 for m in out):
        out = [m & ((1 << (nw - 1)) - 1) for m in out]
        nw -= 1
    while nw > 1 and all(m & 1 == 0 for m in out):
        out = [m >> 1 for m in out]
        nw -= 1
    return nw, out


def make_f(glyphs):
    """Build 'F' from 'E' by clearing its bottom bar (rows 7-9)."""
    w, rows = glyphs["E"]
    rows = list(rows)
    for dy in (7, 8, 9):
        # keep only the leftmost 2 columns (the stem)
        rows[dy] &= (0b11 << (w - 2)) if w >= 2 else rows[dy]
    return w, rows


def make_hyphen():
    """Simple mid-height bar for '-' (KERO-CHAN)."""
    rows = [0] * 10
    rows[5] = 0b1111
    rows[6] = 0b1111
    return 4, rows


def render_sheet(glyphs, names):
    """Render the 16 names into a 128x256 index grid (1 = background)."""
    grid = [[1] * 128 for _ in range(256)]
    condensed = {}
    for ch, (w, rows) in glyphs.items():
        condensed[ch] = condense(rows, w)
    for row, name in enumerate(names):
        # measure total width (glyph widths + 1px spacing, space = 3px)
        total = 0
        for ch in name:
            if ch == " ":
                total += 3
            else:
                total += condensed[ch][0] + 1
        total -= 1  # no trailing spacing
        x = max(0, (128 - total) // 2)
        y0 = row * 16 + 2
        for ch in name:
            if ch == " ":
                x += 3
                continue
            w, rows = condensed[ch]
            for dy in range(10):
                mask = rows[dy]
                for j in range(w):
                    if (mask >> (w - 1 - j)) & 1:
                        if 0 <= x + j < 128:
                            grid[y0 + dy][x + j] = 0
            x += w + 1
        print(f"row {row:2d} {name:22s} width {total:3d} at x={max(0, (128 - total) // 2)}")
    return grid


def main():
    out_tim = Path(sys.argv[sys.argv.index("--out") + 1]) \
        if "--out" in sys.argv else WORK / "new-namesheet.tim"
    out_png = Path(sys.argv[sys.argv.index("--png") + 1]) \
        if "--png" in sys.argv else WORK / "new-namesheet.png"
    us_data = (WORK / "us-gamemes-dec" / "bpe00_0xe94.bin").read_bytes()
    jp_data = (WORK / "gamemes-dec" / "bpe01_0xd20.bin").read_bytes()
    _, _, _, _, us_grid, _ = parse_tim_4bpp(us_data)
    header, clut, w, h, _, vram = parse_tim_4bpp(jp_data)
    glyphs = harvest_glyphs(us_grid)
    print(f"harvested {len(glyphs)} glyphs: {''.join(sorted(glyphs))}")
    missing = set("".join(JP_NAMES)) - set(glyphs) - {" ", "-"}
    print("missing glyphs:", missing or "none")
    if "F" not in glyphs:
        glyphs["F"] = make_f(glyphs)
        print("built F from E")
    glyphs["-"] = make_hyphen()
    grid = render_sheet(glyphs, JP_NAMES)
    tim = build_tim_4bpp(header, clut, w, h, grid, vram)
    out_tim.write_bytes(tim)
    print(f"wrote {out_tim} ({len(tim)} bytes)")
    # PNG preview
    sys.path.insert(0, str(HERE))
    from tim2png import parse_tim
    img = parse_tim(tim)
    img = img.resize((img.width * 4, img.height * 4),
                     __import__("PIL.Image", fromlist=["Image"]).NEAREST)
    img.save(out_png)
    print(f"wrote {out_png}")


if __name__ == "__main__":
    main()

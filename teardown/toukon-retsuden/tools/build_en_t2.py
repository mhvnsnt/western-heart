#!/usr/bin/env python3
"""Build the English T2 atlas for Toukon Retsuden (TR1) slot 203.

The T2 atlas holds the results headers + save/load messages + digits:
  y=0   digits 0-9
  y=16  GAUNTLET RESULTS
  y=32  TOURNAMENT RESULTS
  y=48  PPW CHAMPIONS          <- JP: IWGP title holders
  y=64  ( save enabled )       <- JP: (best bout save)
  y=80  LOAD FAILED
  y=96  SAVE FAILED
  y=112 FORMATTING

The US version (Power Move Pro Wrestling) already has all of these in
English, so the base is the US T2 TIM verbatim — except row y=48, which
says "PPW CHAMPIONS". This game is NJPW/IWGP, not PPW, so that row is
re-rendered as "IWGP CHAMPS" from glyphs harvested out of the US T2
("IWGP CHAMPIONS" is too wide for the results-menu rect — it clipped
to "IWGP CHAMPIC" in DuckStation QA 2026-11-20)
itself (same pixel font, same red shadow).

Usage:
  python3 build_en_t2.py
Outputs:
  work/en-t2.tim             - new TIM (US header/CLUT + EN pixels)
  work/font-hunt/en-t2.png   - preview PNG
"""
import struct
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
WORK = HERE.parent / "work"
US_T2 = WORK / "us-slot203.bin"

# US T2 words per row: (word, x_min, x_max) for glyph harvesting.
US_WORDS = {
    16:  [("GAUNTLET", 25, 108), ("RESULTS", 116, 183)],
    32:  [("TOURNAMENT", 8, 119), ("RESULTS", 127, 194)],
    48:  [("PPW", 21, 53), ("CHAMPIONS", 61, 155)],
    64:  [("save", 23, 56), ("enabled", 63, 119)],
    80:  [("LOAD", 75, 116), ("FAILED", 125, 176)],
    96:  [("SAVE", 76, 116), ("FAILED", 124, 175)],
    112: [("FORMATTING", 74, 176)],
}


def load_tim_idx(path):
    """Return (header_bytes, idx array, W, H) for a 4bpp TIM."""
    d = Path(path).read_bytes()
    assert d[:4] == b"\x10\x00\x00\x00", "not a TIM"
    clen = struct.unpack_from("<I", d, 8)[0]
    off = 8 + clen
    w16, h = struct.unpack_from("<HH", d, off + 8)
    W = w16 * 4
    px = d[off + 12:off + 12 + w16 * 2 * h]
    idx = [[0] * W for _ in range(h)]
    for y in range(h):
        for x in range(W):
            b = px[y * (W // 2) + x // 2]
            idx[y][x] = (b >> 4) if (x & 1) else (b & 0xF)
    return d[:off + 12], idx, W, h


def components(band):
    """Connected components in a binary band. Returns list of
    (x0, x1, y0, y1, pts), sorted by x0."""
    from collections import deque
    H = len(band)
    W = len(band[0])
    seen = [[False] * W for _ in range(H)]
    comps = []
    for y in range(H):
        for x in range(W):
            if band[y][x] and not seen[y][x]:
                q = deque([(y, x)])
                seen[y][x] = True
                pts = set()
                while q:
                    cy, cx = q.popleft()
                    pts.add((cx, cy))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < H and 0 <= nx < W and band[ny][nx] \
                                and not seen[ny][nx]:
                            seen[ny][nx] = True
                            q.append((ny, nx))
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                comps.append((min(xs), max(xs), min(ys), max(ys), pts))
    return sorted(comps, key=lambda c: c[0])


def harvest_glyphs(us_idx):
    """Harvest glyphs from the US T2, word by word."""
    glyphs = {}
    for y0, words in sorted(US_WORDS.items()):
        band = [[us_idx[y0 + dy][x] == 0 for x in range(256)]
                for dy in range(16)]
        comps = components(band)
        for word, wx0, wx1 in words:
            grp = [c for c in comps if wx0 <= (c[0] + c[1]) / 2 < wx1]
            nchars = len(word)
            if len(grp) != nchars:
                print(f"WARN y={y0}: word {word!r} has {len(grp)} comps, "
                      f"want {nchars}, skipping", file=sys.stderr)
                continue
            for ch, comp in zip(word, grp):
                x0, x1, yc0, yc1, pts = comp
                w, h = x1 - x0 + 1, yc1 - yc0 + 1
                norm = {(x - x0, y - yc0) for (x, y) in pts}
                if ch not in glyphs or (w * h) < glyphs[ch][0] * glyphs[ch][1]:
                    glyphs[ch] = (w, h, norm)
    return glyphs


def text_width(glyphs, text, spacing=2):
    w = 0
    for ch in text:
        if ch == " ":
            w += 8
        elif ch in glyphs:
            w += glyphs[ch][0] + spacing
    return w - spacing if text else 0


def render_text(canvas, glyphs, x, y, text, spacing=2, cap_top=2):
    cx = x
    for ch in text:
        if ch == " ":
            cx += 8
            continue
        if ch not in glyphs:
            print(f"WARN: no glyph for {ch!r}", file=sys.stderr)
            cx += 8
            continue
        w, h, pts = glyphs[ch]
        top = y + cap_top if h >= 9 else y + cap_top + (10 - h) - 1
        for (dx, dy) in pts:
            px, py = cx + dx, top + dy
            if 0 <= px < 256 and 0 <= py < len(canvas):
                canvas[py][px] = 0
        cx += w + spacing
    return cx


def apply_shadow_row(canvas, y0):
    """Red shadow (idx 2) at (x+1, y) for white pixels in one row band."""
    for y in range(y0, y0 + 16):
        for x in range(255):
            if canvas[y][x] == 0 and canvas[y][x + 1] == 1:
                canvas[y][x + 1] = 2


def main():
    header, us_idx, W, H = load_tim_idx(US_T2)
    print(f"US T2: {W}x{H}")
    glyphs = harvest_glyphs(us_idx)
    print(f"harvested {len(glyphs)} glyphs: {''.join(sorted(glyphs))}")

    # Start from the US pixels verbatim.
    canvas = [row[:] for row in us_idx]
    # Clear row y=48 (PPW CHAMPIONS) to black (idx 1).
    for y in range(48, 64):
        for x in range(256):
            canvas[y][x] = 1
    # Render "IWGP CHAMPS" LEFT-ALIGNED at x=21 on y=48 (matching the
    # US rows' left edge). Centering does NOT work here: the results-menu
    # rect's right edge is ~x=176, so centered text ("IWGP CHAMPIONS" at
    # 56-201, "IWGP CHAMPS" at 69-188) clips to "IWGP CHAMPIC" / "IWGP
    # CHAMP". Left-aligned at x=21 the 117px text ends at x=138, safely
    # inside the rect. (Proven by the v2/v3 DuckStation runs 2026-11-20.)
    text = "IWGP CHAMPS"
    x0 = 21
    end = render_text(canvas, glyphs, x0, 48, text, spacing=2)
    apply_shadow_row(canvas, 48)
    print(f"  y=48 {text!r} x={x0}-{end} (width {end - x0})")

    # Pack to 4bpp (low nibble = even x).
    px = bytearray((W // 2) * H)
    for y in range(H):
        for x in range(0, W, 2):
            lo = canvas[y][x] & 0xF
            hi = canvas[y][x + 1] & 0xF
            px[y * (W // 2) + x // 2] = (hi << 4) | lo
    tim = header + bytes(px)
    out_tim = WORK / "en-t2.tim"
    out_tim.write_bytes(tim)
    print(f"wrote {out_tim} ({len(tim)} bytes)")

    sys.path.insert(0, str(HERE))
    from tim2png import parse_tim
    img = parse_tim(tim)
    img.save(WORK / "font-hunt" / "en-t2.png")
    img.resize((1024, 512), Image.NEAREST).save(
        WORK / "font-hunt" / "en-t2-4x.png")
    print("wrote preview PNGs")


if __name__ == "__main__":
    main()

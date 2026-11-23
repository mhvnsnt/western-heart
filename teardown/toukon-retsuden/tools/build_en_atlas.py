#!/usr/bin/env python3
"""Build the English T1 menu atlas for Toukon Retsuden (TR1).

Harvests the English font glyphs from the US version's atlas (Power Move Pro
Wrestling slot 202), renders NJPW-correct English menu text into the JP atlas
layout (same TIM header/palette, same rect positions), and writes a new TIM.

Usage:
  python3 build_en_atlas.py
Outputs:
  work/en-atlas.tim        - new TIM (JP header/CLUT + EN pixels)
  work/font-hunt/en-atlas.png - preview PNG
  work/font-hunt/en-atlas-2x.png - 2x preview

Font: US atlas glyphs (white idx 0). JP-style red shadow (idx 2) at +1x.
Missing glyphs (X, J, ., #, /) are drawn in matching style.
"""
import struct
import sys
from collections import deque
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
WORK = HERE.parent / "work"
US_TIM = WORK / "us-slot202.bin"
JP_TIM = WORK / "t1-atlas.bin"

# US atlas words per row: (word, x_min, x_max). Comps are assigned to a
# word by x-center. Verified from comp x-ranges 2026-11-20. Gap-based
# grouping does NOT work: word gaps (7-15px) overlap the gap before "!"
# (8px) and the paren gaps in "(cont)" (7px).
US_WORDS = {
    0:   [("12", 0, 28), ("Man", 28, 60), ("Gauntlet", 60, 125),
          ("BEST", 125, 170), ("BOUTS", 170, 225)],
    16:  [("PPW", 50, 90), ("LEAGUE", 90, 160), ("off", 225, 256)],
    32:  [("PPW", 40, 90), ("TOURNAMENT", 90, 210), ("on", 225, 256)],
    48:  [("CHAMPIONSHIP", 0, 150), ("START", 150, 245)],
    64:  [("RESULTS", 0, 85), ("LOAD", 85, 150), ("DRAWS", 150, 230)],
    80:  [("2", 0, 36), ("PLAYER", 36, 116), ("WOW!", 116, 190),
          ("LEVEL", 190, 245)],
    96:  [("1", 0, 35), ("PLAYER", 35, 125), ("(cont)", 125, 210)],
    112: [("VIEW", 0, 55), ("DEMO", 55, 115), ("MATCH", 115, 180),
          ("MONO", 180, 245)],
    128: [("1", 0, 60), ("2", 60, 140), ("3", 140, 220)],
    144: [("NO", 0, 55), ("LIMIT", 55, 115), ("CROCK", 115, 195)],
    160: [("VENUE", 0, 60), ("SAVED", 60, 125), ("GAME", 125, 180),
          ("RING", 180, 250)],
    176: [("1st", 0, 50), ("FLOOR", 50, 115), ("SOUND", 180, 250)],
    192: [("STEREO", 0, 85), ("HARD", 85, 160), ("TIME", 160, 215),
          ("L", 215, 240), ("m", 240, 256)],
    208: [("DOME", 0, 70), ("VITO'S", 70, 150), ("EASY", 150, 250)],
    224: [("2nd", 0, 28), ("FLOOR", 28, 95), ("4", 95, 140),
          ("1st", 140, 188), ("W vs", 188, 235), ("T", 235, 256)],
    240: [("SLAM", 0, 48), ("ROCK", 48, 103), ("GO!", 103, 148),
          ("MEDIUM", 148, 235), ("s", 235, 256)],
}

# x-ranges to exclude from harvesting (symbols, not letters).
EXCLUDE = {176: [(112, 176)]}  # OXO symbols


def load_tim_pixels(path):
    """Return (header_bytes, pixel_bytes, pixel_index_array 256x256)."""
    data = Path(path).read_bytes()
    clen = struct.unpack_from("<I", data, 8)[0]
    off = 8 + clen
    px = data[off + 12:off + 12 + 32768]
    idx = [[0] * 256 for _ in range(256)]
    for y in range(256):
        for x in range(256):
            b = px[y * 128 + x // 2]
            idx[y][x] = (b >> 4) if (x & 1) else (b & 0xF)
    return data[:off + 12], px, idx


def components(band):
    """Connected components in a binary band. Returns list of
    (x0, x1, y0, y1, set-of-(x,y)), sorted by x0."""
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
                        if 0 <= ny < H and 0 <= nx < W and band[ny][nx] and not seen[ny][nx]:
                            seen[ny][nx] = True
                            q.append((ny, nx))
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                comps.append((min(xs), max(xs), min(ys), max(ys), pts))
    return sorted(comps, key=lambda c: c[0])


def harvest_glyphs(us_idx):
    """Harvest glyphs from the US atlas, word by word. Returns dict
    char -> (w, h, pts) with (0,0) at the glyph's top-left."""
    glyphs = {}
    for y0, words in sorted(US_WORDS.items()):
        band = [[us_idx[y0 + dy][x] == 0 for x in range(256)] for dy in range(16)]
        for (ex0, ex1) in EXCLUDE.get(y0, []):
            for dy in range(16):
                for x in range(ex0, ex1):
                    band[dy][x] = False
        comps = components(band)
        # Merge "!" dot+stem: two comps with same x-range (dot above stem).
        merged = []
        i = 0
        while i < len(comps):
            c = comps[i]
            if i + 1 < len(comps):
                n = comps[i + 1]
                if c[0] == n[0] and c[1] == n[1] and c[3] < n[2]:
                    pts = c[4] | n[4]
                    merged.append((c[0], c[1], min(c[2], n[2]), max(c[3], n[3]), pts))
                    i += 2
                    continue
            merged.append(c)
            i += 1
        # Assign comps to words by x-center.
        for word, wx0, wx1 in words:
            grp = [c for c in merged if wx0 <= (c[0] + c[1]) / 2 < wx1]
            nchars = len(word.replace(" ", ""))
            if len(grp) != nchars:
                print(f"WARN y={y0}: word {word!r} has {len(grp)} comps, "
                      f"skipping", file=sys.stderr)
                continue
            for ch, comp in zip(word.replace(" ", ""), grp):
                x0, x1, yc0, yc1, pts = comp
                w, h = x1 - x0 + 1, yc1 - yc0 + 1
                norm = {(x - x0, y - yc0) for (x, y) in pts}
                # Keep the smallest instance (same font; a bigger one is a
                # mis-merge).
                if ch not in glyphs or (w * h) < glyphs[ch][0] * glyphs[ch][1]:
                    glyphs[ch] = (w, h, norm)
    return glyphs


def draw_missing_glyphs(glyphs):
    """Draw X, J, ., #, /, l in the US font's style (caps ~10px tall)."""
    # X: two diagonals, 8 wide x 10 tall. The first version (7 wide, thin
    # diagonals meeting at one center pixel) read as "Y" in-game
    # ("G1 CLIMAY") — this one has 2px-thick diagonals, so the bottom
    # fork is unmistakable.
    x_pts = set()
    for y in range(10):
        lx = y * 6 // 9          # left diag x: 0..6
        rx = 7 - y * 6 // 9      # right diag x: 7..1
        x_pts.add((lx, y))
        x_pts.add((lx + 1, y))
        x_pts.add((rx - 1, y))
        x_pts.add((rx, y))
    glyphs["X"] = (8, 10, x_pts)
    # I: the harvested I is a ~3px bar that vanishes at spacing 0
    # ("TRAINING" read as "TRANNG"). Redraw as a 5px bar with top and
    # bottom serifs so it stays visible.
    i_pts = set()
    for y in range(10):
        i_pts.add((2, y))
    for x in range(5):
        i_pts.add((x, 0))
        i_pts.add((x, 9))
    glyphs["I"] = (5, 10, i_pts)
    # J: vertical bar + bottom hook, 6 wide x 10 tall.
    j_pts = set()
    for y in range(9):
        j_pts.add((4, y))
        j_pts.add((5, y))
    for x in range(0, 5):
        j_pts.add((x, 8))
        j_pts.add((x, 9))
    j_pts.add((0, 7))
    j_pts.add((1, 7))
    glyphs["J"] = (6, 10, j_pts)
    # Period: 2x2 dot at baseline (dy 8-9 of a 10px cell).
    glyphs["."] = (2, 10, {(0, 8), (1, 8), (0, 9), (1, 9)})
    # Hash: two verticals + two horizontals, 7 wide x 10 tall.
    h_pts = set()
    for y in range(10):
        h_pts.add((2, y))
        h_pts.add((5, y))
    for x in range(7):
        h_pts.add((x, 3))
        h_pts.add((x, 6))
    glyphs["#"] = (7, 10, h_pts)
    # Slash: diagonal, 6 wide x 10 tall.
    s_pts = set()
    for i in range(5):
        s_pts.add((5 - i, i * 2))
        s_pts.add((5 - i, i * 2 + 1))
    glyphs["/"] = (6, 10, s_pts)
    # Lowercase l: vertical bar, 3 wide x 10 tall (its only US instance is
    # merged with the 't' in "Gauntlet").
    l_pts = {(1, y) for y in range(10)} | {(2, y) for y in range(10)}
    glyphs["l"] = (3, 10, l_pts)
    return glyphs


# Glyphs harvested by explicit x-range (their words fail the count check,
# or the smallest-instance rule picked a wrong comp).
MANUAL = [
    ("u", 0, 81, 87),    # "Gauntlet" u
    ("e", 0, 105, 111),  # "Gauntlet" e
    ("M", 0, 30, 39),    # "Man" M (smallest-instance picked a C)
    ("L", 16, 95, 101),  # "LEAGUE" L (smallest-instance picked an I)
    ("W", 80, 134, 148),  # "WOW!" W (smallest-instance picked an O)
    ("m", 192, 227, 236),  # US "m" (minutes unit); the word harvest misses it
]


def manual_glyphs(us_idx, glyphs):
    """Harvest single glyphs by explicit (row, x0, x1) range."""
    for ch, y0, x0, x1 in MANUAL:
        pts = set()
        for y in range(y0, y0 + 16):
            for x in range(x0, x1 + 1):
                if us_idx[y][x] == 0:
                    pts.add((x - x0, y - y0))
        if not pts:
            print(f"WARN manual glyph {ch!r}: no pixels", file=sys.stderr)
            continue
        ys = [p[1] for p in pts]
        ytop = min(ys)
        norm = {(x, y - ytop) for (x, y) in pts}
        glyphs[ch] = (x1 - x0 + 1, max(ys) - ytop + 1, norm)
    return glyphs


# English atlas layout: (x, y, text, spacing). Positions match the JP fragments.
# y is the row; text is rendered with cap-top at y+2.
LAYOUT = [
    # y=0: Gauntlet + Best Bouts ("MAN GAUNTLET" spacing 0 at x=28:
    # spacing 1 is 111px wide and collides with BEST BOUTS at 128;
    # spacing 0 ends exactly at 128 so rect 33 shows "12 MAN GAUNTLET")
    (0, 0, "12", 1), (28, 0, "MAN GAUNTLET", 0), (128, 0, "BEST BOUTS", 1),
    # y=16: G1 League + OFF
    (0, 16, "G1 CLIMAX", 1), (144, 16, "LEAGUE", 0), (224, 16, "OFF", 1),
    # y=32: G1 Tournament + ON (TOURNAMENT moved left so the full-line
    # rect 36 (x=0-208) shows it whole)
    (0, 32, "G1 CLIMAX", 1), (80, 32, "TOURNAMENT", 0), (224, 32, "ON", 1),
    # y=48: IWGP Championship + Start + BVD
    (0, 48, "IWGP CHAMPIONSHIP", 0), (144, 48, "START", 1), (208, 48, "BVD", 1),
    # y=64: Results + Load + Draws
    (0, 64, "RESULTS", 1), (80, 64, "LOAD", 1), (176, 64, "DRAWS", 1),
    # y=80: VS Player 2 + Cement + Level + / (CEMENT spacing 0: must fit
    # in the options rect 112-176 AND stay out of game-menu rect 42 (0-128))
    (0, 80, "VS PLAYER 2", 1), (128, 80, "CEMENT", 0), (192, 80, "LEVEL", 1),
    (240, 80, "/", 1),
    # y=96: VS Computer + (cont.)
    (0, 96, "VS", 1), (36, 96, "COMPUTER", 0), (160, 96, "(cont.)", 1),
    # y=112: Seats + Demo Match + Mono
    (0, 112, "SEATS", 1), (64, 112, "DEMO MATCH", 1), (192, 112, "MONO", 1),
    # y=128: ring numbers as bare digits at the US positions (the US
    # release does exactly this). "NJPW2"/"NJPW3" as full words SPLIT on
    # the options screen (the RING row draws y=128 in 80px chunks, so any
    # word straddling x=80 or x=160 breaks in two: "NJ"+"PW2", "NJP"+"V3"
    # — proven by the ABCDE/FGHIJ diagnostic 2026-11-20). Single digits
    # can't straddle, so they render clean.
    (37, 128, "1", 1), (116, 128, "2", 1), (198, 128, "3", 1),
    (240, 128, "#", 1),
    # y=144: No Limit + Osaka (代 blanked)
    (0, 144, "NO LIMIT", 1), (96, 144, "OSAKA", 1),
    # y=160: Venue + Series + Ring (RING at x=208: the options label rect
    # starts at ~208 — at 192 the label showed only "NG")
    (0, 160, "VENUE", 1), (64, 160, "SERIES", 1), (208, 160, "RING", 1),
    # y=176: Ringside + (OXO copied from JP) + Sound
    (0, 176, "RINGSIDE", 1), (176, 176, "SOUND", 1),
    # y=192: Stereo + Strong + Time + L/m (TIME at x=144: the options
    # label rect starts at ~144 — at 128 the label showed only "ME" — and
    # 144 keeps TIME out of the STRONG options rect (64-144) so the LEVEL
    # row no longer shows "STRONG TII". "L"/"m" at the US positions: the
    # minutes unit — the options time value draws a 16px rect at ~224
    # that showed "ES" (the tail of LOSSES); the US version puts "m"
    # there instead. LOSSES (JP 敗分数) is dropped, as in the US release.)
    (0, 192, "STEREO", 1), (64, 192, "STRONG", 1), (144, 192, "TIME", 1),
    (209, 192, "L", 1), (227, 192, "m", 1),
    # y=208: Tokyo A + Tokyo B + Training (spacing 1: the I's vanished at
    # spacing 0 — "TRANNG" — and the new serif I needs the room; at x=180
    # because spacing 1 makes TRAINING 71px wide and x=192 overflows)
    (0, 208, "TOKYO A", 1), (96, 208, "TOKYO B", 1), (180, 208, "TRAINING", 1),
    # y=224: 2nd Floor + ring 4 + 1st + W vs + D ("4" as a bare digit at
    # the US position, matching the y=128 digits)
    # ("1st" was blanked in the v5 test and the SEATS fragment persisted,
    # so "1st" is innocent and restored.)
    (0, 224, "2nd FLOOR", 1), (117, 224, "4", 1), (176, 224, "1st", 1),
    (208, 224, "W vs", 1), (246, 224, "D", 1),
    # y=240: Outdoor + GO! + Sparring + s ("PLAY" doesn't fit the 32px slot)
    (0, 240, "OUTDOOR", 1), (112, 240, "GO!", 1), (144, 240, "SPARRING", 1),
    (240, 240, "s", 1),
]


def render_text(canvas, glyphs, x, y, text, spacing=1, cap_top=2):
    """Render text onto the canvas (256x256 index array). Returns end x."""
    cx = x
    for ch in text:
        if ch == " ":
            cx += 4
            continue
        if ch not in glyphs:
            print(f"WARN: no glyph for {ch!r}", file=sys.stderr)
            cx += 6
            continue
        w, h, pts = glyphs[ch]
        # Align caps (h>=9) to cap_top; lowercase (h<=7) sits on baseline.
        top = y + cap_top if h >= 9 else y + cap_top + (10 - h) - 1
        for (dx, dy) in pts:
            px, py = cx + dx, top + dy
            if 0 <= px < 256 and 0 <= py < 256:
                canvas[py][px] = 0  # white
        cx += w + spacing
    return cx


def apply_shadow(canvas):
    """JP-style red shadow: idx 2 at (x+1, y) for each white pixel."""
    for y in range(256):
        for x in range(255):
            if canvas[y][x] == 0 and canvas[y][x + 1] == 1:
                canvas[y][x + 1] = 2


def main():
    import os
    diag = os.environ.get("EN_ATLAS_DIAG") == "1"
    _, _, us_idx = load_tim_pixels(US_TIM)
    header, _, jp_idx = load_tim_pixels(JP_TIM)
    glyphs = harvest_glyphs(us_idx)
    glyphs = manual_glyphs(us_idx, glyphs)
    glyphs = draw_missing_glyphs(glyphs)
    print(f"harvested {len(glyphs)} glyphs: {''.join(sorted(glyphs))}")
    missing = [c for _, _, t, _ in LAYOUT for c in t if c != " " and c not in glyphs]
    if missing:
        print(f"WARN missing glyphs for layout: {sorted(set(missing))}", file=sys.stderr)

    # Start from black canvas (idx 1).
    canvas = [[1] * 256 for _ in range(256)]
    # NO OXO COPY: the JP ○×□ symbols (y=176, x=112-176) are NOT copied.
    # The options RINGSIDE rect extends past x=112 and caught the left
    # edge of the ○, showing a red fragment between RINGSIDE and 2nd
    # FLOOR on the SEATS row (proven by the v5/v6 tests 2026-11-20:
    # blanking "1st" did not remove it, removing OXO did). No verified
    # screen uses ○×□ (title, menus, options, char select, VS, match,
    # demo, results, champs, save prompts, best bouts all checked) —
    # if a future screen needs them, reposition them off y=176.
    # Render all layout strings.
    layout = LAYOUT
    if diag:
        # Diagnostic: replace NJPW2/NJPW3 with distinct letters so the
        # options-screen split shows exactly which letters land where.
        layout = [(x, y, {"NJPW2": "ABCDE", "NJPW3": "FGHIJ"}.get(t, t), sp)
                  for (x, y, t, sp) in LAYOUT]
        print("DIAGNOSTIC MODE: NJPW2->ABCDE, NJPW3->FGHIJ")
    for (x, y, text, sp) in layout:
        end = render_text(canvas, glyphs, x, y, text, spacing=sp)
        flag = " OVERFLOW" if end > 256 else ""
        print(f"  ({x:3d},{y:3d}) {text!r} -> ends x={end}{flag}")
    apply_shadow(canvas)

    # Pack to 4bpp (low nibble = even x).
    px = bytearray(32768)
    for y in range(256):
        for x in range(0, 256, 2):
            lo = canvas[y][x] & 0xF
            hi = canvas[y][x + 1] & 0xF
            px[y * 128 + x // 2] = (hi << 4) | lo
    tim = header + bytes(px)
    out_tim = WORK / "en-atlas.tim"
    out_tim.write_bytes(tim)
    print(f"wrote {out_tim} ({len(tim)} bytes)")

    # Preview PNG.
    sys.path.insert(0, str(HERE))
    from tim2png import parse_tim
    img = parse_tim(tim)
    img.save(WORK / "font-hunt" / "en-atlas.png")
    img.resize((512, 512), Image.NEAREST).save(WORK / "font-hunt" / "en-atlas-2x.png")
    print("wrote preview PNGs")


if __name__ == "__main__":
    main()

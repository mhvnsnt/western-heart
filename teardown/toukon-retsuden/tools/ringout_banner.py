#!/usr/bin/env python3
"""Create the "Ring Out!" banner for Toukon Retsuden (PAC_GAME_MES bpe07).

The US version has no single ring-out banner (only "Double Ring Out!"),
but that banner contains every glyph needed: "Ring Out!" is its last
10 characters. This script crops the "Ring Out!" portion from the US
"Double Ring Out!" banner (BIG_MES big07) and centers it on a fresh
256x32 canvas with the same palette/header as the JP bpe07 TIM.

Usage:
  python3 ringout_banner.py [--out <tim>] [--png <png>]
"""
import struct
import sys
from pathlib import Path

HERE = Path(__file__).parent
WORK = HERE.parent / "work"
sys.path.insert(0, str(HERE))
from name_sheet import parse_tim_4bpp, build_tim_4bpp


def main():
    out_tim = Path(sys.argv[sys.argv.index("--out") + 1]) \
        if "--out" in sys.argv else WORK / "new-ringout.tim"
    out_png = Path(sys.argv[sys.argv.index("--png") + 1]) \
        if "--png" in sys.argv else WORK / "new-ringout.png"
    us_data = (WORK / "us-bigmes-tim" / "big07_0x7640.bin").read_bytes()
    jp_data = (WORK / "gamemes-dec" / "bpe07_0x28c0.bin").read_bytes()
    _, _, uw, uh, us_grid, _ = parse_tim_4bpp(us_data)
    header, clut, jw, jh, _, vram = parse_tim_4bpp(jp_data)
    print(f"US Double Ring Out!: {uw}x{uh}; JP bpe07: {jw}x{jh}")
    assert (uw, uh) == (jw, jh), "size mismatch"
    # column ink profile (index 0 = white)
    cols = [any(us_grid[y][x] == 0 for y in range(uh)) for x in range(uw)]
    # find the gap between "Double" and "Ring": word gaps are ~11px,
    # letter gaps only 3-5px. Take the first >= 8px gap after x=64.
    gap_start = None
    x = 64
    while x < uw:
        if not cols[x]:
            x0 = x
            while x < uw and not cols[x]:
                x += 1
            if x - x0 >= 8:
                gap_start = x0
                gap_end = x
                break
        else:
            x += 1
    print(f"gap between Double and Ring: x {gap_start}..{gap_end}")
    # "Ring Out!" runs from gap_end to the last ink column
    x1 = max(xx for xx in range(uw) if cols[xx]) + 1
    crop = [[us_grid[y][xx] for xx in range(gap_end, x1)]
            for y in range(uh)]
    cw = x1 - gap_end
    print(f"Ring Out! crop: x {gap_end}..{x1} width {cw}")
    # center on a fresh canvas (background index 1 = black)
    grid = [[1] * jw for _ in range(jh)]
    ox = (jw - cw) // 2
    for y in range(jh):
        for xx in range(cw):
            grid[y][ox + xx] = crop[y][xx]
    tim = build_tim_4bpp(header, clut, jw, jh, grid, vram)
    out_tim.write_bytes(tim)
    print(f"wrote {out_tim} ({len(tim)} bytes)")
    from tim2png import parse_tim
    from PIL import Image
    img = parse_tim(tim)
    img = img.resize((img.width * 4, img.height * 4), Image.NEAREST)
    img.save(out_png)
    print(f"wrote {out_png}")


if __name__ == "__main__":
    main()

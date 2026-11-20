# VGS Format — Namco PS2 UI Screen (Urban Reign)

Reverse-engineered 2026-10-13 from `data/kageTest/vgs/title.vgs`,
`data/rt/menu.vgs`, `data/rt/f_menu.vgs` (DVD000.AFS).

## Overview

VGS = Namco's PS2 UI screen container: a display list of textured sprites
plus (usually) the embedded texture blob. Every menu screen, title card,
and HUD element is a `.vgs`. Tool: `tools/vgs_decode.py`.

## Header

| Offset | Size | Field |
|--------|------|-------|
| 0x00 | 4 | Magic `03 08 04 00` |
| 0x04 | 2 | Grid width W (u16) = number of **column** records |
| 0x06 | 2 | Grid height H (u16) = tiles per column |
| 0x08 | 4 | Reserved (0) |
| 0x0C | 4 | Section offset A (u32, near EOF — palette/tail) |
| 0x10 | 4 | Section offset B (u32) |
| 0x14 | 4 | Section offset C (u32) |
| 0x18 | 4 | Section offset D (u32, == C) |
| 0x1C | 4 | Reserved (0) |

## Column table

At 0x20: W records × 32 bytes. Each record:

```
[0x50000000, payload_offset(u32, absolute file offset), 0, 0,
 0x60000000, 0, 0, 0]
```

Grid is W columns × H rows; each column payload draws its H tiles.

## Display list payload

Sequence of 16-byte `(u64 value, u64 reg)` commands per column,
terminated by `reg == 0x60000000`. Sprite block registers observed:

| Reg | Meaning |
|-----|---------|
| 0x50 | Texture address (EE RAM address, u64 value) |
| 0x52 | Sprite dimensions: value low u32 = w, high u32 = h |
| 0x51, 0x53 | Block separators (0x53 ends a sprite) |
| 0x460 / 0x4 | Texture select variant |
| 0xE | Draw flags |
| 0x0 | Extra params (two u64s per sprite) |
| 0x60000000 | End of column payload |

Example (`title.vgs` col0): 320×224 main tile, plus 16×16, 16×8,
8×2, 48×24, 64×32 UI sprites. (`menu.vgs`: 640×39 menu bar,
192×32 / 320×32 / 128×64 items — matches a vertical menu.)

## Texture blob

Files with unique art embed the texture after the display lists
(`title.vgs`: 218,984 bytes @ 0x12BD0). Small/shared UI files
(`f_menu.vgs`, 752 bytes) are display-list-only and reference
external textures.

Pixel format: 8-bit indexed (values span full 0–255 range);
renders recognizably at 320 px wide, even-field deinterlaced.
Exact CLUT/color pipeline is still open — current decode is
luminance-approximate but structurally correct (title banner,
menu bars, text rows all visible).

## Status

- [x] Header / column table / payload offsets
- [x] Sprite (w,h) + texture-ref parsing (`vgs_decode.py --info`)
- [x] Texture blob location heuristic + PNG dump
- [ ] Exact CLUT / color decode (luminance approx. works)
- [ ] Batch decode of all 48 VGS files

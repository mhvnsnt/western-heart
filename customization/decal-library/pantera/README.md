# Pantera Decal Library

Owner-ordered (2026-10-17) interchangeable customization set for Pantera's Attire 3
(snow leopard). WWE/Tekken-style: every piece is a saved option that can be
swapped back in at any time — at the EXACT original placement, or repositioned.

## What's in here

**Logo options** (thigh decals, transparent PNGs — drop-in interchangeable):

| File | Description |
|---|---|
| `pantera-logo-white-scratches.png` | The ORIGINAL: black leaping panther + white scratch marks, extracted from the tights texture |
| `pantera-logo-red-scratches.png` | Variant: black panther + RED scratch marks |
| `pantera-logo-snow-leopard.png` | Owner's snow leopard artwork (blue keyed out) — **currently applied** on Attire 3 |

**Tights / pants options** (full textures, re-apply whole):

| File | Description |
|---|---|
| `tights-blue-snow-leopard.png` | Blue tights WITH the snow leopard decal baked in (current Attire 3 state) |
| `tights-blue-clean.png` | Blue tights, clean — neutral base for compositing any logo option |
| `pants-black-trunks.png` | Black trunks texture (with PANTERA logo) |

**`MANIFEST.json`** — machine-readable index: every entry's id, type
(`logo` | `tights` | `pants`), PNG, and `default_placement`. Placement is
parameterized (`pixel_rect` + `uv_rect` + scale/rotation), so the game UI can
move/resize/rotate a logo — or snap it back to the exact original spot.

## Canonical placement

The original thigh decal lives in `King_PantsLower_D`
(`Modelthighs_Material029` baseColor, 512x512) at pixel rect
**x=176, y=34, w=186, h=390**. Both thighs share this UV region (mirrored),
so one placement covers both legs. Pixel space: x right, y DOWN from the
top-left of the texture as stored in the GLB.

## Swapping a logo

1. Take `tights-blue-clean.png` (or the current tights texture).
2. Composite the logo PNG into the canonical rect (contain-fit, centered) —
   or anywhere else at any scale/rotation the customization UI allows.
3. Re-embed as image 44 (`Modelthighs_Material029` baseColor) in
   `roster/pantera/attires/snow-leopard/pantera-snow-leopard.glb`.
4. To put the original back exactly: composite
   `pantera-logo-white-scratches.png` at the canonical rect. Nothing else moves.

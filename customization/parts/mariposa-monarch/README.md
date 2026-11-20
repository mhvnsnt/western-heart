# Mariposa — "Monarch" Reskin Library

Mariposa's FIRST custom look (owner order 2026-10-18): a monarch-butterfly wing
colorway following the Pantera Attire-3 pattern. Texture work only — no
geometry, rig, or deletion changes.

## The look

- **Wing membranes:** indigo/violet -> vibrant monarch orange (luminance-mapped
  colorize; variation preserved, veins/borders deepened to black).
- **Eye-spots:** PRESERVED — the realistic wing eyes are kept intact (cream
  sclera masked out of the recolor). Their blue irises double as the
  blue-morpho accents.
- **Untouched:** black braided hair, skin, gold ring belt, dark attire/leggings.
- **Silhouette:** unchanged (butterfly wings, T-pose-ish stance).

## Files

- `mariposa-color-original.jpg` — original 4096x4096 color texture, extracted
  byte-identical from `game/assets/models/mariposa.glb`.
- `mariposa-color-monarch.jpg` — the Monarch reskin (currently applied).
- `MANIFEST.json` — parameterized placements (single-texture full replace).
- `README.md` — this file.

## The reskinned model

`roster/mariposa/attires/monarch/mariposa-monarch.glb` — full model with the
Monarch texture embedded. Original `game/assets/models/mariposa.glb` untouched.

## How to swap

See `MANIFEST.json` > `how_to_swap`. Both options are drop-in full replacements
of image 0 (`Color_187bb8a9-...`). Nothing is overwritten — every variant is
saved, Tekken/WWE-style.

## Eyes

Mariposa's eyes are painted into the single 4096x4096 color map (Tripo-baked,
no separate eye texture). Her ORIGINAL eyes are preserved in the original
texture. The universal yellow tiger eye (`customization/eye-library/`) is
available as a swappable option — composite the 128x128 tiger eye into her eye
UV rect (see eye-library `character_mappings` for Mariposa). Her default eyes
were NOT overwritten.

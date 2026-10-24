# KayKit Adventurers — Creation Suite Parts

14 separated, named parts from the KayKit Character Pack: Adventurers 1.0
(Kay Lousberg, kaykit.com), **CC0-1.0** — free for personal, educational and
commercial projects, no attribution required.

## What's here

| Slot | Parts |
|------|-------|
| Headgear (3) | Barbarian fur hat, Knight helmet, Mage wizard hat |
| Tops (4) | Barbarian wrap, Knight armor, Mage robe, Rogue tunic |
| Bottoms (4) | Barbarian / Knight / Mage / Rogue leg pairs |
| Accessories (3) | Cape, Round shield, Spike shield |

Every part is a self-contained GLB with its material and texture embedded.
All parts own-eyes verified via front renders (see `*-front.png`).

## Attach guide

Parts are static meshes in KayKit character space (origin at feet, ~2 units
tall). Suite attach: headgear -> head bone socket; tops -> spine/chest;
bottoms -> hips/legs; cape -> neck/back (enable double-sided); shields ->
hand/forearm. Auto-scale to fit non-standard bodies.

## Provenance

Separated from the 5 character GLBs via Blender mesh extraction
(`~/workspace/customization-pulls/kaykit/` staging, 2026-10-08 pull).
Materials and textures preserved per part. Nothing modified, nothing deleted
from the source characters.

## Honest flags

- Stylized low-poly house style — not photorealistic WWE 2K rips.
- Rogue's hood is fused with the head in a single mesh+material; not separable,
  not shipped.
- Each GLB embeds its character texture (~3.2MB/part); textures are duplicated
  across parts from the same character. Self-contained by design.

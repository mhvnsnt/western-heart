# CHATUR (Rahkasa) — PARTS.md

Attire 1: `roster/rahkasa/attires/attire1/model.glb` (3.7 MB) — byte-inspected 2026-10-23.
Source `.blend`: `roster/rahkasa/intake/RahkasaV1.1.blend` (zstd-compressed stream; decompresses to a valid `BLENDER` file).

**Summary: 1 mesh.** The entire body is a single baked mesh. There are NO separable clothing meshes — Chatur ships nude (spirit body); every garment must be authored new in the creation suite. The `.blend`'s extra objects are rig widgets, not wearable parts.

## Mesh inventory

| # | Mesh name | Verts | Region | Description | Category | Swappable | Layer |
|---|-----------|-------|--------|-------------|----------|-----------|-------|
| 1 | `ReVAmped_body_base_female_standard` | 118,261 | full body | The complete four-armed spirit body in one mesh (938 primitives, 2 materials: `AO`, `Material_002`). Unrigged static (0 skins, 1 node). | full-body | no — base body, never removed | skin |

## Source `.blend` objects (not in GLB — rig/intake aids, NOT parts)

| Object | What it is | Ships? |
|--------|------------|--------|
| `OBRahkasaBody` | body mesh (source of the GLB mesh) | yes (as the GLB) |
| `OBRahkasaHair` | hair mesh | **NO — not exported to the GLB** (rig-lane follow-up: export or rebuild) |
| `OBRahkasaRIG` / `OBRahkasaRIG_Deform` | armatures | no (rig lane) |
| `OBWGT*` | IK/rig widget objects | no |
| `OBNSFWNipples` | nipple meshes | no (detail pass decision) |
| `OBCamera`, `OBFloor`, `OBPoint*`, `OBgodrays` | intake scene dressing | no |

## Four arms — verified

Rig bone inspection of the decompressed `.blend` confirms the four-armed structure: **four forearm chains per side** (`forearm.L`, `forearm.L.001`, `forearm.L.002`, `forearm.L.003`, mirrored on R), with matching upper-arm/hand duplicates. The extra arm pairs are real geometry. Creation-suite clothing for Chatur must support 4-arm sleeve variants.

## Creation-suite notes

- **Tops:** none exist — author new (must drape over 4 arms; sleeve system needs a 4-arm variant).
- **Bottoms:** none exist — author new.
- **Full-body:** the base mesh itself (category full-body, not swappable).
- **Underwear:** none — author new.
- **Accessories:** none in GLB. Hair exists in the `.blend` (`OBRahkasaHair`) but was not exported — either export it or rebuild in-suite.
- **Gloves / footwear / headwear:** none — author new.
- Every future garment layers OVER the single body mesh (layer: clothing > skin). No hide-to-undress path exists for this model — undress is a no-op (she is the body).

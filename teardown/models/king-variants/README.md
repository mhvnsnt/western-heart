# King Model Variants — DeviantArt Pull (2026-10-13)

5 King-family 3D model archives pulled from DeviantArt (logged in as fmmgmars),
organized 2026-10-13. All models are Bandai Namco property, collected for
reverse-engineering reference (steal-like-an-artist playbook).

**Storage:** original archives live on GitHub Release
[`king-variants-2026-10-13`](https://github.com/mhvnsnt/western-heart/releases/tag/king-variants-2026-10-13).
Extracted working copies live here (local only, ~2.1 GB total).
SHA-256 checksums: `_incoming/SHA256SUMS.txt`.

## Variants

### 1. t8-king-base-1p-whitemagesunny/ — Tekken 8 King (Base / 1P)
- **Archive:** `Tekken_8_-_King_TK8_Base.7z` (106,832,127 bytes)
- **Artist:** WhiteMageSunny (DeviantArt)
- **Format:** FBX (5 part files) + TGA textures — 53 files, 237 MB extracted
- **Rig:** 33,021 verts / 50,950 polys total
  - Torso 9,438v / 17,366p · Feet 2,494v / 4,338p · Head 8,608v / 11,212p ·
    Head 2 8,316v / 10,636p · Legs 4,165v / 7,398p
- **Note:** FBX part files are internally labeled "King S2" despite the archive
  being the TK8 Base — verify against the S2 variant before treating as 1P.
- **Status:** DUPLICATE — byte-identical archive already on the release
  (`Tekken.8.-.King.TK8.Base.7z`).

### 2. t8-king-s2-whitemagesunny/ — Tekken 8 King (Season 2)
- **Archive:** `Tekken_8_-_King_S2.rar` (119,455,403 bytes)
- **Artist:** WhiteMageSunny (DeviantArt)
- **Format:** FBX (single `King S2.fbx`) + TGA textures — 106 files, 478 MB extracted
- **Rig:** 29,507 verts / 43,462 polys
- **Status:** DUPLICATE — byte-identical archive already on the release
  (`Tekken.8.-.King.S2.rar`).

### 3. t8-king-tekken3-sticklove/ — Tekken 8 King in Tekken 3 legacy outfit
- **Archive:** `Tekken8_King_Tekken3.7z` (110,601,820 bytes)
- **Artist:** Sticklove (DeviantArt)
- **Format:** XPS (.mesh + .mesh.ascii) + TGA textures — 60 files, 378 MB extracted
- **Rig:** 297 bones · 22 meshes · 41,526 verts / 66,052 tris
- **Why it matters:** legacy Tekken 3 attire on a modern King base — directly
  relevant to the Tekken 3 = alt-costume rule (retro King vs modern King).

### 4. t7-king-1p-1vote4sake/ — Tekken 7 King (1P)
- **Archive:** `T7_King_1P.7z` (92,672,642 bytes)
- **Artist:** 1Vote4Sake (DeviantArt)
- **Format:** XPS binary `Generic_Item.mesh` + TGA textures — 182 files, 452 MB extracted
- **Rig:** 271 bones · 43 meshes · 34,909 verts / 54,612 tris
- **Attires:** 1P + 2P + Wet + 2PWet texture sets in subfolders
- **Note:** 54,612 tris matches the rigmodels "Tekken 7 King 54k static" spec —
  likely the same source mesh.

### 5. t8-armor-king-battle-cloth-whitemagesunny/ — Tekken 8 Armor King (Battle Cloth)
- **Archive:** `Tekken_8_-_Armor_King__Battle_Cloth_.rar` (132,892,118 bytes)
- **Artist:** WhiteMageSunny (DeviantArt)
- **Format:** FBX (2 files) + TGA textures — 66 files, 585 MB extracted
- **Rig:** `Armor King Battle Cloth.fbx` 30,361 verts / 48,870 polys;
  `Armor King Battle Cloth Head No Acc.fbx` (no head-accessory variant)
- **Why it matters:** YUKIHYŌ is based on Armor King — this is his attire reference.

## Poly-count method
FBX counts via Blender 4.0.2 headless import (exact). XPS ascii via text parse
(exact). XPS binary via custom parser (bone/uv/stride validated; 101-byte file
trailer unparsed, geometry counts exact).

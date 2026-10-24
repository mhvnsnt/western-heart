# BLENDER17-01 Direct Mesh Extractor

Direct mesh extractor for `.blend` files from the custom BLENDER17-01 fork
(popular with SmutBase uploaders). Bypasses Blender entirely.

## Format

**File header (17 bytes):** `BLENDER17-01v050X`
- `BLENDER` (7 bytes) — magic
- `17-01` (5 bytes) — fork identifier (replaces standard ptrsize+endian+version)
- `v0500` / `v0501` (5 bytes) — fork build version
- Files are usually wrapped in a **zstd stream** mislabeled `.blend`
  (magic `28 B5 2F FD`) — use `--auto` to decompress first.

**Block header (32 bytes)** — vs standard 24 bytes:
| Offset | Size | Field |
|--------|------|-------|
| 0 | 4 | Block code (e.g. `REND`, `ME\0\0`, `DNA1`) |
| 4 | 4 | SDNA index (STRC struct index — matches vanilla Blender) |
| 8 | 8 | Old pointer (memory address at save time) |
| 16 | 4 | Data size in bytes |
| 20 | 4 | Unknown |
| 24 | 4 | Count |
| 28 | 4 | Padding (0) |

**Key differences from standard:**
- Header is 17 bytes, not 12
- Block headers are 32 bytes, not 24 (64-bit) or 20 (32-bit)
- Mesh `mvert`/`mloop`/`mpoly`/`dvert` struct pointers are NULL — mesh arrays
  live in *untyped* DATA blocks (struct `raw_data`, sdna 0) matched by size
- Save-time pointers that DO survive: `Object.data` → ME block,
  `bArmature.bonebase`/`Bone.childbase` → Bone blocks,
  `MDeformVert.dw` → MDeformWeight entries. The block-header old-pointer
  map resolves all of them.

## Usage

```bash
# Decompressed 17-01 file
python3 extract.py <decompressed.blend> <output_dir>/

# Auto-decompress zstd-mislabeled .blend first
python3 extract.py --auto <file.blend> <output_dir>/

# Also usable as a module: detect(), decompress_zstd(), extract_blend17()
```

Outputs per mesh: `<name>.obj` (verts + faces + `vt` UVs + `usemtl`),
`<name>.mtl` (material base colors from MA blocks), `<name>.json`
(meta + deform weights as `{vidx: [[def_nr, weight], ...]}`).
Per file: `armature_<n>_<name>.json` (bone tree: name/head/tail/parent/children).

## Status

- ✅ Header parsing (incl. zstd auto-detect/decompress)
- ✅ Block walking (32-byte headers) + old-pointer resolution map
- ✅ DNA parsing (struct layouts, all field offsets from DNA — no hardcoding)
- ✅ Mesh discovery (ME blocks)
- ✅ Vertex extraction (MVert.co)
- ✅ Face extraction (MPoly + MLoop, robust: typed-size match + MLoop/UV classifier)
- ✅ UV layers (untyped float2-per-loop blocks; first layer → `vt`)
- ✅ Materials (MPoly.mat_nr → MA block name + r/g/b/roughness/metallic → MTL)
- ✅ Armatures (bonebase/childbase tree walk → JSON)
- ✅ Deform weights (MDeformVert → resolved MDeformWeight entries → JSON)
- ⚠️ Material slot → MA block mapping is file-order best-effort
      (mesh->mat array pointers are NULL; slot index mod material count)
- ⚠️ Deform-group names: Object.defbase is NULL in these files, so weights
      are emitted as def_nr indices; group names usually match bone names
- ❌ Normals not extracted (4.5 stores them as generic float3 layers)
- ❌ Custom fork binary not identified (web search found nothing)

## Files handled

- Mirko (Tobi) — `mirkoIK.blend` (v0500)
- Rahkasa (Chatur) — `RahkasaV1.1.blend` (v0501)
- Mina Ashido (Ryusan) — `Mina Ashido rigify.blend`
- Lily (Birodo) — `lily.blend`

## Wiring into creation suite

This extractor is the **fallback import path** for BLENDER17-01 files:
`tools/blender17-extract/route.py` exposes `handle_17xx(src, workdir)` —
detect → decompress → extract → build GLB (mesh + UVs + materials via a
dependency-free GLB writer) + sidecars (armature/weights JSON).
`tools/import_model.py` routes here when it sees the 17-byte header
(or a zstd-mislabeled `.blend`) instead of failing at the GLB gate.

Related: `tools/blend17-repair/blend17_to_standard.py` (PR #722, worker 75)
takes the *other* path — container repair → open in Blender ≥ 4.2 for full
fidelity (textures, shape keys, modifiers). Use the repair path when Blender
is available; use this extractor when it isn't, or when you need just the
mesh/UV/material/armature data fast.

## Materials and textures (per-mesh slots)

- `usemtl` uses each mesh's **own** slots (`Mesh.mat`, overridden by
  `Object.matbits`), never the file-wide material list. Out-of-range
  `mat_nr` clamps to the last slot, as Blender does. Blender 4.x int32
  `material_index` attributes are read; old byte arrays are the fallback.
- Images are mapped through each material's node tree: every TexImage node
  is followed downstream to the Principled socket it feeds (Base Color →
  `map_Kd`, Emission → `map_Ke`, Normal (via NormalMap) → `norm`, …).
- Image data: packed (`Image.packedfile`) first, then external
  `//textures\..` paths next to the source `.blend`, then
  `textures/<basename>`. Unresolved images print `[no data] image ...`.
  Output goes to `<out>/textures/`.

## retexture_glb.py — put real textures on an already-rigged GLB

```
gltf-transform dequantize in.glb plain.glb   # if meshopt/quantized
python3 retexture_glb.py plain.glb <extract_out_dir> out.glb [--uvs] --report rep.json
gltf-transform meshopt out.glb final.glb --level medium
```

Each GLB mesh is aligned to its source mesh (similarity fit + ICP, rejected
above 1% residual), each triangle takes the material (and with `--uvs` the
UVs) of the matching source face. Skins, joints, weights, animations and
triangle counts are unchanged; nothing is cut. Parts with no source slot keep
their shipped material. Write to a NEW file next to the old one, verify, then
rewire `game/js/assets.js`.

## Private T7 skin textures (Yukihyo)

`game/js/assets.js` `PRIVATE_SKIN_TEXTURES` maps Yukihyo's `MI_CH_malebody_<part>_02_skin`
materials to `T_CH_male_<part>_D.webp` under `game/assets/private/textures/t7-skin/male/`,
but only when `globalThis.__WH_PRIVATE_ASSETS` is set. Copy the files from the private
repo path `teardown/pakchunk0/textures/Character/Common/shader/Texture/skin/male/`.
Never commit them here. The King-face `MI_CH_knk_*`, loincloth and `MI_Cal_Mesh` maps
are still missing from every private pull, so Yukihyo stays quarantined.
Armor King: there are no T7 or TTT2 Armor King mask/face textures in the private repo.
`tekken7/king/` is a fan FBX rip with its own UVs, not the T7 `arm1u` layout.

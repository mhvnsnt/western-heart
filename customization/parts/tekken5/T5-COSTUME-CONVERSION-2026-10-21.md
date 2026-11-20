# TEKKEN 5 COSTUME-PACK CONVERSION — W7e (2026-10-21)

Gap-closure W7e: the conversion pass named in survey §S9
(`T5-CUSTOMIZATION-SURVEY-2026-10-21.md`). All 80 costume packs'
whole-costume models (sub02 NUDP + sub01 TIM2 textures) are now GLBs in
`CATALOG.json` `parts[]` at `FULL_BODY` granularity.

## Method (the proven W7b path, no hand-tooling)

1. **Reproduce** — TK5DATA1.BIN was NOT re-downloaded whole. Each pack's
   byte range was fetched from GitHub release `tekken5-disc-v1`
   (mhvnsnt/game-reverse-engineering) by HTTP Range against the release
   assets (packs live in `TK5DATA1.BIN.part_01`/`part_02`), using the E5
   file table (`0x27B5B0`, sector×2048) from the decompressed E5 module
   held in the teardown lanes. Each pack was then verified against the
   E5 word-sum checksum (`0x27E838`): stored raw if the sum matched, else
   LCG-XOR decrypted (seed = file index, FileTableGetPS2 method, as W7b)
   and re-checked. **80/80 packs checksum-verified** (all 80 took the
   decrypted path). Spot proof: pack 0240's sub01/sub02 are byte-identical
   (sha256) to the W7b probe copies extracted from the full disc assembly.
2. **Split** — per pack, the 19-entry archive table gives sub01 (TIM2
   texture set) and sub02 (NUDP costume model, magic-verified).
3. **Geometry** — ModelMagic (`NUDP` + `VIFerator`, the tooling W7b's
   renders proved) decodes the VIF streams (globalFlags 0x91/0x93). The
   W7e OBJ writer (`tools/nudp2obj_uv.py`) additionally emits the `vt`/`vn`
   streams VIFerator already parses and one `usemtl` per submesh carrying
   the NUDP material's `textureIndex`. PS2 UVs are kept raw — the data
   contains out-of-0..1 ranges (e.g. pack 0240 tex0: −2..5) that the GS
   addresses with REPEAT wrap; the GLB samplers/texture nodes use REPEAT.
4. **Textures** — TIM2 pictures decoded to PNG with `tim2dump` (the C
   tool pulled in by the teardown research lanes). Only the pictures a
   pack's materials actually reference are decoded and bound (per-pack
   texture-index sets are in each catalog entry's `textures` field).
5. **GLB** — Blender 4.0.2 (xvfb): OBJ import, per-material texture nodes
   (sRGB, REPEAT), mesh objects joined per material, glTF binary export
   with images embedded.
6. **Validation** — every GLB is re-parsed (header, JSON chunk, accessor
   counts): triangle count must equal the OBJ face count from the VIF
   decode, and every material must carry a baseColorTexture. Failures and
   skipped VIF blobs are logged per pack below — none are hidden.

## Storage (repo convention: release + manifest + pull-back proof)

- GLB bytes: GitHub release **`tekken5-costume-glbs-v1`**
  (mhvnsnt/western-heart), one asset per pack (`packNNNN-costume.glb`),
  plus `manifest.json` (per-file size + sha256 + geometry counts).
- Catalog entries keep the canonical repo path in `file`/`glb`
  (`customization/parts/tekken5/full_body/<slug>/<slug>.glb`) and carry
  the release coordinates + sha256 in `conversion.glb_release`.
- Pull-back proof: after upload, assets were re-downloaded from the
  release and their sha256 re-verified against the manifest
  (see "Pull-back verification" in the manifest / PR proof section).

## Character attribution

**None proven — `char_id` stays `null` on all 80 entries.** No
pack→character table exists in the held data: the E5/E6 frontend holds
customize screens but no per-pack character mapping (survey S3/S9), and
the contact-sheet visual IDs are survey evidence, not a mapping table.
Per the per-character isolation law and the W7e brief, attribution is
only set where data proves it; it does not here. Entries keep
`scope: "character"` (each pack IS one character's costume) with the
character unnamed.

## Results

- Packs reproduced + checksum-verified: **80/80** (all 80 via the
  LCG-decrypted path). The whole reproduction was run **twice**; the
  second run's sub02 sha256 matched the first run's on **80/80** packs,
  with identical VIF blob statistics and texture-index sets.
- Conversions: **79/80 fully textured GLBs** + **1 geometry-only**
  (below). Totals: 55,402,120 GLB bytes; 653,163 triangles; per-file
  size/sha256/geometry in `GLB-MANIFEST.json` (this directory and the
  release).
- VIF blobs: 31,461 decoded OK, **40 skipped** by the tolerant decoder
  across 11 packs (pack: skipped blobs — 0306: 1, 0339: 7, 0350: 3,
  0372: 1, 0526: 3, 0592: 1, 0669: 3, 0757: 5, 0768: 6, 0801: 2,
  0878: 8; also in each entry's `conversion.source_pack.vif_blobs_bad`).
  A skipped blob is one VIF DMA chunk whose stream desyncs ModelMagic's
  VIFerator; that chunk's submesh piece is absent from the GLB. The
  other 69 packs are blob-complete. Every GLB still passes structural
  validation (triangle count == decoded face count; all materials
  textured, except the one documented case below).

### The one partial conversion — pack 1109 (geometry only)

Pack 1109's sub01 is a **192-byte placeholder TIM2** (a single 8×8
4-bit picture) — the only pack of the 80 whose texture set is not in
its own pack (next-smallest sub01 is ~90 KB). Its model's only material
references `textureIndex 4`, which does not exist in that TIM2, and no
companion file in its group carries a TIM2. The costume's textures
therefore cannot be bound from pack data. Its GLB
(`pack1109-costume.glb`, 71,336 B, 856 tris) contains the full decoded
geometry with an untextured material, and its catalog entry carries
`conversion.status: converted_geometry_only_missing_pack_texture` with
`missing_tex_indices: [4]`. It is counted honestly as a partial, not
as a textured conversion.

## Proof renders

`proof/` in this directory: front textured renders (Cycles, frontal fill)
of packs 0240, 0515 and 0735 from the shipped GLBs, viewed by this lane
before delivery (see PR proof section for the frames).

## Tooling (this directory)

- `tools/fetch_convert.py` — range-fetch + checksum + split + OBJ + TIM2.
- `tools/nudp2obj_uv.py` — ModelMagic-based NUDP→OBJ (UV/normals/materials).
- `tools/blender_batch.py` — in-session Blender OBJ→GLB batch.
- `tools/validate_glb.py` — GLB structural validator.
- `tools/build_catalog.py` — CATALOG.json builder from the run manifest.
- `tools/render_proof.py` — textured proof renders from shipped GLBs.

## Remaining gaps (unchanged, still named in CATALOG.json)

- ctype-5 container models (VIF 0x82, undecoded) — teardown-lane format work.
- TK5DATA0.BIN (second cipher layer) — teardown-lane cipher work.
- Skull mask — NOT FOUND in DATA1 (survey S5).
- Pack→character attribution — needs a data-side mapping table.

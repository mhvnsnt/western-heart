# Pond model fix — 2026-11-03

Owner order (2026-11-03 ~17:09 CST), on seeing Pond's visual-gate renders:
she needs fixing in textures, eyes, and face; her crotch reads like a futa —
fix the crotch so she looks how she should. GROUND TRUTH = how she looks
when you download her file and open it CLEAN (the fresh source opened in
Blender), not the shipped/rigged version. The gate's "pelvis wedge is an
inherited source trait (A/B proven)" verdict is superseded by this order.
Method: Blender + whatever else helps; research first. Her T7 bank stands;
the model fix is its own job; her final video records the fixed model.

## What was actually wrong (evidence: docs/proof/2026-11-03/pond-model-fix/)

1. **The gate's A/B was circular.** The "orig" GLB the gate rendered is
   md5-identical to the 2026-10-23 rig conversion — the shipped file's own
   ancestor. Shipped vs "orig" geometry is byte-identical (max position
   delta 0.0 on all 15 primitives). The defects were baked in at the
   blend→GLB conversion, not by the SmutBase-6 fix lane.
2. **Crotch (D1, critical):** the conversion exported an object that is
   HIDDEN in the clean source. In the intake .blend
   (`roster/tsuyu-asui/intake/Tsuyu Asui IK/Tsuyu Asui IK.blend`, opened
   fresh in Blender 5.2.3), object `Penis` is authored
   hide_viewport=True, hide_render=True. In the GLB it became mesh
   `Mesh0000_004` (material literally named `penis`), 30,708 verts,
   protruding to z = +0.427 m at crotch height — 28.7 cm in front of the
   suit surface (z ≈ 0.145), further forward than her breasts (0.297), the
   forward-most point of the whole model. That is the wedge the owner saw.
3. **Bulge (D2):** GLB mesh3 (`Mesh0000_003`) is the .blend's `Bulge`
   object — exact tri-count match (8,284), same authored `boots` material,
   same UV sliver. Three facts override the 2026-10-22 intake KEEP note:
   (a) Bulge is authored HIDDEN in the clean .blend, exactly like Penis —
   in the owner's ground truth (clean open) it is not visible;
   (b) its vertex groups are the penis/balls bone chain
   (Penis0…Penis5, Balls, Balls.L/R, Bulge1) — it is part of that anatomy
   rig, not a cover over the female anatomy;
   (c) rendered kept, it hangs at the crotch as a dark mottled mass
   (z to 0.241) — proof-pondfix-after-keepbulge-q34-20261103.png — and
   still fails the owner's "reads female" test.
   The shipped fix therefore excludes BOTH hidden anatomy objects.
   A keep-bulge build (penis-only removal) was produced and is one file
   swap away if the owner rules otherwise:
   pond-fixed-keepbulge-20261103.glb, md5 1a755506fbfbe452567b70b9ac24b73e
   (lane scratch ~/workspace/_smutbase-t7-banks-20261103/pond-fix/).
4. **Eyes / hair / googles / belt (D3–D5):** the four "flat colour"
   materials were never flat in the source — the .blend carries their real
   images PACKED inside it, and the conversion dropped them, keeping only
   diffuse-colour stamps. Extracted byte-exact from Pond's own .blend:
   eyes 512×256 (pale sheet, two black oval eyes), hair 1024×512 (dark
   green with highlights), googles_mask 512×512, outfit 2048×2048. These
   are NOT in the repo intake textures/ folder (7 files only) — they live
   in the .blend. The fix wires all four back.
5. **UV regression (D6, shipped-only):** the previous encode's prune()
   deleted TEXCOORD_0 on all 6 flat prims. In the fixed build every prim
   carries UVs again (13/13 prims textured in the viewer, no errors).
6. **Boots (logged GAP, not fixed here):** the real `boots` object
   (3,096 polys, at her feet in the .blend, material `tsuyu-boots`) was
   dropped entirely by the conversion — no counterpart mesh exists in any
   GLB, which is why she renders barefoot. Restoring it is a rig-transfer
   job (transfer onto the 52-joint WH skeleton), NOT done here and not
   fabricated. Follow-on job, logged.

## The fix (this PR)

`roster/tsuyu-asui/attires/attire1/model-rigged-textured.glb` replaced with
the fixed derivative (8,235,624 B, md5 73be6cdbb62cc8276804a4acbca72aa5),
built from the shipped file's own decode with only these edits:

- Penis mesh and Bulge mesh removed (verts 295,975 → 240,415; tris
  98,721 → 80,201 — the deltas are exactly the two removed meshes).
  Whole-model z max 0.427 → 0.297; crotch slices now = suit surface
  0.145–0.165; every remaining mesh's skinned bbox identical to shipped.
- Eyes, hair, googles_mask, outfit materials wired to the images extracted
  byte-exact from her own intake .blend (sha256 verified in-file).
- TEXCOORD_0 restored on all prims; skins of remaining parts intact
  (7 skins × 52 joints — the two removed parts took their skins with them).
- Kept, verified byte-identical: all 5 pre-existing base images and the
  suit/boots metallicRoughness maps the fix lane added from her intake
  roughness PNGs; seam unification (117 → 0) preserved.

Method: Blender 5.2.3 scripted dump of the clean .blend (ground truth) →
codec decode of the shipped GLB (tools/anim/gltf_codec.mjs) → scripted
JSON/BIN edits (build_fix.py / build_fix2.py in the lane scratch) →
re-encode → per-part skinning audit reproducing the diff report's shipped
numbers before trusting the fixed ones → renders via the visual-gate
Chrome + three.js viewer.

## Proof (docs/proof/2026-11-03/pond-model-fix/)

- proof-pondfix-before-{front,q34,face}-20261103.png — shipped, as rejected
- proof-pondfix-after-{front,q34,face}-20261103.png — fixed: cone gone,
  crotch flush, hair dark green, authored eye texture in the close-up
- proof-pondfix-after-keepbulge-q34-20261103.png — the Bulge evidence
- pond-model-diff-20261103.md — clean-vs-shipped diff (the full audit)
- blend-ground-truth-20261103.md — the clean .blend dump
- build-log-20261103.md, audit-fixed-20261103.md — every edit + audit
- pond-verdict-fixedmodel.json — identity-gated play-probe AFTER the model
  swap: her T7 bank (PR: T7 banks for Pond + Ryusan) still binds and fires
  on the fixed model.

## Repeatability

For the next fighter whose conversion exported hidden objects: dump the
intake .blend's object visibility + packed images FIRST (that is the
ground truth), diff against the GLB per-mesh with per-part skinning, and
never A/B a GLB against its own conversion ancestor. Packed .blend images
are a texture source the intake textures/ folder does not show.

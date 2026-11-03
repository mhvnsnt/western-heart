# SmutBase Six Fix — Lane Handoff (2026-11-02)

Owner order (2026-11-02): "Correct the rig and textures on pond and ryusan and tobu and the other smutbase models fully. And the animations and moves." Method order (same day): "Use whatever industry standard stuff or game code from official games we have that can help u that u can access."

Canon pairings (docs/decisions/2026-10-23-smutbase6-parts-system.md — the ONLY source; an opposite pairing circulated earlier the same day from a corrupted tool-output stream and was retracted): **Pond = Tsuyu Asui (Raven) · Ryusan = Mina Ashido (Lucky Chloe) · Tobi = Mirko (Hwoarang) · Chatur = Rahkasa (True Ogre) · Megami = Parvati (Jun Kazama) · Menajerii = Vixen (Roger Jr.)**.

The game loads the six from SOURCE folders (game/js/assets.js + docs/rigs/RIG-AUDIT-2026-11-01.md); there are no roster folders for pond/ryusan/megami/chatur and NO rewiring was needed or done.

## Audit correction (read this before trusting the repo rig audit on these files)

tools/auto_rig/anim_check.py applies skins[0]'s inverse bind matrices to ALL primitives and does not dequantize KHR_mesh_quantization. Three of the six loaded files are multi-skin exports (three.js skins per-part), so the audit's region verdicts for them are tool artifacts:

- tsuyu-asui: audit said CONE FACE + CRUSHED ARMS. Per-part probe (tools/auto_rig/audit_parts.py, added by this lane): height 1.800 m, face Head 96.2%, head+hair Head 92.5% — the shipped rig is correct. The audit's seam column (position-based, skin-independent) IS valid for these files and is what the fixes below used.
- mina-ashido / miruko: coherent split-bone rigs, 1.800 m; their single-skin-style verdicts (SEAM CRACKS) were real and are fixed below.
- vixen: single skin, audit trustworthy except its ERROR (below). parvati, rahkasa: audit trustworthy, verdict OK.

## Per-fighter results (all numbers measured this lane; official tool = tools/auto_rig/batch_audit.py)

### Pond (Tsuyu) — PR #1530 — landed pending visual gate
- Defects: 117 disagreeing UV-seam copies; suit + boots Roughness maps dropped by the exporter (blanket roughnessFactor 0.8 instead).
- Fix: seam unification (117 -> 0); suit/boots metallicRoughnessTexture packed from intake Roughness PNGs (roster/tsuyu-asui/intake/textures/); factors -> 1.0; repo-codec re-encode. 7,053,488 B -> 9,467,192 B; 9 skins / 468 joints / 7 images verified on the encoded file.

### Ryusan (Mina) — PR #1532 (part 1 of 2) — landed pending visual gate; textures = part 2
- Defects: SEAM CRACKS 20,748; ZERO images; NO TEXCOORD_0 on any primitive (rerig export dropped UVs).
- Fix part 1: seam unification (20,748 -> 0, verdict OK); UV restoration by world-space barycentric transfer from sibling model-rigged.glb (11/11 prims carry TEXCOORD_0; UV file re-audits OK, 0 seams); repo-codec re-encode. 2,121,260 B -> 2,259,084 B.
- Part 2 (parked, evidence complete): the texture assignment authority is intake rigify.blend (Blender 5.0) — read this lane with Blender 5.2.3: 6 materials (body, eyes, hair, Mina-hero-outfit, Penis, skin.000); all 10 packed images unpacked and recovered in the lane scratch (body 2048, eyes, FaceS, hair, skin_head, mina body, mina penis, hero-outfit Base/Height/Roughness). Object map: boots/jacket/suit -> hero-outfit; Fur/Horns -> body; Hair -> hair; Mina -> skin.000/body/skin_head/eyes; Penis -> Penis. BUT every GLB in the lineage collapsed to 2 materials (body/eyes) with single-material meshes — the polygon material groups were lost in export, so prim-level assignment is NOT safely derivable. Faithful route: re-export from the blend through tools/model-import/rig_smutbase6.py carrying the blend's materials. Do NOT bake by guesswork.

### Tobi (Mirko) — PR #1529 — landed pending visual gate
- Defects: SEAM CRACKS 37,445; 5/11 materials missing maps that exist in her own intake.
- Fix: seam unification (37,445 -> 0, verdict OK; per-part probe confirms 36,798 -> 0 with region weights unchanged); texture completion from her own art only — Body x2 wired to her embedded body atlas set, hero-suit MR packed from intake Roughness+Metallic (roster/miruko/intake/miruko IK/textures/), belt AO from intake. Images 6 -> 8. Hair/Eyes/Eyeshadow: no source map exists (flat by source design — closed). Repo-codec re-encode: 4,823,088 B; 11 skins, animation preserved.

### Chatur (Rahkasa) — NO model change (close-out)
- Shipped file is the cleanest of the six: rig OK, seams 0, 3/3 materials textured. Moves verified (below). Nothing to fix; do not touch.

### Megami (Parvati) — PR #1528 — landed
- Defect: 30,860,048 B — over the 20 MB jsDelivr CDN limit.
- Owner's "missing clothing textures" flag investigated FIRST: the 33 untextured materials are flat-color by source design (parvati-full.glb wires them identically). A prior lane note claiming 2 normal maps missing from the shipped file was DISPROVEN by sha256 (byte-range fetches from release asset 669070364): NM.1001/NM.1002 are already embedded (image[10]/image[7]) and wired.
- Fix: gltfpack -cc -kn (the PR #1482 route). 30,860,048 B -> 19,511,432 B. Equivalence: triangles 311,325 =; joints 52 =; images 65/65 sha256 sets identical; verts -10 (exact duplicates welded); materials 68 -> 52 (16 exact duplicates merged — disclosed in the PR).

### Menajerii (Vixen) — PR #1531 — landed pending visual gate; palette bake parked with source located
- Defect 1: official audit ERROR. Root cause: mesh4 prim15 in an interleaved bufferView (byteStride 44) flush with BIN end; the audit reader overruns 12-28 B. File is spec-valid but reader-hostile. Fix: repo-codec decode->encode rebuild. A/B: ERROR -> OK.
- Defect 2: seams 598 (first readable audit) -> 113 after unification (1,890 copies, 14 meshes; Parvati's accepted file sits at 75). Size 13,896,480 B -> 3,164,796 B.
- Textures (parked, source LOCATED): shipped file has 0 images and 0 TEXCOORD_0. Siblings checked by direct read: model-rigged.glb also bare; vixen-full.glb (release) 0 images; **model.glb carries 2 images — PaletteBaseColor + PaletteMetallicRoughness (webp), 18 materials** (MPFB palette set). Faithful bake = UV transfer from model.glb + palette assignment. Never borrow another character's maps (Parvati's were explicitly not used).

## Moves / animations state (official plan_coverage_audit.mjs, Node planner)
- tobi 0/360 no-clip · chatur 0/214 no-clip · menajerii 0/208 no-clip (planner finds plans for all steps).
- pond 312/312, ryusan 226/226, megami 324/324 show no-clip IN NODE ONLY because the planner does not load motbin/T7-bank clips in Node (documented tool limitation) — these are NOT real counts. The browser stepped probe is the real verifier; play-verification of the motbin wiring for these three is still owed.
- NO Pantera-rule promotions exist for the six: none of their moveset JSONs carry string_step_plans/candidate_row fields; pond's t7_motbin_clips.playable_wiring is explicitly NONE (title->move join not play-verified; collisions exist). Moves completion for pond/ryusan/megami = play-verification + bank production work, not text edits.
- Menajerii's Roger Jr. bank does not exist in-repo; per the brief it must be pulled from the TTT2 teardown holdings on GRE — NOT done this lane; never substitute another character's bank.

## Tooling notes
- unify_seams.py crashed on Vixen (IndexError: a mesh uses <4 distinct joints); the lane copy carries a zero-pad guard. The repo copy should get the same guard when the drivers are next touched.
- anim_check.py's reader overrun on interleaved bufferViews (Vixen) is a repo tool bug worth fixing upstream; the codec rebuild is the file-side workaround used here.
- audit_parts.py (per-part skinning probe) is added at tools/auto_rig/audit_parts.py by this lane's handoff PR — use it for any multi-skin file before believing a region verdict.
- REJECTED variants (evidence only, never ship): work/mina-ibmfix.glb and work/miruko-ibmfix.glb (IBM patch made seams worse: 21,195 / 36,627) and patch_ibm.py.

## Visual gate — OWED for every landed model PR
No renders were produced this lane: Blender 4.0.2's render path crashes (libEGL.so.1 missing) and a Blender 5.2.3 EEVEE render of Tsuyu was OOM-killed (VM: 8 GB RAM, load avg ~34 from parallel lanes). All model PRs above are marked landed-pending-visual-gate. When the box clears: render front A/B pairs (original plain decode vs final plain decode) for tsuyu, miruko, parvati, vixen, mina from the lane scratch (~/workspace/_smutbase6-fix-20261102/, render_one.py + plain decodes are staged there), view them, and only then call the models finished.

## Execution notes
- The lane ran through the 2026-11-02 disk-write storm (exec writes EPERM/0-byte for ~1 h; it zeroed ~/MEMORY.md at 05:38 CST). The storm cleared mid-run (~12:25 UTC); all PRs were still landed via the Git Data API (the standing preferred path), gitleaks clean on all five model files.
- Merge SHAs for PRs #1528-#1532 are appended by a follow-up amendment once the merges verify on main.

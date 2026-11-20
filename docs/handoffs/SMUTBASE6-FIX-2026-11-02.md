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

## Amendment (2026-11-02, lane close) — merges verified on main
- PR #1528 Megami pack — MERGED, squash sha 11b2ab387d3b4381659f60f64bf6a23b83547169; main blob b79bda9260, 19,511,432 B.
- PR #1529 Tobi fix — MERGED, squash sha 598823872d6599f6d9d7a35459f2742eb7454b05; main blob f46f8c4427, 4,823,088 B.
- PR #1530 Pond fix — MERGED, squash sha f90f161cc0c2d91f05ba219b133f954c8ae2f6d9; main blob 26e8e53aaf, 9,467,192 B.
- PR #1531 Menajerii fix — MERGED, squash sha 6c5a7094e9ccb94ca482e75cdf0eaa80f12fb3a4; main blob e03b212923, 3,164,796 B.
- PR #1532 Ryusan part 1 — MERGED, squash sha 0d0129cd9b963e81c4ecd2dcd2986cf00b0bcbc3; main blob 1a818241cc, 2,259,084 B.
- PR #1533 this handoff — MERGED, squash sha 559acff3bdce693e279e1c13a6567fe9309669e9.
- Chatur: no change; loaded file on main untouched (blob a23c514f68, 2,361,776 B).
- All merges were squash merges after full CI green (incl. instruction-gate, deletion-guard, rig-guard) and gitleaks-clean file sets. Still owed (unchanged): the visual gate renders for the five landed models, Ryusan texture bake part 2, Menajerii palette bake, Menajerii's Roger Jr. bank from the TTT2/GRE holdings, and browser play-verification of pond/ryusan/megami motbin wiring.

## Amendment (2026-11-03, texture-bake lane) — Ryusan part 2 + Menajerii palette bake LANDED; visual gate done
- Visual gate (owed above) was completed 2026-11-03 by the lead: front + 3/4 renders of all five landed models through the game's own three.js stack (proofs in the lane scratch visual-gate/proofs/). Verdicts: Pond PASS, Tobi PASS, Ryusan PARTIAL (zero textures — fixed by PR #1540 below), Menajerii PARTIAL (untextured + black splotches — fixed by PR #1541 below), Megami PARTIAL (flat-gray outfit is a pre-existing source-material trait, A/B-proven, not a pack defect).
- PR #1540 Ryusan texture bake part 2 — MERGED, squash sha 1cc550b567bfe51aa3b3a5d0ddbe190473e7e23a; main blob 470afb0c7e, 5,079,568 B. Method note: the faithful route named in the part-1 handoff (re-export via tools/model-import/rig_smutbase6.py) does not exist in this repo or any other (verified by tree + code search); a literal re-export would also carry the blend's 520-bone Rigify rig, which the game cannot load. Instead the blend's own per-triangle material groups and UVs were transferred geometrically onto the proven part-1 file (body-mesh group counts reproduce the blend EXACTLY: skin.000 36,258 / skin_head 4,460 / eyes 442 / body 104 tris; the sibling model.glb sits in the blend's exact local space with 100% UV agreement, proving the lineage's rerig UVs were never the blend's). 8 images embedded (7 blend maps + hero-outfit metallicRoughness packed from her own Roughness map, B=0 for the blend's metallic 0.0). Not wired, by the blend's own authority: hero-outfit Height (Displacement — no glTF core slot), skin_head bump map (no glTF core slot), and the intake folder's Normal/Metallic/AO maps (the blend does not wire them either). Seams 0 PASS before/after (repo rig_inspect); 73 joints, 73,431 tris preserved. Gate renders: 11/11 materials textured (pink skin/hair, camo hero outfit + boots, tan suit). Pre-existing placement trait, unchanged by the bake: the Fur part binds low in this rig lineage (visible identically in the 2026-10-23 proof render docs/proof/smutbase-6-2026-10-23/mina-ashido-front-v1.png).
- PR #1541 Menajerii palette bake — MERGED, squash sha c8086bf4b440533c9569b05e3e678a6fe415e3ef; main blob 0108a67568, 3,194,880 B. Assignment proven by NAME, not geometry: the loaded file's 69 primitives carry the original DAZ material names; the intake master vixen-full.glb (release megami-menajerii-smutbase-20261023) lists the same names in the same primitive order; model.glb lists the palette slot for the same order — chain verified clean on all 28 meshes (69/69 primitives; Pupils-2 -> PaletteMaterial002, EyeMoisture-2 + Cornea-2 -> PaletteMaterial003, Irises-2 + Sclera-2 -> PaletteMaterial004). All 18 palette materials, both palette webp images and the sampler copied verbatim from model.glb; per-primitive UV = that primitive's own median UV in model.glb (palette is flat per primitive, NEAREST sampler). No geometry touched: original BIN is a byte-identical prefix; 403,383 tris / 28 skins preserved; round-trip decode re-verifies 69/69 prims' material + UV. The palette is near-monochrome by design (skin = white swatch; bodystocking + panties = black). Appearance disclosures are in the PR body (texture liveness proven by a black-swatch control render; the jagged dark shard pattern is a pre-existing shell-breach property of this shipped file, identical in the pre-bake gate render; the palette source renders smooth in EEVEE because its un-decimated shells sit proud). The PR also regenerates game/js/material-status.js: menajerii + menajerii-attire1 (both wired to this file) LEAVE quarantine ('55 untextured' — they now pass the material audit); megami + megami-attire1 remain quarantined (untouched). Menajerii is therefore selectable/fightable again per the material gate's rules.
- Still owed (unchanged, out of this lane's scope): Menajerii's Roger Jr. bank pull from the TTT2/GRE holdings; browser play-verification of pond/ryusan/megami motbin wiring.
## Amendment (2026-11-03, final-three remainders lane) — Roger bank GAP, motbin play-verification DONE, Megami outfit GAP

Method note for all three jobs: play-verification used the repo's own stepped probe semantics
(tools/anim/move_coverage_probe.mjs) ported to the lane's headless-Chrome harness against a
locally served tree of main (identical module graph to the 2026-11-03 deploy build, with the
four current-main GLBs at their canonical paths and game/js/material-status.js refreshed to
main HEAD, blob 17e3eb2d). The game boots into an attract fight (zen vs pantera) before any
?quick= fight, so the probe's ready gate requires g.p1.char.id === <fighter> AND
roundState === 'fight' — an earlier ungated run measured the attract fight's Zen for
menajerii and was retracted (kept in lane scratch as menajerii-verdict-INVALID-attract-zen.json).

### Job 1 — Menajerii's Roger Jr. bank: GAP (not in the holdings in any extractable form)
- In-game today: FIGHTER_BANK binds menajerii: 'kuma' (2026-10-23). Play-verified below: the
  T3 Kuma bank binds (22 actions) and her basics fire matched Kuma rows. Her moveset
  (game/assets/movesets/menajerii.json, 193 moves) references Roger Jr. move DATA via 19
  anim_refs ttt2:rog:row:N into game/assets/ttt2/movesets/rog.json — data, not clips.
- Searched: GRE teardown/tekken-tag-tournament-2/ subtree contains ONLY HEADER-LISTING.txt +
  tools (god_surgical/stfs_blobs/xdvdfs_reader) — no extracted banks; GRE full-tree grep for
  'roger': 0 hits; GRE tekken6/extracted = PSP index files only; tekken5 = name tables +
  catalogs only. Local data001 decode = 669 NTXR textures, 0 MOTA; data028 = audio container,
  0 MOTA. The only MOTA-bearing TTT2 container identified is data004.bin (LZX; decoded copy not
  on disk; reproducible from release ttt2-7z-v1 via in-repo lzx-decode/ttt2-section-decode
  tools); 33 of 42 dataNNN inner files were never pulled (disk-gated). No TTT2 MOTA parser
  exists in WH/GRE tooling and the engine has no TTT2 clip loader (banks are T3-format via
  t3anims.js) — the same blocker class as Jun (everything-else Step 1). Producing her bank =
  the dedicated TTT2 motion lane (pull + decode + MOTA format RE + converter + loader).
  No substitute motion was wired; the 'kuma' stand-in binding is untouched.

### Job 2 — Motbin play-verification (identity-gated, per fighter)
- pond (Raven/T7): bank loads NO — none exists. t3actions 0, mixer actions 0. 13 inputs:
  11 fired with NO clip plan (procedural poses only), 2 NOFIRE (d/f+1,2; f,f+2). Console:
  "[WH-THROW] pond vs pantera: no file pair (no T3 bank for pond (UNMAPPED))". FIGHTER_BANK
  has no pond entry; her moveset's t7_motbin_clips.playable_wiring = "NONE".
- ryusan (Lucky Chloe/T7): bank loads NO — none exists. t3actions 0, mixer actions 0.
  13 inputs: 12 fired with no clip plan, 1 NOFIRE (d+3). No FIGHTER_BANK entry.
- megami (Jun/TTT2): CANNOT BE INSTANCED INTO A FIGHT — she is in material quarantine
  (game/js/material-status.js on main HEAD: megami "20 untextured"), and the loader itself
  refuses quarantined models: game/js/assets.js:1349 assertModelUsable(id) — "quarantined
  (broken materials) never loads into select or a fight" (see also material-runtime.js).
  Three identity-gated quick-fight attempts (900 s each; the last on the main-current tree)
  never requested her model, while pond/ryusan/menajerii loaded and fought in the same
  tree. Bank state by data: no FIGHTER_BANK entry, no TTT2 MOTA parser/loader exists —
  same absence class as pond/ryusan, plus the quarantine gate on top (see Job 3).
- menajerii (control, not a Job 2 target): fight loads, Kuma bank binds — 22 t3actions;
  13 inputs: 10 fired real clips at weight 1 with matched rows (1->row:34, 2->row:108,
  3->row:225, 4->row:230, 1+2->row:101, d/f+1->row:129, d/f+2->row:159, 1+3->row:211,
  1,2->row:108, d,d/f,f+1->row:141), 3 NOFIRE (d+1; u/f+4; b+1+2,1). Proves the harness and
  the bank pipeline; her animation today is the Kuma stand-in, not Roger Jr. (Job 1).
- Proof (this PR): docs/proof/2026-11-03/smutbase6-final-three/ — the four verdict JSONs
  (pond/ryusan/megami/menajerii-verdict.json), menajerii fight stills (headless fight-scene
  rendering blows her near-white palette out to a glowing silhouette; identity is
  state-verified — p1.char.id + her 69 DAZ-named skinned meshes — and her textured
  appearance is proven by the visual-gate renders), and job1-job3-evidence.md (the full
  search/diagnosis record). Harness: lane scratch ~/workspace/_smutbase6-fix-20261102/
  (playprobe.py, diag.py, gatetest.py, fightshot2.py).
- Bottom line: the everything-else Step-1 evidence is confirmed in live play — pond/ryusan/
  megami have NO playable move clips; the fix is the bank-production route named in
  docs/movesets/MOVE-CLIP-COVERAGE-2026-11-02.md (bake real bases via t7_move_resolve.py +
  t7_move_bake.py for the T7 pair; TTT2 lane for Jun), not wiring repair. Nothing was mis-wired.

### Job 3 — Megami's outfit materials: GAP (no outfit textures exist in her own data)
- The brief's transmission/clearcoat suspicion is REFUTED by her material data: those
  extensions exist only on the eye micro-materials (EyeMoisture-3/-4, Cornea-2), in source
  and shipped file alike, and they render correctly.
- The visible outfit is a Marvelous-Designer-style set (24_Material43_0.25_0_0 shell +
  25_Material40_1_0_0 headpiece; isolation renders in lane scratch). In the INTAKE SOURCE
  (parvati-full.glb, release megami-menajerii-smutbase-20261023) those materials are
  literally "pbrMetallicRoughness": {} — no textures, no baseColorFactor — and their COLOR_0
  is placeholder white (1,1,1) on 100% of sampled vertices. All 66 source images inventoried:
  none belongs to the outfit. The shipped file additionally lost the outfit prims' TEXCOORD_0
  + COLOR_0 in the rig rebuild (sibling attires/attire1/model.glb retains both) — immaterial,
  since there is no texture to sample and the colours are white.
- Black splotches = the black Bodystocking-2 under-layer breaching between the outfit shells
  (same shell-breach family as Menajerii's shards) + unlit double-sided fabric undersides.
  Pre-existing in the source; the visual gate's A/B already proved the pre-pack original
  identical. Torso-6 (metallic 0.9/roughness 0.2, no maps) is the RenderStrandHairGeom
  material — hair, not outfit.
- Repo audit (game/js/material-resolve.js auditGltf) on the shipped file: 39 ok / 19
  untextured prims — the 6 outfit prims plus eyes x3, strand hair, bangs, shoe parts x7,
  PANTIES-1, all textureless IN THE SOURCE ITSELF. Her quarantine (Job 2) is therefore not
  curable by any faithful edit: the outfit texture set was never part of the commission
  intake. No textures were invented and no materials were recoloured; nothing was changed.
  If the original outfit textures are ever supplied, the enabling step is restoring the
  outfit prims' TEXCOORD_0/COLOR_0 from attires/attire1/model.glb (retains both) — recorded
  here so a future lane can do it in one step.

# SmutBase 6 — Fidelity Gap Report (2026-11-04)

Owner order (2026-11-04 ~18:01 CST): the six must look EXACTLY like their source .blend
files opened in Blender — perfect — with the FULL rigs that come with their own files,
all textures and everything else from those files. The 2026-10-23 48-bone MPFB-template
conversion is NOT the standard.

Method: every source located and hashed; shipped GLBs parsed from their JSON chunks;
source blends opened in Blender 5.2.3 (restored from tools-archive-2026-10-31) for the
authoritative inventory + reference renders. Ground truth = the clean source file,
never the shipped conversion.

## Source location summary

| Fighter | WH char | Source .blend | Where | Size | sha256 |
|---|---|---|---|---|---|
| Pond | Tsuyu Asui (Raven) | `Tsuyu Asui IK.blend` | WH repo `roster/tsuyu-asui/intake/Tsuyu Asui IK/` | 14,248,117 | 034d0972… |
| Ryusan | Mina Ashido (Lucky Chloe) | `Mina Ashido rigify.blend` | WH repo `roster/mina-ashido/intake/Mina Ashido rigify/` + local lane copy (byte-identical, same git blob) | 7,396,031 | 75f96a45… |
| Tobi | Mirko (Hwoarang) | `mirkoIK.blend` | WH repo `roster/miruko/intake/miruko IK/` | 6,310,244 | 7aba517f… |
| Chatur | Rahkasa (True Ogre) | `RahkasaV1.1.blend` | WH repo `roster/rahkasa/intake/` | 11,459,182 | 85610cee… |
| Megami | Parvati (Jun Kazama) | `Parvati(Commission).blend` | **NOT IN HOLDINGS** — was staged at `~/workspace/fix2/smutbase-source/parvati/` (596 MB, Blender 4.02, GZM rig, 90 objects); folder gone, original `ParvatiCommission.rar` (sha256 2601d935…) also gone. Best surviving source: `parvati-full.glb` (191,604,148 B, release `megami-menajerii-smutbase-20261023`) — a RIGLESS static export. | — | — |
| Menajerii | Vixen (Roger Jr.) | `Vixen (Commission).blend` | **NOT IN HOLDINGS** — was staged at `~/workspace/fix2/smutbase-source/vixen/` (985 MB, Blender 4.02, GZM rig + body morphs, 88 objects); folder gone, original `Vixen_Commission.rar` (sha256 e6d2754b…) also gone. Best surviving source: `vixen-full.glb` (629,742,368 B, same release) — RIGLESS, TEXTURELESS static export; only texture data in holdings = sibling `model.glb` 2-image palette. | — | — |

All four in-repo blends are **Blender 5.0, zstd-compressed** (decompressed header
`BLENDER17-01`); Blender 4.0.2 cannot read them ("not a blend file") — Blender 5.2.3
is required, matching the fix lane's earlier Mina read.

## Blender 5.2.3 inventory of the four in-repo blends (authoritative)

Blender 5.2.3 LTS restored (official tarball, 385,331,224 B, size-verified; the
tools-archive chunk route is the canonical restore path and holds the same build).
All four blends opened clean. Full dumps: `blend-inv-*.json` beside this report's
lane copies; reference renders under `docs/proof/2026-11-04/smutbase6-fidelity/`
(EEVEE front + 3/4 from the blends as opened, hide flags respected).

| Fighter | Armature(s) | Bones | Meshes (real) | Shape keys | Materials | Packed images |
|---|---|---:|---|---:|---|---:|
| Pond | `tsuyu rig` | **224** | 19 (body 20,911v/67 keys, suit, boots 3,084v, gloves 4,070v, belt/goggles/mask, Hair) | **82** | 11 | 12 (suit/boots 2048² sets, eyes, hair, outfit, skin_face…) |
| Ryusan | `Mina Ashido` (+ `backup-metarig` 65) | **520** | Mina 20,719v/63 keys, suit, jacket, boots, Fur, Hair, Horns, Penis | **71** | 7 | 10 (body/outfit 2048² sets, FaceS, skin_head…) |
| Tobi | `Miruko Rig` | **254** | Mirko 21,706v/55 keys, Hair 38 keys, tail 31 keys, Ears, Gloves, Suit, tights, foot wear, belt | **129** | 10 | 12 (Body/Eyes/Eyeshadow/Face/Hair maps + suit/belt PBR sets) |
| Chatur | `RahkasaRIG` 983 + `RahkasaRIG_Deform` | **983 / 133** | RahkasaBody 29,489v/**99 keys**, RahkasaHair 10,185v (+ scene Floor/godrays) | **98** | 6 | 9 (Body/Head base+emission, Eyes, Hair base+normal…) |

Bone deltas vs shipped: **Pond 224 → 52 (−172) · Ryusan 520 → 73 (−447) ·
Tobi 254 → 73 (−181) · Chatur 133 deform (983 full) → 52 (−81 / −931).**
Shape keys shipped: **0 for all four** (blend counts 82 / 71 / 129 / 98).

Settled by the dumps:
- **Pond: Bulge AND Penis are `hide_viewport` + `hide_render` in the blend itself** —
  #1552's removal matches the author's own flags; the as-opened render (proof set)
  shows the clean suited figure with boots + gloves the shipped file lacks.
- **Tobi: "Eyes/Eyeshadow/Hair flat by source design" is REFUTED** — the blend packs
  real Eyes (1024×512), Eyeshadow (512²), Hair (1024²), Face and Body maps. The shipped
  flatness is a conversion loss. Bulge + Penis are author-hidden here too.
- **Chatur: FOUR ARMS CONFIRMED** — the deform rig carries two full arm chains per
  side (`DEF-upper_arm.L` + `.001`, `.002/.003` in the full rig) and the as-opened
  render shows the second arm pair at the waist. The shipped GLB has ONE chain per
  side: the conversion amputated two arms. Her blend pose is an authored flex pose,
  and the file carries its own scene (Floor, godrays).
- **Ryusan: Penis author-hidden (VP+R); Fur is `hide_render` only** (visible in
  viewport, absent in renders — the shipped "Fur binds low" quirk sits in this area).

GLB reference renders (Workbench, texture mode) were also produced for the two
blend-less characters from their best surviving sources: Parvati from
`parvati-full.glb` (front/3-4/face — dark skin and face textured, silver hair, the
full tactical outfit geometry rendering flat gray exactly as the source materials
dictate) and Vixen from the un-decimated sibling `model.glb` (front/3-4/face —
smooth shells, no shard breaches). NOTE: the local `models/src/vixen-full.glb`
(100,078,094 B) is TRUNCATED — Blender rejects it ("Bad GLB: file size doesn't
match"); the intact master is the 629,742,368 B release asset, not yet pulled down.

## Per-character gaps (GLB-level, verified by parse)

### Pond = Tsuyu Asui
- Blend (5.2.3 dump): 22 objects / 19 meshes — body `tsuyu` (20,911v, 67 shape keys),
  SEPARATE suit (12,403v, 10 keys) / boots (3,084v, 3,096 polys) / gloves (4,070v)
  objects, belt/goggles/mask, Hair, Bulge, Penis, face/mouth templates, `tsuyu rig`
  armature = **224 bones**, 82 shape keys total, 11 materials, 12 packed images.
  Frog hat is NOT in the source.
- Shipped (current main, #1552): 8,235,624 B, 7 meshes, 240,415 verts, 52 joints, 8 images.
- Gaps: **bone delta −172 (224 → 52)**; **82 shape keys → 0 morphs**; boots object in
  NO shipped file (barefoot); gloves object lost at the original conversion; #1552
  removed the two meshes the blend itself flags hidden (Bulge 4,144v + Penis 5,120v
  objects; their GLB incarnations carried split-vert counts) — removal CONFIRMED
  faithful by the blend's own hide flags.

### Ryusan = Mina Ashido
- Blend: **520-bone Rigify rig** (+ metarig), separate boots/jacket/suit objects, Fur,
  Horns, Hair, Penis; 6–8 materials; **10 packed images**; **31+ driver-referenced
  shape keys** (brows/eyes/mouth/NipplesFlat).
- Shipped (#1540): 5,079,568 B, 73 joints × 8 skins, 8 meshes/11 prims, 218,546 verts,
  7 materials, 8 images.
- Gaps: **bone delta −447** (520 → 73, CONFIRMED by the 5.2.3 dump, +65-bone
  backup-metarig also in file); **all 71 shape keys lost** (0 morphs shipped;
  Mina body alone carries 63);
  images 10 → 8 (Height + skin_head map not embedded); clothing separability lost
  (objects folded into multi-prim meshes); material groups collapsed to 2 in the whole
  pre-#1540 lineage (#1540 rebuilt 7 from the blend's own per-triangle groups).

### Tobi = Mirko
- Blend (5.2.3 dump): `Miruko Rig` = **254 bones**; Mirko body 21,706v / 55 shape keys,
  Hair 38 keys, tail 31 keys, Penis 8 keys (author-hidden, as is Bulge); separate Ears,
  Gloves, Suit, tights, foot wear, belt, neck fluff; 129 shape keys total; 10 materials;
  12 packed images INCLUDING Eyes/Eyeshadow/Hair/Face maps.
- Shipped (#1529): 4,823,088 B, 11 meshes/17 prims, 266,980 verts, 11 skins × 73 joints,
  11 materials (8 images after #1529), seams 37,445 → 0, CMU boxing clip.
- Gaps: **bone delta −181 (254 → 73)**; **129 shape keys → 0 morphs**; Eyes/Eyeshadow/
  Hair ship flat DESPITE real maps packed in the blend ("flat by source design"
  closure REFUTED by the dump); separate objects (Ears/tail/Gloves/tights) collapsed
  into SFM-named prims; `Mirko body unshaded.png` unused; no normal maps in GLB
  (blend suit/belt sets are Base/Metallic/Roughness only).

### Chatur = Rahkasa
- Blend (5.2.3 dump): `RahkasaRIG` = **983 bones** + `RahkasaRIG_Deform` = **133 bones**;
  RahkasaBody 29,489v / **99 shape keys**, RahkasaHair 10,185v; 98 shape keys total;
  6 materials; 9 packed images (Body/Head base+emission, Eyes, Hair base+normal,
  Nipples set). Sole intake file, all maps packed inside.
- Shipped: 2,361,776 B, byte-identical orig = shipped (no fix PR ever touched it),
  1 mesh / 4 prims, 176,555 verts, **52-joint `WH_Skeleton` template**, 3 materials,
  5 images, 0 anims, 0 morphs. GLB-level audit is genuinely clean (seams 0, 3/3
  textured, face Head 98%) — VERIFIED at GLB level, and now shown to be beside the
  point: the file is clean AND unfaithful.
- Gaps: **bone delta −81 vs the deform rig, −931 vs the full rig**; **98 shape keys
  → 0 morphs**; **FOUR ARMS → TWO**: the deform rig carries two arm chains per side
  and the as-opened render shows the waist-level second pair — the shipped file has
  one chain per side; single collapsed mesh vs the blend's body+hair structure;
  Hair Normal + Nipples maps and the emission sets reduced (5 images vs 9 packed);
  authored flex pose + scene (Floor/godrays) exist only in the blend.

### Megami = Parvati
- Source GLB (best surviving): 25 meshes / 71 prims, **1,154,840 tris / 718,178 verts**,
  69 materials, 66 images, **0 skins / 0 joints / 0 animations** (static DAZ export).
- Shipped (#1528 pack): 19,511,432 B, 311,325 tris, 52 materials, 65 images, 52-joint
  template rig. No-outfit variant (#1549): 297,167 tris.
- Gaps: **geometry −73.0% tris**; the source carries NO rig — the "full rig from her own
  file" exists only in the missing commission blend (GZM rig); 7 outfit materials are
  literally empty `pbrMetallicRoughness {}` in the source (meshes 3,4,5,6,7,22 —
  0/66 images belong to them; SOURCE TRAIT, never invent textures); 8 hair-strand
  materials have no texture/color anywhere (silver-white flat = faithful ceiling);
  hair prims collapsed 9 → 2; TEXCOORD_0 dropped on ~half the shipped prims by the pack;
  PLUS the live defect found 2026-11-04: Megami renders TINY/crumpled under her Jun
  bank (fix lane already launched separately — bank skeleton scale vs her rig).

### Menajerii = Vixen
- Source GLB (best surviving): 29 meshes / 72 prims, **986,895 tris / 532,326 verts**,
  69 DAZ materials, **0 images / 0 textures**, 0 skins. Sibling `model.glb`:
  854,295 tris, 18 palette materials, 2 palette images (612 B total).
- Shipped (#1541): 3,194,880 B, 403,383 tris, 28 skins × 52 joints, 18 palette materials.
- Gaps: **geometry −59.1% tris** (the decimation causes the jagged shell-breach shards —
  absent in the un-decimated sibling); source's real per-vertex UVs stripped in the
  conversion, palette bake restored only a constant UV point per prim; NO DAZ textures
  exist in holdings — photoreal fidelity is IMPOSSIBLE from current holdings; the
  palette is the ceiling unless the commission blend / DAZ texture folders are
  recovered; rig + body morphs exist only in the missing commission blend.

## Rebuild plan (per character, JOB-SEQUENCE: simplest first)

Order rationale: start where the blend is in hand AND the shipped gap is smallest,
prove the faithful-export pipeline end to end on one character, then scale.

1. **Tobi (Mirko)** — blend in repo, shipped geometry already 1:1 with the conversion
   (266,980 verts, seams fixed, textures completed). Job: faithful re-export from
   `mirkoIK.blend` keeping the blend rig, verify Eyes/Hair against the blend, retarget
   Hwoarang bank onto the blend rig. Smallest delta, proves the pipeline.
2. **Pond (Tsuyu)** — blend in repo. Job: faithful export restoring boots + gloves
   objects (both verified present in the blend), hidden meshes stay hidden per the
   blend's own flags (dump-confirmed), 82 shape keys → morph targets, retarget the
   Raven T7 bank (20 actions) onto the 224-bone blend rig's deform set.
3. **Chatur (Rahkasa)** — blend in repo, shipped file untouched/clean at GLB level
   but structurally unfaithful: **restore the second arm pair** (deform rig has both
   chains), 98 shape keys → morphs, full 9-image set incl. Hair Normal. True Ogre
   has no TTT2 moveset file (Ancient Ogre only) — bank stays pose-only per current
   state.
4. **Ryusan (Mina)** — blend in repo (local byte-identical copy too). Job: the big rig
   case — 520-bone Rigify → game-usable full rig (keep the FULL source rig in the
   fidelity master; derive the engine skeleton from it without dropping the source),
   restore all 31+ shape keys as morph targets, embed all 10 images, retarget Lucky
   Chloe bank.
5. **Megami (Parvati)** — BLOCKED on source recovery: re-download
   `ParvatiCommission.rar` from SmutBase (browser lane; scripted downloads are
   Anubis-blocked) or locate the 596 MB blend in TeraBox/backup stores. Until then the
   191 MB full GLB is the geometry/material/texture target (un-decimate back to
   1,154,840 tris) and the Jun-bank tiny/crumpled fix proceeds on the current rig.
6. **Menajerii (Vixen)** — BLOCKED on source recovery, same route
   (`Vixen_Commission.rar`, 985 MB blend). Interim: rebuild from the un-decimated
   sibling (854,295 tris, smooth shells) + full GLB UVs/materials instead of the
   decimated shipped file; Roger bank (15 clips) retargets after the rig question is
   settled by the recovered blend.

Size management for all rebuilds: the established pack route (gltfpack/KTX2-class
compression as in #1482/#1528) applied AFTER the faithful export, with image sha256
sets verified identical pre/post pack — compression must never drop textures,
materials, morphs, or meshes.

## Recovery actions opened by this report
- [ ] Locate or re-download the two commission .rar originals (hashes recorded above).
- [ ] Store the four in-repo blends + this report's renders per the storing laws
      (they are already safe in the repo; local scratch copies are cache only).

---

## TOBI REBUILD — LANDED (2026-11-05, this PR)

Rebuilt from her own blend (`roster/miruko/intake/miruko IK/mirkoIK.blend`,
sha256 7aba517fdb7f2b1cb3b09fc9fe5d36eb0e3a1a877c79db2ced5154a375a27269) in
Blender 5.2.3. The 48-bone-template conversion is retired for her.

**Files**
- Game model (replaces the shipped conversion at the path the game loads):
  `roster/miruko/attires/attire1/model-rerig-textured.glb` — 2,495,616 B
  (was 4,823,088 B), 255 joints (her full 254-bone rig + the exporter's
  standard neutral_bone), 11 embedded images, morph targets on every mesh
  that has them in the blend: body 54, Hair 37, tail 30, Gloves 1.
- Canonical master (original Blender bone names, every object incl. the
  author-hidden Bulge/Penis, tail unskinned exactly as authored):
  `roster/miruko/attires/attire1/model-blend-master.glb` — 2,874,744 B,
  255 joints, 12 images, 345 morph targets.
- Blend totals preserved: 254 bones / 129 shape keys across the kept meshes
  (122 in the game file; the 7 Penis keys live only in the master with the
  author-hidden mesh) / all 12 packed images + the intake
  `textures/Mirko body.png` wired in (the blend's one unpacked reference).

**Method notes (reusable for Pond/Chatur/Ryusan)**
- The body mesh's 3 MASK modifiers are baked through the depsgraph per shape
  key (armature modifier kept ACTIVE — this DMX mesh's bind is not identity;
  muting displaces the surface ~5 cm). The authored key mix (suit-fit /
  tights-fit at 1.0) is folded into the basis; after `shape_key_add`, every
  key block's value must be reset to the authored value or all morphs apply
  at once and the surface bulges (caught by eye on the pelvis proof, fixed,
  re-proven: evaluated front surface matches the blend to 4 decimal places).
- Scale: blend is authored 9.388 units tall; uniform 0.189475 applied to
  reach the shipped model's 1.7755 m. Inverse bind matrices scale by
  translation only (uniform S: IBM' = S·IBM·S⁻¹).
- Pack: repo codec (meshopt + quantization); embedded image sha256 sets
  verified identical pre/post pack; the material gate audit
  (game/js/material-resolve.js auditGltf) passes 14/14 primitives ok.

**Proof (this PR)**
- Renders from the shipped file: `docs/proof/2026-11-04/smutbase6-fidelity/tobi-fidelity-front-20261104.png`, `docs/proof/2026-11-04/smutbase6-fidelity/tobi-fidelity-q34-20261104.png`, `docs/proof/2026-11-04/smutbase6-fidelity/tobi-fidelity-face-20261104.png`, pelvis pair `docs/proof/2026-11-04/smutbase6-fidelity/tobi-pelvis-blend-20261104.png` + `docs/proof/2026-11-04/smutbase6-fidelity/tobi-pelvis-glb-20261104.png`.
- Fight proof video: `docs/proof/2026-11-04/smutbase6-fidelity/tobi-fight-probe-20261104.mp4` (stepped-capture from the game's own harness; frames eye-checked: stance scale vs Pantera correct, strike poses real; the throw phase rides the game's low throw camera — the driver log records throwSeen + 15 dmg for the grapple).
- Roster probe (game harness, BASICS): all 10 press true; strikes deal the
  roster-pass baseline damage (1: 2.4, 2: 4–4.8, 3: 4–4.8, 4: 6.3, d/f+1: 4.8,
  d+1: 2.4, d/f+2: 13.5–17.5 across runs); 1+3 throw connects for 15 (proven
  at the baseline spacing in a distance sweep: connects at 0.7 / 1.15 / 1.8).
  Play-probe: all 10 inputs OK, mixer weight 1.0, bind-pose fraction 0.17,
  22 T3 actions built on the new rig (rows 91–294, own + donor).

**Deviations (all game-file only; the master is the blend exactly)**
1. 22 core bones renamed to the engine's canonical names (hips→Hips,
   upper_arm.L→LeftArm, …). The runtime retargeter (t3anims.js
   analyzeRig/canonBoneName) matches NO Blender-style name, so without this
   the model gets no animation at all. Alternative (extend canonBoneName for
   Blender-style names engine-side) noted as a follow-up; not done here
   because an engine change risks all 59 fighters.
2. Tail repair: the blend's tail ARMATURE modifier has object=None (source
   defect — the tail could never deform as authored). Game file assigns the
   rig and renames the orphan SFM vertex group to Hips.
3. Author-hidden Bulge/Penis + 0-poly rig helpers excluded from the game
   file (Pond #1552 precedent — the author hid them in the blend itself);
   all present in the master.
4. Neck fluff: the blend gives it NO material (renders plain white). Game
   file gives it an authored flat warm-white (0.90, 0.88, 0.84) so the
   material gate passes and the collar reads as the blend's white fluff.
   (The old conversion put it on the Body texture → skin-toned collar.)
5. Authored fit-key mix folded into the basis (see method notes).
6. Hero-suit Metallic/Roughness merged into one MR image by the glTF
   exporter (standard glTF behaviour).

**Track 1 (Megami/Menajerii source recovery) — status**
- Disk search (full workspace, trash, staging dirs): NEITHER rar/blend found.
- GitHub releases + trees (western-heart, game-reverse-engineering,
  cape-jones, agent-ops; 158 releases / 3,892 assets): NOT FOUND. Only the
  two known GLBs exist.
- Interim masters pulled from release `megami-menajerii-smutbase-20261023`
  and hash-verified against the release digests:
  parvati-full.glb 191,604,148 B sha256 0165575b…d232 (25 meshes,
  1,154,840 tris, 66 images, rigless) and vixen-full.glb 629,742,368 B
  sha256 7b4df9fb…eafa (29 meshes, 986,895 tris, palette materials — INTACT,
  supersedes the truncated local copy). Local cache:
  ~/workspace/_smutbase6-fidelity-20261104/recovered-masters/.
- Still open: TeraBox check (browser lane) and, if empty there, the
  SmutBase re-download (browser lane; scripted downloads are Anubis-blocked).

## POND REBUILD — LANDED (2026-11-05, PR #1571)

Rebuilt from her own blend (`roster/tsuyu-asui/intake/Tsuyu Asui
IK/Tsuyu Asui IK.blend`, sha256 034d0972eafd…) in Blender 5.2.3. The
52-joint MPFB-template conversion (#1552) is retired for her.

**Files**

- Game model (replaces the shipped conversion at the path the game
  loads — `game/js/assets.js` `pond:`): `roster/tsuyu-asui/attires/
  attire1/model-rigged-textured.glb` — 7,726,484 B packed (was
  8,235,624 B), 224 joints (her full 224-bone rig), 10 embedded
  images, morphs on the meshes that have them: body 66, suit 9.
- Canonical master (original Blender bone names, every
  polygon-bearing object incl. the author-hidden Bulge/Penis):
  `roster/tsuyu-asui/attires/attire1/model-blend-master.glb` —
  8,098,424 B packed, 224 joints, 11 images, 82 morphs total
  (66 body + 9 suit + 7 Penis).
- Blend totals preserved: 224 bones / 82 shape keys / 12 packed
  images (11 in the master; 10 in the game file — the penis image
  leaves with its dropped mesh, and `phong_exp` is referenced by no
  mesh, only by the unused outfit_toon material).
- BOOTS + GLOVES RESTORED: the boots mesh (3,084 verts, tsuyu-boots
  materials) and gloves mesh (4,070 verts) that the original
  conversion dropped entirely are back in both files — she rendered
  barefoot with sleeve-cuff hands before; now she doesn't.

**Method notes (deltas from the Tobi recipe)**

- TWO masked meshes: `tsuyu` carries 3 MASKs (vg `suit hide`,
  `Bootshide`, `expose vagina`) and `suit` carries 2 MASKs
  (`boots hide`, `expose vagina`) — both baked through the depsgraph
  per shape key with the armature ACTIVE, same method as Tobi.
- NO authored fit mix: every shape-key value in this blend is 0
  (dump-verified), so no fold was needed; the value-reset step still
  applied after `shape_key_add`.
- FLOOR LIFT: the blend's floor is NOT the armature origin — her
  boot soles evaluate at z = −0.1869 (the footTip helper bones
  corroborate). The armature object is lifted +0.1869 before
  evaluation/export so the exported soles sit at y = 0, the shipped
  model's footprint. Uniform scale 0.404717 to the shipped model's
  1.80 m total height (blend character 4.4476 → 1.80).
- POSE: the blend's `pose_position` is POSE but every pose bone is
  at rest (0 nonzero pose bones, dump-verified) — exporting at REST
  is the authored bind either way.
- Pack = repo codec (meshopt + quantization). Embedded-image sha256
  sets verified identical pre/post pack (10/10 game, 11/11 master).
  Material-gate audit (`auditGltf`): game file 10/10 prims ok, no
  repairs. The master's one sub-ok prim is `Plane.002` (the
  mouth_template object) which has NO material in the blend itself —
  source trait, archival file only, not gated.

**Proof (this PR, docs/proof/2026-11-04/smutbase6-fidelity/)**

- Renders from the packed game file (decoded; geometry/images
  byte-identical to the packed file): `pond-fidelity-front-20261105.png`,
  `pond-fidelity-q34-20261105.png`, `pond-fidelity-face-20261105.png`.
- Pelvis/suit-coverage pair (EEVEE, same bbox-relative framing):
  `pond-pelvis-blend-20261105.png` vs `pond-pelvis-glb-20261105.png`
  — baked MASK regions and suit coverage match the blend. (The
  Workbench TEXTURE view of the blend shows the suit's roughness
  map, not its base color — the pair is EEVEE for that reason.)
- Fight proof: `pond-fight-probe-20261105.mp4` + driver log
  `pond-fight-probe-20261105.json` — live game, Pond (P1) vs
  Pantera (P2) with the game's own AI driving the opponent (not
  stubbed); frames eye-checked: Pond at correct scale vs Pantera (slightly shorter, grounded), animated in stance and attacks with hit sparks, throw seen in the grapple phase (driver log: attack:1 dmg 4.8, d/f+2 dmg 0.8, grapple throwSeen true). The capture assembles the screencast's 22 real frames at a fixed 0.4 s each (8.8 s) — the headless harness emits frames sparsely, same as the Tobi capture.
- Probes: roster BASICS all 10 press true at shipped-model baseline
  damage parity (1: 2.5 · 2: 4.2 · 3: 5 · 4: 7.5 vs baseline 6.7,
  run variance · 1+2: 21.2 · d/f+2: 14.7 · u/f+4: 5.3); 1+3 throw
  connects for 15.8 (baseline 15.8). Play-probe: all 11 fired
  inputs OK, mixer weight 1.0, bind-pose fraction 0.08–0.17, her
  20 T7 Raven actions built on the new rig with the same plans as
  baseline. d+1 plans the generic light fallback exactly as on the
  shipped model (pre-existing moveset-data state, not a model
  regression); the string extras d/f+1,2 and f,f+2 don't fire under
  single-press harness input on either model.

**Deviations (all game-file only; the master is the blend as authored)**

1. 22 core bones renamed to the engine's canonical names — same
   reason as Tobi deviation 1 (`canonBoneName` matches no
   Blender-style names): `spine`→Hips (this rig's `spine` IS the
   pelvis bone — thighs/pelvis hang off it), `spine.001`→Spine,
   `spine.002`→Spine1, `spine.003`→Chest, `spine.004`→Neck,
   `spine.005`→Head, `shoulder/upper_arm/forearm/hand`→
   Left/RightShoulder/Arm/ForeArm/Hand, `thigh/shin/foot/toe`→
   Left/RightUpLeg/Leg/Foot/ToeBase. The short in-chain helpers
   `Elbow.L/R` + `Knee.L/R` and every twist/breast/pelvis/facial
   bone keep their names and ride at rest local rotation — the
   pattern `game/js/assets.js` documents for other fighters.
2. Author-hidden Bulge/Penis + non-character helper objects
   dropped (`directional`, `switch`, `up/down`, `face_template`,
   `mouth_template`, `WGT-*` widgets). Bulge/Penis are
   hide_viewport + hide_render IN THE BLEND (owner-approved Pond
   precedent, #1552); the helpers are wireframe-only gizmos with
   0 polygons — glTF cannot represent them, they export as bare
   nodes even in the master.
3. Floor lift +0.1869 (see method notes) — a placement correction
   to the shipped model's footprint; proportions untouched
   (uniform scale only).

**Next in the owner's order after Pond: Chatur** (Rahkasa; 983-bone
full rig / 133 deform in the blend, four arms — see the gap report).

## CHATUR REBUILD — LANDED (2026-11-05, PR #1572)

Rebuilt from her own blend (`roster/rahkasa/intake/RahkasaV1.1.blend`,
11,459,182 B, sha256 85610cee5dafc070bd9d05bc75b7ca33d3f96dc8987693b4d5a5cb232c97c7e3)
in Blender 5.2.3. The 52-joint template conversion is retired for her.
**The second arm pair is restored** — she is four-armed again, as the
blend authors her.

**Files**

- Game model (replaces the shipped conversion at the path the game
  loads — `game/js/assets.js` `chatur:`): `roster/rahkasa/attires/
  attire1/model-rigged-textured.glb` — 4,787,016 B packed (was
  2,361,776 B), ONE skin of **264 joints** (the RIG's full 263-bone
  deform set + armature root) shared by body and hair, **98 morph
  targets on all 3 body prims**, 7 embedded images.
- Canonical master (original Blender bone names, every
  polygon-bearing object incl. the NSFW spare-parts sheet, Floor and
  the godrays prop): `roster/rahkasa/attires/attire1/model-blend-master.glb`
  — 5,010,320 B packed, **984 joints** (the full 983-bone RahkasaRIG
  + root), 98 morph targets, 7 images.
- Blend totals preserved: 983 bones / 263 deform / 98 shape keys /
  9 packed images (7 export — see deviation 4).

**The rig, as the blend actually works (measured, supersedes the
gap report's framing)**

- The blend carries TWO armatures. `RahkasaRIG` (983 bones, 263
  deform) is the skinning rig — both meshes' ARMATURE modifiers point
  at it. `RahkasaRIG_Deform` (133 bones, all deform) is a SEPARATE
  single-armed skeleton whose arm bones sit at averaged positions
  between the RIG's two chains; NO mesh references it as a modifier
  target. The gap report's "133 deform" figure describes that helper
  skeleton, not the skin. The game skin therefore carries the full
  263-bone deform set of the real rig — no runtime subset was forced;
  both arm chains fit the engine as-is.
- FOUR ARMS are in the RIG's deform set, two full chains per side:
  shoulder chain DEF-upper_arm→.001 (segment)→DEF-forearm→.001→
  DEF-hand (head z≈1.175 in armature space) with DEF-palm.01–04 +
  finger sets, and the waist chain DEF-upper_arm.002→.003→
  DEF-forearm.002→.003→DEF-hand.001 (z≈0.922) with .001-suffixed
  palm/finger sets. All of it is in the game file (waist chains keep
  their source names — deviation 2).
- TRAP FOUND AND FIXED: the body object is object-parented to
  RahkasaRIG_Deform in the blend, and the Blender glTF exporter skins
  an object to its PARENT armature — a naive export puts the body on
  the 133-bone single-armed skeleton and amputates the waist arms and
  every face weight. The export reparents the body to RahkasaRIG with
  keep_transform first (measured world delta 0.0 — both armatures
  share the same object transform).

**Method notes (deltas from the Tobi/Pond recipe)**

- AUTHORED SHAPE-KEY MIX FOLDED: the body carries 13 nonzero keys as
  authored (HipsThiccness 1.0, AnklesThiccness 1.0, ArmsThiccness
  1.0, ForearmsDefined 1.0, BreastsLarge 2.5, BreastsRounded 1.0,
  BreastsPaizuri 0.4797, BreastsBalloons 0.4959, BreastsApart 1.0,
  'No Nipples' 1.0, BellyDefine 1.0, BellyChubby 0.4797,
  AssThiccness 1.0). The exporter writes glTF mesh.weights ALL ZERO
  (measured on the test export), so the mix is folded into the basis
  via a depsgraph bake with the armature ACTIVE (Tobi method) — the
  exported model renders as the blend opens, and all 98 keys remain
  as morph targets. No MASK modifiers exist on either character mesh,
  so no mask bake was needed.
- REST export: RahkasaRIG carries an authored flex pose (61 nonzero
  pose bones). Both files export at REST (Tobi/Pond precedent — the
  pose lives in the blend; the bind is the export). Declared, not
  silent.
- SCALE: uniform ×0.214655 to a 2.0 m total height (blend character
  9.3172 → 2.0), matching the shipped model's 2.0 m bind height.
  Imported packed-file bounds measured: height exactly 2.0, soles at
  y≈0 (the blend's soles evaluate 0.0303 below the armature origin;
  the game's GROUNDING block in assets.js grounds by bind-pose min.y,
  so floor placement is unchanged from the shipped file).
- Pack = repo codec (meshopt + quantization). Embedded-image sha256
  sets verified identical pre/post pack (7/7, both files). Material
  gate audit (`auditGltf`, the game's own) on the packed game file:
  **4/4 prims ok, 0 missing / 0 placeholder / 0 untextured** — she
  passes the gate that quarantined fighters before.

**Proof (this PR, docs/proof/2026-11-04/smutbase6-fidelity/)**

- Renders from the packed game file, eye-checked for scale AND pose:
  `chatur-fidelity-front-20261105.png`, `chatur-fidelity-q34-20261105.png`,
  `chatur-fidelity-face-20261105.png`. ALL FOUR ARMS are visible in
  the front and 3/4 views (shoulder pair spread, waist pair below
  them, full finger sets on all four hands); the folded authored mix
  reads in the proportions; face close-up shows the packed eye/hair
  maps and her authored grin.
- In-game (repo serve harness, `?quick=chatur,pantera,shrine`):
  roundState reached **fight** with both models loaded; a live
  instance bone probe measured 264 bones with all 14 of the engine's
  required canonical bones present by name. The engine declined to
  bind the 'ogre' T3 bank — correct and required: that bank is
  Ancient Ogre's, TRUE OGRE HAS NO TTT2 MOVESET FILE, and Chatur is
  pose-only by owner decision; no bank was fabricated or borrowed.
  Her t3actions count is 0, the same pose-only state as the shipped
  file (roster pass: pose-only, 0/214 no-clip).
- In-game still: `chatur-ingame-pose-20261105.png` (follow-up PR
  #1573 — the screenshot call timed out twice under SwiftShader,
  then succeeded on the third attempt with a longer timeout). It
  shows her in the arena vs an animated, stance-posed Pantera at
  correct scale (she reads taller on screen, 2.0 m vs his height at
  similar depth). CAVEAT, stated plainly: under this serve harness
  she renders blown-out white (her packed Body/Head emission maps
  under the harness's stage lighting), while the same packed file
  renders her authored dark skin correctly in Blender — a
  harness/engine rendering state to re-check on the current build,
  not a defect measured in the file. The fight state itself was
  verified by state probe on every run.

**Deviations**

1. 22 core bones renamed to the engine's canonical names in the game
   file (DEF-spine→Hips, DEF-spine.001→Spine, .002→Spine1,
   .003→Chest, DEF-neck→Neck, DEF-head→Head, DEF-shoulder/upper_arm/
   forearm/hand→Left/RightShoulder/Arm/ForeArm/Hand, DEF-thigh/shin/
   foot/toe→Left/RightUpLeg/Leg/Foot/ToeBase) — the runtime
   retargeter matches no Blender-style names (Tobi #1570 / Pond #1571
   precedent). Master keeps the original names.
2. The waist arm pair keeps its source names (DEF-upper_arm.L.002
   etc.) in the game file: the engine has no canonical names for a
   second arm pair, and inventing names would be fabrication. The
   pair rides at rest, fully skinned, exactly as authored.
3. Game file drops: Floor + godrays (scene set), NSFWNipples (an
   unskinned, material-less spare-parts sheet floating beside her at
   x 2.71..3.87 — not worn geometry), RahkasaRIG_Deform (the
   non-skinning helper skeleton), and the 206 zero-polygon WGT-*
   widget gizmos. ALL of it is preserved in the master (widgets as
   bare nodes before pack; see 5).
4. 7 of 9 packed images export, in BOTH files: Rahkasa_Body_Nipples_
   BaseColor + _Emission feed the B inputs of Mix nodes inside the
   Rahkasa_Body material (node-audited) — a custom overlay blend with
   no glTF PBR slot, so Blender's exporter omits them. Doubly moot
   for the authored look: the 'No Nipples' key is authored at 1.0 and
   folded into the basis. The two maps remain packed in the blend,
   which stays in the repo at roster/rahkasa/intake/.
5. Master pack (repo codec prune): the unreferenced RahkasaRIG_Deform
   SKIN object and the 206 zero-geometry WGT widget nodes were pruned
   by the codec (the Deform armature's object node survives; the
   skeleton was never a skinning target for any mesh, and it remains
   fully in the source blend). The master's skinning rig (984
   joints), every polygon-bearing object, all 98 shape keys and all
   7 exportable images are intact.
6. Both files export at REST, not at the blend's authored flex pose
   (61 pose bones) — Tobi/Pond precedent; the blend in the repo is
   the canonical source and keeps the pose.

**Next in the owner's order after Chatur: Ryusan** (Mina Ashido;
520-bone Rigify blend in repo, 71 shape keys, Lucky Chloe T7 bank to
retarget). Megami/Menajerii recovery status has CHANGED since the
last checkpoint update: the TeraBox check came back NEGATIVE, and the
two commissions were identified on SmutBase as MilkGuy_3D's
"Parvati Holcomb" (ParvatiCommission.rar) and "Vixen"
(Vixen_Commission.rar) — a browser lane is downloading both rars.

## RYUSAN REBUILD — LANDED (2026-11-05, PR #1574)

Rebuilt from her own blend (`roster/mina-ashido/intake/Mina Ashido
rigify/ryusan-mina.blend`, 7,396,031 B, sha256
75f96a453d2b8a673232af91138a9160d8d0ff3e682c0bfce10ab662219e328d) in
Blender 5.2.3. The 73-joint template conversion is retired for her.
Rebuild script: tools/anim/export_ryusan_fidelity.py.

**Files**
- Game (loaded path, replaced in place):
  roster/mina-ashido/attires/attire1/model-rerig.glb — 3,267,036 B
  (was 5,079,568 B shipped), 521 joints (the blend's full 520-bone
  skinning rig + root), 64 morph targets, 7 images, 6 materials.
- Master: roster/mina-ashido/attires/attire1/model-blend-master.glb —
  3,535,264 B, 521 joints with the ORIGINAL bone names, 71 morph
  targets, 8 images, 7 materials, every polygon-bearing object.
- Proof: docs/proof/2026-11-04/smutbase6-fidelity/
  ryusan-fidelity-{front,q34,face}-20261105.png (EEVEE renders of the
  rebuilt game file).

**The rig, as measured** — two armatures live in the blend. The
skinning rig is the object "Mina Ashido": 520 bones, 169 of them
deform — a Rigify DEF- body plus a GZM-style face rig (brows, lids,
eyeballs, lips, Jaw, Tongue, Breast, Butt, Penis0-5). Every
character mesh's ARMATURE modifier points at it. The 65-bone
"backup-metarig" skins NOTHING (no modifier references it); it is
dropped from the game file and its skin is pruned from the master
pack (deviation 5; the metarig object node survives, and the
skeleton remains fully in the source blend). The blend's pose is
all-rest (0 nonzero pose bones, dump-verified).

**A measured trap: deform-only export flattens Rigify.** The first
game build exported Blender's deform-only subset (170 joints).
Blender's deform-only path re-roots every ORG-parented DEF bone at
the skin root (Rigify parents DEF- bones to ORG- control bones),
disconnecting the arms/legs from the spine. The engine's rig
analysis (t3anims.js analyzeRig — chest = lowest common ancestor of
the two arms) then returns null and the bank never binds ("lacks
core humanoid bones", all-inputs TPOSE in the play probe). The game
skin therefore carries the FULL 520-bone rig (Pond 224 / Tobi 254
precedent — the full rigs ride), with the authored hierarchy intact
(verified live: LeftArm -> ORG-shoulder.L -> ORG-spine.003 ...;
Head -> Neck -> DEF-spine.004 -> Chest).

**Method notes** — 32 driver fcurves drive Mina's shape keys from
the face-rig bones (authored mixes read Mina NipplesFlat = 1.0,
suit 'nipples flat' = 1.0). Drivers have no glTF representation;
they are stripped in the export copy only, after capturing the
rest-evaluated authored values, and the shapes ship as morph
targets (the repo blend keeps the driver rig). The MASK modifier
(SuitHide, inverted) on Mina is baked through the depsgraph with
the armature ACTIVE (authored mixes folded into the bases per the
Tobi method; folded keys keep zero-delta targets so nothing
double-applies): Mina 20,719 -> 13,044 verts; the suit bakes the
same way. Floor lift +0.0473 on the armature (her soles sit at
z = -0.0473 in the blend's own coordinates); uniform scale
x0.3128614551655725 to 1.992 m total character height (the shipped
file's own stance span -0.996..+0.996). Repo codec pack (meshopt +
quantization, keepSolidTextures); embedded-image sha256 sets are
identical raw vs packed (game 7/7, master 8/8 — the master's extra
image is the penis texture).

**Shape-key accounting: 71/71** — Mina 62 + Horns 1 + suit 1 ride
in both files (64 targets); the Penis mesh's 7 ride only in the
master (author-hidden mesh, deviation 2). Nothing fabricated:
Horns' single key is named 'Armature' — a rest-state key with
measured-zero deltas that exists in the blend as authored.

**Material gate** (the game's own auditGltf): game file 10/10 prims
ok, 0 missing/placeholder/untextured. Master 11 ok + 1 'missing' =
the material-less template helper prim (Plane.003 — it has no
material in the blend; source trait, archival only).

**Proof + probes**
- Blender EEVEE renders of the packed game file (front / 3/4 /
  face): pink skin and hair read pink everywhere, tan horns,
  black-sclera / yellow-iris eye maps, teal/purple camo hero suit,
  fur collar, jacket, boots — matching the phase-1 blend reference
  renders. No white blow-out (contrast Chatur's in-game harness
  caveat: hers is a serve-harness lighting state; Ryusan's Blender
  proof is clean).
- Roster probe (game harness, BASICS): all 10 press true; damage
  parity class with the shipped model (4: 13.1, 1+2: 5.3, d/f+1:
  11.4, d+1: 2.6, d/f+2: 12.3 exact; 1/2/3 in the single-hit variance
  class the Tobi/Pond probes also showed; u/f+4: 19 vs shipped 7 —
  the rebuilt hop kick lands its full multi-hit where the shipped
  conversion chunked to one hit; 1+3 throw deals 0 at probe spacing
  on BOTH models).
- Play probe: t3actions 20 (= shipped), mixer 20 actions, 12/13 OK
  at mixer weight 1.0 with the SAME plans as the shipped model (t7
  rows for 1/2/3/4/d/f+1/d+1/f+2, generics for 1+2/d/f+2/1,2, grab
  for 1+3); d+3 NOFIRE on both models (single-press harness
  limitation, same class as Pond's string extras). Bind-pose
  fraction 0.25-0.33 (metric counts more same-named bones on the
  full Rigify hierarchy; 75% of measured bones are off bind
  mid-clip = animated; TPOSE threshold is 0.7).
- Gate check vs a live animated Pantera: roundState 'fight',
  "[WH] Fighter ryusan: 20 real T3 actions from bank 'luckychloe'
  (retargeted onto ryusan)" + 27 real T7 move clips loaded.
  Canvas frame grabs came out black in this headless harness (the
  same capture limitation the Pond lane hit) — logged honestly;
  the Blender renders above are the visual proof.

**Deviations (game file only unless noted; the master keeps
everything)**
1. 22 core bones renamed to the engine's canonical names
   (DEF-spine->Hips, DEF-spine.001->Spine, .002->Spine1,
   .003->Chest, DEF-spine.005->Neck, .006->Head,
   DEF-shoulder/upper_arm/forearm/hand -> Left/RightShoulder/Arm/
   ForeArm/Hand, DEF-thigh/shin/foot/toe -> Left/RightUpLeg/Leg/
   Foot/ToeBase). DEF-spine.004 keeps its blend name as an in-chain
   helper (the engine drives the spine through it; Pond Elbow/Knee
   precedent), as do the segment/FK/tweak bones. The runtime
   retargeter matches NO Blender-style name, so without this the
   model gets no animation at all. Master keeps original names.
2. Author-hidden Penis excluded from the game file (Pond #1552
   precedent — the author hid it in the blend itself:
   hide_viewport + hide_render). It is also UNSKINNED as authored
   (8 ARMATURE modifiers, all with object=None) — a source trait,
   recorded, not repaired. Preserved in the master with its 7
   shape keys and its texture.
3. Template helper meshes (directional, switch, up, down,
   face_template, mouth_template) and the 131 zero-polygon WGT-*
   widget gizmos are dropped from the game file; all preserved in
   the master.
4. 8 of 10 packed images export, in BOTH files:
   Mina-hero-outfit_Height.png feeds a Displacement node (no glTF
   slot), and the skin_head image sits in a $bumpmap node whose
   outputs are NOT LINKED in the blend's own node tree
   (node-audited) — the exporter omits both. Both maps remain
   packed in the blend, which stays in the repo.
5. Master pack (repo codec prune): the unreferenced
   backup-metarig SKIN and 135 zero-geometry WGT/template nodes
   were pruned by the codec (the metarig object node survives;
   Chatur deviation-5 precedent). The master's skinning rig (521
   joints), every polygon-bearing object, all 71 shape keys and
   all 8 exportable images are intact.
6. Shape-key drivers stripped in the export copy only (see method
   notes); the repo blend keeps the driver rig.
7. The game skin carries the FULL 520-bone rig, not a deform-only
   subset (see the measured trap above) — the full deform set
   (169 bones) rides inside the full rig.
8. Fur kept in both files although it is hide_render in the blend:
   it is visible in the blend as opened (viewport state) and it
   shipped in the old file; the phase-1 EEVEE reference renders
   omit it only because renders honor hide_render.

**Next in the owner's order after Ryusan: Megami** (Parvati /
Jun Kazama) — gated on the Track 1 recovery close-out lane
(ParvatiCommission.rar + Vixen_Commission.rar re-downloads), which
is running in parallel; this lane does not start Megami.


---

## MEGAMI + MENAJERII SOURCE RECOVERY — FOUND (2026-11-05, this PR)

The two commission packages are recovered. The TeraBox check came back
negative; a browser lane then identified the original SmutBase listings
(MilkGuy_3D: "Parvati Holcomb" project 9ca4fe0b…, "Vixen" project
c7db985f…) and re-downloaded both archives from the free mirror. The
recovered files were extracted, inventoried in Blender 5.2.3, rendered
for identity, and stored on the intake release (below) — they no longer
exist in only one place.

**The archives are byte-identical to the lost originals.** The full
original sha256 values were preserved in the lane checkpoint
(`~/workspace/agent-ops/checkpoints/smutbase6-fidelity-20261104.json`)
all along, and both re-downloaded rars match them exactly:

| File | Bytes | sha256 | vs original record |
|---|---|---|---|
| `ParvatiCommission.rar` | 326,033,257 | `2601d9356f5e530cd0abb0956db99fc47e2b70bba4bec58908ce64fc8dc68ff7` | **EXACT match** |
| `Vixen_Commission.rar` | 412,236,235 | `e6d2754b09f6de050e8a586d6fca3c4ed49f57fcdc4c1f36abfdc41c2be5e5a7` | **EXACT match** |

Hash note (the open question this lane had to settle): the SmutBase
mirror page states a "source" SHA-256 for the Parvati archive of
`2601d935e1f8a09e1da0d67ad3b47eae4d2f4e9f38bc3a0d6dd0b0b5fbb6da8` —
same 8-char prefix, different thereafter. That page value is the
artifact: the downloaded archive's own hash matches the ORIGINAL
intake record digit for digit, and the contents independently match
the intake description (below). The Vixen mirror page value matches
in full.

**Extracted blends (inventory: Blender 5.2.3, measured)**

| | Parvati(Commission).blend | Vixen (Commission).blend |
|---|---|---|
| Bytes | 595,860,144 | 984,617,116 |
| sha256 | `cfc9864a15b03989b9dcb559e5fffc02bde8075f26472eeb4308500f01a8612a` | `085d914c6539e0bef89f881ba6887336a1d93115ee6bef792161ec737c375670` |
| File version | Blender 4.2 (reads 4.2.66) | Blender 4.2 (reads 4.2.66) |
| Scene objects | 66 (55 MESH, 1 ARMATURE, 5 LIGHT, 1 CAMERA, 4 EMPTY) | 67 (56 MESH, 1 ARMATURE, 5 LIGHT, 1 CAMERA, 4 EMPTY) |
| Armature | `Parvati` — 469 bones | `Vixen` — 450 bones |
| Rig | GZM — `GZM_*` controller objects present (GZM_Arrows / GZM_CircleChest / GZM_FaceHead / …) | GZM — same controller set |
| Shape keys | 474 non-Basis, all on `Parvati Mesh` | 2,509 non-Basis across 24 meshes (515 on `Vixen Mesh`, 365 Body Suit, 355 Suit, …) |
| Images | 124 total, 123 packed | 125 total, 124 packed |

Intake-record deltas, stated plainly: the old record said "Blender
4.02, 90 / 88 objects." The files read as Blender 4.2 and hold 66 / 67
scene objects (the old counts evidently enumerated more than scene
objects). Every hard identifier — archive hashes, byte sizes, GZM rig,
character identity — matches; these are counting/label deltas in the
old record, not a different package.

**Identity proof (eye-checked, this PR)**
- `docs/proof/2026-11-04/smutbase6-fidelity/parvati-src-front-20261104.png`
  + `parvati-src-q34-20261104.png` + `parvati-src-face-20261104.png`:
  the recovered Parvati, fully textured in her blend — same character,
  face, and steampunk outfit (goggles, chest plate, belt + hanging
  cloth, thigh pouch, arm guards) as `parvati-full.glb`, piece for
  piece. (In the GLB she reads silver-haired because the 8 hair-strand
  materials carry no texture — the source trait recorded above; the
  blend's hair is dark and textured.)
- `docs/proof/2026-11-04/smutbase6-fidelity/vixen-src-front-20261104.png`
  + `vixen-src-face-20261104.png`: the recovered Vixen — same suit
  (high collar, spiked neck emblem, long sleeves, pelvis emblem, knee
  guards, boots), face, and proportions as the intact sibling
  `model.glb`, piece for piece.
- Full inventories: `inventory-parvati-recovered.json`,
  `inventory-vixen-recovered.json` in the same proof folder.

**Store (mirror law — never one copy again)**
Release `megami-menajerii-smutbase-20261023` (mhvnsnt/western-heart)
now holds, alongside the original two GLBs:
- `ParvatiCommission.rar` (326,033,257 B) — whole, digest verified
- `Vixen_Commission.rar` (412,236,235 B) — whole, digest verified
- Both blends as 300 MB parts (`ParvatiCommission.blend.part-00/01`,
  `VixenCommission.blend.part-00…03`) with `MANIFEST-recovered-blends.md`
  (whole-file + per-part hashes, reassembly commands).

Why parts: uploads above ~412 MB from the work VM never finalized on
GitHub's side in this session — assets stayed in "starter" state with
no retrievable content (range GET → 404) even though both the gh CLI
and a direct curl POST reported success and sent the full byte count.
A 419,430,400-byte part failed repeatedly; everything ≤ 412,236,235 B
succeeded. The blends therefore went up as ≤ 314,572,800-byte parts,
one at a time via direct API POST. (GitHub also sanitizes asset names,
so the blends' parts use the undressed names; the manifest maps them
back to the original filenames.) Every stored asset's size + sha256
digest was verified against the local file via the Releases API, and
the store was pull-back proven: all six parts re-downloaded,
reassembled, and both whole-file sha256 values reproduced exactly;
`ParvatiCommission.rar` likewise re-downloaded and hash-matched.
Local copies:
`~/workspace/_smutbase6-fidelity-20261104/recovered-sources/` (blends +
renamed rars); the browser-download originals remain untouched in
`~/workspace/browser_downloads/sess-316653875/`. The only deletions in
this lane were the lane's own empty "starter" upload shells, removed
to retry the same files until they landed. Nothing else was deleted.

**Status change:** Track 1 recovery is DONE. Rebuild steps 5 (Megami)
and 6 (Menajerii) in the plan above are UNBLOCKED — the "BLOCKED on
source recovery" wording is superseded by this section. The rebuilds
themselves are NOT started here; they keep their place in the owner's
order (Chatur → Ryusan → Megami → Menajerii). The full rigs, morphs,
and textures the fidelity order demands for these two now exist in
hand: Parvati 469-bone GZM rig + 474 shape keys + 123 packed images;
Vixen 450-bone GZM rig + 2,509 shape keys + 124 packed images.

## MEGAMI REBUILD — LANDED (2026-11-05, PR #1576)

Rebuilt from her own recovered blend
(`ParvatiCommission.blend`, 595,860,144 B, sha256
cfc9864a15b03989b9dcb559e5fffc02bde8075f26472eeb4308500f01a8612a —
byte-identical to the lost original commission, recovery #1575) in
Blender 5.2.3. The 52-joint template conversion is retired for her.
Rebuild script: tools/anim/export_megami_fidelity.py; texture pipeline:
tools/anim/megami_texture_pipeline/.

**Files**
- Game (loaded path, replaced in place):
  roster/parvati/attires/attire1/model-rigged.glb — 41,319,032 B,
  469 joints, 474 morph targets, 40 images, 28 materials.
  The registry previously loaded model-rigged-nooutfit.glb (WH #1549);
  game/js/assets.js now points `megami` + `megami-attire1` at
  model-rigged.glb, and model-rigged-nooutfit.glb stays on disk
  untouched as the named no-outfit option.
- Master: roster/parvati/attires/attire1/model-blend-master.glb —
  61,156,276 B, 469 joints with the ORIGINAL bone names, 474 morph
  targets, 86 images, 71 materials, every polygon-bearing object
  (incl. the floor Plane and all author-hidden garments).
- Full-resolution master (uncapped textures, 314,555,688 B) on release
  `megami-menajerii-smutbase-20261023` as megami-master-packed.glb —
  the in-repo files cap textures at 1024 px (the shipped roster's
  class); the source blend remains the full-res record.
- Proof: docs/proof/2026-11-04/smutbase6-fidelity/
  megami-fidelity-{front,q34,face}-20261105.png (front/q34 EEVEE;
  face Cycles — see the eyes note below).

**The rig, as measured** — one armature "Parvati": 469 bones, 211
deform, DAZ/GZM construction. Skin weights ride `.twk` terminal
deformers under bend/twist mid-bones; the arm assemblies hang off
`hip` via arm_parent.L/R, which Blender drives by COPY_TRANSFORMS
from armSocket.L/R on the clavicles. glTF carries no constraints, so
the export copy repairs the hierarchy to the rig's own constraint
intent (arm_parent→armSocket, upper_arm.bend→upper_arm,
thigh.bend→thigh — the Ryusan/Tobi pattern); a TEST-mode A/B export
measured the bind-pose cost at max joint-world delta 0.000001
(bind-neutral). 23 core bones renamed to the engine's canonical
names in the game file only. The blend carries an authored pose
(12 nonzero pose bones, hair + IK poles); export is at REST like
every lane before this one. All 474 non-Basis shape keys sit on
Parvati Mesh, are ALL driver-driven, and ALL evaluate to 0 after a
depsgraph update — the authored look is the Basis; drivers are
stripped in the export copy and every key ships as a morph target
(474 accounted: 474 targets, 0 folded, 0 on hidden meshes).

**The authored look is a view-layer state, and it decides the game
file's wardrobe.** The blend's only view layer EXCLUDES the
collections Wearables 1, Wearables 2, Wearables 3, Hair 2 and
Public Hair from viewport and render alike. Opened and rendered as
saved, she wears only the `Original` collection (Top, Bottom,
Gaunlet, Goggles, Shoes), the Hair.001 updo and the Full chest
patch — exactly what the recovery lane's source renders show. The
excluded 17 objects (Bra, Pantie, Stocking.001, Heels, Body Suit,
Heels 3 robe, Belt, Bra (2), Choker, Glove L/R, Pantie 3, Stocking,
Heel R, the 184k-vert Hair hairstyle, Triangle, Stripe) are the
author's alternate wardrobe, toggled off in her own file. A first
build that shipped everything put three outfits on her at once —
bra cups over the corset, the sheer robe over the pants, a second
hairstyle, and the Heels/Heel R shells floating at her feet (their
z-minimum, -0.146, even set that build's floor lift). Those 17
objects are author-hidden in the Pond #1552 sense: out of the game
file, all present in the master. The GZM widget meshes (0-poly) and
the floor Plane are likewise game-dropped, master-kept.

**Floor and scale** — evaluated REST sole (her Shoes) at
z = -0.1176, lift +0.1176 applied to the root objects of both
files. Uniform scale x0.69382 on the game file, anchored to the
shipped model's own body height (sole->top 1.3597 m, measured on
the decoded shipped file); the raw blend figure is 1.9598 m
sole->top. In-game she stands 1.334 m at idle (Box3 of the live
skinned model, feet at minY -0.001 — grounded), against Pantera's
1.85 m in the same capture: ~72% of his height body-to-body, the
same body scale the WH #1568 Jun-bank fix was baked against. (The
older "~85% of Pantera" record compared full file spans including
the robe hem that trailed 0.18 m below her soles in the old
conversion.) NOT tiny, NOT crumpled: the Jun bank play probe on
the new rig reads bindFrac 0.08 — identical to the shipped rig.

**Textures: the stock exporter cannot lift this blend on this
box, so the wiring is the exporter's own, transplanted.** 61 of
the used images are 4096x4096 (17.1 GB of float pixels); a direct
AUTO export OOM-dies mid-extraction, and export_keep_originals
embeds zero images (the packed originals point at dead DAZ paths).
The lane therefore exports a 64x64 proxy blend through the stock
exporter (identical script and settings — the exporter's own
wiring decisions at trivial memory), rebuilds every image payload
at full resolution from the blend's packed data following the
exporter's own packing rules (base+alpha packs, metallic/roughness
channel packs, bump maps riding the normal slot exactly as the
exporter emits them), and grafts the payloads onto the morph/
geometry export. Every payload was verified against its proxy
image in a channel-independent comparison (worst mean error 9.1,
JPEG generation noise; median 2.5). Image accounting: the blend
holds 124 images = 123 packed textures + Blender's "Render
Result" slot. The master carries 86 GLB image entries covering 91
distinct blend images (97 source slots; the exporter's material
variants re-emit 6 images). The 32 packed textures not carried are
the channels the Principled conversion itself does not carry:
SSS maps (4), the hair SSS/specular/translucency set (6),
GoldenPalace group-internal maps superseded by the carried set
(4), *_N normal companions of carried *_B bump maps and the
choker's factor-resolved companions (7), Kayla heel bump maps the
exporter did not wire (2), the t_char *_l light maps (5), a wall
coat and a scene lightmap not on the character (2), plus
G8FBaseArmsMapS_1004 (specular carried for face/torso/legs only).
The game file carries the 40 images of the authored-look subset;
the other 51 master-carried images belong to the author-hidden
garments. Two codec findings, both verified by A/B runs:
(1) the repo codec's prune() step drops TextureInfo.texCoord and
then the TEXCOORD_1 attribute it considers unused — Parvati's
GP_Torso-1/GP_Torso_Back-1 sample their maps on TEXCOORD_1, so
both Megami files are packed with the codec's meshopt step only
(encode_meshopt_only.mjs in the texture pipeline); any future
model with texCoord>0 materials will lose them in the standard
encode. (2) Bump maps exported as normalTexture are the stock
exporter's own behavior on DAZ graphs and are preserved as-is.

**The material gate needed one honest amendment.** The rebuild's
audit: 26 ok / 0 missing / 0 placeholder / 4 untextured — the 4
being EyeMoisture-3, EyeMoisture-4, Cornea-2 (clear eye shells,
transparent by design) and Torso-6 (inner strand shell) — exactly
the source-faithful classes the owner's 2026-11-03
OUTFIT-NOT-THE-GATE exemption already names. But the exemption
also voided itself if ANY 24_/25_-named material remained in the
file, on the 2026-11-03 premise that those shells "never had
textures in her source file". The recovered blend refutes the
premise: all seven 24_/25_ outfit materials carry base textures
in the rebuild, because they carry them in her file. Both gate
implementations (game/js/material-runtime.js and
tools/assets/material_gate.mjs) now void the exemption only on a
TEXTURELESS 24_/25_ material, and the gate's exempt URL follows
the registry to model-rigged.glb. Verified live: with the
amendment the fight loads; without it the runtime gate blocks her
(4 untextured).

**Eyes note** — in the EEVEE proof harness the transmissive
cornea/moisture layers frost white and hide the iris (a
diagnostic render with those two materials temporarily
transparent shows the full authored eye: hazel iris, pupil,
sclera, all from her own textures). The face proof is therefore
rendered in Cycles, the source file's own engine, where the stack
reads as authored. The game uses three.js physical materials;
the parent lane's live check owns the final in-game read.

**Probes (serve tree at main + this PR's files)**
- Gate/load: fight state reached, no gate errors (post-amendment).
- BASICS damage parity vs the shipped model, exact on all 10:
  1:6.4, 2:7.3, 3:12.8, 4:15.6, 1+2:16.5, d/f+1:9.2, d+1 no-fire
  (dead on the shipped model too), d/f+2:12.8, u/f+4:5.5,
  1+3:32.1 (throw).
- Jun bank play probe: 12 t3 actions attached; sampled inputs
  (BASICS + 1,2 / d/f+1 / f,f+2) identical to the shipped-rig
  baseline — all OK at action weight 1, bindFrac 0.08; d+1 and
  f,f+2 no-fire on both rigs (known dead inputs, not a rebuild
  regression). The WH #1568 re-baked clips play on the new rig
  unchanged: the rebuild's scale matches the rig they were baked
  against (above), so no re-bake was needed.
- Scale: measured in the live scene (above) — 1.334 m vs
  Pantera 1.85 m, feet grounded.
- Canvas frame grabs in the swiftshader harness come out black
  and page.screenshot times out on fonts (the Pond/Ryusan harness
  limitation); the scale verdict above is numeric from the live
  scene, and the visual proof is the Blender renders. Logged
  honestly, not faked.

**Deviations (each with its ref)**
1. 23 core bone renames, game file only — engine canon-name
   requirement; precedents #1570-#1574, approval WH #1567.
2. 6 hierarchy reparents in the export copy — constraint-intent
   repair, bind delta measured 0.000001; same refs.
3. REST export (authored pose of 12 bones stays in the blend) —
   all-lane precedent.
4. Author-hidden set (17 wardrobe objects) + GZM widgets + Plane
   dropped from the game file, all kept in the master — Pond
   #1552 author-hidden precedent; view-layer evidence above.
5. Dead object=None ARMATURE modifiers removed in the export
   copy (Shoes 1, Top 1, Hair.001 1 — Hair.001 therefore ships
   rigid on its head bone-parent, exactly as authored; weight
   authoring would be fabrication).
6. SUBSURF ships as cage (export_apply=False) — all-lane
   precedent.
7. Game + in-repo master textures capped at 1024 px — shipped
   roster class; full-res master on the release, source blend
   untouched.
8. Texture wiring via proxy-export graft (stock exporter OOMs
   on 61x 4096^2 images); payloads verified per-image.
9. Encode without prune() — the codec finding above; output
   format identical (EXT_meshopt_compression).
10. Material-gate exemption amendment (runtime + CI mirror) —
    owner rule 2026-11-03; premise correction documented in both
    files' comments.

**Next: Menajerii (Vixen, Roger Jr.) — the last of the six. NOT
started here.** Her recovered blend (450 bones, 2,509 shape keys,
124 packed images) is inventoried in the recovery section above.


## MENAJERII REBUILD — LANDED (2026-11-05, PR #1577)

Rebuilt from her own recovered blend
(`VixenCommission.blend`, 984,617,116 B, sha256
085d914c6539e0bef89f881ba6887336a1d93115ee6bef792161ec737c375670 —
byte-identical to the lost original commission, recovery #1575) in
Blender 5.2.3. The 52-joint template conversion is retired for her —
the last of the six. Rebuild script:
tools/anim/export_vixen_fidelity.py; texture pipeline: the Megami
lane's tools/anim/megami_texture_pipeline/ (proxy-graft), with the
payload solver run per-image (this lane's solver:
scripts/build_payloads.py in the lane record).

**Files**
- Game (loaded path, replaced in place):
  roster/vixen/attires/attire1/model-rigged-noplane.glb —
  39,136,632 B, 450 joints, 932 morph targets, 26 images,
  21 materials. game/js/assets.js already pointed `menajerii` +
  `menajerii-attire1` at this path; the registry comment now records
  the rebuild. model-rigged.glb (the #780 crew file) and model.glb
  stay on disk untouched as the earlier named options.
- Master: the full blend export (451 joints — 450 blend bones +
  the exporter's generated neutral_bone for the unskinned meshes —
  2,509 morph targets, 80 images, 69 materials, every
  polygon-bearing object incl. the floor Plane and all
  author-hidden garments) is 114,293,416 B even with textures
  capped at 1024 px, over GitHub's 100 MB per-file limit, so there
  is NO in-repo model-blend-master.glb for her (deviation 14).
  Both master builds are parked on release
  `megami-menajerii-smutbase-20261023` (her oversized-artifact home
  since intake): menajerii-master-capped1024.glb (114,293,416 B,
  sha256 07b5428ea31f09c457825e5910f85128420012ec70eaba81c9443b171333bb20)
  and menajerii-master-packed.glb (493,068,228 B, uncapped
  textures, sha256 e4a425cc2ccc4260d730ccf39095a13803bcd4a550a85757e5af916c0248526e),
  both digest-verified on the release via the API. The game file's
  textures are capped at 1024 px (the shipped roster's class); the
  source blend remains the full-res record.
- Proof: docs/proof/2026-11-04/smutbase6-fidelity/
  menajerii-fidelity-{front,q34,face}-20261105.png.

**The rig, as measured** — one armature "Vixen": 450 bones, 192
deform, DAZ/GZM construction, identified by modifier reference
(every character mesh's live ARMATURE modifier points at it). Same
DAZ/GZM family as Parvati: arm_parent.L/R hang off `hip` under
COPY_TRANSFORMS from armSocket.L/R on the clavicles; leg_parent
likewise from legSocket on the pelvis. glTF carries no constraints,
so the export copy repairs the hierarchy to the rig's own
constraint intent (arm_parent→armSocket, leg_parent→legSocket,
upper_arm.bend→upper_arm, thigh.bend→thigh — 8 reparents); a
TEST-mode A/B export measured the bind-pose cost at max joint-world
delta 0.0000128 (bind-neutral, float-noise class). 23 core bones
renamed to the engine's canonical names in the game file only (the
identical set to Megami's). The blend's only nonzero pose bones are
the 4 IK pole targets; export is at REST like every lane before
this one. All 2,509 shape keys across 24 meshes are driver-driven
and ALL evaluate to 0 after a depsgraph update — the authored look
is the Basis; drivers are stripped in the export copy and every key
ships as a morph target: 932 in the game file (Vixen Mesh 515, Suit
355, Necklace 21, Hair 18, Arms 13, Boots 10) and 2,509 in the
master (the remaining 1,577 ride the author-hidden wardrobe meshes).
20 meshes carry a dead object=None ARMATURE modifier (a source
defect, also present on Ryusan's blend); removed in the export
copy. Hair and Necklace are two of them — as authored they are
bone-parented (Hair→head, Necklace→neck) and ship rigid on those
bones, exactly as the file has them; weight authoring would be
fabrication.

**The authored look is the blend's single view layer, and it
decides the game file's wardrobe.** The layer EXCLUDES the
collections Public Hair, Lingerie 1, Lingerie 2, Lingerie 3, BDSM
and Hidden (the 31 GZM widget meshes) from viewport and render
alike. Opened and rendered as saved she wears the cheetah-print
suit, the tall hair, arms, necklace and boots — the game set. The
excluded 22 wardrobe meshes (three lingerie sets, the BDSM
harness set, three public-hair cards) are the author's alternates,
toggled off in her own file: out of the game file, all present in
the master (the Pond #1552 author-hidden sense). The GZM widgets
(0-poly) and the floor Plane are likewise game-dropped,
master-kept. Vixen has NO literal fox ears in the blend or the
rebuild — none added (recovery #1575 finding).

**Floor and scale** — evaluated REST sole (her Boots) at
z = -0.0576, lift +0.0576 applied to the root objects of both
files. Uniform scale x0.94643 on the game file, anchored to the
shipped model's own in-game idle height (1.80 m, measured in the
live scene on the shipped file); the raw blend figure is 1.9019 m
sole->top. In-game she stands 1.80 m idle, feet grounded (minY -0.0),
against Pantera's 1.85 m in the same harness = 97.3%
body-to-body — the shipped model's own anchored scale,
reproduced exactly. (Canvas grabs come out black in the
swiftshader harness, the known Pond/Ryusan/Megami limitation;
the verdict is numeric from the live scene.)

**Textures: the proxy-graft route again.** The packed set is
410 MB across 124 images (several 4K); as with Megami, the lane
exports a 64x64 proxy blend through the stock exporter (identical
script and settings — the exporter's own wiring decisions), solves
every image's payload rule against the proxy pixels, rebuilds the
payloads at full resolution from the blend's packed data, and
grafts them onto the morph/geometry exports. Game set: 24 of 25
images are the source bytes verbatim (identity-bytes, verify error
at JPEG/PNG generation noise, worst 7.4 on the small mouth maps);
the one pack — the hair base color — is the exporter's own
base+alpha pack (RGB from Cheetah_A_Hair_Color, alpha =
luma(Cheetah_A_Hair_CO)), verified at 0.92 mean error with a
channel-independent comparison (PIL's RGBA resize premultiplies
alpha and reports a phantom 14.5 on this pack — a verify-method
artifact, recorded here so the next lane doesn't chase it). DAZ
bump-in-normal-slot wart the Megami lane preserved as-is is
CORRECTED here (deviation 12): on Vixen's strong G8F bump maps it
breaks the authored look outright (charcoal skin), so the slots
carry authored normals / hand-applied bump bakes instead.
GP_Torso-1 / GP_Torso_Back-1 sample their maps on TEXCOORD_1, so
both files are encoded with the codec's meshopt step only — the
prune() landmine from the Megami lane applies unchanged.
Image accounting: the blend holds 125 images = 124 packed +
Blender's "Render Result" slot. The game file carries 26 GLB
entries covering 26 distinct blend images (the 25 the exporter
wires, plus the one appended GP_Torso normal conversion of
deviation 12); the master carries 80 GLB entries covering 89
distinct blend images. The 35 packed images not carried are
declared, none silent: 16 pixel-identical duplicate datablocks of
carried images; 10 height/bump companions superseded in their own
normalTexture slots by the authored normal maps or the deviation-12
conversions; 4 GoldenPalace group-internal maps superseded by the
carried GP trio; 2 Mix.B inputs the Principled conversion drops
(the Necklace group's 3f0a05d6…jpg and the Cheetah groups'
NormalMap (27).png); 1 displacement map with no glTF slot
(dtt_HHSBC1_Displace); 2 wall-coat scene-dressing images. The
per-image record lives in the lane's payload manifests.

**Probes (serve tree at main + this PR's files)**
Gate: the loaded file audits ok 21 / missing 0 / placeholder 0 /
untextured 2 — the 2 are EyeMoisture-2 + Cornea-2, clear
transmission shells (deviation 15 extends the outfit-rule
exemption to her keys, the Megami #1576 mechanism); the harness
gatecheck reaches roundState fight with p1model loaded and no
load error. BASICS roster probe vs Pantera: all 10 inputs press
true; damage parity with the shipped model on 7 of 10 (1: 6.7,
1+2: 16.3, d/f+1: 5.8, d+1: 11.5, d/f+2: 14.4, u/f+4: 12.5,
1+3: 33.5 with the throw seen); inputs 2, 3, 4 land different
hit-segment totals (9.6 -> 11.5, 22 -> 24, 19.2 -> 15.3,
deterministic across two runs — deviation 16; the moveset data
is untouched). Grabs probe: 1+3 connects at 33.5; 2+4 presses
and grabs for 0 damage, exactly the shipped model's pre-existing
throw-execution anomaly (cf. Pantera A1) — matched, not masked.
Roger bank play probe: 15 T3 actions bound, 15 mixer actions,
all 10 BASICS rows OK at weight 1, bindFrac 0.08, 1+3 playing
Roger's own grab clip — row-for-row identical to a control run
of the shipped model in the same tree. (Probe-environment note:
the lane's probe copy of the tree was missing
game/assets/anim/t3/roger/; restored from main before probing —
on main the bank was always present.) Proof renders
(front/q34 EEVEE, face Cycles) eye-checked in the lane: warm tan
skin, red lips, blue irises, cheetah suit, silver arm guards,
orange boots — the authored look; an intermediate build failed
this check with charcoal skin and was rebuilt (deviation 12).

**Deviations (each with its ref)**
1. 23 core bone renames, game file only — engine canon-name
   requirement; precedents #1570-#1576, approval WH #1567.
2. 8 hierarchy reparents in the export copy — constraint-intent
   repair, bind delta measured 0.0000128; same refs.
3. REST export (the authored pose touches only the 4 IK pole
   targets) — all-lane precedent.
4. Author-hidden set (22 wardrobe meshes) + GZM widgets + Plane
   dropped from the game file, all kept in the master — Pond
   #1552 author-hidden precedent; view-layer evidence above.
5. Dead object=None ARMATURE modifiers (20) removed in the export
   copy — Hair and Necklace therefore ship rigid on their
   bone-parents, exactly as authored; weight authoring would be
   fabrication. Ryusan/Megami precedent.
6. SUBSURF ships as cage (export_apply=False) — all-lane
   precedent.
7. In-repo textures capped at 1024 px; the uncapped master is
   parked on the release — Megami #1576 precedent (deviation 8
   there).
8. Proxy-graft texture transplant (the exporter's own wiring at
   64x64, payloads rebuilt at full res) — Megami #1576 precedent
   (deviation 9 there).
9. Meshopt-only encode, prune() skipped — Megami #1576 A/B proof
   (deviation 7 there): prune() drops TextureInfo.texCoord +
   TEXCOORD_1, which her GP_Torso materials sample.
10. Game-file scale x0.94643 anchored to the shipped model's
    in-game idle height — Megami #1576 precedent (deviation 11
    there); the game has no height normalization, scale is baked
    into the file.
11. The master carries the exporter's generated neutral_bone as a
    451st joint — it is what the stock exporter emits for the
    unskinned meshes (Plane, strand cards, widgets); the game
    file, whose meshes are all skinned, carries exactly the 450
    blend bones.
12. Bump-to-normal payload correction (the one place this lane
    overrides the exporter's literal output). Where the blend
    feeds Principled.Normal through a Bump node sitting behind
    DAZ group nodes, the stock exporter skips its bump bake and
    writes the raw HEIGHT map into the normalTexture slot. On
    Parvati the same wart was invisible (her bump maps are
    low-contrast); on Vixen the G8F bump maps are strong and the
    shading breaks outright — measured: her skin renders
    charcoal with the height maps in the slots, and renders as
    authored (warm skin, red lips, blue irises) with them
    corrected. The correction is the exporter's own bake,
    applied by hand: where the material chain also carries an
    authored NormalMap companion (the XF lingerie *_N set, the
    BDSM harness normal, ASB2_Mat1_Normal), the payload is that
    authored normal; otherwise it is a Sobel tangent-space
    normal derived from the blend's own height map at the
    blend's own Bump strength x distance. The GP_Torso normal
    slot, which the exporter had filled with the Specularity
    image, receives the Torso bump conversion as one appended
    image (the Specularity image stays for its specularColor
    duty). Slots, sources and strengths are recorded per image
    in the lane's payload manifests (rule "bump-to-normal" /
    "authored-normal-swap"). Deviation from the Megami #1576
    precedent of preserving the wart as-is, because here the
    wart defeats the owner's fidelity bar itself.
13. Buffer-domain payloads for the ASB2 heel set. Three ASB2
    datablocks (Height, Opacity, and the Metallic/Roughness
    pair) hold in-memory pixel buffers that differ from their
    packed file bytes (the file copies are stale — the Height
    file is pure white; the buffer holds the authored leather
    height). The exporter reads the buffers, so the ASB2
    payloads are built from buffer dumps (img.pixels), verified
    against the proxy export at <=1.5 mean error where the file
    bytes scored 15-114. The same check was run across the
    master manifest: every other payload verifies against the
    buffer-derived proxy export at generation-noise levels, so
    no other datablock is affected.
14. Master parked on the release instead of in-repo (both
    builds) — the 1024-capped master is 114,293,416 B, over
    GitHub's 100 MB per-file limit; the release is this
    fighter's established oversized-artifact home (her
    629.7 MB intake original lives there). Sizes + sha256 in
    the Files section above and in ATTIRE-SLOTS.md.
15. Material-gate exemption extended to menajerii /
    menajerii-attire1 (game/js/material-runtime.js) with the
    matching expected-failure entries in
    tools/assets/material_gate.mjs — her audit's only
    untextured materials are EyeMoisture-2 and Cornea-2, clear
    transmission shells with no base texture by design. Same
    class and mechanism as Megami #1576 (deviation 10 there).
16. BASICS damage on inputs 2, 3, 4 differs from the shipped
    template model (9.6 -> 11.5, 22 -> 24, 19.2 -> 15.3;
    deterministic across two probe runs; the other seven
    inputs match exactly, including the 33.5 grab). The
    moveset data is untouched — the totals are hit-segment
    sums, and her real limb proportions change which segments
    connect at probe spacing. Declared rather than tuned away:
    editing damage data to force the template's totals would
    falsify her moveset.

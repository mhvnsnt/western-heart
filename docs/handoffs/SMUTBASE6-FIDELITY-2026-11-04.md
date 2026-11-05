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

## CHATUR REBUILD — LANDED (2026-11-05, PR #CHATURPR)

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
- In-game still capture: attempted twice; the headless harness's
  screenshot call times out under SwiftShader with this scene (the
  fight state itself verified by state probe both runs). Logged as a
  harness limitation, not hidden.

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

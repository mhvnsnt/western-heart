# SmutBase-6 Fidelity Inventory — Pond (Tsuyu Asui) & Ryusan (Mina Ashido)

Lane date: 2026-11-04 CST · Read-only inventory · Full machine data: `inventory-pond-ryusan.json` (+ raw GLB parses in `_glb_parse_raw.json`)

**Method:** every GLB parsed from its JSON chunk in pure python (no Blender). Mina's `.blend` was zstd-decompressed + header/ID-name/driver-string scanned. One Blender 4.0.2 headless attempt on Mina's blend **failed** — both source blends are **Blender 5.0, zstd-compressed**, and 4.0.2 returns "not a blend file". No render was started; the running CJ v5 render was not touched. A Blender 5.x dump is still owed for exact bone counts / hidden flags / shape-key ownership in both blends.

---

## POND — Tsuyu Asui

### Source: FOUND (repo-only, no local copy)
- **Authoritative:** `mhvnsnt/western-heart` main → `roster/tsuyu-asui/intake/Tsuyu Asui IK/Tsuyu Asui IK.blend` — **14,248,117 B**, git blob `0689c144a6b862b436f2d3f909dd8b39df627c67`; `.blend1` 14,211,267 B, blob `043e258a19cceffa2a0b77859fce36cb2c63975f`.
- Origin: `Tsuyu_Asui_IK_V1.1.zip` (intake batch 2, 2026-10-22). Targeted local find (`_smutbase6-fix-20261102`, `model-intake`) found **no Tsuyu .blend locally** — GLBs + textures only.
- **Blend inventory** (from the repo's own `INTAKE-NOTES.md` byte-inspection): 37 objects — body `tsuyu`, separate `suit`, `boots`, `gloves`, `Body_belt.dmx`, `Body_google.dmx`, `Body_mask.dmx`, `Hair`, `Bulge`, `Penis`, `face_template`, `mouth_template`, armature `tsuyu rig` + IK widgets. Clothing is separate modeled geometry. **Frog hat is NOT in the source at all.** Bone count and shape keys were never recorded — **unknown, needs the Blender 5 read.**
- **Intake textures (repo, ×2 locations `intake/textures/` and `Tsuyu Asui IK/textures/`):** Tsuyu_skin 145,979 · skin_face 365,230 · suit_Base_color 1,816,505 · suit_Roughness 1,748,546 · boots_Base_color 1,163,402 · boots_Roughness 747,163 · penis 119,133.
- Local loose intake (`work/tsuyu-intake/`): Roughness PNGs real (2048×2048, sizes match repo); **both Base_color PNGs are 0-byte placeholders** — real bytes live in the repo / embedded in GLBs.

### GLB headline (52 joints in EVERY variant — rig delta orig→shipped = 0)
| File | Bytes | Meshes | Verts (Σ POSITION) | Mats | Images | Anims |
|---|---|---|---|---|---|---|
| orig `models/orig/tsuyu-pond.glb` (sha256 3d429058…) | 7,053,488 | 9 | 295,975 | 9 | 5 | 0 |
| plain decode `work/tsuyu-plain.glb` | 19,982,728 | 9 | 295,975 | 9 | 5 | 0 |
| `work/tsuyu-fixed.glb` (pre-#1552) | 22,485,060 | 9 | 295,975 | 9 | 7 (+suit_MR, boots_MR) | 0 |
| shipped #1530 (superseded) `serve/…/model-rigged-textured.glb` | 9,467,192 | 9 | 295,975 | 9 | 7 | 0 |
| **shipped current main #1552** `visual-gate/models/pond-fixed-20261103.glb` | **8,235,624** | **7** | **240,415** | **7** | **8** | 0 |

Current-main verification: contents API reports 8,235,624 B / blob `73c217ae0a2ad65379f72efd88cc601ddd4d929d`; the local `pond-fixed-20261103.glb` recomputes to that exact blob (md5 `73be6cdbb62cc8276804a4acbca72aa5`) — byte-identical.
Joint names (all variants): 52-name humanoid set Hips→Spine→…→Head, full 15-bone fingers per hand, legs to ToeBase. Meshes (orig): Tsuyu (4 prims), Holo_001, Mesh0000_004, Mesh0000_003, Plane_003, Goggles, Hair, Belt, Mask.

### Pond gaps
1. **#1552 dropped two whole meshes** vs orig/#1530: `Mesh0000_003` (boots, 24,852 verts) and `Mesh0000_004` (penis, 30,708 verts) — exactly the −55,560 vert delta. Materials `boots`/`penis` gone (9→7); `boots_Base_color.png`, boots MR and `penis.png` no longer embedded. **She ships barefoot.**
2. **Gloves lost at the original conversion**: blend has separate `OBgloves`; no glove mesh in any GLB.
3. **Bulge excluded**: separate blend object, absent from every GLB (standing note: reversible by file swap).
4. **Bone delta vs source = UNKNOWN** — blend armature never probed. GLB side is a stable 52 joints.
5. **Shape keys: 0 morph targets in every GLB**; blend shape-key inventory unknown.
6. Gained in #1552: real `eyes.png` / `googles_mask.png` / `hair.png` / `outfit.png` embedded (flat colors in orig) + suit_MR retained.

---

## RYUSAN — Mina Ashido

### Source: FOUND — local copy byte-identical to repo
- **Authoritative:** `roster/mina-ashido/intake/Mina Ashido rigify/Mina Ashido rigify.blend` — **7,396,031 B**, git blob `2771133518074d9c2b8bb7a754bf181e2f4b81c3`; `.blend1` 7,600,277 B, blob `aaaf63e559e0c3fb28ef3eaa74e14581cba4d35c`.
- **Local:** `~/workspace/_smutbase6-fix-20261102/work/mina-intake/rigify.blend` — 7,396,031 B, sha256 `75f96a453d2b8a673232af91138a9160d8d0ff3e682c0bfce10ab662219e328d`, **recomputes to the same git blob → byte-identical to the repo file.**
- `rigify-unpacked.blend` beside it is **0 bytes** (empty placeholder, sha256 of empty file) — not a usable copy; the unpack output is the texture folder.
- **Format:** zstd-compressed, 33,814,160 B decompressed, header = **Blender 5.0**, 64-bit little-endian.

### Blend inventory headline
- **Rig: 520-bone Rigify rig** (per PR #1540 handoff record; not re-probable in 4.0.2) + `metarig` + `backup-metarig`. String scan corroborates: DEF- ×367, MCH- ×497, ORG- ×221 occurrences; armatures `rig`, `metarig`.
- **Objects (non-widget):** Mina, Mina Ashido, **boots, jacket, suit** (separate clothing), Fur, Horns, Hair, Penis, Circle, Cube, Plane, cameras/light, + 100+ `WGT-rig_*` widgets. Object→material map (prior Blender-5 probe): boots/jacket/suit→Mina-hero-outfit, Fur/Horns→body, Hair→hair, Mina→skin.000/body/skin_head/eyes, Penis→Penis. `[Hero]boots/jacket/suit` props + `SuitHide` driver exist — hidden flags themselves **not probed** (Blender 5 read owed).
- **Materials:** 6 used per prior probe (body, eyes, hair, Mina-hero-outfit, Penis, skin.000); string scan finds 8 MA names — adds `skin_head` and `Jiro-hero-outfit` (latter likely unused/leftover).
- **Images: 10 packed**, all recovered to `work/mina-intake/unpacked/`: body 2048² 1,204,030 · mina body 2048² 92,318 · mina penis 2048² 114,724 · hero-outfit Base 2048² 508,747 · Height 2048² 79,203 · Roughness 2048² 22,444 · skin_head 1024² 189,136 · FaceS 1024² 171,241 · eyes 512×256 15,312 · hair 512² 8,976.
- **Shape keys: 31 driver-referenced** — brows (angry/cheerful/lower/sad/serious/upper ×L/R), eye-blink ×4, eyes-look ×4, mouth (a/ch/e/o/u, frown/grin/widen ×L/R), NipplesFlat — plus name strings eyes-slant/surprised/stare/front.

### GLB headline
| File | Bytes | Joints | Meshes/Prims | Verts | Mats | Images | Anims |
|---|---|---|---|---|---|---|---|
| orig `models/orig/mina-ryusan.glb` (sha256 a2190a4b…) | 2,121,260 | 73 ×8 skins | 8 / 11 | 219,951 | 2 | 0 | 1 (CMU135_04_boxing) |
| source-space sibling `work/mina-model-src.glb` | 4,387,244 | — (no skin) | 8 / 62 | 173,165 | 2 | 0 | 0 |
| intermediate `work/mina-rigged-src.glb` | 12,146,544 | 52 ×1 skin | 8 / 11 | 219,943 | 2 | 0 | 0 |
| **shipped current main #1540** `serve/…/model-rerig.glb` | **5,079,568** | **73 ×8 skins** | **8 / 11** | **218,546** | **7** | **8** | 1 |

Current-main verification: contents API 5,079,568 B / blob `470afb0c7e082e85065e5f5d82e9c6ba2f786176`; local serve copy (== `work/mina-textured.glb`) recomputes to that exact blob — byte-identical.
Shipped materials: skin.000, body, skin_head, eyes, hair, Mina-hero-outfit, Penis. Shipped images: body, eyes, hair, hero-outfit Base, hero-outfit MetallicRoughness (packed from Roughness), mina penis, mina body, FaceS.

### Ryusan gaps
1. **Bone delta −447: 520-bone Rigify source rig → 73 shipped joints.** No GLB carries the blend's own rig/IK/FK/metarig/widgets; the lineage is re-rigs only (73-joint split-bone orig; a separate 52-joint intermediate also exists).
2. **All 31+ shape keys lost** — 0 morph targets in the shipped GLB.
3. **Material collapse in the lineage:** every pre-#1540 GLB collapsed the blend's polygon material groups to 2 materials (body/eyes). #1540 rebuilt 7 materials/11 prims from the blend's own per-triangle groups. Residual: `skin_head` material ships with **no skin_head-named image embedded** (189,136 B map absent; FaceS is embedded), and blend-string material `Jiro-hero-outfit` has no shipped counterpart.
4. **Images 10 → 8:** hero-outfit **Height not embedded** (Displacement — no glTF core slot, per #1540) and **skin_head.png not embedded by name**.
5. **Clothing separability lost:** separate blend objects boots/jacket/suit exist as no same-named GLB mesh — geometry is folded into multi-prim source meshes (Cube 24 prims, Fur 29 prims in the sibling export) and single-prim shipped meshes. Undress/hide per-object is impossible from the shipped file.
6. Verts 219,951 (orig) → 218,546 (shipped), −1,405 from the #1540 re-split. Shipped animation is a retargeted CMU clip, not a blend-authored action.

---

## Search record / negatives
- Local `.blend` find (targeted, both trees): Mina rigify ✅ (above); Tsuyu ❌ none; only other hit was an unrelated fishnet material blend. `model-intake/models/*.blend` are other Physique Lab models, none Tsuyu/Mina.
- `gh release list` (top 50): **no Pond/Ryusan intake release** — their originals are in-repo intake (above). The only SmutBase-6 intake release is `megami-menajerii-smutbase-20261023` (other pair).
- Repo `roster/mina-ashido/intake/Mina textures/` dir exists (tree `361c13fe…`) but its listing wasn't retrieved (API 404 on encoded path) — local unpacked set above stands in for it.
- **Still owed (both characters):** one Blender 5.x (5.2.3) inventory dump per source blend — exact armature bone count/names, per-object hide_viewport/hide_render, per-object verts, shape-key ownership, actions. That dump is the fidelity rebuild's true baseline; everything above marked "prior probe / string scan / intake notes" should be re-verified against it.

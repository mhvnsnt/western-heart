# SmutBase 6 Fidelity Inventory — Tobi (Mirko) + Chatur (Rahkasa)

Date: 2026-11-04 · Read-only inventory · GLB JSON chunks parsed with python `struct`/`json` (no Blender)
Checkpoint used: `~/workspace/agent-ops/checkpoints/smutbase6-fix-20261102.json`
Machine-readable version: `inventory-tobi-chatur.json` (same folder)

## Core finding — the .blend question

**Both source .blends EXIST — in the repo, not on local disk.**

| Fighter | Source .blend (mhvnsnt/western-heart) | Size | Git blob |
|---|---|---:|---|
| Tobi / Mirko | `roster/miruko/intake/miruko IK/mirkoIK.blend` | 6,310,244 B | `16032badf812…` |
| Chatur / Rahkasa | `roster/rahkasa/intake/RahkasaV1.1.blend` | 11,459,182 B | `6427d66ea600…` |

Search record:

- `find ~/workspace/_smutbase6-fix-20261102 -iname "*.blend"` → only Mina's `work/mina-intake/rigify.blend` (+ 0 B unpacked copy) and the shared Fishnet material blend in the serve tree. **No Miruko/Rahkasa blend.**
- `find ~/workspace/model-intake -iname "*.blend"` → 21 blends (Essi, Poppy, Qhala, Orn, PiranhaPlant, KirillVolkov, Baigo, Lestya, Succubus_rigify, ReptilianAlienWoman, JuniperActias, MataraKan, Grussy, Lizzy, Hara, MaeOkyra, Daree, DesertGobbo, Vielra, MrSmith). **No Miruko/Rahkasa blend.**
- `gh release list --repo mhvnsnt/western-heart` (50) → no Miruko/Rahkasa release; the only SmutBase-six originals release is Megami+Menajerii (`megami-menajerii-smutbase-20261023`).
- `gh api …/contents/roster/miruko`, `…/roster/rahkasa` + recursive git tree → both intake blends above, confirmed with sizes/blobs.

⚠️ The local "orig" GLBs are **not** sources: they are the pre-fix shipped files downloaded from main (`models6.json`), generator `glTF-Transform` (meshopt-packed repo codec builds). A fidelity rebuild must start from the repo .blends.

---

## Tobi = Mirko (Miruko)

### Source located
- **.blend (repo only):** `roster/miruko/intake/miruko IK/mirkoIK.blend` — 6,310,244 B, blob `16032badf812…`. Provenance: SmutBase `miruko_IK` zip, 7.6 MB, IK-rigged, 14 intake files.
- **Intake textures (repo, 10 PNGs + 1 `~` backup):** `Mirko body.png` 320,986 B · `Mirko body unshaded.png` 26,712 B · `Mirko face.png` 61,652 B · `Neck.png` 5,736 B · `mirko penis.png` 126,015 B · `mirko-belt_Base_color.png` 25,840 B · `mirko-belt_Mixed_AO.png` 550,815 B · `miruko-hero-suit_Base_color.png` 147,823 B · `miruko-hero-suit_Metallic.png` 19,115 B · `miruko-hero-suit_Roughness.png` 28,429 B (all under `roster/miruko/intake/miruko IK/textures/`).
- **Local intake subset** (`~/workspace/_smutbase6-fix-20261102/work/miruko-intake/`, only 3 of 10): belt AO 550,815 B sha256 `784025a5…` (2048²), hero-suit Metallic 19,115 B sha256 `52c2cdaf…`, hero-suit Roughness 28,429 B sha256 `7da18010…`.

### Local orig GLB (pre-#1529 shipped file)
`~/workspace/_smutbase6-fix-20261102/models/orig/miruko-tobi.glb` — **4,119,856 B, sha256 `8df163bcb3b3ec6a5b5eba73db950e31df19ded3806c2c0e4bd688978a691ef7`**

- 11 meshes / 17 prims / **266,980 verts / 89,116 tris** · 85 nodes
- **11 skins × 73 joints** (all skins named `rig`; split-bone set incl. `LeftArm.001`, Left/RightBreast, Left/RightPelvis, HeadTop, palm bones)
- 11 materials, **6 with baseColor texture**, 5 flat-factor only (Eyes, Eyeshadow, Hair, Body ×2) · 6 textures / 6 images (belt, penis, hero-suit, body, Neck, Face base colors) · **0 normal / 0 MR / 0 occlusion**
- 1 animation: `CMU135_04_boxing` (219 channels) · **0 morphs** · all 17 prims have TEXCOORD_0
- Baseline audit: **SEAM CRACKS — 37,445** copies >0.1 (region verdicts are multi-skin tool artifacts; per-part probe: coherent rig, 1.800 m)

### Shipped GLB (game loads, after PR #1529)
`roster/miruko/attires/attire1/model-rerig-textured.glb` — **4,823,088 B, blob `f46f8c4427…`**, PR #1529 merged `59882387…`
Local verified copy parsed: `~/workspace/_smutbase6-fix-20261102/visual-gate/models/tobi-miruko.glb`, sha256 `4a7a96734de44b272241ca7fa04459be9c89c3114430c3e77768237c1b62f61f`

- Geometry/rig/animation **identical to orig**: 11 meshes / 17 prims / 266,980 verts / 89,116 tris / 11 skins × 73 joints / CMU boxing clip preserved
- Textures **6 → 8 images**: Body ×2 wired to the embedded `Mirko_body.png` atlas; hero-suit gains packed MR (`miruko-hero-suit_MR.png`, from intake Roughness+Metallic); belt gains AO occlusion (`mirko-belt_Mixed_AO.png`)
- Seams **37,445 → 0** (checkpoint); visual gate PASS (white/purple suit, purple boots, lavender hair, horns)
- Delta found in JSON: 3 prims lost TEXCOORD_0 vs orig (Eyes, Eyeshadow, Hair prims — all flat materials, so no texture sampling lost)
- Unparsed siblings in repo: `model.glb` 5,648,588 B · `model-rigged.glb` 14,674,608 B · `model-rerig.glb` 2,570,352 B — `model.glb` is a candidate closest-to-blend export for the fidelity lane.

### Gap list (vs source .blend)
1. **Rig is not the blend's IK rig** — GLB is an 11-skin × 73-joint split-bone gamerig. Blend bone count/names unknown until `mirkoIK.blend` is opened; delta unquantifiable from GLB alone.
2. **0 morphs** — any blend shape keys are lost.
3. **Eyes / Eyeshadow / Hair still flat** (no texture in GLB, no named map in intake). Fix lane closed this as "flat by source design" with the blend read still pending — fidelity lane must confirm in the .blend.
4. **Unused intake art:** `Mirko body unshaded.png` embedded in neither GLB.
5. **No normal maps anywhere; no MR maps except hero-suit** (post-#1529); blanket roughness 0.8 / metallic 0 elsewhere.
6. Only animation is a CMU mocap test clip, not source-blend actions.
7. Mesh names are SFM/DMX remnants (`puppershupper_…`, `Cube_001`, `Plane`, `Torus`) — parts labelling needs the blend's object names.
8. Nothing to rebuild from locally: no .blend, only 3/10 textures extracted. Pull blend + full `textures/` from repo first.

---

## Chatur = Rahkasa

### Source located
- **.blend (repo only):** `roster/rahkasa/intake/RahkasaV1.1.blend` — **11,459,182 B, blob `6427d66ea600…`**. Sole intake file — **no separate texture PNGs filed**; any further maps must be packed inside the blend. Provenance: SmutBase download sha256 prefix `85610cee…`, 11.5 MB.
- No local .blend, no local intake textures.

### Orig GLB = shipped GLB (byte-identical)
`~/workspace/_smutbase6-fix-20261102/models/orig/rahkasa-chatur.glb` and serve copy `serve/roster/rahkasa/attires/attire1/model-rigged-textured.glb` — both **2,361,776 B, sha256 `a75649cab620bd15538e1188626f90ec311de36113c1075da73f1ff9d477d0b4`**
Repo: `roster/rahkasa/attires/attire1/model-rigged-textured.glb`, blob `a23c514f68…`, **unchanged — no PR in the fix lane**.

- 1 mesh (`ReVAmped_body_base_female_standard`) / 4 prims / **176,555 verts / 58,911 tris** · 54 nodes
- **1 skin, 52 joints, named `WH_Skeleton`** (standard Hips/Spine/finger set — no breast, HeadTop, or extra chains)
- **3 materials, 3/3 with baseColor texture** · 5 textures / 5 images: Body base+emissive, Head base+emissive, Eyes base · 0 normal / 0 MR / 0 occlusion; blanket roughness 0.8 / metallic 0
- **0 animations · 0 morphs** · all 4 prims carry POSITION/NORMAL/TEXCOORD_0/JOINTS_0/WEIGHTS_0
- Unparsed siblings in repo: `model-rigged.glb` 9,817,884 B · `model.glb` 3,706,016 B.

### "Cleanest of the six" — verified or refuted?
**Verified at shipped-GLB level:**
- Lane GLB audit (`audit-2.json`): seams >0.1 = **0**, unweighted verts **0**, bad weight sums **0**, 3/3 materials textured.
- Repo baseline audit: verdict **OK** — 176,555 seam copies, **0 disagreeing** (max L1 0.0), face Head 98%, chin 73%, upper-arm trunk 0%/0%, height 1.8 m. Single-skin file, so this audit is trustworthy for Rahkasa.
- Own parse (2026-11-04) agrees on every count above; orig and shipped are the same bytes (sha256 match), consistent with "untouched" in the checkpoint.
- Moves planner (handoff): chatur 0/214 no-clip. (Bank state is separate: pose-only, no bank; True Ogre has no TTT2 moveset file.)

**Refuted as a fidelity claim** — "no defects in the converted GLB" ≠ "looks like the .blend":

### Gap list (vs source .blend)
1. **Template rig, not source rig:** 52-joint `WH_Skeleton` vs the unknown rig inside the 11.46 MB blend (4.85× the GLB's size — the GLB cannot hold everything the blend holds).
2. **⚠️ Four-arm question (flagged, not proven):** intake canon describes Rahkasa as a **four-armed** female spirit body; the shipped skeleton has exactly one Left + one Right arm chain and one collapsed generic-named mesh. If the blend is four-armed, an arm pair is lost. Settle only by opening the .blend.
3. **Mesh collapse:** 1 mesh / 4 prims / 3 materials — separate blend objects (clothing/accessories/parts) are merged away; no parts separation survives.
4. **0 morphs, 0 animations** in the GLB.
5. **PBR thin:** only baseColor + emissive survive; no normal/MR/AO maps, blanket factors.
6. Nothing to rebuild from locally: pull `RahkasaV1.1.blend` from repo first.

---

## Headline numbers

|  | Tobi / Mirko | Chatur / Rahkasa |
|---|---|---|
| Source .blend | ✅ repo only, 6,310,244 B | ✅ repo only, 11,459,182 B |
| Orig GLB | 4,119,856 B · 73 joints ×11 skins · 89,116 tris · 6 img | 2,361,776 B · 52 joints ×1 skin · 58,911 tris · 5 img |
| Shipped GLB | 4,823,088 B · same geometry/rig · **8 img** · seams 0 | **identical bytes** (sha256 match) · seams 0 · 3/3 textured |
| Morphs / anims (shipped) | 0 / 1 (CMU boxing) | 0 / 0 |
| Fidelity gap | non-source 73-joint rig, flat Eyes/Hair, no normals | template `WH_Skeleton`, collapsed mesh, four-arm question |

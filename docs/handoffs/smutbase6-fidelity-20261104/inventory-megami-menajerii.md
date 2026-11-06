# SmutBase 6 Fidelity Inventory — Megami (Parvati) & Menajerii (Vixen)

Generated 2026-11-04 · Read-only inventory (GLB JSON-chunk parsing + sha256, targeted `*.blend` finds, `gh api` repo listings). Full machine-readable data: `inventory-megami-menajerii.json` in this folder.

## Bottom line up front

- **No `.blend` exists for either character** in `~/workspace/_smutbase6-fix-20261102`, in `~/workspace/model-intake`, or in the repo (intake inventory, verified 2026-11-02 against live repo trees, records both as *"intake .blend not in repo (source held outside)"*). The fidelity bar — "exactly like the source `.blend` opened in Blender" — has **no `.blend` to open** for these two. Best surviving source for both is a Blender-exported GLB (generator `Khronos glTF Blender I/O v4.0.44`, from GitHub release `megami-menajerii-smutbase-20261023`).
- **Neither source GLB contains a rig**: 0 skins / 0 joints / 0 animations in both `parvati-full.glb` and `vixen-full.glb`. They are static DAZ exports. The 52-joint skeleton in every shipped file comes from the 2026-10-23 template conversion, not from the source files.
- Both shipped files are **heavily decimated** vs source: Parvati −73.0% tris, Vixen −59.1% tris.

---

## MEGAMI = Parvati (Jun Kazama)

### Source located

| File | Bytes | sha256 (head) | Meshes | Prims | Verts | Tris | Mats | Tex | Images | Skins |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 99,973,212 | `0c71536e4db704ea…` | 25 | 71 | 718,178 | 1,154,840 | 69 | 96 | 66 | 0 |
| 191,604,148 | `0165575bdf3000c1…` | 25 | 71 | 718,178 | 1,154,840 | 69 | 96 | 66 | 0 |
| 23,541,928 | `7907f8d39b157a74…` | 25 | 71 | 718,178 | 1,154,840 | 69 | 66 | 66 | 0 |
| 30,860,048 | `cb101ed1a79e70c3…` | 24 | 70 | 200,229 | 311,325 | 68 | 95 | 65 | 1 |

- Primary: `/home/hatch/workspace/_smutbase6-fix-20261102/models/src/parvati-full.glb` — full sha256 in JSON.
- Release copy: `/home/hatch/workspace/_smutbase6-fix-20261102/megami-src/parvati-full.glb` (191,604,148 B).
- Sibling: `/home/hatch/workspace/_smutbase6-fix-20261102/megami-src/model-sibling.glb` (23,541,928 B, glTF-Transform meshopt re-encode).
- All three variants carry **identical counts** (25 meshes / 71 prims / 69 mats / 66 images / 1,154,840 tris / 718,178 verts / 0 skins) — they differ only in encoding, never byte-identical.
- `megami-src/parvati-full-json.json` is a **0-byte placeholder** — not a JSON dump. The real extracted JSON is `work/full/parvati-full.json` (3.5 MB).
- **`.blend`: NOT FOUND** (search record in JSON).

### Source headline

- Bones/joints: **none** (0 skins). Meshes 25, prims 71, **1,154,840 tris, 718,178 verts**, materials 69, textures 96, images 66 (17,982,544 B of image data), animations 0.
- TEXCOORD_0 on 70/71 prims (only `RenderStrandHairGeom` lacks it); JOINTS_0 on 0/71.

### Known traits — VERIFIED from the GLB data

1. **Outfit materials empty `pbrMetallicRoughness {}` — VERIFIED, scoped.** Exactly **7 materials** are literally `{}` with no texture slot of any kind: `24_Material43_0.25_0_0`, `24_Material45_0.25_0_0`, `24_Material44_0.25_0_0`, `24_+headgear.Material39_1_0_0`, `24_Material42_0.25_0_0`, `25_Material40_1_0_0`, `25_Material41_1_0_0`. They sit on source meshes **3, 4, 5, 6, 7, 22** — exactly the meshes the no-outfit variant excludes. **0 of the 66 source images are referenced by them.**
   - ⚠️ Scope correction: the *other* garments **do** have real textures in-source — top (`V2.BLK.*`), garter/top/bottom/bows/socks (`XF_Roses_Bows_*`), bodystocking, choker, shoes (`Tracy_tx_*`, `Kayla HH`). "Outfit textureless" is true only of the 24_*/25_* set.
2. **8 hair-strand materials with no texture anywhere — VERIFIED.** Mesh 23 *Flora Hair Genesis 8 Female*: `Bangs1-1, Bangs2-1, Front1-1, SideBangs1-1, Back1-2, SideBangs2-1, Front2-1, Back2-2` — entire pbr is `{metallicFactor: 0.5, roughnessFactor: 0.5}`, no baseColorTexture **and no baseColorFactor** (renders default white = the recorded silver-white trait). Plus strand material `Torso-6` also untextured; `Cap-1` *is* textured.
3. **Counts CONFIRMED:** 66 images, 69 materials, **35 with baseColorTexture / 34 without** (7 outfit-empty + 8 hair + Torso-6 + EyeMoisture×2 + Cornea (normal only) + brow Layer1/Layer2 flat + PANTIES (normal only) + 10 shoe/metal flat-factor + Material.001).

### Shipped headline

| File (repo path) | Bytes | Meshes | Prims | Verts | Tris | Mats | Images | Skins×Joints |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `roster/parvati/attires/attire1/model-rigged.glb` (#1528 pack) | 19,511,432 | 24 | 58 | 200,219 | 311,325 | 52 | 65 | 1×52 |
| `roster/parvati/attires/attire1/model-rigged-nooutfit.glb` (#1549) | 19,510,660 | 18 | 52 | 187,174 | 297,167 | 52 | 65 | 1×52 |
| orig conversion `models/orig/parvati-megami.glb` | 30,860,048 | 24 | 70 | 200,229 | 311,325 | 68 | 65 | 1×52 |

Local serve copies match the task-supplied sizes exactly; `work/parvati-packed.glb` is byte-identical to the shipped packed file. Git blob for packed: `b79bda9260` (per task/PR #1528). Joint names (52, DAZ-style Hips→Head→fingers→toes) are listed in the JSON.

### Gap list (Megami)

- NO .blend in holdings (see blend_search) - fidelity rebuild cannot open the original Blender file; best source is the Blender-exported GLB.
- NO RIG IN SOURCE: source GLB has 0 skins/0 joints. Any fidelity rebuild must rig from scratch or reuse the shipped 52-joint template rig - the order's 'full rigs that come with their own files' cannot be satisfied from this source because the file carries none.
- GEOMETRY DECIMATION: source 1,154,840 tris / 718,178 verts -> shipped 311,325 tris / 200,219 verts = -843,515 tris (-73.0%), -517,949 verts. Shipped is a heavily decimated re-export, not the source geometry.
- MESH LOSS/MERGE: source 25 meshes / 71 prims -> shipped 24 meshes / 58 prims. Body mesh geometry-5's 16 prims merged and GP_Torso/GP_Torso_Back prims dropped in shipped mesh 19 (14 prims); Flora Hair's 9 prims collapsed to 2 prims in shipped mesh 13 (Cap-1 + Bangs1-1 only as separate prims - the other 7 hair-strand materials are GONE from the shipped material list, folded into merged prims).
- MATERIAL LOSS: source 69 materials -> orig conversion 68 -> shipped 52 (gltfpack duplicate-merge). Shipped materials without baseColorTexture: 20 (vs 34 in source; several source flat materials were merged into the repeated '24_Material43_0.25_0_0' prims).
- IMAGE LOSS: source 66 images -> shipped 65. Image byte total is unchanged in orig (17,945,530 B vs 17,982,544 B source - small delta); the packed file preserves the orig's 65-image set (PR #1528 verified sha256 sets identical between orig and packed).
- TEXCOORD LOSS IN PACK: source 70/71 prims have TEXCOORD_0; shipped packed file has TEXCOORD_0 on only ~35/58 prims (gltfpack dropped UVs on prims whose materials have no texture - acceptable for those materials, but the UV data itself is lost for a future re-texture).
- OUTFIT: the 7 empty-pbr outfit materials / 6 meshes can never be textured faithfully - there is no texture for them anywhere in the source (0/66 images). No-outfit variant (297,167 tris) is the honest playable form.
- HAIR: 8 strand materials have no texture/color in source - silver-white flat is the faithful ceiling from this source.
- megami-src/parvati-full-json.json is a 0-byte placeholder - do not cite it as the source JSON; use work/full/parvati-full.json.

---

## MENAJERII = Vixen (Roger Jr.)

### Source located

| File | Bytes | sha256 (head) | Meshes | Prims | Verts | Tris | Mats | Tex | Images | Skins |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 100,078,094 | `636958185cad8370…` | 29 | 72 | 532,326 | 986,895 | 69 | 0 | 0 | 0 |
| 13,896,480 | `e06f7a811ce691ea…` | 28 | 69 | 230,694 | 403,383 | 69 | 0 | 0 | 1 |
| 41,676,940 | `9f4915998bf1deb9…` | 29 | 72 | 456,073 | 854,295 | 18 | 2 | 2 | 0 |

- Primary: `/home/hatch/workspace/_smutbase6-fix-20261102/models/src/vixen-full.glb` — full sha256 in JSON.
- **Sibling `model.glb` LOCATED (local form):** `work/vixen-model-src.glb` = `visual-gate/models/vixen-model-src.glb` (byte-identical, 41,676,940 B, sha256 `9f4915998bf1deb9…`). This is the local download of repo sibling `roster/vixen/attires/attire1/model.glb` that the #1541 palette bake reads ("her own palette set from model.glb", `work/build_vixen_textured.py`). Contents: 29 meshes (incl. Plane), 72 prims, **18 materials `PaletteMaterial001–018`, 2 images** (`PaletteBaseColor` 200 B + `PaletteMetallicRoughness` 412 B, webp), 0 skins, **854,295 tris / 456,073 verts**, TEXCOORD_0 on all 72 prims (flat palette UVs).
- `work/vixen-sib-*.glb` (×2) are **0-byte failed-download placeholders** — not the sibling.
- **`.blend`: NOT FOUND** (search record in JSON).

### Source headline

- Bones/joints: **none** (0 skins). Meshes 29 (incl. material-less `Plane`, mesh 28), prims 72, **986,895 tris, 532,326 verts**, materials 69, **textures 0, images 0**, animations 0.
- **All 69 DAZ materials lack baseColorTexture**; 4 are empty `pbr {}` (`DM04:lambert1SG-1`, `leather-1`, `straps_-_neck-1`, `ring_neck-1`). Real DAZ UVs exist (TEXCOORD_0 on 69/72 prims; the 3 strand-hair prims lack it) but **no image data was ever in this file**.

### Shipped headline

| File (repo path) | Bytes | Meshes | Prims | Verts | Tris | Mats | Images | Skins×Joints |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `roster/vixen/attires/attire1/model-rigged-noplane.glb` (#1541) | 3,194,880 | 28 | 69 | 230,694 | 403,383 | 18 palette | 2 | **28×52** |
| pre-bake intermediate `work/vixen-final.glb` | 3,164,796 | 28 | 69 | 230,694 | 403,383 | 69 DAZ | 0 | 28×52 |
| orig conversion `models/orig/vixen-menajerii.glb` | 13,896,480 | 28 | 69 | 230,694 | 403,383 | 69 DAZ | 0 | 1×52 |

Local serve copy matches the task-supplied 3,194,880 B exactly; git blob `0108a67568` (per task/PR #1541). Parse confirms 69/69 prims palette-baked. Note the shipped file's **28 skins** (one per mesh, each the same 52 joints) vs orig's single skin.

### Decimation

- Source **986,895 tris → shipped 403,383 tris (−583,512, −59.1%)**; verts 532,326 → 230,694 (−56.7%).
- Even the palette sibling (854,295 tris) is reduced vs the intake master, though its 29-mesh/72-prim structure matches the master exactly.

### Gap list (Menajerii)

- NO .blend in holdings (see blend_search) - same blocker as Megami.
- NO RIG IN SOURCE: 0 skins/0 joints in vixen-full.glb. Shipped 52-joint rig is the template conversion, not a source rig.
- NO TEXTURES IN SOURCE GLB: vixen-full.glb embeds 0 images / 0 textures and all 69 DAZ materials have no baseColorTexture (4 are empty pbr {}: DM04:lambert1SG-1, leather-1, straps_-_neck-1, ring_neck-1). Unlike Parvati, there are no DAZ texture maps in the intake master at all - the ONLY texture data in the holdings for Vixen is the sibling model.glb's 2-image MPFB palette (612 B total, near-monochrome white/gray/black swatches). A photoreal DAZ-texture fidelity rebuild is IMPOSSIBLE from current holdings; the palette bake is the ceiling unless the original DAZ texture folders are located outside these holdings.
- GEOMETRY DECIMATION: 986,895 -> 403,383 tris (-583,512, -59.1%); 532,326 -> 230,694 verts (-56.7%). The jagged dark shard pattern on arms/legs recorded in PR #1541 is a property of this decimated shell geometry (inner garment shells breach outer shells) - it does not exist in the un-decimated sibling (854,295 tris, renders smooth).
- UV STRIP + FLAT-UV SUBSTITUTE: orig conversion stripped TEXCOORD_0 from all 69 prims despite the source carrying real DAZ UVs on 69/72 prims. The shipped palette bake restored only a single CONSTANT UV point per prim (median palette UV from model.glb) - the source's real per-vertex UVs are still not in the shipped file.
- PLANE REMOVED: source mesh 28 'Plane' dropped in orig + shipped (intentional '-noplane').
- BODY PRIM MERGE: source body mesh geometry-1 has 18 prims (Torso-3.001 and Arms-4.001 each appear twice); shipped has 16 (duplicates merged, same palette slot on both occurrences per PR #1541 verification).
- SKIN FRAGMENTATION: shipped file carries 28 skins (one per mesh, each 52 joints) vs orig's single skin - structurally heavier/odd for engines expecting one skeleton, though joints are identical.
- MATERIAL IDENTITY REPLACED: shipped materials are the 18 MPFB palette slots, not the 69 DAZ materials of the source. Palette assignment was proven by DAZ-name chain via the intake master (PR #1541), but per-material DAZ properties (transmission/clearcoat/specular factors of the originals) survive only insofar as the palette materials carry their own extension blocks.

---

## Repo check

`gh api` listings (repo `mhvnsnt/western-heart`, returned after slow/flaky calls):

- `roster/parvati/` and `roster/vixen/` roots: `ATTIRE-SLOTS.md`, `CANON.md`, `PARTS.md`, `anatomy/`, `attires/`, `intake/` (+ `parvati.json`) — no `.blend`.
- **`roster/parvati/intake/` = ONLY `README.md`** (1,210 B, blob `fee76530c2e8e9e480f00348d8a83739bf4d3fa1`) — definitive.
- **`roster/vixen/intake/` = ONLY `README.md`** (1,603 B) — definitive.
- `roster/vixen/attires/attire1/`: `model-rigged-noplane.glb` 3,194,880 B blob `0108a675680edb38420025f66dd3e00ff4375ef5` · `model-rigged.glb` 14,653,404 B blob `b5388913e56ed85d00c1576394bad422c8e09ffc` · **`model.glb` 41,676,940 B blob `ca7a656f93713c6471a9476b3de4415c0a478712`** — exactly the size of local `vixen-model-src.glb`, confirming it as the palette sibling. The zero-byte local `vixen-sib-<sha>.glb` files are named by these blob SHAs (failed download attempts).
- `roster/parvati/attires/attire1/` listing failed twice with stream-CANCEL errors and was not re-listed; Parvati shipped sizes are verified from local serve copies + PR #1528/#1549 records.

This directly confirms `~/workspace/model-intake/INVENTORY.md` (2026-11-02): both intake `.blend`s = **"not in repo (source held outside)"**.

## What a fidelity rebuild can and cannot use

- **Can use:** the two `*-full.glb` masters (full source geometry + Parvati's full DAZ texture set), Vixen's palette sibling `model.glb`, the extracted JSON chunks in `work/full/`.
- **Cannot conjure:** either `.blend`, either character's original DAZ rig (the GLBs carry none), Parvati's outfit textures (never existed in-source), Vixen's DAZ textures (never in the intake master — palette is the ceiling in current holdings).

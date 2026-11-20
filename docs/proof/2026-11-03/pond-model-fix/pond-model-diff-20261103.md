# Pond (Tsuyu Asui) — Model Diff: Clean Source vs Shipped

**Date:** 2026-11-03 · **Lane:** SMUTBASE (mhvnsnt/western-heart), Pond MODEL DIFF sub-job
**Type:** Investigation ONLY. No GLB was edited, committed, or pushed.
**Owner order being answered:** shipped Pond rejected — textures, eyes, face wrong; crotch reads male/futa. Ground truth = the clean source opened fresh. The earlier visual gate claimed "pelvis wedge + speckled belt are inherited source traits (A/B proven)"; the owner overruled that with his own eyes. This report establishes what is *actually* different, with numbers.

---

## 0. Verdict up front

1. **Between the designated clean source GLB and the shipped GLB, the geometry is byte-identical.** Every primitive in both files has identical POSITION, index, and NORMAL arrays (max position delta = 0.00e+00 on all 15 primitives, verified on md5-checked decodes). Nodes, skins, and inverse bind matrices are also identical. **Nothing about the crotch, eyes, face, or hair was changed by the SmutBase-6 fix lane** — except skin weights on 240 vertices of the small Mask primitive (seam unification) and the texture additions in §2.
2. **The defects the owner sees are baked into BOTH GLBs** — including the file this lane calls "clean source". That file is **not** the fresh SmutBase download. It is the 2026-10-23 rig conversion (52-joint `WH_Skeleton`, glTF-Transform re-encode). The visual gate's A/B compared the shipped file against *its own ancestor conversion*, so "inherited, A/B proven" was circular.
3. **The true ground truth still exists and is named in the lane's own intake record:** `Tsuyu_Asui_IK_V1.1.zip` → IK `.blend` + `textures/`, in-repo at `roster/tsuyu-asui/intake/` (see §7). It is **not on local disk** anywhere on this VM (full-workspace find, 2026-11-03). Every fix in §8 is sourced from that intake or from Pond's own GLB/intake files — nothing fabricated.
4. **The crotch object is real, measured, and is the single most forward-protruding part of the entire model** in both files: mesh `Mesh0000_004`, material literally named **`penis`**, 30,708 verts, reaching **z = +0.427 m** at crotch height — 28.7 cm in front of the suit surface at the same height and 13 cm in front of her breasts. Details in §4.

---

## 1. Files and identity checks

| File | Size | MD5 | Role |
|---|---|---|---|
| `~/workspace/_smutbase6-fix-20261102/models/orig/tsuyu-pond.glb` | 7,053,488 B | `3e1124a3d4171a6b0adf5d38a112fe82` | designated CLEAN SOURCE |
| `~/workspace/_smutbase6-fix-20261102/visual-gate/models/orig-pond.glb` | — | `3e1124a3d4171a6b0adf5d38a112fe82` | gate's "orig" — **byte-identical copy of the source above** |
| `~/workspace/_smutbase6-fix-20261102/visual-gate/models/pond-tsuyu.glb` | 9,467,192 B | `28cf3cb70538a738536818de0382bb09` | SHIPPED |
| `~/workspace/_smutbase-t7-banks-20261103/serve2/roster/tsuyu-asui/attires/attire1/model-rigged-textured.glb` | — | `28cf3cb70538a738536818de0382bb09` | game/T7-lane copy — **byte-identical to shipped** |
| `~/workspace/_smutbase6-fix-20261102/work/tsuyu-encoded.glb`, `gl-scan/tsuyu-encoded.glb` | 9,467,192 B | `28cf3cb70538a738536818de0382bb09` | also byte-identical to shipped |

**Lineage chain (md5-verified this run):**

- Decoding the source GLB with the lane's own codec (`gltf_codec.mjs decode`, glTF-Transform 4.1.1) produces a file **md5-identical to `work/tsuyu-plain.glb`** (`31af36782c68bf5ba10d6608b2d21d96`). So `tsuyu-plain.glb` *is* the decoded source.
- Decoding the shipped GLB produces a 22,485,060 B file, the same size as `work/tsuyu-fixed.glb`.
- Chain: source → `tsuyu-plain` (decode) → `tsuyu-seams` (unify_seams.py) → `tsuyu-fixed` (+2 roughness maps via glb_tex.py) → `tsuyu-encoded` = shipped.

**Method:** both GLBs carry `EXT_meshopt_compression` + `KHR_mesh_quantization`. All geometry numbers below come from fresh decodes of the two files above (not from the intermediates), cross-checked three ways: (a) accessor `count`/`min`/`max` in the encoded JSON, (b) a numpy per-part skinning implementation (three.js semantics: each mesh skinned by its own skin's `bindWorld × IBM`), brute-force-verified on individual vertices, (c) Blender 5.2.3 headless inspection — which agrees with (a) and (b) on all 9 meshes (§6).

**Totals, both files:** 9 meshes, 15 primitives, 62 nodes, 9 materials, 9 skins × 52 joints, 0 animations, 0 morph targets, **295,975 verts, 98,741 tris**, skinned height **1.800 m**, Hips joint at y = 0.950 m.

---

## 2. The complete source → shipped diff (everything that actually changed)

| # | Change | Detail |
|---|---|---|
| 1 | **+2 images / +2 textures / +1 sampler** | `suit_MR.png` (2,048×2,048, 1,505,138 B) and `boots_MR.png` (2,048×2,048, 996,844 B) appended; wired as `metallicRoughnessTexture` on materials `suit` and `boots`. Packed from Pond's own intake `suit_Roughness.png` / `boots_Roughness.png` (`work/tsuyu-intake/`, the only 4 files in that intake copy: suit/boots Base_color + Roughness). |
| 2 | **roughnessFactor removed on suit + boots** | Was 0.8 (blanket stamp on all 9 materials); with a real MR map the factor defaults to 1.0. All other materials still carry 0.8 in both files. Visible effect: shipped suit renders glossier in the gate renders. This is a *correct* change, from her own intake maps. |
| 3 | **Texture indices remapped — correctly** | Inserting the MR images shifted texture indices. Verified hash-by-hash: all 5 base-color images are **byte-identical** in both files (sha256 prefixes: skin `a1d48bb786eaf1a0`, face `70ee32e081b41ce5`, suit `b4a0009a0207addf`, penis `4d843be411203646`, boots `ac0f46f61d34298b`), and every material still points at its own image. **No base texture was swapped, lost, or resized.** |
| 4 | **TEXCOORD_0 dropped on 6 primitives (shipped-only regression)** | The encode step's `prune()` removed UVs from every primitive whose material has no texture: mesh0 prim1 (`eyes`), mesh5 (Googles), mesh6 (hair), mesh7 prim0+prim1 (Belt), mesh8 (Mask). Source has these UVs (atlas-tile offsets, §5); shipped does not. Cosmetically inert today (those materials are flat color), but **any future texture wiring for eyes/hair/googles/belt is blocked until the UVs are restored from source.** |
| 5 | **Skin weights/joints changed on exactly one primitive** | Mesh8 (Mask) prim0: 240 of 540 verts have rewritten JOINTS_0/WEIGHTS_0 (seam unification). Every other primitive: weights and joints byte-identical. Positions/normals/indices: byte-identical on **all 15** primitives. |
| 6 | **Container bookkeeping** | Generator string glTF-Transform v4.5.1 (source) → v4.1.1 (shipped); accessors 99 → 83, bufferViews 83 → 79 (prune/merge during re-encode). Nodes array fully equal; all 9 skins' IBMs equal (max delta 0.0). |

**That is the entire diff.** Anything visible in the shipped model that is not on this list came from the source GLB itself.

---

## 3. Per-mesh table (skinned bind pose, three.js semantics — identical in BOTH files)

Skinned bbox = per-part skinning (each mesh with its own skin), metres, x = left/right, y = up, z = forward. Vert/tris counts identical in both files; bboxes identical to 4 decimal places in both files.

| Mesh | Node name (abbrev.) | Prim | Material | Verts | Tris | BBox min (x,y,z) | BBox max (x,y,z) |
|---|---|---|---|---|---|---|---|
| 0 | Tsuyu (body) | 0 | `Material` (Tsuyu_skin.png) | 94,830 | 31,616 | (−0.776, 0.000, −0.080) | (0.776, 1.394, 0.295) |
| 0 | Tsuyu | 1 | **`eyes` (flat, no texture)** | 1,284 | 428 | (−0.076, 1.458, 0.125) | (0.076, 1.530, 0.149) |
| 0 | Tsuyu | 2 | `skin_face` (skin_face.png) | 14,734 | 4,914 | (−0.141, 1.376, −0.063) | (0.141, 1.662, 0.179) |
| 0 | Tsuyu | 3 | `Material` (Tsuyu_skin.png) | 13,444 | 4,484 | (−0.046, 0.783, 0.020) | (0.046, 0.894, 0.148) |
| 1 | Holo_001 (suit) | 0 | `suit` | 73,304 | 24,450 | (−0.530, 0.118, −0.083) | (0.530, 1.387, 0.297) |
| 1 | Holo_001 | 1 | `suit` | 480 | 160 | (−0.009, 0.791, 0.035) | (0.009, 0.821, 0.137) |
| 2 | **Mesh0000_004** | 0 | **`penis` (penis.png)** | **30,708** | **10,236** | **(−0.082, 0.667, 0.099)** | **(0.082, 0.882, 0.427)** |
| 3 | Mesh0000_003 | 0 | `boots` | 24,852 | 8,284 | (−0.083, 0.664, 0.091) | (0.083, 0.841, 0.241) |
| 4 | Plane_003 | 0 | `suit` | 24,132 | 8,080 | (−0.780, 1.210, −0.042) | (0.780, 1.339, 0.095) |
| 4 | Plane_003 | 1 | `suit` | 48 | 16 | (−0.689, 1.210, 0.085) | (−0.669, 1.226, 0.095) |
| 5 | …SFM_mdl_Googles_Body | 0 | `googles_mask` (flat) | 6,864 | 2,288 | (−0.171, 1.631, −0.117) | (0.171, 1.800, 0.216) |
| 6 | …SFM_mdl_hair_BodyHai | 0 | `hair` (flat) | 6,087 | 2,029 | (−0.251, 0.784, −0.311) | (0.251, 1.692, 0.182) |
| 7 | …SFM_mdl_Belt_Body_be | 0 | `outfit` (flat) | 4,656 | 1,552 | (−0.130, 1.018, 0.002) | (0.130, 1.094, 0.188) |
| 7 | …SFM_mdl_Belt_Body_be | 1 | `outfit` (flat) | 12 | 4 | (−0.116, 1.054, 0.062) | (−0.010, 1.080, 0.186) |
| 8 | …SFM_mdl_Mask_Body_ma | 0 | `googles_mask` (flat) | 540 | 180 | (−0.102, 1.441, 0.048) | (0.102, 1.513, 0.175) |

Notes on names: only meshes 0, 1, 5–8 carry meaningful names. Meshes 2/3 (`Mesh0000_004`/`Mesh0000_003`) and mesh 4 (`Plane_003`) are converter leftovers — no descriptive name survives for them in either GLB. All geometry is non-welded triangle soup (index count ≈ vertex count on every primitive), which is why seam-copy counts are high on this model generally.

---

## 4. Pelvis / crotch focus

Pelvis band used: Hips y = 0.950 m ± 15% of height (1.800 m) → **y ∈ [0.680, 1.220]**, centre column |x| < 0.06 m for the slice profile.

### 4.1 The protrusion: mesh 2, `Mesh0000_004`, material `penis`

| Measurement | Value |
|---|---|
| Verts / tris | 30,708 / 10,236 (10.4% of the whole model's verts) |
| Skinned bbox | x −0.082…0.082 (16.4 cm wide), y 0.667…0.882 (21.5 cm), **z +0.099…+0.427 (32.8 cm deep)** |
| Centroid | (−0.000, 0.804, **+0.248**) — the mass sits *in front of* the pelvis, not inside it |
| Forward-most vertex | (0.005, 0.836, **0.427**) |
| Verts below Hips−0.10 m (y < 0.85) | 23,942 / 30,708 (78%) |
| Dominant joints (by max weight) | Hips 24,687 · RightLeg 2,302 · LeftLeg 2,156 · RightUpLeg 806 · LeftUpLeg 757 — rigid with the pelvis, it will swing with the hips in animation |
| Texture | `penis.png` (2,048×2,048, 119,133 B) — a near-flat skin-pink sheet (full-image mean RGB ≈ (233, 169, 149)) with a darker pink region; the cone reads brown-pink in the gate renders under the viewer's shading. The geometry, not the texture, is what makes it read as a foreign object: a smooth 33 cm-deep cone where the suit's own crotch surface sits at z ≈ 0.145. |
| Present in source? | **Yes — byte-identical geometry, material, and texture in the source GLB.** Not added, duplicated, displaced, or rescaled by rigging/merge in this lane. |

**Front-profile slices (centre column, max z per 5 cm y-slice, source = shipped):**

| y slice | body skin | suit | mesh3 (`boots`) | **mesh2 (`penis`)** |
|---|---|---|---|---|
| 0.65–0.70 | 0.134 | 0.136 | 0.232 | 0.195 |
| 0.70–0.75 | 0.139 | 0.141 | 0.241 | 0.201 |
| 0.75–0.80 | 0.137 | 0.139 | 0.231 | **0.395** |
| 0.80–0.85 | 0.137 | 0.145 | 0.217 | **0.427** |
| 0.85–0.90 | 0.163 | 0.165 | — | **0.423** |
| 0.90–0.95 | 0.176 | 0.179 | — | — |

Read: at crotch height the body's own front surface is at z ≈ 0.14–0.15 and the suit covers it at z ≈ 0.145–0.165. Mesh2 ignores both and extends to **z = 0.427 — 28.7 cm proud of the suit, and further forward than the breasts (z max 0.297)**. It is the forward-most point of the entire model (whole-model z max = 0.4272, set by this mesh alone). In the gate's q34 renders (`visual-gate/shots2/proof-pond-q34-20261103.png` and `proof-orig-pond-q34-20261103.png` — visually identical in this region) it reads exactly as measured: a horizontal cone/wedge sticking out of the crotch. **The owner's reading is correct, and it is not a rendering artefact.**

### 4.2 The second pelvis mass: mesh 3, `Mesh0000_003`, material `boots`

- 24,852 verts / 8,284 tris; skinned bbox x ±0.083, y 0.664…0.841, z +0.091…+0.241. A **single central mass** (x-histogram is full across the centre — no left/right split), sitting *between* the suit front (0.145) and the mesh-2 cone (0.427), i.e. the three shells **intersect** in the band z 0.09…0.43 at the crotch (body, suit, mesh3, mesh2 all occupy overlapping space — z-fighting territory wherever surfaces cross, e.g. mesh3's front at 0.241 vs suit front 0.145 in y 0.66–0.84).
- It wears the `boots` material, but its UVs cover only a tiny sliver of `boots_Base_color.png` (u 0.71…0.73, v 0.68…0.69), so it samples one solid green patch (sampled RGB = (30, 154, 45) at effectively every vertex) — it does not wear the boots artwork in any meaningful sense.
- **No mesh lands at the feet** under game (three.js) skinning except the body and suit: Pond renders barefoot in the gate proofs, and a boots-textured mass sits at her pelvis instead. Whatever mesh3 was in the source .blend (intake lists a separate `OBboots` object *and* a central `OBBulge` crotch cover — §7), in the GLB conversion it does not end up on her feet.
- The body's own crotch geometry also exists and is correctly placed: mesh0 prim3 (`Material`/skin texture, 13,444 verts, x ±0.046, y 0.783…0.894, z front 0.148 ≈ suit front 0.145 — a flush skin patch under the suit, UV region u 0.003…0.099 / v 0.295…0.403 of `Tsuyu_skin.png`).

### 4.3 What did *not* happen at the pelvis

- No mesh exists in shipped that is absent in source (mesh/prim counts identical, all arrays identical).
- No source pelvis mesh is displaced or rescaled in shipped (max position delta 0.0 on mesh2, mesh3, mesh0 prim3, suit).
- The overlap of shells at the crotch is present in the source GLB in the same measure.
- **Conclusion for §4:** the fix lane neither caused nor worsened the crotch. The cone and the stacked pelvis shells were baked in at the earlier blend→GLB conversion that produced the file now labelled "orig". Whether the cone sits this way in the true source .blend is the one question this GLB pair cannot answer — see §7.

---

## 5. Eyes / face / head focus

| Part | Mesh/prim | Material in GLB | Texture | Numbers (both files unless noted) |
|---|---|---|---|---|
| Face/head skin | mesh0 prim2 | `skin_face` | `skin_face.png` 1,024×1,024 (365,230 B, byte-identical both files) | 14,734 verts; bbox x ±0.141, y 1.376…1.662, z −0.063…0.179. The texture is a painted cartoon face sheet: big black oval eyes + mouth painted on skin, dark-green hair region at the top edge. |
| Eye patches | mesh0 prim1 | **`eyes` — NO texture, flat `baseColorFactor` [0.5273, 0.7664, 0.7745] (pale cyan)** | none in either file | 1,284 verts; two patches, bbox x ±0.076, y 1.458…1.530, z 0.125…0.149 — floating just in front of the face surface. In the gate renders these read as the pale-cyan flower/starburst blobs over her face: faceted flat-colour geometry with no iris/pupil artwork anywhere in the file. |
| Hair | mesh6 | **`hair` — NO texture, flat [0.5319, 0.6440, 0.5805] (pale grey-green)** | none in either file | 6,087 verts; y 0.784…1.692, z −0.311…0.182 (long back fall, correct placement). The flat factor is why her hair renders washed-out pale instead of dark green. No hair image exists in either GLB. |
| Googles | mesh5 | `googles_mask` — NO texture, flat [0.9538, 0.6731, 0.7567] (pink) | none | 6,864 verts; y 1.631…1.800 (top of head), z −0.117…0.216. |
| Mask (chin strap) | mesh8 | `googles_mask` — same flat pink | none | 540 verts; y 1.441…1.513, z 0.048…0.175. This is the strap across the mouth/chin that reads dark in the renders (flat colour + shadowing); geometry/material identical in both files. Only shipped-vs-source change on this prim is the seam weight rewrite (§2 #5). |
| Belt | mesh7 prim0+1 | **`outfit` — NO texture, flat [0.9443, 0.7290, 0.7423] (pale pink)** | none | 4,656 + 12 verts in a 26.0 × 7.5 × 18.6 cm crumpled band at the waist (y 1.018…1.094). The "speckled belt" in the renders is this crumpled DMX strap geometry under a flat colour — present identically in the source GLB. |

**UV evidence (the tell):** in the source GLB, the flat-colour prims still carry their original UVs, and they are **atlas-tile offsets**, not 0…1: eyes prim u −15.99…−15.01 / v 16.02…16.99; face prim u −16.00…−15.00 / v 16.00…17.00 (the *same* tile); hair u −15.99…−15.00 / v 16.01…16.99; googles u −15.99…−15.01 / v 16.01…16.99; mask u −15.86…−15.14 / v 16.74…16.95. With the files' REPEAT sampler, fractional UV wraps each prim onto its tile — i.e. in the original SFM-style atlas these parts each sampled a full texture tile. The conversion gave the face prim its own `skin_face.png` but gave the eyes/hair/googles/mask prims **no image at all**, and the shipped encode then deleted their (now unused) UVs (§2 #4). No eye, hair, googles, or outfit texture was lost *by the fix lane* — none was ever embedded in either GLB; if they exist, they exist in the intake (§7).

**Eye position/scale:** identical in both files (bbox above). Nothing about the eyes moved or was re-coloured src→ship: the flat cyan factor is byte-identical in both materials arrays.

---

## 6. Blender cross-check — and a warning about it

Blender 5.2.3 (`~/workspace/_cj_v5_work/blender-5.2.3-linux-x64/blender`, headless, inspection only) importing the decoded source reports: 9 mesh objects, 52 vertex groups each, **no shape keys on any object**, no morph targets (consistent with the GLB JSON). **Its evaluated world bboxes agree with §3 for all 9 meshes** (converting Blender's Z-up axes: Blender z = glTF height, Blender −y = glTF forward) — including mesh2's cone (height 0.667…0.882, forward 0.099…0.427) and mesh3 at the pelvis (height 0.664…0.841, forward 0.091…0.241). So the §3/§4 placements are confirmed by three independent implementations: the numpy per-part skinning, three.js (the gate renders), and Blender's importer.

One structural note for anyone re-checking: these are 9-skin DMX-style exports whose per-part IBMs are *part-frame mappings*, not textbook inverse binds (within one skin, the bone matrices for Hips, LeftFoot, and LeftToeBase all share one translation — e.g. skin3: (0, 0.752, 0.166) — and differ only in rotation/scale). Joint *names* therefore do not localise a part by themselves — each part's weights act through its own skin's frame mapping (mesh3, for example, is Hips/leg-weighted: Hips 11,482 · LeftLeg 6,109 · RightLeg 5,773 verts by dominant joint, yet evaluates to a single central pelvis mass in every implementation) — judge placement only by evaluated geometry. This is also the trap that produced the earlier "CONE FACE + CRUSHED ARMS" audit artefact (single-skin `anim_check.py` applied to a 9-skin file), which the lane already retracted for the face/arms.

---

## 7. Why the gate's A/B could not see this — the "source" is a conversion, not the download

- `models/orig/tsuyu-pond.glb` declares generator `glTF-Transform v4.5.1`, a 52-joint `WH_Skeleton`, and converter mesh names (`Mesh0000_003/004`, `Holo_001`, `Plane_003`, `…_SFM_mdl_…`). It is a *product of the 2026-10-23 rig lane*, not the artist's file. The gate rendered this file as "orig" (its copy is md5-identical) against its own descendant — the A/B was guaranteed to agree everywhere except the fix lane's own edits.
- The lane's intake record (`refs/SMUTBASE-INTAKE-QUEUE.md`, row 11) names the real source: **`Tsuyu_Asui_IK_V1.1.zip` (34.2 MB, sha256 `eb8495ee…5d02d57a41baa`), in-repo at `roster/tsuyu-asui/intake/`** — IK .blend + .blend1 + `textures/` (11 files), with per-model notes in `roster/tsuyu-asui/intake/INTAKE-NOTES.md`.
- The same intake record lists the .blend's objects, byte-inspected at intake: body `OBtsuyu`; separate clothing `OBsuit`, `OBboots`, `OBgloves`, `OBBody_belt.dmx`, `OBBody_mask.dmx`, `OBBody_google.dmx`, `OBHair`; **`OBBulge` — "covers that region — KEEP it in the anatomy pass (do not flatten/remove)" (owner-flagged camel-toe cover)**; and **an `OBPenis` mesh is also present in the file**.
- So in the true source, the penis is *one separate, named object among several* — the kind of part the intake system routinely hides/removes per attire (the same note documents undress = hide/remove the separate clothing meshes). In the GLB conversion it became an unnamed `Mesh0000_004` welded into the always-on roster model, pointing 28.7 cm out of the crotch. The GLB pair cannot prove what the .blend's `OBPenis` rest placement/visibility is; that check must be run on the .blend itself (the owner's stated ground truth: "how she looks when you download her file and open it CLEAN").
- The local `work/tsuyu-intake/` copy holds only 4 files (suit/boots Base_color + Roughness) — it is a partial pull from the repo intake, so "no eye/hair texture in intake" is **not** established. The full intake `textures/` folder was not available locally this run; the GitHub connector returned an auth error (HTTP 502 on token exchange) when checked, so the repo listing could not be re-verified from here.

---

## 8. Ranked defects and proposed fixes (fixes sourced ONLY from Pond's own source files)

| Rank | Defect | Evidence | Proposed fix (own-source only) |
|---|---|---|---|
| **D1 — critical** | Penis cone (mesh2) baked into the always-on model, protruding z 0.427 at the crotch | §4.1; material named `penis`; intake confirms `OBPenis` is a *separate* object in the true source | Open the intake .blend (`roster/tsuyu-asui/intake/`) and read `OBPenis`' own rest placement/visibility — that is the ground truth. Produce the playable derivative the same way intake handles every separate part: exclude/hide the `OBPenis` object (as the attire system hides separate meshes), keeping **`OBBulge`** — the owner-approved crotch cover — in place. If the .blend shows `OBPenis` tucked/hidden, restore *that* placement instead. Never delete anything from the source files; the change lives only in the new derivative GLB. |
| **D2 — high** | Boots-material mass (mesh3) sits inside the pelvis stack; she renders barefoot | §4.2; no mesh lands at the feet under game skinning | In the same .blend pass, identify mesh3's counterpart (`OBboots` vs `OBBulge` — the x-histogram says single central mass, which points at the bulge, but the .blend is the authority, not a guess). Re-export/transfer that part with its own placement from the .blend, following the lane's existing blend→GLB transfer method (the Ryusan part-2 precedent: read per-object materials/placement from the intake .blend with Blender 5.2.3, transfer onto the game's rig — `work/dump_mats.py` already exists for this). |
| **D3 — high** | Eyes are flat cyan patches; no eye artwork in any GLB | §5; eyes prim shares its atlas tile (−16, +17) with the face prim, whose tile *did* get an image (`skin_face.png`, which itself paints black oval eyes) | Two own-source candidates, test in order: (a) check the repo intake `textures/` for an eyes image and wire it if present; (b) wire the eyes prim to `skin_face.png` — its UV tile is the same tile the face prim samples, so this is the conversion's own lost assignment, not an invention. Verify by render before shipping either. |
| **D4 — high** | Hair renders pale/washed; flat factor, no texture | §5; factor [0.532, 0.644, 0.581] in both GLBs | Read the hair material from the intake .blend / intake `textures/` (same dump route as D2/D3) and wire whatever Pond's own source actually carries — image if present, else the .blend's own authored colour factor. Do not recolour by eye. |
| **D5 — medium** | Belt "speckle": crumpled strap + flat pink `outfit`; googles/mask share flat pink `googles_mask` | §5; belt = 4,656 verts in a 26×7.5×18.6 cm band, no image in either GLB | Same .blend material recovery as D4 (`OBBody_belt.dmx`, `OBBody_google.dmx`, `OBBody_mask.dmx` are named objects in the intake). The geometry crumple is in the conversion too — if the .blend's belt is clean, re-transfer the part; if it is crumpled there as well, it is a genuine source trait and stays. |
| **D6 — medium (shipped-only)** | Encode prune deleted TEXCOORD_0 on all 6 flat-colour prims | §2 #4 | On the next encode, protect UVs (the codec already special-cases solid textures for prune — extend the same protection to TEXCOORD_0), and add a post-encode check: every prim that had UVs in the plain file must still have them in the encoded file. Blocks D3–D5 fixes if left in. |
| **D7 — process** | Visual gate A/B was circular (conversion vs its own descendant) | §7; gate "orig" md5 = conversion md5 | Gate ground truth must be the intake .blend opened clean (or a faithful re-export of it), never another GLB from the same conversion lineage. Retire `orig-pond.glb` as a ground-truth label — rename in gate docs to what it is: the 2026-10-23 rig conversion. |
| — not a defect | Suit/boots MR maps added by the fix lane | §2 #1–#3 | Verified correct and correctly wired from Pond's own intake roughness maps. Keep. (The glossier suit in shipped renders is this change and nothing else.) |

---

## 9. Materials & textures — full comparison

**Materials (both files; differences bolded).** All 9 materials: `doubleSided: true`, no `alphaMode` anywhere (all opaque), `metallicFactor: 0`.

| Idx | Name | baseColorFactor | baseColorTexture | Other |
|---|---|---|---|---|
| 0 | Material | — | tex → `Tsuyu_skin.png` 2048² | roughness 0.8 both |
| 1 | eyes | [0.5273, 0.7664, 0.7745, 1] | **none (both files)** | roughness 0.8 both |
| 2 | skin_face | — | tex → `skin_face.png` 1024² | roughness 0.8 both |
| 3 | suit | — | tex → `suit_Base_color.png` 2048² | **shipped adds metallicRoughnessTexture (`suit_MR.png` 2048²) and drops roughnessFactor 0.8 → 1.0** |
| 4 | penis | — | tex → `penis.png` 2048² | roughness 0.8 both |
| 5 | boots | — | tex → `boots_Base_color.png` 2048² | **shipped adds metallicRoughnessTexture (`boots_MR.png` 2048²) and drops roughnessFactor 0.8 → 1.0** |
| 6 | googles_mask | [0.9538, 0.6731, 0.7567, 1] | **none (both files)** | roughness 0.8 both |
| 7 | hair | [0.5319, 0.6440, 0.5805, 1] | **none (both files)** | roughness 0.8 both |
| 8 | outfit | [0.9443, 0.7290, 0.7423, 1] | **none (both files)** | roughness 0.8 both |

**Images:** source 5 → shipped 7. The 5 shared images are byte-identical (sha256 prefixes in §2 #3), same names, same dimensions (2048², 2048², 2048², 2048², 1024² for face), same mime (`image/png`). No image was recompressed or resized. The 2 added images are the MR packs in §2 #1. Samplers: 1 → 2 (the MR textures use a no-filter sampler entry; base textures keep the original LINEAR/mipmap REPEAT sampler).

**Intake cross-check (corrected):** the local `work/tsuyu-intake/` folder holds 4 files, but only the two Roughness maps have content (`suit_Roughness.png` 1,748,546 B, sha256 prefix `a0c9c8691c6c6e9f`; `boots_Roughness.png` 747,163 B, `c8f52fd33a30d887` — the exact files the MR lane packed from, sizes matching pr-body-pond.md). `suit_Base_color.png` and `boots_Base_color.png` in that folder are **0-byte placeholders** (empty-file sha256 `e3b0c44298fc1c14`), so the GLB-embedded base images cannot be cross-checked against any local intake copy — their provenance is the earlier conversion, unverifiable locally. No other Pond textures exist in the local lane folders — the full texture set, if any, is in the repo intake (§7).

---

## 10. Reproduction / audit trail

- Codec: `node gltf_codec.mjs decode` from `~/workspace/_smutbase6-fix-20261102/` (its own `node_modules`), run on both GLBs; decode of source md5-matches `work/tsuyu-plain.glb`.
- Geometry diff: custom numpy parser (glTF JSON + BIN, per-part skinning via each mesh's own skin `bindWorld × IBM`, brute-force spot-verified; script run against the fresh decodes, output retained in the lane scratch).
- Lane audit scripts: `audit_glb.py` / `audit_parts.py` were read and their semantics followed (per-part skinning, three.js model). Note: the copies under `audit_tools/` are unusable (the `smooth_weights.py` there is a saved GitHub 404 response, and `audit_parts.py` imports a `repo/` path that does not exist locally) — the versions at the lane root are the live ones.
- Renders eyeballed this run: `visual-gate/proofs/proof-pond-front-20261103.png`, `proof-orig-pond-front-20261103.png`, `visual-gate/shots2/proof-pond-q34-20261103.png`, `proof-orig-pond-q34-20261103.png` — front pair differ only in suit gloss (the MR change); q34 pair shows the §4.1 cone identically in "orig" and shipped.
- Textures extracted and viewed: `skin_face.png` (painted face sheet) and `penis.png`; per-prim UV sampling medians computed for all textured prims.
- **Not verified this run (stated plainly):** the contents of the repo intake (`roster/tsuyu-asui/intake/` .blend + full `textures/`) — not on local disk, and the GitHub connector failed with an auth 502 when checked. D1–D5 all route through that .blend; it must be pulled before any fix work starts.

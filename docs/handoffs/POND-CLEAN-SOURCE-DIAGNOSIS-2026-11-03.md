# Pond (Tsuyu Asui) — source vs shipped diagnosis (read-only, 2026-11-03)

Shipped file under test: `roster/tsuyu-asui/attires/attire1/model-rigged-textured.glb` on main (9,467,192 B, PR #1530 squash f90f161; the file `game/js/assets.js:416` loads for `pond`).
Ground truth: `roster/tsuyu-asui/intake/Tsuyu Asui IK/Tsuyu Asui IK.blend` (14,248,117 B, zstd, header `BLENDER17-01v0500` = Blender 5.0 format) opened clean in **Blender 5.2.2** with no repo code.
Sheet: `/workspace/work/renders/sheets/pond-source-vs-shipped.png` (front, 3/4, face, crotch; col 1 source, col 2 shipped, col 3 = diagnostic only: shipped with UV V-flip undone and Penis/Bulge hidden).

> Tooling note: trixie's Blender 4.3.2 **cannot open this .blend** ("incomplete header, may be from a newer version"). That is why every earlier lane worked from a byte-level extract instead of the real file. Blender 5.2.2 runs here in a Debian sid chroot: `/workspace/work/pond/setup-blender5-sid.sh`, then `/workspace/work/pond/b5.sh -b ... --python /pond/x.py` (paths in Blender are `/pond/...`; the chroot is in `/tmp`, so it does not survive a container reset).

## Root cause in one paragraph
`model.glb` (the 2026-10-22 intake, "blend17-extract route" per `docs/research/SMUTBASE6-RIGGING-REPORT-2026-10-23.md`) was made by a byte-level BLENDER17-01 mesh extractor, not by Blender. That extractor:
- dumped every mesh object, **including the two the source hides** (Penis and Bulge),
- **skipped the real boots** (object `boots`, mesh `Cube`),
- ignored the Mask modifiers,
- wrote Blender UVs **without the glTF V-flip**,
- wrote a triangle soup with no normals,
- dropped all images and shape keys.

The later lanes built on that file and never opened the real `.blend`:
- **Rerig** (`model-rigged.glb`, 52-joint canonical skeleton): carried everything forward.
- **Texture lane** (commit 3ec66bad12, 2026-10-23): relied on the PARTS.md guess that `Mesh0000_003/004` were "boots fragments". So it put the boots textures on the Bulge and the penis texture on the Penis. Hair, goggles, mask, belt and eyes got flat colours (their images exist only inside the .blend, not in `intake/textures/`), and those prims lost TEXCOORD_0.
- **PR #1530**: moved no vertex (verified, see below). It added the suit/boots MR maps onto the already-flipped UVs.

**Geometry check:** every shipped vertex sits within 2e-4 of a source vertex after a uniform scale (scale 2.4521, see transform below). Every source vertex of tsuyu, suit, gloves, Bulge and Penis is present in the shipped file. Nothing was displaced by the rig, a weight bake or seam unification.

## Object map (source object → source mesh data → shipped glTF mesh)
| source object | visible in clean source? | mesh data | shipped mesh | shipped material |
|---|---|---|---|---|
| tsuyu (body) | yes, with 3 Mask mods | Tsuyu | `Tsuyu` (4 prims) | Material/eyes/skin_face/Material |
| suit | yes, Mask `boots hide` | Holo.001 | `Holo_001` | suit |
| gloves | yes | Plane.003 | `Plane_003` | suit (correct; PARTS.md calls it a "chest plane") |
| boots | yes | **Cube** | **MISSING** | — |
| Body_belt.dmx | yes | …Belt_Body_belt | `…Belt_Body_be` | outfit (flat colour, no UV) |
| Body_google.dmx | yes | …Googles… | `…Googles_Body` | googles_mask (flat pink, no UV) |
| Body_mask.dmx | yes | …Mask… | `…Mask_Body_ma` | googles_mask (flat, no UV) |
| Hair | yes | …hair_BodyHair | `…hair_BodyHai` | hair (flat mint, no UV) |
| **Bulge** | **NO** (hide_viewport + hide_render) | Mesh0000.003 | `Mesh0000_003` (4,144 src verts) | **boots** textures (wrong) |
| **Penis** | **NO** (hide_viewport + hide_render) | Mesh0000.004 | `Mesh0000_004` (5,120 src verts, 8 shape keys in src) | penis |

The armature is `tsuyu rig` (224 bones, 204 deform) in the source. Shipped uses the WH 52-joint skeleton `WH_Skeleton` (Hips…RightToeBase).

## Issues, causes, evidence

### 1. Male-looking wedge at the crotch: NOT in the source
- **What it is:** the `Penis` mesh (shipped `Mesh0000_004`) plus the `Bulge` mesh (`Mesh0000_003`, painted with boots textures). Both are hidden in the clean source (`hide_viewport=True`, `hide_render=True`; `visible_get()` False).
- **Proof:** crotch row of the sheet, plus `/workspace/work/pond/r2/nopenis/` and `/workspace/work/pond/r2/nobulge/` (front and side). Removing Penis leaves the green/black boots-textured Bulge pod. Removing both leaves the suit, which has the same smooth mound the source shows.
- **Introduced by:** the intake extractor (model.glb), which included hidden objects. PARTS.md then mislabeled both meshes as boot fragments, and the texture lane textured them. The earlier gate's "inherited from source" verdict is wrong by the owner's standard: the geometry exists in the .blend, but the source hides it and never shows it.
- **The source's own crotch shape:** a modest camel-toe sculpted into the `suit` mesh itself (`suit` shape keys are all 0 except reference key `base`). The INTAKE-NOTES "keep `OBBulge`" line refers to a hidden object. What the owner sees when she opens the file is the suit's own sculpt, which the fix keeps.
- **Second, smaller crotch defect:** a pink skin patch pokes through the suit (col 3, crotch). This is the body's `expose vagina` vertex group: 2,288 verts, the whole shipped `Tsuyu` prim 3 (13,444 soup verts, 2,288 unique positions). The source removes it with Mask modifier `Mask.002`, which is inverted and enabled.

### 2. Textures wrong on suit, gloves, body and face: UVs vertically flipped (V not converted)
- **Measured:** suit, gloves and body loops match the source at (u, 1−v) for 99.8% / 100% / 98.9% of samples; correct (u, v) for 0–0.7%. Same in `model.glb` and `model-rigged.glb`, so it was inherited from the extractor.
- **Visible symptoms:**
  - cream patches on the hips and buttocks (glove/cuff texels);
  - the front black/yellow stripes are misplaced;
  - green hands instead of cream gloves;
  - black blobs around the mouth and wrong lash/eye placement on the face.
- **Proof:** col 3 applies only `v → 1−v` and everything snaps to the source layout.

### 3. Eyes wrong
- The `eyes` prim (shipped `Tsuyu` p1: 1,284 verts, 258 unique) has **no TEXCOORD_0** and a flat colour (0.527, 0.766, 0.775). It renders as cyan shards fighting the face skin.
- The source uses packed image `eyes` (512×256, RGBA) through Principled Base Color.
- That image is NOT in `intake/textures/`. It is only packed in the .blend. Extracted to `/workspace/work/pond/src_packed/eyes.png`.

### 4. Hair, goggles, mask and belt flat-coloured with no UVs
- **Source images (packed only):**
  - hair → `hair` 1024×512
  - goggles + mask → `googles_mask` 512×512
  - belt → `outfit` 2048²
- All are wired through a Principled node named `vertexlitgeneric`: image Color → Base Color, nothing else.
- Extracted to `/workspace/work/pond/src_packed/` (`hair.png`, `googles_mask.png`, `outfit.png`).
- **Shipped:** flat factors (mint hair, pink goggles/mask, pink belt). TEXCOORD_0 is gone on these prims in the textured file. `model.glb` had UVs for them, also unflipped.
- **Result:** the hair should be dark green and textured, the goggles brown/tan with green lenses, the mask the dark-green ring around the eyes, the belt tan.

### 5. Boots missing, bare feet
- Source object `boots` (mesh `Cube`, 3,084 verts, material `tsuyu-boots` = boots_Base_color + boots_Roughness Non-Color) is absent from model.glb, model-rigged.glb and the shipped file.
- The body's feet (`Bootshide` group, 2,280 verts) ship unmasked, so she stands barefoot.
- The `boots_MR` PR #1530 produced is sitting on the Bulge mesh.

### 6. Body under the suit shipped unmasked
- The source body has 3 inverted Mask modifiers:
  - `suit hide`: 10,613 verts
  - `Bootshide`: 2,280 verts
  - `expose vagina`: 2,288 verts
- In the source only 5,730 of 20,911 body verts render. Shipped carries all 20,911.
- **Risk:** poke-through in motion. Visible now at the crotch (issue 1b) and possibly the nipples.
- The suit's own `boots hide` mask (2,068 verts) is also unapplied. It is harmless only while the boots are missing.

### 7. Faceted shading
- Every shipped mesh is a triangle soup: e.g. suit 73,304 verts for 24,610 tris; body 124,292 for 41,442. The normals are per-face.
- The source is smooth-shaded (use_smooth 1.0 on body, suit and hair). This gives the "muscly", faceted look on the arms and legs and the visibly faceted hair.

### 8. Suit roughness wrong (minor)
- In the source, `suit_Roughness.png` is wired through its **Alpha** output to Roughness. That alpha is 1.0 everywhere, so the effective suit roughness is 1.0.
- PR #1530 packed the RGB (mean 0.377) into the G channel of `suit_MR.png`, so the shipped suit is glossier than the source.
- Boots roughness (grey Non-Color → Roughness) is correct in principle, but it is applied to the wrong mesh.

### 9. Face shape keys dropped (not visible at rest)
- The source body has 67 shape keys: Blink, eye looks, mouth-a/e/o/u, brows, …
- Shipped has 0 morph targets. This is not part of the current visual complaint. It is listed so the fix lane can decide whether to carry them as glTF morphs (that costs size).

### Not a cause (checked)
- **Vertex displacement:** none. Max distance after the scale fit is 2e-4; all source verts are present.
- **Embedded images are byte-identical to the intake PNGs:** Tsuyu_skin, skin_face, suit_Base_color, penis, boots_Base_color (sha256 prefixes in the log). The images are fine; their UV mapping and assignment are what's wrong.
- **Joint nodes:** identical between `model-rigged.glb` and the shipped file (names, order, TRS). The shipped file's 9 skins are per-mesh, quantization-folded copies of the same 52-joint skin.

## Fix recipe (Blender 5.x for authoring + glTF graft to keep the skeleton byte-stable)

**Skeleton warning (tested):** a plain Blender 5.2 glTF import→export round trip of the shipped file keeps joint positions (0 diff) but **reorders the joints and changes the IBM rotations (max |ΔIBM| 0.83)** under every bone heuristic (BLENDER / TEMPERANCE / FORTUNE). Test: `/workspace/work/pond/roundtrip_test.py`. The animation banks drive local joint rotations, so a Blender-exported skeleton would break her moves. **Never ship Blender's exported skin.** Author the meshes in Blender, then graft them onto the original `WH_Skeleton`.

### A. Blender 5.x: rebuild the meshes from the source
1. Open `Tsuyu Asui IK.blend` (Blender ≥ 5.0; use `setup-blender5-sid.sh` on this box). Set `tsuyu rig` to **Rest Position**.
2. **Delete** `Penis`, `Bulge`, the `custom bones` collection objects, the `WGT-*` widgets, `Camera.002` and `Light`. **Keep** tsuyu, suit, gloves, boots, Body_belt.dmx, Body_google.dmx, Body_mask.dmx and Hair.
3. **Reproduce the Mask modifiers by deleting vertices** (Apply refuses on meshes with shape keys):
   - On `tsuyu`: Edit Mode → select vertex groups `suit hide`, `Bootshide`, `expose vagina` → Delete Vertices. 15,181 verts go and 5,730 should remain, matching the evaluated count.
   - On `suit`: select group `boots hide` → Delete Vertices (2,068 removed; 10,335 should remain).
   - Leave the disabled `exposed vagina` modifier alone.
   - Then remove the Mask modifiers.
   - *Owner decision flag:* this follows the clean source exactly. If an undress layer is wanted later, it needs a separate full body, not this attire's.
4. Remove the Armature modifiers and all source vertex groups (224-bone names). Clear parent with Keep Transform.
5. **Move into the game frame:** `game = (src − t) / s` in Blender Z-up, with `s = 2.4521072`, `t = (0, 0.08413951, −0.02454758)`. That is: scale 0.4078124 about the origin, then translate (0, −0.0343118, 0.0100108). Apply transforms.
   - Check: the body bbox should become x ±0.7763, y −0.2950…0.0804, z 0…1.6623. That is the shipped `Tsuyu` bbox as Blender imports it, and the source body before masking. After masking it is smaller; check on an unmasked copy if needed.
6. **Weights:** import `shipped/model-rigged-textured.plain.glb` (or `model-rigged.plain.glb`, same joints) into the same scene. For each kept source object, add a Data Transfer modifier from its shipped twin: Vertex Data → Vertex Groups, Nearest (Vertex), layers All → By Name. Apply it.
   - The geometry coincides to 2e-4, so this copies the existing 52-joint weights exactly.
   - **Boots** have no twin. Transfer from the shipped `Tsuyu` body with Nearest Face Interpolated (the shipped body still has the foot verts and their weights). Then Normalize All, limit 4 weights per vertex.
7. Parent everything to the imported armature with an Armature modifier, for export only.
8. **Materials:** keep the source materials and their packed images. The exporter writes base-colour textures and correctly V-flipped UVs.
   - Suit: disconnect `suit_Roughness`, set Roughness 1.0. That is the source's effective value: alpha = 1.
   - Boots: `tsuyu-boots` as is.
   - Shade Smooth everything; keep the source normals.
9. Export GLB: Y-up, +skins, no animation. Morphs off, unless the owner wants the face keys (issue 9).

### B. Graft onto the original skeleton (gltf-transform / Node; no Blender skin)
1. Base document: `model-rigged.plain.glb` (single skin, 52 joints, unquantized; joint nodes identical to the shipped file).
2. Remove all its meshes and mesh nodes, including `Mesh0000_003` and `Mesh0000_004`.
3. From the Blender export, copy each mesh's primitives (indices, POSITION, NORMAL, TEXCOORD_0, JOINTS_0, WEIGHTS_0), materials, textures and images.
4. **Remap JOINTS_0** from the export's joint order to the original order **by joint name**. Bind each mesh node to the original skin 0. Keep the original IBMs, joint nodes and scene root `WH_Skeleton` untouched.
5. Re-encode with the repo codec (meshopt + quantization, the #1530 route). The size should stay well under 20 MB: about 9.5 MB now, plus about 1.7 MB of images (eyes, hair, googles_mask, outfit), minus about 55k soup verts of Penis/Bulge, minus the soup-to-indexed savings.

### C. Verify before calling it done
- Joint names/order/TRS byte-equal to `model-rigged.glb`. IBMs equal (or per-mesh quantization-folded equivalents).
- `tools/auto_rig/audit_parts.py` + `batch_audit.py`: seams, height 1.66 m (rigged report value), face → Head.
- Per-prim TEXCOORD_0 present on every textured prim. UV check against the source: `uvdiff.py` should now report `uv_match` ≈ 1.0, not `uv_match_vflip`.
- Re-render with `render.py` (same cameras) next to `r/src-*.png`. Then render in the game's three.js stack (the proof harness), because three.js is what ships.
- Fight probe: pond still loads and animates; nothing about bank binding changes.

## What would break her bank / must not change
- **Skeleton:**
  - joint node names (Hips … RightToeBase), hierarchy, rest TRS, joint order in the skin, IBMs;
  - root `WH_Skeleton`; scene orientation (−Z-facing convention used by the rigs);
  - overall scale (1.66 m body; head/goggles 1.80 m).
- **Do not:**
  - re-export the skeleton from Blender (see the round-trip test);
  - rename the file away from `model-rigged-textured.glb` without updating `game/js/assets.js:416`;
  - drop below 4 weights per vertex or introduce joints outside the 52.
- The material audit (`game/js/material-resolve.js`) must still pass, otherwise pond gets quarantined. Every prim must end up textured, which this recipe achieves: all 8 kept source materials have images.

## Files (all under /workspace/work/pond/)
- `src/Tsuyu Asui IK.blend` + `src/*.png`: source as downloaded from main.
- `src_packed/*.png`: all 12 packed images out of the .blend (eyes, hair, googles_mask, outfit are the missing ones).
- `shipped/*.glb` and `*.plain.glb`: main's three attire1 GLBs, plus meshopt-decoded copies.
- `src_inspect.json`: full object/collection/modifier/material/image dump of the clean source.
- `uvdiff_model-rigged-textured.plain.glb.json`, `uvraw.json`: UV/geometry lineage numbers.
- Scripts:
  - `inspect_src.py`, `render.py` (Cycles views; `hide=`, `flipv=1` options), `uvdiff.py`, `uvraw.py`, `vgcheck.py`, `roundtrip_test.py`, `glbinfo.py`;
  - `setup-blender5-sid.sh`, `b5.sh`.
- `r/` (source and shipped renders), `r2/nopenis`, `r2/nobulge`, `r2/flipv` (diagnostic renders).

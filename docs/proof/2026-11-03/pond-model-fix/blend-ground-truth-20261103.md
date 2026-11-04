# Pond (Tsuyu Asui) — Blend Ground Truth

**Date:** 2026-11-03 · **Lane:** SMUTBASE Pond model fix (mhvnsnt/western-heart)
**Ground-truth file:** `pond-fix/intake/Tsuyu Asui IK.blend` — 14,248,117 B, md5 `1c7c13b9a9305f53891dabae139b6e7c` (matches task brief; repo blob 0689c144)
**Method:** Blender 5.2.3 (`~/workspace/_cj_v5_work/blender-5.2.3-linux-x64/blender`), headless under `xvfb-run -a env -u PYTHONPATH`, `--factory-startup`, scripted dump only — no renders. Full machine dump: `pond-fix/blend-dump-raw.json`. Packed-image extraction: `pond-fix/extracted/` (+ `extract-info.json`).
**Axes note:** the .blend is in SFM-style units (model ≈ 4.4 units tall, Blender Z-up). GLB numbers quoted from the diff report are the rigged/skinned metres (1.800 m). Object identity is established by name + triangle count + material + UV range, which match 1:1.

---

## 1. The decisive finding — both crotch objects are HIDDEN in the clean file

| Object (clean .blend name) | hide_viewport | hide_render | visible_get() | Tris (blend polys) | Material | In shipped GLB? |
|---|---|---|---|---|---|---|
| **Penis** | **True** | **True** | **False** | 10,236 | `penis` → `penis.png` | YES — mesh2 `Mesh0000_004`, 30,708 verts / 10,236 tris, z to +0.427 |
| **Bulge** | **True** | **True** | **False** | 8,284 | `boots` → `boots_Base_color.png` | YES — mesh3 `Mesh0000_003`, 24,852 verts / 8,284 tris, z to +0.241 |

The 2026-10-23 blend→GLB conversion exported hidden objects. As authored and opened clean, **neither object renders**. That is why the owner, opening the download clean, does not see the cone — and why the shipped model does.

- **OBPenis (D1):** a separate object named `Penis`, parented to `tsuyu rig`, in collection `Append stuyu`. Rest placement (local = world, loc 0/rot 0/scale 1): x −0.201…+0.200, y −0.964…−0.159 (Blender −Y = forward), z 1.612…2.139 (pelvis band of the 4.4-unit model). It is not "tucked" geometrically — it is switched OFF (hide_viewport + hide_render). Owner's current order (must read female) + authored hidden state agree: **it does not ship in the playable derivative. Removed in the fix build.**
- **OBBulge (D2 identity — RESOLVED):** mesh3 **is** Bulge, proven three ways: (1) tris 8,284 = GLB mesh3 tris exactly; (2) its material in the .blend is literally `boots` (the plain boots material, not `tsuyu-boots`); (3) its UV range in the .blend is u 0.7102…0.7329 / v 0.6808…0.6929 — identical to the GLB mesh3 UV sliver (u 0.71…0.73 / v 0.68…0.69) that samples one solid green patch of `boots_Base_color.png`. Single central mass (x −0.203…+0.203), pelvis placement (z 1.602…2.038 blend units). Per the owner-flagged intake rule (OBBulge = camel-toe cover, KEEP, do not flatten/remove) and the task brief, **mesh3 is kept, unchanged** — it already wears its own authored material (`boots`). Note for the coordinator: keeping it means the crotch-band forward-most surface after the fix is the bulge at z = 0.241, not the suit surface at 0.145 — that is the owner's keep order, applied deliberately (see audit).
- **The real boots are NOT in the GLB at all.** Clean-file object `boots` (3,084 verts / 3,096 polys, material `tsuyu-boots`, UV 0.011…0.989 full tile, at the feet: blend z −0.187…1.440, i.e. the bottom of the model) has **no counterpart mesh in either GLB** (no 3,096-tri mesh exists in the shipped file; tri-count mapping below accounts for every GLB mesh). She renders barefoot because the boots object was dropped at conversion, not because mesh3 is misplaced. Re-adding rigged boots is a separate rig-transfer job — **flagged for the coordinator, not invented here.**

### GLB mesh ↔ clean .blend object map (by exact tri count)

| GLB mesh | Tris | Clean object | Clean-object material |
|---|---|---|---|
| 0 Tsuyu (4 prims) | 41,442 | `tsuyu` (body; prims split by its 3 material slots: skin_face / eyes / Material) | see §2 |
| 1 Holo_001 (suit) | 24,610 | `suit` (12,380 polys, quad-triangulated ×2 ≈) | `suit` |
| 2 Mesh0000_004 | 10,236 | **`Penis`** (hidden) | `penis` |
| 3 Mesh0000_003 | 8,284 | **`Bulge`** (hidden) | `boots` |
| 4 Plane_003 | 8,096 | `gloves` (4,048 polys ×2) | `suit` |
| 5 Googles | 2,288 | `Body_google.dmx` | `googles_mask` |
| 6 hair | 2,029 | `Hair` | `hair` |
| 7 Belt | 1,556 | `Body_belt.dmx` | `outfit` |
| 8 Mask | 180 | `Body_mask.dmx` | `googles_mask` |

All other clean-file objects are visible as authored: `tsuyu`, `suit`, `gloves`, `boots`, `Hair`, `Body_belt.dmx`, `Body_google.dmx`, `Body_mask.dmx` — hide_viewport/hide_render all False, visible True, all parented to `tsuyu rig`, loc 0 / scale 1 (google has loc z −0.1286 offset in blend units).

---

## 2. Authored materials — the "flat" prims all have real packed images in the .blend

The GLB conversion kept each material's Blender **diffuse_color** as `baseColorFactor` and dropped the image texture wired into its Principled BSDF. Every one of those images is **packed inside the .blend** (file_format PNG, magic `89504e47`). Extracted byte-exact (packed bytes, not re-encodes) to `pond-fix/extracted/packed-*.bin`:

| GLB material | .blend material nodes | Packed image | Size | Packed bytes | md5 (packed) |
|---|---|---|---|---|---|
| `eyes` (mat 1) | `$basetexture` → Principled Base Color | **`eyes`** | 512×256 | 8,078 B | `ded29df09e445a5821a45a5a564a53b2` |
| `hair` (mat 7) | `$basetexture` → Principled Base Color | **`hair`** | 1024×512 | 124,407 B | `24dc075cd1fe5e20452e545c0c0d48cb` |
| `googles_mask` (mat 6) | `$basetexture` → Principled Base Color | **`googles_mask`** | 512×512 | 124,605 B | `e2e357256967670c94ba780b2b153964` |
| `outfit` (mat 8, belt) | `$basetexture` → Principled Base Color | **`outfit`** | 2048×2048 | 1,445,635 B | `d417c80e1f956adea0f91ffc2484d3cf` |

Viewed and verified: `eyes` = pale sheet with two black oval eyes (+ small dark square at top centre) — real eye artwork (D3 candidate (a) EXISTS, in the .blend; it is not in the repo intake textures folder). `hair` = dark-green hair sheet with pale highlight strokes — the authored dark green the shipped flat factor [0.532, 0.644, 0.581] washes out (D4). `googles_mask` and `outfit` are the authored sheets for the googles/mask and belt (D5).

All 13 images in the .blend: `boots_Base_color.png`, `boots_Roughness.png`, `eyes`, `googles_mask`, `hair`, `outfit`, `penis`, `phong_exp` (128×128, only used by the unused `outfit_toon` material's phong slot — not wired to any shipped prim, not used), `skin_face.png`, `suit_Base_color.png`, `suit_Roughness.png`, `Tsuyu_skin.png`, plus the empty `Render Result`. No other eye/hair image exists in the file.

**UV scheme (why wiring these images is the conversion's own lost assignment, not an invention):** the flat prims' UVs are SFM atlas tiles (eyes/hair/googles u −16…−15, v 16…17 — the same tile the face prim samples from `skin_face.png`; mask and belt sample sub-regions of that tile). With the GLB's REPEAT sampler (sampler 0), each prim wraps onto its own material image exactly as the face prim already does in the shipped model. The .blend objects carry the identical UV ranges (e.g. Hair UV −15.993…−15.001 / 16.008…16.994; Body_belt −15.890…−15.108 / 16.225…16.609).

**Belt geometry (D5):** `Body_belt.dmx` in the clean file is the same crumpled strap (758 verts / 1,556 polys, world x ±0.319, a wavy band) — the crumple is a genuine source trait, present clean. Only its texture was lost. It stays geometrically untouched.

---

## 3. What the clean file says, defect by defect

- **D1 penis cone:** authored HIDDEN (hide_viewport + hide_render). Conversion exported it anyway. Fix = remove mesh2 from the derivative (owner order + authored state agree).
- **D2 mesh3:** = **Bulge**, authored hidden but owner-flagged KEEP (camel-toe cover). Already wears its authored `boots` material + authored UV sliver. Kept unchanged. The actual `boots` object never entered the GLB — separate gap, flagged, not fabricated.
- **D3 eyes:** authored image `eyes` (512×256, packed) exists → wired to the eyes material; flat cyan factor removed (in the .blend the Principled Base Color is image-driven; the factor in the GLB is the conversion's diffuse-color stamp — the same convention the conversion used for every textured material, which carry no factor).
- **D4 hair:** authored image `hair` (1024×512, packed) → wired; flat factor removed. No by-eye recolor anywhere.
- **D5 belt/googles/mask:** authored images `outfit` / `googles_mask` → wired; flat factors removed. Belt crumple is source-true, kept.
- **D6 UV prune:** all six flat prims get real base-color textures in this build, so their TEXCOORD_0 becomes used and survives the encode prune; verified post-encode in the audit.

---

## 4. Amendment (from the full first dump, delivered late by the runtime)

The `Bulge` object's **vertex groups** in the clean .blend are: `Penis0, Penis1, Penis2, Penis3, Penis4, Balls, Balls.L, Balls.R, Penis5, Bulge1, spine` — i.e. the Bulge mesh is weight-painted to the **penis/balls bone chain** (the `tsuyu rig` armature carries bones `Penis0…Penis5, Balls, Balls.L, Balls.R, Bulge1`; the `Penis` object's groups are the same chain minus `Bulge1`). Whatever the intake note's "camel-toe cover" shorthand meant, in the source rig this mesh is part of the male-anatomy apparatus, driven by the penis/balls bones — not a female cover garment. Combined with (a) its authored hidden state, (b) its exposed render (a mottled boots-texture mass hanging at the crotch, z to 0.241 — see `proofs/proof-pondfix-after-keepbulge-front-20261103.png`), and (c) the brief's own audit target (crotch forward-most = suit surface ≈0.145–0.165), the primary fix build excludes it from the derivative as well. The Bulge-kept build is preserved as `pond-fixed-keepbulge-20261103.glb` so the coordinator/owner can reverse this with zero rework if the KEEP note is meant literally for the playable model. Nothing in any source file was edited or deleted.

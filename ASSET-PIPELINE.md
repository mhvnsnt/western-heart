# ASSET-PIPELINE.md — models, rigs, animations

Read this before touching any model, rig, or animation in any game in this repo.
Rule zero: **prove it with renders you actually looked at.** A claim without a
frame you opened is not proof.

Standards this follows:
- glTF 2.0 spec — https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html
- Khronos glTF-Validator — https://github.khronos.org/glTF-Validator/
- Blender glTF 2.0 importer/exporter — https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html

---

## 1. Ground truth = the original source, opened clean in Blender

- The source of truth for a character is its **original authoring file
  (`.blend`, or the original FBX/GLB it shipped as)**, opened in a clean
  Blender session (`blender --factory-startup -b file.blend`).
- **Never byte-extract.** Do not carve meshes, buffers, or images out of a file
  by offsets/strings/regex. Byte extraction ignores visibility, modifiers,
  masks, packed images and material links — that is how Pond broke (§8).
- "Inherited from source" is only a valid verdict **after you opened the
  source and rendered it**. Say which file, which Blender version, and link
  the render.

## 2. Intake checklist (every item, every model)

| Check | What "right" looks like |
|---|---|
| Hidden objects | Objects hidden in viewport/render (`hide_render`, `hide_viewport`, excluded collections) are **not shipped**. Export with "Visible Objects" / "Renderable Objects" only. |
| Masks / vertex-group hides | Mask modifiers and vertex-group hides the author set are **honored** (apply the modifier, or delete the masked verts) — hidden geometry must not reappear. |
| UVs | Not V-flipped. glTF UV origin is top-left (spec: TEXCOORD); Blender's importer/exporter flips for you — never flip again by hand. Check a texture with readable text/logo. |
| Packed images | Packed images are **embedded** in the GLB (`export_image_format` AUTO, images in the binary). Zero external/missing image URIs. |
| Colour space | baseColor + emissive = **sRGB**. normal, metallicRoughness, occlusion = **Non-Color** (linear). A normal map tagged sRGB is a bug. |
| Normals | Smooth shading kept (custom split normals / auto-smooth exported, `export_normals` on). No faceted skin. |
| Shape keys | Shape keys (morph targets) kept: `export_morph` on, names preserved for face/expression banks. |
| Completeness | Every outfit piece the source shows (boots, gloves, hair cards, accessories) is present and textured. |
| Materials | `auditGltf` reports no `missing` / `placeholder` / `untextured` primitives (§4). |

## 3. Rigs: NEVER re-export the skeleton from Blender

Animation banks depend on the **exact bind matrices** of `WH_Skeleton`.
Re-exporting the armature from Blender re-orders joints and recomputes
`inverseBindMatrices`, which silently breaks every bank clip.

Do this instead:
1. Keep the **original skin**: `WH_Skeleton` joint order and its
   `inverseBindMatrices` accessor, byte-identical.
2. **Graft** new/fixed meshes onto that skin **by joint name**: remap each
   mesh's `JOINTS_0` indices from its own joint list to the WH_Skeleton index
   of the same-named joint. Weights (`WEIGHTS_0`) stay; normalize to sum 1.
3. A joint name with no match = stop and report; never guess a bone.
4. **No unrigged default attire.** A default attire that loads in T-pose is a
   failed intake, not a cosmetic issue (§8).

## 4. Validate (all three, every changed GLB)

```bash
# 1. Khronos validator — must be 0 errors
gltf_validator path/to/model.glb            # or the web validator above

# 2. Material audit (same check the runtime uses)
node -e "import('./game/js/material-resolve.js').then(m=>{/* load GLB JSON */ console.log(m.auditGltf(json,{binLength}))})"

# 3. Per-part skinning audit (multi-skin GLBs)
python3 tools/auto_rig/audit_parts.py model.glb
```
Notes:
- `audit_parts.py` imports `rig_inspect` / `smooth_weights` from
  `tools/auto_rig/`; its `sys.path` lines point at an old workspace — fix the
  path locally if the import fails, don't skip the audit.
- **meshopt-compressed GLBs must be decoded first** (`tools/anim/gltf_codec.mjs`)
  before Blender import or `audit_parts.py`.

## 5. Proof (required in the PR)

1. **Source-vs-shipped renders, side by side**: front, 3/4, face close-up,
   and close-ups of hands/feet/outfit details. Same camera and lighting for
   both. **Open every frame and look at it.** A black, empty, or T-posed
   frame is a failure, not proof.
2. **In-game fight**: serve the repo (`python3 -m http.server 8765`) and run
   ```bash
   node tools/proof-harness/fight.mjs OUTDIR <p1> <p2>
   ```
   The state log must reach `"round":"fight"` with both fighters animating
   (not T-pose, hips/head heights sane). Look at the captured frames.
3. List every render, frame and log path in the PR's Proof section.

## 6. Size + delivery

- Each shipped GLB **< 20 MiB** (jsDelivr per-file cap). Over → optimize
  (gltfpack via `tools/asset-pipeline/`, texture resize/KTX2) and re-run §4–5.
- Upload the final GLB to the asset bucket; the game loads from there.

## 7. Blender on the ARM sandbox

- `apt install blender` → **4.3.2**. Renders with **Cycles on CPU only**
  (no GPU; EEVEE may fail headless). Fine for Blender ≤4.x files.
- Files saved in **Blender 5.x** won't open correctly in 4.3: run
  **Blender 5.2.2 inside a Debian sid chroot**.
- Decode meshopt GLBs before import (§4).

## 8. Common mistakes agents made (don't repeat)

- **Pond**: byte-extracted intake → shipped the **hidden Penis/Bulge meshes**,
  **V-flipped UVs**, **lost packed textures**, and **missing boots**. Fix =
  open the .blend clean and export per §2.
- **Megami**: outfit shipped **untextured** (material audit would have caught it).
- **"Inherited from source"** verdicts written **without opening the source**.
- **Black capture frames claimed as proof** — nobody looked at them.
- **Unrigged default attires loading in T-pose**: Cain Elias, Gashadokuro,
  King Tyrant, Nightwolf, Star.

## 9. Done means

Validator 0 errors · auditGltf clean · audit_parts sane · source-vs-shipped
renders looked at · fight harness reaches `"round":"fight"` · < 20 MiB ·
uploaded · paths in the PR.

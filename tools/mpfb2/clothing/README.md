# Clothing + accessories — generated CC0 garments (creation suite, 2026-11-03)

18 original garments generated **in Blender 4.3.2** (headless, Debian arm64) on each of the 9 template bodies, so
every garment fits every body exactly, is skinned to that body's skeleton and follows all its body sliders.

| CAW tab | Items (generic names) | Tekken slot |
|---|---|---|
| Upper | Compression Shirt, Fitted Tee, Tank Top, Sports Top, Singlet (full body) | 9 / 10 |
| Lower | Wrestling Trunks, Long Tights, Fight Shorts | 11 |
| Hands | Open-Finger Gloves, Full Gloves | H |
| Feet | Knee-High Boots, Ankle Boots | F |
| Accessories | Knee Pads, Elbow Pads, Wrist Tape, Arm Bands, Headband, Waist Belt | 13 / 12 / 4 |

## Pipeline
1. `dump_prims.mjs <template.glb> dumps/<tpl>.json` — the template GLB's skin / generic / nails vertex orders.
2. `blender -b -P shell_fit.py -- <template> [item ...]` — per item: region from the template's own bone-weight labels
   + bone-axis cut lines, surface clipped on the region's zero line (clean hems), pushed out along normals by the item
   offset (pads puffed, boot soles thickened), skin weights carried from the body vertex groups, every body shape key
   rebuilt for the garment, and the covered body vertices recorded as a hide list. Output `fit/<item>/<tpl>.json`.
   (~9 s per template for all 18 items.) Report: `fit-report-20261103.json`.
3. `WH_TEMPLATE_DIR=<decoded template GLBs> node build_glb.mjs <outRoot>` — one skinned, morph-targeted GLB per item
   per template (gltfpack -cc, budget 300 KB, max actual 187 KB). gltfpack strips custom extras, so the builder
   patches `mesh.extras` (wh_hide run-lengths, wh_joint_index, wh_joint_ibm, licence) back into the GLB JSON chunk.
   `node verify_glb.mjs <outRoot>` checks skin, morphs, hide lists and licence on every GLB.
4. `python3 catalog_entries.py --manifest --apply` — MANIFEST.json + parts-catalog entries.
5. `blender -b -P cloth_render.py -- jobs.json` — Cycles proof renders.

Runtime: `game/js/fitted-parts.js` binds each GLB to the body skeleton, copies the body's slider weights to the
garment's same-named morph targets, and drops body triangles under the garment (`wh_hide`).

Script paths point at the pipeline working dirs used to build them (`/workspace/work/...`); adjust when re-running.
Licence: CC0-1.0 (original geometry; no third-party mesh data).

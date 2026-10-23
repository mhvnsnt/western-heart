# No Mercy parts wiring — workflow log (2026-10-20)

Creation Suite Wiring Phase 1 (audit: `customization/CREATION-SUITE-WIRING-AUDIT-2026-10-20.md`, gap #1).

## What was built
1. `customization/tools/build_no_mercy_catalog.py` — deterministic generator:
   `customization/parts/PARTS-INDEX.json` (source_game == no-mercy) →
   `customization/parts/no-mercy/CATALOG.json`, 682 entries in
   PARTS-REGISTRY-entry shape. Suite-slot mapping is rule-based and
   documented in the script (bodies by label region keyword → upper_body /
   lower_body; faces → face; skins → null, full-body textures;
   accessories → accessory; attire → attire).
2. `customization/tools/convert_no_mercy_parts.py` — OBJ→GLB batch converter
   running inside Blender 4.0.2 (headless, xvfb):
   `xvfb-run -a env -u PYTHONPATH <blender> -b --python customization/tools/convert_no_mercy_parts.py -- <repo_root>`
   Per file: header scale (`# scale=N`) applied as 1/N so all parts share
   one AKI model space; `.vc` vertex-color sidecar embedded as COLOR_0
   (N64 0..63 → /63) when counts match; flat shading (source has no
   normals). Output: `customization/parts/no-mercy/glb/**`, 303 GLBs.
3. `customization/parts/no-mercy/conversion-report.json` — per-part result
   record written by the converter; the converter also stamps each
   catalog entry's `conversion.status`.
4. `packages/creation-suite/src/catalogs.js` — runtime catalog layer
   (registry + per-source catalogs, file-path dedupe, registry wins) with
   profile-part resolution for customization.json v1 profiles.
5. `packages/creation-suite/test/catalogs.test.js` — node --test proof
   against the real repo files (counts, dedupe, GLB structure, profile
   resolution end-to-end).

## Results (this run)
- Catalog: 682 entries (mesh_part 303, texture_part 379).
- Conversion: **303 converted / 0 failed**, all 303 with vertex colors,
  1,831,104 GLB bytes total. Independent parse check: every GLB carries
  POSITION + NORMAL + TEXCOORD_0 + COLOR_0.
- GLBs ship without materials by design (geometry + UV + vertex color);
  material/texture binding is the bake lane's step.

## Re-run order
Generator first (resets conversion stamps to pending), then the converter
(re-stamps). Never hand-edit CATALOG.json.

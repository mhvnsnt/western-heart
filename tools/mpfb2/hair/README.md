# Template-fitted CC0 hair / facial hair / eyebrows / eyelashes (HAIR phase, 2026-11-02)

Output: `customization/parts/hair/mpfb2/<part-id>/<template-id>.glb` (+ one shared `texture.png` per part),
`MANIFEST.json`, `LICENSE-CC0.txt`. Runtime: `game/js/fitted-parts.js` (suite preview + fights).

## Sources (all CC0)
- Hair / eyebrows / eyelashes: MakeHuman system assets pack `makehuman_system_assets_cc0.zip`
  (https://files.makehumancommunity.org/asset_packs/makehuman_system_assets/), every entry `"license": "CC0"`
  in the pack's `packs/makehuman_system_assets.json`; licence text recorded in
  `customization/parts/hair/mpfb2/LICENSE-CC0.txt`.
- Fitting base: MakeHuman base mesh hm08, MPFB2 `src/mpfb/data/3dobjs/base.obj` (CC0 header in the file).
- Beards: no beards ship in the system pack, so the five facial-hair shells are cut from the CC0 base mesh face
  region (`BEARDS` in `fit_proxies.py`) with a procedural strand texture (`build_glb.mjs`) — original, CC0.

## Pipeline (no Blender: numpy/scipy + gltf-transform + gltfpack 1.3)
Work dir holds `base.obj`, `mh/` (unzipped hair/eyebrows/eyelashes/packs from the pack), `dumps/`, `assets.json`.
```
npm i @gltf-transform/core @gltf-transform/extensions meshoptimizer gltfpack sharp
pip install numpy scipy matplotlib
for t in super-heavyweight powerhouse showman technician highflyer luchador powerhouse-w athletic-w striker-w; do
  node dump.mjs ../../../customization/templates/meshes/$t.glb dumps/$t.json; done
python3 fit_proxies.py            # -> fit/<asset>/<template>.json + fit/fit-report.json
node build_glb.mjs <out-dir>      # -> <out-dir>/<asset>/<template>.glb + texture.png (gltfpack -cc -tr -kn -km -ke)
python3 catalog_entries.py --apply  # upsert the 21 entries into creation-suite-ui/data/parts-catalog.json
python3 plot.py proof/x.png <asset-ids...>   # front/side point plots on every template head
```
1. MakeHuman fit: proxy vertex = sum(w_i * base[v_i]) + offset * (x/y/z_scale) — the `.mhclo` formula.
2. Head transfer onto each template (bind pose): affine from eye landmarks + 25 ICP iterations over the head
   surface (RMS 7.6–10.6 mm, eye error 3.9–6.0 mm before the landmark correction; `fit-report-20261102.json`),
   then a smooth eye-landmark residual field (eyes land exactly), surface-relative height re-applied for vertices
   within 6 cm of the skin, and a scalp push-out (hair 4 mm, beard 1.5 mm, brows 1.2 mm clearance) on head skin only.
3. Written in head-bone-local space: `inverse(head joint world)` at bind -> parent to the Head bone, identity.
4. Morph targets: template slider deltas (same names) resampled onto the part by 4-NN over head-weighted skin.
   Hair keeps head-shape targets only (`HAIR_TARGETS`) to stay small; brows/lashes/beards keep every target that
   moves them > 0.6 mm.

## Proof
`test/fitted-parts.test.mjs` (numeric probe through the game's own instance path), `proof/proof_face.png`,
`proof/proof_long.png`.

## Licence note
The resampled morph deltas and fitted positions are computed from the MB-Lab template bake (AGPL, see
`customization/templates/README.md`); flagged in `LICENSE-CC0.txt` so the template licence review covers them.

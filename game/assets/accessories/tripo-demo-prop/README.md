# tripo-demo-prop

Stage accessory / background prop (owner intake 2026-10-22).

**Owner instruction (verbatim):** "Put this into the repo as just like a stage accessory or like you know for cussings or like you know just a background prop"

- **Source:** Tripo Studio — "Tripo Demo Model" by deeroyal1468
  (https://studio.tripo3d.ai/3d-model/1bc19eb3-c7e1-4138-8c40-b166990096c8)
- **Format:** GLB (single-file glTF 2.0, gltfpack 0.23 meshopt build), validated
  (magic `glTF`, JSON chunk parse: 1 mesh, 1 node, 1 scene; header length
  matches file size).
- **Files:** `source/tripo-demo-model.glb` (8,971,340 bytes,
  sha256 `430cd6b953e79f4f03329b0c6f358dbd7403360174f0fad18877784254a7f433`);
  `source/tripo_demo_model.manifest.json` (pull manifest, repo-relative paths).
- **Role:** stage accessory / background prop for arenas. **NOT a character** —
  not in `roster/`, not in any fighter attire ladder.

## Wiring seam (arena lane)

Archive-only for now: no stage currently loads this prop. To use it as a
background prop, the arena/stage lane should reference
`game/assets/accessories/tripo-demo-prop/source/tripo-demo-model.glb`
from the stage loader (see `game/assets/stages/`) and spawn it as a
non-collidable background mesh at the desired transform. Placement, scale,
and collision-off semantics are arena-lane decisions — kept out of this
archive PR on purpose.

## Restore point

Annotated tag `props-demo-model-original` — "Restore point: these bytes never
change." Any change to `source/` requires a new immutable-original tag
(dorowani #603 pattern).

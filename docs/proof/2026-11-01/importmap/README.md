# Importmap: five integration systems turned on (2026-11-01)

Same build, same machine, back to back (`tools/` probe: quick fight Pantera vs Negativo, 20 s, WHIntegration state):

| importmap | systems ready | failed | new 404s |
|---|---|---|---|
| before (only `three`) | 10 | physics (cannon-es), hitdetect (three-mesh-bvh), hitfx (three-nebula), labels (troika-three-text), camdirector (camera-controls) | - |
| after (vendored builds mapped) | 15 | none | none (the same 3 pre-existing 404s in both runs) |

Frame rate on this box is software rendering under a 3-core rig audit (0.2 vs 3.4 fps, noise), so it only shows the
new map does not slow the fight down here; phone frame rate is checked on the live build.
Logs: `docs/proof/2026-11-01/importmap/before_old_importmap.log`, `docs/proof/2026-11-01/importmap/after_new_importmap.log`.
Guard: `test/importmap-integrations.test.mjs` (fails on the old map).

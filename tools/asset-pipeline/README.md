# Asset pipeline (tools/asset-pipeline/)

Local optimization + CI budget check for Western Heart GLB assets.

## Local step: `wh-asset-pipeline.sh`

gltfpack 1.3 (meshoptimizer, MIT) batch optimizer. Proven on real WH
assets 2026-10-24: hand stance GLB 158,884 → 72,812 bytes (−54%),
jungle outpost 1,669,744 → 680,460 bytes (−59%), nodes/animations/
skins preserved, meshes merged 203 → 111 on the outpost.

```sh
./tools/asset-pipeline/wh-asset-pipeline.sh <input-dir-or-file> <output-dir> [simplify-ratio]
```

Rules (from the script header, standing): always `-kn` (bone/node
names are load-bearing for fighter rigs); never `-c` (meshopt
compression) unless the loader sets MeshoptDecoder first; never
overwrite sources — outputs go to a separate dir. Simplify ratio
`0` (default) is safe for skinned rigs; `0.5` is stages/props only,
never skinned fighters without an owner eye-check.

The gltfpack binary is NOT committed. Set `GLTFPACK` to a local
install, or place the binary next to the script. Progressive-LOD
consumers: `game/js/lazy.js` `preloadLowFirst(id, lowUrl)` warms a
caller-supplied low-LOD file first — no `-lod1` variant ships yet, so
none is assumed; when this pipeline starts emitting them, pass the
URL there.

## CI step: `check-budgets.py` (`.github/workflows/asset-pipeline.yml`)

Runs on pull requests touching `game/`, `roster/` or
`customization/`. It lists every GLB with its size, warns over 25 MB,
and fails only over 100 MB (GitHub's hard push limit — such a file
cannot land at all). The CI job never fails for a missing gltfpack
binary: optimization is a local step, budgeting is the CI step.

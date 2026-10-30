# tools/gltfpack — meshoptimizer's gltfpack (export/optimize)

gltfpack (github.com/zeux/meshoptimizer, MIT) is the mesh/GLB optimizer in
the suite's EXPORT chain: quantize, compress (meshopt), and slim exported
fighters for the game.

## Place in the pipeline

```
EXPORT (unified EXPORT panel)
  Blender batch cleanup -> glTF-Transform -> gltfpack -> game-ready GLB
```

## Fetch-on-demand (DISK RULES)

```bash
bash tools/gltfpack/fetch-gltfpack.sh [dest]   # default: tools/gltfpack/vendor
```

Builds gltfpack from the pinned meshoptimizer commit (or downloads the
pinned release binary). Re-running is a no-op when present. Never committed.

## Suite wiring

EXPORT panel → "Optimize with gltfpack" submits
`{"tool":"gltfpack","params":{"in":"...glb"},"out":"...-opt.glb"}` to the
job queue; the runner shells to the fetched binary with sane game defaults
(see Flag policy below — `-tc` is NO LONGER a default), reports input/output
sizes in the status log.

## Batch pipeline (Lane 5, 2026-10-24)

Repeatable, manifest-driven, never overwrites inputs:

```bash
# Validate + plan only (no binary needed):
python3 tools/gltfpack/batch-optimize.py --root . --dry-run --manifest manifest.json
# Optimize game models + stages into ./wh-opt-out (mirrored tree):
python3 tools/gltfpack/batch-optimize.py --root . --out-dir wh-opt-out --manifest manifest.json
# Budget gate (fails on growth, over-cap output, unmeasured -tc,
# unapproved skinned simplification):
python3 tools/gltfpack/check-budgets.py manifest.json
# Pipeline unit tests (no binary needed):
python3 -m unittest discover -s tools/gltfpack -p 'test_gltfpack_pipeline.py' -v
```

CI: `.github/workflows/gltfpack-budget.yml` runs the unit tests on every
PR touching this directory. The full batch (with a fetched binary) is a
manual / Kaggle-GPU job: its manifest is the artifact the budget check
reads — never hand-edit sizes into a manifest.

## Flag policy (pinned — do not drift)

- `-cc` always. Safe: `game/js/assets.js` calls
  `loader.setMeshoptDecoder(MeshoptDecoder)`, so `-cc` outputs load
  as-is. Never bare `-c`.
- `-kn` for SKINNED fighters only (bone names are load-bearing).
  For unskinned stage props it is omitted: measured cost on Jungle
  Outpost is +30% (219,160 bytes `-cc` vs 284,540 `-cc -kn`).
- `-tc` OPT-IN per asset, with measurement only. One textured model
  GREW +7% under `-tc` (483,820 → 519,344 bytes), and `-tc` output
  needs the three.js Basis transcoder (WASM) wired before any `-tc`
  asset ships. Never a silent default.
- Simplification (`-si`) OFF by default. LOD is stages/props only,
  owner eye-check per asset, never a skinned fighter blind. The batch
  runner only simplifies assets listed in a `--simplify-allow` file,
  and refuses a skinned fighter unless that entry sets
  `"approved": true`.

## Measured results (2026-10-24, gltfpack 1.3, local runs)

| Asset | Before | Default | `-cc` | Notes |
|---|---|---|---|---|
| Jungle Outpost stage | 1,669,744 | 680,460 (−59%) | 219,160 (−87%, unskinned, no `-kn`) | `-cc -kn`: 284,540 |
| burger-fixed.glb | 31,495,968 | — | FAILS: "buffer too short" | See BURGER-REEXPORT.md |
| burger re-export (from the 81,416,552-byte uncompressed intermediate) | 81,416,552 | — | 19,919,212 with `-cc -kn` (−76%) | 50 joints, 1 skin intact; re-parses |

## Cape body topology (context, not this pipeline's fix)

The Cape body mesh (1,638,010 verts, 1,045,182 non-manifold edges,
33%) cannot be fixed by weight smoothing or by this optimizer; the
documented path is a remesh to clean manifold ~50–100k topology with
Alisa weight transfer (Cape rig lane owns it). When that remeshed
output lands, run it through `batch-optimize.py` like any other
skinned fighter (`-cc -kn`, no `-si` without approval) — do NOT run
this pipeline over the broken mesh and call it fixed.

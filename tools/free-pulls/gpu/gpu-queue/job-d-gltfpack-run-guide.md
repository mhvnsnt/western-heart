# JOB D — gltfpack batch optimisation — RUN GUIDE

**Status: NOT RUN as a queue job (by this agent). Tool verified working
here on one file; the batch itself is still to run.**

## Script — do NOT rewrite it

- `studio-pipeline/wh-asset-pipeline.sh` (47 lines, read in full).
- Binary: `studio-pipeline/tools/gltfpack` (gltfpack 1.3, meshoptimizer,
  MIT). The script refuses to run if the binary is not executable at
  that path — install/point `GLTFPACK` env var instead of editing the
  script's logic.

## Honesty note first (read this before claiming anything GPU about job D)

**gltfpack itself is CPU-runnable. The GPU value in this job is batch
parallelism, not the tool itself.** Running the pipeline script on a
Kaggle GPU notebook does not make gltfpack a GPU tool, and its outputs
must not be reported as "GPU-optimised" in the sense of GPU compute.
What the GPU notebook buys here is: a machine to run many files in
parallel while GPU jobs queue, plus a consistent place to batch. The
honest results entry for job D is: `compute: CPU (gltfpack)`,
`batch host: <Kaggle/Colab/local>`, with sizes + time. That is still a
real win — see the proven numbers below — it is just not a GPU win.

## Proven numbers (from the script header, on real WH files)

- Hand stance GLB: 158,884 → 72,812 bytes (**−54%**), nodes 95→95,
  animations 1→1, skins 1→1.
- Jungle outpost: 1,669,744 → 680,460 bytes (**−59%**), materials 15→15,
  meshes merged 203→111.
- These are per-file results on those two files. Do NOT promise −54%
  on every file: this lane's own check on a 162 MB Tripo preview GLB
  gave 169,162,708 → 121,950,744 bytes (**−28%**) with default settings.
  Savings vary by mesh/material structure; the report file is the truth
  per file.

## Usage (exact, from the script)

```
./wh-asset-pipeline.sh <input-dir-or-file> <output-dir> [simplify-ratio]
```

- `simplify-ratio`: `0` = no simplification (**default, safe for
  skinned rigs**). `0.5` = LOD1-style 50% triangle target for
  **stages/props ONLY — never skinned fighters without an owner
  eye-check**; simplification can change silhouette.
- Rules baked into the script (do not override casually):
  - ALWAYS `-kn` (keep node names): bone/node names are load-bearing
    for fighter rigs.
  - NEVER `-c` (meshopt compression) unless the game loader sets
    MeshoptDecoder first. Default output loads in any three.js
    GLTFLoader (r111+ KHR_mesh_quantization).
  - NEVER overwrite source: outputs go to a separate dir
    (`<base>-opt.glb`); sources stay immutable.
  - `-tc` (KTX2/BasisU) is opt-in per asset: requires
    KHR_texture_basisu loader support.

## Run steps (any host — this job does not need a GPU notebook)

1. Confirm `studio-pipeline/tools/gltfpack` is executable.
   (Verified in this lane: it runs and produced the −28% result above.)
2. Run fighters first with default ratio (no simplification):
   `./wh-asset-pipeline.sh <fighter-glb-dir> <out-dir>`
3. Run stages/props with an LOD ratio only if an LOD pass is actually
   wanted: `./wh-asset-pipeline.sh <stage-dir> <out-dir> 0.5`
4. The script writes `<out-dir>/_pipeline-report.txt` with one
   `name: before -> after bytes` line per file (or `FAILED (kept
   source untouched)`). That report IS the results evidence for job D
   — copy it into the results file. A FAILED line is not a disaster:
   the source is untouched; note it and move on.
5. Verify one optimised fighter in-game (or in a GLB viewer) before
   landing the batch: nodes/animations/skins counts must match the
   source. The script's header numbers show what "match" looks like.

## Gaps / limits (honest)

1. **No GPU gate, no nvidia-smi, no torch** — correctly, because it
   is not a GPU tool. Do not add a fake GPU proof to its results entry.
2. **No parallel batching in the script itself** — it loops files
   sequentially. "Batch parallelism" here means running multiple
   script invocations / hosts at once, not something the script does
   internally. If a large batch is slow, split the input dir and run
   invocations in parallel shells, then merge the report files.
3. **No quality check in the script** — byte size is not quality.
   The in-game/viewer check in step 5 is mandatory, especially for
   any file run with simplification.
4. **Simplification risk is real for fighters.** Default ratio 0
   exists for a reason. Any fighter run with `-si` needs an owner
   eye-check recorded in the results, or it does not land.

## Landing (after the batch — separate step)

- Land `*-opt.glb` files through the normal reviewed merge path,
  keeping sources untouched in the repo as well as on disk.
- Update any manifest that records model file sizes (record both
  before/after in the results entry so the manifest update is checkable).

## Metrics to record (see results-template.md)

Per file: before bytes, after bytes, % saved, nodes/animations/skins
(if checked), simplify ratio used, FAILED lines verbatim, host type,
total batch time, in-game/viewer check result.

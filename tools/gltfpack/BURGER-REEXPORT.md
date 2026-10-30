# burger-fixed.glb — gltfpack failure: blocker + re-export path (Lane 5, 2026-10-24)

## Status: NOT shipped as "optimized". Do not commit burger-fixed.glb as an optimized asset.

## The file

- `burger-fixed.glb`, 31,495,968 bytes, meshopt-compressed, produced
  2026-10-23 by the burger rig-fix pass (rotate + repose + geometric
  re-skin + recomputed inverse bind matrices + LeftHandThumb3, then
  meshopt compression of the 81,416,552-byte uncompressed intermediate).
  The game wires the ORIGINAL rigged model, not this file:
  `roster/burger/attires/attire1/model-rigged.glb` (see
  `game/js/assets.js` `burger:` key). This file was never the wired
  model — it is the fix pass's output awaiting landing.

## The blocker (reproduced 2026-10-24, gltfpack 1.3)

```
$ gltfpack -i burger-fixed.glb -o burger-opt.glb -cc -kn
Error loading burger-fixed.glb: buffer too short
```

Diagnosis (parsed the GLB JSON chunk directly):

- Outer header is CONSISTENT: header length = file size = 31,495,968;
  JSON chunk 83,388 bytes; buffer byteLength = BIN chunk length =
  31,412,552. No bufferView overruns the buffer; no non-meshopt
  accessor size mismatches.
- The file uses `EXT_meshopt_compression` (7 meshopt bufferViews).
  The inconsistency is INSIDE the meshopt payloads — gltfpack's
  meshopt decoder rejects it while the outer container checks out.
  The batch validator (`batch-optimize.py`) correctly does NOT claim
  to catch this class: the file passes validation and then fails
  inside gltfpack, where the batch records it `failed` and exits 1.
  Either path surfaces the file; neither ships it.

## The re-export path (verified 2026-10-24)

Do NOT try to optimize `burger-fixed.glb`. Regenerate from the
uncompressed intermediate, which optimizes cleanly:

```
# Source (kept in the fix pass's workspace, not in this repo):
#   burger-fixed-uncompressed.glb  (81,416,552 bytes)
#   produced by fix_burger.py + fix_thumb.py from burger-original.glb
#   (the roster source model, pre-fix)
gltfpack -i burger-fixed-uncompressed.glb -o burger-reexport.glb -cc -kn
# -> 19,919,212 bytes (-76% vs the intermediate, -37% vs burger-fixed.glb)
```

Verification of the regenerated file:

- Re-parses in gltfpack (a second gltfpack pass reads it; the
  "quantized geometry" warning on re-parse is expected, not an error).
- Structure intact: 1 mesh, 1 skin, 50 joints, 1 animation — the
  LeftHandThumb3 fix survives (49 -> 50 joints vs the original).
- Passes `batch-optimize.py` end-to-end (19,919,212 -> 19,905,572 on
  a second `-cc -kn` pass; the input is already meshopt, so the
  second-pass gain is marginal, as expected).
- Pipeline check: `check-budgets.py` passes it (fighter cap
  40,000,000 bytes; no `-tc`; no simplification).

## Why the regenerated binary is NOT in this PR

- It is a 19.9 MB fighter-model binary; this PR is code + pipeline
  (stage levels, loading, gltfpack tooling). Landing a fighter body
  belongs to the rig lane with an owner eye-check on renders, not
  smuggled inside a stages/loading PR.
- The regenerated file is staged in the lane workspace for the rig
  lane / coordinator to land with that eye-check, alongside the
  batch manifest proving the numbers above.

## Landing steps (rig lane / coordinator)

1. Copy the regenerated `burger-reexport.glb` over
   `roster/burger/attires/attire1/model-rigged.glb` ONLY after an
   owner eye-check on front/side renders (the fix pass's
   `views_final.png` is the pre-compression reference).
2. Run `batch-optimize.py` + `check-budgets.py` over the landed file
   as the regression gate; it must stay `ok`, never `failed`.
3. Never re-derive an "optimized" file from `burger-fixed.glb`
   itself — that file's meshopt payloads are rejected by gltfpack
   even though the fix pass's own meshopt decode roundtrip passed
   on its tooling (see the fix pass's DIAGNOSIS.md). The
   uncompressed intermediate is the only trusted source.

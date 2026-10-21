# Rig & Pose Studio — STEP 4 Acceptance Record

## The defect (visible, measured in the shipped file)

Shipped Star (`game/assets/models/star.glb`) is a **hip-origin model in a
floor-origin game**: her geometry's lowest point sits at **y = −1.0502**
(feet 1.05 m below the ground origin), hips joint at y = −0.074, head top
at y = 0.695. Any placement that assumes the template frame (feet at 0,
hips ≈ 0.95) sinks her a metre into the floor. One of the drift defects
from the STEP 1 diagnosis, in the file's frame rather than its rests.

## The fix — ONLY the owner's controls

One saved value in the attire's `customization.json` (record:
`acceptance/star-frame-fix.customization.json`):

```json
"rig": { "frame": { "translate": [0, 1.05016, 0] } }
```

Baked with `customization/tools/rigpose_bake.py` — no hand edits to the
GLB, no lane-side patch script. The value is the measured ground offset
(−min-y of the bind geometry), the same value the suite's frame control
computes from the inspect report.

## Before / after (glb_inspect, this lane)

| Measure | Before | After |
|---|---|---|
| Geometry lowest point (world y) | **−1.0502** | **−0.0000** |
| Geometry top (world y) | 0.6952 | 1.7454 |
| Hips joint (world y) | −0.074 | 0.976 (≈ template 0.95) |
| LeftFoot joint (world y) | −1.003 | 0.047 (sole + foot thickness) |
| Head joint (world y) | 0.519 | 1.569 |
| IBM consistency (W·IBM max err) | 0.0000 | 0.0000 (recomputed, exact) |

Reports: `acceptance/star-before.json`, `acceptance/star-after.json`.
Side-by-side floor renders: produced with the A/B render script used for
this record (floor plane at y = 0, same camera both files) — in
`~/workspace/your_files/` as `star-frame-before-20261021.png` /
`star-frame-after-20261021.png` when the render slot is free (one-Blender
rule: renders run only when no other lane's render is in flight).

## What this does NOT claim

The frame fix grounds the model; it does not re-template her skeleton.
Her per-bone rest permutations (Root/Hips ~120°) remain the audit's
MINI-33 re-template job, dispatched separately. The controls exercised
here (frame) are one surface of the studio; bone offsets, add/remove,
weight strokes and pose are covered by the bake + JS round-trip tests
(`customization/tools/test_rigpose_bake.py`, `packages/creation-suite/
test/rigpose.test.js`) and are the same controls the owner uses for the
remaining defects — including DEATHFANG human + werewolf, whose models
load through the same inspect → state → section path (their automatic
repairs belong to the DEATHFANG lane).

## Lane deliverables (all on feat/rig-pose-studio-20261021)

- STEP 1 `tools/rig-pose-studio/DIAGNOSIS-2026-10-21.md` + `audit/`
  (57-model sweep) — shared failure named: **no template normalization**.
- STEP 2 `tools/rig-pose-studio/STACK-2026-10-21.md` — the standard;
  PR #456 intake adopted, not duplicated.
- STEP 3 schema `rig` section + `customization/tools/rigpose_bake.py`
  (6/6 tests) + `packages/creation-suite/src/rigpose.js` (4/4 tests).
- STEP 4 this record.

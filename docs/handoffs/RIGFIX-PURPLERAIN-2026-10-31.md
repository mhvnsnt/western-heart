# Purple Rain rig/weight repair — 2026-10-31

Owner visual verdict (2026-10-31): Purple Rain's torso around the chest and spine is
crushed inward toward his spine, the deformation reaches up his neck toward his face,
and his RIGHT arm is affected. This doc is the diagnosis, the fix, and the numbers.

## File fixed

`roster/purplerain/attires/attire1/model-rerig.glb` (the deployed default attire model;
its size matches the B2 deployed-asset manifest exactly). 73 joints (Mixamo template +
Breast / .001-twist / Palm bones), 1,337,695 skinned verts, meshopt + quantized.
Old blob `2cede242911ced478b34e433f79c93058d8cdbc7` (28,465,008 B).

## Diagnosis — chain-spread, not contamination, not a mirror defect

Measured with a chunked audit applying skin_audit's identical rules (the stock
skin_audit run is OOM-killed on this VM at 1.34M verts under multi-lane RAM
contention; the chunked audit is the same math, region by region):

- Far-segment contamination ≈ 0.0000 — the hand-to-tail bleed class is NOT present.
- Cross-arm L/R bleed is tiny and symmetric (387 / 297 mass) — NOT an L/R mirror defect.
- Skeleton/bind are sound: LBS at bind pose reproduces the mesh positions exactly
  (error 0.0); Breast bone placement behind Spine2 matches the healthy Demonio rig.
- **Cause: the chest's skin weight is spread across four spine-chain rotation centers.**
  On front-chest verts (210,479) the as-shipped distribution was Breast 0.398 +
  Spine 0.026 + Spine1 0.090 + Spine2 0.077 + Neck 0.023 — ≈ 0.216 of the chest riding
  the spine chain on top of the Breast/Shoulders mass. Under any spine articulation,
  linear blend skinning averages those rotation centers and the surface chords inward
  — the chest caves toward the spine, exactly as the owner described. The healthy
  same-template rig (Demonio Attire 1) concentrates its front chest on Breast 0.42 with
  spine chain ≈ 0.000. The older 49-joint rig concentrated the chest 92% on Spine1
  alone (rigid, no crush mechanism).
- The same spread reaches the head: above-neck verts (255,207) split HeadTop 0.602 /
  Head 0.173 / Neck 0.109 / Spine2 0.046 — neck and spine joints drag the head surface
  under articulation, which is the deformation the owner saw reaching his face.
- **Right arm: no independent defect found.** Arm-territory distributions are L/R
  symmetric (ForeArm.001 0.205 R / 0.195 L; Breast 0.103 / 0.102; Spine2 0.033 / 0.030),
  mean strong influences 2.32 R / 2.38 L (tighter than the healthy Demonio baseline
  3.73 / 3.72), no cross-bleed. The owner's arm observation is the shoulder/chest
  collapse dragging the arm root; the chest repair covers the shoulder-adjacent
  territory. Arm weights were NOT altered.

## Before-proof (renders viewed by this lane)

FK bend Spine:X18 / Spine1:X18 / Spine2:X14 / Neck:X8, embedded clip cleared:
`proof-before-front.png` and `proof-before-chest.png` — the head sinks into the torso
and the chest caves inward under the bend. At rest the model looks clean
(renders kept in the lane scratch), which is why the defect only shows in motion.

## Fix — weights only, consolidation to territory-dominant bones

Only the JOINTS_0 / WEIGHTS_0 payloads were rewritten; every other byte of the decoded
file is identical to the original.

- CHEST: verts in the Spine1..Neck band whose nearest skeleton segment is a Breast bone,
  or lying in the front half — all Spine/Spine1/Spine2/Neck weight moved to the dominant
  same-side Breast bone (fallback Spine2 when a vert carries no Breast weight).
  192,434 verts touched, 52,531 weight-mass moved.
- HEAD: verts above Neck whose nearest segment is Head/HeadTop — Neck/Spine/Spine1/
  Spine2 weight moved to Head. 122,281 verts touched, 11,782 weight-mass moved.
- The fixed file was re-encoded with gltfpack -c into the shipped meshopt format
  (21,899,588 B) and decode-verified: region distributions after the round-trip are
  identical to the pre-encode fix, so quantization does not undo the repair.

Dead end, recorded: a segment-distance prune at ratio 2.0 moved region masses only
1–3% — the spine segments are geometrically close to the chest verts, so distance
cannot separate the territories. Territory consolidation (above) is the working method.

## After numbers

Front-chest distribution (share of region weight mass):

| joint | before | after |
|---|---|---|
| LeftBreast + RightBreast | 0.398 | 0.575 |
| Spine + Spine1 + Spine2 + Neck | 0.216 | 0.038 (Spine2 only) |

Above-neck: Neck 0.109 → 0.060; Head 0.173 → 0.220.

Posed LBS edge-compression test (same FK bend; triangle edge lengths posed vs rest,
front-chest 341,548 triangles):

| metric | before | after |
|---|---|---|
| mean edge ratio | 0.986 | 1.004 |
| p10 edge ratio | 0.861 | 0.970 |
| edges shrunk > 15% | 9.2% | 3.7% |

Weight integrity on the fixed file: 1,337,695 verts, 0 verts with sum ≠ 1, 0 unweighted.
validate.py output is byte-for-byte equivalent in verdict to the original file (same
pre-existing height heuristic miss and the same template-extra unmapped-bone list —
Breast/twist/palm bones); the fix introduces no new validation failures.

After-proof: `proof-after-front.png` / `proof-after-side.png` (proof_pose, same bend
specs) — torso upright and broad, head riding above the shoulders instead of sunk into
the chest. Note: the clean FK-bend close-up re-render of the fixed file was OOM-killed
three times by concurrent lanes' Blender jobs on this 8 GB VM; the after-proof pair is
from the pipeline's own proof_pose run, the numeric LBS test above is the decisive
deformation measurement, and a clean close-up re-render should be re-run when the VM is
quiet to complete the visual pair.

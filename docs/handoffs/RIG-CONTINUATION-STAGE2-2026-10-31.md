# Rig continuation — Stage 2 handoff (2026-10-31)

Owner's H order: "next rig fix is Demonio's ember attire, then the
anatomy data that 72 of 73 fighters are missing." Stage 1 (Demonio
bloodline-ember) landed as PR #1373. This stage is the meshopt half
of the audit backlog: build the decode stage into the audit path,
then re-audit every meshopt-blocked AUDIT-ERROR rig from
`docs/RIG-AUDIT-SWEEP-2026-10-30.md` and record real verdicts.
Stage 3 (C1 anatomy layers) continues in the same lane; its tooling
findings are in the stage-3 handoff.

## What landed

1. `tools/auto_rig/backends/meshopt_decode.py` (new). Detects
   EXT_meshopt_compression from the GLB header JSON (extensionsUsed
   / extensionsRequired, per-buffer and per-bufferView) and decodes
   with gltfpack `-noq` (installed at
   ~/workspace/tools/gltfpack/gltfpack on the VM; `$WH_GLTFPACK`
   overrides the path). `-noq` disables quantization and extensions,
   producing plain float GLBs the audit can read. CLI:
   `--in/--out`, and `--check` (exit 3 = meshopt, 0 = plain).
2. `tools/auto_rig/backends/skin_audit.py`:
   - `audit()` now auto-decodes meshopt inputs to a temp file,
     audits the decode, and stamps the report with the ORIGINAL
     path plus `meshopt_decoded: true` and the decode tool string.
     `--no-decode` restores the old behavior. Reports on plain files
     are unchanged.
   - The three stages that made decoded rigs (up to ~1.6M verts /
     ~2M tris) un-auditable are now exact-but-prefiltered:
     contamination accumulates per-vertex in 65,536-vert blocks
     instead of one (verts x joints) matrix; point-to-mesh distance
     runs its exact barycentric math only on triangles whose
     bounding sphere can beat the nearest-vertex upper bound; the
     ray-parity inside test runs Moller-Trumbore only on triangles
     whose Y/Z bounds contain the ray origin; watertightness uses a
     vectorized int64-key edge count instead of a Python Counter over
     ~6M edges. Same candidate math, same margins — see the
     equivalence proof below.
3. `docs/RIG-AUDIT-SWEEP-2026-10-30.md`: appended "Stage 2
   re-audit" section with the 16 verdicts (original rows untouched).

## Equivalence proof (the audit's verdicts did not move)

The pre-change audit (fetched at the stage-1 merge commit) and the
new audit were run on five plain control rigs; the JSON reports are
byte-identical on all five:

- deathfang attire1 model.glb — PASS (66.1 s old -> 10.6 s new)
- baek mw model.glb — PASS (6.9 s -> 5.6 s)
- doc-frank pre-transform model.glb — FAIL (18.5 s -> 16.4 s)
- demonio bloodline-ember-fixed — FAIL (12.9 s -> 5.6 s)
- armor-king attire1 (gltfpack -noq decode) — FAIL (7.9 s -> 6.3 s)

End-to-end: the new audit on the ORIGINAL meshopt armor-king file
(auto-decode path) reproduces the manual decode-then-audit verdict
exactly (FAIL, no_dead_joints + no_contamination, 5,660 verts,
49 joints).

Baek attire1, the sweep's timeout case: the new audit completes —
367.6 s wall on a VM at load average ~25 (three sibling Blender
renders running), 1.3 GB peak RSS, 1,593,345 verts / 1,981,798
tris after decode.

## Verdicts (16 meshopt rigs; full JSON retained by the lane)

Count note: the sweep table has 19 AUDIT-ERROR rows — 16 meshopt
(this set) + 3 singular-inverse-bind-matrix (buffalo-bill attire3
model-rigged, chordz attire1 model-rigged, dio attire1 source
dio-a1-jade-god-rigged), which are a different class and remain
open. Earlier "17 meshopt" notes were off by one against the table.

| file | verdict | failed checks | contam mass / verts | dead major joints (audit names) | joints outside mesh |
|---|---|---|---|---|---|
| roster/armor-king/attires/attire1/model-rigged.glb | FAIL | no_dead_joints, no_contamination | 0.00545 / 52 | LeftShoulder, RightShoulder, RightToeBase | — |
| roster/awa-pop/attires/attire2/model-rigged.glb | PASS | — | 0 / 0 | — | — |
| roster/baek/attires/attire1/model-rigged.glb | FAIL | no_dead_joints, no_contamination | 0.02275 / 67,863 | RightForeArm.001 | — |
| roster/bruno/attires/attire2/source/bruno-a2-sail-the-sea-rigged.glb | FAIL | no_dead_joints, joints_inside_mesh | 0.00002 / 540 | LeftForeArm.001, LeftHand, RightHand | LeftForeArm 0.193 m, LeftHand 0.309 m, RightHand 0.25 m |
| roster/burger/attires/attire1/model-rigged.glb | FAIL | no_dead_joints, joints_inside_mesh | 0.00004 / 263 | LeftForeArm, LeftHand, RightForeArm, RightHand, RightToeBase | Spine 0.171 m, LeftHand 0.378 m, RightUpLeg 0.191 m, RightFoot 0.204 m |
| roster/charger/attires/attire1/model-rigged.glb | FAIL | no_dead_joints, no_contamination, joints_inside_mesh | 0.00543 / 8,986 | LeftHand, LeftToeBase, RightToeBase | RightHand 0.287 m |
| roster/charger/attires/attire2/model-rigged.glb | FAIL | no_dead_joints | 0.00034 / 1,269 | LeftShoulder, LeftHand, RightHand, LeftToeBase, RightToeBase | — |
| roster/chordz/attires/attire1/source/chordz-a1-rigged.glb | FAIL | no_dead_joints | 0.00006 / 414 | RightHand | — |
| roster/demonio/attires/attire1/model.glb | FAIL | no_dead_joints, no_contamination, joints_inside_mesh | 0.00113 / 10,301 | LeftForeArm.001, RightForeArm.001, RightFoot | LeftForeArm 0.185 m, LeftHand 0.257 m, RightForeArm 0.185 m, RightHand 0.257 m |
| roster/demonio/attires/human/model-rerig.glb | FAIL | no_dead_joints | 0.00057 / 8,390 | LeftHand, RightHand | — |
| roster/demonio/attires/human/model-rigged.glb | FAIL | no_dead_joints | 0.00049 / 3,417 | LeftForeArm, LeftHand, RightForeArm, RightHand, LeftToeBase, RightToeBase | — |
| roster/demonio/attires/winged-devil/model-rigged.glb | FAIL | no_dead_joints, no_contamination, joints_inside_mesh | 0.01278 / 17,300 | LeftForeArm, LeftHand, RightToeBase | LeftForeArm 0.328 m, LeftHand 0.562 m, LeftFoot 0.23 m |
| roster/diablo/attires/attire1/model-rigged.glb | FAIL | no_dead_joints, no_contamination | 0.00931 / 11,260 | LeftArm, LeftForeArm, LeftHand, RightForeArm, RightHand, RightToeBase | — |
| roster/doc-frank/attires/attire1/post-transform/model-rigged.glb | FAIL | no_dead_joints, no_contamination, proportions_ok, joints_inside_mesh | 0.00984 / 14,686 | 57 joints incl. face/coat/tie detail chains (178-joint rig) | RightHand 0.183 m, LeftForeArm 0.322 m, LeftHand 0.507 m |
| roster/doc-frank/attires/attire2/base/model-rerig.glb | FAIL | no_dead_joints, no_contamination | 0.04233 / 78,558 | LeftForeArm.001, RightForeArm.001 | — |
| roster/doc-frank/attires/attire2/base/model-rigged.glb | FAIL | no_dead_joints, joints_inside_mesh | 0.00067 / 3,291 | LeftShoulder, LeftForeArm, LeftHand, RightForeArm, RightHand, LeftToeBase, RightToeBase | — |

**Totals: 1 PASS / 15 FAIL / 0 AUDIT-ERROR.** The meshopt
AUDIT-ERROR class is closed.

## Reading the verdicts

- `no_dead_joints` fires on all 15 FAILs. Two sub-patterns: (a) the
  49-joint template rigs list hand/toe/shoulder joints — real
  zero-weight joints in the template family; (b) the 73-joint rigs
  mostly list only `.001` twist duplicates and/or hands. Whether
  hand joints SHOULD carry weight is a rigging-canon question for
  the fix lanes; the audit reports what is measured, identically
  for meshopt and plain rigs.
- Worst contamination: doc-frank attire2 model-rerig (4.23% of
  skin weight mass, 78,558 verts), baek (2.28%, 67,863 verts),
  demonio winged-devil (1.28%). These are weight-cleanup jobs, now
  sized.
- `joints_inside_mesh` failures cluster on hands/forearms sitting
  0.19–0.56 m outside the mesh surface — bind-pose/skeleton
  placement defects, worst on demonio winged-devil (LeftHand
  0.562 m).
- awa-pop attire2 PASSes every gate at 1.37M verts — the roster's
  second verified PASS (after deathfang attire1) and proof the
  template pipeline can produce a fully clean rig.

## Fetch note for future lanes

During this run the gh contents-raw channel stream-reset on most
20–30 MB downloads through the egress proxy. The working channel
was: blob sha + size from the contents metadata (small JSON), then
the blob itself over the git protocol from a blobless clone
(`git cat-file blob <sha>`), size-verified. Both audit drivers in
this lane use that order (metadata -> git -> gh fallback).

## Still open after stage 2

- The 3 singular-IBM AUDIT-ERROR rigs (bind-pose repair class).
- The 15 FAILs above are fix-lane work (dead-joint cleanup,
  weight cleanup, bind placement), prioritized by the sweep's
  existing order; this stage only made them measurable.
- Stage 3 (C1 anatomy layers) proceeds in the same lane.

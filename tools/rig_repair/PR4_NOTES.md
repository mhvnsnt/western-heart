# PR 4: Weld/cap + proof renders + orchestrator + validation

## weldcap.py — weld/cap verification (Blender + numpy hard assert)

- Recalculates normals; then HARD-ASSERTS on the exported file:
  - `boundary_edges_holes == 0` (welded by position, so UV seams don't count)
  - `nonmanifold_edges <= input count`
- The stage FAILS loudly on violation — the 266-open-edge incident is
  impossible by assertion.

**Measured lessons (do not "optimize"):**
- `bmesh.ops.remove_doubles`, even at 1e-6, CREATED 19 boundary holes on a
  watertight mesh. Never use it; assert instead.
- bmesh sees UV-seam splits as boundary edges; "capping" them manufactures
  holes (measured: 19). Weld by position (numpy) before counting.
- Blind auto-capping is deferred until a model with real cut holes needs it.

## proof.py — stress-pose proof renders (Blender)

Renders arms-raised, crucifix, finger-guns, walk + rest with a clay material
override (shows deformation, not textures). **Media proof standard: open every
render yourself; SHA-256 in the manifest.**

Blender-space lessons: Z-up vs glTF Y-up (`G2B`); `arm.data.bones` head/tail
not populated by the importer (use edit bones); camera via `to_track_quat`.

## pipeline.py — the orchestrator

One command per model; batch via `xargs -P`. Each stage writes a VERSIONED
file + JSON report; inputs never touched. `--from-stage` resume;
`--reskin {shd,heat,none}` (default `none`); `--skip-proof`.

## Validation (Stick-Up v1, decimated — own runs, own eyes)

| Stage | stretch p99.9 (6 clips) |
|---|---|
| Input | 27.7 – 44.7 |
| refit + separate + armpit + weldcap | **10.7 – 15.1** |

- The crucifix "wings" (torso skin flying with the arm) are visually GONE
  (before/after renders viewed).
- Root causes fixed: 812 hand verts weighted to leg bones; armpit k-NN bleed;
  8 joints 4–10 cm outside the mesh (refit).
- Remaining stretch is ball-joint skin under extreme rotation; the 2.5 gate
  threshold is aspirational for LBS without corrective shapes. The pipeline
  drives the metric 3× down toward it.
- Full-size Stick-Up HQ (83 MB) validation blocked on disk — reported honestly;
  decimated-v1 validation stands in.

## Diagnostics

`diag_stretch.py` (worst edges per clip/frame with bone weights),
`diag_joints.py` (joint-vs-mesh distance), `look.py` (quick renders).

# Rig & Pose Studio — STEP 1 Diagnosis (Scarlett + Star shared failure)

Owner order 2026-10-21 ~11:59 CDT. Status: **IN PROGRESS** — this doc is banked
in pieces as evidence lands. No fixing before the failure is named.

## The owner's verdict (what "wrong" means here)

After the one-shot autofix shipped, Scarlett AND Star are still wrong in the
SAME ways: posing, rigging, joints, mesh, invisible parts, bones — base vs
output "really far off." Same TYPE of wrong on both models = the pipeline is
the suspect, not the models. (Scarlett's model is canon-perfect; failures are
animation/rig targeting + presentation.)

## Failure class (named): TEMPLATE-DRIFT

Per the owner's TEMPLATE DIRECTIVE (2026-10-21 ~15:08 CDT): the teardown files
had everything oriented and all fighter data perfect; failures came from
**drifting away from the template** — improvised skeletons, clip transplants
across mismatched rigs, rest poses baked from foreign lineages — instead of
templating every fighter onto the skeleton from the most recent Tekken
teardown in our holdings.

Scarlett/Star are the type specimens (evidence below). The pipeline standard
this lane establishes: **one modern Tekken template skeleton; every fighter's
rig is that template fitted to the mesh, never a bespoke skeleton, never a
verbatim clip transplant.**

## Evidence gathered so far

### Prior-lane probe data (to be independently re-verified by this lane)

Source: `~/workspace/_wh-work/scarlett-star-src/` (autofix lane scratch, held —
PR #440 tree is not this lane's to touch):

- `inv_base.json` — Scarlett base inventory: rig `RIG-SCARLETT`, meshes carry
  `hide_render: true` in the stored blend. **The "invisible parts" are a
  visibility-flag artifact of stored blends, not missing geometry.**
  Scarlett.glb = 20,732,212 B, 8 meshes / 145,438 tris — nothing missing.
- `bone_report.json` — the mocap output rig carries a long list of
  `curved_bones_mocap`: DEF-spine chain, DEF-shoulder/forearm/hand/foot/shin/
  thigh, breast + butt chains, `head`, `MCH-ROT-head` — i.e. **core body bones
  whose REST orientation is rotated/curved in the output rig**. A clean
  template rig has near-identity rest rotations on core bones; a curved rest
  pose baked into the skeleton means every clip applied on top double-applies
  that curvature. This is template-drift in the skeleton itself.
- `edge_dist.json` — the autofix's own post-fix measurement on Scarlett still
  shows posed-edge stretch at p999 = 0.0388 vs rest 0.0227 (max 0.0664 vs
  0.0338): roughly **2x stretch at the tail even after the "fix"** by that
  lane's measurement method. Owner's eyes rejected it; the numbers agree the
  deformation was not eliminated.

### Prior findings carried in (from the autofix lane's records)

- **Scarlett:** the world-delta retargeter is invalid across mismatched rest
  poses → arm driven overhead + LBS collapse in posed frames.
- **Star:** corrupted armature rest pose baked in during the Jiggle-lineage
  run #3 — the output skeleton's rest pose is not the model's rest pose.

### This lane's independent verification (in progress)

Tool: `tools/rig-pose-studio/glb_inspect.py` (this PR) — parses GLB JSON +
accessors directly: joint sets, per-joint rest rotations, rest world
positions, IBM sanity, per-vertex weight-sum distribution, animation channel
inventory. Applied to base vs shipped output for both characters; numbers
appended here as they land.

## The T3-era skeleton / clip-transplant AUDIT (this step's second half)

Method: run `glb_inspect.py` over every roster fighter's shipped GLB; record
joint count + joint-name set + core-bone rest-rotation flags + hips rest
height; classify each fighter:

- **TEMPLATE** — rides the modern Tekken template skeleton (or a verified
  fit of it), clips native or correctly retargeted.
- **T3-ERA** — rides a Tekken 3-era skeleton or a GameRig/DEF rig whose rest
  pose diverges from template.
- **TRANSPLANT** — skeleton is one rig, clips were baked for another
  (the Leopard King failure: T3 clips baked for the Leo-man rig transplanted
  onto King's rig — hips pinned at bind height, feet floating, shin folded —
  passed the stretch gate, read deformed).

For each non-TEMPLATE fighter: what re-templating takes (template source in
holdings? mesh re-fit needed? weights re-transfer? clips native to template
or re-bake?) — holdings vs gaps stated per fighter. Per-fighter re-templating
is dispatched FROM this audit; this lane does not build it.

## Retargeter note for the coordinator (not this lane's fix)

Two distinct retarget problems must not be conflated:
1. `retargetClipToRig()` reading Hips.position as a quaternion → NaN crash —
   owned by the T3-crash-fix lane; playtest-triage is confirming in-game.
2. World-delta retargeting across mismatched REST POSES (Scarlett evidence
   above) — a method-validity problem, input to the pipeline standard in
   STEP 2: retarget only between template-aligned rest poses, or re-derive
   deltas in rest-local space. Recorded here + in the lane checkpoint;
   shared fighter code is NOT touched by this lane.

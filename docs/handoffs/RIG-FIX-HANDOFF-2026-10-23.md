# Rig-Fix Handoff — 2026-10-23

**From:** Universal Rig-Fix agent (DoggByte crew)  
**To:** Claude's lane (PR #795 / #804 branch)  
**Date:** 2026-10-23

## Summary

The 2026-10-23 rig audit (18 models, 9 wonky cases) found 2 wonky cases on
your branch (PR #795, now merged as #804). Per the user's lane division, I
did NOT fix these — they're yours when #804 lands on main.

## Your 2 wonky cases

1. **doc-frank-a2**: finger→leg mis-weight (finger bones influencing leg verts)
2. **doc-frank-a4-transformed**: arm→leg mis-weight (arm bones influencing leg verts)

## Systematic issue: shoulder L/R cross-blend

The audit found a **systematic shoulder L/R cross-blend** across 9 of 10
#795 models: left shoulder verts weighted to right shoulder bones (and vice
versa) at ~0.15–0.25. This is not a per-model bug — it's a pipeline issue.

**Root cause hypothesis:** The skinning pipeline mirrors weights across the
sagittal plane without checking bone laterality. When a left-shoulder vert is
near the midline, the mirror operation assigns it to the right-shoulder bone.

**Universal fix direction:** In the weight pipeline, after mirroring, verify
that each vert's dominant bone is on the same side (L/R) as the vert's
position. If not, remap to the same-side bone. This is a pipeline-level fix,
not per-model.

## Tooling available

I've built universal rig-repair tools at `tools/rig-repair/` (PR forthcoming):
- `finger_symmetry.py` — detect/fix finger bone asymmetry vs T7 convention
- `weight_validate.py` — flag cross-region weights (hand/arm↔leg, L↔R bleed)
- `limb_mirror.py` — add bones + weights for duplicate limbs

These are yours to use. The `weight_validate.py` tool can detect the
shoulder cross-blend: run it with `--fix` to apply the universal repair
policy (moves suspicious cross-region influences to the dominant bone).

## Main-branch fixes (my lane, for reference)

Fixed 7 main-branch models (PRs forthcoming):
- pantera-leopard-king: LeftHandThumb3 added; leg→tail bleed fixed
- mariposa-monarch: LeftHandThumb3 added; hand→leg @0.50 fixed
- mina-ashido-a1: pinky L/R cross-contamination fixed
- parvati-a1: bilateral pinky→leg @0.37 fixed
- vixen-a1: pinky→leg + shoulder L/R @0.39 fixed
- dorowani-a1: forearm→leg @0.47 fixed
- rahkasa-a1: lower arm pair rigged (38 new bones)

## T7 finger convention (do not "fix")

Tekken 7 ships 2-segment pinkies — this is CORRECT. The defect is L/R
asymmetry (e.g., LeftHandThumb3 missing while right has it). Match T7:
3-seg thumb/index/middle/ring, 2-seg pinky, symmetric L/R.

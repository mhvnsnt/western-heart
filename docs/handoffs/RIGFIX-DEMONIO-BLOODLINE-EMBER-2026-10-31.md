# Rig fix — Demonio bloodline-ember (rig continuation Stage 1, 2026-10-31)

Lane: WESTERN HEART rig continuation (owner "H — model paths" lane,
resumed by owner order 2026-10-31). Target named by the rig sweep
(`docs/RIG-AUDIT-SWEEP-2026-10-30.md`, PR #1312): the worst measured
weight defect in the audited range. Per-character isolation: this
change touches Demonio's bloodline-ember file only, plus two shared
`tools/auto_rig` backend fixes whose need this file proved.

File: `roster/demonio/attires/bloodline-ember/demonio-bloodline-ember.glb`
(25,698,348 B before and after — the repairs patch skin accessors in
place; geometry, skeleton, materials and textures are untouched,
proven below).

## Diagnosis (all numbers re-measured by this lane on main's file)

Audit before (skin_audit.py, exit 1): FAIL on `no_dead_joints`,
`no_contamination`, `proportions_ok`. 14,498 verts, 50 joints,
contaminated weight mass **0.37875** (5,530 verts), dead major joints
**LeftUpLeg, LeftLeg, RightUpLeg, RightLeg**. Three distinct defects:

1. **The skin is L/R-mirrored in JOINTS_0.** Geometry and skeleton
   agree (finger verts sit exactly on the same-side finger joint
   heads), but the weight indices name the mirror-side joint:
   LeftFoot-dominated verts sit at mean x = +0.098 (the right side),
   a vert at (−0.819, 1.364, 0.063) is weighted 0.516 to
   RightHandThumb2. Decisive test: remapping JOINTS_0 through the
   Left↔Right name swap drops contamination 0.37834 → 0.00324
   (>100×). A prune+fill cleanup alone would have destroyed the
   authored weight gradients to fix this; the swap restores them.
2. **All four leg joints carry zero weight.** Thigh/shin verts are
   weighted to Foot/ToeBase/Hips/Spine and to `neutral_bone` (a root
   helper at the origin, 983 verts dominated, y 0.10–1.40) — the two
   upper leg segments were skipped by the original weight paint.
3. **Hips proportion flag (ratio 4.66) is a template mismatch, not
   damage.** Inverse-bind positions equal node-graph world positions
   for all 50 joints (internally consistent export); the chain sums
   coherently (Hips→Spine 0.326 m, legs 0.434/0.481, height 1.7956 m).
   This is a long-torso stylized skeleton measured against the
   Mixamo-shaped template (expects Hips→Spine ≈ 0.070 m at this
   height). Arm warnings (1.84×) are the same story: long arms by
   design. Skeleton-domain — see "Not fixed" below.

## Fixes applied (weights domain only)

1. **New tool `tools/auto_rig/backends/unmirror_weights.py`** —
   remaps JOINTS_0 through the Left↔Right joint-name swap, but only
   after measuring that the swap is a decisive win (≥10× contamination
   drop and < 1% after); otherwise it refuses to rewrite the file.
   Here: 21 swap pairs, **9,536 joint slots remapped**, contamination
   0.37834 → 0.00324. Weight values, geometry and skeleton untouched.
2. **`tools/auto_rig/backends/weight_cleanup.py` parent fix** — the
   dead-joint revival derives chain parents from CANON_CHILD, which
   maps Hips→Spine and therefore leaves `parent_joint[UpLeg]` unset:
   a dead UpLeg had no parent territory and no parent in its chain
   set, so it could never be revived (first cleanup pass revived
   both Legs, both UpLegs stayed at zero). `joint_geometry` now fills
   missing parents from the full node tree (canonical parents still
   win where both exist). This is the humanoid-general case: every
   humanoid's UpLegs hang off Hips beside Spine.
3. **Standard rigfix pass** (`tools/auto_rig/rigfix.py`, the Baek
   pipeline) on the un-mirrored file: 3,078 contaminated slots
   pruned, **5,929 verts revived** onto the dead leg joints, 526
   unweighted verts filled, edge smoothing, prune + renormalize.

## Result (re-audited by this lane on the shipped file)

| Check | Before | After |
|---|---|---|
| contaminated weight mass | 0.37875 (5,530 verts) | **0.0 (0 verts)** |
| dead major joints | LeftUpLeg, LeftLeg, RightUpLeg, RightLeg | **none** |
| weight_sum_bad / unweighted | 0 / 0 | 0 / 0 |
| folded chains / joints outside / feet planted | pass | pass |
| validate.py hard checks | — | **all pass** (valid_gltf, skinned_mesh, bones_present, height_ok) |
| proportions_ok | FAIL (Hips 4.66) | FAIL (Hips 4.66) — skeleton-domain, see below |

9 of 10 audit checks pass; both weight-domain gates are fully clear.
Minor finger joints LeftHandIndex2 / RightHandIndex2 /
RightHandThumb3 sit below the audit's dead threshold after cleanup
(they carried 19–47 total mass before; not major joints, not gated —
the same disclosure class as Baek's minor fingers).
`fingers_symmetric` in validate.py is false before and after
(pre-existing, not a regression, not claimed fixed).

**Weights-only proof:** the fixed GLB's JSON chunk is byte-identical
to the original; of 820 comparable accessors, only JOINTS_0 /
WEIGHTS_0 accessors differ — every POSITION/NORMAL/TEXCOORD/index/
inverse-bind accessor is bit-identical. Blob SHA: `02975562…` →
`65c7d10babe3b2848dccdbaa67ffa53786d47263` (sha256 after:
`e9e7b82b7f9e3de16deb6c9c5b1af42b2e962eeca0cd96aaf6e3de8715275ca5`).

**Proof renders** (proof_pose.py, same pose on both files:
LeftUpLeg:X:35, LeftLeg:X:-50, RightUpLeg:X:-25, LeftArm:X:-40;
viewed by this lane): before, the posed leg bones move nothing
(feet stay planted and symmetric) and the arm pose drags a thin
cross-body stretching bar off the opposite hand; after, the posed
leg lifts and bends and the arm swings as one piece, no stretching.
Files: `proof-before-front.png`, `proof-after-front.png`,
`proof-before-side.png`, `proof-after-side.png` beside this doc
(the tool's "back" camera is this model's true front).

## Not fixed — named blocker

`proportions_ok` still fails on Hips (ratio 4.66) with warnings on
Spine1 (1.86) and Arm/ForeArm (1.84–1.86). Per the diagnosis above
this is the skeleton's authored proportions vs the WH template, not
weight damage; this lane's mandate is weights-only and does not
alter skeletons or proportions. Clearing it needs a skeleton-domain
decision (accept this skeleton's proportions for Demonio, or a
refit) — it is recorded here as the blocker, not forced.

`neutral_bone` still carries weight on central verts (983 dominated
before; the audit does not gate helper-bone weight and cleanup's
revival only reassigns verts whose dominant joint is in the dead
joint's chain family). Disclosed, not hidden: under root-follow
animation those verts track the root rather than the spine/legs.

## Environment note

Blender proof renders on this VM need the staged EGL stack (system
libEGL.so.1 is absent): `xvfb-run -a env -u PYTHONPATH
LD_LIBRARY_PATH=~/workspace/tools/egl-stack/usr/lib/x86_64-linux-gnu
__EGL_VENDOR_LIBRARY_DIRS=~/workspace/tools/egl-stack/usr/share/glvnd/egl_vendor.d
LIBGL_ALWAYS_SOFTWARE=1 <blender> …`. Input file was fetched from
main and verified by git blob SHA before use.

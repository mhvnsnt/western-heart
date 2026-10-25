# Scarlett + Star — jiggle/mocap stack upgrade (2026-10-20)

Owner order (2026-10-20 ~20:11 CDT): "Those need to be improved, and tested on
Scarlett and Star, and pulled in with open source and industry standard full
stack fixes — no more hand tooling bullshit." ("Those" = the lambada mocap set
+ the Wiggle 2 proofs, incl. PR #380's rejected video.)

## What was wrong with the old proofs (recap)
- PR #380's video was rendered at 320×320 in a near-black world from the
  dance's deepest back-arch frames — the character was unreadable; the jiggle
  itself was fine but unjudgeable. Full diagnosis:
  `docs/scarlett-proof/DIAGNOSIS-scarlett-proof-380-2026-10-20.md` (PR #395).
- Star's earlier demos came from a hand-rolled spring script; the "dance" in
  `star-jiggle-baked-v3.blend` is nearly static (its action animates only Hips
  location + Spine2 + the jiggle bones) — no real mocap on the body at all.

## The stack now (all open source, all wired into production runs)

| Layer | Tool | Source / license | Role in these proofs |
|---|---|---|---|
| Runtime | Blender 4.2.23 LTS | blender.org, GPL | bake environment (Jiggle Physics needs ≥4.2) |
| Jiggle physics | **Jiggle Physics v4.5.3** (naelstrof) | github.com/naelstrof/blender-jiggle-physics, GPL; official Blender Extensions platform | Verlet spring solver — the maintained Wiggle 2 fork, same solver family as Unity Jiggle Physics; collision + squash/stretch support |
| Mocap retarget | repo delta-math retargeter (PR #364 method) | in-repo | Star: CMU BVH → StarRig via `star_retarget_delta.py`; Scarlett: her existing MocapRetarget action (hash-audited in run #3) is kept — re-retargeting a verified action would change approved motion, not improve it |
| Mocap retarget (evaluated, rejected) | **Rokoko Studio Live Blender plugin** | github.com/Rokoko/rokoko-studio-live-blender | Scripted headless fine (90 fcurves / 22 bones), gross pose reads clean — but it TEARS this rig: a mixed-weight patch (UpperArm/ForeArm/Shoulder blend) rips into a ribbon across the face in motion. Bisected: present with the jiggle layer muted, absent at rest, absent under the delta-math retarget on the same frame. Rejected by measurement for StarRig, same as Keemap before it. Driver kept in repo as the evaluation record (`star_retarget_rokoko.py`) |
| Rig/weights | existing production rigs | in-repo | Scarlett RIG-SCARLETT (production skinning, PR #364 diagnosis); Star StarRig + 7 Jiggle_* bones (inverse-distance weights, jiggle-work 2026-10-19) |

Paid tools evaluated and excluded (not open source): BoneDynamics Pro,
SpringFX, Auto-Rig Pro, mimem Mocap Blender. Keemap stays rejected by
measurement (PR #377, owner: leave open as the record).

## Parameters — no hand-tuned numbers
Jiggle Physics ships author presets; these proofs use them **verbatim**:
- Breast preset (breast + butt/glute/thigh chains): root elasticity 0.9,
  angle 0.8, length 0.9, soften 0.5, gravity 0.0, drag 0.0, friction 0.1.
- Tail preset (Scarlett's DEF-tail chain — new in this stack; PR #380 never
  simulated the tail): root 0.9, angle 0.6, length 0.9, soften 0.1,
  gravity 0.5, drag 0.2, friction 0.4.
Bake preroll 24 frames. The jiggle bake writes ONLY jiggle-bone curves into a
separate `JiggleAction`, layered over the base action via NLA — the base
mocap action is never modified.

## Verification (both characters)
- Face integrity: the baked JiggleAction contains **zero** face-bone fcurves
  (Scarlett: 270 curves, all on the 27 jiggle bones; Star: 70 curves, all on
  the 7 Jiggle_* bones). On Scarlett, no face curves exist in either action at
  all — the face was never keyed by anything in the chain.
- Star retarget: delta-math produced `MocapRetarget` (220 fcurves, all 22
  base bones keyed loc/rot/scale, frames 1–72). Test frame 24 rendered +
  viewed: full-color Star mid-dance, skin intact everywhere — the same
  frame tears under the Rokoko action. (A world-space delta simplification
  was also tried and exploded the mesh; the local-rest-relative formulation
  is the correct one and is what the tool implements.)
- Foundations stored before work: releases `scarlett-source-blends-v1` and
  `star-source-blends-v1` on this repo (API size-verified, pull-back
  sha256-verified for Scarlett base; Star sha256 recorded at upload).

## Pipeline notes (environment)
- Blender 4.2 quirk found during the Star work: removing the imported BVH
  armature before saving makes `save_as_mainfile` fail with
  "Operation not permitted"; saving with the source armature still in the
  scene works (the tools save first, removal is optional cleanup).

## Pipeline note (render environment)
Bakes run on Blender 4.2.23 (required by Jiggle Physics). Proof renders run
on Blender 4.0.2: EEVEE Next under this VM's software GL (llvmpipe) was
OOM-killed repeatedly at render time, while 4.0's EEVEE renders the same
files reliably; the 4.2-saved blends open in 4.0 without data loss for these
scenes. Renders use the soft-studio setup from the v2 re-proof (bright
world, large area key/fill/rim, sun) so the characters are judgeable.

## Tools added to the repo by this lane
- `tools/jiggle/jiggle_physics_bake.py` — generic Jiggle Physics bake +
  fcurve-digest verification + optional NLA layering (configs: scarlett, star).
- `tools/anim-retarget/star_retarget_delta.py` — production Star retarget
  (local-delta math, BVH → StarRig bone map).
- `tools/anim-retarget/star_retarget_rokoko.py` — the Rokoko evaluation
  driver (kept as the record of the rejected path).
- `tools/jiggle/render_soft.py` — the soft-studio proof renderer used for
  the v2/v3 proofs (bright, framed on evaluated bounds).

## Addendum — Star's face, investigated to ground (2026-10-20, late)
In the delta take's front stills, Star's bowed face reads as a pale column in
front of the face at small size. Because the Rokoko take had genuinely torn
this area, the reading was investigated with five independent checks on the
delta file: (1) edge-stretch audit — 14 mildly stretched verts total (feet /
spine joints), none facial, vs 1,068 in the Rokoko file; (2) head-bone-space
rigidity — head-region verts move ≤0.022 rig units relative to the Head bone
(rigid, as skinned); (3) spike-region occupancy — zero verts occupy the
protrusion volume beyond the posed mesh itself; (4) right-arm paint test —
the shape is not the arm crossing; (5) dominant-bone-group color render —
the silhouette is continuous with the head and colored as Head/Neck groups.
Conclusion: the geometry is sound; the reading is the lambada's deep head
bow + turn acting on the sculpt's strong nose/lip profile at proof
resolution. No fix was applied because no defect exists in the data — the
Rokoko take's measured tearing (the real defect) is absent here.

## Honest limits
- Scarlett's surviving local blends are a reduced working copy whose body
  materials resolve to a black-and-white vertex-color pattern — no skin-tone
  layer exists in the file (see PR #395 diagnosis). The full-color master is
  the TeraBox `Scarlett_tqZQxX.blend`, still blocked on a TeraBox session.
  No recolor was fabricated.
- Star renders in her true Tripo colors (packed 4K PBR in the foundation
  file).

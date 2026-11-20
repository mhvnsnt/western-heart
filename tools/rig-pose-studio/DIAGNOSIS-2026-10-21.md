# Rig & Pose Studio — STEP 1 Diagnosis (Scarlett + Star shared failure)

Owner order 2026-10-21 ~11:59 CDT. Status: **STEP 1 COMPLETE** (diagnosis +
audit below, measured by this lane 2026-10-21). STEP 2 (stack) in progress.

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

### This lane's independent verification (measured 2026-10-21, this lane)

Tool: `tools/rig-pose-studio/glb_inspect.py` (this PR). Raw reports banked in
`tools/rig-pose-studio/audit/`.

**Star — SHIPPED in-game model** (`game/assets/models/star.glb`, 904,980 B,
Blender I/O export): **33 joints; nearly every core joint carries a large
constant REST rotation** — Root 120.0°, Hips 120.05°, Spine2 119.64°, Neck
126.77°, Jaw 111.39°, Left/RightShoulder 170.95°, Left/RightUpLeg ~177°,
Breasts ~179°, Hands ~90°. Rest world positions: Hips at y = −0.074, feet at
y = −1.003 — **the figure hangs DOWNWARD in −Y from the origin**: a Z-up
authored figure exported without a clean axis conversion, the conversion
smeared per-bone into rest rotations instead of applied once at the root.
Weights are clean (sums = 1.0, ≤4 influences) — the mesh and skinning are not
the problem; **the skeleton's rest frame is**.
Contrast: Star's rated-M lineage rigs (`star-nojiggle.glb`,
`star-attire-ratedm-nude-rigged.glb`, pygltflib path) measure **0 core
rest-rotation flags** — a clean-rest Star skeleton exists; the shipped game
file is from the drifted lineage (the "corrupted rest pose, Jiggle run #3"
finding, now measured directly).

**Scarlett** (`Scarlett.glb`, 20,732,212 B — the canonical file): **1,111
joints, 1,121 nodes, 8 meshes** — a complete Daz Genesis 9 figure with a
Rigify-style ORG/MCH/DEF/c_* control rig. Weights clean (normalized,
≤4 influences on the body). Her rig is a legitimate professional rig — and
nothing like any skeleton the game was built for. The large rest rotations
(DEF-spine 90°, breast/face control bones 140–180°) are Daz/Rigify bone-roll
CONVENTIONS, not corruption. **Scarlett's base is not broken; she was never
template-normalized.** Note: she has **no model in `game/assets/models/`** on
main at all — her in-game presence rides entirely on the unmerged PR #440
attire tree.

**Neither file contains any animation.** All motion is applied at runtime by
the game's clip banks + name-map retargeting. Every posing wrongness the
owner sees is generated at that boundary.

### THE SHARED FAILURE (named, with the mechanism)

> **The pipeline has no template-normalization step.** Models enter with
> whatever skeleton, rest pose, axis convention, and bone-roll convention
> their source used, and the same clip banks are then retargeted onto all of
> them by bone NAME. Retarget math that is valid only between rigs sharing a
> rest pose is applied across rigs that share nothing but names.

- Scarlett = the extreme case: a 1,111-bone Daz/Rigify rig receiving clips
  baked for ~49-bone game rigs via a name map + world-delta retargeter that
  is **invalid across mismatched rest poses** (autofix lane's finding;
  consistent with the rest-pose measurements above) → arm overhead, LBS
  collapse, "contorted."
- Star = the same missing step from the other side: her shipped skeleton's
  rest frame itself is drifted (baked axis conversion, inverted world frame),
  so even name-correct clips land on joints whose rests are pre-rotated
  90–180° → twists and folds that read as rigging/mesh damage.
- Same missing step, same family of symptoms — posing, joints, bones,
  "invisible parts" (hide flags in stored blends), mesh reading as damaged.
  **This is TEMPLATE-DRIFT as a pipeline property, not two model defects.**

## The T3-era skeleton / clip-transplant AUDIT

Full sweep: `tools/rig-pose-studio/audit/roster_sweep.json` (57 shipped
models in `game/assets/models/`, measured with `glb_inspect.py`).

**There is no roster skeleton.** Joint counts: 49 (×21), 50 (×20), 33 (×3),
32 (×1), and one-offs at 109/142/160/174/178/244/246/311/328, plus 3 models
with **no skin at all**. Classes:

| Class | Files | What they ride | Re-templating takes |
|---|---|---|---|
| HOUSE-49/50 (41) | awa-pop, baek, cape-jones, demonio, dxmmii, jin(-body), kai-body, kiko-tanaka ×2, king-tyrant ×2, kinpo(+alt), lili, mariposa, n3g4tiv0, nightwolf, pantera ×4, phantom, purple-rain ×2, rave, retsu-body, rin-body, saku-ra ×3, sam-ur-a1 ×2, sha-body, skull, steve-fox, thor, waterfall, zen-body, zui ×2 | The de-facto house rig (King-family 49-joint + 1-joint variants; uniform 7–8 rest-flag signature = shared conventions). Leopard King lane verified A1/A3 joint-by-joint = **T7 King's canonical 49-joint rig**. | None for the skeleton — this family IS the anchor. Clips must be native or rest-locally retargeted per rig (the T3-bank transplant problem: T3 clips were baked for the Leo-man variant of this family and fold other members — see TRANSPLANT note). |
| MINI-33/32 (4) | **star**, michiko, torch (33), diablo (32) | Daz-style mini rigs; 16–18 of ~33 core joints rest-rotated (baked axis conversion, cf. Star measurements above). | Full re-template: fit template skeleton, re-transfer weights, discard drifted rests. Meshes are small (1 mesh each) — cheapest re-templates on the roster. |
| FOREIGN-BIG (9) | bruno 142, cyborg-x 160, dio 174, doc-frank 178, kinpo-t8 244, zafina 246, phantom-t8 311, yukihyo 328, sun-ra 109 | Source-game / UE rigs, each its own convention (incl. raw T8 exports). Doc Frank's non-standard bind locals (Spine1 90° X, Hips 180° Z) already produced the folded-torso defect via fighter.js stage-2 — same class. | Re-template onto the house skeleton (fit + weight transfer from the foreign rig as donor), OR keep the rig and generate a per-rig rest-local retarget profile. Template-first is the standard; per-rig profiles are how we got here. |
| UNSKINNED (3) | scimitar, sun-ra-base, thor_alt1 | No skin — static meshes wired as fighters. | Rig from template via the intake pipeline (PR #456's one-command tool is the current path; STEP 2 evaluates it). |
| OFF-ROSTER (1) | **scarlett** (1,111, Daz G9 + Rigify control rig) | Not in `game/assets/models/`; PR #440 attire tree only. | Do NOT shrink her rig to the template by deletion — she is canon-perfect. Correct treatment: template-side adapter — retarget in rest-local space against her DEF skeleton with a verified bone map, or bake clips onto her rig offline through the full stack (STEP 2). The pipeline adapts to her; not the reverse. |

**TRANSPLANT note (clips, not skeletons):** most shipped GLBs carry 0
animations; clips live in runtime banks (T3 banks especially) that were
baked against ONE member rig and are applied across the family. The T3
retarget crash is the T3-crash-fix lane's; the Leopard King lane owns the
T7-King re-anchor. This audit's dispatchable output: the MINI-33/32 and
FOREIGN-BIG re-template list (13 models) + the UNSKINNED rig list (3).

**Template-standard gap (for STEP 2):** the repo's own
`tools/auto_rig/backends/skeleton_template.json` is a **52-joint Mixamo-style
T-pose** skeleton — Mixamo convention, not Tekken. The owner's standard is
the most recent Tekken teardown skeleton. Holdings check: T7 teardown is in
the repo (`teardown/tekken7/`), the house-49 family is verified T7-King —
so a fitted, proven Tekken template exists in practice. T8 models exist in
holdings only as raw UE exports (kinpo-t8, phantom-t8, yukihyo) — no fitted
T8 template skeleton has been extracted yet. STEP 2 sets the standard
explicitly: house template = T7-King-family skeleton (fitted/proven),
with T8 template extraction logged as the gap to close.

## Retargeter note for the coordinator (not this lane's fix)

Two distinct retarget problems must not be conflated:
1. `retargetClipToRig()` reading Hips.position as a quaternion → NaN crash —
   owned by the T3-crash-fix lane; playtest-triage is confirming in-game.
2. World-delta retargeting across mismatched REST POSES (Scarlett evidence
   above) — a method-validity problem, input to the pipeline standard in
   STEP 2: retarget only between template-aligned rest poses, or re-derive
   deltas in rest-local space. Recorded here + in the lane checkpoint;
   shared fighter code is NOT touched by this lane.

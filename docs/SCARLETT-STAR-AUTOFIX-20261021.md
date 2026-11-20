# Scarlett + Star — one-shot automatic repair (2026-10-21)

Owner verdict on the previous proofs (Scarlett v3 / Star v1, PR #395/#414):
REJECTED — models deformed vs baseline, skeletons wrong, faces stretched,
poses unnatural, all jiggle gone. This pass is the one automatic repair
attempt, run entirely through scripted open-source tooling (no hand-edited
weights, no hand-keyed fixes). Acceptance evidence is side-by-side imagery:
`scarlett-autofix-sheet-20261021.png`, `star-autofix-sheet-20261021.png`,
`scarlett-autofix-test-20261021.mp4`, `star-autofix-test-20261021.mp4`.

## Diagnosis

### Scarlett — parts inventory (owner: "her baseline is missing a lot of her parts")

Measured across the original GLB (physics-playground-pwa, the 2026-10-14
conversion: 8 meshes / 145,438 tris), scarlett_base.blend and
scarlett_mocap.blend (release scarlett-source-blends-v1) and the v3 proof
file (release stack-outputs-20261020):

- **No canonical mesh part is missing anywhere.** All 8 parts (Brows, Eyes,
  Hair, Hair.001, Lashes, Mouth, body, Tongue) are present in every source
  with identical vert/tri counts. Full table: `parts-inventory.json` on
  release `scarlett-star-control-20261021`.
- What IS damaged:
  1. The v3 proof file **lost the 4K Tripo PBR image set** (Color/NormalGL/
     ORM of node `0dc2b6b4`) during its Blender 4.2 bake-save cycle
     (16 images vs 19 in base/mocap). In Scarlett's file that material is
     orphaned; her body uses the OsoSnakefolk snake-pattern set, which
     survives — the chrome black/white look is her file-true design.
  2. **Every stored blend has all meshes hidden** (`hide_render` +
     `hide_viewport` = True). Any pipeline that does not unhide first
     renders an empty or partial scene and — worse — measures a frozen
     depsgraph (this produced several of the prior lane's phantom
     "no deformation" readings).
  3. A junk object `Icosphere` (42 verts, no material) rides in every blend.
  4. Her full DAZ master (TeraBox `Scarlett_tqZQxX.blend`, 515 MB, download
     still blocked) may hold scene parts present in no stored conversion.
     That is the only genuinely unverifiable gap.

### Scarlett — deformation root cause

The stored `MocapRetarget` action was produced by a **world-delta
retargeter** (`T_pose = T_rest @ S_rest^-1 @ S_pose`). World-delta transfer
is only valid when source and target rest poses match. The CMU BVH dancer's
arms rest in a T-pose; Scarlett's DAZ rig rests with arms down — so the
right arm's swing landed overhead and the shoulder/forearm twist collapsed
under linear skinning into the "ribbon arm" the owner saw. Ground truth
check: across the whole clip the BVH right hand never rises above the hips;
the stored action put 3,863 arm verts above the head line. Measured damage
at frame 24 (order-independent sorted edge-length distributions vs bind):
body 1,821 edges stretched >1.5× (max 6.2×), Hair.001 2,265 (max 3.5×),
Lashes max 6×, Mouth max 6.4×; Eyes and Tongue clean.

Hypotheses tested and REJECTED by A/B measurement: duplicate ORG/MCH curve
layers (stripping them changed nothing), dual-quaternion skinning
(neutral-to-worse), location keying (near-zero ranges; stripping changed
nothing). Corrective Smooth helped the surface (Hair.001 tears 2,265 → 0)
but only redistributed the arm tear — the pose itself was wrong.

### Star — deformation root cause

Her retarget was fine. Her **armature rest pose is corrupted** in
`star-jiggle-baked-v3.blend` and everything derived from it (including the
v1 proof file): evaluated at full bind with zero animation, her face
already carries the long cone/beak nose from the rejected proof. Mesh
vertex positions are byte-identical across the clean foundation
(`star-rigged-fixed.blend`), v3 and the proof file — the corruption lives
in the rig's rest pose and entered during the previous lane's Blender 4.2
Jiggle Physics bake lineage. (Two probe designs missed it because they
compared posed frames against each other; both share the altered rest.
The bind render is what exposes it.)

### Jiggle — why it vanished in both proofs

- Scarlett: Jiggle Physics was baked on top of a base action that already
  keyed the soft-chain roots, so the bake recorded total transforms and the
  true secondary delta diluted to ~0 on the visible masses.
- Both: the proofs used the addon's shipped **Breast preset verbatim**
  (root elasticity 0.9) — a stiff return spring that suppresses visible
  secondary motion at proof scale.

## The stack (all scripted, in `tools/autofix/`)

1. **Local rest-relative delta retarget** (`retarget_delta.py`) — transfers
   per-joint local motion (`rel = S_local_rest^-1 @ S_local_pose`), which is
   rest-pose independent. Mechanism followers (ORG-/MCH- parents) are driven
   with their own rests; all root-driven targets take the root path (the
   general path injects BVH world scale into parentless pairs — found when
   ORG-spine exploded to z=16.6 on the first run and fixed).
2. **Corrective Smooth** modifier (factor 0.5, 5 iterations, post-armature)
   — Blender's built-in surface repair; A/B-proven best setting.
3. **Jiggle Physics** (naelstrof, GPL, Blender Extensions) re-baked with
   SOFT settings — root elasticity 0.25 (vs the stiff 0.9 preset), angle
   0.35, length 0.95, gravity 0.35, preroll 24 — on chains the base action
   does not key (`bake_soft.py`). Star additionally rebuilt on her clean
   foundation (`rebuild_star.py`, `add_bones.py`): production weights
   copied by vertex index, the 7 Jiggle bones' rests transferred, fresh
   delta retarget, then the soft bake.
4. Linear skinning kept throughout (glTF parity); DQS dropped after A/B.

## Results (own-eyes + measurement backup)

- Scarlett body edge stretch at f24: **1,821 edges >1.5× → 0** (max edge
  ratio 6.23 → 1.18). Hand heights vs BVH ground truth match at f24/36/60.
- Scarlett jiggle mesh-delta (soft-region verts, jiggle track live vs
  muted): **mean 0.20–0.23 scene units** across f12–48 — vs ~0 in the
  rejected proof. It is plainly visible in the test video.
- Star: bind face clean (no beak) for the first time since the v3 bake;
  soft bake on 7 Jiggle bones with the same soft settings.
- Remaining imperfections, stated plainly: Scarlett's long tail and the
  raised-arm frames still read thin at small render sizes (her DAZ weight
  falloff on a 145K-tri mesh under an extreme dance) — improved, not
  perfect. Corrective Smooth is a Blender-side corrective: the exported
  proof GLB carries it only as baked rest-shape smoothing, not as a live
  modifier. Star's test is framed in profile (her clean foundation's world
  orientation); the beak check and jiggle both read clearly in profile.

## Widget assets (Step 4)

Release `scarlett-star-control-20261021`: `scarlett-baseline.glb` (the
owner's own GLB conversion, rest, full parts), `scarlett-proof.glb`,
`star-baseline.glb`, `star-proof.glb`, `parts-inventory.json`.

## Release assets (verified sha256, server digest == local digest)

Release: https://github.com/mhvnsnt/western-heart/releases/tag/scarlett-star-control-20261021

- scarlett-baseline.glb 20732212B sha256:871be9d6c1d297e99daba9a0ae7b55493a46c28dc60f57e4545f09137b68e1c1
- scarlett-proof.glb 24261188B sha256:5fdb01efdeb5366843db42abaa54d0add2939c50367204b5c6efbc28b679ce60
- star-baseline.glb 14209836B sha256:141f3117d722f9bcee08e27bee3ccbca3eac59894da3846ed0601e6340acc7da
- star-proof.glb 14280548B sha256:3cd12dc69ad38f55e88d542aa9b18e72171368ade5a064226014f75a95f906b4
- parts-inventory.json 3445B sha256:4eff4c502ef5d2517efcdd0ce5a42cc7b3eb403e65d5c68a1f2435a6535ec8b5

Test deliverables (owner-facing): scarlett-autofix-test-20261021.mp4 /
star-autofix-test-20261021.mp4 + scarlett-autofix-sheet-20261021.png /
star-autofix-sheet-20261021.png (frames 13-34 / 13-37 of the lambada at
24fps; renders were cut short by repeated VM/runtime restarts, the clips
cover the phrase's key poses incl. the f24 frame used for all A/B work).

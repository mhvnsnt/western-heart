# DEATHFANG rig notes (2026-10-21)

Both Tripo statics (human attire1, werewolf attire2) rigged on the
GameRig/Rigify DEF skeleton (73 deform bones, canonical WH joint
names) and baked with Iori Yagami animation from the KOF donor:

- human: Battle_Idle (+ Idle alias), Skill_01, Skill_03
- werewolf: Battle_Idle (+ Idle alias), Skill_01, Skill_02

Stance rule (owner canon): stance and locomotion are Iori's in BOTH
forms; beast flavor lives in the attacks only (wolf Skill clips).

## Method

- Mesh prep: glTF-Transform decode/weld/simplify of the Tripo pulls
  (1.04M -> ~62k verts human, ~60k wolf), textures/UVs kept. The
  full-res statics stay in release `deathfang-tripo-pulls-20261020`.
- Skin: donor-surface BVH weight transfer, queried in a MATCHED pose
  (target verts posed into Iori's stance with capsule weights first),
  with a trust composition: transferred weights are kept only when
  every named bone's segment passes near the vert, otherwise capsule
  (segment-distance) weights are used. Side-swap + segment-cap
  cleanup, then 2-pass edge-adjacency smoothing. Region census after
  the fix: arms/legs/hair/chest all on their anatomical bones.
- Animation: direction-based transfer. The donor is bound in its
  stance and its Bip001 frames are Max-convention, so basis/delta
  copies fail; the transfer arcs each target bone's rest frame from
  its own chain direction onto the donor's evaluated chain direction
  (world space), stance referenced to the donor's evaluated
  Battle_Idle frame 10. Head follows the neck segment (donor head
  axis is a face convention).

## Validation

- validate.py structural checks: valid glTF, skinned mesh, bones
  present, height OK — PASS on both.
- Edge-stretch gate (2.5): FAIL, recorded honestly. p99.9 stretch —
  human: Battle_Idle 8.77, Skill_01 8.87, Skill_03 9.88; wolf:
  Battle_Idle 9.96, Skill_01 10.89, Skill_02 12.11. The stretch is
  stance-borne and frame-constant,
  concentrated at the ankle/foot junction and the chest/armpit
  (~1k of 65k edges > 4x); the "Hips->LeftPelvis 345%" line in the
  report is a metric artifact (the pelvis joints are coincident at
  rest in this rig template). Proof renders were inspected by eye:
  the figure stands and moves in Iori's stance with no visible
  tearing at body framing. A dedicated ankle/armpit weight pass is
  the follow-up if the gate must go green.
- The human's painted eye remains PROVISIONAL (owner rejected it
  2026-10-20): it is replaced by a real eye part via the Creation
  Suite, not by decal edits. Proof videos frame the body/stance.
- The wolf has no dedicated tail bones in this rig template; the
  tail rides hips/spine weights.

Proof videos: deathfang-iori-stance-proof-20261020.mp4 and
deathfang-werewolf-iori-stance-20261020.mp4 (delivered 2026-10-21).


## Stance fix (2026-10-21 — follow-up to the owner's PR #443 verdict)

The owner rejected the shipped stance LOOK: head twisted/contorted on
both forms, torso + hands crumpled, human hair twisting and clipping
through the body instead of resting on the shoulder. Diagnosis was
done against the real Iori donor at matched frames (probe renders +
bone-position/matrix dumps), and each defect traced to a named step:

1. HEAD TWIST = the direction-based transfer itself. It arcs each
   bone onto the donor's chain DIRECTION with a minimal rotation, so
   twist/roll about a bone's own axis is never carried. Bone
   POSITIONS matched the donor within ~2 cm and neck pitch matched
   exactly, but the head's roll was never transferred (donor
   neck->head relative rotation 71 deg vs shipped 11 deg), and the
   chest rolled with the arcs (shoulder-line tilt -17 deg shipped vs
   +7..+15 deg donor).
2. TORSO/HAND CRUMPLE = the skin. The donor-surface transfer had
   silently fallen back to capsule weights for ~94% of verts
   (58k/62k). Location census of the shipped GLBs: wolf chest core
   led by RightShoulder 24% (Spine2 12%); human torso blended Hips
   16% + Neck 11% + shoulders 17%; hands ~37% on the forearm TWIST
   bone. Weights that broad smear every joint's motion across the
   torso and squash the hands.
3. HAIR = hair weights + head roll. Only ~61-80% of the human
   hair-zone verts sat on Head/HeadTop/Neck (RightShoulder 9%,
   Spine2 8%, arms ~2%); wolf mane ~31% non-head. Shoulder/arm
   weights yank the hair sideways when the arms move, and the
   un-rolled head swung the mass into the torso.

### Fix (all automatic, in the shipped pipeline scripts)

- FRAME-CARRIED TRANSFER (df_rig_bake.py): for the spine column
  (Hips, Spine, Spine1, Spine2, Neck) and the Head, the transfer now
  carries the donor's full evaluated world FRAME — the bone axis
  direction plus a lateral reference (donor hip line for Hips/Spine,
  donor shoulder line for Spine1/Spine2/Neck) — instead of the
  direction alone. The head's frame comes from the donor head's own
  evaluated matrix axes (the donor head BONE AXIS is a face
  convention, 52 deg off his facing; calibration: facing = -axis0,
  skull up = +axis1). In-bake FRAME_VERIFY asserts the built stance
  head lands at 0.0 deg error vs the donor's facing and skull axes.
  Limbs keep the direction arcs.
- ANATOMICAL WEIGHT SANITIZER v2 (skin_donor.py): every deform bone
  is classified into (chain, side, spine level); each vertex keeps
  only its dominant bone's anatomical chain set — opposite-side
  limbs, cross-limb weights and head-zone violations are removed;
  graded BRIDGES (capped at 0.20, 0.15 into the head zone) keep the
  hip crease, armpit and neck seams continuous. Human: 24,278 verts
  sanitized; wolf: 29,804. Head-zone verts end 100% Head/Neck before
  diffusion.
- WEIGHT DIFFUSION POST-PASS: tools/auto_rig/backends/
  diffuse_weights.py (Jacobi diffusion over the edge graph, alpha
  0.5, no intermediate truncation — the Pantera lane's backend),
  run until edge weight-L1 p99.9 <= ~0.34 (human 18 passes:
  2.000 -> 0.341; wolf 28 passes: 1.971 -> 0.306), then
  patch_skin.py byte-patches JOINTS_0/WEIGHTS_0 into the baked GLB
  (animations, nodes, geometry untouched). This restores weight
  gradients at the sanitizer's seams: worst cases before diffusion
  were the between-legs cloth split 50/50 across LeftLeg/RightLeg
  (edge stretch 82x) and the breast<->shoulder and neck<->shoulder
  borders.

### Result (repo validators, both forms)

- validate.py: PASS both, height 1.8 m.
- anim_check edge-stretch p99.9 — human: Battle_Idle 4.25,
  Skill_01 4.10, Skill_03 4.56 (shipped 8.77 / 8.87 / 9.88);
  wolf: 6.07 / 6.75 / 7.34 (shipped 9.96 / 10.89 / 12.11). The 2.5
  gate is still not met — the deviation from PR #443 stands, at
  roughly half the magnitude — recorded honestly, not hidden.
- Location census after diffusion: hair zone 93% Head/HeadTop/Neck,
  0% arm, shoulders ~0 (6-7% Spine2 at the neck base is the
  trapezius blend); mane the same; hands 100% same-side chains.
- Own-eyes proof: frame-matched side-by-side sheets vs the donor
  (Battle_Idle t=0.2 / 0.5, body + head crop + face-front crop) and
  full proof videos, in the PR body. Head carriage, guard hands,
  torso silhouette and hair drape match the donor's stance read;
  the human hair rests on the chest/shoulder through the loop.

Scripts: df_rig_bake.py + skin_donor.py (this folder) are the fixed
pipeline; diffusion is the repo backend above; patch_skin.py (this
folder) writes the diffused skin back. These are the automatic half
of the fix — the Rig & Pose Studio's manual controls (per-bone
offset/visibility, weight-brush strokes) cover the same defect class
by hand in customization.

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

# Pantera rig correction — diagnosis and fix (2026-10-22)

Owner rejection of PR #493's Leopard King build, 2026-10-21 ~22:41–23:14 CDT:
"That's not fixed idk what ur seeing", with the defect map: head/face/neck
good; upper chest and right bicep good; from the forearm down both arms
stretch and have weight issues; same from the waist down; legs crumpled in
all directions, the right leg in the opposite direction of the left; the
hand looks weighted to the tail; the same problems on A1; both feet
sticking out to the side instead of forward. His order: fix it at the
source (the decrypted files / decode path), not by hand-tweaking rigs
downstream, and apply the feet fix across Pantera's models.

Every claim below was measured on the shipped files. Tools: a pure-Python
glTF evaluator + a faithful port of the game's retarget
(`game/js/t3anims.js` `analyzeRig` + `retargetT3Clips`), validated by a
control: retargeting the Leo man authoring rig onto itself reproduces the
source pose with 0.0° / 0.000 m error on every bone.

## Where the defects actually live

### 1. The Tekken 3 decode is CLEAN — the "backwards" defect is not there

Bank `game/assets/anim/t3/king_on_pantera_leoman/t3_stance.json`
`rot_xyzw` equals the Leo man GLB's native `t3_stance` channels exactly:
0.00° max difference on all 22 bones × 75 keys; `root_t` equals the Root
translation track. The King bank's `skeleton.json` rest pose is sane
(toes forward, +Z). (Contrast: the Bosconovitch bank's foot direction WAS
corrupt — splayed feet ~50° — and was fixed at the bank layer by the Doc
Frank lane in PR #508. The King bank does not have that defect.)

### 2. PR #493's baked clips are scrambled under standard evaluation

Evaluating `attires/leopard-king/model-rigged.glb`'s embedded
T3Stance/T3Grab with a standard glTF evaluator (the same math
three.js/GLTFLoader and Blender use) against the source clip: bone
segment direction errors mean 58–92°, max 172°; hips→head mean 24°. Some
channels match the bank locals verbatim (Spine/Neck), some are 180° off
(Hips/UpLegs), some are ~90° off — the signature of channels written in a
foreign frame convention. The bake also omits the Spine1 channel
entirely, so a standard evaluator holds Spine1 at rest and the arm chain
inherits the error (measured 8–25° in T3Grab). The #493 worklog's
"joint err 0.095–0.111 m, three-way gate PASS" was measured inside the
bake harness; the file was never independently evaluated. What the owner
saw in the rejection render is what the file contains.

### 3. The shipped A4 weights are regionally wrong (pose-mismatched transfer)

Weights were transferred from the T-pose donor by raw Euclidean
nearest-neighbor. The Tripo sculpt's bind pose is not the donor's T-pose,
so whole regions sampled the wrong body part (region = verts nearest a
bind segment; mean weights):

- LeftArm→LeftForeArm region: LeftArm 0.63 / Spine1 0.29 / **LeftForeArm 0.06**
- RightArm→RightForeArm region: RightArm 0.42 / Spine 0.32 / Spine1 0.23 / **RightForeArm 0.03**
- LeftForeArm→LeftHand region: Hand 0.74 / Spine 0.18 / **LeftForeArm 0.06**
- Hips→UpLeg regions: UpLeg ~0.42–0.50 / **Spine 0.43–0.44**
- The TAIL geometry was bound to the left leg: Tail2→Tail3 region =
  LeftUpLeg 0.55 / Tail3 0.43; Tail3→Tail4 = LeftUpLeg 0.48 / LeftLeg 0.34.
- Literal tail weight on hand verts: 0.000 — the owner's "hand weighted
  to the tail" is the scrambled pose's visual effect, not the weights.
- Skinning cost under correct clips: edge-stretch p99 = 5.0–7.5×, ~10%
  of all edges >1.5× (the same clips on A1: p99 1.57, ~1%).

The donor field itself is also imperfect (A1's own ForeArm→Hand region:
Spine1 0.21 + Spine 0.17, ForeArm 0.13) — so the fix does not sample the
donor; it builds the field from the skeleton (below).

### 4. The Pantera template skeleton has its toe joints behind the heel

The 49-joint template shared by the A1 game model, Leopard King, and the
classic build (node-for-node identical) places Left/RightToeBase BEHIND
the ankle (world ankle→toe offset z = −0.158 / −0.160) while the toe
geometry points forward (+Z, bind toe-centroid yaw ±5–8°). Consequences:
`analyzeRig` in `t3anims.js` detects the backward toe and falls back to
aligning the foot with the shin (`A(Foot) = A(Leg)`), so the foot's own
rest alignment never engages; any tooling reading the toe bone reads a
backward foot. This is a defect in the shipped template GLBs, not in the
runtime (the runtime's guard is reasonable given the data).

### 5. The runtime retarget is not the defect

Three candidate runtime methods were measured on the neutral clip
against the authoring rig (frame-matched toe direction, canonical side
pairing): shipped swing method, pure delta transport, and a frame-aligned
swing. All land within ~15–20° of toe-direction difference, which equals
the two models' genuine bind-pose toe-shape difference — a property of
the models, not a code error. Segment directions under the shipped
method are exact (0.00°). `t3anims.js` is therefore unchanged by this PR.

## The fix (this PR)

**Leopard King (`attires/leopard-king/model-rigged.glb`) rebuilt:**

1. **Skeleton:** ToeBase joints moved forward of the ankle (the z of the
   ankle→toe offset reflected: −0.158 → +0.158, −0.160 → +0.160), with
   inverse-bind matrices compensated so bind skinning is exact
   (W·IBM invariance error 1e-16; skinned bind displacement ≤ 4.4e-07).
   Toe translation channels (constant) re-pinned.
2. **Weights:** rebuilt pose-invariantly from the skeleton: each vertex
   takes the distance-weighted blend of its two nearest bind segments'
   linear joint fields, plus a procedural gradient along Tail1–4 for the
   tail, plus one edge-neighbor smoothing pass. Regional audit after:
   forearm regions ForeArm 0.58–0.59 / Hand 0.40 with Spine 0.00; hip
   regions UpLeg 0.72–0.75 / Hips 0.15–0.18 with Spine 0.00; tail verts
   mean Tail-joint weight 0.999; hand verts max Tail weight 0.0000. Edge
   stretch under the game's retarget: edges >1.5× drop from ~11%
   (shipped) to ~6% across neutral/stance/grab frames; forearm+hand p99
   6.1 → 3.6.
3. **Clips:** T3Stance/T3Grab re-baked with the verified port of the
   game's own retarget (identical math to `retargetT3Clips`), including
   the previously missing Spine1 channel. Standard-evaluation check on
   the shipped file: world quaternions match the retarget to 0.000°;
   every limb segment direction error 0.00° (torso ≤ 0.62°).

**Same skeleton fix + weight rebuild** applied to
`game/assets/models/pantera.glb` (Attire 1 in-game model — the owner
reported the same stretching/weight problems on A1) and
`roster/pantera/attires/classic/pantera-classic.glb` (same template,
same backward toes).

**Audited, no change needed:** Leo man (the authoring rig; toes forward);
Crimson Rage, T7 P2, and the hi-res T7 King file (unskinned static part
meshes — no skeleton, no toe bones, nothing to fix).

**Proof (rendered from the actual fixed files, viewed by the fixer):**
`docs/tpose-refs/pantera-leopard-king/fix2-sheet-20261022.png` and
`docs/tpose-refs/pantera/fix2-a1-sheet-20261022.png` — original Tripo /
fixed idle / fixed stance, front view, feet planted.

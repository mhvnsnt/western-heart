# Tekken 7 — hand/arm rigging + posing reference

## Ground truth 1: SKT_CH_base_Skeleton (via WH's 53-joint derivative)

Verified from repo files (roster/pantera/attires/leopard-king/model-rigged.glb and
roster/mariposa/attires/monarch/mariposa-monarch-rigged.glb — GLB JSON parse):

- One shared base skeleton for all fighters (confirmed in tekkenmods-docs:
  dennisstanistan.com custom-mesh tutorial — "M.Raven uses a base skeleton so
  select 'SKT_CH_base_Skeleton'").
- Arm chain per side: LeftShoulder -> LeftArm -> LeftForeArm -> LeftHand
  (Right mirrors; UE4 Left/Right prefix convention).
- Finger chains per hand: Thumb1->Thumb2 (->Thumb3), Index1->2->3,
  Middle1->2->3, Ring1->2->3, Pinky1->2.
- KNOWN DEFECT (WH rigs, not Tekken): left hand is missing LeftHandThumb3 and
  LeftHandPinky3 (2-segment thumb/pinky on the left, 3-segment on the right).
  Fix = add the missing bones and mirror weights; the T7 convention is symmetric.

## Ground truth 2: Tekken 6-era 147-bone layout (full detail)

From release tekken-models-batch-3 / beast-king-tekken-revolution.zip
(RoxasKennedy SFM port), file generic_item.mesh.ascii — the T6-era instance of
the shared Tekken hand convention (see tekken6-era-hand-arm.json in this directory
for the complete parsed table):

- "arm {side} finger {1..5}{a|b|c}" naming; a = proximal, c = distal.
- Right hand: 3/3/3/3/2 segments (thumb..pinky); left hand: 3/3/3/3/3.
  (The missing 'arm right finger 5c' is a port artifact, not a convention.)
- Bind-pose positions (meters) for every finger root — use for retarget scaling.
- Adjustment bones: elbow adj, shoulder 2 adj, shoulder 1 adj 1-2, back —
  these carry the deformation falloff that keeps shoulders/elbows smooth.

## Posing conventions (authored, not procedural)

- Fists, open hands, grips, points = authored animation poses on the finger chains.
- No procedural fist/open/spread system exists in any Tekken teardown — per-move
  finger animation is baked into the move's animation data.
- Idle stance: fingers in a relaxed half-curl; win poses/intros carry the
  character-specific hand acting (open taunts, fist pumps, weapon grips).

## Weight-painting guidance (from the modding docs + WH defects)

- 4 influences max per vertex, normalized (UE4/glTF standard).
- L/R symmetric naming required for X-mirror painting (the finger asymmetry bug
  breaks this until fixed).
- Known pipeline-level mis-weights to guard against: hand weighted to tail
  (Pantera), face weighted to pelvis/spine (Armor King pattern) — validate with
  bone-proximity checks at intake.

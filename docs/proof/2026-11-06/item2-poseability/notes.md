# Item 2 proof — kingtyrant / nightwolf / cainelias poseability (Wave 3, 2026-11-06)

All three attire-1 models were unrigged Tripo statics (0 bones): they fought on
the engine's fallback pose at native scale lying sunk (kingtyrant/nightwolf —
stance height 0.97 m, minY -0.49) or on S3's node-transform bake (cainelias),
and the select screen could not pose them at all (the M3 POSE-BLOCKERS
residue). Each now has a rigged successor beside its untouched static, wired by
one assets.js line each, on the L2 pipeline (tools/auto_rig refit at each
fighter's presentation height; canonical 50-joint set).

## Heights (presentation anchors)
- kingtyrant 1.644 m — S3's roster-anchor method (canon Eddy 188 cm x Pantera
  1.749 m / 200), same method cainelias was sized by.
- nightwolf 1.67 m — her own fully-rigged classic attire's measured figure
  height (game/assets/models/nightwolf.glb, 37/37 textured, same character).
- cainelias 1.819 m — his shipped S3 presentation, unchanged. His static's S3
  node transform (scale 1.858144 + lift 0.909593) is baked into the geometry
  (world bbox z 0..1.819 verified on 992,141 verts); the canon-sizing double-scale
  trap noted in S3 does not apply (no `height` field on his canon entry).

## Fits (all three needed hand work over the driver's automatic fits)
The driver's landmark fit degenerated on all three (kingtyrant right arm
plunged through the torso — driver verdict FAIL, official p99.9 4.362;
nightwolf both arms dragged down; star hit the same class in L2). Shipped:
template fits with the pantera template's missing LeftHandThumb3 restored
mirrored (its absence measured 137/137 thumb verts unweighted). Cainelias is
A-posed, so neither automatic fit works (template ghosts a T-pose; landmark
over-extends the hands into the boots): his fit composes the template body
with arm chains along landmark directions seated on slice-band centroids
(measure_arms.py record: shoulder (0.0685,1.471,-0.038), elbow
(0.208,1.152,-0.002), wrist (0.196,0.905,0.004) — fit_corrected.json).

Nightwolf's first (coarse-proxy) bake tore her fringe/loincloth (max edge
elongation 916 mm); the FINE proxy (voxel 0.006 / 80k faces) fixed the cloth at
the source — posed_side.png shows it hanging naturally on a -55 deg kick. The
shipped file is the fine bake (rig_ft.glb), not the seam-smoothed coarse one.

## Gates (validate.py: all three PASS — heights above, foot_y 0.0, fingers
symmetric, 0 unweighted)
- kingtyrant: seams PASS (max L1 0.0004); anim_check (official 18f) stretch
  p99.9 1.616 / max 1.749, 40 tearing spikes = the shipped aotsuki baseline
  count (rigid boot verts on kicks; the coarse 72f sampling reads stretch
  p99.9 1.622). Secondary chains found his braids (Head/Spine2-rooted).
- nightwolf: seams PASS (0.0005); anim_check p99.9 2.433 (within the 2.5 gate),
  max 3.162, 40 spikes = aotsuki baseline. Chains self-skipped (no long hair).
- cainelias: seams PASS (0.0002); anim_check p99.9 10.26 — DEVIATION, see below.

## Fights (harness standard: fixed-step, live Pantera, 1.1 m; JSONs + stills
in this folder)
- kingtyrant: eddy bank BINDS (22 actions, bones 50, motion range 0.813 —
  capoeira sway); stance 1.372 m in the low eddy crouch, minY -0.019.
  Damage 7/10 identical (1: 2.8, 2: 5.5, d+1: 5.5, d/f+1: 9.2, d/f+2: 17.4,
  1+3/2+4: 17.4); throws UPGRADED legacy-lock -> paired path at identical
  17.4. Inputs 3 (27.5->6.4), 4 (5.5->22), d+2 (9.2->17.2) switched from the
  generic fallback to his real eddy bank rows (star/L2 precedent class).
- nightwolf: julia bank BINDS (22 actions, bones 50, motion 0.716); stance
  1.572 m grounded (minY +0.008) — the S2 "prone/tiny" fight presentation was
  the fallback path, not her file. Damage 9/10 identical; input 2 switched
  fallback -> bank row (9.2 -> 5.5, plan t7:1~t7.julia).
- cainelias: king bank BINDS (22 actions, bones 50, motion 0.378); stance
  1.809 m, minY +0.017. Damage 10/10 IDENTICAL to the pre-rig state (1: 6.4,
  2: 11, 3: 8.3, 4: 16.5, d+1/d+2: 0 — his documented dead-slot class,
  unchanged, d/f+1: 11, d/f+2: 11, 1+3: 22 lock, 2+4: 25.7 lock); plans now
  resolve real king-bank rows. His select card is posed by his OWN king bank
  stance (the only one of the three whose bank stance passes the PreviewPane
  fit gate — binds A-posed, so the stance's shoulder swing stays in range).

## Cards
Recaptured via tools/portraits/capture.mjs against the after-serve; all three
viewed true to character. kingtyrant + nightwolf on cmu-14_01 (kingtyrant's
eddy stance fit-rejected: "Left shoulder swung 0.69 rad from bind" — item-7
class evidence); cainelias on tekken-bank. POSE-BLOCKERS blocked map is now
EMPTY (all three entries cleared); test/portraits.test.mjs on the post-change
tree: "50 select fighters, 0 pose blockers, 7 registered placeholders — PASS".

Cain card note: the dark shapes flanking his bust on the card are his LEATHER
VEST (zoom-leftslab.png / zoom-rightslab.png: stitching, a snap button, the
collar folded over his hair) pitched toward the camera by the king stance's
forward lean — verified by 3x crops of the shipped card, not an artifact.

## Cainelias deviations (declared in the PR)
1. anim_check stretch p99.9 10.26 exceeds the 2.5 gate on the CMU boxing
   stress clip. Evidence it is a stress-proxy artifact, not a fight defect:
   the strict inspect shows the over-2x edges concentrate in the PANTS'
   hip-fold dense mesh (UpLeg|UpLeg 170k of 278k) with median over-2x
   elongation 4.53 mm; his actual king-bank motions in-game (stance + the full
   basic set incl. jumping attacks) render clean (fight stills here); an
   independent exact-LBS skinning of this file with a 60 deg LeftArm rotation
   displaces 0 verts > 0.5 m (worst = a fingertip at 0.43 m, the correct
   swing). Same documented-deviation class as L2's gashadokuro (3.29).
2. The Blender posed-render path (tools/auto_rig/proof_pose.py) shows hair
   sheeting for this rig under hand-set local-axis rotations; the sheets do
   not occur in file-space LBS or in the game. Three weight surgeries (z-band,
   capsule, geodesic-claim) were built and rejected as unnecessary — the
   shipped file is the UNSURGERIED bake (validate/seams/in-game all pass).
   The Blender artifact is recorded here so nobody re-chases it.
3. The three fighters' Blender driver run (refit_rig.py end-to-end) failed on
   kingtyrant (landmark arm degeneration) and was not used as the bake path
   for any of the three; the bakes are the pipeline stages run individually
   with hand-verified fits (method-used disclosure, same as L2).

# T7 stances and attacks: the arm-roll correction removed (2026-11-10)

Owner (verbatim): "Arms at shoulders, forearms, and hands are all crushed and twisted some have extreme weight painting
issues all over and some have twisted necks or stretched faces evaluate and fix it all".

## What was wrong

The arm-frame normalization added on 2026-11-07 (`be48d0fc4`, `estimateArmCorr` in `game/js/t3anims.js`) was built for
the Tekken 3 banks, but it also ran on the real Tekken 7 stances and on every T7 attack retargeted with them.

- It compares each arm joint's LOCAL twist on the fighter's rig with the source's. That only measures a transport
  error on a rig whose rest rotations are identity, which is what its tests used.
- Real fighter rigs (Blender / Tripo exports) carry bone-aligned rest frames with arbitrary rolls. The measure read
  those rolls as errors and applied large constant rolls to the arms.
- Result in the fight: rolled arms and twisted forearms, shoulder armour stretched up to the ears (Negativo, Burger),
  chest pieces folded (Negativo's emblem), guards turned into crossed or flipped hands (Skull, Retsu, Nightwolf).

Constants it applied (poselab sweep, each fighter's real T7 stance on the model the fight loads; Pantera measured clean):

| Fighter | Arm rolls applied before this fix |
|---|---|
| negativo | LeftShoulder 69.5°, LeftArm 82.6°, LeftForeArm 82.6°, LeftHand 83.1°, RightShoulder -71.0°, RightArm -84.8°, RightForeArm -84.8°, RightHand -82.9° |
| burger | LeftShoulder -171.9°, LeftArm -173.3°, LeftForeArm -173.3°, LeftHand -173.3° |
| retsu | RightShoulder 177.4°, RightArm -172.8°, RightForeArm -172.8°, RightHand -172.8° |
| skull | LeftShoulder 46.5°, LeftArm -51.8°, LeftForeArm -48.5°, LeftHand -48.4°, RightShoulder -44.6°, RightArm 65.1°, RightForeArm 55.0°, RightHand 55.1° |
| nightwolf | LeftShoulder 51.6°, LeftArm 49.3°, LeftForeArm 49.3°, LeftHand 49.1°, RightShoulder -200.8°, RightArm 77.3°, RightForeArm 77.3°, RightHand 84.7° |
| diablo | RightShoulder 164.8°, RightArm 170.0°, RightForeArm 170.0°, RightHand 170.0° |
| gashadokuro | LeftShoulder 102.3°, LeftArm 83.5°, LeftForeArm 83.5°, LeftHand 77.9°, RightShoulder -85.1°, RightArm -65.5°, RightForeArm -65.5°, RightHand -60.3° |
| sha | RightShoulder 126.2°, RightArm 135.1°, RightForeArm 135.1°, RightHand 135.1° |
| aotsuki | LeftShoulder 52.1°, LeftArm -85.8°, LeftForeArm -81.2°, LeftHand 171.3°, RightShoulder -43.0°, RightArm 87.7°, RightForeArm 83.4°, RightHand 149.9° |
| chordz | LeftShoulder 61.4°, LeftArm -38.4°, LeftForeArm -38.1°, LeftHand -38.1°, RightArm 92.1°, RightForeArm 84.8°, RightHand 84.9° |
| purplerain | LeftShoulder 43.2°, LeftArm -44.1°, LeftForeArm -42.1°, LeftHand -42.2°, RightShoulder -33.6°, RightArm 61.6°, RightForeArm 56.4°, RightHand 56.4° |
| phantom | LeftShoulder 51.9°, LeftArm -49.5°, LeftForeArm -47.6°, LeftHand -47.5°, RightShoulder -62.5°, RightArm 73.1°, RightForeArm 68.1°, RightHand 68.0° |
| sakura | LeftShoulder 36.2°, LeftArm -60.2°, LeftForeArm -56.7°, LeftHand -56.6°, RightArm 78.7°, RightForeArm 74.2°, RightHand 74.3° |
| tobi | LeftShoulder 26.5°, LeftArm -54.9°, LeftForeArm -48.1°, LeftHand -48.0°, RightShoulder -23.6°, RightArm 57.1°, RightForeArm 48.1°, RightHand 48.1° |
| pond | LeftShoulder 34.7°, LeftArm 61.2°, RightShoulder -51.7°, RightArm -69.0° |
| ryusan | LeftShoulder 28.5°, LeftArm -54.4°, LeftForeArm -50.6°, LeftHand -50.7°, RightShoulder -27.8°, RightArm 55.1°, RightForeArm 50.4°, RightHand 50.5° |

The rolls applied to the T7 stance AND every T7 attack of these fighters (the attacks reuse the stance's cached
constants).

## The fix

`t3anims.js`: `'t7:'` skeletons skip the arm-frame normalization, as they already skip the head-frame and spine-pitch
ones. T7 data needs no correction: the T7 mannequin and the fighters' rigs are both T-poses, so the world-delta
transfer (each bone's source world rotation, aligned to the fighter's own bone direction and applied to its own rest)
carries every bone's direction and roll exactly, whatever the rig's rest frames. The Tekken 3 banks are unchanged.

## Checked

- **By eye:** `before-after-1.jpg`, `before-after-2.jpg`: each fighter's upper body in his T7 stance, the game before
  this fix and after it, front and three-quarter. Better on Negativo, Burger, Retsu, Skull, Nightwolf and Gashadokuro;
  equal or slightly better on the rest; worse on none. Pantera is unchanged (no correction fired on him).
- **Same pixels as the switch:** the fixed game path renders pixel-identical (mean difference 0.0) to the
  `__WH_RETARGET_LAYERS = { arm: false }` renders for all 17 fighters, both views; no T7 arm constant fires.
- **Test:** `test/arm-frame-normalization.test.mjs` "negativo (T7 Negan stance) on a rolled-rest rig": a rig with
  Blender-style rest frames, every arm joint's posed world rotation against the source's. 133 deg off before the
  fix, under 1 deg after. All 8 tests in the file pass.
- **Unit suite:** 106 of the 107 `test/*.test.mjs` files pass. `hitbox.test.mjs` fails the same way with and without
  this change in this container (`this.ui.attackData is not a function`) and passed in CI on this branch.

## Not fixed here

- Walk, block, hit and KO for these fighters still come from their Tekken 3 banks (Negativo's is `bryan`). Next: each
  base's own T7 generic actions (`tools/anim/t7_generic_bank_bake.py`), so no Tekken 3 data is left on them.
- Hands: the game's clips carry 21 body joints and no finger tracks, so every fighter's hands stay flat.
- Hair and armour pieces torn off by bad weights (Tobi, Ryusan, Sha, Phantom's hair) are rig weights, not this
  correction.
- The same local-twist measure probably misfires for Tekken 3 banks on real rigs too (Thor: 48-76 deg). Not changed
  here; the Tekken 3 banks are being replaced with T7 data.

Renderer: `game/poselab.html` (the game's own loader and retarget) driven by Playwright, stance at 0.5 s, `closeup`
upper body.

# Brutal Fist fighters: their own select cards, facing their opponent (2026-11-11)

Owner (2026-11-11): "all of the new characters from ... brutal fist ... that we just pulled in all the new characters
that don't have character cards they need characters like the cards on the character select screen and that needs to
be pushed to the deployable build".

## What was wrong
- The 26 Brutal Fist fighters (pull-in 2026-11-08) had card files. But every card was a low side profile: shoulder
  in frame, face turned away, top of the head cut off (`cards_before.png`).
- **Cause:** every Brutal Fist mesh faces **+X**. In the rest pose the face is at yaw 90 and the back at yaw 270
  (`rest_yaw90_yaw270_sheet0.png`, `rest_yaw90_yaw270_sheet1.png`; Bannon from four angles at rest and in stance:
  `bannon_four_angles_rest_and_stance.png`).
- `game/assets/models/model-facing.json` had no record for them. The fallback feet cue only tells +Z from -Z, so the
  instance was never turned.
- The select card and the fight use the same instance (`assets.createInstance`), so these fighters also stood
  side-on in fights.

## Fix
- `tools/portraits/record_facing.py` (new) records +X, with this evidence, for the 23 models verified by eye.
  `assets.js` already turns a +X model a quarter turn (`facingYaw`), so the card and the fight are both fixed.
- The 23 cards are re-captured by `tools/portraits/capture.mjs`: the game's own preview, attire 1, each fighter's
  own bank stance (`cards_before_after.png`, left = before, right = after).
- `capture.mjs` now loads playwright through `createRequire`, like `facing_probe.mjs`. An ESM bare import does not
  resolve without a local `node_modules`.
- `test/portraits.test.mjs` passes.

## Not fixed here (stated, not hidden)
- **bf-jager, bf-tarzanian-devil:** their meshes sit ~0.95 m above their skeleton. The mesh bounds are y 0..1.90
  while every other Brutal Fist mesh is centred on the same skeleton template (y -0.94..0.94). So the head bone is
  at chest height, the card frames the legs, and posed vertices swing around joints a metre away (stretched mesh).
  The model fix is a mesh re-alignment to the skeleton, next.
- **bf-maime:** hidden from the select screen by the material gate (`game/js/material-status.js`: 15 untextured
  parts). Her model needs its textures from the Brutal Fist source before she can have a card.

# Sweep body = the body the game loads (2026-10-29)

`test/e2e/moveset-sweep.bodies.mjs` now asks the game which attire a roster fighter
loads (`game/js/attires.js` selectableAttires()[0], no saved pick) before falling back
to roster_map.json attire slot 1. When the material gate hides the fighter
(attiresFor -> [] because its own attire 1 is quarantined in `game/js/material-status.js`),
the row is a BLOCKER naming the quarantine instead of a sweep on the fallback body.

Bodies that changed (9 of 128 movesets):

| moveset | before | now |
|---|---|---|
| negativo | n3g4tiv0 | negativo-attire1 (OWNER-MODEL-FIRST ladder) |
| awapop | awa-pop | awa-pop-attire2 |
| bruno | bruno | bruno-attire2 |
| cyborgx | cape-jones | cape-jones-attire1 |
| demonio | demonio | demonio-a1 |
| dio | dio | dio-attire1 |
| yukihyo | yukihyo | yukihyo-attire1 |
| menajerii | menajerii | BLOCKER: material gate quarantine, menajerii + menajerii-attire1 (55 untextured) |
| megami | megami | BLOCKER: material gate quarantine, megami + megami-attire1 (20 untextured) |

Rerun: negativo 279/311 pass, 16 fail, 16 n/a (it previously stopped on the model mismatch).

## Why menajerii / megami cannot be textured from their sources here

- menajerii plays `roster/vixen/attires/attire1/model-rigged-noplane.glb`: 69 materials,
  55 untextured, and **no TEXCOORD_0 on any primitive**. The textured source
  `roster/vixen/attires/attire1/model.glb` (palette atlas, 71/72 ok) shares geometry with
  only 1 of the 69 rigged primitives (mesh name + vertex count), so its textures cannot be
  mapped onto the rigged mesh. Needs a re-rig from the textured source.
- megami plays `roster/parvati/attires/attire1/model-rigged.glb`; its source
  `roster/parvati/attires/attire1/model.glb` has the same 20 untextured parts
  (EyeMoisture, Cornea, PANTIES-1 ...), so there is nothing to transfer.

# Dio and Deathfang faced backwards (2026-11-06)

Both select cards showed the fighter's back. `tools/portraits/facing_probe.mjs` rendered the game's own instance (the
one the fight uses) from four camera angles, in the bind pose and in the stance: both faces sit at 180 deg from the
card camera (`facing-probe-rest-vs-stance.png`). So these two model files face -Z: `deathfang` was recorded `+Z`, and
`dio-attire1` was unlisted (the feet cue read `+Z`). Both are now `-Z` in `game/assets/models/model-facing.json`.

- `dio-deathfang-cards-old-new.png`: old card / recaptured card, both fighters now face the camera.
- `dio-vs-deathfang-fight.png`: a real local fight (`SETTLE_S=12 node tools/proof-harness/fight_entry_probe.mjs ...
  dio deathfang`), both standing and fighting toward each other. Owner, on this picture: "U fixed them both already in
  that picture".

The broken originals stay in `game/assets/portraits/broken-originals-20261106/`.

## Dorowani (same day)

His card showed his back too. Here the game had already turned him (the feet cue read `-Z`, `assets.facing = -1` read
back in the page), and his face was still at 180 deg in the probe, so his mesh faces `+Z`: `dorowani` is now recorded
`+Z`. `dorowani-card-and-fight.png`: old card / new card (his face) and a real fight vs Pantera, facing his opponent.

## Slice (same day): a quarter turn

His card showed his side and back, and in a fight he stood with his back to the camera while Pantera, opposite, was in
profile (`slice-fight-before.png`). In the bind pose his chest is square to the camera at yaw 90 (camera on +X): the
mesh faces +X, which a 180 deg turn cannot fix. `model-facing.json` gains quarter-turn records (`+X` / `-X`, read in
`game/js/assets.js` as `facingYaw`); `slice-attire1` is `+X`. `slice-card-and-fight.png`: the new card from four
angles (front at yaw 0) and the same fight, Slice now in profile facing Pantera.

## Waterfall and Koreshi (same day)

- **Waterfall:** her card showed her turned away and in a real fight she faced the camera instead of Pantera. The feet
  cue had already turned her a half (`assets.facing = -1`); with it her face sat at yaw 270, so her raw mesh faces +X.
  Recorded `+X` (a `-X` record was tried first and put her face at yaw 180: rejected). `waterfall-card-and-fight.png`:
  four-angle probe (face front-on at yaw 0), the fight (in profile facing Pantera), old / new cards.
- **Koreshi:** his card / poselab head views were ambiguous (helmet-like hair), so a same-moment A/B of the real fight
  decided (`koreshi-fight-ab.png`, both at 7 s): unrecorded he crouches with his weapon arm pointing away from his
  opponent; with `-Z` he stands bladed, weapon at his opponent, scroll box on his back. Recorded `-Z`.

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

# MADE animations — Pantera (2026-10-24)

Every `.json` file in this directory is labelled **MADE** in its filename
and in its JSON `provenance`/`source` fields. Each is an ADAPT of a real
decoded T3 King clip (see `docs/anim/MADE-PANTERA-2026-10-24.md` for the
per-move source + transform). **None of these files is decoded motion,
and none may be described as decoded.**

## Wiring precondition — DO NOT WIRE YET

- `game/js/t3anims.js` hardcodes `clip.userData.source = 'REAL T3 decoded
  motion'`. That line must become data-driven (`data.source`) before any
  MADE clip is wired, or the game would mislabel MADE clips as decoded
  at runtime.
- `game/js/fighter.js` `_attackClipPlan()` never reads moveset
  `anim_ref`; wiring needs a new `made` tier keyed by a `made_clip`
  moveset field, plus hit-window entries per clip.
- Until that wiring PR lands, the game keeps its current fallback for
  Pantera's three signatures. These clips are shipped, validated
  (structural only), and unwired.

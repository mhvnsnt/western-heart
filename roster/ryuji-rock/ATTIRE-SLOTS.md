# RYUJI-ROCK / CORNERSTONE — ATTIRE SLOTS

Canon: Cornerstone — Ryuji Yamazaki (KOF) × The Rock (early Attitude Era).
Owner design drop 2026-10-21. Internal id stays `ryuji-rock` (owner order).

## Slots

| Slot | Model key | File | Source |
|---|---|---|---|
| 1 (default) | `ryuji-rock` | `roster/ryuji-rock/attires/attire1/model-rigged.glb` (29,112,760 B, blob sha `5b6bdf1b…`) | Tripo `20c1fd2e-40d0-4500-9be6-50f6494ab5e1` ("tattooed man"), owner-provided. Rigged 2026-10-23 (landing wave 2, GameRig auto-rig, 73 joints). |
| 2 | `ryuji-rock-source` | `roster/ryuji-rock/attires/attire1/model.glb` (18,872,720 B, blob sha `bc3efc80…`) | Same Tripo pull, unrigged static, byte-identical to `attires/attire1/source/cornerstone-a1.glb`. Kept beside the rigged build as source. |

## History

- 2026-10-21: owner design drop + Tripo pull (20c1fd2e).
- 2026-10-22: pull archived (`attires/attire1/source/cornerstone-a1.glb`,
  18,872,720 B; release `cornerstone-tripo-pulls-20261021`).
- 2026-10-23: copied byte-identical to the wired `model.glb` (landing wave 1)
  and rigged (landing wave 2). A 2026-10-23 note saying it was "never copied
  to the wired path, never rigged" is SUPERSEDED — both files are on main.
- 2026-11-21 (Lane F model audit): ladder added (`game/js/attires.js`
  `'ryuji-rock'`), MODEL_URLS key `ryuji-rock-source` added. No default
  change: slot 1 was already the roster default (`roster-full.js` model
  `ryuji-rock`).

Note: bare **RYUJI** (roster id `ryuji`, modelPending) is a different fighter —
same-body hybrid of Cornerstone per owner ruling #6, hidden, no own model.
Do not point Ryuji at this ladder without the owner's call.

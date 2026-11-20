# Training Mode + Replay Theater — Teardown Research (2026-10-22, worker 29)

User-approved scope (verbatim): "Wire up: (3) Training mode depth — frame
data display, record/playback dummy, hitbox viewer. (5) Replays — save/watch
fights, slow-mo, camera control."

Standing user lock: **Gungaku (軍楽, "war music")** — the fight lab /
programmable training dummy mode (TTT2 Combot equivalent). The lab UI is
branded GUNGAKU accordingly.

## What each teardown contributed

### Tekken 7 — practice mode (gold standard)
- Dummy settings: action (stand/crouch/jump), guard (stand/crouch/all),
  counter-hit toggle, ukemi. → Our `TrainingDummy` behaviors
  (stand/crouch/block/jump) in `game/js/training.js`.
- Practice recording: two slots, record-your-inputs → dummy plays back
  looped. → `DummyRecorder` + `PlaybackDummy` (raw inputs re-resolved
  against the dummy's own moveset — exactly T7's semantics).
- Command display + frame data overlay. → Live frame-data readout in the
  lab panel (`frameDataFor`) + per-move startup/active/recovery columns
  in the movelist overlay.
- Replay: auto-saves ranked/quick matches; theater with slow-mo.
  → `ReplayRecorder` auto-attaches to versus/arcade/demo fights;
  `ReplayPlayer` transport (0.25×/0.5×/1×/2×, frame step, restart).

### Tekken Tag Tournament 2 — Combot (programmable dummy)
- The user explicitly named Gungaku as the TTT2 Combot equivalent: a
  dummy you program by demonstration. Our record/playback is the
  demonstration-programming loop (record → looped playback).
- TTT2 replay chapter select → our round-based replay structure
  (per-round snapshots; round transitions restore from snapshots).

### DOA5/6 — move details + slow-mo viewer
- DOA's move-details list shows startup/active/recovery per move →
  the movelist overlay's `Sf/Af/Rf · dmg` columns.
- DOA5's replay viewer slow motion → 0.25×/0.5× speeds.

### SoulCalibur VI — frame-data overlay
- SCVI's in-fight frame meter → the lab's live per-move phase bar
  (startup gold / active red / recovery blue with frame counters).

### Street Fighter — input display
- SF training input display → covered by the existing control hints +
  the lab's recording indicator; not duplicated.

## Determinism design (the core engineering decision)

Replays are **resolved fighter-call logs + per-round snapshots**, NOT
video and NOT raw input logs. Reason, verified against the engine:

- The input→move resolution path (`TekkenBuffer.press`,
  `input.js` chord detection) depends on **wall-clock**
  (`performance.now()`: 140 ms chord windows, 600 ms motion-event
  windows) and per-tick direction history. A raw input log would
  re-resolve differently on replay.
- The fight sim itself (`Fighter` methods, `_resolveCombat`,
  throw locks, hitstop) is deterministic given the call sequence:
  all `Math.random` / `performance.now` uses in `fighter.js` are
  visual-only (soul-aura particles, trail pulses) — verified by grep
  2026-10-22. AI randomness never re-runs: the AI's *resolved calls*
  are what gets recorded.

Recording boundary (monkey-patched per fight, removed after):
`setStick tryMove tryJump tryBlock tryCrouch trySidestep tryDodge
tryTransform tryThrowBreak tryAttack` — continuous ones logged on
change only. `tryAttack` additionally logs its resolved notation so
replay fires it via `Fighter.replayMove` (new, mirrors
`_tryAttackFresh`'s post-resolution tail) instead of re-resolving.

Round snapshots capture positions, facing, state, hp/meter, attack
state and the TekkenBuffer's `lastMove` — the intro's wall-clock
`setTimeout` is bypassed by restoring the first-fight-tick snapshot.

## Files
- `game/js/replay-codec.js` — pure data layer (node-tested).
- `game/js/replay.js` — recorder, player, FreeCam, library.
- `game/js/training.js` — Gungaku lab (dummy, record/playback,
  hitbox viewer, frame data, reset, free cam).
- `game/js/fighter.js` — `Fighter.replayMove` (additive).
- `game/js/game.js` — tick counter/hooks, replay branch, timeScale,
  stepTicks, recorder finalization (additive).
- `game/js/scene.js` — `arena.freeCam` (additive).
- `game/js/main.js` — attach wiring, movelist frame-data columns,
  replay theater UI, keyboard shortcuts (additive).
- `game/index.html`, `game/styles.css` — lab panel, transport bar,
  library screen (additive).

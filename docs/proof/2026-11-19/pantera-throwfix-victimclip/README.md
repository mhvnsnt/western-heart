# Pantera throw victim clip — proof + diagnosis (2026-11-19)

Lane A (PR #1764, merged 83b2e090) fixed the pair *selection* for Pantera's
front throws (1+3 / 2+4): the file's `throw_inputs` is now authoritative, so
1+3 selects slot 2795 / victim 3018 and 2+4 selects slot 2797 / victim 3051
(node tests 4/4, 21/21 with the throw suites).

This directory holds the live-capture proof for 2+4 and the diagnosis of
what still blocks the paired victim clip in the live game.

## What the capture proves

- `pantera-2plus4-victimclip-trimmed-20261119.mp4` — 0.9 s, 20 fps, 18 frames:
  Pantera grabs Demonio and lifts him; the victim is visibly animated through
  the grab and the start of the throw (not frozen).
- Frame log `video-pantera-log.json` — all 132 sim frames: the victim plays a
  real clip on **84/84 thrown/thrownExec frames** (pre-fix: 0/118, Lane D).
  Damage lands (24.7, hp 180 to 155.3). States: thrower
  attack to throwing to throwExec to idle; victim idle to thrown to thrownExec
  to knockdown to idle.
- The three stills show the throw connect, the victim mid-throw, and the
  victim in the launch pose.

## What it does NOT prove — the paired clip does not play live yet

The victim's clips in the capture are the generic reactions
(`t3_jin_stance` to `t3_jin_hit` to `t3_jin_launch`), not the paired clip
(`t3_react_3051`, the slot-3051 clip). The pair never binds in the live game
because of a **distance gate**:

- The file's 2+4 branch (attempt 274, cond 2 to slot 2797) has `param: 1536`.
  Max range = 1536 x pack `anchor_mm_to_rig_m` (0.000829923) = **1.2748 m**.
- The live throw connects at a **1.45 m** gap (the engine's body separation
  holds the fighters at about 1.45 m; the grab lunge does not close it — the
  victim is pushed away as Pantera advances, gap stays 1.45 m).
- `selectthrow-distance-demo.log` (real modules + real file data): 2+4
  selects slot 2797 at 1.0 m and 1.27 m, returns NULL at 1.28 m and 1.45 m.
  1+3 (attempt 273 to slot 2795, same param 1536) is NULL at 1.45 m too.
- So `_throwPairFor` returns null at connect time, `startThrowLock` takes
  the legacy lock, and the victim plays the hit/launch fallbacks. The node
  tests never caught this: they place the victim at 1.0 m, inside the range.

Resolving the gate is a coordinator decision: it touches shared
throw-selection semantics (`selectThrow` distance, used by all throws) or
grab/connect tuning (body separation, grab reach). No unilateral change was
made here.

## Capture caveats (honest)

- The full 44-shot capture goes **pure black from shot 18** (sim frame ~54).
  The sim stays healthy (states advance, damage lands, positions finite), so
  this is a capture-environment failure, not a game defect: the VM was under
  memory contention (another lane's browser + a Blender render running
  concurrently; a later probe run's renderer was OOM-killed in the same
  window). The trimmed video keeps only the 18 good frames. The full frame
  log (all 132 frames, clip names included) is in `video-pantera-log.json`.
- 1+3 live video was not captured: the identical distance gate makes the
  outcome determined (node-proven NULL at 1.45 m); a 1+3 live capture belongs
  with the follow-up fix's proof, after the gate is resolved.
- Method: local serve of merged main 83b2e090 on 127.0.0.1:8891 (headless
  Chromium cannot reach https from this VM), opponent Demonio (the repo's
  play-verify pair; the other opponent is not shell-bundled and cannot load
  headless), hand-stepped 60 Hz sim, frames from the renderer's canvas.

## Files

- `pantera-2plus4-victimclip-trimmed-20261119.mp4` — 0.9 s, 800x450, 20 fps.
- `frame-001-throw-connect.png` — throw connects (sim frame ~0).
- `frame-010-victim-thrown.png` — victim in `thrown`, hit clip (sim frame ~28).
- `frame-018-victim-launch.png` — victim in `thrownExec`, launch clip (sim frame ~52).
- `video-pantera-log.json` — per-frame states, clips, positions, hp (132 frames).
- `selectthrow-distance-demo.log` — node `selectThrow` at 1.0 / 1.27 / 1.28 / 1.45 m.

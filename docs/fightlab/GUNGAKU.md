# FIGHT LAB · GUNGAKU (軍楽)

**Official name — owner-locked 2026-10-22.** "War music." This is the
programmable training dummy mode, Western Heart's TTT2 Combot equivalent.
There is no working title and nothing left to confirm.

## What it is

Training mode's passive dummy, upgraded: the dummy runs a **Gungaku
program** — an ordered, looping sequence of button/state-level ops —
instead of standing still. Programs are authored two ways, Combot-style:

1. **Presets** — the classic lab drills: IDLE (sandbag), GUARD ALL,
   CROUCH, WALK IN / WALK OUT, PUNISH CHECK, JUGGLE SANDABAG,
   SIDESTEP DRILL, MIXUP LOOP.
2. **Recorder** — demonstrate on your own fighter; the lab captures
   your buttons (`1`/`2`/`3`/`4`) and stances into a program and the
   dummy plays it back.

Ops are button/state level, never move names: `1`–`4` resolve through
the dummy's own TekkenBuffer, so a program recorded on one fighter
plays back sensibly on any other fighter.

## Files

| File | Role |
|---|---|
| `game/js/fightlab-gungaku.js` | `GungakuProgram`, `GUNGAKU_PRESETS`, `GungakuRecorder`, `GungakuAI extends AIController`, `mountGungakuPanel` |
| `game/js/modes.js` | `startMode('fightlab')`, `onConfirm` routing, `_beginFightLab` (builds on worker 29's `_beginTraining`) |
| `game/js/game.js` | instantiates `GungakuAI` when `enemyChar.ai.gungaku` (dynamic import, boot path untouched) |
| `game/js/main.js` | `mode-fightlab` menu dispatch |
| `game/js/mainmenu.js` | worker 37's T8-style menu had a "GUNGAKU FIGHT LAB" placeholder card (`badge: 'soon'`) — flipped to `badge: 'live', action: 'mode-fightlab'`, wiring their placeholder to this implementation |

## Controls

- **G** — toggle the lab panel (in Fight Lab only)
- Panel: preset select, ● REC / ■ STOP, ▶ PLAY (programs the recorded sequence onto the dummy)
- Recorder captures attacks as buttons and compresses repeated stances; max 32 steps.

## Coordination

- Builds on worker 29's training mode (`modes.js` `_beginTraining`);
  training itself is untouched — Fight Lab is a separate mode entry.
- `GungakuAI extends AIController` (game/js/ai.js) so the fight loop
  needs no changes: `game.ai.update(dt, p1)` drives programs the same
  way it drives personalities.
- Fails safe everywhere: a failed op degrades to idle, the panel is
  best-effort, and recording never interrupts the fight.

## Name status

**LOCKED.** Owner approved "Gungaku (軍楽)" on 2026-10-22. Used
verbatim in UI, docs, code, and file names. No UNCONFIRMED flags.

# Pantera voice triggers (2026-10-24, integration one-pass)

## What was already wired (PR #1028, merged)

- `game/data/voices/pantera.json` — Pantera voice manifest, 52 clips,
  provenance TekkenMods mod 681 (Classic) + mod 1242 (T2 grunts, preferred
  per owner ear-check 2026-10-24), triggers hit 21 / ko 8 / win 8 / taunt 7
  / intro 6 / select 2, assigned by duration rank only (clip content NOT
  ear-verified — to be confirmed at the owner voice session).
- `game/assets/voices/pantera/` — 52 OGG clips, converted with loudnorm.
- `game/js/voice.js` — the voice engine (`voice.play(fighterId, trigger)`),
  fire-and-forget, never throws, subtitle layer included.
- 9 suspect F_KING stage-sound files deleted by #1028.

## What was missing (found by integration verification)

NOTHING in the game called `voice.play()` during fights — not `game.js`,
not `main.js`, not `fighter.js`, not select/modes/menu. The engine and the
bank were wired data with no trigger. A parallel PR (#1035) that built a
SECOND voice system under `game/assets/audio/voice/` plus new `audio.js`
methods was closed unmerged in favor of hooking the existing engine.

## What this wires (5 added lines, nothing else)

- `game/js/game.js` — imports the voice engine, and fires it at the 4
  existing grunt sites, victim id + trigger:
  - throw KO site: `voice.play(victim, 'ko')`
  - throw (non-KO) site: `voice.play(victim, 'hit')` (no grab trigger
    exists in the Pantera manifest; hit is the closest real trigger,
    documented here, not invented)
  - strike KO site: `voice.play(victim, 'ko')`
  - strike hit site: `voice.play(victim, 'hit')`
- The existing procedural `audio.grunt()` calls are KEPT at all 4 sites:
  fighters without a voice bank must not go silent, and `voice.play()`
  no-ops for them (manifest missing = silent no-op by engine contract).
  For Pantera, voice + synth grunt layer until the user playtests and
  judges the layering; gating the synth grunt when a bank is loaded is
  the documented follow-up, not done silently here.
- `test/voice-triggers.test.mjs` — verifies import, all 4 trigger calls,
  trigger names existing in the Pantera manifest, and grunt preservation.

## Honest gaps (not claimed fixed until played)

- **User playtest still owed.** Script-verified only (`node --check`,
  test ALL PASS locally). No one has yet played a Pantera fight and heard
  the real voice fire on hit/KO. Do NOT tell the user voice is "fixed"
  until they play and confirm.
- **Trigger assignment is duration-rank only.** The manifest itself says
  clip content was NOT verified by ear; a "hit" clip might in reality be a
  roar. Owner voice session still owed to confirm assignments.
- **Intro / win / select / taunt triggers not hooked to fight-flow
  events yet.** This PR hooks hit + ko only. Intro (fight start), win
  (match end), select (character pick) are next-lane hooks.
- **Subtitle layer.** `voice.play()` builds subtitles via the engine's
  own layer; whether subtitles appear in a real fight is part of the same
  owed playtest.

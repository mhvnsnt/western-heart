# Pantera voice wiring (2026-10-24, integration one-pass)

## What was missing

Pantera's voice (King bank clips, owner ear-checked 2026-10-24, T2 set
preferred) was pulled to `~/workspace/king-mods/` but was 0% wired into the
game:

- No `game/assets/audio/` directory existed on main at all (contents API
  returned 404).
- `game/js/audio.js` was fully procedural (synthesized oscillators only).
- `game/js/game.js` called `audio.grunt(pitch)` with no fighter id, so every
  fighter played the same synth grunt.

## What this wires

- `game/assets/audio/voice/pantera/manifest.json` — 53 clips in 3 sets:
  classic (TekkenMods mod 681, 26 clips), t2grunts (mod 1242, 26 clips,
  preferred — owner ear-check: better quality), t8death (mod 3111 preview,
  1 clip). Clip content labels are NOT assigned from bank data (the bank
  carries slot IDs, not names); clips are identified by position number.
- `game/assets/audio/voice/pantera/classic/*.wav` (26),
  `game/assets/audio/voice/pantera/t2grunts/*.wav` (26),
  `game/assets/audio/voice/pantera/t8death/8052665.wav` (1) — all validated
  as real WAV files before commit (RIFF/WAVE headers checked, 53/53 valid).
- `game/js/audio.js` — additive voice-bank methods on `AudioEngine`:
  `loadVoiceBank(fighterId)` (fetches manifest, decodes preferred-set
  grunt-sized clips ≤2.0s), `voiceGrunt(fighterId)` (round-robin playback
  through `sfxGain`), and `grunt(pitch, fighterId)` (voice clip when a bank
  is loaded, procedural grunt otherwise — never silence, never a wrong
  fighter). Existing pitch-only call sites behave exactly as before.
- `game/js/game.js` — all 4 grunt call sites now pass the victim fighter
  id (`def.char.id` at throw sites, `defender.char.id` at hit/KO sites),
  so Pantera-as-victim grunts with Pantera's real voice once the bank loads.
  Bank loading is fire-and-forget on first grunt, so the first grunt may
  still be procedural while the bank decodes; later grunts use real voice.
- `test/voice-bank.test.mjs` — verifies code wiring always, and manifest
  integrity on full checkouts (skipped, not failed, on the sparse CI
  checkout, which excludes `game/assets/audio/`).

## Honest gaps (not claimed fixed until played)

- **User playtest still owed.** The wiring is script-verified (node
  `--check` on both edited files, test passes locally), but no one has yet
  played a Pantera fight and heard the real grunts. Do NOT tell the user
  voice is "fixed" until they play and confirm.
- **Roars reserved.** Clips longer than 2.0s (roars, e.g. the 6.27s clip)
  are in the manifest but NOT used for grunts; they are reserved for KO /
  soul-surge moments, which need their own trigger wiring (next lane).
- **Other fighters' voices not wired.** This PR wires Pantera only. Other
  fighters still use the procedural grunt until their banks are pulled and
  wired the same way.
- **Sampler MP3s stay in workspace.** The 3 sampler MP3s (review artifacts)
  are NOT committed to the repo; the game-ready individual WAVs are.
  Workspace source: `~/workspace/king-mods/` (manifest + samplers + raw
  banks preserved there).

## Verification (local, pre-commit)

- All 53 WAVs: RIFF/WAVE headers valid (53/53).
- `node --check` on edited `game/js/audio.js` and `game/js/game.js`: OK.
- `node test/voice-bank.test.mjs` against a full local copy: ALL PASS
  (manifest checks included).
- CI note: `game-unit-tests` sparse checkout excludes
  `game/assets/audio/`, so manifest checks skip there by design; code
  checks still run.

# Music rotation + Nosferatu multi-track wiring (2026-10-24)

## What changed

- `game/js/music.js`: rotation pools (`pickRotationTrack`, `_poolFor`,
  `_nextRotation`, persisted per stage/mode in localStorage), T7
  match-point variant swap (`playFinalRound`), ordered cue sequences
  (`playSequence`, `_playSequenceNext`), victory-jingle → results-theme
  chaining. `pickTrack` is unchanged (backward compatible).
- `game/data/music-library.json`: 44 tracks (14 existing unchanged +
  25 Nosferatu game tracks + 5 Tekken data-only slots), `rotation`
  mode sequential, `ep01-fight` sequence. One tag fix:
  `battle-implosion` stages `helios-palace` → `helix-palace`
  (the `stages.js` id; the old tag could never match a stage).
- `game/js/main.js`: music call sites — `show()` routes menu/select/
  stage/online themes, `matchOver` plays the victory jingle,
  `unlockAudio` unlocks the music engine, `startFight` plays the
  rotating stage pool (replacing the direct procedural start; the
  engine falls back to procedural internally, so this cannot double
  music or silence a fight).
- `game/js/game.js`: round-flow intensity — round start 0.55, FIGHT
  0.7 (final round 0.85 + variant swap), KO/time-up 0.3, under-25%-HP
  lift to 1.0 (edge-triggered).
- `test/music-rotation.test.mjs`: 31 checks, all passing locally
  (rotation order/wrap, pending exclusion, final-round swap/no-op,
  sequence advance/resume, shipped library contiguity + tags).

## Why this shape (Tekken rules, from the files)

- Tekken jukebox rule: tracks assigned by stage/mode/mood tags; the
  pool rotates instead of one track per stage forever. Stage-tagged
  tracks still open their stage's rotation.
- T7 match-point rule: Round 1 theme + Final Round variant (e.g.
  Arena "Attack on Rhythm 1st/2nd"); the deciding round crossfades
  to the variant. Music plays across rounds and changes only on
  screen/stage change (existing engine behavior, kept).
- Nosferatu cut rule: M4 boundaries + subdivide pieces over 300s at
  interior novelty peaks >= 2.5 with >= 100s spacing. 25 tracks,
  contiguous 0–5067s. The GPU cutting script ships in this PR at
  tools/music/kaggle-cut-tracks.py; the full per-track table is the
  library JSON itself plus the workspace cut plan
  (nosferatu-tracks-manifest.json).

## Sources + license flags (no guesses, no invented names)

- Nosferatu audio: `nosferatu-exact.mp3` = owner's video audio =
  Internet Archive `Nosferatu1922VHS` transfer (waveform r ≈
  0.997–0.998). Anonymous 1980s VHS synth score, MoMA 1947 print.
  NO composer name exists in any documented source; none invented.
  Track titles use the film-scene + time-range scheme name.
- Excluded: `nosferatu-full.mp3` (Schirmann orchestral, verified
  NO-MATCH) and all Bernard/Erdmann cue names. Never used.
- License: the VHS synth score's copyright status is UNKNOWN — do
  NOT label it public domain. Use-basis decision pending.
- Tekken slots: Tekken 7 OST / TekkenMods BGM mods, data-only until
  audio bytes are downloaded (browser task). License: tekken-pending.

## What is still pending (browser tasks — this lane cannot do them)

1. Run `kaggle-cut-tracks.py` in the Kaggle GPU notebook (attach
   `nosferatu-exact.mp3` first). The script proves the GPU with a
   real CUDA job and fails loudly without one.
2. Commit the 25 cut mp3s to `game/assets/music/` (library filenames
   already match; no code change needed once they land). Then copy
   the run's loop points into the library's `loopStart`/`loopEnd`.
3. Download Tekken 7 OST / BGM-mod audio for the 5 pending slots and
   set their `file` fields.
4. Story-lane one-liner: call `playSequence('ep01-fight')` from the
   Ep1 story fight (engine + data are done; the hook point belongs
   to the story lane).

Until 1–3 land, the game plays correctly: rotation over existing
tracks + procedural fallback. Nothing in this PR claims otherwise.

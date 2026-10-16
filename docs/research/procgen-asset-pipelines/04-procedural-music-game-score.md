# 04 — Procedural Music for Game Soundtracks (2026 research)

**Date:** 2026-10-16 · **Scope:** game-score-oriented procedural music tools.
**Coordination note:** sibling audio branch covers YuE / Stable Audio / MusicGen — those are
*not* duplicated here. This doc covers **real-time procedural/adaptive score** for the
playable build (Three.js), where shipping audio *files* is the wrong answer and a
generative engine is the right one.

## What we found

### Tone.js (Tonejs/Tone.js) — PULLED (wired)
- Web Audio framework for interactive music in the browser. **MIT**, 14,772 stars,
  pushed 2026-10-12 (actively maintained). The standard answer for browser music.
- **Why it beats what we have:** today the playable build has no adaptive score. A
  Tone.js engine gives **infinite, state-driven music** — menu/explore/combat/victory
  layers that crossfade on game state, zero audio files shipped, tiny download.
  Precedent: No Man's Sky "Pulse" (game-state-gated generative layers) and Spore's
  Markov melody generator ("composing in probabilities").
- Wire-up: `tools/procgen/game-score/` — `wh_adaptive_music.mjs`:
  - pure, node-testable composition core (scales, chord progressions, Markov melody,
    intensity → layer mapping — no Web Audio dependency),
  - `wh_tone_adapter.mjs`: thin Tone.js adapter (Transport scheduling, synths, effects),
  - `test_music.mjs`: offline tests (deterministic seed → reproducible output).
  Tested 2026-10-16.

### Web Audio adaptive-score pattern (documented)
- **ouigame** (aurelienpautet): `MusicEngine` — look-ahead Web Audio scheduler, 4-bar loop,
  8 layers (melody/bass/arp/kick/snare/hat/cymbal/timpani) each on its own gain node,
  crossfaded by gameplay intensity; separate sfx/music buses. Clean, small, proven —
  our adapter follows this architecture.
- **veilborn** (stobieee-bit): layered Web Audio score with 5 situation states
  (calm/explore/threat/combat/episode); no audio assets, everything synthesized at runtime.
- **tropico2** (vincent-p-essy): deterministic seeded music generator kept on its own RNG
  stream so toggling sound never changes the simulation. Adopted as a rule: **music RNG is
  isolated from gameplay RNG**.

### MIDI-GPT (Metacreation Lab) — EXCLUDED (license)
- Transformer MIDI generation, **MIT-licensed code**, pretrained models on Hugging Face,
  `pip install "midigpt[inference]"`. BUT: "its use has been restricted to **non-commercial
  purposes** so far" (model/training-data terms). Per license honesty: documented, not
  pulled. Revisit if terms change — it would be the offline BGM composer for menus.

### Melodrive "unlocked" tools — EXCLUDED (commercial crack)
- Search surfaced `melodrive-unlocked-tool` repos: cracked commercial adaptive-music
  middleware. **Never crack commercial software.** Excluded, documented as a hard no.

### kleer001/music_loom — research reference
- `research/game_music_structure.md`: excellent survey of generative flagships
  (NMS Pulse, Spore). Reference only — no code to pull.

## Design rules adopted for WH score
1. Music RNG isolated from gameplay RNG (tropico2 rule).
2. Intensity-driven layer crossfades, never hard cuts (ouigame/veilborn pattern).
3. Composition core pure + seeded → reproducible; adapter thin → swappable (Tone.js today).
4. Zero shipped audio files for adaptive layers; composed stems only where authored music
   is wanted (sibling audio branch owns that).

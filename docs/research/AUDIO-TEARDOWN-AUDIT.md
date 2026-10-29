# AUDIO TEARDOWN AUDIT (worker 26, 2026-10-22)

What the teardown tree actually contains for voice + music, and what was
pulled into the game. Method: file inventory + doc grep across
`teardown/`; no copyrighted bytes shipped (owner law #8).

## Voice systems found

1. **`teardown/tekken3/tools/tekken3recompiled/src/tekken3_jun_voices.c`**
   — the Tekken 3 (recompiled) character-voice dispatcher: per-player
   voice banks, sample ids 160–171, routed through the SPU before the host
   audio queue, with sha256-verified private banks. Pulled lesson: voice is
   a SEPARATE bus from SFX/music with its own gain — our `audio.voiceGain`
   / `voiceBus()` mirrors this.
2. **`teardown/tekken7/tekkenmods-docs/.../Structures/Voiceclip/index.md`**
   — Voiceclip structure doc (stub: "More info coming soon"). Confirms
   Tekken maps voice clips as data structures per character; trigger
   taxonomy taken from series convention instead.
3. **`teardown/urban-reign/sound/ok_adx/ADX-INVENTORY.csv`** — 1,000+ ADX:
   per-character voice clips named `v_<char>_*` (e.g. `v_masa44.adx`,
   `v_ms012.adx`), separate from BGM. Pulled lesson: voice clips live in a
   per-character namespace apart from music — our
   `game/assets/voices/<fighter>/` mirrors this.
4. **Trigger taxonomy (series convention, no single doc)**: round intro →
   "FIGHT!" → hit efforts → KO call → win pose line → taunt beat. Wired
   1:1 in `game/js/game.js` (see `docs/VOICE-MAPPING.md` trigger map).

## Music systems found

1. **Urban Reign ADX inventory** — battle BGM as `bgNN_01.adx` (ONE track
   per stage: bg01..bg10+), menu/DC music as `bgm_*`. Pulled lesson:
   **stage-tagged BGM assignment** — `MusicEngine.pickTrack({stage})`.
2. **Tekken convention** (across tekken3/7/8 teardowns): stage BGM +
   title/select/versus/results themes; music continues ACROSS rounds;
   final-round lift; announcer ducks music. All implemented in
   `game/js/music.js`.
3. **No music CODE** (sequencers, transition logic) was recovered from any
   teardown — the systems above are reconstructed from the asset naming +
   series convention and documented as such. Nothing is presented as
   "pulled code" that wasn't.

## Shippable audio found (owner's own Eastern Mind game — extraction 100% complete 2026-10-22)

`teardown/eastern-mind/` — the owner's own game, so copyright-clean.
Final tally per the extraction report: **5,321 bitmaps** (art pipeline —
not this lane), **229 sounds** (this lane), **22 videos** (cutscene system
— not this lane), **3 CD audio tracks** (music library — this lane).

- **Sound bank**: all 229 sounds ship as `game/data/sound-bank.json` +
  `game/assets/sounds/*.ogg`, categorized voice/prologue/stage with
  durations, playable via `voice.playSound(bankId)`. The voice-manifest
  clips (`mappedTo`) are drawn from this bank.
- **Voice**: `incarnation-system/sounds/R_{BYOU,GYOU,GYOU2,JIN,KAI,LETS,LETSB,SHA,TOH,ZEN,ZEN2,SYSTEM}/`
  (18 clips, 0.2–8 s), `stage-1-plains-of-chi-u/sounds/F_KING/` (9 clips),
  `stage-4-tree-of-life/sounds/L_KING/` (5 clips),
  `prologue-ending/sounds/{D_BOOK,D_FACE,D_MIRROR,D_ROCK,D_SEA,D_SUMIE,SHARED}/`
  (60 clips — prologue narration/ambience, in the bank as cutscene candidates).
- **Music**: `soundtrack/` — the 3 CD tracks `cda-tong-nou-theme.wav`
  (269 s — **the Tong-Nou Theme, flagship of the jukebox**),
  `cda-tong-nou-esoteric-mix.wav` (480 s),
  `cda-transmigration-ending.wav` (316 s), plus `ending-theme.wav`
  (301 s). Converted WAV→OGG Vorbis and shipped in `game/assets/music/`.

## Explicitly NOT shipped

- Tekken/SF/KOF/DOA/SC voice bytes or announcer audio (copyrighted).
  Manifests carry the mapping + placeholder lines only.
- Urban Reign ADX (Namco-copyrighted). Documented as the reference
  architecture + local extraction path only.
- Crowd reactions — deferred by owner decision (see VOICE-MAPPING.md).

## Voice-line content caveat

Tier-A clip `text` is canon-flavored but the clip bytes were never
auditioned by ear in this pass. Every such clip's `note` says
"unverified by ear". The voice session transcribes/verifies before any
clip is marked final. Nothing fake is presented as final.

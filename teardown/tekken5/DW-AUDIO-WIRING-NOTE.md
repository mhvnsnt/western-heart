# DW Audio Wiring — blocker note (Job 3, 2026-11-08)

**Status: NOT WIRED — three measured blockers, no workaround built.**
The decoded audio is measurements + 3 proof WAVs only. Nothing below is
a guess; each blocker names the exact measurement that would unblock it.

## What exists (measured)

- `teardown/tekken5/dw-audio-decoded.json` (187,999 B) — measurements only:
  18 P3Dp files, 391 clips, 318 unique regions, 6,562,472 samples,
  297.6 s at 22050 Hz. Per-clip fields are `clip_id`, `size_bytes`,
  `start`, `field5/6/7` + decoded frames/samples/duration/peak/rms.
  No audio bytes, no per-clip sample-rate flag.
- 3 proof WAVs only, workspace-only, NOT in git:
  `~/workspace/devil-within-decode/audio-proof/` — `blu-clip0.wav`
  (0.18 s), `c10-clip0.wav` (0.21 s), `largest.wav` (7.44 s), all
  ffprobe-verified PCM s16le mono 22050 Hz.
- Decoder tool (landed): `tools/snd_decode.py` — ffmpeg adpcm_psx via
  synthetic VAGp header. Re-running it over the snd containers
  regenerates the full WAV set; the tool exists, the run is owed.
- 2 clips undecodable: `snd_title.dat` clips 6–7 (0 bytes in file —
  data absent from this disc image). 1 short clip: `snd_title.dat`
  clip 5 (only its first 60%).

## The precedent in the game (the wiring pattern to follow)

`game/js/audio.js` already wires real decoded game audio exactly this
way for Eastern Mind: 229 real 8-bit/22kHz mono WAVs, decoded on demand
via `fetch` + `decodeAudioData`, cached (`_emSfxCache`), played through
the SFX bus (`playEMSfx(id)` → `AudioEngine.EM_SFX` slot map, catalog
`game/data/eastern-mind-sfx.json`, acoustic categorization with a
listening pass refining semantics). The DW set wants the same shape:
a `DW_SFX` slot map + a `game/data/dw-sfx.json` catalog, played through
the same fetch/decode/cache path. No new sound engine is needed.

## Blockers

1. **No full WAV set on disk.** Only the 3 proof WAVs exist. The 391
   clips' WAVs were never generated, and the `snd_*.dat` containers are
   NOT in the repo (only in the disc image / workspace extraction).
   Generating them is a re-run of the landed `tools/snd_decode.py`
   (~13 MB as 22050 Hz mono s16le WAV: 6,562,472 samples × 2 bytes).
   The outputs CANNOT go in git — decoded commercial audio stays out
   of git (decode log §19) — so live wiring needs remote-asset hosting
   (R2/B2) or build-time generation from the disc bytes. **Unblocks:**
   Jay's call on hosting (R2/B2 credentials/setup) or on a build-time
   generation step; then run the decoder and host the WAVs.
2. **Sample rate per clip unconfirmed.** 22050 Hz is the DEFAULT tier
   of a 3-rate select measured in the code blob (DW-DECODE-LOG §20,
   function at file 0x50050: header flag bit 0x20 → 48000, 0x40 →
   44100, else 22050). The per-clip flag word (sound-header struct
   +0x58) is NOT in `dw-audio-decoded.json` — the clip table carries
   only field5/6/7. **Unblocks:** read the header flag bits per clip
   from the snd containers (a measurement step in `snd_decode.py`,
   not a guess) and record the rate per clip before any WAV is
   trusted as 22050.
3. **Clip → event curation owed.** The 391 clips have no semantic
   mapping — which clip is a hit, a roar, a UI blip is unknown from
   peak/rms/duration alone. The Eastern Mind precedent used an
   acoustic categorization catalog + a listening pass. **Unblocks:**
   a listening pass over the generated WAVs (or a measured mapping
   from the game's sound-table data, if it is found) producing the
   `dw-sfx.json` catalog with event slots.

## What was NOT done

No slot map pointing at nonexistent files was written — that would be
a stub, and the standing rule forbids stubs presented as done. When
blockers 1–3 clear, the wiring is: run the decoder → host the WAVs →
write the catalog + slot map following the Eastern Mind pattern →
verify with a watched in-game check that a DW sound plays on its event.

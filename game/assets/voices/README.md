# game/assets/voices — character voice recordings

One subdirectory per fighter: `game/assets/voices/<fighter-id>/`.

Files are produced by the voice cloning pipeline
(`tools/character-voice/voice-clone/`, contract:
`docs/VOICE-CLONING-PIPELINE.md`) — never hand-place files here without
updating the matching manifest in `game/data/voices/<fighter-id>.json`.

Asset spec (enforced by the pipeline's `master` stage):
- OGG Vorbis (MP3 fallback), 44 100 Hz, mono, peaks ≈ −3 dBFS
- 80 ms room tone head/tail, one clip ≤ 3 s (win lines ≤ 5 s)
- ≤ 500 KB per clip, named `<trigger>-<NN>.ogg`
  (e.g. `dorowani/win-01.ogg`)

Manifest clip `status` is `"placeholder"` until the real recording lands;
the in-engine voice pipeline (`game/js/voice.js`) plays subtitle-only for
placeholders — honest by design.

**Standing rule (2026-10-22):** audio sent to the owner goes as direct
download links via remote-storage upload, NEVER as in-chat attachments
(the in-chat audio player is broken on the owner's Android app).

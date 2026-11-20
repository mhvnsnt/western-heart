# tools/character-voice — Western Heart character voice wiring (2026-10-16)

**Owner law: Chatterbox stays the character-voice default. Everything here complements, never replaces.**
Research: `docs/research/CHARACTER-VOICE-2026.md` · canonical: cape-jones `docs/research/AUDIO-VOICE-MUSIC-2026.md`.

## Files
- `phone_cleanup_chain.py` — phone-recorded line → DeepFilterNet (de-reverb/denoise)
  → resemble-enhance (neural polish) → ffmpeg `loudnorm` (broadcast). Run on Kaggle T4
  or any machine with the pip packages installed.
- `voice-changer-rig.md` — create-a-fighter real-time voice changer integration notes.

## Quick start (Kaggle T4)
```bash
# installs all eight audio-2026 tools + smoke tests
python3 kaggle_setup_audio2026.py   # from cape-jones production/pipeline/audio-2026/
# clean a phone-recorded fighter line
python3 phone_cleanup_chain.py raw_line.wav clean_line.wav
```
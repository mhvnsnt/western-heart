# tools/character-voice — Western Heart character voice wiring (2026-10-16)

**Owner law: Chatterbox stays the character-voice default. Everything here complements, never replaces.**
Research: `docs/research/CHARACTER-VOICE-2026.md` · canonical: cape-jones `docs/research/AUDIO-VOICE-MUSIC-2026.md`.

## Files
- `phone_cleanup_chain.py` — phone-recorded line → DeepFilterNet (de-reverb/denoise)
  → resemble-enhance (neural polish) → ffmpeg `loudnorm` (broadcast). Run on Kaggle T4
  or any machine with the pip packages installed.
- `voice-changer-rig.md` — create-a-fighter real-time voice changer integration notes.
- **`voice-clone/`** (2026-10-22) — PRODUCTION voice cloning pipeline:
  `clone_pipeline.py` orchestrates spec → remote generation → creature-FX →
  master → deposit → deliver. **Model weights never touch local disk** —
  inference runs on serverless APIs (`backends/remote_api.py`) or a remote
  GPU (`backends/remote_gpu.py`). Dorowani is the pilot
  (`voice-specs/dorowani.yaml`: raspy, low, Squirtle-like creature voice).
  Contract: `docs/VOICE-CLONING-PIPELINE.md`.

## Quick start (Kaggle T4)
```bash
# installs all eight audio-2026 tools + smoke tests
python3 kaggle_setup_audio2026.py   # from cape-jones production/pipeline/audio-2026/
# clean a phone-recorded fighter line
python3 phone_cleanup_chain.py raw_line.wav clean_line.wav
```

## Quick start (voice cloning — no local weights)
```bash
cd voice-clone
python3 clone_pipeline.py --fighter dorowani --backend remote_api --dry-run
# needs WH_VOICE_API_URL + WH_VOICE_API_KEY for a real generation run;
# without them the pipeline refuses loudly instead of faking output.
```

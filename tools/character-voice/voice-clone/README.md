# tools/character-voice/voice-clone — remote-first voice cloning pipeline

Production voice cloning for the Western Heart roster. **Model weights
never touch local disk** — all inference runs on serverless APIs or a
remote GPU. Built around Chatterbox (owner law: the character-voice
default, never replaced).

Contract: `docs/VOICE-CLONING-PIPELINE.md`

## Layout

```
voice-clone/
  clone_pipeline.py      orchestrator: spec → generate → creature-fx →
                         master → deposit → deliver
  backends/
    remote_api.py        serverless inference (Replicate / fal.ai / HF)
                         — pure HTTPS, zero local weights (recommended)
    remote_gpu.py        RunPod / Kaggle / SSH GPU box — weights live
                         remotely, only WAVs come back
  voice-specs/
    dorowani.yaml        PILOT: raspy, low, Squirtle-like creature voice
  README.md              this file
```

## Quick start

```bash
# 1. Validate the pilot spec (no inference, no spend)
python3 clone_pipeline.py --fighter dorowani --backend remote_api --dry-run

# 2. Serverless generation (needs WH_VOICE_API_URL + WH_VOICE_API_KEY)
export WH_VOICE_API_URL=https://api.replicate.com/v1/models/resemble-ai/chatterbox/predictions
export WH_VOICE_API_KEY=...
python3 clone_pipeline.py --fighter dorowani --backend remote_api --deliver
# → prints direct download links for owner review (never attachments)

# 3. After owner approval, deposit into the game + flip manifest to final
python3 clone_pipeline.py --fighter dorowani --backend remote_api --deposit --deliver

# Remote GPU instead:
python3 clone_pipeline.py --fighter dorowani --backend remote_gpu \
    --host user@gpu-box --deliver
```

## The honesty rules (enforced)

- `clone_pipeline.py` **refuses** local weight downloads (see `refuse_local_weights()`).
- Only `creature-fx` (ffmpeg filters) and `master` (loudnorm/encode) run
  locally — no ML, no weights.
- Clips stay `status: "placeholder"` in the game manifest until `--deposit`
  runs after owner approval. We never synth a fake "final" voice.
- `deliver` uploads via remote-storage and prints **direct download links**
  (standing audio-delivery rule — the in-chat player is broken on Android).

## New fighter

1. Copy `voice-specs/dorowani.yaml` → `voice-specs/<fighter>.yaml`.
2. Fill `direction` (owner's words), `qualities`, `chatterbox_params`,
   `creature_fx` (or omit for a straight human voice), `reference_audio`.
3. `--dry-run`, then generate → review links → `--deposit`.

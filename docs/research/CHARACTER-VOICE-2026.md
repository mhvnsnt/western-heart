# Character Voice 2026 — Western Heart

**Date:** 2026-10-16 · Companion to cape-jones `docs/research/AUDIO-VOICE-MUSIC-2026.md` (canonical research).
**Owner law (standing): Chatterbox is the BEST TTS — never replace for characters. Everything below complements only.**

## Voice stack for the roster

| Layer | Tool | License | Use |
|---|---|---|---|
| **Default character voice** | Chatterbox (already pulled) | MIT | Every roster fighter's voice. Zero-shot clone + `exaggeration`/`cfg_weight` dials. |
| Bulk ADR / scratch | **F5-TTS** (new) | MIT | Fast zero-shot TTS for episode ADR, scratch dialogue, multilingual dubs. `pip install f5-tts==1.1.22`. Wired into cape-jones `dialogue_pipeline.py` (`--engine f5tts`, needs `ref_audio`+`ref_text` per line). |
| Cross-lingual + directed emotion | **CosyVoice 3** (new) | Apache-2.0 | `Fun-CosyVoice3-0.5B-2512`: clone a voice across 9 languages (EN↔JA), per-line direction via `inference_instruct2` ("say it angry, fast"). GGUF quants run on CPU. Wired into `dialogue_pipeline.py` (`--engine cosyvoice`). |
| CPU fallback | **audio.cpp** chatterbox-GGUF (new) | Apache-2.0 (engine) | Chatterbox-quality voices quantized for laptop/phone. Per-model weights keep own licenses. |
| **Create-a-fighter voice changer** | **w-okada/voice-changer** (new) | MIT | Real-time VC rig: `server/MMVCServerSIO.py` socket server, RVC/ONNX model slots. Player's mic (or base voice) → character voice live. See `tools/character-voice/voice-changer-rig.md`. |
| Entrance music stems | **python-audio-separator** (new) | MIT | Split entrance tracks into stems (vocals/drums/bass/other) for dynamic in-game mixing. |
| Menu / entrance music | **DiffRhythm** (new) | Apache-2.0 | Lyrics→full song on Kaggle T4 (`--chunked`, 8GB VRAM min). Entrance themes, menu beds. |
| Phone-line cleanup | **DeepFilterNet → resemble-enhance** (new) | MIT/Apache-2.0, MIT | `tools/character-voice/phone_cleanup_chain.py`: de-reverb/denoise → neural polish → loudnorm. For owner-recorded lines. |

## What was NOT pulled (and why)
- **IndexTTS2** — bilibili model-use agreement (commercial needs permission).
- **XTTS** — no v3 exists; CPML non-commercial; Coqui defunct.
- **YuE2-3B** — best open song quality but weights CC-BY-NC-4.0 (research only).
- **TangoFlux** — best open text-to-SFX but Stability AI Community License (non-commercial).
- **seed-vc** — GPL-3.0; MIT voice-changer covers the slot.
- Full tables: cape-jones `docs/research/AUDIO-VOICE-MUSIC-2026.md`.

## Install (Kaggle T4)
Run cape-jones `production/pipeline/audio-2026/kaggle_setup_audio2026.py`
(GPU, internet ON) — installs all eight, smoke-tests each.
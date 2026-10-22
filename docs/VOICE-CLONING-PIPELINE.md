# WESTERN HEART — Voice Cloning Pipeline (production)

Owner context (2026-10-22): the user **rejected** a Hubert TTS voice for
Dorowani — *"it doesn't have any of the qualities I asked for"* (raspy,
low, Squirtle-like creature voice). Generic TTS cannot do directed
character voices. This pipeline replaces placeholder TTS with **real AI
voice cloning**, built around the standing default:

**Owner law (standing): Chatterbox is the BEST TTS — never replace for
characters.** (`docs/research/CHARACTER-VOICE-2026.md`)

## 1. What this pipeline is

A remote-first voice cloning system that turns a **voice spec** (character
+ qualities + reference) into finished, game-ready voice clips:

```
voice-specs/<fighter>.yaml
      │  (direction, qualities, chatterbox params, creature FX, lines)
      ▼
┌─────────────┐   ┌──────────────┐   ┌─────────────┐   ┌──────────┐
│   generate  │──▶│  creature-fx │──▶│    master   │──▶│ deposit  │
│ (REMOTE ONLY│   │ (local CPU,  │   │ (loudnorm,  │   │ (game/   │
│  see §3)    │   │  no ML)      │   │  44.1k/OGG) │   │  assets) │
└─────────────┘   └──────────────┘   └─────────────┘   └──────────┘
                                                        │ status
                                                        ▼  placeholder→final
                                              game/data/voices/<fighter>.json
```

Code: `tools/character-voice/voice-clone/` (`clone_pipeline.py` +
`backends/`). Every stage is logged; the `deliver` stage uploads finished
clips via remote-storage and prints **direct download links** (standing
audio-delivery rule — never in-chat attachments).

## 2. How character qualities are actually achieved

Cloning reproduces a reference voice; **direction** produces the
qualities. Two levers, both spec'd per fighter:

1. **Chatterbox zero-shot clone** from a direction-matched reference
   sample + the `exaggeration` / `cfg_weight` / `temperature` dials.
   `exaggeration` is the expressiveness lever — creature voices live
   high on it.
2. **Creature FX chain** (deterministic, local CPU, no ML weights) for
   what TTS alone cannot give a creature: pitch shifted down, formant
   shifted down, subtle growl (amplitude-modulated saturation), breath
   retention. This is how film creature vocals are built — the clone
   gives the voice its *identity*, the FX chain gives it its *species*.

Dorowani's target (pilot): **raspy, low, Squirtle-like creature voice** —
playful trickster energy, Japanese word bursts, never sentences. Spec:
`tools/character-voice/voice-clone/voice-specs/dorowani.yaml`.

## 3. Weight handling — NO local weights, ever

Model weights **never touch local disk**. The user's disk rules are
mandatory (`docs/owner-directives.md`: "No full game downloads", and this
task: "must NOT pull model weights onto local disk and clutter it up").
Three remote options, in preference order:

| # | Backend | How weights are handled | Needs |
|---|---------|------------------------|-------|
| 1 | **Serverless inference API** (`backends/remote_api.py`) — Replicate / fal.ai Chatterbox endpoints | Weights live on the provider's infra. Pure HTTPS: text+params in, WAV out. Zero local weights, zero local GPU. | `WH_VOICE_API_KEY` (pennies per generation) |
| 2 | **Remote GPU** (`backends/remote_gpu.py`) — RunPod / Kaggle / SSH box | Weights live on the remote machine; a runner executes there; only finished WAVs `scp` back. | SSH access or provider key; GPU billed by the minute |
| 3 | **Streaming inference** — HF Inference API | Weights stay on HF infra; streamed inference, nothing persisted locally. | `HF_TOKEN` |

The pipeline **refuses** local weight downloads: `clone_pipeline.py`
aborts if it detects a local Chatterbox/HF snapshot path or a
`pip install chatterbox` style step. Rationale is logged every run —
disk bloat is how the Hubert attempt went wrong.

Only the **FX/master stages run locally** (ffmpeg filters — no ML, no
weights). Everything that needs model weights runs remote.

## 4. Creating a new character voice

1. **Write the spec**: copy `voice-specs/dorowani.yaml` →
   `voice-specs/<fighter>.yaml`. Fill `direction` (owner's words),
   `qualities`, `chatterbox_params`, `creature_fx` (or `null` for a
   straight human voice), and `reference_audio`.
2. **Reference audio** (the most important input): a 10–60 s sample
   embodying the qualities — the owner records/approves it (voice
   direction is theirs), or point at an existing archetype sample.
   Clean it with `tools/character-voice/phone_cleanup_chain.py` first.
3. **Run**: `python3 clone_pipeline.py --fighter <id> --backend remote_api`
   (or `--backend remote_gpu --host ...`). Dry-run with `--dry-run` to
   validate the spec without spending inference.
4. **Review**: the `deliver` stage prints direct download links for every
   clip. The owner listens (on their phone — links, not attachments)
   and approves or redirects ("raspiter", "lower", "more growl" →
   adjust spec, re-run — iteration is cheap).
5. **Deposit**: on approval, `--deposit` writes clips to
   `game/assets/voices/<fighter>/` and flips the manifest
   `status: placeholder → final`. The in-engine voice pipeline
   (`game/js/voice.js`) picks them up with zero code changes.

## 5. Asset spec (what "final" means)

Same as `docs/VOICE-PIPELINE.md` §5, enforced by the `master` stage:

- OGG Vorbis (MP3 fallback), 44 100 Hz, mono, peaks ≈ −3 dBFS,
  80 ms room tone head/tail, one clip ≤ 3 s (win lines ≤ 5 s),
  ≤ 500 KB per clip, named `<trigger>-<NN>.ogg`.
- The `master` stage rejects (does not deposit) any clip that fails
  these — a bad file never reaches the game.

## 6. Dorowani pilot status (2026-10-22)

- ✅ Voice pipeline (engine, triggers, subtitles): shipped.
- ✅ Dorowani voice manifest (9 clips): shipped, all `placeholder`.
- ✅ Intro-interaction voice refs: wired.
- ✅ Cloning pipeline (code + backends + spec): shipped in this PR.
- ⬜ **Reference audio**: needed — owner to provide/approve a raspy,
  low, creature-ish sample (or approve archetype-first generation).
- ⬜ **Inference credentials**: needed — `WH_VOICE_API_KEY` (serverless)
  or remote GPU access. No generation run happens without one.
- ⬜ **Generation + owner review loop**: pending the above.

The pipeline will NOT fabricate a "final" voice locally and present it —
that is exactly the Hubert mistake the owner rejected. Placeholders stay
honest until the real clone lands.

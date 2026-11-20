# AI Inference for Western Heart (game-side) — 2026-10-16

Companion to the master research doc in cape-jones
(`docs/research/AI-INFERENCE-HARDWARE-2026.md`) — this one is scoped to what the
**game and its tooling** need. Same hardware: Kaggle T4 x2 (30 GPU-hrs/wk), Colab T4,
local CPU VM, phone.

## 1. Architecture rule

**No model inference inside the game client.** The game (and the owner's phone) are
thin clients: they speak HTTP to inference servers running on the Kaggle/Colab T4s.
Reasons: 16GB VRAM is a server budget, not a per-player budget; model weights carry
licenses that forbid redistribution (Gemma, Llama-family, FLUX); and a server lets us
swap models without shipping a new build.

```
game client / tools / phone
        │  OpenAI-compatible HTTP (:8080) or ComfyUI API (:8188)
        ▼
llama-server  (dialogue, tools, docs)   ← tools/ai-inference/inference_client.py
ComfyUI       (textures, promo art)     ← workflows in cape-jones tools/inference/
```

## 2. NPC dialogue / tool-calling backend

- **Now:** `llama-server` (llama.cpp, MIT) on one Kaggle T4, exactly as documented in
  the cape-jones runbook. Single binary, GGUF-native, OpenAI-compatible.
- **Model pick:** Qwen3-30B-A3B MoE UD-IQ3_XXS (~11–13GB) or a 14B dense Q4_K_M for
  headroom; both leave VRAM for context. Qwen3.x has strong tool-calling; run coding/
  tool finetunes with thinking **disabled** (no-think) — 2026 coder models over-think
  by default and burn the token budget.
- **Later:** vLLM (Apache-2.0) if we need concurrent NPCs; SGLang (Apache-2.0) if
  dialogue traffic shares long prefixes (system prompts) — ~29% better there.
- **Client:** `tools/ai-inference/inference_client.py` (stdlib only, tested) — copy it
  into any tool; point `INFERENCE_URL` at the server.

## 3. Game-asset generation (textures, promo art)

- **Base renders:** FLUX.1-dev GGUF Q4_0 on the T4 via ComfyUI + vendored
  city96/ComfyUI-GGUF node (Apache-2.0) — see cape-jones `tools/inference/`.
- **Style LoRAs:** train per-game/per-faction style LoRAs with Ostris ai-toolkit (MIT)
  on the Kaggle T4 (quantized base + 8-bit optimizer fits 16GB). A style LoRA is
  tens of MB — version it in the repo like any other asset.
- **License honesty:** FLUX.1-dev weights are BFL **non-commercial** — fine for our
  internal production art, do NOT redistribute the weights. Log any FLUX-derived
  checkpoint accordingly.

## 4. Character voices

- **Trained voices:** RVC v2 (MIT architecture) trains on a T4 with ~10 min of clean
  audio per character. Pipeline: TTS line (Chatterbox, already in the voice pipeline)
  → RVC timbre conversion → game-ready voice.
- **Zero-shot:** Chatterbox (MIT) / IndexTTS-2.5 for 6–15s-sample cloning with no
  training step.
- **Excluded:** XTTS-v2 (CPML non-commercial), F5-TTS weights (CC-BY-NC) — documented
  in the master doc, not pulled.

## 5. Fine-tuning for game behavior

- **Dialogue/behavior LoRAs:** Unsloth QLoRA (Apache-2.0) on Colab T4 — 8B models train
  in ~12h; adapters are 10–100MB. Train per-character speech patterns, quest logic,
  announcer style as separate adapters served via multi-LoRA (vLLM) or swapped at
  load (llama-server).
- **Reproducible runs:** Axolotl YAML configs (Apache-2.0) checked into the repo.

## 6. What landed in THIS repo from the 2026-10-16 pull

| Item | Where |
|---|---|
| This doc | `docs/research/AI-INFERENCE-GAMESIDE-2026.md` |
| OpenAI-compatible client (tested) | `tools/ai-inference/inference_client.py` |
| Server choice + upgrade path | `tools/ai-inference/serve-config.md` |

Heavy pieces (ComfyUI node, workflows, runbooks, master research) live in
**mhvnsnt/cape-jones** `tools/inference/` + `docs/research/AI-INFERENCE-HARDWARE-2026.md` —
one copy, referenced here, not duplicated.

## 7. License summary (game-side relevant)

- Safe to use/ship in tooling: llama.cpp (MIT), vLLM/SGLang/Unsloth/Axolotl (Apache-2.0),
  ComfyUI-GGUF (Apache-2.0), ai-toolkit (MIT), RVC arch (MIT), Wan 2.1 (Apache-2.0).
- Referenced, not vendored: ComfyUI (GPL-3.0).
- Non-commercial — internal use only, never redistribute: FLUX.1-dev weights,
  XTTS-v2, F5-TTS weights.
- Model weights (Llama, Gemma families) carry their own terms — serving publicly =
  redistribution. Our servers are internal.

## 8. Open test items (flagged for parent)

- [ ] `llama-server` end-to-end with a real GGUF (model download was in flight at pull time)
- [ ] First GPU run of the ComfyUI FLUX/Wan workflows on a Kaggle/Colab T4
- [ ] RVC training smoke test for one character voice on the T4

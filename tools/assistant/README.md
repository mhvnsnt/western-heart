# tools/assistant — Western Heart Assistant Tool Suite

Two-tier tool routing for the assistant. **Tier 2 (free) is the default.**
Tier 1 (token-based) is used when quality demands it.

## The Tiers

| | Tier 1: Token-based | Tier 2: Free |
|---|---|---|
| **Cost** | Consumes assistant tokens per call | $0 — no tokens, no API keys |
| **Quality** | Highest available | Good to excellent |
| **When** | User-facing deliverables, user explicitly wants the best, free options fall short | Bulk work, drafts, pipeline/crew use, default choice |

**Routing policy:** Try Tier 2 first. Escalate to Tier 1 when:
1. Tier 2 quality is insufficient for the use case
2. The user explicitly asks for the best quality
3. The output is user-facing and first impressions matter
4. Tier 2 is rate-limited or unavailable

Never escalate for bulk/background work unless the user approves the token spend.

## Tools

### `image-edit-generative` — natural-language image editing
- **Tier 1:** Assistant's media pipeline (`media.generate_image` with image + text). Highest quality — Gemini/Grok-class surgical edits. Use for character art that must stay on-model, complex/subtle changes.
- **Tier 2:** `tools/image-edit/backends.py` → `gradio` backend (public InstructPix2Pix Space). True instruction-based editing, free, no key, no download. Default for pipeline/crew use.

### `image-generate` — text-to-image generation
- **Tier 1:** Assistant's media pipeline (`media.generate_image`). Highest quality, detailed, on-prompt.
- **Tier 2:** Pollinations API (free, no key, FLUX-based). Good for drafts and bulk work.

### `image-edit-basic` — resize, crop, rotate, recolor, text, convert
- **Tier 2 only:** `tools/image-edit/edit.py` (PIL, fully offline). Pixel-precise. No reason to spend tokens on basic ops.

### `tts-voice` — text-to-speech / character voice lines
- **Tier 1:** Assistant's TTS (`/opt/hatch/bin/tts`). Production voices, multiple languages. Good for previews and drafts.
- **Tier 2:** Repo voice pipeline (`tools/character-voice/`, Chatterbox default) on remote GPU. Best for production character voices — zero-shot cloning, per-fighter tuning. Runs on Kaggle/remote, never clutters local disk.

### `video-generate` — video from prompt or image animation
- **Tier 1 only:** Assistant's media pipeline (`media.generate_video`).

## Usage

```python
from tools.assistant.router import route, describe, Tier

# Standard quality — tries free first
tier = route("image-edit-generative")  # -> "tier2"

# High quality — goes to token-based
tier = route("image-edit-generative", quality="high")  # -> "tier1"

# Force a specific tier
tier = route("image-edit-generative", force_tier=Tier.TIER1)

# See what's available for a tool
info = describe("image-edit-generative")
```

## Cost Transparency

Every tool documents its tier, method, quality level, and when to use which.
The user should always know whether something is free or uses tokens.
When in doubt, ask — don't silently burn token budget on bulk work.

## Wiring

- **In conversation:** The assistant calls Tier 1 via its built-in capabilities
  (media pipeline, TTS) and Tier 2 via the repo CLIs.
- **In the creation suite:** `tools/image-edit/server.py` exposes the Tier 2
  generative backends via HTTP API (`/api/ai-edit`). The suite's ART panel
  uses this. Tier 1 (assistant pipeline) is available in conversation only.
- **In the pipeline/crew:** Always Tier 2. Crew work never touches token budget
  without explicit user approval.

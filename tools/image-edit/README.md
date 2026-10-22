# image-edit — Western Heart image editing tool

Programmatic image editing for the crew + a web UI for the creation suite.
Two layers:

1. **PIL basics** (`edit.py`) — resize, crop, rotate, flip, color adjustments,
   tint, overlay, text, format conversion, batch. Works offline, no credentials.
2. **Generative** (`--instruction` + `backends.py`) — natural-language edits
   ("make the shell red and white like a Mario Koopa shell") routed to a
   pluggable backend. See [Generative backends](#generative-backends).

Part of the creation suite's ART section (TOOL-TO-MENU WIRING LAW).
MIT licensed.

## Install

```bash
pip install -r requirements.txt   # Pillow + Flask
# Optional, per backend:
pip install huggingface_hub   # hf backend
pip install torch diffusers   # local backend (needs CUDA GPU)
```

## Basic operations

```bash
# Resize
python edit.py in.png --resize 800x600 -o out.png

# Crop (x,y,width,height) + rotate + flip
python edit.py in.png --crop 100,100,400,400 --rotate 90 --flip horizontal -o out.png

# Color: brightness / contrast / saturation / sharpness (1.0 = unchanged)
python edit.py in.png --brightness 1.2 --contrast 1.1 --saturation 1.4 -o out.png

# Hue shift (degrees) and tint
python edit.py in.png --hue 180 -o out.png
python edit.py in.png --tint "#ff8800" --tint-strength 0.25 -o out.png

# Grayscale, blur
python edit.py in.png --grayscale -o out.png
python edit.py in.png --blur 2.5 -o out.png

# Overlay another image (watermark / logo)
python edit.py in.png --overlay logo.png --overlay-pos bottom-right \
    --overlay-opacity 0.6 --overlay-scale 200x200 -o out.png

# Text (positions: top-left|top-center|top-right|center|bottom-left|bottom-center|bottom-right|x,y)
python edit.py in.png --text "DOROWANI" --text-pos top-center \
    --text-size 64 --text-color "#ffffff" -o out.png

# Format conversion
python edit.py in.png --convert webp -o out.webp
python edit.py in.png --convert jpg --quality 85 -o out.jpg

# Batch: every image in a directory
python edit.py in_dir/ --batch --resize 512x512 --convert jpg -o out_dir/
python edit.py in_dir/ --batch --saturation 1.3 --tint "#ff8800" -o out_dir/
```

Ops chain in order: resize → crop → rotate → flip → grayscale →
brightness → contrast → saturation → sharpness → hue → tint → blur →
overlay → text. Generative (`--instruction`) runs first, on the source image.

## Generative backends

`--instruction "describe the edit" --backend <name>`

| Backend | What it does | Needs | Surgical? |
|---------|--------------|-------|-----------|
| `pollinations` | Text-guided generation via pollinations.ai | Nothing (free, rate-limited) | No — generates a variation guided by the instruction, doesn't preserve pixels |
| `hf` | Qwen-Image-Edit / FLUX Kontext via HuggingFace Inference | `HF_TOKEN` env var | **Yes** — true instruction-based editing |
| `local` | InstructPix2Pix via diffusers | CUDA GPU (~4GB VRAM), `torch` + `diffusers` | **Yes** — fully offline |
| `auto` (default) | Tries backends in order, uses the first that works | — | Depends on what succeeds |

```bash
# Free tier: guided generation (concept drafts, variations)
python edit.py in.png --instruction "make the shell red and white like a Mario Koopa shell" \
    --backend pollinations -o out.png

# True surgical editing (needs free HF token from huggingface.co/settings/tokens)
export HF_TOKEN=hf_...
python edit.py in.png --instruction "change the turtle shell to red and white, keep everything else identical" \
    --backend hf -o out.png

# Fully offline on a GPU machine
python edit.py in.png --instruction "make it cyberpunk" --backend local -o out.png

# Combine: generative edit, then PIL polish
python edit.py in.png --instruction "sunset lighting" --backend hf \
    --saturation 1.2 --text "v2" --text-pos bottom-right -o out.png
```

**In-conversation:** when the assistant edits images in chat, it uses Muse's
media pipeline directly — that path is separate from this CLI. This tool is
for the pipeline, batch jobs, and the suite's web UI.

## Web UI (creation suite)

`server.py` exposes the tool as an HTTP API for the suite's ART panel:

```bash
python server.py --port 8791
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Status + backend availability |
| `/api/backends` | GET | List generative backends |
| `/api/ai-edit` | POST | `image` file + `instruction` + `backend`/`size`/`seed` → PNG |
| `/api/basic-edit` | POST | `image` file + `ops` JSON → PNG |

The suite embeds it at **Create Fighter → ART → AI EDIT**.
Manual (non-AI) editing in the suite uses the vendored
[TOAST UI Image Editor](https://github.com/nhn/tui.image-editor) (MIT)
under **ART → STUDIO**.

## Testing

Basic ops are exercised against real images:

```bash
python edit.py <image> --resize 400x400 --saturation 1.3 \
    --tint "#ff8800" --tint-strength 0.15 \
    --text "TEST" --text-pos top-center --text-size 32 -o /tmp/t.png
python edit.py <image> --crop 100,100,300,300 --rotate 45 --flip horizontal -o /tmp/t2.png
python edit.py <image> --hue 120 --grayscale -o /tmp/t3.png
```

Generative backends: `pollinations` verified returning valid images
(no key). `hf`/`local` are code-complete; they activate when their
requirements are met (`HF_TOKEN` / CUDA GPU).

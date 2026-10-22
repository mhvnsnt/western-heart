#!/usr/bin/env python3
"""
backends.py — generative image-editing backends for tools/image-edit.

Each backend takes a PIL image + a natural-language instruction and returns
an edited PIL image. Backends are tried in order for --backend auto.

    gradio        FREE, no API key, no local weights. True instruction-based
                  surgical editing via the public InstructPix2Pix Gradio Space
                  (timbrooks/instruct-pix2pix on HuggingFace). This is the
                  DEFAULT — it just works.
    pollinations  Free, no API key. Text-guided GENERATION (not surgical
                  img2img): describes the edit as a fresh render. Good for
                  concept drafts and variations. Rate-limited per IP.
    hf            HuggingFace Inference Providers (Qwen-Image-Edit / FLUX
                  Kontext). True instruction-based surgical editing.
                  Needs HF_TOKEN env var (free tier available at
                  https://huggingface.co/settings/tokens).
    local         InstructPix2Pix via diffusers on a local GPU.
                  Needs torch + diffusers + ~4GB VRAM. Nothing leaves the machine.

In-conversation editing (the path the assistant uses day-to-day) goes through
Muse's media pipeline, which is a separate capability, not a CLI backend.
"""
import io
import os
import tempfile
import urllib.parse
import urllib.request

from PIL import Image


def _clean_proxy_env():
    """Work around httpx choking on IPv6 entries in no_proxy.

    The sandbox sets no_proxy with bracketed IPv6 addresses ([::1], etc.)
    which httpx fails to parse ('Invalid port'). We simplify it for our
    subprocess calls. Safe: only affects the current process.
    """
    os.environ["no_proxy"] = "localhost,127.0.0.1"
    os.environ["NO_PROXY"] = "localhost,127.0.0.1"


# ---------------------------------------------------------------------------
# Backend: gradio (FREE, no key, no local weights) — DEFAULT
# Uses the public InstructPix2Pix HuggingFace Space for true
# instruction-based image editing. No token, no download, no GPU needed.
# ---------------------------------------------------------------------------

GRADIO_SPACE = "timbrooks/instruct-pix2pix"
GRADIO_ENDPOINT = "/generate"


def gradio_available():
    try:
        import gradio_client  # noqa: F401
        return True
    except ImportError:
        return False


def gradio_edit(img, instruction, size=512, seed=None):
    """True instruction-based editing via public InstructPix2Pix Gradio Space.

    Free, no API key, no local model download. The image is sent to the
    public HuggingFace Space, edited, and returned. Rate-limited by the
    Space's queue (usually a few seconds).
    """
    _clean_proxy_env()
    try:
        from gradio_client import Client, handle_file
    except ImportError:
        raise RuntimeError(
            "gradio backend needs gradio_client: pip install gradio_client"
        )

    # Prepare input (InstructPix2Pix works best at 512px)
    work = img.convert("RGB")
    work.thumbnail((size, size))

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        work.save(tmp_path, format="PNG")

        client = Client(GRADIO_SPACE)
        job = client.submit(
            input_image=handle_file(tmp_path),
            instruction=instruction,
            steps=50,
            randomize_seed="Fix Seed",
            seed=seed if seed is not None else 42,
            randomize_cfg="Fix CFG",
            text_cfg_scale=7.5,
            image_cfg_scale=1.5,
            api_name=GRADIO_ENDPOINT,
        )
        result = job.result(timeout=300)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    # Result is a tuple: (seed, text_cfg, image_cfg, output_path)
    out_path = None
    if isinstance(result, (list, tuple)):
        for item in result:
            if isinstance(item, str) and os.path.exists(item):
                out_path = item
                break
    elif isinstance(result, str) and os.path.exists(result):
        out_path = result

    if not out_path:
        raise RuntimeError(f"gradio backend: unexpected result format: {str(result)[:200]}")

    out = Image.open(out_path).convert("RGB")
    out.info["backend"] = "gradio"
    out.info["space"] = GRADIO_SPACE
    out.info["instruction"] = instruction
    return out


# ---------------------------------------------------------------------------
# Backend: pollinations (free, no key) — text-guided generation
# ---------------------------------------------------------------------------

def pollinations_available():
    return True  # no credentials needed; fails gracefully on network/rate limit


def pollinations_edit(img, instruction, size=512, seed=None):
    """Generate a variation guided by the instruction.

    NOTE: this is text-to-image generation, not surgical img2img. The output
    is guided by a caption of the source image + the instruction. Best for
    concept drafts, not for pixel-precise edits.
    """
    prompt = (
        f"Digital artwork variation. {instruction}. "
        f"High quality, clean composition."
    )
    params = {
        "width": size,
        "height": size,
        "model": "flux",
        "nologo": "true",
    }
    if seed is not None:
        params["seed"] = seed
    query = urllib.parse.urlencode(params)
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = r.read()
    except Exception as e:
        raise RuntimeError(f"pollinations backend failed: {e}")
    out = Image.open(io.BytesIO(data)).convert("RGB")
    # Tag the output so downstream knows its provenance
    out.info["backend"] = "pollinations"
    out.info["instruction"] = instruction
    return out


# ---------------------------------------------------------------------------
# Backend: HuggingFace Inference Providers (needs HF_TOKEN)
# ---------------------------------------------------------------------------

def hf_available():
    return bool(os.environ.get("HF_TOKEN"))


def hf_edit(img, instruction, size=512, seed=None):
    """True instruction-based editing via Qwen-Image-Edit / FLUX Kontext.

    Requires HF_TOKEN env var. Uses huggingface_hub's InferenceClient with
    automatic provider routing.
    """
    try:
        from huggingface_hub import InferenceClient
    except ImportError:
        raise RuntimeError("hf backend needs huggingface_hub: pip install huggingface_hub")

    token = os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError("hf backend needs HF_TOKEN env var (https://huggingface.co/settings/tokens)")

    work = img.convert("RGB")
    work.thumbnail((size, size))
    buf = io.BytesIO()
    work.save(buf, format="PNG")
    payload = buf.getvalue()

    last_err = None
    for model_id in ("Qwen/Qwen-Image-Edit-2511", "black-forest-labs/FLUX.1-Kontext-dev"):
        try:
            client = InferenceClient(model=model_id, token=token)
            result = client.image_to_image(payload, prompt=instruction)
            out = result.convert("RGB")
            out.info["backend"] = "hf"
            out.info["model"] = model_id
            out.info["instruction"] = instruction
            return out
        except Exception as e:
            last_err = e
    raise RuntimeError(f"hf backend failed on all models: {last_err}")


# ---------------------------------------------------------------------------
# Backend: local diffusers (needs GPU)
# ---------------------------------------------------------------------------

def local_available():
    try:
        import torch  # noqa: F401
        import diffusers  # noqa: F401
        return True
    except ImportError:
        return False


def local_edit(img, instruction, size=512, seed=None):
    """InstructPix2Pix locally via diffusers. Needs CUDA GPU (~4GB VRAM)."""
    try:
        import torch
        from diffusers import StableDiffusionInstructPix2PixPipeline
    except ImportError:
        raise RuntimeError("local backend needs torch + diffusers: pip install torch diffusers")

    if not torch.cuda.is_available():
        raise RuntimeError("local backend needs a CUDA GPU (none detected)")

    model_id = "timbrooks/instruct-pix2pix"
    pipe = StableDiffusionInstructPix2PixPipeline.from_pretrained(
        model_id, torch_dtype=torch.float16, safety_checker=None,
    ).to("cuda")
    pipe.enable_model_cpu_offload()

    work = img.convert("RGB")
    work.thumbnail((size, size))
    # InstructPix2Pix wants even dimensions
    w, h = work.size
    work = work.resize((w - w % 8, h - h % 8))

    generator = torch.Generator("cuda").manual_seed(seed) if seed is not None else None
    out = pipe(
        instruction,
        image=work,
        num_inference_steps=50,
        image_guidance_scale=1.5,
        guidance_scale=7.5,
        generator=generator,
    ).images[0]
    out.info["backend"] = "local"
    out.info["model"] = model_id
    out.info["instruction"] = instruction
    return out


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

BACKENDS = {
    "gradio": (gradio_available, gradio_edit,
               "FREE, no key, no download — true instruction editing via public InstructPix2Pix Space (DEFAULT)"),
    "pollinations": (pollinations_available, pollinations_edit,
                     "free, no key — text-guided generation (not surgical)"),
    "hf": (hf_available, hf_edit,
           "needs HF_TOKEN — true instruction-based editing (Qwen/FLUX Kontext)"),
    "local": (local_available, local_edit,
              "needs GPU + torch/diffusers — InstructPix2Pix, fully offline"),
}


def list_backends():
    rows = []
    for name, (avail_fn, _, desc) in BACKENDS.items():
        try:
            ok = avail_fn()
        except Exception:
            ok = False
        rows.append((name, ok, desc))
    return rows


def run_instruction(img, instruction, backend="auto", size=512, seed=None):
    """Run a natural-language edit. Returns a PIL image."""
    order = list(BACKENDS) if backend == "auto" else [backend]
    if backend != "auto" and backend not in BACKENDS:
        raise ValueError(f"unknown backend: {backend} (choose from {list(BACKENDS)})")

    last_err = None
    for name in order:
        avail_fn, run_fn, _ = BACKENDS[name]
        try:
            if not avail_fn():
                last_err = RuntimeError(f"backend '{name}' not available here")
                continue
        except Exception as e:
            last_err = e
            continue
        try:
            return run_fn(img, instruction, size=size, seed=seed)
        except Exception as e:
            last_err = e
            if backend != "auto":
                raise
    raise RuntimeError(
        f"no generative backend worked (tried: {order}). Last error: {last_err}\n"
        "Options: pip install gradio_client for the free 'gradio' backend,\n"
        "set HF_TOKEN for the 'hf' backend, or run on a GPU machine for 'local'.\n"
        "In-conversation, the assistant edits via Muse's media pipeline instead."
    )

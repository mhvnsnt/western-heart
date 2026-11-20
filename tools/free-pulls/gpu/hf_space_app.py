"""
Western Heart — Hugging Face Space sketch (DEMO ONLY, not a batch pipeline).

Status: ZeroGPU genuinely exists as a free tier for Gradio Spaces, so this
sketch is provided — but read the limits before expecting it to do real work:

  * Free-account daily quota (HF docs, current): 3.5 min/day for a signed-in
    free account, 2 min/day unauthenticated, 25 min/day PRO. Some secondary
    write-ups still quote the older 5 min/day figure — treat the docs number
    as current and check https://huggingface.co/docs/hub/spaces-zerogpu
    at deploy time. Quota resets 24 h after first GPU use.
  * Quota is charged on the DECLARED duration, not actual runtime: the
    default @spaces.GPU call reserves 60 s, even if the function finishes in
    2 s, and failed calls can consume the reservation too. A free account
    therefore gets roughly 3 default calls a day — not a batch queue.
  * Gradio Spaces ONLY. Docker/Streamlit Spaces cannot use ZeroGPU.
  * Free personal accounts: max 2 ZeroGPU Spaces (verified email, account
    >30 days, good standing, per HF docs summaries).
  * No torch.compile on ZeroGPU. GPU is allocated per @spaces.GPU call and
    released on return — there is no persistent GPU worker.
  * Over-quota use is billed ($1 per 10 min, from prepaid credits, per HF
    docs). Do NOT enable credits if the goal is strictly free.

Conclusion for WH: this Space is a tiny interactive DEMO (upload one texture,
get a resized copy back, plus one trivial torch GPU op proving the device).
It is NOT a replacement for Kaggle/Colab batch jobs. Do not route stage
production through it.

HOW TO DEPLOY (needs an HF account — this file alone does nothing):
  1. Create a Space (Gradio SDK) and add this file as app.py.
  2. In the Space settings, choose hardware: ZeroGPU (not CPU, not a paid GPU).
  3. requirements.txt: gradio, pillow, torch, spaces
     (the `spaces` package provides @spaces.GPU; on a plain local run the
     import below falls back to a no-op decorator so the demo still works.)

Local test (no GPU, no gradio install needed for the pure function):
  python3 -c "import hf_space_app; print(hf_space_app.resize_texture_bytes(open('x.jpg','rb').read()))"
  — the Gradio UI is only built under __main__, so importing is safe.
"""
import io

try:
    import spaces  # HF ZeroGPU decorator; only present in a Space
    GPU = spaces.GPU
except Exception:  # noqa: BLE001 - local runs without the spaces package
    def GPU(*dargs, **dkwargs):
        def wrap(fn):
            return fn
        # Support both @GPU and @GPU(duration=...) forms.
        if dargs and callable(dargs[0]):
            return dargs[0]
        return wrap


def resize_texture_bytes(data: bytes, max_edge: int = 1024) -> bytes:
    """Pure-PIL resize to JPEG. CPU work — the GPU part is gpu_probe() below."""
    from PIL import Image

    with Image.open(io.BytesIO(data)) as im:
        im = im.convert("RGB")
        w, h = im.size
        scale = min(1.0, max_edge / max(w, h))
        out = im.resize((max(1, int(w * scale)), max(1, int(h * scale))),
                        Image.LANCZOS)
        buf = io.BytesIO()
        out.save(buf, "JPEG", quality=85)
        return buf.getvalue()


@GPU(duration=30)  # Short declared duration: better queue priority, less quota.
def gpu_probe():
    """One trivial torch op on the ZeroGPU device. Proves GPU, does no WH work."""
    try:
        import torch
    except ImportError:
        return "torch not installed here — GPU probe skipped (install torch in the Space)."

    if not torch.cuda.is_available():
        return "No CUDA device in this Space (ZeroGPU not attached?)"
    x = torch.arange(1024, dtype=torch.float32, device="cuda")
    return (f"ZeroGPU OK: {torch.cuda.get_device_name(0)} | "
            f"sum(arange(1024)*2) = {float((x * 2).sum().item())} "
            f"(expect 1047552.0)")


def demo_resize(file_bytes: bytes):
    """Returns (PIL image, message). Each click also runs gpu_probe(),
    which consumes one declared 30 s ZeroGPU reservation — that cost is
    the reason this demo must stay a demo, not a pipeline."""
    if not file_bytes:
        return None, "Upload a JPG/PNG texture first."
    try:
        out_bytes = resize_texture_bytes(file_bytes)
        from PIL import Image

        out_img = Image.open(io.BytesIO(out_bytes))
        out_img.load()
    except Exception as exc:  # noqa: BLE001 - surface as UI message
        return None, f"Could not read that image: {exc}"
    return out_img, f"Resized to <=1024 px JPEG ({len(out_bytes)} bytes). " + gpu_probe()


if __name__ == "__main__":
    import gradio as gr

    with gr.Blocks(title="Western Heart — texture demo (ZeroGPU)") as demo:
        gr.Markdown(
            "# Western Heart texture demo (ZeroGPU, demo only)\n"
            "Upload ONE texture, get a <=1024 px JPEG back. Free ZeroGPU quota "
            "is minutes per day and charged on declared duration — this is a "
            "demo, not a batch pipeline. See the header of app.py for limits."
        )
        inp = gr.File(label="Texture (JPG/PNG)", file_types=["image"], type="binary")
        btn = gr.Button("Resize")
        out_img = gr.Image(label="Resized image")
        out_msg = gr.Textbox(label="Result")
        btn.click(demo_resize, inputs=inp, outputs=[out_img, out_msg])
    demo.launch()

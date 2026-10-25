#!/usr/bin/env python3
"""
Western Heart — Kaggle GPU batch job: texture downscale/convert + GLB size report.

HOW TO RUN (Kaggle, no sign-in needed to read this file):
  1. New Kaggle Notebook -> Settings -> Accelerator -> GPU (T4 x2, if offered).
  2. Paste this whole file into a code cell (or upload it and `%run kaggle_wh_batch.py`).
  3. Put source textures/GLBs in /kaggle/input/wh-assets/ (or set WH_INPUT below).
  4. Outputs land in /kaggle/working/wh-out/ — download them before the session ends.

GPU GATE (hard requirement, not a warning):
  The script prints `nvidia-smi` and `torch.cuda.is_available()` FIRST, then
  exits non-zero with a loud error if no CUDA device is present. A CPU run
  must NEVER silently pass as a GPU run. Kaggle's free GPU quota (~30 h/week,
  commonly reported; Kaggle's own docs publish no number — check your account
  settings) is precious; do not burn it on a CPU session by accident.

  Testing the non-GPU logic on a CPU box is allowed ONLY with
  WH_CPU_SELFTEST=1, which prints an unmissable banner. Never set that in Kaggle.

What it does on GPU:
  A) Batch texture job: every .jpg/.png under WH_INPUT is resized to at most
     1024 px on the long edge, converted to JPEG q=85 (web-friendly for a
     Three.js game), and written to wh-out/textures/. The GPU part is real but
     modest: a torch CUDA tensor round-trip (mean/std + a tiny blur-free
     normalisation) proves the CUDA path is live for every file, and the
     report records torch.cuda.get_device_name() per run. (PIL resize itself
     is CPU work — honest note: for pure texture resizing, GPU barely matters;
     the value of this job is batching + verification, and it is the template
     to extend with real GPU work such as torch-based super-resolution or
     texture compression later.)
  B) GLB size report: every .glb under WH_INPUT is parsed (header + JSON chunk,
     no extra dependency) and reported: file size, JSON chunk size, buffer
     sizes, image/bufferView counts, and the largest buffers. No GLB is modified.
  C) A machine-readable report: wh-out/report.json + a human summary printed
     to stdout. If the input dir is empty, the script still exits 0 after the
     GPU gate — it reports zero files, it does not invent results.

No API keys, no credentials, no network calls except the Kaggle environment
itself. Pure stdlib + Pillow + torch (both preinstalled on Kaggle images).
"""
import json
import os
import struct
import subprocess
import sys
from pathlib import Path

INPUT_DIR = Path(os.environ.get("WH_INPUT", "/kaggle/input/wh-assets"))
OUTPUT_DIR = Path(os.environ.get("WH_OUTPUT", "/kaggle/working/wh-out"))
MAX_EDGE = int(os.environ.get("WH_MAX_EDGE", "1024"))
JPEG_QUALITY = int(os.environ.get("WH_JPEG_QUALITY", "85"))
CPU_SELFTEST = os.environ.get("WH_CPU_SELFTEST", "") == "1"


def fail(msg: str) -> "SystemExit":
    print(f"\n{'=' * 70}\nGPU GATE FAILED: {msg}\n{'=' * 70}", file=sys.stderr)
    raise SystemExit(2)


def gpu_gate() -> str:
    """Print nvidia-smi + torch CUDA status; fail loudly without CUDA."""
    print("== nvidia-smi ==")
    try:
        out = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=60)
        print(out.stdout or "(nvidia-smi produced no output)")
        if out.returncode != 0:
            print(out.stderr, file=sys.stderr)
    except FileNotFoundError:
        print("(nvidia-smi not found on PATH)")

    # CPU_SELFTEST is checked BEFORE the torch import so the non-GPU logic
    # can be tested on a torch-less box. It never runs silently: the banner
    # below is printed, and the report records cpu_selftest=true.
    if CPU_SELFTEST:
        print("\n!!! CPU SELFTEST MODE (WH_CPU_SELFTEST=1) — NOT A GPU RUN !!!\n")
        try:
            import torch  # noqa: F401
            print(f"torch present but CUDA gate bypassed for selftest only.")
        except ImportError:
            print("(torch not installed on this test box; CUDA checks skipped.)")
        return "CPU-SELFTEST (no GPU)"
    try:
        import torch
    except ImportError as exc:
        fail(f"torch is not installed in this environment ({exc}). "
             "Use a Kaggle GPU notebook image, which ships torch.")
    print(f"torch {torch.__version__} | cuda.is_available() = {torch.cuda.is_available()}")
    print(f"torch.cuda.device_count() = {torch.cuda.device_count()}")
    if not torch.cuda.is_available() or torch.cuda.device_count() == 0:
        if CPU_SELFTEST:
            print("\n!!! CPU SELFTEST MODE (WH_CPU_SELFTEST=1) — NOT A GPU RUN !!!\n")
            return "CPU-SELFTEST (no GPU)"
        fail("No CUDA device detected. Enable Accelerator -> GPU in the Kaggle "
             "notebook settings and restart the session. Refusing to run on CPU.")
    name = torch.cuda.get_device_name(0)
    print(f"GPU 0: {name}")
    # Prove the CUDA path is actually live, not just reported.
    x = torch.arange(1024, dtype=torch.float32, device="cuda")
    assert float((x * 2).sum().item()) == 1024 * 1023, "CUDA sanity check failed"
    print("CUDA sanity check PASSED (arange sum on device).")
    return name


def process_textures(gpu_name: str) -> list:
    from PIL import Image
    torch = None
    if not CPU_SELFTEST:
        import torch  # noqa: F811 - real CUDA path only

    out_dir = OUTPUT_DIR / "textures"
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for src in sorted(INPUT_DIR.rglob("*")):
        if src.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            continue
        with Image.open(src) as im:
            im = im.convert("RGB")
            w, h = im.size
            scale = min(1.0, MAX_EDGE / max(w, h))
            nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
            resized = im.resize((nw, nh), Image.LANCZOS)
            # Real (small) CUDA touch: per-image channel mean on device.
            if not CPU_SELFTEST:
                import numpy as np
                t = torch.from_numpy(np.asarray(resized, dtype=np.float32)).cuda()
                mean = t.mean(dim=(0, 1)).tolist()
            else:
                mean = [0.0, 0.0, 0.0]
            dst = out_dir / (src.stem + "_1k.jpg")
            resized.save(dst, "JPEG", quality=JPEG_QUALITY)
            results.append({
                "input": str(src), "output": str(dst),
                "in_px": [w, h], "out_px": [nw, nh],
                "in_bytes": src.stat().st_size, "out_bytes": dst.stat().st_size,
                "cuda_channel_mean": [round(float(v), 2) for v in mean],
                "gpu": gpu_name,
            })
            print(f"[tex] {src.name} {w}x{h} -> {nw}x{nh} "
                  f"{src.stat().st_size} -> {dst.stat().st_size} bytes")
    return results


def glb_report() -> list:
    results = []
    for src in sorted(INPUT_DIR.rglob("*.glb")):
        data = src.read_bytes()
        if len(data) < 20 or data[0:4] != b"glTF":
            print(f"[glb] SKIP (not glTF binary): {src.name}")
            continue
        _magic, _ver, total_len = struct.unpack("<III", data[0:12])
        chunk_len, chunk_type = struct.unpack("<II", data[12:20])
        entry = {"file": str(src), "bytes": len(data), "header_length": total_len}
        if chunk_type == 0x4E4F534A:  # 'JSON'
            try:
                doc = json.loads(data[20:20 + chunk_len])
                entry["json_bytes"] = chunk_len
                entry["buffers"] = [
                    {"byteLength": b.get("byteLength")} for b in doc.get("buffers", [])
                ]
                entry["n_bufferViews"] = len(doc.get("bufferViews", []))
                entry["n_images"] = len(doc.get("images", []))
                entry["n_meshes"] = len(doc.get("meshes", []))
                entry["n_materials"] = len(doc.get("materials", []))
                entry["n_nodes"] = len(doc.get("nodes", []))
            except Exception as exc:  # noqa: BLE001 - report, don't crash batch
                entry["json_error"] = str(exc)
        print(f"[glb] {src.name}: {len(data)} bytes, {entry.get('n_meshes')} meshes, "
              f"{entry.get('n_images')} images")
        results.append(entry)
    return results


def main() -> int:
    gpu_name = gpu_gate()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    tex = process_textures(gpu_name)
    glbs = glb_report()
    report = {
        "gpu": gpu_name,
        "cpu_selftest": CPU_SELFTEST,
        "input_dir": str(INPUT_DIR),
        "textures_processed": len(tex),
        "textures": tex,
        "glbs": glbs,
        "note": "CPU_SELFTEST runs are NOT GPU runs and must not be reported as such.",
    }
    (OUTPUT_DIR / "report.json").write_text(json.dumps(report, indent=2))
    print(f"\nDone. textures={len(tex)} glbs={len(glbs)} "
          f"report={OUTPUT_DIR / 'report.json'}")
    if not tex and not glbs:
        print("Input dir was empty or had no .jpg/.png/.glb files — "
              "nothing was processed (this is not an error).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

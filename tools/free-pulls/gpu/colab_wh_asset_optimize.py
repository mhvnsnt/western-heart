#!/usr/bin/env python3
"""
Western Heart — Google Colab (free tier) backup/overflow asset-optimize job.

USE WHEN: Kaggle's weekly GPU quota is exhausted. This is the overflow lane,
not the primary lane: Colab free gives NO published quota, NO guaranteed GPU
model, and NO guaranteed session length (Google's own FAQ: usage limits "can
vary over time" and "are not published"; free notebooks run "at most 12 hours").
Community reports commonly cite a T4, ~90 minutes idle timeout, and a ~12 h
session ceiling — all UNVERIFIED against Google's docs and marked as such in
catalog-gpu-assets.md. Plan jobs that finish in well under an hour and save
outputs early and often (Drive mount, or download the output zip).

HOW TO RUN (Colab):
  1. Runtime -> Change runtime type -> Hardware accelerator -> GPU -> Save.
  2. Paste this file into a cell, or upload it and run:  %run colab_wh_asset_optimize.py
  3. Upload assets to /content/wh-in/ (Files pane) or set WH_INPUT.
  4. Outputs: /content/wh-out/ (+ wh-out.zip for one-click download).

GPU GATE: same rule as the Kaggle job — prints nvidia-smi + torch CUDA
status first and exits non-zero without CUDA, unless WH_CPU_SELFTEST=1
(which prints an unmissable banner and must never be used to claim a GPU run).

JOB: batch asset optimize for a Three.js game —
  * images (.jpg/.png): resize to <=1024 px long edge, save as WebP q=85
    (smaller than JPEG for the web build) AND keep a JPEG fallback copy.
  * .glb files: size report only (header + JSON chunk, no dependency),
    plus a duplicate-size warning if a GLB is over WH_GLB_WARN_MB (default 25 MB),
    which is the point where it needs decimation/compression before shipping.
  * report.json with before/after bytes per file and totals.

No keys, no credentials. Stdlib + Pillow + torch (Colab preinstalls both;
torch is used only for the CUDA gate + a tiny per-file device check).
"""
import json
import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path

INPUT_DIR = Path(os.environ.get("WH_INPUT", "/content/wh-in"))
OUTPUT_DIR = Path(os.environ.get("WH_OUTPUT", "/content/wh-out"))
MAX_EDGE = int(os.environ.get("WH_MAX_EDGE", "1024"))
QUALITY = int(os.environ.get("WH_QUALITY", "85"))
GLB_WARN_MB = float(os.environ.get("WH_GLB_WARN_MB", "25"))
CPU_SELFTEST = os.environ.get("WH_CPU_SELFTEST", "") == "1"


def fail(msg: str):
    print(f"\n{'=' * 70}\nGPU GATE FAILED: {msg}\n{'=' * 70}", file=sys.stderr)
    raise SystemExit(2)


def gpu_gate() -> str:
    print("== nvidia-smi ==")
    try:
        out = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=60)
        print(out.stdout or "(nvidia-smi produced no output)")
    except FileNotFoundError:
        print("(nvidia-smi not found on PATH)")
    if CPU_SELFTEST:
        print("\n!!! CPU SELFTEST MODE (WH_CPU_SELFTEST=1) — NOT A GPU RUN !!!\n")
        try:
            import torch  # noqa: F401
            print("torch present but CUDA gate bypassed for selftest only.")
        except ImportError:
            print("(torch not installed on this test box; CUDA checks skipped.)")
        return "CPU-SELFTEST (no GPU)"
    try:
        import torch
    except ImportError as exc:
        fail(f"torch is not installed ({exc}). Use a standard Colab GPU runtime.")
    print(f"torch {torch.__version__} | cuda.is_available() = {torch.cuda.is_available()}")
    if not torch.cuda.is_available() or torch.cuda.device_count() == 0:
        if CPU_SELFTEST:
            print("\n!!! CPU SELFTEST MODE (WH_CPU_SELFTEST=1) — NOT A GPU RUN !!!\n")
            return "CPU-SELFTEST (no GPU)"
        fail("No CUDA device. Set Runtime -> Change runtime type -> GPU, "
             "restart the runtime, and retry. Refusing to run on CPU.")
    name = torch.cuda.get_device_name(0)
    print(f"GPU 0: {name}")
    x = torch.arange(256, dtype=torch.float32, device="cuda")
    assert float((x * 2).sum().item()) == 256 * 255, "CUDA sanity check failed"
    print("CUDA sanity check PASSED.")
    return name


def optimize_images() -> list:
    from PIL import Image

    out_dir = OUTPUT_DIR / "optimized"
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
            webp = out_dir / (src.stem + ".webp")
            jpg = out_dir / (src.stem + ".jpg")
            resized.save(webp, "WEBP", quality=QUALITY)
            resized.save(jpg, "JPEG", quality=QUALITY)
            row = {"input": str(src), "in_px": [w, h], "out_px": [nw, nh],
                   "in_bytes": src.stat().st_size,
                   "webp_bytes": webp.stat().st_size, "jpg_bytes": jpg.stat().st_size}
            print(f"[img] {src.name} {w}x{h} -> {nw}x{nh} "
                  f"{row['in_bytes']} -> webp {row['webp_bytes']} / jpg {row['jpg_bytes']}")
            results.append(row)
    return results


def glb_report() -> list:
    results = []
    for src in sorted(INPUT_DIR.rglob("*.glb")):
        data = src.read_bytes()
        row = {"file": str(src), "bytes": len(data),
               "over_warn_mb": len(data) > GLB_WARN_MB * 1_000_000}
        if len(data) >= 20 and data[0:4] == b"glTF":
            chunk_len, chunk_type = struct.unpack("<II", data[12:20])
            if chunk_type == 0x4E4F534A:
                try:
                    doc = json.loads(data[20:20 + chunk_len])
                    row.update({"n_meshes": len(doc.get("meshes", [])),
                                "n_images": len(doc.get("images", [])),
                                "n_materials": len(doc.get("materials", [])),
                                "buffers_bytes": [b.get("byteLength")
                                                  for b in doc.get("buffers", [])]})
                except Exception as exc:  # noqa: BLE001 - report, don't crash
                    row["json_error"] = str(exc)
        if row["over_warn_mb"]:
            print(f"[glb] WARNING over {GLB_WARN_MB} MB, needs compression: {src.name}")
        print(f"[glb] {src.name}: {len(data)} bytes")
        results.append(row)
    return results


def main() -> int:
    gpu_name = gpu_gate()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    imgs = optimize_images()
    glbs = glb_report()
    saved = sum(r["webp_bytes"] for r in imgs)
    orig = sum(r["in_bytes"] for r in imgs)
    report = {"gpu": gpu_name, "cpu_selftest": CPU_SELFTEST,
              "input_dir": str(INPUT_DIR), "images": imgs, "glbs": glbs,
              "totals": {"images_in_bytes": orig, "images_webp_bytes": saved,
                         "glbs": len(glbs)}}
    (OUTPUT_DIR / "report.json").write_text(json.dumps(report, indent=2))
    zip_path = shutil.make_archive(str(OUTPUT_DIR), "zip", root_dir=str(OUTPUT_DIR))
    print(f"\nDone. images={len(imgs)} glbs={len(glbs)} "
          f"webp total={saved} (in {orig}) zip={zip_path}")
    print("Colab free reminder: download the zip NOW — the VM disk is wiped "
          "when the session ends.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

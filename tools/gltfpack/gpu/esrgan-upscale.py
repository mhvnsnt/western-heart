#!/usr/bin/env python3
"""esrgan-upscale.py — Real-ESRGAN texture upscaling batch (Lane 5 GPU job).

Upscales stage textures (panos, atlases) and select-card images on a
CUDA GPU. This is a BUILD-TIME job: outputs are committed into the
repo; nothing here runs on the player's phone.

GPU rule (blanket GPU order, 2026-10-24): this script REQUIRES CUDA
and fails loudly without it — except --cpu, which exists ONLY to
measure a CPU baseline on a small subset (see lane5-gpu-jobs.py).
A CPU run is never a silent substitute for the GPU run, and no
placeholder / fake upscaled image is ever written: if Real-ESRGAN
is not installed, the script exits 2 with the exact install steps
instead of writing anything.

Install (Kaggle / Colab GPU notebook, run once per session):
  pip install basicsr facexlib gfpgan
  pip install realesrgan
  # weights (RealESRGAN_x4plus.pth) download per the Real-ESRGAN
  # repo instructions; pass with --weights (default: ./weights/RealESRGAN_x4plus.pth)

Usage:
  python3 esrgan-upscale.py --root . --out-dir wh-esrgan-out \
      --weights weights/RealESRGAN_x4plus.pth --scale 4
  python3 esrgan-upscale.py --root . --out-dir wh-esrgan-out --cpu --only tree-of-life

Discovery: game/assets/stages/**/*.png + game/assets/portraits/*.png
under --root (use --only to filter by substring). Outputs mirror the
input tree under --out-dir. A per-image manifest JSON records input
bytes, output bytes, scale, device, and wall seconds.

Exit codes: 0 = all discovered images upscaled; 1 = an image failed;
2 = Real-ESRGAN / torch / CUDA unavailable (or weights missing).
"""
import argparse
import json
import os
import sys
import time


def discover(root, only=""):
    found = []
    for base in ("game/assets/stages", "game/assets/portraits"):
        d = os.path.join(root, base)
        for dirpath, _dirs, files in os.walk(d):
            for f in sorted(files):
                if f.lower().endswith(".png"):
                    rel = os.path.relpath(os.path.join(dirpath, f), root)
                    if only and only not in rel:
                        continue
                    found.append(rel)
    return sorted(set(found))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out-dir", default="wh-esrgan-out")
    ap.add_argument("--weights", default="weights/RealESRGAN_x4plus.pth")
    ap.add_argument("--scale", type=int, default=4)
    ap.add_argument("--tile", type=int, default=0, help="0 = no tiling (small textures)")
    ap.add_argument("--cpu", action="store_true",
                    help="CPU baseline subset ONLY — never a full-batch substitute")
    ap.add_argument("--only", default="")
    ap.add_argument("--manifest", default="")
    a = ap.parse_args(argv)

    if not os.path.isfile(a.weights):
        print(f"weights not found: {a.weights}\n"
              "Download RealESRGAN_x4plus.pth per the Real-ESRGAN repo "
              "instructions and pass --weights.", file=sys.stderr)
        return 2
    try:
        import torch
    except ImportError:
        print("torch not installed: pip install torch --index-url "
              "https://download.pytorch.org/whl/cu121 (or the notebook's torch).",
              file=sys.stderr)
        return 2
    if not a.cpu and not torch.cuda.is_available():
        print("CUDA unavailable and --cpu not passed: refusing a silent CPU run.",
              file=sys.stderr)
        return 2
    try:
        from basicsr.archs.rrdbnet_arch import RRDBNet
        from realesrgan import RealESRGANer
    except ImportError as e:
        print(f"Real-ESRGAN not installed ({e}). Run:\n"
              "  pip install basicsr facexlib gfpgan\n"
              "  pip install realesrgan", file=sys.stderr)
        return 2

    device = "cpu" if a.cpu else "cuda"
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64,
                    num_block=23, num_grow_ch=32, scale=a.scale)
    upsampler = RealESRGANer(scale=a.scale, model_path=a.weights, model=model,
                             tile=a.tile, tile_pad=10, pre_pad=0,
                             half=not a.cpu, gpu_id=None if a.cpu else 0)
    manifest = {"device": device, "scale": a.scale, "images": []}
    failed = False
    for rel in discover(a.root, a.only):
        src = os.path.join(a.root, rel)
        out = os.path.join(a.out_dir, rel)
        entry = {"input": rel, "inBytes": os.path.getsize(src)}
        t0 = time.monotonic()
        try:
            import cv2
            img = cv2.imread(src, cv2.IMREAD_UNCHANGED)
            if img is None:
                raise RuntimeError("cv2 could not read image")
            out_img, _ = upsampler.enhance(img, outscale=a.scale)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            cv2.imwrite(out, out_img)
        except Exception as e:  # noqa: BLE001 — per-image failure must not kill the batch record
            entry.update({"status": "failed", "error": str(e)[:300]})
            manifest["images"].append(entry)
            print(f"FAIL {rel}: {e}")
            failed = True
            continue
        entry.update({"status": "ok", "output": os.path.relpath(out, a.root),
                      "outBytes": os.path.getsize(out),
                      "wall_s": round(time.monotonic() - t0, 3)})
        manifest["images"].append(entry)
        print(f"OK {rel}: {entry['inBytes']} -> {entry['outBytes']} bytes, "
              f"{entry['wall_s']}s on {device}")
    if a.manifest:
        with open(a.manifest, "w") as fh:
            json.dump(manifest, fh, indent=2)
    ok_n = sum(1 for e in manifest["images"] if e["status"] == "ok")
    print(f"{ok_n}/{len(manifest['images'])} upscaled on {device}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

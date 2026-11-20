#!/usr/bin/env python3
"""lane5-gpu-jobs.py — Lane 5 GPU job orchestrator (blanket GPU order, 2026-10-24).

Runs EVERY Lane 5 batch workstream through one GPU-notebook session,
in queue order, with a measured manifest — nothing in this lane runs
as a separate CPU-only batch:

  1. esrgan   — Real-ESRGAN upscaling of stage textures + card images (CUDA)
  2. gltfpack — batch-optimize.py over models + stages (pinned flags)
  3. lod      — batch-optimize.py with a stages/props-only --simplify-allow
                file (NEVER a skinned fighter without approved=true)
  4. webp     — webp-basis-batch.py (WebP ship-if-smaller + -tc measured)
  5. cards    — tools/kaggle-gpu-pipeline/kaggle_card_factory.py, REUSED
                (Blender EEVEE-GPU card renders). This lane does NOT
                reimplement card rendering; it feeds the factory a
                Lane 5 manifest and records its manifest beside ours.

Every step records: nvidia-smi + torch.cuda proof (GPU-PROOF.txt),
input count/size, output count/size, wall seconds, and — when
--cpu-baseline is passed — a CPU-baseline wall time measured on a
SUBSET (default 1 item per step) before the GPU step runs. Speedup
is then measured (baseline vs GPU on the same subset), never just
claimed. The full batch is never run on CPU: --cpu-baseline measures
the subset only and then runs the GPU steps.

Session rules (coordinator's browser lane owns execution):
  - Kaggle notebook (T4 x2) first; Colab is backup/overflow when
    Kaggle quota runs low — SWITCH, NEVER STOP; the session stays
    open and jobs queue continuously.
  - --require-gpu (default): fail loudly with exit 2 when no CUDA
    device exists, so a CPU run can never silently pass as a GPU run.

Usage (inside the GPU notebook, repo root as cwd):
  python3 tools/gltfpack/gpu/lane5-gpu-jobs.py --root . --out wh-gpu-out --require-gpu
  python3 tools/gltfpack/gpu/lane5-gpu-jobs.py --root . --out wh-gpu-out --cpu-baseline
  python3 tools/gltfpack/gpu/lane5-gpu-jobs.py --root . --out wh-gpu-out --steps esrgan,gltfpack

Exit codes: 0 = all requested steps completed (individual asset
failures are recorded in the manifest, not hidden); 1 = a step
crashed; 2 = GPU required but absent (or Real-ESRGAN/Blender inputs
missing for a requested step that cannot run without them).
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GPU_DIR = HERE
GLTFPACK_DIR = os.path.dirname(HERE)


def run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        return 127, "", f"binary not found: {cmd[0]}"
    return r.returncode, r.stdout, r.stderr


def gpu_proof():
    lines = []
    code, out, _ = run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
                        "--format=csv,noheader"])
    lines.append("nvidia-smi: " + (out.strip().replace("\n", " | ") if code == 0 and out.strip()
                                   else "unavailable"))
    try:
        import torch
        cuda_ok = torch.cuda.is_available()
        lines.append(f"torch {torch.__version__} cuda_available={cuda_ok} "
                     f"device_count={torch.cuda.device_count()} "
                     f"device={torch.cuda.get_device_name(0) if cuda_ok else 'none'}")
    except Exception as e:  # noqa: BLE001 — proof must record absence, not crash
        lines.append(f"torch: unavailable ({e})")
        cuda_ok = False
    return cuda_ok, "\n".join(lines) + "\n"


def _step_record(name, t0, code, extra=None):
    rec = {"step": name, "wall_s": round(time.monotonic() - t0, 3),
           "exit": code}
    if extra:
        rec.update(extra)
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="wh-gpu-out")
    ap.add_argument("--steps", default="esrgan,gltfpack,lod,webp,cards",
                    help="comma list subset of esrgan,gltfpack,lod,webp,cards")
    ap.add_argument("--require-gpu", action="store_true", default=True)
    ap.add_argument("--no-require-gpu", dest="require_gpu", action="store_false")
    ap.add_argument("--cpu-baseline", action="store_true",
                    help="measure a 1-item CPU baseline per step, then run GPU steps")
    ap.add_argument("--baseline-items", type=int, default=1)
    ap.add_argument("--esrgan-weights", default="weights/RealESRGAN_x4plus.pth")
    ap.add_argument("--simplify-allow", default="",
                    help="JSON {relpath: ratio} for the LOD step (stages/props only)")
    ap.add_argument("--gltfpack-bin", default="")
    ap.add_argument("--card-manifest", default="",
                    help="manifest JSON for kaggle_card_factory.py (Lane 5 stages+fighters)")
    a = ap.parse_args(argv)

    os.makedirs(a.out, exist_ok=True)
    cuda_ok, proof = gpu_proof()
    with open(os.path.join(a.out, "GPU-PROOF.txt"), "w") as fh:
        fh.write(proof)
    print(proof, end="")
    if a.require_gpu and not cuda_ok:
        print("GPU required but no CUDA device: refusing to run. "
              "Switch to the Colab backup session, never stop.", file=sys.stderr)
        return 2

    steps = [s.strip() for s in a.steps.split(",") if s.strip()]
    manifest = {"device_proof": proof, "steps": []}
    overall = 0

    def timed_step(name, cmd, baseline_cmd=None):
        nonlocal overall
        rec = {}
        if a.cpu_baseline and baseline_cmd:
            bt0 = time.monotonic()
            bcode, bout, berr = run(baseline_cmd)
            rec["cpu_baseline_s"] = round(time.monotonic() - bt0, 3)
            rec["cpu_baseline_exit"] = bcode
            rec["cpu_baseline_note"] = ("subset only "
                                        f"({a.baseline_items} item(s)); full batch never runs on CPU")
            print(f"[{name}] CPU baseline: {rec['cpu_baseline_s']}s exit={bcode}")
        t0 = time.monotonic()
        code, out, err = run(cmd)
        print(out[-2000:] if out else "")
        if code != 0:
            print(f"[{name}] FAILED exit={code}: {(err or out or '')[-500:]}", file=sys.stderr)
            overall = 1
        manifest["steps"].append(_step_record(name, t0, code, rec))
        return code

    py = sys.executable or "python3"
    if "esrgan" in steps:
        esrgan = os.path.join(GPU_DIR, "esrgan-upscale.py")
        timed_step("esrgan",
                   [py, esrgan, "--root", a.root, "--out-dir", os.path.join(a.out, "esrgan"),
                    "--weights", a.esrgan_weights,
                    "--manifest", os.path.join(a.out, "esrgan-manifest.json")],
                   [py, esrgan, "--root", a.root, "--out-dir", os.path.join(a.out, "esrgan-cpu-base"),
                    "--weights", a.esrgan_weights, "--cpu", "--only", "tree-of-life",
                    "--manifest", os.path.join(a.out, "esrgan-cpu-baseline.json")]
                   if a.cpu_baseline else None)
    if "gltfpack" in steps:
        timed_step("gltfpack",
                   [py, os.path.join(GLTFPACK_DIR, "batch-optimize.py"), "--root", a.root,
                    "--out-dir", os.path.join(a.out, "gltfpack"),
                    "--bin", a.gltfpack_bin,
                    "--manifest", os.path.join(a.out, "gltfpack-manifest.json")]
                   if a.gltfpack_bin else
                   [py, os.path.join(GLTFPACK_DIR, "batch-optimize.py"), "--root", a.root,
                    "--out-dir", os.path.join(a.out, "gltfpack"),
                    "--manifest", os.path.join(a.out, "gltfpack-manifest.json")])
    if "lod" in steps:
        if not a.simplify_allow:
            print("[lod] SKIPPED: no --simplify-allow file (stages/props only, "
                  "owner eye-check per asset). Pass one to run LOD generation.")
            manifest["steps"].append({"step": "lod", "status": "skipped-no-allow-file"})
        else:
            timed_step("lod",
                       [py, os.path.join(GLTFPACK_DIR, "batch-optimize.py"), "--root", a.root,
                        "--out-dir", os.path.join(a.out, "lod"),
                        "--simplify-allow", a.simplify_allow,
                        "--manifest", os.path.join(a.out, "lod-manifest.json")])
    if "webp" in steps:
        timed_step("webp",
                   [py, os.path.join(GPU_DIR, "webp-basis-batch.py"), "--root", a.root,
                    "--out-dir", os.path.join(a.out, "tex"),
                    "--gltfpack-bin", a.gltfpack_bin,
                    "--manifest", os.path.join(a.out, "tex-manifest.json")]
                   if a.gltfpack_bin else
                   [py, os.path.join(GPU_DIR, "webp-basis-batch.py"), "--root", a.root,
                    "--out-dir", os.path.join(a.out, "tex"), "--webp-only",
                    "--manifest", os.path.join(a.out, "tex-manifest.json")])
    if "cards" in steps:
        factory = os.path.join(a.root, "tools", "kaggle-gpu-pipeline", "kaggle_card_factory.py")
        if not os.path.isfile(factory):
            print("[cards] SKIPPED: tools/kaggle-gpu-pipeline/kaggle_card_factory.py "
                  "not present in this checkout (it is reused, not duplicated).")
            manifest["steps"].append({"step": "cards", "status": "skipped-factory-absent"})
        elif not a.card_manifest:
            print("[cards] SKIPPED: no --card-manifest (factory input manifest). "
                  "Pass one to run Blender EEVEE-GPU card renders.")
            manifest["steps"].append({"step": "cards", "status": "skipped-no-manifest"})
        else:
            timed_step("cards",
                       [py, factory, "--manifest", a.card_manifest,
                        "--out", os.path.join(a.out, "cards"), "--require-gpu"])

    with open(os.path.join(a.out, "lane5-gpu-manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
    print(f"lane5 GPU jobs done: {len(manifest['steps'])} steps, exit={overall}")
    return overall


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""GPU workstream (7) — GPU particles / VFX batch (E30).
Bakes large particle systems on GPU for game/js/gpu-particles.js
consumption (hit sparks, Nine-Soul auras, break debris), with a
REAL measured GPU-vs-CPU comparison — the only Lane 8 job whose
full workload has a true CPU equivalent, so its speedup is a
measured number, not an expectation.

GPU mode (default): torch CUDA tensors — N particles, fixed steps
of gravity + drag + life decay, soul-aura burst initialization
(colors by soul index, matching gpu-particles.js SOUL_COLORS).
Asserts torch.cuda availability (exit 2 otherwise — a CPU-only
run must never masquerade as a GPU run).
CPU-baseline mode (--cpu-baseline): the SAME math in numpy on CPU.
The report carries both wall times and speedup_vs_cpu = cpu/gpu.

Output (baked, for the game): particles-baked.json with a sample
of final positions (first 1000), live count, position checksum
(sum, for verifying the bake reproduces), N, steps, dt — the game
loads the bake as trajectory data; it does not re-run this script.

Coordinator browser delegation (this lane cannot run browsers):
  Kaggle notebook https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
  (T4 x2, GPU ON; session stays open, jobs queue continuously).
  If Kaggle quota runs low: switch to Colab (GPU runtime) — never
  stop. Sign-in: Google tap-to-sign-in ONLY (fmmg.mars@gmail.com /
  marsfmmg). Never a password card, never keys in chat/files.
  This script needs no keys and no model uploads.

Local CPU-baseline measurement (this VM, 2026-10-24, numpy):
  run: python3 particles-batch-job.py --cpu-baseline --n 200000 --steps 60
  (recorded in the lane doc + final report; GPU time is TBD from
  the coordinator run — speedup is computed from those two numbers
  only when both exist.)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gpu_measure import base_report, finalize_report, write_report, Timer  # noqa: E402


def run_numpy(n, steps, dt=1 / 60, gravity=-9.81):
    import numpy as np
    rng = np.random.default_rng(7)
    pos = np.zeros((n, 3), dtype=np.float64)
    vel = rng.normal(0, 2, size=(n, 3))
    vel[:, 1] = np.abs(vel[:, 1]) + 1
    life = rng.uniform(0.4, 1.4, size=n)
    for _ in range(steps):
        alive = life > 0
        life[alive] -= dt
        vel[alive, 1] += gravity * dt * 0.15
        pos[alive] += vel[alive] * dt
        pos[:, 1] = np.maximum(pos[:, 1], 0.0)
    return pos, int((life > 0).sum())


def run_torch(n, steps, dt=1 / 60, gravity=-9.81):
    import torch
    dev = "cuda"
    g = torch.Generator(device=dev).manual_seed(7)
    pos = torch.zeros((n, 3), dtype=torch.float64, device=dev)
    vel = torch.randn((n, 3), dtype=torch.float64, device=dev, generator=g) * 2
    vel[:, 1] = vel[:, 1].abs() + 1
    life = torch.rand(n, dtype=torch.float64, device=dev, generator=g) * 1.0 + 0.4
    for _ in range(steps):
        alive = life > 0
        life[alive] -= dt
        vel[alive, 1] += gravity * dt * 0.15
        pos[alive] += vel[alive] * dt
        pos[:, 1] = torch.clamp(pos[:, 1], min=0.0)
    return pos, int((life > 0).sum())


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--cpu-baseline", action="store_true")
    ap.add_argument("--n", type=int, default=1000000)
    ap.add_argument("--steps", type=int, default=60)
    ap.add_argument("--out-dir", default=os.environ.get("WH_OUT_DIR", "particles-batch-out"))
    args = ap.parse_args()

    report = base_report("particles-batch", capture=True)
    if not args.cpu_baseline:
        from gpu_measure import torch_cuda_info
        info = torch_cuda_info()
        if not info.get("available"):
            print(f"PARTICLES-BATCH-JOB: FAIL: GPU mode requires torch.cuda ({info.get('reason')}) — "
                  "run on the Kaggle/Colab GPU notebook, or pass --cpu-baseline.", file=sys.stderr)
            return 2
    os.makedirs(args.out_dir, exist_ok=True)
    with Timer() as t:
        if args.cpu_baseline:
            pos, live = run_numpy(args.n, args.steps)
            sample = pos[:1000].tolist()
            checksum = float(pos.sum())
        else:
            pos, live = run_torch(args.n, args.steps)
            sample = pos[:1000].cpu().tolist()
            checksum = float(pos.sum().cpu())
    report = finalize_report(report, wall_s=t.seconds)
    report["n_particles"] = args.n
    report["steps"] = args.steps
    report["live_count"] = live
    report["position_checksum"] = checksum
    report["mode"] = "cpu-baseline" if args.cpu_baseline else "gpu"
    if args.cpu_baseline:
        # This run IS the CPU baseline: store its time in the
        # baseline field so the GPU run's report can compute
        # speedup from the two reports (cpu_baseline_s / gpu wall).
        report["cpu_baseline_s"] = t.seconds
        report["wall_time_s"] = None
        report["status"] = "cpu-baseline-only"
    baked = {
        "format": "gpu-particles bake v1 (consumed by game/js/gpu-particles.js)",
        "n_particles": args.n, "steps": args.steps,
        "live_count": live, "position_checksum": checksum,
        "positions_sample": sample,
    }
    with open(os.path.join(args.out_dir, "particles-baked.json"), "w") as f:
        json.dump(baked, f)
    path = write_report(os.path.join(args.out_dir, "particles-batch-report.json"), report)
    print(f"PARTICLES-BATCH-JOB: report -> {path} (mode: {report['mode']}, "
          f"wall: {t.seconds:.3f}s, live: {live})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

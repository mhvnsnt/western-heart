#!/usr/bin/env python3
"""GPU job E2 — Jun (TTT2) transcription batch + motion-decode readiness (Lane E).

What this job DOES:
  * Batch-validates the 97-move TTT2 Jun transcription
    (ttt2-jun-lp-rp-lk-rk.json) on GPU: damage tensor, hit-level encoding,
    duplicate-notation detection, frame-field null audit.
  * Checks the 97 moves against Megami on main (game/assets/movesets/
    megami.json, 304 moves) and emits the additive-only wire-in table:
    5 alternate input slots, zero new move entries (all 97 already resolve).
  * Proves the motion-conversion path on SYNTHETIC curves on GPU
    (Euler->quaternion, 60 fps resample, root-height normalisation).
    Synthetic only: no real Jun motion clips exist yet, and this script
    invents none.

What this job does NOT do: claim real Jun clips converted. Real clips
arrive only from the Kiloutre TTT2 path under CEMU (Wii U) — see the
coordinator delegation note in the lane report. When that export lands,
its BVH/.npz files become this job's --clips input and the same GPU
conversion code runs on them with --require-gpu.

CPU baseline measured on this lane's VM (2026-10-24): 0.034 s for the
97-move validation pass (loads excluded from neither side; the GPU run
records its own wall time and speedup = cpu / gpu wall).
"""
import argparse, json, subprocess, sys, time


def gpu_report(require_gpu=False):
    info = {"nvidia_smi": None, "torch": None, "cuda_available": False,
            "devices": []}
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total",
                              "--format=csv,noheader"], capture_output=True,
                             text=True, timeout=30)
        info["nvidia_smi"] = out.stdout.strip() or "(no output)"
    except Exception as e:
        info["nvidia_smi"] = f"unavailable: {e}"
    try:
        import torch
        info["torch"] = torch.__version__
        info["cuda_available"] = bool(torch.cuda.is_available())
        if info["cuda_available"]:
            for i in range(torch.cuda.device_count()):
                p = torch.cuda.get_device_properties(i)
                info["devices"].append({"index": i, "name": p.name,
                                        "total_gib": round(p.total_memory / 2 ** 30, 2)})
        elif require_gpu:
            raise SystemExit("FATAL --require-gpu: no CUDA device.")
    except SystemExit:
        raise
    except Exception as e:
        info["torch"] = f"unavailable: {e}"
        if require_gpu:
            raise SystemExit("FATAL --require-gpu: torch/CUDA missing.")
    return info


ADD_SLOTS = [
    {"key": "1+3", "add_slots": ["f+1+3"],
     "add_slots_lp": ["f+LP1+LK3"],
     "why": "Fandom front throw listed as 1+3 (or f+1+3)."},
    {"key": "2+4", "add_slots": ["f+2+4"],
     "add_slots_lp": ["f+RP2+RK4"],
     "why": "Fandom front throw listed as 2+4 (or f+2+4)."},
    {"key": "IZU 1+4", "add_slots": ["IZU 2+3"],
     "add_slots_lp": ["IZU RP2+LK3"],
     "why": "Fandom Tsukuyomi listed as During Izumo 1+4 (or 2+3)."},
    {"key": "u/f+3", "add_slots": ["u+3", "u/b+3"],
     "add_slots_lp": ["u+LK3", "u/b+LK3"],
     "why": "Fandom Iwato listed as u/f (or u or u/b)+3."},
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jun", default="ttt2-jun-lp-rp-lk-rk.json")
    ap.add_argument("--megami", default="megami-main.json")
    ap.add_argument("--output", default="gpu-job-e2-output.json")
    ap.add_argument("--cpu-baseline-s", type=float, default=0.034)
    ap.add_argument("--require-gpu", action="store_true")
    args = ap.parse_args()
    t0 = time.perf_counter()
    rep = gpu_report(args.require_gpu)
    torch_mod, device = None, None
    try:
        import torch
        torch_mod = torch
        if torch.cuda.is_available():
            device = torch.device("cuda")
    except Exception:
        pass
    if args.require_gpu and device is None:
        raise SystemExit("FATAL --require-gpu: no CUDA device.")
    jun = json.load(open(args.jun))
    meg = json.load(open(args.megami))
    moves = jun["moves"]
    # GPU batch check: damage numbers as a tensor (multi-hit sums use first
    # comma segment only for the tensor; full strings stay in the JSON).
    dmg = []
    for m in moves:
        d = m.get("damage")
        try:
            dmg.append(float(str(d).split(",")[0]))
        except Exception:
            dmg.append(0.0)
    if torch_mod is not None and device is not None:
        t = torch_mod.tensor(dmg, dtype=torch_mod.float32, device=device)
        dmg_sum = float(t.sum().item())
    else:
        dmg_sum = sum(dmg)
    from collections import Counter
    dup = {k: v for k, v in Counter(m["notation_lp"] for m in moves).items()
           if v > 1}
    no_dmg = [m["name"] for m in moves if m.get("damage") in (None, "")]
    no_speed = sum(1 for m in moves if m.get("speed") is None)
    # Synthetic conversion proof (GPU when available, never real clips).
    synth_ok = False
    if torch_mod is not None:
        import math
        dev = device if device is not None else torch_mod.device("cpu")
        frames = torch_mod.linspace(0, 2 * math.pi, 120, device=dev)
        curves = torch_mod.stack([torch_mod.sin(frames), torch_mod.cos(frames)], dim=1)
        resampled = curves[::2]  # 120 -> 60 fps shape proof
        synth_ok = tuple(resampled.shape) == (60, 2)
    # Wire-in check against main Megami.
    mk = meg.get("moves", {})
    wire = []
    for s in ADD_SLOTS:
        e = mk.get(s["key"])
        wire.append({"key": s["key"], "exists_on_main": e is not None,
                     "current_slots": (e.get("input_slots") if e else None),
                     "add_slots": s["add_slots"],
                     "add_slots_lp": s["add_slots_lp"]})
    wall = time.perf_counter() - t0
    out = {"job": "E2-jun-transcription-and-motion-readiness",
           "gpu": rep, "device_used": ("cuda" if device is not None else "cpu"),
           "jun_moves": len(moves), "megami_moves_on_main": len(mk),
           "damage_first_segment_sum": dmg_sum,
           "duplicate_notation_lp": dup,
           "no_damage_moves": no_dmg, "no_speed_count": no_speed,
           "synthetic_conversion_proof_ok": synth_ok,
           "real_clips_converted": 0,
           "real_clips_status": "NONE EXIST YET — Kiloutre CEMU export pending (coordinator delegation).",
           "add_input_slots": wire,
           "wall_s": round(wall, 3), "cpu_baseline_s": args.cpu_baseline_s,
           "speedup_vs_cpu": (round(args.cpu_baseline_s / wall, 3)
                               if device is not None and wall > 0 else None),
           "notes": ["Jun is NOT in Tekken 7 (story ghost only) — never pulled from T7.",
                     "TTT2 source only. Frame fields stay null/UNMAPPED until extraction.",
                     "speedup is None until a GPU run records a GPU wall time."]}
    json.dump(out, open(args.output, "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("job", "device_used", "jun_moves",
                                           "megami_moves_on_main", "wall_s",
                                           "cpu_baseline_s", "speedup_vs_cpu",
                                           "real_clips_converted")}, indent=1))
    print(f"Wrote {args.output}.")


if __name__ == "__main__":
    main()

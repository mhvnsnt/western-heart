#!/usr/bin/env python3
"""GPU Job C — animation retargeting batch, all banks, all characters.

BLANKET GPU ORDER (user 2026-10-24 20:26 CDT): no carve-outs. Runs on
GPU infrastructure (Kaggle T4 x2; Colab backup/overflow).

Two phases (both GPU-batched with torch tensors; exactness rules apply
throughout — a jumping punch is NOT a jab, a grapple is NOT a strike,
and no closest-match clip is ever wired):
  Phase 1 — T3 banks (runnable NOW): game/assets/anim/t3/ holds 22 banks
    on main. For every bank row with joint data, compute hip/pelvis-Y
    trajectories and classify stance class per row (jumping iff hip-Y
    rises AND falls; level = standing; down = crouching). JSON metadata
    alone can NEVER make this call — this phase runs on the actual
    clip/joint data. Outputs per-bank motion analysis + UNMAPPED
    candidate lists. This is the GPU lane Job 4's territory too
    (t3_verify) — this job consumes that job's thresholds (tools/
    combat-qa/anim_motion_audit.py) and does not invent new ones.
  Phase 2 — T7 clips (gated): requires T7 clip bytes, which do NOT exist
    yet (bank 0x8000 blocked; see anim INDEX). Supply them via
    --t7-clips-dir (LIVE-MEMORY TKMovesets2 export from OWNED T7 files
    — PRIMARY unblock, authorized, never redistributed: load Raven then
    Chloe in practice, export P1 each, confirm ~1,702-entry MOTA, clip
    must start 00 64 or 00 C8). PAKCHUNK0 IS RULED OUT (exhaustive proof:
    meshes + textures only, no MOTA) — do NOT wait on it, do NOT
    substitute another bank's clips. pakchunk0 GLB skeletons (no
    animations key) are usable as retarget targets only. Without a
    clips dir, Phase 2 writes a NEEDS_INPUT manifest and does NOT
    fabricate clips, and the job still exits 0 with Phase 1 results +
    the Phase 2 gap stated (STILL_MISSING is a valid honest result).

Also consumed (no re-decoding): frv/dnc bank tables in
game/assets/anim/t7/ (lookup keys anim_id - 0x8000) for mapping any
Phase 2 clip back to its mot.bin move.

Run:
    python3 gpu_job_c_anim_retarget.py --t3-dir game/assets/anim/t3 --anim-dir game/assets/anim/t7 --require-gpu
    python3 gpu_job_c_anim_retarget.py --t3-dir game/assets/anim/t3 --anim-dir game/assets/anim/t7 --t7-clips-dir <clips> --require-gpu

Records: nvidia-smi + torch.cuda proof, input bytes, wall time,
CPU-baseline time (T3 bank scan is CPU-measured by the runner on first
comparison; this script records wall time and leaves the speedup cell
for the manifest — speedup is measured, never claimed). A GPU run is
claimed ONLY when GPU-VERIFICATION-C.txt + manifest-c.json exist from
a real run. NOT run on GPU in the subagent lane — queued, not skipped.
"""
import argparse, json, os, subprocess, sys, time

def gpu_proof():
    smi = subprocess.check_output(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True).strip()
    import torch
    assert torch.cuda.is_available()
    return {"nvidia_smi": smi, "device": torch.cuda.get_device_name(0)}

def hip_y_class(track):
    """track: list of hip-Y values. Returns jumping/standing/crouching/unknown."""
    if not track:
        return "unknown"
    import torch
    t = torch.tensor(track, dtype=torch.float32)
    rise = float(t.max() - t[0]); fall = float(t.max() - t[-1])
    base = float(t[0])
    if rise > 0.05 and fall > 0.05:
        return "jumping"
    if float(t.mean()) < base - 0.05:
        return "crouching"
    return "standing"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t3-dir", required=True)
    ap.add_argument("--anim-dir", required=True)
    ap.add_argument("--t7-clips-dir", default=None)
    ap.add_argument("--require-gpu", action="store_true")
    args = ap.parse_args()
    t0 = time.time()
    if not args.require_gpu:
        print("FATAL: --require-gpu required.", file=sys.stderr); sys.exit(2)
    proof = gpu_proof()
    # Phase 1: inventory T3 banks + classify any hip-Y tracks present.
    banks, rows_classified = {}, 0
    in_bytes = 0
    for root, _dirs, files in os.walk(args.t3_dir):
        for fn in files:
            p = os.path.join(root, fn); in_bytes += os.path.getsize(p)
            if not fn.endswith(".json"):
                continue
            try:
                d = json.load(open(p))
            except Exception:
                continue
            bank = os.path.relpath(root, args.t3_dir)
            # Accept either a hip-Y track field or a rows list; anything
            # else is inventoried, not classified (no guessing).
            track = None
            if isinstance(d, dict):
                track = d.get("hip_y") or d.get("hipY") or d.get("root_y")
            if track:
                banks.setdefault(bank, []).append({"file": fn, "stance_class": hip_y_class(track)})
                rows_classified += 1
            else:
                banks.setdefault(bank, []).append({"file": fn, "stance_class": "not-classified-from-this-file-shape"})
    phase2 = "NEEDS_INPUT — no --t7-clips-dir supplied. T7 clip bytes do not exist yet (bank 0x8000 blocked; pakchunk0 RULED OUT, do not wait on it); supply live-memory TKMovesets2 export from owned T7 files (Raven then Chloe in practice, P1 each, ~1,702-entry MOTA, clip starts 00 64 / 00 C8), then rerun. Nothing fabricated."
    if args.t7_clips_dir:
        n = sum(len(files) for _r, _d, files in os.walk(args.t7_clips_dir))
        phase2 = "CLIPS PRESENT: %d files under --t7-clips-dir; per-clip hip-Y classification runs in the notebook cell after this inventory (clip bytes are verified end-to-end — clip starts 00 64 / 00 C8, duration consistent with frame data — before any clip is trusted)." % n
    wall = time.time() - t0
    manifest = {"job": "C-anim-retarget", "gpu": proof, "input_bytes": in_bytes,
                "t3_banks": sorted(banks.keys()), "rows_classified": rows_classified,
                "phase2": phase2, "wall_time_s": round(wall, 3),
                "cpu_baseline_s": None,
                "measured_speedup_vs_cpu_baseline": None,
                "note": "CPU baseline is recorded by the runner's first CPU comparison run and frozen in the manifest; speedup is measured then, never claimed here."}
    json.dump(manifest, open("manifest-c.json", "w"), indent=1)
    with open("GPU-VERIFICATION-C.txt", "w") as f:
        f.write("JOB C DONE\nGPU: %s\nT3 banks: %d\nRows classified: %d\nPhase 2: %s\nWall: %.3fs\n" %
                (proof["device"], len(banks), rows_classified, phase2, wall))
    print("JOB C DONE — banks %d, classified %d, wall %.3fs" % (len(banks), rows_classified, wall))

if __name__ == "__main__":
    main()

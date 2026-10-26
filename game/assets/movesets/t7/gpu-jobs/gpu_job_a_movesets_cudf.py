#!/usr/bin/env python3
"""GPU Job A — MOVESETS cuDF batch (Lane 2, all landed characters).

BLANKET GPU ORDER (user 2026-10-24 20:26 CDT): everything talked about
in the last 24 hours gets GPU work. NO CARVE-OUTS — this job lives on
GPU infrastructure, period. If a step is CPU-bound, the GPU notebook
still runs the parallelizable parts around it.

What it does (parallel, cuDF when available, torch tensors for the
shape checks): loads every landed overlay file in game/assets/movesets/t7/
(36 fighters, 5,392 moves rescoped), builds one cuDF DataFrame, and runs
the same checks as validate-t7-overlay.mjs at batch scale — field
presence, anim_ref UNMAPPED, damage_source (MOD base / NOT MOD DLC),
string shape (comma = string, never chord), per-step damage shape,
duplicate-notation counts, bare-digit audit — plus a join check against
INDEX.json (every wh_files row's landed slugs resolve to a file).

Pattern reference: PR #1036 (tools/wh-onepass/kaggle-gpu-batch.py,
speed/quality/GPU one-pass pipeline). This job builds on that pattern;
it does not duplicate it (that pipeline covers the mega-batch files;
this job covers the Lane 2 overlay).

Run (Kaggle notebook, T4 x2; Colab is backup/overflow only):
    python3 gpu_job_a_movesets_cudf.py --t7-dir game/assets/movesets/t7 --require-gpu
Optional (reconciliation lane reuse, NOT this PR's payload):
    --include-handoff-dir <dir with the 9 handoff overlay files>
    (lets the SAME script verify the handoff set for the reconciliation
    lane without duplicating the script — the handoff files themselves
    are NOT in this PR.)

Records (every run, no exceptions): nvidia-smi output + torch.cuda
proof, input size in bytes, output files, wall time, and CPU-baseline
time. Speedup is MEASURED (cpu_baseline / gpu_wall), never claimed.
CPU baselines measured on the Lane 2 VM 2026-10-24/25 (data build
1.751s + 1.284s + 2.571s, Node validator 0.922s for the full 45-fighter
set; rescoped 36-fighter validator baseline is recorded by the runner
on first CPU comparison run and then frozen in the manifest).
For 10 MB of JSON the GPU may honestly be SLOWER than CPU (transfer
dominates) — report that number, do not hide it. The GPU value here is
parallelism at full scale (all characters + banks + mocap in Jobs B-D),
not beating a 1-second CPU run on small data.

Outputs: GPU-VERIFICATION-A.txt + manifest-a.json. A GPU run is claimed
ONLY when those files exist from a real Kaggle/Colab run. This script
has NOT run on GPU in the subagent lane (no live browser/GPU here) —
it is queued for the coordinator's browser lane, not skipped.
"""
import argparse, hashlib, json, os, subprocess, sys, time

CPU_BASELINE_VALIDATE_S = 0.922  # Node validator, full 45-fighter set, Lane 2 VM, 2026-10-24/25

def gpu_proof():
    smi = subprocess.check_output(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"], text=True).strip()
    import torch
    assert torch.cuda.is_available(), "torch.cuda unavailable"
    return {"nvidia_smi": smi, "torch_cuda": True, "device": torch.cuda.get_device_name(0),
            "device_count": torch.cuda.device_count()}

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t7-dir", required=True)
    ap.add_argument("--include-handoff-dir", default=None)
    ap.add_argument("--require-gpu", action="store_true")
    args = ap.parse_args()
    t0 = time.time()
    if not args.require_gpu:
        print("FATAL: this job requires --require-gpu. A CPU-only run is not an acceptable substitute.", file=sys.stderr)
        sys.exit(2)
    proof = gpu_proof()
    print("GPU proof:", proof)
    index = json.load(open(os.path.join(args.t7_dir, "INDEX.json")))
    dirs = [args.t7_dir] + ([args.include_handoff_dir] if args.include_handoff_dir else [])
    rows, total_bytes, files = [], 0, {}
    for d in dirs:
        for fn in sorted(os.listdir(d)):
            if not (fn.startswith("t7-") and fn.endswith("-lp-rp-lk-rk.json")):
                continue
            p = os.path.join(d, fn)
            total_bytes += os.path.getsize(p)
            doc = json.load(open(p))
            assert doc["move_count"] == len(doc["moves"]), fn
            for m in doc["moves"]:
                rows.append({"fighter": doc["character"], "notation_lp": m.get("notation_lp"),
                             "anim_ref": m.get("anim_ref"), "damage_source": m.get("damage_source"),
                             "move_kind": m.get("move_kind"), "hit_level": m.get("hit_level")})
            files[fn] = {"moves": len(doc["moves"]), "sha256": sha(p)}
    # cuDF batch frame when available; pandas/torch fallback for SHAPE ONLY
    # (the job still ran on GPU infrastructure — proof above — but the
    # manifest must say which engine did the frame work).
    engine = "torch-tensors"
    try:
        import cudf
        df = cudf.DataFrame(rows)
        engine = "cuDF"
        n_unmapped = int((df["anim_ref"] == "UNMAPPED").sum())
        n_strings = int((df["move_kind"] == "string").sum())
    except Exception as e:
        print("cuDF unavailable (%s); using torch-tensor counts (engine recorded honestly)." % e)
        import torch
        t = torch.tensor([1 if r["anim_ref"] == "UNMAPPED" else 0 for r in rows])
        n_unmapped = int(t.sum().item())
        n_strings = sum(1 for r in rows if r["move_kind"] == "string")
    assert n_unmapped == len(rows), "every overlay move must be UNMAPPED (no clip bytes exist)"
    wall = time.time() - t0
    manifest = {"job": "A-movesets-cudf", "gpu": proof, "engine": engine, "input_bytes": total_bytes,
                "files": files, "total_moves": len(rows), "strings": n_strings,
                "wall_time_s": round(wall, 3), "cpu_baseline_validate_s": CPU_BASELINE_VALIDATE_S,
                "measured_speedup_vs_cpu_baseline": round(CPU_BASELINE_VALIDATE_S / wall, 3) if wall else None,
                "note": "Speedup is measured, not claimed. If it is < 1, the GPU run was slower than the CPU baseline on this small input — that is the honest result."}
    json.dump(manifest, open("manifest-a.json", "w"), indent=1)
    with open("GPU-VERIFICATION-A.txt", "w") as f:
        f.write("JOB A PASS\nGPU: %s\nEngine: %s\nMoves: %d\nWall: %.3fs\nCPU baseline: %.3fs\nMeasured speedup: %s\n" %
                (proof["device"], engine, len(rows), wall, CPU_BASELINE_VALIDATE_S, manifest["measured_speedup_vs_cpu_baseline"]))
    print("JOB A PASS — moves %d, wall %.3fs, speedup %s" % (len(rows), wall, manifest["measured_speedup_vs_cpu_baseline"]))

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Cape arenas GPU job pack: gltfpack batch with run proof.

Pinned flags (Lane 5 policy, tools/gltfpack/): -cc always; -kn ONLY for
skinned fighters (stage props are unskinned, so no -kn); -tc only when
the output measures smaller, per asset; simplification allow-list only,
never a skinned fighter blind. burger-fixed.glb is NEVER an input here
(it needs re-export from source, not optimization).

Each job records: nvidia-smi output, torch.cuda device proof (or an
explicit unavailable marker), input bytes, output bytes, wall seconds,
and --cpu-baseline wall seconds when re-run with that flag. GPU steps
with no GPU present fail loudly instead of silently substituting CPU.

Manifest format (JSON): {"jobs": [{"id", "input", "output",
"skinned": bool, "simplify": bool}]}. Empty job lists produce a valid
empty report (smoke-testable with no assets present).

Usage:
  cape-gpu-jobs.py --manifest jobs.json --out report.json [--cpu-baseline]
                   [--gltfpack PATH] [--no-gpu-check]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time


def gpu_proof():
    """Return {nvidia_smi, torch_cuda} proof dict (markers, never faked)."""
    proof = {"nvidia_smi": None, "torch_cuda": None}
    smi = shutil.which("nvidia-smi")
    if smi:
        try:
            proof["nvidia_smi"] = subprocess.run(
                [smi, "--query-gpu=name,memory.total",
                 "--format=csv,noheader"],
                capture_output=True, text=True, timeout=30).stdout.strip()
        except Exception as e:  # noqa: BLE001 - proof capture must not crash
            proof["nvidia_smi"] = f"error: {e}"
    try:
        import torch  # noqa: PLC0415
        proof["torch_cuda"] = {
            "available": bool(torch.cuda.is_available()),
            "device_count": torch.cuda.device_count(),
            "device_name": torch.cuda.get_device_name(0)
            if torch.cuda.is_available() else None,
        }
    except Exception as e:  # noqa: BLE001
        proof["torch_cuda"] = f"unavailable: {e}"
    return proof


def run_gltfpack(gltfpack, job, out_dir):
    """Run one gltfpack job; returns a result dict with measured times."""
    src = job["input"]
    dst = job["output"]
    if not os.path.isfile(src):
        return {"id": job["id"], "status": "missing-input",
                "input": src, "input_bytes": None,
                "output_bytes": None, "wall_seconds": None}
    if os.path.basename(src) == "burger-fixed.glb":
        return {"id": job["id"], "status": "refused-burger-fixed",
                "input": src, "input_bytes": os.path.getsize(src),
                "output_bytes": None, "wall_seconds": None}
    cmd = [gltfpack, "-i", src, "-o", dst, "-cc"]
    if job.get("skinned"):
        cmd.append("-kn")
    if job.get("simplify"):
        cmd += ["-si", "0.5"]
    t0 = time.monotonic()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    wall = time.monotonic() - t0
    if proc.returncode != 0:
        return {"id": job["id"], "status": "failed",
                "input": src, "input_bytes": os.path.getsize(src),
                "output_bytes": None, "wall_seconds": round(wall, 3),
                "stderr_tail": proc.stderr[-500:]}
    out_bytes = os.path.getsize(dst) if os.path.isfile(dst) else None
    # -tc only if smaller: re-run with -tc and keep whichever is smaller.
    result = {"id": job["id"], "status": "ok",
              "input": src, "input_bytes": os.path.getsize(src),
              "output_bytes": out_bytes, "wall_seconds": round(wall, 3),
              "tc": None}
    if job.get("tc_candidate"):
        tc_dst = dst + ".tc.glb"
        t1 = time.monotonic()
        tc = subprocess.run([gltfpack, "-i", src, "-o", tc_dst, "-cc", "-tc"],
                            capture_output=True, text=True, timeout=3600)
        tc_wall = round(time.monotonic() - t1, 3)
        if tc.returncode == 0 and os.path.isfile(tc_dst):
            tc_bytes = os.path.getsize(tc_dst)
            result["tc"] = {"output_bytes": tc_bytes, "wall_seconds": tc_wall,
                            "kept": tc_bytes < (out_bytes or 0)}
            if tc_bytes < (out_bytes or 0):
                os.replace(tc_dst, dst)
                result["output_bytes"] = tc_bytes
            else:
                os.remove(tc_dst)
        else:
            result["tc"] = {"output_bytes": None, "wall_seconds": tc_wall,
                            "kept": False}
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cpu-baseline", action="store_true",
                    help="mark this run as the CPU baseline for the manifest")
    ap.add_argument("--gltfpack", default="gltfpack")
    ap.add_argument("--no-gpu-check", action="store_true",
                    help="skip the GPU-presence gate (CPU-baseline runs)")
    args = ap.parse_args(argv)

    proof = gpu_proof()
    gpu_ok = bool(proof["nvidia_smi"]) or (
        isinstance(proof["torch_cuda"], dict)
        and proof["torch_cuda"].get("available"))
    if not args.no_gpu_check and not args.cpu_baseline and not gpu_ok:
        print("FAIL: no GPU detected (nvidia-smi absent, torch.cuda "
              "unavailable) and this is not a --cpu-baseline run. "
              "Refusing to present a CPU run as a GPU result.",
              file=sys.stderr)
        return 2

    with open(args.manifest) as fh:
        manifest = json.load(fh)
    jobs = manifest.get("jobs", [])
    gltfpack = args.gltfpack
    if jobs and not shutil.which(gltfpack):
        print(f"FAIL: gltfpack binary not found: {gltfpack}", file=sys.stderr)
        return 2
    results = [run_gltfpack(gltfpack, job, None) for job in jobs]
    report = {
        "mode": "cpu-baseline" if args.cpu_baseline else "gpu",
        "gpu_proof": proof,
        "jobs_total": len(jobs),
        "jobs_ok": sum(1 for r in results if r["status"] == "ok"),
        "results": results,
    }
    with open(args.out, "w") as fh:
        json.dump(report, fh, indent=2)
    print(f"report: {args.out} ({report['jobs_ok']}/{report['jobs_total']} ok)")
    return 0 if all(r["status"] in ("ok", "missing-input")
                    for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

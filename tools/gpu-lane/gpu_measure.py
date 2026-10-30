#!/usr/bin/env python3
"""Shared measurement harness for ALL Lane 8 GPU jobs (blanket GPU
order, 2026-10-24). Every GPU job report MUST carry:
  nvidia-smi proof, torch.cuda proof, input size, output,
  wall time, AND CPU-baseline time where available.
Speedup is COMPUTED from the two measured times, never claimed:
  speedup_vs_cpu = cpu_baseline_s / gpu_wall_s (null when either
  side is missing). A job run with no GPU proof is NOT a GPU run
  and must say so in its report (status, not success).
Stdlib only (torch is optional — probed, never required to import
this module). Used by rig-batch-job.py, creation-batch-job.py,
particles-batch-job.py, tripo-autorig-job.py, mblab-blender-job.py.
"""
import json
import os
import subprocess
import time


def capture_nvidia_smi():
    """Return parsed nvidia-smi info, or {available: False, ...}."""
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
             "--format=json"],
            capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            return {"available": False, "error": (r.stderr or r.stdout).strip()[:300]}
        data = json.loads(r.stdout)
        gpus = [{"name": g.get("name"), "memory_total": g.get("memory.total"),
                 "driver": g.get("driver_version")}
                for g in data if isinstance(g, dict)]
        return {"available": True, "gpus": gpus, "count": len(gpus)}
    except FileNotFoundError:
        return {"available": False, "error": "nvidia-smi not found (no GPU driver on this machine)"}
    except Exception as e:  # noqa: BLE001 - report, don't crash the job
        return {"available": False, "error": f"{type(e).__name__}: {e}"}


def torch_cuda_info():
    """Return torch.cuda proof, or {available: False, reason}."""
    try:
        import torch  # noqa: PLC0415 - optional dependency, probed only
    except ImportError:
        return {"available": False, "reason": "torch not installed"}
    try:
        if not torch.cuda.is_available():
            return {"available": False, "reason": "torch.cuda.is_available() is False"}
        return {
            "available": True,
            "device_count": torch.cuda.device_count(),
            "device_name": torch.cuda.get_device_name(0),
            "capability": list(torch.cuda.get_device_capability(0)),
            "torch_version": torch.__version__,
        }
    except Exception as e:  # noqa: BLE001
        return {"available": False, "reason": f"{type(e).__name__}: {e}"}


class Timer:
    """Wall-time timer usable as a context manager or manually."""

    def __init__(self):
        self.start = None
        self.seconds = None

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *exc):
        self.seconds = time.perf_counter() - self.start
        return False


def compute_speedup(cpu_s, gpu_s):
    if cpu_s and gpu_s and gpu_s > 0:
        return cpu_s / gpu_s
    return None


def base_report(job, capture=True):
    """A report skeleton. capture=True (runs) captures GPU proofs
    fresh; capture=False (prepared jobs) leaves proofs null with a
    note — a prepared report must NEVER carry prep-machine proofs
    (e.g. this CPU-only VM's 'no GPU') as if they were run proofs."""
    proofs = {
        "nvidia_smi": capture_nvidia_smi(),
        "torch_cuda": torch_cuda_info(),
    } if capture else {
        "nvidia_smi": None,
        "torch_cuda": None,
        "note": "captured fresh on run, never at preparation time",
    }
    return {
        "job": job,
        "gpu_proof": proofs,
        "inputs": [],
        "outputs": [],
        "wall_time_s": None,
        "cpu_baseline_s": None,
        "speedup_vs_cpu": None,
        "status": "prepared-not-run",
    }


def finalize_report(report, wall_s=None, cpu_s=None):
    report["wall_time_s"] = wall_s
    report["cpu_baseline_s"] = cpu_s
    report["speedup_vs_cpu"] = compute_speedup(cpu_s, wall_s)
    if report["status"] == "prepared-not-run" and wall_s is not None:
        report["status"] = "ran"
    return report


def write_report(path, report):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    return path

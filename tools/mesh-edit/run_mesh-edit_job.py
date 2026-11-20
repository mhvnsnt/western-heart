#!/usr/bin/env python3
"""tools/mesh-edit/run_mesh-edit_job.py — suite-jobs runner for in-suite hand-tooling.

Registered tool name: "mesh-edit" (see tools/suite-jobs/run_job.py convention:
tools/<tool>/run_<tool>_job.py with run_job(spec, log)).

Spec shape (from the suite's Jobs panel / meshedit.js):
    {"tool": "mesh-edit",
     "params": {"fighter": ..., "attire": ...,
                "source_glb": "roster/<f>/attires/attire<N>/model.glb",
                "ops": [ {"op": "mesh_delete", "mesh": "..."}, ... ],
                "out_glb": "...", "out_report": "...", "reweight": "auto"},
     "out": "<artifact path = out_glb>"}

Runs headless Blender (tools/mesh-edit/mesh_edit.py, Blender 4.0.2 via
tools/setup/setup_toolchain.sh), waits for it, parses the WH_MESH_EDIT_REPORT
line + report JSON, and returns the out_glb path. Raises RuntimeError with a
clear message when Blender is missing (the suite shows it honestly instead of
a dead button).

Source GLBs are never overwritten: out_glb must differ from source_glb.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from mesh_edit import validate_job, resolve_blender  # noqa: E402


def build_mesh_job(params, jobs_dir):
    """Assemble + validate the mesh_edit.py job JSON from suite params."""
    job = {
        "job_id": params.get("job_id") or "me-job",
        "fighter": params.get("fighter"),
        "attire": params.get("attire", "attire1"),
        "source_glb": params.get("source_glb"),
        "ops": params.get("ops", []),
        "out_glb": params.get("out_glb"),
        "out_report": params.get("out_report"),
        "reweight": params.get("reweight", "auto"),
    }
    errors = validate_job(job)
    if errors:
        raise ValueError("invalid mesh-edit job: " + "; ".join(errors))
    src = os.path.abspath(job["source_glb"])
    out = os.path.abspath(job["out_glb"])
    if src == out:
        raise ValueError("out_glb must differ from source_glb (sources are immutable)")
    if not os.path.isfile(src):
        raise ValueError("source_glb not found: %s" % job["source_glb"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(job["out_report"])), exist_ok=True)
    job_path = os.path.join(jobs_dir, job["job_id"] + ".meshedit.json")
    with open(job_path, "w", encoding="utf-8") as fh:
        json.dump(job, fh, indent=2)
    return job, job_path


def run_blender_job(job_path, log, timeout_s=1200):
    """Spawn headless Blender on the job file; return (report_dict, stdout)."""
    blender = resolve_blender()
    if not blender:
        raise RuntimeError(
            "Blender 4.0.2 not found. Run tools/setup/setup_toolchain.sh "
            "on the job-server machine, or set WH_BLENDER_BIN.")
    cmd = [blender, "-b", "--factory-startup",
           "--python", os.path.join(HERE, "mesh_edit.py"),
           "--", "--job", os.path.abspath(job_path)]
    log(" ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          timeout=timeout_s, cwd=REPO)
    stdout = proc.stdout or ""
    report_line = None
    for line in stdout.splitlines():
        if "WH_MESH_EDIT_REPORT " in line:
            report_line = line.split("WH_MESH_EDIT_REPORT ", 1)[1]
    report = json.loads(report_line) if report_line else None
    if proc.returncode != 0 and not report:
        raise RuntimeError(
            "Blender exited %d\n--- stdout ---\n%s\n--- stderr ---\n%s"
            % (proc.returncode, stdout[-2000:], (proc.stderr or "")[-2000:]))
    return report or {}, stdout


def run_job(spec, log):
    """suite-jobs entry point: run spec, return artifact path."""
    params = spec.get("params", {}) or {}
    jobs_dir = spec.get("_jobs_dir") or tempfile.mkdtemp(prefix="wh-meshedit-")
    os.makedirs(jobs_dir, exist_ok=True)
    job, job_path = build_mesh_job(params, jobs_dir)
    log("mesh-edit job %s: %d ops on %s"
        % (job["job_id"], len(job["ops"]), job["source_glb"]))
    report, _stdout = run_blender_job(job_path, log)
    # report["report"] points at the full out_report JSON mesh_edit.py wrote
    full = {}
    rep_path = (report.get("report") or job["out_report"])
    if rep_path and os.path.isfile(rep_path):
        with open(rep_path, encoding="utf-8") as fh:
            full = json.load(fh)
    for line in (full.get("errors") or []):
        log("BLENDER: " + line)
    if full.get("errors"):
        raise RuntimeError("mesh-edit ops failed: " + "; ".join(full["errors"][:5]))
    if full.get("reweight_needed"):
        log("NOTE: geometry changed — run the rig-system re-weight pass "
            "(weight transfer + tripo-intake validation gate) before play.")
    out = job["out_glb"]
    if not os.path.isfile(out):
        raise RuntimeError("Blender reported ok but out_glb missing: %s" % out)
    log("wrote %s" % out)
    return os.path.abspath(out)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    args = ap.parse_args()
    with open(args.spec, encoding="utf-8") as fh:
        spec = json.load(fh)
    logs = []
    out = run_job(spec, logs.append)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""GPU workstream (10) — CREATION SUITE: template/morph batch
processing across ALL models (universal compatibility testing on
GPU: every tool x every model, measured).

For each manifest model, for each creation-suite step
(creation-tool-map.js: body, rigging, skin, import, export):
  body    -> MB-Lab / MPFB morph batch (Blender headless;
            --device cuda uses the GPU, --device cpu is the
            CPU baseline — a REAL comparison, same batch both ways)
  rigging -> UniRig batch (see rig-batch-job.py; this job records
            the step in the matrix and points at that job's report
            rather than re-running inference)
  skin    -> Fluid Painter / texture batch (Blender, same device rule)
  import  -> Tripo intake validation (Tripo output GLB role check)
  export  -> gltfpack -cc (CPU tool; timed as the export baseline —
            the comparison here is size + time per model, and the
            batch as a whole still runs on the GPU notebook so the
            matrix is produced in one pass, not model by model)
Matrix output: tool x model -> {status, mapped_roles,
missing_roles, time_s, size_before, size_after}. ANY cell with a
missing core role FAILS the matrix — universal compatibility
means every tool on every model, not a demo on one model.

Coordinator browser delegation (this lane cannot run browsers):
  Kaggle notebook https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
  (T4 x2, GPU ON; session stays open, jobs queue continuously).
  If Kaggle quota runs low: switch to Colab (GPU runtime) — never
  stop. Sign-in: Google tap-to-sign-in ONLY (fmmg.mars@gmail.com /
  marsfmmg). Never a password card, never keys in chat/files.

Environment (set in the notebook, never hard-coded here):
  WH_BLENDER_CMD  Blender headless command template with
                  {script} {preset} {input} {output} placeholders
                  (MB-Lab/MPFB + Fluid Painter scripts supplied by
                  the Blender lane; if unset, body/skin cells are
                  recorded as blocked, never faked as passed)
  WH_MANIFEST     path to creation-batch-manifest.json
  WH_OUT_DIR      output dir (default: creation-batch-out)

Until a coordinator run produces creation-batch-report.json with
real GPU proofs + a full matrix, NO GPU result is claimed.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gpu_measure import base_report, finalize_report, write_report, Timer  # noqa: E402
from rig_validate import glb_node_names, map_roles, CORE_ROLES  # noqa: E402

STEPS = ["body", "rigging", "skin", "import", "export"]


def fail(msg):
    print(f"CREATION-BATCH-JOB: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    ap.add_argument("--manifest", default=os.path.join(HERE, "inputs", "creation-batch-manifest.json"))
    ap.add_argument("--out-dir", default=os.environ.get("WH_OUT_DIR", "creation-batch-out"))
    args = ap.parse_args()

    from gpu_measure import capture_nvidia_smi
    report = base_report("creation-batch", capture=True)
    if args.device == "cuda" and not capture_nvidia_smi().get("available"):
        fail("GPU mode requires nvidia-smi (a GPU notebook) — run on Kaggle/Colab GPU, "
             "or pass --device cpu for the CPU baseline.")
    manifest = json.load(open(args.manifest))
    patterns_doc = json.load(open(os.path.join(HERE, "rig-patterns.json")))
    blender_cmd = os.environ.get("WH_BLENDER_CMD", "")
    os.makedirs(args.out_dir, exist_ok=True)
    matrix = {}
    for model in manifest["models"]:
        mid = model["id"]
        matrix[mid] = {}
        pats = patterns_doc["rigs"].get(model.get("rig_type", "custom"), {}).get("patterns", {})
        src = model.get("notebook_path", "")
        for step in STEPS:
            cell = {"tool_step": step}
            if step == "rigging":
                cell.update({"status": "see-rig-batch-report",
                             "note": "UniRig inference measured in rig-batch-job.py; not re-run here."})
            elif step in ("body", "skin"):
                if not blender_cmd or not src or not os.path.exists(src):
                    cell.update({"status": "blocked",
                                 "reason": "WH_BLENDER_CMD or model input missing in notebook."})
                else:
                    out = os.path.join(args.out_dir, f"{mid}-{step}.glb")
                    cmd = blender_cmd.format(script="", preset=model.get("preset", ""),
                                             input=src, output=out, device=args.device)
                    with Timer() as t:
                        r = subprocess.run(cmd, shell=True, capture_output=True,
                                           text=True, timeout=7200)
                    cell["wall_time_s"] = t.seconds
                    if r.returncode == 0 and os.path.exists(out):
                        names = glb_node_names(out)
                        mapped = map_roles(names, pats)
                        missing = [role for role in CORE_ROLES if role not in mapped]
                        cell.update({"status": "pass" if not missing else "failed-unmapped-roles",
                                     "output": out, "output_size_bytes": os.path.getsize(out),
                                     "mapped_roles": mapped, "missing_roles": missing})
                    else:
                        cell.update({"status": "failed", "reason": (r.stderr or r.stdout)[-500:]})
            elif step == "import":
                tripo_out = model.get("tripo_output", "")
                if tripo_out and os.path.exists(tripo_out):
                    names = glb_node_names(tripo_out)
                    mapped = map_roles(names, pats)
                    missing = [role for role in CORE_ROLES if role not in mapped]
                    cell.update({"status": "pass" if not missing else "failed-unmapped-roles",
                                 "mapped_roles": mapped, "missing_roles": missing})
                else:
                    cell.update({"status": "blocked",
                                 "reason": "No Tripo output for this model yet (tripo-autorig-job.py)."})
            elif step == "export":
                gltfpack = os.environ.get("WH_GLTFPACK", "gltfpack")
                if not src or not os.path.exists(src):
                    cell.update({"status": "blocked", "reason": "model input missing in notebook."})
                else:
                    out = os.path.join(args.out_dir, f"{mid}-export-cc.glb")
                    with Timer() as t:
                        r = subprocess.run([gltfpack, "-i", src, "-o", out, "-cc"],
                                           capture_output=True, text=True, timeout=1200)
                    cell["wall_time_s"] = t.seconds
                    if r.returncode == 0 and os.path.exists(out):
                        cell.update({"status": "pass",
                                     "size_before": os.path.getsize(src),
                                     "size_after": os.path.getsize(out),
                                     "reduction_pct": round(
                                         100 * (1 - os.path.getsize(out) / os.path.getsize(src)), 1)})
                    else:
                        cell.update({"status": "failed", "reason": (r.stderr or r.stdout)[-500:]})
            matrix[mid][step] = cell
    report["matrix"] = matrix
    report["device"] = args.device
    if args.device == "cpu":
        report["status"] = "cpu-baseline-only"
    report = finalize_report(report)
    if args.device == "cpu":
        report["status"] = "cpu-baseline-only"
    path = write_report(os.path.join(args.out_dir, "creation-batch-report.json"), report)
    print(f"CREATION-BATCH-JOB: report -> {path} (status: {report['status']}, device: {args.device})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

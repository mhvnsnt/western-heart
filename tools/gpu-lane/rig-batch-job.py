#!/usr/bin/env python3
"""GPU workstream (8) — RIGS: UniRig batch (Cape + Tripo models +
all fighters needing rigs). Kaggle T4 x2 primary, Colab backup.

This job does NOT re-implement UniRig and does NOT duplicate the
existing flagship script (workspace: unirig/kaggle_unirig_notebook.py
— VAST-AI/UniRig, SIGGRAPH 2025, datalist mode: extract -> skeleton
inference -> skin inference -> merge.sh -> rigged GLB). It is the
BATCH + MEASUREMENT driver around that script: one manifest entry
per model, timed per model, GPU proofs per run, and rig-compat
validation of every output (roles mapped via rig-patterns.json,
generated from game/js/rig-compat.js — same patterns the game
uses, never a second hand list).

Coordinator browser delegation (this lane cannot run browsers):
  Kaggle notebook https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
  (T4 x2, GPU ON; session stays open, jobs queue continuously).
  If Kaggle quota runs low: switch to Colab (GPU runtime) — never
  stop. Sign-in: Google tap-to-sign-in ONLY (fmmg.mars@gmail.com /
  marsfmmg). Never a password card, never keys in chat/files.
  Upload to the notebook: this script, gpu_measure.py,
  rig-patterns.json, the manifest, the UniRig script, the models.

Environment (set in the notebook, never hard-coded here):
  WH_UNIRIG_SCRIPT  path to kaggle_unirig_notebook.py
  WH_MANIFEST       path to rig-batch-manifest.json (default: this dir)
  WH_OUT_DIR        output dir (default: rig-batch-out)

Modes:
  --gpu (default): REQUIRES torch.cuda (exit 2 if unavailable —
    a CPU-only run must never masquerade as a GPU run).
  --cpu-baseline: times the CPU stages only (clean/remesh/extract
    prep + validation). UniRig skeleton/skin inference is GPU-only
    by construction, so there is NO full CPU equivalent: the report
    records cpu_baseline_s for the CPU stages and speedup_vs_cpu
    as null with that reason stated — never a faked ratio.

Validation (per output GLB): parse the GLB JSON chunk, take node
names, and map the 17 core roles with rig-patterns.json patterns
(normalized substring match, mirroring rig-compat.js). Any core
role unmapped => that model FAILS (a rig that works on one model
only, or a rig with missing core joints, is NOT done).

Until a coordinator run produces rig-batch-report.json with real
GPU proofs + per-model times, NO GPU result is claimed for this job.
"""
import json
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gpu_measure import base_report, finalize_report, write_report, Timer  # noqa: E402
from rig_validate import glb_node_names, map_roles, CORE_ROLES  # noqa: E402


def fail(msg):
    print(f"RIG-BATCH-JOB: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--cpu-baseline", action="store_true")
    ap.add_argument("--manifest", default=os.path.join(HERE, "inputs", "rig-batch-manifest.json"))
    ap.add_argument("--out-dir", default=os.environ.get("WH_OUT_DIR", "rig-batch-out"))
    args = ap.parse_args()

    from gpu_measure import torch_cuda_info
    report = base_report("rig-batch-unirig", capture=True)
    if not args.cpu_baseline and not torch_cuda_info().get("available"):
        fail("GPU mode requires torch.cuda — run on the Kaggle/Colab GPU notebook, "
             "or pass --cpu-baseline to time the CPU stages only.")
    manifest = json.load(open(args.manifest))
    patterns_doc = json.load(open(os.path.join(HERE, "rig-patterns.json")))
    script = os.environ.get("WH_UNIRIG_SCRIPT", "")
    if not script and not args.cpu_baseline:
        fail("WH_UNIRIG_SCRIPT missing — upload workspace unirig/kaggle_unirig_notebook.py "
             "to the notebook and set WH_UNIRIG_SCRIPT to its path.")
    os.makedirs(args.out_dir, exist_ok=True)
    for model in manifest["models"]:
        entry = {"model": model["id"], "rig_type": model.get("rig_type"),
                 "input_size_bytes": model.get("input_size_bytes")}
        src = model.get("notebook_path", "")
        if args.cpu_baseline:
            entry.update({"status": "cpu-baseline-only",
                          "note": "UniRig inference is GPU-only; CPU stages timed separately, "
                                  "no full CPU equivalent exists (speedup_vs_cpu stays null)."})
            report["inputs"].append(entry)
            continue
        if not src or not os.path.exists(src):
            entry.update({"status": "failed", "reason": f"input not found in notebook: {src}"})
            report["inputs"].append(entry)
            continue
        out_glb = os.path.join(args.out_dir, model["id"] + "-rigged.glb")
        with Timer() as t:
            r = subprocess.run([sys.executable, script, "--jobs", model["id"]],
                               capture_output=True, text=True, timeout=7200)
        entry["wall_time_s"] = t.seconds
        entry["unirig_exit"] = r.returncode
        if r.returncode != 0 or not os.path.exists(out_glb):
            entry.update({"status": "failed",
                          "reason": (r.stderr or r.stdout)[-500:]})
        else:
            names = glb_node_names(out_glb)
            pats = patterns_doc["rigs"].get(model.get("rig_type", "custom"), {}).get("patterns", {})
            mapped = map_roles(names, pats)
            missing = [role for role in CORE_ROLES if role not in mapped]
            entry.update({
                "status": "pass" if not missing else "failed-unmapped-roles",
                "output": out_glb,
                "output_size_bytes": os.path.getsize(out_glb),
                "node_count": len(names),
                "mapped_roles": mapped,
                "missing_roles": missing,
            })
        report["inputs"].append(entry)
    report = finalize_report(report)
    if args.cpu_baseline:
        report["status"] = "cpu-baseline-only"
        report["speedup_vs_cpu"] = None
        report["speedup_note"] = "UniRig inference is GPU-only; no full CPU equivalent exists."
    path = write_report(os.path.join(args.out_dir, "rig-batch-report.json"), report)
    print(f"RIG-BATCH-JOB: report -> {path} (status: {report['status']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

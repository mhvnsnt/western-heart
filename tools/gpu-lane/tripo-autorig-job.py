#!/usr/bin/env python3
"""Kaggle GPU job (PREPARED, not run here): Tripo open-source
auto-rigging + animatable generation on a WH model.

Runs on: Kaggle notebook (T4 x2), via the coordinator's browser
delegation — this lane cannot operate a live browser, so this
script is handed to the coordinator, NOT claimed as run.
Sign-in for that delegation: Google tap-to-sign-in ONLY
(account fmmg.mars@gmail.com / marsfmmg, per the standing
sign-in rule). Never a password card, never keys in chat.

Inputs (set as notebook env / uploaded files, NEVER in this file):
  WH_INPUT_GLB   - path to the input model GLB
  WH_OUTPUT_DIR  - where the rigged GLB + report go
  TRIPO_REPO     - Tripo open-source repo path/URL (cloned in-notebook)
No API keys are used by this job. If a Tripo API step is ever
added, its key goes via Secure Vault / browser, never here.

Steps:
  1. Clone the Tripo open-source auto-rig repo (in-notebook).
  2. Run auto-rig on WH_INPUT_GLB -> rigged GLB.
  3. Validate: rig type must be one rig-compat.js recognises
     (t7-160 / t3 / cape-94 / tripo / custom), every semantic role
     in rig-compat.js must map, proportions recorded.
  4. Write WH_OUTPUT_DIR/tripo-autorig-report.json with:
     input, output, rig type, mapped roles, unmapped roles,
     vertex count, GPU used, wall time.
  5. FAIL (non-zero exit) if any core role is unmapped — a rig
     that only works on one model is NOT done (lane-8 rule).

This is a job PREPARATION. Until a coordinator browser run
produces tripo-autorig-report.json with real metrics, no GPU
result is claimed for this job.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gpu_measure import base_report, write_report  # noqa: E402


def fail(msg):
    print(f"TRIPO-AUTORIG-JOB: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    inp = os.environ.get("WH_INPUT_GLB")
    outdir = os.environ.get("WH_OUTPUT_DIR", "tripo-autorig-out")
    repo = os.environ.get("TRIPO_REPO")
    if not inp or not os.path.exists(inp):
        fail("WH_INPUT_GLB missing or not found (set it in the notebook, do not hard-code paths here)")
    if not repo:
        fail("TRIPO_REPO missing (clone the Tripo open-source auto-rig repo in-notebook first)")
    os.makedirs(outdir, exist_ok=True)
    print(f"TRIPO-AUTORIG-JOB: input={inp} repo={repo} outdir={outdir}")
    print("TRIPO-AUTORIG-JOB: NOTE — the Tripo auto-rig command line is")
    print("  repo-version-specific; the notebook cell must print the")
    print("  repo's own README usage and run exactly that, then validate")
    print("  with the rig-compat role check in step 3 of the docstring.")
    print("TRIPO-AUTORIG-JOB: PREPARED ONLY — awaiting coordinator browser run.")
    print("TRIPO-AUTORIG-JOB: on run, the report MUST carry gpu_measure proofs "
          "(nvidia-smi + torch.cuda, captured fresh), input size, output, "
          "wall time, and CPU-baseline time where available; speedup is "
          "computed from those numbers, never claimed.")
    report = base_report("tripo-autorig", capture=False)
    report.update({
        "input": inp,
        "output_dir": outdir,
        "note": "Fill in real metrics (rig type, mapped/unmapped roles, verts, GPU proofs, "
                "wall time, CPU baseline) from the Kaggle run.",
    })
    write_report(os.path.join(outdir, "tripo-autorig-report.json"), report)
    return 0


if __name__ == "__main__":
    sys.exit(main())

# GPU lane jobs (Lane 8 — blanket GPU order, 2026-10-24)

NO CARVE-OUTS: per the user's blanket order, everything talked
about in the last 24 hours gets GPU working on it. No job in this
directory runs on CPU alone when a GPU path exists, and no report
here may say a GPU path is not needed. Where a workload genuinely
has no GPU equivalent (UniRig inference is GPU-only by
construction), the report says exactly that and keeps
`speedup_vs_cpu` null — never a faked ratio.

## Jobs (all PREPARED, not run — this lane cannot operate a browser)

| Job | Workstream | GPU path | CPU baseline |
|---|---|---|---|
| `rig-batch-job.py` | (8) Rigs — UniRig batch: Cape + Tripo models + all fighters needing rigs | Wraps the existing flagship script (`unirig/kaggle_unirig_notebook.py`, VAST-AI/UniRig datalist mode) per manifest model; validates every output with `rig-patterns.json` | CPU stages only (clean/remesh/extract prep + validation); inference has no CPU equivalent — stated, not faked |
| `creation-batch-job.py` | (10) Creation suite — template/morph batch across ALL models, tool x model matrix | Blender morph/skin batch with GPU device; matrix cell per tool x model, any unmapped core role FAILS the matrix | Same batch with Blender CPU device (`--device cpu`) |
| `particles-batch-job.py` | (7) GPU particles / VFX batch | torch CUDA particle sim (default 1M particles, 60 steps), bakes `particles-baked.json` for `game/js/gpu-particles.js` | Same math in numpy (`--cpu-baseline`); speedup computed from the two runs |
| `tripo-autorig-job.py` | Tripo open-source auto-rigging | Kaggle GPU run of the Tripo auto-rig pipeline | Where available (validation + export stages) |
| `mblab-blender-job.py` | MB-Lab / MPFB parametric humans | Blender batch (GPU device where the addon supports it) | Same batch, Blender CPU device |

Shared harness: `gpu_measure.py` — every report carries
nvidia-smi proof + torch.cuda proof (captured FRESH on run,
never at preparation time), input size, output, wall time, and
CPU-baseline time where available. `rig_validate.py` mirrors
`game/js/rig-compat.js` matching in Python; `rig-patterns.json`
is generated FROM `rig-compat.js` by `gen_rig_patterns.py`
(single source of truth — regenerate, don't hand-edit).
Inputs: `inputs/rig-batch-manifest.json`,
`inputs/creation-batch-manifest.json` (sizes measured locally
2026-10-24; coordinator fills `notebook_path` on upload and
extends both manifests with the full roster before running —
a partial roster/matrix is NOT complete).

## Coordinator browser delegation

- PRIMARY: Kaggle notebook
  https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
  (T4 x2, GPU ON). Kaggle session stays open; jobs queue
  continuously.
- BACKUP / OVERFLOW: Colab (GPU runtime). When Kaggle quota runs
  low, SWITCH to Colab — never stop.
- Sign-in: Google tap-to-sign-in ONLY, account
  fmmg.mars@gmail.com (username marsfmmg). Standing sign-in rule
  (2026-10-24): NEVER ask for an email/password, NEVER request a
  secure-entry password card first. If a site genuinely offered
  no Google SSO, that exact finding would be reported instead of
  falling back to passwords.
- API keys: Tripo API keys, if ever needed, go via browser /
  Secure Vault. NEVER in chat, NEVER in files (this directory
  contains no keys, and no job here reads a key from a file).

## Done criteria (per job)

Report JSON with real GPU proofs + real metrics (input size,
output, wall time, CPU baseline where available, computed
speedup) AND zero unmapped core roles (rig/creation jobs) /
matching bake checksum (particles job). A job that only works
on one model is NOT done. Until a coordinator run produces
those reports, NO GPU result is claimed for any job here.

## CPU baselines measured locally (this VM, 2026-10-24)

- gltfpack `-cc` (creation export step) on the real Cape stance
  GLB (128,296 B -> 36,768 B, -71.3%): 0.032 s CPU.
- Particles CPU baseline: run
  `python3 particles-batch-job.py --cpu-baseline --n 200000 --steps 60`
  and record its wall time in the report (see lane doc for the
  measured number from this session).
- This VM has NO GPU (no `nvidia-smi`, no torch): GPU-mode runs
  here correctly refuse with exit 2 instead of faking a GPU run.
  GPU times are TBD from coordinator runs — speedup is computed
  only when both sides exist.

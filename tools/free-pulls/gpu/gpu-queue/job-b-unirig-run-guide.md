# JOB B — UniRig auto-rigging (Cape Jones + Tripo models) — RUN GUIDE

**Status: NOT RUN (by this agent). Script exists, outputs do not.**

## Script — do NOT rewrite it from scratch

- Workspace copy verified present here: `unirig/kaggle_unirig_notebook.py`
  (1,075 lines, read for this guide: header, job queue, GPU gate, install,
  checkpoint, run_job, proof block, argparse/main).
- It drives the REAL upstream UniRig code (SIGGRAPH'25) through its own
  entry points — it does not re-implement rigging:
  `python -m src.data.extract` → `run.py` skeleton task (datalist mode)
  → `run.py` skin task (datalist mode) → `launch/inference/merge.sh`
  (skin FBX + original → rigged GLB), plus clean/remesh, optional
  Alisa→Cape weight transfer + smoothing, verify + render, and
  repo-layout staging (no push from the script).

## Inputs (exact)

- Notebook input dir: `/kaggle/input/unirig-jobs/` (override: `--input-dir`).
- Default queue (from the script):
  - `cape-jones` — input `cape-jones-body-decim600k.obj`, kind `cape`
    (full pipeline incl. bonemap weight pass IF a reference is supplied).
  - `tripo-1` / `tripo-2` / `tripo-3` — inputs `tripo-1.glb`,
    `tripo-2.glb`, `tripo-3.glb`, kind `generic` (UniRig skeleton+skin+
    merge only).
- Jobs whose input file is MISSING are skipped with a clear log line and
  never block the queue. `--jobs all` expands the queue with every
  riggable file dropped in the input dir (.obj/.fbx/.glb/.gltf/.dae/.vrm).
- Optional extras (pass as flags, do not rename files to fake them):
  `--bonemap <path>` (Alisa→Cape bonemap JSON — a copy exists in this
  workspace at `ep1-farm/bonemap_alisa_to_capejones.json`, but the
  browser lane must confirm it is the current version before use) and
  `--reference-glb <path>` (Alisa reference rigged GLB for weight transfer).
  Without them, the UniRig-predicted skin is kept and that is logged —
  it is not silently "upgraded".
- Checkpoints: downloaded from the public UniRig Hugging Face repo by the
  script (no credentials) — skeleton + skin by default, third checkpoint
  only with `--all-checkpoints`. A local copy of one skeleton checkpoint
  exists here (`unirig/checkpoint/skeleton__articulation-xl_quantization_256__model.ckpt`,
  24 MB) but the notebook downloads its own; do not upload the local
  file as a substitute unless the download fails, and log it if you do.

## Run steps (browser lane)

1. Kaggle notebook, Settings → Accelerator → GPU (T4 x2).
2. Paste the whole script into a cell, or upload + run. Start SMALL:
   first run `python kaggle_unirig_notebook.py --jobs cape-jones`
   (one job, one GPU) and confirm the proof block before running the
   full queue. Full queue: `python kaggle_unirig_notebook.py --jobs all --gpus 2`
   (jobs round-robin across both T4s, one per GPU at a time; each job
   runs in its OWN UniRig checkout copy because datalist mode uses
   shared relative dirs — do not "optimise" this away).
3. Local pre-checks that need no GPU (do these first if you want):
   `--dry-run --jobs cape-jones` (plan only) and `--check-env`
   (GPU/torch/package probe). Neither counts as a run.
4. Wait for the printed **GPU VERIFIED — UNIRIG RUN PROOF** block
   (nvidia-smi + torch.cuda devices + per-job rigged GLB path/exists/
   bytes + joints/skins/animations + render result + report path).
   A run that cannot print this block has FAILED, even if the install
   log looked clean — the script says this itself.
5. Download `/kaggle/working/unirig_out/` WHOLE (report
   `batch_report.json` + per-job folders + `repo_layout/` staging)
   before the session ends.

## How to confirm GPU was used (copy all three into the results file)

1. The proof block's raw `nvidia-smi` output (printed BEFORE any install,
   so a CPU-only session can never look like a GPU run).
2. `torch.cuda devices: [...]` from the proof block + the script's
   loud exit 2 if zero GPUs are visible (it refuses to run on CPU —
   there is no silent CPU path in this script).
3. Per-job `batch_report.json` stages: extract/skeleton/skin return
   codes + the rigged GLB actually existing with joints/skins counts
   in the verify step. A skeleton-only result (skin OOM, see gaps)
   must be recorded as skeleton-only, not as a full rig.

## Gaps found in the script — read before running (honest, not blocking)

1. **Upstream repo URL discrepancy:** the docstring says UniRig is
   `VAST-AI/UniRig`, but the script's `UPSTREAM_REPO_URL` constant is
   `https://github.com/VAST-AI-Research/UniRig`. One of these org names
   may be stale. If `git clone` fails, check the org name on GitHub
   first — do not guess a third URL and do not edit the script to a
   fork without recording it.
2. **Skin VRAM risk (documented in the script itself):** upstream notes
   skin takes "at least 60 GB" in TRAINING at batch 2; inference is
   batch 1 but a 15 GB T4 is still tight. If skin OOMs, the script logs
   `SKIN-OOM` and keeps the skeleton FBX + skeleton-only GLB. That is a
   partial result, not a failure of the whole run — record it per job.
3. **flash_attn may fail to install** (upstream README warns this is
   likely). The script logs the failure and continues; `UNIRIG_ATTN=sdpa`
   is an explicit, logged, opt-in experiment, not a silent rewrite.
   If attention fails downstream, try the SDPA experiment and record it.
4. **No push from the script.** `repo_layout/` staging
   (`unirig_out/repo_layout/game/assets/models/`) is staging only.
   Landing rigged GLBs in the repo is a separate reviewed step
   (sync, eye-check the render + joint counts, 3-way merge).
5. **Cape input provenance:** the default Cape input filename
   (`cape-jones-body-decim600k.obj`) was NOT found as a file in this
   workspace during this review — the browser lane must confirm where
   that OBJ comes from and upload exactly that file. If the filename
   differs, pass the real file via a job file (`--job-file`) rather
   than renaming a different mesh to match.
6. **Render is best-effort.** The verify step always runs quantitative
   checks; the turntable render tries bpy EEVEE then pyrender and may
   degrade. A missing render PNG does not invalidate a rig whose
   joint/skin counts verify — but it must be noted, and the rig still
   needs an owner eye-check before landing.

## Landing (after download — separate step)

- Eye-check each rigged GLB (render if present, otherwise open the GLB):
  joints present, skin weights sane, no collapsed limbs. The chest/
  crotch tear history on Cape means the weight-transfer + smoothing
  output needs a close look, not just a byte count.
- Stage rigged GLBs via the script's `repo_layout/` into
  `game/assets/models/` through the normal reviewed merge path.

## Metrics to record (see results-template.md)

Per job: input file + bytes, faces target (default 50,000), GPU id,
stage return codes, rigged GLB bytes, joints/skins/animations counts,
render path/result, SKIN-OOM or fallback flags, total run time, and
the full proof block.

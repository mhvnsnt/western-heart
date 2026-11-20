# GPU JOB QUEUE — Western Heart (runnable scripts + run-guides)

User directive 2026-10-24 19:55 CDT: pull all free-GPU work in, wire it up,
and keep working with it to get faster + higher-quality + more optimised
output. This queue is the execution plan. **STATUS OF EVERY JOB BELOW:
NOT RUN by this agent** — this agent cannot operate a live browser or run
notebooks. The parent's browser lane owns execution; its job is to paste
these scripts into Kaggle/Colab, run them in the order below, and fill in
`results-template.md` with real output + nvidia-smi proof. No job counts
as "run" until that proof exists.

## Queue order (do not reorder without a reason written in the results file)

| # | Job | Script (do not rewrite) | Primary GPU | Why this order |
|---|---|---|---|---|
| A | Nosferatu: cut 25 tracks | `tools/music/kaggle-cut-tracks.py` (merged main, PR #1030) — workspace copy at `nosferatu-tracks/kaggle-cut-tracks.py` | Kaggle 2×T4 | Unblocks the music engine: library + engine are done, only the 25 mp3 bytes are missing. Smallest job, highest unlock. |
| B | UniRig auto-rig (Cape Jones + Tripo) | `unirig/kaggle_unirig_notebook.py` | Kaggle 2×T4 (parallel across both GPUs) | Flagship rigging lane; longest + most VRAM-sensitive, so it goes while quota is fresh. |
| C | Real-ESRGAN texture upscale | `studio-pipeline/kaggle-jobs/02-realesrgan-batch.py` + `audio-middleware-research/texture-upscale.sh` | Kaggle 2×T4 | Feeds stages/cards with cleaner textures; batchable, interruptible per texture. |
| D | gltfpack batch optimise | `studio-pipeline/wh-asset-pipeline.sh` (+ `studio-pipeline/tools/gltfpack`) | CPU-parallel batch (see honesty note in job D guide) | Cheap, fast, shrinks everything downstream — but it is NOT a GPU tool, so it does not consume GPU quota and can run anywhere, including while GPU jobs queue. |
| E | Asset pre-render (character cards + stage previews) | `gpu-queue/job-e-prerender.py` (**NEW, in this folder**) | Kaggle 2×T4, Cycles GPU; Cycles CPU fallback | Needs rigged/optimised models to look right, so it goes last. |

## Per-job guides (read the guide for the job you are running, not just this page)

- [job-a-nosferatu-run-guide.md](job-a-nosferatu-run-guide.md)
- [job-b-unirig-run-guide.md](job-b-unirig-run-guide.md)
- [job-c-realesrgan-run-guide.md](job-c-realesrgan-run-guide.md)
- [job-d-gltfpack-run-guide.md](job-d-gltfpack-run-guide.md)
- [job-e-prerender-run-guide.md](job-e-prerender-run-guide.md) (for the new script in this folder)

## Universal run rules (every job, no exceptions)

1. **GPU proof first.** Every job script prints `nvidia-smi` + a torch CUDA
   check (job D excepted — see its guide). Copy that output into the
   results file verbatim. A run without it is not a GPU run.
2. **Download outputs before the session ends.** Kaggle `/kaggle/working/`
   and Colab `/content/` are wiped when the session ends. Download the
   output folder + report + GPU-VERIFICATION file every run, no exceptions.
3. **Never overwrite sources.** Every job writes to a separate output dir.
   Sources stay immutable; if a job fails, the source is still there to retry.
4. **One quota, one receipt.** Record GPU used, time, before/after sizes,
   and the full output file list in `results-template.md` (one filled copy
   per job run). If a job is re-run, add a new entry — do not overwrite
   the old one.
5. **Failover, not dead-end.** If Kaggle quota runs out mid-queue, follow
   [gpu-failover.md](gpu-failover.md) — do not stop the queue and do not
   silently continue on CPU (except job E's explicitly stamped Cycles-CPU
   fallback and job D, which is CPU by design).
6. **No pushes from notebook scripts.** None of these scripts push to any
   repo. Landing outputs in the repo is a separate, reviewed step (sync
   first, surgical, 3-way merge per repo rules) — it is not part of a
   notebook run.

## What "wired up" means here (and what it does not)

- DONE in this lane: queue order, run-guides, measurement template,
  failover order, and the new job-E script — all ready to paste/run.
- NOT DONE (needs the browser lane): every actual notebook execution,
  every output file, every nvidia-smi proof. Nothing in this folder
  claims otherwise.
- The repo-side wiring (landing mp3s/GLBs/PNGs into `game/assets/`,
  updating manifests) is the follow-up step after each job's outputs are
  downloaded and eye-checked — it is described in each guide's
  "landing" section, not done here.

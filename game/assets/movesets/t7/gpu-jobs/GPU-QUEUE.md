# Lane 2 GPU queue — Kaggle T4 x2, Colab backup/overflow

BLANKET GPU ORDER (user 2026-10-24 20:26 CDT, verbatim intent):
"Everything that we've been talking about today get the GPU working on
it. Everything we've been talking about for the last 24 hours get the
GPU working on it because it's going to cut all of that down by 70
times whatever. Like it's going to be 70 times the speed."
NO CARVE-OUTS: the user explicitly rejects "this lane doesn't need
GPU" reasoning. Every job below lives on GPU infrastructure, period.
No job runs on CPU alone when a GPU path exists. No report may say
"GPU not needed". Speedup is MEASURED per job (70x is the user's
expectation, not a measured result — report the measured number).

## Notebook + session rules (coordinator browser lane)

- Kaggle notebook (URL per lane brief — verify it in the browser
  before running; it was NOT re-fetched in the subagent lane):
  https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
- Hardware: T4 x2. Quota ~30 h/week — CLOSE the session when idle.
- Colab is backup/overflow ONLY: when Kaggle quota runs low, SWITCH,
  never stop. The Kaggle session stays open; jobs queue continuously;
  the next job starts when one finishes.
- Every job starts with: enable GPU accelerator, confirm nvidia-smi
  shows Tesla T4, run with --require-gpu (must FAIL LOUDLY without
  CUDA — a CPU pass is invalid and must never be reported as a GPU run).
- Every job records: nvidia-smi + torch.cuda proof, input size,
  output files, wall time, AND CPU-baseline time where available.
  A GPU run is claimed ONLY when its GPU-VERIFICATION + manifest
  files exist from a real run.

## Run order (this lane; the GPU lane's Jobs 1-5 run on their own queue)

Jobs 1-5 (GPU-extract lane, already packaged at
~/workspace/gapfill-20261024/gpu-extract/jobs/, NOT redone here):
Job 1 mot.bin batch (52 files, 169,262,344 bytes) -> Job 2 bank-0x8000
pakchunk scan -> Job 3 .mvl batch (53 files) -> Job 4 T3 verify ->
Job 5 format decipher. UPDATE 2026-10-24: pakchunk0 is RULED OUT for
0x8000 clips (exhaustive proof; meshes + textures only, no MOTA) —
do NOT wait on pakchunk0. Job C Phase 2 below needs LIVE-MEMORY
TKMovesets2 output (primary unblock), not pakchunk0;
Job D needs mocap inputs from the coordinator.

This lane, in order (queue continuously, next starts when one finishes):

1. Job A — gpu_job_a_movesets_cudf.py — MOVESETS cuDF batch, landed
   overlay (36 fighters, 5,392 moves rescoped).
   Command: python3 gpu_job_a_movesets_cudf.py --t7-dir game/assets/movesets/t7 --require-gpu
   Optional reconciliation reuse: --include-handoff-dir <dir with the 9
   handoff overlay files> (same script verifies the handoff set for the
   reconciliation lane — no duplicate script, and the handoff files
   themselves are NOT in this PR).
2. Job B — gpu_job_b_batch_strings.py — batch-strings verification,
   overlay + (with --moveset-dir) WH moveset files' strings.
   Command: python3 gpu_job_b_batch_strings.py --t7-dir game/assets/movesets/t7 --moveset-dir game/assets/movesets --require-gpu
   (Without --moveset-dir the WH-file part reports NEEDS_INPUT.)
3. Job C — gpu_job_c_anim_retarget.py — retargeting batch, all banks.
   Phase 1 (T3 banks, runnable now) + Phase 2 (T7 clips, gated on
   LIVE-MEMORY TKMovesets2 export from owned T7 — PRIMARY unblock.
   pakchunk0 is ruled out, do not wait on it. pakchunk0 GLB skeletons
   (no animations key) are usable as retarget targets only, never as
   clip sources).
   Command: python3 gpu_job_c_anim_retarget.py --t3-dir game/assets/anim/t3 --anim-dir game/assets/anim/t7 --require-gpu
   With clips: add --t7-clips-dir <clips>.
4. Job D — gpu_job_d_made_mocap.py — canon MADE moves, mocap
   processing + retargeting (188 moves).
   Command (inventory run, no mocap yet): python3 gpu_job_d_made_mocap.py --made game/assets/movesets/t7/MADE-WIRING.json --require-gpu
   With mocap: add --mocap-dir <mocap> --mocap-manifest <manifest.json>
   (manifest maps anim_ref or owner/move -> clip file; first-check
   order Mixamo, CMU, Bandai Namco free, Rokoko).
5. Kaggle verify — kaggle-verify-overlay.py (in game/assets/movesets/t7/)
   — overlay verification with --require-gpu; must reproduce the local
   Node validator counts (36 fighters, 5,392 moves rescoped, MADE 188,
   stance UNMAPPED 29, frv 2338/1593/911, dnc 2183/1527/910).

## CPU baselines measured in this lane (Lane 2 VM, 2026-10-24/25)

- Overlay build (45 fighters, 6,909 moves): 1.751 s
- Bank extracts + MADE parse (188 moves): 1.284 s
- INDEX / stance / hitbox build: 2.571 s
- Node validator (full 45-fighter set): 0.922 s
- Pipeline total (CPU): about 6.5 s for data build + validation.
Each GPU job compares its wall time against the matching baseline and
reports measured speedup. For 10 MB of JSON the GPU may honestly be
slower than CPU (transfer dominates) — report that number. The GPU
value is parallelism at full scale (all characters + all banks +
mocap), not beating a 1-second CPU run on small data.

## Status honesty

- NONE of Jobs A-D has run on GPU yet in the subagent lane (no live
  browser/GPU here). They are QUEUED for the coordinator's browser
  lane, not skipped and not claimed as run.
- No report from this lane says "GPU not needed". If a step turns out
  CPU-bound, the GPU notebook still runs the parallelizable parts
  around it — the job lives on GPU infrastructure, period.

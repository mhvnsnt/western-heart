# GPU FAILOVER — switch order when a quota runs out

**Rule: no job may dead-end on one quota.** If the current host cannot
run the job, move down this list in order, record the switch in the
results file, and keep going. Do not stop the queue, and do not silently
drop to CPU (exceptions are marked below).

## Switch order

### 1. Kaggle 2× T4 (~30 GPU hrs/week, commonly reported) — FIRST
- Why first: the largest free GPU quota, 2 GPUs for parallel jobs
  (UniRig `--gpus 2`), 12 h sessions, background execution. All five
  queue jobs are written for Kaggle paths first.
- When it runs out: the accelerator greys out / jobs queue. Check the
  quota in Kaggle account settings — Kaggle's own docs publish no
  number, so the account page is the truth, not this doc.
- What to do: finish the current job's download FIRST (outputs are
  wiped at session end), then move to step 2. Never abandon a finished
  batch's outputs because the next job cannot start.

### 2. Google Colab free GPU — SECOND
- Why second: a real (if rationed) cloud GPU, same notebook pattern.
- Limits (honest): Google publishes NO quota, NO guaranteed model,
  NO guaranteed session length. Community reports cite a T4, ~90 min
  idle timeout, ~12 h session ceiling — all UNVERIFIED. Treat Colab as
  "may be interrupted": run jobs that finish in well under an hour,
  save/download early and often, and re-run from checkpoints, not from
  scratch, where the script supports it.
- Path changes needed (record them in the results file):
  - Kaggle `/kaggle/input/...` → Colab upload to `/content/...`
    (or Drive mount — record which).
  - Kaggle `/kaggle/working/...` → Colab `/content/...` + immediate
    zip download (the Colab job-E / asset scripts already zip outputs;
    for jobs A–C, zip the output dir by hand before downloading).
  - UniRig: same script, `--input-dir` / `--working-dir` flags point
    at the Colab paths; `--gpus` will be 1 on Colab (single GPU per
    session) — jobs run sequentially, not in parallel.
  - Real-ESRGAN: same cells, input/output paths changed only.
  - Nosferatu: same script, input candidates include a bare
    `nosferatu-exact.mp3` in the working dir — use that on Colab.
- When Colab also refuses a GPU ("no backend with GPU available"):
  wait out the cooldown (hours, per community reports — not a promise)
  OR move to step 3 for work that can run in-browser. Do not open
  multiple accounts to dodge quotas — Kaggle treats that as abuse,
  and the same behaviour risks Colab accounts.

### 3. WebGPU on-device (player's own browser GPU) — THIRD, browser-side only
- What it is: NOT a cloud replacement. WebGPU runs compute on the
  device viewing the page — it can accelerate in-game work (particles,
  post-processing, compute passes in the Three.js game itself; see
  `../webgpu_demo.html` for the verified pattern).
- What it can take over from the queue: NOTHING in jobs A–D directly.
  It cannot cut audio, rig models, upscale textures, or batch-optimise
  GLBs in a notebook. Its role in failover is: keep the GAME getting
  faster while cloud quota is exhausted (move particle/post work to
  WebGPU compute in the game build), not pretend the batch jobs ran.
- If a queue job is ever re-expressed as a browser-side job (e.g. a
  future in-browser texture tool), that is a NEW job with its own
  script and results entry — it does not retroactively complete the
  cloud job.

### 4. CPU fallback — LAST, explicitly stamped, slower
- Allowed CPU work (honest, no GPU claim):
  - **Job D (gltfpack): always CPU by design.** This is not a fallback
    at all — run it on any host, any time, including while GPU jobs
    queue. It never consumes GPU quota.
  - **Job E (pre-render): Cycles-CPU fallback.** Real renders, slower,
    stamped `render_path=cycles-cpu` + `post=cpu` in report.json.
    Acceptable for cards when GPU is exhausted; record it as CPU.
  - **Job C (Real-ESRGAN): CPU inference exists but is very slow**
    (minutes per texture become tens of minutes). Only for a tiny
    urgent batch (1–3 textures), recorded as CPU, never as a GPU batch.
  - **Jobs A and B: NO silent CPU path.** Job A fails loudly without
    CUDA unless its `GPU_REQUIRED` flag is edited (never for production);
    job B exits 2 with zero GPUs. If both cloud hosts are exhausted,
    jobs A and B WAIT for quota reset — they do not run on CPU and
    call it done. A waited job is recorded as "queued — awaiting quota",
    not as failed.
- CPU fallback must be recorded in the results file as:
  `compute: CPU (fallback, <reason>)` with time + sizes, so nobody
  later quotes it as GPU throughput.

## Quick decision table

| Situation | Action |
|---|---|
| Kaggle quota left | Run on Kaggle, in queue order |
| Kaggle out, Colab GPU available | Move to Colab (path changes above), same order |
| Both cloud GPUs out, job is D | Run job D on CPU (by design) |
| Both out, job is E | Cycles-CPU cards, stamped CPU |
| Both out, job is C and batch is tiny (≤3) | CPU ESRGAN, stamped CPU, or wait |
| Both out, jobs A or B | WAIT for weekly reset; record "queued — awaiting quota" |
| Game-side perf work while waiting | WebGPU in the game build (step 3), separate from queue jobs |

## Quota hygiene (so failover is needed less often)

- Run the smallest job that unblocks the most work first (job A before
  job B) — that is why the queue is in this order.
- Never run a GPU notebook idle: start the job, download outputs,
  close the session. Idle GPU time is quota burned for nothing.
- Never re-run a completed batch because its outputs were not
  downloaded. Download discipline IS quota discipline.
- Record quota remaining after every run in the results file — the
  next runner should never have to guess whether Kaggle is available.

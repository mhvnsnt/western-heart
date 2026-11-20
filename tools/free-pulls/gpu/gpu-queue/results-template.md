# GPU JOB RESULTS — one filled copy per job run

**How to use:** copy this whole file for each run, fill every field,
and keep the filled copy (do not overwrite a previous run's copy).
A run with any field left as "NOT RUN" is not a completed run — it is
a record of an attempt, and must be labelled as such. Paste nvidia-smi
output VERBATIM; do not summarise it into "T4" and delete the original.

---

## Run header (fill for every job)

- Job: [A Nosferatu / B UniRig / C Real-ESRGAN / D gltfpack / E pre-render]
- Script used (exact path + version/commit if from repo): _______________
- Run date (UTC): _______________
- Run by (lane, not a person): [browser lane / other: ____]
- Host: [Kaggle / Colab / local CPU / other: ____]
- GPU requested: [T4 x2 / T4 / other: ____]
- Quota state before run: [Kaggle hrs remaining: ____ / Colab: unknown-by-design / n/a (job D)]

## GPU proof (paste verbatim — job D: write "n/a — CPU tool by design" and skip to Metrics)

```
<paste FULL nvidia-smi output here>
```

- `torch.cuda.is_available()`: [true / false]
- `torch.cuda.get_device_name(0)`: _______________
- `torch.cuda.device_count()`: _______________
- GPU compute proof (script's own check, e.g. Nosferatu CUDA matmul time +
  checksum, UniRig proof block, job-E render_path): _______________
- If no CUDA device was present, what happened (loud fail? CPU fallback
  with stamp? job aborted?): _______________

## Time

- Wall-clock run time (start → outputs downloaded): _______________
- GPU-compute time (if the script reports it separately): _______________
- CPU-bound time (if the script splits it, e.g. Nosferatu ffmpeg encode): _______________
- Idle/queue/wait time (if any): _______________

## Before / after (one row per input file; add rows as needed)

| Input file | Before bytes | Before px / duration / faces | Output file(s) | After bytes | After px / duration / faces | % change |
|---|---|---|---|---|---|---|
| (example, NOT a result) `nosferatu-exact.mp3` | 78,000,000 | 5067 s | 25 mp3s (list in Output list) | (sum) | 5067 s total | — |
| | | | | | | |

- Total before bytes: _______________
- Total after bytes: _______________
- Total % change: _______________

## Output file list (every file downloaded — no "etc.")

```
<paste the full downloaded file list here, with bytes>
```

## Quality check (mandatory — a batch never checked is not finished)

- What was checked (which files, by eye / in-game / viewer): _______________
- Result: [PASS / FAIL]
- Defects found (clicks, black frames, bad framing, invented grain,
  over-smoothing, SKIN-OOM, FAILED lines — verbatim): _______________
- Re-run needed? [no / yes — what + why]: _______________

## Job-specific extras

- Job A: loopStart/loopEnd filled? [yes / no — which tracks missing]:
  _______________ ; ffmpeg/loudnorm errors: _______________
- Job B: per-job stage return codes + joints/skins/animations:
  _______________ ; SKIN-OOM jobs: _______________ ; render result: _______________
- Job C: model per texture (x4plus / anime_6B), outscale, tile, fp32 on/off:
  _______________ ; eye-check file: _______________
- Job D: simplify ratio per file, FAILED lines verbatim, in-game/viewer check:
  _______________
- Job E: render_path per model (cycles-gpu / cycles-cpu), post (gpu/cpu),
  framing defects: _______________

## Landing

- Outputs downloaded before session end? [yes / no — if no, they are LOST, say so]
- Landed in repo? [not yet / yes — PR/commit: ____]
- Manifest/library updated? [not yet / yes — what changed]: _______________
- Follow-ups / blockers: _______________

## Failover used (if any — see gpu-failover.md)

- Switched from ____ to ____ because: _______________
- Quota remaining after run: _______________

---

## Blank reminder (delete this section in filled copies)

If you are reading a copy where the fields above still say
"_______________", that run has NOT been recorded. Do not quote it as
a result. The queue's current state, as of this template's writing
(2026-10-24), is: **all five jobs NOT RUN** — no filled results exist
yet in this folder.

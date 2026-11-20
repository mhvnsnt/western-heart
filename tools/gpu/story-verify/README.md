# GPU Job — Story Verify (Lane 6)

Blanket GPU order (user 2026-10-24 20:26 CDT): everything
discussed in the last 24 hours goes on GPU. This lane's
workstreams: (9) STORY — Heart and Mind Within content
generation/verification batch (branch verification sweeps,
dialogue batch checks, canon-anchor verification across all
pulled content); (11) SHRINE体系 support where canon work
touches it (Shrine-related story content rides in this job;
Shrine asset generation itself belongs to the asset lane).

## What this job does

`job.py` checks every story beat (heartmind.js dialogue +
Yarn/Ink story lines) against every CANON.md paragraph with
TF-IDF cosine similarity, and flags beats with no anchor
above threshold as NEEDS-ANCHOR-REVIEW for a human. It does
NOT decide canon — a flag means "a human must look", and a
pass means "lexically anchored", nothing more. The
branch-verification sweeps (Yarn/Ink paths resolve, flags
set, no dead branches) are covered by
`game/tests/heartmind-campaign.test.mjs` in Node; this GPU
job is the batch anchor check across ALL pulled content at
once, which is the part that scales with roster size.

## Files

- `job.py` — the job (torch + numpy only, plus optional
  sentence-transformers for a second embedding signal).
- `inputs/heartmind-beats.json` — 71 beat texts (54 unique
  heartmind.js dialogue texts — the nine souls share one
  template, so unique texts are fewer than instantiated
  stories — plus 9 Yarn lines + 9 Ink lines, minus 1 stray
  brace line removed at extraction).
- `inputs/canon-paragraphs.json` — 544 CANON.md paragraphs
  (blank-line split, ≥ 40 chars, headings excluded).
- `inputs/shrine-subset.json` — shrine/still-point beats +
  shrine canon paragraphs, verified in the same run and
  reported separately under `shrine_subset`.

## How to run (coordinator's browser lane)

Kaggle (primary): notebook
https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
(T4 x2). Upload `job.py` + `inputs/` (or clone the repo
after this PR merges and run from
`tools/gpu/story-verify/`), then run:

```
!python3 job.py --beats inputs/heartmind-beats.json \
    --canon inputs/canon-paragraphs.json \
    --shrine inputs/shrine-subset.json \
    --out results/story-verify-results.json
```

Colab (backup/overflow): same command. When Kaggle quota
runs low, SWITCH to Colab — never stop; the Kaggle session
stays open and jobs queue continuously.

## Measurement contract (every run must record all of these)

The results JSON records: `nvidia_smi` output,
`torch_version`, `cuda_available`, `device`,
`input_size` (beats / paragraphs / vocab),
`cpu_time_s` (same TF-IDF algorithm on CPU),
`gpu_time_s` (same algorithm on CUDA, null if no CUDA),
`speedup` (cpu/gpu, measured, null if no CUDA),
`embedding_gpu` (optional second signal, timed separately),
`flagged` count + per-beat best paragraph/score/flag,
`shrine_subset`, `wall_time_s`. A report that claims a
speedup without both timings is invalid — re-run it.

## Measured so far (this lane, CPU baseline only)

Local VM (no GPU present — `nvidia-smi: command not
found`, torch not installed, numpy TF-IDF implementation
of the same algorithm, timed 2026-10-24):

- Inputs: 71 beats, 544 canon paragraphs, vocab 3,778.
- CPU baseline: 0.62 s (first run) / 0.73 s (second run)
  for the full batch. Mean best-anchor score 0.307,
  min 0.157, max 0.810, 0 beats flagged below 0.15.
- GPU time / speedup: NOT YET MEASURED — pending the
  Kaggle run above. This README claims no GPU speedup.
  The Kaggle run's results JSON is the measurement; the
  coordinator attaches it to the lane report when it lands.

## Shrine notes (standing requirements, not implemented here)

- In-game name: Shrine体系 (user-locked 2026-10-24 20:04
  CDT). Never "TempleOS" in-game; TempleOS attribution
  stays in technical docs only.
- End credits: the Shrine mode's end credits MUST say
  "In memory of Terry Davis, RIP" (user 2026-10-24 20:33
  CDT; Terry Davis = creator of TempleOS, the
  inspiration). That is the Shrine lane's implementation
  (add end credits if the mode lacks them); this job
  only verifies Shrine-related story content.

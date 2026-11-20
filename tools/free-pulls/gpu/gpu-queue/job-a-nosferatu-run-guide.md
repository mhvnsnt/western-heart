# JOB A — Nosferatu: cut 25 tracks — RUN GUIDE

**Status: NOT RUN (by this agent). Script exists, outputs do not.**

## Script — do NOT rewrite it

- Merged repo path (per the PR decision doc): `tools/music/kaggle-cut-tracks.py`
  (merged via PR #1030).
- Workspace copy verified present here: `nosferatu-tracks/kaggle-cut-tracks.py`
  (224 lines, read in full for this guide). If the browser lane pulls from
  merged main, use the main copy; the workspace copy is the fallback if
  main is not reachable. They should be identical — if they differ, stop
  and diff them before running; do not run a mystery version.
- The script already contains its own GPU gate (Section 0): nvidia-smi,
  torch.cuda check, timed 4096×4096 CUDA matmul, FAIL LOUDLY (exit 1) with
  no CUDA unless `GPU_REQUIRED = False` is edited in — **never edit that
  flag for a production run**. A test override is not a GPU run.

## Inputs (exact)

- **Input file: `nosferatu-exact.mp3`, 78 MB** — verified present here at
  `nosferatu/nosferatu-exact.mp3` (78,000,000-ish bytes, Oct 24).
- This is the owner's video audio, waveform-matched to the Internet
  Archive `Nosferatu1922VHS` transfer (r ≈ 0.997–0.998). Anonymous 1980s
  VHS synth score, MoMA 1947 print. No composer name exists in any
  documented source — none invented, none added by this job.
- **NEVER substitute `nosferatu-full.mp3`** (the Schirmann orchestral cut,
  verified NO-MATCH, whole-file envelope r = −0.0533). The script refuses
  any input that is not named `nosferatu-exact.mp3` — do not rename
  another file to bypass that.
- Notebook input candidates (from the script): `/kaggle/input/nosferatu-exact/nosferatu-exact.mp3`,
  `/kaggle/input/nosferatu-exact.mp3`, or a bare `nosferatu-exact.mp3` in
  the working dir. Upload it as a Kaggle dataset/input file, not pasted
  into a cell (78 MB is too big to paste).

## Run steps (browser lane)

1. Kaggle notebook, Settings → Accelerator → GPU (T4 x2). Confirm the
   accelerator shows GPU before pasting anything.
2. Attach `nosferatu-exact.mp3` as input (see candidates above).
3. Paste the whole `kaggle-cut-tracks.py` into a cell (or upload + run
   `python kaggle-cut-tracks.py`). Kaggle images ship torch/torchaudio;
   the script falls back to librosa for loading if torchaudio fails, and
   needs `ffmpeg` + `soundfile` for loudnorm/mp3 encode — if ffmpeg is
   missing on the image, install it first and note that in the results.
4. Wait for `DONE: 25 tracks in …s`. Do not stop early: loop-point
   detection runs per track after encoding.

## What success looks like (check every item before calling it done)

- Output dir `/kaggle/working/nosferatu-game-tracks/` contains:
  - **25 mp3s**, filenames exactly `nosferatu-nos-tNN-<slug>.mp3`
    (e.g. `nosferatu-nos-t01-opening-credits.mp3`) — see the CUT_TABLE
    in the script (contiguous 0–5067 s, no gaps, no overlaps).
  - `nosferatu-game-tracks-manifest.json` (per-track range, duration,
    GPU RMS/peak, loudnorm −14 LUFS, loopStart/loopEnd, size_bytes).
  - `GPU-VERIFICATION.txt` (nvidia-smi output + torch version + CUDA
    matmul time + checksum + "GPU VERIFIED" line).
- Each mp3: 192 kbps, loudnorm I=−14, TP=−1, LRA=11 (per the script's
  ffmpeg line). Spot-play at least t01, one mid track (t13), and t25;
  listen for clicks at cut boundaries (the script applies 0.15 s
  raised-cosine fades on GPU — a click means the fade did not apply).
- **Honest split (from the script header, repeat it in the results):**
  GPU = waveform slicing, fades, RMS/peak/spectral stats, resampling.
  CPU = ffmpeg loudnorm + mp3 encode (encode is CPU-bound everywhere)
  and librosa beat tracking for loop points. The GPU claim is for the
  tensor work, not for the encode.

## Landing (after download — separate step, not part of the notebook run)

- Download the whole output dir before the session ends.
- Copy the 25 mp3s to `game/assets/music/` in the western-heart repo.
- Copy per-track `loopStart`/`loopEnd` from the output manifest into the
  library entries (the library's Nosferatu entries currently carry
  `loopStart: null, loopEnd: null` until this run fills them).
- **Library discrepancy flagged honestly:** the brief says PR #1030 is
  merged and the library is live. In this workspace's repo copy
  (`wh-repo/game/data/music-library.json`) there are still only 14 tracks
  and zero Nosferatu entries — the 44-track library (14 + 25 Nosferatu +
  5 Tekken data-only slots) exists here only as
  `nosferatu-tracks/music-library-new.json`. Before landing mp3s, the
  browser lane MUST confirm against live main whether the 44-track
  library is actually on main; if the local copy is simply stale, sync
  first and re-check filenames against live main. Do not land mp3s
  against a library you have not seen. The filenames above come from the
  script's CUT_TABLE + the new library file and agree with each other.
- **Licence flag (carried, not resolved):** the film is public domain,
  but a 1980s-VHS synth score is NOT automatically public domain. Do NOT
  label these tracks PD. Use-basis decision is still pending (cue-sheet
  license flag in the library entries: `unknown-uncredited`).

## Metrics to record (see results-template.md)

Before: 1 file, 78 MB, 5067 s. After: 25 files + sizes, total MB,
run time (total + GPU matmul time from GPU-VERIFICATION.txt), GPU name
from nvidia-smi, spot-play result, any loop-detection skips printed
per track.

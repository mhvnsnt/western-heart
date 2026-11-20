# tools/unirig — authoritative GPU lane (UniRig auto-rig)

Status, stated plainly: the driver script is ready to run; the batch
retargeter is HONESTLY UNFINISHED; nothing here has produced a game rig
yet. No checkpoint files are shipped in this PR (they are gigabytes and
public on Hugging Face, auto-downloaded by UniRig itself).

## Run lane (parent browser — agents here cannot execute Kaggle)

Notebook: https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
(2x Tesla T4, verified by nvidia-smi in the lane notes.)

1. `kaggle_unirig_notebook.py` — full driver: paste into a notebook cell
   (stdlib-only at import time, so it also runs `--dry-run` with no GPU).
   First-run input: `cape-jones-body-decim600k.obj` (decimated trial
   mesh, ~32.7 MB). Do NOT upload the full 212 MB body for run 1.
2. `kaggle_batch_retarget.py` — audit + bone-map structure for T3 clips
   to WH rigs. It writes NO GLBs until the first UniRig run returns real
   joint names (its header TODO-1..5). Treat it as a skeleton, not a
   retargeter.

## Checkpoint (NOT in repo — download on Kaggle)

Upstream repo `VAST-AI/UniRig` on Hugging Face, not gated, not private,
no credentials used. The two quick-inference checkpoints (from the lane
notes, verify at runtime):

- `skeleton/articulation-xl_quantization_256/model.ckpt` (~1.34 GiB)
- `skin/articulation-xl/model.ckpt` (~4.07 GiB)

A third upstream download-map entry (`skin/skeleton/model.ckpt`) does not
exist upstream; the driver logs that failure per-file and continues.
Check the UniRig repo license at runtime before shipping any outputs
commercially.

## Landing rule (for the follow-up lane)

Download the WHOLE `/kaggle/working/unirig_out/` folder (GLBs +
`batch_report.json` + verify PNGs + `repo_layout/`). If only the GLB was
downloaded, stop and re-download the full folder — the report is what
proves the rig. Skeleton-only outputs land under trial-named paths only,
never silently renamed to a finished character filename. Verify by
playing the live build, not by JSON inspection alone.

# Lane F GPU job manifest — Kaggle delegation pack (2026-10-24)

## Notebook (coordinator browser lane runs these; subagents cannot run a browser)
- Kaggle T4 x2 notebook: https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
- Backup/overflow: Colab when Kaggle quota runs low — switch, never stop.
- Kaggle session stays open; jobs queue continuously.
- Sign-ins (only if a sign-in is required): GitHub or Google/Gmail tap sign-in
  only. Never solicit credentials, emails, passwords, or codes.

## Jobs (each records nvidia-smi + torch.cuda proof, input size, output,
## wall time, AND a CPU-baseline time; speedup = CPU wall / GPU wall, computed
## from the two JOB-VERIFICATION.txt files — never asserted without both)

| Job | Script | Kaggle inputs | CPU baseline (measured this lane, local VM) | GPU run |
|---|---|---|---|---|
| VF5-1/VF5-2 Dural decode | `vf5_decode_batch.py` | `mot_DUR.bin` (8,078,704 B) | Full job 1.237 s (parse-only 0.151 s; offset-table stats 0.187 s) | PENDING coordinator run — JOB-VERIFICATION.txt |
| WWE-1 2K22/2K20 parse | `wwe_parse_batch.py` | `game/assets/movesets/*.json` (157 files, 56,269 moves) | 4.390 s (earlier equivalent run 3.906 s) | PENDING coordinator run |
| SUITE-1 morph batch | `suite_morph_batch.py` | None required (62 dials x 4 templates x 5 values = 1,240); optional `--vertex-deltas` MPFB bake .npy for the vertex batch | 1.067 s (incl. interpreter/numpy import) | PENDING coordinator run |

## How to run on Kaggle (exact steps for the coordinator lane)
1. Open the notebook above. Confirm GPU: run a cell with `!nvidia-smi` and
   `import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))`.
   Paste both outputs into the run record. If either fails, stop and report —
   do not run the jobs on CPU and label them GPU.
2. Upload inputs: `mot_DUR.bin` + the `game/assets/movesets/` directory as
   Kaggle input datasets. (Raw commercial files go ONLY to the private
   game-reverse-engineering repo, never to public western-heart; these two
   inputs are a single extracted motion file already in the workspace and
   public repo JSONs.)
3. Run each job twice and keep both verification files:
   - `python3 vf5_decode_batch.py --mode gpu --input <mot_DUR.bin> --out-dir ./vf5-decode-out`
   - `python3 vf5_decode_batch.py --mode cpu --input <mot_DUR.bin> --out-dir ./vf5-cpu-out`
   - Same pair for `wwe_parse_batch.py --movesets-dir <dir>` and
     `suite_morph_batch.py` (add `--vertex-deltas <npy>` only when bake
     deltas exist; otherwise the vertex batch stays pending and the grid
     result stands on its own).
4. Compute speedup per job = CPU wall / GPU wall from the two
   JOB-VERIFICATION.txt files. Commit the outputs + verification files to
   the lane PR (or a follow-up PR) — never report a speedup without both
   numbers attached.
5. Local VM GPU state (measured this lane): `nvidia-smi` NOT installed,
   `torch` NOT installed. That is why these jobs are Kaggle jobs: the local
   VM cannot produce a GPU measurement, so none is claimed here.

## What the jobs do NOT claim
- VF5 stance identification: the job outputs a candidate SCREEN (smallest
  segC + fewest tracks). Stance = key-stream decode + loop/root-motion
  measurement, a follow-up step, not this job's output.
- WWE per-slot numeric IDs inside real .moveset files: not asserted anywhere
  in this pack; they come from a Data Editor dump on an owned install.
- Morph vertex batch without bake deltas: the grid runs; the vertex batch
  activates when `--vertex-deltas` is supplied. Baked MPFB shape keys remain
  the ground truth.

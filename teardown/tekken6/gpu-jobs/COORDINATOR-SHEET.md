# T6 GPU JOBS — COORDINATOR BROWSER DELEGATION (Lane D)
Notebook: https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit (Kaggle T4 x2; Colab as backup/overflow when Kaggle quota runs low — switch, never stop; Kaggle session stays open, jobs queue continuously).

## Jobs (run in order; each writes its *_results.json — that file is the proof)
1. `job1_idx_grid.py` — IDX parameter grid. Inputs: `DATA401.IDX` (26,028 bytes, encrypted).
   Expected: best combo keyset0/chunk=1024/t0=byte_off, tile_fails=0, last_end=187525.
2. `job2_bulk_census.py` — bulk census. Inputs: `bulk_decrypted.bin` (384,073,728 bytes) + `idx_decrypted_keysetA_chunk1024.bin`.
   CPU baseline (VM, 2026-10-24): 98.5s for the same census. Report measured speedup from `job2_results.json` only.
3. `job3_audio_split.py` — voice-bank split. Inputs: `bulk_decrypted.bin` + `voice_bank_inventory_v3.json`.
   Needs vgmstream for AT3 decode; if absent the job records `vgmstream_absent` per stream (never fakes a decode).

## Upload rules (PRIVATE handling — read before uploading)
- `bulk_decrypted.bin` is derived from an owned game. It goes to the notebook as a PRIVATE Kaggle dataset/upload only. It must NEVER be committed to the public western-heart repo or any public dataset.
- Safe to handle openly: `DATA401.IDX` (encrypted index), `t6_idx_solve.py`, census/inventory JSONs (offsets/sizes only, no audio bytes), the three job scripts.
- Each job prints `nvidia-smi` + `torch.cuda` proof at the top; copy those lines into the job's results report. No report may say "GPU not needed". If a job runs slower on GPU than its CPU baseline, report the measured ratio honestly.

## Measured CPU baselines (VM, 2026-10-24, for speedup math)
- IDX single-keyset verify: ~0.07s (single-call); 20-combo chunked grid: ~1.6s; full tiling verify: ~0.4s.
- Full 2,093-file census (magic + full-file entropy): 98.5s.
- Audio tag scan, first 256KB x 2,093 files: 3.1s.
- Local VM has NO GPU (no nvidia-smi, no torch) — that is why these run on Kaggle/Colab, not here.

## Separate browser delegations (NOT GPU jobs — parent handles)
- A. PS3 `TEKKEN.psarc` parts ad–aj (parts aa–ac already local, 1.27GB of ~5.5GB): download remaining parts, reassemble, verify sha256 `c98fb02602d58564ef4e80d386310cb3c48634566990a5050ef20ef2a4afd340` from the split manifest, then list PSARC filenames. Purpose: filename anchor for the 40 character voice-bank pairs (which pair is King). Parts aa–ac heads look random (no PSAR magic in first 64MB) — identify the container before trusting the reassembly.
- B. Owner ear-check of decoded candidate clips before ANY Pantera voice lock. No clip is King-attributed until then.

## What is NOT done (do not let the GPU report imply otherwise)
- King voice attribution: pairs are indexed 0–39 by entry/group only. No pair is claimed as King.
- GZIP-container second layer: 216 GZIP/GZIP+prefix16 files bulk-decrypt to a GZIP header whose zlib body fails decompression (Oct 15 finding, reconfirmed in census kinds). GPU job 2 re-measures this; it does not solve it by itself.
- Moveset/animation wiring + playing verification: still owed; needs file identification (motion = MOTA entry 0 + NTPP/NTXL families) plus the moveset/audio lanes' wire-in.

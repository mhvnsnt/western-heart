# Lane E GPU jobs — inputs, baselines, and coordinator delegations (2026-10-24)

Jobs in this directory (run in order E1, E2, E3; queue continuously):
- gpu-job-e1-ttt2-13.py — TTT2 13-file identification batch.
- gpu-job-e2-jun.py — Jun transcription batch + motion-readiness.
- gpu-job-e3-t3-banks.py — T3 bank verification + divmot15.

## Where to run (coordinator's browser lane)

- Primary: Kaggle notebook https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
  (T4 x2). Keep the session open; queue jobs continuously.
- Backup/overflow: Colab, when Kaggle quota runs low. Switch, never stop:
  if Kaggle stops, move the same scripts + inputs to Colab and continue
  the queue there; record which platform each job ran on.
- Every job run must record: nvidia-smi output, torch.cuda device info,
  input size/count, output file, wall time, and the CPU baseline below.
  Speedup = CPU baseline / GPU wall time, computed from the run's own
  numbers. Never report a speedup that was not measured on that run.

## CPU baselines (measured on this lane's VM, 2026-10-24)

- E1 files mode: 1.985 s for 2,957,312 bytes (3 passes: hash+entropy+
  strings 1.182 s, PNG carve 0.131 s, header/display-name dump 0.672 s).
- E1 manifest mode: 0.154 s end-to-end process median (6 runs: 0.179,
  0.128, 0.064, 0.094, 0.345, 0.405 s). Tiny workloads are
  startup-dominated; read a manifest-mode speedup as measured, not as
  a large claimed factor.
- E2 validation pass: 0.034 s for the 97-move check.
- E3 verification pass: 0.879 s for the 22-bank load + count + mapping.
- Run each job with --require-gpu on Kaggle/Colab so a CPU-only run
  fails fast instead of silently standing in for a GPU run.

## Inputs (what to upload where)

- E1 manifest mode (Kaggle-safe, default): ttt2-13-identification.json
  in this directory (header fields, display names, PNG offsets, SHAs
  only — no raw game binaries). Command: python3 gpu-job-e1-ttt2-13.py
  --mode manifest --manifest ttt2-13-identification.json --require-gpu
- E1 files mode (private-repo copy only, never western-heart):
  --mode files --input-dir <private extracted-small copy>.
  Raw STFS files stay in the PRIVATE game-reverse-engineering repo.
- E2: ttt2-jun-lp-rp-lk-rk.json (97-move transcription, from the Jun
  lane) + game/assets/movesets/megami.json from main (304 moves).
  Real clips converted: 0 — see delegation below.
- E3: a fresh main checkout's game/assets/anim/t3/ (22 bank dirs).
  Expected: 4,685 clips, divmot numbers 00–14, 16–20, heihachi the sole
  bank missing rows.pack.json.

## Delegation 1 — Jun motion (the only route that yields real clips)

Jun is NOT in Tekken 7 (story ghost only). Never pull her from T7.
TTT2 source only, via Kiloutre TekkenMovesetExtractor under CEMU
(Wii U emulator), per the extractor's own Tag2 instructions:
- Tool: https://github.com/Kiloutre/TekkenMovesetExtractor
- Steps: start TTT2 (Wii U Edition) in CEMU; find the game's base address
  with Cheat Engine (standing/crouching values 32770 / 32769, 4-byte big
  endian, or 41943040 / 25165824 regular); write cemu_base (and
  cemu_p1_addr, found once per Tag2 version) into game_addresses.txt;
  load Jun (practice or versus mode) and click Export.
- Deliver to the PRIVATE game-reverse-engineering repo (new TTT2 Jun
  dir, not western-heart directly): Jun moveset JSON (TTT2) + animation
  clips in movelist order, priority stance/guard first, then LP1/RP2/
  LK3/RK4 core strings, then Genjitsu (b+LP1+RP2) and Izumo (f+LP1+RP2)
  follow-ups, then the rest; plus a README naming game version/platform,
  tool used, and any clips that could NOT be extracted (gaps listed,
  not dropped).
- When that export lands, it becomes job E2's --clips input (BVH/.npz);
  run the same GPU conversion code on it with --require-gpu and wire the
  resulting animation IDs into Megami's 97 entries, replacing MADE specs
  where a decoded clip genuinely matches — never alongside them as if
  decoded. Note: the LukzB T7 Jun mod files were withdrawn by their
  author and are segregated; the T7-mod Rage Art (d/f+3+4) is NOT a TTT2
  move and must not enter Megami as TTT2 data.

## Delegation 2 — divmot15 re-rip (exact parameters)

- Target: divmot15.bin, 127,368 bytes, SHA-256
  5cead15fe33b1e88cf54cf25b2c773763a71f89cdd369b85b584110ec6acc57c,
  original Japan SLPS-01300 BNS records 194 / 198, LBA 10862 / 11000.
- Re-rip that record from a complete disc image, SHA-verify, then run
  the identical divmot bake pipeline as the other 21 banks. Do NOT bake
  the data found at sector 17534 on the owner's disc as Mokujin — that
  sector holds Gun Jack data on that image.
- Separate, do not conflate: heihachi rows.pack.json is baked ONLY from
  a divmot13 source, never by copying heihachi_on_jin rows.

## What is NOT done by these jobs

- Play verification (fight played on the live build, phone portrait) —
  owed by the deploy lane after merge; this lane has no live browser.
- Jun playable with decoded motion — blocked on Delegation 1.
- divmot15 bank — blocked on Delegation 2.
- These jobs do not claim the 70x figure or any speedup until a GPU run
  measures it. The blanket GPU order's jobs are queued here; their
  measured results replace these baselines when they land.

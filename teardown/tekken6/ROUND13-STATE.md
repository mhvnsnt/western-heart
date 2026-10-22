# Tekken 6 PSP — ROUND 13 STATE

Branch: `teardown/tekken6-round13-renderer-batches` stacked on PR #550
(`teardown/tekken6-round12-caller-textureroot` @ 2dfbd1e6).
Started: 2026-10-22.

## Jobs

1. **NTPP PIXELS — tk renderer hop** — IN PROGRESS.
   Locate `tk` sprite/texture renderer from the RTTI neighbourhood of
   `tk::sprite::fade::CMainTcb_t` + code-scan for GE texture-command
   immediates (0xC0-0xE9 family) in the EBOOT; read upload function(s)
   with Capstone; extract pixel contract; decode ONE NTPP section with
   only code-derived parameters; render + view. If proven: batch
   character-paired NTPP -> textured character GLBs + stage idx24's
   40 NTPP sections. If noise: land renderer read + exact residual,
   one hop only, then stop.
   Palette: DO NOT re-hunt (round 12 terminal, capture-only).

2. **STAGE GEOMETRY BATCH** — NOT STARTED.
   Decode every NDPP section in the 16 stage/object packages (all
   slots) from the r10 inventory with `tools/r9_ndpp_decode.py` into
   stage GLBs; per-package inventory; one stage GLB rendered + viewed.

3. **SLICE-PARTS BATCH** — NOT STARTED.
   Decode NDPP sections of all A-slice part packages (3,002 boned +
   436 rigid per r10 census) per B3 segment under
   `models/parts/seg{NN}/`; batch manifest JSON; failures reported
   per package with reason, never silently skipped.
   VOLUME RULE (declared early): disk is tight (~13 GB free at start);
   if GLB total exceeds ~150 MB, ship GLBs as a GitHub RELEASE
   (100 MB parts + sha256 manifest in git) and keep only manifest +
   inventory in-tree. Decision will be recorded here before the batch
   runs to completion.

4. **COM B4 — BINARY COMMAND ENCODING** — NOT STARTED.
   From round-7 moveset JSONs + COM bytes: (a) census 4x20B tail
   records (108) per-position; (b) classify 32-slot pointer-table
   targets; (c) test encoding hypotheses against the 7,341 name
   records; revisit count-word "176". Proven only when a command
   record decodes to a named move + Tekken-input notation via a rule
   reproducing on >=2 files.

5. **STATE / WIRING** — this file kept current per job;
   WIRING-INVENTORY gate lines updated honestly (G3 texture portion
   only when textured GLBs pass gates; G6 stage portion when stage
   GLBs land).

## Method notes
- Capstone targeted disassembly is the asm route (accepted deviation,
  rounds 11-12); NO full Ghidra analysis (VM RAM low).
- Bulk / decoded outputs in `~/workspace/_t6r4-work/` are read-only
  inputs (CLEAN bulk + decode_all76 outputs).
- Skeletons: ONLY the r11 set (`models/idx{nn}_*_r11.glb`); r9/r10
  skeletons are superseded (`models/SKELETON-SUPERSEDE.md`).
- Additions-only; no `git add -A`; per-job commits.
- Blender: `xvfb-run -a env -u PYTHONPATH ~/workspace/tools/blender/blender-4.0.2-linux-x64/blender`, Cycles CPU, unique filename per render.

## Deletions
None.

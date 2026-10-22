# Tekken 6 PSP — ROUND 10 STATE (palette → skinned GLBs; full-section batch; NTPP pixels; census; stage layout)

Date: 2026-10-22. Branch: `teardown/tekken6-round10-palette-batch`,
stacked on `teardown/tekken6-round9-ndpp-unpack` @ 22de309 (PR #515 OPEN).
Workdir retained: `~/workspace/_t6r4-work/` (3.2GB, NEVER delete).
Clone reused: `~/workspace/_t6r9-clone` (46M sparse, teardown/tekken6 only).
Disk tight (~98% used, ~2.7G free): minimal footprint, no new bulk copies.

## Inherited verified truth (rounds 5–9, not re-derived)

- Containers 76/76 adler-exact; bulk per-1024B cipher
  (`tools/bulk_decrypt.py`); census: 5,470 containers = 3,702 A-model /
  1,432 B-texture / 336 dir-other.
- 12 CHARACTER packages (indices 00,01,04,05,08,09,12,13,16,17,20,21),
  16 stage/object packages, 29 NTPP texture packages. Movesets 18/18
  JSONs landed (round 7).
- NDPP DECODE CRACKED (round 9, PR #515): NDPP sections are embedded
  PSP GE display lists. Unit = 20B header (cmd 0x14 ORIGIN, 0x10
  REGION1, 0x12 VTYPE + 2 unresolved words = header words 3–4) +
  strip table (VADDR 0x01+offset; PRIM 0x04: bits 16–18 prim type
  4=strip/3=list, low16 = vertex count) + terminator 0x13/0x0B +
  vertex stream. VTYPE: bits 0–1 UV fmt, 5–6 normal, 7–8 position,
  9–10 weight fmt, bits 14–16 = weight count−1. Decoder:
  `tools/r9_ndpp_decode.py`. Shipped: 24 unskinned GLBs
  `models/idx{12 pkgs}_slot{0,10}_r9.glb`.
- BONE ROLES PROVEN (round 9 Job 2): parents u32×N (−1 root) /
  local translations f3×N / local Eulers f3×N (R = Rz·Ry·Rx) /
  scales f3×N / 32B name table. Skeletons:
  `models/idx00_skeleton_r9.glb` (110 bones),
  `models/idx04_skeleton_r9.glb` (146 bones). Body BONE file =
  8,032B (146 bones), head BONE = 1,664B (22 bones, constant).
- NTPP: interior mapped byte-exact on idx02 (+16 = first-block
  size; two GIDX blocks @+80/+3232, format words 0x10400612 /
  0x10400610); pixel format NOT proven. NTPP-class methods:
  FUN_0892f99c / FUN_0892fac0 / FUN_0892f6c4 / FUN_08930440 /
  FUN_089304a4; NTPP ctor FUN_0892fdf0.
- Ghidra full analysis OOM-killed on this 8GB VM (round 9).
  Round 10 uses capped-heap targeted passes only (-Xmx2g..3g,
  named functions) or Capstone targeted disassembly.

## Jobs

1. JOB 1 — BONE PALETTE (unit header words 3–4). Routes in order:
   (a) targeted capped-heap Ghidra/Capstone read of the GE-list
   submit path (ctor FUN_0886fe88 / vtable 0x08b918b8 context);
   (b) DATA test on 1-weight units vs BONE arrays (bone counts
   110/146/22 bound plausible ranges); (c) cross-unit statistics
   (head vs body sections). PROOF: palette rule puts every
   vertex's weights on bones whose bind positions are near that
   vertex (skinning coherence) → SKINNED GLBs for the 12
   character packages, gated by skeleton-inside-mesh overlay
   render VIEWED + bind-pose reproduces T-pose. No guessed
   skinning if it resists.
2. JOB 2 — FULL-SECTION BATCH: enumerate the FULL slot map of
   each of the 12 character packages; decode EVERY NDPP section
   with `tools/r9_ndpp_decode.py` (per-character isolation).
   GLBs under `models/` (r9 naming extended by slot) +
   per-package section inventory. Also decode the 16
   stage/object packages' 624B transform-node NDPP units.
3. JOB 3 — NTPP PIXELS: pin pixel format from format words
   0x10400612/0x10400610 + GIDX structure via targeted reads of
   the NTPP-class methods; decode idx02 blocks; PROVE with a
   viewed render. Then decode proven character pairings only →
   TEXTURED character GLBs (embedded images; textured front
   render VIEWED side-by-side vs untextured r9 GLB).
4. JOB 4 — B3 CENSUS: attribute remaining A-model packages
   beyond the 12 characters + 16 stage/object from r7 census +
   slot maps + name chunks (kao_/MODEL_HEAD). Census JSON +
   doc update; unknowns stay unknown with evidence.
5. JOB 5 — B5 STAGE SLOT-9 (idx24): push layout one level:
   record structure from BE offset table (sizes from consecutive
   offsets), decode a first record class; stage GLB if
   geometry-bearing (viewed render), else layout map + exact
   residual.
6. STATE: this file current per job; WIRING-INVENTORY / status
   gate lines updated honestly (G3 full only when the
   skinned+textured batch passes its gates).

## Results

- BOOTSTRAP: branch created from 22de309 (PR #515 head), this
  file is the first commit. Analysis follows.
- JOB 1: PENDING.
- JOB 2: PENDING.
- JOB 3: PENDING.
- JOB 4: PENDING.
- JOB 5: PENDING.

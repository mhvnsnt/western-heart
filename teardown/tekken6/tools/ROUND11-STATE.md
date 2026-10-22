# Tekken 6 PSP — ROUND 11 STATE (palette draw-code xref; idx00 skeleton discrepancy; NTPP class methods; B3 assignment via DATA401 order; B5 page records)

Date: 2026-10-22. Branch: `teardown/tekken6-round11-palette-xref`,
stacked on `teardown/tekken6-round10-palette-batch` @ 690f12f (PR #520 OPEN).
Workdir retained: `~/workspace/_t6r4-work/` (read-only this round; NEVER delete).
Clone reused: `~/workspace/_t6r9-clone` (sparse, teardown/tekken6 only).
Disk tight (~91% used): minimal footprint, scratch in clone workdir, no bulk copies.

## Inherited verified truth (rounds 5–10, not re-derived)

- Containers 76/76 adler-exact; census 5,470 (3,702 A / 1,432 B / 336 other).
  12 character packages (idx 00,01,04,05,08,09,12,13,16,17,20,21) hold
  EXACTLY slots 0+10 NDPP — the 24 r9 GLBs are the complete mesh set,
  re-decoded clean round 10. Movesets 18/18 JSONs (round 7); COM files
  idx58–75 named LAW..ZAFINA via the @624 string.
- NDPP = embedded GE display lists; VTYPE is the vertex contract;
  decoder `tools/r9_ndpp_decode.py`. BONE roles PROVEN (parents u32 /
  translations f3 / Eulers f3 Rz·Ry·Rx / scales f3 / 32B names).
  24 skeleton GLBs shipped round 10 (`tools/r10_batch.py`): body
  110 bones (idx04: 146) + head 22 per package.
- PALETTE (round 10, PR #520, `round10-evidence/JOB1-PALETTE-VERDICT.md`):
  header words 3–4 = GE USCALE/VSCALE (proven, NOT bones); NOTHING
  file-side carries a palette (bbox prefix blocks, BONE small section =
  char dims, slot 6 = 5-entry table, vertex streams = weights only — all
  excluded with proof). RAM ground truth (round-5 PPSSPP attract dump):
  the engine builds single-bone GE fragments at runtime (12× 0x2B matrix
  words + 0x0B, 52B stride, 520+ fragments) and CALLs them in palette
  order per frame. Palette = runtime/code product.
- NTPP (round 10): the GIDX word 0x1040xxxx = chunk tag 0x1040 + SERIAL
  (proven — not a format). idx02 slot-4 payload (70,880B) = directory of
  (0x10, offset, 0x460) records → 1,120B items (pixel candidates,
  UNTESTED). 16 data-side decode variants of block 1 = all noise (do not
  repeat). NTPP-class methods in the EBOOT: FUN_0892f99c / FUN_0892fac0 /
  FUN_0892f6c4 / FUN_08930440 / FUN_089304a4; ctor FUN_0892fdf0.
- B3 (round 10): structural census complete (28 full-char pattern /
  3,002 boned part / 436 rigid / 236 stage-object in the A slice);
  per-character ASSIGNMENT unproven — needs DATA401 index-order analysis.
- B5 (rounds 8–10): stage idx24 slot-9 = BE directory of 0x20B records +
  40× (0x8a0, offset) page pairs stepping exactly 0x8a0 from 0x9f0,
  tiling to EOF + embedded NTPP @+0x1c0; payload 95% BE-float-sane.
- Ghidra: FULL auto-analysis OOM-kills on this 8GB VM. Capped-heap
  (-Xmx2g..3g) TARGETED passes only (named functions) or Capstone.
  Ghidra 12.1.4 at ~/workspace/tools/ghidra/ghidra_12.1.4_PUBLIC/;
  JAVA_HOME=/home/hatch/workspace/tools/ghidra/jdk-21.0.12.1+1.

## Jobs

1. JOB 1 — PALETTE EBOOT DRAW-CODE XREF (route 1): find the code that
   emits the runtime GE fragments (anchors: model-class vtable
   0x08b918b8, ctor FUN_0886fe88, code writing 0x2B000000-pattern
   immediates, display-list submission path). Targeted capped-heap
   Ghidra decompile or Capstone of the emitting function + callers.
   GOAL: rule mapping unit → bone matrix. PROOF if found: apply to one
   package (idx00/idx01), build SKINNED GLB, pass coherence gate
   (bind-pose reproduction + skeleton-inside-mesh overlay VIEWED),
   then batch all 12. If builder found but mapping ambiguous: land
   decompile + exact ambiguity. ALSO route 3 cheaply: cross-read COM
   moveset 32-slot pointer tables + part-package census for
   per-character part references. Route 2 (live PPSSPP GE capture):
   feasibility note only, no interactive session.
2. JOB 2 — idx00 SKELETON DISCREPANCY: round 10 flagged idx00's composed
   ATAMA/TE values (−969.6) differing from round-9 spot values (−800.8)
   while idx01/05/08 land on round numbers, + finger chains extending
   past the slot-10 mesh arm span. Recompose idx00 with BOTH composers,
   diff bone-by-bone, determine from BONE file bytes which is correct
   (different scale row? second skeleton variant? finger chain dropped /
   mis-parented?). Verdict + corrected skeleton GLB if a composer was
   wrong; if both right under different conventions, state the
   difference exactly + which one shipped GLBs use.
3. JOB 3 — NTPP CLASS METHODS + ONE ITEM: (a) targeted decompile /
   Capstone of the five named NTPP methods; extract pixel-path facts
   (what the 1,120B slot-4 items are; swizzle/CLUT/format constants).
   (b) decode ONE slot-4 0x460 item using ONLY code-derived parameters;
   render + VIEW: coherent = format proven → decode idx02 fully +
   proven character-paired NTPP packages → TEXTURED character GLBs
   (embedded images; textured front render VIEWED side-by-side vs r9
   untextured GLB). Noise = land decompile evidence + item statistics +
   exact residual. No blind variant sweeps.
4. JOB 4 — B3 ASSIGNMENT VIA DATA401 INDEX ORDER: correlate bulk
   container order with the game's own ordering evidence: the 12 known
   character packages' bulk positions, COM positions (idx58–75) + @624
   names (LAW..ZAFINA), any DATA401 index/table from PR #187-era work.
   TEST (not assume) the contiguity hypothesis: slice packages between
   two known character anchors belong to the preceding character.
   Score plausibility (part counts/sizes per character). Assignment
   JSON with per-package confidence (anchor-proven /
   contiguity-inferred / unassigned); INFERRED stays labeled inferred,
   census doc ONLY, never per-character model dirs.
5. JOB 5 — B5 PAGE RECORDS: idx24 slot-9 pages are 0x8a0 = 2,208B of
   BE-float-sane data. Arithmetic record hypotheses first (2,208/12 =
   184 f3, /24 = 92, /32 = 69, /48 = 46). Leading hypothesis (BE f3
   position stream, possibly interleaved normal/uv): extract page 0
   positions, render point cloud / triangle-soup PNG, VIEW it —
   coherent surface = geometry proven → assemble stage GLB from all
   40 pages (viewed arena render). Gibberish = page statistics + next
   discriminator. Every tested stride gets a one-line verdict.
6. STATE: this file current per job; WIRING-INVENTORY gate lines
   updated honestly (G3 full only when skinned (+textured) GLBs pass
   gates).

## Results

- BOOTSTRAP: branch created from 690f12f (PR #520 head), this file
  committed + PR opened before analysis.
- JOB 1: pending.
- JOB 2: pending.
- JOB 3: pending.
- JOB 4: pending.
- JOB 5: pending.

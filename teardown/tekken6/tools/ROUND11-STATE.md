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
  committed + PR #536 opened before analysis (96de961).
- JOB 1 (PALETTE XREF) — BUILDER PROVEN, mapping ambiguous, no
  skinned GLBs: the GE fragment emitter is FUN at 0x08ad161c —
  emit(obj, out, index): reads a 3×4 float matrix from
  obj->[0] + index*48, converts each float to GE imm24, writes
  12× 0x2B + 0x0B = 52 B (byte-exact vs the RAM fragments).
  RAM pool = exactly 110 fragments (one 110-bone set). The
  emitter takes the bone index as an argument and has NO jal /
  data xref in the EBOOT (jalr/vtable-called) — the per-unit
  index rule lives in the unidentified caller; two candidate
  sources stated exactly (unit ordinal vs per-part index).
  Route 3 run, negative (no bone table in COM/census). Route 2
  feasibility note landed. Evidence:
  `round11-evidence/JOB1-PALETTE-XREF.md` +
  `round11-evidence/dis/dis_08ad161c_emitter.txt`.
- JOB 2 (idx00 DISCREPANCY) — VERDICT LANDED: composition
  convention difference. Round-9 spot values (T·R chain, BONE
  scales NOT propagated into descendant translations) are the
  correct bind pose — recomposing idx00 both ways reproduces
  both rounds' numbers to 0.1; TRS puts ASHI_R at y=−9.7
  (mesh floor −0.7) and fingers 30% past the mesh span, TR is
  in-mesh on every check (overlay VIEWED). idx00 unique: all
  110 bones scale 1.04 = header f32. 24 CORRECTED skeleton
  GLBs shipped (`models/idx{nn}_*_r11.glb`): standard glTF
  walk reproduces the TR bind pose to ≤0.02 units on all 24
  (r10-shipped walks err up to 597.3). Evidence:
  `round11-evidence/JOB2-IDX00-SKELETON-VERDICT.md`,
  tool `tools/r11_skeleton_fix.py`.
- JOB 3 (NTPP) — CLASS FULLY READ, NO PIXEL PATH: the five
  named methods + ctor are the complete NTPP class (vtable
  0x08b9c568; RTTI record at 0x08b9c5b0 names it "NTPP") — a
  texture placement/animation object (defaults +0x98=1,
  +0x9c=110.0f; flag/state/float bookkeeping). NO byte loops,
  swizzle, CLUT, or GE texture commands in any of the six
  functions → no code-derived pixel parameters exist, so the
  one-item decode cannot be run as specified and no blind
  sweep was substituted. Slot-4 items = embedded NTPP
  sections (item stats: entropy 5.51, 9.9% zeros). Residual:
  pixel consumer = datatextureroot / render layer. Evidence:
  `round11-evidence/JOB3-NTPP-CLASS-VERDICT.md` + `dis/`.
- JOB 4 (B3 ASSIGNMENT) — LANDED with confidence labels:
  contiguity hypothesis scored STRONG (A/B interleave 28/28;
  21/28 segments near-identical kits; 12+28 = 40 full-char
  packages). Labels: 28 anchor-proven / 5,206
  contiguity-inferred / 236 unassigned (all stage-pattern).
  Anomalies kept (5 double segments, stub seg 26, seg-27
  stage cluster). No fighter names claimed; inferred stays in
  the census evidence only. Deliverable:
  `round11-evidence/r11_b3_assignment.json` +
  `round11-evidence/JOB4-B3-ASSIGNMENT.md`.
- JOB 5 (B5 PAGES) — GEOMETRY REJECTED, format narrowed:
  inherited "95% BE-float-sane" premise corrected (denormal
  artifact; pages are 80.5% zero bytes). BE f3/f6/f8/f4, LE
  float, byte-image, and GE-list hypotheses all REJECTED with
  one-line verdicts + VIEWED page images. Measured positive:
  pages are sparse byte-record arrays with a 16 B / 32 B
  record period (autocorrelation r=0.763 @16), constant
  0x800 word at page offset 52, small-enum byte alphabet.
  No stage GLB. Evidence:
  `round11-evidence/JOB5-B5-PAGES-VERDICT.md`.

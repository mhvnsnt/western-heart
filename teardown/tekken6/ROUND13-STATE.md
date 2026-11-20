# Tekken 6 PSP — ROUND 13 STATE

Branch: `teardown/tekken6-round13-renderer-batches` stacked on PR #550
(`teardown/tekken6-round12-caller-textureroot` @ 2dfbd1e6).
Started: 2026-10-22. All jobs landed 2026-10-22.

## Jobs

1. **NTPP PIXELS — tk renderer hop** — DONE (renderer READ; pixel
   decode NOT proven — stopped at the named residual, one hop only).
   The tk renderer was located by both briefed routes (RTTI
   neighbourhood of `tk::sprite::fade::CMainTcb_t`; GE
   texture-command immediate scan — the brief's 0xC6/0xC7 naming was
   corrected: TBP0-7 = 0xA0–0xA7, TBW = 0xA8–0xAF, TPSM 0xC3,
   TMODE 0xC2, TFLT 0xC6, TWRAP 0xC7). The shared image-descriptor
   contract is PROVEN from the builders: +0x08 u16 format word (low
   nibble = GE TPSM enum 0=5650…4=T4, 5=T8…; bit 7 = swizzled),
   +0x0a u16 width, +0x0c u16 height, +0x28 pixel pointer; CLUT
   travels as a separate pointer on the same resource object
   (obj+8), CLUT format = the descriptor format word itself
   (CMODE/CBP/CLOAD builders at 0x08acce14/0x08acce50; texture bind
   builder at 0x08acd030). RESIDUAL: no function in the three hops
   read (NTPP class → datatextureroot → tk builders) populates that
   descriptor from NTPP section bytes — per-section field values are
   not code-derived, and guessing them from header bytes was refused
   (several mutually inconsistent readings fit). No decode run, no
   textured GLBs. One hop further named, then stopped: the
   archive-loader-side descriptor factory that instantiates NTPP/GIDX
   resource objects; alternative = live GE capture.
   Doc: `tools/round13-evidence/JOB1-TK-RENDERER-VERDICT.md` +
   Capstone reads in `tools/round13-evidence/dis/`.
   Palette: not re-hunted (round 12 terminal, capture-only).

2. **STAGE GEOMETRY BATCH** — DONE (batch run over all slots of all
   16 packages + the 236 slice stage-pattern twins; **0 arena
   GLBs** — structural verdict). The only NDPP section in any stage
   package is slot 0 (624 B), the proven transform node; the decoder
   fails it identically 16/16 (spurious tail unit, bad VTYPE 0x11d,
   no vertex payload). Slice twins: 235/236 fail identically; the
   single decodable stage-class section in the whole sweep (bulk
   3640 slot 0, 4 verts / 2 tris) shipped at
   `stages/slice/unassigned/bulk3640_slot0_r13.glb` and its gate
   render was VIEWED: one flat 2×2 quad — a ground-plane card, not
   an arena. Stage packages are placement + texture containers;
   NDPP geometry lives in character/part packages. No textured
   idx24 variant (depends on Job 1's residual).
   Docs: `tools/round13-evidence/JOB2-STAGE-VERDICT.md`,
   `tools/round13-evidence/r13_stage_inventory.json`,
   `tools/round13-evidence/r13_stage_slice_manifest.json`,
   gate render `tools/round13-evidence/r13_gate_stage_bulk3640_quad.png`.

3. **SLICE-PARTS BATCH** — DONE. 3,438 part packages (3,002 boned +
   436 rigid) → **3,039 GLBs in-tree** under `models/parts/seg{NN}/`
   (2,005,929 verts / 1,211,043 tris / 65,388,452 bytes — under the
   ~150 MB rule, no release). 405 failures, all reported per package
   with reason: 400 = VTYPE color-format 7 (`0x*33d` family) layout
   unproven in the r9 decoder (stride measured 20/24 B and the
   layout hypothesis tested, but it did NOT validate against the
   descriptor bbox — not guessed, named residual), 4 = `KeyError:
   'pos'`, 1 = truncated buffer. Decode is deterministic: two runs,
   3,039/3,039 sha256-identical. Gate render VIEWED: seg00
   bulk0086 = coherent female torso costume part (corset, arms,
   hands) — `tools/round13-evidence/r13_gate_part_bulk0086_front.png`.
   Segment assignment stays labeled contiguity-INFERRED; nothing
   merged into the 12 proven character packages.
   Manifest: `tools/round13-evidence/r13_parts_manifest.json`;
   doc: `tools/round13-evidence/JOB3-PARTS-BATCH.md`.

4. **COM B4 — BINARY COMMAND ENCODING** — DONE (partial; encoding
   NOT proven, primary hypothesis falsified). (a) The 4×20B tail
   records: all 72 byte-identical empty MOTA stub headers
   (`MOTA`, ver 1, size 20, 0, 256) — placeholders, not commands;
   tail closed. (b) All 31 pointer-table slots classified across 18
   files (size/entropy/zero-fraction/first-bytes). (c) No slot in
   any file satisfies word_a == name count or len/stride == name
   count (strides 8–64) — the fixed-stride name-indexed command
   list does not exist in the pointer-table sections. The input
   notation demonstrably lives inside the per-move name records as
   game-font PUA glyphs (U+E000–U+E02x; U+E018 ×6,162 etc.).
   Residual hops named (not chained): the font glyph→button map;
   the high-entropy slots 25/26/30 (compression probes).
   (d) Count-word "176" (per-file 7–16, sum 176): matches nothing in
   the files' own censuses (r ≈ −0.1 vs names/size/strings);
   bounded hypothesis: an external structural count (DATA401-level
   or a move-category table), NOT a moveset-size measure.
   Doc: `tools/round13-evidence/JOB4-COM-B4-VERDICT.md`; data:
   `tools/round13-evidence/r13_com_census.json`.

5. **STATE / WIRING** — this file; WIRING-INVENTORY round-13 section
   appended. G3 texture portion NOT crossed (no textured GLBs —
   Job 1 residual); G6 stage portion NOT crossed (no stage GLBs —
   Job 2 structural verdict). G3 mesh portion advanced by Job 3's
   3,039 proven part GLBs.

## Method notes
- Capstone targeted disassembly is the asm route (accepted deviation,
  rounds 11-12); NO full Ghidra analysis (VM RAM low).
- Bulk / decoded outputs in `~/workspace/_t6r4-work/` are read-only
  inputs (CLEAN bulk + decode_all76 outputs).
- Skeletons: ONLY the r11 set (`models/idx{nn}_*_r11.glb`); r9/r10
  skeletons are superseded (`models/SKELETON-SUPERSEDE.md`).
- Additions-only; no `git add -A`; per-job commits.
- Blender: `xvfb-run -a env -u PYTHONPATH ~/workspace/tools/blender/blender-4.0.2-linux-x64/blender`, Cycles CPU, unique filename per render.
- Note: `/tmp` on this VM is a volatile 512 MB tmpfs that reset
  mid-round; the parts batch was re-run into the repo tree and
  verified sha256-identical to the first run's manifest.

## Deletions
None.

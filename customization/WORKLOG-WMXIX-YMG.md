# WORKLOG — WMXIX YOBJ→GLB geometry conversion (Creation Suite gap-fill JOB 3, 2026-10-20)

Owner instruction (verbatim): "get the Def Jam converter done all the 22k
parts the WM 19 texture batch decode the Tekken 6 item table search and
the assigned catalog that's missing on main get all of that handled"

## Outcome (honest summary)

**Zero GLBs shipped.** The YOBJ geometry decode was built, gated, and
run over all 998 blocked parts; the sample renders AND a second
gate-passing sample set both failed own-eyes validation in Blender
(Workbench renders viewed by the converting agent): the decoded
triangle strips are internally coherent surface fragments, but they do
not assemble into the part — the per-strip-group placement transform is
still unsolved (the same open problem that blocks skinned wrestler
assembly). Per the repo's no-faked-progress rule and Worker A's
"no fake GLBs" precedent, fragment GLBs were revoked rather than
cataloged as parts. CATALOG.json statuses are unchanged (correctly
`blocked_ymg_decode`), now backed by a complete per-file evidence log.

## What was built

- `customization/tools/convert_wmxix_ymg.py` — deterministic converter /
  research instrument (pure python3 + numpy, no Blender in the loop):
  YOBJ parser, strip-pool decoder, numeric validation gate (incl.
  welded-connectivity), GLB writer, resumable batch, CATALOG stamper,
  report writer. Subcommands: `list | convert | catalog | report`.
- `customization/parts-converted/wmxix-conversion-log.jsonl` — one
  record per .ymg file (1,200): status + precise failure reason +
  decode metrics for every blocked file.
- `customization/parts-converted/wmxix-conversion-report.json` — run
  summary (regenerable via the tool's `report` subcommand).
- `packages/creation-suite/test/catalogs.test.js` — new test:
  "wmxix ymg parts stay honestly geometry-pending (J3 eye-validation)".

## Format facts (measured this session; sources in teardown docs)

- YOBJ header (BE u32): [0x08] version, [0x14] skeleton offset, [0x38]
  GCTC offset, [0x5C] Table1 offset, [0x60] skin-batch table offset.
- Positions: one s16x3 BE strip-ordered pool starting right after the
  skin-batch descriptor table (header record + batch records +
  count-byte-0 terminator, 8-byte records), ending at the GCTC offset,
  scale /64. Ground truth reproduced exactly: Elbow me0_000/l0.ymg →
  145 position verts / 14 strips / 113 tris (teardown doc's "148"
  included 3 GCTC-header words past the pool end).
- Strip split: consecutive-step > max(400, 4× median step)
  (tools/yobj_strips.py lineage). Individual strips are well-formed
  zigzag ribbons (measured: two smooth rails, healthy triangle areas,
  per-strip PCA thin-axis ≈ 0).
- Skin-batch table records are 8 bytes [u8 bone][u8 count][u16 count]
  [u32 offset]; for CAW parts there is effectively ONE batch — the
  table does NOT segment the pool into the visible strip groups.
- Table1 payloads are (u16, 0) pairs; the following record region's
  (u16, u16) payloads ARE UV-scale values (12-bit /4096 fractions,
  measured on faces/man/Face/mf0_001) — but a proven per-vertex UV
  mapping does not exist yet, so no texture was bound (textures remain
  separate converted catalog parts from Worker A).

## Batch results (tool output, 1,200 files evaluated in 4 chunks)

| YOBJ version | files | fragmented_assembly | pool_steps_incoherent | eye_validation_failed | long_edge_tris |
|---|---|---|---|---|---|
| 0x00030001 | 754 | 445 | 225 | 77 | 7 |
| 0x00030002 | 3 | 0 | 3 | 0 | 0 |
| 0x00040001 | 175 | 119 | 56 | 0 | 0 |
| 0x00040002 | 32 | 0 | 32 | 0 | 0 |
| 0x00040003 | 31 | 0 | 31 | 0 | 0 |
| 0x00040004 | 2 | 0 | 2 | 0 | 0 |
| tiny (<0x80 B) | 1 | — not_yobj_or_tiny — | | | |
| DUMY | 202 | blocked_dumy_placeholder (no geometry by design, untouched) | | | |

Reason key: `fragmented_assembly` = pool decodes smoothly but welded
mesh splits into many components (< 75% of triangles in the largest —
measured range across samples: 7–44 components, largest 14–68%);
`pool_steps_incoherent` = < 85% of consecutive steps ≤ 700 raw units
(embedded non-position segments in the pool window; ALL v0x40002+ files
land here); `eye_validation_failed` = passed every numeric gate,
converted, then REVOKED after Blender renders showed crossing-fan
fragments (6 class samples viewed: upper_body r1/l1, gloves r2,
wrist r1, gears g0, lower_body l3 — none read as a part; two files of
different categories rendered pixel-identically, a further sign the
pool read is not the part assembly); `long_edge_tris` = > 5% of
triangles span more than the split threshold.

## Eye-validation evidence (viewed 2026-10-20 by the converting agent)

- 10-file sample across versions/categories (elbow r0, wrist l1, face
  mi0_000/mi0_001, gear g0, glove l2, hair c0, lower l3, shoe c8,
  upper c5): all rendered as disconnected shards in Blender Workbench —
  FAIL.
- 6-file sample of the 77 numeric-gate passes: also fragments — FAIL,
  all 77 GLBs deleted and their log records superseded (see the log's
  `eye_validation_failed` entries; deletions logged in
  ~/workspace/agent-ops/disk-cleanup-log.md per the storing/moving law —
  they were this lane's own uncommitted output).

## Runtime verification

- `python3 customization/build_suite_catalog.py` regenerates
  `customization/creation-suite-ui/data/parts-catalog.json` with
  IDENTICAL parts: total 4,523 entries, unchanged (registry 1,148 +
  parts-converted 3,372 + hair 1 + brows 2); parts-converted geometry
  GLBs remain 303 (No Mercy). No runtime totals changed — correctly,
  since no geometry converted.
- Tests (by filename; directory mode is broken on this VM):
  `node --test test/catalogs.test.js` → 6/6 pass (incl. the new test);
  `node --test test/dna.test.js` → 4/4 pass.

## The remaining blocker — precise statement + next-step path

The pool's strips are real surface patches in *some* local frames; the
transform placing each strip group into the part frame is not in any
doc in either teardown repo, and three prior efforts (2026-10-15 skin
"solution" — disproven by re-render; 2026-10-17 assembly — artifacts
absent from the repo; Worker A) stopped at the same wall. Evidence
gathered here narrows the search:

1. The runtime (main.dol, YOBJ-DOL-DECODER-REPORT.md) builds 0x20-stride
   ring records (pos@+0, normal@+0x14, uv@+0x1C) — the FILE pool is
   therefore probably NOT a pure position stream end-to-end; the
   "incoherent" classes likely interleave fields the ring builder
   deinterleaves. Re-deriving the file→ring transform from the DOL
   disassembly (Ghidra) is the highest-value next step.
2. Batch descriptor semantics are still unisolated (three parsers in
   the repos give three different record readings of the same table).
   A controlled experiment: corrupt one field at a time in a copy of a
   part file and diff the runtime/GX-facing records — needs the game
   running (Dolphin) or a full DOL trace.
3. Table2 (u16,u16) payloads are UV-scale; if their run structure maps
   1:1 to strip groups, they may carry the group segmentation the batch
   table doesn't.

Until one of those lands, `blocked_ymg_decode` is the honest status,
and this tool + log are the standing census: when the transform is
cracked, the same tool converts and stamps the catalog in one run
(gate first, eye validation per class, then `catalog`).

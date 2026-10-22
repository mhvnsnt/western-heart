# Soulcalibur II (Xbox) — Stages (Phase 13, JOB 3)

All v404 stage VMXs assembled into textured GLBs in `stages/`
(textures embedded via the same part → rec80 material → VXT record
chain as the fighters, `VXT-FORMAT.md`). Tool: `tools/build_stage.py`.

## Method

- Stage part layout per GRE PR #28 (per-part vertex stream at
  part+0x14, end at part+0x24, stride 40 B: pos, normal, RGBA color,
  UV; u16 index stream at part+0x10, count at part+0x04). Positions
  are world-space — no node transform applied (the phase-2 m003
  floor-plan verification used the raw positions, and the assembled
  m003 render below is coherent in place).
- Face topology was NOT resolved upstream for stages. Per part, this
  lane measured triangle-strip vs triangle-list by the phase-3 parity
  method (agreement between geometric face normals and authored
  vertex normals) and shipped the winner per part; the split is
  recorded per stage below. No topology ships unmeasured.
- Cross-check: the assembled m003 totals **35,390 verts — exactly the
  phase-2 own-eyes-verified vertex count** for this stage.

## Proof (viewed by the lane)

- `phase13-proof/stage-m003-arena.png` — ground-level view inside
  m003: marble temple architecture, arches, lattice gate, gold
  candlesticks, veined marble textures, water in the foreground.
  Coherent, correctly textured, correctly joined.
- `phase13-proof/stage-m003-plan.png` — top-down plan of the whole
  environment (temple, surrounding water, snow-capped mountain
  backdrop) matching the spatial layout of the phase-2 position plots
  (`plot_m003.png`, GRE phase 2).
- `phase13-proof/stage-m003-front.png` — first framing attempt
  (whole-environment bbox); kept as the framing record.

## Inventory — 41 stage files in v404

Names: the VMX bytes carry no stage names, so files are inventoried
by their v404 entry index (m000…m120, stride 3 in the archive's
MED/SMALL/BIG triples). Stage identity by content is visible in the
GLBs/renders; no names are invented.

| File | Verts | Tris | Parts | Embedded images | Topology strip/list |
|---|---|---|---|---|---|
| m000 | ERROR | | | | |
| m003 | 35390 | 26198 | 142 | 51 | 133/9 |
| m006 | 21526 | 14877 | 183 | 83 | 156/27 |
| m009 | 14192 | 19029 | 53 | 44 | 50/3 |
| m012 | 32096 | 21592 | 229 | 58 | 195/34 |
| m015 | 27792 | 23616 | 126 | 64 | 116/10 |
| m018 | 21330 | 17105 | 182 | 78 | 159/23 |
| m021 | 28064 | 21960 | 194 | 72 | 171/23 |
| m024 | 20942 | 13989 | 314 | 78 | 266/48 |
| m027 | 32458 | 18923 | 150 | 62 | 129/21 |
| m030 | 21758 | 15797 | 110 | 70 | 100/10 |
| m033 | 13948 | 7312 | 7 | 7 | 7/0 |
| m036 | 34428 | 23529 | 93 | 46 | 75/18 |
| m039 | 30434 | 20276 | 111 | 49 | 91/20 |
| m042 | 23710 | 17642 | 124 | 74 | 107/17 |
| m045 | 25734 | 22144 | 166 | 87 | 146/20 |
| m048 | 34416 | 24868 | 190 | 58 | 165/25 |
| m051 | 33384 | 24172 | 190 | 58 | 166/24 |
| m054 | 32522 | 23540 | 190 | 58 | 166/24 |
| m057 | 32732 | 23409 | 244 | 60 | 214/30 |
| m060 | 35652 | 33132 | 45 | 42 | 44/1 |
| m063 | 29478 | 26663 | 43 | 41 | 41/2 |
| m066 | 28078 | 26539 | 47 | 44 | 46/1 |
| m069 | 25364 | 22849 | 39 | 37 | 39/0 |
| m072 | 22708 | 20392 | 39 | 37 | 38/1 |
| m075 | 26030 | 25966 | 34 | 32 | 32/2 |
| m078 | 28256 | 26075 | 39 | 36 | 37/2 |
| m081 | 26890 | 24460 | 37 | 35 | 35/2 |
| m084 | 31780 | 28563 | 44 | 42 | 41/3 |
| m087 | 28414 | 27004 | 158 | 39 | 157/1 |
| m090 | 28420 | 27004 | 158 | 39 | 157/1 |
| m093 | 13920 | 15001 | 64 | 23 | 60/4 |
| m096 | 16556 | 18887 | 26 | 23 | 25/1 |
| m099 | 13664 | 14513 | 57 | 25 | 55/2 |
| m102 | 11594 | 12464 | 50 | 24 | 48/2 |
| m105 | 9614 | 10179 | 24 | 23 | 23/1 |
| m108 | 11676 | 13312 | 28 | 25 | 27/1 |
| m111 | 11132 | 11883 | 25 | 24 | 24/1 |
| m114 | 15086 | 16708 | 27 | 25 | 26/1 |
| m117 | 9418 | 9952 | 24 | 22 | 23/1 |
| m120 | 0 | 0 | 0 | 0 | 0/0 |
Totals (39 assembled stages): 940,586 verts, 791,524 tris, 1,795
embedded texture images. m087 and m090 have identical part/vert/tri
counts but different bytes (sha256 differs) — variant entries of the
same arena, not duplicates.

## Exceptions (no guessed geometry shipped)

- **m000 — VMX version 2.** The v2 part records are 36 B (not 40 B)
  and parts draw from 58 distinct shared vertex streams (fighter-style
  layout); stream extents are not self-describing under the v4 rules
  (the v4 stream-end word is absent). Part 0's stream decodes sanely
  at stride 40, so the format is close, but assembling the full stage
  needs the v2 loader path read from the XBE — named blocker, no GLB
  shipped for m000.
- **m120 — VMX version 3** (246,144 B, the archive's small outlier).
  Single part whose stream-end word is the sentinel 0xFFFFFFFF;
  geometry not assembled — named blocker (v3 part semantics), no GLB
  shipped for m120.

Parts skipped inside assembled stages are the same class the phase-2
extractor skipped (span ≤ 0 or not a multiple of 40 — non-geometry
records in the part arrays); the m003 vertex total matching the
verified 35,390 exactly confirms nothing geometric was dropped there.

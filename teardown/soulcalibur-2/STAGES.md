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
| m000 | 505744 (40065 unique) | 18959 | 265 | 84 | 102/163 |
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
| m120 | 401 | 760 | 1 | 0 | 1/0 |
Totals (39 assembled stages): 940,586 verts, 791,524 tris, 1,795
embedded texture images. m087 and m090 have identical part/vert/tri
counts but different bytes (sha256 differs) — variant entries of the
same arena, not duplicates.

## Phase 14 update — exceptions resolved (41/41)

Both exceptions were assembled in phase 14 with the same
measured discipline (full layout evidence:
`PHASE14-STAGE-LAYOUTS.md`; tool: `tools/build_stage2.py`):

- **m000 — VMX version 2: ASSEMBLED.** 36 B part records; parts
  share one 40 B-stride vertex stream per node (58 streams, extents
  proven by exact tiling: span = nv·40 or nv·40+8 trailer); parts
  placed by node matrices (translation ×1.0, stage units); the 3
  type-4 parts use the fighter skinned-pool split-stream layout
  (color+UV 12 B/vert + pos+normal 32 B/vert, triplicated
  byte-identical). VXT is version 1 (32 B records; mip-chain size
  accounting exact over all 86 records). 265/265 parts, 0 skipped:
  40,065 unique stream verts (505,744 verts as stored in the GLB,
  shared streams emitted per part), 18,959 tris, 84 embedded
  images, topology strip/list 102/163. Proof (viewed):
  `phase14-proof/stage-m000-arena.png`,
  `phase14-proof/stage-m000-arena-flat.png`,
  `phase14-proof/stage-m000-plan.png`.
- **m120 — VMX version 3: ASSEMBLED.** Standard 40 B record; the
  0xFFFFFFFF word is the stream-end sentinel and the vertex count
  (401) is exact by (iptr − vptr) = 401·40 + 8. Its VXT holds 0
  textures and its only material is color-only; the geometry is a
  unit sphere with uniform white vertex colors — shipped exactly
  as stored (401 verts, 760 tris, 0 images). Proof (viewed):
  `phase14-proof/stage-m120-plan.png`,
  `phase14-proof/stage-m120-arena.png`.

**Stage totals are now 41/41**: 940,586 + 505,744 + 401 GLB verts,
791,524 + 18,959 + 760 tris, 1,795 + 84 embedded images.

Parts skipped inside assembled stages are the same class the phase-2
extractor skipped (span ≤ 0 or not a multiple of 40 — non-geometry
records in the part arrays); the m003 vertex total matching the
verified 35,390 exactly confirms nothing geometric was dropped there.

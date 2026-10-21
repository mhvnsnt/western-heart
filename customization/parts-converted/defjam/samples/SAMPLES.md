# Def Jam FFNY — Phase V sample validation (J4, 2026-10-21)

Sample set: 18 `.o` + sibling `.ssh` pulled read-only from
mhvnsnt/wrestling-game `teardown/def-jam-fight-for-ny/models/caw-parts`
(codes 110/111/112/113 = head / upper_body / lower_body /
accessories), converted with `customization/tools/convert_defjam_o.py`.

## Conversion results (tool output)

| sample | status | vertices | blocks |
|---|---|---|---|
| V2CP_110_0001_A/B/D/E/F | converted (pool) | 1160 ea. | 27 |
| V2CP_110_0001_C | compiled_variant | — | — |
| V2CP_111_0001_A/B | converted (pool) | 1242 ea. | 29 |
| V2CP_111_0002_A/B | converted (pool) | 1249 ea. | 29 |
| V2CP_112_0002_A/B | converted (pool) | 1181 ea. | 29 |
| V2CP_112_0003_A/B | converted (pool) | 1251 ea. | 29 |
| V2CP_113_0001_A/B | converted (pool) | 1140 ea. | 27 |
| V2CP_113_0002_A/B | converted (pool) | 1170 ea. | 28 |

0 errors. GLBs in this directory are POINTS pools (see verdict 3).

## Verdict 1 — SHPS textures: PASS (own eyes)

- `V2CP_111_0001_A01_01.png` (256×256): blue denim garment —
  waistband, pocket curves, seam stitching. PASS.
- `V2CP_113_0001_A01_01.png` (256×256): white/cream garment with
  reddish-brown panels and checkered trim. PASS.
- `V2CP_361_0013_A01_01.png` (64×62, batch set): coherent banded
  stitch pattern — this is the partial-page texture that proved
  the padded-page swizzle rule (spec §7.10). PASS.

## Verdict 2 — stream framing / extraction: PASS

Block framing verified byte-exactly on every block of every
sample; block counts match the `_C` compiled twin's strip
descriptor table exactly for 110_0001 (27 strips). RefPack
decompression byte-exact. The extracted Coordinates pool has
part-shaped statistics (x symmetric about 0; z the long axis).

## Verdict 3 — geometry / topology: FAIL — BLOCKED (do not ship meshes)

- A triangle-strip build of V2CP_110_0001_A rendered in Blender
  (EEVEE) is scrambled spikes, not a head part:
  `teardown/def-jam-fight-for-ny/sample-renders/V2CP_110_0001_A_STRIP_FAILED.png`.
- The raw pool rendered as points is a loose scatter, not a
  surface shell: `.../V2CP_110_0001_A_points.png`,
  `.../V2CP_111_0001_A_points.png`.
- Conclusion: the stored vertex order is not the draw order, and
  the pool's geometric interpretation is unproven. Falsified
  readings and the live leads (bone-local assembly, the VU-packed
  companion stream, the `_C` packed form) are documented in
  EAGL-FORMAT-SPEC.md §7.9. Per the lane rule — a sample we
  wouldn't ship stops the line — NO mesh GLBs are shipped for
  Def Jam. The converter emits the proven pool as POINTS with
  `topology_status=unproven_vertex_order`.

## Batch note

The Phase B census over all 2,624 extracted `.o` is in spec
§7.10 and `customization/parts-converted/defjam/CATALOG.json`:
1,201 pool+texture extractions (POINTS GLBs), 654 compiled
variants, 767 files with no valid RefPack record, 2 pose-palette
objects, 0 errors. The other 19,736 indexed parts were never
extracted from the disc (spec §7.10).

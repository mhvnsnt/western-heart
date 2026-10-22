# Soulcalibur II (Xbox) — Phase 16 State: Full Re-decode with Fixed Reader

Lane: TEARDOWN COMPLETION SWEEP, Phase 16. Stacked on PR #562
(`scii-phase15-ivy-probes` @ 4e7c611a, OPEN). Branch:
`scii-phase16-redecode-fixed-reader`. Workdir: `~/workspace/scii-work/p13/`
(sparse clone `wh/` + `work/`). Banned file NOT touched:
`~/workspace/scii-work/p2/v982_idx47.bin`.

## Defect being repaired (phase 15, PR #562)

`tools/build_skinned.py` carried a phase-4 "+8 start shift" for rigid
parts whose span = count×40+8. Those parts carry an 8-byte TRAILER;
their vertices start at rec[5] in standard format. The shift misread
the +0x18 ARGB color word as normal-Y: white colors → NaN → the part
was EXCLUDED as a "sheet"; grey colors → ≈−3.4e38 → overflow. The fix
is landed in `tools/build_skinned.py` on the #562 branch (shift
deleted + finite assertions before all packing). Phase 15 proved at
+0 alignment: all 725 rigid parts across 25 bundles have unit
normals + 0xFF-alpha colors for every vertex.

Consequence: all GLBs shipped before the fix are missing their
trailer-span rigid parts — 255 parts across the 25 bundles censused
in phase 15. No garbage shipped (phase-15 scan: no non-finite /
|n|>2 normals anywhere in the shipped set) — parts were DROPPED,
not corrupted.

## Jobs

1. RE-DECODE THE BASE 22: full pipeline (fixed `build_skinned.py` +
   `apply_textures.py`) → rebuild `models-skinned/` +
   `models-textured/`. Gates per file (assert, don't sample):
   (a) every part in the OLD GLB present in the NEW GLB with
   identical POSITION/index/JOINTS counts + identical skin joint
   set; (b) recovered trailer-span parts counted per fighter,
   reconciled against the phase-15 census (725 rigid / 25 bundles);
   (c) all normals finite; (d) textured: embedded image counts ≥ old,
   mapping pointer-exact as before. Per-fighter delta table below.
2. RE-DECODE THE VARIANTS: same pipeline + gates, per-fighter
   variant dirs; batch commits per fighter group; clear each
   batch's fetched bundles after commit. NOT rebuilt (already
   correct, phase 15): idx283, idx291 (Ivy) + idx789 (rigid).
3. NIGHTMARE CHECK: render re-decoded Nightmare (base, textured)
   FRONT + thigh-region close view, viewed, vs the phase-3 gap
   record; state whether recovered parts close the thigh gap and
   what the formerly-"sheet" parts are. Also render Mitsurugi +
   2–3 fighters with the largest recovered counts, viewed.
4. DOC CORRECTIONS: CORRECTIONS section here + inventory-doc
   updates — the "sheet" class never existed; the parts are
   trailer-span rigid parts, now decoded. Additive only; no old
   PR bodies rewritten, no old docs deleted.
5. CENSUS CLOSEOUT: `CENSUS-PHASE13.md` / `WIRING-INVENTORY.md`
   phase-16 sections: final part counts per set; variants with the
   fixed reader; the 255-part recovery reconciled.

## In-place GLB replacement notice

This phase REPLACES shipped GLB files in-tree on its branch — that
is its purpose. The PR diff will show modified GLBs; that is
expected and is NOT a violation of additions-only. The per-file
gate table is the proof nothing else changed (gate (a): existing
parts byte-identical in counts and skinning; the fix only ADDS
parts).

## Status log

- 2026-10-22 ~04:41 CDT — lane start. Branch created from
  4e7c611a (PR #562 head); this state doc is the first commit;
  PR opened immediately after (stacked on #562).
- Disk ~87% at start; work in batches, never more than one batch
  of bundles + outputs held at once; clears logged below.
- 2026-10-22 ~05:05 CDT — JOB 1 DONE: base 22 rebuilt with the
  fixed in-repo tools (`tools/build_skinned.py` +
  `tools/apply_textures.py`, VMX0 @0x3880), all gates run per file
  (see delta table). 891 → 1,081 parts (+190 recovered, = the
  from-bytes trailer-span census of the 22 bundles exactly);
  textured images 559 → 601. 44 GLB files replaced in-tree
  (22 skinned + 22 textured), 0 deletions. Only deviation:
  idx632 JOINTS_0/WEIGHTS_0 tail-slot bytes on 2/4,406 verts at
  ~1e-9 weights (characterized in the delta-table note; gate (a)
  as specified passes). Base bundles were already on disk in
  `p13/work/bundles` from phase 13 (header-verified then); no
  new fetch needed for JOB 1.

## Clears log

- (none yet)

## Per-fighter delta table (base 22) — JOB 1 DONE

Gate method: old GLBs snapshotted before replacement (per-mesh
POSITION/NORMAL/JOINTS_0/WEIGHTS_0/index accessor counts + SHA-256
of the accessor bytes, skin joint name list, image count,
normals-finite scan). New GLBs must contain every old mesh with
identical counts and (stricter than the task gate) identical
accessor bytes, the identical skin joint set, finite normals
everywhere, and ≥ old embedded images in the textured set.
Recovered count = meshes present in the new GLB and absent in the
old; independently, a from-bytes census of each bundle
(VMX0 @0x3880 part records; trailer-span = span − rec[5] ==
count×40 + 8) gives the same numbers per fighter.

| Entry | Fighter | Old parts | New parts | Recovered | Textured images (old → new) | Gate |
|---|---|---|---|---|---|---|
| 47 | Mitsurugi | 39 | 51 | +12 | 23 → 26 | PASS |
| 86 | Seong Mi-na | 55 | 63 | +8 | 32 → 33 | PASS |
| 125 | Taki | 41 | 49 | +8 | 32 → 34 | PASS |
| 164 | Maxi | 32 | 36 | +4 | 22 → 23 | PASS |
| 203 | Voldo | 34 | 36 | +2 | 18 → 19 | PASS |
| 242 | Sophitia | 33 | 37 | +4 | 29 → 31 | PASS |
| 281 | Ivy | 46 | 59 | +13 | 27 → 29 | PASS |
| 320 | Kilik | 30 | 32 | +2 | 29 → 30 | PASS |
| 359 | Xianghua | 22 | 24 | +2 | 20 → 21 | PASS |
| 398 | Yoshimitsu | 83 | 102 | +19 | 29 → 33 | PASS |
| 437 | Nightmare | 56 | 86 | +30 | 28 → 36 | PASS |
| 476 | Astaroth | 25 | 34 | +9 | 21 → 23 | PASS |
| 515 | Cervantes | 49 | 62 | +13 | 35 → 37 | PASS |
| 554 | Raphael | 39 | 41 | +2 | 36 → 37 | PASS |
| 593 | Talim | 36 | 38 | +2 | 32 → 33 | PASS |
| 632 | Cassandra | 40 | 42 | +2 | 35 → 36 | PASS (a) — see idx632 note |
| 671 | Necrid | 17 | 24 | +7 | 10 → 13 | PASS |
| 710 | Yun-seong | 33 | 40 | +7 | 29 → 30 | PASS |
| 827 | UNIDENTIFIED (1e) | 28 | 37 | +9 | 23 → 24 | PASS |
| 866 | UNIDENTIFIED (1f) | 24 | 28 | +4 | 20 → 21 | PASS |
| 905 | UNIDENTIFIED (20) | 54 | 79 | +25 | 17 → 19 | PASS |
| 944 | Spawn | 75 | 81 | +6 | 12 → 13 | PASS |
| **total** | **22 fighters** | **891** | **1081** | **+190** | **559 → 601** | |

Base totals reconcile with the phase-13 record (891 meshes / 559
images shipped) exactly. The 1,081 new parts = the full source
part census of the 22 bundles (every skinned + rigid part in
VMX0), verified from the bundle bytes.

**idx632 (Cassandra) note — gate (a) passes as specified; one
stricter-hash deviation, characterized:** identical
POSITION/index/JOINTS counts (4,406 verts) and identical
187-name skin joint set; POSITION/NORMAL/INDEX accessor bytes
identical for every part. JOINTS_0/WEIGHTS_0 bytes differ in
exactly 2 of 4,406 verts (4404, 4405), only in >4-influence
truncation-tail slots carrying weights 2.1e-09…3.9e-09 (e.g. old
slot joint 74 @ 2.13e-09 vs new joint 70 @ 3.87e-09). Skinning
effect ≤ 4e-09 weight — numerically negligible; the skinned path
is untouched by the rigid fix, so this is solver/DP float-tail
behaviour differing between the phase-5-era original build and
the in-repo build, not a geometry or skinning change. No other
file shows any old-part byte difference.

**Reconciliation against the phase-15 census (725 rigid parts /
25 bundles, 255 trailer-span):** the 25 censused bundles are the
22 P1 bundles + idx283 + idx291 + idx789. Base 22: 579 rigid
parts, 190 trailer-span (= the +190 recovered above; old base
GLBs were independently verified to be missing exactly those 190
parts and nothing else). Phase 15 recorded 7 recovered
trailer-span parts in each of idx283 and idx291. Remainder:
255 − 190 − 7 − 7 = 51 trailer-span parts in idx789 (of its 102
rigid parts), consistent with 579 + (idx283 rigid) + (idx291
rigid) + 102 = 725. The variant bundles rebuilt in JOB 2 were
never part of the 25-bundle census; their recovered counts are
additional and are reported per fighter in the JOB 2 table — the
"≈255" figure is the census-scope total, not a cap on the
variant recovery.

## CORRECTIONS

- (populated by JOB 4)

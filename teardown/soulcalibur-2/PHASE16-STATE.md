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
- 2026-10-22 ~06:20 CDT — JOB 2 DONE: 80/80 variant GLBs rebuilt,
  all gates pass, +597 parts (2,850 → 3,447), images
  1,964 → 2,105. Landed in 8 batch commits (bundles cleared per
  batch, see clears log). JOB 3 DONE: Nightmare + Mitsurugi +
  Yoshimitsu + idx905 old-vs-new renders + Nightmare thigh
  close-up, all viewed — thigh gap CLOSED (JOB 3 section).
  JOB 4/5: CORRECTIONS section here + phase-16 sections in
  `CENSUS-PHASE13.md` / `WIRING-INVENTORY.md` + annotations on
  the two "sheet-class" inventory entries + a count note in
  `TEXTURED-MODELS.md`. `CANON-CONVERSION.md` untouched.

## Clears log

- 2026-10-22 ~05:12 CDT — recon fetches idx283 + idx789
  (~2.6 MB, used only to verify the 7 / 51 trailer counts for the
  255 reconciliation) cleared immediately after the census ran.
- 2026-10-22 — variant batch bundles cleared after each batch's
  commit: batch 1 (48,49,55,56,57,87,88,94,95,96 — note: the
  first-run outputs for 55,56,57,87,88,94,95,96 were lost to a
  scratch sweep and re-run; the re-run bundles were then cleared
  after their commit), batch 2 (126,127,133,134,135,165,172,173,
  204,205), batch 3 (243,244,250,251,252,282,289,290,321,328),
  batch 4 (329,360,361,367,368,369,399,406,407,438), batch 5
  (439,445,446,447,477,478,484,485,486,516), batch 6 (523,524,
  555,556,562,563,564,594,595,601), batch 7 (602,603,633,634,
  640,641,642,672,711,718), batch 8 (719,828,829,867,868,906,
  907,945,952,953). Each batch ~15–21 MB; fetched size-verified +
  VMX@0x3880 header-verified per file. Skinned intermediates in
  the scratch `out/` dir cleared per batch. Base-22 bundles in
  `p13/work/bundles` predate this lane (phase 13) and are not
  cleared here. Banned file untouched.

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
25 bundles, 255 trailer-span) — closed exactly, from bytes:**
the 25 censused bundles are the 22 P1 bundles + idx283 + idx291
+ idx789. Measured this phase with the same from-bytes census:
base 22 = 579 rigid / 190 trailer-span (old base GLBs were
independently verified to be missing exactly those 190 parts and
nothing else); idx283 = 22 rigid / 7 trailer-span (fetched and
measured, then cleared); idx789 = 102 rigid / 51 trailer-span
(measured the same way). idx291 mirrors idx283 (same part counts
in its phase-15 gate: 41 meshes total, 7 recovered). Totals:
579 + 22 + 22 + 102 = **725 rigid** ✓ and 190 + 7 + 7 + 51 =
**255 trailer-span** ✓. The 80 variant bundles rebuilt in JOB 2
were never part of the 25-bundle census; their +597 recovered
parts are additional (each variant bundle is a separate costume
bundle with its own trailer-span parts) — the "255" figure is
the census-scope total for the 25 censused bundles, not a cap
on the variant recovery. Grand total recovered by the fixed
reader across every shipped set: 190 (base, counted once per
bundle; they appear in both the skinned and textured sets) +
597 (variants) = **787 parts**, plus the 65 already recovered in
phase 15 (7 + 7 + 51).

## JOB 2 — variants re-decoded (DONE)

80 variant GLBs rebuilt with the fixed reader, same pipeline and
gates as JOB 1 (per-file gate JSONs were produced for all 80; all
pass gate (a) in its strict form — every old part byte-identical,
identical skin joint set — plus finite normals and images ≥ old).
idx283 / idx291 / idx789 were NOT rebuilt (already correct,
phase 15). idx399 and idx407 (Yoshimitsu) contain zero
trailer-span parts: their rebuilt outputs are byte-identical to
the shipped files (no git diff) — a determinism proof for the
pipeline. Per-fighter aggregates (files: parts old → new,
recovered; textured images old → new):

| Variant set | Files | Parts | Recovered | Images |
|---|---|---|---|---|
| Mitsurugi (47) | 5 | 147 → 169 | +22 | 117 → 126 |
| Seong Mi-na (86) | 5 | 201 → 217 | +16 | 136 → 141 |
| Taki (125) | 5 | 177 → 199 | +22 | 144 → 152 |
| Maxi (164) | 3 | 94 → 116 | +22 | 72 → 77 |
| Voldo (203) | 2 | 22 → 24 | +2 | 19 → 20 |
| Sophitia (242) | 5 | 139 → 185 | +46 | 117 → 123 |
| Ivy (281; 282/289/290 only) | 3 | 140 → 163 | +23 | 87 → 93 |
| Kilik (320) | 3 | 92 → 108 | +16 | 87 → 94 |
| Xianghua (359) | 5 | 108 → 138 | +30 | 82 → 85 |
| Yoshimitsu (398) | 3 | 167 → 186 | +19 | 89 → 93 |
| Nightmare (437) | 5 | 242 → 330 | +88 | 144 → 164 |
| Astaroth (476) | 5 | 129 → 182 | +53 | 103 → 109 |
| Cervantes (515) | 3 | 109 → 138 | +29 | 65 → 69 |
| Raphael (554) | 5 | 177 → 191 | +14 | 160 → 167 |
| Talim (593) | 5 | 160 → 190 | +30 | 130 → 143 |
| Cassandra (632) | 5 | 194 → 228 | +34 | 133 → 138 |
| Necrid (671) | 1 | 24 → 37 | +13 | 20 → 23 |
| Yun-seong (710) | 3 | 103 → 130 | +27 | 93 → 106 |
| UNIDENTIFIED 1e (827) | 2 | 61 → 77 | +16 | 46 → 51 |
| UNIDENTIFIED 1f (866) | 2 | 54 → 62 | +8 | 47 → 48 |
| UNIDENTIFIED 20 (905) | 2 | 85 → 128 | +43 | 37 → 40 |
| Spawn (944) | 3 | 225 → 249 | +24 | 36 → 43 |
| **Variants total** | **80** | **2,850 → 3,447** | **+597** | **1,964 → 2,105** |

The old variant image total (1,964) matches the phase-14 record
exactly. Work note: the first variant batch's outputs for 8 files
were lost when the scratch dir outside the surviving work tree
was swept mid-lane (the delivered batch log for those files also
reported numbers that do not match the files; the gate snapshot
was re-verified against all 78 then-unreplaced tree files —
0 mismatches — and the 8 files were re-run from re-fetched
bundles into the surviving `p13/work` scratch, re-gated, and
landed). All other batches ran in `p13/work` throughout.

## JOB 3 — Nightmare check + sample renders (DONE, all viewed)

Proof renders in `phase16-proof/` (Blender/Cycles fronts of the
textured GLBs, old GLB taken from the #562 branch in git):

- `nightmare-old-vs-new-front.png` — **the thigh gap is CLOSED.**
  Old Nightmare: thighs entirely absent — the shorts end and the
  greaves float below an empty gap; also missing the helmet
  (bare head) and the cuirass front. New Nightmare: complete —
  horned helmet, cuirass with the eye emblem, faulds, and solid
  armored thighs joining hip to knee.
- `nightmare-thigh-close-old-vs-new.png` — close view of the
  thigh band: old shows hollow shorts rims, a bare gap, and
  floating knee guards; new shows continuous plate cuisses from
  shorts to knee cops (with the spiked knee side-plates).
  Nightmare's 30 recovered parts, by bind-pose bounds, are plate
  armor: cuisses (thigh plates, y 0.60–0.93), knee/shin/foot
  plates (y 0.12–0.74), fauld/hip plates (y 0.87–1.16), cuirass
  (y 1.17–1.45), helmet (y 1.57–2.09), pauldrons and gauntlet
  plates. The phase-3 "sheet" parts on Nightmare were his armor.
- `mitsurugi-old-vs-new-front.png` — old: right forearm/hand
  detached and floating, scabbards reduced to red/white shards,
  shoulder guards partial. New: complete arms with the chainmail
  forearm guard and full scabbards at both hips. Mitsurugi's
  "illegible sheets" were his scabbards, forearm guard, and
  armor trim.
- `yoshimitsu-old-vs-new-front.png` (+19) — old: face a dark
  void, mechanical arm fragmented. New: complete skull mask and
  mechanical arm assembly.
- `unidentified-20-old-vs-new-front.png` (idx905, +25) — old:
  left arm detached in three floating pieces, thigh armor
  missing. New: arm connected (pauldron + chainmail + gauntlet),
  cuisses in place.

## CORRECTIONS

1. **The phase-3/4 "sheet part class" never existed.** The parts
   recorded as an illegible "sheet class" (phase-4 decode record;
   summarized in `WIRING-INVENTORY.md` — "sheet-class parts only
   in the `_full` variants" and the Nightmare entry's "sheet-class
   parts in `_full` do not form legible coverage") are ordinary
   rigid parts whose vertex streams carry an 8-byte trailer
   (span = count×40 + 8). The old reader's +8 start shift misread
   them (phase 15, PR #562, root-cause proof in
   `PHASE15-PROBES.md` job 1). With the fixed reader they decode
   as legible, textured armor/equipment plates — see the JOB 3
   renders. `WIRING-INVENTORY.md` entries are annotated in place
   (additive; original text kept).
2. **PR #31's open "Nightmare thigh gap" is RESOLVED.** The gap
   was the dropped trailer-span cuisses (thigh plates) and
   associated leg armor. The re-decoded Nightmare (base, textured)
   has continuous armored thighs — `phase16-proof/` renders above.
   (The `models/` placed GLBs still carry the phase-4 decode; they
   are outside this phase's rebuild scope — see Deviations.)
3. Phase-13's textured-model counts (886/891 meshes textured,
   559 images) described the pre-fix set; the fixed set is
   1,081/1,081 parts with 601 images (JOB 1 table). A phase-16
   note is added to `TEXTURED-MODELS.md` and the census closeout
   is in `CENSUS-PHASE13.md`.

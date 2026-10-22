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

## Clears log

- (none yet)

## Per-fighter delta table (base 22)

- (populated by JOB 1 gate run)

## CORRECTIONS

- (populated by JOB 4)

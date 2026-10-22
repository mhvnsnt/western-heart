# Soulcalibur II (Xbox) — Census of the Rest (Phase 13, JOB 4)

Everything outside fighters/stages/movesets, censused from the source
tables themselves (root.olk entry table, v982/v516 entry tables, AFS
headers — all range-fetched from the release ISO asset and parsed;
no contents claimed beyond what was probed).

## Costume-variant bundles — v982 (982 slots, 577 non-empty entries)

Character blocks are 39 entries, keyed by the XBE `FUN_00047440` table
(bases below). The P1 model bundle is base+1 (the 22 decoded fighters
of PR #406 + the 2 rigid-only bundles at slots 19/24). Costume-variant
model bundles sit at base+2, base+3, base+9, base+10, base+11; their
sizes (1.5–2.2 MB) match the P1 model-bundle class, i.e. they are full
model bundles decodable by the existing VMX pipeline — census only
here, per the job scope; decode is mechanical follow-up work, not a
format blocker. Each P1 bundle itself also contains a second VMX
(VMX#2: 2 VMXs in 21 of 22 sampled bundles; Necrid's bundle has 6),
the in-bundle extra model (weapon/2P-costume class, cf. phase-3/4).

| Slot | Base | P1 entry | Costume entries present (of +2/+3/+9/+10/+11) | Block entries non-empty |
|---|---|---|---|---|
| 01 Mitsurugi | 46 | 47 | 5/5 | 27/39 |
| 02 Seong Mi-na | 85 | 86 | 5/5 | 27/39 |
| 03 Taki | 124 | 125 | 5/5 | 27/39 |
| 04 Maxi | 163 | 164 | 3/5 (+3, +11 empty) | 25/39 |
| 05 Voldo | 202 | 203 | 2/5 (+9..+11 empty) | 21/39 |
| 06 Sophitia | 241 | 242 | 5/5 | 27/39 |
| 0b Ivy | 280 | 281 | 5/5 | 27/39 |
| 0c Kilik | 319 | 320 | 3/5 | 25/39 |
| 0d Xianghua | 358 | 359 | 5/5 | 27/39 |
| 0f Yoshimitsu | 397 | 398 | 3/5 | 25/39 |
| 11 Nightmare | 436 | 437 | 5/5 | 27/39 |
| 12 Astaroth | 475 | 476 | 5/5 | 27/39 |
| 13 (rigid-only) | 748 | 749 | 0/5 | 5/39 |
| 14 Cervantes | 514 | 515 | 3/5 | 25/39 |
| 15 Raphael | 553 | 554 | 5/5 | 27/39 |
| 16 Talim | 592 | 593 | 5/5 | 27/39 |
| 17 Cassandra | 631 | 632 | 5/5 | 27/39 |
| 18 (rigid-only) | 787 | 788 | 1/5 (+2 only) | 7/39 |
| 19 Necrid | 670 | 671 | 1/5 (+2 only) | 20/39 |
| 1a Yun-seong | 709 | 710 | 3/5 | 25/39 |
| 1d Spawn | 943 | 944 | 3/5 | 25/39 |
| 1e UNIDENTIFIED | 826 | 827 | 2/5 (+2, +3) | 16/39 |
| 1f UNIDENTIFIED | 865 | 866 | 2/5 (+2, +3) | 16/39 |
| 20 UNIDENTIFIED | 904 | 905 | 2/5 (+2, +3) | 16/39 |

Remainder of the 577: per-block common/motion bundles (the ~2.6–2.8 MB
series at block bases, stride +39 — motion, GATED/out of scope for
this lane), in-bundle resource classes, and ~434 small unclassified
entries (100–600 KB) already flagged in `WIRING-INVENTORY.md`.

## Standalone texture containers — v516 (516 slots, 371 non-empty)

206.1 MB total (94 entries ≥ 1 MB, 231 at 100 KB–1 MB, 46 < 100 KB).
Files carry `VXT.` sections and no `VMX.` (sampled: entry 1,
955,264 B — exactly 1 VXT section, 0 VMX). These are the non-model
texture sets (UI / menu / weapon / common). The fighter and stage
texture needs are already fully covered by the per-VMX VXT sections
(JOBs 1–3); v516 contents are inventoried here, not decoded — no
blocker, decode is the same proven VXT pipeline if a consumer appears.

## Audio — bgm.afs (CRI AFS, ISO sector 2031)

Header probed from the ISO: `AFS\0`, **76 entries**, sizes
162,558–17,590,374 B (first entry at file offset 524,288,
5,633,622 B). Entry 0's first bytes are a CRI **ADX** header
(`80 00 00 20 03 12 04 02`, sample rate 0xBB80 = 48,000 Hz, stereo) —
the music is standard ADX, decodable with existing ADX tooling.
Census only (per job scope); extraction is cheap and proven-format.

## Video — movie.afs (CRI AFS, ISO sector 119047)

Header probed: `AFS\0`, **3 entries** — 402,294,784 B /
17,285,120 B / 19,556,352 B. Entries 0 and 1 both start with
`00 00 01 BA` — **MPEG program stream** (Sofdec-class cutscene
video), decodable with standard MPEG tools. Census only.

## In-bundle sound (v982, resource type 0xc)

Character sound resources ride inside the model bundles (type 0xc in
the `FUN_00033fb0` resource table, phase-2 §1). Not extracted here;
the bundle resource table is parsed, so extraction is mechanical.
Format inside the resources was not probed this phase — named
blocker: type-0xc payload format unprobed (expected CRI ADX-family,
unproven).

## Phase 14 update — costume variants decoded (JOB 2)

The 83 non-empty variant bundles censused above were range-fetched
(header/VMX-verified per file) and run through the proven pipeline
(`build_skinned.py` VMX0 @0x3880 → `apply_textures.py`). Variant
bundles are structurally identical to P1 bundles (VMX0 = skinned
fighter pool + VXT; VMX1 = rigid extra) — no format delta. Gates
per file: skin-solve residual reported by the builder, accessor
counts asserted identical by the texture tool, GLB re-parsed with
embedded images > 0 and exactly 1 skin. Results: **80 decoded,
3 blocked**; 1,964 embedded texture images total; GLBs under
`models-textured/variants-idx<P1>-<slug>/` (per-fighter isolation).
Proof (viewed): `phase14-proof/variant-idx48-mitsurugi-front.png`
— Mitsurugi's idx48 costume (sash wrap, black flame-embroidered
hakama), coherent and fully textured.

| P1 entry | Fighter (source ID) | Variants held | Decoded | Blocked |
|---|---|---|---|---|
| 47 | Mitsurugi | 5 | 5 | — |
| 86 | Seong Mi-na | 5 | 5 | — |
| 125 | Taki | 5 | 5 | — |
| 164 | Maxi | 3 | 3 | — |
| 203 | Voldo | 2 | 2 | — |
| 242 | Sophitia | 5 | 5 | — |
| 281 | Ivy | 5 | 3 | idx283, idx291 — build_skinned produces non-finite normals at GLB export (OverflowError); source pool normals are finite (0 NaN / 3,898 verts in idx283) — solver-side degenerate-bone residual, re-runnable when the solver handles it |
| 320 | Kilik | 3 | 3 | — |
| 359 | Xianghua | 5 | 5 | — |
| 398 | Yoshimitsu | 3 | 3 | — |
| 437 | Nightmare | 5 | 5 | — |
| 476 | Astaroth | 5 | 5 | — |
| 515 | Cervantes | 3 | 3 | — |
| 554 | Raphael | 5 | 5 | — |
| 593 | Talim | 5 | 5 | — |
| 632 | Cassandra | 5 | 5 | — |
| 671 | Necrid | 1 | 1 | — |
| 710 | Yun-seong | 3 | 3 | — |
| 788 | (rigid-only slot) | 1 | 0 | idx789 — rigid-only bundle class (730,240 B; its base slot was never a skinned fighter); the skinned pipeline reads past EOF on its rec28 layout — decode path is the rigid/placed route, not run here |
| 827 | UNIDENTIFIED (1e) | 2 | 2 | — |
| 866 | UNIDENTIFIED (1f) | 2 | 2 | — |
| 905 | UNIDENTIFIED (20) | 2 | 2 | — |
| 944 | Spawn | 3 | 3 | — |

Audio/video census above is superseded by extraction:
`PHASE14-AV-INVENTORY.md` + `PHASE14-AV-MANIFEST.json` (release
`scii-phase14-av`).

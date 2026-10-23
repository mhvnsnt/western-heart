# DOA4 Phase 15 — Containment Audit

The provenance decision for the DOA4 mirror streams, made with the
verified retail ISO in hand. Question (phase 14 residual): are the
mirror tar's `chrone`/`chrtwo`/`chrthree` streams a permuted copy of
the retail ISO's AFS containers, or a different build's layout?

**Answer, evidenced below: a different (earlier) build's package
layout.** Byte-level containment of retail entries is real but
regional: it is total in a retail-layout tail block of the chrone
stream and in the matched bundle runs of chrtwo/chrthree, and it
fails — by re-authoring, not by permutation — across the rest.
Phases 6–12's model library stands on the mirror's own packages;
name-grade identity is now proven for 70 of the 148 packages
(`package-name-map.json`) and unproven for the other 78.

## Method

1. **ISO re-assembly (verified before any byte was trusted).** The
   30 parts of release `doa4-iso-v1` were fetched with a resumable
   range driver (`tools/iso_fetch_driver_p15.py`); every part's
   sha256 was checked against the release digest BEFORE the
   assembler wrote it. The phase-13 assembler then produced the
   ISO. Whole-ISO sha256 =
   `4423cd5ca0979e38b48fce3dbdd78de6416abfd4dd01fc8cc9140e2c92b104aa`,
   size exactly 7,834,892,288 B — identical to the phase-14
   closeout value. All extraction below ran against this verified
   ISO (`tools/afs_extract_p15.py`, gated on the whole-hash).
2. **Mirror streams** were re-fetched from release
   `doa4-mirror-20261017` parts 02–05 with per-part sha256 verified
   (chrone @1212324864, chrtwo @1578419712, chrthree @2135433728 in
   the extracted-tar layout). One inherited gh partial (part 03)
   failed its digest after resume and was discarded and re-fetched
   from zero; a partial is a trustworthy prefix only with exactly
   one writer attempt. Logged in PHASE15-STATE.md.
3. **Pass 1 — whole-entry exact search** (`tools/containment_p15.py`):
   each ISO entry searched byte-exact in its mirror stream; on
   failure, head/mid/tail 64 B window probes + greedy segment walk.
4. **Pass 2 — 64 KiB block map** (`tools/containment2_p15.py`):
   completed for chrone (block coverage 29.0994 %); superseded by
   pass 3 before chrtwo finished.
5. **Pass 3 — 16 KiB chunk scatter** (`tools/containment_scatter_p15.py`):
   per 16 KiB chunk, 64 B head-window search, full-chunk verify.
   Completed for ALL 44 non-contiguous chrone entries and for 9
   chrtwo entries (hak04–hak08 pairs). Not run to completion for
   the remaining chrtwo/chrthree entries (wall-clock; the identity
   bridges below closed the provenance question without it). Those
   entries carry verdict `piecewise_unresolved` /
   `absent_windows` from pass 1 in the machine map — stated, not
   smoothed over.
6. **Identity bridges** (for the name map): XPR2 directory
   fingerprints (`tools/xpr2_fingerprint_p15.py`) and assembly
   graph keys (`tools/graph_key_match_p15.py`, running the
   phase-3/6 assembly-graph parser on every ISO `.tpr`).

## Containers extracted from the verified ISO

| container | entries | sha256 (container) | notes |
|---|---|---|---|
| chrone.afs | 73 | `256886a0…` | chr_version.bin + .tpr/.cat pairs + 16 B dmy.bin placeholders; NO zac03 pair exists in retail |
| chrtwo.afs | 128 | `a9169c2a…` | gen00.tpr … aya05.cat |
| chrthree.afs | 188 | `da9386ea…` | boy00.tpr … helAE.cat; duplicate TOC names exist (kasumi slots) |
| mot.afs | 197 | `5329bc05…` | see MOT-CENSUS.md (Job 2) |
| cmn.afs | 7 | `c7d23333…` | cmn_version.bin … cam_raw.bin; comon.mot lives here |

`chr_version.bin` contents (16 B): `00000001 00000000 00000000
00000000` — u32 BE version 1 + zeros. Full per-entry lists +
sha256 are in `containment-map.json` (and `mot-entries-manifest.json`
for mot.afs).

## Per-entry verdicts (389 chr entries)

| volume | contiguous | scattered (16 KiB) | piecewise unresolved | absent (windows) |
|---|---|---|---|---|
| chrone (73) | 29 | 44 | — | — |
| chrtwo (128) | 79 | 9 | 38 | 2 |
| chrthree (188) | 81 | — (not run) | 66 | 41 |

Contiguous = the whole entry occurs byte-identical at one mirror
offset (189 entries proven byte-identical to retail). Scattered =
per-chunk fractions measured. The chrone scatter fractions expose
the structure: the retail-named fighters split into a fully
contained set (zac/tin00/01, contiguous) and a re-authored set —
and inside the re-authored set, `.cat` (texture) data survives at
61–88 % in a few big segments while `.tpr` (model) data survives at
0–25 %: **textures were largely carried over between the mirror's
build and retail; model data was re-authored/re-packed.**
`jan02.tpr` chunks are absent from ALL THREE mirror streams at
16 KiB granularity (cross-volume probe) — its retail bytes are
simply not in the mirror set.

## Mirror coverage

Union of all verified entry segments per stream (pass 1 + scatter
where run): **chrone 29.7553 %, chrtwo 51.1871 %, chrthree
48.2684 %.** The complement is NOT unexplained filler:

- Each mirror stream is a sequence of XPR2 bundles: chrone 30,
  chrtwo 68, chrthree 75 bundle starts (16-aligned census), and the
  phase-6 inventory offsets coincide EXACTLY with bundle starts
  (chrone 30/30, chrtwo 68/68; chrthree's 50 packages contain the
  extra 25 bundles as sub-bundles). The stream is fully accounted
  for as *bundles + inter-bundle gaps*; there is no additional
  hidden data class.
- The uncovered bytes are overwhelmingly the bundle bytes of the
  re-authored region: packages whose retail counterparts differ
  (78 of 148 packages have no name-grade match — §Name map).
- In the contiguous tail block the gaps between consecutive
  retail files are small (448–1,376 B) — the same small-gap
  pattern phase 14 measured between AFS entries.

## The retail tail block (chrone)

Mirror chrone [262,148,096, 366,094,336) holds, in TOC order and
byte-identical: zac00.tpr/.cat, zac01, zac02, zac04, tin00, tin01
(all contiguous, plus tin02's bundle fingerprint-identical at
361,709,568). This is a retail-layout region inside the earlier
build's stream — the region phase 14's spot checks happened to
hit. It is the exception, not the rule.

## Package name map (identity harvest)

70 of 148 phase-6 packages now carry PROVEN entry names
(`package-name-map.json`, tiers: proven-byte+fingerprint,
proven-fingerprint, proven-graphkey, proven-shared-order — shared
directory identities like the seven Spartan colorways assigned by
bundle order == TOC order, an ordering every uniquely-matched run
confirms). The identified runs:

- chrone pkg23–29 = zac00, zac01, zac02, zac04, tin00, tin01, tin02
- chrtwo pkg46–67 = gen00–03, hel00–03/05/06, leo00–03, bas00–03,
  hak00/03/04/05
- chrthree pkg09–49 = boy00–04, lis00–04, alp01, tng00/02,
  spa00–06, bra01–03, cri00/01/04/05/06, kor00–03/05–09, rtm00–03

The other 78 packages (chrone pkg00–22, chrtwo pkg00–45, chrthree
pkg00–08) sit in the re-authored regions: their bundles differ
from every retail `.tpr` in directory fingerprint AND graph key.
They are **unassigned** — no name is claimed for them. Their
directory-record counts were compared against the unmatched
retail `.tpr`s as a sanity check only; the counts are
non-discriminative (e.g. chrone pkg02 nrec 222 vs retail jan02
208 / kas02 205 / ryu02 223) and are NOT assignment evidence.
A mirror-order rotation hypothesis (unmatched bundles following
the remaining TOC entries in order) fits the matched runs but is
NOT used to assign any name in this lane.

What this means for phases 6–12: the composites and renders built
from mirror packages in the identified runs now have
filename-grade identities (see ID-CORRECTIONS.md). The library
built from unassigned packages remains valid as *mirror-build*
content; it must not be cited as the named retail fighter's data.

## Tools

`tools/containment_p15.py`, `tools/containment2_p15.py`,
`tools/containment3_p15.py` (single-base walk — falsified model,
kept for the record), `tools/containment_scatter_p15.py`,
`tools/xpr2_fingerprint_p15.py`, `tools/graph_key_match_p15.py`,
`tools/package_spans_p15.py`, `tools/package_name_map_p15.py`,
`tools/merge_maps_p15.py`, `tools/iso_fetch_driver_p15.py`,
`tools/mirror_fetch_driver_p15.py`, `tools/afs_extract_p15.py`.
Machine-readable results: `containment-map.json` (per entry:
name, size, sha256, verdict, mirror offsets/segments,
pass-2/pass-3 coverage), `package-name-map.json`.

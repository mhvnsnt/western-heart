# DOA4 Phase 16 — CONTAINMENT-AUDIT-2 (scatter-pass completion)

Closes phase 15's disclosed deviations #dev-1/#dev-2: every
entry whose phase-15 verdict rested on probe-grade passes
(`piecewise_unresolved`, `absent_windows`) in chrtwo and
chrthree has now had the FULL piecewise reconstruction —
an exhaustive multi-resolution scatter over its own volume's
mirror stream — and jan02.tpr's absence has been re-verified
cross-volume in the same pass. Machine-readable results:
`phase16/containment-map-2.json` (additive: the full phase-15
map with a `p16_scatter` record attached per re-examined
entry, verdicts superseded only where the scatter changed
them, every change logged in `p16_changes`) and the raw
per-entry output `phase16/scatter2-results.jsonl`. Tooling:
`phase16/tools/scatter2_p16.py` (+ `afs_extract_p16.py`,
`mirror_materialize_p16.py`, `merge_map2_p16.py`).

## Inputs (all digest-verified before use)
- Entry bytes: re-assembled retail ISO, 30/30 parts each
  sha256-verified against release `doa4-iso-v1` digests as
  written; whole-ISO sha256 recomputed =
  `4423cd5ca0979e38b48fce3dbdd78de6416abfd4dd01fc8cc9140e2c92b104aa`
  — byte-identical to the closed retail ISO. Entries extracted
  with the phase-13 XDVDFS tree; every target entry's sha256
  asserted against the phase-15 map before scattering.
- Mirror streams (release `doa4-mirror-20261017`, parts 02–05
  each sha256-verified): chrone 366,094,336 B sha256
  `d6b99c60af3712a73a0a3901882c364ed1b613f55458bb400e066aa85e6000bc`;
  chrtwo 548,042,752 B sha256
  `a7ca3ec4cc18bbcef99cb46eca78c8e0086930be13df343abd9ee9f801548e75`;
  chrthree 762,955,776 B sha256
  `34eca0637d4c076503800aac89833ad0d8f27bc988e0097d8f53890c04482622`.

## Method
Per entry, a resolution ladder over its own volume's stream:
16 KiB pieces, then still-missing spans re-probed at 4 KiB,
1 KiB, and 256 B. All pieces of all targets at a tier are
searched in one Aho-Corasick pass (pyahocorasick; the VM's
build is str-only, so patterns/haystack are bridged through
latin-1 — 1 char == 1 byte — and the haystack is scanned in
64 MB chunks because the build widens it ~4× internally,
measured). Every candidate is verified BYTE-EXACT against
the full piece before being recorded. All-zero pieces are
recorded as zero (they match everywhere; not containment
evidence) and excluded from the non-zero coverage figure.
`absent_proven` means: zero verified pieces at EVERY tier —
the search is whole-stream and exhaustive at each piece
size, so absence is proven down to 256 B pieces with 24 B
windows. Per-tier state was persisted atomically (the pass
survived two OOM kills and two runtime restarts with no
tier re-run beyond the one in flight).

Tier yield (pieces found / pieces searched):
- chrtwo: 16 KiB 2,103/13,653; 4 KiB 1,970/46,067;
  1 KiB 6,481/167,230; 256 B 12,312/635,978.
- chrthree: 16 KiB 3,284/19,288; 4 KiB 5,954/63,781;
  1 KiB 27,863/225,912; 256 B 151,272/788,518.

Duplicate rows: chrthree's target list contains byte-identical
duplicate AFS entries (leiCA.tpr ×7 rows, hakAA.tpr ×7,
helAA.tpr ×5, korAA.tpr ×2 — same name, same sha256, same
size). 107 target rows = 90 distinct files; each distinct
file was scattered once and its result applied to every
duplicate row (all 107 rows appear in the outputs).

## Verdicts — 147 of 147 target rows resolved (147 changes logged)
- `piecewise_unresolved` → `scattered`: **104 rows**
  (chrtwo 38, chrthree 66) — every one has real, byte-exact
  pieces in its own volume's stream, with the full ordered
  piece map in the machine-readable map.
- `absent_windows` → `scattered`: **14 rows** — phase 15's
  absence-by-probe was wrong for these; byte-exact pieces
  exist (chrtwo: hyt02.cat 12.0863%, aya03.cat 74.7202%;
  chrthree: 12 rows incl. hakAB.cat 0.0531%, lisCA.cat
  0.5154% — some are fragments only, but present).
- `absent_windows` → `absent_proven`: **29 rows**, all
  chrthree `.cat` files (rtm04.cat, bay00.cat, bay01.cat,
  kasBA/CA/DA.cat, leiBA/CA/CB/CC/CD/CF/EA/GA.cat, ayaAA.cat,
  lisAA/DA/EA.cat, criAA.cat, korAA.cat, korAB.cat,
  einAA.cat, janAA.cat, boyAA.cat, hakAA/AC/AD/AE/AG.cat) —
  proven absent from the chrthree stream at every piece
  size down to 256 B. (Their `.tpr` twins all have at least
  fragmentary pieces; the catalog halves of these costumes
  simply do not live in this volume's mirror stream.)
- `fully_scattered` (100.0% coverage, a sub-class of
  scattered recorded in `p16_scatter`): **6 chrthree .cat
  files** — lis04.cat, spa01.cat, spa02.cat, spa04.cat,
  spa05.cat, spa06.cat. No chrtwo target reached 100%
  (best: hak11.cat 87.1186%).

Coverage character: chrthree's spa*/lis04/hel* families are
nearly whole in their own stream (85–100%); the AA/BA/CA…
costume-variant entries are mostly fragments (0.04–7.8% for
many `.tpr`s) — their bulk lives in the other volumes'
streams, consistent with phase 15's whole-map picture.
chrtwo `.cat` files run 12–87%, `.tpr` files 0.97–34.7%
(lei10.tpr lowest at 0.967% — present, barely).

Union mirror coverage (all entries, phase-15 segments +
phase-16 segments, mirror space):
- chrtwo: 51.1871% → **52.0069%**
- chrthree: 48.2684% → **50.6650%**

## jan02.tpr (chrone) — absence OVERTURNED
Phase 15 recorded jan02.tpr's chunks as absent from all
three mirror streams at 16 KiB granularity. The exhaustive
pass finds jan02 pieces in ALL THREE streams:
- chrone (own volume): 0 pieces at 16 KiB (consistent with
  phase 15's granularity-limited observation), but 123
  verified pieces at finer tiers = 71,424 B (0.7285%).
- chrtwo: 150 pieces = 480,768 B (4.9039%), including 24
  full 16 KiB pieces — so even the 16 KiB-granularity claim
  does not hold for the cross-volume probe.
- chrthree: 140 pieces = 75,776 B (0.7729%).
Verdict: `scattered_cross_volume`. jan02.tpr is NOT
reconstructible from any single mirror stream (>95% missing
in each), but it is not absent: it survives as small
fragments distributed across all three volumes — the same
fragment pattern as the AA-variant costumes above.

## What this closes and what it does not
Phase 15's containment question is now answered at
reconstruction grade for every entry it left open: each of
the 147 rows has either an ordered byte-exact piece map
(118 rows) or a proof of absence at 256 B granularity
(29 rows), and jan02.tpr's status is corrected on the
record. Nothing here changes the phase-15 verdicts for
entries outside the target set, and the phase-15 map file
itself is untouched — supersession lives only in
`containment-map-2.json`'s per-entry records and its
`p16_changes` log.

# Tekken 6 PSP — ROUND 12 JOB 4 (B3 ANOMALIES): all four anomalies resolved or bounded with direct evidence

Date: 2026-10-22, round 12. Script: `round12-evidence/j4_b3_anomalies.py`;
machine-readable results: `round12-evidence/r12_b3_anomalies.json`.
Method addition over round 11: every container in the segments
below was **re-decoded directly** from the bulk slice (zlib,
adler-verified path of the round-7 census) and its decoded bytes
scanned — not just its slot map.

## (a) The 5 double-size segments (1, 17, 20, 23, 25) — NO hidden anchor; two kits, one anchor, shared core

- **Direct interior scan (new):** in all 1,807 containers of the
  five segments, the count of `BONE` fourccs in the decoded bytes
  equals the slot-map BONE count exactly — **zero BONE sections
  exist outside slot starts, and zero hidden midpoint anchors
  exist in the bytes.** The round-11 slot-map negative is now a
  byte-level negative. The segments are NOT split (there is
  nothing to split at).
- **What doubles:** every class roughly doubles vs modal
  segments (boned parts 181–222 vs 92–105; B-textures 86–113 vs
  37–47), and — the discriminating measurement — each double
  segment contains **18–29 byte-identical duplicate containers**
  (sha256 extras: seg 1: 29, 17: 29, 20: 18, 23: 29, 25: 26),
  while four modal control segments (0, 2, 5, 10) contain
  **exactly 0** internal duplicates each.
- **Bounded verdict:** a double segment = **two near-complete
  kits under the one anchor, sharing a ~29-part byte-identical
  common core**. Two independent characters' kits would share
  ~0 parts (the modal segments' internal-duplicate rate is 0,
  and no second anchor-pattern base exists in the bytes —
  every proven character in this data owns exactly one such
  base). The reading consistent with all evidence is a second
  costume/form (2P-variant-class) kit of the anchor's
  character, re-referencing the shared core parts — stated as
  the bounded conclusion, with the alternative (a second
  character whose base package deviates from the anchor
  pattern) recorded as not excludable from census data alone
  but unsupported by any byte found. Assignments stay as
  round 11 labeled them (contiguity-inferred; not split).

## (b) Stub segment 26 — a compact reduced kit, not an empty stub

29 containers under anchor n=5247 (the 129-bone anchor, (c)):
1 full-char anchor, 12 B-textures, 8 rigid parts, 4 boned
parts, 2 stage-pattern, 2 dir-other (full listing in the
script output / JSON summary). Verbatim slot-11 name chunks
include `prac`, `kata`, `silv`, `cmn_`, `bon1`, `miss`, `tfm_`
(no identity claimed from them). Its boned parts are small
(BONE 656 / 432 / 8,672) except the anchor itself and one
8,032 part (`prac`). The segment is "stub" only in count: it
is a **reduced kit** — a fraction of a modal kit's ~90 boned
parts — consistent with a variant/bonus package set whose
remaining parts live outside this segment. Bounded as such.

## (c) Closing anchors' BONE 9,440 / 9,696 — SOLVED: 129- and 132-bone body skeletons

BONE layout (proven on five sections: N=22/110/129/132/146):
`size = 64 + 4N (parents) + 12N (translations) + 12N (Eulers)
+ X (middle sections) + 32N (names) + 12N (scales) + pad-to-16`,
verified byte-exact against each section's own offset table.

- Anchor 26 (n=5247) slot 1: **N = 129** (read at BONE +16;
  table (64, 580, 2128, 3676, 0, 3756, 7884, 0), X = 80):
  64+516+1548+1548+80+4128+1548+8 = **9,440** ✓.
- Anchor 27 (n=5276) slot 1: **N = 132** (table (64, 592, 2176,
  3760, 3852, 3884, 8108, 0), X = 124):
  64+528+1584+1584+124+4224+1584+4 = **9,696** ✓.
- Both anchors' head slot 12 is the standard N=22 / 1,664.

**Verdict:** the closing anchors are a different skeleton
class — **expanded body skeletons of 129 and 132 bones**
(standard body = 110; the roster's other outlier is idx04 at
146) with standard 22-bone heads. The atypical BONE sizes are
fully explained by bone count; no format variant is involved.

## (d) Segment 27's 42-strong stage cluster — SEVERAL stages' objects, not one stage

The 42 stage-pattern containers carry **34 distinct full slot
signatures**; container lengths span 22,528–273,088 and slot-9
payloads 13,808–132,976+. All share the stage-pattern skeleton
(624 B NDPP node + 48 B slot 6 + 2,384 B slot 7 + `tfm_` name),
but their slot-8/slot-9 payloads differ almost per container.
Cross-read against the 16 known top-76 stage packages (same
pattern, one package per stage, payloads 61–218 KB varying by
stage): the cluster's spread matches a pool of **several
stages' object packages** appended at the slice tail — it is
2.6× the entire top-76 stage-package count by itself and does
not reduce to one stage's repeated objects. It stays
`unassigned` in the round-11 assignment (correctly), now with
its composition bounded: a multi-stage object pool, not a
per-character kit and not a single stage.

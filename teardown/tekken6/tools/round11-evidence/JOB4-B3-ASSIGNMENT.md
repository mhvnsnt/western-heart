# Tekken 6 PSP — ROUND 11 JOB 4 (B3 ASSIGNMENT VIA DATA401 INDEX ORDER)

Date: 2026-10-22, round 11. Script: `round11-evidence/j4_assign.py`;
deliverable: `round11-evidence/r11_b3_assignment.json` (every one of
the 5,470 slice containers labeled). Source order: the round-7
census (`round7-evidence/r7_census.json`) — containers in bulk
(DATA401 entry-87 slice) order, each with bulk offset + sha256.

## Method

Anchors = the 28 slice containers matching the full-character
pattern (BONE slot 1 + NDPP slots 0/10 + BONE slot 12 of 1,664 B) —
the same structural pattern the 12 proven top-76 character
packages carry. Hypothesis TESTED (per brief): the containers
between two anchors belong to the preceding anchor's character
(index-order contiguity). Stage-pattern containers are NEVER
assigned to a character. Character IDENTITY is not claimed for
any segment: slice slot-11 name chunks are the same generic
`kao_…`/`MODEL_HEAD` strings as the top-76 packages (verified on
idx00/01/04/05) — they name face/head objects, not fighters.
Segments are numbered, not named.

## Score of the contiguity hypothesis — STRONG structural support

1. **A/B interleave is exact**: the container immediately after
   every anchor is a B-texture package — 28/28. (Matches the
   round-7/10 pairing observation: a character's A package is
   followed by its B texture package.)
2. **Segment uniformity**: 21 of 28 segments hold 158–196
   containers with a near-constant kit: 89–116 boned parts,
   34–48 B-textures, 11–16 rigid parts, 8–19 dir-other, and
   4.0–4.8 MB total. Random slicing of the bulk would not
   produce 21 near-identical blocks walled by full-char anchors.
3. **Roster arithmetic (consistency, not identity proof)**:
   12 proven top-76 character packages + 28 slice anchors = 40
   full-character packages — the Tekken 6 PSP roster size.
4. **The constant 6–7 "stage-pattern" containers per segment**
   are uniformly distributed (not clustered), i.e. inside
   segments they behave like a per-character repeated class
   (624 B node + large slot 9 — plausibly per-character effect /
   item packages), NOT like stage blocks. They are still left
   `unassigned` (conservative): the class name comes from the
   top-76 stage packages and the per-segment reading is
   unproven. The one true stage cluster is the tail: segment
   27's trailing block carries 42 stage-pattern containers.

## Anomalies (reported, not smoothed over)

- **Five double-size segments** (1, 17, 20, 23, 25): 337–385
  containers, every class ≈ 2× the modal segment (e.g. seg 1:
  222 boned / 101 B-texture / 13 stage vs modal ~107 / ~45 /
  ~6.5). A search for a hidden midpoint anchor (near-full-char
  slot maps: BONE 8,032 + BONE-12 1,664 + NDPP 0/10) found NONE
  — the only score-4 hits are ordinary boned parts (the 8,032 B
  BONE is the standard part-skeleton size everywhere). Two
  readings remain open: (a) these characters genuinely carry
  ~2× parts (extra costume/form sets), or (b) one character's
  base package in each pair deviates from the full-char pattern
  somewhere the slot-map census can't see. The assignment does
  NOT split these segments.
- **Segment 26 is a stub** (29 containers, 0.86 MB) between
  anchors n=5247 and n=5276, and both closing anchors are
  atypical: BONE slot-1 sizes 9,440 / 9,696 (all other anchors:
  8,032 / 10,768 family), anchor 27's whole package is 26,224 B
  with a 7,056 B slot 0. Flagged as atypical-anchor territory
  (variant/bonus packages are a plausible class — NOT named).
- Segment 27 (the last) is half modal size in boned parts (45)
  and carries the 42-strong stage cluster — its non-stage
  containers are labeled inferred like the rest, but the
  segment is the weakest in the table; treat its tail with
  suspicion.

## Assignment counts (the deliverable's labels)

| Confidence | Count | Meaning |
|---|---|---|
| anchor-proven | 28 | the full-char anchors themselves (structure-proven; identity unnamed) |
| contiguity-inferred | 5,206 | boned-part / rigid-part / B-texture / dir-other / A-other containers inside a segment, assigned to that segment's anchor — INFERRED, labeled as such in the JSON |
| unassigned | 236 | all stage-pattern containers (incl. the per-segment 6–7 and the tail cluster) |

Per the brief: inferred assignments live ONLY in
`round11-evidence/r11_b3_assignment.json` + this doc. Nothing
was copied into per-character model dirs. COM-file ordering
(idx58–75, @624 names LAW..ZAFINA) was cross-read as the game's
own character order but does NOT map onto slice segments —
no byte-level link between COM positions and slice anchors was
found, so no segment carries a fighter name.

Route-3 cross-read for Job 1 (palette) is recorded here as
briefed: the COM moveset files' tables and this census give
per-character PART references (this assignment), but neither
contains a per-unit bone table — no palette evidence found in
either; the palette question stays with the EBOOT draw code
(Job 1).

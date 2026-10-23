# DOA4 Phase 11 — Job 2: head-origin reseat (skin-weight read → measured anchors → viewed gates)

Tools: `phase11/tools/head_weight_read.py` (weight mass per joint),
`head_bind_read.py` (dominant-joint bind = inverse-IBM translation),
`head_skinbind.py` (true skinned bind bounds), `neck_measure.py`
(center-column junction measurement), `composite_ab.py` (A/B anchors),
`composite_final.py` (the shipped batch). Full numeric tables in scratch
`p11/head_weights.json`, `p11/head_bind.json`, `p11/head_skinbind.json`.

## The weight read (all 42 head packages, chrtwo pkg04–45)

- Every head's geometry is dominated by ONE skin joint (45–96% of total
  weight mass); the skinned bind pose equals the raw positions
  (World·IBM = identity — the phase-6 assembler baked bind into positions),
  so a head package renders in package-local space, Y ∈ [−0.79…+0.29].
- The dominant joint's bind position splits heads into two flavors:
  **bind-at-origin** (04, 05, 06, 07, 09, 23, 24, 27, 29, 30, 32, 41–45) and
  **bind-at-anchor** (08, 10–22, 25, 26, 28, 31, 33–40 — dominant joint binds
  at a body-family head position, e.g. (0, 0.478, −0.020)).
- **The bind flavor does NOT decide the float.** Counterexamples both ways:
  pkg08 (anchor-bound) seated in phase 10 while pkg33 (anchor-bound) floated;
  pkg29 (origin-bound) seated while pkg09 (origin-bound) floated. Phase 10's
  "bind-node-local" label is therefore superseded by the measured rule below.

## The operative rule (measured, then proven by viewed renders)

Measure each head's **center-column bottom**: the 1st-percentile Y of
vertices weighted ≥0.5 to the dominant joint with |x| ≤ 0.04
(`neck_measure.py`). Two classes:

- **Deep class** (bottom ≤ −0.136): geometry (neck/hair/collar mass) reaches
  well below the package origin → the phase-10 neck-base anchor
  (headY − 0.080) seats them. All 11 phase-10 seated heads are this class.
- **Floater class** (bottom ≈ 0.00…+0.04): NO center-column geometry below
  the origin — the package's neck segment is fragmentary (the known neck-decl
  gap) and its origin sits one neck segment higher than the deep class's.
  The phase-10 anchor leaves a ~0.10 air gap (reproduced and viewed in the
  A/B batch: `composite_ab.py`; raising to the head-joint anchor made it
  strictly worse, also viewed). Correct anchor, measured per head:
  `anchor = bodyTop99.9 − headBottom` (body top = 99.9th-percentile
  center-column Y of the body GLB), which lands 0.083–0.133 BELOW the
  phase-10 anchor for every floater.

## Reseat results — every rebuilt composite gated by a VIEWED front render

| composite | class data (dom joint, frac, bind, headBottom) | anchor | verdict (viewed) |
|---|---|---|---|
| chrone10+pkg09 | node7, 76%, origin, +0.012 | 0.283 | **SEATED** — `renders/p11-composite-chrone-pkg10+chrtwo-pkg09-rs.png` |
| chrone10+pkg33 | node7, 91%, (0,0.478,−0.024), −0.003 | 0.298 | **SEATED** — `renders/p11-composite-chrone-pkg10+chrtwo-pkg33-rs.png` |
| chrone00+pkg18 | node20, 64%, (0,0.483,−0.022), +0.012 | 0.303 | **SEATED** — collar wraps the junction |
| chrone00+pkg19 | node20, 55%, (0,0.483,−0.022), +0.028 | 0.303 | **SEATED** |
| chrone00+pkg20 | node20, 64%, (0,0.483,−0.022), +0.012 | 0.303 | **SEATED** |
| chrone17+pkg21 | node6, 92%, (0,0.468,−0.025), +0.002 | 0.305 | **SEATED** |
| chrtwo50+pkg25 | node8, 80%, (0,0.477,−0.041), +0.034 | 0.264 | **SEATED** — cat-ear head's neck column meets the torso |
| chrone17+pkg07 (marginal) | node7, 72%, origin, −0.249 (deep but narrow-neck) | 0.338 | **CONNECTED** — no air gap at either anchor (nb render also committed); the long visible column is the package's own neck geometry, not a placement gap. Marginal closed. |

All 7 phase-10 floaters are reseated and seated. Rebuilt composite GLBs are
in scratch `p11/composites/` (rebuildable via `composite_final.py`); they
supersede the floater versions in scratch `p10/composites/`.

## Extensions — every remaining DISTINCT head with a proven pairing

Distinct-head census (phase 9, md5): 31. Phase 10 built 20. Remaining
distinct heads with a phase-10 pairing: pkg10 and pkg43 (pkg43's render
existed but was never viewed). Plus two pairings the weight read itself
proves (next section): pkg22, pkg31.

| composite | anchor | verdict (viewed) |
|---|---|---|
| chrone14+pkg10 | 0.284 (rs; A/B vs nb 0.501 — nb floats badly, both committed) | **SEATED** — pkg10 is floater-class (headBottom +0.029), unlike its near-twin pkg11 (deep, −0.187): the twins are different origin classes despite near-identical census stats |
| chrtwo50+pkg22 | 0.258 | **SEATED** — new pairing (proof below) |
| chrone07+pkg31 | 0.345 (rs; A/B vs nb 0.445 — nb floats, both committed) | **SEATED** — new pairing (proof below); long-haired head + katana on the group-C armored body |
| chrtwo50+pkg43 | 0.397 (phase-10 nb) | **SEATED** — phase-10's unviewed render gate now closed with a fresh viewed render; long neck column is continuous geometry |

**Distinct composites now: 23 / 31.** The 8 distinct heads still unpaired:
pkg05, 06, 23, 24, 26, 27, 28, 32 (below).

## Two NEW pairings proven by the weight read (stated proof)

Phase 10 left 9 packages unpaired because their ROOT anchor copies are
identity matrices. The skin palette carries the true family bind:

- **pkg22 → family (0, 0.477, −0.041)** (bodies chrtwo50–55, chrthree02–07):
  dominant joint node 6 carries 88% of the weight mass and binds at exactly
  (0, 0.477, −0.041) — Δ = 0.000 against the family anchor, the same standard
  phase 10 accepted for its 20 pairings. Composite built on chrtwo50 and
  viewed seated (above), corroborating.
- **pkg31 → group-C family (0, 0.525, −0.025)** (bodies chrone06–09,
  chrtwo00/31, chrthree29–31): dominant joint node 8 carries 96% of the
  weight mass and binds at exactly (0, 0.525, −0.025), Δ = 0.000. Composite
  built on chrone07 and viewed seated; the head (long straight hair,
  katana over the shoulder) is visually consistent with the group-C ninja
  bodies.

## Still unpaired (7 packages / 8 distinct) — no proof available

- pkg05, 06, 23, 24, 27: dominant joint binds at the ORIGIN (no family
  signal in roots or skin). pkg24/27 are the 15-joint rigs.
- pkg26: dominant binds at (0, 0.277, −0.030) — no body family exists at
  0.277. pkg28: binds at (0, 0.310, −0.041) — no family at 0.310.
- pkg32: dominant binds at origin.
These stay unpaired and listed, per the job's rule. Alternate evidence
(TX2D colors / slot adjacency) was not produced this phase.

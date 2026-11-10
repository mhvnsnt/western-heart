# Hair Fit — Lane 12 Addendum: the continuity fix, its verdict, and the rim-travel finding

Companion to REPORT-draft.md (research + diagnosis + gate history through lane 11).
This addendum covers lane 12's work: implementing the continuity-constrained
projection (refit_v5), running it, and what its failure proved.

## What was implemented (method change, gate untouched)

`scripts/refit_v5.py` = `refit_v4.py` with ONLY the final-stage placement replaced
(rounds, reconcile diffusion, gate block, and write path verified byte-identical
by diff; the gate block differs only by a diagnostic npz dump inside the failure
branch, written after the verdict is computed). `scripts/continuity.py`:

- `query_full`: HeadSurf.query + the winning patch-tri index and bary coords.
- Assignment, computed once at final-stage entry over the cap's weld groups:
  seeds = anchor groups whose global assignment is locally coherent (>= half of
  anchor-group neighbours' global q within 25 mm); multi-source BFS over the
  welded group graph; each newly reached group inherits its neighbour's tri and
  WALKS on the surface (greedy edge-crossing descent, strict decrease only) to
  its local closest tri — the walk cannot flip sheets, it stops at local minima
  such as the fold's groove bottom. Unreached components fall back to their own
  global tri.
- Placement: anchors and pushed verts go to closest-point ON THE ASSIGNED TRI +
  offset along the tri's barycentric-interpolated vertex normal. Detection and
  the GATE stay on the global query. Gate numbers unchanged.

Offline validation on the torn v4 final state (tmp/diag_field.npz,
tmp/test-continuity.log): baseline gate arithmetic reproduces exactly (growth
max 3.80, bad 4); intra-group spread 0.000 mm; assignment healthy (99/106 anchor
groups coherent seeds, 7 incoherent = the fold groups, BFS assigned 1097,
0 fallback, walk max 58 steps).

## Afro run verdict (tmp/refit-afro-v5.log)

- Rounds byte-match v4 (inside 148/144/148; anchor err p95 33.13/32.28/31.59 mm).
- Assignment at entry: identical stats to the offline test (99 seeds,
  7 incoherent, walk max 58 steps).
- Final iter 0 converged, inside 0; reconcile iter 0 converged, inside 0.
- Anchor terms are the best recorded: |sd − standoff| p50 0.01 / p95 0.04 /
  **max 0.05 mm** (v2/v4 max was 0.15–0.16 mm).
- **GATE FAILED — not writing: growth p50 0.95 / p99 1.37 / max 3.83; max edge
  93.6 mm (orig 27.6); bad 4; anchor inside 0.** Same tris: 553/554/1848/1849.
  Full gate history is now: v2 FAILED (3.79), v4 FAILED (3.80), v5 FAILED (3.83).

## What the v5 failure proves (tmp/diag-v5-afro-dome.npz)

The continuity machinery worked as designed: the fold verts no longer teleport
to a single opposite sheet (vert 1192 shifted 8.1 mm and vert 3756 11.3 mm
relative to the torn v4 state; the cluster lands on a third, intermediate,
topology-coherent locus, and every anchor sits within 0.05 mm of its standoff
target). The tear persists because the 8 rim verts' final loci genuinely span
~70–95 mm of surface arc (z from −0.081 to +0.010 at near-constant height,
the sideburn band) while their authored spacing is 15–24 mm.

Root cause, one level deeper than the q-jump: **the rim itself must travel.**
The authored dome's temple rim verts sit at h −0.118…−0.144 in the head frame
(lane 8's diag_inside: 20 authored verts inside, temples, sd p50 −9.9 mm) —
wrapped under the ear/jaw. Her own authored scalp cap (bodyscalp.npz, the
body's bundled AngelHairScalpCap) puts the true temple hairline boundary at
h +0.047 (right, az 108°) / +0.055 (left) — roughly 165–190 mm above where
those rim verts were authored. FIT5's delta field, which every refit since
inherits and diffuses, already contained this travel in torn form; placement
variants (global, reconciled, continuous-sheet) only choose WHERE the travel
tears, not whether.

Arithmetic of the impossibility: an original edge that must fund ~40 mm of
rim travel grows ~3.7× at best (observed top edge growth 2.5–2.7 in the
next-worst tris 1787/1788/550/1768 — the travel is already distributed as far
as this parametrization allows). The authored dome's rim triangulation is
uniform (per-tri max-edge 14.8–27.6 mm, min edge 1.66 mm, zero degenerate
tris — lane 10), so no local slack exists. **The ≤2.0× growth gate + this
dome + a hairline-true fit are jointly unsatisfiable by placement alone,**
for any projection method, because the gate implicitly freezes the rim's
vertex distribution and the fit requires re-spacing that distribution along
a ~90 mm longer rim path at the temples.

## The missing ingredient (decision for the parent)

A **rim re-parametrization** — the weave-track rebuild, in the standard's own
terms: the cap's rim verts are placed BY CONSTRUCTION on the offset scalp-cap
boundary curve (bodyscalp boundary per azimuth sector, +1.5 mm standoff) at
even arc spacing, adding/re-spacing rim verts along the temple climb; the
interior then blends to that rim through the existing diffused delta field +
reconcile machinery, with the same gate measuring the result. The gate
arithmetic, thresholds, and target surface do not change; what changes is the
dome's rim vertex distribution, which all placement-only refits implicitly
froze. This is a change to what the gate implicitly assumed, so it is escalated
as a method decision rather than applied silently. Affected scope is small:
12 rim verts in 2 clusters today; the rebuild touches the rim band only
(dome interior + FIT5 mass untouched).

Until that decision lands, FIT5 remains the best afro candidate on disk
(mass clean; dome = the inherited fit, REJECTED by parent own-eyes for the
ribbons — which are precisely this temple tear rendered). No afro winner is
claimed by this lane.

## Straight cap — GATE PASSED (tmp/refit-straight-v5.log)

As predicted, the straight cap carries NO rim travel: its assignment came
back **498/498 anchor groups coherent, 0 incoherent** — the FINAL tear was
pure q-jump, exactly the class the continuity fix addresses. Run record:

- Rounds: inside 257 → 232 → 219, anchor err p95 ~6.0–6.3 mm (vs the afro's
  ~32 mm — the straight delta field is far closer to its surface).
- Final loop: pushed 53 inside verts, converged iter 1, inside 0.
  Reconcile loop: pushed 58, converged iter 1, inside 0.
- Anchor |sd − standoff|: p50 0.00 / p95 0.02 / max 0.67 mm.
- **GATE: growth p50 0.78 / p99 1.05 / max 1.66 (limit 2.0); max edge 12.6 mm
  (orig 15.0); bad tris 0; anchor inside 0.**
- Wrote `out/megami-hair-angel-straight-REFIT.glb` (11,606,864 B — same size
  as FINAL; cap POSITION accessor only). FINAL's record was 16 bad tris /
  max edge 60.4 mm; the REFIT is the straight winner.

The contrast between the two parts is the cleanest statement of the whole
diagnosis: same solver, same gate, same continuity machinery — the part
whose rim only had to *seat* (straight) passes with margin; the part whose
rim has to *travel* ~90 mm up the temple (afro) cannot pass any placement
method under a frozen rim parametrization.

## Straight REFIT — measurements

- topology_check vs ORIGINAL (scripts/topology_check.py): cap growth
  p50 0.78 / p99 1.05 / max 1.66, bad 0, mid 0 — identical to the gate.
  Headband prim untouched by the refit: positions identical to FINAL's
  (accessor audit below), its apparent "growth" 0.45 is vs the ORIGINAL
  because FINAL had already re-seated the band. Strand prims (p1/p2):
  growth vs ORIGINAL is FINAL's inherited seating, byte-identical here.
- Accessor audit (FINAL → REFIT): 19 accessors total, exactly ONE changed —
  mesh1/prim0 (AngelCap) POSITION. Strands, headband, normals, UVs, indices
  all byte-identical to FINAL.
- measure_rim on the closed surface: cap 0.0% inside everywhere. Cap-RIM
  proxy (lowest-h 3% per 30° sector, n=78): TEMPLE p50/p90/max = 1.5/1.5/1.5
  mm, 0% >2 mm; NAPE 1.5/1.5/1.5 mm, 0% >2 mm; FRONT p50 0.64 mm but p90
  7.39 / max 8.15 mm — 3 of the 9 front rim-proxy verts sit up to 8.15 mm
  off the surface (a sparse-sector small-n effect: the front rim's lowest
  verts include a few parting/fringe verts that sit proud by design).
  Verdict on the rim: temples + nape sit exactly at the 1.5 mm standoff
  with zero ring; front is tight at p50 with a small proud fringe subset.
  Headband (not refit): floats 5.7–11.8 mm off the surface as shipped in
  FINAL — unchanged by this lane, flagged for the parent (the stage's
  band on/off proofs exist from earlier lanes).

## Straight REFIT — proof frames + a stage finding (own-eyes)

Full set shot on the standard stage (:8843 stage, hair.glb → REFIT, brown
eye, band meshes present): face, face34, front (full body), top; the tq
camera at 640×960 framed below the head (body-only frame — kept on disk as
straight-refit-tq.png, no hair evidence in it). Parent-own-eyes items:

- The cap's forehead edge is CLEAN: no torn band, no floating shards across
  the forehead (FINAL's face frame shows grey shard planes + a light patch
  at the same place). The temple/side seating reads continuous.
- BUT the frames show a smooth black dome over the crown (front frame AND
  the face34 frame, proof/straight-refit-face34.png — a hard straight
  vertical cap edge also cuts down in front of the ear there, the same
  defect family the parent flagged on the GNM face frames). Measured cause
  (POSITION audit, ALL prims): the flattening is in the STRANDS too and
  was introduced by the predecessor FINAL, not by v5. Per-prim max y /
  verts above 1.80: ORIGINAL cap 1.853/654, black strands 1.875/26422,
  blonde 1.848/1838 → FINAL cap 1.752/0, black 1.783/0, blonde 1.761/0 →
  REFIT identical strands (byte-proven), cap 1.778/0. FINAL's whole-part
  field compressed the crown ~90–100 mm; v5 changed only the cap shell
  and partially recovered it. Everything above y 1.80 was deleted from the
  part by FINAL, so the strand mass no longer covers the crown and the
  smooth cap shell shows through as a bald dome. This is a whole-part
  VOLUME/height defect inherited from FINAL, NOT a seating defect: the
  rim evidence above stands. It belongs to the same class of decision as
  the afro rim rebuild (the part needs its crown profile restored toward
  the authored heights across all prims — a field rebuild, not a
  placement change) and is escalated with it.
  **RING VERDICT (straight): PASS at the rim (temples/nape exact 1.5 mm,
  0% inside, no ring/tear at the hairline in either frame shot);
  CROWN verdict: FAIL — inherited whole-part crown flattening (FINAL),
  needs the parent decision below before this can ship as the
  standard-meeting winner.**

## Decisions escalated to the parent (both are field/parametrization changes)

1. AFRO: rim re-parametrization (weave-track rebuild) per the section above.
2. STRAIGHT: crown-height restoration — re-derive the delta field for ALL
   prims (cap + strands) so the crown profile returns toward the authored
   heights (cap 1.853 / black strands 1.875 / blonde 1.848) while keeping
   the v5 seating (which is gate-proven). Concretely: a delta field
   anchored on the ORIGINAL part instead of FINAL above the seating band,
   or a height-profile blend; either re-opens the field the gate diffuses,
   so it is a new refit variant (v6), not a tweak of the landed REFIT file.

# Pilot 2 v2fix — forearm S-curve warp: attribution + fix (2026-11-09)

## Verdict
The warp lives in the **AngelBody morph build stage** — not in the source
blends, not in the rig, not in the export bind, not in the v4 game GLB.
`megami-angel-pilot2-v2fix.glb` on release `megami-pilot2-20261108` carries
the fix; the original asset is kept untouched beside it.

## Stage attribution (measured, attribute_model_defects method)
- Export bind is clean: JW·IBM = Identity on the shipped v2, max err
  1.54e-05 (v1: 1.36e-05). Inverse bind matrices are innocent.
- Basis geometry is byte-identical between v1 and v2 (all basis arm metrics
  equal to the decimal). The warp exists only at AngelBody = 1.
- Stored morph defaults verified in file: AngelFace = 1, AngelBody = 1.
- The AngelBody key was built in `_pilot2-v2-20261108/scripts/blend_ops.py`
  (lines 363–458) as an analytic height field — radial r(z) + shift(z) from
  control curves, gaussian-smoothed — applied per-vertex to every vertex.
  The diagonal forearm tube crosses the field's steep-gradient waist and
  shoulder bands, so each arm cross-section is sheared by the field's
  spatial gradient across the tube.

## Measurements (cross-section instrument, arm tube binned along its arc)
- Within one forearm cross-section, the shipped AngelBody delta varies by
  up to 21.7 mm (x std). Sections are radially stretched: major radius
  20→33 mm and 18→28 mm vs basis.
- Tube spine angle: basis 1.8°/0.8° (mid-tube bins) → shipped 19.1°/18.8°.
- Replicating the paper field from blend_ops.py in GLB coordinates does
  NOT reproduce the shipped deltas (arm-vertex error up to 10.7 mm), so the
  correction was derived empirically from the shipped file itself.

## Fix (fix_angelbody_arms5.py — Laplacian de-shear of the delta field)
Adjacency-Laplacian diffusion (400 iterations, λ=0.5, graph from the
primitive indices) of the AngelBody delta over arm-influenced vertices
only (Σ arm-joint weights > 0.02); all other vertices held fixed as
boundary conditions. The within-section shear (high-frequency) is removed;
the along-tube lengthening (low-frequency) survives. Only AngelBody
POSITION records of touched vertices were rewritten.

## Verification
- Within-section std(Δ): 7–22 mm → 0.2–1.7 mm.
- Section radii restored to basis: bin5 (33,21)→(20,18) = basis (20,18);
  bin6 (28,17)→(18,16) ≈ basis (18,15).
- Mid-tube spine angles 19.1°/18.8° → 1.5°/1.4°; the ~17° remaining at the
  elbow/wrist bins matches the basis pattern.
- Preservation audit at byte level: the BIN diff between v2 and v2fix is
  92,905 bytes, ALL inside the 5 patched AngelBody POSITION accessor
  ranges (accessors 111, 594, 3492, 4941, 7866). JSON diff = only the
  min/max scalars of accessors 111/3492/4941. Textures, basis geometry,
  the other 475 morph targets, indices and weights are byte-identical.
  Max per-vertex correction 48.6 mm.
- Morph target count on the body mesh is 476 (474 originals + AngelFace +
  AngelBody last) — the build brief's "480" was approximate; 474 is the
  real original count, all preserved.

## Files
- Fixed GLB: release `megami-pilot2-20261108`, asset
  `megami-angel-pilot2-v2fix.glb`, 59,108,500 B,
  sha256 4a96ce087ad262ffbbb9ad730ef43cf7a14d00c7df7c02a7fec49ee4a114fbdb.
  Original asset `megami-angel-pilot2-v2.glb` kept.
- Proofs (this PR): hero front + back on the dark standard stage
  (#14121c, Neutral 1.1, 3-point rig) with the fixed afro + Angel-brown
  eyes, plus forearm close-ups front/side, in
  `docs/proof/2026-11-09/megami-hero-v2fix/`.

## Caveats
- The glossy/oiled skin sheen under the standard stage (parent-flagged on
  the original hero set) is unchanged — it is a stage-lighting property,
  not part of this defect.
- AngelBody = 0 still shows the basis mesh on the field-moved deform rig
  (the v2 build's known frame caveat); untouched by this fix.

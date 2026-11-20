# MEGAMI BODY REBUILD — AngelBody replaced parametrically (2026-11-09)

Owner orders 2026-11-09 ~09:18–09:23 CST: the hand-built AngelBody morph field
comes OUT ("I can tell ur hand tooling instead of wiring up and using the best
of the best"); height/shape and skinning are SEPARATE operations and the
rebuild must prove it ("It wasn't supposed to mess up any skin weights when
you made the motherfucker taller"); hips/ass width + depth EQUAL to the
original Megami body ("u narrowed her thick frame out a bit with the
stretch"); the default body/height (fixed v4, attire1, PR #1694) stays
preserved untouched as the return-to state — the Angel build is its own
variant file, and if the Angel height cannot be hit with hips + weights
intact, the saved default ships instead. **All gates pass; the Angel build
ships.**

## What shipped

- `megami-angel-pilot2-v3.glb` on draft release `megami-pilot2-20261108`
  (originals kept: v1, v2, v2fix all still there): **59,095,772 B,
  sha256 `47e0c6dfaec4afc6a799a2999813672d3a204abd3f17d7c938efb6f3788d67e5`**.
  Built from the v2 GLB with ONLY the AngelBody target (34 accessors), the
  skeleton node locals, and the inverse bind matrices changed — byte-level
  audit below. Tattoo textures byte-identical; AngelFace byte-untouched
  (the face redo is the GNM lane's, not this lane's); all 476 morph targets
  present, 475 byte-identical to v2.
- The fixed v4 default (`roster/parvati/attires/attire1/model-rigged.glb`,
  PR #1694) was NOT touched.

## Step 1 — the hand-built field's measured footprint (v2, ON vs OFF)

Cross-section instrument (dominant-joint regions + arm-tube bins + torso
slabs; lane scratch `results/footprint-v2.json`):

| region | max within-section delta std |
|---|---|
| shin | 36.2 mm |
| forearm | 29.8 mm (PR #1693's finer instrument: 21.7 mm, radii 20→33 mm, spine 1.8°→19.1°) |
| thigh | 28.2 mm |
| torso | 14.9 mm |
| hand | 11.6 mm |
| bust | 7.7 mm |
| upper arm | 7.6 mm |
| shoulder | 3.9 mm |
| neck | 1.3 mm |
| head | 0.8 mm (pure translation, +275 mm) |

Waist slabs (GLB y 0.90–0.94): width +11–15%, delta std 7.8–10.4 mm — the
radial peak (×1.20) and its gradient. Underbust slab (y 0.94): width +20 mm,
std 7.8 mm — the field's tail reaching the bust (the owner's "her tits").
Hip band (same verts, y 0.70–0.79): width99 0.3393→0.3427, depth99
0.2374→0.2383 — the field did not cut absolute hip width on the hip verts
themselves; it ballooned the waist (+11–16%) and stretched stature,
collapsing the hip/stature ratio 0.264→0.213 — the visible "narrowed thick
frame." Mechanism: the field (blend_ops.py `body` stage) is a function of
world z alone — vertical shift + radial r(z) applied to every vertex by
height band, anatomy-blind; a diagonal arm tube crossing the steep-gradient
bands is sheared by construction.

## Step 2 — route: MPFB2 parametric donor + cross-section profile transfer

Licence-clean per the Build-A-Bitch survey (physics-playground-pwa
docs/build-a-bitch/): MPFB2 = "primary body system" (CC0 data); Anny's
architecture = parametric forward model + measurement fit. Two transfer
designs were built and measured before this one was chosen:

- v1 (direct Anny-style mesh→params ICP fit + closest-point delta
  transfer): the MPFB-internal segment solve converged exactly (ratios
  1.3448/1.3448/1.1153/1.0566), but her proportions (waist/hip 0.48, bust
  ratio 2.83) sit OUTSIDE the donor's reachable shape space, so the fit
  saturated (incr+decr of one family both at cap) and the waist response
  attenuated ~50× through bad correspondences.
- v2 (restricted fit verts, signed families): correspondence still 46 mm
  mean on the restricted set; waist response saturated at 1.06.

Chosen (v3): the parametric system supplies every number; transfer is by
CROSS-SECTION PROFILES (the standard deformation-transfer pattern for
unlike topologies):

- Delta parameters solved on the donor's own skeleton landmarks:
  upperleg-height w=1.399, lowerleg-height w=1.620, torso-scale-vert
  w=0.576, neck-height w=0.170 → segment ratios 1.346/1.345/1.115/1.0566
  against sheet goals 1.344/1.344/1.1143/1.0566.
- The donor's radial response is measured per cross-section (torso
  width/depth ratio per normalized column bin; leg/neck radial change per
  segment bin) and applied inside HER sections: torso verts scale about
  her own section centroids; thigh/shin verts move radially about her own
  bone lines; arm verts receive NOTHING (no arm parameter exists in the
  order — the donor's arm-tube readings under the torso targets are noise,
  measured −8..+15 mm, and deliberately not applied: applying height-band
  effects to arms was the old field's shear mechanism).
- MAX rule: bust sections and hip sections pinned to ratio 1.000 exactly.
- Waist: the waist-circ delta weight is solved against her waist section
  (same-verts width at GLB y 0.9016) to the sheet's ratio: w=5.056 →
  measured 1.2000 (see Deviations).
- Vertical: segment-anchored stretch profile on HER skeleton joints
  (ankle 0 / knee +0.1065 / hip +0.2201 / neck +0.2651 / crown +0.2751,
  gaussian-smoothed, feet planted) — the parametric systems' own height
  mechanism; no x/z coupling.
- Skeleton: joint globals = clean v4 globals + the field evaluated at the
  joint; v4 (clean) global rotations; locals + IBMs recomputed. Skin
  weights are never written anywhere in the pipeline.

## Verification — every gate pass/fail

| gate | result |
|---|---|
| Tattoo textures (33 images) byte-identical to v2 | **PASS** — all 33 sha256 equal |
| Changed accessors vs v2 | **PASS** — exactly 35: 34 AngelBody targets + 1 IBM accessor; everything else byte-identical |
| WEIGHTS_0 / JOINTS_0 accessors changed | **PASS** — none |
| Bind pose JW·IBM max err (gate ≤ 1e-4) | **PASS** — 6.24e-08 |
| Stature ON (goal 1.609 ± 0.01) | **PASS** — 1.6088 |
| Thigh / shin joint segment ratios vs v4 (goal 1.344 ± 0.01) | **PASS** — 1.3411 / 1.3417 |
| Arm tube bin delta-std, max (shear) | **PASS** — **2.15 mm** (hand-built field: 14.44 mm same instrument, 21.7 mm per PR #1693) |
| Waist section width ratio (goal 1.20 ± 0.02) | **PASS** — 0.1756 → 0.2108 m = **1.2000** |
| **Hip width99 ON vs OFF (owner gate: EQUAL ± 0.002)** | **PASS** — 0.3393 → **0.3393** (Δ 0.0000) |
| **Hip/ass depth99 ON vs OFF (owner gate: EQUAL ± 0.002)** | **PASS** — 0.2374 → **0.2374** (Δ 0.0000) |
| Bust slabs y 0.96 / 0.98 / 1.00 width+depth ON vs OFF (MAX rule) | **PASS** — identical to 4 decimals on all three slabs |

**Weights-integrity table (owner gate — height ≠ weights).** Decoded
comparison vs the clean v4 base (attire1 decoded via Blender; basis matched
vertex-for-vertex, max nearest-neighbour distance 5.2e-05 mm; joint-name
mapped weight vectors):

| region | verts | max \|Δweight\| vs v4 |
|---|---|---|
| arms | 1,636 | 4.79e-08 |
| bust | 1,350 | 4.76e-08 |
| torso | 1,529 | 4.82e-08 |
| waist | 471 | 4.77e-08 |
| neck | 134 | 4.77e-08 |
| legs | 4,104 | 4.80e-08 |

Max drift ≈ 5e-08 is float32 decode noise — i.e. **zero**: the pilot's
weights were already the clean v4 weights, and the rebuild changed none of
them. The height deformation dragged NO weight drift with it, in any
region. (For contrast, what the rebuild DID change in the rig is position:
joint globals moved with the field; rotations are the clean v4 rotations.)

## Proofs (dark stage #14121c, Neutral 1.1, 3-point rig, PR #1690 harness)

In `docs/proof/2026-11-09/megami-rebuild/` (+ `stage.html`, the #1690 stage
with one added arm camera):

- `rebuild-v3-front.png` — hero front: arms straight clean tubes, no melt;
  bust full/natural; waist defined, hips full width; T1/T2/T4 + XIV +
  sternum glyph read.
- `rebuild-v3-back.png` — hero back: glute depth/fullness intact (MAX
  rule visible), T5/T6/T7 fields read, arms clean.
- `rebuild-v3-arm.png` — left forearm close-up: even taper elbow→wrist, no
  S-curve, no balloon.
- `rebuild-v3-chest.png` — bust close-up: smooth underbust transition (the
  v2 field's slab distortion is gone), natural areola tone variation
  preserved, XIV + sternum glyph crisp.
- Afro fitted by the harness's measured head-joint alignment: body Head
  world (0.000, 1.480, −0.002) vs afro bind head (0.000, 1.629, −0.004) →
  root delta (0.000, −0.149, +0.001). Angel-brown eyes on Irises-2; the 10
  bundled nodes hidden per the composition rule. (The glossy skin sheen in
  the frames is the known stage/material family from the hero set —
  materials are byte-identical; the lighting/vcolor lane owns it.)

## Deviations

- Waist-circ weight 5.056: MPFB measure targets are authored as subtle
  adjustments on the donor (its own waist section moves ≈ +4% at w=1);
  her sheet target is +20% at the section, which takes w≈5 in the target's
  own linear direction. What is applied to her is verified in section
  space — smooth profiles, ratios clipped to the donor-observed envelope
  [0.95, 1.28] — and the measured outcome is exactly 1.2000.
- Auto-skin dependency: the learned auto-skin stack is the parallel
  auto-rig lane's deliverable (UniRig wired, PR #1697; its Kaggle
  skinning run has been quota-blocked since 2026-11-08, 30 h weekly cap).
  Its outputs were not available to this lane, so the rebuild keeps the
  Daz production weights and proves above that they carry zero collateral
  drift. Her 469-bone rig is retained — the animation banks retarget onto
  it; a replacement skeleton would break every bank.
- Correspondence transfer (Anny ICP fit) was built twice, measured, and
  rejected on evidence (fit saturation; 46 mm residual correspondence);
  cross-section profile transfer replaced it. Both attempts' metrics are
  in the lane scratch (`results/fit_metrics_v2.json`, fieldbuild logs).
- The donor's arm-tube radial readings under the torso targets were
  measured but not applied (no arm parameter in the order).
- `stage.html` adds one `arm` camera to the PR #1690 harness stage; all
  other stage parameters are the hero set's, unchanged.

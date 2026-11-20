# MEGAMI BODY V5 — bigger, wider, rounder, fatter hips/ass + wider thigh gap, stallion-stance show (2026-11-09)

Owner order 2026-11-09 (~13:00 CST), on saving the v4 body as the Angel
default: **"show me the bigger wider hips and ass rounder fatter version
still with the face and glam update I asked for"** — combined with the
standing combined-show order: saved straight hair + collision + face update
+ glam update, on a body with hips/ass fatter and wider, a **wider thigh
gap**, and a **stallion stance** (wide hips, upper-hip/ass included).

V5 is a body build on the owner-saved v4 (the Angel default). It does NOT
replace the v4 registration: `customization/profiles/megami-angel.json`
still names v4. V5 is presented for the owner's dial; registration changes
only on his ruling.

## What shipped

- `megami-angel-pilot2-v5.glb` on draft release `megami-pilot2-20261108`:
  59,095,872 B, sha256
  `07d4bacc47a4bf6c1cdc6830e141167099e8aeb781876b716a4eca388b8ab000`.
  Release copy stream-verified byte-identical to the build output (API
  stream → sha256; landing lane 5, 2026-11-09).
- Built from the v4 field: v5 radial profile curves RELATIVE to v4's,
  applied about the basis ring centroid on top of the v4 field (sanity: v4
  reproduced exactly under its own formalism, max |F4r−F4| = 0.00000 m).
  Above y 0.905 the v4 curves are kept (waist anchor and bust pin
  untouched); a build-1 shelf defect at the decline rings was fixed in
  build 2 by joining the absolute v5 curves to v4's calibrated curve
  across y 0.905–0.945 with the blend extended to 0.965 — no ratio-1.0
  shelf exists anywhere in v5.

## Hips/ass deltas (owner dial)

| measure | original | v4 | v5 | Δ vs v4 | Δ vs original |
|---|---|---|---|---|---|
| hip width99 | 0.3393 | 0.3800 | **0.4141** | **+8.97%** | **+22.05%** |
| hip depth99 | 0.2374 | 0.2661 | **0.2901** | **+9.02%** | **+22.2%** |
| hip width raw | 0.3586 | 0.4000 | 0.4344 | +8.6% | +21.1% |
| hip depth raw | 0.2583 | 0.2940 | 0.3204 | +9.0% | +24.0% |

Fullness carried high, per the design: upper-hip band (y 0.80–0.86)
width99 0.3322 → 0.3609 (+8.6%), depth99 0.2768 → 0.3162 (+14.2%); depth
ring peak 0.2873 → 0.3217 (+12.0%) at y = 0.79; upper-glute rings
(y 0.83–0.87) depth +15–17% vs v4 — rounder through the upper hip/ass, no
low sag (depth tails to 1.10 at y 0.42).

## Thigh gap — three honest instruments

Bind-pose inner thighs INTERPENETRATE in both v4 and v5, so a vertex-extreme
bind-pose "clearance" is not an honest number and none is claimed. The
instruments that are honest (`results/thigh-gap-v4v5.json`):

1. **Gap-pass displacement** (same-vertex v4→v5, topology identical):
   pass band n=939, mean displacement **8.85 mm**, max **32.11 mm**;
   inner verts (|x|<0.075) n=383, mean 8.57 mm, max 32.11 mm. The pass is a
   CENTRED radial expansion (mean signed x-shift 0.00 by construction): it
   fattens the thigh sections; the visible gap in a stance comes from this
   plus the wider profile.
2. **Front midline-column clearance** (Z-facing tris, |x|=4 mm split),
   v4→v5: y 0.80: 72.95 → **100.65 mm (+27.70)**; y 0.85: **+28.11**;
   y 0.75: +6.61; y 0.70: +3.15; y 0.60: 0.00; y 0.65: −21.33 (column
   composition shifts as sections widen — recorded, not hidden);
   y 0.90: −9.43 (above the pass).
3. **Band slice widths** (all-vert, local y): y 0.70: 330.9 → 358.0 mm;
   y 0.75: 355.6 → 394.8; y 0.80: 370.2 → 411.8; y 0.55 unchanged 279.6
   (below the profile's effective range).
   Fieldbuild slice instrument adds: mid-thigh band (y 0.58–0.68) inner
   clearance mean 19.8 → 27.4 mm (+7.6); top slices y 0.70–0.72 are the
   crotch/pelvis bridge in BOTH versions (0.1 mm) — anatomical contact
   zone, unchanged by design.

## Stallion stance — render pose, never a bind change

The show frames pose her rig at render time only; the GLB bind is
untouched (gate G3: weights/joints changed = none). Pose (stage source is
the record): world-Z rotations premultiplied onto the DEFORM leg chain —
thighs (`LeftUpLeg`/`RightUpLeg`) abducted ±18° from bind, shins
(`LeftLeg`/`RightLeg`) compensated ×0.35, feet (`LeftFoot`/`RightFoot`)
levelled by the remaining angle and yawed ±10° toe-out (toes via `tarsal`),
root dropped by the mean foot/tarsal-joint world height so both feet
ground. Measured posed facts (stance width, feet-level delta, applied
angles) are logged by the stage into `window.__facts.pose` and printed in
the shoot logs for the PR.

Pose-bone finding (lane 11, diag9/diag10): the stance MUST rotate the
deform chain, not the FK chain. The FK bones (`thigh.fk.L` etc.) carry ZERO
skin weight — the mesh is skinned to the DAZ-style deform/tweak bones
(`thigh.bend.twk`, `pelvis.twk`, `foot.twk`, `tarsal`, ...); glTF exports
the hierarchy and weights but not the Blender constraints that would drive
the deform bones from the FK controls. Rotating the FK bones moved bone
matrices (the first facts dump looked right) but deformed nothing — even a
45° FK abduction plus a forced bone-texture refresh changed zero pixels.
The deform-chain pose is proven on the render (diag10: feet span 140 ->
538 px, knees 162 -> 304 px).

Measured pose facts (lane 11, `results/facts-v5-lane11.json`, deform
chain): hip abduction 18°, knee comp ×0.35, foot-level comp 11.7°,
toe-out 10°, body drop 0.197 m, feet level to 0.14 mm, stance width
0.832 m (foot joints ±0.415 m).

Implementation note (lane 11, diag2/diag3): the stage first failed to find the
FK leg bones because three.js r160 GLTFLoader sanitizes node names at load —
dots are stripped, so file-side `thigh.fk.L` is the runtime object `thighfkL`.
The stage looks the bones up by their runtime (dot-free) names; all 8 FK leg
bones are real skin-joint Bones in the loaded scene (diag3: traverse finds
all 470), and the full stance above executes. An earlier lane-11 note claiming
the foot/toe FK nodes were not skin-joint Bones was wrong and is retracted.

## Gate table (v5 — `results/verify-v5.json`, `results/continuity-v5.json`)

| gate | result |
|---|---|
| Release == build bytes | sha256 identical (streamed) |
| Tattoo/texture images | identical (G1 ✓) |
| Changed accessors | exactly the AngelBody targets + IBMs (35) |
| Weights/joints changed | none (list empty) |
| Weights vs v4, per region | max \|Δ\| ≈ 4.8e-08 all regions — float noise |
| Bind JW·IBM | max err 6.24e-08 |
| Stature (AngelBody ON) | 1.6088 (unchanged) |
| Arm shear | 2.15 mm (field excludes arm regions; v4 elbow verdict carries) |
| Waist width ratio | 1.1974 (v4: 1.1975) |
| Hip width99 / depth99 | 0.4141 / 0.2901 (+8.97% / +9.02% vs v4) |
| Bust slabs OFF vs ON | identical widths/depths (owner-accepted v4 bust) |
| Continuity, waist-hip width window | max jump 0.0201 (v4: 0.0195) — holds |
| Continuity, decline window width | 0.0680 (v4: 0.0732) ✓ |
| Continuity, waist-hip DEPTH window | max jump 0.0648 vs v4 0.0310 — DISCLOSED below |

## Deviations

- **Depth-continuity excess at one ring pair (y = 0.84, buttock-fold ring):**
  the popfilter waist-hip depth step is 0.0648 vs v4's 0.0310. It is ONE
  ring pair (n=17–28, sparse percentile sampling): v5's designed depth
  rise (1.31→1.375 through the fold) amplifies the same sampling jitter
  present in v4, which steps +0.031 at the same ring. The width continuity
  — the owner's visible crop-step axis — holds (0.0201 vs 0.0195), the
  full-window unfiltered depth step matches v4 (0.0986 vs 0.0988), and no
  ratio-1.0 shelf exists. Reported, not hidden.
- **Face: PENDING OWNER BARE-FACE VERDICT.** The GLB still carries the
  v2 AngelFace byte-untouched, and the show's face close-up is shot on
  that carried face. The GNM face lane's attached build
  (`megami-angel-gnmface-v2.glb`, corr3_a on THIS v5 body, release-verified)
  was REJECTED by the owner in its combined/glam presentation
  (2026-11-09 19:22 CST — "that's not the face we built for angel, that's
  a weird mashup"); its BARE face proof is pending the owner's own
  at-a-glance verdict, and face PR #1701 is DO NOT MERGE. No GNM or glam
  face is presented as approved anywhere in this show. The glam update
  is likewise a separate lane's landing (PENDING here).
- **Hair: gate-passed REFIT straight (hair lane PR #1705).** The show
  wears `megami-hair-angel-straight-REFIT.glb` — the continuity-constrained
  refit of the owner-saved straight hair: fit gate PASS (edge growth max
  1.66 vs limit 2.0; bad tris 0 — the FINAL it refits had 16, max edge
  60.4 mm; rim exactly 1.5 mm at temples/nape, 0% inside; strands
  byte-identical to FINAL; exactly one accessor changed, the cap
  POSITION). Disclosed caveat: the crown is flattened against the
  authored profile (authored cap max-y 1.853 / strands 1.875; the FINAL
  lineage measures 1.752 / 1.783, zero verts above 1.80) — inherited
  from the predecessor FINAL, not introduced by the refit; crown
  restoration is the hair lane's open v6 item, and the crown reads
  smoother in top/full frames. Rim standard: MET. Crown: caveat open,
  not passed off as restored.
- **Hair collision: PENDING.** The collision system's Phase B proof has
  not landed; the show hair is seated by the measured head-joint delta
  fit only (same method as the v4 proofs).
- Waist ratio 1.1974 vs the 1.2000 goal — carried from v4's calibration
  (0.2% shortfall, reported there; v5 keeps the v4 waist anchor by design).
- Proofs shot at 640×960 (the v4 show's 820×1230 capture path OOM-crashes
  on this box; identical 2:3 framing, resolution only). Disclosed per the
  standing deviation rule.
- Glossy sheen in proofs is the known stage/material family (materials
  byte-identical); owned by the vcolor/lighting lane, not this build.

## Proof

- docs/proof/2026-11-09/megami-rebuild-v5/rebuild-v5-full-front.png
- docs/proof/2026-11-09/megami-rebuild-v5/rebuild-v5-full-back.png
- docs/proof/2026-11-09/megami-rebuild-v5/rebuild-v5-full-side.png
- docs/proof/2026-11-09/megami-rebuild-v5/rebuild-v5-close-hipfront.png
- docs/proof/2026-11-09/megami-rebuild-v5/rebuild-v5-face.png
- docs/proof/2026-11-09/megami-rebuild-v5/stage.html

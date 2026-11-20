# MEGAMI BODY V4 — waist→hip step fixed, hips/ass +12%, registered ANGEL DEFAULT (2026-11-09)

Owner orders 2026-11-09 ~11:40 CST, on the v3 body (PR #1698): (1) the waist→hip
"crop" — a straight chopped segment where the waist flows into the hips at the
V-taper start — must connect as one smooth curve; profile continuity becomes a
gate. (2) Hips and ass "way fatter and wider" than her original measurements —
first-pass target +12% width / +12% depth over original, exact deltas reported
for the owner dial (this supersedes the v3 Δ0.0000 hip restore for hips/ass
only). (3) Elbows: raised, then retracted by the owner ("maybe the elbows look
fine") — check-only: inspect, report with evidence, fix only on proof of a
defect. Owner rulings 2026-11-09 ~13:00 CST on this build's full-front proof:
**"Save this body as angel default"** and, on the bust, **"the tits look fixed
here"** (v4 bust accepted).

## What shipped

- `megami-angel-pilot2-v4.glb` on draft release `megami-pilot2-20261108`
  (v1/v2/v2fix/v3 kept): 59,095,940 B, sha256
  `c82aa47a9fae80bd2701d633893c9b260c302a7d64dadb4d42428631d85bf216`.
  Release copy stream-verified byte-identical to the build output (API stream
  → sha256, zero-disk check, landing lane 2026-11-09).
- Registered as the **Angel variant's default body**:
  `customization/profiles/megami-angel.json` (+ `megami-angel` added to
  `customization/profiles/index.json`). Megami's base default is untouched:
  `customization/profiles/megami.json` on the fixed attire1 base (PR #1694)
  remains the Megami base default — two variants, two defaults.
- Built from the v3 GLB: the v3 parametric field (MPFB2 cross-section profile
  transfer, PR #1698) plus ONE change — the waist→hip profile replacement
  below. Everything v3 proved (weights zero-drift, tattoo bytes, bind) is
  re-verified for v4 in the gate table; nothing else moved.

## The step — cause, measured

v3 hit two owner gates literally at once: waist sections scaled to ratio
1.2000 while hip sections were pinned at exactly 1.000 (Δ 0.0000). The section
instrument (`results/profile-step1.json` in the lane scratch) shows the two
bands meeting at a hard boundary: v3's worst ring-to-ring relative width step
is **0.1405 at y = 0.875 on every metric variant** — one height, the
pin/scale boundary, exactly where the waist sweeps into the hip. The gates
measured the bands; nothing measured the curve through them. The owner's eye
did.

## The fix — one continuous profile

The waist→hip sweep is now a single continuous radial profile (PCHIP anchors,
monotone-smooth through the sweep), replacing the two-rule band structure in
the y ≈ 0.80–0.96 window for both width and depth, with the hip peak itself
raised to the +12% target inside the same curve — no boundary anywhere in the
sweep. Calibration (2 iterations, `results/fit_metrics_v4.json`): hip width99
0.3796 → 0.3800, hip depth99 0.2620 → 0.2661, waist ratio 1.1945 → 1.1975.

Continuity, defined (window y 0.80–0.96, ring-to-ring relative steps of the
ON-state width/depth profiles; raw + two smoothing passes;
`results/continuity-recompute.json`):

| metric | v3 | v4 |
|---|---|---|
| max width step (raw) | 0.1405 @ y 0.875 | **0.0675** @ y 0.92 |
| max depth step (raw) | 0.1833 @ y 0.875 | **0.0988** @ y 0.92 |
| max width step (smoothed ×2) | 0.0398 | 0.0327 |
| max depth step (smoothed ×2) | 0.0538 | 0.0463 |

Section-profile instrument (gate G11, sweep window 0.78–0.905): worst jump
0.1405 → **0.0195**. The residual v4 maximum sits at y 0.92 — the profile's
return shoulder above the hip peak, inside one continuous curve, not a rule
boundary. Parent own-eyes on the full-front frame: the sweep reads smooth,
no ledge; the back/side/close-up frames in the proof set carry the same
verdict to the remaining angles.

## Hips/ass deltas (owner dial)

| measure | original | v3 | v4 | Δ vs original |
|---|---|---|---|---|
| hip width99 | 0.3393 | 0.3393 | **0.3800** | **+12.0%** |
| hip depth99 | 0.2374 | 0.2374 | **0.2661** | **+12.1%** |
| hip width raw | 0.3586 | — | 0.4000 | +11.5% |
| hip depth raw | 0.2583 | — | 0.2940 | +13.8% |

## Elbow check (check-only) — PASS, no defect, no fix applied

- E4: the v4 field's radial component on the arm chains is **0.0 mm max**,
  both arms — the field cannot bend an elbow; arms receive no radial push
  (the v2 shear mechanism is absent by construction).
- E1: elbow bend in the proof pose, clean skeleton: **24.78° L / 24.53° R**
  (v3 skeleton: 23.7° / 23.46°) — a natural slight bend, symmetric.
- E5: elbow joint vs its section centroid: 9.5 mm L / 9.4 mm R.
- Frame evidence: `rebuild-v4-elbow.png` — smooth through the joint.
The owner's retraction stands confirmed by measurement: the elbows were fine.

## Gate table (v4, all PASS — `results/verify-v4.json` + landing re-checks)

| gate | result |
|---|---|
| Release == build bytes | sha256 identical (streamed) |
| Tattoo/texture images | 33/33 byte-identical (independently re-hashed vs v3 AND vs untouched v2) |
| Changed accessors | exactly the AngelBody targets + IBMs (35) |
| Weights/joints changed | none (list empty) |
| Weights vs clean base, per region | max \|Δ\| ≈ 4.8e-08 (arms/bust/torso/waist/neck) — float noise |
| Bind JW·IBM | max err 6.24e-08 |
| Stature (AngelBody ON) | 1.6088 (goal 1.609) |
| Arm shear (bin delta-std) | 2.15 mm (hand-built v2 field: 14.44 mm) |
| Waist width ratio | 1.1975 (goal 1.20) |
| Hip width99 / depth99 | 0.3800 / 0.2661 (+12.0% / +12.1%) |
| Bust slabs OFF vs ON | identical (owner-accepted 2026-11-09) |
| Profile continuity | table above — worst step halved (ring) / 7× down (section) |

## Deviations

- Waist ratio landed at 1.1975 against the 1.2000 goal — the calibration
  converged there with the hip targets exact; a 0.2% shortfall on one ratio,
  reported rather than rounded up.
- Face: the GLB still carries the v2 AngelFace byte-untouched. The GNM face
  (owner order 2026-11-09) attaches to THIS body as the Angel default's face
  landing; it supersedes the face only, not this body registration.
- Learned auto-skin output still does not exist (Kaggle GPU quota; PR #1697
  wiring landed, watcher armed). Her Daz production weights are retained with
  zero drift proven — unchanged from v3.
- Glossy sheen in proofs is the known stage/material family (materials
  byte-identical); owned by the vcolor/lighting lane, not this build.

## Proof

- docs/proof/2026-11-09/megami-rebuild-v4/rebuild-v4-full-front.png
- docs/proof/2026-11-09/megami-rebuild-v4/rebuild-v4-full-back.png
- docs/proof/2026-11-09/megami-rebuild-v4/rebuild-v4-full-left.png
- docs/proof/2026-11-09/megami-rebuild-v4/rebuild-v4-close-hipfront.png
- docs/proof/2026-11-09/megami-rebuild-v4/rebuild-v4-close-hipside.png
- docs/proof/2026-11-09/megami-rebuild-v4/rebuild-v4-hipback34.png
- docs/proof/2026-11-09/megami-rebuild-v4/rebuild-v4-elbow.png
- docs/proof/2026-11-09/megami-rebuild-v4/stage.html

Proof-frame resolutions (landing disclosure): rebuild-v4-full-front.png was
shot at 820×1230 (before the box saturated); every other frame — full-back,
full-left, close-hipfront, close-hipside, hipback34, elbow — at 640×960.
Identical 2:3 aspect and framing; resolution only. The 820×1230 capture
path OOM-crashes on this box under multi-lane load (lane records in the PR
body).

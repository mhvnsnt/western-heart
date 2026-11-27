# Measurement sheets — Angel Fernandez & Megami (Parvati)

Pilot 2 v2, 2026-11-08. Owner foundation rule: real measurements and data of
everything, every inch of their bodies — every number below carries its method.
Anything the evidence cannot measure is logged as **unmeasured**, never invented.

Units: Angel sheet = ratios to her own stature/image (absolute scale unverified);
Megami sheet = model file units (1 unit = 1 m in the source Daz rig scale) plus
ratios, so the two sheets compare ratio-to-ratio.

---

## Sheet A — Angel Fernandez (from held evidence)

Evidence: video 457 frames (360×640 samples + 720×1280 detail frames), video 482
frames (1080×1920), owner's 5 supplied public-post screenshots (incl. the
full-length doorway photo, his photo 5 main image).

| Measure | Value | Method |
|---|---|---|
| Height | **unverified** — publicly reported 6'7"–6'8" (2.01–2.03 m); NOT verified from footage | Study record; doorway-frame geometry is consistent (~0.96 of a standard frame height in-image) but is not a verification |
| Leg length / stature | 0.558 | Pixel grid on the doorway photo: hip-crease→floor vs full stature (860 px) |
| Shin / thigh | ≈1.09 (range 0.96–1.25) | Same grid; hip-crease point uncertain ±30 px — noisy, NOT forced onto the model |
| Hip width / waist width | 1.57 | Same grid, front view |
| Bust width / waist width | 1.26 | Same grid, front view |
| Hip width / stature | 0.209 | Same grid |
| Waist width / stature | 0.134 | Same grid |
| Bust width / stature | 0.169 | Same grid |
| Shoulder width / stature | 0.186 | Same grid — arms raised in the photo; read with caution |
| Hip span / shoulder span | 0.716 | Video-457 pose tracking (Physique Lab study, landmark spans) |
| Shoulder width | 1.90 head-units | Video-457 pose tracking (head unit = face box) |
| Hip span | 1.36 head-units | Video-457 pose tracking |
| Forearm / upper arm | 0.82 | Video-457 pose tracking |
| Circumferences (bust/waist/hip/thigh) | **unmeasured** | Only front-view widths exist in the evidence; no depth view at measurable quality |
| Arm segment absolutes | **unmeasured** | No scaled full-arm view |
| Head size absolute | **unmeasured** | No scale reference in any held frame |

Skin reference (for the light-touch tone shift): sampled photo skin means —
thigh (184,137,118) + (186,139,121) (doorway photo), cheek (203,153,119)
(detail_457_f002, landmark-located). These are lit-photo values, not albedo;
only their hue direction was used (see handoff V2 §skin).

---

## Sheet B — Megami / Parvati (measured off the model, pre-reshape)

Evidence: `pilot2_v2.blend` evaluated Basis mesh + armature rest pose
(Blender measurement pass, 2026-11-08). Stature = evaluated rest-pose height
1.334 units (feet point in rest pose; basis-mesh bounding height 1.2524).

| Measure | Value | Method |
|---|---|---|
| Stature | 1.334 | Evaluated mesh z-extent (min −0.0827 → max 1.2512) |
| Thigh length | 0.3308 | Armature: hip joint (z 0.682) → knee (z 0.3519) |
| Shin length | 0.3106 | Knee (z 0.3519) → ankle (z 0.0424) |
| Leg (hip→ankle) | 0.6414 (0.481 of stature) | Sum of segments |
| Hip joint span | 0.139 | Hip joint heads x ±0.0696 |
| Shoulder joint span | 0.231 | Shoulder joint heads x ±0.1155 |
| Upper arm | 0.1829 | Armature bone lengths |
| Forearm | 0.2020 | Armature bone lengths (forearm/upper-arm 1.104) |
| Waist width | 0.1698 @ z 0.82 | Mesh cross-section (arm-dominant verts excluded) |
| Hip width | 0.352 @ z 0.66 | Mesh cross-section |
| Bust width | 0.48 @ z 0.88 | Mesh cross-section |
| Bust / waist (width) | 2.83 | Ratio of the above |
| Hip / waist (width) | 2.07 | Ratio of the above |
| Bust width / stature | 0.360 | Ratio |
| Waist width / stature | 0.127 | Ratio |
| Hip width / stature | 0.264 | Ratio |
| Thigh perimeter (per leg) | ≈0.40–0.43 @ z 0.44–0.48 | Cross-section convex estimate |
| Bust/hip perimeters | **unreliable — not used** | GoldenPalace shell + multi-island bands corrupt the ring trace at those heights; widths used instead (stated caveat) |

## MAX-rule calls (bust / hips / ass — fatter wins, per area)

| Area | Angel (evidence) | Megami (model) | Winner | Action |
|---|---|---|---|---|
| Bust | bust/waist 1.26; bust/stature 0.169 | bust/waist 2.83; bust/stature 0.360 | **Megami** | Untouched (radial factor 1.0 in the bust band) |
| Hips/ass | hip/waist 1.57; hip/stature 0.209 | hip/waist 2.07; hip/stature 0.264 | **Megami** | Untouched (radial factor 1.0 at/below z 0.80) |
| Waist (not a MAX area) | waist/hip 0.64 | waist/hip 0.48 | — shapes toward Angel | Waist radial ×1.20 peak (target waist/hip ≈0.58; partial move, not a full match — see report) |

## Post-reshape (AngelBody key = 1.0)

| Measure | Before | After |
|---|---|---|
| Stature | 1.334 | ≈1.609 (+20.6%) |
| Leg gain | — | +0.220 of the +0.275 total (80% of the gain is legs) |
| Thigh / shin | 0.3308 / 0.3106 | lengthened proportionally (+34.4% each); her own shin/thigh ratio kept (Angel's noisy 1.09 not forced) |
| Torso + neck gain | — | +0.055 |
| Bust / hips / ass | — | unchanged (MAX zones excluded from the radial field) |

# Megami GNM Face — corr3_a on the v5 Body (Angel variant)

Instruction-gate proof packet. **Do not merge on sight** — parent own-eyes +
at-a-glance pass first.

## Deliverable

- Build: `megami-angel-gnmface-v2.glb` — 58,774,357 B,
  sha256 `5811bb88f0e8a501dbe6153d6743a15fe4249388caf1500a70e4d194f9dcef5f`
- Shipped on release `megami-pilot2-20261108` as `megami-angel-gnmface-v2.glb`;
  stream-verified byte-identical (server digest == local sha256; full download
  re-hashed identical).
- Construction: winner key `key_corr3_a` (GNM fit `corr2_a` + stage-3
  correction pass, `fit_correct2.py` alpha 300 / beta 0.3, |dF| mean 0.44 mm /
  max 1.38 mm) spliced into the v5 body (`build_glb.py base=v5`).
  `verify_glb` vs v5: **only the 12 AngelFace accessors + image 21 (the face
  atlas) differ**; all 476 mesh-10 morph targets preserved, target names and
  weights identical; nodes / skins / materials / skin weights untouched.

## Winner call — with the honesty attached

Gate = MediaPipe FaceLandmarker landmark error vs Angel references
(front ref `identity`, q34 ref `f003`), mean / max err %. Full table in
`GATE-SUMMARY.json`.

| build | front | q34 |
|---|---|---|
| **corr3_a — gate stage (v3-based candidate)** | 1.59 / 5.80 | **2.34 / 7.23** |
| **final build (corr3_a on v5) — clean stage front** | 1.39 / 4.80 | — |
| **final build — q34 (gate-stage frame)** | — | **2.24 / 6.69** |
| v2 warp (owner-REJECTED) — same-stage re-measure | 1.19 / 4.31 | 2.79 / 9.16 |
| corr2_b | 1.31 / 4.37 | **no measurement exists** |

- corr3_a is the **only build that beats the re-measured v2 baseline on a
  full view (q34)** while holding the front at corr-family level. On q34 the
  jaw region is decisive: oval_jaw 3.18 (corr3_a) / 3.14 (final) vs v2's 6.47.
- **The front deficit vs v2 stands and is reported plainly:** 1.59 (gate
  stage) / 1.39 (final, clean stage) vs v2's 1.19. v2 was owner-REJECTED on
  eyes regardless, and its front frame carries a scalp-cap hairline defect.
- The historical v2 numbers (front 0.95 / q34 2.91) were measured on a
  different stage; the same-stage re-measurement (1.19 / 2.79) supersedes them.
- corr2_b has the best front of all candidates (1.31) but **no q34
  measurement** — MediaPipe returned no face on its only q34 frame (detector
  miss), so it cannot be certified on both views and was not chosen. corr3_a
  descends from corr2_a, not corr2_b.
- Residual q34 error concentrates in the far-side eye_L (~4.2) and brow_L
  (~5.0) — expression-bearing landmarks, 0.35-weighted by gate design.
- Final-build q34 method note: the clean-stage with-hair q34 frame
  (`final_q34_corr3_a.png`) returns **NO FACE** from MediaPipe — the fitted
  straight hair sheet covers the far cheek (detector miss, same class as
  corr2_b's; not a fit verdict). The q34 gate therefore ran on the gate-stage
  frame of the final GLB (`gate_on_q34_final.png`); a clean-stage frame of
  the identical face state without the fitted hair part
  (`final_q34_nohair.png`) gates **identically: 2.24 / 6.69**, regions equal
  to 0.01–0.23 — the number belongs to the final build's face, not the stage.
- Own-eyes (finishers 2 + 5): q34 jaw is clean and the profile reads Angel;
  the pale jaw/neck outline line present in corr_a1 / hybrid_v2 / thr_mu002 /
  gnm v1 is **absent**. Neck seam is continuous (`final_neck_seam.png` — no
  seam line; mole and sternum ankh tattoo intact).

## Texture — owner's spec, measured

Skin stays **Megami's own tones**; Angel contributes **lip tone + facial
texture gradient as measured tonal ratios only — her photos were never used
as texture** (`texture_report.json`).

- Angel ratios = trimmed interior-disc samples, median of 4 frames; gradient
  gains clamped to [0.90, 1.12], lip gain applied [1.135, 1.112, 1.25].
- Face mean preserved: (106.93, 71.53, 57.53) → (106.83, 71.41, 57.43).
- Lips: (109.24, 75.12, 60.41) → (124.01, 83.50, 75.52).
- Final-GLB tone samples (`skin_tone_samples.json` + `skin_tone_strip.png`):
  cheek (104.75, 71.40, 57.55) · forehead (120.02, 78.16, 63.05) · lips
  (124.01, 83.50, 75.52) · torso, image 19 (120.92, 82.07, 62.82) · arm,
  image 26 (130.86, 91.53, 72.75).

## Stage defects vs fit defects — separated

**Fit (this build):** face geometry + atlas as above; brown Angel iris set in
all final frames; neck seam clean.

**Stage / hair-part (NOT this build's fit):**

1. The fitted straight hair hangs as heavy curtains; in the clean-stage q34
   it covers the far cheek/jaw as a solid sheet — and caused the q34 detector
   miss above.
2. Hairline/cap: a pale pink scalp patch at the part line and dark
   star-shaped cap tabs at the hairline, with the cap edge crossing the
   forehead (`final_face_closeup.png`). This is the saved straight hair's
   **torn cap** (known topology damage in the hair-fit lane; the refit to the
   HAIR-FIT STANDARD is in progress — hair remains PENDING-STANDARD).
3. Heavy glossy skin sheen = the known VCOLOR / fight-stack lighting lane,
   not this build. The clean stage nulls SKIN normalMaps + vertex colours
   and uses NeutralToneMapping.
4. Exposure: the final set ran at exp 1.0 (gate stage is fixed at 1.1) — the
   chest blowout seen in earlier proofs is gone at 1.0.
5. The hero's A-pose is the stage's bind pose, not a fit signal.

## Proof

- `final_front_corr3_a.png` — final build, clean stage, front (gate camera)
- `final_q34_corr3_a.png` — final build, clean stage, 3/4 with fitted hair (detector-miss frame, kept as evidence)
- `gate_on_q34_final.png` — final build, gate stage, 3/4 (the gated q34 frame)
- `final_q34_nohair.png` — final build, clean stage, 3/4, no fitted hair part (gates identically: 2.24 / 6.69)
- `final_hero_front.png` — final build, full body hero
- `final_face_closeup.png` — final build, face close-up (shows the hair-cap defect, item 2 above)
- `final_neck_seam.png` — final build, jaw/neck seam close-up
- `sbs_front_v2.png` — side-by-side: winner vs rejected v2 warp, front
- `sbs_front_orig.png` — side-by-side: winner vs original Megami face, front
- `sbs_front_angel.png` — side-by-side: winner vs Angel reference f0004, front
- `sbs_q34_v2.png` — side-by-side: winner vs rejected v2 warp, 3/4
- `sbs_q34_corr2a.png` — side-by-side: winner vs corr2_a (its stage-2 parent), 3/4
- `sbs_q34_angel.png` — side-by-side: winner vs Angel reference 482_f003, 3/4
- `skin_tone_strip.png` — sampled skin-tone strip from the final GLB
- `skin_tone_samples.json` — the tone sample values behind the strip
- `GATE-SUMMARY.json` — every gate number in this report, with frame provenance
- `g_final_front_metrics.json` — final build front gate metrics (1.39 / 4.80)
- `g_final_front_deltas.json` — final build front gate per-landmark deltas
- `g_final_q34_metrics.json` — final build q34 gate metrics (2.24 / 6.69)
- `g_final_q34_deltas.json` — final build q34 gate per-landmark deltas
- `g_corr3_a_front_metrics.json` — winner candidate front gate metrics (1.59 / 5.80)
- `g_corr3_a_q34_metrics.json` — winner candidate q34 gate metrics (2.34 / 7.23)
- `texture_report.json` — texture pass: Angel ratios, clamps, before/after zone means

## Deviations

None.

- [x] Self-check: every payload file listed under Proof exists in this PR and was read back after the push; gate numbers match GATE-SUMMARY.json; the GLB hash above matches the release asset.

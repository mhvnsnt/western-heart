# Megami GNM face — corr3_a on the v5 body (2026-11-09)

Instruction-gate proof packet for the GNM face fit: Megami's body (v5) carrying
the Angel face, built as `megami-angel-gnmface-v2.glb`. **Not merged — owner's
call.** Read the caveat block before judging any frame in this folder.

## The build

- Winner candidate: **corr3_a** — GNM fit iterated in three stages
  (corr2_a → stage-3 correction `fit_correct2.py`, alpha 300 / beta 0.3;
  correction field |dF| mean 0.44 mm, max 1.38 mm).
- Attached to the v5 body with `build_glb.py` (base=v5). `verify_glb` vs v5:
  ONLY the 12 AngelFace accessors + image 21 (face atlas) differ; all 476
  mesh-10 morph targets preserved (AngelFace is the only face-identity content
  replaced); weights / nodes / skins / materials identical. VERIFY OK.
- `megami-angel-gnmface-v2.glb`: 58,774,357 B,
  sha256 `5811bb88…f5f`. On release `megami-pilot2-20261108`; stream-verified
  byte-identical (server digest == local sha256; full download re-hashed).
  The GLB itself is a release asset, not a repo file.
- Texture (owner spec): skin is Megami's own. Angel contributes **tonal ratios
  only** — median of 4 reference frames, gradient gains clamped to
  [0.90, 1.12] albedo, lip gain clamped [0.85, 1.25] (applied 1.135 / 1.112 /
  1.25), face mean renormalised (106.93, 71.53, 57.53) → (106.83, 71.41,
  57.43). Angel's photos were never used as texture. Full data:
  `texture_report.json`; samples: `skin_tone_samples.json` +
  `skin_tone_strip.png`.

## Gate numbers (MediaPipe matched-camera gate, % of reference face width)

Gate: `_pilot2-v2-20261108/scripts/gate.py`; front ref = identity,
q34 ref = f003. All baselines below were re-measured on this stage — the
historical v2 figures (0.95 / 2.91) were measured elsewhere and are NOT the
comparison.

| build | front mean / max | q34 mean / max |
|---|---|---|
| **final GLB (corr3_a on v5)** | **1.39 / 4.80** | **2.20 / 7.03** (no-hair frame — see Q34 note) |
| corr3_a (candidate stage) | 1.59 / 5.80 | 2.34 / 7.23 |
| corr2_a | 1.56 / 6.00 | 2.96 / 8.73 |
| corr2_b | 1.31 / 4.37 | no measurement (detector miss) |
| rejected v2 warp (re-gated) | 1.19 / 4.31 | 2.79 / 9.16 (oval_jaw 6.47) |
| original Megami face | 1.77 / 5.93 | — |

Final front regions (`g_final_front_metrics.json`): oval_jaw 2.19, lips 1.49,
eye_L 0.73, eye_R 1.06, brow_L 2.88, brow_R 1.28, nose 1.60. brow_L is
expression-bearing (the reference pose carries brow expression; the gate
down-weights it by design).
Final q34 regions (`g_final_q34_metrics.json`): oval_jaw 3.51, lips 1.86,
eye_L 4.16, eye_R 0.80, brow_L 4.98, brow_R 1.59, nose 1.00 — consistent with
the candidate-stage q34 (`g_corr3_a_q34_metrics.json`: oval_jaw 3.18,
eye_L 4.26, brow_L 5.14): the residual q34 error concentrates in far-side,
expression-bearing features.

### Winner honesty (reported plainly)

- corr3_a is the ONLY build that beats the re-measured v2 baseline on a full
  view: q34 2.34 vs 2.79 (max 7.23 vs 9.16; oval_jaw 3.18 vs 6.47).
- On the front, corr3_a does NOT beat v2: candidate-stage front 1.59 vs v2
  1.19 stands as a measured deficit. The final build's own front gate improved
  to 1.39 / 4.80 but still does not beat 1.19. v2 was owner-REJECTED on eyes
  regardless, and its front frame shows a scalp-cap hairline defect.
- corr2_b posted the best candidate front (1.31) but has NO q34 measurement —
  MediaPipe returned no face on its q34 frame (detector miss, not a fit
  verdict) — so it cannot be certified on both views and was not chosen.
- corr3_a descends from corr2_a, not corr2_b.
- Eyes-vs-gate tension is on record for v2's q34: its profile reads clean to
  the eye while the gate puts its error in depth (oval_jaw 6.47) that a
  profile view hides. The owner's eyes overrule the gate where they conflict.

### Q34 note — how the final q34 was measured

The final PROOF q34 frame (`final_q34_corr3_a.png`, fitted straight hair on)
returns MediaPipe NO FACE — the hair mass occludes the detector; same
signature as corr2_b's miss. That is a detector limitation, not a fit verdict,
and it is not left as a bare miss: the final GLB was re-rendered on the same
proof stage / camera / brown iris / exposure with the fitted hair part off
(`final_q34_nohair.png`; the body's own bun shows — a stage element, not part
of the shipped look) and gated vs f003: **2.20 / max 7.03**
(`g_final_q34_metrics.json`). Disclosed difference from the proof frame: hair
state only. The number agrees with the candidate-stage q34 gate of the same
face key (2.34 / 7.23, `g_corr3_a_q34_metrics.json`), and both beat the
re-measured v2 q34 baseline (2.79 / 9.16).

## Parent own-eyes verdict (2026-11-09, recorded)

- THE FACE ITSELF READS AS ANGEL in both final frames — brow / nose / lips /
  jaw credible front AND profile; clean jaw, no jaw-line defect. **The fit is
  good.**
- The frames are NOT showable as clean proof because of STAGE / HAIR defects
  (the torn straight-FINAL cap — known, PENDING the hair-fit standard refit):
  (1) a scalp window/hole at the crown with skin + a pale circular patch
  showing, black star-shaped gaps at the parting; (2) a pinkish forehead
  patch; (3) q34: a hard straight vertical cap edge cutting down the face in
  front of the ear, dark slab inside the hair mass, flat grey band pieces;
  (4) heavy glossy sheen on forehead/chest (the VCOLOR lane owns that fix);
  (5) eyes slightly pale.
- These are hair-part + stage defects, NOT fit failures. The face is never
  presented as proven by these frames without this caveat block; the clean
  re-shoot follows the hair refit.

## Files

- `final_front_corr3_a.png`, `final_q34_corr3_a.png` — final GLB on the clean
  proof stage (gnmproof2.html): fitted straight hair, Angel-brown iris,
  exposure 1.0. Caveat block above applies.
- `final_hero_front.png`, `final_face_closeup.png`, `final_neck_seam.png` —
  same stage/build: full frame, face close-up, neck-seam close-up.
- `final_q34_nohair.png` — the gated final q34 frame (fitted hair off; see
  Q34 note).
- `sbs_front_v2.png`, `sbs_q34_v2.png` — winner vs REJECTED v2 warp,
  matched camera.
- `sbs_front_orig.png` — winner vs original Megami face, front.
- `sbs_front_angel.png`, `sbs_q34_angel.png` — winner vs Angel reference
  (f0004 / 482_f003).
- `sbs_q34_corr2a.png` — winner vs corr2_a (its parent candidate), q34.
- `skin_tone_strip.png`, `skin_tone_samples.json` — tone samples from the
  final GLB's own atlas/images.
- `g_final_front_metrics.json` — final front gate (full output incl. deltas
  data in the lane archive).
- `g_final_q34_metrics.json` — final q34 gate, on the no-hair frame (see
  Q34 note).
- `g_corr3_a_q34_metrics.json` — candidate-stage q34 gate of the same face
  key, for comparison.
- `g_v2base_q34_metrics.json` — rejected-v2 q34 baseline, re-measured.
- `texture_report.json` — texture pass: Angel zone samples, median ratios,
  applied gains, before/after face means.

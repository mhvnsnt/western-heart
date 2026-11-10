# Megami GNM Face — corr3_a (Angel identity) on the v5 body

**Deliverable:** `megami-angel-gnmface-v2.glb` — the GNM-fitted Angel face
(winner **corr3_a**) attached to the Megami v5 body.
Release `megami-pilot2-20261108`, 58,774,357 B,
sha256 `5811bb88f0e8a501dbe6153d6743a15fe4249388caf1500a70e4d194f9dcef5f`
(server digest == local sha256; byte-identical — re-verified at PR time).

**Verify (structural):** vs the v5 body, ONLY the 12 AngelFace accessors +
image 21 (the retuned face atlas) differ. All 476 morph targets on the face
mesh are preserved; weights / nodes / skins / materials are identical.
AngelFace is the only face-identity content replaced.

**Method:** corr3_a = stage-3 projection-correction round
(`scripts/fit_correct2.py`, alpha 300, beta 0.3, on the stage-2 corr2_a key;
displacement |dF| mean 0.44 mm, max 1.38 mm — see `key_corr3_a.npz.meta.json`).
Texture: Angel contributes LIP TONE + FACIAL TEXTURE GRADIENT only, as
measured tonal ratios (median of 4 reference frames) applied to Megami's own
atlas — gradient gains clamped [0.90, 1.12], lip gain [1.135, 1.112, 1.25];
face mean preserved ((106.93, 71.53, 57.53) → (106.83, 71.41, 57.43)).
Angel's photos were never used as textures. Skin stays Megami's own sampled
tones. Full numbers: `texture_report.json`; samples: `skin_tone_samples.json`
+ `skin_tone_strip.png`.

---

## ⚠ PARENT OWN-EYES CAVEAT — READ BEFORE JUDGING THE FRAMES

Parent own-eyes, 2026-11-09 ~18:12 CST, on `final_front_corr3_a.png` and
`final_q34_corr3_a.png`:

- **THE FACE ITSELF READS AS ANGEL in both frames** — brow / nose / lips / jaw
  credible front AND profile; clean jaw, no jaw-line defect. **The fit is
  good.**
- **The frames are NOT showable as proof**, because of stage / hair defects —
  the torn straight-FINAL hair cap, which is known and PENDING the hair-fit
  standard refit (a different lane owns it):
  1. a scalp window / hole at the crown, with skin and a pale circular patch
     showing, and black star-shaped gaps at the parting;
  2. a pinkish forehead patch;
  3. in q34: a hard straight vertical cap edge cutting down the face in front
     of the ear, a dark slab inside the hair mass, flat grey band pieces;
  4. heavy glossy sheen on forehead / chest (the VCOLOR lane owns that fix);
  5. eyes slightly pale.
- These are **hair-part + stage defects, NOT fit failures**. The frames in
  this PR are included for the record and must not be presented as the face
  proof without this caveat block. The owner sees the face **with the caveat
  stated**; the clean re-shoot follows the hair refit.

Finisher-6 own-eyes on the two frames landed after that verdict
(`final_face_closeup.png`, `sbs_q34_angel.png`) are consistent with it: the
close-up shows the same crown window, pink forehead patch and sheen (all
hair/stage-owned), with the face itself credible; the q34 side-by-side shows
the cap edge in front of the ear exactly as the parent described.

---

## Gate metrics (MediaPipe landmark gate; mean landmark error % vs refs)

Front ref = Angel identity frame; q34 ref = Angel f003. All rows re-measured
on the same stage + gate (`gate.py`) unless noted.

| Build | Front mean / max | q34 mean / max | Note |
|---|---|---|---|
| **corr3_a, final GLB on clean stage** | **1.39 / 4.80** | detector miss — see below | `final_front_corr3_a.png` |
| corr3_a (stage-2 gate, v3-era body) | 1.59 / 5.80 | **2.34 / 7.23** | beats the v2 baseline on q34 |
| rejected v2 warp (re-gated on this stage) | 1.19 / 4.31 | 2.79 / 9.16 | owner-REJECTED on eyes; front frame shows a scalp-cap hairline defect |
| original Megami face (AngelFace = 0) | 1.77 / 5.93 | — | `g_gnm_off_metrics.json` |
| corr2_a (stage-2 parent of corr3_a) | 1.56 / 6.00 | 2.96 / 8.73 | |
| corr2_b | 1.31 / 4.37 | **no measurement** | detector miss — uncertifiable |

Final-front regions: oval_jaw 2.19 · lips 1.49 · eye_L 0.73 · eye_R 1.06 ·
brow_L 2.88 · brow_R 1.28 · nose 1.60.
corr3_a q34 residual error concentrates in the far-side eye_L 4.26 + brow_L
5.14 — expression-bearing landmarks, 0.35-weighted by gate design;
oval_jaw 3.18 vs the v2 warp's 6.47.

**Final q34 gate:** MediaPipe returned NO FACE on
`final_q34_corr3_a.png` (the fitted straight hair occludes the detector on
this frame) — a **detector miss, not a fit verdict**. The same failure hit
corr2_b's q34 earlier. corr3_a's q34 standing rests on its stage-2 gate
(2.34 / 7.23, measured) plus the parent's own-eyes profile verdict above.

## Winner honesty

- corr3_a is the **only** build that beats the re-measured v2 baseline on a
  full view (q34: 2.34 vs 2.79; max 7.23 vs 9.16) while holding the front at
  corr-family level.
- On the stage-2 gate the front stands at **1.59 vs v2's 1.19 — a measured
  deficit, reported plainly.** (On the final clean stage the front improved
  to 1.39 / 4.80; the deficit vs v2's 1.19 is still not closed.) v2 was
  owner-REJECTED on eyes regardless of its numbers.
- **corr2_b is uncertifiable**: best front of the field (1.31 / 4.37) but no
  q34 measurement exists (detector miss), so it cannot be certified on both
  views. corr3_a descends from corr2_a, not corr2_b.
- Eyes-vs-gate tension is on record: v2's q34 oval_jaw error (6.47) sits in
  depth the profile render hides — its q34 jaw *looks* clean. The owner's
  eyes overrule the gate either way.

## Stage-vs-fit defect separation

Stage / hair / other-lane defects present in the proof frames (NOT fit):
torn straight-FINAL cap (crown window, parting gaps, forehead patch, q34 cap
edge + dark slab + grey bands) — hair-fit lane; glossy skin sheen —
VCOLOR/lighting lane; slightly pale eyes — stage eye state.
Fit defects: **none identified** — jaw line clean in both views (the pale
jaw/neck outline line present in corr_a1 / hybrid_v2 / thr_mu002 / gnm v1
q34 frames is absent in corr3_a).

## Contents

- Final frames: `final_front_corr3_a.png`, `final_q34_corr3_a.png`,
  `final_hero_front.png`, `final_face_closeup.png`, `final_neck_seam.png` —
  clean stage (`stage-gnmproof2.html`), fitted straight hair, Angel-brown
  iris, exposure 1.0.
- Side-by-sides (winner vs rejected v2 / original Megami face / Angel
  reference, front + q34): `sbs_front_v2.png`, `sbs_front_orig.png`,
  `sbs_front_angel.png`, `sbs_q34_v2.png`, `sbs_q34_corr2a.png`,
  `sbs_q34_angel.png` (composed by `scripts/compose_proofs2.py`).
- Tone evidence: `skin_tone_strip.png`, `skin_tone_samples.json`,
  `texture_report.json`.
- Gate data: `g_final_front_metrics.json` + `g_final_front_deltas.json`,
  `g_corr3_a_*`, `g_corr2_a_*`, `g_corr2_b_front_*`, `g_gnm_off_metrics.json`,
  `key_corr3_a.npz.meta.json`.
- Pipeline scripts: `scripts/` (build / verify / fit / render / compose +
  `shots_final.json`).

## Status

**DO NOT MERGE on the numbers alone.** Owner reviews the face with the
caveat block above; the clean re-shoot of these same frames follows the
hair-fit standard refit, and the glossy-sheen fix is the VCOLOR lane's.

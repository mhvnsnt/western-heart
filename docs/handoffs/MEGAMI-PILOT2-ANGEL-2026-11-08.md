# Pilot 2 — Megami ← Angel Fernandez: Build Report (2026-11-08)

**Status: PR open for parent/owner proof pass. NOT merged. Bio is a DRAFT.**
Owner order (2026-11-08 ~18:25 CST): Megami gets Angel Fernandez's face exactly,
all of Angel's tattoos exactly how/where Angel has them, Angel-inspired elements
mixed into her bio adapted to the Western Heart universe + Megami canon.
Canon-fill rule (owner 18:27 CST): unreadable tattoo words are filled from
Megami canon. Skin rule (owner): Megami keeps her own skin colour; all ink
black/grey monochrome.

## 1. Evidence recovery

| Source | State |
|---|---|
| Tattoo catalogue (physics-playground-pwa `docs/likeness-pilot2/TATTOO-CATALOGUE-2026-11-08.md`) | RECOVERED (copy worked from in scratch) |
| Face plan (`docs/scan-pipeline/FACE-FROM-PHOTO-PLAN-2026-11-08.md`) | RECOVERED |
| Angel study (STUDY.md) | RECOVERED |
| Evidence stills/crops (`tattoo-work/detail/`, 27 files) | RECOVERED — all present |
| Video 457 frames | RECOVERED as extracted frame samples (every-20f, 21 frames + f340/f360 + detail frames) in scratch |
| `v457_face_mesh.csv` (mocap lane's original tracking) | NOT in any repo/release found. REPLACED by re-tracking the held frames with MediaPipe Face Landmarker (Apache-2.0) — see §2 |
| Videos 482/476/898 full files | Not on this machine; their evidence stills + catalogue data are recovered, which is what the tattoo build consumes. 482 face backup not needed (457 fit completed) |

Nothing was substituted or guessed: every build input traces to the catalogue,
the study, or a recovered frame.

## 2. Face (item A) — licence-clean chain only

Chain used: **MediaPipe Face Landmarker (Apache-2.0) + Megami's own mesh +
Blender.** No FLAME/SMPL/BFM/DECA/EMOCA/MICA/SMIRK/SPECTRE/Pixel3DMM anywhere.
(The previous lane's ICT-FaceKit experiment found in scratch was NOT used —
outside the approved chain — and was deleted.)

- Angel identity landmarks: re-tracked from held 457 frames; neutral gate per
  the face plan (mouthSmile avg ≤ 0.32, jawOpen < 0.1) selected frames
  f0002 + f0004 of the every-20f samples; Procrustes-averaged on anchors
  [33, 263, 133, 362, 1]. Saved: `identity_angel.json` (in scratch, summary in §6).
- Megami landmarks: same landmarker on her current front render.
- Measured differences (per inter-ocular distance): cheek width ×0.962,
  jaw width ×0.999 (identical), nose width ×0.989, mouth width ×1.062,
  eye width ×1.12 / ×1.04, inner eye gap ×0.883. Vertical ratios (face height,
  nose length, lip heights) were EXCLUDED from the warp: the two sources were
  shot at different camera pitches, which contaminates vertical measures —
  stated here rather than hidden. Lip thinning was applied damped (×0.85
  local) on the strength of both lip ratios reading the same direction.
- Build: shape key **`AngelFace`** added to the body mesh (target #475,
  weight 1.0 in the exported GLB, adjustable/removable), plus matching keys
  on the Eyebrow and Eyelashes meshes so the whole face moves coherently.
  Max vertex displacement 3.0 mm — Angel's and Megami's horizontal proportions
  are genuinely close; the key is a measured refinement, not a resculpt.
  Preserved: v4 skin standard, body, Flora hair, tiger eyes (parent's build,
  applied in the proof harness exactly as the parent does), default attire.
- Gate (plan §6.1 method: MediaPipe on the render, similarity-aligned to the
  Angel identity landmarks, error as % of face width). Same-camera A/B in the
  proof harness: AngelFace OFF = mean err 9.57% (jaw 14.69, nose 8.25, lips
  15.70, eyes 3.67); AngelFace ON (v2) = 9.77% (jaw 15.08, nose 8.49, lips
  15.65, eyes 3.94). **The key is neutral on this gate — it does not pass
  the plan's ≤3% bar, and the OFF state doesn't either.** The residual is
  dominated by camera mismatch (Angel's selfie vs the harness camera:
  focal length, distance, pitch), which the plan's gate assumes away by
  requiring matched framing. What the key verifiably does is move the
  model's 3D proportions to the measured Angel ratios (table above,
  same-camera re-measurement); whether the likeness reads is the owner's
  call on the side-by-side, per the plan. A first warp version (parent-camera
  ratios + eye shift) measured clearly worse (10.57%) and was replaced by
  this v2 (same-camera ratios, no eye shift) — the iteration is documented
  here, not hidden.

Honest limit: a landmark-proportion key is not a pore-level clone. It moves
every measured horizontal proportion to Angel's values; the owner's eyes on
the side-by-side are the final authority, per the plan.

## 3. Tattoos (item B) — all 11 catalogue pieces + T3 canon-fill

Method: each tattoo was placed by MEASURED mapping — triangles of her own
mesh were selected by 3D region + material, and the design was painted into
her skin textures inside those triangles' UV footprint (mask-limited, so ink
can only land on the body part it belongs to). Ink black/grey over her own
skin tone; never-tattooed areas (chest, stomach, inner thighs, lower legs,
feet, neck/face) left bare.

| ID | Placement | Build |
|---|---|---|
| T1 | Right thigh front | 6 butterflies (2 large / 2 med / 2 small), solid black-grey, lighter centres |
| T2 | Left thigh front | 5 butterflies (incl. 1 vertical closed-wing) |
| T3 | Left thigh front-centre | Canon-fill script "shizuka" — see §4. Catalogue had this mark UNCONFIRMED; built only under the owner's canon-fill order, flagged for owner ruling |
| T4 | Left outer thigh, hip→knee | Large feather column, anchor-placed down the outer thigh |
| T5 | Upper back, blade to blade | Feathered wing rows anchor-placed from spine outward |
| T6 | Lower back / hips | Central butterfly motif + feather shading hip to hip |
| T7 | Buttocks + backs of thighs | Dense swirling linework field, continuous with T6 |
| T8 | Right upper arm, outer | Feathers above + canon-fill script, 2 lines — §4 |
| T9 | Right upper arm, outer/back | Large feather/wing-line stack, shoulder→mid-arm |
| T10 | Right inner forearm | Dark vertical shaded piece, wrist→mid-forearm |
| T11 | Left hand, back near wrist | Canon-fill tiny script "koko" — §4 |
| T12 | Right hand, back near wrist | Canon-fill tiny script "made" — §4 |

Side convention verified from the armature/orientation math (her right =
−x in mesh space); counts differ per side (6 right / 5 left) exactly as
catalogued, so a side flip would be visible in the proof — check it there.

## 4. Canon-fill wording (item C) — every filled word + its canon source

Source for all: `roster/parvati/CANON.md` (her existing canon lines).

| Tattoo | Words | Canon source |
|---|---|---|
| T8 (right upper arm, 2 lines) | "The shrine was here before you. / It will be here after." | Bio-draft phrasing of her door-guardian pronouncements ("Koko made." / the sealed-door canon in CANON.md) — DRAFT wording, owner to approve or swap |
| T11 (left hand) | "koko" | Fight-start line "Koko made." (This far. No further.) |
| T12 (right hand) | "made" | Same line, split across the hands (left reads first, as catalogued position) |
| T3 (left thigh) | "shizuka" | Win line "Tobira wa, shizuka." (The door is quiet.) |

All kept as fine cursive at catalogue sizes. The arm script (T8) is placed
on the right upper arm and partially legible in
`proof-tattoo-arm-20261108.png`; the hand scripts (T11/T12) are placed at
the wrist-backs by the same measured UV mapping but are too small to read
in the renders — true to their catalogue size (a few tiny letters).

## 5. Bio (item D) — DRAFT

`roster/parvati/BIO-DRAFT-ANGEL-MIX-2026-11-08.md` — Angel-inspired elements
(towering Latina presence, unhurried confidence, larger-than-life scale,
southern heat) rewritten as Megami's shrine canon: the tallest soul the Trial
has pulled, the shrine's southern heat, her tattoos as the shrine's ledger.
NOT transferred: real name/handles, follower counts, real places as her home,
any real-life biography. Her kit (Jun Kazama base), student (Chatur), voice
lines, and skin all stay hers. Three owner-decision flags are listed inside
the draft (pre-fight line addition, ink-as-ledger framing, "tallest soul"
superlative).

## 6. Hairstyles (item E)

- **Flora = main default, unchanged** (owner pick). The Angel styles are
  additional switchable options.
- **Angel straight (a) — BUILT (v1):** `megami-hair-angel-straight.glb` —
  card-workflow hair: scalp cap + 36 layered cards, centre part, front length
  to collarbone, back to shoulder blades, **wide blonde streak as its own
  material layer at the front-left**, **black headband** as a separate mesh
  across the hairline. Vertex group `head` (weight 1.0) on all parts; rig
  binding + spring-bone physics are the hair-wiring lane's step (coordination
  note in §8). Textures: procedural strand cards (black + blonde).
  Known v1 limits: cards are a first pass — the hair lane's Kimiko-grade
  pass (guide-curve flow, strand-map bake) is the upgrade path.
- **Curly afro (b) — NOT BUILT, reference missing.** Web search of her public
  presence (2026-11-08) surfaced no verifiable public post of THIS Angel
  Fernandez wearing a curly afro (results were interviews/articles about her
  straight-hair look, plus unrelated people). Per the brief: not guessed.
  **Needed from the owner: one photo or a link to her own public post/video
  showing the afro** — then it can be built to the same standard.

## 7. Assets in this PR

- `megami-angel-pilot2.glb` — full model: v4 base + AngelFace key (on) +
  tattooed skin textures. Blender re-export, uncompressed, 90.7 MB —
  uploaded as release asset `megami-pilot2-20261108` (too large for a
  git blob); the 45 MB meshopt-preserving tattoo-base GLB is on the same
  release (the blob API rejected it at 45 MB with a 422). Export note:
  morph-target normals were disabled in the final export (VM memory);
  base normals are untouched and three.js renders the targets correctly
  (see proof), but a production re-export with morph normals on is a
  worthwhile pipeline step.
- `megami-hair-angel-straight.glb` — hairstyle option (a).
- Painted skin textures (Parvati_Torso / Parvati_Leg / Parvati_Arm) as
  standalone PNGs for the game pipeline.
- Proof renders (§8) + this report + the bio draft.

## 8. Proof (all rendered from the shipped GLBs, viewed by the builder)

Under `docs/proof/2026-11-08/megami-pilot2/`:
- `proof-face-sidebyside-front-20261108.png` — Angel 457 frame | Megami
  before | Megami Pilot 2 (AngelFace on). Cameras differ per panel
  (source video vs two harnesses) — labelled in the image.
- `proof-face-sidebyside-34-20261108.png` — Angel 457 f120 | Pilot 2 3/4.
- `proof-face-front-20261108.png` / `proof-face-front-angeloff-20261108.png`
  — same-camera gate pair (key on/off).
- `proof-tattoo-front-20261108.png` — T1 (6 butterflies, right thigh),
  T2 (5, left thigh), T3 script, T4 outer-left-thigh piece at the edge,
  T8 script visible on the right arm.
- `proof-tattoo-back-20261108.png` — T5 wing row blade-to-blade, T6/T7
  swirl field hip-to-hip and down the backs of the thighs.
- `proof-tattoo-arm-20261108.png` — right arm: T9 feather patch + T8
  two-line canon script.
- `proof-fullbody-attire-20261108.png` — full body in attire1 with Flora.
- `proof-hair-angel-front/34/back-20261108.png` — Angel straight style:
  centre part, blonde streak layer front-left, headband, back length to
  shoulder blades.
- `proof-hair-compare-20261108.png` — Flora (kept default) vs Angel
  straight, same framing.

## Deviations

- The mocap lane's original `v457_face_mesh.csv` could not be recovered from
  any repo/release; identity landmarks were re-tracked from the held frames
  with the same tool (MediaPipe) and the plan's own gates. Numbers differ
  from the lost CSV only in sampling (every-20f frames).
- Vertical face ratios excluded from the warp (camera-pitch contamination,
  §2). If the owner wants the vertical likeness pushed too, a matched-pitch
  render pair is the next step.
- Hair (a) is a v1 card build, not the Kimiko-grade final; the headband is a
  separate strip mesh (toggleable in the mesh list).
- The face gate does not pass at the plan's ≤3% bar for either the keyed or
  unkeyed model (camera-mismatch dominated, §2). The key ships at weight
  1.0 as the measured-ratio build; if the owner prefers, it dials to 0
  with no other change.
- T3 built under the canon-fill order despite the catalogue's "unconfirmed"
  flag; flagged in §3 for the owner's ruling.

## Proof

- [x] Self-check: face side-by-sides, tattoo placement renders (front/back/arm),
  full-body, and both hairstyle comparisons rendered from the shipped GLBs
  and viewed by the builder before this PR was opened.

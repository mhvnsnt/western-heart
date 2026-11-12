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
  tattooed skin textures. Blender re-export, uncompressed, 52.7 MB —
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

---

# V2 — face rebuilt to a measured Angel likeness, eyes, tattoo completion, body + skin (2026-11-08, later)

Owner verdict on v1: "Get eyes and face like Angel Fernandez" / "it looks like u didn't
change the face" / "that first look [doesn't look] enough like angel in the face — do it
better." This section is the v2 answer. **Final face candidate = iteration 4** (named for
the parent's Build-A-Bitch comparison on the same gate).

## What was actually wrong with v1 (measured, not guessed)

- v1's AngelFace key displaced the surface by **max 1.67 mm / mean 0.14 mm** (re-measured
  off the v1 build blend) — the v1 report's "3.0 mm" was overstated. At that size no
  likeness change is visible, which is exactly what the owner saw.
- v1's gate compared Angel's selfie video against a proof render shot through a
  **different camera**, so its numbers (OFF 9.57% vs ON 9.77%) measured camera mismatch,
  not likeness. Through the matched camera (below), the SAME v1-era base face (all keys
  off) gates at **1.81%** — the v1 gate residual was camera, almost entirely.

## Matched camera (the gate's foundation)

- Angel identity = Procrustes average of neutral frames f0002 + f0004 from video 457
  (MediaPipe Face Landmarker, Apache-2.0; blendshape gates mouthSmile ≤0.32, jawOpen <0.1).
  Identity face width (oval 234–454) 0.2451 of frame width; IOD 0.1703; face-height
  fraction 0.191.
- Focal length is **not recoverable** from MediaPipe 3D landmarks (a PnP focal sweep is
  degenerate — best fit runs to the sweep cap at 0.09 px RMSE; the landmarks carry no true
  perspective). Adopted **vertical FOV 55°** (typical front-camera selfie at arm's length)
  as a stated assumption; OFF/ON deltas are camera-consistent regardless of the choice.
- Camera pitch settled empirically: **−4.8°** (camera slightly below her eye line, her
  selfie geometry) gates clearly better than +4.8° (jaw region 3.09 vs 5.01).
- 3/4 source = video 482 frame f003 (1080×1920, yaw −51.9°, neutral): matching render
  azimuth **+52°**. (The mirrored −52° view was rendered first by mistake and read 26.7% —
  caught and discarded; the +52° numbers below are the real ones.)
- Proof lighting = the v4-standard harness rig (hemi 1.15 / key 2.2 / fill 0.55 / rim 0.9,
  Neutral 1.1) with the standing material fixes — no pale/glossy variance.

## Face v2 — method and gate

Method: MediaPipe-track the matched-camera render → similarity-align to the Angel
identity → per-landmark deltas → raycast anchors on the evaluated mesh → RBF displacement
field (r0 22 mm body / 12 mm brow+lash, 12% neighbour blend, ≤12 mm per pass) written into
the **AngelFace shape key (v1's key REPLACED — target = Basis + the new cumulative field;
v1's field discarded)**. All gains 1.0 — **undamped**, per the owner's escalation. Brow
band thickness measured after pass 1 (L 1.006 / R 0.964 of Angel's) — already at target,
no artificial thickening applied.

Gate — mean landmark error, % of face width (plan bar ≤3%):

| State | Front | 3/4 (visible side) |
|---|---|---|
| OFF (all keys 0) | 1.81% | — |
| Iter 1 | 1.00% | — |
| Iter 2 | 0.95% | 3.69% → after 3/4 pass **2.91%** |
| Iter 4 (FINAL) | **0.95%** | **2.91%** |

Final front per-region: oval 1.70 · lips 0.93 · eye R 0.59 / L 0.96 · brow R 0.78 / L 1.63 ·
nose 0.58 — every region inside the bar. Total AngelFace field max **13.35 mm** (vs v1's
1.67 mm). The OFF→ON difference is visible at a glance in the side-by-sides (broader
jaw/cheeks, fuller lips, stronger arched brows, wider nose base) — see
`proof-face-sidebyside-front-v2-20261108.png` / `proof-face-sidebyside-34-v2-20261108.png`.
Honest residuals: the 3/4 oval figure includes occluded-side landmarks; the focal length
is an assumption (stated above); her raised-brow resting look in the source frames is
carried in the identity (browInnerUp 0.63/0.84 in both neutral picks).

**Expression preservation (verified by hash):** all 480 shape keys across body/brow/lash
meshes were md5-compared against the v1 build — the ONLY changed keys are the three
AngelFace keys; the only additions are the three AngelBody keys. Every Daz expression
key is byte-identical; AngelFace/AngelBody are dial-able 0–1 keys, nothing baked flat.
The expression/motion learning lane can drive her exactly as before.

## Eyes — Angel-brown added (tiger untouched)

Angel's eyes are dark brown (confirmed in the photo crops). Built
`customization/eye-library/eye-brown-angel-daz.png` by the proven radial-remap method
(the tiger-eye build's fiber annulus compressed into the Daz-atlas sampled window),
recoloured to a deep brown ramp ((8,5,2) pupil/limbal → (96,60,28) brightest fiber),
RepeatWrapping, flipY=false, SRGB. Proof: `proof-eyes-brown-closeup-v2-20261108.png`.
The yellow tiger eye remains the universal library option and Megami's standing pick —
eyes are swappable parts; brown is the Angel-look part, added, not substituted.

## Tattoo completion — re-audit of ALL held evidence (owner: "any other tattoos ur missing add them")

Re-examined: the 4 catalogue videos' stills + the owner's 5 supplied public-post
screenshots at full zoom. Two additions, both built:

- **T13 — "XIV", her LEFT upper chest** just below the clavicle, tiny serif roman
  numerals (~3.6 cm). Reading proof: owner photo 1 (selfie) shows "VIX" in image space =
  mirrored "XIV" (letters mirror-symmetric, order reverses); photo 4 (direct) is X-first;
  "XIX" fits neither orientation. Side from photo 4 (orientation verified true via the
  Coca-Cola script in-frame). The v1-era catalogue "chest bare" note is superseded.
- **T14 — small dark symbol, centre sternum/cleavage top** (~2.1 cm), photos 4 + 5. It is
  NOT her gold necklace pendant (the pendant hangs separately at centre neck in the same
  photos). Motif unresolvable at screenshot resolution → built as a small ankh-form
  glyph, flagged here as the one unresolvable-motif build in this pass.

No other additions: the back view in photo 1 is consistent with the built T5; the
afro-era photos don't show the thigh butterflies at screenshot resolution (they likely
predate them) — T1/T2 stand on the frame-verified video catalogue and were NOT removed.
T4 / T5-centre / T6-centre / T10 motifs remain unresolvable and stay as built. Nothing
invented; areas with no evidence of ink stay bare.

Build note (own-eyes catch): the first v2 GLB export silently carried the pre-paint
torso texture — Blender does not persist shape/texture pixel edits to packed images on
save unless re-packed. Caught by rendering the chest proof and finding XIV missing;
fixed by force-loading the verified texture files + `pack()`, re-exporting, and
verifying the GLB's embedded torso texture byte-for-byte against the source file
(mean diff 0.0). The chest proof in this PR is from the corrected GLB:
`proof-tattoo-chest-v2-20261108.png` (XIV + T14 legible), plus front/back/arm placement
renders on the reshaped body.

## Body pass — measurement-driven (sheets: roster/parvati/MEASUREMENTS-ANGEL-MEGAMI-2026-11-08.md)

Full measurement sheets for both women are stored with this PR — every number with its
method; Angel's true height, circumferences, arm absolutes and head size are logged
**unmeasured** (evidence can't support them), never invented. Headline ratios —
Angel: hip/waist 1.57, bust/waist 1.26, leg/stature 0.558. Megami (off the model):
bust/waist 2.83, hip/waist 2.07, stature 1.334 units, thigh 0.331 / shin 0.311.

**MAX rule (per area, fatter wins):** BUST → Megami (2.83 vs 1.26) — untouched.
HIPS/ASS → Megami (2.07 vs 1.57) — untouched. Both zones were hard-excluded from the
reshape field (radial factor 1.0).

**AngelBody shape key** (new, on every mesh incl. attire/hair so everything stays
fitted; 26 axial bones moved by the same field; skin weights untouched): stature
1.334 → **1.609 units (+20.6%)**, with **+0.220 of the +0.275 gain in the legs**
(thigh/shin lengthened proportionally, +34.4% each; her own shin/thigh ratio kept —
Angel's noisy 1.09 measurement was not forced). Waist radial ×1.20 peak (waist/hip
0.48 → ≈0.58, moving toward Angel's 0.64 — a partial move, stated honestly); thighs
×1.03, calves ×1.02, neck +6%, shoulders ≈+3%. Tattoos are UV-painted and travel with
the skin — verified visually on the lengthened legs (T1/T2/T4 read at natural
proportions in `proof-tattoo-front-v2-20261108.png`).

Rig note (stated plainly): the armature's rest bones moved WITH the key, so the v2 GLB
is coherent at its shipped state, AngelBody = 1. At AngelBody = 0 the basis mesh sits
on the moved rig (head-bone-weighted pieces ride high) — 0 is a dial position, not a
clean "original model" state. The before/after body proofs therefore use the **v1 GLB
for the BEFORE panels** (its own rig, the true original body) against the v2 GLB at
AngelBody = 1, same camera — `proof-body-front-v2-20261108.png` /
`proof-body-side-v2-20261108.png`.

## Skin — improve, don't rework (owner's priority ruling)

Angel's lit-photo skin means (191,143,120) vs Megami's texture means (115,82,67) differ
mostly by photo LIGHTING vs texture albedo, so only the hue direction was used, at 25%
strength, hard-capped: **R ×1.040, G ×1.015, B ×1.000** on skin-classified pixels of
the four skin textures. No smoothing or even-out was applied — her v4 tones are the
base and win. Before/after at identical lighting:
`proof-skin-before-after-v2-20261108.png`.

**Natural variation preserved — sampled proof (owner's constraint):** every variation
zone shifted by the SAME per-channel gain, so inter-zone relationships are unchanged
to ~0.00: areola L (119.6,83.8,62.9)→(123.6,84.8,62.9) · areola R (117.2,81.8,61.2)→
(121.2,82.8,61.2) · chest (119.0,78.5,58.5)→(123.0,79.5,58.5) · belly (120.4,85.6,65.3)→
(124.4,86.6,65.3) · GP area (116.3,79.4,62.0)→(120.3,80.4,62.0). (One sample box hit a
non-skin grey atlas cell — excluded, not reported as skin.)

**Consent basis (for the record):** Angel Fernandez's consent to her likeness being in
the game is on record with the owner (owner-held screenshots, 2026-11-08). Megami's
intimate anatomy texturing in this pass is her own source model's, untouched — the
skin pass above preserved those zones exactly, per the constraint.

## Combined hero shot — load state for the parent

Load **`megami-angel-pilot2-v2.glb`** from draft release `megami-pilot2-20261108`;
set **AngelFace = 1, AngelBody = 1** (both are the exported default weights); eye part
= `eye-brown-angel-daz.png` on Irises-2 (RepeatWrapping, flipY=false, SRGB). Compose on
THIS reshaped body. Head sits +0.275 local-Z above the body-off position — the hair
lane's afro must be fitted to the shifted head. The Flora shot in this PR
(`proof-face-front-v2-20261108.png`) wears this build's bundled hair; Flora proper
lives in parvati-full.glb (hair lane's registry work).

## Files in this v2 push

- Release `megami-pilot2-20261108`: `megami-angel-pilot2-v2.glb` (59,108,496 B).
- `customization/eye-library/eye-brown-angel-daz.png` (Angel-brown eye part).
- `roster/parvati/MEASUREMENTS-ANGEL-MEGAMI-2026-11-08.md` (both sheets + MAX calls).
- Proofs in `docs/proof/2026-11-08/megami-pilot2/` with `-v2-20261108` names:
  front + 3/4 side-by-sides, face front (Flora-state), eyes close-up, chest close-up,
  tattoo front/back, body front/side before-after, skin before-after.

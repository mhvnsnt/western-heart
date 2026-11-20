# TOU BODY — BUILD RECORD (roster wire-up Batch C, 2026-11-09)

Tou was one of the last two modelPending souls: no own-body file existed in
holdings, and the no-wrong-body gate (owner 2026-10-23, #866) forbade the
declared Pantera rider body. His base is Paul Phoenix, whose parts the owner
holds in the Tekken 7 pakchunk0 (Steam depot pull, game-reverse-engineering
releases). This build extracts Paul's own parts and assembles them into
`game/assets/models/tou-body.glb` — Tou's first body of his own.

## Extraction (PR #1700 machinery, reused as-is)

Driver: `tools/extract/t7/` pattern, run from the T7 wire-up lane's
`extract_bases.py` (pak range reader over the GRE wave1 release parts —
byte-identical depot bytes; the western-heart mirror transfer is not a
prerequisite). Kit located from the pak index, code `pau`:

| Slot | Pak asset | Joints | Verts |
|---|---|---|---|
| face | `Face/pau_fac/Meshes/SK_CH_pau_face.uasset` | 207 | 2,686 |
| face hair | `Face_Hair/pau_fah_1p/Meshes/SK_CH_pau_fah_1p.uasset` | 207 | 514 |
| hair | `Hair/pau_har_1p/Meshes/SK_CH_pau_har_1P.uasset` | 207 | 3,438 |
| upper | `Upper/pau_bdu_1p/Meshes/SK_CH_pau_bdu_1p.uasset` | 213 | 4,376 |
| lower | `Lower/pau_bdl_1p/Meshes/SK_CH_pau_bdl_1p.uasset` | 213 | 21,477 |

Deviations found in the game itself, recorded plainly:

- Paul's face mesh is named `SK_CH_pau_face`, not the `SK_CH_pau_fac` stem
  every other base uses — the standard kit pattern misses it; it was
  extracted explicitly. There are no Head/ or Extra/ item dirs for `pau`;
  the face mesh carries the head.
- The face package skins against a face-variant skeleton spelling two bones
  `Base`/`HEAD` where the body skeleton uses `BASE`/`Head`. Proven the same
  bones before merging: inverse bind matrices match to ≤5e-7 (and `Base`
  weights zero vertices in the face mesh).

## Assembly (one model, Paul's parts only)

- Single merged skin on the shared T7 base skeleton (union of the parts'
  joint sets, 213 joints, Namco weights carried per-vertex; umodel's
  normalized-ubyte WEIGHTS_0 decoded to float).
- Core bones canonicalized to the game's bone names — `Hip→Hips`,
  `L_Shoulder→LeftShoulder`, `L_Arm→LeftArm`, `L_UpLeg→LeftUpLeg`,
  `L_Toe→LeftToeBase`, fingers to `LeftHandThumb1…` form — the
  kinpo-t8/phantom-t8 precedent (native skeleton kept, names
  canonicalized) so the game's name-indexed banks bind. Facial, helper and
  offset bones keep their T7 names as inert extras. The T7 skeleton's
  first spine bone is `Spine1`; there is no `Spine` bone (the game does
  not require that track — same class as the 2-spine T8 models).
- Inverse bind matrices recomputed from the final node tree; post-build
  check: max |globalBind × IBM − I| = 6e-08.
- Uniform scale to the soul-body class height: total bounds 1.750 m,
  feet at y = 0 (native span 2.054 m including the flat-top).
- Materials (28): 26 textured from Paul's own T7 textures — the parts'
  own diffuse/normal maps plus his Common skin material instances
  (`MI_CH_pau_skin_face/arm/body/hand/neck`) and the shared mouth/teeth
  assignments Paul's face mesh itself declares (`MI_CH_mouth`,
  `MI_CH_lar_teeth` — shared Common assets in his own kit list). Two
  materials carry an authored flat colour because the game's own
  instances carry no diffuse texture: `MI_CH_tear_2` (near-black) and
  `MI_CH_eye_shadow_2` (soft shadow tint) — the material audit's
  authoredFlat class, same as kai's hair repair in Batch A.

Validation (structural, on the shipped file): 5 meshes, 32,491 verts,
weight sums = 1 on every vertex, 0 joint-index overflows, game-canonical
bones 49/50 (only `Spine` absent, above), bounds exactly 1.750 m.

`tou-body.glb`: 48,766,932 B, sha256
18cf4f362e9bcb00dc31c4403603fec084cd1a2a0637b57e1a48822a87550edf.

## Wiring (Batch A pattern)

- `game/js/assets.js`: `tou-body` key. `game/js/roster-full.js`: tou
  `model: 'tou-body'`, modelPending removed. `game/js/select-screen.js`:
  tou off SELECT_HIDDEN. `game/tests/model-key-guard.test.mjs`: tou
  `pending` → `own: [tou-body]`.
- Portraits: tou's select card IS the fresh capture from this build,
  taken through the game's own portrait path (window.capture on
  game/portrait-capture.html — attire-1 model, paul bank stance):
  manifest records model tou-body, 213 bones, stance true, framed true,
  and tou leaves KNOWN-PLACEHOLDERS (byou is the last registered
  placeholder). The same capture session re-shot gyou and kai on this
  branch and reproduced Batch B's carried cards BYTE-IDENTICALLY
  (sha256 ecaa2e20… / 88942c0e…), which is Batch B's branch-state load
  proof. The fight-harness proof (tools/proof-harness/fight.mjs) did not
  complete in this lane's sparse tree — page load timed out on repeated
  attempts under box load; it remains the one open proof item and is
  named as such in the PR.

Untouched per orders: ZEN (owner ruling pending), RYUJI (owner ruling
#6), BYOU (still no Wang body in holdings — stays modelPending),
BF-MAIME (texture production, not wiring), MADELYN (separate lane).

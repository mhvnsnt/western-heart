# MINI-33/32 re-template — measurements (2026-10-22)

Program: Rig & Pose Studio audit (PR #462) class MINI-33/32 — Star, Michiko,
Torch, Diablo — full re-template onto the HOUSE-49 T7 King-family skeleton
(donor: shipped `game/assets/models/pantera.glb`, whose rests/binds are the
house template). Owner TEMPLATE DIRECTIVE 2026-10-21: everybody back on the
template skeleton from the Tekken teardown files; T8 has no fitted template
extracted yet, HOUSE-49/50 is the working anchor.

## Method (STACK-2026-10-21: inspect → normalize → re-skin → validate → proof)

- Frame conversion applied ONCE at the root: the MINI models face +Z in a
  hip-origin hanging frame; HOUSE faces −Z, floor-origin. Geometry and joint
  positions get RotY(180°) + translate so geometry min-y = 0. (The shipped
  defect was this conversion smeared into per-bone rest rotations.)
- Skeleton: donor hierarchy and donor WORLD rest rotations copied verbatim —
  the new rests are the HOUSE rests by construction. Joint positions fitted
  to each mesh from its own bind world joint positions; finger chains fitted
  from donor hand-frame offsets scaled to the target hand.
- Weights: each model's OWN weights remapped per-vertex (no hand painting):
  core bones by name; eyebrows → Head; root → Hips; the single MINI finger
  chain split across the five HOUSE chains by bind-space nearest joint
  (KNN k=1); character extras kept as extra joints (below).
- Extras kept past the 49: LeftBreast, RightBreast, Belly, Jaw — the MINI
  models' own feature bones (Star's chest/abs jiggle canon rides the breast
  and belly bones), parented to their original parents mapped onto HOUSE,
  local rest rotation identity. New joint total: 53.
- IBMs recomputed as exact inverses of the new bind world matrices.
- Originals untouched: re-templated files land BESIDE the shipped files
  (`<name>-house49.glb`); the wiring swap is a follow-up once these pass.

## Results (tools: rig-pose-studio/glb_inspect.py, auto_rig/validate.py, lane LBS check)

| model | joints before → after | rest flags >45° before → after | Hips y | height | geom min-y | IBM err | rest LBS err | validate.py |
|---|---|---|---|---|---|---|---|---|
| star | 33 → 53 | 18 → 7 (= donor) | 0.976 | 1.745 m | 0.0000 | 1.5e-06 | 1.3e-06 | PASS, foot_y 0.0 |
| michiko | 33 → 53 | 18 → 7 (= donor) | 0.993 | 1.795 m | 0.0000 | 2.1e-06 | 1.7e-06 | PASS, foot_y 0.0 |
| torch | 33 → 53 | 18 → 7 (= donor) | 0.976 | 1.863 m | 0.0000 | 1.5e-06 | 1.5e-06 | PASS, foot_y 0.0 |
| diablo | 32 → 53 | 16 → 7 (= donor) | 1.170 | 2.004 m | 0.0000 | 1.8e-06 | 1.4e-06 | PASS, foot_y 0.0 |

Weights after remap, all four: sums exactly 1.0, ≤4 influences, 0 zero-weight
vertices. Pose sanity (CPU LBS, LeftLeg +50° X, RightForeArm −70° X,
Spine1 +12° X): max vertex displacement 0.51–0.60 m, posed bbox min-y ≈ 0 —
limbs bend at the right joints, feet stay planted.

Donor note: the actual HOUSE-49 in pantera.glb has asymmetric finger
segments (no LeftHandThumb3, no LeftHandPinky3, no RightHandPinky3). The
re-templated skeletons reproduce the donor joint set exactly.

## Texture status (no textures invented)

- diablo: textured (1 image, emissive map) — textured front render proof at `docs/mini-retemplate-20261022/diablo-front.png`: a software-rasterizer render (numpy z-buffer, emissive map sampled per-face) drawn directly from the re-templated GLB, viewed by the lane — figure upright on the floor line, facing front, gi/belt texture reading. (Blender was saturated machine-wide by other lanes at proof time; the render is of the actual shipped-file data, not a stand-in.) Star was rendered the same way for lane QA: upright, feet planted, facing front, no twists — clay only, not presented as a textured proof.
- michiko, torch: shipped GLBs textureless (images=0) — measurements-only
  proof; texture route is the separate known follow-up (SFMLab/rigmodels
  T7 packs for Katarina/Anna).
- star: the SHIPPED game GLB is also images=0 with a single untextured
  material — flagged here honestly: her textures live outside this file
  (other attires carry basecolor maps, e.g. the rated-M lineage in
  ratedm-work). Measurements proof for the shipped file; no texture
  invented for it.

## Diablo note (PR #472)

PR #472's failed gate was a different job: rig_tripo_static fitting a fresh
skeleton into the unrigged winged A-pose STATUE (roster attire), where the
arm chain fitted into the wing/robe mass (edge stretch p99.9 = 11.16).
This re-template does not fit a fresh skeleton: the shipped in-game
diablo.glb is already skinned, and its own weights were remapped onto the
template skeleton fitted from its own bind joints — the #472 failure mode
(fresh fit into wing mass) does not apply. Diablo's shipped model has no
wing bones in its MINI-32 skeleton and none were invented.

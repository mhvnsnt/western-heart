# Phase B2 proof — Megami, straight hair, STRAND-LEVEL sim (megami-straight-v2)

**Verdict first.** Phase B (v1) was vacuous: the collision core was
proven, but the visible hair was never simulated — 19 guide bones
whose tips never came within ~68 mm of the body. This v2 proof fixes
exactly that. The visible hair — all 174,406 strand vertices of the
registered straight part — is now deformed from 217 simulated guide
strands (2,120 Verlet/PBD particles) that FALL under gravity and
COLLIDE with the body. The measured pair discriminates, in numbers
and on screen:

| settled state (node, 200 steps) | strand verts inside body SDF | maxPen |
|---|---|---|
| BIND floor (as authored/worn, no sim) | 2,605 / 174,406 (1.5%) | 35.2 mm |
| BEFORE — sim, collision OFF | 75,630 / 174,406 (43.4%) | 102.2 mm |
| AFTER — sim, collision ON | 16,354 / 174,406 (9.4%) | 47.7 mm |

Browser full-motion run (160 frames, head turn + torso sway),
AFTER: inside mean 15,547/frame (8.9%), worst frame 19,364,
maxPen 69 mm. The BEFORE browser run never survived the box's
renderer weather (three attempts, §5): its video covers frames
0–36 and is labelled partial; the BEFORE *measurement* of record
is the node settled pair above plus the in-frame overlay counts
on the captured frames. Nothing is stitched or reconstructed.

**Read §4 before quoting the AFTER vert counts.** The solver's own
contract — the simulated particles — is exact: after settle, every
FREE particle rests at or outside the SDF margin (237 particles in
the margin band, 0 deep). The residual inside *vertices* are a
binding-geometry fact, disclosed and measured, not solver
penetration.

## 1. Design (researched, industry standard)

- **Guide/follow strands (AMD TressFX, Tomb Raider 2013)** — Hodes/
  Engel GDC deck: simulate a few hundred guide strands; every
  render vertex follows its guide. Sources: slideshare.net/
  slideshow/hair-intombraider-final/20208628; wccftech TressFX
  coverage. Per-strand Cosserat rods (film) were rejected: no
  60 Hz CPU win at this scale; Follow-the-Leader rejected in
  favour of PBD + substeps.
- **Integration** — Verlet + position-based dynamics (Jakobsen;
  Müller et al. 2007; XPBD, Macklin et al. 2016): distance
  constraints preserve LENGTH ONLY — direction is free, gravity
  wins, strands drape. There is deliberately NO stiffness-to-
  animated-pose term (that term is what made v1's hair-spring
  vacuous).
- **Contact layer** — the collision core from PR #1703
  (collideSphere / BodySDF project + PBD friction), unchanged.
- **Bake** (`tools/collision/bake-strands.mjs`): cards = connected
  components of the strand prims (3,208 cards); centrelines by
  PCA-axis row binning; guides selected greedily by PATH distance;
  every vert bound to a guide with a RELATIVE-frame binding
  (offset in the vert's own card frame + 9-float frame-change
  matrix). Bind round-trip gate: **0.000 mm worst over all
  174,406 verts**, enforced at bake time.
- **Wear seating**: the bake takes the body GLB and skins the
  strand verts by the part skeleton driven by the BODY skeleton
  at bind (per-joint world delta; 24/28 joints matched). Bake
  space == sim space == body-joint frame. This was forced by
  measurement: the part's geometry is authored elevated (head-
  weighted verts up to y 1.875 in geometry; part head joint 1.629
  vs body Head 1.4802) — unseated guides rooted at the scalp ran
  up to y 1.86 and gravity dropped those masses through the body.
  The upstream cause is the part's fit state (HAIR-FIT lane); the
  bake seats strands as-worn so collision can be proven on them.
- **bindSdf**: with `--sdf-prefix`, the bake samples every guide
  particle's bind signed distance against the body SDF and ships
  it in the header — the data behind the scalp-attach rule (§3).

## 2. Solver rules added this lane (all measured, all regression-tested)

1. **Deepest-projection-wins collision.** Sequential projection
   against OVERLAPPING colliders ping-pongs a trapped particle
   between facing surfaces; the distance constraint converts the
   ping-pong into a slingshot (measured 13 m/s on a guide-root
   particle trapped between Neck→Head and the fitted r=0.2434 m
   Spine2→Neck capsule; end speed scaled monotonically with the
   capsule radius). `_collideAll` now evaluates every collider
   against the particle's original position and applies only the
   deepest projection, friction once, with that collider's
   normal — order-independent (the same pair in either array
   order: 0.108 m/s frame-delta).
2. **Fringe rule.** Guides with ≤3 particles (43 on this bake) are
   bang wisps/cap fringe: pinned wholesale to the head anchor.
   A single free particle of a 2-particle guide inside a collider
   volume was teleported 155 mm to the collider surface,
   stretching every bound card.
3. **Scalp-attach rule.** Particles authored within 12 mm of the
   body surface at bind (52 on this bake) are attached along the
   scalp — the cap/weave anchoring model of the HAIR-FIT
   STANDARD. Endpoint-only guides cannot represent up-swept
   strands that lie ON the head: unattached, guide 65's chain
   swung off the scalp and its bound verts landed 86 mm inside
   the body while every particle was outside the SDF.
4. **Capsules excluded from the strand posed set.** The fitted
   capsule radii (up to 0.3313 m for Arm→ForeArm) put capsule
   SURFACES inside the head volume — body-scale colliders, unfit
   at 15–30 mm hair-segment scale. Strands collide against the
   body SDF (the true surface) + the fitted head sphere. The
   capsules remain the core's colliders for body-scale use.

## 3. What was run

- Stage: `proof-stage/stage-strands.html` (in this PR under
  docs/proof/2026-11-09/megami-collision-strands/), same dark
  stage/lighting/camera as v1 (validated `&cx=0.36&cy=0.34&cz=0.85`),
  deterministic 60 Hz, 3 substeps × 6 iterations, bend 0.15;
  200 settle steps at bind before frame 0 (disclosed in-stage).
  Motion: settle → head turn (yaw 0.55) → torso sway → settle,
  160 frames = 8.0 s.
- Body: `megami-angel-pilot2-v5.glb`; hair: registered straight
  part; bake: `baked/megami-v5/` (SDF + strands, wear-seated).
- Anchors: bake space IS the joint frame — setAnchor identity;
  posed quantities are bind-relative bone deltas; the sunk-skin
  compensation (−0.1946 on the part root) applies only when
  converting sim → render space, as in v1.
- Measurement: EVERY captured frame, all 174,406 deformed strand
  verts sampled against the body SDF in-page (inside / maxPen /
  meanPen), never from pixels. Node diags reproduce the settled
  state independently (diag_seated / diag_sdfset patterns).

## 4. The honest limits (read before quoting)

- **Bind floor 2,605 verts.** The part as worn interpenetrates the
  body before any simulation (authored offsets reach 152 mm;
  159 verts >10 mm deep at bind). No particle solver can un-author
  card offsets; the AFTER count can never go below this floor
  without a hair refit (the hair-fit lane's open work).
- **Residual AFTER inside verts (16,354 settled)** are bound verts
  whose card offsets wrap INTO the body around guides that rest
  ON the surface — e.g. guide 73's root sits at SDF +19 mm while
  its s≈0 card verts sit 37 mm inside. Particle-level penetration
  after settle is ZERO deep (deepest free particle at the margin).
- **Deform integrity**: triangles >50 mm edge — OFF 15 (worst
  61.5 mm), ON 139 (worst 64 mm): bound cards stretched across
  the body surface by their offsets. Disclosed, not hidden.
- Textures capped at 512 px on the stage for SwiftShader memory
  (presentation only; v1 used 1024 — physics/measurement never
  touch textures).
- The legacy HairSpringSystem still runs on the stage for the
  cap/headband skinning path; it does not touch the strand prims.

## 5. Run record

- AFTER: 160/160 frames, first attempt crashed at page load under
  box load ~30 (other lanes' renders), retry completed clean.
- BEFORE: three attempts, all killed by renderer crashes under
  multi-lane box load (target crash at load; segfault after
  f002; target closed after f036; third resume crashed during
  its settle phase). Landed: frames f000–f036 (37 frames, the
  settle + head-turn-in segment), assembled as `before.mp4`
  labelled PARTIAL (37/160 frames). The full-run BEFORE measures
  file does not exist and is not fabricated; per-frame overlay
  counts are visible in the video itself.
- Unit tests: hair-strands 11 tests — 10 pass, 1 skip (the raw-GLB
  deform gate is wear-gated off BY DESIGN for a wear-seated bake;
  the bake's own ≤2 mm round-trip gate + finiteness carry it),
  including 3 new regressions (overlap trap, fringe pin, scalp
  attach). Core suites unchanged: collision 11/11.
- Sim cost at real counts: 2.9–3.1 ms/step (Node, 3 substeps ×
  4–6 iterations, SDF included) — 60 Hz capable; browser deform +
  normals are presentation cost on top (110–420 ms/frame under
  SwiftShader on a loaded box).

## 6. Files

- `before.mp4` (PARTIAL, 37/160 frames — §5) / `after.mp4`
  (160/160) — labelled in-frame.
- `side-by-side/` — matched frames (BEFORE left, AFTER right).
- `measures-after.json` / `summary-after.json` (full run).
  No measures-before file exists (§5) — the node settled pair in
  the verdict table is the BEFORE measurement of record.
- `diag/diag-bind.png` — settled bind still (AFTER).
- Code: `game/js/hair-strands.js`, `game/js/hair-strands.test.mjs`,
  `tools/collision/bake-strands.mjs`,
  `customization/collision/megami/megami-strands.json/.bin`.

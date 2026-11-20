# 2026-10-22 — Jiggle/face/hands teardown wiring (worker 21)

Owner: "Wire the DOA/SF/Tekken teardown findings on jiggle bones, skin
weights, facial rig, and hands into our pipeline — standardize the jiggle
setup across characters instead of hand-tuning per character."
Research: `~/workspace/jiggle-face-hands-teardown.md` (landed 2026-10-22).

## Teardown verdicts wired in

- **JIGGLE = SFV pattern**: extra spring bones in the game skeleton + runtime
  spring sim. Tekken 7 has NO jiggle bones in its base skeleton (negative
  example). DOA's Soft Engine (runtime soft-body mesh deformation) is out of
  budget for a browser game and has no recoverable bone/param data; DOA's
  product contribution = user-tunable intensity presets (Natural/DOA/OMG).
- **WEIGHTS = Tekken's shared-skeleton model**: placement solved by
  inheritance (53-joint shared skeleton); the work is painting quality —
  4 influences max (glTF vec4 + UE4), normalized weights, L/R symmetric
  naming.
- **FACE = Tekken 7 morph targets, zero face bones**. WH faces are 100%
  static today (no morphs, no face bones) — the biggest gap vs all three
  reference games. MVP set: 10 morphs. Blink timer 3–6 s, 150 ms
  close-open. Lip-sync = Tekken-style (text UI in fights; jawOpen + mouth
  morphs for cutscenes/Dorowani voice moments; full phonemes deferred until
  story mode needs them).
- **HANDS = Tekken's full finger chains**; no procedural curl in any of the
  three games (all use authored poses). Verified defect: `LeftHandThumb3`
  missing on shipped rigs (pantera leopard-king, mariposa monarch) —
  asymmetric chains are a rig-authoring bug.

## New files

- `tools/jiggle/jiggle_chains.json` (schema `wh-jiggle-chains-v2`): the
  single canonical jiggle standard. Canonical game bones (Tekken/UE4
  Left/Right-prefix convention): `Breast_L/R` (+`.001` second segments,
  parent `Spine2`), `Butt_L/R` (parent `Hips`), `Belly` (parent `Spine1`),
  optional `ThighFat_L/R`. Per-region runtime spring params (0–1 scale,
  derived from the creation-suite jiggle-schema female family — same
  owner-approved feel numbers, now driving real spring bones). Intensity
  presets: `natural` 1.0 / `doa` 1.5 / `omg` 2.2. Family sets: female
  [breast, butt, belly], male [butt], male_fat [butt, belly]. Camel-toe
  (`Pelvic_L/R`) is per-character ONLY — Torch A3 reference piece, stays out
  of the shared standard by owner spec. `bake_path` section preserves the
  PROVEN Scarlett/Star Wiggle 2 bake values byte-identical.
- `tools/jiggle/jiggle_placement.json` (schema `wh-jiggle-placement-v2`):
  standardized bone placement + weight falloff regions for adding canonical
  jiggle bones to NEW rigs (breast falloff → Spine2/shoulders, butt →
  Hips/UpLegs).
- `game/js/jiggle.js`: runtime spring-bone solver (ES module, `node
  --check` clean). Per-chain spring-damper excited by parent acceleration,
  gravity bias, intensity scaling, substepped. NOT wired into the game loop
  — integration contract in the header (game lane follow-up:
  `JiggleRig.fromMesh(mesh, family)` after load, `jig.update(dt)` per frame
  after animation, `jig.dispose()` on swap).
- `tools/auto_rig/backends/weight_conventions.py`: the WH weight standard as
  code — island fixup (moved verbatim from `blender_heat.py`), normalize all
  verts, 4-influence cap, `TEARDOWN_RULES` (max-4, normalize, L/R-symmetric
  names, finger-region isolation).
- `tools/auto_rig/backends/face_morphs.json` (schema `wh-face-morphs-v1`):
  canonical 10-morph set (`blink_L/R`, `jawOpen`, `browUp/Down`,
  `mouthSmile/Frown/Open`, `eyesWide/Squint`). Morph NAMES are the contract.
- `docs/JIGGLE-FACE-HANDS-WIRING-2026-10-22.md`: the wiring map (verdicts →
  files, what's standardized vs per-character, research priority order →
  status).
- `docs/FACE-RIG-STANDARD-2026-10-22.md`, `docs/HAND-RIG-STANDARD-2026-10-22.md`
  (hand doc carries the asymmetry repair spec for the model lane).

## Surgical edits

- `tools/jiggle/wiggle2_jiggle.py`: table-driven — bone names, spring
  params, face-guard tokens, iterations, preroll all load from
  `jiggle_chains.json` (`--chains-json` override, `--jiggle-family`
  selection). Scarlett/Star bake behavior unchanged (same 18 bones, same
  params; `ast.parse` clean; loader logic unit-tested).
- `tools/auto_rig/backends/blender_heat.py`: delegates weight fixup to
  `weight_conventions.apply()`; new `--max-influences` flag, default 4.
- `tools/auto_rig/validate.py`: new `fingers_symmetric` gate. Verified on
  `roster/pantera/attires/leopard-king/model-rigged.glb`: correctly FAILS,
  flagging exactly `RightHandThumb3` → missing `LeftHandThumb3`.

## Deleted

- `tools/auto_rig/backends/face_template.json`: superseded by the
  morph-target standard (file was 20 minutes old, unshipped, mine).

## Still per-character and why

- Camel-toe chains: Torch A3 reference piece by owner spec.
- Per-character intensity preset choice: design choice (like DOA's
  per-character bounce tuning).
- Per-mesh fitting of jiggle bone positions: placement JSON gives
  proportional defaults; the intake backend fits them.
- The asymmetric-bone repair itself: per model (model-quality lane).
- Per-move finger poses: authored with the movesets (no procedural system,
  per all three games).
- Per-character extra face morphs; full lip-sync: deferred until cutscenes
  need it.

## Flags for coordinator

- The two verified shipped rigs (pantera leopard-king, mariposa monarch)
  now FAIL the playable gate on `fingers_symmetric` — model lane should run
  the repair spec in HAND-RIG-STANDARD-2026-10-22.md (add mirrored
  `LeftHandThumb3` + mirror weights).
- `game/js/jiggle.js` needs the game lane to wire `JiggleRig` into the
  frame loop per its header contract.
- Face morph MVP sculpting (10 morphs per character) is intake-lane
  follow-up.
- WORKLOG.md was NOT touched by this lane (concurrent writers; entry lives
  here instead to avoid clobbering). During this session the local
  WORKLOG.md was accidentally truncated by a sandbox write failure and
  restored byte-exact from the GitHub blob (sha 39c0b1b5f9e4c686, 125613
  bytes, verified).

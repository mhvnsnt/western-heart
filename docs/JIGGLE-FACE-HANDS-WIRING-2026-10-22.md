# Jiggle / Face / Hands — Teardown Wiring (2026-10-22)

What the DOA/SF/Tekken teardown research
(`~/workspace/jiggle-face-hands-teardown.md`, 2026-10-22) found, and exactly
where each finding is now wired into the WH pipeline. Owner instruction:
standardize the jiggle setup across characters instead of hand-tuning per
character.

## 1. Jiggle → SFV spring-bone pattern (standardized, not hand-tuned)

**Research verdict:** DOA uses runtime soft-body mesh deformation (Soft
Engine — out of budget for a browser game, and no bone/param data
recoverable); Tekken 7 has NO jiggle bones in its base skeleton (negative
example); SFV uses extra physics bones + runtime spring sim — cheap, tunable
per region, authorable in Blender. DOA's product contribution: user-tunable
intensity presets (Natural/DOA/OMG).

**Wired:**
- `tools/jiggle/jiggle_chains.json` (schema `wh-jiggle-chains-v2`) — the
  single canonical jiggle standard:
  - Canonical game-skeleton bones (Tekken/UE4 Left/Right-prefix convention):
    `Breast_L/R` (+`.001` second segments, parent `Spine2`),
    `Butt_L/R` (parent `Hips`), `Belly` (parent `Spine1`),
    optional `ThighFat_L/R`.
  - Per-region runtime spring params (0–1 scale, derived from the
    creation-suite jiggle-schema female family — same owner-approved feel
    numbers, now driving real spring bones).
  - Intensity presets: `natural` 1.0 / `doa` 1.5 / `omg` 2.2.
  - Family sets: female [breast, butt, belly], male [butt],
    male_fat [butt, belly]. Camel-toe (`Pelvic_L/R`) is per-character ONLY —
    Torch A3 reference piece, stays out of the shared standard by owner spec.
  - `bake_path` section preserves the PROVEN Wiggle 2 bake values for the
    Scarlett/Star Rigify chains (unchanged numbers, verified in
    `tools/jiggle/proof/scarlett-wiggle2-metrics.json`).
- `tools/jiggle/wiggle2_jiggle.py` — now table-driven: bone names, spring
  params, face-guard tokens, iterations, and preroll all load from the JSON
  (`--chains-json` override, `--jiggle-family` selection). Behavior on the
  Scarlett/Star bake path is byte-identical (same 18 bones, same params).
- `tools/jiggle/jiggle_placement.json` (`wh-jiggle-placement-v2`) —
  standardized bone placement + weight falloff regions for adding canonical
  jiggle bones to NEW rigs (breast falloff → Spine2/shoulders, butt →
  Hips/UpLegs, per the research).
- `game/js/jiggle.js` (NEW) — runtime spring-bone solver (ES module):
  per-chain spring-damper excited by parent acceleration, gravity bias,
  intensity preset scaling, substepped for stability. Integration contract
  documented in its header; NOT yet wired into the game loop (game lane
  follow-up: `JiggleRig.fromMesh(mesh, family)` after load,
  `jig.update(dt)` per frame after animation, `jig.dispose()` on swap).

**Still per-character and why:** camel-toe chains (Torch A3 reference piece
by owner spec); per-character intensity preset choice (design choice, like
DOA's per-character bounce tuning); per-mesh fitting of bone positions
(placement JSON gives proportional defaults, the intake backend fits them).

## 2. Skin weights → Tekken's shared-skeleton model (fix the painting)

**Research verdict:** placement is solved by inheritance (53-joint shared
skeleton, one skeleton = trivial retargeting). The work is weight QUALITY:
4 influences max (glTF vec4 + UE4), normalized weights, L/R symmetric
naming.

**Wired:**
- `tools/auto_rig/backends/weight_conventions.py` (NEW) — the WH weight
  standard as code: island fixup (moved verbatim from `blender_heat.py`),
  normalize-all-verts, 4-influence cap, and `TEARDOWN_RULES` (max-4,
  normalize, L/R-symmetric names, finger-region isolation).
- `tools/auto_rig/backends/blender_heat.py` — delegates to
  `weight_conventions.apply()`; new `--max-influences` flag, default 4.

## 3. Face → Tekken 7 morph-target pipeline (biggest gap)

**Research verdict:** T7's skeleton has Neck→Head and NOTHING more — faces
are UE4 morph targets driven by animation curves. SFV same. WH today has
zero morphs AND zero face bones — completely static faces, worse than all
three reference games.

**Wired:**
- `tools/auto_rig/backends/face_morphs.json` (NEW, `wh-face-morphs-v1`) —
  canonical MVP set of 10 morphs: `blink_L`, `blink_R`, `jawOpen`,
  `browUp`, `browDown`, `mouthSmile`, `mouthFrown`, `mouthOpen`,
  `eyesWide`, `eyesSquint`. Mandatory on every humanoid face; morph NAMES
  are the contract for the blink timer, intro interactions, win poses, and
  hit reactions.
- `docs/FACE-RIG-STANDARD-2026-10-22.md` — the standard: NO face bones on
  new rigs (skeleton stays 53 joints); blink timer 3–6 s randomized, 150 ms;
  lip-sync = Tekken-style (text UI in fights; `jawOpen` + mouth morphs for
  cutscenes/Dorowani voice moments; full phonemes only when story mode
  needs them).
- `tools/jiggle/wiggle2_jiggle.py` face_guard unchanged — still protects
  any legacy face bones from jiggle bakes (hash-verified).

**Still per-character and why:** per-character extra morphs (creature
mouths etc.); viseme/expression tuning for cutscenes (later, when story
mode needs it).

## 4. Hands → Tekken's chains (already have them; fix + use)

**Research verdict:** full finger chains in T7's base skeleton, 2–3 segments
per digit; NO procedural curl in any of the three games — fist/open/point
are authored animation poses. Verified WH defect: asymmetric chains
(`LeftHandThumb3` missing).

**Wired:**
- `tools/auto_rig/validate.py` — new `fingers_symmetric` gate: every finger
  bone must have its L/R mirror. Verified against
  `roster/pantera/attires/leopard-king/model-rigged.glb`: correctly FAILS,
  flagging exactly `RightHandThumb3`→missing `LeftHandThumb3`.
- `docs/HAND-RIG-STANDARD-2026-10-22.md` — repair spec for the model lane
  (add mirrored `LeftHandThumb3`, mirror the weights), mitt/paw exception,
  authored pose library (fist/open/point/grab), thumb/index k-NN mapping
  rule.

**Still per-character and why:** the asymmetric-bone repair itself (per
model, model-quality lane); per-move finger poses (authored with the
movesets).

## Research priority order (from the doc) → status
1. Finger asymmetry + weight pipeline — gate wired (this PR); model repair
   is the model lane's follow-up.
2. Jiggle spring chains — standard + runtime solver wired (this PR); game
   loop integration is the game lane's follow-up.
3. Facial morph MVP — standard + canonical names wired (this PR); sculpting
   the 10 morphs per character is the intake lane's follow-up.
4. Blink timer + hit-reaction faces — runtime follow-up (game lane).
5. Lip-sync proper — only when cutscenes need it (deferred, per research).

## Files changed
- NEW: `tools/jiggle/jiggle_chains.json`, `tools/jiggle/jiggle_placement.json`,
  `game/js/jiggle.js`, `tools/auto_rig/backends/weight_conventions.py`,
  `tools/auto_rig/backends/face_morphs.json`,
  `docs/JIGGLE-FACE-HANDS-WIRING-2026-10-22.md`,
  `docs/FACE-RIG-STANDARD-2026-10-22.md`, `docs/HAND-RIG-STANDARD-2026-10-22.md`
- MODIFIED (surgical): `tools/jiggle/wiggle2_jiggle.py` (table-driven),
  `tools/auto_rig/backends/blender_heat.py` (weight_conventions +
  --max-influences), `tools/auto_rig/validate.py` (finger-symmetry gate)
- DELETED: `tools/auto_rig/backends/face_template.json` (superseded by the
  morph-target standard; file was 20 minutes old, unshipped, mine)
- WORKLOG.md entry (this work)

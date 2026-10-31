# Rig continuation — Stage 3 handoff (2026-10-31): C1 anatomy layers

Owner's H order: "next rig fix is Demonio's ember attire, then the
anatomy data that 72 of 73 fighters are missing." Stage 1 = PR
#1373, stage 2 = PR #1432. This stage builds the C1 anatomy layers
(`wh.anatomy-layers/2`, spec
`docs/research/ANATOMY-LAYERS-SPEC-2026-10-23.md`) for the roster,
each fighter from his OWN primary rigged model, in per-batch PRs.
This handoff covers the tooling and batch 1; later batches append
their sections here.

## Why the generator only ever worked on Pantera

`tools/anatomy/generate_layers.py` produced Pantera's layers in
October and silently produced EMPTY bone/muscle/organ layers for
every other rig it was pointed at. Four distinct causes, all fixed
in this PR's tooling update:

1. **Joint-name dialects.** The layer builders key on the 13
   canonical landmark names of the template skeleton (hips, spine,
   chest, neck, head, shoulder.L/R, thigh.L/R, shin.L/R, foot.L/R —
   exactly Pantera's skeleton). Roster rigs use dialect names
   (template Title-Case `Hips`/`LeftUpLeg`, Mixamo
   `mixamorig:LeftShoulder`, Unreal `clavicle_l`, lowercase
   variants). New: `canonicalize_joint_names()` maps each rig's
   landmarks (plus the arm chain upperarm/forearm/hand) onto the
   canonical names — side is always taken from the joint's own
   name, never guessed; competing claims (production rigs carry
   adjunct chains, e.g. doc-frank's 178 joints) resolve to the most
   specific stem with deterministic tie-breaks; the map used is
   recorded in every artifact under `source.joint_name_map`.
2. **Identity inverse bind matrices.** Several exporters write
   identity IBMs and carry the bind pose in node TRS only; the
   generator's inv(IBM) positions came out all-zero (deathfang:
   every joint at the origin, torso radius 0, skull radius 0). New:
   when the IBM-derived positions are all ~zero, joint world
   positions come from the node hierarchy (TRS composition),
   the same method the skin audit uses.
3. **Mesh 0 is not always the body.** The generator hard-coded
   mesh 0; on multi-mesh rigs mesh 0 can be a 16-vert attachment
   (armor-king). New: `pick_body_mesh()` builds anatomy from the
   skinned mesh with the most vertices; the chosen index is
   recorded in `source.mesh` and the skin layer's mesh_ref.
4. **Stance-posed arms.** The arm frame was fitted only from a
   T-pose horizontal protrusion; stance-posed rigs (baek) got no
   arm muscles and the morph proof crashed the run
   (`StopIteration` on the missing `biceps.L` group — after the
   layers were written, so fighters lost their proof set). New:
   `fit_arm_frame_skeleton()` falls back to the skeleton chain
   (shoulder -> hand axis, geometric radius — the same method the
   legs always used), and the morph-proof block skips with a
   warning instead of crashing when a group is genuinely absent.

**Regression proof:** with all four fixes in, Pantera's own rig
regenerates byte-identical to his landed 2026-10-23 artifact
(every field, modulo the `generated` date and the new additive
`source.joint_name_map` key, which is `{}` for him — his names
were already canonical, his IBMs real, his file single-mesh).

## Quality gate (applied per fighter before landing)

Anatomy lands only when ALL hold: >= 11 of the 13 canonical
landmarks present; >= 8 bone primitives; >= 15 muscle groups;
>= 5 organ groups; the landmark joints sit inside the bone layer
(SDF < 0, at most one miss); the generator's own proof validation
reports organs_inside_body at full count; proof.json + PROOF.md +
the 7 renders exist. Fighters failing the gate are named in this
handoff with their blocker — never landed with empty or partial
layers.

## Batch 1 (this PR) — 8 fighters

All eight: 12 bone primitives, 25 muscle groups, 7 organ groups,
13/13 landmarks — the same layer counts as Pantera's proof set.

| fighter | source model (his own) | joints | vertices |
|---|---|---|---|
| cyborg-x | roster/cyborg-x/attires/attire1/model-rigged.glb | 49 | 991,082 |
| deathfang | roster/deathfang/attires/attire1/model.glb | 73 | 67,755 |
| demonio | roster/demonio/attires/attire1/model.glb | 73 | 1,286,272 |
| diablo | roster/diablo/attires/attire1/model-rigged.glb | 53 | 989,471 |
| dio | roster/dio/attires/attire1/source/dio-a1-jade-god-rigged.glb | 73 | 1,153,744 |
| dorowani | roster/dorowani/attires/attire1/source/dorowani-a1-crimson-cheeks-rigged.glb | 73 | 1,592,528 |
| sakura | roster/sakura/attires/attire1/model-rigged.glb | 49 | 1,007,860 |
| sam-ur-a1 | roster/sam-ur-a1/attires/attire1/model-rigged.glb | 49 | 1,013,029 |

Each lands `roster/<fighter>/anatomy/` with anatomy-layers.json,
proof.json, PROOF.md and renders/ (5 layer renders + 2 morph
renders), mirroring Pantera's set. Meshopt-compressed sources were
decoded with the stage-2 decode stage before generation; the
artifact's `source.glb` always names the ORIGINAL repo path.

## Named skips (not in any batch unless their state changes)

- Owner-gated / decision-list: star (item 1), gyou (item 5),
  charger (item 6), cain-elias (item 8), koreshi (item 10) —
  anatomy is additive, but these fighters' base data is unruled;
  skipped per the continuation brief's skip-and-name rule.
- Deferred (sibling re-rig in flight — anatomy built now would be
  built on a rig being replaced): burger, negativo, purplerain.
- No roster model on main to build from (docs/intake only):
  jin-eastern-mind, kiko-tanaka, purple-rain, rave, saku-ra,
  sun-ra, tobi, wizard-gang.
- Fighters whose only roster GLB is unskinned, and gate failures
  from the first batch run, are listed per batch below as their
  fix-up results land.

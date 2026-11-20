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

## Batch 2 — 12 fighters

Same gate, same 12 bone / 25 muscle / 7 organ counts, 13/13
landmarks each.

| fighter | source model (his own) | joints | vertices |
|---|---|---|---|
| silvertongue | roster/silvertongue/attires/attire1/model-rigged.glb | 73 | 1,387,339 |
| skull | roster/skull/attires/attire1/model-rigged.glb | 49 | 1,009,636 |
| slice | roster/slice/attires/attire1/model-rigged.glb | 73 | 1,455,593 |
| thor | roster/thor/attires/attire1/model-rigged.glb | 49 | 1,023,358 |
| tsuyu-asui | roster/tsuyu-asui/attires/attire1/model-rigged-textured.glb | 52 | 123,535 |
| vainabel | roster/vainabel/attires/attire1/model-rigged.glb | 73 | 1,378,962 |
| vixen | roster/vixen/attires/attire1/model-rigged-noplane.glb | 52 | 109,854 |
| waterfall | roster/waterfall/attires/attire1/model-rigged.glb | 49 | 1,016,906 |
| yukihyo | roster/yukihyo/attires/attire1/source/yukihyo-a1-rigged.glb | 73 | 1,461,745 |
| zangief | roster/zangief/attires/attire1/model-rigged.glb | 49 | 362,385 |
| zen | roster/zen/attires/attire1/model-rigged.glb | 73 | 1,406,973 |
| zui | roster/zui/attires/attire1/model-rigged.glb | 73 | 1,542,135 |

Running total: 21 of 73 fighters with C1 anatomy on main
(Pantera + batches 1-2). The remaining candidates are in the
fix-up pass (dialect coverage extended to VRoid-numbered and
verbose joint naming; unskinned-primary fighters retried against
their rigged alternates) — results land as batch 3.

## Batch 3 — generator hardening + 9 fighters

The first batch run exposed three more dialect families and one
tooling incident; all are fixed in the `generate_layers.py` update
in this batch's PR:

- Ranked canonical claims: when several joints claim one landmark
  (production rigs carry adjunct chains — doc-frank has 178
  joints), the most specific stem wins ('LeftLeg' over
  'leg left'), with shortest-name then alphabetical tie-breaks.
  Previously any collision silently disabled mapping for the
  whole rig.
- Dialect coverage: Mixamo prefixes (side token survives the
  prefix strip), VRoid numbered rigs ('Waist_06' -> hips,
  'Stomach_07' -> spine, L/R single-letter prefixes), and the
  verbose family ('root hips', 'spine lower/upper',
  'arm right shoulder 1', 'leg left knee') via internal side
  tokens + anatomical keyword claims, with finger/toe joints
  barred from claiming landmarks. Numbered-suffix stripping is a
  fallback only, so 'spine_02' keeps its chest claim. Unit-verified
  13/13 landmarks on seven dialect sets (canonical, template,
  doc-frank real, Mixamo, Unreal, VRoid real, verbose real).
- A span-replace during the ranked-claims edit briefly removed
  the node-hierarchy fallback function; every identity-IBM
  fighter generated in that window failed with a NameError. The
  function is restored (smoke-verified on deathfang) and all
  casualties were regenerated in this batch's fix-up pass.
- Batch driver: candidates are now probed for skins and fall
  through to rigged alternates (bruno's attire1 sources are
  unskinned; his anatomy is built from his attire2 rigged model).

Pantera regression re-run against the final generator: still
byte-identical to the landed artifact (modulo date + the empty
joint_name_map key).

| fighter | source model (his own) | joints | vertices |
|---|---|---|---|
| awa-pop | roster/awa-pop/attires/attire2/model-rigged.glb | 73 | 1,365,801 |
| baek | roster/baek/attires/attire1/model-rigged.glb | 73 | 1,593,345 |
| bruno | roster/bruno/attires/attire2/source/bruno-a2-sail-the-sea-rigged.glb | 73 | 1,257,159 |
| buffalo-bill | roster/buffalo-bill/attires/attire3/model-rigged.glb | 73 | 1,381,580 |
| chordz | roster/chordz/attires/attire1/model-rigged.glb | 73 | 1,154,216 |
| doc-frank | roster/doc-frank/attires/attire1/post-transform/model-rigged.glb | 178 | 981,052 |
| dxmmii | roster/dxmmii/attires/attire1/model-rigged.glb | 73 | 1,303,667 |
| jin | roster/jin/attires/bloodline-ember/jin-bloodline-ember.glb | 50 | 4,326 |
| kinpo | roster/kinpo/attires/attire1/model-rigged.glb | 49 | 1,000,648 |

All nine pass the gate (doc-frank carries 13 bone primitives —
one extra axial capsule from his adjunct spine chain; the rest
are the standard 12/25/7). Note buffalo-bill and chordz generate
from the very files the rig audit records as singular-IBM
AUDIT-ERRORs: the generator's bind-position path (with the
hierarchy fallback) reads them, and the gate verifies the
resulting layers geometrically.

Running total: 30 of 73 fighters with C1 anatomy on main
(Pantera + batches 1-3).

Named, still without anatomy after the fix-up pass (final list
in the closing batch): blanka and king-tyrant (every roster GLB
unskinned — no skeleton to build from), iori (only a 3,097-vert
partial model resolves; gate landmarks 2/13).

## Batch 4 (closing) — merged body meshes + 14 fighters

One more generator correction: some bodies are split across
several skinned meshes (armor plates, shells). The generator
previously built the SDF body from the single largest skinned
mesh — armor-king's anatomy was first generated from a
1,102-vert shell of his 5,660-vert body and still passed its
containment checks against itself. `load_body_mesh` now merges
ALL skinned meshes into the body (single-mesh rigs merge to
exactly their one mesh; Pantera regression re-verified
byte-identical). Regenerated under the merged loader: armor-king
(1,102 -> 5,660 verts), jin (4,326 -> 14,498; supersedes his
batch-3 artifact), vega (a 1,991-vert fragment at 10 bone /
17 muscle -> full 12/25/7 at 10,589 verts), zafina (2,970 ->
22,462 verts).

| fighter | source model (his own) | joints | vertices |
|---|---|---|---|
| armor-king | roster/armor-king/attires/attire1/model-rigged.glb | 49 | 5,660 |
| jin | roster/jin/attires/bloodline-ember/jin-bloodline-ember.glb | 50 | 14,498 |
| kronos | roster/kronos/attires/attire1/model-rigged.glb | 49 | 1,000,375 |
| mariposa | roster/mariposa/attires/monarch/mariposa-monarch-rigged.glb | 49 | 1,013,363 |
| michiko | roster/michiko/attires/attire1/model-rigged.glb | 73 | 1,395,522 |
| mina-ashido | roster/mina-ashido/attires/attire1/model-rigged.glb | 52 | 123,772 |
| miruko | roster/miruko/attires/attire1/model-rigged.glb | 52 | 129,834 |
| panda | roster/panda/attires/attire1/source/aotsuki-a1-rigged.glb | 73 | 1,347,672 |
| parvati | roster/parvati/attires/attire1/model-rigged.glb | 52 | 109,877 |
| phantom | roster/phantom/attires/attire1/model-rigged.glb | 49 | 1,053,847 |
| rahkasa | roster/rahkasa/attires/attire1/model-rigged-textured.glb | 52 | 174,504 |
| ryuji-rock | roster/ryuji-rock/attires/attire1/model-rigged.glb | 73 | 1,454,471 |
| vega | roster/vega/attires/attire1/model.glb | 364 | 10,589 |
| zafina | roster/zafina/attires/butterfly-default/mariposa-butterfly-default.glb | 246 | 22,462 |

## Stage 3 final accounting

43 fighters carry C1 anatomy layers on main: Pantera
(2026-10-23) plus 42 generated in this stage (batches 1-4).
Every other fighter is named here with his reason:

- Owner-gated / decision list (skipped by instruction): star,
  charger, cain-elias, koreshi, gyou.
- Sibling re-rig in flight (deferred, do not double-work):
  burger, negativo, purplerain.
- No roster model on main — docs/intake only, nothing to build
  from: jin-eastern-mind, kiko-tanaka, purple-rain, rave,
  saku-ra, sun-ra, tobi, wizard-gang.
- Every GLB on main is unskinned (no skeleton to build from;
  each was probe-verified across all his candidate files):
  blanka, king-tyrant, kuma, kuma-replacement, lili, nightwolf,
  scimitar, theory, torch.
- Skeleton does not resolve to the canonical landmarks: iori
  (his only model yields 2 of 13 landmarks even with merged
  meshes; 1 bone primitive).

Stage 3 is complete for every fighter the current roster models
allow. The unskinned nine unblock the day rigged models land for
them — the generator + driver handle them unchanged.

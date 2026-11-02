# Phase 4b — created fighters in fights (2026-11-02)

Owner task (2026-11-02 coordinator sequence, step 1): wire created
fighters into fights so their template body and morphs show up in
fights, then parts and hair are next. This note records what landed,
the proof, and what is still owed. No deploy was made with this
change — the republish stays held for the owner's playtest.

## The bug

A fighter created in the Creation Suite saved its template body
(`template` + `baseGlb`, e.g. `customization/templates/meshes/
powerhouse.glb`) and its morph slider values, and the game side
already carried both through (`game/js/custom-fighter.js`,
`game/js/morph-apply.js`, PR #1496) — but the in-fight model still
resolved through the `custom` slot, the legacy Soldier base. Two
separate reasons a template body could not simply be swapped in:

1. **Bone names.** The 9 template GLBs (Blender + MB-Lab, 71 joints
   each) name their bones `pelvis, spine01/02/03, clavicle_L,
   upperarm_L, lowerarm_L, hand_L, thigh_L, calf_L, foot_L,
   toes_L, ...`. None matches the game's canonical T3 names, so
   `t3anims.js` `analyzeRig` returned null (RIG_REQUIRED unmet)
   and no T3 bank bound.
2. **No embedded clips.** The template GLBs ship ZERO animation
   clips. With no bound bank and no embedded Idle, a template
   body in a fight had no animation at all and stood in its bind
   pose — the T-pose.

## What changed

- `game/js/assets.js`
  - New `MODEL_URLS` keys `custom-template-<id>` for all 9
    templates, pointing at `customization/templates/meshes/<id>.glb`.
    The legacy `custom` (Soldier) key is untouched — the rig guard
    forbids removing MODEL_URLS keys.
  - New `remapMblabBones` (exported) + `MB_LAB_T3_BONE_REMAP`,
    following the existing Vega and Slice remap contract exactly:
    rename the cloned instance's core joints to T3 names BEFORE
    the bones dict and mixer are built; the source gltf is
    untouched; a signature guard (all MB-Lab sources present, no
    T3 target already present) makes it a strict no-op for every
    other model. Mapping: `pelvis -> Hips`, `spine01 -> Spine`,
    `spine02 -> Spine1`, `spine03 -> Chest`, `neck -> Neck`,
    `head -> Head`, `clavicle_* -> *Shoulder`, `upperarm_* ->
    *Arm`, `lowerarm_* -> *ForeArm`, `hand_* -> *Hand`,
    `thigh_* -> *UpLeg`, `calf_* -> *Leg`, `foot_* -> *Foot`,
    `toes_* -> *ToeBase`, `root -> Root` (23 joints). Twist
    and breast bones stay unrenamed: they ride their driven
    parent at rest local rotation, like Vega's intermediates.
    No bind-frame conversion was needed: the T3 retarget
    rebuilds clips from decoded frames + both rest poses, and
    the MB-Lab bind pose is already upright, Y-up, feet at
    y~0 (pelvis rest y 0.889, head 1.652, left hand at +X,
    toes pointing +Z — measured from `technician.glb`, not
    guessed). The retarget's own side/facing measurement
    agrees (swapLR false, facing +Z).
  - Spine alias guard fix: `createInstance` used to overwrite
    `bones.Spine1` with `bones.Spine` whenever any remap ran.
    Vega/Slice had no Spine1, so that was harmless there; the
    MB-Lab remap provides a real Spine1 (spine02), and
    overwriting it would collapse the torso chain. Aliases now
    fill only missing entries (`Spine2 = Chest` still applies).
  - Feet-facing cue now also recognises MB-Lab `foot_L/R`
    names, so a template's facing is measured instead of
    defaulted (it measures +Z either way).
  - `preloadBaseIdle` takes the created fighter's resolved
    template model key, so the idle warm lane warms the
    template body (2 MB) instead of the Soldier body it no
    longer fights on.
- `game/js/custom-fighter.js`
  - `customFighterToRoster` now resolves `model` through
    `templateModelFor`: a blank-mode save's `template` (or its
    `baseGlb` `meshes/<id>.glb`) becomes `custom-template-<id>`;
    a template-less legacy save defaults to `technician`, the
    suite's own migration target (`suite.js` `migrateLegacy`).
    Roster-mode saves keep the legacy `custom` slot — see
    Still owed below.
  - Moveset fallback made explicit: `moveset: 'jin'` plus
    `movesetFallback: 'jin'`, with a comment naming custom
    moveset slots as still TODO.
- `game/js/fighter.js`
  - `bankIdFor('custom', ...)` now returns `'jin'` explicitly
    (logged once) when no real `custom` moveset is registered,
    so the template body gets an animation bank. The fallback
    lifts automatically when a real `custom` moveset lands.
    Frame data for a created fighter still falls back to the
    generic move table (`getRealMove`'s `MOVES` fallback) —
    that is the pre-existing behaviour, now documented, not
    a new silent default.
  - T3-use log (owner law, 2026-10-23): the jin bank is a
    Tekken 3 decoded bank, used because no T5/T6/T7/T8/TTT2
    custom-moveset bank exists for a created fighter yet, and
    because the roster object already named jin as the
    placeholder. When custom moveset slots are wired, this
    fallback is replaced, not extended.
- `game/js/main.js`
  - The select-screen idle warm call passes the created
    fighter's resolved template model key.
- `test/custom-template-fight.test.mjs` (new, runs in CI's
  game-unit-tests job): the fight-animation proof — see below.
- Morphs stay light on a phone by construction: morphs are
  applied once at build (`Fighter._build`, and again only
  after a transform model swap in `_doModelSwap`). This
  change adds no per-frame morph call; `morph-apply.js` is
  untouched.

## Proof (test/custom-template-fight.test.mjs, 5 tests)

Run locally 2026-11-02: 5/5 pass (after the jin bank files were
present; see the Node limit below).

- All 9 templates: 71 joints, 168 morph targets each, every
  MB-Lab source bone present, `b_weight+/-` targets present.
- Roster resolution: powerhouse save -> `custom-template-
  powerhouse`; legacy save -> `custom-template-technician`;
  roster-mode save -> `custom` (still owed, by design here).
- `bankIdFor('custom', ...)` -> `'jin'`.
- Remap scope: `pantera` and `custom` are untouched; a second
  remap run on a renamed rig is a no-op.
- **Fight-animation proof on the real rig** (technician GLB
  parsed with the game's vendored three.js + meshopt decoder,
  instanced through `assets.createInstance`, jin bank bound
  through `t3anims.js` retarget, played on the mixer):
  remapped bones include all of RIG_REQUIRED plus Spine /
  Spine1 / Spine2 / Chest / Neck; Spine1 is the real spine02
  (not a clobbered alias); Spine2 aliases Chest; `b_weight`
  0.5 sets live morph influences and clearing returns to the
  template shape; the jin stance retargets and holds with
  head above hips and feet on the floor through 1.0 s; a real
  jin attack row (row:32, first row in the bank's attack pool)
  retargets and moves a limb 0.959 m from its rest pose (jin
  bank: 249 real T3 clips, 227 move-row clips, loaded in the
  test run; a T-posing fighter would measure 0).

Node limit, stated plainly: Node cannot decode the GLB's
embedded PNG textures (no `Image`), so the proof parses the
GLB directly and injects it into `assets.gltfs` instead of
going through `assets.loadModels` / `_ingest`, whose material
gate needs decoded images. In a browser the same textures
decode through the same GLTFLoader path every other fighter
uses. The material gate for template bodies is therefore NOT
proven by this test; the rig, the remap, the retarget and the
motion are. The PR's CI run (menu-touch-e2e: menu -> select
-> stage -> fight) is the browser-side fight-load check.

## Still owed (not in this change)

- Roster-mode edits (editing an existing fighter in the suite)
  still fight on the legacy Soldier slot: their `baseGlb` is
  that roster fighter's attire GLB, which has no MODEL_URLS
  key. Wiring roster attire models into fights is ORDER doc
  Phase 4 (edit existing fighters -> save attire/version).
- Custom moveset slots: still TODO. A created fighter
  animates on the jin bank (placeholder, logged) and fights
  on generic frame data.
- Parts and hair, then clothing, accessories, tattoos, scars
  and eyes, then movesets — the owner's order after fights.
  Those are the next PRs in the coordinator sequence.
- No deploy: this change rides the held republish, for the
  owner's playtest, like #1494/#1495/#1496.

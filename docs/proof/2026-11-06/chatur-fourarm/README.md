# Chatur fight-ready — Phase 1 proof (2026-11-06)

Chatur (Rahkasa, True Ogre base) was pose-only in game: her ogre bank
(211 T3 clips) loaded, her moveset was bound, but
`retargetT3Clips` returned null for every clip, so no action ever
bound. This change makes her fight, four arms included.

## Root cause (measured, not guessed)

Her fidelity GLB (PR #1572) has a FLAT hierarchy: the torso chain is
intact (Hips → Spine → Spine1 → Chest → Neck → Head), but the limb
roots — LeftShoulder/LeftArm/RightShoulder/RightArm, both up-legs,
and the secondary (waist) arm roots — are all direct children of the
armature root node `RahkasaRIG`, because the deform-only Blender
export dropped their ORG parents. `analyzeRig`'s chest search
(lowest common ancestor of the two arm parents) therefore landed on
the armature Object3D, hit `if (!chest || !chest.isBone) return
null`, and every retarget bailed. (Wave 3 item 7's DIAGNOSIS.md
recorded the bail; the flat export is the mechanism.)

## The fix (game/js/t3anims.js — data-driven retarget profile)

The industry bone-mask pattern (Unreal IK Retargeter / Unity Avatar
Mask): extra chains are unmapped from the core fit, never errors.

1. `RETARGET_PROFILES`, keyed by model key (same key
   `retargetT3Clips` already receives), holds Chatur's profile:
   `chestAnchor: 'Chest'` plus two `secondaryChains` naming her
   waist pair in the source file's own bone names
   (L: `DEF-upper_arm.L.002 → DEF-forearm.L.002 → DEF-hand.L.001`,
   R mirrored) — the names PR #1572 deliberately did not invent
   canonical replacements for.
2. When the LCA chest search lands on a non-bone, `analyzeRig`
   falls back to the rig's canonical chest anchor (profile's
   chestAnchor, else Chest/Spine2/Spine1) if it sits in the hips
   subtree. Rigs with neither still bail, exactly as before.
3. The core fit metric (contact/floor set) covers only canonical
   bones — for hierarchy-intact rigs the set is unchanged (canonical
   bones are the hips subtree there by construction).
4. Bone-name resolution survives GLTFLoader sanitization: loaded
   names lose their dots (`DEF-upper_arm.L.002` arrives as
   `DEF-upper_armL002`), so profile bones resolve through a
   punctuation-stripped index.
5. SECONDARY LAYER (Phase 1 fill): the waist pair is driven by the
   SAME bank clip sampled `timeOffsetFrames: 4` later, composed
   through the same swing-alignment solve, emitted as override
   tracks on the waist chain only (`secondaryLayer: { mode:
   'override-masked', source: 'self' }` in the profile). It is real
   clip data, not procedural motion. The layer is a per-chain slot:
   Phase 2 swaps the source per move from `layer2` blocks in
   chatur.json (donor T3 banks) without touching this plumbing.

## Unit proof — test/chatur-retarget.test.mjs (6/6, CI)

Built on test/fixtures/chatur-rig.json — the node table extracted
from her shipped GLB — with GLTFLoader name sanitization applied,
so the test runs under the browser's conditions. Asserts: retarget
no longer bails; the stance's intrinsic stamp stays the measured
source truth (L 0.69 / R 0.55 rad); stance pose passes the gate
geometry checks (head above hips, hands within reach); the waist
pair carries all six secondary tracks and its hand MOVES under an
AnimationMixer; row 38 (her "1") retargets with primary + secondary
tracks; only `chatur` has a profile; a synthetic canonical rig
retargets the jin bank unchanged and gains no secondary tracks.
Full unit suite before/after: identical results except this file
going fail → pass (the 12 sparse-checkout environment failures are
pre-existing and unchanged).

## Fight proof — live game, Chatur (P1) vs Pantera (P2), serve harness

- Bind: bank `ogre`, **22 T3 actions** (stance/light/medium/heavy/
  grab/block/hit/launch/ko/walk/dash/jumps/sidesteps). Before: 0.
- Idle plays `t3_ogre_stance@chatur`; waist hands sit posed by the
  layer (off bind pose, L/R asymmetric), not hanging at rest.
- Scripted inputs (probe sessions 1–2, opponent live, CPU frozen
  after round start; HP read from game state):

  | input | resolved | move | anim | P2 HP |
  |---|---|---|---|---|
  | 1 | 1 | First Mudra | ogre row 38 | 100 → 91.5 |
  | 2 | 2 | Second Mudra | ogre row 50 | 100 → 86.7 |
  | 3 | 3 | Low Sweep Step | ogre row 57 | 100 → 81.9 |
  | 4 | 4 | Rear Heel | ogre row 74 | whiff at 1.15 m (no damage) |
  | d/f+1 | WS.1 | Rising Palm | ogre row 134 | fired, no contact in window |
  | f+2 | f+2 | Procession Punch | ogre row 110 | 100 → 80.7 |
  | 1+3 | 1+3 | First Binding (throw) | ogre row 220 | clip fired; throw damage lands past the 0.5 s sample |

- Secondary pair in a live attack: during First Mudra the waist
  hand's max per-90 ms step is **0.191 m** against the primary
  hand's 0.280 m — the second pair swings with the strike on the
  offset layer.
- Stills: `chatur-fight-stance-20261106.png` (both fighters in
  stance), `chatur-input-1-20261106.png`,
  `chatur-input-2-20261106.png` (Pantera down, hit FX live).

## Known remaining items (stated plainly)

- **Select-screen preview gate:** the gate's check (c1) compares
  the stance clip's intrinsic clavicle swing (ogre neutral: L
  0.69 rad) against the 0.6 rad cap item 7 deliberately held. Her
  stance still exceeds it, so her select CARD keeps the CMU
  fallback pose. The threshold was NOT moved; the fight path does
  not use that gate. Separate decision, not part of this change.
- **Harness white-out:** in the serve harness her model renders
  blown-out white under stage lighting (the same known harness
  state recorded for Cyborg X in #1604; the identical GLB renders
  her dark skin correctly in Blender). Poses/animation read fine;
  a lighting/materials re-check is owed at playtest, unchanged by
  this change.

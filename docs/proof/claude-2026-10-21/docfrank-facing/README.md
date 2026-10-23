# Doc Frank "owl" fix — proof (2026-10-21, Claude session, branch claude/amazing-keller-p8644u)

Owner: "his whole body is facing the wrong way and his head is facing the right way like a owl
his body needs to turn the way his head is facing".

## Root cause (measured, not guessed)

- Doc Frank's GLBs are fine: inverse bind = node rest on all 178 joints (0.000 deg / 0.0000 m);
  the 90 deg pelvis frame in doc-frank.glb is cancelled by Spine1 (+89.99 deg) and is NOT the
  cause — the hood attire has no such frame and folded identically, and turning the bank alone
  fixed all three rigged Doc Frank models with the GLBs untouched.
- The **bosconovitch T3 animation bank** was baked facing **-Z** while declaring +Z
  (`lab/tools/t3_to_gltf.py` picks forward from the head-mesh centroid; Dr. B's hair mass sits
  behind his face). The runtime retarget copies the torso/arm/leg swings as world directions
  (they landed behind him) while hips and head keep his own facing -> the owl.
- Same flip on 4 more banks: eddy (King Tyrant, Kai), gunjack (Sam-ur-a1, Cyborg X, Raiden),
  yoshimitsu (Phantom, JIN), heihachi own-rig. `bank_facing.txt` = `tools/anim/t3_bank_facing.py`.
- Separate: Dr. B's slot-3 "neutral" is a 15-frame fall onto his back, and his bank's lying
  heights sit ~0.9 m below the floor -> looped as the idle he sank through the stage.

## Fix (game/js/t3anims.js, generic, data-derived)

1. `bankFacing()` at bank load: knee-bend cue from the bank's own frames; a bank whose knees bend
   behind its hips is turned 180 deg about Y and its Left/Right joints relabelled.
2. `standingIdle()`: a bank whose slot-3 clip drops > 1/4 hip height idles in its own standing
   guard (block hold, ping-pong) — Tekken's neutral stance is the standing guard. Only
   bosconovitch triggers.
3. Floor contact in `retargetT3Clips`: no joint below its standing-rest height.

## Files here

| File | What |
|---|---|
| 1_diagnosis_bank_vs_flipped_walk.png | Doc Frank walk frame: shipped bank (left pair, owl) vs bank turned 180 (right pair) |
| 2_before_after_all_turned_banks_walk.png | Old code vs new code, walk, all four affected banks (King Tyrant, Steve Fox on yoshimitsu, Cape Jones on gunjack, Doc Frank) |
| 3_live_fight_BEFORE.png | Live fight before: Doc Frank mostly invisible (under the floor), one frame bent backwards |
| 4_live_fight_AFTER.png | Live fight after: hunched toward Pantera, hands up, on the floor, every frame |
| 5_idle_source_check_intro_walk_block.png | Why the idle is his guard: round-start clip frames (sit, rise, arms-wide stretch, stand) vs walk / block / walk-back / hit |
| 6_regression_fights.png | King Tyrant vs Phantom, JIN vs Kai, Sam-ur-a1 vs Cyborg X, Pantera vs Demonio — 0 page errors |
| measure_before.json / measure_after.json | Facing yaw of hips, head, torso, knees, hands per clip (tools in the session scratch, see WORKLOG) |

All images were viewed by the agent before committing. Phantom and Sam-ur-a1 load with ZERO
skinned meshes (unrigged statics on main since 2026-10-18) — unrelated, queued for auto-rig.

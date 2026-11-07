# Xiaoyu-bank fighters stood in a T-pose guard: wrong bank skeleton (fixed 2026-11-07)

Owner (verbatim): "Arms at shoulders, forearms, and hands are all crushed and twisted some have extreme weight painting
issues all over and some have twisted necks or stretched faces evaluate and fix it all".

## What was wrong

Every fighter on the Xiaoyu bank (Sha, Sakura, Star, Mariposa, Silvertongue) played every bank clip with the arms
spread out like a T-pose and the knees locked, and every attack came out turned wrong. In poselab, the bank's own source
rig (left in each pair) shows a compact guard with the hands up; the three fighters (right) do not
(`before-sakura-star-mariposa-stance.png`).

## Why

The bank clips are LOCAL joint rotations of the rig they were baked onto (`lab/game/assets/t3_xiaoyu_t3real.glb`), at
that rig's own joint positions. `tools/anim/t3_bank_skeleton.py --check` confirms it: all 522 clip channels equal the
GLB's own animation channels (max error 8e-7).

On 2026-10-22, `skeleton.json` for this bank was rewritten as a neutral T-pose (`NEUTRAL_BIND`, kept here as
`skeleton-neutral-bind-RETIRED.json`). The reasoning was that the rig's joint positions were "a posed stance frame, not
a bind". But that stance frame is the very reference the clips were baked against. With the rest replaced, a
near-identity stance frame lands in a T-pose, which is exactly what the fighters showed.

The "130-170 deg off the decoded motion" that the rewrite meant to fix was measured against poselab's source preview.
At the time that preview dropped every clip's chest track: `jsonToClip` names it `Spine2`, and the source rig's node is
`Chest`. So the reference itself was broken.

Every other T3 bank's skeleton equals its source rig. The exceptions are the five that were deliberately turned 180°
with Left and Right relabelled (yoshimitsu, gunjack, eddy, heihachi, bosconovitch), which are consistent with their
rigs.

## Fix

- `game/assets/anim/t3/xiaoyu/skeleton.json` is regenerated from its source rig by the repo's own tool:
  `python3 tools/anim/t3_bank_skeleton.py --bank xiaoyu`.
  - `NEUTRAL_BIND_GLBS` is now empty and documented.
  - `--bank` regenerates one bank. Without it the tool rewrites every bank, which would undo the five offline turns.
- `game/poselab.html` source preview plays the chest track, so the reference is now right.

## Result, judged by eye (`after-six-clips.png`)

Each pair is the source rig and the fighter, front and side. Poselab's per-bone direction error is at most 2.3° on
every clip shown, where before it was 68-149° on the arms and 31-37° on the legs.

- **Star:** stance with hands up and knees bent, light (low sweep), heavy.
- **Mariposa:** stance and medium (kick).
- **Sakura:** block (both arms cover the face).

`source-rig-own-clips.png` shows the bank's source rig alone playing its own clips: a coherent guard, sweep and
acrobatic kick. This is the motion the fighters now reproduce.

## Same pass

Mariposa's Slot 1 default (`mariposa-butterfly-default`, built from T6-era parts) names its bones descriptively, for
example `arm right elbow`. `canonBoneName` did not know those names, so in a fight she bound no bank at all ("rig lacks
core humanoid bones"). The names are now mapped (`t3anims.js DESCRIPTIVE`), and she animates on the bank like the
others.

`test/arm-frame-normalization.test.mjs` used to pin Xiaoyu's "source-true" 29-33° elbow hinge error. That number was a
product of the T-pose skeleton. On the real rest her elbow is a pure hinge (0.0°), like 24 of the 26 banks, so the test
now asserts that instead.

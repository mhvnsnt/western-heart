# KAI and TOU in their own Eastern Mind bodies

Owner, 2026-11-10 (verbatim): "And u have kai and tou looking like Paul Phoenix and Eddy, they are souls and if u
research the eastern mind games and canon and images you will see what they really look like"

## What they really look like

The souls' designs are Osamu Sato's own Eastern Mind art, in the repo's teardown. Contact sheets:
`eastern-mind-R_KAI.png`, `eastern-mind-R_TOH.png`.

- `teardown/eastern-mind/incarnation-system/bitmaps/R_KAI/`, `R_TOH/`: the incarnation screens' head studies.
- `teardown/eastern-mind/prologue-ending/bitmaps/CHARA/CHARA_b006` (KAI) and `CHARA_b012` (TOU): full bodies.

**KAI 海 (the sea):**
- Head: a red egg crowned with long thin spikes that reach far out sideways.
- Face: a blue mask down the face with gold ornaments, and two disc eyes (teal ring, gold, dark pupil).
- Body: a blue neck, a chest of red spheres wider than the head (each with a gold spiral), and a red pelvis with two
  big bulbs.
- Limbs: thin blue arms and legs, red feet.

**TOU 闘 (battle):**
- Head: a teal head behind square purple glasses with red-iris eyes, a crown of five knobbed stalks, and an orange
  ring mouth between bulbous cheeks.
- Body: a neck of beads and a big ring for a torso.
- Limbs: long thin arms with knobbed elbows, huge five-fingered hands with bulb tips, short thin legs.

Before this, the game showed KAI as Eddy Gordo's T7 shell (`kai-body.glb`) and TOU as Paul Phoenix's real T7 parts
(`tou-body.glb`, carried from the roster lane in #1720). Neither is a soul.

## How they were made

`tools/souls/build_soul.py` + `tools/souls/specs.py`, run in Blender 4.0.2. Sato built these creatures from 3D
primitives in 1994; each soul here is built the same way:

- Every part (ellipsoids, tubes, cones, rings, discs, boxes) is measured off the full-body art. The pixel-to-metre scale
  is recorded per soul, with feet at 0.
- The pose is the game's T-pose, on the game skeleton (Mixamo joint names, Hips .. ToeBase).
- Each part is bound rigidly to one bone, the standard rig for segmented characters, so no part ever stretches.

`kai-tou-art-vs-built.jpg` shows the art beside the build, front view in the game's own renderer.

## Results

- **In motion** (`kai-tou-in-motion.jpg`; stance / walk / guard / hit / KO / 1 / 4 on their bound banks: KAI on
  Eddy, TOU on Paul): every part follows its bone and nothing tears.
- **Cards** (`kai-tou-cards.png`): KAI's old card (Eddy) against the new one, and the new TOU card beside its R_TOH
  head study.
- **Gates:**
  - `tools/auto_rig/validate.py` passes both: skinned, joints present, height 2.11 m (KAI, spikes included) and
    1.89 m (TOU).
  - The material gate passes both, 0 untextured.
  - Files: `kai-soul.glb` 1.5 MB, `tou-soul.glb` 1.3 MB.
- **Kept beside them:** `kai-body.glb` / `kai-body-cdn.glb` (the Eddy shell) and `tou-body.glb` / `tou-body-cdn.glb`
  (the Paul kit).

## Sato's surfaces (2026-11-10, later)

The art's surfaces are dithered and speckled, not flat. `tools/souls/textures.py` synthesises a tileable texture per
surface from Sato's own pixels:

- It collects that surface's pixels from the soul's full-body art (a region plus a colour rule that excludes the
  background).
- It keeps the lit ones: a render's shadows are not the surface's colour, and the first pass came out too dark without
  this.
- It scatters that palette with periodic low-frequency plus per-texel noise.

The textures are `tools/souls/tex/` (preview `sato-surface-textures.png`). `kai-body` / `tou-body` now load
`kai-soul-tex.glb` (1.8 MB) / `tou-soul-tex.glb` (1.6 MB). The flat-colour builds stay beside them.
`kai-tou-textured-vs-art.jpg` shows the art beside the textured build, front and close up. validate.py and the material
gate pass both, and the cards are re-captured.

## Not done here

- The other souls' bodies (RIN, BYOU, SHA, JIN, RETSU, ZEN) are still Tekken shells. Their own art is in the same
  teardown (R_RTOG, R_BYOU, R_SHA, R_JIN, R_LETS, R_ZEN).

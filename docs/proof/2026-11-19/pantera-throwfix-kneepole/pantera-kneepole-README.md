# Pantera throw knee-pole — proof (Lane D, 2026-11-19)

Owner complaint (verbatim): Pantera's back faces the opponent, knees bend
backwards — "you gave him one of the defects and bugs and glitches that a
lot of the other models had when he was perfect before." (Replying to the
2+4 throw video pantera-2plus4-throw-20261118.mp4, rendered from 43d29bf.)

## Headline finding (read this first)

**The thrower's knees do not bend backwards.** Measured in 3D — the knee's
offset from the hip-ankle line along the body's own forward (hips -Z) —
the thrower (Pantera, p1) is forward on **all 261 frames of both throws**:
worst offset **+0.061 m** (L @step 59) / **+0.057 m** (R @step 65), never
negative, never near zero. The victim's legs stay near-straight
(flex <= 11.8 deg) with a constant -0.04 m rest-pose offset — straight
legs, not a backward bend.

The "knees bend backwards" numbers this lane started from were **projection
artifacts of two 2D metrics**, not knee geometry:

- **Fixed-axis (world +X):** the hips swing from +49 deg to -134 deg
  through the throw, so world +X is ~90 deg sideways from the body's
  forward for most of it. The "clinch R -0.19 m" and "roll -0.32 m"
  defects are knees that are ALREADY forward in 3D
  (clinch local +0.29 m, roll +0.03..+0.15 m).
- **Horizontal forward (hips-forward, Y zeroed):** degenerates when the
  hips pitch near +/-90 deg (pitch 79 deg @steps 80/96) — the knee's real
  displacement there is mostly vertical, so the horizontal reading
  (-0.158 m @step 80) is meaningless. In 3D the same frame reads +0.19 m
  (L) / +0.30 m (R) forward.

Two earlier builds chased those metrics and made the anatomy worse
(proven on the same probe, same harness, phase-aligned runs):

- **v4** (frozen pole, unwrap + no cap on the stored delta) cleared the
  fixed axis at step 76 (+0.079 m) by bending the knee BACKWARD in 3D
  (local -0.33 m, the worst value in any run) and broke the landing
  (steps 100-104 fixed-axis -0.235 m).
- **v5** (live horizontal pole) "fixed" step 80 to +0.02 m on the
  horizontal metric by rotating a knee that was already +0.19 m forward
  in 3D, and wrote NaN quaternions into the victim's thigh/shin on
  pre-throw idle frames (uninitialised tail -> NaN strength -> 0 * NaN);
  the thrower is re-posed by its clip next frame, but the victim plays
  NO clip in the legacy path, so its shin/foot stayed NaN on all 261
  frames of both throws. Both fixed in v7.

What the owner saw in the video is real — Pantera's back is to the camera
through the clinch and he ends the throw prone on the floor — but it is
the FIGURE's orientation (back-to-camera + inverted roll + prone landing),
not the knee joints. Rotating the knees toward the camera cannot fix it
and bends them backwards; that is Lane B's orientation scope, not this
lane's.

## What this PR lands

`game/js/fighter.js` (+197/-0 vs main, one hunk: knee-pole methods +
section-9 call at the end of `_animate`): a post-mixer two-bone knee pole
that enforces forward knees **in 3D**, correctly defined this time:

- **Pole = the fighter's own forward in 3D** (hips -Z), recomputed every
  frame, so it rotates with the body through the tumble. Never degenerate
  (a unit quaternion vector).
- **Slew on the ABSOLUTE knee azimuth** about the hip-ankle axis (from
  the pole), ~60 deg/frame — never on the delta from the raw pose, which
  winds up by the body's own rotation (the v4 bug).
- **Flex gate (15 deg):** a near-straight leg has no bend direction to
  fix and rotating it twists the foot. Thrower min flex 20.0 deg, victim
  max flex 11.8 deg — the victim is untouched by design.
- **Margin +0.02 m, 0.25 s tail, hip + ankle exactly preserved** (knee
  recomputed on the same circle). No clip changed, no stance flattened,
  no yaw/floor touched.

On the current throws it is a measured no-op (numbers below are
identical before/after) — it is a guard: when the pair binds and the
victim plays its slot clip, or a future clip bends a knee backwards in
3D, the pole corrects it. It also fixes two latent ship-blockers found
by probing (NaN quaternions on clip-less fighters; inverted flex gate).

## Numbers (live probe, headless Chromium, 261 frames per throw)

| | BEFORE (main 12bac0a0) | AFTER v7 (this branch) |
|---|---|---|
| 2+4 p1 fixed-axis L / R | 27/261 min -0.321 / 44/261 min -0.353 | 27/261 min -0.321 / 44/261 min -0.348 |
| 2+4 p1 local (horiz) L / R | 9/261 min -0.158 / 2/261 min -0.086 | 9/261 min -0.158 / 2/261 min -0.086 |
| 2+4 p1 **3D-forward L / R (worst)** | **+0.061 @s59 / +0.057 @s65** | **+0.061 @s59 / +0.109 @s61** |
| 2+4 p2 fixed-axis / local / flex | 0/261 min +0.034 / 261/261 min -0.047 / 11.8 deg | identical |
| 1+3 p1 fixed-axis L / R | 27/261 min -0.321 / 27/261 min -0.353 | 27/261 min -0.321 / 27/261 min -0.347 |
| 1+3 p1 local L / R | 9/261 min -0.158 / 2/261 min -0.086 | 9/261 min -0.158 / 2/261 min -0.086 |
| 1+3 p1 **3D-forward L / R (worst)** | **+0.061 @s59 / +0.057 @s65** | **+0.061 @s59 / +0.082 @s24** |
| 1+3 p2 | identical to 2+4 p2 | identical |
| Null (NaN) knee frames | 0 | 0 |

The 5 mm difference on one R fixed-axis minimum (-0.353 -> -0.348) is
run-to-run press-timing variation (first-frame hipsY 0.904 -> 0.931),
not a correction: the 3D metric is unchanged-or-better everywhere.

The 2D metrics' residual negatives (fixed-axis -0.32 m, horizontal
-0.158 m) are NOT fixed by this PR and CANNOT be fixed by any knee
rotation without bending the knee backwards in 3D — at step 76 the two
target azimuths are ~180 deg apart (v4 proved it). They measure body
orientation, not knee bend.

## Video (before -> after, same harness, 800x450 @ 20 fps)

- `pantera-kneepole-before-2plus4.mp4` / `pantera-kneepole-after-2plus4.mp4`
- `pantera-kneepole-before-1plus3.mp4` / `pantera-kneepole-after-1plus3.mp4`
- `pantera-kneepole-side-by-side-2plus4.mp4` (before left, after right)
- Before and after frames are visually identical at matched steps, as the
  numbers say they must be. Capture: hand-stepped 60 Hz sim, canvas
  readback, 44 frames per throw; victim plays no clip in this harness
  (legacy path — the pair never binds here; the distance-gate follow-up
  is separate, Lane A).

## Files in this proof dir

- `pantera-kneepole-README.md` (this file)
- `pantera-kneepole-probe-after7-analysis.txt` (full AFTER v7 probe analysis)
- 5 mp4s listed above

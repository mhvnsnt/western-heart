# AKI Bake — CornerStone's No Mercy Rock Set (2026-10-21)

Workstream W3 of the gap-closure program (owner order 2026-10-21 08:19 CDT:
"AKI BAKE = FINISH IT (No Mercy Rock clips must actually play, not stay
data-only)").

## Verdict up front

**The bake does not ship. No rows were written into the king bank pack, and
no move was rewired to a baked clip — because the baked clips are not
playable, and this lane will not ship motion it has seen fail.** What ships
instead: the corrected converter (v3), real pose artifacts for all 11 Rock
clips, the full-pipeline bake tool with a calibrated quality gate that now
*proves* the blocker numerically, and the exact remaining step. The blocker
is the same one the teardown's own retarget doc named in its v1 scope
limits and never executed: **AKI FK → T3 IK targets**. Details and measurements below.

## What was found (converter state)

- `teardown/wwf-no-mercy/aki_to_tekken3_v2.py` is the proven converter:
  one clip (0x339A, 58f, on T3 King) exists as `aki_to_tekken3_v2.json`.
  Its verification was channel-space correlation only — it was never run
  through the game's pose builder (PoseBuildMatrices) or a bank.
- **v2 has a real bug**: the AKI rotation channel is an angle modulo 256
  units (256 = 360°) stored as s8. Joints rotating past ±127 wrap mid-clip
  (measured on system clip 0x2DDA: pelvis reads 105, 121, 121, **−103**,
  121, −103 — smooth only modulo 256, steps of +16/+32). v2 averaged and
  overlaid the wrapped series, injecting phantom ~224° swings.
- v2 also read the King stance pose from `~/workspace/game-reverse-engineering/…`;
  the same file lives in this repo (`teardown/tekken3/models/king95/king95_stance0_pose.json`).

## What was built

### 1. `teardown/wwf-no-mercy/aki_to_tekken3_v3.py` (extends v2)

Same joint map, same stance overlay, same root handling as v2, plus:
per-joint **s8 unwrap (period 256)** before the overlay, in-repo stance
path, and batch conversion of the whole Rock set. Output:
`teardown/wwf-no-mercy/aki-rock-v3/*.json` — 49-channel pose vectors in the
same schema as the proven `aki_to_tekken3_v2.json`.

| MK id | Move | File | Frames | Channel correlations (pelvis/chest/arm/head) |
|---|---|---|---|---|
| MK-1240 | Rock Bottom | anim_37FA | 49 | 0.971 / 0.993 / 0.909 / 0.886 |
| MK-2843 | People's Elbow (grounded) | anim_3E3D | 7 | 1.000 / 0.651 / 0.875 / 0.853 |
| MK-3473 | People's Elbow (running) | anim_40B3 | 16 | 0.996 / 0.952 / 0.841 / 0.913 |
| MK-4353 | Rock Taunt 01 | anim_4423 | 62 | 0.960 / 0.775 / 0.900 / 0.774 |
| MK-4347 | Rock Taunt 02 | anim_441D | 49 | 0.959 / 0.619 / 0.919 / 0.979 |
| MK-4354 | Rock Taunt 03 | anim_4424 | 55 | 0.955 / 0.534 / 0.906 / 0.940 |
| MK-4233 | Rock Entry Way taunt | anim_43AB | 34 | 0.984 / 0.994 / 0.831 / 0.783 |
| MK-4269 | Rock In The Ring taunt | anim_43CF | 35 | 1.000 / 0.824 / 0.967 / 0.990 |
| MK-1885 | Rock Spinebuster | anim_3A7F | 16 | 1.000 / 1.000 / 0.839 / 0.949 |
| MK-3120 | Rock Stomp | anim_3F52 | 16 | 1.000 / 0.908 / 0.940 / 0.641 |
| MK-3659 | Rock Spinning DDT | anim_416D | 28 | 0.963 / 0.984 / 0.875 / 0.838 |

Frame counts match the moveset file's own source notes exactly
(49 / 7 / 16 / 62 / 49 / 55 / 34 / 35 / 16 / — / 28).

### 2. `tools/anim/aki_row_bake.py` (the bank bake, gated)

Runs the game's own full pipeline per clip — v3 poses →
`usa_tables.pose_to_slot_rotations` (bit-exact PoseBuildMatrices port) →
pose_assemble FK over the King KMD → `T3Space.frame_globals` →
`t3_motion_bake.retarget` onto the king bank rig (`pantera_leoman.glb`) →
wh-anim-pack/1 rows (format mirrored from `t3_row_bake.py`) — and writes a
row into `game/assets/anim/t3/king_on_pantera_leoman/rows.pack.json` **only
if the clip passes both gates**, each calibrated on the pack's 176 real T3
rows:

1. **Step gate**: worst-bone mean per-frame rotation step ≤ 60.6°
   (= the worst value among the real rows; median real row: 16.5°).
2. **Height gate**: peak root height ≥ 0.70 m (real standing rows peak
   ~0.96 m). Added after own-eyes inspection caught smooth-but-collapsed
   poses passing gate 1 (below).

### 3. Measured gate results — all 11 FAIL

| Row | Frames | Worst bone | Mean step | Peak root height | Gate |
|---|---|---|---|---|---|
| mk1240 Rock Bottom | 49 | RightArm | 74.3°/f | 0.52 m | FAIL (step + height) |
| mk2843 People's Elbow | 7 | RightArm | 102.1°/f | 0.52 m | FAIL (step + height) |
| mk3473 Elbow (running) | 16 | LeftArm | 85.1°/f | 0.53 m | FAIL (step + height) |
| mk1885 Spinebuster | 16 | LeftArm | 85.1°/f | 0.51 m | FAIL (step + height) |
| mk3120 Stomp | 16 | LeftUpLeg | 109.0°/f | 0.53 m | FAIL (step + height) |
| mk3659 Spinning DDT | 28 | RightUpLeg | 93.5°/f | 0.54 m | FAIL (step + height) |
| mk4233 Entry taunt | 34 | RightUpLeg | 81.3°/f | 0.53 m | FAIL (step + height) |
| mk4353 Taunt 01 | 62 | LeftArm | 50.4°/f | **0.52 m** | FAIL (height) |
| mk4347 Taunt 02 | 49 | RightArm | 60.4°/f | **0.52 m** | FAIL (height) |
| mk4354 Taunt 03 | 55 | RightArm | 47.0°/f | **0.53 m** | FAIL (height) |
| mk4269 In-ring taunt | 35 | LeftArm | 32.1°/f | **0.52 m** | FAIL (height) |

Pack integrity after the gated `--write` run: **byte-identical** (all 176
real rows and every top-level field unchanged — the tool wrote nothing).

## Own-eyes evidence

FK stick renders on the bank skeleton (numpy, no Blender — the box had 5
other lanes' Blender jobs running; see harness note):

- Real row 281 (King's own Rock Bottom): coherent standing fighter in
  every frame — renderer validated.
- Baked mk4353 (Rock Taunt 01): frame 0 compact, frames 20/40 a crumpled
  skeleton collapsed at floor level, frame 61 a partial crouch. Not a
  taunt. Not playable.

Both renders: `docs/anim/aki-bake-2026-10-21/stick_mk4353.png`,
`docs/anim/aki-bake-2026-10-21/stick_281.png`.

## Why it fails — the mechanism (measured, not guessed)

T3 pose channels split in two kinds (pose.py `pose_build_matrices`,
verified against the USA EXE tables in-repo):

- **Euler joints** (slots 0,1,11,2,3,7,6,10,14,17): root, chest, hips,
  head, shoulder frames, hands, feet.
- **IK limbs** (slots 4,5,8,9,12,13,15,16): arm and leg segments are
  *overwritten* by the IK solver from the IK target channels (pose
  channels 3–14) + swivels (15–18).

The v2/v3 overlay drives Euler joints only and leaves IK targets at the
King stance constants. Result: the pelvis/chest rotate through the throw
while the IK solver keeps hands/feet pinned at stance targets — limbs
whip (step gate) and the pelvis is dragged to half height (height gate).
Slot-level diagnostic for MK-1240 through PoseBuildMatrices: mean slot
delta 53.5°/frame with v2's wrapped input, 25.8°/frame after the v3
unwrap, vs **2.4°/frame** for a real T3 King stream.

## The remaining step (named, scoped)

**AKI FK → T3 IK targets**, exactly the YANM v2 pattern
(`teardown/wwe-wrestlemania-xix/docs/YANM-TEKKEN3-RETARGET.md`: FK the
source chains → wrist/ankle trajectories → overlay onto the stance IK
channels with a measured scale; torso/head stay on Euler). It needs the
AKI skeleton FK — how a PivotRotation frame (pivot XZ + s8 rotation per
joint, plus the MovementXYZ joints) composes into joint world positions.
That composition lives in the No Mercy ROM's animation player code; the
ROM data alone does not reveal it (same status as Toki2 semantics,
`TOKI2-SEMANTICS.md`). Route: Ghidra on the player (per the no-hand-tooling
law — full RE systems, not guesswork scripts). Once wrist/ankle
trajectories exist, `aki_row_bake.py` gains an IK-feed step and the same
gate decides what ships; the moveset wiring (`t3_row: "mk####"` +
`t3_source: "king"` on each mk move, the pattern every other fighter's
rows use) is a five-minute follow-up **after** a clip passes — wiring it
now would point moves at rows that do not exist.

Until then the mk moves keep their current behavior: they resolve through
CornerStone's King bank (his stance + King's real Rock Bottom row 281
etc.) — playable today, just not yet the No Mercy motion.

## Moveset file state (this PR)

`game/assets/movesets/ryuji-rock.json` gains an additive `aki_bake` record
on each No Mercy move (poses path, gate result) and a
`cornerstone_build.aki_bake_v3` summary. No move data changed; no
`t3_row` was added (no baked rows exist to point at).

## Harness proof — PENDING (two blockers)

1. The clips themselves (above) — no honest frame of CornerStone
   performing a No Mercy Rock move can exist until the FK→IK step lands.
2. RAM: at bake time the box ran 5 other lanes' Blender jobs with
   ~1.9 GB available; per the RAM law this lane started no Blender job.

## Def Jam transfer notes (AKI lineage)

Def Jam: Fight for NY is AKI-lineage (teardown-verified on-disc:
`AKI_CFG.XML` with `pause_use_aki`, `MOTION/MAIN_ALL.DAT` opening with the
**WAZA** magic, 676 named moves; motion bank `MOTION/WRES_ALL.VIV`,
sets `wres001`–`wres141` — `teardown/def-jam-fight-for-ny/ANIMATION-FINDINGS.md`).
What transfers from this lane's work:

- **The diagnostic method transfers**: any Def Jam clip conversion should
  be gated the same way (smoothness + pose sanity vs the target bank's
  real-row distribution) before anything is called playable.
- **The s8-wrap check transfers conditionally**: IF WRES_ALL motion
  decodes to the same PivotRotation channel layout (pivot XZ + s8
  rotation), the v3 unwrap applies verbatim. That layout is **not yet
  verified** for the PS2 .VIV bank — do not assume it.
- **The FK→IK requirement transfers**: Def Jam clips fed into WH's T3
  banks will hit the same IK wall; the AKI FK work, once done for No
  Mercy, is the first thing to test against the WRES sets.

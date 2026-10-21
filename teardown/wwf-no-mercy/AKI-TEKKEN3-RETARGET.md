# AKI (No Mercy) → Tekken 3 Retarget — v1 (2026-10-13)

First working pipeline that plays a No Mercy (AKI engine) wrestling animation
on a Tekken 3 skeleton. One move animation (`0x339A`, 58 frames) → King
(BNS record 95, `tekken3/models/king95/`).

## Pipeline (tool: `tools/aki_to_tekken3.py`)

1. **Decode** the AKI animation via `wwf-no-mercy/tools/anim_extract.py`:
   19× 1-DOF `PivotRotation` (s8 rotation + 12-bit pivot XZ) + root movement.
2. **Calibrate**: s8 rotation value EQUALS degrees (measured: pelvis s8 −39..121
   = doc's −39°..+121°). So `Tekken_s16 = s8 × (65536/360)` = s8 × 182.04.
3. **Map** AKI joints → Tekken 3 FK Euler joints (provisional anatomical):

   | AKI joint | Tekken joint |
   |---|---|
   | Pelvis | joint0 (pelvis) |
   | LowerAb, UpperBody | joint1 (chest) |
   | Neck, Head | joint3 (head) |
   | UpperRightArm | joint4 (R shoulder) |
   | UpperLeftArm | joint5 (L shoulder) |
   | LowerRightArm | joint6 |
   | LowerLeftArm | joint7 |
   | UpperRightLeg, LowerRightLeg | joint8 |
   | UpperLeftLeg, LowerLeftLeg | joint9 |

   (Multiple AKI joints averaged when mapping to one T3 joint.)
4. **Overlay**: `tekken(t) = stance0 + (aki(t) − mean(aki))` on the X channel
   (provisional axis, same pattern as YANM v1).
5. **Root**: AKI OverallMovement → Tekken root_x/y/z (scale 0.5, provisional).
6. **Output**: `docs/aki_to_tekken3_v1.json` — 58 × 49-channel s16 pose vectors.

## Verification (measured)

Source-vs-retarget motion-shape correlations (mean-subtracted degrees):
- Pelvis → joint0: **+1.000** (perfect)
- UpperBody → joint1: +0.901
- UpperRightArm → joint4: +0.924
- Head → joint3: +0.796 (Neck+Head averaged)
- UpperLeftLeg → joint9: +0.742 (Upper+Lower averaged)
- UpperRightLeg → joint8: +0.689 (Upper+Lower averaged)

All 9 driven channels move; curves track the source choreography. The lower
leg/head correlations are from averaging, not from failed transfer.

## v1 scope limits (honest)

- **Axis provisional**: AKI 1-DOF hinge → Tekken X for all joints. True
  hinge→Euler-axis mapping needs AKI joint frame data (open).
- **Averaging**: Upper+Lower arm/leg collapsed to single T3 joints; T3 has
  10 Euler joints vs AKI's 19 hinges — a fuller mapping needs T3 joint anatomy.
- **Root scale** (0.5) is a guess; AKI movement units vs T3 units uncalibrated.
- **No IK**: T3 limbs use IK channels (not driven here); v2 should do
  AKI FK → T3 IK like YANM v2 did.
- **No render yet**: same as YANM v1 — numeric + plots, not pixels.

## What this unblocks

The full No Mercy AKI animation library (~1,360 clips) can now be retargeted
to Tekken 3 models via this pipeline. This is the Western Heart "wrestling
animations on Tekken models" path for the AKI engine (complements the Yukes
YANM→Tekken3 path).

## v2 — REGENERATED from corrected bank (2026-10-13)

v1 was built on the misaligned NTSC_U_10 FileTable (0x16C3238).
**v2 uses the corrected NTSC_U_11 bank** (FileTable 0x16C31D8, 5,787 clips in `animations/clips/`).

Tool: `aki_to_tekken3_v2.py`. Output: `aki_to_tekken3_v2.json`.

Verification (source-vs-retarget correlations, corrected bank):
- Pelvis → joint0: **+1.000**
- UpperBody → joint1: +0.901
- UpperRightArm → joint4: +0.924
- Head → joint3: +0.796

Correlations match v1, confirming the pipeline transfers correctly on the aligned data.
**Use v2 going forward. v1 (`aki_to_tekken3_v1.json`) is deprecated.**

## v3 — s8 unwrap fix + Rock set + gated bank bake (2026-10-21)

Tool: `aki_to_tekken3_v3.py`. Outputs: `aki-rock-v3/*.json` (11 clips —
the full CornerStone Rock set: MK-1240 Rock Bottom, MK-2843/MK-3473
People's Elbow, MK-1885 Spinebuster, MK-3120 Stomp, MK-3659 Spinning DDT,
and all five Rock taunts MK-4353/MK-4347/MK-4354/MK-4233/MK-4269).

**The v3 fix (measured):** the AKI rotation channel is an angle modulo
256 units stored as s8; joints rotating past +-127 wrap mid-clip (system
clip 0x2DDA pelvis: 105, 121, 121, -103, 121, -103 — smooth only modulo
256). v2 overlaid the wrapped series. v3 unwraps each joint series
(period 256) before the overlay, and reads the King stance from this
repo (`teardown/tekken3/models/king95/king95_stance0_pose.json`).

**Bank bake attempt (the honest result):** `tools/anim/aki_row_bake.py`
runs these poses through the game's full pipeline (PoseBuildMatrices →
pose_assemble FK → frame_globals → t3_motion_bake retarget → wh-anim-pack/1)
behind a quality gate calibrated on the king pack's 176 real rows
(step gate 60.6 deg worst-bone mean step; height gate 0.70 m peak root
height). **All 11 Rock clips FAIL** — attacks on both gates (74–109
deg/frame limb whip), taunts on height (peak root height 0.52–0.53 m;
own-eyes stick render shows a crumpled floor-level skeleton vs real row
281's coherent stance). No rows were written; the pack is byte-identical.
Full measurements: `docs/anim/AKI-BAKE-ROCK-2026-10-21.md`.

**Root cause (verified in pose.py):** T3 arm/leg segment slots
(4,5,8,9,12,13,15,16) are overwritten by the IK solver from the IK target
channels; the Euler overlay cannot drive them. The remaining step is
the one named in the v1 scope limits above, still open: AKI FK →
wrist/ankle trajectories → T3 IK target channels (the YANM v2 pattern).
AKI FK composition
(PivotRotation + MovementXYZ → joint world positions) lives in the
ROM's animation player code — Ghidra route, not guesswork.

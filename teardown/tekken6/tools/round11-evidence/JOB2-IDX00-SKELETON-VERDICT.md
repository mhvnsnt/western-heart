# Tekken 6 PSP — ROUND 11 JOB 2 (idx00 SKELETON DISCREPANCY): VERDICT

Date: 2026-10-22, round 11. Scripts: `round11-evidence/j2_compose.py`,
`round11-evidence/j2_followup.py`, `round11-evidence/j2_overlay.py`,
tool `tools/r11_skeleton_fix.py`, numbers in
`round11-evidence/r11_skeleton_correction.json`, overlay VIEWED:
`round11-evidence/r11_idx00_skeleton_overlay.png`.

## The discrepancy, restated

Round 9's spot values for idx00 (JOB2-BONE-ROLES.md): ATAMA
(0, 1653.8, 0), TE_R (−800.8, 1560, 0), ASHI_R (−104, 135.2, 0).
Round 10's batch (`r10_batch.py` `bone_world()`): ATAMA y 1708.9,
TE_R −969.6. Round 10 flagged this + finger chains extending past
the slot-10 mesh arm span, unresolved.

## Verdict (proven from the BONE bytes + the package's own mesh)

**The two rounds used different composition conventions. Round 9's
spot values are the correct bind pose; round 10's `bone_world()`
composition is wrong. The shipped GLB node data (both rounds) is
byte-faithful local TRS — but a standard glTF world walk of those
GLBs compounds the per-bone scales and reproduces the WRONG
(round-10) positions, so corrected skeleton GLBs are shipped this
round (below).**

The two conventions:

- **TR (round 9 spot check)**: world joint position = parent world
  rotation chain applied to local translations, `W = Π (T·R)`;
  the BONE scale array does NOT enter joint positions.
- **TRS (round 10 `bone_world()`)**: local matrix = T·R·S composed
  down the chain (standard glTF node semantics), so every
  ancestor's scale multiplies every descendant's translation.

Recomposing idx00's BONE slot-1 bytes both ways reproduces BOTH
published number sets EXACTLY (to 0.1): TR → ATAMA 1653.8 /
TE_R −800.8 / ASHI_R y 135.2 / KUBI 1570.5 (= round 9 verbatim);
TRS → ATAMA 1708.9 / TE_R −969.6 (= round 10 verbatim). No byte
was misread by either round; the difference is purely the scale
treatment.

## Why TR is correct (ground truth = idx00's own decoded meshes)

| Check | TR | TRS | Ground truth |
|---|---|---|---|
| ASHI_R y | **135.2** (ankle above floor) | **−9.7 (below floor)** | slot-10 mesh min y = −0.7 |
| ATAMA y | **1653.8** (at head-mesh base) | 1708.9 (51 units inside the skull volume) | slot-0 head mesh y ∈ [1657.8, 1906.5] |
| TE_R x | **−800.8** (hand joint inside hand volume) | −969.6 (≈ the fingertip surface itself) | slot-10 mesh x span ±981.2 |
| Finger-tip joints max \|x\| | 1029.5 (tip joints, ~5% past the low-poly mesh's last verts) | 1278.9 (30% past the mesh — the round-10 "finger overshoot") | mesh ±981.2 |

The overlay render (VIEWED, `r11_idx00_skeleton_overlay.png`)
shows it directly: the TRS walk stretches both arms well past
the mesh point cloud and drops both feet below the floor line;
the TR walk sits inside the mesh volume everywhere.

## Why idx00 was the loud case (the BONE scale rows differ per package)

- **idx00: ALL 110 bones carry scale (1.04, 1.04, 1.04)** — equal
  to the BONE header f32 (1.04). Compounding 1.04 over a 5-deep
  arm chain inflates TE_R by 1.04^5 ≈ 1.22× — exactly the
  −800.8 → −969.6 jump.
- idx01/05/08 "landed on round numbers" in round 10 because their
  non-unit scales sit ONLY on hand/face subtrees (idx01: 0.95 on
  TE + all finger bones; idx05: 0.7 on TE + fingers, 0.93 on face;
  idx08: 1.03 on face only) — no key joint (ATAMA/TE/ASHI) has a
  non-unit-scale ANCESTOR, so TR and TRS agree on those joints.
  Their subtrees still diverge (max |TR−TRS| 17.2 / 66.6 / 2.6).
- The other global-scale packages diverge much worse under TRS:
  max joint error vs TR — idx04 127.9, idx12 49.4, idx13 116.4,
  idx16 319.1, idx17 381.9, **idx20 597.3**, idx21 302.3
  (scale rows: idx13 uniform 1.02; idx16 {1.04, 1.144}; idx17
  {1.0441, 1.06}; idx20 {0.9527, 1.095}; idx12 {0.9405, 0.99};
  idx04 {0.98, 1.0}; full table in the correction JSON).

So the BONE scale array is a per-bone LOCAL scale (character-size
/ segment scale baked per bone — note values like 1.144 = 1.04²
and 0.9405 ≈ 0.99²·… on idx12/16), which the engine evidently
applies to the bone's own skinning matrix, NOT a quantity that
propagates into descendant joint positions. There is no second
skeleton variant and no dropped/mis-parented finger chain in
idx00's BONE — the finger overshoot was purely the compounding.

## Corrected deliverables

`tools/r11_skeleton_fix.py` ships, for all 12 packages × (slot-1
body + slot-12 head) = 24 GLBs:
`models/idx{nn}_skeleton_r11.glb` + `models/idx{nn}_bone_slot12_r11.glb`.
Each node keeps its BONE rotation and its own BONE scale value;
its translation is divided by the accumulated ancestor scale
product (all BONE scales are uniform per bone, so this is exact),
which makes a standard glTF world walk reproduce the proven TR
bind pose: **max error vs the TR composition ≤ 0.02 units on all
24 skeletons** (vs up to 597.3 for the r10-shipped GLBs).
The r9/r10 GLBs are NOT deleted (additions-only); consumers
should prefer the r11 files for bind-pose/skeleton work.

## Convention statement (for all future rounds)

- Bind joint world positions: compose `T·R` only (R = Rz·Ry·Rx).
- BONE scales: per-bone local data, carried on the node, never
  compounded into descendant translations.
- The shipped r9/r10 skeleton GLBs encode byte-faithful local
  TRS; their world walks are the TRS numbers, NOT the bind pose.

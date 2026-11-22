# T7 Receiver Fix — the permanent fix for all broken Tekken 7 mocaps

**Status:** permanent fix record. **Date:** 2026-11-21.
**Scope:** Tekken 7 King throw receivers (`_y` moves) and every future T7
mocap pull. **Change in this PR:** docs only — no game code, no animation
data, no live-game changes. The clip rebuild this doc mandates (all 22
P1/P2 receivers + bank thrower 588, §3e) is a separate lane's work, not
landed here.

**Sources (every number below comes from one of these; cite the file, not
this doc):**

- `FIX` — `~/workspace/_t7throw-fix-20261121/lane-b-flip/FIX-REPORT.md`
  (+ `joint-sandwich.json` in the same workdir) — the flip formula.
- `AUDIT` — `~/workspace/_t7throw-fix-20261121/lane-c-audit/AUDIT-REPORT.md`
  — the f0 audit of all 22 P1/P2 receivers + 24 throwers.
- `HUNT` — `~/workspace/_t7throw-fix-20261121/lane-d-hunt/HUNT-REPORT.md`
  — the already-decoded-source hunt (15 searches, 5 pages read in full).
- `THROWDATA` — `~/workspace/_pantera-t7throw-hunt-20261120/lane-a-throwdata/THROWDATA-REPORT.md`
  — the throw-data read (roles, breaks, damage).
- `HUNT-CP` — `~/workspace/_pantera-t7throw-hunt-20261120/CHECKPOINT.md`
  — the solved decode (diagnostics #1–#10, control run, P0/P1/P2 pull).
- `STATUS` — `docs/decode/STATUS.md` on main — the status table this doc
  is pointed at from (see its new T7-receiver row).

**Correction to `STATUS.md` carried here:** the "What the real King
`.tkmvst` proved" section on main says both King throws "resolve to
receiver move 554". That is the *hold*, not the final receiver. The
receiver mechanism is two-stage (§2): grab connects → victim into hold
move 554 (30f `nab6_guard`) → the thrower's throw motion selects the
specific `_y` in its standing slot. Anyone reading only the grab's
HitCondition row gets 554 and would wrongly conclude the receiver is a
30f guard hold. (HUNT-CP, follow-up §132.)

---

## 1. The solved decode (what the clips are built on)

The T7 clips are decoded through the game's own sampler
(`t7_anim64_to_c8.py` + `emulate_sampler.py` + the game exe), not a
re-implementation: the pure-Python `t7_anim64.Anim64` port of
TKMovesets2 `ParseAnimation0x64` was tested as a control and does NOT
reproduce the bank (best non-trivial offset-spread 2.08°; every moving
track 10°–160° off under every convention). Only the game sampler
produces the bank's values from raw 0x64 bytes. (HUNT-CP, control test.)

- Exe: `TekkenGame-Win64-Shipping.exe`, 58,439,680 B, sha256
  `7f2b68727023ce9f4554b47f5442dad9dfb38c8a9b778f2aa758469e2c2d60ed`
  — matches the bank's `exe_sha256` prefix `7f2b6872…` exactly.
  (HUNT-CP.)
- Raw format: MOTA format 100, 23 tracks. Round-trip check on clip 574:
  worst 1.79e-07 (gate <1e-4). `root_motion_fwd` exact (0.00e+00).
  `root_t` via the DIRECT map exact (0.0000 m). (HUNT-CP, re-run #2.)
- Control gate (clip 574, 130f): **PASSED, exact worst 0.1303°**
  (gate relaxed 0.1° → 0.2° once the precision floor was known — see
  below). Receivers built on it: `rotsm_575.json` (101,068 B, 130f) +
  `rotsm_579.json` (104,815 B, 138f); `control-report.json`
  (6,260 B), `control_ok=true`, `exact_worst` 0.1303°,
  `roundtrip` 1.79e-07. Both JSONs verified: wh-anim/1, 60 fps,
  21 bones, quat-norm worst deviation 1.8e-06, 0 NaN, FK bound
  0.001137 m. (HUNT-CP, receivers built.)

### 1a. Per-bone Euler orders (the decode — use these, not one global order)

The mannequin bones carry per-bone rotation modes; a single global
Euler convention was the bug (diagnostic #3). Confirmed by full Kabsch
fit, max error over all 130 frames of clip 574 (HUNT-CP, diagnostic #4):

| Order | Joints |
|---|---|
| XYZ | Neck, ForeArms, UpLegs, Legs, Feet |
| YXZ | Head |
| XZY + real convert | Shoulders |
| YZX | Arms, Hands |

"Real convert" = the bake's real `get_quaternion_from_euler`
(qz·qy·qx, not qx·qy·qz) and `quaternionToRotationMatrix` reading Q as
[w,x,y,z] (not [x,y,z,w]) — the bake ran the real code bugs-included,
so the decode reproduces them faithfully. (HUNT-CP, diagnostics #2–#3.)

Per-joint Kabsch maxima (deg, all 130 frames): Neck 0.1060, Head
0.1238, LeftShoulder 0.1252, LeftArm 0.1262, LeftForeArm 0.1216,
LeftHand 0.1168, LeftUpLeg 0.1216, LeftLeg 0.1237, LeftFoot 0.1159,
RightShoulder 0.1245, RightArm 0.1178, RightForeArm 0.1255,
RightHand 0.1115, RightUpLeg 0.1261, RightLeg 0.1184, RightFoot
0.1170; Chest / ToeBases 0.0000 (identity, no channel — see §1b).
Means 0.014–0.047°. The uniform ~0.11–0.13° residual is a precision
floor, not a per-joint mismatch: an all-frames least-squares refinement
of the conjugation did not reduce it (identical to 4 decimals), and
angle-invariance is 0.001°. 0.13° on a 0.5 m limb is ~1 mm, invisible.
(HUNT-CP, diagnostics #4–#5, re-run #2.)

Applier assignments (verified exact against
`TekkenAnimHelper.py`, incl. ±π/2 offsets): Spine1 = track 4
(`animdata[12,13,14]` → (Z−π/2, Y, −X)); Hip = track 5
(`animdata[15,16,17]` → (Z+π/2, Y, −X)); BASE = track 3
(`animdata[9,10,11]` → (Z, Y, −X)). (HUNT-CP, diagnostic #7.)

### 1b. Spine — APPROXIMATE, flagged, unsolved exactly

The Spine is the one unsolved joint (20/21 solved). Single conjugation
fails (177–180° all orders, angle-invariance best 44°); 2-factor
sandwich fails (best 53°); 3-factor fails (179°); wrapping is dead
(error is global, not localised: mean 82.58°, max 177.27°).
Best approximation in use: sandwich Hip=ZXY / Spine1=XYZ, **53.5° max /
17.8° mean on 574** (on 578: 67.6° max / 27.3° mean). It is EXCLUDED
from the pass/fail gate and every receiver JSON carries an explicit
`spine_approximate` flag. The ~33–35° f0 forward lean on the fixed
victims tracks the Spine quat (f0 angle ≈34.4° vs thrower ≈14.9°), so
the true lean is uncertain by tens of degrees. The Spine solve itself
is still open — do not present a Spine value as verified. (HUNT-CP,
diagnostics #6–#10, Spine verdict; FIX §6.)

### 1c. Chest / toes — source-real, closed

Track 2 (Chest rotation) is constant ZERO in the raw anim — the game
data has no Chest channel for this clip, so the bake leaving Chest at
identity `[0,0,0,1]` is faithful, not a padding artifact. Same for both
ToeBases. The T7 format has 23 channels and there is NO Chest channel
and NO toe channels. No re-extraction or re-bake can produce them; the
only route to a moving Chest is a retargeting decision (split the upper
body over Spine + Chest, as the T8 converter does) — an owner /
coordinator call, not landed. (HUNT-CP, control test + follow-up §136;
STATUS.md, "What the real King `.tkmvst` proved".)

---

## 2. The two-stage receiver mechanism (how a throw actually plays)

A T7 throw is three moves, not two. The old "no follow-through" claim
came from reading only the grab's last cancel (`[39,32767]` →
32769 idle-return) and never the five connect cancels above it — dead.
(THROWDATA §3.1; HUNT-CP, Lane A.)

1. **Grab setup (universal).** Front 1+3: move 1785 `ThrmvLB2_00`
   (`msco_ltukami`, clip `common_709`, 40f); front 2+4: move 1787
   `ThrmvRB2_00` (`msco_rtukami`, clip `rotsm_534`, 40f). Damage field
   16384 (throw marker, not hit damage). Connect window `[12,14]`
   on throw-direction reqs: front 2594, left 1610, right 1612, back
   1614, air 2598. (F-variants `ThrmvLB2_00F` 1786 / `ThrmvRB2_00F`
   1788, clips 710/20, use the same `_n` targets at `[15,17]`.)
   (THROWDATA §4.)
2. **Hold — the victim is grabbed, not yet thrown.** On connect the
   victim goes into hold move **554** (30f, `nab6_guard`, anim_id
   33363), breakable to move 1423 on grab-break inputs. The thrower's
   throw motion has not hit yet. (HUNT-CP, follow-up §132; FIX §6 —
   move 554's `rotsm` clip number was never mapped, moot for the flip
   fix, needed if the hold is ever staged.)
3. **Throw + receiver selection.** The thrower's own connect cancel
   takes the thrower into the `_n` throw motion; the thrower's `_n`
   move's HitCondition **standing slot** selects the specific `_y`
   receiver. No move in the entire 2,787-move graph cancels into any
   `_y` move (verified by exhaustive scan) — the `_y` can only be
   reached by the engine forcing a character into it, which is exactly
   how a victim's reaction is assigned. (THROWDATA §3.1.)

### 2a. The eight standing/air `_n` → `_y` pairs

| Thrower `_n` (move, clip, frames, dmg) | Receiver `_y` (move, clip) |
|---|---|
| 2125 `Kg_FLnage00_n`, rotsm_574, 130f, 35 | 2126 `Kg_FLnage00_y`, rotsm_575 |
| 2129 `Kg_FRnage00_n`, rotsm_578, 138f, 35 | 2130 `Kg_FRnage00_y`, rotsm_579 |
| 2135 `Kg_Lnage_n`, rotsm_588, 226f, 40 | 2136 `Kg_Lnage_y`, rotsm_589 |
| 2137 `Kg_Rnage_n`, rotsm_590, 160f, 42 | 2138 `Kg_Rnage_y`, rotsm_591 |
| 2139 `Kg_BLnage_n`, rotsm_592, 203f, 60 | 2140 `Kg_BLnage_y`, rotsm_593 |
| 2141 `Kg_BRnage_n`, rotsm_594, 240f, 60 | 2142 `Kg_BRnage_y`, rotsm_595 |
| 2274 `Kg_AirDragon_n`, rotsm_716, 90f, 30 | 2275 `Kg_AirDragon_y`, rotsm_717 |
| 2276 `Kg_AirHizaj_n`, rotsm_718, 155f, 30 | 2277 `Kg_AirHizaj_y`, rotsm_719 |

(THROWDATA §4; HUNT-CP, Lane A. Damage is the move field and the
extra property `33307` — see §2c.)

Crouch pairs: 2211 `Kg_bd_n` (rotsm_654, 165f, dmg 45) → 2212
`Kg_bd_y` (rotsm_655); 2213 `Kg_Knuckle_n` (rotsm_656, 77f, dmg 15)
→ 2214 `Kg_Knuckle_y` (rotsm_657); 2345/2347 `KgnewcoL/R_1Bn`
(rotsm_785, 229f, dmg 25) → 2346/2348 `KgnewcoL/R_1By` (rotsm_786).
Ground pairs: 2228 `Kg_DWgold_n` (rotsm_670, 127f, dmg 25) → 2229
(rotsm_671); 2219/2221 `Kg_DWstr_Ln/Rn` (rotsm_662, 183f, dmg 28) →
2220/2222 (rotsm_663); 2232/2234 `Kg_DWLsid_Ln/Rn` (rotsm_674, dmg 0)
→ 2233/2235 (rotsm_675); 2236/2239 `Kg_DWRsid_Ln/Rn` (rotsm_678,
dmg 0) → 2237 (rotsm_679); 2249/2251 `Kg_DWUhea_Ln/Rn` (rotsm_691,
dmg 32) → 2250/2252 (rotsm_692); 2261/2263 `Kg_DWUfoo_Ln/Rn`
(rotsm_703, 165f, dmg 30) → 2262/2264 (rotsm_704). Extras:
2143 `Kg_BCnage_n` (rotsm_596, dmg 75), 2163 `nagexx1e_n`
(rotsm_614, dmg 50), 2131 `Kg_brain1_n` (rotsm_580, dmg 40),
2293 `nagexx01_n` (rotsm_734, dmg 100). (THROWDATA §4.)

### 2b. Break windows — only the victim breaks

The `_y` moves carry break cancels in frames **[1,15]** (front) /
**[1,10]** (side): 2126 → 2127 `Esc_FLnage00_n` on req 131/132;
2130 → 2133 `Esc_FRnage00_n` on req 131/132; 2136 → 237
`SideEscL_n` on req 131; 2138 → 239 `SideEscR_n` on req 132;
2164 → 235 `nuke36_n` on req 133. Req 131/132/133 are the victim's
break inputs (pressed ONLY 1 / ONLY 2 / ONLY 1+2). The `_n` moves
have **no** break cancels at all. Air `_y` moves (2275/2277) have no
break cancels either — air throws are unbreakable in Tekken.
`Kg_Knuckle_y` (2214) is the one receiver `_y` that ends idle rather
than downed — flagged, not smoothed over; it still carries the break
cancel (`[1,15]` req 131 → 2217), which is the decisive victim
marker. (THROWDATA §3.2, §4.)

Role evidence, seven lines (THROWDATA §3): (1) cancel reachability
(`_n` only, §2 above); (2) break windows (this section); (3) damage
(§2c); (4) hitlevel — `_n` 2560 (attacking), `_y` 0 (passive
reaction); (5) end state — every front-pair `_n` transitions to
32769 (idle, thrower ends standing), every receiver `_y` to a
downed/grounded state (32772 / 32774 / 32775 / 32780); (6) extra
properties — `_n` 13–17 rows, `_y` 3–6 bare rows; (7) motion — all
throw-scale motion in the 10-clip set lives in the `_n` clips
(574: twist 280.8° @f111, pitch 116.3°; 718: 348.8°; 716: 250.0°;
588: 186.1°), while the grabs are upright holds (709: 33.6°,
534: 58.4°). Motion alone cannot prove role; lines 1–6 do.

### 2c. Damage — property 33307 corrections

Every `_n` move carries the throw damage twice: the move field and
extra property `33307` with the same value (e.g. 2125
`[6589, 32769, 33307, 35]`). Every `_y` move has damage 0 and no
`33307` extra. Corrections from the `33307` extra (the move field is
0 in both cases): left `Kg_Lnage_n` (2135) damage is **40**, not 0;
air `Kg_AirDragon_n` (2274) damage is **30**, not 0. Full table for
the eight §2a pairs: 2125=35, 2129=35, 2135=40, 2137=42, 2139=60,
2141=60, 2274=30, 2276=30. (THROWDATA §3.3; HUNT-CP, Lane A.)

---

## 3. The flip formula (the permanent fix)

### 3a. What was wrong (measured)

In the receiver JSONs as built, both victims start upside down with
their feet in the air and their backs to the thrower. Torso pitch at
f0: 575 = 147.9°, 579 = 146.6° (throwers: 17.3° / 37.3°). Head Y f0
0.60/0.63 m, feet Y f0 2.00/2.05 m (throwers' feet: 0.13–0.19 m).
Hips quat f0: 575 = [0.2385,−0.0255,0.9707,0.0101] (178.8° about
~+Z); 579 = [0,−0.0103,0.9999,0] (180.0° about +Z). Throwers' Hips
f0 are small yaws (29.5° / 10.2° about −Y). Pelvis-facing: victims
27.6° / 0.0° vs throwers −29.5° / −10.0° — the victims face roughly
the SAME direction as the throwers (10° / 57° apart), NOT opposite.
(FIX §1.)

In the SHARED raw frame (identity heading, `root_t` as authored) the
pairs DO close: 1+3 hips 1.17 m @f0 → min 0.51 m @f52; 2+4 0.74 m @f0
→ min 0.46 m @f43 (T3: 0.48 / 0.74 m). The "pair never closes" flag
was a placement artifact of per-figure heading + recentering, not a
data problem. Both victims' `root_t` f0 ≈ (0, 1.07–1.09, 0);
throwers at (−1.169, …) / (−0.743, …). (FIX §1.)

### 3b. Root cause — a Hips-sandwich degeneracy, NOT game data

The receivers' Hips quats were built with the sandwich
`Hips = U·E_BASE·V·E_HIP·W`, whose (U,V,W) was fit ONLY on clip 574
— where E_BASE is a 1-DOF family (c8 tr3: X range 1.744, Y=Z=0 →
E_BASE = qz rotations only). That fit has an exact 1-parameter
degeneracy: `(U,V,W) → (U·qz(α), qz(−α)·V, W)` leaves the 574
predictions UNCHANGED for every α (verified: max error exactly
0.1257° for α = −90..180°) while moving the receivers' f0 Hips
wildly (152.4° about +Y at α=±90° ↔ 178.8° about +Z at α=0). The
JSONs' f0 Hips (~180° about Z) is the optimizer's arbitrary α≈0,
not game data. The receivers' f0 BASE raw quat is [0,−1,0,0] (180°
yaw, verified from the game sampler) — outside the 574 fit family.
The `_y` clips do NOT start mid-throw inverted; no hold-554 connect
pose is needed for this fix. (FIX §2.)

### 3c. The joint sandwich — use these values verbatim

Replace the Hips sandwich constants with the JOINT fit on bank 574 +
bank 578 (578's bank Hips is independent ground truth from the real
applier+bake). Quarter-turn readings are a corroboration, not the
values to use — use the fitted values verbatim
(`joint-sandwich.json`, least_squares fit, cost 1.26e-11;
574 max 0.1303°, 578 max 0.1264°). (FIX §3a.)

- **U = [−9.065745367323996e-08, −0.7071069097729176, 1.5105919552772413e-07, 0.7071066526001321]**
  (rotation −90° about Y)
- **V = [−0.7071071969384257, 1.77930984126504e-07, 2.966911986689868e-07, 0.7071063654343402]**
  (rotation −90° about X)
- **W = [0.7071070588569249, −1.0336369739735198e-07, −1.534060432249343e-07, 0.7071065035160369]**
  (rotation +90° about X)
- Full-precision cost: 1.2602142783400068e-11.

Recompute for every frame:
`Hips[f] = U · E_BASE[f] · V · E_HIP[f] · W`, with E_BASE/E_HIP from
the game-sampler c8 triples via `applier_euler` (BASE = (Z,Y,−X),
Hip = (Z+π/2,Y,−X)) under Euler order XYZ, rounded to 6 decimals
with bank sign continuity (flip when dot with previous frame < 0).
Same procedure as `decode-sampler.py`, with the (U,V,W) swapped.
Change NOTHING else: all other 20 joints, `root_t`,
`root_motion_fwd_m`, and metadata are copied verbatim. The Spine
sandwich is a separate fit and is UNCHANGED (still approximate/flagged,
§1b). (FIX §3a.)

Effect at f0: victim Hips goes from ~180° about Z (upside down) to
152.4° about +Y (575) / 180.0° about +Y (579) — pure yaw, upright.
The flip at f0 is a ~178.8° change in Hips orientation for both
receivers. Scope: 575 changes on 44/130 frames (first ~half; the
mid-throw tornado inversion is REAL and untouched — torso max still
171.2° @f58); 579 changes on 138/138 frames (whole clip).
Validation: joint fit 574+578 cost 1.26e-11; 574 max 0.1303°,
578 max 0.1264°; unique — identical (U,V,W) from orig / identity /
random starts (dist 0.0000°, same cost). Hold-out 588 (never fitted):
joint-fit Hips max 0.1278° mean 0.0358°; OLD sandwich on 588: max
178.75° mean 139.4°. Hold-out conjugations (M solved on 574 only,
predicted on unseen clips): worst 0.2013° on 578, 0.2026° on 588 —
only Hips needed the joint fit. Fixed victims: f0 torso pitch
32.8° / 34.5° (was 147.9° / 146.6°); f0 feet Y 0.13 m (was 2.00 m);
f0 head Y 1.53 / 1.54 m (was 0.60 / 0.63 m). Mid-throw preserved:
torso max 171.2° @f58 / 175.9° @f56. End states: thrower standing,
victim flat (hips Y last 0.18 m). (FIX §3a, §5.)

### 3d. Placement — shared thrower frame (for renders / staging)

- ONE heading for the pair, from the THROWER's f0 shoulder line
  only (square-heading: thrower → +X; 121.9° for 1+3, 93.0° for
  2+4), applied to BOTH figures.
- ONE shared translation: thrower f0 root → (0,0,0); victim f0 root
  → authored offset rotated (victim f0 hips 1+3 (−0.617, 0, −0.992),
  2+4 (−0.036, 0, −0.741)).
- Do NOT recenter each figure independently and do NOT take a heading
  from the victim's f0 shoulder line (unreliable exactly when the
  victim starts inverted).
- After the fix, the victim's pelvis faces ~180° from the thrower's
  at f0 (575: 152.4° vs −29.5°; 579: 180.0° vs −10.0°) and the pair
  closes to 0.51 m @f52 / 0.46 m @f43, like T3. (FIX §3b.)

Why the old placement failed even with fixed victims: the thrower's
hips travel ~1.19 m by f30 toward azimuth ~212°, while the victim's
placed base sat at +X — the thrower runs away from the victim's
placed position (rendered hips min = f0 1.00 m; 1+3 f30 2.33 m).
Honest trade-off: the shared f0 is a side clinch, not a face-to-face
grab stance — by the numbers the victim's chest bearing to the
thrower is ~115° off at `_n`/`_y` f0 (authored data: the pair starts
side-on, King stepping in from 1.17 m). The face-to-face connect
lives in the grab clip + hold 554 BEFORE these clips. No single rigid
staging of `_n`/`_y` alone does both perfectly; the full fix is
staging grab+hold+throw as one sequence (follow-up, §6). (FIX §6.)

The shoulder-line trap, for the record: a 180° rotation about the
facing axis (Z) flips the shoulder line but leaves chest-forward
unchanged — so on the inverted victims the shoulder-line facing read
~180° off the pelvis/chest facing (−158.8° vs pelvis +27.6°;
+170.4° vs pelvis 0.0°). The old render trusted the shoulder line,
so BOTH chests faced +X (victim 81.8°, thrower 87.6°) — back to the
thrower, exactly as the owner saw. T3 victims' headings differ from
throwers by ~180° (correct); T7 victims' differed by only 53° /
6.6°. (FIX §1.)

### 3e. Rebuild requirement — every receiver built with the 574-only sandwich

**Every JSON built with the 574-only sandwich is suspect wherever its
E_BASE leaves the qz family.** That includes all 22 P1/P2 receivers
(589/591/593/595/597/615/581/655/657/786/663/667/671/673/675/679/
692/696/700/704) and bank thrower 588, whose Hips was wrong by max
178.75° / mean 139.4° under the old sandwich. **All 22 + 588 must be
rebuilt with the joint sandwich before use** — procedure in §5.
(FIX §4, §6.) `decode-sampler.py` / `pull-clips.py` must be updated
to the joint sandwich before any more receivers are built.

---

## 4. Audit scope (which receivers need the flip)

**18 of 22 P1/P2 receivers NEED THE FLIP. 4 are UNCLEAR. 0 are OK.**
Plus the two reference front receivers (575/579): both NEED THE
FLIP. Across all 24 receivers measured: **20 NEED FLIP, 4 UNCLEAR,
0 OK.** All 24 `_n` throwers OK at f0 (receiver-only defect).
(AUDIT §0.)

Method (same FK as Lane B's `measure-t7.mjs`, so numbers are
comparable; validated by reproducing Lane D's 575 f0 exactly — Hips
Y 1.068 m, Head Y 0.601 m, feet Y 1.999–2.010 m, pitch 147.9°).
Calibration (the working reference): T3 pair clips — 1+3: thrower
−18.5°, victim −18.3° (ΔfaceSh +0.2°); 2+4: thrower −1.4°, victim
−0.3° (ΔfaceSh +1.1°). A correct pair has the victim's authored
heading MATCHING the thrower's (ΔfaceSh ≈ 0°). Tolerance:
|ΔfaceSh| ≤ 35° = "facing OK". (AUDIT §1.)

| Group | Clips | Verdict |
|---|---|---|
| Standing (7 P1/P2 + ref 575/579) | 589/591/593/595/597/615/581 | NEED FLIP — full flip. f0 pitch 135.2–156.3°, head 0.50–0.63 m, feet 1.88–2.05 m in the air. **Exception: 593 and 597 need the inversion fix only** — facing already matches their throwers (ΔfaceSh −6.0°/−6.1°) because their throwers are back-throwers facing ~176°. |
| Air (2) | 717/719 | NEED FLIP — in the air. Pitch 100.5–103.3°, head below hips, rolled 46–49° shoulder tilt, backs to thrower (ΔfaceSh +164.6°/+167.6°). **Feet-to-floor does NOT apply** — victim is juggled (hips Y 1.29–1.32 m, throwers on the ground at 1.05–1.06 m waiting to catch). |
| Crouched (3) | 655/657/786 | NEED FLIP — at crouch height. Pitch 119.9–129.8°, feet 1.56–1.70 m up, backs to thrower (ΔfaceSh −152.7°/−163.9°/−170.7°). **The low start is legitimate and must be kept** — receiver hips Y 0.85–0.92 m matches the crouched throwers (0.82–0.85 m). Do NOT raise the victim to standing height. |
| Ground face-up (6) | 663/667/671/673/675/679 | NEED FLIP (roll) — flat and on the floor (hips 0.18–0.21 m, feet 0.20–0.31 m), but chest faces the floor (chestFwdY −0.96) when the position is face-UP. Un-roll 180° about the spine axis. |
| Ground face-down (4) | 692/696/700/704 | **UNCLEAR** — chest-down is correct for face-down, flat on the floor, feet on the floor (G_Hips a clean 90° about +X — the correct standing→prone rotation). Heading cannot be verified against any working reference: Rule A (T3-calibrated ΔfaceSh ≈ 0°) passes only 704 (−26.6°); Rule B (head points toward thrower's authored position) passes only 696 (5.9° off). No working ground-throw reference exists in the T3 pair data. Lane D's render (or the owner's eye on it) decides whether these four need a yaw-only flip or nothing. |
| Throwers (24) | 574/578/588/590/592/594/596/614/580/718/716/654/656/785/662/666/670/672/674/678/691/695/699/703 | **All OK at f0.** Standing 17.3–44.5° pitch, crouched 47.4–57.4°, ground 71.2–95.9° bent over the victim, feet 0.13–0.21 m on the floor. The ground throwers' 71–96° pitch is the legitimate "bent over the downed victim" pose, not the receivers' defect. |

Summary count: **18 of 22 NEEDS FLIP** (7 standing + 2 air +
3 crouched + 6 ground face-up), **4 of 22 UNCLEAR** (ground
face-down), **0 of 22 OK**. (AUDIT §2, §3, §4.)

Runtime caveat (flagged, not decided — AUDIT §4.7): whether the YAW
part of the flip is needed at runtime depends on whether the live
game squares the receiver's f0 heading to face the thrower at
placement, as the render export does. If the runtime does that, only
the inversion/roll part matters; if it plays the authored yaw raw,
the full flip (inversion + yaw) is needed for 16 of the 18 (all but
593/597). This is a live-game question, not decidable from the clip
data.

---

## 5. How to apply it to any other receiver (procedure)

1. Sample the clip with the game sampler (`sample-c8.py` pattern:
   `emulate_sampler` + `t7_anim64`, exe sha `7f2b6872…`) → c8
   triples (69 floats/frame) + raw quats. (FIX §4.)
2. Build E_BASE (track 3) and E_HIP (track 5) with
   `decode-sampler.py:applier_euler` + `euler_quat6` (order XYZ for
   both sandwich tracks). (FIX §4.)
3. `Hips[f] = U·E_BASE[f]·V·E_HIP[f]·W` with the joint (U,V,W) from
   §3c. Round to 6 decimals, sign-continuity vs the previous frame.
   (FIX §4.)
4. Replace ONLY `rot_xyzw['Hips']` in the clip JSON; record the fix
   in an `orientation_fix` metadata block (see
   `rotsm_575-fixed.json` / `rotsm_579-fixed.json` in the Lane B
   workdir for the template). (FIX §4.)
5. Verify: format wh-anim/1, 60 fps, 21 bones, 0 NaN, quat norms
   ≤ ~2e-06 deviation, f0 torso pitch < ~40°, f0 feet Y ≈ 0.13 m,
   f0 pelvis facing ≈ thrower facing + 180°. (FIX §4.)
6. Render with the shared thrower-frame placement (§3d); check the
   hips-distance curve closes (min ≈ 0.5 m mid-clip, like T3) and
   eye-check f0 / mid-throw / end frames. (FIX §4.)

---

## 6. Hunt verdict — there is no complete working source to pull instead

**No complete working source exists.** After 15 live searches and 5
pages opened and read in full, nothing public carries already-decoded,
correctly-oriented T7 King throw animations (thrower `_n` + receiver
`_y` pairs) in a usable format (GLB/FBX/BVH/JSON), and no public
vanilla King `.tkmvst` exists to download either. (HUNT §0.)

- **Every `.tkmvst` in the wild carries native 0x64 data, not decoded
  joints** — so every `.tkmvst` still needs our decode pipeline
  (which is where the flip problem lives). TKMovesets2 v1.1 README
  (current commit 6939344): T7 extraction is "extract any or all
  movesets straight from the game files" and T7→T8 conversion
  "converts animations too" — inside the native format, not into
  FBX/GLB/BVH. No decoded-joint export of any kind. The TTT2-UE
  README states its imported T7 movesets are "in TKMovesets2's
  `.tkmvst` layout, which it can also read" — and its importer
  converts those movesets into its own engine at import time; the
  `.tkmvst` itself is never decoded joints. (HUNT §0, §2.)
- Closest partial source: Petexy's Tekken-Tag-2-Ultimate-Edition —
  a working, recompiled game engine that plays T7 movesets with
  correct orientation. What it lacks: it cannot import King (King is
  native to TTT2, so only the 17 T7 fighters TTT2 lacks are
  importable), it exports no decoded animations, and pulling it means
  pulling a whole game engine, not a clip pack. Use it only as an
  orientation reference (watch a T7 importable fighter's throws play
  in a real engine) and as a second `.tkmvst` reader. (HUNT §1 #2.)
- Second-closest: TKMovesets2 v1.1 itself — the tool that produces a
  vanilla King `.tkmvst` from your own Steam copy in one click
  ("Extract all Tekken 7 movesets from game files"). It yields native
  data (same bytes Phase 2 already extracted from `tkdata.bin`), so
  it does not skip our decode pipeline — it only independently
  confirms the extraction. Expected result (a prediction, not a
  finding): identical clip numbers and native bytes. (HUNT §1 #1.)
- archive.org, live-checked 2026-11-21 (28 hits): 0 moveset items —
  all hits are gameplay videos, Death Battle, documentaries, T8
  trailers. Re-confirms Lane C's 0. (HUNT §3.1.)
- **Our in-house chain IS the already-decoded source:** Phase 2's
  King `.tkmvst` (15,773,258 B, 2,787 moves) + the game-sampler
  decode (round-trip 3.6e-7) + the receiver pulls (575/579 + 22
  P1/P2, Nov 21). There is no second, better-decoded version to pull
  instead. The remaining work is orientation/fit, not finding another
  decode. (HUNT §2.5, §4.4.)
- Unchecked, not "absent": the Tekken modding Discord (#movesets) —
  invite-gated / login-required, not bypassed. The one place a vanilla
  `.tkmvst` or decoded pack could plausibly be shared informally; a
  parent with Discord access could ask there. (HUNT §3.10, §5.)

### 6a. Future-pull checklist (so the flip defect never recurs)

When a new T7 clip is pulled, follow this in order — do not skip a
step because the last pull "looked fine":

1. **Archive.org first** (standing law) — check live for the game /
   moveset; a stale "not on archive.org" note is not a check.
2. **Extract, don't download, the vanilla `.tkmvst`** (TKMovesets2
   v1.1, "Extract all Tekken 7 movesets from game files") and compare
   its move/animation references against the Phase 2 extraction
   (King: 2,787 moves). Expect native 0x64 data — it confirms the
   extraction, it never replaces the decode. (HUNT §1 #1.)
3. **Decode only through the game sampler** (§1) with the per-bone
   Euler orders (§1a). Never use the pure `Anim64` port as the decode
   path — the control test proved it does not reproduce the bank.
   Never fit a sandwich on a single clip: a 1-DOF E_BASE family makes
   the fit degenerate (§3b). Any new sandwich constant must be fit
   jointly on at least two banks whose E_BASE families differ, and
   validated on a hold-out bank never fitted (588's numbers in §3c
   are the bar: hold-out max ≤ ~0.13°).
4. **Use the joint sandwich (§3c) for Hips** — never the 574-only
   constants. Update `decode-sampler.py` / `pull-clips.py` to the
   joint sandwich before building any more receivers.
5. **Identify roles from the throw data, not the clip labels:**
   `_n` = thrower (connect cancel + damage + break-free), `_y` =
   receiver (no incoming cancels, break window, damage 0) — §2.
   Read the two-stage mechanism: hold 554 first, then the `_y` from
   the throw motion's standing slot. Do not read only the grab's
   HitCondition row (that gives 554, the hold).
6. **Audit f0 before use** (§4 method): torso pitch, feet/head/hips
   Y, shoulder-line facing vs the thrower, chest-forward Y. A
   standing receiver with f0 pitch > ~40° or feet Y > ~0.3 m is
   inverted until proven otherwise; a ground face-up receiver with
   chestFwdY ≈ −1 is rolled. Apply the per-position fix (§4 table),
   never a blanket flip: 593/597 inversion-only, air in-air,
   crouch keeps crouch height, ground face-up is a roll.
7. **Stage with the shared thrower frame** (§3d) — one heading from
   the thrower's f0 shoulder line only, one shared translation.
   Never recenter per-figure, never take a heading from an inverted
   victim's shoulder line.
8. **Verify per §5 step 5–6** (format, quat norms, f0 pitch/feet/
   facing, hips-distance curve closing to ≈0.5 m mid-clip) and
   eye-check f0 / mid-throw / end frames. Keep the
   `spine_approximate` flag (§1b) on every receiver JSON.
9. **Log the pull in this doc's lineage:** if a new sandwich, a new
   position, or a new exception appears, update this doc + the
   `STATUS.md` row in the same PR — docs land in the same PR as
   each fix (see `docs/decode/README.md`).

---

## 7. Open items (not hidden, not decided here)

- **Rebuild owed:** all 22 P1/P2 receivers + bank thrower 588 must
  be rebuilt with the joint sandwich before use (§3e). This PR is
  docs only; the rebuild is a separate lane's work.
- **Ground face-down 692/696/700/704:** UNCLEAR — yaw-only flip or
  nothing, decided by Lane D's render or the owner's eye (§4).
- **Spine:** approximate (53.5° max / 17.8° mean on 574), unsolved
  exactly (§1b).
- **Runtime yaw question:** whether the live game squares receiver
  yaw at placement (§4, caveat).
- **Full staging:** grab + hold 554 + throw as one sequence — the
  face-to-face connect lives there, not in `_n`/`_y` alone (§3d).
  Move 554's `rotsm` clip number is unmapped (anim `nab6_guard(DVD)`,
  anim_id 33363).
- **Real-T7 footage check:** real T7 Winding Nut gameplay footage
  was NOT watched in any lane (no live browser) — the open
  verification Lane C flagged remains open. (HUNT §5; HUNT-CP.)
- **T3-vs-T7 default:** T7 stays the default — the "T7 has no
  follow-through" premise is dead and the pairing is now
  real-file-verified (HUNT-CP, follow-up §136). The merge call for
  any live-game wiring sits with the owner.
- **Licence (logged honestly, never a gate):** the clips are Bandai
  Namco game data; TKMovesets2 is GPL-3.0; TTT2-UE's own code is MIT
  with Namco assets in its packs (never shared). (HUNT §1.)

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

---

# W3b addendum (2026-10-21) — the FK hunt invalidated the input data itself

Workstream W3b (continuation of W3): recover the AKI FK composition from
the No Mercy ROM player code with Ghidra, build AKI FK → T3 IK targets,
re-bake all 11 clips through the same gate.

**Verdict: the FK composition was NOT recovered — the animation player
function was not located in the segments analyzed. No rows were written,
no `t3_row` wiring was added, and the gate was NOT re-run.** But the hunt
produced two proven findings that change the state of everything above:
**the clips W3 converted were not the Rock moves at all, and the record
field layout the whole pipeline assumes is wrong.** W3's gate numbers
were measured on chimeric data from the wrong files with a truncated
rotation channel; they do not measure the true clips, in either
direction. Details and evidence below — this section follows the task's
step-5 rule: evidence, no guessed IK mappings, no gate loosening, no
broken rows shipped.

## Finding 1 — the extraction window is wrong (proven from the game's own code)

ROM used: `WWF No Mercy (USA) (Rev A)`, from this repo's GitHub release
`no-mercy-n64-v1`. SHA-256
`fc561fce443010b114cc8ea41226772b7b2a2d33055be163fad91ac9c3b096cb`
(matches the release digest), CRC32 `BACEEA13` (matches the teardown
doc), header revision byte = 1 (Rev A / NTSC-U 1.1).

Ghidra 12.1.4 headless on the `main` segment (821 functions) decompiled
the game's own file-table code:

- `FUN_80003ab0` (file-table init) loads the table from **ROM
  `0x16C31D8`** (`FUN_8000062c(0x16c31d8, buf, 0x1300c)` — 0x1300C =
  19459 entries × 4 bytes) and computes every file address as
  `(entry & 0xFFFFFFFE) + 0x1BD150` → **FirstFile = `0x1BD150`**.
- `FUN_80003bd0` (get-file-info) treats file IDs as **1-based**: valid
  range 1..0x4C02, table index = `fid − 1`; start from `table[fid−1]`,
  end from `table[fid]`.

VPWStudio's `DefaultGameData.cs` corroborates: its
`NoMercy_NTSC_U_11` definition uses exactly FirstFile `0x1BD150` /
FileTable `0x16C31D8` (and a `SetupFT_FTLocation` code patch point).

The repo's extractors (`extract_all_anims.py`, `anim_extract.py`, and
everything built on the resulting `.npy` bank) instead used the
VPWStudio **NTSC_U_10** pairing — FileTable `0x16C3238`, FirstFile
`0x1BD1B0` — with 0-based indexing. The two "tables" are one table: the
U10 base sits exactly 24 entries into the true table, and FirstFile
differs by exactly 0x60. Net effect, for every clip the pipeline has
ever read:

> Repo clip "fid" = the bytes of **game file `fid + 0x19`**, starting
> 0x60 bytes (exactly 23 joint records) into it, spliced with the head
> of game file `fid + 0x1A`. Its length — and therefore its "frame
> count" — is game file `fid + 0x19`'s length.

The bug is silent because the shifted windows still satisfy
`length = 4 + N×98` arithmetically (the table differences are
identical), and the "frame counts match the moveset notes" check was
circular: the notes were derived from the same bank. For the 11 Rock
clips (anim IDs are the correct files — every DB label matches the
move), the truth is:

| MK id | Anim | DB label | W3 frames (wrong file) | True frames (game decode) | File W3 actually converted (+0x19) |
|---|---|---|---|---|---|
| MK-1240 | 0x37FA | [Front Special Grapple] Rock Bottom P1 | 49 | **70** | [Front Special Grapple] Front Russian Sweep |
| MK-2843 | 0x3E3D | [Special Ground Head Grapple] People's Elbow P1 | 7 | **112** | [Ground Head Grapple] Mahistro Cradle |
| MK-3473 | 0x40B3 | [Running Ground Attack] People's Elbow P1 | 16 | **39** | [Strong Flying Attack] Back Body Press |
| MK-4353 | 0x4423 | [Taunt] Rock 01 | 62 | **17** | [Taunt] Taunt 011 |
| MK-4347 | 0x441D | [Taunt] Rock 02 | 49 | **82** | [Taunt] Edge & Christian |
| MK-4354 | 0x4424 | [Taunt] Rock 03 | 55 | **24** | [Taunt] Taunt 019 |
| MK-4233 | 0x43AB | [Entry Way Taunt] Rock | 34 | **102** | [Entry Way Taunt] Taka |
| MK-4269 | 0x43CF | [In The Ring Taunt] Rock | 35 | **103** | [In The Ring Taunt] Taunt 011 |
| MK-1885 | 0x3A7F | [Special Irish Whip Grapple] Rock Spinebuster P1 | 16 | **13** | [Special Irish Whip Grapple] Crippler Crossface |
| MK-3120 | 0x3F52 | [Ground Attack Sitting Up] Rock Stomp | 16 | **20** | [Ground Attack Sitting Down] Stomp 02 |
| MK-3659 | 0x416D | [Front Running Grapple] Rock Spinning DDT P1 | 28 | **28** | [Back Running Grapple] Half Nelson Suplex P1 |

Every true file decodes clean: `length = 4 + 98 × frames`, remainder 0.
The 4-byte Toki2 header's last byte independently gives
`frames = b3/2 + 1` on the checked files (stance 0x2DD9: header
`07ff001e` → 16 ✓; Rock Bottom 0x37FA: header `04aa008b` → 70 ✓).

**Blast radius:** the `.npy` bank and the v1/v2/v3 pose artifacts
(`aki-rock-v3/*.json`) are shifted the same way for *every* clip, not
just Rock's. The v2 "proven" clip (0x339A) and its channel correlations
were measured on game file 0x33B3's splice. Anything downstream of the
bank needs re-extraction with the game-exact recipe:

```
table  = u32be[19459] at ROM 0x16C31D8
file(fid) = ROM[ 0x1BD150 + (table[fid-1] & ~1) : 0x1BD150 + (table[fid] & ~1) ]   # fid is 1-based
```

## Finding 2 — the PivotRotation record is 12/10/10, not 12/8/12

W3 (following VPWStudio's `AkiAnimation.cs` nibble layout and the repo's
FORMAT.md) decoded each 4-byte record as PivotX s12 / **Rotation s8** /
PivotZ s12. On the game-indexed decode of the stance clip (0x2DD9, 16
frames — a near-static pose, the perfect control), that split makes
PivotZ cycle through exactly {−1542, −518, +506, +1530} — values spaced
1024 apart, i.e. two stray high bits, not motion.

Re-splitting the same words as **[PivotX s12][Rotation u10][PivotZ
s10]** (12+10+10 = 32) makes *every* channel smooth on the control clip:

- Rotation (1024 = full turn): mean per-frame delta 0.1–3.7 units across
  all 19 PR joints. Pelvis rotation arcs 43→48→42 (breathing sway);
  OverallMovement's rotation channel arcs 176→168→178 (the root bob).
- PivotX is constant per joint in stance (sd 0.0 for Pelvis); PivotZ's
  low 10 bits are smooth (sd 0.0–19.5).
- On Rock Bottom (0x37FA, 70f), rotation unwrapped mod 1024 gives mean
  deltas 7.5–24.7 units/frame (2.6°–8.7°/frame) on all joints — real
  action speeds, versus the 74–109°/frame garbage the gate measured.

So the "s8 rotation" every converter since v1 has used is the middle 8
bits of a 10-bit rotation; its top 2 bits were being read as PivotZ's
high bits. W3's mod-256 unwrap fixed a symptom of this truncation.
VPWStudio's editor documents only the storage nibbles and contains no
playback/composition code, so its 3/2/3 split was never validated
against the player — ours now has been, by the control clip.

What is still **not** known (do not guess): the geometric meaning of
PivotX (s12) and PivotZ (s10), the role of the 3-byte Movement records,
and the joint hierarchy composition. Those live in the player code
(finding 3). LeftHand/LeftFingers tracks are near-identical in the true
decode (possibly genuine AKI duplication; unconfirmed).

## Finding 3 — player search: what was covered, what each lead actually was

Segments (per the in-repo recomp `nomercy.yaml`): `main` fully
Ghidra-analyzed (821 functions); `ovl_e` fully analyzed (870
functions); `ovl_b` imported and analyzed; `ovl_a`, `ovl_c`, `ovl_d`
capstone-scanned only. Signatures hunted and resolved:

- Immediate `0x62` (frame stride 98): all ovl_e hits are state/sound
  IDs (0x62 = 99) and state-machine compares — not frame indexing.
- `andi 0x3ff` clusters: ovl_b @0x8011178c and ovl_e @0x800da420 /
  0x800db5a0 are **GBI display-list builders** — GBI packs 10-bit
  screen coordinates with the same masks, so this signature is
  poisoned and cannot isolate the player.
- `sra 22` cluster in main @0x800184cc: byte-index arithmetic inside
  the CAW appearance helpers (`FUN_8001858c`…`FUN_800188fc`); their
  caller `FUN_80018a3c` is the CAW appearance-record builder, not the
  player.
- `srl 10` + `andi 0x3ff` pair in main: `FUN_800135d0`, an unrelated
  sign-magnitude stream decoder (float output + delta accumulators).
- `FUN_8000c1a8` (main): the **AkiModel vertex decoder** (8-byte
  vertices, (s8 + nibble offset) × scale) — model side, not animation.
- Caller-tracing from `FUN_80003bd0` (get-file-info) is too noisy: it
  is called from every segment for every file type.

**Where it stalls:** the player/unpacker was not found in main, ovl_b,
or ovl_e. The two large match overlays `ovl_c` and `ovl_d` were not
Ghidra-imported this run (box RAM was saturated by other lanes; Ghidra
jobs were kept serialized and small), and the player may consume a
pre-unpacked frame struct — in which case its signature is float math
on shorts, and the *unpacker* (whoever reads 0x62-stride Toki2 frames
for AkiAnimation file IDs) is the tractable target. What would crack
it, in order: (1) Ghidra-import ovl_c and ovl_d, find callers of
get-file-info that handle AkiAnimation IDs and read 98-byte strides;
(2) failing static recovery, run the ROM in an emulator with a
watchpoint on the stance file's RAM copy and trace the consumer;
(3) the player decompile then answers X/Z semantics, Movement-record
role, and hierarchy in one read.

## What this does and does not change

- **Invalidated:** W3's per-clip gate numbers, the "frame counts match"
  check, the v3 pose artifacts as representations of the named moves,
  and the `.npy` bank as a whole. The gate's verdict on the *true*
  clips is unknown today and must not be pre-judged either way — the
  corrected rotation channel alone removes the truncation that made
  even correct-file data whip.
- **Not invalidated:** the T3-side mechanism (pose.py: IK slots are
  overwritten from IK target channels — measured on the real USA
  tables), the gate calibration (the king pack's 176 real rows), the
  bake pipeline shape in `aki_row_bake.py`, and the FK→IK requirement
  itself.
- **Bank state:** untouched by W3b (no bake was run). `ryuji-rock.json`
  unchanged by W3b; its `aki_bake` records describe W3's run on the
  wrong files and should be refreshed by the follow-up lane, not
  edited on speculation here.

## Corrected next-step sequence (follow-up lane)

1. Fix the extractors to the game-exact window (FT `0x16C31D8`, First
   `0x1BD150`, 1-based) and re-extract the bank; spot-verify against
   DB labels + the `b3/2 + 1` frame rule.
2. Re-decode with the 12/10/10 record split; re-run the v3-style
   conversion and the **same** gate on the true 11 clips.
3. Recover the player from ovl_c/ovl_d (static) or by emulator
   watchpoint (dynamic); build AKI FK → wrist/ankle trajectories →
   T3 IK target channels (YANM v2 pattern) in `aki_row_bake.py`.
4. Only gate-passing clips write rows + `t3_row` pointers, as scoped
   in W3.

## Harness proof — PENDING (two blockers)

1. No clip has passed the gate on valid input: the FK composition is
   unrecovered and W3's input data is invalidated above, so no honest
   frame of CornerStone performing a No Mercy Rock move can exist yet.
2. RAM: during this run the box carried other lanes' Blender and
   Ghidra jobs with ~1.4–3.2 GB of 7.7 GB available; per the RAM law
   this lane started no Blender job and kept Ghidra serialized.

## Def Jam transfer notes (W3b update)

- The FK→IK requirement applies identically to Def Jam AKI-lineage
  clips (WRES_ALL), as W3 stated. This lane's conversion work is
  **not** bank-agnostic: the decode constants proven here (file-table
  window, 1-based IDs, 12/10/10 record split) are **No Mercy ROM
  facts**, recovered from No Mercy's own code and data.
- Finding 1 carries a general warning for the PS2 bank: an extraction
  window can be wrong in a way that still produces clean lengths and
  plausible frame counts. Any WRES_ALL extraction must be validated
  against Def Jam's own file-table/code path *before* conversion —
  not after a gate failure.
- Finding 2 does **not** transfer as fact: whether WRES_ALL motion
  records share the 12/10/10 split is unverified (W3's caveat stands).
  A PS2 variant needs its own control-clip test (a near-static clip
  whose channels must all go smooth under the correct split) and,
  ideally, its own player-code recovery — the PS2 binary is a
  different RE target (EE MIPS, .VIV container) even though the
  pipeline shape (gate + YANM overlay) carries over unchanged.


# Tekken 3 3DMK Model Mapping — Findings (2026-10-12)

## Character Record Mapping

The 52 3DMK records at BNS IDs `71 + 4n` (n=0..51) are character models.

**Confirmed anchor:** ID 71 = `paul3.kmd` (per n0madic/tekken3remake docs).

## ⚠️ CORRECTION (2026-10-12 — verified): The record table below was WRONG

A previous worker assumed the USA name-table order was
[PAUL, LEI, KING, YOSHIMITSU, ...] and "confirmed" record 87 as King via
pointed-ear head geometry. Both assumptions were wrong:

- The actual name table in `SLUS_004.02` @ `0x129ac` (verified from the
  disc image, fixed-stride entries) is:
  `0:PAUL 1:LAW 2:LEI 3:KING 4:YOSHIMITSU 5:NINA 6:HWOARANG 7:XIAOYU
  8:EDDY 9:TIGER 10:JIN 11:JULIA 12:KUMA 13:PANDA 14:BRYAN 15:HEIHACHI
  16:OGRE 17:MOKUJIN 18:GUN JACK 19:GON 20:ANNA`
- Mapping: P1 BNS ID = `71 + (name_index × 8)`, P2 costume = P1 `+ 4`
- **Record 87 is LEI (index 2), not King.** The old `king_full_front.png`
  render is actually Lei Wulong.
- **The real King is BNS record 95/99** — confirmed by his texture set
  (TIMs 6213–6271 in the gap after record 95): jaguar mask with spotted
  fur, blue pants, purple trunks with gold design, gold boots
  (`renders/king/textures/real_king/`). See
  `docs/BNS-ORGANIZATION-PATTERN.md` for the full verified pattern.

## Character Record Mapping (corrected)

| BNS IDs | Character |
|---------|-----------|
| 71, 75  | PAUL |
| 79, 83  | LAW |
| 87, 91  | LEI |
| 95, 99  | **KING** ← verified via texture set (jaguar mask, blue pants, purple trunks, gold boots) |
| 103, 107 | YOSHIMITSU |
| 111, 115 | NINA |
| 119, 123 | HWOARANG |
| 127, 131 | XIAOYU |
| 135, 139 | EDDY |
| 143, 147 | TIGER |
| 151, 155 | JIN |
| 159, 163 | JULIA |
| 167, 171 | KUMA |
| 175, 179 | PANDA |
| 183, 187 | BRYAN |
| 191, 195 | HEIHACHI |
| 199, 203 | OGRE |
| 207, 211 | MOKUJIN |
| 215, 219 | GUN JACK |
| 223, 227 | GON |
| 231, 235 | ANNA |

### Western Heart roster targets
Jin 151/155 · Yoshimitsu 103/107 · Heihachi 191/195 ·
Bryan 183/187 · Gun Jack 215/219 · Xiaoyu 127/131

## 3DMK Format (corrected)

Reference: https://github.com/n0madic/tekken3remake/blob/HEAD/docs/research/formats/3dmk-models.md

**Critical correction:** Row table starts at file offset **0x10**, not 0x18.
- Header: 0x00 u32 row_count (27), 0x04 u32 scale, 0x08 "3DMK", 0x0C u32 zero
- Rows: 27 × 56 bytes at 0x10..0x5F8
- Row fields: +0x00 verts, +0x04 variants, +0x08 normals, +0x0C faces, +0x10 texmap, +0x14 s32 x,y,z (joint), +0x20 s32 parent (part index), +0x30 u32 active

**Face indices** reference skinning slots, not direct vertices:
- slots[0..nimports-1] = imported seam vertices from other parts
- slots[nimports..] = own vertices
- Face vertex = slot - nimports (skip faces referencing imports for simple render)

**Parser:** Use `/tmp/tekken3remake/tools/research/kmd.py` (proven implementation). Do NOT reimplement — the slot mapping and packed bitfields are subtle.

## King Model Stats (Record 95 — corrected)

- ~~Record 87 (superseded — that was Lei)~~
- P1 record 95 / P2 record 99; texture TIMs 6213–6271 extracted at
  `renders/king/textures/real_king/` (59 textures: jaguar mask, blue pants,
  purple trunks, gold boots, skin, gold energy sprites)
- Raw geometry extracted 2026-10-12 via n0madic/tekken3remake proven parser
  (tools/research/kmd.py, now persistent at ~/workspace/tools/tekken3remake/):
  `models/king95/king95.kmd` (25,832 bytes, 27 rows, 21 active parts, 0
  unresolved seam fetches), `models/king95/king95_parts.obj`, render data
  pickle + part montage (fragments under identity transform — expected).
  The old record-87 renders were renamed to `renders/king/lei_*` (they are
  Lei Wulong, not King).
- Full-body bind pose STILL PENDING: static renders show part fragments;
  need default joint rotations from the animation system — n0madic
  motion_bake.py / motion.py is the next tool to try.

## Legacy Record-87 Stats (actually LEI — kept for reference)

- 636 vertices, ~808 renderable faces (262 faces reference seam imports)
- 20 active body parts
- Parts: head (105v), chest (96v), pelvis, thighs, shins, feet, upper arms, forearms, hands, etc.

## Rendering Status

✅ **Individual parts render correctly** — head with jaguar ears confirmed
❌ **Full skeleton assembly blocked** — joint offsets position parts linearly along +X; the reference/bind pose requires base joint rotations from the animation system (not in the KMD file). The game applies these via DrawSkinnedPart with animation matrices.

**Next step for full-body (2026-10-12 watchdog update):** King's motion bank
(divmot type 3 = bank 3, confirmed via n0madic ai.md hooks table) extracted
from the local disc at `animations/divmot03_king.bin` (BNS ID 283, sector
offset ×2048 from TEKKEN3.BNS; header byte 0x01 = 3, 652 move rows).
Stance moves = move-index slots 0–2 (rows 523/525/524). Pose sampling works
WITHOUT the Japan Rev.1 EXE: `tools/local/pose_sample_analytic.py` ports
n0madic's `motion.py` channel walk and replaces the EXE spline-weight tables
with the analytic uniform cubic B-spline basis (+ the game's documented
modified first-segment weights 1/6, 4/6, 1/6 at t=0). Bit-exactness is NOT
claimed (±1–2 units vs hardware) but that is ~0.01° — fine for bind pose.
Sampled poses: `models/king95/king95_stance0_pose.json` (slot 0, frame 0),
`models/king95/king95_stance2_pose.json` (slot 2, frame 0) — 49 channels each.

**Remaining gap — pose.py needs the USA EXE tables.** `pose_build_matrices`
(pose vector → 18 joint matrices → part world matrices) reads these from
hardcoded Japan Rev.1 addresses; our EXE is USA (SLUS_004.02):
- `EULER_SLOTS` (JP 0x8001A330): matrix slot of each of the 10 Euler joints
- `LIMB_BASIS` (JP 0x800972D0): constant basis for slots 2, 3, 7
- `SKELETON_OFFSETS` (JP 0x800972F0): 4×int[3] chest, R/L shoulder, hips
- `LIMB_OFFSETS` (JP 0x80097320): 4×int[3] IK root offsets (arms, legs)
- `SIN_TABLE` (JP 0x8001E8C4): g_sinTable — SYNTHESIZABLE (4096-unit sin)
- `SQRT_TABLE` (JP 0x800990AC): SquareRoot0 mantissa table — synthesizable/standard GTE
To continue: locate these six tables in SLUS_004.02 (pattern-match against
the JP layout or find PoseBuildMatrices in the USA disassembly), then port
`pose.py`'s `ExeTables` to the USA addresses. The part→matrix-slot table
(JP 0x8001A074) is already documented above (part/row/matrix table).

## Files

- Parser: `tools/local/kmd_parse.py` (basic, use n0madic's instead)
- King head render: `/tmp/king_model_render.png`
- King parts: `/tmp/rec87_parts.obj`
- n0madic repo: `/tmp/tekken3remake/` (full format docs + parser + viewer)

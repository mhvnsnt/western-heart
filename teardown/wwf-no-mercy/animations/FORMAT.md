# Animation export format — WWF No Mercy AKI keyframe bank

Source ROM: `WWF No Mercy (USA) (Rev-A).z64` (CRC32 `BACEEA13`).
Bank: FileTable @ `0x16C31D8`, FirstFile `0x1BD150`, file IDs **1-based** (game-exact W3c correction — FUN_80003ab0/FUN_80003bd0; the old `0x16C3238`/`0x1BD1B0` 0-based window read game file fid+0x19 spliced at +0x60, see `docs/anim/AKI-BAKE-ROCK-2026-10-21.md` W3b Finding 1). File IDs **`0x2DD9`–`0x4473`** = **5,787 clips**. The full bank was re-extracted 2026-11-19 with the W3c-corrected decode and verified (exact 4+98N lengths on all clips; Toki2 frame rule holds on 95%+; the 11 Rock clips are byte-identical to the W3c re-extraction; stance control 0x2DD9 reproduces the W3c smoothness numbers exactly). The true bank end is 0x4473, not 0x445A — the old end was an artifact of the buggy window: files 0x445B..0x4473 all fit the layout and satisfy the Toki2 rule, with a hard break at 0x4474.
Tool: `../tools/extract_all_anims.py` (decodes with `anim_extract.py` logic).

Note: prior docs said "~1,360 clips" — that count came from a survey capped
at file ID `0x3400`. The bank actually runs to `0x4473`; every file in the
extended range parses as AkiAnimation (`4 + N*98` bytes) and decodes to
plausible motion (verified smooth joint deltas on spot checks across the
range, including the extended 0x445B..0x4473 clips).

## Layout

- `clips/anim_XXXX.npy` — one NumPy file per clip (`XXXX` = hex file ID).
  Array: **int16, shape (nframes, 26, 3)**.
- `manifest.json` — joint order/kinds, per-clip `file_id`, `toki2` header,
  `nframes`, `kind` (`system` | `move`), and `anim_id` for move clips.

## Joint order (fixed, 26 entries)

Index 0–25, kinds PR = PivotRotation, OM = OverallMovement, MV = MovementXYZ:

```
0 Pelvis (PR)            9 UpperLeftLeg (PR)      18 UpperRightLeg (PR)
1 OverallMovement (OM)  10 LeftLegMovement (MV)  19 RightLegMovement (MV)
2 LowerAb (PR)          11 LeftFoot (PR)          20 RightFoot (PR)
3 LowerAbMovement (MV)  12 LeftHand (PR)         21 LowerRightArm (PR)
4 UpperBody (PR)        13 LeftFingers (PR)       22 RightHand (PR)
5 UpperBodyMovement(MV) 14 LowerLeftArm (PR)     23 RightFingers (PR)
6 Neck (PR)             15 UpperLeftArm (PR)      24 UpperRightArm (PR)
7 Head (PR)             16 LeftArmMovement (MV)   25 RightArmMovement (MV)
8 LowerLeftLeg (PR)     17 LowerRightLeg (PR)
```

(Full list with indices is in `manifest.json["joints"]`.)

## Channel semantics per joint kind

- **PR** (PivotRotation): `[pivot_x, rotation, pivot_z]` — packed `[PivotX s12][Rotation u10][PivotZ s10]` (W3b Finding 2; the old 12/8/12 split truncated rotation and corrupted PivotZ)
  - `pivot_x`: signed 12-bit fixed-point pivot offset
  - `rotation`: unsigned 10-bit, 1024 = full turn
  - `pivot_z`: signed 10-bit pivot offset
- **OM** (OverallMovement): `[overall_x, overall_y, overall_z]`
  - root/body translation: 12-bit signed X/Z, 8-bit unsigned Y
- **MV** (MovementXYZ): `[move_x, move_y, move_z]`
  - raw u8 triplets (joint-relative offsets; AKI-specific scale)

## Clip kinds

- `system` (`0x2DD9`–`0x3321`, 1,353 clips): stances, walks, entrances,
  taunts, getups, referee/misc motion.
- `move` (`0x3322`–`0x4473`, 4,434 clips): grapple/strike/throw animations.
  Per VPWStudio `MenuItems_Moves.cs`, a move's `AnimID` = `file_id − 0x3322`,
  so `manifest.json`'s `anim_id` is the key that joins a move-table entry to
  its clip (see `docs/ANIMATION-ISOLATION.md` §6).

## Retargeting

See `AKI-TEKKEN3-RETARGET.md`: `aki_to_tekken3.py` maps the 26 AKI joints to
a Tekken skeleton and converts the u10 rotations to Euler angles (v1 proven on
King; v3 uses the corrected u10 channel with period-1024 unwrap — see the W3c
addendum in docs/anim/AKI-BAKE-ROCK-2026-10-21.md). These NPY files are the direct input to that pipeline — no ROM needed
downstream.

# WWF No Mercy — Animation isolation status (ROM-verified)

Source ROM: `WWF No Mercy (USA) (Rev-A).z64` (CRC32 `BACEEA13`).
Helpers: `../tools/anim_extract.py` (keyframe bank),
`../tools/caw_parse.py` (tables). All offsets are ROM file offsets.

## 1. KEYFRAME BANK — ISOLATED (2026-10-13)

Animations live in the ROM **FileTable** at `0x16C3238` (19,462 entries;
each entry = u32 BE `(location & 0xFFFFFFFE) | encoded-bit`; file data starts
at `FirstFile = 0x1BD1B0`; encoded files are Asmik-LZSS). Locations confirmed
against AKI-Club/VPWStudio `DefaultGameData.cs` (NoMercy_NTSC_U_11 = our
Rev-A):

- `FirstAnimationFileID = 0x2DD9`, `FirstMoveAnimationID = 0x3322`
  (`MoveAnimationFileID = 0x01F0`, `MoveDamageFileID = 0x01EF`).
- Files `0x2DD9`–`0x335F` (~1,360 files) all parse as animations:
  frame counts 1–123 (mode 13), sizes `4 + N*98` exactly.
- **AkiAnimation format** (VPWStudio `AkiAnimation.cs`): 4-byte `Toki2`
  header, then N × **0x62 (98)-byte frames**. Each frame = 19×
  `PivotRotation` (4 B: 12-bit pivot X, s8 rotation, 12-bit pivot Z,
  packed 3-2-3) + 1× `OverallMovementXYZ` (4 B, same packing) + 6×
  `MovementXYZ` (3 B), in fixed joint order: Pelvis, OverallMovement,
  LowerAb, LowerAbMovement, UpperBody, UpperBodyMovement, Neck, Head,
  LowerLeftLeg, UpperLeftLeg, LeftLegMovement, LeftFoot, LeftHand,
  LeftFingers, LowerLeftArm, UpperLeftArm, LeftArmMovement, LowerRightLeg,
  UpperRightLeg, RightLegMovement, RightFoot, LowerRightArm, RightHand,
  RightFingers, UpperRightArm, RightArmMovement.
- Verified: file `0x2DD9` (13 f) decodes to a smooth lunge (pelvis rot
  −39°…+121°, overall X −864…+1); move anims (`0x3322`+) decode with
  snappier deltas, as expected for grapples.
- **Move → animation linkage** (VPWStudio `MenuItems_Moves.cs`): move menu
  entries carry `AnimID` = animation file ID **− 0x3322**
  ("animation ID (-3322)", 3322 presumed hex), plus `RepeatAnimID`.

## 2. CORRECTION — pointer table `@0x13E4A0` is a move-category string table

The earlier note ("10-ptr move-data index → ovl_c ROM 0xF4930") was **wrong**:
it used the wrong overlay context. Overlays B/C/D all load at vram
`0x80106760`, so a vram pointer resolves differently per overlay. The table
sits at ROM `0x13E4A0`, which is inside **ovl_d**'s ROM range
(`0xFD250`–`0x144BE0`, see §4) — so under ovl_d the 10 pointers
(`0x8014CD5C`…`0x8014CD00`, stored **descending**) resolve to ROM
`0x1437F0`+ and land exactly on 10 UI strings:

`Grappling`, `Standing`, `Running`, `Ground`, `Turnbuckle`, `Ringside`,
`Apron`, `Irish Whip`, `Taunt`, `Double Team` (followed by `Favorite:`,
`%d`, `best`). This is the **move-list category name table** for the
move-assignment UI (ovl_d). The pointers occur nowhere else in ROM —
consumed via computed addressing at runtime.

## 3. Move database (ovl_c region)

- Move records at `0xF4730`+ are real: `04 00 [u8 idx ×4][u32 LE p1]
  [u16 LE p2] FF FF` (14 B) interleaved with `04 <sub> <params>` records
  (`04 4B 08 00 FE 50 VV VV`, `04 4A`, `04 5F`, `04 5E`, `04 60`, `04 5C`,
  `04 1F`, `04 20`, `04 24`, `04 64`, `04 62`, `04 1C/1D`, `04 77–7A` …).
- **Move DB index table at `0xF5BF8`**: 40 entries of
  `(u32 BE move-record ptr, u32 LE count)` — each entry points at the first
  move record of a run and gives its length (targets land back in the
  `0xF3ACC`+ record bank, e.g. `0x8014BE9C,cnt=2` → ROM `0xF3ACC`).
  The move bank proper spans roughly `0xF2390`–`0xF6390` (high `04 xx` /
  `FF FF` density, entropy ~4.4–5.1).
- Second pointer block at `0x13E530` (ovl_d context): `0x8014D504` →
  `"No Data"` string, zeros, `0x8014D5C4` → `" "`, `u32 1`, then a u16
  index remap table (`00 04 00 04 00 03 …`) — move-slot UI data, not
  move attributes.

## 4. Overlay DMA table — `@0x539A0` (36-byte entries)

`[u32 rom_start][u32 rom_end]` + vram words. True overlay ROM ranges
(**larger than recomp's dump.toml** — data sections included):

| ovl | ROM range | size |
|-----|-----------|------|
| a | `0x57310`–`0x81210` | 0x29F00 |
| b | `0x81210`–`0xAE390` | 0x2C180 |
| c | `0xAE390`–`0xFD250` | 0x4EEC0 |
| d | `0xFD250`–`0x144BE0` | 0x47890 |
| e | `0x144BE0`–`0x1BD150` | 0x78670 |

All of B/C/D share vram base `0x80106760` — vram pointers must be resolved
in the correct overlay context (§2 was the lesson).

## 5. recomp/syms cross-reference

- `recomp/syms/dump.toml`: 7 sections; function symbols near the table's
  neighborhood are all unnamed (`func_8013D630`, …). No animation-named
  symbols in `extra_funcs.txt` / `stub_candidates.txt`. Cross-ref remains a
  dead end until the decomp names those functions — but it is no longer
  needed for animation extraction (§1).

## 6. What this unblocks for Western Heart

- **Full AKI animation library extracted**: ~1,360 clips, joint-level
  keyframes, machine-readable via `tools/anim_extract.py` (`info` /
  `json` / `survey`). Next step: retarget onto Tekken skeletons (same
  pattern as the working YANM→Tekken3 path — map the 19 AKI joints to
  Tekken bones, convert s8 rotations to Euler).
- Move DB index (40 runs) + move records give the move→clip structure;
  per-move `AnimID` linkage documented by VPWStudio.
- OPEN: Toki2 byte semantics; per-wrestler vs shared clip assignment;
  which clips the entrances use.

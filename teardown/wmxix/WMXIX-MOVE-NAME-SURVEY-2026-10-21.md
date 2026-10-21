# WMXIX BY-MOVE-NAME SURVEY — 2026-10-21 (gap-closure W4)

Owner hypothesis (2026-10-21 08:19 CDT): WMXIX probably indexes its moves
BY MOVE NAME, not by wrestler name — re-survey WMXIX by move names
(Rock Bottom, uranage, People's Elbow…) for CornerStone's Rock set.

## VERDICT — PARTIALLY CONFIRMED, in a sharper form than stated

- **Move names DO exist in WMXIX as data — in two places no prior survey
  searched:**
  1. `//menu/menu.mpq` holds per-wrestler profile blocks naming each
     wrestler's special moves by slot category — **99 named specials across
     45 wrestlers** (Appendix B). The Rock's are: **Rock Bottom**
     [Front Grapple], **People's Elbow** [Upper Down Grapple Facing Up],
     **People's Spine Buster** [Irish Whip Grapple].
  2. `//Entrance/EMotName.dat` is a code→name table (**177 pairs**) for the
     A/B/C/D motion codes: `A002 = ROCK`, `C000 = ROCK`, `D105 = ROCK_01`,
     `D106 = ROCK_02`, plus generic labels (TAUNT_01…, WALK_01…, NEUTRAL).
- **The animation FILES are indexed by those codes, not by name strings** —
  and for the loose `//ringmotion/*.yag` set the codes are **wrestler-keyed**
  (they are the entrance motions; provenance `ringmotion/cnv.bat`:
  Nyujo = entrance, per `teardown/wwe-wrestlemania-xix/docs/WMXIX-TEARDOWN.md`).
  So the null is also partly true: the index is numeric codes; the *name
  tables* are what make wrestlers and moves identifiable.
- **THE ROCK IS IDENTIFIED IN WMXIX — two of his clips were already decoded
  and sitting in this library unlabeled:**
  - `ML-A002-0A` = **A002 ROCK — The Rock's (single) entrance**
    (`ringmotion/a002_0a.yag`, 27,996 B, decoded est. 33.856 s)
  - `ML-C000-0A` = **C000 ROCK — trio/stable entrance variant**
    (`ringmotion/c000_0a.yag`, 68,876 B)
  - Mapping fragment: `moveset-library/movesets/rock-moves-wmxix.json`.
- **115 of the 170 decoded ringmotion clips are now name-mapped** via
  EMotName (Appendix A). The prior "all 169 moves are provisional grapple
  placeholders" framing in `moveset-library/movesets/WMXIX-MOVES.json` is
  superseded for these clips: they are **entrance/taunt/win motions**, not
  gameplay grapples. (That file was NOT edited by this lane — flagged here
  for central integration.)
- **What is still NOT identified: the gameplay animations for Rock Bottom /
  People's Elbow / People's Spine Buster.** Gameplay grapple/strike
  animations live inside the `//motion/*.mpc` YANM packages
  (`move.mpc` alone carries 1,905 YANM markers; `common.mpc` 1,587) under a
  numeric container index with **no name strings inside** (strings scan =
  YANM/POF0/DATA markers only). The name→clip mapping for gameplay moves is
  an open decode item. **No Rock Bottom clip is claimed in this survey.**

## Method

Existing tools/data only, no hand-rolled format guessing:

- Read prior checkpoints (`extract-wmxix.json`, `wh-wmxix-100*.json`,
  `wmxix-100-retail*.json`, `wmxix-yobj-dol-recordwriter.json`) for data
  locations; surveyed the decoded libraries on GitHub main
  (`WMXIX-MOVES.json`, `WMXIX-CLIP-INDEX.json`, `atr_all_events.json`,
  `teardown/wmxix/TEARDOWN.md`, `docs/WMXIX-FILE-LISTING.txt`,
  `docs/WMXIX-TEARDOWN.md`).
- Targeted range pulls from release `wmxix-iso-v1` using the repo's own
  range-reader pattern (`teardown/wwe-wrestlemania-xix/tools/wmxix_range_iso.py`):
  ISO header, `main.dol`, `//menu/menu.mpq`, `//motion/move.mpc`,
  `//motion/common.mpc`, `//Entrance/{EMotName,CamName,Defwres,EffName}.dat`,
  `//tutorial/menu/lesson_text1-4.tutmenumsg`. Only the bytes needed were
  pulled (~45 MB total) — disk stayed at 90%.
- **Release layout note (measured, corrects the range tool's header):** the
  current `wmxix-iso-v1` assets are `part_00` (524,288,000 B, starts with
  the GW9E78 ISO header) + `part_aa` (524,288,000 B) + `part_ab`
  (411,402,240 B) = 1,459,978,240 B. The old tool's "part_00 is a stale
  duplicate" warning no longer applies. Layout proven: bytes at ISO
  0x5470198C (`//viewer/hhh.ymg`) read `YOBJ` magic under this layout, and
  the FST at 0x362F00 / DOL at 0x1F700 from the ISO header parse cleanly.

## Evidence — surfaces searched

| Surface | File / identifier | Result |
|---|---|---|
| FST file/dir naming | `docs/WMXIX-FILE-LISTING.txt` — 4,222 files | **0 move-name hits.** All gameplay paths are numeric (`ringmotion/a002_0a.yag`, `model/wrestler/000_0.ymg`). Only word-names are CAW body-part dirs (`edit_data/MODEL/Man/Elbow/…`, `Knee/…`, `Face/…`) — not moves. Searched: rock, bottom, uranage, spinebuster, sharpshooter, samoan, clothesline, bulldog, suplex, powerslam, neckbreaker, backbreaker, piledriver, ddt, peoples — all 0 (elbow = 42 CAW part hits only). |
| DOL string tables | `main.dol` (ISO 0x1F700, 3,422,208 B pulled) — ASCII + UTF-16BE/LE + Shift-JIS scans | **No move names.** No `Rock`, no suplex/grapple/slam at all. Strings = stage names (CONSTRUCTION SITE, SHOPPING MALL, PARKING LOT, WAREHOUSE, WRESTLEMANIA XIX), file paths (`motion/move.mpc`, `menu/menu.mpq`, …), debug text. |
| Decoded move library | `moveset-library/movesets/WMXIX-MOVES.json`, `moveset-library/animations/WMXIX-CLIP-INDEX.json` | 0 hits for rock/people/elbow/uranage/sharpshooter/spinebuster/ddt/samoan/taunt — confirms the prior survey's negative **for these two files only**. |
| .atr event records | `teardown/wmxix/atr_all_events.json` (242,384 B) | 0 hits (rock/elbow/ddt). .atr = numeric event records. |
| YANM packages | `//motion/move.mpc` (8,183,296 B @ ISO 0x105925CC), `//motion/common.mpc` (4,396,640 B @ 0x0FB6CF8C) | Binary YANM containers (1,905 / 1,587 YANM markers). Strings = `YANM`/`POF0`/`DATA` markers only — **no names inside**. This is where gameplay move animations physically live, under a numeric index. |
| Tutorial text | `//tutorial/menu/lesson_text1-4.tutmenumsg` | Generic category prose only ("Light Front Turnbuckle Grapple", "Irish Whip Strike"…) — no named moves, no wrestler names. |
| Entrance name table | `//Entrance/EMotName.dat` (11,360 B @ ISO 0x08F38000, magic EDTN) | **HIT — 177 code→name pairs** (A/B/C/D series). Rock: A002 ROCK, C000 ROCK, D105 ROCK_01, D106 ROCK_02. Full dump pattern in Appendix A. |
| Entrance wrestler table | `//Entrance/Defwres.dat` (9,248 B @ ISO 0x08F10000, magic EDDR; 0x30 header + 128 B records) | **HIT — wrestler-keyed motion assignment.** THE ROCK record @ file offset 0xB0: codes ASCII `A0020000C000D106` = A002 (single entrance) / no B / C000 (trio entrance) / D106 = ROCK_02 (D-motion). Same record format for all 71 wrestlers/teams/CAW presets. |
| Entrance camera/effect names | `//Entrance/CamName.dat` (EDCN), `EffName.dat` | Camera/effect labels only (GENERAL_01, RAMP_CAM, TAKER_RUMBLE_CAM…) — no moves. |
| Menu/profile text | `//menu/menu.mpq` (29,953,536 B @ ISO 0x093E8460) | **HIT — the move-name vocabulary.** Per-wrestler profile blocks @ 0x5B52B–0x62500: 45 wrestlers, **99 named specials** with slot categories (Appendix B). Each special name occurs exactly once (Stone Cold Stunner ×2: Austin + Vince McMahon) — this is a per-wrestler specials table, not a separate master list; no second copy exists in the archive's readable text. |

## The Rock in WMXIX — complete findings

| Wanted | WMXIX data | Status |
|---|---|---|
| Rock Bottom | Named in menu.mpq profile: `[Front Grapple]` @ 0x5B6EF, name `Rock Bottom` @ 0x5B6FF | Name + slot CONFIRMED. Animation NOT identified (inside .mpc packages, numeric index). Would feed the same CornerStone slot as No Mercy `mk:MK-1240`. |
| People's Elbow | `[Upper Down Grapple Facing Up]` @ 0x5B70F, name @ 0x5B72E | Name + slot CONFIRMED. Animation NOT identified. Would feed `mk:MK-2843`'s slot. (Vince McMahon's profile also lists People's Elbow @ 0x60984.) |
| People's Spine Buster | `[Irish Whip Grapple]` @ 0x5B741, name @ 0x5B756 | Name + slot CONFIRMED. Animation NOT identified. WMXIX's name for the Rock Spinebuster class — would feed `mk:MK-1885`'s slot. |
| Entrance (single) | EMotName A002 = ROCK; Defwres A-field = A002 | **IDENTIFIED + DECODED:** `ringmotion/a002_0a.yag` (ISO 0x1132EE30, 27,996 B; .atr 36 B @ 0x1132EE0C) = `ML-A002-0A`, `teardown/wmxix/animations/a002_0a.json`, est. 33.856 s, 29 tracks. |
| Entrance (trio) | EMotName C000 = ROCK; Defwres C-field = C000 | **IDENTIFIED + DECODED:** `ringmotion/c000_0a.yag` (ISO 0x1154CC28, 68,876 B; .atr 1,028 B @ 0x1154C824) = `ML-C000-0A`, `teardown/wmxix/animations/c000_0a.json`, est. 173.244 s (decoder estimate), 29 tracks. |
| ROCK_01 / ROCK_02 (D-motions) | EMotName D105 = ROCK_01, D106 = ROCK_02; Defwres assigns D106 to The Rock (Jericho shares D106) | Named + assigned, but **no `ringmotion/d105|d106` file exists** — the D-series animation source package is not yet decoded/located. |
| uranage (by that name) | — | **No hit anywhere.** Rock Bottom is the uranage-class throw; WMXIX names it Rock Bottom only. |
| Samoan drop, floatover DDT, clothesline (Rock) | — | Not among The Rock's three named WMXIX specials; no Rock attribution in any searched surface. |
| Sharpshooter | menu.mpq @ 0x61F66 | Belongs to **LANCE STORM**'s profile ([Lower Down Grapple Facing Up]), not The Rock's, in WMXIX data. |

## What the A/B/C/D codes are (measured from EMotName + Defwres)

- **A-series** (`a000-a033` in ringmotion): single-wrestler entrances +
  generic TAUNT_xx slots. A002 = ROCK.
- **B-series** (`b000-b022`): tag-team entrances (B008 = HBK per EMotName).
  b013/b017 exist as files but have blank EMotName names.
- **C-series**: C000-C017 = trio/stable entrances (C000 = ROCK);
  C100-C147 = 48 files with **no EMotName entries** (open: second entrance
  set?); C200-C228 + C400-C403 = win/taunt motions keyed to wrestlers
  (C203 = TAKER, C224 = TAKER BIKE…).
- **D-series**: basic motions (D000 NEUTRAL, D100-D104+ WALK_xx,
  RUN_01/02) + wrestler-named motions (D105 ROCK_01, D106 ROCK_02,
  D107 AUSTIN, D108 TRIPLE H…). Only d000, d100-d103, d107 exist as
  ringmotion files.

## Remaining unknowns (honest)

1. **Gameplay name→clip mapping** — which YANM clips inside
   `motion/move.mpc` / `common*.mpc` (+ `common_1/2/3.mpc`) are Rock Bottom,
   People's Elbow, People's Spine Buster. Needs .mpc container decode +
   a per-wrestler moveset assignment table (the `motion/sheet/91xx.yad`
   sheets — 41 files — and `motion/win/91xx_00A.tmp` — 64 files — are
   numeric-keyed candidates not yet decoded).
2. **D-series animation source** for D105/D106 (ROCK_01/ROCK_02).
3. **C100-C147 identity** (48 decoded clips, no EMotName names).
4. Per-clip identity for the 55 ringmotion clips EMotName leaves blank.
5. `WMXIX-MOVES.json` still labels the 169 clips as grapples — central
   integration should re-label the 115 name-mapped clips as
   entrance/taunt/win motions per Appendix A (this lane did not edit it).

### Appendix A - ringmotion clip -> EMotName name (115 of 170 mapped)

| Clip file | Code | EMotName label | Canon ID |
|---|---|---|---|
| a000_0a.yag | A000 | TAKER | ML-A000-0A |
| a001_0a.yag | A001 | TRIPLE H | ML-A001-0A |
| a002_0a.yag | A002 | ROCK | ML-A002-0A |
| a003_0a.yag | A003 | JERICHO | ML-A003-0A |
| a004_0a.yag | A004 | TAUNT_01 | ML-A004-0A |
| a005_0a.yag | A005 | CHRISTIAN | ML-A005-0A |
| a006_0a.yag | A006 | TAUNT_02 | ML-A006-0A |
| a007_0a.yag | A007 | TAUNT_03 | ML-A007-0A |
| a008_0a.yag | A008 | BUBBA | ML-A008-0A |
| a009_0a.yag | A009 | TAUNT_04 | ML-A009-0A |
| a010_0a.yag | A010 | TAUNT_05 | ML-A010-0A |
| a011_0a.yag | A011 | TAJIRI | ML-A011-0A |
| a012_0a.yag | A012 | TAUNT_06 | ML-A012-0A |
| a013_0a.yag | A013 | TAUNT_07 | ML-A013-0A |
| a014_0a.yag | A014 | TAUNT_08 | ML-A014-0A |
| a015_0a.yag | A015 | ORTON | ML-A015-0A |
| a016_0a.yag | A016 | CHAVO | ML-A016-0A |
| a017_0a.yag | A017 | TAUNT_09 | ML-A017-0A |
| a018_0a.yag | A018 | TAUNT_10 | ML-A018-0A |
| a019_0a.yag | A019 | TAUNT_11 | ML-A019-0A |
| a020_0a.yag | A020 | STEPHANIE | ML-A020-0A |
| a021_0a.yag | A021 | TAUNT_12 | ML-A021-0A |
| a022_0a.yag | A022 | TAUNT_13 | ML-A022-0A |
| a023_0a.yag | A023 | TAUNT_14 | ML-A023-0A |
| a024_0a.yag | A024 | TAUNT_15 | ML-A024-0A |
| a025_0a.yag | A025 | TAKER BIKE | ML-A025-0A |
| a026_0a.yag | A026 | FLAIR | ML-A026-0A |
| a027_0a.yag | A027 | GOLDUST | ML-A027-0A |
| a028_0a.yag | A028 | LANCE | ML-A028-0A |
| a029_0a.yag | A029 | TAUNT_16 | ML-A029-0A |
| a030_0a.yag | A030 | TAUNT_17 | ML-A030-0A |
| a031_0a.yag | A031 | TAUNT_18 | ML-A031-0A |
| a032_0a.yag | A032 | KANE | ML-A032-0A |
| a033_0a.yag | A033 | EDGE | ML-A033-0A |
| b000_0a.yag | B000 | ANGLE | ML-B000-0A |
| b001_0a.yag | B001 | JERICHO | ML-B001-0A |
| b002_0a.yag | B002 | BENOIT | ML-B002-0A |
| b003_0a.yag | B003 | CHRISTIAN | ML-B003-0A |
| b004_0a.yag | B004 | TAUNT_01 | ML-B004-0A |
| b005_0a.yag | B005 | TAUNT_02 | ML-B005-0A |
| b006_0a.yag | B006 | LITA | ML-B006-0A |
| b007_0a.yag | B007 | RVD_01 | ML-B007-0A |
| b008_0a.yag | B008 | HBK | ML-B008-0A |
| b009_0a.yag | B009 | TAUNT_03 | ML-B009-0A |
| b010_0a.yag | B010 | MYSTERIO | ML-B010-0A |
| b011_0a.yag | B011 | BOOKER T | ML-B011-0A |
| b012_0a.yag | B012 | TAUNT_04 | ML-B012-0A |
| b013_0a.yag | B013 | (no entry / blank) | ML-B013-0A |
| b014_0a.yag | B014 | AL SNOW | ML-B014-0A |
| b015_0a.yag | B015 | MATT | ML-B015-0A |
| b016_0a.yag | B016 | HOGAN | ML-B016-0A |
| b017_0a.yag | B017 | (no entry / blank) | ML-B017-0A |
| b018_0a.yag | B018 | TAKER BIKE | ML-B018-0A |
| b019_0a.yag | B019 | FLAIR | ML-B019-0A |
| b020_0a.yag | B020 | REGAL | ML-B020-0A |
| b021_0a.yag | B021 | TAUNT_05 | ML-B021-0A |
| b022_0a.yag | B022 | RVD_02 | ML-B022-0A |
| c000_0a.yag | C000 | ROCK | ML-C000-0A |
| c001_0a.yag | C001 | AUSTIN | ML-C001-0A |
| c002_0a.yag | C002 | ANGLE | ML-C002-0A |
| c003_0a.yag | C003 | JERICHO | ML-C003-0A |
| c004_0a.yag | C004 | BUBBA | ML-C004-0A |
| c005_0a.yag | C005 | REGAL | ML-C005-0A |
| c006_0a.yag | C006 | TAJIRI | ML-C006-0A |
| c007_0a.yag | C007 | BOOKER T | ML-C007-0A |
| c008_0a.yag | C008 | TAUNT_01 | ML-C008-0A |
| c009_0a.yag | C009 | VINCE | ML-C009-0A |
| c010_0a.yag | C010 | STEPHANIE | ML-C010-0A |
| c011_0a.yag | C011 | FLAIR | ML-C011-0A |
| c012_0a.yag | C012 | TAUNT_02 | ML-C012-0A |
| c013_0a.yag | C013 | TAUNT_03 | ML-C013-0A |
| c014_0a.yag | C014 | TAUNT_04 | ML-C014-0A |
| c015_0a.yag | C015 | TAUNT_05 | ML-C015-0A |
| c016_0a.yag | C016 | TAUNT_06 | ML-C016-0A |
| c017_0a.yag | C017 | TAUNT_07 | ML-C017-0A |
| c100_0a.yag | C100 | (no entry / blank) | ML-C100-0A |
| c101_0a.yag | C101 | (no entry / blank) | ML-C101-0A |
| c102_0a.yag | C102 | (no entry / blank) | ML-C102-0A |
| c103_0a.yag | C103 | (no entry / blank) | ML-C103-0A |
| c104_0a.yag | C104 | (no entry / blank) | ML-C104-0A |
| c105_0a.yag | C105 | (no entry / blank) | ML-C105-0A |
| c106_0a.yag | C106 | (no entry / blank) | ML-C106-0A |
| c107_0a.yag | C107 | (no entry / blank) | ML-C107-0A |
| c108_0a.yag | C108 | (no entry / blank) | ML-C108-0A |
| c109_0a.yag | C109 | (no entry / blank) | ML-C109-0A |
| c110_0a.yag | C110 | (no entry / blank) | ML-C110-0A |
| c111_0a.yag | C111 | (no entry / blank) | ML-C111-0A |
| c112_0a.yag | C112 | (no entry / blank) | ML-C112-0A |
| c113_0a.yag | C113 | (no entry / blank) | ML-C113-0A |
| c114_0a.yag | C114 | (no entry / blank) | ML-C114-0A |
| c115_0a.yag | C115 | (no entry / blank) | ML-C115-0A |
| c116_0a.yag | C116 | (no entry / blank) | ML-C116-0A |
| c117_0a.yag | C117 | (no entry / blank) | ML-C117-0A |
| c118_0a.yag | C118 | (no entry / blank) | ML-C118-0A |
| c119_0a.yag | C119 | (no entry / blank) | ML-C119-0A |
| c120_0a.yag | C120 | (no entry / blank) | ML-C120-0A |
| c121_0a.yag | C121 | (no entry / blank) | ML-C121-0A |
| c122_0a.yag | C122 | (no entry / blank) | ML-C122-0A |
| c123_0a.yag | C123 | (no entry / blank) | ML-C123-0A |
| c124_0a.yag | C124 | (no entry / blank) | ML-C124-0A |
| c125_0a.yag | C125 | (no entry / blank) | ML-C125-0A |
| c126_0a.yag | C126 | (no entry / blank) | ML-C126-0A |
| c127_0a.yag | C127 | (no entry / blank) | ML-C127-0A |
| c128_0a.yag | C128 | (no entry / blank) | ML-C128-0A |
| c129_0a.yag | C129 | (no entry / blank) | ML-C129-0A |
| c130_0a.yag | C130 | (no entry / blank) | ML-C130-0A |
| c131_0a.yag | C131 | (no entry / blank) | ML-C131-0A |
| c132_0a.yag | C132 | (no entry / blank) | ML-C132-0A |
| c133_0a.yag | C133 | (no entry / blank) | ML-C133-0A |
| c134_0a.yag | C134 | (no entry / blank) | ML-C134-0A |
| c135_0a.yag | C135 | (no entry / blank) | ML-C135-0A |
| c136_0a.yag | C136 | (no entry / blank) | ML-C136-0A |
| c137_0a.yag | C137 | (no entry / blank) | ML-C137-0A |
| c138_0a.yag | C138 | (no entry / blank) | ML-C138-0A |
| c138_0b.yag | C138 | (no entry / blank) | ML-C138-0A |
| c139_0a.yag | C139 | (no entry / blank) | ML-C139-0A |
| c140_0a.yag | C140 | (no entry / blank) | ML-C140-0A |
| c141_0a.yag | C141 | (no entry / blank) | ML-C141-0A |
| c142_0a.yag | C142 | (no entry / blank) | ML-C142-0A |
| c143_0a.yag | C143 | (no entry / blank) | ML-C143-0A |
| c144_0a.yag | C144 | (no entry / blank) | ML-C144-0A |
| c145_0a.yag | C145 | (no entry / blank) | ML-C145-0A |
| c146_0a.yag | C146 | (no entry / blank) | ML-C146-0A |
| c147_0a.yag | C147 | (no entry / blank) | ML-C147-0A |
| c200_0.yag | C200 | TAUNT_08 | ML-C200-0A |
| c200_0a.yag | C200 | TAUNT_08 | ML-C200-0A |
| c200_1a.yag | C200 | TAUNT_08 | ML-C200-0A |
| c200_2a.yag | C200 | TAUNT_08 | ML-C200-0A |
| c201_0a.yag | C201 | TAUNT_09 | ML-C201-0A |
| c202_0a.yag | C202 | TAUNT_10 | ML-C202-0A |
| c203_0a.yag | C203 | TAKER | ML-C203-0A |
| c204_0a.yag | C204 | KANE | ML-C204-0A |
| c205_0a.yag | C205 | BENOIT | ML-C205-0A |
| c206_0a.yag | C206 | TAUNT_11 | ML-C206-0A |
| c207_0a.yag | C207 | CHRISTIAN | ML-C207-0A |
| c208_0a.yag | C208 | TAUNT_12 | ML-C208-0A |
| c209_0a.yag | C209 | TAUNT_13 | ML-C209-0A |
| c210_0a.yag | C210 | LITA | ML-C210-0A |
| c211_0a.yag | C211 | D-VON | ML-C211-0A |
| c212_0a.yag | C212 | RVD_01 | ML-C212-0A |
| c213_0a.yag | C213 | TAUNT_14 | ML-C213-0A |
| c214_0a.yag | C214 | TAUNT_15 | ML-C214-0A |
| c215_0a.yag | C215 | TAUNT_16 | ML-C215-0A |
| c216_0a.yag | C216 | TAUNT_17 | ML-C216-0A |
| c217_0a.yag | C217 | TEST | ML-C217-0A |
| c218_0a.yag | C218 | BIG SHOW | ML-C218-0A |
| c219_0a.yag | C219 | TAUNT_18 | ML-C219-0A |
| c220_0a.yag | C220 | TAUNT_19 | ML-C220-0A |
| c221_0a.yag | C221 | TAUNT_20 | ML-C221-0A |
| c222_0a.yag | C222 | TAUNT_21 | ML-C222-0A |
| c223_0a.yag | C223 | TAUNT_22 | ML-C223-0A |
| c224_0a.yag | C224 | TAKER BIKE | ML-C224-0A |
| c224_1a.yag | C224 | TAKER BIKE | ML-C224-0A |
| c225_0a.yag | C225 | RIKISHI | ML-C225-0A |
| c226_0a.yag | C226 | TAUNT_23 | ML-C226-0A |
| c227_0a.yag | C227 | LANCE | ML-C227-0A |
| c228_0a.yag | C228 | RVD_02 | ML-C228-0A |
| c400_0a.yag | C400 | TRIPLE H | ML-C400-0A |
| c401_0a.yag | C401 | TAUNT_24 | ML-C401-0A |
| c402_0a.yag | C402 | TAUNT_25 | ML-C402-0A |
| c403_0a.yag | C403 | TAUNT_26 | ML-C403-0A |
| d000_0a.yag | D000 | NEUTRAL | ML-D000-0A |
| d100_0a.yag | D100 | WALK_01 | ML-D100-0A |
| d101_0a.yag | D101 | (no entry / blank) | ML-D101-0A |
| d102_0a.yag | D102 | WALK_02 | ML-D102-0A |
| d103_0a.yag | D103 | WALK_03 | ML-D103-0A |
| d107_0a.yag | D107 | AUSTIN | ML-D107-0A |

### Appendix B - menu.mpq profile specials (99 entries, 45 wrestlers)

| Wrestler | Slot category | Move name | menu.mpq offset (category) |
|---|---|---|---|
| THE ROCK | Front Grapple | Rock Bottom | 0x5b6ef |
| THE ROCK | Upper Down Grapple Facing Up | People's Elbow | 0x5b70f |
| THE ROCK | Irish Whip Grapple | People's Spine Buster | 0x5b741 |
| TRIPLE H | Front Grapple | Pedigree | 0x5b990 |
| TRIPLE H | Rear Grapple | Reverse Suplex | 0x5b9ad |
| HULK HOGAN | Front Grapple | Hulk Up Combination | 0x5bcc9 |
| HULK HOGAN | Running Strike | Axe Bomber | 0x5bcf1 |
| UNDERTAKER | Front Grapple | Last Ride | 0x5bf2c |
| UNDERTAKER | Rear Grapple | Dragon Sleeper | 0x5bf4a |
| UNDERTAKER | Front Grapple | Tombstone Pile Driver | 0x5bf6c |
| KURT ANGLE | Front Grapple | Angle Slam | 0x5c1f5 |
| KURT ANGLE | Lower Down Grapple Facing Down | Ankle Lock | 0x5c214 |
| KURT ANGLE | Rear Grapple | Multiple German Suplex | 0x5c244 |
| BOOKER T | Attack from Turnbuckle | Rolling Guillotine Leg Drop | 0x5c4e4 |
| ROB VAN DAM | Attack from Turnbuckle | Five Star Frog Splash | 0x5c703 |
| ROB VAN DAM | Weapon Attack | Van Daminator | 0x5c736 |
| BROCK LESNAR | Front Grapple | F-5 | 0x5c956 |
| BROCK LESNAR | Attack from Turnbuckle | Shooting Star Splash | 0x5c96e |
| EDGE | Lower Down Grapple Facing Up | Edgecator | 0x5cbf0 |
| EDGE | Rear Grapple | Edge O'matic | 0x5cc1d |
| STACY KEIBLER | Front Grapple | Lip Lock | 0x5ce35 |
| STACY KEIBLER | Rear Grapple | Golden Hip | 0x5ce52 |
| REY MYSTERIO | Springboard Attack | 619 | 0x5d059 |
| REY MYSTERIO | Attack from Top Rope | West Coast Pop | 0x5d076 |
| REY MYSTERIO | Rear Grapple | Mysterio Rana | 0x5d0a0 |
| CHRIS JERICHO | Front Grapple | Walls of Jericho | 0x5d2f7 |
| CHRIS JERICHO | Springboard Attack | Lionsault | 0x5d31c |
| CHRIS JERICHO | Rear Grapple | Flashback | 0x5d33f |
| CHRIS BENOIT | Front Grapple | Crippler Crossface | 0x5d5f5 |
| CHRIS BENOIT | Attack from Turnbuckle | Diving Headbutt | 0x5d61c |
| CHRIS BENOIT | Rear Grapple | Multiple German Suplex | 0x5d649 |
| TRISH STRATUS | Front Turnbuckle Grapple | Stratusphere | 0x5d8b5 |
| TRISH STRATUS | Rear Grapple | High Angle Rolling Clutch Pin | 0x5d8e1 |
| KANE | Rear Grapple | Reverse Suplex | 0x5daf7 |
| BUBBA RAY DUDLEY | Rear Grapple | Bubba Bomb | 0x5dd42 |
| BUBBA RAY DUDLEY | Double Team Grapple | Dudley Death Drop | 0x5dd60 |
| BUBBA RAY DUDLEY | Front Grapple | Diamond Cutter | 0x5dd8c |
| SHAWN MICHAELS | Front Grapple | Sweet Chin Music | 0x5e00b |
| SHAWN MICHAELS | Attack from Turnbuckle | Diving Elbow Drop | 0x5e030 |
| SHAWN MICHAELS | Rear Grapple | Japanese Rolling Clutch Pin | 0x5e05f |
| EDDIE GUERRERO | Attack from Turnbuckle | Frog Splash | 0x5e34e |
| EDDIE GUERRERO | Lower Down Grapple Facing Down | Lasso from El Paso | 0x5e377 |
| EDDIE GUERRERO | Front Grapple | Splash Mountain Bomb Pin | 0x5e3af |
| BIG SHOW | Rear Grapple | Eye of the Hurricane | 0x5e5f3 |
| MATT HARDY | Attack from Turnbuckle | Mattitude Guillotine Leg Drop | 0x5e8ab |
| MATT HARDY | Rear Grapple | Flashback | 0x5e8e6 |
| JEFF HARDY | Attack from Turnbuckle | Swanton Bomb | 0x5eb3b |
| JEFF HARDY | Front Grapple | Twist of Fate | 0x5eb65 |
| JEFF HARDY | Rear Grapple | High Angle Rolling Clutch Pin | 0x5eb87 |
| LITA | Front Grapple | Twist of Fate | 0x5edf6 |
| LITA | Rear Grapple | Spinout Power Bomb Pin | 0x5ee18 |
| RIC FLAIR | Front Grapple | Nature Boy Special | 0x5f0ad |
| RIC FLAIR | Rear Grapple | Reverse Suplex | 0x5f0d4 |
| SCOTT STEINER | Upper Down Grapple Facing Down | Steiner Recliner | 0x5f33d |
| SCOTT STEINER | Front Grapple | Steiner Screw Driver | 0x5f373 |
| SCOTT STEINER | Rear Grapple | Tilt Slam | 0x5f39c |
| CHRISTIAN | Rear Grapple | Unprettier | 0x5f575 |
| CHRISTIAN | Front Grapple | Gordbuster | 0x5f593 |
| D-VON DUDLEY | Double Team Grapple | Dudley Death Drop | 0x5f7ee |
| D-VON DUDLEY | Front Grapple | Power Bomb | 0x5f81a |
| THE HURRICANE | Rear Grapple | Eye of the Hurricane | 0x5fa2a |
| BATISTA | Front Grapple | Sit Down Power Bomb | 0x5fc2d |
| BATISTA | Rear Grapple | Tilt Slam | 0x5fc55 |
| JOHN CENA | Front Grapple | Death Valley Driver | 0x5fe1f |
| JOHN CENA | Rear Grapple | Protoplex | 0x5fe47 |
| TORRIE WILSON | Rear Grapple | Japanese Rolling Clutch Pin | 0x6002e |
| VICTORIA | Front Grapple | Widow's Peak | 0x60210 |
| VICTORIA | Rear Grapple | Reverse DDT | 0x60231 |
| STEVE AUSTIN | Front Grapple | Stone Cold Stunner | 0x60425 |
| STEVE AUSTIN | Rear Grapple | Cobra Clutch | 0x6044c |
| GOLDUST | Front Turnbuckle Grapple | Shattered Dreams | 0x6069c |
| GOLDUST | Front Grapple | Curtain Call | 0x606cc |
| VINCE McMAHON | Front Grapple | Stone Cold Stunner | 0x6093e |
| VINCE McMAHON | Upper Down Grapple Facing Up | People's Elbow | 0x60965 |
| VINCE McMAHON | Side Down Grapple Facing Up | Running Leg Drop | 0x60997 |
| STEPHANIE McMAHON | Front Grapple | Full Swinging Slap | 0x60ba8 |
| STEPHANIE McMAHON | Rear Grapple | Grapevine Choke | 0x60bcf |
| STEPHANIE McMAHON | <[ WILLIAM REGAL  | Regal Stretch | 0x60c53 |
| WILLIAM REGAL | Front Grapple | Power of the Punch | 0x60df8 |
| DAWN MARIE | Rear Grapple | Reverse Momo Clutch Pin | 0x6102c |
| TAJIRI | Front Grapple | Buzzsaw Kick with Poisonmist | 0x6120a |
| TAJIRI | Rear Turnbuckle Grapple | Tarantula | 0x6123b |
| AL SNOW | Front Grapple | Snow Plow | 0x61413 |
| AL SNOW | Rear Grapple | Full Nelson Face Drop | 0x61431 |
| CHAVO GUERRERO | Front Grapple | Brainbuster | 0x61650 |
| CHAVO GUERRERO | Rear Grapple | High Angle Rolling Clutch Pin | 0x61670 |
| RANDY ORTON | Front Grapple | Diamond Cutter | 0x61887 |
| RANDY ORTON | Rear Grapple | German Suplex Pin | 0x618aa |
| CHRIS NOWINSKI | Front Grapple | Honor Roll | 0x61a7e |
| CHRIS NOWINSKI | Rear Grapple | Reverse DDT | 0x61a9d |
| TEST | Front Grapple | Sideswipe Falling Power Bomb | 0x61cc9 |
| TEST | Rear Grapple | Test Drive | 0x61cfa |
| LANCE STORM | Lower Down Grapple Facing Up | Sharpshooter | 0x61f47 |
| LANCE STORM | Front Grapple | Super Kick | 0x61f77 |
| RIKISHI | Rear Grapple | Full Nelson Slam | 0x621b5 |
| RIKISHI | Turnbuckle Lower Grapple | Stink Face | 0x621d9 |
| GOLDBERG | Front Grapple | Jack Hammer | 0x6240a |
| GOLDBERG | Running Strike | Spear | 0x6242a |
| GOLDBERG | Rear Grapple | Tilt Slam | 0x62445 |

EMotName pairs in order: 177

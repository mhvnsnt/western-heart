# VF5 PS3 motion inventory — proven present in the full dump (2026-11-21)

**Lane:** 1A — VF5 complete teardown
**Source archive:** `GAMES.rar` (3,686,456,692 B), reassembled from release
`vf5-ps3-v1` parts `vf5-500m.part_00`–`part_07` (mhvnsnt/western-heart).
**How verified (own-eyes, no 4.2 GB download, zero disk writes):** the RAR5
archive carries a QuickOpen file index in its tail. Streaming only the last
1,000,000 bytes of `vf5-500m.part_07` (HTTP Range) through grep returned
the file list (~1,221 entries). A read-only `7zz l` on the first 168 MB
(truncated part_00) independently confirmed the archive is the genuine
BLES00029 dump, RAR5, alphabetical filesystem order. The Oct 22 gap doc's
"may contain motion files, unverified" is now VERIFIED YES.

**Archive root:** `GAMES/BLES00029-[Virtua Fighter 5]/PS3_GAME/USRDIR/`
**USRDIR top-level counts (QuickOpen):** `rom/` 666, `lang/` 338,
`sound/` 78, `objset/` 60, `training/` 35, `ps3/` 13, `movie/` 7.

## The motion files — `USRDIR/rom/rob/` (all present)

Per-fighter motion archives (`mot_<ID>.farc`, 21 files):

| ID | Fighter | File |
|---|---|---|
| AKI | Akira | `mot_AKI.farc` |
| AKIXX | Akira (alt) | `mot_AKIXX.farc` |
| AOI | Aoi | `mot_AOI.farc` |
| BRA | Brad Burns — **Realizzt** | `mot_BRA.farc` |
| CMN | Common | `mot_CMN.farc` |
| DUR | Dural — **Zen base** | `mot_DUR.farc` |
| ENB | — | `mot_ENB.farc` |
| GOH | Goh Hinogami — **Kutz** | `mot_GOH.farc` |
| JAK | Jacky | `mot_JAK.farc` |
| JEF | Jeffry | `mot_JEF.farc` |
| KAG | Kage | `mot_KAG.farc` |
| LAU | Lau | `mot_LAU.farc` |
| LEI | Lei-Fei | `mot_LEI.farc` |
| LIO | Lion | `mot_LIO.farc` |
| MON | — | `mot_MON.farc` |
| MSK | — | `mot_MSK.farc` |
| PAI | Pai | `mot_PAI.farc` |
| SAR | Sarah | `mot_SAR.farc` |
| SHU | Shun | `mot_SHU.farc` |
| VAN | Vanessa | `mot_VAN.farc` |
| WOL | Wolf | `mot_WOL.farc` |

Plus: `mot_AUTH_<ID>.farc` ×18 (AKI, AOI, BRA, DUR, GOH, JAK, JEF, KAG,
LAU, LEI, LIO, MON, MSK, PAI, SAR, SHU, VAN, WOL),
`mot_TEST_DESIGN.farc`, `mot_TEST_ITEM.farc`.

Supporting motion files in `rom/rob/`:

- `mot_db.farc` — the motion database (every motion ID/name in the game;
  convert with DatabaseConverter → XML for the per-fighter inventory).
- `rob_mot_tbl.bin` — motion table.
- `ctrl_<ID>.bin` ×17 (AKI, AOI, BRA, GOH, JAK, JEF, KAG, LAU, LEI, LIO,
  MON, MSK, PAI, SAR, SHU, VAN, WOL — no `ctrl_CMN`, no `ctrl_DUR` in the
  listing as read).
- `mothead_<ID>.bin` ×19 (AKI, AOI, BRA, CMN, DUR, GOH, JAK, JEF, KAG, LAU,
  LEI, LIO, MON, MSK, PAI, SAR, SHU, VAN, WOL).

And the bone database: `USRDIR/rom/bone_data.bin` (present).

**Caveat:** this inventory is as-read from the QuickOpen window in the
last 1 MB of the archive. It is complete and self-consistent (every
fighter present in `mot_*.farc`), but the extraction lane must confirm it
with `7zz l` on the full reassembled RAR before running the tools.

## The four files the extraction lane needs first

1. `USRDIR/rom/rob/mot_GOH.farc` — Kutz
2. `USRDIR/rom/rob/mot_BRA.farc` — Realizzt
3. `USRDIR/rom/rob/mot_DUR.farc` — Zen base
4. `USRDIR/rom/rob/mot_db.farc` + `USRDIR/rom/bone_data.bin` — the
   databases MikuMikuLibrary needs to open/port the motions
   (`obj_db.bin` / `tex_db.bin` are already in release `vf5-ps3-v1`).

Toolchain (vendored): `tools/anim/vf5-mikumikulibrary/` — FarcPack extracts
the mot farcs; DatabaseConverter turns `mot_db.farc` into XML. Then map
mot_db names to the Goh/Brad/Dural move lists and convert to `wh-anim/1`
at `game/assets/anim/vf5/{goh,brad,dural}/`. Full run spec:
`docs/research/VF5-COMPLETE-TEARDOWN-20261121.md` ("The fork").

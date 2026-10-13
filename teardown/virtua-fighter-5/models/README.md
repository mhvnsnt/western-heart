# VF5 Extracted Character Models

7 priority fighters extracted from Virtua Fighter 5 PS3 (BLES00029).

**Character .farc archives** are on GitHub Release `vf5-ps3-v1`:
- `wol.farc` + `wolitm.farc` — Wolf Hawkfield (160 files)
- `kag.farc` + `kagitm.farc` — Kage-Maru (186 files)
- `aoi.farc` + `aoiitm.farc` — Aoi Umenokouji (156 files)
- `goh.farc` + `gohitm.farc` — Goh Hinogami (168 files)
- `shu.farc` + `shuitm.farc` — Shun Di (140 files)
- `lio.farc` + `lioitm.farc` — Lion Rafale (144 files)
- `van.farc` + `vanitm.farc` — Vanessa Lewis (176 files)

Each `.farc` contains decompressed:
- `*_obj.bin` — model data (binary, needs chrrox 3ds Max script for import)
- `*_tex.bin` — texture data (use TXP.bms via QuickBMS)

**Extractor:** `../tools/farc_extract.py` — pure Python, handles FArC format
(magic + BE u32 entries + gzip payloads).

**Full game:** on GitHub Release `vf5-ps3-v1` (8× 500MB chunks).
Reassemble: `cat vf5-500m.part_* > vf5-ps3-games.rar`

**Note:** El Blaze and Eileen are NOT in base VF5 (added in VF5R/FS).
Jean Kujo and Taka-Arashi are FS-only.

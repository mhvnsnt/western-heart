# VF5 Extracted Character Models

Full 19-fighter roster extracted from Virtua Fighter 5 PS3 (BLES00029).

**Character .farc archives** are on GitHub Release `vf5-ps3-v1`:

| # | Fighter | Code | Body .farc | Item .farc | Inner files | Notes |
|---|---------|------|-----------|-----------|-------------|-------|
| 1 | Akira Yuki | aki | `aki.farc` | `akiitm.farc` | 176 | Bajiquan |
| 2 | Akira Yuki (alt) | akixx | `akixx.farc` | — | 2 | variant body (4.3MB uncompressed) |
| 3 | Pai Chan | pai | `pai.farc` | `paiitm.farc` | 152 | Ensei-Ken |
| 4 | Lau Chan | lau | `lau.farc` | `lauitm.farc` | 146 | Koen-Ken — biggest item pack (114MB uncompressed) |
| 5 | Wolf Hawkfield | wol | `wol.farc` | `wolitm.farc` | 160 | Pro Wrestling — HIGH priority |
| 6 | Jeffry McWild | jef | `jef.farc` | `jefitm.farc` | 162 | Pancratium |
| 7 | Kage-Maru | kag | `kag.farc` | `kagitm.farc` | 186 | Hagakure-ryu Jujutsu — HIGH priority, most files |
| 8 | Sarah Bryant | sar | `sar.farc` | `saritm.farc` | 158 | Martial Arts |
| 9 | Jacky Bryant | jak | `jak.farc` | `jakitm.farc` | 156 | Jeet Kune Do |
| 10 | Shun Di | shu | `shu.farc` | `shuitm.farc` | 140 | Drunken Kung Fu — HIGH priority |
| 11 | Lion Rafale | lio | `lio.farc` | `lioitm.farc` | 144 | Praying Mantis Kung Fu — HIGH priority |
| 12 | Aoi Umenokouji | aoi | `aoi.farc` | `aoiitm.farc` | 156 | Aiki-Jujutsu — HIGH priority |
| 13 | Lei-Fei | lei | `lei.farc` | `leiitm.farc` | 142 | Shaolin Kung Fu |
| 14 | Vanessa Lewis | van | `van.farc` | `vanitm.farc` | 176 | Vale Tudo — HIGH priority |
| 15 | Brad Burns | bra | `bra.farc` | `braitm.farc` | 156 | Kickboxing |
| 16 | Goh Hinogami | goh | `goh.farc` | `gohitm.farc` | 168 | Judo — HIGH priority |
| 17 | Eileen | mon | `mon.farc` | `monitm.farc` | 172 | Monkey Kung Fu (code `mon` = monkey) |
| 18 | El Blaze | msk | `msk.farc` | `mskitm.farc` | 164 | Lucha Libre (code `msk` = mask) |
| 19 | Dural (boss) | dur | `dur.farc` | `duritm.farc` | 26 | final boss, minimal item set |

**Shared/common archives** (also on `vf5-ps3-v1`):
- `itmcmn.farc` — common item data
- `effcmn.farc` — common effects
- `dbg.farc` / `test.farc` — debug/test assets
- `obj_db.bin` / `tex_db.bin` — object/texture databases

Each `*itm.farc` contains decompressed:
- `*_obj.bin` — model data (binary, needs chrrox 3ds Max script for import)
- `*_tex.bin` — texture data (use TXP.bms via QuickBMS)

**Note:** This PS3 dump IS the Ver.C revision — Eileen and El Blaze ARE present
(`mon`/`msk` farcs). They were arcade additions in Ver.C, not FS-only.
Jean Kujo and Taka-Arashi are FS-only and NOT in this dump.

**Extractor:** `../tools/farc_extract.py` — pure Python, handles FArC format
(magic + BE u32 entries + gzip payloads). Validated on all 79 objset farcs.

**Full game:** on GitHub Release `vf5-ps3-v1` (8× 500MB chunks).
Reassemble: `cat vf5-500m.part_* > vf5-ps3-games.rar`

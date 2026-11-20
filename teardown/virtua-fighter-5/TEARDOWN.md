# Virtua Fighter 5 — Teardown

**Game #7 for the Western Heart chimera build.** Owner-directed 2026-10-13.

## Source

| Item | Details |
|------|---------|
| **Title** | Virtua Fighter 5 (PS3, 2007) |
| **Source** | Archive.org `games_20250220` → `Virtua Fighter V PS3/GAMES.rar` (3.69GB) |
| **Note** | This is the base VF5, NOT Final Showdown. FS was digital-only (PSN/XBLA) and has no free Archive.org dump. Base VF5 has 17 fighters; FS added Jean Kujo + Taka-Arashi (19 total). |
| **Status** | 100% — full 19-fighter roster + all 38 stage archives extracted and on Release `vf5-ps3-v1` (2026-10-13) |

## Roster (17 fighters — base VF5)

| # | Fighter | Style | Priority |
|---|---------|-------|----------|
| 1 | Akira Yuki | Bajiquan | — |
| 2 | Pai Chan | Ensei-Ken | — |
| 3 | Lau Chan | Koen-Ken | — |
| 4 | Wolf Hawkfield | Pro Wrestling | **HIGH** |
| 5 | Jeffry McWild | Pancratium | — |
| 6 | Kage-Maru | Hagakure-ryu Jujutsu | **HIGH** |
| 7 | Sarah Bryant | Martial Arts | — |
| 8 | Jacky Bryant | Jeet Kune Do | — |
| 9 | Shun Di | Drunken Kung Fu | **HIGH** (pairs with ZUI) |
| 10 | Lion Rafale | Praying Mantis Kung Fu | **HIGH** |
| 11 | Aoi Umenokouji | Aiki-Jujutsu | **HIGH** |
| 12 | Lei-Fei | Shaolin Kung Fu | — |
| 13 | Vanessa Lewis | Vale Tudo | **HIGH** |
| 14 | Brad Burns | Kickboxing | — |
| 15 | Goh Hinogami | Judo | **HIGH** |
| 16 | Eileen | Monkey Kung Fu | — |
| 17 | El Blaze | Lucha Libre | **HIGH** |

**FS-only (not in this dump):** Jean Kujo (Karate), Taka-Arashi (Sumo)

## File Formats (documented from community RE)

| Format | Description | Tool |
|--------|-------------|------|
| `.farc` | Sega archive container (models, textures) | FarcPack (MikuMikuLibrary) |
| `.gz` | Gzip-compressed individual files | WinRAR / 7z / gunzip |
| `.bin` | Model data (after .gz extraction) | chrrox 3ds Max script |
| `.txp` | Texture container | TXP.bms (QuickBMS) |
| `rin_tex500.gz` pattern | Per-character texture packs | farc extractor → gunzip → TXP.bms |

## Directory Layout (PS3)

```
USRDIR/
  rom/
    objset/     ← character + stage models (.farc files)
    sound/
      bgm/      ← background music (ADX format)
```

- Stage files start with `stg` prefix
- Character models: ~40,000 polygons each (highest of its era)
- Stages: up to 300,000 polygons each
- 60fps, with diffuse/specular/bump/normal mapping

## Extraction Pipeline

1. Extract `.farc` files with FarcPack
2. Decompress `.gz` files (WinRAR/7z/gunzip)
3. Import `.bin` models via chrrox 3ds Max script (includes facial expressions + skeleton)
4. Extract textures: farc → `.gz` → `.bin` → TXP.bms (QuickBMS) → textures
5. Convert PNG ↔ DDS with DXTBmp as needed

**Tools** (in `~/workspace/tools/vf5-extract/`):
- `MikuMikuModel.7z` — model/texture extraction and replacement
- `FarcPack.7z` — .farc archive pack/unpack

**Also needed** (not yet pulled):
- chrrox 3ds Max import script (from Xentax thread)
- TXP.bms QuickBMS script (from Xentax thread)
- QuickBMS itself

## Character Polygon Counts

Per Sega: each VF5 character uses 40,000+ polygons. For comparison, Gears of War (2006) used 10,000–15,000 per character. VF5's count was unsurpassed until Ninja Gaiden II (2008).

## What's Next — DONE 2026-10-13

1. ~~Complete download → verify RAR integrity~~ — RAR verified on disk (3.69GB)
2. ~~Split → GitHub Release~~ — 8× 500MB chunks on Release `vf5-ps3-v1`
3. ~~Extract characters~~ — ALL 19 fighters (was 7 priority, now full roster: Akira, Pai, Lau, Wolf, Jeffry, Kage, Sarah, Jacky, Shun, Lion, Aoi, Lei-Fei, Vanessa, Brad, Goh, Eileen, El Blaze + Dural boss)
4. ~~Extract stages~~ — all 38 stage archives (`stg*.farc`) on the release, cataloged in `stages/README.md`
5. Extract UI/menus (remaining)
6. ~~Push all to this directory~~ — models/README.md + stages/README.md updated

**Release `vf5-ps3-v1` contents:** 8 game chunks + 18 `*itm.farc` + 19 body `*.farc` + 38 `stg*.farc` + shared (effcmn, itmcmn, dbg, test, obj_db.bin, tex_db.bin)

## Sources

- Xentax: "(PS3) Virtua Fighter 5 / Project Diva Dream Theater" thread (chrrox scripts)
- VirtuaFighter.com: "Modding VF5 Final Showdown PC/RPCS3" (MikuMikuLibrary pipeline)
- Sega Retro: Virtua Fighter 5 technical specs

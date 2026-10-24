# DOA Wardrobe System — extracted for the customization suite

**Source game:** Dead or Alive 6 (Team Ninja / Koei Tecmo, 2019)
**Extracted from:** repo research docs
(`customization/CUSTOMIZATION-RESEARCH.md` §7, `teardown/dead-or-alive-6/`)
— no game binaries were pulled (see `GAP.md`), so this is the *system/menu*
layer, not part files.

## The system (verified from research)

DOA6's customization is a **wardrobe loadout** system — the series' only
real customization (DOA3/4/5 are fixed-costume-select only):

- Per character, a loadout = **Costume + Hairstyle + Glasses + Title**
  (Title = two combined phrases, e.g. "RAGING" + "BEAST")
- **10 saved slots per character**, swappable at character select
- Hairstyles (~5,000 coins) and glasses (~2,000 coins) bought with
  **Player Points**
- Costumes use a **parts system**: random drops from Quest / Arcade /
  Survival → collect all parts → spend coins to purchase the costume
- DLC costumes arrive fully unlocked (paid)

## Suite mapping (UNIFIED-UI-SPEC.md §5.3)

| DOA concept | Suite home |
|---|---|
| Costume | ATTIRE tab slots (T7 slot spine) |
| Hairstyle | BODY → Hair (mirrors ATTIRE Hairstyle slot) |
| Glasses | ATTIRE → Glasses (T7 slot 5) |
| Title (two phrases) | WARDROBE slot label |
| 10 loadout slots | WARDROBE tab: SAVE CURRENT LOOK / LOAD per slot |
| Parts-drop economy | Unlock flow: play modes → earn parts → complete sets → items appear in ATTIRE shop |
| Player Points purchases | Suite currency hook (open question §12) |

## When part files land

Extracted costume/hair/glasses meshes go here per the slot map above,
registered in `manifest.json`, and picked up by `../build_parts_index.py`
(`source_game: "doa"`). File formats will be Koei Tecmo `.g1m` (models)
+ `.g1t` (textures) — see `GAP.md` for the extraction path.

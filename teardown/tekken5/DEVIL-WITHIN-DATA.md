# DEVIL WITHIN — Extracted Game Data (File-Level)

**Owner priority: Devil Within content FIRST.** This doc records what the T5 PS2 disc
holds for the Devil Within mode — the file-level grounding for Western Heart's
"Heart and Mind Within" story mode. Design research (structure, mechanics, adaptation
blueprint): `~/workspace/devil-within-teardown.md` (2026-10-22).

**Status 2026-10-23:** DW animation files LOCATED in `TK5DATA2.BIN`. DW stage geometry,
boss AI, and mechanics are in the binary `TK5DATA0.BIN`/`TK5DATA3.BIN` formats —
mapped for the RE bench, not yet extracted.

---

## 1. Located: DW animation files (`TK5DATA2.BIN` romD)

| File | Likely content |
|------|----------------|
| `gym_dw_nog00.dat` | Devil Within enemy animation ("nog" — enemy type TBD) |
| `gym_dw_raribxk.dat` | Devil Within boss/enemy animation ("rari" — TBD) |
| `gym_dw_rarixk.dat` | Devil Within boss/enemy animation |
| `gym_djin_newhane00.dat` … `newhane03.dat` | Devil Jin transformation ("hane" = wings/feathers — the black-feather disintegration visual) |
| `dwfkao00.dat` | DW-specific data ("kao" = face — possibly Devil Jin face/model) |
| `dwhadoh00.dat` | DW-specific data |
| `dwup00.dat` | DW-specific data ("up" — possibly Devil Gene meter UI or power-up) |

Character sound: `c30dvj.dat` (Devil Jin), `c10jin.dat` (Jin), `c15hei.dat` (Heihachi clones), `c21jac.dat` (JACK).

## 2. Stage files (`TK5DATA2.BIN`)

`stg00.dat`, `stg01.dat`, `stg02.dat`, `stg04.dat` — stage data files. (`stg03` absent from manifest.)
`moj_stg02.dat` — stage 2 text ("moji" = characters/text).

DW's 5 stages (G Corp lab → medical wing → ruins → spaceship → deeper) are likely among
these or in `TK5DATA0.BIN`'s binary format. Mapping stage IDs → DW stages is RE bench work.

## 3. Mapped for RE bench (in `TK5DATA0.BIN` / `TK5DATA3.BIN`)

Not yet extracted (binary proprietary formats, no ASCII filenames):
- DW stage geometry (5 stages: lab, medical wing/child's bedroom, ruins, spaceship, deeper)
- Boss data (Modified Gun Jack, Heihachi clones, True Ogre, Soul Sphere, Monstrous Ogre)
- Enemy data (JACK variants, G Corp soldiers, Adam/Eve/Duke/Regal/Jill mutants)
- Devil Gene meter mechanics, gem/Force systems, ranking
- DW UI/menus (mode select, HUD, rank screen)

**Why they're there:** DW mode is a separate executable path loaded from the TK5DATA
archives. The bootloader (`SLUS_210.59`) loads `TK5DATA3.BIN`; DW stage/boss data is in
the 2.07 GB `TK5DATA0.BIN` (character/stage data) — confirmed by absence of DW markers
in TK5DATA1/3 and presence of DW animations in TK5DATA2.

## 4. What the mode needs (from design doc, for the RE bench)

When the formats are reversed, extract in this order:
1. Jin's DW brawler moveset (simplified: punch/kick/block/jump — distinct from versus)
2. Devil Gene meter + Devil Jin transformation data (fill rates, laser damage, health drain)
3. 5 stage layouts (rooms, breakables, gem/Force spawns, Devil symbol locations, boss arenas)
4. Boss patterns (Modified Gun Jack, Heihachi clones, True Ogre, Soul Sphere, Monstrous Ogre)
5. Ranking thresholds (time/damage/retries/Force → S/A/B/C)
6. UI layouts (per MENUS FROM TEARDOWNS ONLY law — WH story menus rebuild FROM these)

---

## Extraction log

| Date | Action | Result |
|------|--------|--------|
| 2026-10-23 | Scanned TK5DATA2.BIN motion manifest | 3 `gym_dw_*` + 4 `gym_djin_*` + 3 `dw*.dat` + 4 `stg*.dat` found |
| 2026-10-23 | Scanned TK5DATA0/1/3 for DW markers | 0 hits — DW stage/boss data in binary formats, queued for RE bench |

# DEVIL WITHIN — Extracted Game Data (File-Level)

**Owner priority: Devil Within content FIRST.** This doc records what the T5 PS2 disc
holds for the Devil Within mode — the file-level grounding for Western Heart's
"Heart and Mind Within" story mode. Design research (structure, mechanics, adaptation
blueprint): `~/workspace/devil-within-teardown.md` (2026-10-22).

**Status 2026-10-23:** DW animation files LOCATED in `TK5DATA2.BIN`. DW stage geometry,
boss AI, and mechanics are in the binary `TK5DATA0.BIN`/`TK5DATA3.BIN` formats —
mapped for the RE bench, not yet extracted.

**Status 2026-11-08 (index-level decode, see `DW-DECODE-LOG.md`):** all 242 Devil
Within files in the romD manifest are inventoried by name with romaji glosses in
`dw-motion-index.json` (Devil Jin kit 52, Modified Gun Jack 39, True Ogre 29,
Monstrous Ogre 36, monster archetypes, transform, stage text, sounds). No offsets,
sizes, or file contents are resolved — the archive bytes are not in the repo.
CORRECTION: there are NO plain `stg*.dat` stage files in the romD manifest at all
(§2 below was wrong); only `moj_stg*` stage text. The romD table format is
documented in `ROMD-FORMAT.md`; the reader is `tools/romd_extract.py`.

---

## 1. Located: DW animation files (`TK5DATA2.BIN` romD)

| File | Likely content |
|------|----------------|
| `gym_dw_nog00.dat` | Devil Within enemy animation ("nog" — enemy type TBD) |
| `gym_dw_raribxk.dat` | Devil Within boss/enemy animation ("rari" — TBD) |
| `gym_dw_rarixk.dat` | Devil Within boss/enemy animation |
| `gym_djin_newhane00.dat` … `newhane03.dat` | Devil Jin transformation ("hane" = wings/feathers — the black-feather disintegration visual) |
| `gym_dwfkao00.dat` | DW-specific data ("kao" = face — Devil Jin face/model) |
| `gym_dwhadoh00.dat` | DW-specific data ("hadoh" = wave — likely the laser/wave file) |
| `gym_dwup00.dat` | DW-specific data ("up" — power-up; possibly Devil Gene meter UI or power-up object) |
| `gym_dwup_hei.dat` | Power-up, Heihachi variant (the Heihachi-clone version of `dwup`) |

Full inventory: `dw-motion-index.json` — 242 DW files (Devil Jin kit `gym_ikdv_*`
52, Modified Gun Jack `gym_kmb1_*` 39, True Ogre `gym_kob2_*` 29 [inference],
Monstrous Ogre `gym_ozb3_*` 36 [inference], unresolved gun/fly kit `gym_ikt5_*`
26, init objects `gym_init_obj_*` 21, transform `gym_djin_newhane*` 4, stage text
`moj_stg00/01/02/04`, sounds `snd_*` 18), each with a gloss and confidence.

Character sound: `snd_c30dvj.dat` (Devil Jin), `snd_c10jin.dat` (Jin), `snd_c15hei.dat` (Heihachi clones), `snd_c21jac.dat` (JACK), `snd_c02lei.dat` (Lei). These anchor the char codes: c02 = Lei, c10 = Jin, c15 = Heihachi, c21 = JACK, c30 = Devil Jin.

## 2. Stage files (`TK5DATA2.BIN`) — CORRECTED 2026-11-08

**There are NO plain `stg*.dat` stage-geometry files in the romD manifest.**
An earlier version of this doc said `stg00/01/02/04.dat` exist; that was wrong
(verified by grep over all 498 manifest names, 2026-11-08). What exists is
stage **text**: `moj_stg00.dat`, `moj_stg01.dat`, `moj_stg02.dat`,
`moj_stg04.dat` ("moji" = characters/text). `moj_stg03` is absent from the
manifest. Stage geometry is NOT in romD — it lives in `TK5DATA0.BIN`'s binary
format (see §3).

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
| 2026-10-23 | Scanned TK5DATA2.BIN motion manifest | 3 `gym_dw_*` + 4 `gym_djin_*` + 3 `gym_dw*.dat` + 4 `moj_stg*.dat` found (0 plain `stg*.dat` — the earlier "4 `stg*.dat`" note was wrong) |
| 2026-10-23 | Scanned TK5DATA0/1/3 for DW markers | 0 hits — DW stage/boss data in binary formats, queued for RE bench |
| 2026-11-08 | Index-level decode of the 498-name manifest | 242 DW files inventoried with glosses in `dw-motion-index.json`; romD format documented in `ROMD-FORMAT.md`; reader built + self-tested in `tools/romd_extract.py`; log in `DW-DECODE-LOG.md`. Offsets/sizes still BLOCKED — no `TK5DATA2.BIN` bytes in repo or on disk. |

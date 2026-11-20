# Teardown research, part C: Urban Reign + Urban Reign Redux

**Date:** 2026-11-07 (evening CST)
**Repo:** `mhvnsnt/western-heart`, HEAD `3334ebf` at the time of reading
**Method:** read repo files with the GitHub connector only. No game code was edited, nothing was pushed, no commercial game file, ISO, ROM, or code file was downloaded. Public sources were read with web search and page text only.
**Names:** Pantera is male (he/him). Every other fighter is named only, no guessed pronouns.
**Standing limit (unchanged):** measure the behaviour and rebuild it in our own code. Commercial game code files, models, art, audio, logos, and dialogue are NOT copied into the game.

**One limit on this whole report:** the GitHub code-search tool searches all of GitHub and ignores the repo filter, so there is no exhaustive text search for "Urban Reign" across `docs/` and `game/js/`. The mentions listed in §1.4 are the ones found in the docs read for this pass plus the earlier audit. A repo-wide grep is still owed if the parent wants it proven complete.

---

## 1. What Urban Reign material is already in the repo

The folder is named exactly `teardown/urban-reign` (lowercase, hyphen). It is the biggest single-game teardown in the repo: the coverage matrix rates Urban Reign **~95%** complete (`teardown/TEARDOWN-COVERAGE-MATRIX.md`), the highest rating in the matrix.

### 1.1 Top level of `teardown/urban-reign/`

18 doc files + 3 listing files + 18 subfolders.

| File | Size | What it is |
|---|---|---|
| `TEARDOWN.md` | 5,141 B | Main teardown record: role, extraction log, what is blocked |
| `WIRING-INVENTORY.md` | 6,782 B | Phase-4 canonical record: what is decoded, wired, and left before playable |
| `BANK-COMPLETION.md` | 7,278 B | Phase-6 motion-bank census: 285 banks / 3,357 motions searchable |
| `CANON-CONVERSION.md` | 5,369 B | Urban Reign → Western Heart (`street-reign`) conversion record |
| `PHASE3-STATE.md` | 10,954 B | Phase-3 state (textures) |
| `PHASE4-STATE.md` | 4,679 B | Phase-4 state |
| `PHASE4-JOB1-LOADER-SEARCH.md` | 5,230 B | Phase-4 job 1: loader search |
| `PHASE4-JOB3-POLISH.md` | 4,636 B | Phase-4 job 3: polish |
| `PHASE5-STATE.md` | 6,750 B | Phase-5 state (move names) |
| `PHASE5-JOB2-TYPE14.md` | 5,558 B | Phase-5 job 2: type-14 root decode |
| `PHASE5-JOB3-EXECUTIONS.md` | 8,433 B | Phase-5 job 3: executions (char064 recovery, accessories) |
| `PHASE6-STATE.md` | 6,580 B | Phase-6 state (bank completion) |
| `PPK-FORMAT.md` | 3,912 B | PPK container format notes |
| `PPK-GEOMETRY.md` | 6,075 B | PPK geometry notes |
| `UI-SYSTEM.md` | 5,294 B | UI/menu system doc: VGS screens, DCM layouts, mission system |
| `VGS-FORMAT.md` | 2,565 B | VGS UI texture-atlas format notes |
| `dvd000-contents.txt` | 102,639 B | DVD000 AFS contents listing |
| `dvd001-contents.txt` | 52,824 B | DVD001 AFS contents listing |
| `iso-file-listing.txt` | 628 B | ISO file listing |

**The ISO itself is not a folder.** `TEARDOWN.md` records `Urban Reign (USA).iso`, 4.14 GB, from Internet Archive item `urban-reign-usa_202608`, stored as GitHub Release `urban-reign-iso-v1` (https://github.com/mhvnsnt/western-heart/releases/tag/urban-reign-iso-v1), split into 8×500 MB parts, reassembled with `cat urban-reign-500m.part_*`. The local ISO was deleted after verification. This is extracted commercial game material sitting in a public repo release — the same flag the audit already raised (`AUDIT.md`).

### 1.2 Subfolders, level by level

**`afs-map/`** — 2 files: `dvd000_afs_map.json` (186,390 B, all 2,431 DVD000 entries with byte offsets + sizes), `dvd001_afs_map.json` (88,024 B).

**`animations/motion-packs/`** — 46 files: `main.ppk` (3,153,024 B), `main_in.ppk` (3,347,968 B), `mainx.ppk` (128 B, header shell, zero payload), `select.ppk`, `weapon.ppk`, 31 `pmotNNN.ppk` (per-character motion packs, ~281–637 KB each), 10 `tmotNNN.ppk` (team/tag motion packs).

**`audio/`** — 1,000 items listed (README + `.p3d`/`.pbd` sound-bank pairs, e.g. `sound_ok_se_se_at00.pbd` 129,120 B). **Count warning:** the listing hit the GitHub API's 1,000-item cap, so the true count is "at least 1,000", not exactly 1,000. `README.md` is 1,263 B.

**`cutscenes/`** — 35 files: `demo_dataNNN.ppk` cutscene containers (98 KB–1.54 MB each).

**`docs/`** — 2 files: `URBAN-REIGN-TEARDOWN.md` (3,074 B, the short research teardown) and `stage-candidates.txt` (30 B).

**`missions/`** — 2 subfolders, no loose files:
- `missions/definitions/` — 256 files, `mission000.bin`–`mission255.bin`, 8,300 B each (2 MB total).
- `missions/ppks/` — 100 files, `mission001.ppk`–`mission100.ppk`, ~6–10 MB each, 821 MB total (per `UI-SYSTEM.md`).

**`models/`** — 72 subfolders `char001`–`char072` + `ROSTER.json` (4,792 B, a per-character numbers table: verts/indices/PPK size etc.). Each `charNNN/` holds 5 files: `charNNN.glb` (the skinned phase-1 model, e.g. char001 269,412 B), `charNNN_normals.obj`, `charNNN_pos_infl0.obj`, `charNNN_uv.obj`, `charNNN_vmanifest.json`. These are the untextured phase-1 GLBs.

**`motion/`** — 6 files: `general_normal.gyu` (1,532,848 B), `general_30frame.gyu` (1,788,924 B), `general_weapon.gyu` (587,372 B) — the three shared animation pools; `gyu_debug.gyu` (4,016 B); `gyuindex.bin` (8,284 B) and `gyuindex_ppk.bin` (3,467 B) — bank index tables.

**`motion-names/`** — 36 files: the move-name bridge evidence. `BANK-INVENTORY-PHASE6.json` (81,398 B), `DVD001-HEADER-CENSUS.json` (184,329 B), `PHASE6-RERUN-RESULTS.json` (299,168 B), `motdat-info-tables.json` (95,592 B), `name-bridge-charNNN-proven.json` files (one per fighter with proven names), plus Phase-4/5/6 summary docs.

**`ppks/`** — 2 subfolders, no loose files:
- `ppks/chars/` — 72 files, `char001.ppk`–`char072.ppk` (~485–671 KB each, 44 MB total).
- `ppks/stages/` — 7 files: `stage003.ppk` (5,406,080 B), `stage004.ppk` (4,492,928 B), `stage020.ppk` (3,571,328 B), `stage028.ppk` (3,470,464 B), `stage029.ppk` (6,991,232 B), `stage030.ppk` (4,794,624 B), `stage031.ppk` (5,175,168 B). 34 MB total. **Stage geometry inside them is NOT decoded** (`TEARDOWN.md`).

**`rigging-reference/`** — 1 file: `urban-reign-hand-arm.md` (2,450 B).

**`sound/`** — 1 subfolder + 1 file: `ok_adx/` and `ADX-INVENTORY.csv` (41,045 B). `sound/ok_adx/adx/` holds 1,000 items listed (background-music ADX files, e.g. `bg01_01.adx` 4,231,168 B) — again at the API's 1,000-item cap, so "at least 1,000", exact count unmeasured.

**`textured-models/`** — 73 files + 1 subfolder. This is **the canonical fighter model set** (`WIRING-INVENTORY.md`): 72 `charNNN_textured.glb` files (~374–484 KB each) with 733 embedded images total, verified geometry-identical to the phase-1 GLBs per character (`MANIFEST.json`, 11,180 B, with per-character verts/indices/joints/images). `renders/` holds 6 profile PNGs (`ur9-char001/010/020/035/050/072-textured-profile.png`).

**`textures/`** — 72 subfolders `char001`–`char072` + 3 files (all about char001: `char001-census-addendum.md`, `char001-tail-census.json` 40,120 B, `char001-tail-census.md`).

**`tools/`** — 25 Python tools, all own code: `ur_decode.py` (51,070 B, the main decoder), `ur_gyu.py` (9,642 B, motion-bank decoder), `ur_tex_extract.py` (14,008 B), `ur_gates.py` (10,822 B), `ur_tail_census.py` (20,703 B), `ur_build_textured.py` (8,344 B), `ur_embed.py` (6,155 B), `ur_batch_embed.py` (3,216 B), `ur_bake_render.py` (6,638 B), `ur_skin_bake.py` (6,459 B), `ur_extract_meshes.py` (4,256 B), `ur_dvd001_fetch.py` (6,900 B), `ur_parse_vertices.py` (6,958 B), `ur_bone_hunt.py` (4,038 B), `ur_char064_recover.py` (3,218 B), `ur_name_bridge.py` (4,855 B), `ur_motdat_info.py` (3,218 B), `vgs_decode.py` (4,554 B), `vgs_batch_decode.py` (2,394 B), `afs_list.py`, `afs_list_iso.py`, `analyze_iso.py`, `extract_elf.py`, `ppk_probe.py`, `g4_blender_verify.py`.

**`ui/`** — 4 subfolders:
- `ui/character-select/` — 2 files: `face.vgs` (115,752 B, portraits), `select.ppk` (108,032 B).
- `ui/menus/` — 18 files: `.vgs`/`.dcm` menu layouts, pause screen, frames, progress (e.g. `dcm_pause.dcm` 17,620 B, `crow.vgs` 644,680 B).
- `ui/screens/` — 54 files: title, mode select, options, character profiles, victory screens (e.g. `common.vgs` 430,504 B, `charaprofile.v` 483,624 B, `cong00`–`cong12.vgs` victory screens, `mc_stage00`–`mc_stage06.vgs` mission stage art).
- `ui/title-screens/` — 1 file: `title_US.vgs` (303,944 B).

**`vgs/`** — 2 files + 2 subfolders: `VGS-INVENTORY.csv` (2,975 B), `VGS-BATCH-20261013.md` (1,585 B); `vgs/raw/` 48 `.vgs` files; `vgs/decoded/` 38 PNGs (decoded UI screens).

### 1.3 What is already wired into the playable game (`game/`)

Per `WIRING-INVENTORY.md` and `CANON-CONVERSION.md`, read this pass:

- **Models:** `game/assets/models/street-reign/` — 72 files, `char001.glb`–`char072.glb`. These are the **untextured** phase-1 copies. 31 of them carry embedded native animation (clips `ur_m*` + `Idle`). Roster ids `ur-char001`–`ur-char072` in `game/js/roster-full.js`, display names `CHAR001`–`CHAR072`, shared moveset key `street-reign` (`game/js/assets.js` `MODEL_URLS` keys `ur-char001`..`ur-char072`).
- **Movesets:** `game/assets/movesets/` holds 33 Urban Reign files out of 175 total: `street-reign.json` (1,898 B, proxy — the engine base set, labelled `proxy: true`), 31 `ur-charNNN.json` files (the 31 natively animated fighters; sizes 2,805–10,928 B), and `ur-native-index.json` (9,793 B). The 31 fighters with a moveset JSON are char001, 002, 003, 004, 005, 016, 020, 021, 022, 030, 031, 032, 041, 042, 043, 044, 045, 046, 054, 055, 056, 057, 058, 059, 060, 061, 062, 063, 070, 071, 072.
- **Shared animation pools:** `game/assets/anim/` holds 3 Urban Reign folders out of 8 items: `ur-general-normal/`, `ur-general-30frame/`, `ur-general-weapon/` — the converted general-pool banks (829 motions). Shared pool data only, not assigned per fighter.
- **Move names:** 484 move names proven at the Phase-5 gate (max deviation ≤ 0.10 mm, unique) and annotated as `motdatName` in `game/assets/movesets/ur-charNNN.json`, across 27 fighters. 402 records stay unproven: 307 identified only in another fighter's bank (evidence recorded, never assigned), 92 with no bank in the shipped disc at all, 3 borderline over the gate (char042 rec50 0.1361 mm, char055 rec34 0.1253 mm, char057 rec32 0.1020 mm). The 5 P1 records (6, 10, 11, 12, 14 — jump kicks and a double air kick) have no source bank anywhere in the shipped disc; only a live emulator capture could source them. 41 fighters are proxy-only: no native bank and no name list in any shipped file.
- **Tests:** `game/tests/model-key-guard.test.mjs` checks the roster model keys (per `CANON-CONVERSION.md` §5).

### 1.4 `moveset-library/` — no Urban Reign moves there

Checked directly. `moveset-library/movesets/` holds Soulcalibur II movesets (24 files, `scii-*.json`), WMXIX moves (`WMXIX-MOVES.json` 273,757 B, `rock-moves-wmxix.json`), the Mat Kings move database (2,328,042 B), `pantera-moveset.json`, `toguro-moves-yyh.json`, plus `MOVE-DATABASE.json` and `MOVE-SLOTS.json`. `moveset-library/movesets-v2/` holds only the 24 Soulcalibur II files again, bigger. `moveset-library/animations/` holds `ANIMATION-INDEX.json`, `OWNER-MOTION-BANK.json`, `WMXIX-CLIP-INDEX.json`, `UAL-CC0.json`, and an `owner-motion-bank/` folder. **Urban Reign moves live in `game/assets/movesets/ur-charNNN.json`, not in `moveset-library/`.** That is the gap to close if the library is meant to hold all moves in one place.

### 1.5 Other Urban Reign mentions in the repo

- `CANON.md` — two documented canon links: **Cain Elias** has a moveset documented as "Glen Kluger (Urban Reign biker gang leader) or a fitting Tekken character"; the **Slice / Ryuji-based fighter** uses "wrestling moves from Urban Reign / Tekken / other teardown games". (Cited from `CANON-CONVERSION.md` §3; `CANON.md` itself was not re-read this pass.)
- `RENAME-MAP.md` — "Urban Reign | `street-reign` | Street reign brawlers", phase note: "game uses UR systems".
- `CHIMERA-BUILD.md` — the open owner decision: Option A, a third **BRAWL MODE**, vs Option B, Urban Reign systems merged into Wrestling Mode as its hardcore/street-fight variant. Still open.
- `teardown/TEARDOWN-COVERAGE-MATRIX.md` — Urban Reign ~95%, missing: DCM semantics, inner PPK geometry. `teardown/TEARDOWN-STATUS.md` — same ~95% row. `teardown/TEARDOWN-SOURCES.md` — lists the Urban Reign sources.
- `docs/urban-reign/URBAN-REIGN-GATES.md` — cited in `CANON-CONVERSION.md` as the Phase-1 gates record; not read this pass.
- `AUDIT.md` (2026-11-06) — flags the `teardown/` extracted commercial material, Urban Reign included, in a public repo against the repo's own AGENTS.md rule.

### 1.6 What can be wired in directly from the repo itself (no new download)

This is the usable-here list, with exact paths:

1. **Textured fighter swap (named follow-up, NOT done).** `teardown/urban-reign/textured-models/charNNN_textured.glb` (72 files, canonical, 733 images) → `game/assets/models/street-reign/charNNN.glb`. Per `WIRING-INVENTORY.md` it is a one-step follow-up: re-run the phase-2 embedder (`teardown/urban-reign/tools/ur_embed.py` / `ur_batch_embed.py`) with the textured GLBs as the base for the 31 pmot fighters, copy all 72 under the existing `charNNN.glb` names, and re-run the roster resolution check (72/72). The 31 animated game GLBs carry embedded clips the textured GLBs do not, so it is not a plain file swap.
2. **Native animation banks.** Already embedded in the 31 game GLBs as `ur_m*` + `Idle` clips; the shared pools sit in `game/assets/anim/ur-general-{normal,30frame,weapon}/`. Per-fighter assignment of the 829 general-pool motions is still owed (runtime capture is the Phase-4 spec for it).
3. **484 named moves.** Already annotated as `motdatName` in `game/assets/movesets/ur-charNNN.json`; evidence in `teardown/urban-reign/motion-names/`.
4. **UI layout reference.** `teardown/urban-reign/ui/screens/` (54 VGS screens), `ui/menus/` (18 files, incl. `dcm_pause.dcm`), `ui/character-select/face.vgs` + `select.ppk`. The VGS tile payload is still undecodable (proprietary Namco encoding), so these are layout/measure references only — the game uses its own UI. `VGS-FORMAT.md` documents the header (magic `03 08`, grid width/height, offset/size table).
5. **Mission structure data (not decoded).** `teardown/urban-reign/missions/definitions/mission000.bin`–`mission255.bin` + `missions/ppks/mission001.ppk`–`mission100.ppk`. Field layout is unknown; decoding is open work, not a wire-in.
6. **Audio (extracted, not wired).** `teardown/urban-reign/audio/` (sound banks) + `teardown/urban-reign/sound/ok_adx/adx/` (music ADX files). No conversion into the game exists.
7. **Stages (NOT wireable yet).** `teardown/urban-reign/ppks/stages/stage003/004/020/028/029/030/031.ppk` — geometry not decoded. No stage-registry entry exists in `game/js/stages.js`.
8. **Fighter identities (OWNER-pending).** The repo's per-fighter identity is only the id itself (`char001`–`char072`). Only Brad Hawk (the protagonist) and the Tekken guests Paul Phoenix and Marshall Law are named, without saying which PPK numbers they are. No fighter has been renamed to a Western Heart canon name. The one documented mapping is Glen Kluger → Cain Elias's moveset source, and the specific PPK for Glen Kluger is part of the flagged identity pass.

---

## 2. Urban Reign's actual feel and systems, measured from public sources

Game: **Urban Reign**, Namco, PlayStation 2, 2005 (USA release September 13, 2005; Europe 2006). IDs: SLUS-21209 (USA), SLPS-25557 (Japan), SCES-53688 (Europe). Rated Teen. Made by the Tekken/Soulcalibur team.

### 2.1 The shape of the game

- **A 3D arena brawler, not a 1v1 fighter.** Free-roam arenas, several fighters on screen at once, human and AI together. Tekken Wiki: "multiple AI opponents and human controlled characters on the same screen fighting at the same time", free movement in the environment, pick up weapons, throw objects, give instructions to AI partners, pull off moves on multiple opponents at once. Source: https://tekken.fandom.com/wiki/Urban_Reign
- **100-mission Story Mode.** Brad Hawk, a brawler-for-hire, is hired by Shun Ying Lee to find a kidnapped gang member, fighting through the street gangs of Green Harbor. Namco's own gold announcement: "Fighting through the game's 100 missions alone or with a computer-controlled partner, Brad will uncover a trail of corruption and deception that spans throughout Green Harbor." Source: https://uat.gamedeveloper.com/press-release/urban-reigntm-fights-its-way-to-gold
- **60+ playable fighters**, each with a distinct style (boxing, wrestling, karate, brawling, capoeira, kung fu, Muay Thai, Tae Kwon Do). Tekken guests **Paul Phoenix and Marshall Law** are unlockable, with Tekken 5-era models and trademark attacks. Source: Tekken Wiki (same link as above); Namco press release (same link as above).
- **Modes:** Story (100 missions), Free Mode (play Story missions with any unlocked character), Challenge Mode (wave survival, solo or co-op), Versus (KO or points rules), Practice, Tutorial, Fighter Files (character profiles), and 4-player multiplayer with a PS2 multitap: head-to-head, team brawls, **Weapon Battle** (hold the weapon to win) and **Destruction/Object Battle** (protect your object, smash theirs). Sources: USA manual contents and mode screens, https://archive.org/stream/ps2_Urban_Reign_USA/Urban_Reign_USA_djvu.txt ; teardown doc `teardown/urban-reign/docs/URBAN-REIGN-TEARDOWN.md`.
- **Runs at 60 frames per second.** Namco's box copy, quoted in several sources: "the first multiplayer fighting game to unleash never-before-seen double team combos at 60 frames per second." Source: https://thegamesdb.net/game.php?id=9836

### 2.2 Controls (measured from the USA manual itself)

The full manual text is freely readable at https://archive.org/stream/ps2_Urban_Reign_USA/Urban_Reign_USA_djvu.txt (Namco, 2005; archive.org Manual Library). Buttons below are PlayStation buttons as the manual prints them (Circle = Strike, Triangle = Grapple, X = Run/Dash, Square = Dodge/Deflect, R1 = lock target, L1 = pick up/discard weapon, L2 = taunt, R2 = partner commands, right stick = camera, R3 = reset camera).

- **Strike:** Circle. Neutral = a multi-hit combo string; with a direction (Up / Left-Right / Down) the strike targets the Head / Upper Body / Lower Body region. Source: manual pp. 22–25; also https://stinger.actieforum.com/t408-urban-reign ("Each character has a multi-hit combo string that can be performed by pressing Circle without a direction").
- **Grapple:** Triangle. Directional grapples target a body region the same way; neutral grapple grabs and holds the opponent, front or back. Low and high grapples, air grapples, counters and reversals each have their own animation per character. Tekken Wiki: "Especially rich is the grappling system. There are low and high grapples, air grapples, counters and encounters each with its own animations for each character. The grapple system is highly reminiscent of Tobal 2." Source: https://tekken.fandom.com/wiki/Urban_Reign
- **Combo shape:** "most combos start with three presses of the attack button, the third of which will juggle an opponent. Then the player has choices of an air grapple, special move, simply continuing the combo or even running away to pick up a weapon or reposition." Source: Tekken Wiki (same link).
- **Dodge instead of block.** There is no block button. Square, timed to the moment of the attack, dodges it; Up/Down + Square reverses it. Tekken Wiki: "a major difference in Urban Reign from other Beat 'em ups is the replacement of a block action with dodge. Neutralizing attacks by opponents is done with a single button press that must be timed to the moment of the attack." Manual p. 32: "Pressing the Square button at just the right time while under enemy attack will allow you to dodge their Strike Attacks… if you are attacked by several enemies at once, you will be able to dodge all of them." Source: manual (link above); Tekken Wiki (link above).
- **Deflect / Grapple Break:** direction + Square deflects and throws the opponent off balance (and reduces the enemy SPA gauge); Square timed right breaks a grapple, aiming at the body region grabbed. Manual pp. 32–33.
- **Dash / Run-Up:** X to run; running into a wall, enemy, or partner lets the character run up it, then Circle = Diving Strike, Triangle = Diving Grapple. Manual p. 31.
- **Target lock:** R1 locks a target; right stick switches target while R1 is held. Manual p. 21.
- **Double Attack:** Triangle when directly facing, or surrounded by, two enemies hits both at once. Manual p. 30.
- **Quick Recovery:** Square before landing after being launched gets the character up at once, in a chosen direction; it also avoids down strikes and down grapples. Manual p. 33.

### 2.3 Special Arts (SPA) — the meter

- **Two buttons at once:** Circle + Triangle. Neutral SPA is a knockback in all directions (usable while standing or lying face-up, cheapest); Up + SPA is a big slow charged attack; Left/Right + SPA is a quicker multi-hit combo; Down + SPA is a status-effect buff, not an attack. Special Arts cannot be countered, reversed, or dodged except by another Special Art, and they can be buffered. Source: Tekken Wiki (link above); manual p. 28.
- **Status effects (Down + SPA):** Power Up (red, +50% attack), Concentration (blue, auto-deflects / auto grapple-breaks), Super Armor (yellow, less damage, no stagger), Arcanum (green, unlocks special moves). Source: manual p. 28; https://stinger.actieforum.com/t408-urban-reign
- **The gauge** fills when the character attacks, is attacked, or dodges/deflects. It can also be spent to recover from a stunned state. Source: manual p. 8 and p. 28.
- **Unlockable SPAs:** Brad starts with few moves and unlocks more Special Arts over the story, including wrestling moves (running powerbomb, stunner, leg whip, mid-air powerbomb) and the ability to grapple in mid-air and to change a grapple mid-animation with another input. Source: https://www.hardcoregaming101.net/urban-reign/amp/ ; https://stinger.actieforum.com/t408-urban-reign

### 2.4 Weapons and destructible environments

- **30+ weapons:** bats, pipes, bottles, shovels, 2x4s, knives, broken bottles. No weapon durability — a weapon lasts until dropped. Pick up / discard with L1; a weapon thrown into the air by a collision can be caught. Weapon attacks use Circle/Triangle while holding one, with direction picking the body region; Square + X throws the weapon (at the locked target, or the nearest enemy). A thrown weapon can be knocked down with Circle. Enemies sometimes drop recovery items that refill health or the SPA gauge. Source: manual pp. 26–27; Namco press release (link in §2.1).
- **The environment is a weapon:** walls, cars, crates, furniture. The manual says to smash launched enemies into walls or cars for extra damage, and to run up walls for Diving Strikes. Namco: "gritty environments, complete with obstacles and destructible objects"; furniture breaks, shelves shed boxes, cars and pinball machines shatter. Source: manual p. 20; press release; `teardown/urban-reign/TEARDOWN.md`.
- **Body regions matter:** Head, Upper Body, Lower Body each have their own health bar on screen; a region turns yellow when injured, red when destroyed. Destroying the lower body stuns easily; destroying the upper body makes the enemy drop a weapon. Source: manual pp. 8, 25.

### 2.5 Partner / tag mechanics — the heart of it

- **AI partner, earned by beating them.** In Story Mode, a partner is gained by first defeating that character. Source: https://www.hardcoregaming101.net/urban-reign/amp/ ("to gain an AI companion, you must first defeat them").
- **Partner commands (R2):** R2 alone = Call for Double-Team (partner comes over into double-team position); R2 + X = Call for Help (partner joins a concentrated attack on the locked-on enemy); R2 + Circle = Split Up (partner handles the other enemies); R2 + Square = Pass Weapons/Items back and forth; R2 + Triangle = Switch Fighters (take control of the partner). Source: manual p. 34.
- **Double-Team Attacks:** press R2 near the partner, or attack when the player and the partner surround an enemy, face one directly, or stand behind one — the attack differs by which character the partner is. The signature move: launch an enemy into the air and the partner catches and slams the enemy onto the concrete. Namco: "The player can send enemies flying through the air as their partners catch and slam them onto the concrete." Source: manual p. 34; press release (link in §2.1).
- **Grapple assists:** approach an enemy the partner is grappling and press Circle for an extra attack on the held enemy. Source: manual p. 34.
- **Switching is seamless, and the mission still hinges on Brad Hawk:** the player can switch to control the partner at any time, but the mission fails if Brad Hawk's health reaches zero, even while the player controls the partner. Source: manual p. 34 and p. 20; HG101 (link above).
- **Mission failure:** fail if the objectives are not met or Brad Hawk's health hits zero; retry from a menu (RETRY / MISSION INFO / QUIT). Source: manual p. 20.
- **No co-op Story at first:** two players cannot play the single-player missions together until unlocked, and then only with a code, and the camera follows Player 1 only. Source: Tekken Wiki (link above).

### 2.6 Stages

Stage names in the repo are only PPK ids (`stage003`, `stage004`, `stage020`, `stage028`, `stage029`, `stage030`, `stage031`) — **their place names are UNMEASURED from repo data**. Public sources name the kinds of places, not a full list: back alleys, bars, rooftops, Chinatown, junkyards (Namco press release), plus a parking lot, a bar interior, a warehouse, and a motel (seen in Redux gameplay coverage). Mission 01 is "BACK ALLEY — Warming Up". The game's city is Green Harbor. Source: press release (link in §2.1); https://www.facebook.com/reel/1614548087065737/ (Mission 01 title screen, from search).

### 2.7 What is directly usable as a feel reference for Western Heart's HeartMind mode vs what is Urban Reign-specific

**Directly usable for HeartMind (the feel layer):**
- The three-press strike string where the third hit juggles, then a free choice (air grapple / special / reposition / grab a weapon). That is a simple, readable combo shape that fits a phone.
- Direction = body region (Up = head, Left/Right = upper body, Down = lower body) on both strikes and grapples. One idea, reused everywhere, instead of a long move list.
- Dodge-timing instead of a block button, with deflect and grapple-break on the same timing idea. This is the sharpest difference from Tekken-style blocking and the most portable feel.
- The SPA meter shape: builds on attacking, being hit, and dodging; two-button trigger; neutral = get-off-me knockback, Up = big slow hit, Left/Right = multi-hit, Down = buff. Western Heart already has a Nine-Soul Meter and Soul Surge; the SPA shape is the proven reference for how a meter like that should feel.
- Double-Team Attacks and partner commands as the template for any tag/partner play: launch-and-catch slam, surround-an-enemy trigger, grapple assist, switch control, split up.
- Body-region damage (head/upper/lower each injured, then destroyed) as a readable damage idea.
- Wall run-ups and diving strikes/grapples as the arena-movement idea.
- 60 fps as the bar: the original ran its multi-fighter brawls at 60 fps. Western Heart's Piece-1 playtest ran at ~1 timer tick per 30 s on HIGH — the gap to the reference is the point.

**Urban Reign-specific (do not lift as-is):**
- The 100-mission Green Harbor story, Brad Hawk, Shun Ying Lee, the gang plot — that is Namco's story, not a system.
- The exact roster, styles, and names (Brad Hawk, Glen Kluger, Paul Phoenix, Marshall Law, and the rest) — use only the documented canon link (Glen Kluger → Cain Elias's moveset source) and the flagged identity pass.
- Weapon Battle / Destruction Battle as named modes, and the multitap 4-player setup — the rules can inspire a mode, the names and the PS2 setup cannot be copied.
- The VGS/DCM UI art and layout files — layout reference only, never copied art.

---

## 3. Urban Reign Redux — found, read, NOT downloaded

### 3.1 What it is

**Urban Reign Redux** is a community mod project for Urban Reign by **Jasonafex**. Its own words: "More fighters, revised movesets, new voices, music and menus for Urban Reign." It is **not** an official release and is "not affiliated with or endorsed by the original game's publisher."

- **Home:** https://jasonafex.github.io/urban-reign-redux/
- **Code and releases:** https://github.com/Jasonafex/urban-reign-redux
- **Issues:** https://github.com/Jasonafex/urban-reign-redux/issues
- **Community:** the Urban Reign Modding Discord (linked from the project website; invite link on the site, not copied here).

### 3.2 What it contains (version 0.5, released October 28, 2026)

- **More fighters:** the original roster plus Tekken guests (Asuka, Bryan, Jin, Kazuya, King, Nina, Paul, Yoshimitsu, Hwoarang, Heihachi, Devil Jin, Reina, Kunimitsu, Bob, Christie, Armor Queen) and crossovers from other games (Cammy, Leon, Carl Johnson, Kiryu, Jeff Hardy, Snake, Renamon, Vergence, Ricardo). Ricardo gets a separate select slot, name, and Fighter Files page.
- **Revised movesets and sound:** updated Fighter Files stats, styles, and bios; grounded idles (feet on the floor — Reina, Bob, Devil Jin, Ricardo, Kunimitsu, Renamon, Yoshimitsu, Jeff and others no longer float or sink); skeleton repairs; Tekken 8 stances and idles; long strings that connect (mid-string knockdowns became heavy staggers); Yoshimitsu's own voice instead of Law's, and the Player 2 selection freeze fixed; Jeff's Twist of Fate, idle, taunt, and side SPA fixes; Snake's up SPA now does damage.
- **Presentation:** cleaner hair, glasses, and clothing; reduced rainbow sheen; spring-physics repairs; two HD texture packs; smaller battle HUD, hidden player indicators, multiplayer camera controls (L3 follows the player on that controller, R3 restores the shared camera); expanded, paged stage selection with story-mode locations available in multiplayer; Challenge mode retexture; a mouth-animation pilot for Leon, Cammy, and Violet.
- **Known issues in 0.5 (stated by the author):** Kunimitsu's and Devil Jin's rigs still have weight-painting rough spots; Armor Queen has armour colour bleeding onto skin at the waist and hips; Bob has no Fighter Files voice yet; "The Devil Within, stage 1: the first door doesn't block you while enemies are still alive"; Cammy's throws can slide at the start; Reina can show a thin streak on the cheek.

Sources: project README, https://github.com/Jasonafex/urban-reign-redux (README.md, read via the GitHub connector); release notes, https://github.com/Jasonafex/urban-reign-redux/releases/tag/v0.5.0 ; project website (link above).

**Earlier versions (for the record):** 0.4, October 3, 2026 (1.75 GB package; Nina, Baek, and Carl Johnson voice banks; SPA and moveset revisions). 0.2 Alpha, September 30, 2026 refresh (Auto-Installer ~55 MB; 21 character packs; Trial 13 combat update). Source: `CHANGELOG.md` in the same repo.

### 3.3 What it requires

- **A player's own Urban Reign (USA) ISO** — the USA build, SLUS-21209. The tested 0.5 disc has game CRC **74E78599**. European and Japanese editions are refused by the builder.
- **PCSX2** (tested with 2.7.403) with ExtraMemory support enabled, and **the player's own PS2 BIOS**. Neither PCSX2 nor a BIOS is included.
- **Windows 64-bit** for the Mod Manager / Editor (they are `.exe` launchers).
- **A fresh boot, not an old emulator save state.** Memory-card saves are fine.

### 3.4 How it is distributed, and the lawful route

There are **two** downloads, and they are not the same thing:

1. **All-in-one package, 2.67 GB, Google Drive, no sign-in required.** Link: https://drive.google.com/file/d/1anZDvW-zTK52fi4HEZLxqO-3OlE2e1Wl/view — "the ready-made 0.5 disc, HD textures in PCSX2's folder layout, the Extra Memory game setting, START HERE.txt, patch notes and checksums." The ready-made disc is a complete modded copy of the commercial game. **Downloading this means downloading the commercial game itself. Do NOT get it this way.** Its checksums, for identification only: disc SHA-256 `cc2312c1909cec438b8971133445eb7e2bfc7eecf03bdd0fed01cbefd7134541`, all-in-one ZIP SHA-256 `9b0c94b67b2ddd2415a6dddfe1f4385db64461541770d52525a81b984036ba2f`.
2. **Mod Manager + Editor 0.5, GitHub release.** Link: https://github.com/Jasonafex/urban-reign-redux/releases/tag/v0.5.0 — "build the tested release from your own Urban Reign (USA) ISO and choose your packs." The Mod Manager is free, needs no sign-in, and "the shared patch reuses unchanged data from the player's ISO instead of redistributing it." With no extra fighter packs, the build is byte-identical to the tested 0.5 release. **This is the lawful route — but only for someone who already owns the original USA game.** The game ISO and PCSX2 are not included, and the builder refuses non-USA editions.

The project also has a **Mod Manager zip** checksum for identification: `ad222bad1d0cd1a03672bc88e0132e63ceb15ce0129a406b69b925ceb2f0f6d6`.

### 3.5 Licence and terms — what was actually found

- **No LICENSE file exists in the repo.** The root holds `.gitignore`, `CHANGELOG.md`, `PUBLISHING.md`, `README.md`, `docs/`, and `runtime/` only.
- **README's own terms line:** "This repository hosts the release, website and setup support. It does not include the editor's complete source. **No blanket license is granted to third-party game or character assets.** Not affiliated with or endorsed by the original game's publisher."
- **So:** the mod tools are distributed freely by their author, but there is **no open-source licence stated** for the mod code, the editor's full source is not in the repo, and **no permission is granted over the game's own assets or the guest characters** (Tekken, Street Fighter, GTA, Resident Evil, and the rest). Nothing in Redux grants Western Heart any right to use Urban Reign's or Tekken's files.
- **Publishing plans (not done):** a Nexus Mods listing is planned but not created (the workflow "has not been run; it requires your accounts and initial Nexus file ID"); a TekkenMods listing was investigated and the request "has not been sent". Source: `PUBLISHING.md` in the same repo.
- **No paywall and no login bypass were involved in finding any of this.** The GitHub repo, release page, and website are all public, no sign-in. The Google Drive all-in-one link is public too — it is refused here because of what it contains, not because of access.

### 3.6 Verdict for Western Heart

- **Do NOT download the all-in-one package.** It is a ready-made disc — commercial game files. Blocker, stated plainly: the package's own description says it includes the tested 0.5 disc.
- **The Mod Manager route is lawful only with an owned USA ISO.** The repo already holds the USA ISO as release `urban-reign-iso-v1` plus the full extracted teardown, so Redux's disc adds nothing Western Heart does not already have.
- **What Redux is actually worth to this project is its methods and measurements, not its disc:** grounded idles and skeleton repairs (feet on the floor, no floating/sinking — the same class of fault as the Piece-1 King Tyrant sink), Tekken 8 stances, string-connection fixes (mid-string knockdowns → heavy staggers), the Player 2 select freeze fix, the expanded stage select, the multiplayer camera controls, and the mouth-animation pilot. Those are techniques to study and rebuild in our own code, the same way the repo's own teardown is used.
- **It cannot run here.** The Mod Manager and Editor are Windows `.exe` files that build a PS2 disc for PCSX2. Nothing in Redux runs on this Linux VM or in the web game, and its ISO cannot be wired into the web build.
- **Do not confuse it with the other project:** `thiagordsfx/urban-reign-recomp` is a separate PC recompilation port of Urban Reign (GPL-3.0, per its listing), not Redux. It also needs the player's own PS2 disc image (USA SLUS-21209). Found in GitHub code search; its README was not read this pass, so no claim is made about its state beyond that.

### 3.7 Where I looked for Redux

- GitHub code search for "Urban Reign Redux" → found `Jasonafex/urban-reign-redux` (CHANGELOG.md fragment first hit).
- Repo root, `README.md`, `CHANGELOG.md`, `PUBLISHING.md`, `runtime/README.md`, `docs/` and `runtime/` listings — all read via the GitHub connector.
- Release page `v0.5.0` and project website `https://jasonafex.github.io/urban-reign-redux/` — both read as page text.
- Web search "Urban Reign Redux Jasonafex mod PCSX2" — confirmed the same project, plus YouTube/Facebook coverage (gameplay videos, install guides) that add nothing beyond the author's own pages.
- Not visited and not needed: no piracy or leak site, no paywall, no login.

---

## 4. What is still UNMEASURED

1. **Stage names.** The repo has 7 stage PPKs by id only (`stage003/004/020/028/029/030/031`); no place names are recorded for them, and stage geometry is not decoded. Public sources give kinds of places, not a full list.
2. **Mission contents.** 256 `.bin` definitions + 100 mission PPKs exist, but no field layout is decoded — mission objectives, enemy counts, and partner assignments per mission are unmeasured.
3. **Exact audio counts.** `teardown/urban-reign/audio/` and `teardown/urban-reign/sound/ok_adx/adx/` each list 1,000 items, which is the GitHub API's listing cap — the true counts are "at least 1,000 each", and the coverage matrix's "1,033 audio files extracted" does not reconcile with that. Exact counts unmeasured.
4. **Per-fighter identities.** Which PPK is Brad Hawk, which are Paul Phoenix and Marshall Law, which is Glen Kluger — all OWNER-pending. No identity was guessed here.
5. **Whether the 72 game-side GLBs and the 31 moveset JSONs load and play today.** File-existence was checked by listing, not by loading. `CANON-CONVERSION.md` cites a 72/72 resolution check from its own PR (2026-10-21); no fresh load test was run this pass.
6. **Repo-wide text search.** The code-search tool cannot scope to this repo, so "Urban Reign" mentions in `docs/` and `game/js/` beyond the ones listed in §1.5 are not proven absent.
7. **Redux's editor source and any licence beyond the README line.** The editor's complete source is not in the repo (author's own statement), and there is no LICENSE file — so no reuse terms beyond "no blanket license is granted" can be stated.
8. **The recomp project.** `thiagordsfx/urban-reign-recomp` was found but not read beyond search fragments — its state, buildability, and exact licence terms are unmeasured.
9. **Frame data / timings.** No Urban Reign frame data (startup, active, recovery, damage numbers per move) was measured this pass — the manual gives the shape of the systems, not numbers. The repo's 484 named moves are names attached to clips, not a frame-data table.

---

## Sources

**Repo files read this pass (all in `mhvnsnt/western-heart`):**
- `teardown/urban-reign/TEARDOWN.md`, `WIRING-INVENTORY.md`, `BANK-COMPLETION.md`, `CANON-CONVERSION.md`, `PHASE6-STATE.md`, `UI-SYSTEM.md`, `PPK-FORMAT.md`, `VGS-FORMAT.md`, `docs/URBAN-REIGN-TEARDOWN.md`, `docs/stage-candidates.txt`, `audio/README.md`, `models/ROSTER.json`, `textured-models/MANIFEST.json`
- `teardown/TEARDOWN-COVERAGE-MATRIX.md`, `teardown/TEARDOWN-STATUS.md`, `teardown/TEARDOWN-SOURCES.md` (Urban Reign rows only)
- Folder listings: `teardown/urban-reign/` (all 18 subfolders, level by level), `game/assets/movesets/`, `game/assets/models/street-reign/`, `game/assets/anim/`, `moveset-library/movesets/`, `moveset-library/movesets-v2/`, `moveset-library/animations/`
- Prior audit files on disk: `~/workspace/western-heart-audit/AUDIT.md`, `PLAYTEST-PIECE1.md`, `PIECE1-DIAGNOSIS.md`, `TEARDOWN-PART-D-ROSTER-ARCHIVE.md` (§5, archive.org section)

**Urban Reign Redux (all read, nothing downloaded):**
- https://github.com/Jasonafex/urban-reign-redux (README.md, CHANGELOG.md, PUBLISHING.md, runtime/README.md, docs/ and runtime/ listings)
- https://github.com/Jasonafex/urban-reign-redux/releases/tag/v0.5.0
- https://jasonafex.github.io/urban-reign-redux/

**Urban Reign public sources:**
- Tekken Wiki — Urban Reign: https://tekken.fandom.com/wiki/Urban_Reign
- Urban Reign (USA) Manual, full text (Namco, 2005): https://archive.org/stream/ps2_Urban_Reign_USA/Urban_Reign_USA_djvu.txt
- Namco "goes gold" press release: https://uat.gamedeveloper.com/press-release/urban-reigntm-fights-its-way-to-gold
- Hardcore Gaming 101 — Urban Reign: https://www.hardcoregaming101.net/urban-reign/amp/
- The Games Database — Urban Reign: https://thegamesdb.net/game.php?id=9836
- Combat mechanics overview (forum FAQ): https://stinger.actieforum.com/t408-urban-reign
- SuperCheats FAQ/Walkthrough: https://www.supercheats.com/playstation2/walkthroughs/urbanreign-walkthrough06.txt

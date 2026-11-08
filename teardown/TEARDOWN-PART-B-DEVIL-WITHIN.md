# Teardown research, part B: Tekken 5 Devil Within ("god within") hunt + HeartMind mode

**Date:** 2026-11-07 (evening CST)
**Repo:** `mhvnsnt/western-heart`, HEAD `3334ebf` (merge PR #1639)
**Method:** read-only. Repo files read through the GitHub connector and the raw file service; local workspace searched with `grep`; public Devil Within facts from Tekken Wiki and Tekkenpedia (links below). No game code edited, nothing pushed, no commercial game file downloaded, no ISO/ROM/code file fetched from anywhere.
**Gender rule used:** Pantera is male (he/him); every other fighter is named only, no guessed pronouns.

---

## 1. THE HUNT — does decoded Devil Within data exist?

### Short answer

**Partly, and only at file-name level. The names of the Devil Within files were decoded from the Tekken 5 disc. The contents were not.**

What exists in the repo is a survey: the disc was listed, the motion-file manifest was pulled out of one archive (`TK5DATA2.BIN`), and the Devil Within file names were found in that list. No Devil Within animation bytes, stage geometry, boss AI, enemy tables, wave tables, Devil Gene meter numbers, ranking thresholds, or moveset data were ever extracted. The repo's own docs say this plainly, in three places: "mapped for the RE bench, not yet extracted", "0 hits — DW stage/boss data in binary formats, queued for RE bench", and Tekken 5 sits at #16 QUEUED in `tools/re/QUEUE.md` at ~15%.

So if Jay's "god within stuff is decoded somewhere" means *decoded file contents*, that does not exist in the repo or in this workspace. If it means *the file names were found and listed*, that does exist — see below.

Also: the phrase **"god within" appears nowhere** in the repo copy searched (game code, WORKLOG, AGENTS, CANON, DESIGN — zero hits). The mode is always called "Devil Within" in the repo.

### Every file that matters, with exact paths

#### A. The Devil Within data files (repo — the core of the hunt)

| File (repo path) | What it is | What it covers | Origin |
|---|---|---|---|
| `teardown/tekken5/DEVIL-WITHIN-DATA.md` | The Devil Within data map | Lists every DW file name found in the `TK5DATA2.BIN` romD manifest: `gym_dw_nog00.dat`, `gym_dw_raribxk.dat`, `gym_dw_rarixk.dat` (enemy/boss animations), `gym_djin_newhane00.dat` … `newhane03.dat` (Devil Jin transformation — "hane" = wings/feathers, the black-feather disintegration visual), `dwfkao00.dat`, `dwhadoh00.dat`, `dwup00.dat` (DW-specific data, contents unknown), `stg00/01/02/04.dat` (stage files; `stg03` absent), `moj_stg02.dat` (stage 2 text), character sound `c30dvj.dat` (Devil Jin), `c10jin.dat` (Jin), `c15hei.dat` (Heihachi clones), `c21jac.dat` (JACK). Then lists what is mapped-but-NOT-extracted: DW stage geometry (5 stages), boss data, enemy data, Devil Gene meter mechanics, gem/Force systems, ranking, DW UI/menus. Extraction log: 2026-10-23, 3 `gym_dw_*` + 4 `gym_djin_*` + 3 `dw*.dat` + 4 `stg*.dat` found; 0 DW markers in `TK5DATA0/1/3`. | Surveyed 2026-10-23 from the T5 PS2 disc image by the repo's own survey tools (see C below). File names only — no file contents. |
| `teardown/tekken5/INVENTORY.md` | Tekken 5 disc file inventory | The whole disc, 10 files: `SYSTEM.CNF` (57 B), `IOPRP300.IMG` (278 KB), `IRXARC.BIN` (305 KB), `SLUS_210.59` bootloader ELF (689 KB, 522 strings, loads `TK5DATA3.BIN`), `TK5DATA0.BIN` (2.07 GB, main data, proprietary binary, no ASCII filenames), `TK5DATA1.BIN` (1.30 GB), `TK5DATA2.BIN` (244 MB, romD archive — magic `romD` @0, CRLF filename manifest, 498 `.dat` motions, 109 char codes, 21× `BDPK` markers), `TK5DATA3.BIN` (423 MB), `TK5DATA4.BIN` (179 KB MIPS ELF), `TK5DATA5.BIN` (423 MB, duplicate of TK5DATA3). States the ISO was deleted after verified extraction. | Same 2026-10-23 survey. Inventory only — no BIN files are in the repo. |
| `teardown/tekken5/TEARDOWN.md` | Tekken 5 teardown overview | Role in the chimera build (Devil Within source + 32-fighter roster movesets + stages), disc structure, where each kind of data lives, container formats (romD magic, `BDPK` markers; file-table → data-offset mapping NOT yet reversed), the DW file list, what is blocked and why (romD extraction blocked on the file-table mapping; `TK5DATA0/1/3` formats need MIPS reverse engineering of the loader), and next steps (RE bench → extract the 498 motions → wire into `moveset-library/`). | Same survey, 2026-10-23. |
| `teardown/tekken5/t5_motion_manifest.txt` | The 498 named motion files | The full filename list pulled out of `TK5DATA2.BIN`. DW lines (verified by reading the file): `gym_djin_newhane00–03.dat`, `gym_dw_nog00.dat`, `gym_dw_raribxk.dat`, `gym_dw_rarixk.dat`, `gym_dwfkao00.dat`, `gym_dwhadoh00.dat`, `gym_dwup00.dat`, `gym_dwup_hei.dat`. Also directly useful and DW-adjacent: `gym_init_obj_boss1/2/3/5.dat`, `gym_init_obj_devil.dat`, `gym_init_obj_jin.dat`, `gym_init_obj_mon_power1/2.dat`, `gym_init_obj_mon_speed1.dat`, `gym_init_obj_mon_standard1/2.dat`, `gym_init_obj_mon_tricky1.dat` (monster init objects), `gym_ikt5_*_mon.dat` (26 files, `_mon` suffix), `gym_kmb1_*.dat` (39 files — machinegun/shotgun/shoot moves, the Gun Jack boss set), `gym_kob2_*.dat` (29 files — fly/fire/warp/tail/horn moves, the Ogre boss set), `gym_ozb3_*.dat` (36 files — fire/homing/warp moves, the Ogre set), `gym_ikdv_*.dat` (52 files — Devil Jin: beams, `dv2kam2`, jumps, turns). **These are names only. No motion bytes are in the repo.** | Extracted 2026-10-23 from `TK5DATA2.BIN`. |
| `teardown/tekken5/t5_char_codes.txt` | The 109 character codes with file counts | Counts per code, including the DW ones: `dw` 3, `djin` 4, `ikdv` 52, `kmb1` 39, `ozb3` 36, `kob2` 29, `ikt5` 26, `init` 21. The code → fighter mapping is itself listed as RE-bench work (not done). | Same extraction. |
| `teardown/tekken5/STAGES.md` | Tekken 5 stage list | 16 versus stages (Burnt Out, Cathedral — unlockable by Devil Within completion — City at Sunset, Dragon's Nest, Final Stage, Hell's Gate, Moonlit Wilderness, Pirate's Cove, Polar Paradise, Poolside, Secret Garden, Space Colony, Urban Jungle, Waterfall, Winter Palace), marked "documented from public game data — verify against disc file inventory" and "(count/names to verify — T5 has 15–16 versus stages)". DW stages (5): G Corp lab, medical wing/child's bedroom, ancient ruins, alien spaceship, deeper spaceship. No stage geometry anywhere. | Public game data, not disc-decoded. |
| `teardown/tekken5/ROSTER.md` | Tekken 5 roster (32 fighters) | 32 fighters, Devil Jin marked "unlockable (Devil Within completion)", Jin marked "Devil Within playable character", Jinpachi Mishima as unplayable boss. Marked "documented from public game data — verify against disc file inventory"; the disc-verification section is empty. | Public game data, not disc-decoded. |

#### B. The tools that did the survey (repo — own code, reusable)

| File (repo path) | What it is |
|---|---|
| `teardown/tekken5/tools/iso9660_extract.py` | Own-code ISO9660 reader (stdlib only; pycdlib misdetects PS2 ISOs as UDF). Extracted the 10 disc files. |
| `teardown/tekken5/tools/t5_survey.py` | Own-code survey tool (stdlib only; disc layout + format fingerprinting + exe string scan). Produced the manifest and the inventory. |
| `tools/re/QUEUE.md` | The reverse-engineering queue. Tekken 5 is #16, QUEUED, ~15%: "romD file-table RE (`TK5DATA2.BIN` → 498 motion `.dat`s) + `TK5DATA0/1/3` container RE + `SLUS_210.59` loader (MIPS). Survey done 2026-10-23; DW anims + motion manifest in `teardown/tekken5/`." Urban Reign is the proof run (#1, in Ghidra now); Tekken 6 PSP is #2 (active). |

#### C. UI material (repo)

| File (repo path) | What it is |
|---|---|
| `teardown/tekken5/ui/UI-EXTRACTION-STATUS.md` | UI sweep status, 2026-10-23. Says T5 menu art is TIM2 textures inside the game data files; 6 TIM2-extracted PNGs already sit in `game/assets/ui/` (`tim_0947_off_001E6950.p000.png` etc.) plus `title-bg.png`, landed via PR #811 — proof the TIM2→PNG path works. Pull list (once the ISO lands): title/menu background art, 32 character-select portraits, versus screen art, HUD elements, font glyphs, navigation sounds. "The Devil Within mode's UI lives here too." |
| `teardown/tekken5/rigging-reference/tekken5-hand-arm.md` | Hand/arm rigging reference (not DW-specific). |

#### D. Where Devil Within lives in the game's own code (repo — already wired, see §2)

`game/js/brawler.js` (1,469 lines), `game/js/heartmind.js` (569 lines), `game/js/heartmind-campaign.js` (225 lines), `game/js/fighter.js` (Soul Surge form), `game/js/episodes.js` (369 lines), `game/js/story-endings.js` (226 lines), `game/story/heartmind-trial.ink` / `.yarn` / `.json`, plus menu wiring in `game/js/menus.js` and `game/js/mainmenu.js`. These are Western Heart's own code built from public Devil Within research (Tekkenpedia / Tekken Wiki / GameFAQs, per WORKLOG.md) — not from decoded disc data.

#### E. Workspace (local, `~/workspace`)

| Path | Result |
|---|---|
| `~/workspace/western-heart-fix/repo/` | A partial copy of the repo at the same HEAD (`3334ebf`). Contains the game code above and WORKLOG.md, but NO `teardown/`, `docs/`, `moveset-library/`, or `game/data/` folders. Grep for "devil within" hits: `WORKLOG.md`, `game/index.html`, `game/js/brawler.js`, `game/js/fighter.js`, `game/js/heartmind-campaign.js`, `game/js/heartmind.js`, `game/js/mainmenu.js` — all of them are the game's own code/docs, not decoded DW data. |
| `~/workspace/devil-within-teardown.md` | **Does NOT exist.** This is the design doc cited by `DEVIL-WITHIN-DATA.md` and `TEARDOWN.md` ("Design research … `~/workspace/devil-within-teardown.md` (2026-10-22)"). It is referenced but not on this machine. |
| `~/workspace/tekken5-extract/` | **Does NOT exist.** Cited by `UI-EXTRACTION-STATUS.md` as the Oct 23 extraction workspace (`dl_segments.sh`, `t5_survey.py`). Not on this machine. |
| `~/workspace/western-heart-audit/` | No "devil within" / "devilwithin" / "god within" hits at all. |
| Full-workspace text sweep | COMPLETED after this report's first draft. All text files (`*.md/*.txt/*.json/*.js/*.py/*.html`) in `~/workspace` were searched. New hits beyond the repo copy: (1) `~/workspace/self_improvement/staging/memory/.../MEMORY.md` copies — memory entries mentioning the hunt, not data; (2) `~/workspace/hold-none-work/`, `land-push-work/`, `land-everything/`, `repo-push-work/` audit maps (`per-file-map.md`, `root_Bannon.json`, `dir_drive-storage_models.json`) — a spec-pattern note ("The Devil Within design spec … is pulled only as a generic story-mode shape … Archives, data, and any game files are skipped") and raw GitHub API dumps of another repo, no DW data; (3) sibling teardown reports `TEARDOWN-PART-A-TEKKEN-MODES.md`, `TEARDOWN-PART-C-URBAN-REIGN.md`, `TEARDOWN-PART-D-ROSTER-ARCHIVE.md` — mentions only, plus two leads followed up in the addendum below. **No decoded Devil Within data was found anywhere in the workspace.** |

### Addendum — leads from the completed sweep (2026-11-07 ~19:00 CST)

Two repo docs found through the sibling teardown parts, plus the official manual:

- **`docs/modes/TEKKEN-MODES-RESEARCH.md` §4 (Lane G, 2026-10-18)** — Tekken Force (T3) / Devil Within (T5), marked WIRED (2026-10-19, Stream 4). Its DW summary: 5 stages, enemy groups, door/key puzzles, stage bosses, Devil Gene meter (transform at full meter — more power, costs health). Its HeartMind note: "clone-then-proprietize. The skeleton is Devil Within's (5 stages → enemy waves → stage boss, transform meter); the flesh is Western Heart." Phase 1 (shipped): sequential inner battles, each wave a single-round fight vs an echo with HP carry-over + soul-ember restores; stage = 3 echoes + warden, stage 5 = shadow self only. Phase 2 (when the T5 teardown lands): `HM_TEARDOWN` consumes enemy AI patterns, wave tables, and door systems 1:1 for simultaneous multi-enemy density.
- **`docs/modes/HEART-AND-MIND-INSIDE.md`** — the HeartMind design doc. DW structure "researched, to be cloned 1:1 when teardown lands" (from Tekkenpedia / Gamespot T5 bonus preview): 5 stages each unlocked by defeating the stage boss; navigate the stage, fight enemies in groups, minor key quests / door puzzles; **limited button system: Block, Jump, Punch, Kick — but the character's real special moves still work**; Devil Gene meter: full meter → Devil Jin, far more powerful, laser attacks, consumes health; stage themes escalate industrial → industrial → tomb ruins → alien/mystical → alien/mystical at higher complexity; bosses in order. Its mapping table (DW → HeartMind) matches §4 of this report. It also says Phase 1 is "Real, playable, wired end-to-end" — that is the doc's claim, not a watched playthrough; live proof is still owed (see §3).
- **Tekken 5 (USA) official manual, Devil Within section** — freely viewable full text at https://archive.org/stream/ps2_Tekken_5_USA/Tekken_5_USA_djvu.txt (OCR text, noisy in places, readable). Measured facts it adds, in the manual's own words in substance: "As Jin Kazama, defeat a swarm of opponents and uncover the truth of his past and the devil gene." How to play: "Fight your way toward the bottom of the lab by defeating every opponent in the area. A boss fight awaits you at the end. Defeat the boss to complete the stage. The Result screen is displayed when you complete a stage, followed by the Save screen." HUD: Health (runs out = game over), Devil Gauge ("Enter a command when the meter is full to transform Jin into Devil Jin"), Force ("cash just like fight money. Use it to buy items in the Customize screen"). Devil Jin: "press the L1+Triangle buttons when the Devil Gauge is full. Devil Jin's attack power is stronger than usual, but his health declines with time, so use this power wisely." Pause menu: Cancel, Camera Type, Vibration, Restart (stage from the beginning), Return to Devil Within Title. Game over: select Retry on the Game Over screen to continue. The left analog stick works in Devil Within. Mode select lists it as "TEKKEN: DEVIL WITHIN — Play as Jin Kazama in a 3D action-adventure game." Save note: entering Devil Within (or Arcade History) enters save mode — save first, unsaved data is lost; Tekken 5 needs 57 KB on a memory card.

#### F. Places checked with nothing found

- `docs/` top level (136 entries): no Devil Within file; `docs/western-heart/` holds only `IMPORTERS.md`, `INVENTORY.md`, `headless-boot.png`, `inventory.json`.
- `moveset-library/` top level: `MOVES-LIBRARY.md`, `MOVESET-EDITOR-RESEARCH.md`, `UI-DESIGN-SPEC.md`, `animations/`, `customization/`, `movesets/`, `movesets-v2/` — no DW-named entries.
- GitHub code search (`search_code` via the connector) returned 0 results even for "heartmind", which definitely exists in the repo — that search tool is unreliable here, so this hunt relied on directory listings, direct file reads, and local greps instead. GitHub's web code search needs a sign-in, so it was not used.
- No ISO, BIN, `.dat` motion file, or extracted DW content exists in the repo or workspace. The repo docs record that the T5 ISO was downloaded once (2026-10-23, md5-verified), surveyed, then deleted; the source is recorded in the repo docs as an Internet Archive item. No download link is given here — nothing outside the repo/workspace was fetched for this hunt.

### What "decoded" actually means here — plain words

- **Decoded:** the list of file names inside one disc archive, and the disc's file list. That is real and usable as an index.
- **NOT decoded:** what any of those files contain. The archive's file-table mapping (which bytes belong to which named file) was never reversed, and the big data archives (`TK5DATA0/1/3`, 2.07 GB + 1.30 GB + 423 MB) are proprietary binary with no filenames at all. DW stage geometry, boss AI, enemy data, meter numbers, and ranking numbers all live in those unreversed formats. The repo's own next step for all of it is "RE bench".

---

## 2. WHAT DEVIL WITHIN IS (measured base, from public sources)

Sources: Tekken Wiki, "Devil Within (Mode)" — https://tekken.fandom.com/wiki/Devil_Within_(Mode) ; Tekkenpedia, "Devil Within" — https://eng.tekkenpedia.com/wiki/Devil_Within/ ; Tekkenpedia, "Tekken 5" — https://eng.tekkenpedia.com/wiki/T5/ . All facts below come from those pages.

- **What it is:** a 3D action-adventure side game bundled with Tekken 5 (PS2, 2005), replacing the Tekken Force modes of Tekken 3/4. Unlike Tekken Force, the player cannot pick a character — it is Jin Kazama only — and it has a storyline. The official manual calls it "a 3D action-adventure game" and says: "As Jin Kazama, defeat a swarm of opponents and uncover the truth of his past and the devil gene." The manual's how-to-play: "Fight your way toward the bottom of the lab by defeating every opponent in the area. A boss fight awaits you at the end. Defeat the boss to complete the stage. The Result screen is displayed when you complete a stage, followed by the Save screen."
- **Story:** after the tournament, Jin hears Jun Kazama may be alive and goes to a G Corporation lab (run by the Medicern subsidiary) to find her. Jin fights super-soldiers, robots, JACKs, a modified Gun Jack, and Heihachi clones in the lab; loses control of the Devil Gene as the descent goes deeper; finds the lab is built over ancient ruins (Ogre's temple); fights True Ogre, then an energy ball (the ruins' seal), then True Ogre again and Monstrous Ogre. Jin never finds Jun.
- **Stages (5), all indoors, multi-tiered hallways and connected passages, with platforming and door puzzles that get harder as the game goes on:**
  1. G Corp lab — boss: Modified Gun Jack.
  2. Medical wing, including a child's bedroom (sky-blue walls, clouds, yellow stars, big fluffy sheep on the floor) — boss: Heihachi clones. One clone first, then three at once.
  3. Ancient ruins (Aztec temple) — boss: True Ogre.
  4. Alien spaceship (grey/green, mystical) — boss: Soul Sphere, a ball of energy.
  5. Same spaceship theme, harder — boss: True Ogre then Monstrous Ogre, both fought on the same health bar. Monstrous Ogre is taller, more yellow than green, and adds whirlwinds, strong stomps, and powerful sweeps.
- **Enemies (minions):** JACKs, Jack-5, G Corp soldiers, Ogre's mutants. Per the repo's DW data doc, the mutants have names: Adam, Eve, Duke, Regal, Jill. Defeated enemies drop Force (fight money, spent in Customization Mode) or a healing pick-up.
- **Moves:** Square punch, X kick, Triangle block, Circle jump; Square+X throw; Square, Square, X combo; X+Circle combo kick; Square+Circle uppercut; L1+Square 5-hit combo into rising punch; L1+X jump kicks; Square+Circle, X pop-up into kick; R1+Circle forward roll; R1+down, Circle back flip. Double jump (press jump again mid-air) for extra distance. Forward roll and back somersault also listed. Jin fights in Mishima Style Fighting Karate, with some moves from Traditional (Kyokushin) Karate (Evil Intent, Spinning Flare Kick, Double Lift Kick, Thrusting Uppercut).
- **Devil Gene meter / Devil Jin:** when the Devil Gauge is full, L1+Triangle transforms Jin into Devil Jin (press again to change back). The official manual confirms the input (L1+Triangle at full gauge) and the trade-off: "Devil Jin's attack power is stronger than usual, but his health declines with time, so use this power wisely." Devil Jin is much stronger, has advanced Mishima techniques (Hell Scraper, Roundhouse to Triple Spin Kicks) and laser attacks that can hit several enemies at once — but the form drains Jin's health, so it must be used sparingly. Enemies killed in devil form disintegrate into black feathers. The laser is also needed for progress: on stage 4, a door made of crumbled rocks with a red Devil Gene symbol sits across a gap that cannot be crossed — Devil Jin must shoot the rocks with the laser until they break, and a floating bridge forms (medium difficulty or higher). After beating Devil Within on medium difficulty and collecting all Evil Symbols, Devil Jin can be played through the whole mode by holding L2 + SELECT + R3 while selecting a stage or starting a new game; the Devil bar becomes the laser bar. The manual's HUD names the three on-screen meters: Health, Devil Gauge, and Force.
- **Items:** blue gems and red gems (healing pick-ups); 40 red Devil Symbols hidden through the five stages (8 per stage), which unlock customization items for Tekken 5 characters (for example stage 1: Jin wings, Feng claws, Law black mask, Christie Cleopatra headdress, King Armor King mask, Asuka kneepads, Marduk shirtless, Lee electric guitar; stage 5: Nina cat mask, Yoshimitsu bandit hood, Jack-5 exhaust pipes, Paul spiked shoulder pads, Jin demon mask, Kazuya windswept hair, Xiaoyu ponytail, Bryan ski mask). Symbols can sit above breakable objects.
- **Ranking:** after each stage, the player is ranked on time to finish, total damage, number of retries, Force collected, and more. The rank (S highest, then A/B/C) multiplies the Force collected. Exact rank thresholds: **UNMEASURED** — neither public page gives the numbers.
- **Unlocks for finishing Devil Within:** 1,000,000 G, the Cathedral stage, Devil Jin as a playable character, Devil Within stage select, Final Stage, Final Stage 2. After finishing once, stage select opens with difficulty choice, and a second playthrough lets the player collect the 500,000 G customization items via the red symbols. Devil Jin can also be unlocked without finishing Devil Within by finishing Time Attack with Jin or doing 200 arcade battles; Cathedral/Final Stage unlock the same way.
- **Other measured details:** stage 1 and boss-fight music is a remix of Jin's Tekken 3 theme; stage 3's theme was originally meant for Tekken 4's Jungle stage; Jin wears Devil Jin's clothes and gauntlets instead of his own in the mode (reason unknown); the clone Heihachis have serial numbers on their hakama (first clone "0025") and electronic metal cuffs, and no chest scar.

---

## 3. HEARTMIND TODAY — what it is in the game

HeartMind's in-game name is "The Heart and Mind Inside" (owner-locked name, 2026-10-19). It is the Devil Within-style mode of Western Heart. It is reachable from the menu: a "THE HEART AND MIND INSIDE" card ("a descent · beat-em-up", action `mode-heartmind`, `game/js/menus.js`) and a "HEART AND MIND WITHIN" entry in the main menu (`game/js/mainmenu.js`), which lazy-loads `game/js/heartmind.js` (`game/js/lazy.js`). No end-to-end live playthrough of HeartMind is on record in the files (the 2026-11-06 audit says the same for story mode generally); what follows is what the code says, not a played run.

### Flow (what happens when it runs)

1. Pick any fighter — not forced Jin. Any Western Heart fighter plays the descent with their own moveset (`game/js/brawler.js` header; `game/js/heartmind.js`).
2. Entry story beats play (per-fighter text), then the brawler takes over (`HeartmindController.start` → `playStoryBeats(story.entry, …)` → `_beginBrawler`).
3. Five inner stages, each with waves then a boss, in order: The Threshold → The Gallery of Masks → The Drowning Room → The Furnace → The Still Point.
4. On stage clear, the game records the highest stage reached per fighter and pauses 1.2 seconds before the next descent. On victory, the resolution beats play and the result screen says "PURIFIED". On death, a "THE DARK KEEPS WHAT IT CATCHES" beat plays and the game returns to the menu.
5. Between stages, roads connect the rooms (Threshold → Masks → Drowning → Furnace → Still Point), with a one-line walk description each — never a teleport.

### Stages, enemies, bosses (as coded)

| # | Stage (HeartMind name → game arena) | Waves (from `WAVE_TABLES` in `brawler.js`) | Boss |
|---|---|---|---|
| 1 | THE THRESHOLD → tong-nou | 3 waves: echoes ×2, ×3, then echoes ×2 + gunner ×1, brute ×1 + echoes ×2 | WARDEN (Modified Gun Jack analog: bruiser + heavy blockable projectiles, 380 HP, scale 1.35) |
| 2 | THE GALLERY OF MASKS → phantom-marketplace | 3 waves: echoes ×3, echoes ×2 + gunner ×1, then brute ×1 + echoes ×2, gunner ×2 + echoes ×2 | THE MASKS (Heihachi-clone analog: ONE mask first at 135 HP, then THREE at once) |
| 3 | THE DROWNING ROOM → palace-of-dreaming | 3 waves: echoes ×3, brute ×1 + gunner ×1, then echoes ×4, brute ×2 | THE DROWNED OGRE (True Ogre analog: teleports near the player, homing volley, fire-blast area attack, 520 HP, scale 1.42) |
| 4 | THE FURNACE → plains-of-chi-u | 3 waves: gunner ×2 + echoes ×2, brute ×1 + echoes ×3, then echoes ×4, brute ×2 + gunner ×1 | THE SOUL SPHERE (energy orb, 420 HP: contact damage, spawns monsters every ~6 s) |
| 5 | THE STILL POINT → octagonal-shrine | 1 wave (echoes ×3, brute ×1 + gunner ×1), then boss only | SHADOW SELF (the player's own fighter, darkened, power ×1.28, defense ×1.15, speed ×1.10, 460 HP) → on defeat, THE UNMASKED, a second form (320 HP, scale 1.28, same descent, no fresh health bar for the player) |

Enemy types in the brawler: **echo** (a roster fighter as an inner demon — dark tint, hollow name "ECHO OF …", real moveset), **brute** (slow, hunts throws), **gunner** (keeps distance, shoots blockable projectiles), plus the five bosses. At most 5 enemies alive at once. Enemies circle the player instead of lining up, and are clamped inside the fight zone so a kiting gunner cannot stall a wave forever.

### Progression and systems (as coded)

- **Difficulty ramp:** stage difficulty 0.45 → 0.55 → 0.65 → 0.75 → 0.90; between-wave health restore 0.30 → 0.30 → 0.32 → 0.32 → 0.35 (called "soul-ember restore" in the campaign module).
- **Healing pick-ups:** soul embers — a glowing pick-up that heals 22 HP, 35% drop chance from a defeated enemy (Devil Within's healing gems, renamed).
- **Transform:** the Nine-Soul Meter is the Devil Gauge analog. Full meter + transform input = SOUL SURGE FORM: a timed powered state, 25 seconds, no model swap, power ×1.45, speed ×1.15 (capped 3.8), defense ×1.20 (`fighter.js`, `startSurgeForm`). If the fighter has a model-swap transform, that runs instead; otherwise the surge form runs. The shadow boss also surges when its meter is full and the player is close.
- **Ranking:** per-stage S/A/B/C rank from time + damage taken (`brawler.js`, `_rank`): S if under 150 s and under 50 damage; A if under 240 s and under 120 damage; B if under 360 s; else C. Shown as "STAGE N CLEARED — RANK X". These thresholds are Western Heart's own numbers, not Devil Within's — Devil Within's real thresholds are **UNMEASURED** (see §2).
- **Records:** highest stage reached is saved per fighter (`heartmind_<fighter>`), and total clears saved (`heartmind_<fighter>_clear`), via the records system.
- **Stories:** deep written stories for Demonio, Doc Frank, Mariposa, Thor, and the nine souls (each built from CANON.md "Being purified of"); every other fighter gets a generic frame built from roster identity. Before the stage-5 boss, a Shrine terminal segment ("Shrine体系") reads the descending soul. Each stage has its own story beat (masks / drowning / furnace).
- **Campaign layer** (`heartmind-campaign.js`): roads between stages, party switching between fights only (never mid-fight — each member keeps their own stage/wave/HP progress), a stage journal (one record per cleared stage per fighter), ragdoll contexts (launch, KO, wall splat, floor drop — HeartMind/adventure only), and a story-engine adapter that dynamically loads Yarn or Ink dialogue with a fallback to the built-in beats. The Ink/Yarn loaders (`ink-loader.js`, `yarn-parse.js`, vendored inkjs 2.4.0 MIT) exist; the heartmind-campaign header says PR #1044 (Yarn parser + Ink loader) was still open, so the adapter returns null when the engines are absent and the built-in beats are used.
- **Story scripts** (`game/story/`): `heartmind-trial.ink` (1,262 bytes), `heartmind-trial.yarn` (1,338 bytes), `heartmind-trial.ink.json` (2,211 bytes), plus a `demo/` folder. All three are the same short trial: a crossroads, a Trader, a Trial gate, five rooms named, the shadow self waiting at the Still Point, "Named. Faced. Put down." — a small branching intro, not the full descent.
- **Episodes** (`game/js/episodes.js`): a separate mode, "CHARACTER EPISODES" (menu card, action `mode-episodes`): per-fighter chapter ladders with story beats and fights, climbing to the shrine, ending in a shadow-self fight; deep canon first, generic frame for the rest. Endings live in `game/js/story-endings.js` and play from a "WATCH ENDING" button on the clear screen (`game/js/modes.js`).

### What works vs what is doc-only

- **Working code (read, not played):** the full brawler engine (`brawler.js`, 1,469 lines: movement, camera, waves, bosses, AI, projectiles, embers, ranking, throw locks, zone clamping), the HeartMind controller and stories, the campaign layer, menu wiring, and the transform/surge form. Tests exist: `game/tests/brawler-sim.test.mjs` (209 lines), `brawler-surge.test.mjs` (152 lines), `heartmind-campaign.test.mjs` (127 lines).
- **Doc-only / not yet real:** the teardown seam — `HM_TEARDOWN` in `heartmind.js` is an empty placeholder (`ready: false`, `enemyAi: null`, `waveTables: null`, `doorSystems: null`), waiting for the teardown lane to deliver Devil Within's exact mechanics, at which point the wave/boss builders consume them 1:1. The wave tables, enemy AI patterns, boss behaviours, and rank thresholds in the brawler today are Western Heart's own inventions modeled on public Devil Within descriptions — not measured from the disc.
- **No live proof:** no playthrough of a HeartMind descent (menu → pick → stage 1 → boss → stage 5 → PURIFIED) has been watched or recorded in the files checked. The Piece 1 playtest (2026-11-07) covered Versus/Arcade only, not HeartMind. Whether the brawler actually runs on the live build is **UNMEASURED** — it needs a headed playthrough, the same as Piece 1.

---

## 4. MAPPING (draft only, no code) — Devil Within onto HeartMind

How the measured Devil Within design maps onto HeartMind in Western Heart's own code. "Carries over" = already in the game, from public research. "Western Heart's own" = invented for this game. Anything not measured is marked **UNMEASURED**.

| Devil Within (measured) | HeartMind today | Status |
|---|---|---|
| 5 stages, boss at the end of each | 5 inner stages, boss at the end of each | Carries over — structure matches 1:1 |
| Stage order: lab → medical wing/child's bedroom → ruins → spaceship → deeper spaceship | Threshold → Gallery of Masks → Drowning Room → Furnace → Still Point (canon lands, not the lab) | Structure carries over; the places are Western Heart's own |
| Boss 1: Modified Gun Jack (powerful projectiles) | WARDEN (bruiser + heavy blockable projectiles) | Carries over as an analog |
| Boss 2: Heihachi clones — 1 first, then 3 at once | THE MASKS — 1 first, then 3 at once | Carries over 1:1, including the 1-then-3 trick |
| Boss 3: True Ogre (fire breath, flying, teleporting) | THE DROWNED OGRE (teleport, homing volley, fire blast) | Carries over as an analog |
| Boss 4: Soul Sphere (energy ball, contact damage, spawns monsters) | THE SOUL SPHERE (420 HP orb, contact damage, spawns monsters) | Carries over 1:1 in behaviour |
| Boss 5: True Ogre → Monstrous Ogre, same health bar, second form taller/stronger with whirlwinds, stomps, sweeps | SHADOW SELF → THE UNMASKED, second form, same descent | Carries over as an analog; the second form's exact moves (whirlwinds/stomps/sweeps) are **UNMEASURED** in HeartMind — the Unmasked is a stat-buffed shadow, not a measured Monstrous Ogre kit |
| Jin only, forced character | Any fighter, own moveset | Western Heart's own — deliberate change, owner-ordered |
| Enemies: JACKs, Jack-5, G Corp soldiers, Ogre's mutants (Adam/Eve/Duke/Regal/Jill) | Echoes (roster fighters as inner demons), brutes, gunners | Western Heart's own enemy set; the DW mutant names and their behaviour are **UNMEASURED** (names known from the repo doc, behaviour not decoded) |
| Free-roam 3D, multi-enemy waves, camera behind the fighter | Free-roam 3D, multi-enemy waves (max 5 alive), third-person camera | Carries over |
| Platforming + door puzzles, double jump, forward roll, back flip | Not present — no platforming, no doors, no double jump in the brawler | **Missing.** Devil Within's platforming/door systems are the `doorSystems: null` slot in `HM_TEARDOWN`. Whether HeartMind should add them is a design decision, not a measurement. |
| Devil Gene meter fills, L1+Triangle transforms into Devil Jin; form drains health; lasers hit many enemies at once | Nine-Soul Meter fills, transform input = Soul Surge Form (25 s, power ×1.45, speed ×1.15, defense ×1.20, no model swap, no health drain) | Analog carries over; the numbers differ — Devil Jin's fill rates, laser damage, and health-drain rate are **UNMEASURED** (listed as "not yet extracted" in `DEVIL-WITHIN-DATA.md`). HeartMind's surge has no health drain and no laser — that is Western Heart's own choice. |
| Healing gems (blue/red) dropped by enemies | Soul embers, heal 22, 35% drop chance | Carries over as an analog; the real gem heal values and drop rates are **UNMEASURED** |
| Force (fight money) dropped by enemies, spent in Customization | No Force in HeartMind | **Missing.** Devil Within's Force economy is listed as "not yet extracted". |
| Per-stage rank (S/A/B/C) from time, damage, retries, Force | Per-stage rank S/A/B/C from time + damage only (S <150 s & <50 dmg; A <240 s & <120 dmg; B <360 s; else C) | Rank letters carry over; the real thresholds and the retries/Force factors are **UNMEASURED** |
| 40 red Devil Symbols (8 per stage) unlocking customization items | No symbols, no collectibles in HeartMind | **Missing.** The symbol hunt is a whole Devil Within subsystem with no HeartMind equivalent yet. |
| Story beats after each boss (Jin's search for Jun) | Per-fighter story beats per stage + boss lines + resolution, plus the Shrine terminal at the Still Point | Structure carries over; the story is Western Heart's own (purification, shadow self) |
| Finishing unlocks: 1,000,000 G, Cathedral, Devil Jin, stage select, Final Stage 1/2 | Finishing records a clear per fighter; no unlocks gated on it yet | **Missing as a system.** What a HeartMind clear should unlock is a design decision. |
| Stage select + difficulty choice after first completion | No stage select, no difficulty choice in HeartMind | **Missing.** |
| Devil Jin playable through the whole mode via a button code (after medium + all symbols) | No equivalent | **Missing / not applicable** — any fighter can already play, so there is no locked devil form to unlock. |

### What the decoded files would change if the RE bench ever lands them

In priority order (the repo's own order, `DEVIL-WITHIN-DATA.md` §4):

1. **Jin's DW brawler moveset** (punch/kick/block/jump, simplified, distinct from versus) — would give HeartMind a measured base moveset instead of reusing versus movesets. Today: **UNMEASURED**, brawler reuses each fighter's versus moveset.
2. **Devil Gene meter + Devil Jin transformation data** (fill rates, laser damage, health drain) — would let the Soul Surge Form use measured numbers. Today: **UNMEASURED**.
3. **5 stage layouts** (rooms, breakables, gem/Force spawns, Devil symbol locations, boss arenas) — would give HeartMind measured rooms and the platforming/door systems. Today: **UNMEASURED**; HeartMind reuses versus arenas.
4. **Boss patterns** (Modified Gun Jack, Heihachi clones, True Ogre, Soul Sphere, Monstrous Ogre) — would replace the analog boss behaviours with measured ones. Today: **UNMEASURED**; the analogs are built from wiki descriptions.
5. **Ranking thresholds** (time/damage/retries/Force → S/A/B/C) — would replace HeartMind's invented thresholds. Today: **UNMEASURED**.
6. **UI layouts** (mode select, HUD, rank screen) — HeartMind menus must be rebuilt from these per the repo's menu law. Today: **UNMEASURED**; the UI sweep is at the TIM2-texture stage only.

### Files that could be wired in directly (max actual code/data, no new downloads)

These already exist and need no new acquisition:

- `teardown/tekken5/t5_motion_manifest.txt` + `t5_char_codes.txt` — the filename index. Directly usable as the key list the moment the romD file-table mapping is reversed; today they are the only decoded DW data that exists, and the DW/boss/monster filename groups in §1A are the exact wire-in targets (especially `gym_dw_*`, `gym_djin_*`, `gym_ikdv_*`, `gym_kmb1_*`, `gym_kob2_*`, `gym_ozb3_*`, `gym_init_obj_boss*`, `gym_init_obj_mon_*`).
- `teardown/tekken5/tools/iso9660_extract.py` + `t5_survey.py` — the survey tools themselves; rerunning them is the path to any further extraction, and they are already in the repo.
- `game/assets/ui/tim_*.png` + `title-bg.png` — the six TIM2-extracted T5 menu PNGs already in the game (PR #811); the proven TIM2→PNG path for any further T5 UI work.
- `game/js/brawler.js`, `game/js/heartmind.js`, `game/js/heartmind-campaign.js`, `game/js/fighter.js` (Soul Surge form) — the already-built HeartMind implementation; the `HM_TEARDOWN` seam in `heartmind.js` is the exact socket the decoded data plugs into when it exists.
- `game/story/heartmind-trial.ink` / `.yarn` / `.json` — the trial intro scripts, already in the repo.

Nothing else decoded exists to wire in. In particular: no extracted animation bytes, no stage geometry, no boss/enemy tables, no meter numbers, no rank numbers, and no ISO/BIN files — in the repo or in this workspace.

---

## 5. STILL UNMEASURED (the honest list)

1. **Every Devil Within file's contents.** Names decoded; bytes not decoded. Blocked on the romD file-table mapping and the `TK5DATA0/1/3` container formats (RE bench, Tekken 5 #16 QUEUED).
2. **Devil Within's exact mechanics:** enemy AI patterns, wave composition tables, platforming/door systems (the three `HM_TEARDOWN` slots), boss attack patterns and numbers, Devil Gene fill rates / laser damage / health drain, gem heal values and drop rates, Force values, ranking thresholds (including retries and Force factors).
3. **The code → fighter mapping** for the 109 char codes (`dw`, `djin`, `ikdv`, `kmb1`, `kob2`, `ozb3`, `ikt5` etc. are guesses from filenames, not confirmed mappings).
4. **The stage-file mapping:** which of `stg00/01/02/04.dat` is which Devil Within stage (stage IDs → DW stages is RE-bench work).
5. **The design doc `~/workspace/devil-within-teardown.md` (2026-10-22)** cited by two repo docs — not on this machine; its contents are unknown to this hunt.
6. **Whether HeartMind actually plays on the live build.** Code + tests exist; no live playthrough has been watched. A headed playthrough (menu → pick → stage 1 → boss → stage 5 → PURIFIED) is still owed, the same as Piece 1 was for Versus.
7. **The full-workspace text sweep** is now COMPLETE — no decoded Devil Within data anywhere in the workspace; the only new hits were mentions, memory copies, and audit maps (see §1E addendum). The two repo docs and the official manual it surfaced are now in the report.

---

## Sources

- Repo files (HEAD `3334ebf`): `teardown/tekken5/DEVIL-WITHIN-DATA.md`, `INVENTORY.md`, `TEARDOWN.md`, `STAGES.md`, `ROSTER.md`, `t5_motion_manifest.txt`, `t5_char_codes.txt`, `tools/iso9660_extract.py`, `tools/t5_survey.py`, `ui/UI-EXTRACTION-STATUS.md`, `rigging-reference/tekken5-hand-arm.md`, `tools/re/QUEUE.md`, `game/js/brawler.js`, `game/js/heartmind.js`, `game/js/heartmind-campaign.js`, `game/js/fighter.js`, `game/js/episodes.js`, `game/js/story-endings.js`, `game/js/menus.js`, `game/js/mainmenu.js`, `game/js/lazy.js`, `game/js/modes.js`, `game/story/heartmind-trial.ink`, `heartmind-trial.yarn`, `heartmind-trial.ink.json`, `game/tests/brawler-sim.test.mjs`, `brawler-surge.test.mjs`, `heartmind-campaign.test.mjs`.
- Local workspace: `~/workspace/western-heart-fix/repo/` (partial repo copy at `3334ebf`), `~/workspace/western-heart-audit/`.
- Prior audit files: `~/workspace/western-heart-audit/PLAYTEST-PIECE1.md`, `PIECE1-DIAGNOSIS.md`, `AUDIT.md`.
- Public: Tekken Wiki, "Devil Within (Mode)" — https://tekken.fandom.com/wiki/Devil_Within_(Mode) ; Tekkenpedia, "Devil Within" — https://eng.tekkenpedia.com/wiki/Devil_Within/ ; Tekkenpedia, "Tekken 5" — https://eng.tekkenpedia.com/wiki/T5/ ; Tekken 5 (USA) official manual, full text — https://archive.org/stream/ps2_Tekken_5_USA/Tekken_5_USA_djvu.txt .
- Also in the repo, found after the first draft via the sibling teardown parts: `docs/modes/TEKKEN-MODES-RESEARCH.md` §4, `docs/modes/HEART-AND-MIND-INSIDE.md`.

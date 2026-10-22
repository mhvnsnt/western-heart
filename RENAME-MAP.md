# RENAME-MAP — Western Heart Proprietary Universe Rename

**OPERATIONAL DOCUMENT — DELETE WHEN COMPLETE.**
Owner directive 2026-10-14: "rename ALL the files and make it proprietary to our universe."
When every teardown file is renamed and the game hooks up correctly, DELETE this file
so no one knows we renamed stuff. Self-contained; nothing else references it.

**Basis:** "I own all of those games that we did teardown files to." — Owner
**Rule:** Data stays real; names become Western Heart. The game must hook up to
renamed files correctly (not just renamed on disk).

---

## Universe Name Mapping

| Source Game | WH Universe Name | Rationale |
|-------------|------------------|-----------|
| Tekken 3 | `iron-legacy` | The legacy iron-fist tournament |
| Tekken 6 | `iron-storm` | The storm-era tournament |
| Tekken 7 | `iron-prime` | The prime-era tournament |
| Tekken 8 | `iron-apex` | The apex-era tournament |
| Tekken Tag 2 | `iron-tag` | Tag-team tournament |
| Virtua Fighter 5 | `virtual-soul` | Virtual arena fighters |
| Def Jam: Fight for NY | `underground-brawl` | Underground street brawl |
| Urban Reign | `street-reign` | Street reign brawlers |
| Street Fighter (all) | `dragon-strike` | Research only per SF directive |
| WWF No Mercy | `mat-kings` | Kings of the mat |
| WWE WrestleMania XIX | `mat-legends` | Legends of the mat |
| WWE 2K series | `mat-dynasty` | Dynasty-era wrestling |
| Dead or Alive 4/6 | `ninja-heart` | Ninja-heart fighters |
| Soulcalibur II/VI | `soul-blade` | Soul-blade weapons |
| Eastern Mind | `dream-walker` | Dream-walker adventure |

---

## Completed Renames

### 2026-10-14 — T3 Animation Merge (this task)
| OLD | NEW | Status |
|-----|-----|--------|
| `assets/anim/t3/king_on_pantera_leoman/*.json` | `assets/anim/iron-legacy/pantera/*.json` | PENDING |
| `teardown/tekken3/movesets/` | `teardown/iron-legacy/movesets/` | PENDING |
| `teardown/tekken3/animations/` | `teardown/iron-legacy/animations/` | PENDING |
| `lab/tools/t3_motion_bake.py` | `lab/tools/ironlegacy_motion_bake.py` | PENDING |

### Game files wired to renamed sources
| Game File | Sources From (renamed) |
|-----------|------------------------|
| `game/js/t3anims.js` (new) | `assets/anim/iron-legacy/pantera/*.json` (real T3 motion) |
| `game/js/fighter.js` (modified) | Real T3 clips replace procedural combat |
| `game/assets/*_moves.json` | `teardown/iron-legacy/movesets/` (real T3 frame data) |

---

## Still Needed (per game)

### iron-legacy (Tekken 3) — 100% complete ✅
- Nothing missing. 7 fighters, 15 stages, 8,556 textures, 3,247 moves, real anim clips.

### street-reign (Urban Reign) — ~95%
- **Have:** VGS cracked, 509 files, 1,033 audio files, 72 UI screens, 46 motion packs
- **Need:** DCM semantics, inner PPK geometry
- **Blocker:** Format reverse-engineering in progress

### mat-legends (WMXIX) — ~80%
- **Have:** Full extraction, 126 wrestler OBJs, 170 YANM anims, 2,690 CAW parts
- **Need:** ECD identity, base-ID generation, CAW.gci semantics
- **Blocker:** Watchdog lane active, needs Dolphin/browser for CAW.gci

### soul-blade (SCII) — ~60%
- **Have:** Xbox version extracted
- **Need:** PS2 filesystem RE (1.38GB ISO on release)
- **Blocker:** Owner decision: Xbox vs PS2 as primary

### iron-prime (Tekken 7) — ~40%
- **Have:** 5 King variants (T8 base, T8 S2, T3 legacy, T7 1P, Armor King)
- **Need:** Full 51GB game (never acquired)
- **Blocker:** No landing zone; TeraBox could receive via browser

### iron-storm (Tekken 6) — ~30%
- **Have:** 46 videos, ISO structure, 40-fighter roster, decrypted EBOOT
- **Need:** DATA401 models (384MB encrypted)
- **Blocker:** AES key needed; PPSSPP live dump is fastest path

### dream-walker (Eastern Mind) — ~20%
- **Have:** Game safe on release (549MB)
- **Need:** Full extraction (bitmaps, stage art, 3D, audio)

### iron-tag (TTT2) — ~15% → teardown in progress
- **Have:** 26/26 chunks on release `ttt2-7z-v1`, docs (59 fighters, 29 stages), STFS/GoD tooling (zarmanager pure-Python), custom XDVDFS parser (`tools/xdvdfs_reader.py`), surgical GoD pull tool (`tools/god_surgical.py`), STFS blob tool (`tools/stfs_blobs.py`)
- **Need:** 13.3GB reassembly (1/26 chunks, PAUSED for disk emergency — resume at <80%), then surgical extraction: GoD header + DataXXXX on demand → XDVDFS walk → per-fighter model/moveset pull. NO 27GB full extraction needed (surgical approach).
- **Blocker:** Disk emergency 2026-10-15 (was 95%, recovering). TeraBox upload blocked (needs owner sign-in for browser session).
- **Rename plan:** `teardown/tekken-tag-tournament-2/` → `teardown/iron-tag/`; extracted fighter data → `teardown/iron-tag/fighters/<fighter>/`; 59 fighters keep original names as donor refs (per ROSTER.md convention).

### ninja-heart (DOA4) — ~15%
- **Have:** 30/30 chunks on release (7.8GB)
- **Need:** Reassemble + extract
- **Blocker:** Sequenced after TTT2 (disk)

### soul-blade VI / ninja-heart 6 — ~10% each
- **Have:** Mechanics docs only
- **Need:** Game binaries (32GB / 50GB+)
- **Blocker:** Not on Archive.org; need owner source or stepdown

### mat-kings (No Mercy) — 100% complete ✅
### virtual-soul (VF5) — 100% complete ✅

---

## Rename Execution Order

1. ✅ **Phase 1:** iron-legacy (Tekken 3) — files this task touches
2. **Phase 2:** street-reign (Urban Reign) — game uses UR systems
3. **Phase 3:** mat-kings, mat-legends, mat-dynasty (wrestling)
4. **Phase 4:** iron-prime, iron-storm, iron-apex, iron-tag (other Tekken)
5. **Phase 5:** virtual-soul, underground-brawl, dragon-strike, ninja-heart, soul-blade, dream-walker

**Safety rules:**
- `git mv` (preserves history), never manual move
- Update ALL references: code imports, docs, README provenance tables, scripts
- Verify game still boots + fights work after each phase
- One phase per PR; never batch-rename everything at once

---

## Deletion Checklist (when all done)
- [ ] All teardown dirs renamed
- [ ] All references updated (grep for old names returns zero)
- [ ] Game boots, fights load, fighters visible and animating
- [ ] No duplicate downloads (this map prevented re-pulls)
- [ ] DELETE THIS FILE

---

## Character Name Mapping (original → WH proprietary)

Owner creates all proprietary character names. Status: `NEEDED` = awaiting owner;
`PENDING` = assigned, rename not applied; `DONE` = renamed + verified.

### virtual-soul (Virtua Fighter 5) — 18 fighters, release `vf5-ps3-v1`

| Original | File code | WH name | Status |
|---|---|---|---|
| Akira Yuki | `aki` | — | NEEDED |
| Pai Chan | `pai` | — | NEEDED |
| Lau Chan | `lau` | — | NEEDED |
| Wolf Hawkfield | `wol` | — | NEEDED |
| Jeffry McWild | `jef` | — | NEEDED |
| Kage-Maru | `kag` | — | NEEDED |
| Sarah Bryant | `sar` | — | NEEDED |
| Jacky Bryant | `jak` | — | NEEDED |
| Shun Di | `shu` | — | NEEDED |
| Lion Rafale | `lio` | — | NEEDED |
| Aoi Umenokouji | `aoi` | — | NEEDED |
| Lei-Fei | `lei` | — | NEEDED |
| Vanessa Lewis | `van` | — | NEEDED |
| Brad Burns | `bra` | — | NEEDED |
| Goh Hinogami | `goh` | — | NEEDED |
| Eileen | `mon` | — | NEEDED |
| El Blaze | `msk` | — | NEEDED |
| Dural | `dur` | — | NEEDED |

Stages (38 `stg*.farc`): stage WH names NEEDED —
`stgare stgaur stgban stgbar stgcas stgcid stgdjo stgdu1 stgdu2 stgdu3 stgdu4 stgdur
stghai stgjin stgnyc stgriv stgsin stgslk stgtak stgtan stgter stgtr2 stgtr3 stgtr4
stgtr5 stgtr6 stgtr7 stgtr8 stgtr9 stgtrm stgtrn stgtrs stgts2 stgts3 stgtst stgumi
stgwht stgyuk`.

### dragon-strike — Street Fighter EX Plus Alpha (PS1, SLUS_005.48) — 23 fighters

| Original | WH name | Status |
|---|---|---|
| Ryu | — | NEEDED |
| Ken Masters | — | NEEDED |
| Chun-Li | — | NEEDED |
| Guile | — | NEEDED |
| Zangief | — | NEEDED |
| Dhalsim | — | NEEDED |
| Sakura Kasugano | — | NEEDED |
| M. Bison | — | NEEDED |
| Akuma | — | NEEDED |
| Evil Ryu | — | NEEDED |
| Allen Snider | — | NEEDED |
| Blair Dame | — | NEEDED |
| Cracker Jack | — | NEEDED |
| Darun Mister | — | NEEDED |
| Doctrine Dark | — | NEEDED |
| Garuda | — | NEEDED |
| Hokuto | — | NEEDED |
| Kairi | — | NEEDED |
| Pullum Purna | — | NEEDED |
| Skullomania | — | NEEDED |
| Bloody Hokuto | — | NEEDED |
| Cycloid Beta | — | NEEDED |
| Cycloid Gamma | — | NEEDED |

### dragon-strike — Street Fighter EX2 Plus (PS1, SLUS_011.05) — 24 fighters, release `sf-ex2-plus-v1`

| Original | WH name | Status |
|---|---|---|
| Ryu | — | NEEDED |
| Ken Masters | — | NEEDED |
| Chun-Li | — | NEEDED |
| Guile | — | NEEDED |
| Zangief | — | NEEDED |
| Dhalsim | — | NEEDED |
| Blanka | — | NEEDED |
| Vega | — | NEEDED |
| Sagat | — | NEEDED |
| M. Bison | — | NEEDED |
| Cracker Jack | — | NEEDED |
| Darun Mister | — | NEEDED |
| Doctrine Dark | — | NEEDED |
| Garuda | — | NEEDED |
| Hokuto | — | NEEDED |
| Kairi | — | NEEDED |
| Nanase | — | NEEDED |
| Hayate | — | NEEDED |
| Pullum Purna | — | NEEDED |
| Sharon | — | NEEDED |
| Skullomania | — | NEEDED |
| Shadow Geist | — | NEEDED |
| Area | — | NEEDED |
| Vulcano Rosso | — | NEEDED |

### dragon-strike — Street Fighter EX3 (PS2, SLUS_201.30)

Roster inventory pending `PS2.DAT` (604MB) format RE. WH names NEEDED once decoded.

### underground-brawl (Def Jam: Fight for NY) — 78 fighter records

Records live in `mhvnsnt/wrestling-game` (`teardown/def-jam-fight-for-ny/`, PR #2).
WH names NEEDED (owner to create); roster to be transcribed here once assigned.

*Character tables added 2026-10-14 (wh-sf-dj-vf-100 lane).*

### iron-apex (Tekken 8) — public hunt 2026-10-14 (wh-t7t8-hunt)

First T8 models pulled from public modding sources (SFMLab, DeviantArt).
Dir rename `teardown/tekken8/` → `teardown/iron-apex/` is Phase 4 (separate PR).

| Original | WH name | Status |
|---|---|---|
| Yoshimitsu (T8 S1, WhiteMageSunny Blender 4.x) | **PHANTOM** | DONE (`teardown/tekken8/models/PHANTOM-t8-yoshimitsu-s1.7z`) |
| Asuka Kazama (T8, SFMLab/Mokujinh SFM port) | — | NEEDED (`teardown/tekken8/models/asuka-kazama-t8_SFM.rar`) |
| Heihachi Mishima (T8 S1, WhiteMageSunny raw FBX) | **DIABLO** | PENDING (partial download, resumes) |
| Xiaoyu (T8, Sticklove) | **SAKU RA** | PENDING (not yet pulled) |

### iron-prime (Tekken 7) — public hunt 2026-10-14 (wh-t7t8-hunt)

| Original | WH name | Status |
|---|---|---|
| Mishima Dojo stage (open3dlab Blender port, 2024 map) | — | NEEDED (`teardown/tekken7/arenas/mishima-dojo_2024-map.rar`) |
| Mishima Dojo full bundle 2021 (map+textures, 257MB) | — | NEEDED — TeraBox only (over GitHub 100MB/file; see `teardown/TEARDOWN-SOURCES.md`) |

### eastern-mind (Eastern Mind: The Lost Souls of Tong-Nou) — teardown 2026-10-15 (wh-easternmind-100)

5,321 bitmaps + 229 sounds + 3 CD tracks + 22 videos + 31 texts extracted from Director 4 DXRs.
Organized by owner-assigned WH stage names (stages.md). Per-file WH names NEEDED (owner to assign);
files keep EM-descriptive basenames under WH stage directories pending assignment.

| Original (EM) | WH name | Status |
|---|---|---|
| F_* areas (Shi-chieng, Fire/Time) | **stage-1-plains-of-chi-u** | DONE (`teardown/eastern-mind/stage-1-plains-of-chi-u/`, 518 files) |
| G_* areas (Yui-wang, Metal/Desire) | **stage-2-helix-palace** | DONE (`teardown/eastern-mind/stage-2-helix-palace/`, 1,282 files) |
| W_* areas (Man-chien, Water/Dreaming) | **stage-3-palace-of-dreaming** | DONE (`teardown/eastern-mind/stage-3-palace-of-dreaming/`, 676 files) |
| L_* areas (Ming-ken, Wood/Life) | **stage-4-tree-of-life** | DONE (`teardown/eastern-mind/stage-4-tree-of-life/`, 505 files) |
| D_MARKET, D_MERCHA | **stage-5-phantom-marketplace** | DONE (`teardown/eastern-mind/stage-5-phantom-marketplace/`, 100 files) |
| E_* areas (Tong-nou, Earth/Source) | **stage-6-octagonal-shrine-par-fang** | DONE (`teardown/eastern-mind/stage-6-octagonal-shrine-par-fang/`, 223 files) |
| D_* prologue/ending areas | — | NEEDED (`teardown/eastern-mind/prologue-ending/`, 661 files) |
| R_* incarnation system | — | NEEDED (`teardown/eastern-mind/incarnation-system/`, 512 files) |
| TRANSCRI Sato works/promo | — | NEEDED (`teardown/eastern-mind/transcript-promo/`, 1,128 files) |
| CD tracks 2-4 (Tong-Nou Theme, Transmigration, Esoteric Mix) | — | NEEDED (`teardown/eastern-mind/soundtrack/`) |

*Stage directory renames use owner-assigned names from stages.md. Individual asset WH names pending owner.*

## Phase 1 Roster Integration (2026-10-15) — T7-style models → WH names

| Source File | WH Model | WH Fighter | Canon Base |
|-------------|----------|------------|------------|
| asuka-kazama (RigModels) | kinpo.glb | Kinpo | Asuka |
| asuka-alt (RigModels) | kinpo_alt1.glb | Kinpo (alt) | Asuka |
| bryan (RigModels) | skull.glb | Skull | Bryan Fury |
| eddy-gordo (RigModels) | king-tyrant.glb | King Tyrant | Eddy Gordo |
| eddy-gordo-capoeira (RigModels) | king-tyrant_alt1.glb | King Tyrant (alt) | Eddy Gordo |
| ganryu (RigModels) | thor.glb | Thor | Ganryu |
| gun-jack (RigModels) | sam-ur-a1.glb | SAM-UR-A1 | Gun Jack |
| josie (RigModels) | waterfall.glb | Waterfall | Josie Rizal |
| julia (RigModels) | nightwolf.glb | Nightwolf | Julia Chang |
| king-variants (RigModels) | pantera_alt1.glb | Pantera (alt) | King |
| lee (RigModels) | purple-rain.glb | Purple Rain | Lee Chaolan |
| negan (RigModels) | n3g4tiv0.glb | N3GΔTIV0 | Negan |
| nina (RigModels) | awa-pop.glb | Awa Pop | Nina Williams |
| steve-fox (RigModels) | zui_alt1.glb | Zui (alt) | Steve Fox |
| steve-fox-alt (RigModels) | zui_alt2.glb | Zui (alt) | Steve Fox |
| xiaoyu (RigModels) | saku-ra.glb | Saku Ra | Xiaoyu |
| xiaoyu-pink-dress (RigModels) | saku-ra_alt1.glb | Saku Ra (alt) | Xiaoyu |
| yoshimitsu (RigModels) | phantom.glb | Phantom | Yoshimitsu |
| lei (RigModels) | lei.glb | UNMAPPED | — |
| lili (RigModels) | lili.glb | UNMAPPED | — |
| mokujin (RigModels) | mokujin.glb | UNMAPPED | — |
| zafina (RigModels) | zafina.glb | UNMAPPED | — |
| baek (RigModels) | baek.glb | KEVIN | A2 attire for Kevin (owner 2026-10-20: Baek-as-fighter → KEVIN) |

**Blocked:** heihachi-mishima → Diablo (RAR, no extractor on VM); dr-bosconovitch → Doc Frank (XPS format); xiaoyu-t8 → Saku Ra alt2 (RAR).

**Attire rule (owner 2026-10-15):** All above are NON-T3 = front-line attires. T3 legacy models go at back of attire list only.

---

## APPENDIX (2026-10-20) — iron-legacy (Tekken 3) CORRECTION & COMPLETION

*Added by the Tekken 3 full-wiring lane. Append-only; details in
`teardown/tekken3/CANON-CONVERSION.md` and `teardown/tekken3/WIRING-INVENTORY.md`.*

The "iron-legacy (Tekken 3) — 100% complete" entry above was premature when written: at
that time only 7 of 21 motion banks and 7 movesets had been extracted. As of 2026-10-20:
all 20 character banks present on the disc image + the common bank are extracted and
SHA-256-verified, and all 20 movesets are extracted (13 banks / 5,663 move rows added that
day). The one genuine absence is divmot15 (Mokujin): BNS record 295 has size 0 in
`teardown/tekken3/bns-table.pkl` — the data is not on this disc image.
The directory rename `teardown/tekken3/` → `teardown/iron-legacy/` remains PENDING (this
map's table): it must land with all consumer references updated (`game/js/t3anims.js`,
`game/js/movesets.js`, `lab/tools/`, stage pipeline docs) and a boot check, sequenced by
the coordinator — it was not executed by the wiring lane.

<!-- BEGIN WMXIX / MAT-LEGENDS SECTION (WMXIX wiring lane, 2026-10-20 — coordinator reconciles at merge) -->

### mat-legends (WMXIX) — wiring + conversion status, 2026-10-20

- Universe rename `WWE WrestleMania XIX` → `mat-legends` is APPLIED at the data/registry layer: `moveset-library/animations/WMXIX-CLIP-INDEX.json`, `moveset-library/movesets/WMXIX-MOVES.json`, `game/assets/stages/mat-legends/stages.json`, `customization/mat-legends-caw.json`. Per-game record: `teardown/wmxix/CANON-CONVERSION.md`.
- Physical folder renames in `teardown/wmxix/docs/RENAME-ENTRIES-WMXIX.md` (`teardown/wmxix/` → `teardown/mat-legends/`, `teardown/wwe-wrestlemania-xix/` → `teardown/mat-legends-research/`) remain PLANNED — gated on the watchdog lane finishing and owner wrestler-name assignment. Not executed by this lane; nothing deleted.
- Wrestler model files (127 OBJs, slots 000–110): ACCOUNTED-ELSEWHERE — canonical home is mhvnsnt/wrestling-game + mhvnsnt/wrestlemania-xix-mod per the federation rule; WH keeps the mechanics and the teardown.
- The "~80%" status above predates the solved teardown (closed 2026-10-17: assembly solution exact, YANM fully decoded 169/170 clean). Remaining opens: arena face indices, per-clip move semantics, CAW part-level consumption, owner character names.

<!-- END WMXIX / MAT-LEGENDS SECTION -->
<!-- BEGIN No Mercy / mat-kings conversion record (wiring lane 2026-10-20; source of truth: teardown/wwf-no-mercy/CANON-CONVERSION.md) -->
### mat-kings (No Mercy) — conversion record 2026-10-20

| Item | Status |
|---|---|
| Universe name `mat-kings` | DONE (already mapped above) |
| Move IDs `NM-###` → `MK-####` (4,409 moves + 1,353 system clips, `moveset-library/movesets/mat-kings-move-database.json`) | DONE |
| Tekken-style input assignment for every move category | DONE (in the same database) |
| NM-001/002/003 anim_ref corrections (FileTableDB evidence) | DONE |
| 17 stage display names (in `game/js/stages.js`) | AWAITING OWNER — table in CANON-CONVERSION.md §4 |
| 42 wrestler identities → WH names | AWAITING OWNER — none mapped; federated design keeps wrestler characters out of WH |
| Persona-named move labels (e.g. Reverse Tazzplex) | AWAITING OWNER naming pass |
| Directory rename `teardown/wwf-no-mercy/` (Phase 3) | NOT DONE — teardown folder stays per owner law; coordinator decision |
<!-- END No Mercy / mat-kings conversion record -->

### CHARGER — Blanka replacement fighter (owner 2026-10-20) — DONE

| Original | File code | WH name | Status |
|---|---|---|---|
| Blanka (Street Fighter / dragon-strike) | `blanka` | **CHARGER** | DONE |

- Owner's words: "Blanka replacement model from tripo attire 1: CHARGER (his name is charger cause of blankas attacks and movesets will be attach to him but he's got powers of ice and electricity)". Attire 2 followed the same day. CHARGER's powers are ICE and ELECTRICITY.
- **Roster**: `game/js/roster-full.js` — the `blanka` fighter entry is replaced by `charger` ("The Ice Monster", attires `['charger', 'charger-attire2']`) + a `charger-attire2` entry ("The Wild Current"). Blanka's roster slot is CHARGER's now.
- **Models** (owner-made Tripo, pulled via `tools/tripo-pull`, raw meshopt GLBs, render-prep validated — 3 textures each, no NaN): Attire 1 = Tripo `b91318ce-2ccd-43eb-8691-d675b3ee8b10` ("ice monster 3d model") → `roster/charger/attires/attire1/model.glb` (sha256 c0caf06c…); Attire 2 = Tripo `f87e24eb-0c0b-4444-9409-4f4dabc0bb32` ("green spiky creature 3d model") → `roster/charger/attires/attire2/model.glb` (sha256 307b7ade…). Model URL keys added in `game/js/assets.js`.
- **Moveset**: `game/assets/movesets/charger.json` = Blanka's FULL set — all 199 moves from `blanka.json` (post-#363 union), inputs and frame data IDENTICAL (script-verified field-by-field against the source; only `name` strings changed). `charger` added to MOVESET_IDS (`game/js/movesets.js`); animation bank `bryan` in `game/js/fighter.js` MOVESET_MAP (Blanka's T3 source bank).
- **Signature renames** (move data untouched; full map also in charger.json `canon_rename_map`): Electric Thunder family → **Cryo Thunder** (incl. EX Cryo Thunder); Rolling Attack family → **Frostcharge Roll** (Aerial/Vertical/Backstep/Quick variants likewise); Rolling Cannon → **Frostcharge Cannon**; Dynamic Rolling → **Dynamic Frostcharge**; Quick Rolling → **Quick Frostcharge**; Ground Shave Rolling → **Glacier Shave Roll**. 46 distinct names renamed.
- **NOT deleted**: `roster/blanka/` (incl. the Sketchfab GLB), `game/assets/movesets/blanka.json`, `game/assets/movesets/sf-blanka.json`, and the `blanka` keys in assets.js / movesets.js / fighter.js all stay in the repo. Only the playable roster entry changed hands.

<!-- END CHARGER SECTION -->

### CORNERSTONE — Ryuji/Rock hybrid gets his name (owner 2026-10-21)

| Original | File code | WH name | Status |
|---|---|---|---|
| Ryuji Yamazaki (KOF / Fatal Fury) x The Rock (WWE, early Attitude Era) | `ryuji-rock` | **CORNERSTONE** | NAME LOCKED |

- Owner's words (2026-10-21): "I told u how ryuji character will be mixed with the rock from WWE and do the uranage/rock bottom, he will also get the rock bottom from king and from WWE all stars, and some animations of the rock from the WWE teardown games, and kings jumping diving elbow attack, mixed with ryuji yamazakis stance and taunts and moveset and antics mixed with the rock persona from early attitude era WWE. And his name will be CornerStone"
- Foundation (owner 2026-10-19, already logged): Ryuji Yamazaki version — black shirt, blonde top hair — mixed with The Rock (Dwayne Johnson): obnoxious like Ryuji, sticks his tongue out, personality mixed with The Rock. Moveset: Ryuji base + The Rock's moves (Rock Bottom — King has it in Tekken, pull from there) + wrestling moves from Urban Reign / Tekken / other teardown games.
- Canon entry: CANON.md — "CORNERSTONE — The Obnoxious One (Bonus)".
- What changed: the DISPLAY / canonical name only. The `ryuji-rock` roster entry (`game/js/roster-full.js`) shows CORNERSTONE (title kept: "The Obnoxious One"); the internal fighter id, the moveset key (`game/assets/movesets/ryuji-rock.json`), the model key (`ryuji-rock` in `game/js/assets.js`) and the folder (`roster/ryuji-rock/`) keep the source code name so every loader reference stays valid.
- NOT deleted / NOT renamed: `game/assets/movesets/ryuji.json` (the full 103-move KOF Yamazaki set) and the `ryuji` roster entry (the pure-Yamazaki form) stay exactly as they are. The pre-rename records in `roster/ryuji-rock/attires/attire1/README.md` keep the old name as their history.
- Model: the owner delivered his Tripo link on 2026-10-21 — the exact next step the attire-1 README's model hunt (2026-10-19) was waiting on. Pull + wire follow in the same CornerStone build.
- Design sources named by the owner that are NOT yet in the teardown holdings, recorded so they are never silently dropped or faked: the **WWE All Stars** Rock Bottom version (All Stars is queued on the teardown-idle queue — not acquired, not torn down) and **Younger Toguro's fingernail blast** (Yu Yu Hakusho — no YYH game in the holdings). Both wire in when their sources exist.

<!-- END CORNERSTONE SECTION -->

<!-- BEGIN EM-JIN NAMING CONVENTION (owner 2026-10-22) -->
### NAMING CONVENTION — Jin (Eastern Mind)

There is an Eastern Mind character named Jin. This is **NOT Jin Kazama** (Tekken) — completely separate character.

**Convention:** in all files, docs, and code, refer to this character as **"Jin (Eastern Mind)"** or **"EM-Jin"** — never bare "Jin" where confusion with Jin Kazama is possible. This matters because Demonio already uses Jin's moveset as a base, so the name collision is real.

*(Correction 2026-10-22: earlier note said "Gen (Eastern Mind)" — that was a mishearing. It is Jin.)*
<!-- END EM-JIN NAMING CONVENTION -->

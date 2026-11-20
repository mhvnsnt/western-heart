# Western Heart — Teardown research, part D: select-any-character gating + archive.org lawful reference material

**Date:** 2026-11-07 (evening, CST)
**Repo:** `mhvnsnt/western-heart` — read with the GitHub connector. No code edited, nothing pushed, no commercial game file downloaded.
**Sources read:** `game/js/roster-full.js`, `game/js/select-screen.js`, `game/js/core-set.js`, `game/js/main.js` (model-pending gate ~lines 1260–1267), `game/js/modes.js`, `game/js/fighter.js` (MOVESET_MAP, FIGHTER_BANK, bankIdFor), `game/js/t3anims.js` (SOURCE_TO_BANK), `game/js/assets.js` (MODEL_URLS, 195 keys), `game/assets/models/MODEL-STATUS.md` (2026-10-17/18 — stale, see notes), `ROSTER.md`, `GAME-DEV-BRIEFING.md`.
**Names:** Pantera is male (he/him). Every other fighter is named by name only, no pronouns.

## 1. Select any character — the headline numbers

- **59 fighters** in `game/js/roster-full.js` (`FULL_ROSTER`).
- **50 pickable on the select grid today. 9 hidden (not pickable on the grid).**
- **No fighter is locked behind a lock flag.** There is no `locked` flag on any roster entry anywhere in the code. The only gates are: hidden from the grid (`SELECT_HIDDEN`), no model (`modelPending`), and no animation bank (ZEN only, public builds).
- **Only 2 fighters are proven in a live fight:** Pantera and Demonio (Piece 1 playtest, 2026-11-07). The other 48 pickable fighters have a model key and a bank on paper, but no live fight proof was found in this pass.

## 2. How the gating actually works (plain words)

**The grid shows a fighter unless it is hidden.** `select-screen.js` line 480 builds the grid from every roster entry except the ones in `SELECT_HIDDEN` (lines 472–477). `selectVisible()` in `core-set.js` line 72 always returns `true` — it hides nothing. There is no lock, no unlock, no greyed-out card state in the select code at all: a fighter is either on the grid (clickable) or not there.

**The 9 hidden fighters are:**

| Hidden fighter | Why hidden |
|---|---|
| RIN, BYOU, TOU, SHA, KAI, JIN, RETSU | The seven vesseled souls. The code comment says they stay in the roster data for story/other modes and return later as unlockable boss-type characters once story modes progress — that unlock path is future design, not code. **CORRECTED 2026-11-08 (canon):** the seven are RIN, BYOU, TOU, SHA, KAI, JIN, RETSU — GYOU is unvesseled, not one of the seven. "No body of their own yet" is wrong as a file claim: RIN/SHA/KAI/RETSU bodies already exist on disk and passed the loader gate (see §3); only the roster still says `model: null`. JIN fights as Phantom, its vessel, and is pickable — not hidden. |
| ZEN, GYOU | The two unvesseled souls. ZEN has a model (`zen`) but is still in `SELECT_HIDDEN` (see the contradiction note below). GYOU has no rigged model yet — 7 unrigged Tripo statics, archive-only. |
| RYUJI | No model (`model: null`, `modelPending: true`). **CORRECTED 2026-11-08 (canon):** RYUJI is NOT a soul — Ryuji Yamazaki is an inspiration for CORNERSTONE along with The Rock (CANON.md ~1299–1311). The pure-Yamazaki `ryuji` entry is a leftover duplicate that "is untouched and stays in the repo"; no model build and no unhide are owed for it. |

**The safety net at fight start.** If a fighter with no model ever reaches a fight anyway, `main.js` lines 1260–1267 swap it out silently: the player becomes the first ready fighter in roster order (today that is ZEN), and the enemy becomes a random ready fighter (`randomEnemy`, which also filters out `modelPending` and model-less entries, `main.js` line 663). So a model-pending fighter can never fight on another fighter's body — that is the owner law in code. But the swap is silent: the player is never told the pick changed.

**The arcade foe pool is wider than the grid.** `_pickFoe` (`modes.js` lines 1375–1382) draws from the *whole* roster with no model-pending filter — only the player and `custom` are excluded. The `startFight` safety net above is what stops a model-pending foe from actually fighting. One hole: ZEN has a model, so ZEN can be drawn as an arcade foe and will fight with **no animation bank at all** in public builds (see below).

**Unlockables are not fighter locks.** `unlockables.js` (used by Treasure Battle, `modes.js` lines 1070–1080) grants titles/frames/cosmetics. No fighter is gated behind it.

## 3. Roster gating table — all 59 fighters

"Pickable" means: on the select grid today (not in `SELECT_HIDDEN`) with a model key that exists in `MODEL_URLS` (`game/js/assets.js`). "Bank" is the animation bank `bankIdFor` resolves to (fighter.js) — the motion the fighter actually plays. A fighter with no bank fights on embedded locomotion + procedural combat only, never another character's clips. `*` on a soul bank means the bank is bound but moot: the fighter has no model, so the bank never plays.

| Fighter | Tier | Model key | Bank | Status | Gate | Unblocker |
|---|---|---|---|---|---|---|
| RIN | Soul | — (null) | jin* | HIDDEN | Roster `model: null` + hidden only — body `rin-body.glb` (8,808,768 B) already on disk, loader-verified 2026-11-08 (18 skinned, 49 bones, 1.750 m) | Set `model: 'rin-body'` + remove from SELECT_HIDDEN. No new model needed. |
| BYOU | Soul | — (null) | jin* | HIDDEN | No body by canon design — a soul has no body of its own; it fights through its vessel + celestial stand (`docs/souls/VESSELS-AND-STANDS-OWNER-2026-10-21.md`). Vessel Zui is pickable (`model: 'zui-attire1'`). | No model build — canon forbids it. BYOU fights through vessel Zui + the soul-spirit stand (wiring verified 2026-11-08: `soul-spirit.js` → `main.js` startFight → `game.js` attachSoulSpirit). Stays hidden as a card per the 2026-10-22 directive. |
| TOU | Soul | — (null) | paul | HIDDEN | Roster `model: null` + hidden; base Paul models exist unwired in the Godot lab (`lab/game/assets/t3_paul.glb` + `t3_paul_t3real.glb`, the latter already keyed as `t3-paul`) | Convert/rig a Paul model for `game/` + set `model` + unhide. Neither lab file is game-ready as-is (159 validator errors — zero-length normals; 18-joint T3 skeleton, not the 49–50 Mixamo gate). The `pantera` fallback ride is an owner call, not this lane's decision. |
| SHA | Soul | — (null) | xiaoyu | HIDDEN | Roster `model: null` + hidden only — body `sha-body.glb` (16,816,172 B) already on disk, loader-verified 2026-11-08 (32 skinned, 50 bones, 1.750 m) | Set `model: 'sha-body'` + remove from SELECT_HIDDEN. No new model needed. |
| KAI | Soul | — (null) | eddy | HIDDEN | Roster `model: null` + hidden only — body `kai-body.glb` (25,644,156 B) already on disk, loader-verified 2026-11-08 (24 skinned, 50 bones, 1.750 m) | Set `model: 'kai-body'` + remove from SELECT_HIDDEN. No new model needed. |
| RETSU | Soul | — (null) | bryan | HIDDEN | Roster `model: null` + hidden only — body `retsu-body.glb` (472,476 B) already on disk, loader-verified 2026-11-08 (27 skinned, 49 bones, 1.750 m) | Set `model: 'retsu-body'` + remove from SELECT_HIDDEN. No new model needed. |
| ZEN | Soul | zen | NONE (unmapped) | HIDDEN | Hidden by SELECT_HIDDEN + no public bank | Remove from SELECT_HIDDEN + bind a bank (Dural bank is private-build only) |
| GYOU | Soul | — (null) | hwoarang | HIDDEN | Unvesseled soul; no rigged model — 7 unrigged Tripo statics, archive-only (`roster/gyou/spirit-body/`, verified 2026-11-08: 1 mesh, 0 skins, 0 joints, 0 animations) | Rig the spirit-body source (Blender + GameRig, per `roster/gyou/spirit-body/SPEC.md`) → `model-rigged.glb` → set `model` + unhide. Rig job BLOCKED 2026-11-08 on disk quota (no writable repo clone). |
| PANTERA | Main | pantera | king | PICKABLE | — | — |
| DEMONIO | Main | demonio-a1 | jin | PICKABLE | — | — |
| PHANTOM | Main | phantom | yoshimitsu | PICKABLE | — | — |
| DIABLO | Main | diablo | heihachi | PICKABLE | — | — |
| SKULL | Main | skull | bryan | PICKABLE | — | — |
| SAM-UR-A1 | Main | sam-ur-a1 | gunjack | PICKABLE | — | — |
| SAKU RA | Main | saku-ra | xiaoyu | PICKABLE | — | — |
| ZUI | Bonus | zui-attire1 | jin | PICKABLE | — | — |
| KINPO | Bonus | kinpo | jin | PICKABLE | — | — |
| WATERFALL | Bonus | waterfall | jin | PICKABLE | — | — |
| KING TYRANT | Bonus | king-tyrant | eddy | PICKABLE | — | — |
| BURGER | Bonus | burger | bryan | PICKABLE | — | — |
| AWA POP | Bonus | awa-pop-attire2 | nina | PICKABLE | — | — |
| SCIMITAR | Bonus | scimitar | jin | PICKABLE | — | — |
| PURPLE RAIN | Bonus | purple-rain | jin | PICKABLE | — | — |
| NIGHTWOLF | Bonus | nightwolf | julia | PICKABLE | — | — |
| DIO | Bonus | dio-attire1 | heihachi | PICKABLE | — | — |
| CAPE JONES | Bonus | cyborg-x | gunjack | PICKABLE | — | — |
| MICHIKO | Bonus | michiko | jin | PICKABLE | — | — |
| STAR | Bonus | star | xiaoyu | PICKABLE | — | — |
| TORCH | Bonus | torch-tripo-a1 | anna | PICKABLE | — | — |
| BRUNO | Bonus | bruno-attire2 | bryan | PICKABLE | — | — |
| N3GΔTIV0 | Bonus | negativo-attire1 | bryan | PICKABLE | — | — |
| THOR | Bonus | thor | bryan | PICKABLE | — | — |
| YUKIHYŌ | Bonus | yukihyo-attire1 | armorking | PICKABLE | — | — |
| SLICE | Bonus | slice | bryan | PICKABLE | — | — |
| DOC FRANK | Bonus | doc-frank-big | bosconovitch | PICKABLE | — | — |
| KEVIN | Bonus | baek | bryan | PICKABLE | — | — |
| MARIPOSA | Bonus | mariposa-butterfly-default | xiaoyu | PICKABLE | — | — |
| DXMMII | Bonus | dxmmii-tripo | jin | PICKABLE | — | — |
| CHARGER | Bonus | charger | bryan | PICKABLE | — | — |
| DOROWANI | Bonus | dorowani | gon | PICKABLE | — | — |
| CHATUR | Bonus | chatur | ogre | PICKABLE | — | — |
| POND | Bonus | pond | raven | PICKABLE | — | — |
| RYUSAN | Bonus | ryusan | luckychloe | PICKABLE | — | — |
| TOBI | Bonus | tobi | hwoarang | PICKABLE | — | — |
| MEGAMI | Bonus | megami | jun | PICKABLE | — | — |
| MENAJERII | Bonus | menajerii | roger | PICKABLE | — | — |
| KRONOS | Bonus | kronos | king | PICKABLE | — | — |
| DEATHFANG | Bonus | deathfang | heihachi | PICKABLE | — | — |
| RYUJI | Bonus | — (null) | UNMEASURED | HIDDEN | Not a soul — leftover pure-Yamazaki duplicate entry of CORNERSTONE, hidden under the owner no-duplicate law (CANON.md ~1299–1311) | No model build, no unhide. The entry stays in the repo untouched per canon. |
| CORNERSTONE | Bonus | ryuji-rock | king | PICKABLE | — | — |
| KORESHI | Bonus | koreshi | heihachi | PICKABLE | — | — |
| RAVE | Bonus | kiko-tanaka | lei | PICKABLE | — | — |
| BUFFALO BILL | Bonus | buffalo-bill | law | PICKABLE | — | — |
| VAIN ABEL | Bonus | vainabel | UNMEASURED | PICKABLE | Bank unmeasured (no MOVESET_MAP entry; moveset JSON not read) | Read movesets/vainabel.json anim_bank / t3_source and confirm a bank binds |
| CAIN ELIAS | Bonus | cain-elias | king | PICKABLE | — | — |
| CHORDZ | Bonus | chordz | UNMEASURED | PICKABLE | Bank unmeasured (no MOVESET_MAP entry; moveset JSON not read) | Read movesets/chordz.json anim_bank / t3_source and confirm a bank binds |
| GASHADOKURO | Bonus | gashadokuro | kuma | PICKABLE | — | — |
| AOTSUKI | Bonus | aotsuki | kuma | PICKABLE | — | — |
| SILVERTONGUE | Bonus | silvertongue | xiaoyu | PICKABLE | — | — |

### Notes on the table

- **ZEN is the odd one.** The comment above `SELECT_HIDDEN` says "Only ZEN and GYOU stay selectable as spirit fighters" — but both ZEN and GYOU are *in* the hidden set, so neither is on the grid in the code as it stands. ZEN also has **no animation bank in public builds**: `FIGHTER_BANK` maps ZEN to `null` on purpose (owner decision 2026-10-24 — ZEN is neither Heihachi nor Julia; the base chain is Eleven/Twelve → Dural). The Dural bank only binds when `T3_BANKS.dural` exists, which only happens in private builds (`t3anims.js`, `__WH_PRIVATE_ASSETS`). So even if ZEN were unhidden, ZEN would fight bankless in the public build. GYOU is model-pending as well, so the comment is wrong for both.
- **VAIN ABEL and CHORDZ are pickable but their banks are UNMEASURED.** Neither has a `MOVESET_MAP` entry in `fighter.js`, and their moveset JSONs (`movesets/vainabel.json`, `movesets/chordz.json`) were not read in this pass, so `bankIdFor` depends on those files' `anim_bank` / `t3_source` fields, which are unknown here. If a field names a source with no bank, they fight bankless. Everything else in the pickable 50 resolves to a real bank through `MOVESET_MAP` + `FIGHTER_BANK` + `SOURCE_TO_BANK`.
- **Own-slot banks are NOT active.** `OWN_SLOT_BANKS` in `fighter.js` is an empty object (2026-11-07: the TTT2 own-character banks retarget with a strong forward pitch — walks nearly horizontal — so binding them would make fighters look worse). ZUI, KINPO, PURPLE RAIN, CHORDZ, BRUNO, AOTSUKI and others still play shared banks (mostly `jin`) until their own clips pass by eye. That is a quality gap, not a gate: they are pickable, they just do not move like their own base character yet.
- **Bank `jin` for RIN/BYOU/KAI/GYOU is the resolved animation bank, not a mistake.** `bankIdFor` resolves the moveset `demonio` through `game/assets/movesets/demonio.json` (`anim_bank: 'jin'`, `t3_source: 'jin'`) to the `jin` bank. `demonio` is the moveset id; `jin` is the bank it plays on. (The canon correction that "RIN/BYOU's bank is demonio, not jin" is about the moveset, not the resolved bank — the Bank column here names the bank.)
- **Model keys are not proof the GLB file is on disk.** All 50 pickable fighters' model keys exist in `MODEL_URLS` (195 keys total), and a model-key-guard test exists (`game/tests/model-key-guard.test.mjs`). But a key is a path string, not a load test. `MODEL-STATUS.md` (2026-10-17/18) is three weeks stale: it still lists BURGER, SCIMITAR, MICHIKO, STAR, TORCH, DIO, BRUNO, YUKIHYŌ, SLICE, CHORDZ and VAIN ABEL as "no model in repo", while the current roster gives all of them model keys (Tripo pulls landed since). **Update 2026-11-08 (Lane 5): the four soul bodies were loader-verified** — Khronos glTF Validator + the repo's own vendored GLTFLoader (`game/vendor/`) in headless Chromium: rin-body, sha-body, kai-body, retsu-body all parse, all skinned with Mixamo-style bones incl. Head, all 1.750 m tall (rin-body carries 1 validator error — declared buffer length 23,140,476 vs 8,638,536 actual BIN — stale metadata only; every bufferView/accessor ends inside the real BIN, and the file loads). Whether the other 46 pickable fighters' GLBs actually load is still **UNMEASURED** — it needs a fresh loader-path check, not a doc read.
- **The header count is stale.** `roster-full.js` says "48 selectable fighters" in its header comment, but the array holds **59** entries. The real pickable count is 50, not 48.

## 4. The lists disagree — counts

| List | Count | What it says |
|---|---|---|
| `game/js/roster-full.js` header comment | 48 "selectable fighters" | Stale. The array actually holds 59 entries. |
| `game/js/roster-full.js` array (`FULL_ROSTER`) | **59** | 8 souls + 7 main + 44 bonus. This is the code truth. |
| `GAME-DEV-BRIEFING.md` §4 | **36 named fighters** | 9 souls + 7 main + 20 bonus + boss Sun Rā. |
| `ROSTER.md` | **9 souls + 7 main vessels** (16 in detail) | Plus the Trader and the Assembled Soul as post-launch design, not roster entries. |
| `AUDIT.md` (2026-11-06) | 36 named; "~49 entries per the Oct 22 audit" | Both stale now: the array has grown to 59. |

**Disagreements, plainly:**
1. Briefing says 36, code has 59 — **24 fighters were added after the briefing's count** (KEVIN, MARIPOSA, DXMMII, CHARGER, DOROWANI, CHATUR, POND, RYUSAN, TOBI, MEGAMI, MENAJERII, KRONOS, DEATHFANG, RYUJI, CORNERSTONE, KORESHI, RAVE, BUFFALO BILL, VAIN ABEL, CAIN ELIAS, CHORDZ, GASHADOKURO, AOTSUKI, SILVERTONGUE). The briefing was never updated.
2. Briefing names boss **Sun Rā** — Sun Rā has **no entry** in `roster-full.js` at all.
3. `ROSTER.md` lists **9 souls including JIN (the Blade Soul)**. The roster array has **8 soul entries** (no `jin` entry) because JIN fights as Phantom, its vessel — but JIN is still a live soul in the code, not a legacy leftover: `jin_soul` is in `soul-spirit.js` NINE_SOULS (vessels `['phantom']`), `heartmind.js` NINE, and `movesets.js:32`, and appears in `MOVESET_MAP` (`jin_soul: 'yoshimitsu'`) and `SELECT_HIDDEN` as the soul's hidden card. **CORRECTED 2026-11-08 (canon):** the nine souls are RIN, BYOU, TOU, SHA, KAI, JIN, RETSU, ZEN, GYOU; JIN the Blade Soul is NOT Jin Kazama, and the fighter built on that data is DEMONIO.
4. The briefing (§8) still says "36-fighter select". The grid actually shows **50 cards + 1 RANDOM card**.

## 5. Archive.org — lawful Tekken / Urban Reign reference material

Rule followed: manuals, strategy guides, arcade flyers and magazines only. **No ISO, ROM, disc image or code file was downloaded, and none is listed here as a source to get.** Items that are game files are listed under "Excluded" only, so nobody mistakes them for sources.

**A note on what "lawful" means here:** these are publisher-copyrighted scans (Namco, Prima) that archive.org hosts freely viewable in its Manual Library / Folkscanomy collections. They are **not public domain**. They are usable the way this teardown uses them: read them, measure how the real games work (modes, controls, move lists, select flow), and rebuild that behaviour in our own code. Do not copy their text, art, or layouts into the game.

### The best 3 (start here)

1. **Tekken 3 NTSC-U/C Manual** — the single most useful reference for select-any-character + arcade mode. It documents mode select, Arcade Mode (one player vs the computer, no continue limit, Player 2 Start jumps in and switches to Versus), VS Mode, Team Battle, Tekken Force, Practice and Option modes, the pause menu, and the game screen — the exact behaviours the teardown spec needs to measure.
   https://archive.org/details/tekken-3-manual
2. **Tekken 1–5 Strategy Guides (Prima / EGM bundle)** — six guides in one item: Tekken (EGM), Tekken 2 Official Strategy Guide (1996), Tekken 3 Prima Official Strategy Guide (1998 — all moves, all combos, all characters, pro strategies, secret characters, ~8 pages per character), Tekken 4 Prima (2002), Tekken 5 SG. The Tekken 3 Prima guide is the move-list reference for the whole roster.
   https://archive.org/details/tekken_1-5_strategy_guides
3. **Urban Reign (USA) Manual** — the brawl-layer reference: weapons/items, special attacks, dodging, teaming up with a partner, multi-fighter rules, and character info. Directly relevant to the Urban Reign feel the teardown is mixing in.
   https://archive.org/details/ps2_Urban_Reign_USA

### More manuals and guides on archive.org

- **Tekken 5 (USA) Manual** — Story Battle, Arcade, Arcade History, and **Tekken: Devil Within** (play as Jin Kazama in a 3D action-adventure game) — the Devil Within section is the reference for the HeartMind "god within" hunt. Freely viewable full text.
  https://archive.org/stream/ps2_Tekken_5_USA/Tekken_5_USA_djvu.txt
- **Tekken 3 Manual (PlayStation Classic)** — a second Tekken 3 manual scan (same character-profile copy as the NTSC-U/C manual, per the item note). Pause menu, rules, continue, mode select.
  https://archive.org/stream/tekken-3-manual-ps-classic/tekken-3-manual-en_djvu.txt
- **Tekken 3 Prima Strategy Guide (standalone item)** — the same 1998 Prima guide as in the bundle above, as its own item.
  https://archive.org/stream/tekken-3-prima-strategy-guide/Tekken%203%20Prima%20Strategy%20Guide_djvu.txt
- **Tekken 2 Arcade Kit Installation Manual (Namco, 1995)** — arcade-operator manual: specs, game conversion, gameplay ("a one-player game first pits the player against seven randomly selected computer opponents"), installation, control panel, test mode. The "seven randomly selected opponents" line is the original arcade ladder behaviour, measured from Namco's own words.
  https://archive.org/download/namco-tekken-2-arcade-kit-manual/tekken_2_kit_installation_manual.pdf
- **Tekken 3 Kit Installation and Operation Manual** — arcade kit manual in the Arcade Manual Archive / Manual Library collections.
  https://archive.org/details/arcademanual_Tekken3_man
- **Tekken: Dark Resurrection PSP Manual** — inside the Sony PSP Manuals collection on archive.org; covers Arcade Mode (the complete arcade game), Quick Battle, Game Sharing, Ad Hoc / Infrastructure modes.
  https://archive.org/stream/SonyPSPManuals/Tekken%20-%20Dark%20Resurrection%20%28Europe%29_djvu.txt
- **Pachislo Tekken Manual (2005)** — pachinko-machine manual (parts list, installation, troubleshooting). Listed for completeness; low value for the fighting-game teardown.
  https://archive.org/details/pachislotekkenownersmanual

### Arcade flyers — not on archive.org

No Tekken arcade flyer was found on archive.org (the closest archive.org hit is a Tekken 3 Windows desktop theme, not a flyer). The flyers live at **The Arcade Flyer Archive** (flyers.arcade-museum.com), which is the lawful reference source for them: Tekken (Namco, 1994, 2 pages), Tekken 2 (1995, 2 pages), Tekken 3 (1996, 1–2 pages), Tekken 4 (2001, 4 pages), Tekken Tag Tournament (1999, 4 pages).
https://flyers.arcade-museum.com/videogames/list?manuf_id=1522

### Excluded — game files found, NOT sources

- **Urban Reign (EU) PS2 ISO item** — a disc image. Excluded. Do not get it.
  https://archive.org/details/urban-reign-eu-en-fr-de-es-it-2005-beat-em-up-iso-ps2
- **PlayStation 2 RetroAchievements collection (N–Z)** — contains game-file zips including Urban Reign (USA). Excluded. Do not get it.
  https://archive.org/details/retroachievements_collection_PlayStation_2_N-Z

## 6. What is still UNMEASURED

1. **Whether each of the 50 pickable fighters' GLBs actually loads today.** Model keys exist in `MODEL_URLS` for all 50, but that is a path string, not a load test, and `MODEL-STATUS.md` is three weeks stale. Needs a fresh loader-path / model-key-guard run. **Update 2026-11-08 (Lane 5): 4 of the 50 are now measured** — the soul bodies rin-body, sha-body, kai-body, retsu-body all load through the repo's own vendored GLTFLoader (see §3 note). The other 46 remain unmeasured.
2. **VAIN ABEL and CHORDZ animation banks.** No `MOVESET_MAP` entry; their moveset JSONs were not read. They are pickable on the grid with an unknown bank.
3. **Live fight proof for 48 of the 50 pickable fighters.** Only Pantera vs Demonio has been watched in a real fight. A fighter being pickable does not mean the fight plays right — King Tyrant was pickable and fought T-posed and sunk in the playtest.
4. **ZEN's bank in the public build.** The Dural bank path is private-build only; whether any public-build fallback binds for ZEN beyond procedural combat was not live-checked (ZEN is hidden from the grid, so this only matters if ZEN is unhidden or drawn as an arcade foe).
5. **The select-screen comment contradiction** (ZEN/GYOU "stay selectable" vs both being in `SELECT_HIDDEN`) needs an owner call: unhide them, or fix the comment.
6. **Flyer images on archive.org.** None found there; the Arcade Flyer Archive is the source instead (listed above, not archive.org).

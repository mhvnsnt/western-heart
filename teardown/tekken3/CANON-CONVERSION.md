# TEKKEN 3 → WESTERN HEART — CANON CONVERSION RECORD (iron-legacy)

**Lane:** Tekken 3 sub-lane, FULL WIRING + CANON CONVERSION (owner order 2026-10-20 ~08:06 CDT).
**Branch:** `tekken3-wiring-20261020`. **Date:** 2026-10-20.
**Universe name:** Tekken 3 → `iron-legacy` (root `RENAME-MAP.md`, "The legacy iron-fist tournament").
**Companion file:** `WIRING-INVENTORY.md` (every file, its status, its consuming path).

Rules this record follows: no invented names or canon — every mapping below cites the repo
document that already establishes it. Anything without a documented mapping is FLAGGED, never
filled in. The conversion layer is ADDITIVE: teardown files keep their source names for
provenance (the game's own pattern — see §3), and WH canon names are applied at the layer the
game reads (roster data, moveset files, library indexes, canon docs).

---

## 1. Universe / directory rename — status

`RENAME-MAP.md`'s own rename table lists `teardown/tekken3/` → `teardown/iron-legacy/` as
**PENDING**, and its safety rules require updating ALL references and verifying the game still
boots before a rename lands. This lane did **not** execute the directory rename: the path
`teardown/tekken3/` is referenced by `game/js/t3anims.js`, `game/js/movesets.js`,
`lab/tools/t3_motion_bake.py`, `lab/tools/export_moves.py`, the stage pipeline docs, and this
teardown's own tools. Renaming it is a coordinator-sequenced step (root files are shared by
four lanes). What this lane did apply: the `iron-legacy` name is now used for Tekken 3 in the
canon appendix added to root `CANON.md` and the correction appendix in `RENAME-MAP.md`, and
this file is the per-game conversion source of truth the coordinator reconciles from.

## 2. Character conversions (source → WH canon)

Two levels exist in canon and both are recorded: the **soul** (ROSTER.md's Nine Souls) and the
**playable vessel** (CANON.md / `game/ui-wh/roster_canon.json` / `game/js/roster-full.js`).

| T3 source | WH vessel (playable) | Soul | Evidence (repo) | Data status |
|---|---|---|---|---|
| King (divmot03) | **PANTERA** | TOU | CANON.md §2 PANTERA ("King's pro wrestling grappling"); `roster_canon.json` PANTERA body; `roster-full.js` pantera base 'King' | WIRED: anim bank `game/assets/anim/t3/king_on_pantera_leoman/`, moveset `game/assets/movesets/pantera.json` |
| Jin (divmot09) | **DEMONIO** | RIN | CANON.md §2 DEMONIO (body "Jin's karate frame"); `game/js/t3anims.js` ("Tekken's Jin = DEMONIO, owner canon 2026-10-19"); `roster-full.js` demonio base 'Jin Kazama' | WIRED: `game/assets/anim/t3/jin/`, `game/assets/movesets/demonio.json` |
| Yoshimitsu (divmot04) | **PHANTOM** | JIN (the blade) | CANON.md §2 PHANTOM (body "Yoshimitsu's armored frame"); `roster-full.js` phantom base 'Yoshimitsu' | WIRED: `game/assets/anim/t3/yoshimitsu/`, `game/assets/movesets/phantom.json` |
| Heihachi (divmot13) | **DIABLO** | — (the intruder, "not one of the nine") | CANON.md §2 DIABLO; `roster_canon.json` DIABLO body "Heihachi's devastating frame"; `roster-full.js` diablo base 'Heihachi' | Moveset WIRED (`game/assets/movesets/diablo.json`); anim bank NOT decoded — BLOCKED, §5 |
| Bryan (divmot12) | **SKULL** | RETSU | CANON.md §2 SKULL (body "Bryan's brutal frame"); `roster-full.js` skull base 'Bryan Fury' | WIRED: `game/assets/anim/t3/bryan/`, `game/assets/movesets/skull.json` |
| Gun Jack (divmot16) | **SAM-UR-A1** | — (built, no soul) | CANON.md §2 SAM-UR-A1 (body "Gun Jack's heavy frame"); `t3anims.js` SOURCE_TO_BANK gunjack; `roster-full.js` samura1 moveset 'gunjack' (its `base: 'Jack-7'` label refers to the T7 model source, not the T3 data source) | WIRED: `game/assets/anim/t3/gunjack/`, `game/assets/movesets/samura1.json` |
| Xiaoyu (divmot07) | **SAKU RA** | SHA | CANON.md §2 SAKU RA (body "Xiaoyu's flowing frame"); `roster-full.js` sakura base 'Xiaoyu' | WIRED: `game/assets/anim/t3/xiaoyu/`, `game/assets/movesets/sakura.json` |
| Paul (divmot00) | **TOU** (soul fighter, id `tou`) | TOU | ROSTER.md TOU (style/body donor Paul Phoenix); `roster-full.js` tou base 'Paul Phoenix'; CANON.md §4 note: "TOU and GYOU await T6/TTT2 extraction" — the T3 source now exists (below) | Bank + moveset EXTRACTED 2026-10-20; game moveset `tou.json` still proxies Heihachi (`roster-full.js` tou moveset 'heihachi') — conversion pending §3 |
| Eddy (divmot08, shared Eddy/Tiger bank) | **KING TYRANT** | KAI | CANON.md §3 KING TYRANT (owner-locked "Eddy Gordo base", soul "KAI's tide-splinter"); ROSTER.md KAI (style Eddy, body donor King Tyrant) | Bank + moveset EXTRACTED 2026-10-20; `roster-full.js` kai moveset is 'demonio' (proxy) — conversion pending §3 |
| Hwoarang (divmot06) | **GYOU** (soul fighter, id `gyou`) | GYOU | ROSTER.md GYOU (style/body donor Hwoarang); `roster-full.js` gyou base 'Hwoarang' | Bank + moveset EXTRACTED 2026-10-20; `gyou.json` still proxies Demonio — conversion pending §3 |
| Julia (divmot10) | **NIGHTWOLF** (vessel) / **ZEN** (soul) — CONFLICT, §7 | ZEN | CANON.md §6 NIGHTWOLF (owner-locked "Julia Chang base", Julia's Xingyiquan); ROSTER.md ZEN (style/body donor Julia Chang) | Bank + moveset EXTRACTED 2026-10-20; conversion pending + conflict flagged §7 |
| Lei (divmot02) | **BYOU** (soul) — vessel name PENDING OWNER DECISION | BYOU | ROSTER.md BYOU (body donor Lei Wulong, "REPLACED by Rave… T3 Lei moves to legacy"); CANON.md §4 note: "**BYOU is blocked pending the owner's Lei naming decision**" | Bank + moveset EXTRACTED 2026-10-20; conversion waits on the owner's naming decision — FLAGGED §7 |
| Nina (divmot05) | **AWA POP** | SHA (third splinter) | CANON.md §6 AWA POP (owner-locked "Nina Williams base") | Bank + moveset EXTRACTED 2026-10-20; `game/assets/movesets/awapop.json` exists (built from other sources) — T3-source conversion pending §3 |
| Anna (divmot17) | **TORCH** | — (mortal, not called) | CANON.md §6 TORCH (owner-locked "Anna Williams base") | Bank + moveset EXTRACTED 2026-10-20; `game/assets/movesets/torch.json` exists — T3-source conversion pending §3 |
| Dr. Bosconovitch (divmot18) | **DOC FRANK** (Android 9) | — (chose its vessel) | CANON.md §7 DOC FRANK (owner-locked "Dr. Bosconovitch base"); `t3anims.js` SOURCE_TO_BANK maps source 'bosconovitch' → gunjack bank (anim proxy, pre-existing) | Bank + moveset EXTRACTED 2026-10-20 (largest bank: 647 move rows); `docfrank.json` exists — T3-source conversion pending §3 |
| Kuma / Panda (divmot11, shared bank) | **URSA** (name reserved for the bear, not yet a roster fighter) | — | CANON.md §6 DIO owner-locked note: "the bear, if ever pulled, is URSA" | Bank + moveset EXTRACTED 2026-10-20; no roster entry exists — FLAGGED §7 (Panda has no documented mapping at all) |
| Law (divmot01) + Forest Law (divmot20) | **UNMAPPED** | — | No mapping found in CANON.md, ROSTER.md, `roster_canon.json`, or `roster-full.js` (searched 2026-10-20) | Banks + movesets EXTRACTED 2026-10-20 — FLAGGED §7, never invent a name |
| Ogre / True Ogre (divmot14) | **UNMAPPED** | — | No mapping found in the same four sources (searched) | Bank + moveset EXTRACTED 2026-10-20 — FLAGGED §7 |
| Gon (divmot19) | **UNMAPPED** | — | No mapping found in the same four sources (searched) | Bank + moveset EXTRACTED 2026-10-20 — FLAGGED §7 |
| Mokujin (divmot15) | **UNMAPPED + NO BANK** | — | No mapping found; bank absent from the local disc image (BNS record 295 size 0 in `bns-table.pkl`; `docs/BNS-ORGANIZATION-PATTERN.md` motion table) | BLOCKED with evidence §5 |
| Tiger (shares divmot08 with Eddy) | **UNMAPPED** (palette variant of Eddy in T3) | — | No separate mapping found | Shares Eddy's extracted bank/moveset |

## 3. Moveset conversion

**Established naming pattern (already in the game, not invented here):** teardown banks store
no move names — moves are rows. The game's schema-v2 files name each converted move
`"<WH NAME> <input> (T3 <source> r<row>)"` and carry `t3_source` / `t3_row` / `t3_command` /
`anim_ref: "t3:<source>:row:<row>"` provenance (verified in `game/assets/movesets/demonio.json`
and `diablo.json`). That is the canon conversion for moves: WH fighter name + Tekken input
language, source row preserved. Teardown files themselves are **not** renamed — provenance is
the point of the teardown layer, and every existing consumer follows this split.

**This lane's conversion work:**
- 13 round-2 banks extracted (§5) and their full movesets (5,663 rows) produced with the
  teardown's own parser in the exact schema of the original 7 (`movesets/MOVESET-SUMMARY.md`
  round-2 table).
- `moveset-library/animations/ANIMATION-INDEX.json`: Tekken 3 source now indexes all 20
  character banks (was 7) with the stale "pose solving blocked" note replaced by the verified
  current state. `moveset-library/MOVES-LIBRARY.md` source table updated to match.
- The remaining step — schema-v2 game files (`game/assets/movesets/*.json`) for Paul→TOU,
  Eddy→KAI/King Tyrant, Hwoarang→GYOU, Julia→ZEN/Nightwolf, Lei→BYOU, Nina→Awa Pop,
  Anna→Torch, Bosconovitch→Doc Frank, Law/Ogre/Gon (unmapped) — is **pending, flagged §7**:
  the generator that produced the PR #243 game files is not in the repo as a runnable script,
  and hand-writing a one-off converter is exactly the hand-tooling the owner banned
  (NO-HAND-TOOLING LAW). The extracted teardown movesets are the complete, verified input
  for that conversion when the coordinator sequences it.

**Feel note:** today, TOU/KAI/GYOU fighters play on proxy movesets (`tou`→heihachi,
`kai`→demonio, `gyou`→demonio per `roster-full.js`) even though their real T3 banks existed
only as raw disc data. Those real banks + movesets now exist in the teardown; converting them
is the single largest remaining step toward the build feeling like Tekken for those fighters.

## 4. Animation conversion

**Established pattern:** decoded banks become `wh-anim/1` JSON clips under
`game/assets/anim/t3/<bank>/`, one clip per game action (`t3_stance`, `t3_light`, …), loaded by
`game/js/t3anims.js`. Clip provenance (slot, move_row, SHA-256 of KMD/bank/EXE, `hand_keyed:
false`) is embedded in every JSON — conversion is a decode + retarget, never a re-authoring.

**System-clip slot convention (verified identical across all 6 decoded banks — this is a
documented-by-data convention, not an assumption):**

| Clip | Slot | Clip | Slot |
|---|---|---|---|
| t3_stance / _b / _c | 0x0 / 0x1 / 0x2 | t3_sidestep_a–d | 0x11b / 0x11d / 0x11f / 0x121 |
| t3_walk_fwd / _back | 0x15 / 0x18 | t3_block / _b | 0xa85 / 0xa91 |
| t3_dash_fwd / backdash | 0x1b / 0x1e | t3_hit / hit_launch | 0x9a2 / 0x9fc |
| t3_crouch_hold / crouch | 0x28 / 0x3b | t3_ko | 0xd66 |
| t3_jump_up / fwd / back | 0x7f / 0x81 / 0x83 | t3_win_lp / rp / lk / rk | 0xd67 / 0xd68 / 0xd69 / 0xd6a |

Attack clips (light/medium/heavy/grab) were baked by move **row**; the rows are recorded in
`game/assets/<name>_moves.json` (`light/medium/heavy/grab` → `t3_row`) and match the baked
JSONs exactly for King (35/63/230). For Heihachi the recorded rows are light 38, medium 64,
heavy/grab 182 — verified against `moveset_heihachi.json` (damage 12/25/35 matches the
aggregate's `t3_dmg` fields). No guessing is needed for a future Heihachi bake; the blocker is
the model data, §5.

## 5. Extraction & decode — what this lane ran, and the two real blockers

**Ran (all verified):** 13 divmot banks sliced from the in-repo `TEKKEN3.BNS` using the
teardown's own `bns-table.pkl` index (byte offset = sector × 2048, per
`docs/BNS-ORGANIZATION-PATTERN.md`). Every bank: size == table size, header byte 0x01 == divmot
type, SHA-256 prefix == the verified table in that doc (paul 06f6447a, law 14f83938,
lei bd795779, nina 50430e78, hwoarang d0b5b43a, eddy 0383ddb2, julia d4c8ce91, kuma 77804b1f,
ogre f0c14b35, anna 16886320, bosconovitch 130ee660, gon d28e5e77, forestlaw 0aaf8799). The 8
pre-existing banks pass the same three checks. Movesets for the 13 produced by
`tools/local/moveset_extract.py`'s own `extract_bank()` against the in-repo USA `SLUS_004.02`
(104 motion sequences loaded; common bank divmot99, 332 moves). Heihachi's stance OBJ produced
by `tools/local/pose_assemble.py` (slot 0, frame 75, stream 150 frames — same method as the
other six fighters' pose-check OBJs).

**BLOCKER 1 — Mokujin (divmot15) has no data on this disc image.** `bns-table.pkl` record 295
= (sector 17534, size 0); the next record starts at the same sector. The BNS doc's motion table
records the same fact ("MISSING locally (size 0)"). Exhausted: the bank cannot be sliced from
a zero-length record; no other copy of TEKKEN3.BNS exists in the repo. Unblocking requires a
different disc image — an owner-side source decision, not a parser problem.

**BLOCKER 2 — Heihachi wh-anim decode / GLB build.** Attempts, in order:
1. `renders/pose-check/heihachi_stance75.obj` via pose_assemble — SUCCEEDED (18 part groups).
2. `lab/tools/t3_to_gltf.py fighter heihachi.kmd heihachi_stance75.obj` — FAILS:
   `KeyError: 2` at `pivots[0] = pivots[2].copy()`.
3. Root cause verified with two independent parsers (`lab/tools/t3_common.kmd_parse` and
   tekken3remake `kmd.py` via pose_assemble's output): `models/heihachi191/heihachi.kmd`
   rows for parts 2, 9, 13 contain **0 vertices** (Bryan's equivalent rows carry 42/4/4).
4. P2 costume record tested as an alternative source: BNS 195 sliced and parsed the same way —
   parts 2/9/13 are also 0-vertex there (part 1 differs: 75 vs 56 verts, part 17: 90 vs 96).
   The empty parts are a property of Heihachi's model data in this extraction, not a P1 defect.
5. `lab/tools/t3_motion_bake.py` has the same part-2 pivot assumption in `T3Space`, so the
   bake cannot run either. Fixing it means editing the shared bake tool or inventing pivot
   data for the missing parts — both prohibited (NO-HAND-TOOLING; per-character isolation:
   a shared-tool edit risks every other fighter's bake). FLAGGED for the coordinator with
   this evidence; Diablo keeps his wired moveset and his proxy animation state
   (`t3anims.js`: `heihachi: null`, "no decoded bank exists — intentionally absent" — that
   comment's premise is now half-fixed: the raw bank + moveset were always there; the decode
   is what's blocked).

**Also flagged (docs gap):** `t3_motion_bake.py`'s docstring cites `docs/anim/T3_MOTION_BAKE.md`,
which does not exist in the repo.

## 6. Stage conversion

All 15 T3 stage panoramas are wired (`game/js/stages.js` `T3_RETRO` registry →
`game/assets/stages/t3/stg_<letter>_{panorama.obj,atlas.png}`):

| Letter | Source home fighters (TEARDOWN.md stage table) | Game id | WH canon name |
|---|---|---|---|
| a | Paul / Bryan | `t3-a` | NOT ASSIGNED in canon — see below |
| b | Law / Kuma / Panda | `t3-b` | NOT ASSIGNED |
| c | Yoshimitsu / Mokujin | `t3-c` | NOT ASSIGNED |
| d | Xiaoyu | `t3-d` | NOT ASSIGNED |
| e | Hwoarang | `t3-e` | NOT ASSIGNED |
| f | Lei | `t3-f` | NOT ASSIGNED |
| g | Ogre / True Ogre | `t3-g` | NOT ASSIGNED |
| n | Xiaoyu / Jin | `t3-n` | NOT ASSIGNED |
| i | Jin | `t3-i` | NOT ASSIGNED |
| j | Nina / Anna / Gun Jack | `t3-j` | NOT ASSIGNED |
| k | Eddy / Tiger | `t3-k` | NOT ASSIGNED |
| l | King | `t3-l` | NOT ASSIGNED |
| m | Julia / Heihachi | `t3-m` | NOT ASSIGNED |
| t | Gon | `t3-t` | NOT ASSIGNED |
| u | Doctor B. | `t3-u` | NOT ASSIGNED |

No repo document maps individual T3 stages to WH lands/arenas (CANON.md's five lands have no
T3-stage correspondence table), so no WH stage names were invented. The registry entries in
`game/js/stages.js` still carry third-party labels (`name: "T3 RETRO: KING"`,
`universe: "Tekken 3 (legacy)"`, `homeFighters`). `game/js/` is owned by the engine lanes —
this lane did not edit it. FLAGGED §7: the engine lane can rename these labels once the
owner/coordinator assigns WH arena names; the data (geometry, atlas, dims, lighting) needs
no change.

## 7. FLAGGED items (nothing invented, each with its reason)

1. **Law / Forest Law, Ogre, Gon — no WH canon mapping exists** in CANON.md, ROSTER.md,
   `roster_canon.json`, or `roster-full.js`. Owner canon decision required before any
   conversion. Their banks + movesets are extracted and ready.
2. **Mokujin — no bank on this disc image** (Blocker 1, §5) and no canon mapping.
3. **Panda — no documented mapping** (shares divmot11 with Kuma; Kuma's reserved name is
   URSA per CANON.md, as a future pull, not a roster entry).
4. **Lei / BYOU vessel name — owner decision pending**, per CANON.md itself ("BYOU is blocked
   pending the owner's Lei naming decision"). ROSTER.md's "REPLACED by Rave" refers to the
   playable slot (Rave is Kiko Tanaka's WH form, CANON.md §7 KIKO TANAKA), not a Lei rename.
5. **Julia three-way conflict:** ROSTER.md (ZEN's body donor = Julia, style Xingyiquan),
   CANON.md (NIGHTWOLF's base = Julia, same Xingyiquan; §4 note says ZEN's body = T7 Julia),
   `game/js/roster-full.js` (zen base = 'Heihachi', moveset 'heihachi'). Three repo sources
   disagree about what Julia's data drives today. Coordinator/owner call; this lane changed
   none of them.
6. **Heihachi anim decode blocked** on his KMD's empty part rows (Blocker 2, §5). Diablo's
   `t3anims.js` registration (`heihachi` bank + `diablo`/`heihachi` SOURCE_TO_BANK entries)
   is a one-line engine-lane change that only makes sense after the decode lands.
7. **Schema-v2 game movesets for the 13 round-2 banks** await the PR #243 generator (not in
   the repo) or a coordinator-approved conversion lane — §3. Until then TOU/KAI/GYOU and
   others keep proxy movesets at the game layer (feel gap, §8).
8. **Stage registry labels** in `game/js/stages.js` still use third-party names (§6) —
   engine-lane rename pending WH arena name assignments.
9. **T3 retro attires not wired:** TEARDOWN.md's stated role for T3 models is "ALT COSTUMES —
   retro skin selectable as an attire", but `game/js/attires.js` contains no T3/retro entry
   (searched) and the T3 GLBs live only in `lab/game/assets/`. The retro-attire wiring is a
   game-layer step that has not happened.
10. **UI art (23 files) not wired** — extraction templates per `ui/README.md`; WH UI
    generation from them is future work, no consumer exists today.
11. **TEARDOWN.md internal inconsistencies** (recorded, not silently rewritten): its
    "Correction 2026-10-13" BNS table (Jin 143, Bryan 167, Heihachi 175, Gun Jack 199)
    contradicts both `docs/BNS-ORGANIZATION-PATTERN.md` (Jin 151, Bryan 183, Heihachi 191,
    Gun Jack 215) and the actual model folders (`models/jin151`, `bryan183`, `heihachi191`,
    `gunjack215`). The BNS-pattern values are the ones verified by extraction (this lane's
    P2 test used 195 = Heihachi P2 under the pattern and parsed a valid Heihachi variant).
    TEARDOWN.md also still lists remaining-character extraction and pose sampling as
    blocked/pending, which this lane's work supersedes.

## 8. Feel-blocking gaps (acceptance bar: "actually FEELS like playing Tekken")

1. **Proxy movesets on real fighters:** TOU (Paul), KAI (Eddy), GYOU (Hwoarang) — and the
   soul fighters generally — play on borrowed movesets at the game layer today. Their real
   banks + full movesets (372–604 rows each) now exist in the teardown (§3); the schema-v2
   conversion is the gap, not the data.
2. **Diablo has no decoded animation bank** (§5, Blocker 2): the boss fighter's T3 motion
   cannot play; he animates through the generic/proxy path while all six other T3-sourced
   Seven have real banks.
3. **Only 7 of 20 character banks have game-layer anything.** The other 13 fighters' motion
   exists only as raw banks + frame data. Any future fighter built on Law/Ogre/Gon/Bosconovitch
   data starts from extracted, verified inputs — but nothing plays yet.
4. **Engine-layer items this lane was barred from touching** (flagged, not fixed): stage
   labels (§6), `t3anims.js` bank registry (§5), `attires.js` retro attires (§7.9), and the
   known fighter.js tint/stance issues the owner raised 2026-10-20 (outside this lane's
   data scope entirely).

## 9. Per-character isolation statement

**Gating method:** every artifact this lane produced is per-character by construction and
touches no shared state:
- Each divmot bank was sliced independently from its own BNS record and verified against its
  own SHA — no bank's bytes were derived from, or merged into, another's.
- Each moveset was parsed from its own bank file into its own `moveset_<fighter>.{json,csv}`
  (the only shared input is the read-only divmot99 common bank, exactly as the original 7
  were parsed — T3's own design: bank rows reference common-bank anims via the COMMON_FLAG,
  resolved by the parser, never copied between character banks).
- The one stance OBJ generated (Heihachi) derives only from Heihachi's KMD + divmot13.
- No shared rig, shared animation file, global pose/retarget code, or engine file was edited.
  The shared bake tool (`lab/tools/t3_motion_bake.py`) was deliberately NOT patched for the
  Heihachi part-2 blocker, because a shared-tool change could alter every other fighter's
  bake — the blocker is reported instead (§5).
- Library edits (`ANIMATION-INDEX.json`, `MOVES-LIBRARY.md`) are additive index entries;
  the 7 original bank entries are byte-identical to before.

**Deliberate parallels sharing (genuine T3 source sharing, by the source's own design):**
- divmot99 (common bank) is referenced by all character banks — Tekken 3's own architecture,
  preserved as-is.
- divmot08 is one bank shared by Eddy and Tiger in T3 itself; divmot11 is one bank shared by
  Kuma and Panda in T3 itself. They were extracted once, as the source stores them, and are
  documented as shared wherever they are cited.
- The system-clip slot convention (§4) is a property of the game's own move-index layout,
  identical in every bank — recorded as data, not code shared by this lane.
No other sharing was introduced. No character gained another character's skeleton, animations,
or add-ons; no add-ons (extra arms, jiggle, wings, extra hands/wrists) were touched at all.

## 10. Rename / conversion log (everything this lane changed)

| # | Item | Conversion | Where |
|---|---|---|---|
| 1 | 13 motion banks | Extracted under source names (provenance pattern of the original 8); canon mapping recorded | `animations/divmot{00,01,02,05,06,08,10,11,14,17,18,19,20}_*.bin`; mapping in §2 |
| 2 | 13 movesets | Extracted under source names; WH conversion pattern documented (WH name + input + `t3:` provenance) | `movesets/moveset_*.{json,csv}`; pattern in §3 |
| 3 | Moveset summary | Round-2 table appended (original 7-bank section untouched) | `movesets/MOVESET-SUMMARY.md` |
| 4 | Animation index | Tekken 3 source: 7 → 20 character banks indexed; stale blocked-note replaced | `moveset-library/animations/ANIMATION-INDEX.json` |
| 5 | Library doc | Source table: "7 banks" → "20 character banks + common" | `moveset-library/MOVES-LIBRARY.md` |
| 6 | Heihachi stance | `heihachi_stance75.obj` created (had no pose-check OBJ) | `renders/pose-check/heihachi_stance75.obj` |
| 7 | Root canon | Tekken 3 / iron-legacy appendix added (append-only, delimited) | `CANON.md` |
| 8 | Root rename map | Correction/completion appendix added (append-only, delimited) | `RENAME-MAP.md` |
| 9 | This record + inventory | Created | `teardown/tekken3/CANON-CONVERSION.md`, `WIRING-INVENTORY.md` |

No files were renamed on disk and nothing was deleted. The `iron-legacy` directory rename
remains PENDING in `RENAME-MAP.md` for coordinator sequencing (§1).

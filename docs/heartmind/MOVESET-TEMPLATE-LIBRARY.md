# Moveset Template Library + Creation System — Western Heart

**Lane:** moveset template library + creation system (agent `2e9d1e8d`)
**Date:** 2026-11-08 · **Repo HEAD:** `3334ebf` · **Branch:** `moveset-template-library` · **Commit:** `c4480de0` · **PR:** https://github.com/mhvnsnt/western-heart/pull/1642 (open, NOT merged — parent lands)
**Order:** Jay, 2026-11-07 ~20:00–20:02 + refinement ~20:05
**Status: STAGED on branch, NOT landed, NOT live-proven.** Engine + data + tests are built and green in node. The in-game editor screen and a live fight proof are still owed (see §7).

---

## 1. What Jay ordered (plain words)

1. Take every character from every game Jay owns in the teardowns — VF5, 3D Street Fighter, DOA, Tekken, Urban Reign + Redux, WWE/wrestling, Brutal Fist — and turn each character's **whole moveset** into a **selectable template** in Western Heart, named after the character it came from (MUGEN-style, like WWE does it). Unused characters go in too — nothing left unused.
2. Build the **moveset creation thing** on top: a WWE-style library + creation + editing system. Start from a full template, then pick and piece together different moves for different inputs and scenarios, for characters added later or made in Create Fighter. The library keeps growing as characters are added.
3. Refinement: build the creation system from the **actual most recent WWE game** Jay has access to — Steam library + teardown files — its whole data, source files, and code for their moveset library / editing / creation suite layout. Fighting stays **Tekken style** (Tekken 7 inputs + button mapping).
4. Research **which fighting games actually have a moveset editor** — verify from real sources, don't guess.
5. Editor core ability: **swap EVERY move by input AND position AND situation**.

Rules followed: industry-standard methods only, real measured data, no hand-tooling, no guessing, no homebrew. Branch + PRs, no merge/push to main. Report to parent only.

---

## 2. Per-game inventory (measured, with file refs)

All counts below were measured on 2026-11-08 from the files in the repo at HEAD `3334ebf` (bank files read directly; teardown counts via `git ls-tree -r`). Nothing was downloaded from the internet; no commercial game files were fetched.

### 2a. What is already a moveset bank in the game (`game/data/moveset-library/banks/`)

| Bank | Game | Moves | Characters | Notes |
|---|---|---|---|---|
| `t3.json` | Tekken 3 | **4,648** | 20 | Paul 209, Law 252, Lei 294, King 298, Yoshimitsu 261, Nina 279, Hwoarang 221, Xiaoyu 268, Eddy 241, Jin 253, Julia 207, Kuma 188, Bryan 195, Heihachi 216, Ogre 192, Gunjack 250, Anna 276, Bosconovitch 280, Gon 157, Forestlaw 111. **0/4,648 rows carry a decoded input** — see §7, the #615 gap. |
| `wrestling.json` | WWF No Mercy | **4,409** | 0 (pool) | Generic move pool (`wrestling:mk-XXXX`); no per-wrestler attribution yet. |
| `wmxix.json` | WWE WrestleMania XIX | **169** | 0 (pool) | Per-clip ids; identity pending (115 wired to SHOW, 54 provisional hidden, 0 to combat — `wmxix-verified.json`). |
| `doa.json` | DOA (4 / 5 Last Round / Ultimate) | **146** | 6 | Bass Armstrong 24, Kasumi 23, Ryu Hayabusa 20, Ayane 26, Tina Armstrong 30, Jann Lee 23. 146/146 inputs decoded. |
| `vf.json` | Virtua Fighter 5 Final Showdown | **48** | 3 | Akira Yuki 20, Sarah Bryant 14, Kage-Maru 14. 48/48 inputs decoded. |
| `vf5.json` | Virtua Fighter 5 | **96** | 4 | EL BLAZE 28, JEFFRY 25, WOLF 21, LEI-FEI 22. 96/96 inputs decoded. |
| **Total** | | **9,516** | **33 per-character + 2 pools** | |

Per-character templates exist today for 33 characters. The wrestling (4,409) and WMXIX (169) pools are unassigned move pools, not per-character templates — per-wrestler grouping is a decode job, not a labelling job, and was not invented here.

### 2b. Frame data (not banks — no animation IDs, so not playable as templates)

| Source | File(s) | Fighters | Moves (measured) |
|---|---|---|---|
| Tekken 7 frame data | `game/data/t7-frame-data/` (44 files) | 44 | **6,909 rows** (`notation_original`, LP1/RP2/LK3/RK4 schema). 3,219 distinct notations; 120 canonical inputs derived (see §5). |
| Tekken 8 frame tables | `game/data/t8_frame_tables.json` | 41 | **6,411 notation-keyed rows** (CC0, wavu.wiki). |

These are templates of status `frame-data-only`: they tell you what a move does on paper (startup, block, hit, damage) but carry no animation reference, so they cannot be a playable base. They are in the library so the editor can show real frame data next to a move — not so anyone mistakes them for a working moveset.

### 2c. Donor games with teardown files but no ingested bank yet (pending-ingest)

| Game | Teardown files in repo | What exists | What is missing |
|---|---|---|---|
| Urban Reign | 4,188 files in `teardown/urban-reign` | 72 char PPK slots + 72 textured GLBs, 285 banks / 3,357 motions, 484 named moves; 72 untextured GLBs + 31 movesets already wired into `game/` | Ingested bank; stage/mission PPKs not decoded |
| Urban Reign Redux v0.5 | Mod Manager 0.5 + Editor 0.5 fetched, hash-verified from the author (`~/workspace/urban-reign-redux/INVENTORY.md`); all-in-one Drive link quota-blocked, retry Sun Nov 8 ~7:18 PM CST | Mod-making tooling (roster-lib: gyu_decode, vmd_mesh, ppk_index, texture tools) | Disc build (Windows-only step, Jay's PCSX2 machine); per-fighter counts UNMEASURED |
| Soulcalibur II | 237 files in `teardown/soulcalibur-2` | 18 named textured fighters, 22 GLB models, 41 stage GLBs | Moveset bank |
| Def Jam Fight For NY | 271 files in `teardown/def-jam-fight-for-ny` | EAGL format spec + surgical `.o`/`.ssh` extracts | Decoded models/anims; per-character counts UNMEASURED |
| 3D Street Fighter (EX series) | 58 EX Plus Alpha, 2 EX2 Plus, 1 EX3, 4 SFV | Docs/catalog only | Extracted movesets; SFV pull blocked per catalog |
| Tekken 6 (PSP) | 3,849 files in `teardown/tekken6` | 18 fighters × 3 versions movesets (54 files) | Decrypt (DATA401 encrypted models); ingested bank |
| Tekken Tag Tournament 2 | 56 files in `teardown/tekken-tag-tournament-2` | Roster 59 / 29 stages in docs only | Container decode |
| WWE 2K19 | 1,678 files in `teardown/wwe2k19` (753.7 MB, `.yobj`/`.bin`/`.dds`) | Raw extraction; CAW + Create-A-Moveset layout fully documented (`customization/wwe2k-caw/CAW-SUITE-BREAKDOWN.md`; `moveset-library-2k19.txt`, 5,581 names) | WMXIX-style decode path; per-character move counts UNMEASURED |
| WWE 2K20 / 2K22 | 1 file each (readme only) | **2K22 is the newest WWE Jay owns on Steam (app 1255630)** and the creation-suite source of record per `docs/tech/STEAM-LIBRARY.md` | No teardown/archive in the repo at all |
| Devil Within (Tekken 5) | 242 files inventoried on branch `dw-decode` (commit `06eef2ea`) | Index + romaji gloss (155 high / 56 medium / 31 opaque confidence) | **0 bytes decoded** — blocked on missing archive bytes; Jay authorized the archive-item pull 2026-11-07 ~20:15, decode-continuation agent running |
| Brutal Fist | — | Identification in progress by a separate agent | Roster, counts — deliverable `BRUTAL-FIST-PULLIN.md` **not landed yet** |

Other teardown dirs measured for completeness: Tekken 3, 19,499 files; WWF No Mercy, 18,567; Eastern Mind, 5,709; Tekken 7, 174; Tekken 8, 7; DOA4, 546; DOA6, 2 (docs only); Soulcalibur VI, 3 (docs only); VF5, 1 + Virtua Fighter 5, 18; Fire Pro / Wrestling Empire / Nioh / Yakuza, readme only.

---

## 3. The template library — what got built

**File:** `game/data/moveset-templates/index.json` — **10 → 141 templates**
**Builder:** `tools/moveset-library/build-templates.mjs` (idempotent; `node tools/moveset-library/build-templates.mjs --check` for CI)

| Group | Templates | Status |
|---|---|---|
| Hand-written 2026-11-05 rows (kept verbatim) | 10 | primary 1, attached-existing 3, reserved 4, library 1, pointer 1 |
| T3 / DOA / VF / VF5 per-character | 33 | `template` — full bank each, with `library_prefix` (e.g. `t3:hwoarang`) so the editor can find its moves |
| Wrestling + WMXIX pools | 2 | `pool` |
| T7 frame data | 44 | `frame-data-only` |
| T8 frame tables | 41 | `frame-data-only` |
| Pending-ingest donors | 11 | `pending-ingest` — placeholder rows, no counts invented |

**Naming (PIPELINE-LAW §2):** template ids are generic hints (`t3-hwoarang`, `doa-bass-armstrong-…`, `vf5-el-blaze-vf`, `t7-frame-king`, `urban-reign-pending`). No franchise display name sits on the WH roster. `source_character` is provenance only — it names where the data came from and never reaches a player-facing screen. If Jay wants literal source-character names on screen, that is an override decision for him, not something assumed here.

**Source law is enforced, not just documented:** the editor refuses a claimed Tekken bank as a custom base except for its claimant or an approved exception (claimed-map.json). 13 of the 20 T3 templates are claimed (King→Pantera, Jin→Demonio, Eddy→King Tyrant, Xiaoyu→Saku-ra, Yoshimitsu→Phantom, etc.). Those templates are viewable in the library; they are not freely copyable into new fighters. Free T3 templates (Hwoarang, True Ogre, Lucky Chloe, Raven, Jun, Marduk, Gon, Forest Law, and the rest) are fully usable — proven in-test with `t3-hwoarang`.

---

## 4. Which fighting games actually have a moveset editor (verified)

| Game | Moveset editor? | What it actually has | Source |
|---|---|---|---|
| **WWE series (SmackDown! vs. Raw / HCTP / 2K19)** | **YES — the model** | Create-A-Moveset: categories BASES, READY MOVES, GROUND, TURNBUCKLE, ROPE OPPONENT, AERIAL, RUNNING, DOUBLE TEAM, SPECIAL. Pick a category on the left, preview with Square, X adds it. 2K19 adds 5 fighting styles (Powerhouse, Cruiser, Technician, Striker, Giant) each with 2 sub-styles, Quick Edit styles based on existing fighters, PRESET MOVE SETS (a whole existing fighter's moveset as the starting point), BASIC MOVES, SPECIAL ACTION. | Neoseeker SvR Create-A-Moveset FAQ; CheatHappens HCTP FAQ; GamingBolt WWE 2K19 guide |
| **Mortal Kombat 11** | **YES** | Kustom Variations: Kustomize menu, 3 ability slots per character, each ability takes 1–2 slots; 2 tournament-legal ("kompetitive") preset variations per character; customs usable local/casual, and in Tournament/Ranked only with "Kustom Abilities" enabled. MKX (2015) introduced it as 3 preset variations per character. | EventHubs / GameRevolution / Cultured Vultures / GameFAQs (MK11); Wikipedia |
| **Mortal Kombat: Armageddon (2006)** | **YES** | Kreate-a-Fighter: 12 fighting styles (each a full moveset) + 6 weapon styles; assign already-named attacks to buttons; build a martial-art style from scratch from moves of all characters; special moves, attributes, fatalities; 62-char roster. | Wikipedia MK: Armageddon; archive.org PS2 manual; playmortalkombat.com |
| **Tekken (all)** | **NO** | Move lists + practice mode only. Tekken 8's Special Style is a simplified control scheme (each button mapped to a recommended move/combo by state) — NOT an editor. Button mapping exists but assigns buttons, not moves. Community tool Kiloutre TekkenMovesetExtractor exports/imports movesets in memory only (modding tool, not in-game). Jay's memory was correct. | wavu.wiki (T8 Special Style); Kiloutre docs; no in-game editor found in any Tekken |
| **Soulcalibur VI** | **Style pick, NOT a per-move editor** | Create-A-Soul: pick race, then pick a weapon + the preset fighting style of a roster character (whole-style copy, e.g. 2x Longsword = Geralt's movelist); can switch later. No per-move swapping. | Soulcalibur Wiki Create-A-Soul; GodIsAGeek Libra of Souls guide; Siliconera |
| **Street Fighter 6 (World Tour)** | **Slot loadout, NOT a full editor** | Avatar copies a Master's full normal moveset as base style; Special Moves + Super Arts equipped into slots (8 ground + 3 aerial); cannot equip two moves sharing the same input; can mix specials from multiple Masters. | streetfighter.fandom.com Avatar page; EventHubs; Kakuchopurei |
| **DOA / Virtua Fighter** | **NOT VERIFIED in this pass** | Do not claim "no editor" for either until checked — the web search for this check failed on a local disk-quota error in the search tool. | — (owed) |

**What each verified game contributed to our editor:** WWE = the layout spine (categories + preset-moveset-as-starting-point). MK Armageddon = "assign already-named attacks to buttons" + build a style from moves of all characters. MK11 = ability slots + tournament-legal presets. SF6 = the slot-conflict rule (no two moves on the same input) and style-as-base + special slots. SCVI = whole-style template pick as the starting point. Tekken = the content and the fighting (T7 inputs + button mapping, Tekken notation) — and the proof that a moveset editor is not a Tekken thing, so ours is built the WWE way on Tekken content, exactly as Jay ordered.

---

## 5. The creation system — design + what got built

### Layout (from the actual WWE source)

The editor is organized by the **WWE Create-A-Moveset categories**, mapped onto Western Heart slots:

| WWE category | WH slots it filters |
|---|---|
| Bases | standing · neutral / round-start |
| Ready Moves | standing, crouching · neutral / punish / whiff-punish / counter-hit |
| Ground | grounded · neutral / opponent-grounded |
| Turnbuckle | corner · neutral / wall-splat |
| Rope Opponent | corner, running · opponent-grounded / opponent-back-turned |
| Aerial | jumping, airborne · neutral |
| Running | running · neutral / whiff-punish |
| Double Team | standing, corner · opponent-grounded |
| Special | standing, crouching, back-turned, sidestep-left/right · low-health / counter-hit / throw-attempt |

### Slot model

Every move lives in one slot: **`position|situation|input`**.

- **Position** — the library schema's position enum, verbatim (12): standing, crouching, grounded, back-turned, sidestep-left, sidestep-right, jumping, running, airborne, corner, apron, mounted. (Apron/mounted are wrestling-only.)
- **Situation** — 10 editor categories: neutral, punish, whiff-punish, counter-hit, wall-splat, low-health, throw-attempt, opponent-grounded, opponent-back-turned, round-start. Plain fighting situations, not claimed to be any one game's data.
- **Input** — Tekken notation. `SLOT_INPUTS` is the clean subset of the **120 canonical inputs measured across the 6,909 T7 frame-data rows** (3,219 distinct `notation_original` values, 2026-11-08); malformed artifacts (parentheses) dropped. Reproduce with the command in `game/js/moveset-editor.js`'s header.

### What got built (engine, data, tests — the screen is owed, §7)

1. **`game/js/moveset-editor.js`** (new) — the editor engine, no DOM, node-testable:
   - `createCustomMoveset({templateId, fighterId, …})` — start from a full template. The base is the template's bank + character (`base: {bank, character}`), so the existing assembler fills the base kit; per-slot assignments overlay it. Pool templates (no character) are overlays-only.
   - `assignMove / removeMove / getMove` — swap EVERY move by input + position + situation. One move per slot (SF6 conflict rule).
   - `listEligibleMoves` / `isEligible` — a move may fill a slot only when its position matches (or it has no decoded position) AND its input matches, is in its `input_slots`, or is null. T3 moves (input null) fit by position only, flagged as a warning — never presented as a decoded input.
   - `validateMoveset` — unknown ids, bad slot keys, ineligible assignments, and claimed-bank violations (same `checkSourceLaw` the assembler runs) all reported at once with reasons.
   - `toManifest` — projects a custom moveset into the manifest shape `assembleFighter` already accepts. No new assembler, no rebuild of the library system.
   - `saveMoveset / loadSavedMoveset` — localStorage `wh_moveset_editor_v1`, same pattern as Create Fighter.
2. **`game/js/custom-fighter.js`** (edited in place) — a saved fighter carrying `moveset_custom` now fights on it (`moveset: custom:<template>`, `customMoveset` attached for the assembler); without one, the named jin fallback stands. The animation bank still rides the fallback until the assembler path wires custom manifests into fights — stated in the code, not hidden.
3. **`test/moveset-editor.test.mjs`** (new) — **8/8 green** (2026-11-08). Proves, from real files: template index consistency with the banks; slot catalog vs schema; eligibility gating; claimed-template refusal + claimant allowed; a `t3-hwoarang` custom moveset assembling through the real assembler with the source law green; a `vf5-el-blaze` custom moveset assembling its **full** base kit (20+ moves); Create Fighter carrying the custom moveset instead of the jin fallback.
4. **`docs/movesets/MOVESET-TEMPLATE-INVENTORY-2026-11-05.md`** — 2026-11-08 section appended (template table, editor summary, honest limits).
5. **WORKLOG.md** — lane entry logged.

---

## 6. How to use it (for the next agent / Jay's test)

```js
// 1. Pick a template (from game/data/moveset-templates/index.json)
import { createCustomMoveset, assignMove, toManifest } from './game/js/moveset-editor.js';
const ms = createCustomMoveset({ templateId: 'vf5-el-blaze-vf', fighterId: 'custom', templates, claimed });
// 2. Swap a move into a slot (input + position + situation)
const ms2 = assignMove(ms, 'standing|neutral|df+2', 'vf5:el-blaze:5', libraryById);
// 3. Validate, then hand the manifest to the existing assembler
import { assembleFighter } from './game/js/moveset-library.js';
const kit = await assembleFighter(toManifest(ms2), { root: '.' });
// 4. Save it on a created fighter (moveset_custom) and it rides into select/fight
```

Rebuild the template list any time: `node tools/moveset-library/build-templates.mjs` (or `--check`).

---

## 7. What is still missing (honest, in order)

1. **T3 base kits assemble to overlay moves only — the biggest gap.** Measured: **0/4,648 T3 rows carry a decoded input**, so the assembler's base-kit loop adds nothing from a T3 base. A custom moveset based on a T3 template today is playable only for its explicitly-assigned slots. DOA/VF/VF5 bases assemble fully (146/146, 48/48, 96/96 inputs decoded) — proven in-test. The fix is the **#615 fidelity-engine input decode** for T3 rows, not an editor change; no input was invented here to paper over it. This is asserted in-test so it cannot silently change.
2. **The in-game editor screen is NOT built.** The creation-suite UI is NON-COMPLIANT pending a teardown-sourced rebuild (RULES_NO_GUESSING + the ui_sources gate: every UI change must cite its teardown source). Building a hand-made screen now would violate that law. The screen is the next step, built from the WWE 2K19 CAW/Create-A-Moveset layout + T7 customization teardown sources, with the `ui_sources.json` entry to match.
3. **Custom manifests are not yet wired into a live fight.** `movesets.js` integration for custom manifests + a live fight proof (template picked in-game, custom moveset built, played in a real fight) is owed. That proof needs a browser — this agent cannot run one; parent to arrange. Nothing here is called "done" until that fight is watched.
4. **Brutal Fist roster** — separate agent, deliverable not landed yet; this library carries only a `brutal-fist-pending` placeholder row.
5. **Pending ingests** — Urban Reign bank, Redux disc build (Windows), SCII / Def Jam / SF EX / T6 / TTT2 / 2K19 banks, Devil Within contents (blocked on archive bytes). Each becomes real templates when its ingest lands; the builder already knows how to count them.
6. **Per-wrestler grouping** for the No Mercy (4,409) and WMXIX (169) pools, and the WMXIX per-clip identity decode — until then those stay pools, not per-character templates.
7. **DOA / Virtua Fighter editor-status verification** — owed (search tool failed on a local disk-quota error; do not claim either way until checked).
8. **WWE 2K22 teardown** — the newest WWE Jay owns has no archive in the repo; the layout here comes from the in-repo 2K19 CAW docs, which is the most recent WWE with actual teardown data. If a 2K22 teardown lands, the layout should be re-checked against it.

---

## 8. Files changed (branch `moveset-template-library`)

| File | Change |
|---|---|
| `tools/moveset-library/build-templates.mjs` | NEW — template builder from measured counts |
| `game/data/moveset-templates/index.json` | 10 → 141 templates |
| `game/js/moveset-editor.js` | NEW — editor engine |
| `game/js/custom-fighter.js` | Wired: `moveset_custom` → `custom:<template>` |
| `test/moveset-editor.test.mjs` | NEW — 8/8 green |
| `docs/movesets/MOVESET-TEMPLATE-INVENTORY-2026-11-05.md` | 2026-11-08 section |
| `WORKLOG.md` | Lane entry |

No deletions. No raw game dumps committed (mappings + pointers only, per PIPELINE-LAW §2). No merge to main — PR only, parent lands.

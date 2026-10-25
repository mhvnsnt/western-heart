# Heart and Mind Within — Campaign Structure (Lane 6, 2026-10-24)

What this PR adds on top of the existing mode, where each piece came
from, and what is still missing. This doc builds on
`docs/modes/HEART-AND-MIND-INSIDE.md` (the mode design doc) and
`docs/research/REALM-TRAVEL-CANON-2026-10-23.md` (realm travel) —
it does not replace either. No Tekken or MK names appear in-game;
they appear here, in a technical doc, only as source labels.

## What already existed (not re-done)

`game/js/heartmind.js` (main, audited 2026-10-24) already runs the
T5 Devil Within skeleton, proprietized per
`docs/modes/HEART-AND-MIND-INSIDE.md`:

| Devil Within element | Heart and Mind Within element |
|---|---|
| 5 stages, boss-gated | 5 inner stages: Threshold → Gallery of Masks → Drowning Room → Furnace → Still Point (`HEARTMIND_STAGES`) |
| Jin only | ANY fighter, each with their own descent story (`HEARTMIND_STORIES` + `genericStory`) |
| G-Corp / Jack enemies | Echoes — roster fighters as inner demons (dark tint, real movesets) |
| Stage bosses | Wardens (themed echoes) → final boss: your SHADOW SELF (your model, your moveset, darkened, buffed) |
| Devil Gene meter → Devil Jin | Soul Surge as the transform-meter analog (channel the nine against the dark inside) |
| Health pickups (blue gems) | Soul embers: HP restore between waves (+30–35%) |
| Entry → beats → boss → resolution | Entry cutscene → per-stage beats tied to CANON.md "Being purified of" → shadow confrontation → resolution |

Phase 1 (shipped): sequential single-round echo fights with HP
carry-over. Phase 2 (when T5 teardown lands): simultaneous
multi-enemy density via the `HM_TEARDOWN` seam
(`enemyAi` / `waveTables` / `doorSystems` consumed 1:1).

## What this PR adds: the campaign layer

New module `game/js/heartmind-campaign.js` (dependency-free) +
surgical hooks in `game/js/heartmind.js` (party state, road
tracking, journal recording, in-fight switch guard). No combat
logic, no menus, no music, no stage assets touched.

### 1. Roads, not portals (T6 Scenario Campaign traversal + canon)

Source structure: Scenario Campaign stages are traversed on foot
through areas, fighting groups, reaching a boss arena; dialogue
plays at stage start and just before the boss (Tekkenpedia /
Neoseeker Scenario Campaign summaries, researched 2026-10-24).
Canon law: "the lands where souls fight, the roads between
them, the shrine where it ends" (CANON.md L28) and "the long
walks between the lands — the tunnels, the stairs, the desert"
(CANON.md L1391). Realm travel in WH is anatomical — roads are
the vessels between organs of one body
(`docs/research/REALM-TRAVEL-CANON-2026-10-23.md` §1.1) — never
portals between separate worlds (that is MK's grammar, not ours).

`HM_ROADS` (4 roads, one per descent step):

| From → To | Walk (system text, not a canon place name) | Canon anchor |
|---|---|---|
| Threshold → Masks | Past the hung faces | CANON.md L28; L1363–1367 (Threshold keeps a Face — faces "hung like masks in a green room") |
| Masks → Drowning | Down to where what was buried waits under water | CANON.md L28; L1391 |
| Drowning → Furnace | Up out of the water, toward what burns | CANON.md L28; L1391 |
| Furnace → Still Point | Out of the furnace, up the stairs that count the climber back | CANON.md L28; L1347–1362 (Octagonal Shrine Par-fang, climbed by stairs that count the climber back) |

The controller records `run.road` per stage; `currentRoad()`
exposes it. The UI lane may show the `walk` line on the stage
card. No new location is named: the roads connect heartmind.js's
existing inner stages.

### 2. Party switching (Scenario Campaign partner model + MK adventure switching)

Source structure (both, structure only):
- Scenario Campaign: the player leads one fighter, a companion
  travels with them (AI in single player), unlocked fighters can
  be chosen for later stages, and stage bosses unlock their
  fighter when defeated (Tekkenpedia / Neoseeker summaries).
- MK adventure games the owner liked (Deception Konquest,
  Shaolin Monks — research docs
  `docs/research/MK-DECEPTION-2026-10-23.md`,
  `docs/research/MK-SHAOLIN-MONKS-2026-10-23.md`): open-world
  traversal, switching between travelling fighters, quests and
  NPC dialogue between fights. ONLY the adventure structure and
  customization are taken — the owner does not like MK fighting
  games, and no MK fighting system, fatality, or name is pulled.

WH rule (this PR): a party of souls descends together.
`createPartyState` / `switchPartyFighter` keep per-member
progress (stage, wave, HP, cleared stages). The controller's
`setParty()` / `switchFighter()` allow switching BETWEEN
fights only — `switchFighter` returns `{ ok: false, reason:
'in-fight' }` mid-fight. The shadow self follows the active
fighter (it is "yourself, unmasked", so switching fighters
rebuilds it). In-fight partner AI is NOT in this PR — that is
the combat lane's work; this module owns state + the switch
rule, and the select-screen party picker is the UI lane's work.

Unlock-by-defeat (Scenario Campaign) is NOT re-implemented
here: WH's unlock model is the roster + rank ladder + records
(`heartmind_<fighterId>` furthest stage, `..._clear`
completions, per `docs/modes/HEART-AND-MIND-INSIDE.md`). A
warden-defeat unlock, if the owner wants it, is a records-lane
follow-up, not assumed.

### 3. Stage journal (Scenario Campaign journal, as data)

Scenario Campaign gives a post-stage journal entry (Alisa's
Journal, then Raven's). WH version: `recordPartyStageClear` +
`partyJournal` record `{ fighter, stage }` rows — data only.
No journal prose is invented here; the title-card presentation
is the UI lane's work. Deliberately NOT conflated with canon's
Threshold Book (CANON.md L1363–1372: the illustrated record of
the head-world) — the Book is the trial's record, the journal
is the party's record. Different objects.

### 4. Colour-settling as the progress signal (canon, hook only)

Canon: "Colour is how the trial tells the truth when words
would lie. A land whose force has been claimed does not
announce it. Its colours *settle*" (CANON.md L1381–1386).
Design consequence (already in REALM-TRAVEL-CANON §1.4): the
environment IS the progress bar. This PR does NOT change any
arena colours (arena colour lock: never change an arena's look
without an explicit owner say-so). The campaign layer records
clears; the arena lane owns any future per-progress colour
settling hook. No visual change ships here.

### 5. Ragdoll contexts (story/adventure side of the owner law)

Owner law (2026-10-23): ragdoll is contextual ONLY — it fires
in the moment it would happen in a Tekken game (launches, KOs,
wall splats), never always-on; the mix is Euphoria + Gang
Beasts + Human Fall Flat + Tekken. `HM_RAGDOLL_CONTEXTS` names
the four story/adventure contexts this mode allows
(`launch`, `ko`, `wall-splat`, `floor-drop`) and
`ragdollAllowed(id, mode)` is the single gate (adventure
modes only in this module; versus-mode use is the engine
lane's decision, not asserted here). The physics itself
belongs to the open-source/physics lane, not here.

### 6. Story engines: Ink for branching, Yarn for visual authoring

PR #1044 (open) ships `game/js/yarn-parse.js` + `game/js/ink-loader.js`.
This PR builds on it without duplicating it:
- `game/story/heartmind-trial.yarn` — Yarn sample (Trader
  crossroads → Trial gate → descent), parseable by PR #1044's
  parser (proven in tests: Trial path yields souls=3,
  trial_done=true, interpolated "Souls gathered: 3").
- `game/story/heartmind-trial.ink` + compiled
  `game/story/heartmind-trial.ink.json` (inkVersion 21, with
  the compiler BOM the loader strips) — same beats in Ink,
  run through the vendored runtime (see below).
- `game/vendor/inkjs/ink.mjs` + `LICENSE.md` — inkjs 2.4.0
  (inkle, MIT), the runtime PR #1044's loader needs. This PR
  vendors the runtime; it does NOT re-ship the parsers.
- `heartmind-campaign.js` `loadYarnDialogue` /
  `loadInkDialogue` dynamic-import the engines with a null
  fallback: on main today (PR #1044 unmerged) they return
  null and callers keep heartmind.js's built-in beats. No
  behaviour changes until PR #1044 merges. Both states are
  covered by `game/tests/heartmind-campaign.test.mjs`.

## Source authority (owned-game rule, 2026-10-24 correction)

Per the 2026-10-24 owned-game correction, full owned-game
files are the AUTHORITATIVE source where accessible; community
docs help extract and decipher, they do not replace the files.
Applied honestly to this lane:

| Structure claim | Authority today | Follow-up |
|---|---|---|
| Devil Within 5-stage loop, gems, Force, ranking, bosses | Community-documented (Tekkenpedia, GameSpot preview, GameFAQs FAQ) + repo design research `~/workspace/devil-within-teardown.md` (2026-10-22) | File-level: `teardown/tekken5/DEVIL-WITHIN-DATA.md` (2026-10-23) LOCATED DW anims (`gym_dw_*`, `gym_djin_*`) + stage files (`stg00/01/02/04.dat`) in TK5DATA2.BIN; stage geometry, boss AI, gem/Force mechanics are in binary TK5DATA0/3 formats, mapped for the RE bench, NOT yet extracted. When they land, they go through the `HM_TEARDOWN` seam — the story/proprietary layer does not change. |
| Scenario Campaign partner / journal / unlock-by-defeat / stage dialogue | Community-documented (Tekkenpedia, Neoseeker, Fandom summaries, researched 2026-10-24) | T6 files in-repo (`teardown/tekken6/` decrypted bulk, models, tools) are decryption/model work, not scenario scripts. Scenario script/stage extraction from T6 files is a teardown-lane follow-up; this PR's layer is WH state/data, not T6 scripts, so it does not block on it. |
| T6 customization slots (see customization doc) | FULL-FILE: `teardown/tekken6-customization-research.md` (2026-10-16), decrypted T6 PSP EBOOT item tables + NTXL categories | Item definition struct (`sbcustomize_item_t` array) + full per-category counts still locked (teardown lane). Slot taxonomy ships; meshes do not. |
| MK adventure structure (Konquest / Shaolin Monks) | Repo research docs (2026-10-23), structure only | No full-file MK extraction is claimed or needed for this layer. |

## Gaps (honest, with owner/lane)

1. Simultaneous multi-enemy density — waits on T5 teardown
   (`HM_TEARDOWN.waveTables` / `enemyAi`). Unblock: RE bench
   extraction per `teardown/tekken5/DEVIL-WITHIN-DATA.md` §4.
2. Platforming / door-puzzle traversal — stage lane (heartmind
   fights are 1v1 arena fights today; walking the roads is a
   stage-card + dialogue step, not a platforming level, until
   that lane lands it).
3. Partner in-fight AI + party picker UI — combat lane + UI
   lane respectively; state and rules ship here.
4. Live story play verification — NOT done by this lane (no
   live browser in this subagent). Delegated to the
   coordinator's browser lane: play Heart and Mind Within on
   the deployed build, switch party between stages, confirm
   the shadow self follows the active fighter and the journal
   records clears. Doc citation + node tests are the
   verification done here (see PR Proof).
5. Shrine体系 — untouched by this PR except by name
   discipline: if story work ever touches the TempleOS-inspired
   mode, its in-game name is Shrine体系 (user-locked
   2026-10-24 20:04 CDT); TempleOS attribution stays in
   technical docs only. No Shrine assets are generated here.
   STANDING CREDITS REQUIREMENT (user 2026-10-24 20:33 CDT,
   flagged for the Shrine mode lane — NOT implemented by this
   PR, which owns no Shrine mode files): the Shrine mode's end
   credits MUST say "In memory of Terry Davis, RIP" (Terry
   Davis = creator of TempleOS, the inspiration for
   Shrine体系). Add end credits to the mode if it does not
   have them yet. This ships with the mode.

## Files (this PR)

- `game/js/heartmind-campaign.js` (new)
- `game/js/heartmind.js` (surgical: campaign import, party /
  road / journal hooks, switch guard — no existing behaviour
  changed)
- `game/js/versus-banter.js` (comment-only: system-name rule
  pointing at the proprietary-names audit)
- `game/js/customization-t56.js` (new; see customization doc)
- `game/story/heartmind-trial.yarn` (new)
- `game/story/heartmind-trial.ink` (new)
- `game/story/heartmind-trial.ink.json` (new, compiled)
- `game/vendor/inkjs/ink.mjs` + `game/vendor/inkjs/LICENSE.md` (new, vendored runtime)
- `game/tests/heartmind-campaign.test.mjs` (new)
- `docs/story/HEARTMIND-CAMPAIGN-STRUCTURE-2026-10-24.md` (this file)
- `docs/story/PROPRIETARY-NAMES-AUDIT-2026-10-24.md`
- `docs/story/CUSTOMIZATION-SYSTEM-DATA-2026-10-24.md`
- `docs/story/CANON-ANCHOR-INDEX-2026-10-24.md`
- `tools/gpu/story-verify/` (GPU verification job + inputs; see its README)

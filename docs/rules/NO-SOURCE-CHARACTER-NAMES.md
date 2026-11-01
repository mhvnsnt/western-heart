# No source-game character names in Western Heart (owner law, 2026-11-01)

> "Skull is based on Bryan ... Bryan Fury should not appear in our game ... the models have to be completely re-skinned
> using all of our customization and character customization suites and the creation suites so they no longer look
> like the character models, and you got to stop calling them the names of their models from the Tekken games. You got
> to log that into the repo and the AGENTS.md so everyone stops getting confused. The only Jin in our game is one of the
> spirit souls things ... none of the people like Bryan Fury, none of their names appear in this game."
> (owner, 2026-11-01, voice; "Skull not girl" correction)

> "the only time you should be talking about the actual characters from Tekken and other games like DOA and Street
> Fighter and King of Fighters and all of those teardown games is when you're talking about getting their data over and
> the conversion ... we're not having their character names in our game and when we do have their models their models
> are just placeholders for now until they get re-skinned and recreated in the character customization and creation
> suite ... that's why they all have glb replacement models for almost every character" (owner, 2026-11-01)

## The rule
1. **No Tekken / teardown character name appears anywhere a player can see it**: menus, select screen, roster, HUD,
   move list (move names too: "Lee Somersault", "HEIHACHI 4 (T3 ...)", "DEMONIO (Devil) 4" style rows), bios,
   announcer / banter text, loading tips, achievements.
2. **Our fighters are called by their Western Heart names only** (Skull, Retsu, Purple Rain, Chordz, Pantera, Diablo,
   Negativo, ...). Never "Bryan", "Lee", "King" for one of our fighters, in UI, docs, PRs, commits or chat with the
   owner. A source character is named ONLY when the topic is getting its data over (extraction, conversion,
   provenance); recorded provenance (pack `source`, resolver output, research docs) cites the SOURCE DATA (file / T7
   code such as `brymot.json`, `bry`, `Bx_sKAM00_`), never as the fighter's identity.
3. **A model that came from a teardown game is a placeholder**, there to build on until it is completely re-skinned
   and recreated through our customization / character customization / creation suites so it no longer looks like the
   source character. That is why almost every fighter has a GLB replacement model.
4. **JIN is one of the nine Soul Spirit characters** (`jin_soul`, display "JIN") and he is NOT Jin Kazama. Jin Kazama
   does not exist in Western Heart: the fighter built on his data is DEMONIO (`roster/jin/CANON.md`). Never confuse the
   two, and never call Demonio "Jin".
   > "there is a j i n character, Jin, he's one of the nine Soul Spirit characters, he's just not Jin Kazama, you got to
   > remember that" (owner, 2026-11-01)

## Why it is written down
Agents kept naming our fighters after their move/animation sources ("Skull <- Bryan"), which spread into file names,
docs and UI strings and confused the team. Source data stays internal; the game is our own universe.

## Enforcement
- Existing: `tools/canon/check.py` (CI `canon-names`) blocks new player-facing lines that contain a denylisted
  source-game name. Its denylist does not yet hold the Tekken roster: whole-word terms like `king`, `lee`, `jin` also
  match internal identifiers (`bank: 'king'`, `jin_soul`), so the Tekken names get a dedicated player-facing field scan
  (move `name`, display names, bios) with a guard test instead. Tracked in `docs/team/TASKBOARD.md`.

## Roster folders named after source models (2026-11-01)
Many `roster/<folder>/` directories are named after the source-game model they hold. On screen they are ALWAYS the WH
fighter: `tools/canon/roster-folder-wh-names.json` is the map (owner-confirmed: blanka = CHARGER, zangief = KRONOS,
iori = DEATHFANG, vega = KORESHI, ryuji-rock = CORNERSTONE (a wrestler + KOF blend); derived from the game's own
model map: armor-king = YUKIHYŌ, jin = PHANTOM, zafina = MARIPOSA, sakura = SAKU RA, lili = SILVERTONGUE,
cyborg-x = CAPE JONES, kuma / kuma-replacement = GASHADOKURO, panda = AOTSUKI; the generator also derives every folder
from the `base:` field in `game/js/roster-full.js`). A folder nothing names yet shows as "UNASSIGNED BODY n", never
under its folder name. `customization/build_roster_attires.py` applies the map for the
creation suite; extend the JSON when the owner names more.

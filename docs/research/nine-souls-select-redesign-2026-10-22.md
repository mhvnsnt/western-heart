# Nine Souls Character Select Redesign — 2026-10-22 (worker 83)

Owner directives (verbatim, also logged in `docs/owner-directives.md`):

**Directive 1 (~23:02 CDT):**
> "Alright, that means everybody except for Zen and Gaiu has to come off of the character select screen because they don't have actual um bodies to select for fighters. But what we can do is make a version of them where we have an attire for whoever they go to um Ren how he goes to Demonio Bayu goes to Zui two goes to Pantera Shaw goes to Sakura and the other three I mean the other two like we can have attires you know and so on down the whole list um we can have an attire for each of those characters where they have the spirit version of the non soul whatever one goes to them floating behind them as an attire and so I'll make the spirit versions of those of the non but since there's two of the nine that are actually have bodies and fighters then those are the only two that should be on the character select screen all the other ones should just be attire variants like you can select to have them floating behind the attire like on or off like it shouldn't be an in the attire thing whatever fighter has them you should be able to hit it it's like a a tertiary thing where you can turn the um nine soul uh spirit on or off and then choose between the nine souls but if you choose the one that goes to the character you're choosing then it um empowers them more or something like that and then log all of that and put it into the repo word for word exactly how I said it"

**Directive 2 — refinement (~23:03 CDT):**
> "We'll only add them like later on onto the character list as like characters with vessels or bodies as like kind of boss creatures but we'll figure out how that gets done later on as we progress through all the different modes and the stories and things for the characters. The the seven of the nine souls that don't have bodies we'll figure out how to incorporate them into the character select screen later so for right now they have to come off of the character select screen until we get them unlockable and with bodies."

## Phonetic spellings (owner's voice note → canon spelling)

| Heard | Means |
|-------|-------|
| Ren | RIN |
| Bayu | BYOU |
| two | TOU |
| Shaw | SHA |
| Sakura | Saku Ra |
| Gaiu | GYOU |

## The nine souls — select status

| Soul | Kanji | Vessel(s) | Select grid |
|------|-------|-----------|-------------|
| RIN | 凛 | Demonio | OFF (vesseled, no body yet) |
| BYOU | 病 | Zui | OFF (vesseled, no body yet) |
| TOU | 闘 | Pantera | OFF (vesseled, no body yet) |
| SHA | 沙 | Saku Ra + Kinpo + Awa Pop (split three ways) | OFF (vesseled, no body yet) |
| KAI | 海 | King Tyrant + Star (two moods) | OFF (vesseled, no body yet) |
| JIN | 刃 | Phantom | OFF (vesseled, no body yet) |
| RETSU | 烈 | Skull | OFF (vesseled, no body yet) |
| ZEN | 禅 | Unvesseled | **ON — selectable spirit fighter** |
| GYOU | 行 | Unvesseled (splinter in Cyborg X) | **ON — selectable spirit fighter** |

## 1. Character-select dedup

- `SELECT_HIDDEN` in `game/js/select-screen.js` now hides only the seven
  vesseled souls: `rin, byou, tou, sha, kai, jin_soul, retsu`
  (plus the pre-existing non-soul entries `ryuji`, `doc-frank-machine-shop`).
- `zen` and `gyou` were REMOVED from the hidden set — they are selectable.
- The seven stay in the roster data (`game/js/roster-full.js`) for
  story/other modes — same pattern as the existing no-duplicates law.
- Roadmap (per refinement): the seven return LATER as unlockable boss-type
  characters with vessels/bodies; the unlock path is designed as story
  modes progress. Not this change. No code for it yet — this doc is the
  placeholder the future lane builds on.

## 2. Soul-spirit toggle (tertiary, NOT an attire)

New module `game/js/soul-spirit.js` (pure logic, unit-testable):

- `NINE_SOULS`: id, name, kanji, nature, vessel roster ids, aura color.
- Per-side pick `{ enabled, soulId }`, default OFF.
- Select-screen UI (`renderSoulSpirit` in `select-screen.js`): an ON/OFF
  chip per side plate plus a 9-soul picker (name + kanji chips). Vessel
  matches for the highlighted fighter get a double-border chip and an
  ⬢ VESSEL MATCH — EMPOWERED badge. Interactive only while the side is
  active and unlocked (same rule as attire chips).
- Picks snapshot at confirm into `state.spiritLocked`; the fight reads
  them via the new `soulSpiritLocked(side)` API. Versus: both sides.
  Solo modes: P1 only (enemy side resolves null → no-op).

## 3. Empowerment buff (vessel match)

`applySoulSpirit(charEntry, pick)` in `soul-spirit.js`, applied in
`main.js startFight` after attire/mode overrides so it composes:

- Pick OFF or soul with no vessel bond → spirit still shows (aura only),
  no buff.
- Pick ON + soul vessels into the fighter → **empowered**:
  - `stats.power × 1.10` (+10% damage; damage scales on
    `attacker.stats.power` in `fighter.js`)
  - `stats.defense × 1.05` (+5% defense — the soul shields its vessel)
  - Nine-Soul Meter gain × 1.25 (via `Fighter.soulMeterMult`, honored by
    `addMeter` and the block/damage accrual paths)
  - Brighter aura (2.1 vs 1.6 scale, 0.85 vs 0.5 opacity)
- Values are the v1 spec — owner-tunable like every other fight number
  (`SOUL_MATCH_BUFF` in `soul-spirit.js`).

## 4. Floating spirit render — owner-made models, placeholder today

- The owner makes the spirit versions themselves. **No AI-generated
  stand-in spirit models**, per the directive.
- `game.js` implements the ATTACH POINT: `attachSoulSpirit(fighter, mark)`
  parents a soft additive aura sprite (tinted per soul) to
  `fighter.lean` behind the fighter at upper-body height — `lean` flips
  with facing, so the spirit stays behind through side-switches. A
  per-frame bob/pulse runs in `Game._update` via `updateSoulSpirit`.
- When the owner's spirit GLBs land: swap the sprite for the real model
  loader, keep the same contract (`fighter.lean` child, behind,
  upper-body height). The `soulSpirit: { soulId, matched }` stamp on the
  char entry is the stable interface.

## 5. Not this system

- **Soul Kindle** (`soul-kindle.js`) — T7 ki-charge port; the vessel
  focusing its OWN soul fragment.
- **Soul Surge** (canon Nine-Soul Meter) — channeling one of the OTHER
  eight souls for ten seconds mid-fight.
- **Soul Urge** (owner-locked 2026-10-22) — T8 Heat renamed proprietary.

## Files

- `game/js/soul-spirit.js` — NEW: soul data, vessel matching, buff spec, `applySoulSpirit`.
- `game/js/select-screen.js` — `SELECT_HIDDEN` dedup (zen/gyou selectable);
  per-side toggle UI; `soulSpiritLocked(side)` API.
- `game/select.css` — toggle panel styles.
- `game/js/main.js` — `startFight` applies locked picks via `applySoulSpirit`.
- `game/js/fighter.js` — `soulMeterMult` honored in meter accrual.
- `game/js/game.js` — `attachSoulSpirit` / `updateSoulSpirit` placeholder aura.
- `docs/owner-directives.md` — both verbatim directives.
- `docs/research/nine-souls-select-redesign-2026-10-22.md` — this doc.

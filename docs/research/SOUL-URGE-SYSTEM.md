# Soul Urge — Tekken 8 Heat System, Proprietary Rename (WH)

**Status:** implemented 2026-10-22 (worker 28) · **Name user-locked 2026-10-22: "Soul Urge"** — use it everywhere (UI, docs, code, comments).

## Sources pulled
- `teardown/tekken7/tekkenmods-docs/files/en/Tekken_8/Basic_Information/Overview/Moveset/Structures/Move/index.md`
  — Heat Smash as a first-class move category ("Rage Arts, Heat Smashes … each and every one of these is considered a Move").
- `…/Moveset/Structures/Hit_Conditions/index.md` — Heat Engager hit conditions, Heat Dash conditions.
- `…/Moveset/Structures/Cancel/index.md` — Heat as a button input class.
- `…/Moveset/Structures/Input_Extradata/index.md` — `0x10 - Heat` input extradata flag.
- Canonical T8 Heat rules verified against public breakdowns (EventHubs/Harada-Ikeda, Tekken Wiki):
  once per round, blue bar under health, 10 s Heat (burst) / extended from engagers, timer pauses
  while the opponent is hit/grounded, chip damage on block that can't kill, Heat Dash (1 pip),
  Heat Smash (spends all Heat).

## T8 Heat → Soul Urge rename table (locked)
| Tekken 8 | Western Heart |
|---|---|
| Heat (state) | **Soul Urge** |
| Heat Bar | Urge gauge (under the health bar, T8-authentic placement) |
| Heat Burst (2+3) | **Urge Burst** (`UB.2+3`, input 2+3) |
| Heat Engager | **Urge Engager** (fighter's own launcher-class strike, flagged `urgeEngager`) |
| Heat Smash (2+3 in Heat) | **Urge Smash** (`US.2+3`, input 2+3 while urging) |
| Heat Dash | **Urge Dash** (input 1+2 while urging & not raging, 1 pip) |
| Heat Energy pip | Urge pip |

## Rules implemented (T8-faithful)
- **Once per round**; gauge refreshes every round (`SoulUrge.resetRound`).
- **Urge Burst** (`2+3`, armored smash): activates on hit **or block** (T8) → 1 pip, 10 s.
- **Urge Engager**: the fighter's highest-knock real strike (synthesized moves excluded);
  on **hit only** (T8) → 2 pips, 15 s, +10 HP heal, dash-in (T8 engager behavior).
- **During Soul Urge**: all blocked attacks deal chip that **can never kill** (T8);
  timer **pauses while the opponent is hit/grounded** (T8); soul-flame blue aura + urge gauge UI.
- **Urge Dash** (`1+2` while urging): spends 1 pip, committed forward burst (T8 Heat Dash).
  Rage art keeps priority on `1+2` while raging (documented input overlap).
- **Urge Smash** (`2+3` while urging): 30 dmg armored cinematic, **spends all pips, ends Urge** (T8).
- **AI** uses the full loop: burst in range → dash with spare pips → smash cash-out.

## Files
- `game/js/soulurge.js` — `ensureUrgeMoves()` (synthesizes `UB.2+3`/`US.2+3`, flags engager) + `SoulUrge` director.
- `game/js/fighter.js` — urge state fields, `tryUrgeDash()`, `setUrgeAura()`, urge chip in `receiveHit`, `urgeEngager` move passthrough.
- `game/js/movesets.js` — `pressChord` resolves `UB.`/`US.` prefixes from `ctx.urgeBurst`/`ctx.urgeSmash`.
- `game/js/game.js` — director lifecycle, engager/burst/smash triggers in `_resolveCombat`.
- `game/js/ai.js`, `game/js/audio.js` (`urge()`), `game/js/main.js` (`setUrge`/`updateUrge`),
  `game/index.html` + `game/styles.css` (urge gauge).
- Tests: `game/tests/stagerage.test.mjs` (11 tests).

## Differences from T8 (deliberate)
- No per-character enhanced movelists during Urge (T8 has them); the universal chip +
  dash + smash loop is the v1. Character-specific Urge enhancements are future work.
- Visual is soul-flame blue (WH identity), not T8's blue/purple flame.

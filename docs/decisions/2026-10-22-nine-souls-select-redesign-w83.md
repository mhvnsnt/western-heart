# Nine Souls character-select redesign — worker 83 (2026-10-22 ~23:02 CDT)

## Owner directives (verbatim in `docs/owner-directives.md`)

1. Seven vesseled souls (RIN, BYOU, TOU, SHA, KAI, JIN, RETSU) come OFF the
   character-select grid; only ZEN and GYOU stay selectable. Every fighter
   gets a TERTIARY soul-spirit toggle (not an attire): on/off + pick any of
   the nine souls; picking the soul that vessels into the chosen fighter
   empowers them. The owner makes the spirit versions themselves — no
   AI-generated stand-ins.
2. Refinement: the seven return LATER as unlockable boss-type characters
   with vessels/bodies; the unlock path is designed as story modes
   progress — not now.

## What was built

- `game/js/soul-spirit.js` (new): nine-soul data + vessel map, `vesselMatch`,
  `applySoulSpirit`, `SOUL_MATCH_BUFF` v1 spec (power ×1.10, defense ×1.05,
  meter ×1.25), UI labels. 20/20 unit tests pass.
- `game/js/select-screen.js`: `SELECT_HIDDEN` now hides only the 7 vesseled
  (zen/gyou selectable); per-side toggle UI (on/off chip + 9-soul picker +
  vessel-match badge); picks snapshot at confirm; `soulSpiritLocked(side)` API.
- `game/select.css`: toggle panel styles (pointer-events auto inside the
  pointer-events-none plate, mirroring the attire strip).
- `game/js/main.js`: `startFight` applies each side's locked pick via
  `applySoulSpirit` after attire/mode overrides (composes with story buffs).
- `game/js/fighter.js`: `soulMeterMult` honored in meter accrual
  (`addMeter`, block +4, damage +6 paths).
- `game/js/game.js`: `attachSoulSpirit` / `updateSoulSpirit` — placeholder
  aura parented to `fighter.lean` behind at upper-body height (stays behind
  through side-switches); swap for the owner's spirit GLBs when they land.

## Notes for future lanes

- PR #668 is NOT the soul-spirit toggle (it's worker 24's TTT2 team
  battle) — no duplication; this lane built the full system.
- Unlockable boss-type return of the seven is roadmap only (story-mode
  design), no code yet.
- Distinction kept: Soul Kindle (ki charge) vs Soul Surge (Nine-Soul Meter)
  vs Soul Urge (T8 Heat) vs Soul-Spirit Toggle (this).
- MERGE FREEZE: PR opened, reported merge-ready, not merged (overrides the
  repo MERGE-IT-YOURSELF law for this round per coordinator instruction).

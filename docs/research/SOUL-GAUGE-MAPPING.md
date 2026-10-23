# Soul Gauge / Critical Edge → Western Heart Meters (Extension Mapping)

**User directive 2026-10-22:** "BUILD ON OURS — we have meter mechanics already (Nine-Soul meter, etc.).
Extend those rather than importing SC's system. Document how the extension maps to our existing meters."

## Decision: no new meter system. The Nine-Soul meter covers the whole design space.

| Soulcalibur concept | Western Heart equivalent | Status |
|---|---|---|
| Soul Gauge (the meter) | **Nine-Soul Meter** (0–100, 9 segments, `fighter.meter`) | existing — built over several lanes |
| Critical Edge (full-meter cinematic super) | **Soul Surge** (full-meter super, `L` / surge button) | existing — verified this pass |
| Soul Charge (meter-spend power state) | **Soul Urge** (per-round urge gauge, T8 Heat renamed) | NEW this pass — separate per-round gauge, T8-faithful |
| Guard Impact / Reversal Edge | ON HOLD per user 2026-10-22 ("Tekken doesn't use those for a reason") | not built |

## How the extension maps to our existing meters
1. **Nine-Soul Meter = the single persistent meter.** Gains unchanged: +soul on landing
   hits (`registerHit` → `soulGain`), +6 on taking damage, +4 on block. Spends: Soul Surge
   (100), mid-match transformation cinematic (100). Nothing about the meter's economy was
   altered for this lane.
2. **Soul Surge IS our Critical Edge.** Full-meter input → cinematic super with flash,
   name callout (`ui.surgeFlash`/`surgeName`), aura flare. Verified: `tryAttack('surge')`
   still requires `meter >= maxMeter` and spends the gauge; the game.js presentation path
   (`surgePresentation`) is untouched.
3. **Soul Urge is deliberately NOT on the Nine-Soul meter.** T8 Heat runs on its own
   per-round gauge that refreshes every round — importing that structure faithfully is what
   the user approved ("pull straight from the files"). Bolting Heat onto the Nine-Soul
   meter would have distorted both systems; the mapping doc records the separation instead.
4. **Rage (T7) is health-gated, not meter-gated** — unchanged semantics, now fully wired
   (arts, drives, slow-mo). It coexists with both meters.

## What "extend" meant in practice
- No SC meter code, UI, or concepts were imported.
- The Critical-Edge role was confirmed covered by Soul Surge (no duplicate super added).
- The genuinely new system (Soul Urge) was built as a new per-round gauge in the T8
  shape, documented in `docs/research/SOUL-URGE-SYSTEM.md`.
- Tests: `game/tests/stagerage.test.mjs` covers the new gauge; existing meter behavior
  (surge at 100) is untouched — see `fighter.js` `tryAttack('surge')` path, unchanged.

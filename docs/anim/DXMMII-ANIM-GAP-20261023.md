# DXMMII (Mokujin slot) — mimic system doc + precise gap (2026-10-23)

**Mokujin has no fixed moveset BY DESIGN.** DXMMII is the Patchwork DJ on
the Mokujin slot (roster `style: 'Mimicry'`, `archetype: 'Trickster'`) —
he copies another fighter's moveset, Tekken-Mokujin-style. A static pull
is the wrong shape for him; this doc records the mimic system, what is
actually wired today, and the precise gap.

## The mimic system (documented)

- **Design (Tekken rule):** each round/match, the mimic binds a random
  roster fighter's full moveset — moves, stances, and that fighter's
  animation bank. No fixed moveset of his own.
- **Closest existing mechanism:** Trader's Mimic mode
  (`game/js/movesets.js` `playedMoveset` / `game/js/modes.js`
  `traderFoe(playerChar, bout, randomMoveset)`) — the Trader already
  takes a `randomMoveset` per bout. That is the pattern a DXMMII mimic
  mechanic follows; it is mode-scoped today, not a roster-fighter
  mechanic.
- **In-file record:** `game/assets/movesets/dxmmii-patchwork.json`
  carries a top-level `mimic` block (design, current wiring, mechanic
  status, handoff) added this pass.

## Current wiring (verified 2026-10-23 — works, but is NOT mimicry)

- `game/js/roster-full.js:199`: `dxmmii-patchwork` → `moveset: 'demonio'`
  (static). DXMMII plays Demonio's moveset every round — functional, but
  a static borrow, not a mimic.
- `game/assets/movesets/dxmmii-patchwork.json` (166 T3-jin rows) IS in
  MOVESET_IDS and loads, but the roster never plays it. It is the
  fallback bank, not the fighter's moveset.

## Moveset status (done this pass — batch10-special-pull)

+0 moves — a static pull is the wrong shape; nothing was added.

**SHOW-ANIMATION LOCK (owner 2026-10-23):** `anim_set_lock` added;
166/166 fallback-bank moves stamped `"set": "FIGHT"`. No taunts in the
file. The lock applies to the fallback bank as stated; the mimic's
per-round borrowed movesets are each covered by their own fighter's
lock.

## The missing bank — FIGHT vs SHOW (precise gap for the game-code lane)

1. **Mimic selection mechanic (game code, not moveset data):** per
   round/match, bind `dxmmii-patchwork` to a random roster moveset
   (Tekken Mokujin rule) instead of the static `'demonio'` assignment.
   Until that lands, the static wiring stands — do NOT delete it.
2. **Fallback bank motion:** the 166 T3-jin rows bind the jin bank
   (`t3_source: 'jin'`); DXMMII's own motion bank does not exist.
3. **SHOW:** win pose / intro pose / taunts for the Patchwork DJ
   persona: no documented clips — gap. When the mimic mechanic lands,
   SHOW clips must be tagged at intake and never enter any borrowed
   moveset without the user's explicit approval.

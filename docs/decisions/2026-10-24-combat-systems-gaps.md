# Combat-system gaps closed 2026-10-24 — Power Crush, Screw/Tornado, Wall Splat, Recoverable Health, Soul Urge completion, Item-move gate

Owner instruction (verbatim, subagent task 2026-10-24): "WORK COMBAT-SYSTEM GAPS IN WESTERN HEART — Power Crush, Screw, Wall Splat, Recoverable Health, Heat/Soul Urge completion. You are a worker for a completeness audit. Do real work, not just a report: implement in code, test by simulation, ship via PR." Follow-up directive 2026-10-24 19:39 CDT: "Don't leave any PRs unpushed or unmerged don't leave any work unfinished or leave it queued start working on everything use the GPU to get it finished and make sure everything is merged and pushed and playable and testable without clobbering anything on any side."

## Re-verified gaps (grep on main, 2026-10-24)

All five original gaps confirmed present before this change: zero mentions of
powercrush/power_crush, screw/tailspin/kirimomi, wall_splat/wallsplat or
recoverable in `game/js/fighter.js` / `game/js/combat-core.js`; chip damage
existed (12% on block) but created no recoverable pool; Soul Urge existed
(`game/js/soulurge.js`) but its timer was broken by a double call in
`game/js/game.js` (see below) and it supported only a single auto-picked
engager. "Bound" in the old gap note is not a fighter.js system at all —
the only `bound` hits are animation-bank wording — so there is nothing to
"keep for low parry only"; no Bound behaviour was removed.

## What was implemented (technical names only — NEEDS NAME)

No universe (canon) names for Power Crush, Screw, Tornado, Wall Splat or
Recoverable Health exist in CANON.md or SOUL-SYSTEMS.md as of 2026-10-24.
The names below are therefore TECHNICAL placeholders, used in code and
technical docs only, never in CANON.md bios. A canon name still needs an
owner decision — flagged NEEDS NAME, not invented here.

- **Power Crush (T7):** `powerCrush` move flag + `powerCrushAbsorbs()` in
  `game/js/combat-core.js`; defender mid-swing on a flagged move (not in
  recovery) absorbs mid/high/special-mid strikes and keeps swinging
  (result `'powercrush'`, no combo for the attacker, `game/js/game.js`
  handles it with a block-style spark). Lows, throws and unblockables
  interrupt normally. Unknown-level strikes fail closed (interrupt).
  Damage absorbed while power-crushing becomes recoverable (T8 rule).
- **Screw (S!, T7) / Tornado (T!, T8):** `screw` / `tornado` move flags,
  one shared once-per-combo slot (`_spinUsed`). A flagged hit against an
  AIRBORNE victim enters state `screw` / `tornado` (spin, slump on
  landing: stun 0.9 airborne, 0.55 on landing, grounded slump posture =
  down so follow-ups connect). A second flagged hit in the same combo
  falls through to normal knockdown/hitstun. Slot frees on combo expiry,
  when the victim is back on their feet, on KO and on round reset.
- **Wall splat (W!):** state `wallsplat`, entered in `Fighter._physics`
  when a struck victim (hitstun/knockdown/screw/tornado) is clamped at
  the arena limit still travelling toward that wall (>= 0.5 m/s).
  Stun 0.85, vulnerable. DISTINCT from wall break (`game/js/stagebreaks.js`):
  a splat breaks nothing and moves no bounds; a break shatters the wall
  and extends the bounds before the next physics frame, so a breaking
  hit does not also splat at the old limit. Idle/walk/block never splat.
- **Recoverable health (white gauge, T8):** `_recoverable` pool on the
  fighter, invariant hp + pool <= maxHp. Blocked chip and power-crush
  damage enter the pool; the pool is recovered ONLY by dealing damage
  (landed hits and chip inflicted, via `recoverFromPool()`). No time
  recovery. Existing METAL regen heals real hp and therefore eats the
  pool first (invariant, not time recovery of the pool). HUD: classic
  HUD reuses the white `.hp-damage` bar (extends past the hp fill by the
  pool); ui-wh HUD gains a white `<b>` bar segment + bridge forwarding.
- **Soul Urge completion:** (a) per-character engager lists — a moveset
  may declare `urgeEngagers: [...]`; every listed existing non-grab move
  becomes an engager; without a list the old highest-knock launcher
  fallback remains (`listUrgeEngagers()` exported, tested). Urge Smash
  already existed as a distinct synthesized category (`US.2+3`, spends
  all pips, ends Urge) and Urge Burst (`UB.2+3`) already existed — no
  change needed there. (b) Urge Dash cancel: LP1+RP2 (1+2) while urging
  now also cancels out of attack recovery (old code required canAct, so
  no cancel existed); neutral dash unchanged; rage keeps 1+2 priority
  while raging. (c) BUG FIX: `game.js` called `soulurge.update(p1, dt)`
  AND `update(p2, dt)` per frame, so dt arrived as a fighter object and
  the Urge timer went NaN; now a single `update(dt)` per frame, and
  `SoulUrge.update` tolerates the old shape.
- **Item moves (LOW priority, scaffold only):** `requiresItem` flag
  passthrough + `itemMoveAvailable()` gate in `_tryAttackFresh` /
  `_fireNotation`. No item data exists in repo movesets, so the gate is
  currently a no-op and no move is gated. Full item data is PARTIAL —
  see below.

## Moveset wiring — proven only, rest UNMAPPED

Pantera (= King) only, joined by notation to wavu.wiki T7 frame data and
to the repo's own T7 records:

- `db+1+2` Muscle Armor — `powerCrush` (wavu King movelist: pc6~59;
  "damage taken during power crush state is recoverable").
- `db+1+2,3+4` Jaguar Sprint — `powerCrush` (wavu King movelist: listed
  Power Crush).
- `uf+3+4` Sole Crusher — `powerCrush` (wavu King strategy: "-14 mid
  power crush").
- `SS.2` Victory Palm — `screw` (wavu King movelist: SS 2 Tailspin;
  repo T7 record on_hit/on_ch = `S!`).
- NOT flagged, deliberately: `b+3:1+2` is a wavu-listed King power crush
  but no such key exists in `pantera.json` (UNMAPPED, not guessed);
  `db+1+2,2` Emerald Elbow carries a T8 Heat Engager tag on wavu but is
  a throw in WH (`isGrab`), so it cannot be an onHit engager — NOT
  flagged as `urgeEngager` (needs stance-move engager handling, PARTIAL);
  Tornado: engine flag exists, zero Pantera moves carry a proven T8
  Tornado tag in the data checked (UNMAPPED); all other 156 moveset
  files: UNMAPPED — no closest-match guesses were filled in.

## Tests

`game/tests/combat-systems.test.mjs` — 8/8 pass via
`node --test game/tests/combat-systems.test.mjs`:
Power Crush absorb/lose matrix; Screw once-per-combo + airborne-only +
Tornado shares the slot; wall splat geometry + break distinctness;
recoverable pool arithmetic + no time recovery; item gate; Soul Urge
engager lists + fallback + timer-signature fix; fighter/game wiring
anchors (the pure rules are actually called in the live paths, because
fighter.js needs THREE and cannot be imported headlessly); Pantera
flag exactness (only the four proven moves flagged).

## OWED-PLAYTEST (not claimed from simulation)

Playing the live build (phone portrait, human navigation) is still owed
after deploy: Power Crush absorb vs low/throw, Screw slump follow-up,
wall splat vs wall break on a breakable stage, white-bar recovery by
attacking, Urge Dash cancel from recovery, Pantera db+1+2 / SS.2 in a
real match. Simulation passing is not a playability claim.

## Status per gap

- Power Crush: DONE (engine + tests + 3 proven Pantera moves; rest UNMAPPED).
- Screw: DONE (engine + tests + SS.2; rest UNMAPPED).
- Tornado: PARTIAL — engine + shared slot + tests DONE; zero moves wired (UNMAPPED, needs per-character T8 verification).
- Wall splat: DONE (engine + tests; distinct from break).
- Recoverable health: DONE (engine + both HUDs + tests).
- Soul Urge completion: DONE (engager lists + Dash cancel + timer fix + tests; Smash/Burst already existed).
- Item moves: PARTIAL — gate scaffold + tests DONE; no item data wired (needs item/equipment data, none in repo movesets).
- Canon names for these systems: NEEDS NAME (owner decision owed).
- Live playtest: OWED-PLAYTEST (parent/user step; subagent cannot operate a live browser).

# Combat-system gaps closed 2026-10-24 — Power Crush, Screw/Tornado, Wall Splat, Recoverable Health, Soul Urge completion, Item-move gate

Owner instruction (verbatim, subagent task 2026-10-24): "WORK COMBAT-SYSTEM GAPS IN WESTERN HEART — Power Crush, Screw, Wall Splat, Recoverable Health, Heat/Soul Urge completion. You are a worker for a completeness audit. Do real work, not just a report: implement in code, test by simulation, ship via PR." Follow-up directive 2026-10-24 19:39 CDT: "Don't leave any PRs unpushed or unmerged don't leave any work unfinished or leave it queued start working on everything use the GPU to get it finished and make sure everything is merged and pushed and playable and testable without clobbering anything on any side."

## Convergence note — read this first (revised 2026-10-25)

This branch ORIGINALLY implemented the full engine for these systems
(pure rules in `game/js/combat-core.js`, wiring in `game/js/fighter.js`,
Soul Urge completion in `game/js/soulurge.js`, HUD white bars, Pantera
flags, 8 simulation tests). While the branch was in flight, main merged
a parallel lane (GAP-FILL LANE 1, 2026-10-24) that implemented the same
engine independently — Power Crush with armor delay, Screw/Tornado
extender slot, wall splat with 3-hit drop, recoverable pool, item gate,
Urge Dash cancel, per-round resets — in `game/js/combat-core.js` and
`game/js/fighter.js`. Shipping the branch's engine on top would have
DUPLICATED that work (and in one re-sync attempt it literally produced
a duplicate `powerCrushAbsorbs` export). So this PR was rebased onto
main's lane: the engine files are main's, and this PR ships only the
parts main's lane did NOT cover. No work was silently dropped — the
re-sync history is in the branch commits; the engine behaviour below is
main's lane plus this PR's deltas, tested together by the revised suite.

## What main's GAP-FILL LANE 1 already covers (not re-shipped here)

- Power Crush: `isPowerCrushMove` / `powerCrushAbsorbs` (mid/high
  absorbed, lows/throws/unblockables/Rage Arts break it, ~8-frame armor
  delay), crush path in `receiveHit` (damage lands, swing continues,
  no hitstun).
- Screw/Tornado: `isScrewMove` / `isTornadoMove` / `extenderKind`,
  one shared slot per combo, slump/bound stuns, `_extenderUsed`.
- Wall splat: `wallsplat` state, 3-hit drop (`WALL_SPLAT_MAX_HITS`),
  distinct from wall break (`stagebreaks.js`).
- Recoverable pool: chip on block pools (`_addRecoverable`), landing
  hits / forcing blocks recovers (`_recoverOnAttack`), never over
  time, per-round reset via `soulurge.resetRound`.
- Item gate: `requiresItemOf` / `itemGate`, `equippedItems`.
- Soul Urge: Dash cancel in fighter.js, Burst/Smash synthesis,
  single auto-picked engager fallback, correct `update(dt)` timer.

## What THIS PR adds on top of main's lane

1. Pantera moveset flags — the ONLY moveset file touched, by surgical
   text inserts (no JSON re-dump). Joined by notation to wavu.wiki T7
   frame data and the repo's own T7 records:
   - `db+1+2` Muscle Armor — `powerCrush: true` (wavu King movelist:
     pc6~59; "damage taken during power crush state is recoverable").
   - `db+1+2,3+4` Jaguar Sprint — `powerCrush: true` (wavu King
     movelist: listed Power Crush).
   - `uf+3+4` Sole Crusher — `powerCrush: true` (wavu King strategy:
     "-14 mid power crush").
   - `SS.2` Victory Palm — `screw: true` (wavu King movelist: SS 2
     Tailspin; repo T7 record on_hit/on_ch `S!`).
   - Deliberately NOT flagged: `b+3:1+2` is a wavu-listed King power
     crush but no such key exists in `pantera.json` (UNMAPPED, not
     guessed); `db+1+2,2` Emerald Elbow carries a T8 Heat Engager tag
     on wavu but is a throw in Western Heart (`isGrab`), so it cannot
     be an onHit engager — NOT flagged (needs stance-move engager
     handling, PARTIAL); Tornado: zero Pantera moves carry a proven T8
     Tornado tag in the data checked (UNMAPPED). All other 156
     moveset files: UNMAPPED — no closest-match guesses.
2. Power-Crush absorbed damage becomes recoverable (T8 rule, wavu King
   Muscle Armor note) — the one engine gap in main's lane: its crush
   path landed damage but never pooled it. One line in
   `receiveHit`'s `crushActive` branch, capped so hp + pool never
   exceeds maxHp.
3. HUD white recoverable bar (main's lane had the pool but NO HUD
   wiring): classic HUD (`game/js/main.js` `_hp`) shows hp +
   recoverable in the existing white `.hp-damage` element; ui-wh HUD
   (`game/js/ui-wh-bridge.js` forwards `recoverable`, `game/ui-wh/ui.js`
   sets a new white `<b>` segment, `game/ui-wh/index.html` adds `<b>`
   to both plates, `game/ui-wh/ui.css` styles `.bar b`); `game/ui_sources.json`
   lists `game/ui-wh/ui.css` under `hud-fight`.
4. Soul Urge per-character engager LISTS: a moveset may declare
   `urgeEngagers: [...]`; `ensureUrgeMoves` flags every listed
   existing non-grab, non-synthesized move and records
   `_urgeEngagerKeys`; exported `listUrgeEngagers(ms)` returns the
   list, else the single key, else data-flagged moves. The single-key
   auto-pick fallback is untouched for movesets without a list.
5. Revised simulation suite `game/tests/combat-systems.test.mjs`
   (6 tests, run as `node --test game/tests/combat-systems.test.mjs`
   from repo root): Power Crush absorb/break rules + armor delay;
   extender slot + wall-splat drop; item gate; engager lists +
   fallback + onHit activation + timer tick; wiring anchors (fighter
   delta, both HUDs, bridge, manifest); Pantera flag exactness.
   fighter.js is anchor-verified, not imported (it needs THREE).

## Status per gap

- Power Crush: DONE (main lane engine + this PR's pool delta + 3
  proven Pantera moves; rest UNMAPPED).
- Screw: DONE (main lane engine + SS.2; rest UNMAPPED).
- Tornado: PARTIAL — engine + shared slot DONE (main lane); zero
  moves wired (UNMAPPED, needs per-character T8 verification).
- Wall splat: DONE (main lane engine, distinct from break).
- Recoverable health: DONE (main lane pool + this PR's HUD + crush
  pooling + tests).
- Soul Urge completion: DONE (main lane Dash/Burst/Smash/timer +
  this PR's engager lists + tests).
- Item moves: PARTIAL — gate DONE (main lane); no item data wired
  (needs item/equipment data, none in repo movesets).
- Canon names for these systems: PARTLY LOCKED (user 2026-10-24
  22:01 CDT). Spin Juggle is LOCKED as the umbrella mechanic for the
  Screw/Tornado extender: forms are Floor Spin (ground/floor form,
  ex-Screw) and Air Spin (air form, ex-Tornado); Tailspin collapses
  into Floor Spin, no third form. Break + guard break KEEP their
  existing names (no new shared name). Power Crush rename PROPOSED,
  not locked: Kongō (recommended) or Armor Strike — user pick
  pending. Code/docs keep technical names (Screw/Tornado/Power
  Crush) until the owner locks the rest; no invented name is
  presented as canon.
- Live playtest: OWED-PLAYTEST (parent/user step; subagent cannot
  operate a live browser; must be stated as owed, never claimed from
  simulation). Checklist: Power Crush absorb vs low/throw, Screw
  slump follow-up, wall splat vs wall break on a breakable stage,
  white-bar recovery by attacking, Urge Dash cancel from recovery,
  Pantera db+1+2 / SS.2 in a real match, phone portrait, human
  navigation.

## Ownership + use framing correction (2026-10-24 20:22 CDT)

Full-game files from OWNED games are not piracy and are not out of
scope: the user owns the games, owns the files, paid for them —
ownership + paid = authorization for extraction + wiring into Western
Heart, and the owned full files are the AUTHORITATIVE source, not
community approximations where the full files are available. At the
same time WH does NOT supply or redistribute full games for people to
play — it USES the files to build its own game, and ships with NO
famous names + proprietary canon names. Only copies of games NOT owned
are out of scope; ownership is never demanded as proof.

Applied to this PR: the flags do not ship any original game and do not
use any famous name in-game (Pantera, not King; Tekken names stay in
technical files only). Sourcing: the Screw flag on SS.2 is confirmed by
the repo's own T7 record (on_hit/on_ch S!) as well as wavu; the Power
Crush flags follow the repo's established frame-data pipeline
(wavu.wiki / TheBigTuna tables, the same sources frame-tables.js
already cites) — no owned-file property table for these flags was
located in repo teardown, so no community approximation was substituted
for an available owned file. If a T7 owned-file property table for
these moves surfaces in teardown, the four flags should be re-checked
against it as the authoritative source.

## Re-sync history (no clobber, no force-push, no main-direct push)

- Branch `feature/combat-systems-20261024`, PR #1045. Original base
  main `62a44a2c`; re-syncs to `d852a0f6` then to `32f817f4` then to
  current main `dc303991` (each: fresh fetch, surgical re-apply, tests,
  fast-forward branch push only). The final push replaces the branch's
  engine files with main's lane + the deltas above, so the PR diff is
  exactly the 11 files listed in the PR body — no main-side work is
  reverted and no duplicate engine code ships. (The branch push itself
  carries 13 files: game/js/combat-core.js and game/js/game.js are
  pushed at their current-main content, which zeroes their PR diff.)
- GPU: no Kaggle GPU batch job was run — the change is small
  pure-logic code plus one moveset file and no batch processing
  benefited from it. Recorded in the PR body as part of the specified
  method ("for any batch verification/processing that benefits"), not
  as a deviation.
- ui-sources fix (after the merge commit): the gate failed because
  main's manifest rewrite cites a teardown path that does not exist
  in this repo at all (`teardown/tekken7-steam/pakchunk0/.../
  Base_OnlineMenu.png`; the whole `teardown/tekken7-steam/` tree is
  absent at HEAD). screen-menu is touched by this PR because it owns
  the changed bridge file, so the gate validates its sources. Fix:
  remove just that one missing source line from screen-menu; it
  keeps a valid teardown source plus its gre: sources, still
  sourced. No menu, code, or other manifest entry changed for this.

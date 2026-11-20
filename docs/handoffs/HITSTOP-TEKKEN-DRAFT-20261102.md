# Hit-stop tuning — Tekken-anchored DRAFT (2026-11-02)

## Status: DRAFT ONLY — NOT WIRED

Nothing in this document or in `game/js/hitstop-tekken-draft.js` changes
live combat. `game/js/combat-systems.js` (`feelFor`) and `game/js/game.js`
still run the current values in §2. Wiring the draft into combat is a
separate owner decision, because the draft's generic value is a large
change (see §4). Do not import the draft module into `game.js` or
`combat-systems.js` until the owner approves it in chat.

## 1. What was searched (and what was NOT found)

Searched, in order:

- `mhvnsnt/teardown-tekken7` — `TEARDOWN.md`, `TRANSFER-MAP.md`,
  `WIRING-PLAN.md`. Zero mentions of hit-stop / hit-freeze. Its §9 states
  the retail binary's hit-resolution internals are NOT REACHED (binary on
  a private PC only). No per-weight Tekken hit-stop table exists there.
- `mhvnsnt/western-heart/teardown/tekken7` and `teardown/tekken8` —
  roster/model/UI docs, no hit-stop table.
- `mhvnsnt/western-heart/docs/t7t8-reference/frame-data-t7/king.json`
  and `frame-data-t8-full/king.json` (sampled files) — 0 occurrences of
  "hitstop" and 0 of "timestop". Tekken frame-data rows carry startup,
  block, hit and counter-hit advantage — hit-stop is not a per-move
  frame-data column in the TekkenDocs / Wavu schema used in-repo.
- `mhvnsnt/game-reverse-engineering` — `teardown/tekken7-steam`,
  `teardown/tkdata/mothead` (move tables / clip banks). Move tables hold
  animation and frame data, not a hit-stop column; no hit-stop table
  was found there in this pass.
- Public Wavu Wiki Tekken 8 movelists and the Wavu Tekken 7 tech
  compendium (links in §5).

What was NOT found anywhere above: a Tekken 7 or Tekken 8 table of
hit-stop by move weight (light / medium / heavy / counter / wall).
That table does not exist in the sources searched. It is NOT invented
here — the draft in §3 is built from what Tekken actually publishes:
no generic value, plus special-case values only.

## 2. Western Heart current values (live, unchanged by this PR)

Frame = 1/60 s (`game/js/combat-core.js`: `FRAME = 1 / 60`).
`game/js/combat-systems.js` `feelFor` FX table, plus the `+3` frame
counter-hit bonus (not applied on block):

| Reaction | Frames | ms |
|---|---|---|
| hit (generic strike) | 6 | 100.0 |
| block | 4 | 66.7 |
| juggle | 5 | 83.3 |
| spin | 8 | 133.3 |
| stagger | 9 | 150.0 |
| screw | 10 | 166.7 |
| knockdown | 10 | 166.7 |
| guard_break | 10 | 166.7 |
| floor_bound | 11 | 183.3 |
| crumple | 12 | 200.0 |
| launch | 12 | 200.0 |
| wall_splat | 14 | 233.3 |
| throw | 0 | 0 |
| throw_break | 6 | 100.0 |
| wakeup | 0 | 0 |
| counter-hit bonus (any non-block reaction) | +3 | +50.0 |

`game/js/game.js` also sets a base before `feelFor` takes the max:
light 0.08 s (80 ms, 4.8f), heavy 0.11 s (110 ms, 6.6f), grab 0.10 s,
counter 0.14 s (140 ms, 8.4f), KO 0.18 s (180 ms). The FX table above
is therefore the effective value for most reactions, not the base.

## 3. Tekken-anchored DRAFT table (proposed, not wired)

Reading of the evidence: Tekken does not publish a generic,
weight-tiered hit-stop. Standard Tekken strikes carry no published
freeze value; the freeze values Tekken does publish are attached to
specific system / super-style moves only. The draft below mirrors
that shape exactly — it does NOT assign Tekken values to light,
medium or heavy that no source states.

| Reaction | Draft frames | Draft ms | Tekken basis |
|---|---|---|---|
| hit (generic strike) | 0 | 0 | No generic value published (see §1) |
| block | 0 | 0 | No generic block-stop published |
| counter-hit bonus | 0 | 0 | Counter-hit is an advantage column in Tekken frame data, not an extra freeze |
| stagger, spin, crumple, launch, screw, floor_bound, wall_splat, knockdown, guard_break, juggle | 0 each | 0 | No per-reaction Tekken freeze published; Tekken feel here comes from hitstun / reaction animation, not a freeze |
| throw, throw_break, wakeup | 0 | 0 | No freeze published; matches WH throw/wakeup today |
| SPECIAL ONLY — Heat-Burst-equivalent system move, named super-style / unblockable-style moves | 20 | 333.3 | Tekken 8: Heat Burst 20f timestop on block or hit; specific named moves noted "Hitstop 20f on hit" (Wavu T8 movelists, §5) |
| Parry success | NOT FOUND — no number assigned | — | Wavu notes "Hitstop on successful parry" with no duration stated; do not copy the 20f special value onto parry |

## 4. Why this draft needs an owner decision before wiring

Cutting generic freeze from 6–14f (100–233 ms) to 0f is not a tweak:
it removes the 2D-style weight feel Western Heart currently builds its
hit feedback on, and the lag fix in #1504 already separated that
designed freeze from the real uncapped-step bug. If the owner wants
Tekken-accurate feel, the draft is the honest Tekken shape. If the
owner wants to keep weight feel, the alternative already in-repo is
NOT retail Tekken and must not be sold as such:

- `docs/TK-COMBAT-ANALYSIS.md` §8: "Hit-stop: brief freeze on impact
  (0.04–0.12s) for weight" — 40–120 ms, 2.4–7.2f. That doc is a
  2026-10-13 analysis of a free-pull Tekken-like fighting game
  (`assets/free-pull-1/tk-fighting-game/`), not retail Tekken 7/8
  code, and it gives a range, not a per-weight table. Western Heart
  today already exceeds its top end on wall-splat, launch and crumple.

## 5. Sources

In-repo:

- `game/js/combat-systems.js` — FX table and `feelFor` (+3f counter bonus).
- `game/js/combat-core.js` — `FRAME = 1 / 60`.
- `game/js/game.js` — base hit-stop lines (0.08 / 0.11 / 0.14 / 0.18 s)
  and `Math.max(..., fx.stopSec)`.
- `game/js/hit-feel.js` — tuner base note: KO/heavy 0.12s, throw 0.10s,
  grab 0.06s, block 0.04s, strike 0.05–0.10s (tuner multipliers, not the
  FX table in §2 — the two are different layers; §2 is live combat).
- `docs/TK-COMBAT-ANALYSIS.md` §8 — 0.04–0.12s range, free-pull source,
  not retail Tekken (see §4).
- `mhvnsnt/teardown-tekken7/TEARDOWN.md` §9 — retail hit-resolution
  internals NOT REACHED.
- `docs/t7t8-reference/REFERENCE_SOURCES.md` — T8 frame data source
  (Wavu, CC0), T7 frame data link-only.

Public (facts only, no game files pulled):

- Wavu Wiki, Tekken 7 tech compendium — "Since Akuma has the unique
  2D-esque hitstop mechanic" (i.e. standard Tekken 7 moves do not carry
  that mechanic): https://wavu.wiki/t/User:Kalki/tech-compendium
- Wavu Wiki, Tekken 8 movelists — Heat Burst "20f timestop on block or
  hit", and specific moves "Hitstop 20f on hit" / "Hitstop on frame 80
  for 20f":
  https://wavu.wiki/t/Clive_movelist
  https://wavu.wiki/t/Lidia_movelist
  https://wavu.wiki/t/Anna_movelist
- Tekken 8 is the most recent Tekken game in the in-repo reference set
  (`docs/t7t8-reference/frame-data-t8-full/`); Tekken 7 was checked
  first per the owner's order and gives the same generic finding:
  no per-weight hit-stop column.

## 6. Missing, still owed

- Retail Tekken 7/8 engine code or a published per-weight hit-stop
  table: not found in any source above. It would require the retail
  binary / a code-grade extraction, which the teardown already marks
  NOT REACHED — do not guess it.
- Parry-success hit-stop duration: noted in Wavu, duration not stated.
- Wiring decision: owner to approve §3 (generic 0f + special 20f),
  keep current values, or pick the §4 free-pull range as a
  Western-Heart-original feel choice (labelled as such, not as Tekken).

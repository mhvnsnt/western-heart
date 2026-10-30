# KOF XV system actions as engine systems (2026-10-29)

Rows marked with a system qualifier (`(dash)`, `(backdash)`, `(roll)`, `(guard)`, `(MAX)`, `(taunt)`, `(throw escape)`) are now run by engine systems (game/js/fighter.js `KOF`, `_systemPress`, `trySystemMotion`). Before, the qualifier was stripped and the row played as an ordinary move from neutral, or it never parsed at all.

Frame data comes from the Dream Cancel wiki pages for KOF XV: Defense, Offense, and Meters and Gauges.

| System | Rule in the engine | KOF XV source |
|---|---|---|
| dash / backdash | A double tap f,f / b,b (the input buffer's dash latch) starts the row and moves the fighter. A button during the dash is the dash move (f,f+2). | run / backstep |
| roll | 33f total, invulnerable 1-24. It fires on the double tap only when no dash row owns that direction. | "Rolling ... universally last 33f. From frames 1-24 ... invincible" |
| guard cancel (GCAB roll / GCCD) | Fires only from blockstun and costs 1 stock. Neutral presses do nothing. The roll is invulnerable for its whole length; the blowback is invulnerable until its active frames end. | "While in block stun ... at the cost of 1 bar" |
| MAX Mode | Costs 2 stocks. Activation takes 30f (the row's startup of 0.5 s). Damage is +25% while the timer runs; a second activation while active is refused. | "Both cost 2 stocks ... 30f ... increases the damage ... by 25%" |
| taunt | Committed for at least 49f. It has no gauge effect, because XV taunts do not drain the gauge. | taunt: 49f uncancellable |
| throw escape | Its input breaks a throw only during the first 11 frames. In neutral it does not fire as a move. | "press ... during the first 11 frames" |

Gauge mapping: 1 KOF stock = 25 WH souls (the gauge holds 100).

APPROXIMATE: MAX lasts `KOF.MAX_SECONDS` = 10 s. XV's MAX gauge is 1000 points, but its drain rate is not published, so 10 s is an estimate until real frame data is found.

Each sweep check (test/e2e/moveset-sweep.page.js `sysCheck`) tests the rule, not only that a move fired:
- Dash rows: the double tap starts the row and the fighter moves the right way.
- Guard cancel: from neutral, nothing fires. From blockstun (block held), it fires and spends 1 stock.
- MAX: with an empty gauge it is refused. With a full gauge it spends 2 stocks and the timer counts down.
- Taunt: it stays committed for 49f or more.
- Throw escape: from neutral, nothing fires. While thrown, it breaks the throw.

Engine fixes found by the sweep:
- `maxmode` and `taunt` were never slotted on 1+2+3+4 / 2+3, so the earlier "pass" came only from a loadout the sweep equipped. They are slotted now.
- With a MAX row, 1+2+3+4 at 2 or more stocks is MAX before the Nine-Soul release / kindle claims. A taunt row on 2+3 outranks the spirit check.

Known gap: ryuji and ryuji-rock list both `evade_fwd "f,f (roll)"` and `dash "f,f (dash)"`, so the same input has two owners and the dash wins. In KOF XV the roll is A+B. Moving the roll rows to their own input is a data decision for the owner, so the rows are not edited here. The two roll rows are reported as failing, with that reason.

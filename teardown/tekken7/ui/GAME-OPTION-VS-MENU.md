# Tekken 7 GAME OPTION <VS GAME> — versus setup menu teardown

Source: Tekken Tag Tournament arcade operators manual (manuals.plus),
GAME OPTION section; Tekken 7 console GAME OPTIONS (adds INFINITY round
time and VERY EASY difficulty). Researched 2026-10-23 for the
Western Heart versus-setup submenu rebuild (PR #841).

## <VS GAME> options (arcade operator table)

| Option | Values |
|---|---|
| FIGHT COUNT <VS GAME> | 1, 2, 3, 4, 5 |
| ROUND TIME | 30, 40, 60, 80, 90, 99 seconds |
| GUARD DAMAGE | ON (a little) / OFF (none) |
| DIFFICULTY LEVEL | VERY EASY (console), EASY, MEDIUM, HARD, VERY HARD, ULTRA HARD |

## <1P GAME> options (same screen family)

| Option | Values |
|---|---|
| FIGHT COUNT <1P GAME> | 1, 2, 3, 4, 5 |
| LIFE BAR <1P> | -2, -1, 0, +1, +2 |
| ROUND TIME | 30, 40, 60, 80, 90, 99 seconds |
| GUARD DAMAGE | ON (a little) / OFF (none) |

## Tekken 7 console additions
- ROUND TIME: INFINITY (no timeout) added alongside 30/40/60/90/99.
- STAGE SELECT: versus setup offers stage SELECT or RANDOM (console
  versus mode flow: setup → character select → stage select / random).

## Layout grammar (T7 option-list screens)
- Full-screen list of labeled rows; each row shows the current value.
- Values cycle on tap (segmented options) — FIGHT COUNT 1-5, ROUND TIME
  30/40/60/90/99/∞, GUARD DAMAGE ON/OFF, STAGE SELECT/RANDOM.
- Gold/amber accent on the active value; dark background; large
  touch-friendly rows.

## What WH built from this
`game/js/versus-setup.js` + `#screen-vssetup` + `game/submenus.css`:
FIGHT COUNT 1-5, ROUND TIME 30/40/60/90/99/∞, GUARD DAMAGE ON/OFF,
STAGE SELECT/RANDOM. Every option writes `game/js/rules.js`
(`wh_rules_v1`) and changes the fight (rounds, timer, chip damage,
stage routing). See `game/tests/submenu-versus-setup-proof-20261023/`.

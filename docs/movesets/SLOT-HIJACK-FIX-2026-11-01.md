# Slot hijack fix (2026-11-01)

## What players saw
Pressing a basic button fired a different move:

| fighter | button | fired (before) | fires now |
|---|---|---|---|
| Purple Rain | 1 | `1,2,&amp;#58;4` (3-hit string Left Right Mid Kick) | `1~t8.lee` Jab (plays Lee's real T7 jab) |
| Purple Rain | 3 | `3~3` (Mist Trap / Trick Kick) | `3~t8.lee` Mist Kick |
| Purple Rain | 4 | `4,4,&amp;#58;4` (Machinegun Kicks Cardinal) | `4~t8.lee` Head Kick |
| Phantom | 3 / 4 | `3~4` / `4~3` | `3~t8.yoshimitsu` / `4~t8.yoshimitsu` |
| Rave | 3 / 4 | `3~4` / `4~4` | `3~t7.lei` / `4~t7.lei` |
| Diablo, Demonio, Demonio (winged) | 4 | `4~3` | their own single 4 |
| Negativo, Bruno, Dio, Michiko | 4 | `WR 4` (while-running 4) | their own single 4 |
| Michiko | 3 | `(3),4,4)` (unparsed string) | `3~t7.katarina` |
| Nightwolf, T3 Julia | f+3 | `f+3~1` | `f+3~t7.julia` |
| Mariposa, Mariposa (monarch) | SCR.3,3,4 | `SCR 3,3,4~D` | `SCR 3,3,4` |

19 slot lines in 14 files. No move was removed, renamed or changed; the moves that lost a slot stay reachable on
their own inputs (`3~4`, `WR.4`, `1,2:4`).

## Why
`tools/moveset-merge/merge_sources.py` `notation_of` (which builds every `slots` table) misread three things:
1. `VARIANT_SUFFIX` stripped every `~...` ending as a source tag. That is right for `~t7.lei` / `~donor.byou` but
   wrong for real tilde inputs, so `3~4` read as `3`.
2. `notation.py` mapped `WR 4` to plain `4`. The game's own `canonNotation` (`game/js/movesets.js`) reads it as
   `WR.4`, and so does the Python twin now.
3. A string whose input did not parse (scraped twice-escaped `&amp;#58;` = `:`) fell back to `input_slots[0]`, its
   FIRST hit, so `1,2,&amp;#58;4` slotted on `1`. The twin now unescapes until stable and joins `,:4` to the hit
   before it (`1,2:4`). The fallback uses the last `input_slots` entry, which is the whole input.

## Tools and guards
- Fix in the tool: `tools/moveset-merge/merge_sources.py`, `tools/moveset-merge/notation.py`.
- Data repair: `python3 tools/moveset-merge/repair_slots.py` (report; exit 1 while any remain) / `--write`.
  It re-points only the slots the OLD reading assigned (it keeps that reading as `legacy_notation_of`), to the
  move merge_sources ranks first for the input now (signature > T8 base > T7 base > T3 base > donor > proxy).
  Aliases made on purpose (`BT.2` -> `BT.1`, Pantera's `3+4,1` -> `JGS.1`) are not touched.
- Tests: `tools/moveset-merge/tests/test_notation_slots.py` (twin cases, legacy reading, repair plan) and
  `test/moveset-slot-hijack.test.mjs`. The second one, in CI, uses the game's canonNotation: no button slot fires
  a longer or while-running input when a move for the exact input exists.

## Left as is (12): no move answers to the plain input, so the slot keeps the game's no-dead-buttons fallback
aotsuki / gashadokuro / t3-kuma `b+3` -> `b+3~4`; jin_soul / phantom `NSS.4` -> `NSS.4~1`; rave `FC.D.4` / `SLD.4`
-> `4~3` forms (also t3-lei, vf-leifei); zui `d+2~n` -> `d+2~n~1`.

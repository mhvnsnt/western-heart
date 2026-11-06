# BT (back-turned) system fix — 2026-11-06

Owner report: Tekken's back-turned moves fire while the fighter is FACING the
opponent — the fighter turns backwards and does the BT move from the front.
"There's no back turned moment in the game." BT moves must happen on the right
inputs, at the right time, from a real back-turned state, wired straight from
the Tekken data.

## Diagnosis (all measured, none guessed)

The moveset DATA and the input RESOLVER were already Tekken-shaped:

- **758 BT-family rows across 65 fighters** (634 keyed `BT.*`; the rest in the
  source spellings `BT 1`, `BT+1`, composed `BT_RFF.*` / `NSS.BT.*`). BT entry
  is data-declared on **522 rows**: explicit `stance_after: BT`, `,B` / `~B`
  string variants, and the frame-data convention `(BT)` in a move's
  on-block/on-hit text ("the attacker ends back-turned"), which
  `fighter.js stanceAfterFromNotes` already derives.
- The game's own probe (TekkenBuffer, every fighter, fresh presses of
  1/2/3/4 + chords, facing vs back-turned contexts) showed **zero** facing
  presses resolving to a BT row — before this fix as well as after. The buffer
  only ever prefixes `BT.` when the context says back-turned.

What was missing was the STATE itself, in `game/js/fighter.js`:

1. **BT lived in the timed stance slot.** A move ending back-turned set
   `stance = 'BT'` with the generic **0.8 s** stance timer, and entering it
   overwrote any character stance — so the composed rows the data keys
   (`BT_RFF.1`, `NSS.BT.d+1`) could never fire, and BT vanished on a timer
   instead of ending by a turn-around the way Tekken works.
2. **The body never turned.** `Fighter.update()` snapped `facing` and
   `_faceYaw` toward the opponent **every frame** a fighter could act, with no
   BT exception. So during the invisible 0.8 s window the fighter LOOKED
   facing, its input context said back-turned, and its presses resolved BT
   rows — the BT clip then spun the fighter around "from the front". That is
   the owner's report, exactly.

## The fix (data-driven, no per-character code, no invented placements)

**`game/js/fighter.js` — BT is a facing state, not a stance:**

- New flag `Fighter._bt`. The two sites that apply a move's end state
  (`_tickState` attack completion, `_endThrowFollow`) translate
  `stanceAfter === 'BT'` into `_bt = true`; every other stance is unchanged.
  `_inputCtx()` reports `backturned` from `_bt` (a legacy `stance === 'BT'`
  still counts), so a character stance now SURVIVES entering BT.
- No timer: `_bt` persists in neutral until a Tekken turn-around resolves it —
  stepping **toward** the opponent (walk / dash in) re-faces, walking away
  keeps BT, `tryCrouch` / `trySidestep` / `tryJump` clear it, an attack start
  clears it (the press already resolved; the move's own end state re-applies),
  and a landed hit clears it after the back-hit knockdown flags read it
  (`_kdHeadTowards` / `_kdFaceDown` now read `_bt`).
- While `_bt` holds and the fighter can act, the facing block in `update()`
  points `_faceYaw` **away** from the opponent instead of snapping toward —
  there is now a visible back-turned moment, and a BT move's clip starts from
  a body that is actually turned.
- The chord-upgrade save/restore paths and `_preAtk` snapshots carry `bt`
  alongside `stance`, so re-resolving a chord in its pre-attack state keeps
  the facing it was pressed from.

**`game/js/movesets.js` — the buffer honors the data's BT spellings:**

- Prefix order in both resolvers (V2 + legacy): while back-turned, the
  composed prefixes the data keys — `BT_<STANCE>.` and `<STANCE>.BT.` — and
  then `BT.` are tried **before** the bare stance prefix. BT dominates the
  stance (Pond back-turned in MIST pressing 1 fires `BT.1`, not a MIST row).
  The facing matrix is byte-for-byte unchanged (see proof).
- `_prepare` gains a fill-only pass for the frame-data sharing convention:
  a BT row whose own `t7_command` declares a shared button — `BT 1 (or 2)`,
  `BT 3 (or 4)`, `BT d+1 (or d+2)`, `BT 1+3 (or 2+4)`, and the composed
  `(During BT RFF) 1 or 2` — gets the declared alternate slotted on the row
  the primary button fires. This is exactly what demonio's merged slots
  already wired by hand (`BT.2 -> BT.1`, `BT.4 -> BT.3`); the sibling files
  carried the same declarations in their rows but never got the slots, so a
  BT press on the shared button fell through to the FACING row.

## Resolution changes (whole roster, probe before/after): exactly 21

All in the back-turned context; the facing context changed **zero** times.

- BT 2 → BT.1 row, BT 4 → BT.3 row (their own `BT 1 (or 2)` / `BT 3 (or 4)`
  declarations): **demonio-human, demonio-winged, demonio-bloodline-ember,
  gyou-spirit-body, t3-anna, t3-eddy, t3-julia, t3-nina, t3-paul** (18).
- BT 2+4 → BT.1+3 throw (declared `BT 1+3 (or 2+4)`): **sakura, sha, star** (3).
- (Also newly reachable, same mechanism, no before/after press change in the
  basic matrix: t3-anna `BT.d+2 -> BT.d+1`, `BT.d+4 -> BT.d+3`; tobi /
  t3-hwoarang `BT_RFF.2 -> BT_RFF.1`; koreshi `NSS.BT.d+1` via the composed
  prefix; tobi `BT_RFF.1/.4` via the composed prefix.)

Proof: `proof/bt-fix-2026-11-06/bt-probe-summary.json` (probe method, totals,
the 21 changes, the named five's facing/BT matrices) and
`test/back-turned.test.mjs` (roster-wide no-leak assertion, the named five,
the sharing declarations, the composed rows, and the fighter-state rules:
body turned away, no timer, turn-around by step-toward / crouch / sidestep /
jump, stance coexistence). Stance regression family re-run: cd-ss-contexts
(#1601/#1603 CD + SSL/SSR), pond-stances (#1603), stance-reachability,
input-slotting, yaotome-stance, dead-input-s1-slotting — no change vs the
pre-fix engine.

## Open data gaps — left untouched, nothing invented

A BT press on these buttons still falls through to the facing row because the
fighter's own file carries no BT row for the button and no sharing
declaration:

- **koreshi — BT 4.** His file has BT.1 / BT.2 / BT.3 (+ strings, BT.d+1,
  NSS.BT.d+1); no BT.4 row and no `(or 4)` declaration anywhere in it.
- **tobi / t3-hwoarang — plain BT 1 and BT 2.** His only BT 1/2-class rows in
  the file are stance-composed: `t7.hwoarang_202` ("BT LFF 1 (or 2)"),
  `t7.hwoarang_203` ("BT LFF 3"), `t7.hwoarang_238` ("BT LFF 4"). The
  `BT LFF …` spelling does not canonicalize to a slotted notation
  (`canonNotation` returns `BT LFF 1`), and no plain-BT basic exists in his
  data to wire. His BT 3 / BT 4 / BT.d+3 and the RFF-composed rows
  (BT_RFF.1/.2/.3/.4) do fire.
- **megami / menajerii — BT basic strikes.** Their files carry only BT throws
  (`BT 1+3`, `BT 2+4` for megami; `BT 1+3`, `BT 3+4`, `BT d+3`,
  `BT d/f+1+2` for menajerii — all firing correctly in BT). Jun's / Roger
  Jr.'s BT 1/2/3/4 strikes are not in their merged movesets.
- **chatur — no BT rows at all** in her file (and no BT entry rows): Ogre's
  back-turned data is not in her merged moveset. Same for 97 other files with
  zero BT rows — the rule is uniform: no BT rows in the data, no BT moves;
  nothing was fabricated for any of them.

## What did NOT change

- No moveset JSON was edited. Every placement above is derived at load time
  from the rows' own declared commands by `_prepare`, the same mechanism as
  the existing canon-notation / input-slots / dead-d+1 passes.
- No stance behavior changed for any non-BT stance (timers, spins, entries
  from #1601/#1603 all verified by the regression family).
- Blocking while back-turned keeps the engine's existing guard rules; Tekken
  removes guard in BT, but that is a combat-balance change the data does not
  dictate, so it is deliberately out of this fix's scope.

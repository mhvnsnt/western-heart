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
  dictate, so it is deliberately out of this fix's scope. **Superseded the
  same day by the owner's rulings below — see the addendum.**

## Addendum 2026-11-06 — BT guard: Tekken-strict + the multi-arm hybrid

Three owner rulings, same day, after the deliberate omission above was
flagged to him:

1. **Tekken-strict (owner ~15:21 CST: "Yes I want it Tekken strict").**
   While `Fighter._bt` holds, guard is DISABLED: an incoming hit resolves
   through the existing unguarded path in `receiveHit` (full hit, normal
   reactions, the back-hit knockdown flags from the fix above), regardless
   of guard input. The moment `_bt` clears, guard works exactly as before.
   No damage change, no counter-hit addition, no BT entry/exit change, no
   moveset JSON edits.
2. **The multi-arm exception (owner ~15:23 CST):** fighters with more than
   one arm pair keep BT guard. Implemented DATA-DRIVEN — derived from the
   fighter's in-game model (extra arm chain in the rig) by
   `tools/anatomy/bt_guard_arm_scan.py`; the checked-in table lives in
   `game/js/bt-guard.js` and `test/back-turned.test.mjs` re-derives it from
   the GLB bytes on every run.
   - **Chatur QUALIFIES.** Her in-game model
     (`roster/rahkasa/attires/attire1/model-rigged-textured.glb`, 264
     joints) carries 4 arm chain roots: the primary pair (LeftArm /
     RightArm) plus the independently rooted waist pair
     (DEF-upper_arm.L.002 / DEF-upper_arm.R.002).
   - **DXMMII does NOT verify on current data** — attire1, patchwork-dj
     and `game/assets/models/dxmmii.glb` each carry one pair (the `.001`
     bones are mid-chain segments, not a second pair); attire2 is
     unrigged. **Zen does NOT verify either** — attire1 / oversoul /
     tentacle carry one pair (tentacles are not arm chains), spirit
     carries none. For both, the exception activates when their model
     data carries the extra pair; the flag was NOT faked.
   - Roster-wide sweep of `game/assets/models/` (64 GLBs, same detector):
     no other model carries more than one pair.
3. **The handicap — the owner's hybrid (owner ~15:36 CST: "Bleed design
   go with that but we build the guard break design as a layer into it
   from soul calibers files, so we just invented something new
   awesome."):** bleed base + a SoulCalibur guard-break layer, wired as
   the `bt_guard` design in `game/js/bt-guard.js` (per-fighter data hook:
   a fighter's own `btGuard` data block overrides field-by-field). While
   back-turned and guarding, a qualifying fighter blocks highs/mids only;
   every blocked hit bleeds **30% chip** through the existing chip
   formula/recoverable pool (front guard: 0.12), earns **zero meter**
   (front guard: +4), pushes back at **half rate**, does **not** clear
   `_bt`, and adds **strain**. Lows and throws land 100% clean. At strain
   max the back pair is spent — BT guard off for the rest of that BT
   stint (Tekken-strict until a real BT exit); **strain resets when `_bt`
   ends**. HUD tell (SC-style): the defender's own health-bar fill glows
   **yellow at 60% strain, red at 80%** (`.bt-strain-1` / `.bt-strain-2`,
   toggled by `UI._hp` from `Fighter.btGuardState()`).

**Strain derivation (provenance mandatory).** Holdings check first: NO
extracted SoulCalibur system data is held — the SCVI binaries were never
acquired (`teardown/scvi-doa6-acquisition-2026-10-14.md`), and
`teardown/soulcalibur-6/docs/SCVI-MECHANICS.md` is our own qualitative
research write-up. The numbers therefore come from DOCUMENTED system data
(SuperCombo Wiki, SoulCalibur VI / System — extracted game data, read
2026-11-06): guard stamina accumulates 0→100%, bar glows yellow at 60%,
red at 80%, Guard Crush at 100%, Guard Impact costs 10%; 240 HP all
characters; move levels lights 0–21 / mediums 22–34 / heavies 35+; per-move
Guard Burst values published per move (16 dmg → 5%; 18–20 → 9–14%; 30 → 9%;
32 → 18%; 36 → 15%; 40 → 25%; 52 → 41.67%). WH's scale, measured from
`game/assets/movesets/chatur.json` (281 damaging non-grab moves): median
13, p75 16, max 60, basics 7/11. **The fitted rule is
`strain = 0.75 × blocked move damage`** (listed damage, not stat-scaled —
in SC, Guard Burst is a property of the attacking move). Anchors: jab 7 →
5.25 ≈ SC light ~5%; medium ~16 → 12 ≈ SC 9–15%; heavy 30 → 22.5 ≈ SC
18–25%; max 60 → 45 ≈ SC break ceiling 42–50%. Break profile: ~19 jabs,
~8 mediums (≈2–3 medium strings), ~4–5 heavies. **The 100/60/80 gauge is
documented SC data + the owner's spec; the 0.75 slope and the WH↔SC scale
conversion are JUDGMENT CALLS fitted to the documented anchors — they are
not SC data.** Observation (not implemented): in SC, small quick attacks
cannot crush even at 100% stamina; the owner's break-at-max design governs
and is what shipped.

Tests: `test/back-turned.test.mjs` cases (a)–(i) + the model-derivation
test; the #1611 regression family (cd-ss-contexts, pond-stances,
stance-reachability, input-slotting, yaotome-stance, dead-input) re-run
green; full CI suite green.

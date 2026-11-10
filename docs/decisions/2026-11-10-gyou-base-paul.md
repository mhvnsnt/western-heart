# Gyou's base is Paul Phoenix (owner, 2026-11-10)

## Owner, verbatim

- 2026-11-10: "Gyou isn't supposed to have hwoarang guard? Someone else has hwoarangs moves and whollyhot so many things
  mixed like that gyou has someone else's moves"
- 2026-11-10: "Gyou was probably Paul Phoenix and fire attacks"
- 2026-10-23 (recorded in `game/assets/movesets/gyou-spirit-body.json` `flame_attacks.note`): "he can have Paul Phoenix
  moves mixed with like flame attacks or whatever"

## What it resolves

`docs/MOVESET-PATTERN-AUDIT-2026-10-24.md` left Gyou open: "Gyou — NEEDS-DECISION (owner): is Paul the canonical base
(2026-10-23 pull) with Hwoarang rows to be re-slotted out, or is the file intentionally Paul + Hwoarang?" The answer is
Paul. Hwoarang is Tobi's base (`roster-full.js` tobi: base Hwoarang, own Hwoarang T7 stance / bank / move pack). The
old nine-souls-appendix mapping "Hwoarang → GYOU" (`CANON.md` §APPENDIX 2026-10-20) is superseded for the WH fighter.

## What changed

- **Moveset:** `game/assets/movesets/gyou.json` is rebuilt by `tools/moveset-merge/rebase_moveset.py`. It starts from
  `gyou-spirit-body.json`, the Paul + flame moveset a lane built for the 2026-10-23 order: Paul's T3 bank moves plus the
  12 user-requested flame attacks.
  - Carried over: Gyou's own Paul T7/T8 rows from the 2026-10-23 pull (46 new keys), his two WH signatures (Cannot Stop,
    Everywhere Already) and his Paul motbin block.
  - Dropped: 723 Hwoarang rows (T7 326, T8 209, T3 188) and 145 Jin rows. That includes the Mishima crouch dash; Paul
    has none.
  - The old file is archived byte-for-byte at `docs/archive/movesets/gyou-pre-paul-rebase-2026-11-10.json`.
- **Motion:**
  - `FIGHTER_BANK.gyou` hwoarang → paul (Tekken 3 Paul bank).
  - `T7_STANCES.gyou`: Paul's own T7 kamae.
  - `OWN_SLOT_BANKS.gyou` / `OWN_SLOT_CANDIDATES.gyou`: `t7_paul` (walk / dash / crouch / jumps / sidesteps / guard /
    hit / launch / KO from Paul's own T7 states, `tools/anim/t7_generic_slots/pau.json`).
  - The Hwoarang T7 move pack (`moves.gyou.pack.json`) is unwired; the file stays.
- **Roster:** `roster-full.js` gyou base Hwoarang → Paul Phoenix, moveset 'demonio' → 'gyou'.

## Still open

- His real Paul T7 attacks: a Paul move pack through `tools/anim/t7_move_bake.py --code pau`, the same path as
  Pantera's King moves.
- The flame attacks are form-locked to his transformations (Flame Emperor, God of the Flame, Guardian, Flame Eternal).
  They are data in the file; the transformation mechanics that unlock them are not wired yet.

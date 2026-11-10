# Thor plays Ganryu's real T7 attacks; Gyou plays Paul's

Owner, on Gyou (2026-11-10): "Gyou was probably Paul Phoenix and fire attacks". Thor's canon (`roster/thor/CANON.md`,
owner verbatim): "Ganryu is Thor, the literal norse god of lightning".

Before this change, both fighters stood in their own T7 stance and moved with their own T7 walk, guard, hit and KO
(`docs/proof/2026-11-10/thor-ganryu/`, `docs/proof/2026-11-10/gyou-paul/`). Their attacks were still Tekken 3 stand-ins:
- Thor's were Bryan's T3 rows;
- Gyou's were Paul's T3 bank.

Now each attack is the base character's own Tekken 7 move.

## How each move is made

1. **Map.** `tools/anim/t7_move_resolve.py` maps a moveset row to a motbin move only when both of these hold:
   - the row's input, pressed from the stance, reaches the move through the game's own cancel graph;
   - the move's damage and first active frame equal the row's T7 frame data.
2. **Bake.** `tools/anim/t7_move_bake.py` bakes each clip:
   - The 0x64 clips go through the game's own sampler (`tools/anim/t7_anim64_to_c8.py`, read from the shipping exe).
   - Every FK self-check reads 0.000 m.
   - Every clip passes the in-game plausibility gate: upright start, floor contact, no limb flips.
3. **Wire.** `T7_MOVES.thor` uses the Ganryu dir and `T7_MOVES.gyou` uses the Paul dir with `moves.gyou.pack.json`
   (`game/js/t3anims.js`). A pressed row plays its pack clip, timed on the motbin move's own active frames.

## Thor: 25 of Ganryu's own moves

- **The moves:** 1, 2, 3, 4, f+4, 1+2, b+2, b+4, b+1+2, d/f+1, d/f+4, f+2, f+3, f+1+2, f+3+4, d+1, d+2, d+4, d/b+2,
  u/f+2, u/f+1+2, and the dash moves f,F+2 / f,F+3 / f,F+1+2 / f,F+3+4. They come from `ganrotsm.arc` (his own arc)
  and `ganmot.bin`; 24 clips in all, because 4 and f+4 share one.
- **His own 1-4.** Ganryu is not in Tekken 3, so the T3 pass gave Thor Bryan's rows as stand-ins. The 2026-10-20 T7
  import deduped by input, so six of Ganryu's 139 sheet rows never entered the file: 1, 2, 2,1, 2,1,2, 3, d/f+2. The
  sheet's `4 or f+4` row was there, but nothing could press it.
- **`tools/moveset-merge/t7_sheet_fill.py`** puts the dropped rows back on their inputs and makes `4 or f+4`
  reachable on 4 and on f+4:
  - Each Bryan stand-in moves to `<key>~t3proxy` verbatim, so no row is removed. It keeps its input, so the game's
    notation fallback still finds its T3 clip.
  - The new rows' fields follow the import's own rule. Before writing, the tool checks that the rule reproduces all
    126 existing Ganryu strike and string rows exactly.
  - The old file is archived byte for byte: `docs/archive/movesets/thor-pre-t7-fill-2026-11-10.json`.
- **Kept out:**
  - d/f+1+2 (`mm`, damage 10,10) is two slaps, and the second slap is a separate follow-up motbin move, so one clip
    would show half of it. The bake's multi-hit rule now also counts damage values, which catches it.
  - d/f+2 and the rows in `data/thor_resolve.log` marked no_match do not match the motbin. They keep their fallback.

## Gyou: 36 of Paul's own moves

- **The moves:** 1, 2, 3, 4, f+2, f+3, f+1+2, d/f+1, d/f+2, d/f+3, d/f+4, d+1, d+1+2, d/b+2, b+1, b+2, b+3, u/b+2,
  u/f+3 and b+1+2. Also the string steps 1,2 / 1,4 / 2,d+3 / 3,2 / f+2,3 / f+2,3,1 / d/f+1,1 / d/f+1,1,2 /
  d+1,2 / d+1,4 / d+4,2,1+2 / b+1,2 / u/f+3,4 / f,F+3,4, and the dash moves f,F+3 and f,F+4. All come from
  `paurotsm.arc`, Paul's own arc.
- **Paul was not blocked.** The earlier note said "Gyou's Paul attacks are blocked (paumot.bin missing)". In fact
  the resolver crashed on the first missing file. It now records a missing bank file per row as `file-absent`.
- **Kept out:**
  - b+4 (`plkw_s4_4rk`) and u/f+2 (`plkb_earth`) live in `paumot.bin`, which the teardown lacks. They keep their
    current clips.
  - d/f+3,4 fails the plausibility gate (it does not start upright).

## Data

- `data/thor_resolve.json`, `data/thor_resolve.log`, `data/thor_bake.log`
- `data/gyou_resolve.json`, `data/gyou_resolve.log`, `data/gyou_bake.log`

## Tests

- `test/t7-moves-0x64.test.mjs` gains both fighters. It checks the pack format, the exact frame data per row, the
  plausibility of every frame, the wiring, the loader, and that the 1-4 slots reach the pack.
- 139/139 pass across t7-moves-0x64, t7-moves-king, t7-stance and t7-generic-banks. The full suite passes 568/569;
  the one failure, `test/hitbox.test.mjs` (`this.ui.attackData is not a function`), fails on main too.

# T7 graph: the exe cancel walk, loader-derived cancel_option, matcher, list-property timing (2026-11-10)

Dev graph only (`?t7graph=1`, strict). It is not on by default, has no T3 fallback, and is not 100%. Nothing here was checked in a browser, on a model, or by touch.

## Why strict executed 0 commands: the adapter's walk semantics were wrong (not just unknown conditions)
Findings from the shipping exe (IB 0x140000000):
- **The packed moveset carries `cancel_option = 0` on all 11,862 King cancels.** The game derives the option at load in loader `0x140714f5e` (cancels from `0x14071525e`, group cancels from `0x14071539e`):
  - `0x01`: command 0, so the matcher returns 2 (always matches).
  - `0x02`: the requirement list holds an id in [0x32C, 0x8000) (`0x1406fd3b0`).
  - `0x04`: the list holds an id ≥ 0x349 (`0x1406fd3e0`).
  - `0x08`: the list holds 0x84CE.
  - `0x40`: `(extradata & 0x3C00) != 0x2800`.
  - `0x80`: `(extradata & 0x3F) == 0x16`.
- **Main walk `0x140749240`** (body `0x140749568..0x1407496ec`, called at `0x1407500ff` and `0x140750a3d`):
  - Rows go in order. A group reference 0x800B is walked in place until 0x800C; the reference row's own fields are not tested. The walk ends at the AUTO row 0x8000.
  - Each row is checked in this order: frame window [start, end]; skipped if option 0x02; input match `0x140742de0`; requirement list `0x1406f4750` (AND).
  - When the list holds, each list entry is passed to `0x140717750` (phase 1, then phase 0). The var/flag writers run in phase 0 only (`0x140718a82` → `0x140719717` → switch `0x1407198ac`).
  - **The walk stops only on an option-0x40 row.** Rows with extradata `& 0x3C00 == 0x2800` apply their properties and the walk continues.
  - A taken row whose extradata is 0x3FFF is replaced by the AUTO row (`0x1407496a0`). An option-0x80 row is passed over when `[self+0x8fc]` != 0.
- **Secondary walk `0x14074f040`** (called at `0x1407508c5`, same move and frame) handles only option-0x02 rows.
- **Matcher `0x140742de0`:**
  - Direction mask 0 means no direction requirement. Bit 0x400 additionally tests `[self+0xde0]`.
  - The direction test is `[self+0xddc] & mask`.
  - Button test `0x140743d40`:
    - **button word 0 matches whether or not a button is pressed** (`0x140743d4f` → `0x140743e79`);
    - bit 29: any of the press bits;
    - bit 30: one press bit plus all of them held (bit i → held bit 9+i);
    - no mode bit: all press bits;
    - bits 9..17: held;
    - bits 18..26: must be set in `[self+0xdd8]` (meaning untraced, so UNKNOWN);
    - 0x80000000..3 are special words.
- **Requirement id 0** is true (`0x1406f55dc`).
- **Round start** sets yaw = bearing for both players (`0x1406e5623` / `0x1406e566e`), so `[self+0x1c2]` = 0.

## What changed (`game/js`)
- **`t7CancelOption`** applies the loader formula. **`commandMatch`** transcribes the matcher. **`stepCancel`** follows the main walk:
  - option-0x02 rows go to the secondary walk; under strict, a live candidate there is ambiguous because the order of the two walks is not traced;
  - non-stopping rows never block;
  - unknown non-stopping rows only make the state they write unknown.
- **`applyListProps`** gives a passing row's var/flag writers their exact values at walk time, in row order, so later rows see them.
  - The P1 rule is removed: the exe matches button-less rows on press frames.
- **Heading:**
  - `t7RelHeadingFromWorld` derives relHeading16 from WH geometry (own facing vs the vector to the opponent).
  - It returns a value only when |angle| < 0x3fff, where 72/73/80/81 do not depend on the unproven sign.
  - It is used **only until the first source move fires**. The idle loop re-entering the same move with turn word 0 keeps it.
  - After that it is UNKNOWN, because source turning is not modelled: move word +0x56 on entry, extradata 0x8000 flip, per-frame update `0x14074afe0`.
- **`graph.props.json`** now carries `turn_0x56` per move.

## Result (strict, real Fighter, real input path) — `test/t7-graph-adapter-pantera.test.mjs`
- **Opponent ahead:**
  - neutral 1 → `Kg_lp00F`, then 2 → `Kg_lprpF` (1,2 string);
  - f → `Kg_sWALKF`;
  - after an idle loop, 1 still → `Kg_lp00F`;
  - f,n,f → `Kg_sDASHF`. The run is then held back only by 80, because heading is unknown after a source move.
- **No opponent geometry:** nothing fires. Every block is facing 72/80 or item 609. Neutral never blocks.
- **Not done:**
  - the source heading after a source move (next foundation item);
  - `[self+0x390]` (356);
  - extra-property per-frame timing (writers still make state unknown on move entry);
  - `[self+0xdd8]` writer;
  - order of the secondary walk;
  - throws (still no hitbox, UNSUPPORTED);
  - the differential Unicorn oracle (`tools/anim/exe_re/emulate_sampler.py`) is not yet extended to the walker.

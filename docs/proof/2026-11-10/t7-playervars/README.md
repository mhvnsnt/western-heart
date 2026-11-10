# King T7 player variables (809/361), the extra-property import, and strict input semantics (2026-11-10)

## Extra properties imported systematically

`tools/anim/t7_graph_props.py` reads the same King motbin JSON as the graph importer. It writes `game/assets/anim/t7/king/graph.props.json` (`wh-t7-graph-props/1`, 836 KB), keeping every source index:
- 12,227 extra-property rows (1,567 per-move lists);
- 531 end-prop rows;
- 0 start-prop rows.

The layouts come from TekkenMovesetExtractor `motbinExport.py` (T7). The frame flag bits and property semantics are kept raw. The file is separate from `graph.json`, so the 772-clip shards, which carry `graph.json`'s sha256, stay valid with no repack and no rebake.

The throws and throw-extras tables (header 0x260/0x270) are not in that JSON export. They need a bin reader and are **not imported yet**.

## Exe decode

| What | Exe |
|---|---|
| 809 = `[self+0x938] == param` | evaluator case `0x1406f7849` |
| 361 = `[self+0x964] == param` | `0x1406f7e2c` |
| property switch: `id − 0x8001` jump table | `0x1407198ac` / table `0x14071fca8` |
| 0x8414/0x8415/0x8416 = set/add/sub `[0x938]` | cases `0x14071a25e/26a/276` |
| 0x80ed/0x8112/0x8113 = set/add/sub `[0x964]` (low 16 bits of the value) | `0x14071a6a6/6b4/6c2` |
| 0x8106/0x8107/0x8108 = set/add/sub own player flag `[0x968+idx*2]`; 0x8109/0x810a = the same on the opponent | `0x14071a990…` |
| reset that zeroes `[0x964]` and `[0x938]` (7 call sites) | `0x140746ad0` (`0x140746bd7/bdd`) |

The community labels "prop 0x8414" / "prop 0x80ed" agree. The only other `+0x938` write is in a transform-array initialiser of another struct.

**King's data:**
- No extra/start/end property list writes either variable.
- 32 requirement lists do, across 667 cancel rows, for example `[[809,13],[33812,3]]`. The evaluator returns 1 for these entries without side effects (`0x1406f54d9`). When the engine applies them was **not traced**.

## Runtime (strict dev mode)

- Variables are zeroed at match start (exe reset).
- After a cancel whose list contains a writer fires, that variable becomes UNKNOWN.
- After a WH-engine suspension (hit stun etc.) both become UNKNOWN. They are never re-zeroed by guess.
- Result: stance row #0 (`[[809,15],[33812,0],[361,100]]`) is now **known-false** at match start.

**Input semantics.** The old "button-less row ignores a press frame" rule (P1) is unproven. Under STRICT it is no longer applied quietly: such a row, and any row with unproven sequence/mode/special/timing semantics, blocks lower rows unless its requirement list is known-false. It is reported as `input-semantics` and similar reasons.

## Honest state

**Strict still executes 0 stance commands.** Every input is now blocked by stance row #132 → `Co_sabaloRKn`, with `[[815,16],[359,0xA0001],[553,800],…]`:
- 815 "parry low" needs opponent attack state (`0x1406f9085`);
- 359 = own flag 10 == 1, written by 0x8106-family entries (20 requirement-list entries and 21 extra-prop rows in King's data), and its frame/apply semantics are not traced;
- 553 is the engine RNG (`0x1406f6d9e`, LCG `*0x21131993`).

Any one of them being known-false would decide the row.

## Tests

`test/t7-graph-adapter-pantera.test.mjs`, 23/23, through the real Fighter in STRICT:
- six inputs (n, n+1, f, d/f, 3+4, f+1+3): no fire; the block is on row #132 with [815, 359, 553]; the press frames report `input-semantics`; the move holds; there is no hitbox;
- variable zeroing, the writer census (0 in property lists, 667 rows in requirement lists), fail-closed after a writer row, and suspension.

Node only. No browser, touch or model proof. Not 100%.

## Next blockers, in order

1. When the engine applies requirement-list property entries (the cancel-taken path), and the flag-reset semantics. This would make flag 10 and the variables trackable.
2. Opponent state for 815 (parry), or a proof it is false when the opponent is idle.
3. The RNG state for 553, or AND-elimination through 815/359.
4. The throws/throw_extras bin reader.

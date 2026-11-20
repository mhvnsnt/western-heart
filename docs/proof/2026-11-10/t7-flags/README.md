# T7 graph: player flags (359), exe default-false requirement ids, props-driven state writers (2026-11-10)

Dev graph only (`?t7graph=1`, strict). It is not on by default. Nothing here was checked in a browser, on a model, or by touch.

## Source facts (shipping exe `TekkenGame-Win64-Shipping.exe`, IB 0x140000000)
- **Player init 0x140759a50.** `xor esi,esi` at 0x140759ec5. It then zeroes `[+0x938]` (0x14075a033) and `[+0x958]`/`[+0x960]` qwords (the latter covers `[+0x964]`). It also zeroes the 100 player-flag words `[+0x968..+0xa2f]` with `rep stosw`, ecx = 0x64 (0x14075a02c..0x14075a065). The 0x63 bound in the flag writer and in requirement 359 matches this.
- **Requirement 359.** The prologue at 0x1406f551b..0x1406f556d computes idx = param >> 16 and value = sign-extended low word. The case reads word `[+0x968 + idx*2]`, and idx > 0x63 → false.
- **Flag writers.** Property switch 0x1407198ac: 0x8106/0x8107/0x8108 set/add/sub the own flag (0x14071a99d); 0x8109/0x810a write the opponent's flag (0x14071a9f7).
- **Default case.** The evaluator 0x1406f5490 jump table 0x1406f9478 has 0x36C entries. 329 of those slots point at the default 0x1406f56e5 (`xor bl,bl` → false), and ids > 0x36B reach the same default via `ja`. These ids are source-proven always false in this build. The list is extracted from the binary into `T7_EXE_DEFAULT_FALSE`. Among them, 167 and 254 (514 King rows) were previously UNKNOWN.
- **Requirement 356.** `[self+0x390] == param` (0x1406f7e02). The field is not labelled by the community sources and its writers are not traced, so it stays UNKNOWN.

## Runtime (game/js)
- The driver initialises `playerVars` and `playerFlags` (100 × 0) before it enters the stance. Any property entry that can write tracked state makes that state UNKNOWN; it is never given a guessed value. Such entries are:
  - a fired cancel row's requirement-list entries;
  - an entered move's extra/start/end properties from `graph.props.json`, now loaded by `ensureT7Graph`.
- The apply timing within a move is not traced, so writers fail closed for the rest of the run.
- Suspension makes all flags unknown.

## Effect (strict, real Fighter, King stance `Kg_sKAM00_`)
- **Row #132** `[[815,16],[359,655361],[553,800],…]` is now KNOWN-false, because flag 10 is still 0 and an AND with one false term is false. 815 and 553 are not guessed.
- **Remaining blockers** that outrank every tested input:
  - #280/#286 (72 backturn), #306/#308 (80 facing);
  - #322 (356 `[+0x390]`);
  - #221 (609 item + 72).
- So strict still fires **0** stance commands. The cause is now the own-yaw `[+0x1b8]` writers (146, not traced) and `[+0x390]`.
- Command map (match-start state): unknown 13,372 → 12,468; known-false 15,075 → 15,979.
- Tests: `test/t7-graph-adapter-pantera.test.mjs` (25 pass).

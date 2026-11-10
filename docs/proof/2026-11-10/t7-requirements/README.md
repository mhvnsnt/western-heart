# King T7 requirement evaluator: decoded from the shipping exe (2026-11-10)

**Source.** `TekkenGame-Win64-Shipping.exe` (image base 0x140000000) from the private reverse-engineering repo checkout. It is not in this repo.
Disassembled with capstone. The function is located through `.pdata`.

**Community cross-checks:**
- TekkenMovesetExtractor `game_addresses.txt`: `t7_chara_id_offset = 0xD8`.
- TekkenMovesetExtractor `additionalReqDetails.py` (master `ddd676a5`, sha256 `a82162c0…`): chara ID table with 2 = King, and req225 0 = Player, 1 = CPU.
- TKMovesets `editor_t7_requirements.txt`: labels.

## The evaluator

`0x1406f5490` takes `(req* rcx, self rdx, opponent r8)`:
- It loads id = `[req]` and param = `[req+4]`, and sets result = 0.
- **If id & 0x8000 is set, it returns 1 immediately.** The caller has not been inspected, so ids ≥ 0x8000 (for example 33030, 33446, 33816) stay UNKNOWN in the runtime.
- It then runs a switch on id 0..0x36B (875) with a jump table at `0x1406f9478`. Unknown ids go to the default `0x1406f56e5`, which is false.
- Case 0 is true.
- Throw-side cases 2..16 compare the id with a computed throw direction (this matches the community labels).

| id | exe case | decoded semantics | runtime |
|---|---|---|---|
| 217 | `0x1406f6757` → `0x1406f46a0(ecx=[self+0xD8], param)` | **self chara_id == param**. Params 76..90 go through a jump table to fixed ids: 76→0x21, 77→0x22, 78→0x23, 79→0x3d, 81→0x1f, 83→5, 85→0x45, 87→0x1e, 89→0x0f; 80/82/84/86/88/90→0x4b | needs `charId`. Pantera = King = 2 (community table; offset 0xD8 matches the exe) |
| 225 | `0x1406f6827` | controller type `[self+0x1570]` (0 = player). In both exe paths a player-controlled fighter is true only for param 0. A non-player with param 0 depends on flags `[self+0x151c]`, `[self+0x14dc]` and `0x140713980` | needs `controller`. The driver runs only for the human player → 0. CPU + param 0 = UNKNOWN |
| 609 | `0x1406f8683` | false when a global byte at `rip+0x2de6fae` is set; otherwise a virtual call on the customization object `0x140731900` → `[vtbl+0x118](side [self+0xd4], item id)` | needs the full equipped T7 item set. Pantera has none known, so it stays UNKNOWN |
| 72 | `0x1406f5bdd` | word `[self+0x1c4]` > 0x4000 (backturned) | needs `backturned`. WH does not model the source facing word, so it stays UNKNOWN |
| 73 | `0x1406f5bf1` | word `[self+0x1c4]` <= 0x4000 | same |
| 80 | `0x1406f5cd5` | (word `[self+0x1c2]` − 0x3fff) ≤ 0x4000 (unsigned 16-bit) | not modelled, UNKNOWN |
| 81 | `0x1406f5cf4` | (word `[self+0x1c2]` + 0x8000) ≤ 0x3fff | not modelled, UNKNOWN |
| 35 / 36 | `0x1406f583a` / `0x1406f585b` | float param ≥ / ≤ distance `[self+side*4+0x74c]` (needs an opponent) | needs `oppDistT7`, UNKNOWN |
| 126 | `0x1406f6163` | bit 2 of `[opp+0x230+0x34]` | not modelled, UNKNOWN |
| 554 | `0x1406f6e23` | `[self+0x3b0]` mod param == 0 | not modelled, UNKNOWN |
| 254, 1 | default | **always false in this exe** (not yet applied in the runtime; the caller still needs inspecting) | UNKNOWN |

## Effect on King's reachable command rows

Same 37,419 rows; Pantera context `{dead:false, charId:2, controller:0}`:

| Status | before (PR #1728) | now |
|---|---|---|
| evaluable | 7,775 | 8,459 |
| unknown | 28,247 | 13,567 |
| known-false | 1,039 | 15,035 (mostly rows gated to other chara_ids) |
| timing | 151 | 151 |
| special | 134 | 134 |
| seq-mode | 73 | 73 |

- Evaluable stance press commands: 66 → 73. All 73 replay through the real input path.
- Unknown-condition rows now (a row can carry several, so the counts overlap and are not a partition):
  - 609: 7,151
  - 72: 1,852
  - 81: 913
  - 80: 911
  - 254: 448
  - 33030: 386
  - 359: 385
  - 553: 384
  - 33446: 384
  - 33816: 384
- 175 distinct unknown condition ids remain.

## Tests

`test/t7-graph-adapter-pantera.test.mjs`:
- Decoder expectations written from the disassembly, including fail-closed behaviour without context.
- The real Fighter carries charId 2 / controller 0.
- A 300-step real-input replay where every fire gated by 217 is gated to King's own chara_id.
- The existing 400-step replay now checks fires against the full context.

## Not done / next

- The equipped item set for 609.
- The source facing word for 72/73/80/81: posture and backturn state.
- The caller of the evaluator (the ≥0x8000 ids, and whether default-false ids can be applied).
- Throws and `throw_extras`: still unsupported, with no grab.
- Sideways root motion and blending.

Node only. No browser, touch or model proof. Not 100%.

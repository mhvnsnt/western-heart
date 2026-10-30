# Close/far normals by distance, Rush/hop slotting, JGS spin counting (2026-10-29)

Owner: "Wire far/close by distance (KOF/SF standard: close normal within a range threshold), Rush and JGS spin counting so these variants fire in real fights".

## What fires now in a fight
- **Close/far normals** (`game/js/movesets.js` `_variant`, `CLOSE_RANGE = 1.65` m root to root). A plain button fires the move whose input is `N (close)` when the opponent is within 1.65 m. Beyond that it fires `far N`. Standing bodies never get closer than 1.45 m (push `minDist` in `game/js/fighter.js`), so close range is a short step past body contact.
- **Editor wins:** a moveset-editor loadout entry on that button always overrides the distance pick.
- **Chord upgrades still work:** `1` then `1+3` inside the 140 ms window becomes the 1+3 move. `variantBase()` maps `far_1` back to `1` for this.
- **Stance spins:** `fighter._stanceSpins` counts how many times a move re-enters the stance it started from. It resets when the stance times out or the fighter is hit.
  - `JGS.N` after 2–5 Jaguar Steps fires the `JGS* (N spins)` row.
  - pantera `stance_after` now has `3+4_t8` (Jaguar Step) → JGS and `b+3+4` (Reverse Jaguar Step) → JGS, matching T7 King.
- **Rush and hop rows:** name-keyed rows (`rush_l2` "1,1 (Rush)", `hop_1` …) are slotted on their canonical input when no other move owns it.

## Sweep checks (`test/e2e/moveset-sweep.page.js`)
- **Close/far rows:** pressed with NO loadout at 1.45 m (close) or 1.70 m (far). The row passes only when the distance pick fires that exact key and it connects. The base T3 row on the same button is checked as the editor equips it.
- **Spin rows:** the fighter starts from neutral and fires the real stance entry move N times. Then `JGS.N` must fire the N-spin key.

Compared with the previous run (p17/p18): ryuji 135→135, ryuji-rock 135→136, pantera 696→696 and jin_soul 785→785, with 0 regressions. `node --test test/*.test.mjs` passes 116/116, and input determinism reports "non-string failures: 0".

| fighter | key | input | via | setup | result |
|---|---|---|---|---|---|
| ryuji | `far_1` | 1 | far normal by distance | neutral · range 1.70 m (close ≤ 1.65 m) | PASS |
| ryuji | `far_2` | 2 | far normal by distance | neutral · range 1.70 m (close ≤ 1.65 m) | PASS |
| ryuji | `far_3` | 3 | far normal by distance | neutral · range 1.70 m (close ≤ 1.65 m) | PASS |
| ryuji | `far_4` | 4 | far normal by distance | neutral · range 1.70 m (close ≤ 1.65 m) | PASS |
| ryuji | `close_1` | 1 | close normal by distance | neutral · range 1.45 m (close ≤ 1.65 m) | PASS |
| ryuji | `close_2` | 2 | close normal by distance | neutral · range 1.45 m (close ≤ 1.65 m) | PASS |
| ryuji | `close_3` | 3 | close normal by distance | neutral · range 1.45 m (close ≤ 1.65 m) | PASS |
| ryuji | `close_4` | 4 | close normal by distance | neutral · range 1.45 m (close ≤ 1.65 m) | PASS |
| ryuji-rock | `far_1` | 1 | far normal by distance | neutral · range 1.70 m (close ≤ 1.65 m) | PASS |
| ryuji-rock | `far_2` | 2 | far normal by distance | neutral · range 1.70 m (close ≤ 1.65 m) | PASS |
| ryuji-rock | `far_3` | 3 | far normal by distance | neutral · range 1.70 m (close ≤ 1.65 m) | PASS |
| ryuji-rock | `far_4` | 4 | far normal by distance | neutral · range 1.70 m (close ≤ 1.65 m) | PASS |
| ryuji-rock | `close_1` | 1 | close normal by distance | neutral · range 1.45 m (close ≤ 1.65 m) | PASS |
| ryuji-rock | `close_2` | 2 | close normal by distance | neutral · range 1.45 m (close ≤ 1.65 m) | PASS |
| ryuji-rock | `close_3` | 3 | close normal by distance | neutral · range 1.45 m (close ≤ 1.65 m) | PASS |
| ryuji-rock | `close_4` | 4 | close normal by distance | neutral · range 1.45 m (close ≤ 1.65 m) | PASS |
| pantera | `t7.king_160` | JGS.1 | stance spin variant (JGS.1 after 2 stance entries) | stance JGS · 3+4_t8 ×2 → JGS spins=2 | PASS |
| pantera | `t7.king_161` | JGS.1 | stance spin variant (JGS.1 after 3 stance entries) | stance JGS · 3+4_t8 ×3 → JGS spins=3 | PASS |
| pantera | `t7.king_162` | JGS.1 | stance spin variant (JGS.1 after 4 stance entries) | stance JGS · 3+4_t8 ×4 → JGS spins=4 | PASS |
| pantera | `t7.king_163` | JGS.1 | stance spin variant (JGS.1 after 5 stance entries) | stance JGS · 3+4_t8 ×5 → JGS spins=5 | PASS |
| pantera | `t7.king_165` | JGS.2 | stance spin variant (JGS.2 after 2 stance entries) | stance JGS · 3+4_t8 ×2 → JGS spins=2 | PASS |
| pantera | `t7.king_166` | JGS.2 | stance spin variant (JGS.2 after 3 stance entries) | stance JGS · 3+4_t8 ×3 → JGS spins=3 | PASS |
| pantera | `t7.king_167` | JGS.2 | stance spin variant (JGS.2 after 4 stance entries) | stance JGS · 3+4_t8 ×4 → JGS spins=4 | PASS |
| pantera | `t7.king_168` | JGS.2 | stance spin variant (JGS.2 after 5 stance entries) | stance JGS · 3+4_t8 ×5 → JGS spins=5 | PASS |
| pantera | `t7.king_170` | JGS.3 | stance spin variant (JGS.3 after 2 stance entries) | stance JGS · 3+4_t8 ×2 → JGS spins=2 | PASS |
| pantera | `t7.king_171` | JGS.3 | stance spin variant (JGS.3 after 3 stance entries) | stance JGS · 3+4_t8 ×3 → JGS spins=3 | PASS |
| pantera | `t7.king_172` | JGS.3 | stance spin variant (JGS.3 after 4 stance entries) | stance JGS · 3+4_t8 ×4 → JGS spins=4 | PASS |
| pantera | `t7.king_173` | JGS.3 | stance spin variant (JGS.3 after 5 stance entries) | stance JGS · 3+4_t8 ×5 → JGS spins=5 | PASS |
| pantera | `t7.king_179` | JGS.d/f+4 | stance spin variant (JGS.d/f+4 after 2 stance entries) | stance JGS · 3+4_t8 ×2 → JGS spins=2 | PASS |
| pantera | `t7.king_180` | JGS.d/f+4 | stance spin variant (JGS.d/f+4 after 3 stance entries) | stance JGS · 3+4_t8 ×3 → JGS spins=3 | PASS |
| pantera | `t7.king_181` | JGS.d/f+4 | stance spin variant (JGS.d/f+4 after 4 stance entries) | stance JGS · 3+4_t8 ×4 → JGS spins=4 | PASS |
| pantera | `t7.king_182` | JGS.d/f+4 | stance spin variant (JGS.d/f+4 after 5 stance entries) | stance JGS · 3+4_t8 ×5 → JGS spins=5 | PASS |
| pantera | `t7.king_187` | JGS.4 | stance spin variant (JGS.4 after 2 stance entries) | stance JGS · 3+4_t8 ×2 → JGS spins=2 | PASS |
| pantera | `t7.king_188` | JGS.4 | stance spin variant (JGS.4 after 3 stance entries) | stance JGS · 3+4_t8 ×3 → JGS spins=3 | PASS |
| pantera | `t7.king_189` | JGS.4 | stance spin variant (JGS.4 after 4 stance entries) | stance JGS · 3+4_t8 ×4 → JGS spins=4 | PASS |
| pantera | `t7.king_190` | JGS.4 | stance spin variant (JGS.4 after 5 stance entries) | stance JGS · 3+4_t8 ×5 → JGS spins=5 | PASS |

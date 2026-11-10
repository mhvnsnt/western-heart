# T7 graph — source heading trace (14:51 CST pass, 2026-11-10)

Disassembly facts only (static reading of the original executable). No executed-original evidence, no
emulator run, no visual/browser/touch proof. Not full parity. Graph stays opt-in (`?t7graph=1`).

## Proven by disassembly
- Move entry: the new-move setup block (loads the next move from `self+0xda0`) contains the yaw block, so
  these rules run **once per move entry**, not per frame:
  - cancel extradata bit 15 → flip: yaw16 += 0x8000;
  - new move `u_0x98` bit 27 set and `(extradata-derived [0xdb4] & 0x3C00) != 0x1C00` → yaw16 −= `u_0x56`
    (`turn_0x56` is a 16-bit binary angle and is **subtracted**);
  - two further extradata bits (dd0 0x10 → yaw from another field, dd0 0x80 → yaw = 0) — not modelled → unknown;
  - then the facing writer recomputes relative heading against the opponent bearing (atan2 of the XZ delta).
- Per frame: the animation/root update writes `yaw = wrap(base_heading + T)` every frame unless a player
  flag (`0x4a0 & 0x200`) is set. `T` comes from a per-fighter state record whose writer is **not traced**
  (it carries an integer budget initialised to 0x2000 and decremented each frame — consistent with
  tracking, but unproven).

## Consequence (blocker)
Source facing after any move start = base heading + undecoded per-frame term `T`. Facing-gated rows
(72/73 backturned, 80/81 side) therefore cannot be evaluated source-validly after the first source move.
The adapter keeps its current fail-closed behaviour (world heading until the first source move, then
unknown). No code change in this pass: a partial move-entry model would still be unknown every frame
after entry, and inventing `T = 0` would be a guess.

## Continuous commands
Unchanged from the walker commit: from the round-start stance with the opponent ahead, 1 → Kg_lp00F,
1,2 → Kg_lprpF, f → Kg_sWALKF, f,n,f → Kg_sDASHF. Repeated / return-to-stance sequences remain blocked
on heading (labelled), not satisfied by expecting blocks.

## Next
Trace the writer of the per-frame yaw term (record at `+0x78`, budget `+0x74`) and `0x4a0 & 0x200`;
then implement base heading + T in the driver with tests for repeated sequences, both sides, moved opponent.

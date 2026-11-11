# T7 graph — heading tracking fix (19:35–21:30 CST pass, 2026-11-10)

Disassembly facts + node-harness evidence. No executed-original evidence, no emulator run, no visual/browser/touch
proof. Graph stays opt-in (`?t7graph=1`). Supersedes the 14:51 CST pass in `../t7-heading/README.md`, which concluded
the adapter must keep failing closed after the first source move: that conclusion is now overturned — the entry rules
are traced, they are implementable from the shipped data, and the heading stays resolved after every move.

## The bug (reproduced, node harness, STRICT, opponent ahead at x=3)

After any source move fired, `T7GraphDriver.headingFromWorld` went false and every `step()` forced
`evalState.relHeading16 = null`. Conditions 72/73/80/81 went unknown; in STRICT an outranking stopping cancel row
whose requirement was unknown blocked the whole cancel evaluation (`ambiguous`), and at clip end with an ambiguous
row open the move stalled on its last frame instead of transitioning. Repro matrix (`repro2.mjs`, pre-fix):
S1 jab -> stance -> jab again (2nd jab never fired, stance f14 cond 80 row #306); S2 1,2 -> stance -> jab (blocked);
S3 jab -> stance -> hold f (walk never fired, row #467 cond 80 every frame); S4 f,n,f dash -> hold f (run never
came out, dash frozen f30, rows #459/#462 cond 80); S5 five-move sequence (stuck in stance after 1,2); S6 3+4
fstep -> 1 (never fired); S7 walk -> press 1 (walk stalled 16 frames, frozen f20). Blocking rows are button-less
state rows (cmd 0x70/0x40, btn 0, window [1,32767], req [[80,0]]) that match any input once the heading is unknown.

## Proven by disassembly (TekkenGame-Win64-Shipping.exe, Steam depot 389731)

- Move entry, entry function 0x14074ff50-0x1407500b2: TURN — the new move's word at +0x56, when nonzero, is
  SUBTRACTED from the yaw word [self+0x1be], the base heading [self+0x100] and the yaw float [self+0x1b8]
  (0x14074ff8c-0x14075003d; conversion is the split constant pair summing to 2pi/65536). It is UNCONDITIONAL at
  this site — no u_0x98-bit or [0xdb4] gate (the README's gate belongs to the per-frame site 0x14074c7a7, gated by
  [self+0x731], whose writer is untraced). FLIP — the taken row's extradata bit 15 (0x8000) adds pi to base and yaw
  and 0x7fff (not 0x8000 — the 14:51 README is off by 1 LSB) to the yaw word (0x140750045-0x1407500a5).
  Then the facing writer runs (call 0x1406ebfe0).
- Facing writer 0x1406ebfe0: [self+0x1bc] = bearing (atan2 of the opponent-minus-own XZ delta, x65536/2pi);
  [self+0x1c2] = yaw16 - bearing16 (0x1406ec0be) — rel = yaw - bearing; [self+0x1c4] = folded rel (rel >= 0x8000
  gives ~rel). Round start sets yaw = bearing (0x1406e5623), so rel = 0.
- Entry continuity correction, per-frame function 0x14074d086-0x14074d0f1: when a next move is pending and the
  facing mode is not in {0x40,0xC0,0x2C0,0x340} and [self+0x731]==0 and the next move's u_0x98 bit 9 is clear,
  yaw16 += rootYaw_current(frame) - rootYaw_next(frame-1), where the sampler 0x140749f70 returns atan2 of the
  sampled animation's root transform (its frame argument is clamped to >= 1 then minus 1).
- Facing-mode switch 0x14074d0f8: [self+0xdb4]&0x3C0 selects face-opponent (yaw := bearing, rel = 0) vs keep-yaw vs
  yaw := [self+0x1ca]. [0xdb4] is computed by 0x140749bc0 from SMALL CONSTANTS (0xa2/0xa5/0xe2/0xe5 at the call
  sites in 0x14074f800-0x14074f982) plus the next move's u_0x98/u_0xa0/u_0xa4/u_0x68 and [self+0xdb0] — NOT from
  cancel extradata. Its input switch's source is untraced, so the mode is not computable from shipped data today.
- The animation root-yaw track is NOT in the shipped clip bank. Measured from the shipped shards (rot_xyzw Hips
  channel): stance net -0.6deg, jab -2.4, dash +0.6, lk -1.6, walk -13.4, run +51.8, lprpF +33.5, fstep01 +333
  (a real spin, smooth per-frame deltas). But the Hips heading is the PELVIS TWIST, not the facing: the run travels
  EXACTLY straight (root_t heading 0.0deg on all 31 frames) while Hips yaw sweeps 75deg. The bake carries no root
  rotation track, so the continuity correction cannot be computed from shipped data and is not guessed.

## The fix (game/js/t7-graph-driver.js, game/js/fighter.js; t7graph.js unchanged)

The driver tracks the source yaw in the world frame from the shipped entry rules plus the live signed bearing:
- `yaw` (float rad, null until anchored); the first step with a live bearing anchors yaw = bearing (round-start
  rule); entry turn/flip adjustments made before the anchor accumulate in `_yawPending` and apply at the anchor.
  After a suspension re-entry the WH-facing truth re-anchors it (labelled in the code, not hidden).
- `_enter(id, row)`: flip — the taken row's extradata & 0x8000 adds pi; turn — the new move's turn_0x56, when
  nonzero, subtracts turn*2pi/65536. The row is `cancels[fire.index]` for cancel fires (stepCancel returns the
  row index, including the via3fff AUTO-row fire) and the move's AUTO row (cmd 0x8000) resolving to the transition
  target for transition fall-throughs.
- `step()`: every frame, relHeading16 = wrap16(yaw - worldBearingRad). No bearing (no opponent geometry) -> null,
  as before. The test-injection override (`_t7gHeadingOverride`, forwarded as evalState.headingOverride) wins.
- `fighter.js`: new `t7WorldBearingRad(f, opp)` — signed atan2(dz,dx), null without geometry; `t7gFeed` supplies
  it (and the override) and no longer sets relHeading16; the dev-label `assumptions` string states the new model.
  `t7RelHeadingFromWorld` is kept as a magnitude-only utility (the driver no longer uses it).
- Core-loop entry rows have turn 0 and no flip (stance AUTO 0x80, jab row 0x185, walk/dash rows 0x214), so for the
  verified sequences the tracked yaw is exact at entry; the residual is the unmodelled per-entry continuity
  correction (~10-20deg for core entries) plus tracking (turns yaw toward the bearing, so it can only shrink |rel|).
- The 80/81 left/right SIGN keeps the old "sign unproven" caveat: the axis order atan2(dz,dx) is the shipped
  `t7RelHeadingFromWorld` convention, not proven against the exe's vector swizzle in the facing writer. The front
  cone (|rel| < 90deg) is unaffected — 80/81 are both false whatever the sign.

## Verification (node harness, clone @ f7c4fe7 + this fix)

- Full suite `test/t7-graph-adapter-pantera.test.mjs`: 30/30 pass (baseline 28/29). The pre-existing chara_id
  failure is FIXED by this change (heading-gated 217 rows now resolve and fire); one full-suite run out of five
  showed the chara_id test failing once (timing-sensitive 300-iteration replay under load — not reproduced in the
  four runs after it, 3/3 in isolation). New regression test: STRICT, opponent ahead, 1,2 -> walk -> dash ->
  dash-loop -> dashing punch (8 cancel fires, 5+ consecutive moves) — heading resolves on every recorded frame,
  zero facing blocks, zero stalls.
- Repro matrix (`repro2.mjs`, STRICT, opponent ahead): S1/S2/S3/S6/S7 all complete with zero ambiguous blocks and
  zero stalls (2nd jab fires, walk fires, fstep -> 1 fires, walk -> 1 fires). S5 completes 8 fires. S4: the dash
  fires and falls through to the walk with no stall; the heading is resolved (rel 0) throughout. One heading
  subtlety exercised by S5: after the fighter crosses the opponent (root x > 3, bearing pi), the tracked yaw flips
  to pi via a real entry flip (Co_R row extradata bit 15) while rel stays 0 — the cross-up case works as designed.
- Opponent-behind case (new assertion in the end-to-end test): the opponent walks behind mid-fight, bearing flips
  to pi while the tracked yaw stays 0 -> rel 0x8000, cond 72 true, 73 false.

## What is NOT fixed here (residual, named next steps)

- The RUN in STRICT is held back by undecoded cond 124, not by heading. Dash row 478 (re-dash, req 1085 =
  [[124,0]]) is a stopping row at dash frame 12 and blocks the run row 479 (req 0). Cond 124's case is decoded
  (exe evaluator 0x1406f5490, jump table 0x1406f9478 — entries are absolute RVAs; case 124 at 0x1406f60e4): TRUE
  iff any of the three floats at [fighter+0x12d0/0x12d4/0x12d8] is nonzero. The field's identity (velocity?
  root-motion delta?) is unproven, so it is NOT implemented — never guessed. Row 476's run path is held back by
  cond 36 (distance, req 2132 = [[36,3800]]; oppDistT7 not supplied). The run still fires in PERMISSIVE (the
  mechanics test proves the row). Next: trace the writer of [0x12d0..0x12d8] and supply oppDistT7, then implement
  124 + 36.
- Per-frame tracking, the entry continuity correction, and the [0xdb4] facing modes remain unmodelled (see above).
  They matter near the 90deg condition boundaries and after turning moves (240/2787 moves have nonzero
  turn_0x56); the front-cone sequences verified here are exact at entry. Next: re-bake the anim root-yaw track
  from the .arc files (or trace the root-yaw writer) and implement the correction + modes.
- Browser / visual proof is still owed: the node harness proves the interpreter path; a headless-Chromium fight
  run (the playverify harness) has not been run for this fix.
- Disk note: this lane hit the VM disk quota mid-work (EDQUOT, 120G/150G used); the RE exe was deleted from local
  disk to restore writes (it is 100% stored in the GRE release t7-shipping-exe-20261031,
  mhvnsnt/game-reverse-engineering, sha256 7f2b6872...).

## Files changed

- game/js/t7-graph-driver.js — tracked source yaw (entry turn/flip, live bearing), headingFromWorld removed.
- game/js/fighter.js — t7WorldBearingRad; t7gFeed supplies the bearing + override; assumptions string updated.
- test/t7-graph-adapter-pantera.test.mjs — 3 tests rewritten to the resolved-heading behavior + 1 new regression
  test (5+ move sequence); the two tests that asserted heading-unknown-after-a-move are gone.
- docs/proof/2026-11-10/t7-heading-fix/README.md — this file.

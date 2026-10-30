// Pantera hit-from-front string (docs/proof/moveset-sweep-20261028/r17-core8-failing.json):
// t7.king_110 'b+2, 4 (only during hit from front)' (Chupacabra to Olympia Slam).
// Canon used to leave the note as bare words ('b+2,4 only during hit from front',
// via the final paren-to-words rule), so the sweep parse-ERRed before any press ran.
// The honest treatment is a canon strip, NOT a new setup case: the 4 follow-up fires
// only when b+2 hits the foe from the front, and the sweep's default setup IS
// front-facing (foe standing facing the attacker), so the bare input 'b+2,4' is the
// stated situation — unlike CROUCHFOE / TIMER* / WALLSTUN, where the situation
// differs from the default and a setup case was needed. Residual, stated plainly:
// this is mechanism proof (canon + parse path), not a witnessed full-fight pass —
// whether the engine's string machinery fires the conditional follow-up only on a
// front hit is what the next sweep reports.
import test from 'node:test';
import assert from 'node:assert/strict';
import { canonNotation } from '../game/js/movesets.js';

test('hit-from-front condition strips to the bare string', () => {
  assert.equal(canonNotation('b+2, 4 (only during hit from front)'), 'b+2,4');
  assert.equal(canonNotation('b+2,4'), 'b+2,4');
});

test('guards: plain strings, the Front Kick to DDT row, and neighbouring rules are untouched', () => {
  assert.equal(canonNotation('b+2, 4'), 'b+2,4');
  assert.equal(canonNotation('f+3,1+2'), 'f+3,1+2');
  assert.equal(canonNotation('1 (first hit only)'), '1');
  assert.equal(canonNotation('DES.BT.1'), 'DES.BT.1');
  assert.equal(canonNotation('During enemy wall stun... f, hcf+1'), 'WALLSTUN.f,hcf+1');
});

test('guard: a mid-string hit-from-front note is NOT stripped (trailing-only rule)', () => {
  assert.equal(canonNotation('b+2 (only during hit from front), 4'), 'b+2 only during hit from front,4');
});

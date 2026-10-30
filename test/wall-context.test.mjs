// Back-to-wall sweep rows (docs/proof/moveset-sweep-20261028/r17-core8-failing.json):
// '(back to wall).b,b,UB' (Burger, Pantera) and '(Back to wall).b,\u200bb,\u200bUB'
// (Cyborg X, with scraped-list zero-width separators between steps) are wall-jump attacks
// whose input has no button. The sweep classes buttonless inputs as movement (n/a), not
// failures, so the context canonicalises to the WALL. prefix and the rows leave the
// failing list on the next sweep. Wall-position witnessing (pressing the motion with the
// back actually at the wall) is the recorded residual, not a hidden gap.
import test from 'node:test';
import assert from 'node:assert/strict';
import { canonNotation } from '../game/js/movesets.js';

test('back-to-wall rows canonicalise to WALL., zero-width separators stripped', () => {
  assert.equal(canonNotation('(back to wall).b,b,UB'), 'WALL.b,b,U/B');
  assert.equal(canonNotation('(Back to wall).b,​b,​UB'), 'WALL.b,b,U/B');
  assert.equal(canonNotation('(Back to wall).b,b,UB'), 'WALL.b,b,U/B');
});

test('guards: neighbouring context rules unchanged by the WALL rule', () => {
  assert.equal(canonNotation('back to opponent, 2'), 'BT.2');
  assert.equal(canonNotation('(During Jump) qcf+1'), 'AIR.qcf+1');
  assert.equal(canonNotation('f,n,d,d/f+1'), 'f,n,d,d/f+1');
  assert.equal(canonNotation('H.2+3'), 'H.2+3');
});

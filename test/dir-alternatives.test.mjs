// Pantera direction-alternative step (docs/proof/moveset-sweep-20261028/r17-core8-failing.json):
// 'ss2+4,b/db' (Reverse Special Stretch Bomb (Cancel)) was 'unparsed' because
// canonNotation's diagonal rule turned the 'db' in the 'b/db' step into 'd/b', giving
// the unparseable step 'b/d/b'. A step written '<cardinal>/<diagonal>' lists two
// directions for one step; the first listed is the playable one, the same first-listed
// rule the alternatives rule already applies to '1+3_2+4' / 'd/b+1/2/3' / 'U/F or U/B'.
// The row's own T8 id settles the reading: it carries t8_id 'King-ss2+4,b', and T8 ids
// in this moveset are 'King-' + the full T8 input with commas preserved, so a sequence
// reading 'b,d/b' would have read 'King-ss2+4,b,d/b'. No fighter data touched —
// shared canon code only. A grep across all eight core-8 movesets (keys, inputs,
// input_slots) confirms the cardinal/diagonal step pattern hits exactly this one row.
// Residual, stated plainly: this moves the row from 'unparsed' to pressable; the next
// sweep still has to witness it in a fight (sidestep throw cancel timing), and that
// trace is a follow-up, not claimed here.
import test from 'node:test';
import assert from 'node:assert/strict';
import { canonNotation } from '../game/js/movesets.js';

test('direction-alternative steps resolve to the first listed direction', () => {
  assert.equal(canonNotation('ss2+4,b/db'), 'SS.2+4,b');
  assert.equal(canonNotation('b/db'), 'b');
  assert.equal(canonNotation('f/df+1'), 'f+1');
  assert.equal(canonNotation('B/DB'), 'B');
  assert.equal(canonNotation('ss2+4,b'), 'SS.2+4,b');
});

test('guards: lone diagonals, the WR any-horizontal rule, and neighbours unchanged', () => {
  assert.equal(canonNotation('f,n,d,d/f+1'), 'f,n,d,d/f+1');
  assert.equal(canonNotation('u/b+1'), 'u/b+1');
  assert.equal(canonNotation('b/f+1'), 'WR.1');
  assert.equal(canonNotation('CLK(Two spins).3'), 'CLKTwo spins.3');
  assert.equal(canonNotation('(back to wall).b,b,UB'), 'WALL.b,b,U/B');
  assert.equal(canonNotation('WS 1+2* (one spin)'), 'WS.1+2*');
});

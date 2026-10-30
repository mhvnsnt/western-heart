// Demonio just-frame '#' rows (docs/proof/moveset-sweep-20261028/r17-core8-failing.json):
// 'CD.df#1' / 'CD.df#2' were 'unparsed' because canonNotation left the '#' in the
// token ('CD.d/f#1'), which the sweep's parse() rejects. '#' between a diagonal
// direction and a button is Tekken's just-frame mark: the rows' own t8_id spells the
// same slot '${justFrame}' ('Jin-CD.df${justFrame}1'), and the same move already
// exists in this moveset in the ':' spelling ('CD.d/f:1', same name, same anim_ref,
// same on-block -13), where ':' is the codebase's just-frame separator. So the rows
// canonicalise to 'CD.d/f:1' / 'CD.d/f:2' and the sweep equips them on that notation
// through the loadout. No fighter data touched — shared canon only.
// Residual, stated plainly: parse + loadout attempt, not a witnessed frame-perfect
// just-frame pass — the ':' cadence is the codebase's existing just-frame
// representation, not a frame-perfect timing gate.
import test from 'node:test';
import assert from 'node:assert/strict';
import { canonNotation } from '../game/js/movesets.js';

test('just-frame hash rows canonicalise to the colon spelling', () => {
  assert.equal(canonNotation('CD.df#1'), 'CD.d/f:1');
  assert.equal(canonNotation('CD.df#2'), 'CD.d/f:2');
});

test('guards: entity decode, colon rows, and neighbouring rules unchanged', () => {
  assert.equal(canonNotation('df+1,&amp;#58;2*'), 'd/f+1:2*');
  assert.equal(canonNotation('CD.d/f:1'), 'CD.d/f:1');
  assert.equal(canonNotation('CD.df+1'), 'CD.d/f+1');
  assert.equal(canonNotation('f,n,d,d/f+1'), 'f,n,d,d/f+1');
  assert.equal(canonNotation('H.2+3'), 'H.2+3');
});

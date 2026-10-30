// DES.BT two-word stance (docs/proof/moveset-sweep-20261028/r17-core8-failing.json):
// Cyborg X t7.alisa_235 'DES BT 1 (or 2)' canonicalises to 'DES.BT 1' because the
// stance-space rule dots only the first word, and the sweep parse rejects it.
// Joining the second word before a button gives 'DES.BT.1', the spelling the
// existing Hertz Blade - Flare row already carries — so the row leaves the
// parse-error list on the next sweep. Residual, stated plainly: this is a
// parse reclassification, not a witnessed pass — the sweep's DES.BT stance
// setup is the same downstream question as the existing DES.BT.1 row.
import test from 'node:test';
import assert from 'node:assert/strict';
import { canonNotation } from '../game/js/movesets.js';

test('DES BT two-word stance joins to DES.BT. before a button', () => {
  assert.equal(canonNotation('DES BT 1 (or 2)'), 'DES.BT.1');
});

test('guards: neighbouring DES/BT spellings unchanged by the DES.BT join', () => {
  assert.equal(canonNotation('DES.BT.1'), 'DES.BT.1');
  assert.equal(canonNotation('DES.1'), 'DES.1');
  assert.equal(canonNotation('BT.1'), 'BT.1');
  assert.equal(canonNotation('DES BT 1'), 'DES.BT.1');
});

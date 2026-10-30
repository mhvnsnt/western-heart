// Cyborg X trailing spin-count annotations (docs/proof/moveset-sweep-20261028/r17-core8-failing.json):
// t7.alisa_141 'WS 1+2* (one spin)', t7.alisa_142 'WS 1+2 (two spins)' and
// t7.alisa_185 '(During Clockwork) 3 (more than a single spin)' were 'unparsed'
// because canonNotation's final paren rule turned the note into bare words
// ('WS.1+2* one spin'), which the sweep's parse() rejects. The spin count is an
// animation descriptor, not an extra input: the two WS rows stay distinct after
// stripping via the hold mark ('WS.1+2*' vs 'WS.1+2'), and the Clockwork row has
// no same-input conflation partner. No fighter data touched — shared canon only.
// Residual, stated plainly: the next sweep still has to witness these rows in a
// fight (stance entry for CLOCKWORK, WS state for the WS rows); this fix moves
// them from 'unparsed' to pressable, it does not by itself prove the press lands.
import test from 'node:test';
import assert from 'node:assert/strict';
import { canonNotation } from '../game/js/movesets.js';

test('trailing spin-count annotations strip to the bare input', () => {
  assert.equal(canonNotation('WS 1+2* (one spin)'), 'WS.1+2*');
  assert.equal(canonNotation('WS 1+2 (two spins)'), 'WS.1+2');
  assert.equal(canonNotation('(During Clockwork) 3 (more than a single spin)'), 'CLOCKWORK.3');
  assert.equal(canonNotation('WS 1+2* (3 spins)'), 'WS.1+2*');
});

test('guards: mid-string and non-trailing spin notes are untouched by this strip', () => {
  // 'CLK(Two spins).3' was ALREADY mangled by the pre-existing final paren rule
  // ('CLKTwo spins.3') before this change and stays exactly that — this chunk
  // deliberately does not collapse it to 'CLK.3' (a different row, 20 dmg/-9 vs
  // 22 dmg/+0, and stance_after has no CLK entry). The assertion pins the
  // pre-existing value so a future change to it is visible, not silent.
  assert.equal(canonNotation('CLK(Two spins).3'), 'CLKTwo spins.3');
  assert.equal(canonNotation('JGS* (3 spins), 1'), 'JGS.1');
  assert.equal(canonNotation('f,f (roll)'), 'f,f');
  assert.equal(canonNotation('WS.1+2*'), 'WS.1+2*');
  assert.equal(canonNotation('during Ya Otome, qcf,qcf,qcf,qcf+1+2'), 'YA_OTOME.qcf,qcf,qcf,qcf+1+2');
});

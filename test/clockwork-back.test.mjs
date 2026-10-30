// Clockwork back step (docs/proof/moveset-sweep-20261028/r17-core8-failing.json):
// Cyborg X t7.alisa_186 '(Clockwork Spring Middle) B' (t7 damage 0, hit level '-') is a
// buttonless step taken during the Clockwork Spring Middle move: Tekken's B is a held-back
// direction, not a button (buttons are 1-4), and 'Clockwork Spring Middle' is the name of
// the CLOCKWORK.3 row in this same moveset. The t7 Clockwork rows already use the CLOCKWORK.
// prefix ('(During Clockwork) 3' -> 'CLOCKWORK.3'), so the row canonicalises to
// 'CLOCKWORK.B' — the t7-dataset twin of the existing 'CLK.B' Clockwork Cancel row — and
// the sweep's parse() reads it as motion-only (no button), the sweep's own movement class,
// not a failure and not a witnessed pass. Residual, stated plainly: the sweep moves
// alisa_186 from the failing list to movement; what holding back during Spring Middle
// actually does in play (cancel/transition) and entering Clockwork itself are not
// witnessed by this chunk. Deliberately NOT covered: Dio's 'DFLIP N' (space form,
// Hyakkigozan, 23 dmg / low / KND) is a real strike whose entry input is not established,
// so it stays open — this rule touches only the literal Clockwork Spring Middle phrase.
// This test reads the REAL sweep page source and reconstructs its parse(), so a parse
// change that stops treating B as a direction step fails the test.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { canonNotation } from '../game/js/movesets.js';

const pageSrc = readFileSync(new URL('./e2e/moveset-sweep.page.js', import.meta.url), 'utf8');

function realParse() {
  const start = pageSrc.indexOf('const MOT = ');
  assert.notEqual(start, -1, 'sweep page has no MOT table');
  const fnStart = pageSrc.indexOf('function parse(n)', start);
  assert.notEqual(fnStart, -1, 'sweep page has no parse()');
  const ret = pageSrc.indexOf('return { pre, hits };', fnStart);
  assert.notEqual(ret, -1, 'sweep page parse() has no return');
  const end = pageSrc.indexOf('\n  }', ret);
  assert.notEqual(end, -1, 'sweep page parse() has no close');
  const code = pageSrc.slice(start, end + 4);
  return new Function(`${code}; return parse;`)();
}

test('clockwork spring middle back step canonicalises to CLOCKWORK.B', () => {
  assert.equal(canonNotation('(Clockwork Spring Middle) B'), 'CLOCKWORK.B');
});

test('the real sweep parse reads CLOCKWORK.B as motion-only (movement, not a failure)', () => {
  const parse = realParse();
  const p = parse('CLOCKWORK.B');
  assert.equal(p.err, undefined);
  assert.deepEqual(p.motionOnly, ['B']);
  assert.equal(p.pre, 'CLOCKWORK');
  const old = parse('Clockwork Spring Middle B');
  assert.ok(old.err, 'the old bare-words form must still parse-ERR without the fix');
});

test('guards: neighbouring clockwork forms and DFLIP N unchanged', () => {
  assert.equal(canonNotation('(During Clockwork) 3 (more than a single spin)'), 'CLOCKWORK.3');
  assert.equal(canonNotation('CLK.B'), 'CLK.B');
  assert.equal(canonNotation('CLOCKWORK.3'), 'CLOCKWORK.3');
  assert.equal(canonNotation('DFLIP N'), 'DFLIP N');
  assert.equal(canonNotation('DFLIP 1'), 'DFLIP.1');
});

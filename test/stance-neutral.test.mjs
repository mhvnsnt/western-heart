// Stance + neutral rows (docs/proof/moveset-sweep-20261028/r17-core8-failing.json):
// Pantera t7.king_158 'JGS, N' (name '*', damage 0, hit level '-') is a stance row with
// no button: the sweep's parse() already treats N (stick at neutral) as a direction
// step, so canonicalising the leading-stance-comma form to 'JGS.N' reads as
// motion-only — the sweep's own movement class for buttonless inputs (the same
// taxonomy as the WALL. rows in #1239), not a failure and not a witnessed pass.
// Residual, stated plainly: the sweep moves king_158 from the failing list to
// movement; entering Jaguar Step itself is not witnessed by this chunk.
// Deliberately NOT covered: Dio's 'DFLIP N' (space form, Hyakkigozan, 23 dmg / low /
// KND) is a real strike whose entry input is not established, so it stays open —
// this rule touches the comma form only, and the test below pins that exclusion.
// This test reads the REAL sweep page source and reconstructs its parse(), so a
// parse change that stops treating N as a direction step fails the test.
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

test('stance-comma neutral canonicalises to a dotted neutral step', () => {
  assert.equal(canonNotation('JGS, N'), 'JGS.N');
});

test('the real sweep parse reads the dotted neutral step as motion-only (movement, not a failure)', () => {
  const parse = realParse();
  const p = parse('JGS.N');
  assert.equal(p.err, undefined);
  assert.deepEqual(p.motionOnly, ['N']);
  assert.equal(p.pre, 'JGS');
  const old = parse('JGS,N');
  assert.ok(old.err, 'the old comma form must still parse-ERR without the fix');
});

test('guards: neighbouring stance-comma and space forms unchanged, and DFLIP N stays open', () => {
  assert.equal(canonNotation('JGS, 1'), 'JGS.1');
  assert.equal(canonNotation('JGS, 1+4'), 'JGS.1+4');
  assert.equal(canonNotation('JGS* (3 spins), 1'), 'JGS.1');
  assert.equal(canonNotation('DFLIP 1'), 'DFLIP.1');
  assert.equal(canonNotation('DFLIP N'), 'DFLIP N');
  assert.equal(canonNotation('SS, N'), 'SS,N');
});

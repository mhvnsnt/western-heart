// Pantera approach-crouching sweep rows (docs/proof/moveset-sweep-20261028/r17-core8-failing.json):
// t7.king_229 'Approach crouching enemy... d+1+3' (Iron Lariat), t7.king_230 '... d+2+4'
// (V Driver), t7.king_268 '... d/f, D/F+1+3 (or 2+4)' (Reverse Special Stretch Bomb).
// Canon used to leave the prose untouched, so the sweep parse-ERRed before any setup ran.
// These are Tekken crouch throws: the honest treatment is a setup, NOT an n/a — a
// crouching foe is a state the sweep already plays (condSetup T3 condition rows, the
// hit-word crouch branch), unlike the ground-orientation state behind the enemy-on-back
// n/a. Canon maps the prose to a CROUCHFOE. prefix and the sweep's setup() plays the
// stated situation (foe crouching, close). Residual, stated plainly: this is mechanism
// proof (canon + setup + parse path), not a witnessed full-fight pass — the next sweep
// attempts these rows against a crouching foe at close range, and whether each fires
// and connects there is what that sweep reports. Timing rows ('Time with enemy...',
// t7.king_295-297) and the wall-stun row ('During enemy wall stun...', t7.king_247)
// are deliberately NOT covered: they need a timed-opponent-attack setup and a
// wall-stun state respectively, different chunks.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { canonNotation } from '../game/js/movesets.js';

const pageSrc = readFileSync(new URL('./e2e/moveset-sweep.page.js', import.meta.url), 'utf8');

test('approach-crouching prose canonicalises to CROUCHFOE.', () => {
  assert.equal(canonNotation('Approach crouching enemy... d+1+3'), 'CROUCHFOE.d+1+3');
  assert.equal(canonNotation('Approach crouching enemy... d+2+4'), 'CROUCHFOE.d+2+4');
  assert.equal(canonNotation('Approach crouching enemy... d/f, D/F+1+3 (or 2+4)'), 'CROUCHFOE.d/f,D/F+1+3');
});

test('sweep setup() gains a CROUCHFOE case that crouches the foe and closes in', () => {
  const start = pageSrc.indexOf('function setup(pre, f)');
  assert.notEqual(start, -1, 'sweep page has no setup()');
  const end = pageSrc.indexOf('\n  }\n', start);
  const block = pageSrc.slice(start, end);
  const caseIdx = block.indexOf("case 'CROUCHFOE'");
  assert.notEqual(caseIdx, -1, 'no CROUCHFOE setup case');
  const caseBody = block.slice(caseIdx, block.indexOf('\n', caseIdx));
  assert.ok(caseBody.includes("o._enter('crouch')"), 'CROUCHFOE setup must crouch the foe');
  assert.ok(caseBody.includes('f.root.position.x = o.root.position.x - 0.7'), 'CROUCHFOE setup must close to the contactFirst spacing');
});

test('sweep plays the prefix setup before pressing the row', () => {
  const once = pageSrc.indexOf('const sweepOnce');
  assert.notEqual(once, -1, 'sweep page has no sweepOnce');
  const block = pageSrc.slice(once);
  const setupCall = block.indexOf('setup(P.pre, f)');
  const pressCall = block.indexOf('run(f, P, out)');
  assert.ok(setupCall !== -1 && pressCall !== -1 && setupCall < pressCall, 'prefix setup must run before the press inside sweepOnce');
});

test('guards: timing and wall-stun prose are untouched by the CROUCHFOE rule', () => {
  assert.equal(canonNotation('Time with enemy right punch... b+1+3'), 'Time with enemy right punch... b+1+3');
  assert.equal(canonNotation('Time with enemy left kick... b+2+4'), 'Time with enemy left kick... b+2+4');
  assert.equal(canonNotation('During enemy wall stun... f, hcf+1'), 'During enemy wall stun... f,hcf+1');
  assert.equal(canonNotation('b+2, 4 (only during hit from front)'), 'b+2,4 only during hit from front');
  assert.equal(canonNotation('CROUCHFOE.d+1+3'), 'CROUCHFOE.d+1+3');
});

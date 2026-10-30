// Pantera timing throws (docs/proof/moveset-sweep-20261028/r17-core8-failing.json):
// t7.king_295 'Time with enemy right punch... b+1+3' (Arm Whip), t7.king_296
// 'Time with enemy left kick... b+2+4' (Spinning Heel Hold), t7.king_297
// 'Time with enemy right kick... b+2+4' (Leg Screw). Canon used to leave the prose
// untouched, so the sweep parse-ERRed before any setup ran. These are Tekken reversal
// throws: the honest treatment is a setup, NOT an n/a — an attacking foe is a state
// the sweep already plays (condSetup's oppAttack starts foe attacks for T3 condition
// rows), unlike the ground-orientation state behind the enemy-on-back n/a, and NOT a
// canon strip, which would attempt reversal throws against a standing, non-attacking
// foe. Canon maps the prose to a TIMERP/TIMELK/TIMERK prefix and the sweep's setup()
// closes to the 0.7 m contactFirst spacing and starts the foe attacking with the
// matching limb (2 = right punch, 3 = left kick, 4 = right kick, per the Tekken button
// map in movesets.js). Residual, stated plainly: this is mechanism proof (canon +
// setup + parse path), not a witnessed full-fight pass — the next sweep attempts
// these rows against an attacking foe, and whether each fires and connects there, and
// whether the engine resolves the reversal catch at all, is what that sweep reports.
// king_110, king_150, king_158, king_186 are deliberately NOT covered: different
// chunks. The wall-stun row t7.king_247 is now covered by the wall-stun chunk
// (WALLSTUN. canon + sweep setup); the guard test below was updated in that chunk
// to assert the new mapping.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { canonNotation } from '../game/js/movesets.js';

const pageSrc = readFileSync(new URL('./e2e/moveset-sweep.page.js', import.meta.url), 'utf8');

test('timing prose canonicalises to TIMERP/TIMELK/TIMERK prefixes', () => {
  assert.equal(canonNotation('Time with enemy right punch... b+1+3'), 'TIMERP.b+1+3');
  assert.equal(canonNotation('Time with enemy left kick... b+2+4'), 'TIMELK.b+2+4');
  assert.equal(canonNotation('Time with enemy right kick... b+2+4'), 'TIMERK.b+2+4');
});

test('sweep setup() gains TIMERP/TIMELK/TIMERK cases that start the matching foe attack at close range', () => {
  const start = pageSrc.indexOf('function setup(pre, f)');
  assert.notEqual(start, -1, 'sweep page has no setup()');
  const caseIdx = pageSrc.indexOf("case 'TIMERP'", start);
  assert.notEqual(caseIdx, -1, 'no TIMERP setup case');
  const airIdx = pageSrc.indexOf("case 'AIR'", caseIdx);
  assert.notEqual(airIdx, -1, 'AIR case must follow the timing cases');
  const block = pageSrc.slice(caseIdx, airIdx);
  assert.ok(block.includes("case 'TIMELK'") && block.includes("case 'TIMERK'"), 'all three timing cases must exist');
  assert.ok(block.includes("pre === 'TIMERP' ? '2'"), 'right punch must map to button 2');
  assert.ok(block.includes("pre === 'TIMELK' ? '3'"), 'left kick must map to button 3');
  assert.ok(block.includes("const mv = pre === 'TIMERP' ? '2' : pre === 'TIMELK' ? '3' : '4'"), 'right kick (TIMERK) must be the fallback button 4');
  assert.ok(block.includes('f.root.position.x = o.root.position.x - 0.7'), 'timing setup must close to the contactFirst spacing');
  assert.ok(block.includes("o._enter('idle')"), 'timing setup must reset the foe before starting its attack');
  assert.ok(block.includes('o.tryAttack(mv)'), 'timing setup must start the foe attacking with the matching limb');
  assert.ok(block.includes("o.state === 'attack'"), 'timing setup must check the foe attack actually started');
});

test('sweep plays the prefix setup before pressing the row', () => {
  const once = pageSrc.indexOf('const sweepOnce');
  assert.notEqual(once, -1, 'sweep page has no sweepOnce');
  const block = pageSrc.slice(once);
  const setupCall = block.indexOf('setup(P.pre, f)');
  const pressCall = block.indexOf('run(f, P, out)');
  assert.ok(setupCall !== -1 && pressCall !== -1 && setupCall < pressCall, 'prefix setup must run before the press inside sweepOnce');
});

test('guards: wall-stun prose now maps to WALLSTUN. (wall-stun chunk); approach-crouch and generic-attack prose are untouched', () => {
  assert.equal(canonNotation('During enemy wall stun... f, hcf+1'), 'WALLSTUN.f,hcf+1');
  assert.equal(canonNotation('Approach crouching enemy... d+1+3'), 'CROUCHFOE.d+1+3');
  assert.equal(canonNotation('Time with enemy attack... b+1+3 (or b+2+4)'), 'Time with enemy attack... b+1+3');
  assert.equal(canonNotation('TIMERP.b+1+3'), 'TIMERP.b+1+3');
  assert.equal(canonNotation('TIMELK.b+2+4'), 'TIMELK.b+2+4');
});

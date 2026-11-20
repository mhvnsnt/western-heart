// Pantera wall-stun sweep row (docs/proof/moveset-sweep-20261028/r17-core8-failing.json):
// t7.king_247 'During enemy wall stun... f, hcf+1' (Shining Torpedo). Canon used to
// leave the prose untouched, so the sweep parse-ERRed before any setup ran. This is a
// Tekken wall-splat throw: the honest treatment is a setup, NOT an n/a — the engine
// HAS the state (fighter.js 'wallsplat', entered at the arena wall with the
// WALL_SPLAT_STUN window of 0.55 s), the way the sweep already plays a crouching foe
// (CROUCHFOE) and an attacking foe (TIMER*) — and NOT a canon strip, which would
// attempt a wall throw against a standing foe. Canon maps the prose to a WALLSTUN.
// prefix and the sweep's setup() plays the stated situation (foe wall-splatted with
// the full stun window, attacker closed to the 0.7 m contactFirst spacing).
// Residual, stated plainly: this is mechanism proof (canon + setup + parse path),
// not a witnessed full-fight pass — the next sweep attempts this row against a
// wall-splatted foe, and whether the throw reaches exec there is what that sweep
// reports.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { canonNotation } from '../game/js/movesets.js';

const pageSrc = readFileSync(new URL('./e2e/moveset-sweep.page.js', import.meta.url), 'utf8');

test('wall-stun prose canonicalises to WALLSTUN.', () => {
  assert.equal(canonNotation('During enemy wall stun... f, hcf+1'), 'WALLSTUN.f,hcf+1');
  assert.equal(canonNotation('WALLSTUN.f,hcf+1'), 'WALLSTUN.f,hcf+1');
});

test('sweep setup() gains a WALLSTUN case that wall-splats the foe with the full stun window and closes in', () => {
  const start = pageSrc.indexOf('function setup(pre, f)');
  assert.notEqual(start, -1, 'sweep page has no setup()');
  const caseIdx = pageSrc.indexOf("case 'WALLSTUN'", start);
  assert.notEqual(caseIdx, -1, 'no WALLSTUN setup case');
  const airIdx = pageSrc.indexOf("case 'AIR'", caseIdx);
  assert.notEqual(airIdx, -1, 'AIR case must follow the WALLSTUN case');
  const block = pageSrc.slice(caseIdx, airIdx);
  assert.ok(block.includes("o._enter('wallsplat')"), 'WALLSTUN setup must put the foe in the wallsplat state');
  assert.ok(block.includes('o.stun = 0.55'), 'WALLSTUN setup must give the foe the full WALL_SPLAT_STUN window (0.55 s)');
  assert.ok(block.includes('f.root.position.x = o.root.position.x - 0.7'), 'WALLSTUN setup must close to the contactFirst spacing');
});

test('sweep plays the prefix setup before pressing the row', () => {
  const once = pageSrc.indexOf('const sweepOnce');
  assert.notEqual(once, -1, 'sweep page has no sweepOnce');
  const block = pageSrc.slice(once);
  const setupCall = block.indexOf('setup(P.pre, f)');
  const pressCall = block.indexOf('run(f, P, out)');
  assert.ok(setupCall !== -1 && pressCall !== -1 && setupCall < pressCall, 'prefix setup must run before the press inside sweepOnce');
});

test('guards: approach-crouch, timing, and generic-attack prose are untouched by the WALLSTUN rule', () => {
  assert.equal(canonNotation('Approach crouching enemy... d+1+3'), 'CROUCHFOE.d+1+3');
  assert.equal(canonNotation('Time with enemy right punch... b+1+3'), 'TIMERP.b+1+3');
  assert.equal(canonNotation('Time with enemy attack... b+1+3 (or b+2+4)'), 'Time with enemy attack... b+1+3');
});

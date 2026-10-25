/* fight-camera-level.test.mjs — Fight camera follows the fighting level.
 *
 * Owner report 2026-10-25: after a Floor Break or Balcony Break the
 * camera stayed up top while the fight continued on the level below.
 * Root cause (game/js/scene.js): vertical framing applied the 0.45 /
 * 0.25 tracking factors to the fighters' ABSOLUTE root Y, which
 * already includes the ground offset — so after a 6 m drop the camera
 * sat 3.3 m too high and the look target 4.5 m too high, and the
 * fighters fell out of frame below. The fix (game/js/fight-camera-math.js)
 * anchors to the current ground and tracks only height above it.
 *
 * Run: node --test game/tests/fight-camera-level.test.mjs (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { fightCameraY } from '../js/fight-camera-math.js';

const GAME = join(dirname(fileURLToPath(import.meta.url)), '..');
const close = (a, b) => Math.abs(a - b) < 1e-9;
/* The old scene.js formula, for identity checks on the upper level. */
const oldFormula = (maxY) => ({ baseY: 1.75 + maxY * 0.45, lookY: 1.0 + maxY * 0.25 });

test('upper level standing: camera 1.75, look 1.0 (identical to old formula)', () => {
  const got = fightCameraY(0, 0);
  assert.ok(close(got.baseY, 1.75) && close(got.lookY, 1.0));
  const old = oldFormula(0);
  assert.ok(close(got.baseY, old.baseY) && close(got.lookY, old.lookY));
});

test('upper level jump 2 m: tracks airborne height only (identical to old formula)', () => {
  const got = fightCameraY(0, 2);
  assert.ok(close(got.baseY, 2.65) && close(got.lookY, 1.5));
  const old = oldFormula(2);
  assert.ok(close(got.baseY, old.baseY) && close(got.lookY, old.lookY));
});

test('upper level launch 3.5 m: identical to old formula', () => {
  const got = fightCameraY(0, 3.5);
  assert.ok(close(got.baseY, 3.325) && close(got.lookY, 1.875));
  const old = oldFormula(3.5);
  assert.ok(close(got.baseY, old.baseY) && close(got.lookY, old.lookY));
});

test('floor break, depth 6, fighters standing below: camera drops to the new level', () => {
  const got = fightCameraY(-6, -6);
  assert.ok(close(got.baseY, -4.25) && close(got.lookY, -5.0));
  // The bug: the old formula left the camera up top (-0.95 / -0.5).
  const old = oldFormula(-6);
  assert.ok(close(old.baseY, -0.95) && close(old.lookY, -0.5));
  assert.ok(Math.abs(got.baseY - old.baseY) > 3 && Math.abs(got.lookY - old.lookY) > 4);
});

test('balcony break, depth 6, fighters standing below: same drop as floor break', () => {
  const got = fightCameraY(-6, -6);
  assert.ok(close(got.baseY, -4.25) && close(got.lookY, -5.0));
});

test('mid-fall after a 6 m break: camera descends with the fighters', () => {
  // Fighters halfway down (root -2, new ground -6): 4 m above the new ground.
  const got = fightCameraY(-6, -2);
  assert.ok(close(got.baseY, -2.45) && close(got.lookY, -4.0));
});

test('jump on the lower level: ground anchor + airborne tracking', () => {
  // 2 m jump above the -6 ground: camera -3.35, look -4.5.
  const got = fightCameraY(-6, -4);
  assert.ok(close(got.baseY, -3.35) && close(got.lookY, -4.5));
});

test('shallow break, depth 2.5: drop follows the declared depth, not a hardcoded 6', () => {
  const got = fightCameraY(-2.5, -2.5);
  assert.ok(close(got.baseY, -0.75) && close(got.lookY, -1.5));
});

test('wall break: groundY stays 0, framing identical to old formula', () => {
  const got = fightCameraY(0, 1.2);
  const old = oldFormula(1.2);
  assert.ok(close(got.baseY, old.baseY) && close(got.lookY, old.lookY));
});

test('below-ground guard: a root Y under the ground never drags the camera down', () => {
  const got = fightCameraY(0, -0.5);
  assert.ok(close(got.baseY, 1.75) && close(got.lookY, 1.0));
});

test('non-finite inputs default to the upper-level stance', () => {
  const got = fightCameraY(NaN, NaN);
  assert.ok(close(got.baseY, 1.75) && close(got.lookY, 1.0));
  const undef = fightCameraY(undefined, undefined);
  assert.ok(close(undef.baseY, 1.75) && close(undef.lookY, 1.0));
});

test('wiring: scene.js uses fightCameraY with the groundY parameter', () => {
  const src = readFileSync(join(GAME, 'js', 'scene.js'), 'utf8');
  assert.ok(src.includes("from './fight-camera-math.js'"), 'scene.js imports fight-camera-math');
  assert.ok(src.includes('fightCameraY(groundY, maxY)'), 'scene.js calls fightCameraY(groundY, maxY)');
  assert.ok(src.includes('update(dt, fighterA, fighterB, groundY = 0)'), 'update() takes groundY');
});

test('wiring: game.js passes stageBreaks.groundY to arena.update', () => {
  const src = readFileSync(join(GAME, 'js', 'game.js'), 'utf8');
  assert.ok(src.includes('this.stageBreaks ? this.stageBreaks.groundY : 0'),
    'game.js passes the live fighting ground to the camera');
});

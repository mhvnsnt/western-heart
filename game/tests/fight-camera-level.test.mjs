/* fight-camera-level.test.mjs — Fight camera follows the fighting level
 * AND stays inside arena walls at edges (owner t374u 2026-11-05).
 *
 * Run: node --test game/tests/fight-camera-level.test.mjs (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  fightCameraY,
  fightCameraDolly,
  fightCameraCenterX,
  FIGHT_CAM_MAX_DIST,
  FIGHT_CAM_MIN_DIST_LANDSCAPE,
} from '../js/fight-camera-math.js';

const GAME = join(dirname(fileURLToPath(import.meta.url)), '..');
const close = (a, b) => Math.abs(a - b) < 1e-9;
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
});

test('upper level launch 3.5 m: identical to old formula', () => {
  const got = fightCameraY(0, 3.5);
  assert.ok(close(got.baseY, 3.325) && close(got.lookY, 1.875));
});

test('floor break, depth 6, fighters standing below: camera drops to the new level', () => {
  const got = fightCameraY(-6, -6);
  assert.ok(close(got.baseY, -4.25) && close(got.lookY, -5.0));
  const old = oldFormula(-6);
  assert.ok(Math.abs(got.baseY - old.baseY) > 3 && Math.abs(got.lookY - old.lookY) > 4);
});

test('balcony break, depth 6, fighters standing below: same drop as floor break', () => {
  const got = fightCameraY(-6, -6);
  assert.ok(close(got.baseY, -4.25) && close(got.lookY, -5.0));
});

test('mid-fall after a 6 m break: camera descends with the fighters', () => {
  const got = fightCameraY(-6, -2);
  assert.ok(close(got.baseY, -2.45) && close(got.lookY, -4.0));
});

test('jump on the lower level: ground anchor + airborne tracking', () => {
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
});

test('landscape close span: dolly uses min 7m, not the old forced 10.5', () => {
  const got = fightCameraDolly({ span: 4.5, aspect: 16 / 9, baseFov: 45 });
  assert.ok(got.dist >= FIGHT_CAM_MIN_DIST_LANDSCAPE - 1e-9);
  assert.ok(got.dist < 10.5, `landscape close should be under wall line, got ${got.dist}`);
  assert.equal(got.clamped, false);
});

test('wide span clamps to maxDist and widens FOV (landscape)', () => {
  const got = fightCameraDolly({ span: 16, aspect: 16 / 9, baseFov: 45, maxDist: FIGHT_CAM_MAX_DIST });
  assert.ok(got.clamped);
  assert.ok(close(got.dist, FIGHT_CAM_MAX_DIST));
  assert.ok(got.fov > 45 && got.fov <= 80);
});

test('portrait still caps at maxDist and widens FOV', () => {
  const got = fightCameraDolly({ span: 8, aspect: 9 / 16, baseFov: 45 });
  assert.ok(got.dist <= FIGHT_CAM_MAX_DIST + 1e-9);
  assert.ok(got.clamped);
});

test('fightCameraCenterX soft-clamps near walls', () => {
  assert.ok(close(fightCameraCenterX(0, 8.4, 1.2), 0));
  assert.ok(fightCameraCenterX(8.4, 8.4, 1.2) <= 8.4 - 1.2 + 1e-9);
  assert.ok(fightCameraCenterX(-99, 8.4, 1.2) >= -(8.4 - 1.2) - 1e-9);
});

test('wiring: scene.js uses fightCameraY + fightCameraDolly', () => {
  const src = readFileSync(join(GAME, 'js', 'scene.js'), 'utf8');
  assert.ok(src.includes("from './fight-camera-math.js'"), 'scene.js imports fight-camera-math');
  assert.ok(src.includes('fightCameraY(groundY, maxY)'), 'scene.js calls fightCameraY(groundY, maxY)');
  assert.ok(src.includes('fightCameraDolly'), 'scene.js calls fightCameraDolly');
  assert.ok(src.includes('update(dt, fighterA, fighterB, groundY = 0)'), 'update() takes groundY');
});

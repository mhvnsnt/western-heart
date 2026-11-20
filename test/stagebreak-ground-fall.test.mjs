/* stagebreak-ground-fall.test.mjs — Grounded fighter falls when the
 * fighting level drops (floor / balcony break).
 *
 * Owner playtest 2026-10-30: after a Floor Break or Balcony Break the
 * camera got "stuck in the mid" and did not go all the way down.
 * Root cause was NOT the camera: game/js/stagebreaks.js _breakFloor /
 * _breakBalcony lower GROUND_Y without touching fighter state, and
 * game/js/fighter.js _physics applied gravity only to airborne
 * fighters while the ground clamp fired only from below — so a
 * grounded attacker standing in recovery floated at the old level
 * forever while the launched defender landed below, and the camera
 * (correctly framing maxY of both roots) parked mid at
 * fightCameraY(-6, 0) = (-1.55, -3.5).
 *
 * Fix (game/js/fighter.js _physics, primary route): a grounded
 * fighter whose feet are above the current ground is released to
 * gravity, so it falls and the existing clamp re-grounds it on
 * landing. fight-camera-math.js is untouched (it was already
 * correct); game/tests/fight-camera-level.test.mjs covers only the
 * pure camera formula and assumes both roots reach the ground, so
 * it alone is NOT proof of this fix — this file drives _physics.
 *
 * Pattern follows test/attack-anim.test.mjs: node_game_env maps the
 * bare 'three' specifier to the vendored build, and fighters are
 * bare Fighter-prototype objects (no constructor, no models).
 * Run: node test/stagebreak-ground-fall.test.mjs (from repo root;
 * CI game-unit-tests runs every test/*.test.mjs this way).
 * Buttons: LP1/RP2/LK3/RK4.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const F = await import(join(ROOT, 'game/js/fighter.js'));
const { fightCameraY } = await import(join(ROOT, 'game/js/fight-camera-math.js'));

const DT = 1 / 60;
const close = (a, b) => Math.abs(a - b) < 1e-9;

function bareFighter(state, y, airborne) {
  const f = Object.create(F.Fighter.prototype);
  f.state = state;
  f.attackName = state === 'attack' ? 'jab' : null;
  f.vx = 0; f.vy = 0; f.vz = 0;
  f.onGround = !airborne;
  f.stun = 0; f.dead = false; f._cinematic = null; f._ssAlign = null;
  f._wallSplatArmed = false; f._throwPair = null; f.brawler = false;
  f._juggleG = 0; f._atkPlan = null; f._attackId = null; f.attack = null;
  f.root = { position: { x: 0, y, z: 0 } };
  f.blob = { position: {}, scale: { set() {} }, material: {} };
  return f;
}

function step(f, frames, opponent = null) {
  for (let i = 0; i < frames; i++) f._physics(DT, opponent);
}

test('grounded attacker in recovery falls to the new ground after a 6 m drop (not floats)', () => {
  F.setGroundY(0);
  const attacker = bareFighter('attack', 0, false);
  F.setGroundY(-6); // the break: _breakFloor / _breakBalcony lower the ground
  step(attacker, 180);
  assert.equal(attacker.root.position.y, -6);
  assert.equal(attacker.onGround, true);
  // And it stays grounded on the new level (epsilon guard: no re-release).
  step(attacker, 120);
  assert.equal(attacker.root.position.y, -6);
  assert.equal(attacker.onGround, true);
  F.setGroundY(0);
});

test('both fighters landed: camera pair is (-4.25, -5.0)', () => {
  F.setGroundY(0);
  const attacker = bareFighter('attack', 0, false);
  const defender = bareFighter('idle', 3, true); // launched by the break move
  F.setGroundY(-6);
  step(attacker, 180);
  step(defender, 180);
  assert.equal(attacker.root.position.y, -6);
  assert.equal(defender.root.position.y, -6);
  const maxY = Math.max(attacker.root.position.y, defender.root.position.y);
  const cam = fightCameraY(-6, maxY);
  assert.ok(close(cam.baseY, -4.25) && close(cam.lookY, -5.0));
  F.setGroundY(0);
});

test('camera descends past the old stuck-mid value during the fall', () => {
  F.setGroundY(0);
  const attacker = bareFighter('attack', 0, false);
  F.setGroundY(-6);
  step(attacker, 30);
  assert.ok(attacker.root.position.y < 0, 'fighter leaves the old level');
  const cam = fightCameraY(-6, attacker.root.position.y);
  assert.ok(cam.baseY < -1.55, 'camera passes the old stuck value -1.55');
  F.setGroundY(0);
});

test('no regression: ground unmoved, grounded fighter stays put', () => {
  F.setGroundY(0);
  const fighter = bareFighter('idle', 0, false);
  step(fighter, 60);
  assert.equal(fighter.root.position.y, 0);
  assert.equal(fighter.onGround, true);
  F.setGroundY(0);
});

test('throw execution excluded: positions stay driven by _tickState, not physics', () => {
  F.setGroundY(0);
  const fighter = bareFighter('throwExec', 0, false);
  F.setGroundY(-6);
  step(fighter, 60);
  assert.equal(fighter.root.position.y, 0);
  assert.equal(fighter.onGround, true);
  F.setGroundY(0);
});

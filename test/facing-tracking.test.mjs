// QA 2026-10-23: after a sidestep fighters must re-align and face each other,
// so strikes connect again (owner: "targeting is off").
import { test } from 'node:test';
import assert from 'node:assert';
import { readFileSync } from 'node:fs';
import { inReach } from '../game/js/combat-core.js';
const src = readFileSync(new URL('../game/js/fighter.js', import.meta.url), 'utf8');
test('fighter yaw tracks opponent in 3D', () => {
  assert.match(src, /this\._faceYaw = Math\.atan2\(opponent\.root\.position\.x/);
  assert.match(src, /lean\.rotation\.y = \(typeof this\._faceYaw === 'number'\)/);
});
test('z re-aligns after sidestep so a jab connects again', () => {
  const m = src.match(/position\.z \*= Math\.pow\(([\d.]+), dt\)/); assert.ok(m);
  let z = -1.9;
  assert.equal(inReach(0, z, 1, 1.3, 0, { limb: 'arm' }, '1'), false, 'off-axis right after step');
  for (let i = 0; i < 60; i++) z *= Math.pow(+m[1], 1 / 60);
  assert.ok(Math.abs(z) < 0.75);
  assert.equal(inReach(0, z, 1, 1.3, 0, { limb: 'arm' }, '1'), true);
});

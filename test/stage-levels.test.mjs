// Stage levels (Lane 5, 2026-10-24). Node, no browser, no THREE.
// Run: node test/stage-levels.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const M = await import(join(ROOT, 'game', 'js', 'stage-levels.js'));

const shrine = {
  id: 'shrine', dims: { width: 16.8, depth: 6.0, wallDistance: 8.4 },
  breakables: [{ type: 'floor', x: 0, z: 0, r: 2.6, depth: 6 }],
};
const helix = {
  id: 'helix-palace', dims: { width: 16.8, depth: 6.0, wallDistance: 8.4 },
  breakables: [{ type: 'balcony', x: 5.5, z: 0, r: 2.2, w: 4.5, depth: 6 }],
};
const plain = { id: 'tong-nou', dims: { width: 16.8, depth: 6.0, wallDistance: 8.4 } };
const noWall = {
  id: 'cage', dims: { width: 16.8, depth: 6.0, wallDistance: 8.4 }, noWallBreak: true,
};

test('upper level mirrors the def, wall-broken extends by WALL_BREAK_EXTEND', () => {
  const levels = M.resolveStageLevels(plain);
  assert.equal(levels[0].id, 'upper');
  assert.equal(levels[0].groundY, 0);
  assert.equal(levels[0].wallDistance, 8.4);
  assert.equal(levels[1].id, 'wall-broken');
  assert.equal(levels[1].wallDistance, 8.4 + M.WALL_BREAK_EXTEND);
  assert.equal(M.WALL_BREAK_EXTEND, 4.5);
});

test('floor breakable adds a lower level at -depth', () => {
  const levels = M.resolveStageLevels(shrine);
  const lower = levels.find((l) => l.via === 'floor');
  assert.ok(lower);
  assert.equal(lower.groundY, -6);
  assert.deepEqual(lower.zone, { x: 0, z: 0, r: 2.6 });
  assert.equal(M.levelAfterBreak(shrine, { type: 'floor', x: 0 }).groundY, -6);
});

test('balcony breakable adds a lower level at -depth', () => {
  const levels = M.resolveStageLevels(helix);
  const lower = levels.find((l) => l.via === 'balcony');
  assert.ok(lower);
  assert.equal(lower.groundY, -6);
  assert.equal(lower.zone.w, 4.5);
  assert.equal(M.levelAfterBreak(helix, { type: 'balcony', x: 5.5 }).via, 'balcony');
});

test('noWallBreak stages have no wall-broken level; unknown breaks resolve null', () => {
  assert.equal(M.resolveStageLevels(noWall).some((l) => l.via === 'wall'), false);
  assert.equal(M.levelAfterBreak(noWall, { type: 'wall' }), null);
  assert.equal(M.levelAfterBreak(plain, { type: 'ceiling' }), null);
  assert.equal(M.levelAfterBreak(plain, null), null);
  assert.deepEqual(M.resolveStageLevels(null), []);
  assert.deepEqual(M.resolveStageLevels({ id: 'x' }), []);
});

test('composeLevel combines a drop with a broken wall', () => {
  assert.deepEqual(M.composeLevel(shrine, [{ type: 'floor', depth: 6 }]), { groundY: -6, wallDistance: 8.4 });
  assert.deepEqual(
    M.composeLevel(shrine, [{ type: 'floor', depth: 6 }, { type: 'wall' }]),
    { groundY: -6, wallDistance: 8.4 + M.WALL_BREAK_EXTEND },
  );
  assert.deepEqual(M.composeLevel(plain, []), { groundY: 0, wallDistance: 8.4 });
});

/* destruction.test.mjs — voro++-based procedural fracture (2026-10-23).
 *
 * Covers the pure math in game/js/destruction.js: Voronoi cell
 * computation (voro++ cell-by-plane-cuts algorithm), Lloyd relaxation,
 * fracture determinism / area conservation, and DestructionSystem
 * damage accumulation + shard ballistics. No THREE, no DOM.
 *
 * Run: node --test game/tests/destruction.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const d = await import(join(here, '..', 'js', 'destruction.js'));

const BOUNDS = { x0: -2, y0: -1.5, x1: 2, y1: 1.5 };

function rngSeq() { // deterministic stream for tests
  let s = 12345;
  return () => {
    s = (s * 1103515245 + 12345) & 0x7fffffff;
    return s / 0x7fffffff;
  };
}

test('mulberry32 is deterministic', () => {
  const a = d.mulberry32(7), b = d.mulberry32(7);
  for (let i = 0; i < 10; i++) assert.equal(a(), b());
  const c = d.mulberry32(8);
  assert.notEqual(a(), c()); // different seed, different stream (overwhelmingly likely)
});

test('clipHalfPlane keeps the correct side', () => {
  const square = [[0, 0], [2, 0], [2, 2], [0, 2]];
  const kept = d.clipHalfPlane(square, 1, 0, 1); // x <= 1
  assert.ok(kept.length >= 3);
  for (const [x] of kept) assert.ok(x <= 1 + 1e-9);
  assert.equal(d.polygonArea(kept).toFixed(6), (2).toFixed(6)); // half the square
});

test('voronoiCells: every cell contains its seed and tiles the bounds', () => {
  const rand = d.mulberry32(42);
  const seeds = Array.from({ length: 12 }, () => ({
    x: BOUNDS.x0 + rand() * (BOUNDS.x1 - BOUNDS.x0),
    y: BOUNDS.y0 + rand() * (BOUNDS.y1 - BOUNDS.y0),
  }));
  const cells = d.voronoiCells(BOUNDS, seeds);
  assert.equal(cells.length, 12);
  let total = 0;
  for (let i = 0; i < cells.length; i++) {
    const { seed, poly } = cells[i];
    assert.ok(poly.length >= 3, `cell ${i} degenerate`);
    total += d.polygonArea(poly);
    // seed must be the closest seed to each of its own cell's vertices
    for (const [x, y] of poly) {
      const mine = Math.hypot(x - seed.x, y - seed.y);
      for (let j = 0; j < seeds.length; j++) {
        if (j === i) continue;
        const theirs = Math.hypot(x - seeds[j].x, y - seeds[j].y);
        assert.ok(mine <= theirs + 1e-6, `cell ${i} vertex closer to seed ${j}`);
      }
    }
    // all vertices inside bounds
    for (const [x, y] of poly) {
      assert.ok(x >= BOUNDS.x0 - 1e-9 && x <= BOUNDS.x1 + 1e-9);
      assert.ok(y >= BOUNDS.y0 - 1e-9 && y <= BOUNDS.y1 + 1e-9);
    }
  }
  const boundsArea = (BOUNDS.x1 - BOUNDS.x0) * (BOUNDS.y1 - BOUNDS.y0);
  assert.ok(Math.abs(total - boundsArea) / boundsArea < 0.01, `area ${total} vs ${boundsArea}`);
});

test('lloydRelax keeps seeds in bounds and converges-ish', () => {
  const rand = d.mulberry32(9);
  const seeds = Array.from({ length: 8 }, () => ({
    x: BOUNDS.x0 + rand() * 4, y: BOUNDS.y0 + rand() * 3,
  }));
  const out = d.lloydRelax(BOUNDS, seeds, 3);
  assert.equal(out.length, 8);
  for (const s of out) {
    assert.ok(s.x >= BOUNDS.x0 && s.x <= BOUNDS.x1);
    assert.ok(s.y >= BOUNDS.y0 && s.y <= BOUNDS.y1);
  }
});

test('fractureRect is deterministic for a fixed seed', () => {
  const opts = { w: 8, h: 3.4, cells: 24, impact: { x: 0.5, y: 0.2 }, seed: 1234 };
  const a = d.fractureRect(opts), b = d.fractureRect(opts);
  assert.equal(a.length, b.length);
  assert.ok(a.length > 0 && a.length <= 24);
  for (let i = 0; i < a.length; i++) {
    assert.equal(a[i].poly.length, b[i].poly.length);
    assert.equal(a[i].area.toFixed(9), b[i].area.toFixed(9));
  }
});

test('fractureRect conserves area and biases density at impact', () => {
  const shards = d.fractureRect({ w: 6, h: 4, cells: 20, impact: { x: 1, y: 0.5 }, seed: 99 });
  const total = shards.reduce((s, sh) => s + sh.area, 0);
  assert.ok(Math.abs(total - 24) / 24 < 0.02, `conserved area ${total}`);
  const near = shards.filter((sh) => sh.dist < 1.2);
  const far = shards.filter((sh) => sh.dist >= 1.2);
  const avg = (xs) => xs.reduce((s, sh) => s + sh.area, 0) / Math.max(1, xs.length);
  assert.ok(avg(near) < avg(far), 'shards near impact are smaller/denser');
});

test('DestructionSystem: damage accumulates, fracture fires once', () => {
  const sys = new d.DestructionSystem({ rng: rngSeq() });
  sys.registerSurface({ id: 'wall:-9', kind: 'wall', w: 10, h: 3.4, hp: 100, cells: 16, seed: 5 });
  let r = sys.damage('wall:-9', 40, { x: 0, y: 0 });
  assert.equal(r.fractured, false);
  assert.ok(Math.abs(r.progress - 0.4) < 1e-9);
  r = sys.damage('wall:-9', 30, { x: 0, y: 0 });
  assert.equal(r.fractured, false);
  r = sys.damage('wall:-9', 30, { x: 1, y: 0.5 });
  assert.equal(r.fractured, true);
  assert.equal(r.progress, 1);
  assert.ok(r.shards.length > 0 && r.shards.length <= 16);
  assert.equal(sys.fractureCount, 1);
  assert.equal(sys.lastFracture.surfaceId, 'wall:-9');
  // second hit after fracture: no double fracture
  r = sys.damage('wall:-9', 500, { x: 0, y: 0 });
  assert.equal(r.fractured, false);
  assert.equal(sys.fractureCount, 1);
  // unknown surface: safe no-op
  r = sys.damage('nope', 999);
  assert.equal(r.fractured, false);
});

test('DestructionSystem: shards fly from impact, fall, rest, and die', () => {
  const sys = new d.DestructionSystem({ rng: rngSeq() });
  sys.registerSurface({ id: 'w', kind: 'wall', w: 8, h: 3.4, hp: 10, cells: 12, seed: 5 });
  const { shards } = sys.damage('w', 10, { x: 2, y: 0 });
  assert.ok(shards.length > 0);
  const y0 = shards.map((s) => s.pos.y);
  // step: gravity acts — airborne shards gain downward velocity, life decays
  const life0 = shards[0].life;
  for (let i = 0; i < 120; i++) sys.step(1 / 60);
  const s0 = shards[0];
  assert.ok(s0.life < life0, 'life decays');
  const airborne = shards.filter((s) => !s.settled && s.life > 0);
  if (airborne.length) {
    const avgVy = airborne.reduce((a, s) => a + s.vel.y, 0) / airborne.length;
    assert.ok(avgVy < 2, `airborne shards slow their rise/fall (avgVy=${avgVy.toFixed(2)})`);
  }
  for (const s of shards) assert.ok(s.pos.y >= -1e-6, 'no shard below the rest plane yet');
  // long enough: everything settles at rest plane and live list drains
  for (let i = 0; i < 600; i++) sys.step(1 / 60);
  for (const s of shards) {
    assert.ok(s.pos.y >= -1e-6, 'no shard below the rest plane');
    assert.ok(s.life <= 0 || s.settled, 'shard settled or dead');
  }
  assert.equal(sys.live.length, 0, 'dead shards pruned from live list');
  sys.reset();
  assert.equal(sys.surfaces.size, 0);
});

test('DestructionSystem: floor shards fall along local -Z to the lower level', () => {
  const sys = new d.DestructionSystem({ rng: rngSeq() });
  sys.registerSurface({ id: 'f', kind: 'floor', w: 5, h: 5, hp: 10, cells: 10, seed: 5, fallDepth: 6 });
  const { shards } = sys.damage('f', 10, { x: 0, y: 0 });
  assert.deepEqual(shards[0].gravity, { x: 0, y: 0, z: -d.GRAVITY });
  for (let i = 0; i < 600; i++) sys.step(1 / 60);
  for (const s of shards) assert.ok(s.pos.z >= -6 - 1e-6, 'floor shard rests at lower level');
});

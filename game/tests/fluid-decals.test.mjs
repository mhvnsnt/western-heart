/* fluid-decals.test.mjs — Track 3 (fluid dynamics) regression guards.
 *
 * Covers the pure cores of game/js/fx/fluid.js (FluidSim: burst budget,
 * droplet-breakup volume conservation, ground stick/bounce, fighter
 * coat+slide, viscosity damping, determinism) and game/js/fx/decals.js
 * (world<->UV mapping, deterministic splat blobs, stamp recording,
 * upload throttling, clear). The THREE/DOM layers are injected, so the
 * whole suite runs headless under node.
 *
 * Run: node --test game/tests/fluid-decals.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { FluidSim, PRESETS, FLUID, rng32 } from '../js/fx/fluid.js';
import { worldToUV, uvToWorld, computeSplat, mulberry32, SplatLayer } from '../js/fx/decals.js';

/* Minimal stub 2D context recording every call (no DOM needed). */
function fakeCtx() {
  const calls = [];
  return {
    calls,
    save() { calls.push('save'); },
    restore() { calls.push('restore'); },
    beginPath() { calls.push('beginPath'); },
    arc() { calls.push('arc'); },
    fill() { calls.push('fill'); },
    clearRect() { calls.push('clearRect'); },
    createRadialGradient() {
      calls.push('gradient');
      return { addColorStop() { calls.push('stop'); } };
    },
    set globalAlpha(v) { calls.push(`alpha=${v}`); },
    get globalAlpha() { return 1; },
    set fillStyle(v) { calls.push('fillStyle'); },
    get fillStyle() { return null; },
  };
}
function fakeCanvas(size = 256) {
  const ctx = fakeCtx();
  return { width: size, height: size, getContext: () => ctx, _ctx: ctx };
}

const RECT = { minX: -6, maxX: 6, minZ: -6, maxZ: 6 };

/* ---------------- FluidSim ---------------- */

test('burst spawns the requested count inside the particle budget', () => {
  const sim = new FluidSim({ seed: 7 });
  sim.burst(0, 1, 0, 0, 0.4, -1, { count: 120, seed: 7 });
  assert.equal(sim.activeCount, 120);
});

test('burst beyond budget recycles instead of growing unbounded', () => {
  const sim = new FluidSim({ seed: 7, maxParticles: 50 });
  sim.burst(0, 1, 0, 0, 0.4, -1, { count: 5000, seed: 7 });
  assert.ok(sim.activeCount <= 50, `active=${sim.activeCount}`);
});

test('droplet breakup conserves volume', () => {
  const sim = new FluidSim({ seed: 11 });
  const p = sim.spawn(0, 5, 0, 10, 0, 0, 0.03, 'blood', 5);
  const v0 = sim.totalVolume();
  assert.ok(v0 > 0);
  // one substep is enough: speed 10 > breakup threshold 7.0 for blood
  sim.substep([]);
  const v1 = sim.totalVolume();
  assert.ok(sim.activeCount > 1, 'expected the droplet to split');
  assert.ok(Math.abs(v1 - v0) / v0 < 1e-9, `vol drift ${(v1 - v0) / v0}`);
  void p;
});

test('slow ground impact sticks and emits a stamp', () => {
  const sim = new FluidSim({ seed: 3 });
  sim._rand = () => 0; // force adhesion
  const stamps = [];
  sim.onEvent = (e) => stamps.push(e);
  sim.spawn(0, 0.05, 0, 0, -0.3, 0, 0.02, 'blood', 5);
  for (let i = 0; i < 60 && !sim.particles[0].stuck; i++) sim.substep([]);
  assert.ok(sim.particles[0].stuck, 'droplet should stick to the ground');
  assert.ok(stamps.some((s) => s.type === 'stamp' && s.preset === 'blood'),
    'expected a stamp event on stick');
});

test('fast ground impact bounces instead of sticking', () => {
  const sim = new FluidSim({ seed: 3 });
  sim._rand = () => 0.999; // never adhere
  const stamps = [];
  sim.onEvent = (e) => stamps.push(e);
  sim.spawn(0, 0.1, 0, 0, -5, 0, 0.02, 'blood', 5);
  let bounced = false;
  for (let i = 0; i < 90; i++) {
    sim.substep([]);
    const p = sim.particles[0];
    if (!p) break;
    if (!p.stuck && p.vy > 0.1) { bounced = true; break; }
  }
  assert.ok(bounced, 'fast droplet should bounce off the ground');
  assert.ok(stamps.length > 0, 'bounce should still stamp a splat');
});

test('higher viscosity damps motion faster (variable-viscosity dial)', () => {
  const mk = (preset) => {
    const s = new FluidSim({ seed: 5 });
    s.burst(0, 1.2, 0, 0, 0.2, -1, { count: 40, seed: 42, preset, speed: 4 });
    return s;
  };
  const blood = mk('blood'), mud = mk('mud');
  for (let i = 0; i < 30; i++) { blood.substep([]); mud.substep([]); } // 0.25 s: still airborne
  const mean = (s) => s.particles.reduce((a, p) =>
    a + Math.hypot(p.vx, p.vy, p.vz), 0) / Math.max(1, s.particles.length);
  assert.ok(mean(blood) > 0.1 && mean(mud) > 0.1, 'particles should still be moving');
  assert.ok(mean(mud) < mean(blood),
    `mud ${mean(mud).toFixed(3)} should be slower than blood ${mean(blood).toFixed(3)}`);
});

test('same seed gives identical bursts (determinism)', () => {
  const mk = () => {
    const s = new FluidSim({ seed: 99 });
    s.burst(0, 1, 0, 0, 0.4, -1, { count: 30, seed: 99 });
    return s;
  };
  const a = mk(), b = mk();
  for (let i = 0; i < 30; i++) a.substep([]), b.substep([]);
  assert.equal(a.activeCount, b.activeCount);
  for (let i = 0; i < a.activeCount; i++) {
    assert.equal(a.particles[i].x, b.particles[i].x);
    assert.equal(a.particles[i].y, b.particles[i].y);
  }
});

test('slow impact on a fighter sphere coats, slides and drips', () => {
  const sim = new FluidSim({ seed: 21 });
  sim._rand = () => 0; // force adhesion
  const stamps = [];
  sim.onEvent = (e) => stamps.push(e);
  const collider = { cx: 0, cy: 1, cz: 0, cr: 0.4 };
  // off the crown: coats on the flank where tangential gravity is nonzero
  sim.spawn(0.25, 1.35, 0, 0, -0.2, 0, 0.02, 'blood', 5);
  for (let i = 0; i < 40 && !sim.particles[0].coat; i++) sim.substep([collider]);
  const p = sim.particles[0];
  assert.ok(p.coat, 'droplet should coat the fighter sphere');
  const y0 = p.y;
  for (let i = 0; i < 120; i++) sim.substep([collider]);
  assert.ok(Math.abs(sim.particles[0].y - y0) > 1e-4, 'coated droplet should slide');
  assert.ok(stamps.length > 0, 'sliding coat should stamp a drip trail');
});

test('update() with no particles is a safe no-op', () => {
  const sim = new FluidSim();
  assert.doesNotThrow(() => sim.update(0.016));
});

test('presets carry the viscosity dial and colors', () => {
  assert.ok(PRESETS.mud.visc > PRESETS.blood.visc);
  assert.ok(PRESETS.ink.visc < PRESETS.blood.visc);
  assert.deepEqual(PRESETS.blood.color, [0.42, 0.045, 0.06]);
  assert.ok(FLUID.MAX_PARTICLES <= 512, 'mobile budget cap');
});

test('rng32 is deterministic', () => {
  const a = rng32(123), b = rng32(123);
  for (let i = 0; i < 10; i++) assert.equal(a(), b());
});

/* ---------------- decals ---------------- */

test('worldToUV maps rect corners and center', () => {
  assert.deepEqual(worldToUV(-6, -6, RECT), { u: 0, v: 0 });
  assert.deepEqual(worldToUV(6, 6, RECT), { u: 1, v: 1 });
  assert.deepEqual(worldToUV(0, 0, RECT), { u: 0.5, v: 0.5 });
});

test('uvToWorld round-trips worldToUV', () => {
  const { u, v } = worldToUV(2.5, -3.25, RECT);
  const w = uvToWorld(u, v, RECT);
  assert.ok(Math.abs(w.x - 2.5) < 1e-9 && Math.abs(w.z + 3.25) < 1e-9);
});

test('computeSplat is deterministic and irregular', () => {
  const a = computeSplat(0.5, 0.5, 0.02, 777);
  const b = computeSplat(0.5, 0.5, 0.02, 777);
  assert.deepEqual(a, b);
  assert.ok(a.length >= 5, 'main blot + satellites + rim');
  const c = computeSplat(0.5, 0.5, 0.02, 778);
  assert.notDeepEqual(a, c);
});

test('SplatLayer stamps inside the rect and records canvas work', () => {
  const cv = fakeCanvas();
  const layer = new SplatLayer({ size: 256, rect: RECT, canvas: cv });
  assert.equal(layer.stamp(0, 0, 0.1, '#8f1d26', 0.85), true);
  assert.equal(layer.stamp(999, 999, 0.1, '#8f1d26'), false); // outside
  assert.equal(layer.stampCount, 1);
  assert.ok(cv._ctx.calls.includes('arc'), 'expected blob arcs drawn');
  assert.ok(cv._ctx.calls.includes('gradient'), 'expected radial gradients');
  assert.equal(layer.dirty, true);
});

test('uploadThrottled rate-limits GPU uploads', () => {
  const layer = new SplatLayer({ size: 64, rect: RECT, canvas: fakeCanvas(64) });
  layer.stamp(0, 0, 0.1, '#8f1d26');
  assert.equal(layer.uploadThrottled(1000), true);
  layer.stamp(1, 1, 0.1, '#8f1d26');
  assert.equal(layer.uploadThrottled(1050), false); // throttled
  assert.equal(layer.uploadThrottled(1200), true);  // after 150ms
});

test('clear() resets stamps and wipes the canvas', () => {
  const cv = fakeCanvas(64);
  const layer = new SplatLayer({ size: 64, rect: RECT, canvas: cv });
  layer.stamp(0, 0, 0.1, '#8f1d26');
  layer.clear();
  assert.equal(layer.stampCount, 0);
  assert.ok(cv._ctx.calls.includes('clearRect'));
});

test('mulberry32 is deterministic', () => {
  const a = mulberry32(5), b = mulberry32(5);
  for (let i = 0; i < 10; i++) assert.equal(a(), b());
});

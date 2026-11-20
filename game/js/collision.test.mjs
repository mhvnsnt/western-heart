// collision.test.mjs — verifies the shared collision core against
// analytic fixtures (no three.js needed: the core is three-free).
// Run: node --test game/js/collision.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  BodySDF, collideSphere, collideCapsule, applyContactFriction,
  SelfCollider, solveArticulatorCoupling,
} from './collision.js';

/* ---------- BodySDF vs an analytic sphere field ---------- */
function bakeSphereSDF() {
  const dims = [24, 24, 24], voxel = 0.02, origin = [-0.23, -0.23, -0.23];
  const data = new Int16Array(dims[0] * dims[1] * dims[2]);
  const quant = 0.0005, R = 0.15;
  let i = 0;
  for (let z = 0; z < dims[2]; z++) for (let y = 0; y < dims[1]; y++) for (let x = 0; x < dims[0]; x++) {
    const px = origin[0] + x * voxel, py = origin[1] + y * voxel, pz = origin[2] + z * voxel;
    const d = Math.sqrt(px * px + py * py + pz * pz) - R;
    data[i++] = Math.round(d / quant);
  }
  return new BodySDF({ origin, voxel, dims, quant }, data);
}

test('BodySDF: trilinear sample tracks the analytic sphere field', () => {
  const sdf = bakeSphereSDF();
  // on the axis at r=0.20 -> +0.05 outside
  assert.ok(Math.abs(sdf.sample(0.2, 0, 0) - 0.05) < 0.004, `got ${sdf.sample(0.2, 0, 0)}`);
  // inside at r=0.10 -> -0.05
  assert.ok(Math.abs(sdf.sample(0.1, 0, 0) + 0.05) < 0.004, `got ${sdf.sample(0.1, 0, 0)}`);
  // off-axis point
  const p = [0.09, 0.12, 0.05];
  const exact = Math.sqrt(p[0] ** 2 + p[1] ** 2 + p[2] ** 2) - 0.15;
  assert.ok(Math.abs(sdf.sample(...p) - exact) < 0.006, `got ${sdf.sample(...p)} want ${exact}`);
  // far outside: falloff adds box distance, stays positive and growing
  assert.ok(sdf.sample(2, 0, 0) > sdf.sample(0.5, 0, 0));
});

test('BodySDF.project pushes an embedded point out to the margin shell', () => {
  const sdf = bakeSphereSDF();
  const p = [0.05, 0.02, 0.0]; // r=0.0538, deep inside the r=0.15 sphere
  const resolved = sdf.project(p, 0.004);
  assert.ok(resolved > 0.09, `resolved ${resolved}`);
  const d = sdf.sample(p[0], p[1], p[2]);
  assert.ok(d >= 0.0035, `after project sample=${d} (want >= ~margin 0.004)`);
  const r = Math.sqrt(p[0] ** 2 + p[1] ** 2 + p[2] ** 2);
  assert.ok(r > 0.15, `point escaped the solid (r=${r})`);
});

test('BodySDF.project leaves an outside point untouched', () => {
  const sdf = bakeSphereSDF();
  const p = [0.3, 0.1, 0.0];
  assert.equal(sdf.project(p, 0.002), 0);
  assert.deepEqual(p, [0.3, 0.1, 0.0]);
});

/* ---------- analytic colliders ---------- */
test('collideCapsule: point beside the segment is pushed radially out', () => {
  const p = [0.05, 0.5, 0.0];
  const n = [0, 0, 0];
  const depth = collideCapsule(p, [0, 0, 0], [0, 1, 0], 0.1, n);
  assert.ok(Math.abs(depth - 0.05) < 1e-9);
  assert.ok(Math.abs(p[0] - 0.1) < 1e-9 && Math.abs(p[1] - 0.5) < 1e-9);
  assert.ok(Math.abs(n[0] - 1) < 1e-9);
});

test('collideCapsule: point beyond the cap end measures to the end sphere', () => {
  const p = [0.0, 1.05, 0.0];
  const depth = collideCapsule(p, [0, 0, 0], [0, 1, 0], 0.1, null);
  assert.ok(Math.abs(depth - 0.05) < 1e-9);
  assert.ok(Math.abs(p[1] - 1.1) < 1e-9);
});

test('collideSphere: outside point is a no-op', () => {
  const p = [1, 0, 0];
  assert.equal(collideSphere(p, [0, 0, 0], 0.5, null), 0);
  assert.deepEqual(p, [1, 0, 0]);
});

/* ---------- friction ---------- */
test('applyContactFriction: tangential velocity is damped, outward normal kept', () => {
  const p = [0, 0, 0];
  const prev = [-0.01, 0.004, 0]; // velocity = (0.01, -0.004, 0): sliding +x, sinking -y
  applyContactFriction(p, prev, [0, 1, 0], 0.5);
  const vx = p[0] - prev[0], vy = p[1] - prev[1];
  assert.ok(Math.abs(vx - 0.005) < 1e-9, `tangential halved: ${vx}`);
  assert.ok(Math.abs(vy - 0) < 1e-9, `sinking removed: ${vy}`);
});

/* ---------- self-collision ---------- */
test('SelfCollider separates overlapping particles to minDist', () => {
  const pos = new Float32Array([0, 0, 0, 0.004, 0, 0, 0.2, 0, 0]);
  const inv = new Float32Array([1, 1, 1]);
  const sc = new SelfCollider(0.01);
  const resolved = sc.collide(pos, inv, null, 2);
  assert.ok(resolved > 0);
  const d = Math.abs(pos[3] - pos[0]);
  assert.ok(d >= 0.0099, `pair distance ${d}`);
  assert.ok(Math.abs(pos[6] - 0.2) < 1e-6); // far particle untouched
});

test('SelfCollider never moves a pinned particle and honours skipPairs', () => {
  const pos = new Float32Array([0, 0, 0, 0.004, 0, 0]);
  const inv = new Float32Array([0, 1]); // particle 0 pinned
  const sc = new SelfCollider(0.01);
  sc.collide(pos, inv, null, 1);
  assert.equal(pos[0], 0);
  assert.ok(Math.abs(pos[3] - 0.01) < 1e-5, `free particle took the full push: ${pos[3]}`);
  const pos2 = new Float32Array([0, 0, 0, 0.004, 0, 0]);
  const inv2 = new Float32Array([1, 1]);
  sc.collide(pos2, inv2, new Set(['0_1']), 1);
  assert.ok(Math.abs(pos2[3] - 0.004) < 1e-6); // skipped pair untouched
});

/* ---------- articulator coupling (Phase C core, analytic mouth) ---------- */
// Head space: +Z out of the mouth, +Y up. Solids as boxes; the lower
// assembly (lower teeth + lower lip) drops by jaw*lever + lipLower;
// the upper lip rises by lipUpper.
function boxSDF(x, y, z, cx, cy, cz, hx, hy, hz) {
  const dx = Math.abs(x - cx) - hx, dy = Math.abs(y - cy) - hy, dz = Math.abs(z - cz) - hz;
  const ax = Math.max(dx, 0), ay = Math.max(dy, 0), az = Math.max(dz, 0);
  const outside = Math.sqrt(ax * ax + ay * ay + az * az);
  const inside = Math.min(Math.max(dx, Math.max(dy, dz)), 0);
  return outside + inside;
}
function makeMouthOracle() {
  const solids = (drives) => {
    const drop = drives.jaw * 0.085 + drives.lipLower;
    return [
      // upper teeth (static): centre y .009, half .005 -> y in [.004,.014]
      { c: [0, 0.009, 0.010], h: [0.020, 0.005, 0.020], region: 'upper' },
      // lower teeth (jaw-driven): top at -.004 - jawDrop
      { c: [0, -0.009 - drives.jaw * 0.085, 0.010], h: [0.020, 0.005, 0.020], region: 'lower' },
      // upper lip at the mouth front, rises with lipUpper (slabs meet at y=0: closed lips)
      { c: [0, 0.003 + drives.lipUpper, 0.032], h: [0.022, 0.005, 0.004], region: 'upper' },
      // lower lip, drops with jaw + lipLower
      { c: [0, -0.003 - drop, 0.032], h: [0.022, 0.005, 0.004], region: 'lower' },
    ];
  };
  return {
    sample(x, y, z, drives) {
      let d = Infinity;
      for (const s of solids(drives)) d = Math.min(d, boxSDF(x, y, z, ...s.c, ...s.h));
      return d;
    },
    gradient(x, y, z, drives, out) {
      const h = 0.0005;
      out[0] = this.sample(x + h, y, z, drives) - this.sample(x - h, y, z, drives);
      out[1] = this.sample(x, y + h, z, drives) - this.sample(x, y - h, z, drives);
      out[2] = this.sample(x, y, z + h, drives) - this.sample(x, y, z - h, drives);
    },
    classify(x, y, z) {
      // region of the nearest solid at rest drives (the real bake
      // segments regions geometrically; this is the fixture form)
      let best = Infinity, region = 'other';
      for (const s of solids({ jaw: 0, lipLower: 0, lipUpper: 0 })) {
        const d = boxSDF(x, y, z, ...s.c, ...s.h);
        if (d < best) { best = d; region = s.region; }
      }
      return best < 0.004 ? region : 'other';
    },
  };
}

test('articulator coupling: a tongue thrust parts lips, drops the jaw, ends penetration-free', () => {
  const oracle = makeMouthOracle();
  // tongue blade: upper + lower surface sample rows thrust forward
  // through the closed lips (z: -0.005 .. 0.055)
  const pts = [];
  for (let i = 0; i <= 10; i++) pts.push(0, 0.0015, -0.005 + i * 0.006);
  for (let i = 0; i <= 10; i++) pts.push(0, -0.0015, -0.005 + i * 0.006);
  const points = new Float32Array(pts);
  const { drives, stats } = solveArticulatorCoupling(points, oracle, { jaw: 0, lipLower: 0, lipUpper: 0 }, { margin: 0.0015 });
  assert.ok(stats.initialPen > 0.003, `fixture must start penetrating (got ${stats.initialPen})`);
  assert.ok(drives.jaw > 0.005 || drives.lipLower > 0.002, `the mouth made room: ${JSON.stringify(drives)}`);
  assert.ok(stats.residualPen <= 0.0005, `residual penetration ${stats.residualPen} m`);
  // no tongue sample may end up pushed backward through the teeth block
  for (let i = 0; i < points.length; i += 3) assert.ok(points[i + 2] > -0.006, `sample z=${points[i + 2]}`);
});

test('articulator coupling: a tongue at rest inside the mouth changes nothing', () => {
  const oracle = makeMouthOracle();
  const points = new Float32Array([0, 0, -0.01, 0, -0.001, 0.0, 0, 0.001, -0.02]);
  const { drives, stats } = solveArticulatorCoupling(points, oracle, { jaw: 0.1, lipLower: 0, lipUpper: 0 }, { margin: 0.001 });
  assert.equal(stats.initialPen, 0);
  assert.equal(drives.jaw, 0.1);
  assert.equal(stats.residualPen, 0);
});

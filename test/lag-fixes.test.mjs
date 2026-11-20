// Lag fixes (owner 2026-11-11: "the game is really laggy ... it lags a lot ... when you're making contact with the
// hits"). Node, no browser. Run: node --test test/lag-fixes.test.mjs
//  1. game/js/region-normals.js: the soft-body sims recompute normals for the moved region only. Every normal must
//     equal what a full BufferGeometry.computeVertexNormals() gives (indexed and non-indexed meshes).
//  2. game/js/hitfx.js: hit effects reuse pooled sprites; a finished effect is hidden, never disposed (disposing
//     the last sprite material deleted three.js's sprite program, so every hit recompiled it inside render).
import test from 'node:test';
import assert from 'node:assert/strict';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const THREE = await import('three');
const RN = await import(join(ROOT, 'game/js/region-normals.js'));

function deformAndCompare(geo, label) {
  geo.computeVertexNormals();
  const pos = geo.attributes.position;
  // region: vertices inside a sphere off-centre, as the flesh sims pick an ellipsoid
  const region = [];
  for (let i = 0; i < pos.count; i++) if (Math.hypot(pos.getX(i) - 0.6, pos.getY(i) - 0.48, pos.getZ(i) - 0.64) < 0.45) region.push(i); // a patch of the surface
  assert.ok(region.length > 10 && region.length < pos.count / 2, `${label}: a partial region (${region.length}/${pos.count})`);
  const plan = RN.buildRegionNormalPlan(geo, region);
  let seed = 7; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647 - 0.5) * 0.06;
  for (const v of region) pos.setXYZ(v, pos.getX(v) + rnd(), pos.getY(v) + rnd(), pos.getZ(v) + rnd());
  const full = geo.clone(); full.computeVertexNormals();
  RN.updateRegionNormals(geo, plan);
  const a = geo.attributes.normal.array, b = full.attributes.normal.array;
  let maxd = 0; for (let i = 0; i < a.length; i++) maxd = Math.max(maxd, Math.abs(a[i] - b[i]));
  assert.equal(maxd, 0, `${label}: every normal equals the full recompute (max diff ${maxd})`);
  assert.ok(plan.tris.length / 3 < (geo.index ? geo.index.count : pos.count) / 3, `${label}: touches fewer triangles than the mesh`);
}

test('region normals: indexed mesh, bit-for-bit the full computeVertexNormals', () => {
  deformAndCompare(new THREE.SphereGeometry(1, 64, 48), 'indexed sphere');
});

test('region normals: non-indexed mesh, bit-for-bit the full computeVertexNormals', () => {
  deformAndCompare(new THREE.SphereGeometry(1, 40, 30).toNonIndexed(), 'non-indexed sphere');
});

test('hit effects: pooled sprites are reused across hits and never disposed', async () => {
  const { HitFX } = await import(join(ROOT, 'game/js/hitfx.js'));
  const scene = new THREE.Scene();
  // the constructor paints canvas textures (DOM); build the same object with plain textures for Node
  const fx = Object.create(HitFX.prototype);
  Object.assign(fx, { scene, _items: [], _tex: { spark: new THREE.Texture(), dot: new THREE.Texture(), ring: new THREE.Texture() },
    _flashT: 0, _flashMax: 0, _flashEl: null, _pool: { spark: [], debris: [], ring: [] } });
  fx._flash = () => {}; // the screen flash is a DOM overlay, not under test here
  let disposed = 0;
  // 'heavy' spawns all three kinds: spark + debris + ring
  const run = (n) => { for (let h = 0; h < n; h++) { fx.spawn('heavy', 0, 1, 0); for (let i = 0; i < 40; i++) fx.update(1 / 60); } };
  run(1);
  const sprites = scene.children.filter((o) => o.isSprite);
  for (const s of sprites) s.material.addEventListener('dispose', () => { disposed++; });
  const n1 = sprites.length;
  assert.ok(n1 > 0 && sprites.every((s) => !s.visible), 'after an effect ends its sprites are hidden, still in the scene');
  run(25);
  assert.equal(scene.children.filter((o) => o.isSprite).length, n1, 'later hits reuse the same sprites (no growth)');
  assert.equal(disposed, 0, 'no material is disposed between hits');
  assert.equal(fx._items.length, 0);
  // the pooled sprite comes back with the hit's own colour and full opacity
  fx.spawn('block', 0, 1, 0);
  const live = scene.children.filter((o) => o.isSprite && o.visible);
  assert.ok(live.length > 0 && live.every((s) => s.material.opacity === 1));
  assert.ok(live.some((s) => s.material.color.getHex() === 0x9fd8ff), 'block colour');
});

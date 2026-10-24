// Node test for game/js/softbody.js — no DOM, no three.js.
// Run: node test/softbody.test.mjs
// Exercises the jiggle.js-style contract (fromMesh/update/hit/dispose),
// the quality toggle, and — once Jolt loads — a real XPBD sim:
// zero drift at rest, visible dent on hit, recovery, pinned core.
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const here = dirname(fileURLToPath(import.meta.url));

// ---- localStorage shim (mirrors test/ranks.test.mjs) ----
const _ls = {};
globalThis.localStorage = {
  getItem: (k) => (_ls[k] ?? null),
  setItem: (k, v) => { _ls[k] = String(v); },
  removeItem: (k) => { delete _ls[k]; },
};

const { SoftBody } = await import(join(here, '..', 'game', 'js', 'softbody.js'));

let pass = 0, fail = 0;
function ok(cond, name) {
  if (cond) { pass++; }
  else { fail++; console.log('FAIL -', name); }
}

// ---- mock skinned mesh: torso-ish vertex grid + Spine1 bone ----
function V3(x, y, z) { this.x = x || 0; this.y = y || 0; this.z = z || 0; }

function mockMesh() {
  // 12^3 grid over a torso-sized box; deterministic.
  const pts = [];
  for (let ix = 0; ix < 12; ix++)
    for (let iy = 0; iy < 12; iy++)
      for (let iz = 0; iz < 12; iz++) {
        pts.push(-0.25 + ix * (0.5 / 11), 0.75 + iy * (0.5 / 11), -0.2 + iz * (0.4 / 11));
      }
  const arr = new Float32Array(pts);
  const spine = {
    isBone: true, name: 'Spine1',
    getWorldPosition(v) { v.x = 0; v.y = 1.0; v.z = 0; return v; },
    updateWorldMatrix() {},
  };
  const mesh = {
    isSkinnedMesh: true,
    position: { constructor: V3 },
    geometry: {
      attributes: { position: { array: arr, count: arr.length / 3, needsUpdate: false } },
      boundingSphere: null,
      computeBoundingSphere() { this.boundingSphere = { radius: 1 }; },
      computeVertexNormals() { this.normalsRecomputed = (this.normalsRecomputed || 0) + 1; },
      userData: {},
    },
    traverse(cb) { cb(this); cb(spine); },
    updateWorldMatrix() {},
    getWorldPosition(v) { v.x = 0; v.y = 1.0; v.z = 0; return v; },
    worldToLocal(v) { return v; },
  };
  return mesh;
}

// ---- 1. anatomyFor ----
ok(SoftBody.anatomyFor(null) === null, 'anatomyFor(null) -> null');
ok(SoftBody.anatomyFor({ softbody: false }) === null, 'anatomyFor opt-out -> null');
{
  const spec = SoftBody.anatomyFor({ jiggleFamily: 'female' });
  ok(spec && spec.regions[0] === 'belly', 'anatomyFor default -> belly region');
}

// ---- 2. fromMesh builds a region (sync, no Jolt needed) ----
const meshA = mockMesh();
const sbA = SoftBody.fromMesh(meshA, SoftBody.anatomyFor({}), { autoLoad: false });
ok(sbA.particleCount > 0, 'fromMesh builds particles (got ' + sbA.particleCount + ')');
ok(sbA.regionVertexCount > 0, 'fromMesh maps region verts (got ' + sbA.regionVertexCount + ')');
ok(sbA.quality === 'low', 'default quality is low (conservative)');
ok(sbA.ready === false, 'not ready before Jolt loads');

// ---- 3. graceful degradation: update/hit/dispose never throw pre-Jolt ----
let threw = false;
try {
  sbA.update(1 / 60);
  sbA.hit({ x: 0, y: 1, z: 0.1 }, 1, 12);
  sbA.update(0);
  sbA.update(-1);
} catch (e) { threw = true; }
ok(!threw, 'update/hit no-throw before Jolt ready');
// geometry untouched while inert
{
  const arr = meshA.geometry.attributes.position.array;
  let moved = 0;
  for (let i = 0; i < arr.length; i++) if (arr[i] !== sbA._base[i]) moved++;
  ok(moved === 0, 'mesh untouched while sim not ready');
}

// ---- 4. quality toggle ----
ok(sbA.setQuality('ultra') === undefined && sbA.quality === 'low', 'invalid quality ignored');
sbA.setQuality('off');
ok(sbA.quality === 'off', 'setQuality(off)');
sbA.update(1 / 60); // no-throw while off
sbA.setQuality('low');
ok(sbA.quality === 'low', 'setQuality(low) re-enables');
const nLow = sbA.particleCount;
sbA.setQuality('high');
ok(sbA.particleCount >= nLow, 'high rebuilds lattice at >= low resolution');
sbA.setQuality('low');

// ---- 5. global quality + persistence ----
ok(SoftBody.setGlobalQuality('bogus') === false, 'setGlobalQuality rejects invalid');
ok(SoftBody.setGlobalQuality('high') === true, 'setGlobalQuality(high)');
ok(SoftBody.globalQuality === 'high' && _ls['wh_softbody_v1'] === 'high', 'global quality persisted');
ok(sbA.quality === 'high', 'live instance follows global quality');
SoftBody.setGlobalQuality('low');
ok(sbA.quality === 'low', 'live instance follows global quality back');
sbA.dispose();
{
  const arr = meshA.geometry.attributes.position.array;
  let moved = 0;
  for (let i = 0; i < arr.length; i++) if (arr[i] !== sbA._base[i]) moved++;
  ok(moved === 0, 'dispose restores base positions');
}

// ---- 6. real Jolt sim: drift / hit / recovery / pinning ----
const meshB = mockMesh();
const sbB = SoftBody.fromMesh(meshB, { regions: ['belly'] }); // autoLoad: true
const H = sbB._testHandle();
const world = await H.worldPromise;
ok(!!world, 'Jolt world loads');
if (world) {
  // wait for the body to build (poll, 20 s cap)
  let ready = false;
  for (let i = 0; i < 200 && !ready; i++) {
    ready = H.isReady();
    if (!ready) await new Promise((r) => setTimeout(r, 100));
  }
  ok(ready, 'soft body builds once Jolt ready');
  if (ready) {
    const rest = H.restPositions();
    const pinned = H.pinned();
    ok(pinned.some((p) => p === 1), 'some particles pinned (core+caps)');
    ok(pinned.some((p) => p === 0), 'some particles dynamic (shell)');
    // settle 60 steps
    for (let f = 0; f < 60; f++) H.stepOnce(1 / 60);
    let p = H.particlePositions();
    let maxDrift = 0;
    for (let i = 0; i < p.length; i++) maxDrift = Math.max(maxDrift, Math.abs(p[i] - rest[i]));
    ok(maxDrift < 1e-4, 'zero drift at rest (got ' + maxDrift.toExponential(2) + ')');
    // hit the belly front
    sbB.hit({ x: 0.05, y: 1.0, z: 0.2 }, 1, 15);
    for (let f = 0; f < 30; f++) H.stepOnce(1 / 60);
    p = H.particlePositions();
    let maxDent = 0;
    for (let i = 0; i < p.length; i++) maxDent = Math.max(maxDent, Math.abs(p[i] - rest[i]));
    ok(maxDent > 0.005, 'hit dents the volume (got ' + maxDent.toFixed(4) + ' m)');
    // mesh deformation is written by update()
    sbB.update(1 / 60);
    {
      const arr = meshB.geometry.attributes.position.array;
      let moved = 0;
      for (let i = 0; i < arr.length; i++) if (arr[i] !== sbB._base[i]) moved++;
      ok(moved > 0, 'update() writes deformation to the mesh (' + moved + ' comps)');
    }
    // recover 5 s
    for (let f = 0; f < 300; f++) H.stepOnce(1 / 60);
    p = H.particlePositions();
    let maxRes = 0, pinMove = 0;
    for (let i = 0; i < rest.length / 3; i++) {
      const d = Math.hypot(p[i * 3] - rest[i * 3], p[i * 3 + 1] - rest[i * 3 + 1], p[i * 3 + 2] - rest[i * 3 + 2]);
      if (d > maxRes) maxRes = d;
      if (pinned[i] === 1 && d > pinMove) pinMove = d;
    }
    ok(maxRes < 0.05, 'volume recovers toward rest (residual ' + maxRes.toFixed(4) + ' m)');
    ok(pinMove < 1e-6, 'pinned core never moves (got ' + pinMove.toExponential(2) + ')');
  }
}
sbB.dispose();

console.log(`\nsoftbody: ${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);

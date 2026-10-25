/* MpmTissue (CPU MPM-lite tissue backend) — unit tests (node, no DOM/GL).
 * Covers: region build, NDG material defaults (lambda ~= 16*mu), staged
 * muscle/fat particle split, update() boundedness over many steps,
 * hit() injection, the NDG-style inversion guard (det(F) floor),
 * dispose() mesh restore, quality store sharing with the Jolt lane,
 * and the no-top-level-imports (zero boot cost) rule. */
import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { MpmTissue } from '../js/mpm-tissue.js';

const here = dirname(fileURLToPath(import.meta.url));

/* ---- fake SkinnedMesh: box of vertices, spine bone at torso center ---- */
class FakeVec3 {
  constructor(x = 0, y = 0, z = 0) { this.x = x; this.y = y; this.z = z; }
}

function fakeMesh() {
  // Torso-proportioned vertex box so the belly ellipsoid catches a
  // realistic number of region vertices.
  const nx = 16, ny = 24, nz = 16;
  const count = nx * ny * nz;
  const arr = new Float32Array(count * 3);
  let i = 0;
  for (let iz = 0; iz < nz; iz++) {
    for (let iy = 0; iy < ny; iy++) {
      for (let ix = 0; ix < nx; ix++) {
        arr[i * 3] = -0.4 + (0.8 * ix) / (nx - 1);
        arr[i * 3 + 1] = -0.6 + (1.8 * iy) / (ny - 1);
        arr[i * 3 + 2] = -0.35 + (0.7 * iz) / (nz - 1);
        i++;
      }
    }
  }
  const spine = {
    name: 'Spine1',
    getWorldPosition(v) { v.x = 0; v.y = 0.1; v.z = 0; return v; },
    updateWorldMatrix() {},
  };
  const mesh = {
    isSkinnedMesh: true,
    geometry: {
      attributes: { position: { array: arr, count, needsUpdate: false } },
      computeVertexNormals() {},
    },
    skeleton: { bones: [spine] },
    position: new FakeVec3(),
    traverse(fn) { fn(this); },
    updateWorldMatrix() {},
    getWorldPosition(v) { v.x = 0; v.y = 0; v.z = 0; return v; },
    worldToLocal(v) { return v; },
  };
  return { mesh, arr };
}

describe('MpmTissue construction', () => {
  it('builds the belly region synchronously (pure JS, no async load)', () => {
    const { mesh } = fakeMesh();
    const mt = MpmTissue.fromMesh(mesh, MpmTissue.anatomyFor({}));
    assert.equal(mt.ready, true);
    assert.equal(mt.particleCount, 3 * 4 * 3); // low lattice
    assert.equal(mt.gridNodeCount, 5 * 6 * 5);
    assert.ok(mt.regionVertexCount > 50, 'belly ellipsoid should catch vertices');
    assert.equal(MpmTissue.ENGINE, 'mpm-lite');
    mt.dispose();
  });

  it('anatomyFor opts out correctly', () => {
    assert.equal(MpmTissue.anatomyFor(null), null);
    assert.equal(MpmTissue.anatomyFor({ softbody: false }), null);
    assert.deepEqual(MpmTissue.anatomyFor({}).regions, ['belly']);
  });

  it('uses NDG published tissue values (lambda ~= 16*mu), muscle stiffer than fat', () => {
    const { mesh } = fakeMesh();
    const mt = MpmTissue.fromMesh(mesh, MpmTissue.anatomyFor({}));
    const mats = mt._testHandle().materials();
    assert.ok(mats.muscle.mu > 0 && mats.fat.mu > 0);
    assert.ok(Math.abs(mats.muscle.lambda / mats.muscle.mu - 16) < 1.5,
      `lambda/mu = ${mats.muscle.lambda / mats.muscle.mu}, want ~16 (nu=0.47)`);
    assert.ok(mats.muscle.mu > mats.fat.mu * 2, 'muscle stiffer than fat');
    // E ratio 45kPa : 15kPa preserved at solver scale
    assert.ok(Math.abs(mats.muscle.E / mats.fat.E - 3) < 0.01);
    mt.dispose();
  });

  it('splits particles into MUSCLE core + FAT shell with a pinned rigid core', () => {
    const { mesh } = fakeMesh();
    const mt = MpmTissue.fromMesh(mesh, MpmTissue.anatomyFor({}));
    const h = mt._testHandle();
    const pm = h.particleMaterials();
    const pinned = h.pinned();
    assert.ok(pm.includes(0), 'has muscle particles');
    assert.ok(pm.includes(1), 'has fat particles');
    assert.ok(pinned.includes(1), 'has pinned (rigid bone-wrap) particles');
    assert.ok(pinned.includes(0), 'has dynamic particles');
    mt.dispose();
  });

  it('accepts per-character material overrides', () => {
    const { mesh } = fakeMesh();
    const mt = MpmTissue.fromMesh(mesh, MpmTissue.anatomyFor({
      softbodyMaterials: { muscle: { E: 20000, mu: 6800, lambda: 108800, nu: 0.47 } },
    }));
    assert.equal(mt._testHandle().materials().muscle.E, 20000);
    mt.dispose();
  });
});

describe('MpmTissue dynamics', () => {
  it('update() stays bounded over 60 frames (no NaN, no explosion)', () => {
    const { mesh } = fakeMesh();
    const mt = MpmTissue.fromMesh(mesh, MpmTissue.anatomyFor({}));
    for (let f = 0; f < 60; f++) mt.update(1 / 60);
    const pos = mt._testHandle().particlePositions();
    let maxAbs = 0;
    for (let i = 0; i < pos.length; i++) {
      assert.ok(Number.isFinite(pos[i]), 'position must stay finite');
      maxAbs = Math.max(maxAbs, Math.abs(pos[i]));
    }
    assert.ok(maxAbs < 50, `positions bounded (maxAbs=${maxAbs})`);
    mt.dispose();
  });

  it('update() tolerates dt=0 and negative dt', () => {
    const { mesh } = fakeMesh();
    const mt = MpmTissue.fromMesh(mesh, MpmTissue.anatomyFor({}));
    mt.update(0);
    mt.update(-1);
    assert.equal(mt.ready, true);
    mt.dispose();
  });

  it('hit() dents the tissue volume immediately', () => {
    const { mesh } = fakeMesh();
    const mt = MpmTissue.fromMesh(mesh, MpmTissue.anatomyFor({}));
    const h = mt._testHandle();
    const before = h.particlePositions();
    mt.hit({ x: 0, y: 0.12, z: 0.1 }, 1, 20);
    const after = h.particlePositions();
    let moved = 0;
    for (let i = 0; i < before.length; i++) {
      if (Math.abs(after[i] - before[i]) > 1e-9) moved++;
    }
    assert.ok(moved > 0, 'hit() must displace particles');
    // ...and the dent relaxes back toward rest over time (elastic recovery)
    for (let f = 0; f < 90; f++) mt.update(1 / 60);
    const rest = h.restPositions();
    const now = h.particlePositions();
    let disp = 0;
    for (let i = 0; i < rest.length; i++) disp = Math.max(disp, Math.abs(now[i] - rest[i]));
    assert.ok(disp < 0.05, `dent should mostly recover (maxDisp=${disp})`);
    mt.dispose();
  });

  it('NDG-style inversion guard: crushed det(F) is rescaled above the floor', () => {
    const { mesh } = fakeMesh();
    const mt = MpmTissue.fromMesh(mesh, MpmTissue.anatomyFor({}));
    const h = mt._testHandle();
    const pinned = h.pinned();
    const p = pinned.findIndex((v) => v === 0); // a dynamic particle
    assert.ok(p >= 0);
    h.forceDet(p, 0.01); // crush to det = 0.01
    h.stepOnce(1 / 480);
    const det = h.deformationDets()[p];
    assert.ok(det >= 0.34, `inversion guard must lift det(F) (got ${det})`);
    mt.dispose();
  });

  it('dispose() restores the render mesh', () => {
    const { mesh, arr } = fakeMesh();
    const snapshot = arr.slice();
    const mt = MpmTissue.fromMesh(mesh, MpmTissue.anatomyFor({}));
    mt.hit({ x: 0, y: 0.12, z: 0.1 }, 1, 30);
    for (let f = 0; f < 10; f++) mt.update(1 / 60);
    mt.dispose();
    assert.deepEqual(Array.from(arr), Array.from(snapshot), 'mesh must be restored');
  });
});

describe('MpmTissue integration contract', () => {
  let savedQuality;
  beforeEach(() => { savedQuality = MpmTissue.globalQuality; });
  afterEach(() => { MpmTissue.setGlobalQuality(savedQuality); });

  it("shares the 'wh_softbody_v1' quality store with the Jolt lane", async () => {
    const { SoftBody } = await import('../js/softbody.js');
    MpmTissue.setGlobalQuality('high');
    assert.equal(SoftBody.globalQuality, 'high', 'Jolt lane must see the same quality');
    const { mesh } = fakeMesh();
    const mt = MpmTissue.fromMesh(mesh, MpmTissue.anatomyFor({}));
    assert.equal(mt.particleCount, 4 * 5 * 4, 'high quality rebuilds denser');
    mt.dispose();
  });

  it('backendStatus() reports ready (no WASM wait)', () => {
    assert.equal(MpmTissue.backendStatus(), 'ready');
  });

  it('has no heavy top-level imports (no three.js, no Jolt/WASM)', () => {
    const src = readFileSync(join(here, '..', 'js', 'mpm-tissue.js'), 'utf8');
    const staticImports = src.split('\n').filter(
      (l) => /^\s*import\s/.test(l) && !l.includes('import('));
    // Exactly one static import is allowed: the dependency-free shared
    // quality store (zero boot cost, node-testable).
    assert.deepEqual(staticImports, [
      "import { getTissueQuality, setTissueQuality, onTissueQuality, TISSUE_QUALITIES } from './tissue-quality.js';",
    ]);
  });
});

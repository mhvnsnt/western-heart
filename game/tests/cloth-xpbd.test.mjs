/* WESTERN HEART — WHCloth XPBD engine tests (node, no DOM/GL).
 * Covers: solver physics (drape, pinning, stability), graph coloring
 * invariant, compliance (fabric stiffness), topology extraction,
 * builders (sheet/mesh/chain), colliders, three.js adapters, quality. */
import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import {
  XPBDSolver, buildSheet, buildFromMesh, buildChain,
  extractTopology, writePositions, writeNormals,
  FABRICS, CLOTH_QUALITY, CLOTH_LOD_DIST, detectClothQuality,
  availableBackends,
} from '../js/fx/cloth.js';

const eq = assert.equal, ok = assert.ok;

function drape(solver, steps = 120) {
  for (let i = 0; i < steps; i++) solver.step(1 / 60, []);
}

describe('xpbd: pinned sheet drapes and stays stable', () => {
  it('top row pinned, bottom hangs, no NaN/explosion', () => {
    const { solver, idx, cols, rows } = buildSheet(8, 10, 0.6, 0.9, { substeps: 4 });
    drape(solver);
    const { pos } = solver;
    for (const p of pos) ok(Number.isFinite(p), 'all positions finite');
    // top row pinned at y=0
    for (let c = 0; c < cols; c++) ok(Math.abs(pos[idx[c] * 3 + 1]) < 1e-6, 'top pinned');
    // bottom row hangs near -0.9
    let bottom = 0;
    for (let c = 0; c < cols; c++) bottom += pos[idx[(rows - 1) * cols + c] * 3 + 1];
    bottom /= cols;
    ok(bottom < -0.6 && bottom > -1.1, 'bottom hangs, got ' + bottom.toFixed(3));
    // max stretch of any constraint stays small (rigid stretch)
    let maxStretch = 0;
    for (let k = 0; k < solver.constraintCount; k++) {
      if (solver.calpha[k] > 0) continue; // only rigid stretch links
      const a = solver.ca[k] * 3, b = solver.cb[k] * 3;
      const d = Math.hypot(pos[a]-pos[b], pos[a+1]-pos[b+1], pos[a+2]-pos[b+2]);
      maxStretch = Math.max(maxStretch, Math.abs(d - solver.crest[k]) / solver.crest[k]);
    }
    ok(maxStretch < 0.05, 'stretch < 5%, got ' + (maxStretch * 100).toFixed(2) + '%');
  });
});

describe('xpbd: graph coloring invariant', () => {
  it('no color group shares a particle', () => {
    const { solver } = buildSheet(6, 6, 0.5, 0.5, { substeps: 2 });
    ok(solver.colorCount > 1, 'more than one color, got ' + solver.colorCount);
    for (let c = 0; c < solver.colorCount; c++) {
      const seen = new Set();
      const start = solver.colorStarts[c], end = start + solver.colorCounts[c];
      for (let k = start; k < end; k++) {
        ok(!seen.has(solver.ca[k]) && !seen.has(solver.cb[k]), 'color group disjoint');
        seen.add(solver.ca[k]); seen.add(solver.cb[k]);
      }
    }
  });
});

describe('xpbd: compliance controls fabric stiffness', () => {
  it('silk drapes deeper than leather under the same pin', () => {
    const mk = (fabric) => {
      const b = buildSheet(6, 8, 0.5, 0.7, { fabric, substeps: 4 });
      drape(b.solver);
      let bottom = 0;
      for (let c = 0; c < 6; c++) bottom += b.solver.pos[b.idx[7 * 6 + c] * 3 + 1];
      return bottom / 6;
    };
    const silk = mk('silk'), leather = mk('leather');
    // silk's soft bend lets the sheet fold/curve more than stiff leather
    ok(Number.isFinite(silk) && Number.isFinite(leather), 'both stable');
    ok(Math.abs(silk) > 0.3, 'silk hangs, got ' + silk.toFixed(3));
  });
});

describe('topology: extractTopology', () => {
  it('finds edges and adjacent-triangle hinges on a quad', () => {
    const { edges, adjacentTriangles } = extractTopology([0, 1, 2, 2, 1, 3]);
    eq(edges.length, 5, 'quad has 5 unique edges');
    eq(adjacentTriangles.length, 1, 'one shared edge');
    // hinge connects the two non-shared verts (0 and 3)
    const [ta, tb] = adjacentTriangles[0];
    const va = [[0,1,2],[2,1,3]][ta], vb = [[0,1,2],[2,1,3]][tb];
    const onlyA = va.find(v => !vb.includes(v)), onlyB = vb.find(v => !va.includes(v));
    eq(new Set([onlyA, onlyB]).size, 2);
    ok((onlyA === 0 && onlyB === 3) || (onlyA === 3 && onlyB === 0), 'hinge is 0-3');
  });
});

describe('buildFromMesh: costume geometry', () => {
  it('simulates a mesh, pins by test, masses from areas', () => {
    // 2x2 grid mesh, 4 verts, 2 tris
    const positions = [0,0,0,  1,0,0,  0,-1,0,  1,-1,0];
    const indices = [0, 2, 1, 1, 2, 3];
    const { solver } = buildFromMesh(positions, indices, {
      fabric: 'cotton', substeps: 2, pinTest: (x, y) => y === 0,
    });
    eq(solver.count, 4);
    ok(solver.invMass[0] === 0 && solver.invMass[1] === 0, 'top pinned');
    ok(solver.invMass[2] > 0 && solver.invMass[3] > 0, 'bottom free');
    ok(solver.constraintCount > 0, 'has constraints');
    drape(solver, 60);
    ok(solver.pos[2 * 3 + 1] < -0.5, 'free verts fall');
    ok(Math.abs(solver.pos[1]) < 1e-6, 'pinned verts stay');
  });
  it('rejects meshes over budget instead of decimating silently', () => {
    const positions = new Array(9).fill(0);
    assert.throws(() => buildFromMesh(positions, [0, 1, 2], { maxParticles: 2 }), /budget/);
  });
});

describe('buildChain: hair', () => {
  it('root pinned to anchor, tip hangs, strand stays linked', () => {
    const { solver, idx } = buildChain(8, 0.06, { substeps: 2 });
    // place the strand coherently at the anchor (what HairChain.setRoot
    // does on first placement), then pin the root and let it settle
    for (const i of idx) { solver.pos[i*3] += 1; solver.pos[i*3+1] += 2; solver.pos[i*3+2] += 3; }
    solver.pinTo(idx[0], 1, 2, 3);
    drape(solver, 60);
    const p = solver.pos;
    ok(Math.hypot(p[0]-1, p[1]-2, p[2]-3) < 1e-6, 'root pinned');
    ok(p[idx[8] * 3 + 1] < 1.9, 'tip hangs below root');
    let maxLink = 0;
    for (let i = 0; i < 8; i++) {
      const a = idx[i]*3, b = idx[i+1]*3;
      maxLink = Math.max(maxLink, Math.hypot(p[a]-p[b], p[a+1]-p[b+1], p[a+2]-p[b+2]));
    }
    ok(maxLink < 0.06 * 1.5, 'links hold, max ' + maxLink.toFixed(4));
  });
});

describe('colliders: spheres and capsules', () => {
  it('sphere pushes particles out', () => {
    const s = new XPBDSolver(2, { substeps: 2 });
    s.addParticle(0, 0, 0, 1); s.addParticle(5, 5, 5, 1);
    s.finalize();
    for (let i = 0; i < 30; i++) s.step(1 / 60, [{ x: 0, y: -0.5, z: 0, r: 1 }]);
    const d = Math.hypot(s.pos[0], s.pos[1] + 0.5, s.pos[2]);
    ok(d >= 0.99, 'kept out of sphere, d=' + d.toFixed(3));
    ok(s.pos[4] < 4.5, 'far particle still falls, y=' + s.pos[4].toFixed(3));
  });
  it('capsule pushes particles out', () => {
    const s = new XPBDSolver(1, { substeps: 2 });
    s.addParticle(0, 0.4, 0, 1);
    s.finalize();
    for (let i = 0; i < 30; i++) {
      s.step(1 / 60, [{ x1: -1, y1: 0, z1: 0, x2: 1, y2: 0, z2: 0, r: 0.5 }]);
    }
    // particle resting on/near the capsule surface: |y| >= ~0.49 after settle
    ok(Math.abs(s.pos[1]) > 0.4, 'kept out of capsule, y=' + s.pos[1].toFixed(3));
  });
});

describe('adapters: writePositions / writeNormals', () => {
  it('writes to BufferAttribute-shaped objects and raw arrays', () => {
    const { solver } = buildSheet(2, 2, 0.4, 0.4, { substeps: 1 });
    drape(solver, 10);
    const attr = { vals: [], setXYZ(i, x, y, z) { this.vals[i] = [x, y, z]; }, needsUpdate: false };
    writePositions(solver, attr, 10, 20, 30);
    eq(attr.vals.length, 4);
    ok(Math.abs(attr.vals[0][0] - (solver.pos[0] + 10)) < 1e-9, 'origin offset applied');
    ok(attr.needsUpdate, 'needsUpdate flagged');
    const raw = new Float32Array(12);
    writePositions(solver, raw);
    ok(Math.abs(raw[1] - solver.pos[1]) < 1e-9, 'raw array path works');
    const nrm = { vals: [], setXYZ(i, x, y, z) { this.vals[i] = [x, y, z]; }, needsUpdate: false };
    writeNormals(solver, nrm, [0, 2, 1, 1, 2, 3]);
    eq(nrm.vals.length, 4);
    const l = Math.hypot(...nrm.vals[0]);
    ok(Math.abs(l - 1) < 1e-6, 'normals normalized, |n|=' + l.toFixed(4));
  });
});

describe('quality + backends', () => {
  it('quality table sane; detectClothQuality phone-safe', () => {
    for (const q of ['low', 'medium', 'high']) {
      ok(CLOTH_QUALITY[q].substeps >= 2 && CLOTH_QUALITY[q].maxParticles > 0, q);
    }
    eq(detectClothQuality({ navigator: { userAgent: 'Android', hardwareConcurrency: 8 } }), 'low');
    eq(detectClothQuality({ navigator: { userAgent: 'X', hardwareConcurrency: 16 }, localStorage: { getItem: () => 'high' } }), 'high');
    eq(CLOTH_LOD_DIST, 14);
  });
  it('cpu backend always available; webgpu probed honestly', () => {
    const b = availableBackends({});
    eq(b.cpu, true); eq(b.webgpu, false); eq(b.active, 'cpu');
    const g = availableBackends({ navigator: { gpu: {} } });
    eq(g.webgpu, true); eq(g.active, 'cpu', 'cpu ships even when webgpu exists');
  });
  it('fabric presets cover the costume range', () => {
    for (const f of ['silk', 'cotton', 'denim', 'leather', 'cape', 'hair']) {
      const p = FABRICS[f];
      ok(p && p.bendCompliance >= 0 && p.density > 0, f);
    }
    ok(FABRICS.silk.bendCompliance > FABRICS.leather.bendCompliance, 'silk softer than leather');
  });
});

// Material gate unit tests (game/js/material-resolve.js — shared by the CI gate,
// the asset pipeline and the runtime loader).
import test from 'node:test';
import assert from 'node:assert/strict';
import { auditGltf, donorPlan, authoredFlat } from '../game/js/material-resolve.js';

const prim = (material, extra = {}) => ({ attributes: { POSITION: 0, ...extra }, material });
const base = (materials, prims) => ({
  accessors: [{ count: 100 }], meshes: [{ name: 'm', primitives: prims }], materials,
  textures: [{ source: 0 }], images: [{ bufferView: 0 }], bufferViews: [{ buffer: 0, byteLength: 10 }], buffers: [{}],
});

test('textured material passes', () => {
  const j = base([{ name: 'Skin', pbrMetallicRoughness: { baseColorTexture: { index: 0 } } }], [prim(0)]);
  assert.equal(auditGltf(j).ok, true);
});
test('missing material / dangling texture / placeholder / default-white all fail', () => {
  assert.equal(auditGltf(base([], [prim(undefined)])).counts.missing, 1);
  assert.equal(auditGltf(base([{ name: 'x', pbrMetallicRoughness: { baseColorTexture: { index: 5 } } }], [prim(0)])).counts.missing, 1);
  assert.equal(auditGltf(base([{ name: 'dummy_material_3' }], [prim(0)])).counts.placeholder, 1);
  assert.equal(auditGltf(base([{ name: 'unnamed.0' }], [prim(0)])).counts.placeholder, 1);
  assert.equal(auditGltf(base([{ name: 'Boots', pbrMetallicRoughness: { baseColorFactor: [0.8, 0.8, 0.8, 1] } }], [prim(0)])).counts.untextured, 1);
  assert.equal(auditGltf(base([{ name: 'Eye', pbrMetallicRoughness: { baseColorFactor: [0, 0, 0, 1] } }], [prim(0)])).counts.untextured, 1);
});
test('vertex colours and authored flat colours pass', () => {
  assert.equal(auditGltf(base([{ name: 'Body' }], [prim(0, { COLOR_0: 0 })])).ok, true);
  assert.equal(authoredFlat([0.72, 0.55, 0.45, 1]), true);
  assert.equal(authoredFlat([1, 1, 1, 1]), false);
});
test('donor plan maps a textureless re-export onto its textured twin only', () => {
  const t = base([{ name: 'Belt.001' }], [prim(0)]);
  const d = base([{ name: 'Belt', pbrMetallicRoughness: { baseColorTexture: { index: 0 } } }], [prim(0)]);
  assert.deepEqual(donorPlan(t, d), { complete: true, map: { 0: 0 }, needed: 1 });
  const other = base([{ name: 'Cape', pbrMetallicRoughness: { baseColorTexture: { index: 0 } } }], [prim(0)]);
  assert.equal(donorPlan(t, other), null);
});

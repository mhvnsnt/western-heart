// Cainelias scale guard (Roster-100 S3, PR for #1565): both attire GLBs
// must stay floor-grounded at the baked canon scale, and their geometry
// payloads (BIN chunks) must not change silently — the S3 fix is a
// JSON-chunk node transform only (uniform scale + ground lift on the
// single scene node). Any future geometry change to these files must
// re-prove scale/grounding and update the pinned hashes deliberately.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const CASES = [
  { path: 'roster/cain-elias/attires/attire1/model.glb', binSha256: '02f5203e6f6dd8ebbf360a09a07cbaa6c29e451e1f2d4b35ac7afa33ba6d58cd' },
  { path: 'roster/cain-elias/attires/attire2/model.glb', binSha256: '952edca56a2df858b2cdbf031870b4d066010d7375cc4f398a44339c19b671f0' },
];
// Baked target (S3): canon 208 cm (game/data/canon-sizing.js, Undertaker)
// at the roster anchor measured in the same live scene — Pantera 1.749 m
// at his canon 200 cm — so 1.749 * 208/200 = 1.81896 m, feet at y=0.
const TARGET_H = 1.81896;

for (const { path, binSha256 } of CASES) {
  const buf = readFileSync(new URL(`../${path}`, import.meta.url));
  assert.equal(buf.toString('ascii', 0, 4), 'glTF', `${path}: GLB magic`);
  const jlen = buf.readUInt32LE(12);
  assert.equal(buf.toString('ascii', 16, 20), 'JSON', `${path}: JSON chunk`);
  const gltf = JSON.parse(buf.toString('utf8', 20, 20 + jlen));
  const binOff = 20 + jlen;
  const blen = buf.readUInt32LE(binOff);
  assert.equal(buf.toString('ascii', binOff + 4, binOff + 8), 'BIN\0', `${path}: BIN chunk`);
  const binHash = createHash('sha256').update(buf.subarray(binOff, binOff + 8 + blen)).digest('hex');
  assert.equal(binHash, binSha256, `${path}: BIN chunk changed (geometry payload must stay byte-identical to the S3 bake)`);

  assert.equal(gltf.scenes.length, 1, `${path}: one scene`);
  assert.deepEqual(gltf.scenes[0].nodes, [0], `${path}: scene root is node 0`);
  const node = gltf.nodes[0];
  assert.ok('mesh' in node, `${path}: node 0 carries the mesh`);
  assert.ok(Array.isArray(node.scale) && Array.isArray(node.translation), `${path}: node transform baked`);
  const [sx, sy, sz] = node.scale;
  assert.ok(Math.abs(sx - sy) < 1e-9 && Math.abs(sy - sz) < 1e-9, `${path}: uniform scale`);
  assert.equal(node.translation[0], 0, `${path}: no x lift`);
  assert.equal(node.translation[2], 0, `${path}: no z lift`);

  let lo = Infinity, hi = -Infinity;
  for (const mesh of gltf.meshes) {
    for (const prim of mesh.primitives) {
      const acc = gltf.accessors[prim.attributes.POSITION];
      lo = Math.min(lo, acc.min[1]); hi = Math.max(hi, acc.max[1]);
    }
  }
  const effLo = node.translation[1] + sy * lo;
  const effHi = node.translation[1] + sy * hi;
  assert.ok(Math.abs(effLo) < 0.005, `${path}: grounded (effective min.y = ${effLo})`);
  assert.ok(Math.abs((effHi - effLo) - TARGET_H) < 0.005, `${path}: effective height ${effHi - effLo} != target ${TARGET_H}`);
  console.log(`cainelias-scale: ${path} grounded at ${effLo.toFixed(4)}, height ${(effHi - effLo).toFixed(4)} m, BIN pinned ok`);
}
console.log('cainelias-scale: both attires ok');

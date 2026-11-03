// dump_prims.mjs <template.glb> <out.json> — per-primitive POSITION (skin + nails) in the GLB's own vertex order,
// in world bind space (node world matrix applied, glTF axes). The body-hide masks index these orders.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { MeshoptDecoder } from 'meshoptimizer';
import fs from 'fs';
await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.decoder': MeshoptDecoder });
const [, , src, out] = process.argv;
const doc = await io.read(src);
const node = doc.getRoot().listNodes().find((n) => n.getMesh());
const M = node.getWorldMatrix();
const res = { prims: {} };
for (const p of node.getMesh().listPrimitives()) {
  const mat = p.getMaterial()?.getName() || '';
  const key = /skin/i.test(mat) ? 'skin' : /nails/i.test(mat) ? 'nails' : /generic/i.test(mat) ? 'generic' : null; if (!key) continue;
  const a = p.getAttribute('POSITION'); const n = a.getCount(); const P = []; const t = [];
  for (let i = 0; i < n; i++) { a.getElement(i, t); const [x, y, z] = t;
    P.push(M[0] * x + M[4] * y + M[8] * z + M[12], M[1] * x + M[5] * y + M[9] * z + M[13], M[2] * x + M[6] * y + M[10] * z + M[14]); }
  res.prims[key] = { mat, n, pos: P.map((v) => +v.toFixed(6)), idx: Array.from(p.getIndices().getArray()) };
}
fs.writeFileSync(out, JSON.stringify(res));
console.log(src, Object.fromEntries(Object.entries(res.prims).map(([k, v]) => [k, v.n])));

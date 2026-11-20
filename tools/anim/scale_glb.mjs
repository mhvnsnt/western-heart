// Uniform-scale a skinned GLB by factor s (positions, morph deltas, node
// translations, inverse bind matrices). Usage: node scale_glb.mjs IN OUT s
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';

const [, , inp, out, sStr] = process.argv;
const s = parseFloat(sStr);
if (!inp || !out || !(s > 0)) { console.error('usage: scale_glb.mjs IN OUT s'); process.exit(2); }
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(inp);
const root = doc.getRoot();

// POSITION accessors (geometry + morph targets): scale values + bounds.
const posAccessors = new Set();
for (const mesh of root.listMeshes()) {
  for (const prim of mesh.listPrimitives()) {
    const p = prim.getAttribute('POSITION'); if (p) posAccessors.add(p);
    for (const t of prim.listTargets()) { const tp = t.getAttribute('POSITION'); if (tp) posAccessors.add(tp); }
  }
}
for (const acc of posAccessors) {
  const arr = acc.getArray().slice();
  for (let i = 0; i < arr.length; i++) arr[i] *= s;
  acc.setArray(arr); // bounds are derived from the array by gltf-transform
}
// Node translations.
for (const node of root.listNodes()) {
  const t = node.getTranslation();
  if (t) node.setTranslation([t[0] * s, t[1] * s, t[2] * s]);
}
// Inverse bind matrices: IBM' = S * IBM * S^-1 for uniform S, which leaves
// the 3x3 block unchanged and scales only the translation (elements 12-14).
for (const skin of root.listSkins()) {
  const ibm = skin.getInverseBindMatrices();
  if (!ibm) continue;
  const arr = ibm.getArray().slice();
  for (let m = 0; m < arr.length; m += 16) {
    arr[m + 12] *= s; arr[m + 13] *= s; arr[m + 14] *= s;
  }
  ibm.setArray(arr);
}
await io.write(out, doc);
console.log(`scaled x${s} -> ${out}`);

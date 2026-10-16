// wh_attire_variants.mjs — build KHR_materials_variants (P1/P2/alt attires) into one GLB.
// Usage: node wh_attire_variants.mjs base.glb variants.json out.glb
//
// variants.json:
// {
//   "variants": [
//     { "name": "P1" },
//     { "name": "P2",
//       "materialOverrides": {
//         "Body": { "baseColorFactor": [0.05,0.05,0.05,1], "roughnessFactor": 0.9 },
//         "Trim": { "baseColorFactor": [0.8,0.1,0.1,1], "baseColorTexture": "p2_trim.png" }
//       } }
//   ]
// }
// Materials are matched by glTF material name. Variant[0] keeps originals; later
// variants clone + override. Output keeps ONE mesh set — variants switch at runtime
// (three.js: scene.getObjectByProperty + KHR_materials_variants selectVariant).
import { readFileSync } from 'node:fs';
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS, KHRMaterialsVariants } from '@gltf-transform/extensions';

const [basePath, specPath, outPath] = process.argv.slice(2);
if (!basePath || !specPath || !outPath) {
  console.error('usage: node wh_attire_variants.mjs base.glb variants.json out.glb');
  process.exit(1);
}

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({});
const doc = await io.read(basePath);
const spec = JSON.parse(readFileSync(specPath, 'utf8'));
const root = doc.getRoot();
const variantsExt = doc.createExtension(KHRMaterialsVariants);

const matByName = new Map(root.listMaterials().map((m) => [m.getName(), m]));

function applyOverride(mat, ov) {
  if (ov.baseColorFactor) mat.setBaseColorFactor(ov.baseColorFactor);
  if (ov.metallicFactor !== undefined) mat.setMetallicFactor(ov.metallicFactor);
  if (ov.roughnessFactor !== undefined) mat.setRoughnessFactor(ov.roughnessFactor);
  if (ov.emissiveFactor) mat.setEmissiveFactor(ov.emissiveFactor);
  if (ov.baseColorTexture) {
    const bytes = readFileSync(ov.baseColorTexture);
    const tex = doc.createTexture(ov.baseColorTexture.split('/').pop());
    tex.setImage(bytes).setMimeType('image/png');
    mat.setBaseColorTexture(tex);
  }
}

const variantObjs = spec.variants.map((v) => variantsExt.createVariant(v.name));

for (const mesh of root.listMeshes()) {
  for (const prim of mesh.listPrimitives()) {
    const baseMat = prim.getMaterial();
    if (!baseMat) continue;
    const mapping = variantsExt.createMapping();
    mapping.setVariants(variantObjs);
    prim.setExtension('KHR_materials_variants', mapping);
    spec.variants.forEach((v, vi) => {
      let mat = baseMat;
      const ov = (v.materialOverrides || {})[baseMat.getName()];
      if (ov) {
        mat = baseMat.clone();
        mat.setName(`${baseMat.getName()}__${v.name}`);
        applyOverride(mat, ov);
      }
      mapping.addMaterialVariantMapping
        ? mapping.addMaterialVariantMapping(mat, variantObjs[vi])
        : mapping.addMapping(mat, variantObjs[vi]);
    });
  }
}

await io.write(outPath, doc);
console.log(`wrote ${outPath}: ${spec.variants.length} variants, ` +
  `${root.listMaterials().length} materials, ${root.listMeshes().length} meshes`);

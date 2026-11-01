// tools/anim/gltf_codec.mjs — decode / re-encode Tripo GLBs around the Blender rig step.
//
// Tripo pulls ship as gltfpack output (EXT_meshopt_compression + KHR_mesh_quantization),
// which Blender 4.0.2's glTF importer cannot read. This decodes them to plain float GLBs
// for Blender, and re-encodes the rigged result (meshopt + quantization, skin attributes
// included) so the shipped file stays about the size of the original.
//
//   node tools/anim/gltf_codec.mjs decode IN.glb OUT.glb
//   node tools/anim/gltf_codec.mjs encode IN.glb OUT.glb
//
// Deps (pinned, install anywhere on NODE_PATH or next to this file):
//   npm i @gltf-transform/core@4.1.1 @gltf-transform/extensions@4.1.1 \
//         @gltf-transform/functions@4.1.1 meshoptimizer@0.22.0
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dequantize, meshopt, prune, unpartition } from '@gltf-transform/functions';
import { MeshoptDecoder, MeshoptEncoder } from 'meshoptimizer';

const [, , mode, inp, out] = process.argv;
if (!['decode', 'encode'].includes(mode) || !inp || !out) {
  console.error('usage: node gltf_codec.mjs decode|encode IN.glb OUT.glb');
  process.exit(2);
}
await MeshoptDecoder.ready;
await MeshoptEncoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'meshopt.decoder': MeshoptDecoder, 'meshopt.encoder': MeshoptEncoder,
});
const doc = await io.read(inp);
if (mode === 'decode') {
  await doc.transform(dequantize());
  for (const ext of doc.getRoot().listExtensionsUsed()) {
    if (['EXT_meshopt_compression', 'KHR_mesh_quantization'].includes(ext.extensionName)) ext.dispose();
  }
  // a meshopt GLB carries a fallback buffer next to the main one; GLB holds one buffer, so merge them (Diablo's
  // model-rigged.glb failed with "GLB must have 0-1 buffers", 2026-11-01 rig audit)
  await doc.transform(unpartition());
} else {
  // keepSolidTextures: prune() otherwise folds a one-colour texture into the material factor, and a solid WHITE
  // texture (Rahkasa's hair, 2026-10-24) becomes the default factor, which the material gate reads as "no colour
  // authored" and quarantines the fighter. Keep the artist's texture as it is.
  await doc.transform(prune({ keepSolidTextures: true }), meshopt({ encoder: MeshoptEncoder, level: 'medium' }));
}
await io.write(out, doc);
console.log(`${mode} ok -> ${out}`);

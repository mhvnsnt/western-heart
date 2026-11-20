// Encode WITHOUT prune(): gltf-transform 4.1.1 prune() drops TextureInfo.texCoord
// and the TEXCOORD_1 attribute it then considers unused (measured on the Megami
// graft: 8 texCoord=1 slots on GP_Torso-1/GP_Torso_Back-1 + TEXCOORD_1 lost).
// meshopt() alone preserves both. Same EXT_meshopt_compression output format
// as tools/anim/gltf_codec.mjs encode, minus the prune step.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { meshopt } from '@gltf-transform/functions';
import { MeshoptDecoder, MeshoptEncoder } from 'meshoptimizer';
const [, , inp, out] = process.argv;
await MeshoptDecoder.ready; await MeshoptEncoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'meshopt.decoder': MeshoptDecoder, 'meshopt.encoder': MeshoptEncoder });
const doc = await io.read(inp);
await doc.transform(meshopt({ encoder: MeshoptEncoder, level: 'medium' }));
await io.write(out, doc);
console.log('encode-meshopt-only ok ->', out);

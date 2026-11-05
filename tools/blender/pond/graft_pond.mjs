// graft_pond.mjs — put Pond's source-rebuilt meshes on the ORIGINAL WH 52-joint skeleton.
//
//   node graft_pond.mjs [BASE.glb] [SRC.glb] [OUT.plain.glb]
//   defaults: shipped/model-rigged.plain.glb, build/pond_src_export.glb, build/model-rigged-textured.plain.glb
// Then encode with the repo codec:
//   node <wh>/tools/anim/gltf_codec.mjs encode build/model-rigged-textured.plain.glb build/model-rigged-textured.glb
//
// Base keeps: scene, root WH_Skeleton, all 52 joint nodes (names/order/TRS), skin 0 and its inverseBindMatrices.
// Base loses: every mesh node, mesh, material, texture (incl. Penis Mesh0000_004 / Bulge Mesh0000_003).
// Source gives: primitives (indices, POSITION, NORMAL, TEXCOORD_0, JOINTS_0, WEIGHTS_0, morph targets),
//   materials, textures, images. Its skin / joint nodes / scene are discarded.
// JOINTS_0 is remapped source-joint-index -> base-joint-index BY JOINT NAME.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { copyToDocument, prune, unpartition } from '@gltf-transform/functions';
import { MeshoptDecoder, MeshoptEncoder } from 'meshoptimizer';

const [BASE = 'shipped/model-rigged.plain.glb', SRC = 'build/pond_src_export.glb',
  OUT = 'build/model-rigged-textured.plain.glb'] = process.argv.slice(2);
await MeshoptDecoder.ready; await MeshoptEncoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS)
  .registerDependencies({ 'meshopt.decoder': MeshoptDecoder, 'meshopt.encoder': MeshoptEncoder });
const base = await io.read(BASE);
const src = await io.read(SRC);
const bR = base.getRoot(), sR = src.getRoot();
if (bR.listSkins().length !== 1 || sR.listSkins().length !== 1) throw new Error('expected exactly one skin in base and source');
const bSkin = bR.listSkins()[0], sSkin = sR.listSkins()[0];
const bNames = bSkin.listJoints().map((j) => j.getName());
const sNames = sSkin.listJoints().map((j) => j.getName());
if (new Set(bNames).size !== bNames.length) throw new Error('duplicate base joint names');
const remap = sNames.map((n) => { const i = bNames.indexOf(n); if (i < 0) throw new Error('joint not in base: ' + n); return i; });
console.log('joints base', bNames.length, 'src', sNames.length, 'reordered', remap.some((v, i) => v !== i));

// --- 1. strip base meshes (nodes, meshes, materials, textures) ---
const meshParents = new Set();
for (const n of bR.listNodes()) if (n.getMesh()) {
  if (n.listChildren().length) throw new Error('mesh node with children: ' + n.getName());
  meshParents.add(n.getParentNode()); n.dispose();
}
for (const m of bR.listMeshes()) m.dispose();
for (const m of bR.listMaterials()) m.dispose();
for (const t of bR.listTextures()) t.dispose();
if (meshParents.size !== 1) throw new Error('base mesh nodes had several parents');
const parent = [...meshParents][0];
console.log('mesh parent', parent ? parent.getName() : '(scene)');

// --- 2. copy source meshes (+ materials/textures/images/accessors they reference) ---
const sMeshNodes = sR.listNodes().filter((n) => n.getMesh());
for (const n of sMeshNodes) {
  const id = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
  const w = n.getWorldMatrix();
  if (w.some((v, i) => Math.abs(v - id[i]) > 1e-6)) throw new Error('source mesh node not identity: ' + n.getName());
  if (n.getSkin() !== sSkin) throw new Error('source mesh node not on source skin: ' + n.getName());
}
const map = copyToDocument(base, src, sMeshNodes.map((n) => n.getMesh()));
const bScene = bR.listScenes()[0];
const remapped = new Set();
for (const sn of sMeshNodes) {
  const mesh = map.get(sn.getMesh());
  for (const p of mesh.listPrimitives()) {
    // drop anything beyond what the game needs (source had COLOR_n sets on the body in an earlier build)
    for (const sem of p.listSemantics()) if (!['POSITION', 'NORMAL', 'TEXCOORD_0', 'JOINTS_0', 'WEIGHTS_0'].includes(sem)) p.setAttribute(sem, null);
    const J = p.getAttribute('JOINTS_0');
    if (!J || !p.getAttribute('WEIGHTS_0')) throw new Error('prim without skin attrs in ' + sn.getName());
    if (remapped.has(J)) continue; remapped.add(J);
    const a = J.getArray(); for (let i = 0; i < a.length; i++) a[i] = remap[a[i]]; J.setArray(a);
  }
  const node = base.createNode(sn.getName()).setMesh(mesh).setSkin(bSkin);
  if (parent) parent.addChild(node); else bScene.addChild(node);
}
// unused accessors / leftovers only; keepSolidTextures as the repo codec does
await base.transform(prune({ keepSolidTextures: true, propertyTypes: ['ACCESSOR', 'TEXTURE', 'MATERIAL', 'MESH'] }));
await base.transform(unpartition()); // copied accessors came with the source's buffer; GLB holds one
await io.write(OUT, base);
console.log('wrote', OUT, 'meshes', bR.listMeshes().map((m) => m.getName()).join(','));

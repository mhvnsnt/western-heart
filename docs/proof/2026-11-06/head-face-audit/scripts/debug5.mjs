// Debug5: which bones influence head-region verts, and how far each bone's world
// rotation travels during a heavy clip (the divergence that shears the skin).
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const HERE = dirname(fileURLToPath(import.meta.url));
const WH = join(HERE, 'wh');
await import(join(WH, 'tools/anim/node_game_env.mjs'));
const THREE = await import('three');
const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js');
const { MeshoptDecoder } = await import('three/addons/libs/meshopt_decoder.js');
const { clone: skeletonClone } = await import('three/addons/utils/SkeletonUtils.js');
const T = await import(join(WH, 'game/js/t3anims.js'));
globalThis.self = globalThis;
function stripTextures(buf) {
  const dv = new DataView(buf.buffer, buf.byteOffset, buf.byteLength);
  const jlen = dv.getUint32(12, true);
  const gltf = JSON.parse(new TextDecoder().decode(buf.subarray(20, 20 + jlen)));
  delete gltf.textures; delete gltf.images; delete gltf.samplers;
  if (gltf.materials) gltf.materials = gltf.materials.map(() => ({}));
  const jbuf = new TextEncoder().encode(JSON.stringify(gltf));
  const pad = (4 - (jbuf.length % 4)) % 4;
  const binOff = 20 + jlen; const binLen = dv.getUint32(binOff, true);
  const total = 12 + 8 + jbuf.length + pad + 8 + binLen;
  const out = new Uint8Array(total); const odv = new DataView(out.buffer);
  odv.setUint32(0, 0x46546c67, true); odv.setUint32(4, 2, true); odv.setUint32(8, total, true);
  odv.setUint32(12, jbuf.length + pad, true); odv.setUint32(16, 0x4e4f534a, true);
  out.set(jbuf, 20); for (let i = 0; i < pad; i++) out[20 + jbuf.length + i] = 0x20;
  odv.setUint32(20 + jbuf.length + pad, binLen, true); odv.setUint32(24 + jbuf.length + pad, 0x004e4942, true);
  out.set(buf.subarray(binOff + 8, binOff + 8 + binLen), 28 + jbuf.length + pad);
  return out.buffer;
}
const loader = new GLTFLoader(); loader.setMeshoptDecoder(MeshoptDecoder);
const [key, bank] = [process.argv[2], process.argv[3]];
const buf = readFileSync(join(HERE, 'glb', key + '.glb'));
const gltf = await loader.parseAsync(stripTextures(buf), '');
const model = new THREE.Group(); model.add(skeletonClone(gltf.scene));
model.updateMatrixWorld(true);
const byC = (cn) => { let h = null; model.traverse((o) => { if (!h && o.isBone && T.canonBoneName(o.name) === cn) h = o; }); return h; };
const head = byC('Head');
const influence = new Map(); // boneName -> {verts, maxW}
model.traverse((o) => {
  if (!o.isSkinnedMesh || !o.skeleton) return;
  const bi = o.skeleton.bones.indexOf(head); if (bi < 0) return;
  const pos = o.geometry.attributes.position, si = o.geometry.attributes.skinIndex, sw = o.geometry.attributes.skinWeight;
  const headW = head.getWorldPosition(new THREE.Vector3());
  let mh2 = 0; model.traverse((oo) => { if (oo.isBone) mh2 = Math.max(mh2, oo.getWorldPosition(new THREE.Vector3()).y); });
  const vv = new THREE.Vector3();
  for (let i = 0; i < pos.count; i++) {
    vv.fromBufferAttribute(pos, i); o.applyBoneTransform(i, vv);
    const wp = vv.clone().applyMatrix4(o.matrixWorld);
    if (wp.distanceTo(headW) > 0.30 * mh2) continue;
    for (let k = 0; k < 4; k++) {
      const b = o.skeleton.bones[si.getComponent(i, k)]; const w = sw.getComponent(i, k);
      if (!b || w < 0.05) continue;
      const e = influence.get(b.name) || { verts: 0, maxW: 0, canon: T.canonBoneName(b.name), bone: b, parent: b.parent ? b.parent.name : null };
      e.verts++; e.maxW = Math.max(e.maxW, w); influence.set(b.name, e);
    }
  }
});
const clips = await T.loadT3Clips(THREE, bank);
const rc = T.retargetT3Clips(clips, bank, model, THREE, key);
const mixer = new THREE.AnimationMixer(model);
const restW = new Map();
for (const [, e] of influence) restW.set(e.bone, e.bone.getWorldQuaternion(new THREE.Quaternion()));
const clip = rc.heavy || rc.medium;
const act = mixer.clipAction(clip); act.setLoop(THREE.LoopRepeat, Infinity); act.play();
const travel = new Map();
for (let f = 0; f <= 20; f++) {
  mixer.setTime((f / 20) * clip.duration * 0.9); model.updateMatrixWorld(true);
  for (const [, e] of influence) {
    const d = e.bone.getWorldQuaternion(new THREE.Quaternion()).multiply(restW.get(e.bone).clone().invert());
    const a = 2 * Math.acos(Math.min(1, Math.abs(d.w))) * 180 / Math.PI;
    travel.set(e.bone, Math.max(travel.get(e.bone) || 0, a));
  }
}
console.log(`${key} head-region influences (clip=${clip.name}):`);
for (const [name, e] of [...influence.entries()].sort((a, b) => b[1].verts - a[1].verts)) {
  console.log(`  ${name} canon=${e.canon} parent=${e.parent} verts=${e.verts} maxW=${e.maxW.toFixed(2)} worldRotTravel=${(travel.get(e.bone) || 0).toFixed(1)}deg`);
}

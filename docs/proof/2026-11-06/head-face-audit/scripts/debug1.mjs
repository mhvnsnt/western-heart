// Debug: signed face-forward yaw/pitch per frame for one fighter's stance.
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
const head = byC('Head'), neck = byC('Neck'), hips = byC('Hips');
const wp = (o) => o.getWorldPosition(new THREE.Vector3());
const wq = (o) => o.getWorldQuaternion(new THREE.Quaternion());
// head verts
const pts = [];
model.traverse((o) => {
  if (!o.isSkinnedMesh || !o.skeleton) return;
  const bi = o.skeleton.bones.indexOf(head); if (bi < 0) return;
  const pos = o.geometry.attributes.position, si = o.geometry.attributes.skinIndex, sw = o.geometry.attributes.skinWeight;
  const v = new THREE.Vector3();
  for (let i = 0; i < pos.count; i++) {
    let w = 0; for (let k = 0; k < 4; k++) if (si.getComponent(i, k) === bi) w = sw.getComponent(i, k);
    if (w >= 0.5) { v.fromBufferAttribute(pos, i); o.applyBoneTransform(i, v); pts.push(v.clone().applyMatrix4(o.matrixWorld)); }
  }
});
const J = wp(head), N = wp(neck);
const C = pts.reduce((a, p) => a.add(p), new THREE.Vector3()).multiplyScalar(1 / pts.length);
const up = J.clone().sub(N).normalize();
const d = C.clone().sub(J);
const f = d.clone().sub(up.clone().multiplyScalar(d.dot(up))).normalize();
console.log(key, 'headVerts', pts.length, 'J', J.toArray().map(x=>+x.toFixed(3)), 'N', N.toArray().map(x=>+x.toFixed(3)));
console.log('centroid', C.toArray().map(x=>+x.toFixed(3)), 'fRest', f.toArray().map(x=>+x.toFixed(3)), 'd', d.toArray().map(x=>+x.toFixed(3)));
const qRest = wq(head);
const clips = await T.loadT3Clips(THREE, bank);
const rc = T.retargetT3Clips(clips, bank, model, THREE, key);
const mixer = new THREE.AnimationMixer(model);
const act = mixer.clipAction(rc.stance); act.setLoop(THREE.LoopRepeat, Infinity); act.play();
const n = Math.round(rc.stance.duration * 30);
for (let fr = 0; fr < n; fr += 3) {
  mixer.setTime((fr / 30) % rc.stance.duration);
  model.updateMatrixWorld(true);
  const fn = f.clone().applyQuaternion(wq(head).multiply(qRest.clone().invert()));
  const yaw = Math.atan2(fn.x, fn.z) * 180 / Math.PI;
  const pitch = Math.asin(Math.max(-1, Math.min(1, fn.y))) * 180 / Math.PI;
  const relH = wq(hips).invert().multiply(wq(head));
  console.log(`f${fr} faceYaw=${yaw.toFixed(1)} facePitch=${pitch.toFixed(1)}`);
}

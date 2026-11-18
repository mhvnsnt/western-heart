// Debug2: world-delta decomposition (yaw/pitch/roll) for Hips/Chest/Neck/Head during stance.
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
const [key, bank, action] = [process.argv[2], process.argv[3], process.argv[4] || 'stance'];
const buf = readFileSync(join(HERE, 'glb', key + '.glb'));
const gltf = await loader.parseAsync(stripTextures(buf), '');
const model = new THREE.Group(); model.add(skeletonClone(gltf.scene));
model.updateMatrixWorld(true);
const byC = (cn) => { let h = null; model.traverse((o) => { if (!h && o.isBone && T.canonBoneName(o.name) === cn) h = o; }); return h; };
const wq = (o) => o.getWorldQuaternion(new THREE.Quaternion());
const bones = {};
for (const cn of ['Hips', 'Spine', 'Spine1', 'Spine2', 'Chest', 'Neck', 'Head']) { const b = byC(cn); if (b) bones[cn] = b; }
console.log(key, 'bones:', Object.entries(bones).map(([k, b]) => `${k}=${b.name}`).join(' '));
const rest = {}; for (const [k, b] of Object.entries(bones)) rest[k] = wq(b);
function ypr(q) {
  const e = new THREE.Euler().setFromQuaternion(q, 'YXZ');
  return `y=${(e.y * 180 / Math.PI).toFixed(1)} p=${(e.x * 180 / Math.PI).toFixed(1)} r=${(e.z * 180 / Math.PI).toFixed(1)}`;
}
console.log('REST world:', Object.entries(rest).map(([k, q]) => `${k}[${ypr(q)}]`).join(' '));
const clips = await T.loadT3Clips(THREE, bank);
const rc = T.retargetT3Clips(clips, bank, model, THREE, key);
const mixer = new THREE.AnimationMixer(model);
const act = mixer.clipAction(rc[action]); act.setLoop(THREE.LoopRepeat, Infinity); act.play();
const n = Math.round(rc[action].duration * 30);
for (let fr = 0; fr < n; fr += Math.max(1, Math.floor(n / 6))) {
  mixer.setTime((fr / 30) % rc[action].duration);
  model.updateMatrixWorld(true);
  const parts = [];
  for (const [k, b] of Object.entries(bones)) {
    const delta = wq(b).multiply(rest[k].clone().invert());
    parts.push(`${k}[${ypr(delta)}]`);
  }
  console.log(`f${fr}`, parts.join(' '));
}
// source clip's own G rotations at frame 0 (world, identity rest)
const skel = T.getT3Skeleton(bank);
const raw = clips[action].userData.raw;
const par = {}; for (const j of skel.joints) par[j.name] = j.parent;
const G = {};
for (const j of skel.joints) {
  const q = new THREE.Quaternion(); const r = raw.rot[j.name];
  if (r && r.length) q.set(r[0][0], r[0][1], r[0][2], r[0][3]);
  if (par[j.name] && G[par[j.name]]) q.premultiply(G[par[j.name]]);
  G[j.name] = q;
}
console.log('SRC f0 world:', ['Hips', 'Chest', 'Neck', 'Head'].map((k) => `${k}[${ypr(G[k])}]`).join(' '));

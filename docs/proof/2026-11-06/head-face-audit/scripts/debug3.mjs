// Debug3: head world-delta (yaw/pitch/roll) stats across ROW clips for one fighter+bank.
// Usage: node debug3.mjs <key> <bank> [maxRows]
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
const maxRows = +(process.argv[4] || 24);
const buf = readFileSync(join(HERE, 'glb', key + '.glb'));
const gltf = await loader.parseAsync(stripTextures(buf), '');
const model = new THREE.Group(); model.add(skeletonClone(gltf.scene));
model.updateMatrixWorld(true);
const byC = (cn) => { let h = null; model.traverse((o) => { if (!h && o.isBone && T.canonBoneName(o.name) === cn) h = o; }); return h; };
const head = byC('Head'), chest = byC('Chest') || byC('Spine2');
const wq = (o) => o.getWorldQuaternion(new THREE.Quaternion());
const restH = wq(head), restC = wq(chest);
const clips = await T.loadT3Clips(THREE, bank);
T.retargetT3Clips(clips, bank, model, THREE, key); // bind call (estimates + caches)
const rowNames = Object.keys(clips).filter((n) => n.startsWith('row:')).slice(0, maxRows);
console.log(key, bank, 'rows sampled:', rowNames.length);
const mixer = new THREE.AnimationMixer(model);
for (const rn of rowNames) {
  const rc = T.retargetT3Clips(clips, bank, model, THREE, key, [rn]);
  const clip = rc && rc[rn]; if (!clip) { console.log(rn, 'no retarget'); continue; }
  const act = mixer.clipAction(clip); act.setLoop(THREE.LoopRepeat, Infinity); act.play();
  const n = Math.max(2, Math.round(clip.duration * 30));
  const yaws = [], pitches = [];
  for (let f = 0; f < n; f += 2) {
    mixer.setTime((f / 30) % clip.duration);
    model.updateMatrixWorld(true);
    const dh = wq(head).multiply(restH.clone().invert());
    const dc = wq(chest).multiply(restC.clone().invert());
    const rel = dc.clone().invert().multiply(dh);
    const e = new THREE.Euler().setFromQuaternion(rel, 'YXZ');
    yaws.push(e.y * 180 / Math.PI); pitches.push(e.x * 180 / Math.PI);
  }
  mixer.stopAllAction();
  const mean = (a) => a.reduce((x, y) => x + y, 0) / a.length;
  console.log(`${rn}: head-vs-chest delta yaw mean=${mean(yaws).toFixed(1)} pitch mean=${mean(pitches).toFixed(1)} (target-frame, rest-relative)`);
}

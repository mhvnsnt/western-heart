// Debug4: REAL skinning distortion of head-region vertices + embedded scale-track values.
// Distortion = pairwise distance change among head-influenced verts, rest vs posed (skinned
// through the actual bone pose via applyBoneTransform). A rigid head region scores ~0.
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
// embedded scale tracks on head/neck
for (const a of gltf.animations || []) {
  for (const tr of a.tracks) {
    if (tr.name.endsWith('.scale') && /head|neck/i.test(tr.name)) {
      const v = tr.values; let mn = Infinity, mx = -Infinity;
      for (let i = 0; i < v.length; i++) { mn = Math.min(mn, v[i]); mx = Math.max(mx, v[i]); }
      console.log(`EMB ${key} ${a.name} ${tr.name} scale range ${mn.toFixed(3)}..${mx.toFixed(3)}`);
    }
  }
}
const model = new THREE.Group(); model.add(skeletonClone(gltf.scene));
model.updateMatrixWorld(true);
const byC = (cn) => { let h = null; model.traverse((o) => { if (!h && o.isBone && T.canonBoneName(o.name) === cn) h = o; }); return h; };
const head = byC('Head');
// collect head-region verts: (mesh, index) with Head weight >= 0.25, plus their rest skinned positions (model space)
const region = [];
const inv = new THREE.Matrix4().copy(model.matrix).invert();
model.traverse((o) => {
  if (!o.isSkinnedMesh || !o.skeleton) return;
  const bi = o.skeleton.bones.indexOf(head); if (bi < 0) return;
  const pos = o.geometry.attributes.position, si = o.geometry.attributes.skinIndex, sw = o.geometry.attributes.skinWeight;
  const v = new THREE.Vector3();
  const headW = head.getWorldPosition(new THREE.Vector3());
  let mh = 0; model.traverse((oo) => { if (oo.isBone) mh = Math.max(mh, oo.getWorldPosition(new THREE.Vector3()).y); });
  for (let i = 0; i < pos.count; i++) {
    let w = 0, dom = true;
    for (let k = 0; k < 4; k++) { const ww = sw.getComponent(i, k); if (si.getComponent(i, k) === bi) w = ww; else if (ww > w) dom = false; }
    v.fromBufferAttribute(pos, i); o.applyBoneTransform(i, v);
    const wp = v.clone().applyMatrix4(o.matrixWorld).applyMatrix4(inv);
    if (w >= 0.25 && dom && wp.distanceTo(headW) < 0.13 * mh) region.push({ mesh: o, idx: i, rest: wp });
  }
});
console.log(key, 'head-region verts:', region.length);
const sample = region.filter((_, i) => i % Math.max(1, Math.floor(region.length / 42)) === 0).slice(0, 42);
const restD = [];
for (let i = 0; i < sample.length; i++) for (let j = i + 1; j < sample.length; j++) restD.push(sample[i].rest.distanceTo(sample[j].rest));
function distortion() {
  const v = new THREE.Vector3();
  const posed = sample.map((s) => { v.fromBufferAttribute(s.mesh.geometry.attributes.position, s.idx); s.mesh.applyBoneTransform(s.idx, v); return v.clone().applyMatrix4(s.mesh.matrixWorld).applyMatrix4(inv); });
  let sum = 0, mx = 0, idx = 0, cnt = 0;
  for (let i = 0; i < posed.length; i++) for (let j = i + 1; j < posed.length; j++) {
    const rd = restD[idx++]; if (rd < 1e-4) continue;
    const d = Math.abs(posed[i].distanceTo(posed[j]) - rd) / rd;
    sum += d; mx = Math.max(mx, d); cnt++;
  }
  return { meanPct: +(100 * sum / cnt).toFixed(2), maxPct: +(100 * mx).toFixed(2) };
}
const clips = await T.loadT3Clips(THREE, bank);
const rc0 = T.retargetT3Clips(clips, bank, model, THREE, key);
const mixer = new THREE.AnimationMixer(model);
const targets = ['stance', 'light', 'medium', 'heavy'];
const rowNames = Object.keys(clips).filter((n) => n.startsWith('row:')).slice(0, 6);
for (const rn of rowNames) T.retargetT3Clips(clips, bank, model, THREE, key, [rn]);
const rc = T.retargetT3Clips(clips, bank, model, THREE, key, [...targets.filter(t=>rc0[t]), ...rowNames]);
for (const name of [...targets, ...rowNames]) {
  const clip = (rc && rc[name]) || rc0[name]; if (!clip) continue;
  const act = mixer.clipAction(clip); act.setLoop(THREE.LoopRepeat, Infinity); act.play();
  const times = [0.15, 0.4, 0.65, 0.9];
  const ds = times.map((t) => { mixer.setTime(t * clip.duration); model.updateMatrixWorld(true); return distortion(); });
  mixer.stopAllAction();
  console.log(`${key} ${name}: distortion mean% [${ds.map((d) => d.meanPct).join(', ')}] max% [${ds.map((d) => d.maxPct).join(', ')}]`);
}

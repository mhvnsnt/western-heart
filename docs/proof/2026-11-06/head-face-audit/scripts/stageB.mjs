// Stage B: run the REAL retarget pipeline (game/js/t3anims.js) on real GLBs in Node.
// Measures per frame, per clip:
//  - head-vs-chest relative rotation: retargeted vs SOURCE bank clip (artifact deviation)
//  - geometric face-forward yaw/pitch vs the model's facing (+Z in instance space)
//  - head-vertex non-rigidity (stretch): pairwise distances of head verts (weight>=0.9), rest vs posed
//  - head bone world-matrix shear (column-norm ratio)
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

const CASES = [
  { key: 'kinpo', glb: 'kinpo.glb', bank: 'jin' },
  { key: 'zui', glb: 'zui.glb', bank: 'jin' },
  { key: 'yukihyo', glb: 'yukihyo.glb', bank: 'king' },
  { key: 'pantera', glb: 'pantera.glb', bank: 'king' },
  { key: 'demonio', glb: 'demonio.glb', bank: 'jin' },
  { key: 'dio', glb: 'dio.glb', bank: 'heihachi' },
  { key: 'chatur', glb: 'chatur.glb', bank: 'ogre' },
];
const only = process.argv[2] ? process.argv[2].split(',') : null;

globalThis.self = globalThis;
const loader = new GLTFLoader();
loader.setMeshoptDecoder(MeshoptDecoder);

// Strip textures/images/materials from a GLB buffer (geometry/skins/nodes untouched):
// GLTFLoader's texture path needs browser image APIs that Node lacks, and the audit
// measures bones + skinned vertices only.
function stripTextures(buf) {
  const dv = new DataView(buf.buffer, buf.byteOffset, buf.byteLength);
  const jlen = dv.getUint32(12, true);
  const gltf = JSON.parse(new TextDecoder().decode(buf.subarray(20, 20 + jlen)));
  delete gltf.textures; delete gltf.images; delete gltf.samplers;
  if (gltf.materials) gltf.materials = gltf.materials.map(() => ({}));
  const jbuf = new TextEncoder().encode(JSON.stringify(gltf));
  const pad = (4 - (jbuf.length % 4)) % 4;
  const binOff = 20 + jlen;
  const binLen = dv.getUint32(binOff, true);
  const total = 12 + 8 + jbuf.length + pad + 8 + binLen;
  const out = new Uint8Array(total);
  const odv = new DataView(out.buffer);
  odv.setUint32(0, 0x46546c67, true); odv.setUint32(4, 2, true); odv.setUint32(8, total, true);
  odv.setUint32(12, jbuf.length + pad, true); odv.setUint32(16, 0x4e4f534a, true);
  out.set(jbuf, 20); for (let i = 0; i < pad; i++) out[20 + jbuf.length + i] = 0x20;
  odv.setUint32(20 + jbuf.length + pad, binLen, true); odv.setUint32(24 + jbuf.length + pad, 0x004e4942, true);
  out.set(buf.subarray(binOff + 8, binOff + 8 + binLen), 28 + jbuf.length + pad);
  return out.buffer;
}

function boneByCanon(model, canonName) {
  let hit = null;
  model.traverse((o) => { if (!hit && o.isBone && T.canonBoneName(o.name) === canonName) hit = o; });
  return hit;
}
const wp = (o) => o.getWorldPosition(new THREE.Vector3());
const wq = (o) => o.getWorldQuaternion(new THREE.Quaternion());

// source head/chest world quats per frame from a bank clip's raw data + skeleton
function sourceRel(clip, skel) {
  const raw = clip.userData.raw;
  const order = skel.joints.map((j) => j.name);
  const par = {}; for (const j of skel.joints) par[j.name] = j.parent;
  let n = 0; for (const j of order) if (raw.rot[j]) n = Math.max(n, raw.rot[j].length);
  const rel = [], Gw = {};
  for (let f = 0; f < n; f++) {
    for (const j of order) {
      const q = new THREE.Quaternion();
      const r = raw.rot[j];
      if (r && r.length) { const v = r[Math.min(f, r.length - 1)]; q.set(v[0], v[1], v[2], v[3]); }
      const p = par[j];
      if (p && Gw[p]) q.premultiply(Gw[p]);
      Gw[j] = q;
    }
    if (Gw.Head && Gw.Chest) rel.push(Gw.Chest.clone().invert().multiply(Gw.Head));
    else rel.push(null);
  }
  return rel;
}

function headVerts(model, headBone) {
  // vertices dominated by the head bone (weight >= 0.9), in model space at rest
  const pts = [];
  model.updateMatrixWorld(true);
  const inv = new THREE.Matrix4().copy(model.matrix).invert();
  model.traverse((o) => {
    if (!o.isSkinnedMesh || !o.skeleton) return;
    const bi = o.skeleton.bones.indexOf(headBone);
    if (bi < 0) return;
    const pos = o.geometry.attributes.position, si = o.geometry.attributes.skinIndex, sw = o.geometry.attributes.skinWeight;
    if (!si || !sw) return;
    const v = new THREE.Vector3();
    for (let i = 0; i < pos.count; i++) {
      let w = 0;
      for (let k = 0; k < 4; k++) if (si.getX(i + 0) !== undefined && si.getComponent(i, k) === bi) w = sw.getComponent(i, k);
      if (w >= 0.9) { v.fromBufferAttribute(pos, i); o.applyBoneTransform(i, v); v.applyMatrix4(o.matrixWorld).applyMatrix4(inv); pts.push(v.clone()); }
    }
  });
  return pts;
}

const results = {};
for (const c of CASES) {
  if (only && !only.includes(c.key)) continue;
  const buf = readFileSync(join(HERE, 'glb', c.glb));
  const gltf = await loader.parseAsync(stripTextures(buf), '');
  const inner = skeletonClone(gltf.scene);
  const model = new THREE.Group();
  model.add(inner);
  model.updateMatrixWorld(true);
  const head = boneByCanon(model, 'Head'), neck = boneByCanon(model, 'Neck');
  const chest = boneByCanon(model, 'Chest') || boneByCanon(model, 'Spine2');
  if (!head || !chest) { console.log(c.key, 'NO head/chest'); continue; }
  // rest geometry: face-forward from head-dominated vertices
  const hv = headVerts(model, head);
  const J = wp(head), Np = neck ? wp(neck) : wp(chest);
  let fRest = null, restCentroid = null;
  if (hv.length >= 20) {
    restCentroid = hv.reduce((a, p) => a.add(p), new THREE.Vector3()).multiplyScalar(1 / hv.length);
    const up = J.clone().sub(Np).normalize();
    const d = restCentroid.clone().sub(J);
    fRest = d.clone().sub(up.clone().multiplyScalar(d.dot(up)));
    if (fRest.length() > 1e-4) fRest.normalize(); else fRest = null;
  }
  const qHeadRest = wq(head);
  // pairwise rest distances among up to 36 sampled head verts
  const sample = hv.filter((_, i) => i % Math.max(1, Math.floor(hv.length / 36)) === 0).slice(0, 36);
  const restD = [];
  for (let i = 0; i < sample.length; i++) for (let j = i + 1; j < sample.length; j++) restD.push(sample[i].distanceTo(sample[j]));
  // retarget
  const clips = await T.loadT3Clips(THREE, c.bank);
  if (!clips) { console.log(c.key, 'bank load failed', c.bank); continue; }
  const skel = T.getT3Skeleton(c.bank);
  const rc = T.retargetT3Clips(clips, c.bank, model, THREE, c.key);
  if (!rc) { console.log(c.key, 'retarget returned null'); continue; }
  const per = {};
  for (const action of ['stance', 'light', 'medium', 'heavy', 'grab', 'hit', 'walkFwd']) {
    const clip = rc[action]; if (!clip) continue;
    const srcRel = sourceRel(clips[action], skel);
    const mixer = new THREE.AnimationMixer(model);
    const act = mixer.clipAction(clip);
    act.setLoop(THREE.LoopRepeat, Infinity); act.play();
    const n = Math.max(2, Math.round(clip.duration * 30));
    let devMax = 0, devSum = 0, yawAbs = [], pitchAbs = [], shearMax = 1, stretchMean = 0, stretchMax = 0, frames = 0;
    const m4 = new THREE.Matrix4(), col = [new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3()];
    for (let f = 0; f < n; f++) {
      mixer.setTime((f / 30) % clip.duration);
      model.updateMatrixWorld(true);
      const qh = wq(head), qc = wq(chest);
      const relT = qc.clone().invert().multiply(qh);
      const sr = srcRel[Math.min(f, srcRel.length - 1)];
      if (sr) { const d = relT.angleTo(sr) * 180 / Math.PI; devMax = Math.max(devMax, d); devSum += d; }
      if (fRest) {
        const fn = fRest.clone().applyQuaternion(qh.clone().multiply(qHeadRest.clone().invert()));
        yawAbs.push(Math.abs(Math.atan2(fn.x, fn.z) * 180 / Math.PI));
        pitchAbs.push(Math.abs(Math.asin(Math.max(-1, Math.min(1, fn.y))) * 180 / Math.PI));
      }
      m4.copy(head.matrixWorld);
      for (let k = 0; k < 3; k++) col[k].setFromMatrixColumn(m4, k);
      const lens = col.map((v) => v.length());
      shearMax = Math.max(shearMax, Math.max(...lens) / Math.min(...lens));
      // stretch on sampled head verts
      if (sample.length >= 8 && f % 3 === 0) {
        const posed = sample.map((p) => p.clone());
        // recompute posed positions: find each sample's source vertex again is costly;
        // instead use bone-space: verts are head-rigid, so posed = headWorld * headRest^-1 * p (model space)
        const M = new THREE.Matrix4().compose(wp(head), qh, new THREE.Vector3(1, 1, 1))
          .multiply(new THREE.Matrix4().compose(J, qHeadRest, new THREE.Vector3(1, 1, 1)).invert());
        let s = 0, mx = 0, cnt = 0, idx = 0;
        for (let i = 0; i < posed.length; i++) posed[i].applyMatrix4(M);
        for (let i = 0; i < posed.length; i++) for (let j = i + 1; j < posed.length; j++) {
          const rd = restD[idx++]; if (rd < 1e-5) continue;
          const rel = Math.abs(posed[i].distanceTo(posed[j]) - rd) / rd;
          s += rel; mx = Math.max(mx, rel); cnt++;
        }
        if (cnt) { stretchMean += s / cnt; stretchMax = Math.max(stretchMax, mx); }
      }
      frames++;
    }
    const avg = (a) => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
    per[action] = {
      frames, devFromSourceDeg: { max: +devMax.toFixed(1), mean: +(devSum / frames).toFixed(1) },
      faceYawAbsDeg: { mean: avg(yawAbs) !== null ? +avg(yawAbs).toFixed(1) : null, max: yawAbs.length ? +Math.max(...yawAbs).toFixed(1) : null },
      facePitchAbsDeg: { mean: avg(pitchAbs) !== null ? +avg(pitchAbs).toFixed(1) : null, max: pitchAbs.length ? +Math.max(...pitchAbs).toFixed(1) : null },
      headShearMax: +shearMax.toFixed(3),
    };
    mixer.stopAllAction();
  }
  results[c.key] = { bank: c.bank, headVerts: hv.length, hasFaceVec: !!fRest, clips: per };
  console.log(JSON.stringify({ [c.key]: results[c.key] }, null, 1));
}
import { writeFileSync } from 'node:fs';
writeFileSync(join(HERE, 'stageB_results.json'), JSON.stringify(results, null, 1));

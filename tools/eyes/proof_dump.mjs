// proof_dump.mjs — dump world-space head triangles (skinned + morphed body, fitted eyes) for a no-WebGL proof render.
// WebGL draws stall on the agent box, so the EYES phase proof is rasterised in software by tools/eyes/proof_render.py.
//   node tools/eyes/proof_dump.mjs <out.json>     (scenes listed in SCENES below)
import { writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const M = await import(join(ROOT, 'tools/eyes/build_eye_sockets.mjs'));
const THREE = await import('three');
const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js');
const FP = await import(join(ROOT, 'game/js/fitted-parts.js'));
const FE = await import(join(ROOT, 'game/js/fitted-eyes.js'));
const { applyMorphTargets } = await import(join(ROOT, 'game/js/morph-apply.js'));
import { readFileSync } from 'node:fs';

const SCENES = [
  { name: 'technician-natural-brown', tid: 'technician', eyes: { equipped: { EYES: 'wh-eye-natural' }, colors: { iris: '#5a3a22' } } },
  { name: 'striker-w-green-pupil-1.4', tid: 'striker-w', eyes: { equipped: { EYES: 'wh-eye-natural' }, colors: { iris: '#3f6e4a' }, eyes: { pupil: 1.4 } } },
  { name: 'super-heavyweight-blue', tid: 'super-heavyweight', eyes: { equipped: { EYES: 'wh-eye-natural' }, colors: { iris: '#2f5d8a' } } },
  { name: 'technician-sliders-size+spacing+height', tid: 'technician', morphs: { f_eye_size: 0.8, f_eye_space: 0.8, f_eye_h: 0.6 }, eyes: { equipped: { EYES: 'wh-eye-natural' }, colors: { iris: '#2f5d8a' } } },
  { name: 'technician-head-turn-35', tid: 'technician', turn: 35, eyes: { equipped: { EYES: 'wh-eye-natural' }, colors: { iris: '#5a3a22' } } },
  { name: 'athletic-w-red-sclera-dark', tid: 'athletic-w', eyes: { equipped: { EYES: 'wh-eye-natural' }, colors: { iris: '#8a2a2a', sclera: '#1a1a1a' }, eyes: { pupil: 0.6 } } },
];
const SKIN = '#c98d5e';
const matColor = (m) => {
  const n = (m && m.name) || '';
  if (/skin/i.test(n)) return SKIN; if (/teeth/i.test(n)) return '#eeeeee'; if (/tongue/i.test(n)) return '#a04a4a';
  if (/eyelash/i.test(n)) return '#1a1410'; if (/nails/i.test(n)) return '#d9a07a';
  return m && m.color ? '#' + m.color.getHexString() : '#888888';
};
const sceneData = [];
const ball = (await new GLTFLoader().parseAsync((() => { const b = readFileSync(join(ROOT, FE.EYEBALL_GLB)); return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength); })(), '')).scene;
const sockets = JSON.parse(readFileSync(join(ROOT, FE.EYE_SOCKETS_JSON), 'utf8'));
for (const sc of SCENES) {
  const inst = await M.templateInstance(sc.tid); const model = inst.model; const head = FP.findHeadBone(model);
  applyMorphTargets(model, sc.morphs || {});
  if (sc.turn) { head.rotateY(sc.turn * Math.PI / 180); }
  const cfg = FE.selectEyes(sc.eyes, sc.tid);
  FE.attachEyes(model, ball, sockets, cfg, { morphValues: sc.morphs || {} });
  model.updateMatrixWorld(true);
  const hp = new THREE.Vector3().setFromMatrixPosition(head.matrixWorld);
  const tris = [];
  model.traverse((o) => {
    if (!o.isMesh || !o.visible) return;
    for (let a = o; a; a = a.parent) if (a.visible === false) return;
    const g = o.geometry, pos = g.attributes.position, idx = g.index;
    const mp = g.morphAttributes.position, inf = o.morphTargetInfluences;
    const P = [];
    for (let i = 0; i < pos.count; i++) {
      const p = new THREE.Vector3().fromBufferAttribute(pos, i);
      if (mp && inf) inf.forEach((w, k) => { if (w) p.addScaledVector(new THREE.Vector3().fromBufferAttribute(mp[k], i), w); });
      if (o.isSkinnedMesh) o.applyBoneTransform(i, p);
      p.applyMatrix4(o.matrixWorld); P.push(p);
    }
    const col = matColor(o.material);
    const n = idx ? idx.count : pos.count;
    for (let t = 0; t < n; t += 3) {
      const a = idx ? idx.getX(t) : t, b = idx ? idx.getX(t + 1) : t + 1, c = idx ? idx.getX(t + 2) : t + 2;
      const A = P[a], B = P[b], C = P[c];
      if (A.y < hp.y - 0.12 && B.y < hp.y - 0.12) continue; // head + neck only
      tris.push([A.x, A.y, A.z, B.x, B.y, B.z, C.x, C.y, C.z, col]);
    }
  });
  const eyesC = []; model.traverse((o) => { if (o.userData.whFitted && o.userData.whFitted.slot === 'eyes') eyesC.push(new THREE.Vector3().setFromMatrixPosition(o.matrixWorld).toArray()); });
  sceneData.push({ name: sc.name, head: hp.toArray(), eyes: eyesC, tris });
}
writeFileSync(process.argv[2] || '/tmp/eyes-proof.json', JSON.stringify(sceneData));
console.log('scenes', sceneData.map((s) => s.name + ':' + s.tris.length).join(' '));

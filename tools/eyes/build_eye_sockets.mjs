// build_eye_sockets.mjs — author LEFT / RIGHT eye sockets for the 9 creation-suite template bodies
// (creation suite EYES phase, 2026-11-02).
//
//   node tools/eyes/build_eye_sockets.mjs            # writes customization/parts/eyes/eye-sockets.json
//   node tools/eyes/build_eye_sockets.mjs --check    # recompute and diff against the committed file (exit 1 on drift)
//
// Source data: the template GLBs themselves (customization/templates/meshes/<id>.glb, MB-Lab bakes). They have NO
// eye bones (skeleton = MB-Lab game rig: ... neck, head), but every template carries MB-Lab's own eyeball geometry
// (material MBlab_human_eyes = the sclera sphere, MBLab_Iris = the iris disc) skinned rigidly to the head, plus the
// baked face-slider morph targets ('f_eye_size+', 'f_eye_space-', ...; customization/templates/morph-sliders.json)
// on the same primitives. So each socket is MEASURED, not guessed:
//   centre  = mean of that side's sclera-sphere vertices (closed sphere -> mean is the centre)
//   radius  = mean distance of those vertices from the centre
//   forward = unit vector centre -> that side's iris-disc centroid (the gaze axis the fitted eyeball's +Z turns to)
// all in HEAD-BONE-LOCAL space, measured through the game's own instance path (game/js/assets.js createInstance,
// MB-Lab -> T3 bone remap), so the numbers are exactly what game/js/fitted-eyes.js parents to the Head bone.
// For every eye-region slider (Eye Size / Spacing / Height / Tilt / Opening / Almond) the same measurement is
// repeated with the '+' and '-' target at full weight and the DELTA stored, so the fitted eyeballs follow the face
// sliders linearly (dc = centre delta, dr = radius delta per unit slider).
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const THREE = await import('three');
const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js');
const { MeshoptDecoder } = await import('three/addons/libs/meshopt_decoder.js');
const A = await import(join(ROOT, 'game/js/assets.js'));
const FP = await import(join(ROOT, 'game/js/fitted-parts.js'));

export const TEMPLATES = FP.FITTED_TEMPLATES;
export const EYE_SLIDERS = ['f_eye_size', 'f_eye_space', 'f_eye_h', 'f_eye_tilt', 'f_eye_open', 'f_eye_almond'];
const OUT = join(ROOT, 'customization/parts/eyes/eye-sockets.json');

const loader = new GLTFLoader(); loader.setMeshoptDecoder(MeshoptDecoder);
function stripTextures(b) { // Node cannot decode images: drop texture refs, geometry/morphs/nodes untouched
  const jsonLen = b.readUInt32LE(12);
  const j = JSON.parse(b.toString('utf8', 20, 20 + jsonLen));
  if (!j.images) return b;
  delete j.images; delete j.textures; delete j.samplers;
  const drop = (o) => { if (!o || typeof o !== 'object') return; for (const k of Object.keys(o)) { if (/Texture$/.test(k)) delete o[k]; else drop(o[k]); } };
  for (const m of j.materials || []) drop(m);
  let js = Buffer.from(JSON.stringify(j), 'utf8');
  const pad = (4 - (js.length % 4)) % 4; js = Buffer.concat([js, Buffer.alloc(pad, 0x20)]);
  const rest = b.subarray(20 + jsonLen);
  const head = Buffer.alloc(20); head.write('glTF', 0, 'latin1'); head.writeUInt32LE(2, 4);
  head.writeUInt32LE(20 + js.length + rest.length, 8); head.writeUInt32LE(js.length, 12); head.writeUInt32LE(0x4e4f534a, 16);
  return Buffer.concat([head, js, rest]);
}
const quiet = async (fn) => { const w = console.warn, e = console.error; console.warn = () => {}; console.error = () => {}; try { return await fn(); } finally { console.warn = w; console.error = e; } };

export async function templateInstance(tid) {
  const b = stripTextures(readFileSync(join(ROOT, `customization/templates/meshes/${tid}.glb`)));
  const g = await quiet(() => loader.parseAsync(b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength), ''));
  A.assets.gltfs['custom-template-' + tid] = g;
  return quiet(() => A.assets.createInstance('custom-template-' + tid, 0xc98d5e, 0xe8b64c, 0.3));
}

/* skinned + morphed vertex positions (world) of the primitives whose material matches re */
export function eyePoints(model, re) {
  const out = [];
  model.updateMatrixWorld(true);
  model.traverse((o) => {
    if (!o.isSkinnedMesh) return;
    const mats = Array.isArray(o.material) ? o.material : [o.material];
    if (!mats.some((m) => m && re.test(m.name || ''))) return;
    const pos = o.geometry.attributes.position, mp = o.geometry.morphAttributes.position, inf = o.morphTargetInfluences;
    const rel = o.geometry.morphTargetsRelative;
    for (let i = 0; i < pos.count; i++) {
      const p = new THREE.Vector3().fromBufferAttribute(pos, i);
      if (mp && inf) {
        const base = p.clone();
        inf.forEach((w, k) => {
          if (!w) return;
          const t = new THREE.Vector3().fromBufferAttribute(mp[k], i);
          if (rel) p.addScaledVector(t, w); else p.addScaledVector(t.sub(base), w);
        });
      }
      o.applyBoneTransform(i, p);
      out.push(p.applyMatrix4(o.matrixWorld));
    }
  });
  return out;
}

export const SCLERA_RE = /human_eyes/i;
export const IRIS_RE = /iris/i;
const mean = (pts) => pts.reduce((s, p) => s.add(p), new THREE.Vector3()).multiplyScalar(1 / pts.length);

/* measure both sockets in head-local space on the model as it currently stands (morph influences as set) */
export function measureSockets(model, head) {
  model.updateMatrixWorld(true); // whole chain: a fresh instance has never been updated, so head alone would be wrong
  const inv = head.matrixWorld.clone().invert();
  const sclera = eyePoints(model, SCLERA_RE).map((p) => p.applyMatrix4(inv));
  const iris = eyePoints(model, IRIS_RE).map((p) => p.applyMatrix4(inv));
  // split by the head's lateral axis: the side axis is the one where the two eyes are far apart
  const c0 = mean(sclera.map((p) => p.clone()));
  const spread = ['x', 'y', 'z'].map((k) => sclera.reduce((s, p) => s + Math.abs(p[k] - c0[k]), 0) / sclera.length);
  const ax = ['x', 'y', 'z'][spread.indexOf(Math.max(...spread))];
  const side = (pts, sgn) => pts.filter((p) => Math.sign(p[ax] - c0[ax]) === sgn);
  const res = { lateral_axis: ax };
  for (const [name, sgn] of [['pos', 1], ['neg', -1]]) {
    const s = side(sclera, sgn), ir = side(iris, sgn);
    const c = mean(s.map((p) => p.clone()));
    const r = s.reduce((acc, p) => acc + p.distanceTo(c), 0) / s.length;
    const rmin = Math.min(...s.map((p) => p.distanceTo(c))), rmax = Math.max(...s.map((p) => p.distanceTo(c)));
    const fwd = mean(ir.map((p) => p.clone())).sub(c).normalize();
    res[name] = { c, r, rmin, rmax, fwd, n: s.length };
  }
  return res;
}

const r5 = (x) => +x.toFixed(5);
const v3 = (v) => [r5(v.x), r5(v.y), r5(v.z)];

export async function buildAll() {
  const { applyMorphTargets } = await import(join(ROOT, 'game/js/morph-apply.js'));
  const templates = {};
  for (const tid of TEMPLATES) {
    const inst = await templateInstance(tid);
    const model = inst.model;
    const head = FP.findHeadBone(model);
    applyMorphTargets(model, {});
    const m0 = measureSockets(model, head);
    // which side is the fighter's LEFT: MB-Lab / glTF bodies face +Z with the character's left on +X in body space;
    // map through the head's world matrix so it holds whatever axis the head bone uses
    model.updateMatrixWorld(true);
    const worldDir = new THREE.Vector3(); worldDir[m0.lateral_axis] = 1; worldDir.transformDirection(head.matrixWorld);
    const posIsLeft = worldDir.x > 0;
    const sides = posIsLeft ? { left: 'pos', right: 'neg' } : { left: 'neg', right: 'pos' };
    const entry = { lateral_axis: m0.lateral_axis };
    for (const [lr, k] of Object.entries(sides)) {
      const s = m0[k];
      entry[lr] = { center: v3(s.c), radius: r5(s.r), radius_min: r5(s.rmin), radius_max: r5(s.rmax), forward: v3(s.fwd), verts: s.n, sliders: {} };
    }
    for (const sl of EYE_SLIDERS) {
      for (const sgn of [1, -1]) {
        const live = applyMorphTargets(model, { [sl]: sgn });
        if (!live) continue;
        const m = measureSockets(model, head);
        for (const [lr, k] of Object.entries(sides)) {
          const d = m[k].c.clone().sub(m0[k].c), dr = m[k].r - m0[k].r;
          if (d.length() < 1e-5 && Math.abs(dr) < 1e-5) continue;
          entry[lr].sliders[sl + (sgn > 0 ? '+' : '-')] = { dc: v3(d), dr: r5(dr) };
        }
      }
      applyMorphTargets(model, {});
    }
    templates[tid] = entry;
  }
  return {
    _comment: 'Fitted-eye sockets per creation-suite template, HEAD-BONE-LOCAL metres (Head bone after the game\'s MB-Lab -> T3 remap). Measured from each template\'s own MB-Lab eyeball geometry + baked eye-slider morph targets by tools/eyes/build_eye_sockets.mjs; consumed by game/js/fitted-eyes.js (suite + game). left/right = the FIGHTER\'s left/right. sliders["<id>+|-"] = centre delta dc / radius delta dr at slider +-1 (linear in between).',
    generator: 'tools/eyes/build_eye_sockets.mjs',
    eyeball_glb: 'customization/parts/eyes/eyeball.glb',
    eyeball_radius: 0.012,
    templates,
  };
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const data = await buildAll();
  const txt = JSON.stringify(data, null, 1) + '\n';
  if (process.argv.includes('--check')) {
    const cur = readFileSync(OUT, 'utf8');
    if (cur !== txt) { console.error('eye-sockets.json drifted from the template meshes; rerun without --check'); process.exit(1); }
    console.log('eye-sockets.json matches the template meshes');
  } else {
    writeFileSync(OUT, txt);
    for (const [t, e] of Object.entries(data.templates)) console.log(t, 'L', e.left.center, 'r', e.left.radius, 'R', e.right.center, 'fwdL', e.left.forward, 'sliders', Object.keys(e.left.sliders).length);
  }
}

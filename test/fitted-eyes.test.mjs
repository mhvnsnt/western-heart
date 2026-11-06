// EYES phase proof (2026-11-02). Node, no browser, no WebGL draw (draws are stubbed: only Object3D math).
// Run: node --test test/fitted-eyes.test.mjs
// Fitted left / right eyeballs (customization/parts/eyes/eyeball.glb) at measured per-template sockets
// (customization/parts/eyes/eye-sockets.json, tools/eyes/build_eye_sockets.mjs), game/js/fitted-eyes.js:
//  - sockets file covers all 9 templates and matches a fresh measurement of each template's own eye geometry
//  - suite save -> game roster carries the attire's eye type / iris / sclera / pupil
//  - NUMERIC PROBE on all 9 templates through the game's own three.js + meshopt + assets.js instance path:
//    both eyes load and parent to Head, are mirror-symmetric, sit inside the body's own eye sockets within
//    tolerance, hide the body's own eye primitives, follow a head turn rigidly, follow the eye sliders
//    (size / spacing / height), and take iris colour / sclera tint / pupil size.
// Node limit (same as fitted-parts.test.mjs): textures are not decoded, so lens textures are proven only as
// UV + map wiring, not by looking at pixels.

import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
// CI's unit-test job is a sparse checkout without customization/: read missing files from git (as fitted-parts.test).
const bytes = (rel) => existsSync(join(ROOT, rel)) ? readFileSync(join(ROOT, rel))
  : execFileSync('git', ['show', `HEAD:${rel}`], { cwd: ROOT, maxBuffer: 1 << 28 });
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const THREE = await import('three');
const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js');
const { MeshoptDecoder } = await import('three/addons/libs/meshopt_decoder.js');
const A = await import(join(ROOT, 'game/js/assets.js'));
const FP = await import(join(ROOT, 'game/js/fitted-parts.js'));
const FE = await import(join(ROOT, 'game/js/fitted-eyes.js'));
const CF = await import(join(ROOT, 'game/js/custom-fighter.js'));
const { applyMorphTargets } = await import(join(ROOT, 'game/js/morph-apply.js'));

const SOCKETS = JSON.parse(bytes(FE.EYE_SOCKETS_JSON).toString('utf8'));
const CAT = JSON.parse(bytes('customization/creation-suite-ui/data/parts-catalog.json').toString('utf8'));
const loader = new GLTFLoader(); loader.setMeshoptDecoder(MeshoptDecoder);
const origWarn = console.warn, origErr = console.error, origLog = console.log;
const quiet = async (fn) => { console.warn = () => {}; console.error = () => {}; console.log = () => {}; try { return await fn(); } finally { console.warn = origWarn; console.error = origErr; console.log = origLog; } };
function stripTextures(b) {
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
const parse = (rel) => quiet(() => { const b = stripTextures(bytes(rel)); return loader.parseAsync(b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength), ''); });
async function instance(tid) {
  const g = await parse(`customization/templates/meshes/${tid}.glb`);
  A.assets.gltfs['custom-template-' + tid] = g;
  return quiet(() => A.assets.createInstance('custom-template-' + tid, 0xc98d5e, 0xe8b64c, 0.3));
}
const V = () => new THREE.Vector3();
const mean = (pts) => pts.reduce((s, p) => s.add(p), V()).multiplyScalar(1 / pts.length);
/* the body's own sclera vertices (skinned + morphed), world space, split fighter-left (+X) / right (-X) */
function bodyEyes(model, head = null) {
  const pts = [];
  model.updateMatrixWorld(true);
  model.traverse((o) => {
    if (!o.isSkinnedMesh || !/human_eyes/i.test((o.material && o.material.name) || '')) return;
    const pos = o.geometry.attributes.position, mp = o.geometry.morphAttributes.position, inf = o.morphTargetInfluences;
    for (let i = 0; i < pos.count; i++) {
      const p = V().fromBufferAttribute(pos, i);
      if (mp && inf) inf.forEach((w, k) => { if (w) p.addScaledVector(V().fromBufferAttribute(mp[k], i), w); });
      o.applyBoneTransform(i, p); pts.push(p.applyMatrix4(o.matrixWorld));
    }
  });
  // split on the head's own lateral axis (a turned head moves both eyes across world x)
  const inv = head ? head.matrixWorld.clone().invert() : null;
  const lx = (p) => (inv ? p.clone().applyMatrix4(inv).x : p.x);
  const side = (s) => { const q = pts.filter((p) => Math.sign(lx(p)) === s); const c = mean(q.map((p) => p.clone()));
    return { c, r: q.reduce((a, p) => a + p.distanceTo(c), 0) / q.length }; };
  return { left: side(1), right: side(-1) };
}
const eyeballPoints = (g) => { const pts = []; g.updateMatrixWorld(true);
  g.traverse((o) => { if (!o.isMesh || !/sclera/i.test(o.name)) return; const pos = o.geometry.attributes.position;
    for (let i = 0; i < pos.count; i++) pts.push(V().fromBufferAttribute(pos, i).applyMatrix4(o.matrixWorld)); }); return pts; };
const centreOf = (g) => V().setFromMatrixPosition(g.matrixWorld);
const meshNamed = (g, re) => { let m = null; g.traverse((o) => { if (o.isMesh && re.test(o.name)) m = o; }); return m; };

test('eye sockets cover all 9 templates, symmetric, catalog entries generic and wired', () => {
  assert.deepEqual(Object.keys(SOCKETS.templates).sort(), [...FP.FITTED_TEMPLATES].sort());
  for (const [t, s] of Object.entries(SOCKETS.templates)) {
    assert.ok(Math.abs(s.left.center[0] + s.right.center[0]) < 2e-4, t + ' mirror x');
    assert.ok(Math.abs(s.left.center[1] - s.right.center[1]) < 2e-4 && Math.abs(s.left.center[2] - s.right.center[2]) < 2e-4, t + ' same height/depth');
    assert.ok(s.left.center[0] > 0.02 && s.left.center[0] < 0.045, t + ' half interpupillary 2-4.5 cm: ' + s.left.center[0]);
    assert.ok(s.left.radius > 0.010 && s.left.radius < 0.018, t + ' eyeball radius 10-18 mm');
    for (const k of ['f_eye_size+', 'f_eye_space+', 'f_eye_h+']) assert.ok(s.left.sliders[k], t + ' slider delta ' + k);
  }
  const SOURCE_NAMES = /tekken|wwe|king|pantera|tiger|leopard|mb-?lab|makehuman/i;
  for (const id of Object.keys(FE.EYE_TYPES)) {
    const p = CAT.parts.find((x) => x.id === id);
    assert.ok(p, 'catalog has ' + id);
    assert.equal(p.geometry_pending, false); assert.equal(p.part_class, 'mesh_part');
    assert.equal(p.suite_slot, 'eye'); assert.equal(p.equip_slot, FE.EYE_SLOT); assert.ok(p.fitted_eyes);
    assert.equal(p.name, FE.EYE_TYPES[id].name);
    assert.ok(!SOURCE_NAMES.test(p.name), 'generic player-facing name: ' + p.name);
    if (FE.EYE_TYPES[id].lens) assert.ok(bytes(FE.EYE_TYPES[id].lens).length > 1000, id + ' lens texture exists');
  }
  assert.equal(CAT.total, CAT.parts.length);
});

test('suite save -> game roster carries the attire eyes; roster mode keeps the model eyes', () => {
  const save = { profile: { name: 'T', title: ['', ''] }, template: 'athletic-w', attireIndex: 1,
    body: { body_type: 'Medium F', skin_tone: '#c98d5e', morph_targets: { f_eye_size: 0.5 } },
    attires: [{ equipped: {} }, { equipped: { EYES: 'wh-eye-lens-ice' }, colors: { sclera: '#efe6d2' }, eyes: { pupil: 1.4 } }] };
  const r = CF.customFighterToRoster(save);
  assert.deepEqual(r.fittedEyes, { id: 'wh-eye-lens-ice', lens: 'customization/eye-library/eye-blue-snow-leopard.png',
    iris: null, sclera: '#efe6d2', pupil: 1.4, template: 'athletic-w' });
  assert.equal(CF.customFighterToRoster({ ...save, attireIndex: 0 }).fittedEyes, null, 'attire without eyes keeps the body eyes');
  assert.equal(CF.customFighterToRoster({ ...save, mode: 'roster' }).fittedEyes, null);
  // a colour-only attire gets the default eye type; bad values are clamped / ignored
  const c = FE.selectEyes({ colors: { iris: '#2f5d8a', sclera: 'nope' }, eyes: { pupil: 9 } }, 'technician');
  assert.deepEqual(c, { id: 'wh-eye-natural', lens: null, iris: '#2f5d8a', sclera: null, pupil: FE.PUPIL_MAX, template: 'technician' });
  assert.equal(FE.selectEyes({ equipped: { EYES: 'wh-eye-natural' } }, 'not-a-template'), null);
});

for (const tid of FP.FITTED_TEMPLATES) {
  test(`numeric probe on ${tid}: both eyes load on Head, symmetric, inside the sockets, follow head + sliders, styled`, async () => {
    const inst = await instance(tid);
    const model = inst.model;
    const head = FP.findHeadBone(model);
    assert.ok(head && head.name === 'Head');
    applyMorphTargets(model, {});
    const own = bodyEyes(model);
    // sockets file == fresh measurement of this template's own eyes (head-local -> world)
    model.updateMatrixWorld(true);
    for (const side of ['left', 'right']) {
      const s = SOCKETS.templates[tid][side];
      const w = V().fromArray(s.center).applyMatrix4(head.matrixWorld);
      assert.ok(w.distanceTo(own[side].c) < 2e-4, `${tid} ${side}: socket file matches the mesh (${w.distanceTo(own[side].c).toExponential(1)} m)`);
    }
    const eyeball = (await parse(FE.EYEBALL_GLB)).scene;
    const cfg = { ...FE.selectEyes({ equipped: { EYES: 'wh-eye-natural' }, colors: { iris: '#3f6e4a', sclera: '#efe6d2' }, eyes: { pupil: 1.2 } }, tid) };
    const groups = FE.attachEyes(model, eyeball, SOCKETS, cfg);
    assert.equal(groups.length, 2, 'both eyes attached');
    const [L, R] = groups;
    for (const g of groups) assert.equal(g.parent, head, g.name + ' parented to Head');
    model.updateMatrixWorld(true);
    const cL = centreOf(L), cR = centreOf(R);
    // fighter's left eye on +X (glTF body faces +Z), mirror-symmetric
    assert.ok(cL.x > 0 && cR.x < 0, 'left on +X, right on -X');
    assert.ok(Math.abs(cL.x + cR.x) < 5e-4 && Math.abs(cL.y - cR.y) < 5e-4 && Math.abs(cL.z - cR.z) < 5e-4,
      `symmetric: ${cL.toArray().map((x) => x.toFixed(4))} vs ${cR.toArray().map((x) => x.toFixed(4))}`);
    const report = {};
    for (const [side, g] of [['left', L], ['right', R]]) {
      const off = centreOf(g).distanceTo(own[side].c);
      const pts = eyeballPoints(g);
      const rr = mean(pts.map((p) => p.clone())).distanceTo(centreOf(g));
      const outer = Math.max(...pts.map((p) => p.distanceTo(own[side].c)));
      report[side] = { off_mm: +(off * 1000).toFixed(2), radius_mm: +(own[side].r * 1000).toFixed(2), outer_mm: +(outer * 1000).toFixed(2) };
      assert.ok(off < 1e-3, `${side}: centred in the body's own socket within 1 mm (${(off * 1000).toFixed(2)} mm)`);
      assert.ok(outer < own[side].r * 1.04, `${side}: inside the socket sphere (outer ${(outer * 1000).toFixed(2)} mm vs r ${(own[side].r * 1000).toFixed(2)} mm)`);
      assert.ok(outer > own[side].r * 0.96, `${side}: fills the socket (not shrunk)`);
      assert.ok(rr < 1e-3, 'sclera sphere centred on its group');
      // gaze: iris faces forward (+Z body) and slightly matches the measured axis
      const iris = mean(meshNamed(g, /iris/i) ? (() => { const m = meshNamed(g, /iris/i), p = []; const pos = m.geometry.attributes.position;
        for (let i = 0; i < pos.count; i++) p.push(V().fromBufferAttribute(pos, i).applyMatrix4(m.matrixWorld)); return p; })() : []);
      assert.ok(iris.z - centreOf(g).z > own[side].r * 0.8, `${side}: iris faces forward`);
    }
    // styling: iris colour, sclera tint, pupil size
    assert.equal('#' + meshNamed(L, /iris/i).material.color.getHexString(), '#3f6e4a');
    assert.equal('#' + meshNamed(R, /sclera/i).material.color.getHexString(), '#efe6d2');
    assert.ok(Math.abs(meshNamed(L, /pupil/i).scale.x - 1.2) < 1e-9);
    assert.notEqual(meshNamed(L, /iris/i).material, meshNamed(R, /iris/i).material, 'materials cloned per eye');
    // iris + pupil discs sit in front of the sclera cap (eyeball.glb authors them inside it; fitted-eyes lifts them)
    const zMax = (m) => { const pos = m.geometry.attributes.position; let z = -1; for (let i = 0; i < pos.count; i++) z = Math.max(z, pos.getZ(i)); return z; };
    const sclZ = zMax(meshNamed(L, /sclera/i));
    assert.ok(zMax(meshNamed(L, /iris/i)) + meshNamed(L, /iris/i).position.z > sclZ, 'iris in front of the sclera cap');
    assert.ok(zMax(meshNamed(L, /pupil/i)) + meshNamed(L, /pupil/i).position.z > zMax(meshNamed(L, /iris/i)) + meshNamed(L, /iris/i).position.z, 'pupil in front of the iris');
    // body's own eye primitives hidden under the fitted eyes, restored on clear
    let hidden = 0; model.traverse((o) => { if (o.isMesh && !o.visible && FE.EYE_HIDES.test((o.material && o.material.name) || '')) hidden++; });
    assert.ok(hidden >= 2, 'own sclera + iris hidden: ' + hidden);
    // follows a head turn rigidly (yaw 35 deg + pitch 20 deg)
    const before = [L, R].map((g) => eyeballPoints(g).slice(0, 40));
    const hw0 = head.matrixWorld.clone();
    head.rotateY(35 * Math.PI / 180); head.rotateX(20 * Math.PI / 180); model.updateMatrixWorld(true);
    const xf = head.matrixWorld.clone().multiply(hw0.clone().invert());
    let err = 0;
    [L, R].forEach((g, k) => { const after = eyeballPoints(g).slice(0, 40); before[k].forEach((p, i) => { err = Math.max(err, p.clone().applyMatrix4(xf).distanceTo(after[i])); }); });
    assert.ok(err < 1e-5, 'rigid head-follow error ' + err);
    // and the turned eyes are still in the turned body sockets
    const ownTurned = bodyEyes(model, head);
    assert.ok(centreOf(L).distanceTo(ownTurned.left.c) < 1e-3 && centreOf(R).distanceTo(ownTurned.right.c) < 1e-3, 'inside sockets after the head turn');
    head.rotateX(-20 * Math.PI / 180); head.rotateY(-35 * Math.PI / 180); model.updateMatrixWorld(true);
    // follows the eye sliders: spacing + height + size, then compare to the body's own morphed eyes
    const vals = { f_eye_space: 0.8, f_eye_h: -0.6, f_eye_size: 0.7 };
    applyMorphTargets(model, vals);
    assert.equal(FE.updateEyeSockets(model, SOCKETS, vals), 2);
    const ownM = bodyEyes(model);
    model.updateMatrixWorld(true);
    let sErr = 0;
    for (const [side, g] of [['left', L], ['right', R]]) {
      sErr = Math.max(sErr, centreOf(g).distanceTo(ownM[side].c));
      const rNow = g.scale.x * FE.EYEBALL_RADIUS;
      assert.ok(Math.abs(rNow - ownM[side].r) < 6e-4, `${side}: radius follows Eye Size (${(rNow * 1000).toFixed(2)} vs ${(ownM[side].r * 1000).toFixed(2)} mm)`);
    }
    assert.ok(sErr < 1e-3, `eyes follow spacing/height/size sliders within 1 mm (${(sErr * 1000).toFixed(2)} mm)`);
    const moved = centreOf(L).distanceTo(cL);
    assert.ok(moved > 2e-3, 'sliders actually moved the eyes ' + moved);
    applyMorphTargets(model, {}); FE.updateEyeSockets(model, SOCKETS, {});
    // restyle in place + lens wiring (planar iris UVs + map; texture pixels not decodable in Node)
    const lensCfg = FE.selectEyes({ equipped: { EYES: 'wh-eye-lens-amber' } }, tid);
    let made = 0;
    FE.restyleEyes(model, lensCfg, { makeTexture: (url) => { made++; assert.match(url, /eye-library\/eye-yellow-tiger\.png$/); return new THREE.Texture(); } });
    assert.equal(made, 2);
    const irisL = meshNamed(L, /iris/i);
    assert.ok(irisL.material.map && irisL.geometry.attributes.uv, 'lens texture mapped on the iris');
    const uv = irisL.geometry.attributes.uv; let umin = 1, umax = 0;
    for (let i = 0; i < uv.count; i++) { umin = Math.min(umin, uv.getX(i)); umax = Math.max(umax, uv.getX(i)); }
    assert.ok(umin >= -1e-6 && umax <= 1 + 1e-6 && umax - umin > 0.9, 'iris UVs span the texture');
    // clear restores the body's own eyes
    assert.equal(FE.clearEyes(model), 2);
    let vis = 0; model.traverse((o) => { if (o.isMesh && o.visible && FE.EYE_HIDES.test((o.material && o.material.name) || '')) vis++; });
    assert.ok(vis >= 2, 'own eyes visible again');
    origLog(`[probe] ${tid}: L=${cL.toArray().map((x) => x.toFixed(4))} R=${cR.toArray().map((x) => x.toFixed(4))} head-follow err=${err.toExponential(1)} slider err=${(sErr * 1000).toFixed(2)}mm`, JSON.stringify(report));
  });
}

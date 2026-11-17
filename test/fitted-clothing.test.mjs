// CLOTHING + ACCESSORIES phase proof (2026-11-03). Node, no browser, no WebGL draw.
// Run: node --test test/fitted-clothing.test.mjs
// 18 original CC0 garments generated in Blender on each of the 9 template bodies
// (customization/parts/clothing/generated, built by tools/mpfb2/clothing/):
//  - manifest, game list, catalog and files agree; 162 GLBs <= 300 KB; licence CC0; generic names;
//    filed on WWE 2K CAW tabs (Upper / Lower / Hands / Feet / Accessories) + the Tekken slot spine
//  - the suite save -> game roster path carries the chosen garments + per-slot tints
//  - body-triangle hiding helpers (run-length decode, all-3-vertices rule)
//  - NUMERIC PROBE on the real GLBs through the game's own three.js + meshopt + assets.js instance path:
//    every garment loads and is skinned to the body skeleton, lies on the body surface (>= 95 % of its vertices
//    within its layer offset + 2.5 cm of the skin), hides body triangles under it (restored on removal),
//    follows a body slider with the body, and follows a bone rotation by its weights.
// Node limit: materials / look are not proven here (see the Cycles sheets in the PR).

import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
// CI's unit-test job is a sparse checkout without customization/: read missing files from git's object store.
const bytes = (rel) => existsSync(join(ROOT, rel)) ? readFileSync(join(ROOT, rel))
  : execFileSync('git', ['show', `HEAD:${rel}`], { cwd: ROOT, maxBuffer: 1 << 28 });
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const THREE = await import('three');
const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js');
const { MeshoptDecoder } = await import('three/addons/libs/meshopt_decoder.js');
const A = await import(join(ROOT, 'game/js/assets.js'));
const FP = await import(join(ROOT, 'game/js/fitted-parts.js'));
const CF = await import(join(ROOT, 'game/js/custom-fighter.js'));
const { applyMorphTargets } = await import(join(ROOT, 'game/js/morph-apply.js'));

const DIR = 'customization/parts/clothing/generated';
const MAN = JSON.parse(bytes(`${DIR}/MANIFEST.json`).toString('utf8'));
const CAT = JSON.parse(bytes('customization/creation-suite-ui/data/parts-catalog.json').toString('utf8'));
const CLOTH = Object.keys(FP.FITTED_PARTS).filter((id) => FP.isFittedClothing(id));
const loader = new GLTFLoader(); loader.setMeshoptDecoder(MeshoptDecoder);
const origWarn = console.warn, origErr = console.error;
const quiet = async (fn) => { console.warn = () => {}; console.error = () => {}; try { return await fn(); } finally { console.warn = origWarn; console.error = origErr; } };
function stripTextures(b) {  // Node cannot decode images (templates carry textures; garments don't)
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
const SOURCE_NAMES = /tekken|wwe|smackdown|no mercy|doa|def jam|makehuman|mpfb|\b(jin|kazuya|paul|law|hwoarang|king|eddy|christie|undertaker|rock|austin|cena)\b/i;

test('manifest, game list, catalog and files agree; 162 GLBs <= 300 KB; CC0; generic names; CAW + Tekken filing', () => {
  assert.equal(MAN.entries.length, 18);
  assert.deepEqual(MAN.entries.map((e) => e.id).sort(), [...CLOTH].sort());
  const cat = new Map(CAT.parts.map((p) => [p.id, p]));
  const tabs = new Set();
  for (const e of MAN.entries) {
    assert.equal(e.license, 'CC0-1.0', e.id);
    assert.equal(FP.FITTED_PARTS[e.id].slot, e.equip_slot, e.id);
    assert.ok(!SOURCE_NAMES.test(e.name), 'generic player-facing name: ' + e.name);
    assert.deepEqual(e.templates.slice().sort(), FP.FITTED_TEMPLATES.slice().sort(), e.id + ' fitted on all 9 bodies');
    for (const t of e.templates) {
      const b = bytes(`${DIR}/${e.files[t]}`);
      assert.ok(b.length <= 300 * 1024, `${e.id}/${t} ${b.length} B <= 300 KB`);
      assert.equal(FP.fittedPartPath(e.id, t), `${DIR}/${e.files[t]}`);
    }
    const p = cat.get(e.id);
    assert.ok(p, e.id + ' in parts catalog');
    assert.equal(p.name, e.name); assert.equal(p.license, 'CC0-1.0'); assert.ok(p.fitted && p.fitted.hides_body);
    assert.equal(p.t7_slot, e.t7_slot); assert.equal(p.equip_slot, e.equip_slot);
    assert.ok(['Upper', 'Lower', 'Hands', 'Feet', 'Accessories'].includes(p.wwe_caw_tab), e.id + ' WWE CAW tab');
    tabs.add(p.wwe_caw_tab);
  }
  assert.equal(tabs.size, 5, 'all five CAW tabs filled');
  assert.equal(CAT.total, CAT.parts.length);
});

test('suite save -> game roster carries the chosen garments and per-slot tints', () => {
  const save = {
    profile: { name: 'T', title: ['', ''] }, template: 'athletic-w', attireIndex: 0,
    body: { body_type: 'Medium F', skin_tone: '#c98d5e', morph_targets: {} },
    attires: [{ equipped: { 9: 'wh-top-crop', 11: 'wh-tights-long', F: 'wh-boots-knee', H: 'wh-gloves-mma', '13K': 'wh-kneepads', 2: 'mh-hair-ponytail01' },
      colors: { cloth_9: '#7a1e1e', 'cloth_13K': '#1a1410', hair: '#3b2a1e' } }],
  };
  const r = CF.customFighterToRoster(save);
  const by = Object.fromEntries(r.fittedParts.map((p) => [p.id, p]));
  assert.equal(r.fittedParts.length, 6);
  assert.equal(by['wh-top-crop'].path, `${DIR}/wh-top-crop/athletic-w.glb`);
  assert.equal(by['wh-top-crop'].tint, '#7a1e1e');
  assert.equal(by['wh-kneepads'].tint, '#1a1410');
  assert.equal(by['wh-boots-knee'].tint, null);
  assert.equal(by['mh-hair-ponytail01'].tint, '#3b2a1e');
  assert.equal(FP.fittedColorKey('wh-elbowpads'), 'cloth_12E');
  assert.equal(FP.fittedColorKey('mh-brows-001', 'eyebrows'), 'brows');
});

test('body-hide helpers: run-length decode, triangle dropped only when all 3 vertices are hidden', () => {
  assert.deepEqual([...FP.expandRuns([3, 2, 10, 1])], [3, 4, 10]);
  assert.deepEqual(FP.filterTriangles([0, 1, 2, 2, 3, 4], new Set([0, 1, 2, 3])), [2, 3, 4]);
  assert.equal(FP.bodyPrimKey('MBLab_skin2'), 'skin');
  assert.equal(FP.bodyPrimKey('MBLab_generic'), 'generic');
  assert.equal(FP.bodyPrimKey('MBLab_nails'), 'nails');
  assert.equal(FP.bodyPrimKey('MBLab_eyes'), null);
});

/* --- numeric probe --- */
const v = () => new THREE.Vector3();
function bodyPoints(root) {
  const pts = [];
  root.updateMatrixWorld(true);
  root.traverse((o) => {
    if (!o.isSkinnedMesh || !['skin', 'generic'].includes(FP.bodyPrimKey(o.material && o.material.name))) return;
    let fitted = false; for (let a = o; a; a = a.parent) if (a.userData && a.userData.whFitted) fitted = true;
    if (fitted) return;
    const pos = o.geometry.attributes.position;
    for (let i = 0; i < pos.count; i++) { const p = v().fromBufferAttribute(pos, i); o.applyBoneTransform(i, p); pts.push(p.applyMatrix4(o.matrixWorld)); }
  });
  return pts;
}
function partPoints(group) {
  const pts = [];
  group.updateMatrixWorld(true);
  group.traverse((o) => {
    if (!o.isMesh) return;
    const pos = o.geometry.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const p = v().fromBufferAttribute(pos, i);
      if (o.morphTargetInfluences && o.geometry.morphAttributes.position) {
        o.morphTargetInfluences.forEach((w, k) => { if (w) p.addScaledVector(v().fromBufferAttribute(o.geometry.morphAttributes.position[k], i), w); });
      }
      if (o.isSkinnedMesh) o.applyBoneTransform(i, p);
      pts.push(p.applyMatrix4(o.matrixWorld));
    }
  });
  return pts;
}
/* nearest-point distances through a uniform grid (cell 3 cm) */
function nearestDistances(cloud, query) {
  const C = 0.03, grid = new Map(), key = (x, y, z) => `${x},${y},${z}`;
  for (const p of cloud) { const k = key(Math.floor(p.x / C), Math.floor(p.y / C), Math.floor(p.z / C)); (grid.get(k) || grid.set(k, []).get(k)).push(p); }
  return query.map((q) => {
    const cx = Math.floor(q.x / C), cy = Math.floor(q.y / C), cz = Math.floor(q.z / C); let best = Infinity;
    for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) {
      const cell = grid.get(key(cx + dx, cy + dy, cz + dz)); if (!cell) continue;
      for (const p of cell) { const d = p.distanceToSquared(q); if (d < best) best = d; }
    }
    return Math.sqrt(best);
  });
}
function bodyTriangles(root) {
  let n = 0;
  root.traverse((o) => { if (o.isMesh && FP.bodyPrimKey(o.material && o.material.name) && !(o.parent && o.parent.userData && o.parent.userData.whFitted) && o.geometry.index) n += o.geometry.index.count / 3; });
  return n;
}
function dominantBone(group) {
  const count = new Map(); let mesh = null;
  group.traverse((o) => {
    if (!o.isSkinnedMesh) return; mesh = o;
    const si = o.geometry.attributes.skinIndex, sw = o.geometry.attributes.skinWeight;
    for (let i = 0; i < si.count; i++) if (sw.getX(i) > 0.5) count.set(si.getX(i), (count.get(si.getX(i)) || 0) + 1);
  });
  const [k] = [...count.entries()].sort((a, b) => b[1] - a[1])[0] || [];
  return k === undefined ? null : { mesh, bone: mesh.skeleton.bones[k], k };
}
async function instance(tid) {
  const g = await parse(`customization/templates/meshes/${tid}.glb`);
  A.assets.gltfs['custom-template-' + tid] = g;
  return quiet(() => A.assets.createInstance('custom-template-' + tid, 0xc98d5e, 0xe8b64c, 0.3));
}

const PROBE_TEMPLATES = ['technician', 'super-heavyweight', 'athletic-w'];
for (const tid of PROBE_TEMPLATES) {
  test(`numeric probe on ${tid}: all 18 garments load, skin to the body, lie on it, hide body under them, follow slider + bones`, async () => {
    const inst = await instance(tid);
    const model = inst.model;
    const tris0 = bodyTriangles(model);
    const body = bodyPoints(model);
    assert.ok(body.length > 5000, 'body skin points');
    const report = {};
    for (const id of CLOTH) {
      const list = [{ id, slot: FP.FITTED_PARTS[id].slot, path: FP.fittedPartPath(id, tid), tint: null }];
      const [g] = await FP.loadFittedParts(model, list, { loadScene: (url) => parse(url).then((x) => x.scene) });
      assert.ok(g, id + ' loaded');
      assert.ok(g.userData.whFitted.skinned, id + ' skinned to the body skeleton');
      const off = MAN.entries.find((e) => e.id === id).layer_offset_m;
      const d = nearestDistances(body, partPoints(g)).sort((a, b) => a - b);
      const p95 = d[Math.floor(d.length * 0.95)];
      const tris1 = bodyTriangles(model);
      report[id] = { p95_mm: +(p95 * 1000).toFixed(1), hidden_tris: tris0 - tris1 };
      assert.ok(p95 < off + 0.025, `${id}: on the body surface (p95 ${(p95 * 1000).toFixed(1)} mm)`);
      assert.ok(tris1 < tris0, `${id}: hides body triangles under it`);
      // a body slider moves the garment with the body: the garment's first slider target (b_weight where present)
      let dict = null; g.traverse((o) => { if (!dict && o.isMesh && o.morphTargetDictionary) dict = o.morphTargetDictionary; });
      const names = Object.keys(dict || {}).filter((n) => /\+$/.test(n));
      assert.ok(names.length, id + ' carries body slider targets');
      const slider = (names.includes('b_weight+') ? 'b_weight+' : names[0]).slice(0, -1);
      const c0 = partPoints(g);
      const live = applyMorphTargets(model, { [slider]: 1 });
      const c1 = partPoints(g);
      applyMorphTargets(model, {});
      assert.ok(live > 0);
      const moved = Math.max(...c0.map((p, i) => p.distanceTo(c1[i])));
      assert.ok(moved > 0.001, `${id}: ${slider} moves it (${(moved * 1000).toFixed(1)} mm)`);
      // follows its dominant bone (most vertices weighted > 50 % to it): rotate it 25 deg, the garment moves
      const dom = dominantBone(g);
      assert.ok(dom, id + " has vertices weighted mostly to one bone");
      const q0 = dom.bone.quaternion.clone();
      const before = partPoints(g);
      dom.bone.quaternion.multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), 0.436));
      model.updateMatrixWorld(true);
      const after = partPoints(g);
      dom.bone.quaternion.copy(q0); model.updateMatrixWorld(true);
      const bm = Math.max(...before.map((p, i) => p.distanceTo(after[i])));
      assert.ok(bm > 0.002, `${id}: follows bone ${dom.bone.name} (${(bm * 1000).toFixed(1)} mm)`);
      FP.clearFittedParts(model);
      assert.equal(bodyTriangles(model), tris0, `${id}: body restored after removal`);
    }
    console.log(`[clothing probe] ${tid}`, JSON.stringify(report));
  });
}

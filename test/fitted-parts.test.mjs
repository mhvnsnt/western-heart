// HAIR phase proof (2026-11-02). Node, no browser, no WebGL draw.
// Run: node --test test/fitted-parts.test.mjs
// Template-fitted CC0 hair / facial hair / eyebrows / eyelashes
// (customization/parts/hair/mpfb2, built by tools/mpfb2/hair/):
//  - manifest, catalog, game list and files agree; every file small; licence CC0
//  - the suite save -> game roster path carries the chosen parts + tints
//  - NUMERIC PROBE on the real GLBs through the game's own three.js +
//    meshopt + assets.js instance path (MB-Lab -> T3 bone remap):
//    each part loads, is parented to the Head bone, sits on the head
//    within tolerance (hair around the skull, brows above the eyes,
//    lashes on the eyes, beards on the jaw), follows a head rotation
//    exactly, and its face morphs move with the body's.
// Node limit (same as custom-template-fight.test.mjs): textures are not
// decoded in Node, so materials/texture look are NOT proven here.

import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
// CI's unit-test job is a sparse checkout without customization/: a file not on disk is read from git's object
// store (same approach as test/custom-template-fight.test.mjs).
const bytes = (rel) => existsSync(join(ROOT, rel)) ? readFileSync(join(ROOT, rel))
  : execFileSync('git', ['show', `HEAD:${rel}`], { cwd: ROOT, maxBuffer: 1 << 28 });
const has = (rel) => { try { bytes(rel); return true; } catch (e) { return false; } };
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const THREE = await import('three');
const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js');
const { MeshoptDecoder } = await import('three/addons/libs/meshopt_decoder.js');
const A = await import(join(ROOT, 'game/js/assets.js'));
const FP = await import(join(ROOT, 'game/js/fitted-parts.js'));
const CF = await import(join(ROOT, 'game/js/custom-fighter.js'));
const { applyMorphTargets } = await import(join(ROOT, 'game/js/morph-apply.js'));

const MAN = JSON.parse(bytes('customization/parts/hair/mpfb2/MANIFEST.json').toString('utf8'));
const CAT = JSON.parse(bytes('customization/creation-suite-ui/data/parts-catalog.json').toString('utf8'));
const loader = new GLTFLoader(); loader.setMeshoptDecoder(MeshoptDecoder);
const origWarn = console.warn, origErr = console.error;
const quiet = async (fn) => { console.warn = () => {}; console.error = () => {}; try { return await fn(); } finally { console.warn = origWarn; console.error = origErr; } };
// Node cannot decode images: drop texture references from a GLB's JSON chunk (geometry/morphs/nodes untouched).
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

test('manifest, game list, catalog and files agree; files small; licence CC0', () => {
  const ids = MAN.entries.map((e) => e.id).sort();
  assert.deepEqual(ids, Object.keys(FP.FITTED_PARTS).sort());
  const bySlot = {};
  for (const e of MAN.entries) {
    bySlot[e.slot] = (bySlot[e.slot] || 0) + 1;
    assert.match(e.license, /^CC0/, e.id);
    assert.equal(FP.FITTED_PARTS[e.id].slot, e.slot, e.id);
    assert.deepEqual(e.templates, FP.FITTED_TEMPLATES, e.id);
    assert.ok(has('customization/parts/hair/mpfb2/' + e.texture), e.id + ' texture');
    for (const t of FP.FITTED_TEMPLATES) {
      const p = FP.fittedPartPath(e.id, t);
      assert.ok(bytes(p).length < 300 * 1024, p + ' < 300 KB');
    }
  }
  assert.ok(bySlot.hair >= 6 && bySlot.eyebrows >= 1 && bySlot.eyelashes >= 1 && bySlot.facial_hair >= 3, JSON.stringify(bySlot));
  assert.ok(bytes('customization/parts/hair/mpfb2/LICENSE-CC0.txt').toString('utf8').includes('"license": "CC0"'));
  const cat = new Map(CAT.parts.map((p) => [p.id, p]));
  const SOURCE_NAMES = /tekken|wwe|makehuman|mpfb|quaternius|mb-?lab/i;
  for (const e of MAN.entries) {
    const p = cat.get(e.id);
    assert.ok(p, 'catalog has ' + e.id);
    assert.equal(p.geometry_pending, false, e.id);
    assert.equal(p.part_class, 'mesh_part');
    assert.ok(p.fitted && p.fitted.space === 'head-bone-local', e.id);
    assert.ok(!SOURCE_NAMES.test(p.name), 'generic player-facing name: ' + p.name);
    assert.ok(['Hairstyle', 'Facial Hair', 'Eyebrows', 'Eyelashes'].includes(p.wwe_category), e.id);
  }
  // brows and lashes share the Tekken FACE slot (6) but equip separately
  assert.notEqual(cat.get('mh-brows-001').equip_slot, cat.get('mh-lashes-01').equip_slot);
  assert.equal(CAT.total, CAT.parts.length);
});

test('suite save -> game roster carries the chosen fitted parts and tints', () => {
  const save = {
    profile: { name: 'T', title: ['', ''] }, template: 'powerhouse-w', attireIndex: 1,
    body: { body_type: 'Medium F', skin_tone: '#c98d5e', morph_targets: { f_brow_h: 0.4 } },
    attires: [{ equipped: {} }, { equipped: { 2: 'mh-hair-ponytail01', 6: 'mh-brows-006', '6L': 'mh-lashes-02', 7: 'wh-beard-goatee', 9: 'not-fitted' },
      colors: { hair: '#7a1e1e', lashes: '#1a1410' } }],
  };
  const r = CF.customFighterToRoster(save);
  assert.equal(r.model, 'custom-template-powerhouse-w');
  const by = Object.fromEntries(r.fittedParts.map((p) => [p.slot, p]));
  assert.equal(r.fittedParts.length, 4);
  assert.equal(by.hair.path, 'customization/parts/hair/mpfb2/mh-hair-ponytail01/powerhouse-w.glb');
  assert.equal(by.hair.tint, '#7a1e1e');
  assert.equal(by.eyelashes.tint, '#1a1410');
  assert.equal(by.eyebrows.tint, null);
  assert.equal(by.facial_hair.id, 'wh-beard-goatee');
  assert.deepEqual(CF.customFighterToRoster({ ...save, mode: 'roster' }).fittedParts, []);
  assert.equal(FP.fittedPartPath('mh-hair-short01', 'not-a-template'), null);
});

/* --- numeric probe --- */
const v = () => new THREE.Vector3();
function skinnedPoints(root, matRe) {
  const pts = [];
  root.updateMatrixWorld(true);
  root.traverse((o) => {
    if (!o.isSkinnedMesh) return;
    const mats = Array.isArray(o.material) ? o.material : [o.material];
    if (!mats.some((m) => m && matRe.test(m.name || ''))) return;
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
      pts.push(p.applyMatrix4(o.matrixWorld));
    }
  });
  return pts;
}
const mean = (pts) => pts.reduce((s, p) => s.add(p), v()).multiplyScalar(1 / pts.length);

async function instance(tid) {
  const g = await parse(`customization/templates/meshes/${tid}.glb`);
  A.assets.gltfs['custom-template-' + tid] = g;
  return quiet(() => A.assets.createInstance('custom-template-' + tid, 0xc98d5e, 0xe8b64c, 0.3));
}

const PROBE_TEMPLATES = ['technician', 'super-heavyweight', 'striker-w'];
for (const tid of PROBE_TEMPLATES) {
  test(`numeric probe on ${tid}: every fitted part loads, binds to Head, sits on the head, follows head + face morphs`, async () => {
    const inst = await instance(tid);
    const model = inst.model;
    const head = FP.findHeadBone(model);
    assert.ok(head && head.name === 'Head', 'Head bone after MB-Lab -> T3 remap');
    model.updateMatrixWorld(true);
    const eyes = skinnedPoints(model, /human_eyes/i);
    const eyeL = mean(eyes.filter((p) => p.x > 0)), eyeR = mean(eyes.filter((p) => p.x < 0));
    const eyeMid = eyeL.clone().add(eyeR).multiplyScalar(0.5);
    const skull = skinnedPoints(model, /skin/i).filter((p) => p.y > eyeMid.y);
    const top = Math.max(...skull.map((p) => p.y));
    const list = Object.keys(FP.FITTED_PARTS).map((id) => ({ id, slot: FP.FITTED_PARTS[id].slot, path: FP.fittedPartPath(id, tid), tint: '#3b2a1e' }));
    const groups = await FP.loadFittedParts(model, list, { loadScene: (url) => parse(url).then((g) => g.scene) });
    assert.equal(groups.length, list.length, 'all parts loaded');
    const lash = model.getObjectByProperty('isSkinnedMesh', true);
    let hiddenLash = 0; model.traverse((o) => { if (o.isMesh && !o.visible && /eyelash/i.test(o.material && o.material.name)) hiddenLash++; });
    assert.ok(hiddenLash >= 1 && lash, 'base eyelash strip hidden under fitted lashes');
    const report = {};
    for (const g of groups) {
      const { partId, slot } = g.userData.whFitted;
      assert.equal(g.parent, head, partId + ' parented to Head');
      const pts = partPoints(g);
      const c = mean(pts);
      const d = { dx: c.x - eyeMid.x, dy: c.y - eyeMid.y, dz: c.z - eyeMid.z };
      report[partId] = Object.fromEntries(Object.entries(d).map(([k, x]) => [k, +x.toFixed(3)]));
      // side-part / braid styles are asymmetric by design: hair gets 3 cm, everything on the face 1.2 cm
      assert.ok(Math.abs(d.dx) < (slot === 'hair' ? 0.03 : 0.012), `${partId}: centred left/right (${d.dx.toFixed(3)})`);
      if (slot === 'hair') {
        assert.ok(Math.max(...pts.map((p) => p.y)) > top + 0.002 && Math.max(...pts.map((p) => p.y)) < top + 0.09, `${partId}: crown just above the skull top`);
        assert.ok(d.dz < 0.0, `${partId}: mass behind the eyes`);
      } else if (slot === 'eyebrows') {
        // reference: on the MakeHuman base itself the brow centroid sits 10 mm above / 13 mm in front of the eyeball centre
        assert.ok(d.dy > 0.004 && d.dy < 0.03, `${partId}: above the eyes (${d.dy.toFixed(3)})`);
        assert.ok(d.dz > -0.005 && d.dz < 0.03, `${partId}: at the brow ridge (${d.dz.toFixed(3)})`);
      } else if (slot === 'eyelashes') {
        assert.ok(Math.abs(d.dy) < 0.012 && d.dz > -0.002 && d.dz < 0.025, `${partId}: on the eyes (${JSON.stringify(report[partId])})`);
      } else if (slot === 'facial_hair') {
        assert.ok(d.dy < -0.04 && d.dy > -0.15, `${partId}: below the eyes on the jaw (${d.dy.toFixed(3)})`);
      }
    }
    // follows the head bone exactly: rotate Head 30 deg, every part vertex moves rigidly with it
    const g0 = groups[0];
    const before = partPoints(g0).slice(0, 50);
    const hw0 = head.matrixWorld.clone();
    head.rotateX(Math.PI / 6); model.updateMatrixWorld(true);
    const after = partPoints(g0).slice(0, 50);
    const xf = head.matrixWorld.clone().multiply(hw0.clone().invert());
    const err = Math.max(...before.map((p, i) => p.clone().applyMatrix4(xf).distanceTo(after[i])));
    assert.ok(err < 1e-4, 'rigid head follow error ' + err);
    head.rotateX(-Math.PI / 6); model.updateMatrixWorld(true);
    // face morphs drive the parts: brow height raises brows
    const brow = groups.find((g) => g.userData.whFitted.slot === 'eyebrows');
    const y0 = mean(partPoints(brow)).y;
    const live = applyMorphTargets(model, { f_brow_h: 1 });
    const y1 = mean(partPoints(brow)).y;
    applyMorphTargets(model, {});
    assert.ok(live > 1, 'slider reached body and parts');
    assert.ok(Math.abs(y1 - y0) > 0.0005, `brow morph moves the fitted brows (${(y1 - y0).toFixed(4)} m)`);
    console.log(`[probe] ${tid}: ${groups.length} parts on Head; brow f_brow_h+ dy=${(y1 - y0).toFixed(4)} m; head-follow err=${err.toExponential(1)}; offsets from eye midpoint (m):`, JSON.stringify(report));
  });
}

test('all 9 templates: a hair and a beard fit load and sit on that template head', async () => {
  for (const tid of FP.FITTED_TEMPLATES) {
    const inst = await instance(tid);
    const model = inst.model; model.updateMatrixWorld(true);
    const eyes = skinnedPoints(model, /human_eyes/i); const eyeMid = mean(eyes);
    const groups = await FP.loadFittedParts(model, FP.selectFittedParts({ equipped: { 2: 'mh-hair-short02', 7: 'wh-beard-full' } }, tid),
      { loadScene: (url) => parse(url).then((g) => g.scene) });
    assert.equal(groups.length, 2, tid);
    for (const g of groups) {
      const c = mean(partPoints(g));
      assert.ok(c.distanceTo(eyeMid) < 0.13, `${tid} ${g.userData.whFitted.partId}: within 13 cm of the eyes (${c.distanceTo(eyeMid).toFixed(3)})`);
    }
  }
});

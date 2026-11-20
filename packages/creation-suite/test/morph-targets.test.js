// Real body + face morph targets on the creation-suite template bodies (Phase 3, 2026-11-01).
// Checks the slider catalog, that every template GLB carries a '+' and '-' glTF morph target
// for EVERY slider (no stub sliders), that the packed targets really move vertices after
// dequantization, and the influence logic the suite drives.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { flattenCatalog, wiredSliderIds, applyMorphTargets, cleanValues, displayValue }
  from '../../../customization/creation-suite-ui/js/morph-targets.js';
import { report } from '../../../tools/mb-lab/morph_glb_report.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const cat = JSON.parse(fs.readFileSync(path.join(ROOT, 'customization/templates/morph-sliders.json'), 'utf8'));
const sliders = flattenCatalog(cat);
const templates = JSON.parse(fs.readFileSync(path.join(ROOT, 'customization/templates/body-templates.json'), 'utf8')).templates;

function glbJson(file) {
  const b = fs.readFileSync(file);
  return JSON.parse(b.subarray(20, 20 + b.readUInt32LE(12)).toString('utf8'));
}

test('catalog: two windows (Body Morphing, Face Deformation), unique ids, every slider names an MB-Lab property', () => {
  assert.deepEqual(cat.windows.map(w => w.key), ['body-morph', 'face-morph']);
  const ids = sliders.map(s => s.id);
  assert.equal(new Set(ids).size, ids.length, 'duplicate slider id');
  for (const s of sliders) {
    assert.ok(s.label && s.mb, `${s.id} needs label + mb`);
    assert.match(s.id, /^[bf]_[a-z0-9_]+$/);
  }
  const body = sliders.filter(s => s.window === 'body-morph').length;
  const face = sliders.filter(s => s.window === 'face-morph').length;
  assert.ok(body >= 25 && face >= 40, `body ${body} face ${face}`);
  // WWE 2K CAW face regions (jaw, cheeks, brow, nose, eyes, mouth, chin, ears) and body regions all present
  const groups = new Set(sliders.map(s => s.group));
  for (const g of ['jaw', 'cheeks', 'brows', 'nose', 'eyes', 'mouth', 'chin', 'ears',
    'overall', 'shoulder', 'chest', 'waist', 'upperarm', 'thigh']) assert.ok(groups.has(g), g);
});

test('catalog labels are generic (names law: no source game / tool / real-person names)', () => {
  const deny = ['tekken', 'wwe', '2k', 'mb-lab', 'mblab', 'makehuman', 'mpfb', 'daz', 'metahuman', 'smackdown', 'wrestlemania'];
  const denyFile = path.join(ROOT, 'tools/canon/denylist.json');
  if (fs.existsSync(denyFile)) deny.push(...JSON.parse(fs.readFileSync(denyFile, 'utf8')).terms);
  for (const s of sliders) for (const l of [s.label, s.label_female, s.groupLabel, s.windowLabel].filter(Boolean)) {
    for (const t of deny) assert.ok(!new RegExp(`\\b${t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i').test(l), `${s.id}: "${l}" contains "${t}"`);
  }
});

test('every template GLB carries <id>+ and <id>- morph targets for every slider, on every primitive', () => {
  for (const t of templates) {
    const file = path.join(ROOT, t.base_mesh);
    const j = glbJson(file);
    const morphMeshes = j.meshes.filter(m => m.extras && m.extras.targetNames);
    assert.equal(morphMeshes.length, 1, `${t.id}: one morph mesh`);
    const m = morphMeshes[0];
    const names = new Set(m.extras.targetNames);
    for (const s of sliders) {
      assert.ok(names.has(s.id + '+'), `${t.id} missing ${s.id}+`);
      assert.ok(names.has(s.id + '-'), `${t.id} missing ${s.id}-`);
    }
    for (const p of m.primitives) assert.equal((p.targets || []).length, m.extras.targetNames.length, `${t.id} primitive target count`);
    assert.equal(j.skins.length, 1); assert.equal(j.skins[0].joints.length, 71, `${t.id} 71-joint MB-Lab skeleton`);
    // phone budget: the old flat bakes were ~9 MB each with no morphs
    assert.ok(fs.statSync(file).size < 4_000_000, `${t.id} ${fs.statSync(file).size} B over 4 MB`);
  }
});

test('templates are distinct bodies now (the old bake shipped six identical male meshes)', () => {
  const sizes = new Map();
  for (const t of templates) sizes.set(t.id, fs.readFileSync(path.join(ROOT, t.base_mesh)).toString('base64').slice(-4000));
  assert.equal(new Set(sizes.values()).size, templates.length);
});

test('packed targets really move vertices after meshopt decode + dequantization (powerhouse + striker-w)', async () => {
  for (const id of ['powerhouse', 'striker-w']) {
    const r = await report(path.join(ROOT, `customization/templates/meshes/${id}.glb`));
    const tg = r.meshes.find(m => m.targetNames).targets;
    for (const s of sliders) for (const sign of ['+', '-']) {
      const v = tg[s.id + sign];
      assert.ok(v && v.nonzero > 0 && v.max_m >= 0.0003, `${id} ${s.id}${sign} ${JSON.stringify(v)}`);
      assert.ok(v.max_m < 0.25, `${id} ${s.id}${sign} implausibly large ${v.max_m} m`);
    }
    // face targets stay on the head, body targets are body-scale
    assert.ok(tg['f_nose_w+'].max_m < 0.02 && tg['b_belly+'].max_m > 0.03);
  }
});

function mockMesh(names) {
  const dict = Object.fromEntries(names.map((n, i) => [n, i]));
  return { morphTargetDictionary: dict, morphTargetInfluences: new Array(names.length).fill(0) };
}

test('applyMorphTargets: + side for positive, - side for negative, clamps, resets, leaves cs_* proxies alone', () => {
  const m = mockMesh(['b_weight+', 'b_weight-', 'f_jaw_w+', 'f_jaw_w-', 'cs_belly']);
  m.morphTargetInfluences[4] = 0.7;
  assert.equal(applyMorphTargets([m], { b_weight: 0.4, f_jaw_w: -2 }), 2);
  assert.deepEqual(m.morphTargetInfluences, [0.4, 0, 0, 1, 0.7]);
  applyMorphTargets([m], { b_weight: -0.25 });
  assert.deepEqual(m.morphTargetInfluences, [0, 0.25, 0, 0, 0.7]);
  applyMorphTargets([m], {});
  assert.deepEqual(m.morphTargetInfluences, [0, 0, 0, 0, 0.7]);
});

test('wiredSliderIds needs both sides; cleanValues drops zero / unknown; display is -100..100', () => {
  const m = mockMesh(['b_weight+', 'b_weight-', 'b_tone+']);
  const w = wiredSliderIds([m], [{ id: 'b_weight' }, { id: 'b_tone' }]);
  assert.deepEqual([...w], ['b_weight']);
  assert.deepEqual(cleanValues({ b_weight: 0.123, b_tone: 0, zzz: 1, f_jaw_w: 3 }, sliders), { b_weight: 0.12, f_jaw_w: 1 });
  assert.equal(displayValue(-0.5), -50); assert.equal(displayValue(9), 100);
});

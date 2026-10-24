import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { mergeCatalogs, getEntry, resolveProfileParts } from '../src/catalogs.js';
import { SPINE, spineSlotOf, readinessOf, isEquippable, spineCounts } from '../src/slotmap.js';
import {
  createState, setBodyType, setSkinTone, setMorph, equip, setPlacement,
  setItemColors, addLayer, saveSnapshot, loadSnapshot,
  toCustomizationJson, toSuiteRecord, fromSuiteRecord, attachParts,
  BODY_TYPE_NAMES,
} from '../ui/profile.js';

// Proof against the REAL repo files — no fixtures for the catalog data.
// (Same convention as catalogs.test.js; counts pin today's main and ride
// with catalog PRs when the catalogs grow.)
const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const readJson = (rel) => JSON.parse(readFileSync(join(ROOT, rel), 'utf8'));
const merged = mergeCatalogs(
  readJson('customization/PARTS-REGISTRY.json'),
  readJson('customization/parts/no-mercy/CATALOG.json'),
  readJson('customization/parts-converted/CATALOG.json'),
  readJson('customization/parts-converted/defjam/CATALOG.json'),
  readJson('customization/parts/tekken7/CATALOG.json'),
);
const counts = spineCounts(merged);

// +1 vs 6cc479cf2: the T7 generic skull mask (cmn_hef_skull, 79d67ac3b) — mapped + ready.
test('the runtime now sees every cataloged part (before: registry only, 1,148)', () => {
  assert.equal(merged.length, 7794);
  assert.equal(counts.total, 7794);
  assert.equal(counts.mapped + counts.unmapped, counts.total);
  assert.equal(counts.ready + counts.preview + counts.blocked + counts.record, counts.total);
});

test('spine mapping: 5,577 mapped; the unmapped are named, never dropped', () => {
  assert.equal(counts.mapped, 5577);
  assert.equal(counts.unmapped, 2217);
  const unmapped = merged.filter((e) => spineSlotOf(e) === 'unmapped');
  assert.equal(unmapped.filter((e) => e.source_game === 'defjam' && e.slot === 'unknown').length, 2209);
  assert.equal(unmapped.filter((e) => e.category === 'colors').length, 8);
  for (const s of SPINE) assert.ok(s.id && s.title, 'every spine row is a real menu row');
});

test('readiness: 2,872 equippable; blocked and POINTS are never equippable', () => {
  assert.equal(counts.ready, 2872);
  assert.equal(counts.preview, 1201);
  assert.equal(counts.blocked, 3721);
  assert.equal(counts.record, 0);
  for (const e of merged) {
    const r = readinessOf(e);
    if (r === 'blocked' || r === 'preview-only') assert.equal(isEquippable(e), false, `${e.id} (${r}) must not equip`);
    if (e.glb_primitive === 'POINTS') assert.equal(r, 'preview-only', `${e.id}: POINTS pool is preview data`);
    if ((e.status || '').startsWith('blocked')) assert.equal(r, 'blocked', `${e.id}: blocked stays blocked`);
  }
  // The J2 texture population is the biggest ready pool and sits at MAKE_UP.
  assert.equal(counts.per.make_up.ready, 1477);
  assert.equal(counts.per.face.ready, 390);
  assert.equal(counts.per.full_body.ready, 693);
  // The one mesh-eye GLB in the repo equips (owner law: eyes are parts).
  const lenses = getEntry(merged, 'spidergirl-eye-lenses');
  assert.equal(readinessOf(lenses), 'ready-mesh');
  assert.equal(spineSlotOf(lenses), 'gla');
});

test('a UI-built profile resolves end-to-end and round-trips both save shapes', () => {
  const s = createState({ fighter: 'pantera', attire: 'attire1', name: 'PANTERA' });
  setBodyType(s, 'King Frame');
  setSkinTone(s, '#e5b28c');
  setMorph(s, 'muscle', 0.4); setMorph(s, 'eye_size', 0.25); setMorph(s, 'jaw_width', -0.3);
  const face = merged.find((e) => e.suite_slot === 'face' && readinessOf(e) === 'ready-mesh');
  const upper = merged.find((e) => e.suite_slot === 'upper_body' && readinessOf(e) === 'ready-mesh');
  assert.ok(face && upper, 'real No Mercy mesh parts exist to equip');
  assert.equal(equip(s, face, 'face').ok, true);
  assert.equal(equip(s, upper, 'upper').ok, true);
  setPlacement(s, 'upper', { px: 0.01, ry: 45, s: 9 }); // scale clamps to 2.5
  assert.equal(s.equipped.upper.placement.s, 2.5);
  setItemColors(s, 'upper', ['#111111', '#222222', '#333333', '#444444', '#555555', '#666666']);
  const eye = getEntry(merged, 'eye-yellow-tiger');
  addLayer(s, eye, { rect: [0.1, 0.2, 0.3, 0.3] });

  // Tekken conflict law: FULL_BODY over an equipped UPPER asks first.
  const full = merged.find((e) => spineSlotOf(e) === 'full_body' && isEquippable(e));
  assert.ok(full, 'a real full-body part exists to exercise the conflict');
  const attempt = equip(s, full, 'full_body');
  assert.equal(attempt.ok, false, 'conflicting equip must not apply silently');
  assert.ok(attempt.conflicts.some((c) => c.spine === 'upper'));
  const forced = equip(s, full, 'full_body', { force: true });
  assert.equal(forced.ok, true);
  assert.ok(forced.removed.some((c) => c.spine === 'upper'), 'the victim is named');

  // Wardrobe snapshot: save, change, load — the look comes back whole.
  saveSnapshot(s, 1);
  setMorph(s, 'muscle', -0.9);
  loadSnapshot(s, 1);
  assert.equal(s.morphs.muscle, 0.4);

  const json = toCustomizationJson(s);
  assert.equal(json.version, 1);
  assert.deepEqual(Object.keys(json.item_colors), [upper.suite_slot || 'upper']);
  assert.equal(json.item_colors[upper.suite_slot || 'upper'].length, 5, 'color channels cap at Tekken\u2019s 5');
  const resolved = resolveProfileParts(merged, json);
  assert.ok(resolved.length >= 2);
  assert.ok(resolved.every((r) => r.status === 'resolved'), 'every equipped part resolves in the merged catalog');

  const rec = toSuiteRecord(s);
  assert.equal(rec.profile.name, 'PANTERA');
  assert.ok(BODY_TYPE_NAMES.includes(rec.body.body_type), 'consumer body_type contract');
  assert.equal(rec.body.skin_tone, '#e5b28c');
  assert.equal(typeof rec.parameters.arms.offense, 'number');
  assert.equal(typeof rec.fighting_style.aggression, 'number');

  const back = attachParts(fromSuiteRecord(rec), (partId) => {
    const e = getEntry(merged, partId); return e ? spineSlotOf(e) : null;
  });
  assert.equal(back.morphs.muscle, 0.4);
  assert.ok(back.equipped.face && back.equipped.full_body, 'equips survive the round-trip');
  assert.equal(back.textures.length, 1);
  assert.equal(back.textures[0].kind, 'eye');
});

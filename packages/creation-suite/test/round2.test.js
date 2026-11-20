import test from 'node:test';
import assert from 'node:assert/strict';
import {
  createState, equip, setPlacement, setRegionSwap, removeRegionSwap,
  setHideBaseHair, saveSnapshot, loadSnapshot,
  toCustomizationJson, fromSuiteRecord, attachParts, SWAP_REGIONS,
} from '../ui/profile.js';

// Round 2 (owner orders 2026-10-21): placement by hand must round-trip
// EXACTLY into the bake record; piece swaps + the base-hair hide toggle
// save per-attire and restore.

const hairEntry = {
  id: 'cc0-hair-quaternius-buzzed', suite_slot: 'hair',
  glb: 'customization/parts/hair/cc0/Hair_Buzzed.gltf',
  placement: { px: 0, py: 0, pz: 0, rx: 0, ry: 0, rz: 0, s: 1 },
};

test('placement: nudge-grade edits + per-axis scale survive to the bake record', () => {
  const s = createState({ fighter: 'baek', attire: 'master-white' });
  equip(s, hairEntry, 'hair');
  setPlacement(s, 'hair', { px: 0.03, py: -0.02, rz: 12, sx: 1.1, sy: 0.95 });
  const rec = toCustomizationJson(s);
  assert.deepEqual(rec.parts.hair.placement,
    { px: 0.03, py: -0.02, pz: 0, rx: 0, ry: 0, rz: 12, s: 1, sx: 1.1, sy: 0.95 });
  // and back: a saved record restores the same placement untouched
  const s2 = attachParts(fromSuiteRecord(rec), () => 'hair');
  assert.deepEqual(s2.equipped.hair.placement, rec.parts.hair.placement);
});

test('piece swaps: set/replace/remove, bake record shape, restore', () => {
  const s = createState({ fighter: 'baek', attire: 'master-white' });
  assert.deepEqual(SWAP_REGIONS, ['head', 'torso', 'arm_l', 'arm_r', 'legs']);
  setRegionSwap(s, {
    region: 'head', from_glb: 'roster/baek/attires/attire1/model.glb',
    from_fighter: 'baek', from_attire: 'attire1',
  });
  let rec = toCustomizationJson(s);
  assert.equal(rec.region_swaps.length, 1);
  assert.equal(rec.region_swaps[0].region, 'head');
  assert.equal(rec.region_swaps[0].from_glb, 'roster/baek/attires/attire1/model.glb');
  // replacing the same region swaps the source, never stacks
  setRegionSwap(s, { region: 'head', from_glb: 'roster/deathfang/attires/attire1/model.glb' });
  assert.equal(s.region_swaps.length, 1);
  assert.match(s.region_swaps[0].from_glb, /deathfang/);
  // restore: removing the swap removes it from the record entirely
  removeRegionSwap(s, 'head');
  rec = toCustomizationJson(s);
  assert.equal(rec.region_swaps, undefined);
  // bad specs throw, never save silently
  assert.throws(() => setRegionSwap(s, { region: 'soul', from_glb: 'x.glb' }), /unknown swap region/);
  assert.throws(() => setRegionSwap(s, { region: 'head' }), /from_glb/);
});

test('piece swaps + hide toggle ride wardrobe snapshots and suite records', () => {
  const s = createState({ fighter: 'baek', attire: 'master-white' });
  setRegionSwap(s, { region: 'legs', from_glb: 'roster/baek/attires/attire1/model.glb' });
  setHideBaseHair(s, true);
  saveSnapshot(s, 3);
  removeRegionSwap(s, 'legs');
  setHideBaseHair(s, false);
  assert.equal(toCustomizationJson(s).hide_meshes, undefined);
  loadSnapshot(s, 3);
  const rec = toCustomizationJson(s);
  assert.deepEqual(rec.hide_meshes, ['hair']);
  assert.equal(rec.region_swaps[0].region, 'legs');
  const s2 = fromSuiteRecord(rec);
  assert.equal(s2.hide_base_hair, true);
  assert.equal(s2.region_swaps[0].from_glb, 'roster/baek/attires/attire1/model.glb');
});

// catalog.test.mjs — Tekken 7 parts catalog vs the REAL Creation Suite runtime.
//
// Run: node --test customization/parts/tekken7/catalog.test.mjs
//
// Proves, against real files (no fixtures, no copies):
//  1. The T7 catalog loads through the runtime's own loadCatalog validation.
//  2. Merging it into the real PARTS-REGISTRY disturbs nothing (0 parts today).
//  3. The skull-mask named gap behaves honestly: a profile assigning its
//     part_id resolves as 'unresolved' — reported, never silently dropped —
//     and the gap entry is NOT in parts[] (the runtime can never show a
//     phantom part). When the real part is extracted and appended to parts[],
//     flip the expectations in test 3: status 'resolved', glb set.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import {
  loadCatalog,
  mergeCatalogs,
  entriesForSource,
  getEntry,
  resolveProfileParts,
} from '../../../packages/creation-suite/src/catalogs.js';

const catalogUrl = new URL('./CATALOG.json', import.meta.url);
const registryUrl = new URL('../../PARTS-REGISTRY.json', import.meta.url);

const fetcherFor = (url) => async () => ({
  ok: true,
  status: 200,
  json: async () => JSON.parse(await readFile(url, 'utf8')),
});

const SKULL_MASK_ID = 'tekken7:cmn:full_head:skull-mask';
const T7_SLOTS = [
  'HEAD', 'HAIR', 'FULL_HEAD', 'HAIR_ACC', 'GLA', 'FACE', 'FACE_HAIR',
  'MAKE_UP', 'UPPER', 'FULL_BODY', 'LOWER', 'UPPER_ACC', 'LOWER_ACC',
  'EXTRA', 'Effects', 'Aura',
];

test('catalog loads through the real loadCatalog and is honestly empty', async () => {
  const catalog = await loadCatalog('tekken7-catalog', fetcherFor(catalogUrl));
  assert.ok(Array.isArray(catalog.parts), 'catalog must carry parts[]');
  assert.equal(catalog._meta.total, catalog.parts.length);
  assert.equal(catalog.parts.length, 0, 'survey verdict: 0 T7 part meshes in holdings');
  // every slot class surveyed, all zero
  for (const slot of T7_SLOTS) {
    assert.equal(catalog._meta.by_slot[slot], 0, `by_slot.${slot}`);
    assert.ok(catalog._meta.suite_slot_mapping.includes(slot), `mapping covers ${slot}`);
  }
});

test('merging into the real registry disturbs nothing', async () => {
  const registry = JSON.parse(await readFile(registryUrl, 'utf8'));
  const catalog = await loadCatalog('tekken7-catalog', fetcherFor(catalogUrl));
  const merged = mergeCatalogs(registry, catalog);
  assert.equal(merged.length, registry.parts.length, 'T7 catalog adds 0 entries today');
  assert.equal(entriesForSource(merged, 'tekken7').length, 0);
});

test('skull mask: named gap, unresolved by the runtime, never a phantom part', async () => {
  const registry = JSON.parse(await readFile(registryUrl, 'utf8'));
  const catalog = await loadCatalog('tekken7-catalog', fetcherFor(catalogUrl));
  const merged = mergeCatalogs(registry, catalog);

  // the gap is documented, with the full expected classification
  const gap = (catalog.named_gaps || []).find((g) => g.id === SKULL_MASK_ID);
  assert.ok(gap, 'skull mask must be registered as a named gap');
  assert.equal(gap.slot, 'FULL_HEAD');
  assert.equal(gap.slot_id, 3);
  assert.equal(gap.scope, 'generic');
  assert.equal(gap.player_cus_id, 0);
  assert.equal(gap.suite_slot, 'full_head');
  assert.equal(gap.status, 'named_gap_not_in_holdings');

  // …but it is NOT a part: the runtime cannot resolve or display it
  assert.equal(getEntry(merged, SKULL_MASK_ID), null);
  const resolved = resolveProfileParts(merged, {
    parts: { full_head: { part_id: SKULL_MASK_ID } },
  });
  assert.equal(resolved.length, 1);
  assert.equal(resolved[0].part_id, SKULL_MASK_ID, 'assignment is reported, not dropped');
  assert.equal(resolved[0].status, 'unresolved');
  assert.equal(resolved[0].glb, null);
});

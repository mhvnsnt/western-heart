// catalog.test.mjs — Tekken 6 (PSP) parts catalog vs the REAL Creation Suite runtime.
//
// Run: node --test customization/parts/tekken6/catalog.test.mjs
//
// Proves, against real files (no fixtures, no copies):
//  1. The T6 catalog loads through the runtime's own loadCatalog validation.
//  2. Merging it into the real PARTS-REGISTRY disturbs nothing (0 parts today).
//  3. The skull-mask named gap behaves honestly: the name 'Skull Mask' is
//     confirmed in the game's own item tables (see CATALOG.json named_gaps
//     for the two records), but no mesh has been extracted — a profile
//     assigning its part_id resolves as 'unresolved' (reported, never
//     silently dropped) and the gap entry is NOT in parts[] (the runtime
//     can never show a phantom part). When the real part is extracted and
//     appended to parts[], flip the expectations in test 3: status
//     'resolved', glb set.

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

const SKULL_MASK_ID = 'tekken6:cmn:head:skull-mask';
const T6_SLOTS = ['head', 'upper_body', 'lower_body', 'other'];

test('catalog loads through the real loadCatalog and is honestly empty', async () => {
  const catalog = await loadCatalog('tekken6-catalog', fetcherFor(catalogUrl));
  assert.ok(Array.isArray(catalog.parts), 'catalog must carry parts[]');
  assert.equal(catalog._meta.total, catalog.parts.length);
  assert.equal(catalog.parts.length, 0, 'survey verdict: 0 T6 part meshes extracted — decode blocked, see survey doc');
  // every T6 slot class surveyed, all zero
  for (const slot of T6_SLOTS) {
    assert.equal(catalog._meta.by_slot[slot], 0, `by_slot.${slot}`);
    assert.ok(catalog._meta.suite_slot_mapping.includes(slot), `mapping covers ${slot}`);
  }
});

test('merging into the real registry disturbs nothing', async () => {
  const registry = JSON.parse(await readFile(registryUrl, 'utf8'));
  const catalog = await loadCatalog('tekken6-catalog', fetcherFor(catalogUrl));
  const merged = mergeCatalogs(registry, catalog);
  assert.equal(merged.length, registry.parts.length, 'T6 catalog adds 0 entries today');
  assert.equal(entriesForSource(merged, 'tekken6').length, 0);
});

test('skull mask: name confirmed in T6 tables, mesh is a named gap — unresolved, never a phantom part', async () => {
  const registry = JSON.parse(await readFile(registryUrl, 'utf8'));
  const catalog = await loadCatalog('tekken6-catalog', fetcherFor(catalogUrl));
  const merged = mergeCatalogs(registry, catalog);

  // the gap is documented, with the full expected classification
  const gap = (catalog.named_gaps || []).find((g) => g.id === SKULL_MASK_ID);
  assert.ok(gap, 'skull mask must be registered as a named gap');
  assert.equal(gap.slot, 'head');
  assert.equal(gap.slot_id, 1);
  assert.equal(gap.suite_slot, 'hair');
  assert.equal(gap.status, 'named_gap_mesh_not_extracted');
  // name-side evidence is recorded on the gap, not asserted as a part
  assert.ok(gap.expected_source.includes('Skull Mask'), 'gap records the name-table evidence');
  assert.ok(gap.expected_source.includes('124705559'), 'gap records record A (bulk_offset)');
  assert.ok(gap.expected_source.includes('129124535'), 'gap records record B (bulk_offset)');

  // …but it is NOT a part: the runtime cannot resolve or display it
  assert.equal(getEntry(merged, SKULL_MASK_ID), null);
  const resolved = resolveProfileParts(merged, {
    parts: { hair: { part_id: SKULL_MASK_ID } },
  });
  assert.equal(resolved.length, 1);
  assert.equal(resolved[0].part_id, SKULL_MASK_ID, 'assignment is reported, not dropped');
  assert.equal(resolved[0].status, 'unresolved');
  assert.equal(resolved[0].glb, null);
});

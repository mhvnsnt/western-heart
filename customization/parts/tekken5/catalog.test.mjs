// catalog.test.mjs — Tekken 5 parts catalog vs the REAL Creation Suite runtime.
//
// Run: node --test customization/parts/tekken5/catalog.test.mjs
//
// Modeled on customization/parts/tekken7/catalog.test.mjs (PR #437 shape).
// Proves, against real files (no fixtures, no copies):
//  1. The T5 catalog loads through the runtime's own loadCatalog validation
//     and is honestly empty: T5's slot-item meshes were NOT found in DATA1
//     (survey doc S3-S5), so parts[] stays empty until real parts land.
//  2. Merging it into the real PARTS-REGISTRY disturbs nothing.
//  3. The T5 skull-mask survey target behaves honestly: registered as a
//     named gap with status named_gap_not_found_in_surveyed_data, NOT in
//     parts[], and a profile assigning its part_id resolves 'unresolved' —
//     reported, never silently dropped. When/if a real T5 skull mask is
//     extracted (ctype-5 VIF 0x82 decode or the DATA0 cipher), flip test 3.

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

const SKULL_MASK_ID = 'tekken5:cmn:full_head:skull-mask';
const T7_SLOTS = [
  'HEAD', 'HAIR', 'FULL_HEAD', 'HAIR_ACC', 'GLA', 'FACE', 'FACE_HAIR',
  'MAKE_UP', 'UPPER', 'FULL_BODY', 'LOWER', 'UPPER_ACC', 'LOWER_ACC',
  'EXTRA', 'Effects', 'Aura',
];

test('catalog loads through the real loadCatalog and is honestly empty', async () => {
  const catalog = await loadCatalog('tekken5-catalog', fetcherFor(catalogUrl));
  assert.ok(Array.isArray(catalog.parts), 'catalog must carry parts[]');
  assert.equal(catalog._meta.total ?? catalog.parts.length, catalog.parts.length);
  assert.equal(catalog.parts.length, 0, 'survey verdict: 0 T5 slot-item meshes converted from DATA1');
  for (const slot of T7_SLOTS) {
    assert.equal(catalog._meta.by_slot[slot], 0, `by_slot.${slot}`);
    assert.ok(catalog._meta.suite_slot_mapping.length > 0, 'mapping documented');
  }
  // the census behind the empty catalog is pinned, byte-derived numbers
  assert.equal(catalog._meta.census.data1_table_records, 1571);
  assert.equal(catalog._meta.census.data1_files_extracted_checksum_verified, 1355);
  assert.equal(catalog._meta.census.data1_table_failures, 0);
  assert.equal(catalog._meta.census.character_costume_packs_count19, 80);
});

test('merging into the real registry disturbs nothing', async () => {
  const registry = JSON.parse(await readFile(registryUrl, 'utf8'));
  const catalog = await loadCatalog('tekken5-catalog', fetcherFor(catalogUrl));
  const merged = mergeCatalogs(registry, catalog);
  assert.equal(merged.length, registry.parts.length, 'T5 catalog adds 0 entries today');
  assert.equal(entriesForSource(merged, 'tekken5').length, 0);
});

test('named gaps are documented, unresolved by the runtime, never phantom parts', async () => {
  const registry = JSON.parse(await readFile(registryUrl, 'utf8'));
  const catalog = await loadCatalog('tekken5-catalog', fetcherFor(catalogUrl));
  const merged = mergeCatalogs(registry, catalog);

  const gapIds = [
    'tekken5:packs:full_body:costume-models',
    'tekken5:ctype5:unknown_slot:vif-0x82-models',
    'tekken5:data0:unknown_slot:undecrypted-archive',
    SKULL_MASK_ID,
  ];
  for (const id of gapIds) {
    const gap = (catalog.named_gaps || []).find((g) => g.id === id);
    assert.ok(gap, `named gap must be registered: ${id}`);
    assert.equal(getEntry(merged, id), null, `gap must not resolve as a part: ${id}`);
  }

  const skull = (catalog.named_gaps || []).find((g) => g.id === SKULL_MASK_ID);
  assert.equal(skull.slot, 'FULL_HEAD');
  assert.equal(skull.slot_id, 3);
  assert.equal(skull.scope, 'generic');
  assert.equal(skull.player_cus_id, 0);
  assert.equal(skull.suite_slot, 'full_head');
  assert.equal(skull.status, 'named_gap_not_found_in_surveyed_data');

  const resolved = resolveProfileParts(merged, {
    parts: { full_head: { part_id: SKULL_MASK_ID } },
  });
  assert.equal(resolved.length, 1);
  assert.equal(resolved[0].part_id, SKULL_MASK_ID, 'assignment is reported, not dropped');
  assert.equal(resolved[0].status, 'unresolved');
  assert.equal(resolved[0].glb, null);
});

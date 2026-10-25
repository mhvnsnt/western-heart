// catalog.test.mjs — Tekken 7 parts catalog vs the REAL Creation Suite runtime.
//
// Run: node --test customization/parts/tekken7/catalog.test.mjs
//
// Proves, against real files (no fixtures, no copies):
//  1. The T7 catalog loads through the runtime's own loadCatalog validation.
//  2. Merging it into the real PARTS-REGISTRY adds exactly the landed parts.
//  3. The skull-mask named gap FLIPPED 2026-10-21 (W6 lane): a profile assigning its
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

test('catalog loads through the real loadCatalog with the landed skull mask', async () => {
  const catalog = await loadCatalog('tekken7-catalog', fetcherFor(catalogUrl));
  assert.ok(Array.isArray(catalog.parts), 'catalog must carry parts[]');
  assert.equal(catalog._meta.total, catalog.parts.length);
  // FLIPPED 2026-10-21 (W6 piecewise lane): the skull mask was really
  // extracted from the T7 game tree and landed in parts[] — the survey's
  // §3.5 flip, recorded here as instructed there.
  assert.equal(catalog.parts.length, 1, 'one landed part: the skull mask');
  // every slot class present in the mapping; only FULL_HEAD has landed so far
  for (const slot of T7_SLOTS) {
    assert.equal(catalog._meta.by_slot[slot], slot === 'FULL_HEAD' ? 1 : 0, `by_slot.${slot}`);
    assert.ok(catalog._meta.suite_slot_mapping.includes(slot), `mapping covers ${slot}`);
  }
});

test('merging into the real registry adds exactly the landed part', async () => {
  const registry = JSON.parse(await readFile(registryUrl, 'utf8'));
  const catalog = await loadCatalog('tekken7-catalog', fetcherFor(catalogUrl));
  const merged = mergeCatalogs(registry, catalog);
  assert.equal(merged.length, registry.parts.length + 1, 'T7 catalog adds the skull mask');
  assert.equal(entriesForSource(merged, 'tekken7').length, 1);
});

test('skull mask: named gap RESOLVED — the runtime now resolves the real part', async () => {
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
  assert.equal(gap.status, 'resolved_in_parts');

  // FLIPPED 2026-10-21 (W6): the real part landed in parts[] — the runtime
  // resolves it with its GLB, exactly as the survey §3.5/§4 promised.
  const entry = getEntry(merged, SKULL_MASK_ID);
  assert.ok(entry, 'skull mask entry must exist in parts[]');
  assert.equal(entry.glb, 'customization/parts/tekken7/full_head/skull-mask/skull-mask.glb');
  const resolved = resolveProfileParts(merged, {
    parts: { full_head: { part_id: SKULL_MASK_ID } },
  });
  assert.equal(resolved.length, 1);
  assert.equal(resolved[0].part_id, SKULL_MASK_ID, 'assignment is reported, not dropped');
  assert.equal(resolved[0].status, 'resolved');
  assert.equal(resolved[0].glb, 'customization/parts/tekken7/full_head/skull-mask/skull-mask.glb');
});

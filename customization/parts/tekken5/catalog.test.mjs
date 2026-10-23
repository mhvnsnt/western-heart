// catalog.test.mjs — Tekken 5 parts catalog vs the REAL Creation Suite runtime.
//
// Run: node --test customization/parts/tekken5/catalog.test.mjs
//
// Modeled on customization/parts/tekken7/catalog.test.mjs (PR #437 shape).
// Proves, against real files (no fixtures, no copies):
//  1. The T5 catalog loads through the runtime's own loadCatalog validation
//     and carries the W7e conversion: all 80 costume packs as FULL_BODY
//     parts (whole-costume granularity — T5's data predates the slot
//     schema, survey S3/S7), every entry release-backed with a sha256.
//  2. Merging it into the real PARTS-REGISTRY adds exactly those 80
//     entries and disturbs nothing else.
//  3. The remaining named gaps behave honestly: still registered as named
//     gaps, NOT in parts[], and a profile assigning the skull-mask gap id
//     resolves 'unresolved' — reported, never silently dropped. The
//     costume-models gap has flipped: it now resolves as a real part.

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
const COSTUME_ID = 'tekken5:cmn:full_body:pack0240-costume';
const T7_SLOTS = [
  'HEAD', 'HAIR', 'FULL_HEAD', 'HAIR_ACC', 'GLA', 'FACE', 'FACE_HAIR',
  'MAKE_UP', 'UPPER', 'FULL_BODY', 'LOWER', 'UPPER_ACC', 'LOWER_ACC',
  'EXTRA', 'Effects', 'Aura',
];

test('catalog loads through the real loadCatalog with 80 converted FULL_BODY costume parts', async () => {
  const catalog = await loadCatalog('tekken5-catalog', fetcherFor(catalogUrl));
  assert.ok(Array.isArray(catalog.parts), 'catalog must carry parts[]');
  assert.equal(catalog._meta.total ?? catalog.parts.length, catalog.parts.length);
  assert.equal(catalog.parts.length, 80, 'W7e: all 80 T5 costume packs converted');
  assert.equal(catalog.parts.filter((p) => p.conversion.status === 'converted').length, 79, '79 fully textured');
  for (const slot of T7_SLOTS) {
    assert.equal(catalog._meta.by_slot[slot], slot === 'FULL_BODY' ? 80 : 0, `by_slot.${slot}`);
    assert.ok(catalog._meta.suite_slot_mapping.length > 0, 'mapping documented');
  }
  for (const p of catalog.parts) {
    assert.equal(p.slot, 'FULL_BODY');
    assert.equal(p.suite_slot, 'full_body');
    assert.equal(p.slot_id, 10);
    assert.equal(p.part_class, 'mesh_part');
    assert.equal(p.char_id, null, 'no data-proven pack->character table; attribution stays null');
    assert.equal(p.conversion.glb_release.tag, 'tekken5-costume-glbs-v1');
    assert.match(p.conversion.glb_release.sha256, /^[0-9a-f]{64}$/);
    assert.ok(p.conversion.glb_release.size > 0);
    assert.equal(p.glb, p.file);
    assert.ok(p.nverts > 0 && p.ntris > 0, 'validated GLB geometry counts');
    assert.equal(p.textures.materials_textured, p.textures.images_embedded);
    if (p.id === 'tekken5:cmn:full_body:pack1109-costume') {
      // the one documented partial: pack 1109's sub01 is a 192-byte
      // placeholder TIM2 (1 picture); its model references textureIndex 4,
      // which does not exist in the pack — geometry converted, no texture
      // could be bound from pack data (conversion doc, failures section).
      assert.equal(p.conversion.status, 'converted_geometry_only_missing_pack_texture');
      assert.equal(p.textures.images_embedded, 0);
      assert.deepEqual(p.conversion.source_pack.missing_tex_indices, [4]);
    } else {
      assert.equal(p.conversion.status, 'converted');
      assert.ok(p.textures.images_embedded >= 1, 'textures bound');
    }
  }
  // the census behind the catalog is pinned, byte-derived numbers
  assert.equal(catalog._meta.census.data1_table_records, 1571);
  assert.equal(catalog._meta.census.data1_files_extracted_checksum_verified, 1355);
  assert.equal(catalog._meta.census.data1_table_failures, 0);
  assert.equal(catalog._meta.census.character_costume_packs_count19, 80);
  assert.equal(catalog._meta.census.costume_packs_converted_glb, 80);
});

test('merging into the real registry adds exactly the 80 T5 entries', async () => {
  const registry = JSON.parse(await readFile(registryUrl, 'utf8'));
  const catalog = await loadCatalog('tekken5-catalog', fetcherFor(catalogUrl));
  const merged = mergeCatalogs(registry, catalog);
  assert.equal(merged.length, registry.parts.length + 80, 'T5 catalog adds its 80 converted entries');
  assert.equal(entriesForSource(merged, 'tekken5').length, 80);
});

test('named gaps are documented, unresolved by the runtime, never phantom parts', async () => {
  const registry = JSON.parse(await readFile(registryUrl, 'utf8'));
  const catalog = await loadCatalog('tekken5-catalog', fetcherFor(catalogUrl));
  const merged = mergeCatalogs(registry, catalog);

  const gapIds = [
    'tekken5:ctype5:unknown_slot:vif-0x82-models',
    'tekken5:data0:unknown_slot:undecrypted-archive',
    SKULL_MASK_ID,
  ];
  for (const id of gapIds) {
    const gap = (catalog.named_gaps || []).find((g) => g.id === id);
    assert.ok(gap, `named gap must be registered: ${id}`);
    assert.equal(getEntry(merged, id), null, `gap must not resolve as a part: ${id}`);
  }
  // the costume-models gap has flipped: no longer a gap, now a real part
  assert.equal((catalog.named_gaps || []).find((g) => g.id === 'tekken5:packs:full_body:costume-models'), undefined);
  const costume = getEntry(merged, COSTUME_ID);
  assert.ok(costume, 'pack0240 costume resolves as a part');
  assert.equal(costume.slot, 'FULL_BODY');

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

  const resolvedCostume = resolveProfileParts(merged, {
    parts: { full_body: { part_id: COSTUME_ID } },
  });
  assert.equal(resolvedCostume.length, 1);
  assert.equal(resolvedCostume[0].status, 'resolved');
  assert.equal(resolvedCostume[0].glb, 'customization/parts/tekken5/full_body/pack0240-costume/pack0240-costume.glb');
});

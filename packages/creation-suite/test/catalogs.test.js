import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  mergeCatalogs, entriesForSlot, entriesForSource, entriesForClass,
  getEntry, conversionSummary, resolveProfileParts,
} from '../src/catalogs.js';

// Proof against the REAL repo files — no fixtures for the catalog data.
const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const readJson = (rel) => JSON.parse(readFileSync(join(ROOT, rel), 'utf8'));
const registry = readJson('customization/PARTS-REGISTRY.json');
const nmCatalog = readJson('customization/parts/no-mercy/CATALOG.json');
const merged = mergeCatalogs(registry, nmCatalog);

function glbJson(relPath) {
  const buf = readFileSync(join(ROOT, relPath));
  assert.equal(buf.toString('utf8', 0, 4), 'glTF', `${relPath}: bad magic`);
  const jsonLen = buf.readUInt32LE(12);
  assert.equal(buf.readUInt32LE(16), 0x4e4f534a, `${relPath}: first chunk is not JSON`);
  return JSON.parse(buf.toString('utf8', 20, 20 + jsonLen));
}

test('no-mercy catalog shape + counts', () => {
  assert.equal(nmCatalog.parts.length, 682);
  assert.equal(nmCatalog.parts.filter((p) => p.part_class === 'mesh_part').length, 303);
  assert.equal(nmCatalog.parts.filter((p) => p.part_class === 'texture_part').length, 379);
});

test('merge dedupes by file (registry wins), nothing lost', () => {
  const regFiles = new Set(registry.parts.map((p) => p.file).filter(Boolean));
  const shared = nmCatalog.parts.filter((p) => regFiles.has(p.file)).length;
  assert.ok(shared >= 30, `expected the registry's no-mercy files to dedupe, got ${shared}`);
  assert.equal(merged.length, registry.parts.length + nmCatalog.parts.length - shared);
  assert.equal(entriesForSource(merged, 'no-mercy').length, 682);
});

test('enumeration by slot and class reaches the wired parts', () => {
  assert.ok(entriesForSlot(merged, 'face').length >= 194);
  assert.ok(entriesForSlot(merged, 'upper_body').length >= 132);
  assert.equal(entriesForClass(nmCatalog.parts, 'mesh_part').length, 303);
  const anyMesh = nmCatalog.parts.find((p) => p.part_class === 'mesh_part');
  assert.equal(getEntry(merged, anyMesh.id)?.file, anyMesh.file);
});

test('every converted GLB exists and carries position/normal/uv/vertex-color', () => {
  const meshParts = nmCatalog.parts.filter((p) => p.part_class === 'mesh_part');
  for (const p of meshParts) {
    assert.equal(p.conversion.status, 'converted', `${p.id}: not stamped converted`);
    assert.ok(p.glb && existsSync(join(ROOT, p.glb)), `${p.id}: GLB missing at ${p.glb}`);
    const attrs = glbJson(p.glb).meshes[0].primitives[0].attributes;
    for (const a of ['POSITION', 'NORMAL', 'TEXCOORD_0', 'COLOR_0'])
      assert.ok(a in attrs, `${p.id}: GLB missing ${a}`);
  }
  assert.deepEqual(conversionSummary(nmCatalog.parts),
    { total: 682, converted: 303, pending: 0, not_required: 379, failed: 0, none: 0 });
});

test('a customization.json v1 profile resolves its parts end-to-end', () => {
  const face = nmCatalog.parts.find((p) => p.suite_slot === 'face' && p.part_class === 'mesh_part');
  const body = nmCatalog.parts.find((p) => p.suite_slot === 'upper_body' && p.part_class === 'mesh_part');
  const profile = {
    version: 1,
    parts: {
      face: { part_id: face.id, placement: { position: [0, 0, 0] } },
      upper_body: { part_id: body.id },
      hair: { part_id: 'no-mercy:does-not-exist' },
    },
  };
  const resolved = resolveProfileParts(merged, profile);
  assert.equal(resolved.length, 3, 'unresolved parts are reported, never dropped');
  const bySlot = Object.fromEntries(resolved.map((r) => [r.slot, r]));
  assert.equal(bySlot.face.status, 'resolved');
  assert.equal(bySlot.face.glb, face.glb);
  assert.ok(existsSync(join(ROOT, bySlot.face.glb)));
  assert.equal(bySlot.upper_body.status, 'resolved');
  assert.equal(bySlot.hair.status, 'unresolved');
  assert.equal(bySlot.hair.entry, null);
});

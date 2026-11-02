// Parts + face decals step (2026-11-02): 179 WMXIX face overlay PNGs
// wired into the suite catalog as decal_logo texture parts, the same
// way the 99 No Mercy tattoos were wired in #1505.
// - Face_op overlays (140): PNGs with >20% transparent pixels in
//   customization/parts-converted/wmxix-textures/TEX/Face_op/ — masks,
//   face-paint patterns and facial marks, NOT labeled scars (no file
//   in the repo is named "scar"; see the handoff doc).
// - MAKE_UP overlays (39): ty2_* PNGs with >20% transparent pixels
//   in .../TEX/64gara/ — logo/tattoo decals, likewise not scars.
// Node, no browser. Run: node --test test/parts-face-decals.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
// CI's unit-test job is a sparse checkout without customization/: a file that
// is not on disk is read from git's object store (the commit under test).
const bytes = (rel) => existsSync(join(ROOT, rel)) ? readFileSync(join(ROOT, rel))
  : execFileSync('git', ['show', `HEAD:${rel}`], { cwd: ROOT, maxBuffer: 1 << 28 });
const src = (rel) => bytes(rel).toString('utf8');
const TRACKED = new Set(execFileSync('git', ['ls-files'], { cwd: ROOT, maxBuffer: 1 << 28 }).toString().split('\n'));
const shipped = (rel) => TRACKED.has(rel) || existsSync(join(ROOT, rel));

const CATALOG = JSON.parse(src('customization/creation-suite-ui/data/parts-catalog.json'));
const FACEOP = 'customization/parts-converted/wmxix-textures/TEX/Face_op';
const MAKEUP = 'customization/parts-converted/wmxix-textures/TEX/64gara';
const DECALS = CATALOG.parts.filter((p) => p.source === FACEOP || p.source === MAKEUP);

test('catalog header totals match the parts array after face decals', () => {
  assert.equal(CATALOG.total, CATALOG.parts.length, 'header total == parts length');
  const sum = Object.values(CATALOG.counts).reduce((a, b) => a + b, 0);
  assert.equal(sum, CATALOG.total, 'header counts sum == total');
  assert.equal(CATALOG.counts[FACEOP], 140, 'Face_op decal count is 140');
  assert.equal(CATALOG.counts[MAKEUP], 39, 'MAKE_UP decal count is 39');
});

test('the 179 face decals are wired, unique, and not pending', () => {
  assert.equal(DECALS.length, 179, 'face decal entries');
  const ids = new Set(CATALOG.parts.map((p) => p.id));
  assert.equal(ids.size, CATALOG.parts.length, 'no duplicate catalog ids');
  for (const p of DECALS) {
    assert.equal(p.part_class, 'texture_part', `${p.id} part_class`);
    assert.equal(p.suite_slot, 'decal_logo', `${p.id} suite_slot`);
    assert.equal(p.geometry_pending, false, `${p.id} is not pending`);
    assert.ok(p.editable.includes('opacity'), `${p.id} opacity is editable (wear-off)`);
    assert.ok(shipped(p.asset), `${p.id} PNG is in the repo: ${p.asset}`);
  }
});

test('decal_logo totals after face decals: 290 entries', () => {
  const decals = CATALOG.parts.filter((p) => p.suite_slot === 'decal_logo');
  assert.equal(decals.length, 290, 'decal_logo entries (111 before + 179 face decals)');
});

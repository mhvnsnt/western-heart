// Parts + tattoos step (2026-11-02): 99 No Mercy tattoo PNGs wired into the
// suite catalog as decal_logo texture parts.
// Node, no browser. Run: node --test test/parts-tattoos.test.mjs
// Proves the catalog entries exist, are unique, are not pending, and point
// at PNG files that are actually in the repo — not name-only rows.
// Tattoos surface under Decals in the suite (PARTS_TREE has no dedicated
// tattoo category yet); placement is null, so the suite preview falls
// back to its chest-socket marker until a placement is authored.
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
const TATTOOS = CATALOG.parts.filter((p) => p.source === 'teardown/wwf-no-mercy/textures/rom/tattoo');

test('catalog header totals match the parts array after tattoos', () => {
  assert.equal(CATALOG.total, CATALOG.parts.length, 'header total == parts length');
  const sum = Object.values(CATALOG.counts).reduce((a, b) => a + b, 0);
  assert.equal(sum, CATALOG.total, 'header counts sum == total');
  assert.equal(CATALOG.counts['teardown/wwf-no-mercy/textures/rom/tattoo'], 99, 'tattoo count is 99');
});

test('the 99 No Mercy tattoos are wired, unique, and not pending', () => {
  assert.equal(TATTOOS.length, 99, 'tattoo entries');
  const ids = new Set(CATALOG.parts.map((p) => p.id));
  assert.equal(ids.size, CATALOG.parts.length, 'no duplicate catalog ids');
  for (const p of TATTOOS) {
    assert.equal(p.part_class, 'texture_part', `${p.id} part_class`);
    assert.equal(p.suite_slot, 'decal_logo', `${p.id} suite_slot`);
    assert.equal(p.geometry_pending, false, `${p.id} is not pending`);
    assert.match(p.asset, /^teardown\/wwf-no-mercy\/textures\/rom\/tattoo\/Tattoo_[0-9A-F]+\.png$/, `${p.id} asset path`);
    assert.ok(shipped(p.asset), `${p.id} PNG is in the repo: ${p.asset}`);
  }
});

test('decal_logo totals after tattoos: 111 entries', () => {
  const decals = CATALOG.parts.filter((p) => p.suite_slot === 'decal_logo');
  assert.equal(decals.length, 111, 'decal_logo entries (12 before + 99 tattoos)');
});

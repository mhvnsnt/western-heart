// Parts + hair step (2026-11-02): 5 AshLane hair GLBs wired into the suite catalog.
// Node, no browser. Run: node --test test/parts-ashlane-hair.test.mjs
// Proves the catalog entries exist, are unique, are not pending, and point at
// GLB files that are actually in the repo — not name-only rows.
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
const ASHLANE = [
  ['ashlane-hair-echo-long-green', 'customization/parts/ashlane/hair/hair_echo_long_green.glb'],
  ['ashlane-hair-hollow-long-black', 'customization/parts/ashlane/hair/hair_hollow_long_black.glb'],
  ['ashlane-hair-static-blond-beard', 'customization/parts/ashlane/hair/hair_static_blond_beard.glb'],
  ['ashlane-hair-theory-locs-beads', 'customization/parts/ashlane/hair/hair_theory_locs_beads.glb'],
  ['ashlane-hair-theory-locs-pinned', 'customization/parts/ashlane/hair/hair_theory_locs_pinned.glb'],
];

test('catalog header totals match the parts array', () => {
  assert.equal(CATALOG.total, CATALOG.parts.length, 'header total == parts length');
  const sum = Object.values(CATALOG.counts).reduce((a, b) => a + b, 0);
  assert.equal(sum, CATALOG.total, 'header counts sum == total');
  assert.equal(CATALOG.counts.ashlane, 5, 'ashlane count is 5');
});

test('the 5 AshLane hair entries are wired, unique, and not pending', () => {
  const ids = new Set(CATALOG.parts.map((p) => p.id));
  assert.equal(ids.size, CATALOG.parts.length, 'no duplicate catalog ids');
  for (const [id, glb] of ASHLANE) {
    const p = CATALOG.parts.find((x) => x.id === id);
    assert.ok(p, `${id} is in the catalog`);
    assert.equal(p.part_class, 'mesh_part', `${id} part_class`);
    assert.equal(p.suite_slot, 'hair', `${id} suite_slot`);
    assert.equal(p.socket, 'head', `${id} socket`);
    assert.equal(p.geometry_pending, false, `${id} is not pending`);
    assert.equal(p.glb, glb, `${id} glb path`);
    assert.equal(p.asset, glb, `${id} asset path`);
    assert.ok(shipped(glb), `${id} GLB is in the repo: ${glb}`);
  }
});

test('hair totals after wiring: 365 entries, 53 wired, 50 with a glb', () => {
  // 2026-11-08 (hair-wiring lane, Afro PR): +1 — Angel Afro, Megami hair
  // option (suite_slot 'hair', wired with GLB) over 364/52/49.
  // 2026-11-08 (hair-wiring lane, Megami PR): +1 — Flora, Megami's main
  // default hairstyle (suite_slot 'hair', wired with GLB) over 363/51/48.
  // 2026-11-08 (hair-wiring lane): +31 Tekken 7 HAIR entries (suite_slot
  // 'hair', all wired with GLBs) over the 332 / 20 / 17 baseline.
  const hair = CATALOG.parts.filter((p) => p.suite_slot === 'hair');
  assert.equal(hair.length, 365, 'hair entries');
  assert.equal(hair.filter((p) => !p.geometry_pending).length, 53, 'hair wired');
  assert.equal(hair.filter((p) => p.glb).length, 50, 'hair with glb');
});

test('create-fighter catalog header no longer cites the stale 3,372 figure', () => {
  const s = src('customization/create-fighter/js/catalog.js');
  assert.ok(!s.includes('3,372-part'), 'stale 3,372 figure is gone');
  assert.match(s, /7,960-part index/, 'header cites the 7,960-part index');
});

/* Cape Jones arenas (2026-10-24 owner directives 20:35 + 20:38 CDT).
   Verifies the two stage defs in game/js/stages.js by reading the file
   as text (no three.js / DOM runtime needed): ids, tier wiring, builder
   registration, locked beach sky/lighting, standard fight bounds, the
   zero-external-asset rule (no obj/glb/pano/map keys, so fight-load has
   no arena-asset 404 surface), no declared breakables (Lane 5 generic
   stage-levels treatment), music-pool coordination ids, and the mirrored
   Netlify /stages/* proxy pair. Run: node --test test/cape-arenas.test.mjs */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const root = new URL('..', import.meta.url);
const stagesSrc = readFileSync(fileURLToPath(new URL('game/js/stages.js', root)), 'utf8');
const netlifyToml = readFileSync(fileURLToPath(new URL('game/netlify.toml', root)), 'utf8');
const redirects = readFileSync(fileURLToPath(new URL('game/_redirects', root)), 'utf8');

// Slice one stage def: from its `id: '...'` line to the next top-level
// def start (`\n  {\n    id: '`) or the STAGES array close.
function defBlock(id) {
  const start = stagesSrc.indexOf(`id: '${id}'`);
  assert.notEqual(start, -1, `stage def ${id} missing`);
  let end = stagesSrc.indexOf("\n  {\n    id: '", start + 10);
  if (end === -1) end = stagesSrc.indexOf('\n];', start);
  assert.notEqual(end, -1, `stage def ${id} has no terminator`);
  return stagesSrc.slice(start, end);
}

const HOUSE = 'cape-jones-arena';
const BEACH = 'cape-jones-halloween-beach';

test('both Cape Jones stage ids exist, exactly once each, in tier CAPE JONES', () => {
  for (const id of [HOUSE, BEACH]) {
    assert.equal(stagesSrc.split(`id: '${id}'`).length - 1, 1, `${id} must appear exactly once`);
    assert.match(defBlock(id), /tier: 'CAPE JONES'/, `${id} tier`);
  }
});

test('CAPE JONES tier is in STAGE_TIERS so stage select renders both cards', () => {
  assert.match(stagesSrc, /STAGE_TIERS = \[[^\]]*'CAPE JONES'/);
});

test('both builders exist and are registered in BUILDERS', () => {
  for (const [fn, key] of [['buildCapeHouse', 'capehouse'], ['buildCapeBeach', 'capebeach']]) {
    assert.match(stagesSrc, new RegExp(`function ${fn}\\(g, def, api\\)`), `${fn} defined`);
    assert.match(stagesSrc, new RegExp(`${key}: ${fn}`), `${key} registered`);
  }
  assert.match(defBlock(HOUSE), /builder: 'capehouse'/);
  assert.match(defBlock(BEACH), /builder: 'capebeach'/);
});

test('beach sky is LOCKED: dark purple lean-colored stops, exact match', () => {
  const sky = "sky: [[0.0, '#0d0716'], [0.45, '#241038'], [0.72, '#3d1c4e'], [0.88, '#4a2444'], [1.0, '#160a1e']]";
  assert.ok(defBlock(BEACH).includes(sky), 'beach sky stops must match the locked spec exactly');
  // Every stop is dark and muted: no channel above 0x4e, green never dominant.
  for (const hex of ['#0d0716', '#241038', '#3d1c4e', '#4a2444', '#160a1e']) {
    const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
    assert.ok(Math.max(r, g, b) <= 0x4e, `${hex} too bright for the locked dirty-purple sky`);
    assert.ok(g <= r && g <= b, `${hex} is not purple-dominant (green must not lead)`);
  }
});

test('beach atmosphere is thick and dim (fog + grade locked, never brightened)', () => {
  const block = defBlock(BEACH);
  assert.match(block, /fog: \['#1c0f2a', 14, 55\]/, 'thick fog: near 14, far 55');
  assert.match(block, /grade: \{ exposure: 1\.1, bloom: 0\.6 \}/, 'dim grade, not brightened');
  assert.match(block, /sun: \['#9a7aaa', 1\.1, \[-8, 9, 4\]\]/, 'dim murky moonlight');
});

test('both arenas use standard WH fight bounds and spawns', () => {
  for (const id of [HOUSE, BEACH]) {
    const block = defBlock(id);
    assert.match(block, /dims: \{ width: 16\.8, depth: 6\.0, wallDistance: 8\.4 \}/, `${id} dims`);
    assert.match(block, /spawns: \{ p1: -3\.5, p2: 3\.5 \}/, `${id} spawns`);
  }
});

test('zero external-asset keys: no obj/glb/pano/map, so no arena-asset 404 is possible in v1', () => {
  for (const id of [HOUSE, BEACH]) {
    const block = defBlock(id);
    for (const key of ['obj:', 'glb:', 'pano:', 'map:']) {
      assert.ok(!block.includes(key), `${id} must not name a ${key} asset in v1`);
    }
  }
});

test('no declared breakables: Lane 5 generic stage-levels treatment applies', () => {
  for (const id of [HOUSE, BEACH]) {
    assert.ok(!defBlock(id).includes('breakables:'), `${id} must declare no breakables`);
  }
});

test('music-pool coordination ids match the music lane contract', () => {
  assert.match(defBlock(HOUSE), /musicStageId: 'cape-jones-arena'/);
  assert.match(defBlock(BEACH), /musicStageId: 'cape-jones-halloween-beach'/);
  assert.match(defBlock(HOUSE), /associatedFighters: \['cyborgx'\]/);
  assert.match(defBlock(BEACH), /associatedFighters: \['cyborgx'\]/);
});

test('Netlify /stages/* proxy exists in BOTH mirrored files (future living-room.glb)', () => {
  assert.match(netlifyToml, /from = "\/stages\/\*"\n\s+to = "https:\/\/mhvnsnt\.github\.io\/western-heart\/stages\/:splat"\n\s+status = 200/);
  assert.match(redirects, /\/stages\/\* +https:\/\/mhvnsnt\.github\.io\/western-heart\/stages\/:splat +200/);
});

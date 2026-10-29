// Node test for game/js/worldgen — no DOM. Run: node --test test/worldgen.test.mjs
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join, resolve } from 'path';
import { createRequire } from 'module';

const here = dirname(fileURLToPath(import.meta.url));
const wg = join(here, '..', 'game', 'js', 'worldgen');
const require = createRequire(import.meta.url);

let pass = 0, fail = 0;
function ok(cond, name) {
  if (cond) { pass++; }
  else { fail++; console.log('FAIL -', name); }
}

const WFC = await import(join(wg, 'wfc.js'));
const TER = await import(join(wg, 'terrain.js'));
const PRP = await import(join(wg, 'props.js'));
const WG = await import(join(wg, 'worldgen.js'));
const RNG = await import(join(wg, 'seeded-rng.js'));

const templeRs = JSON.parse(readFileSync(join(wg, 'rulesets', 'temple-courtyard.json'), 'utf8'));
const forestRs = JSON.parse(readFileSync(join(wg, 'rulesets', 'hmw-forest.json'), 'utf8'));

// ---- 1. seeded RNG determinism ----
{
  const a = RNG.makeRng('hello');
  const b = RNG.makeRng('hello');
  ok(a.next() === b.next() && a.int(1, 100) === b.int(1, 100), 'seeded rng deterministic');
  ok(RNG.normalizeSeed('x') === RNG.normalizeSeed('x'), 'string seed stable');
}

// ---- 2. WFC bundle == pristine CJS sources ----
{
  const bundle = await import(join(wg, 'vendor', 'wfc.bundle.mjs'));
  const pristine = require(join(wg, 'vendor', 'wavefunctioncollapse', 'index.js'));
  ok(typeof bundle.WFC.SimpleTiledModel === 'function', 'bundle exports SimpleTiledModel');
  ok(typeof pristine.SimpleTiledModel === 'function', 'pristine exports SimpleTiledModel');
  // Same tileset, same seeded rng -> identical observed grids.
  const ts = 4;
  const flat = (c) => { const a = []; for (let i = 0; i < ts * ts; i++) a.push(c[0], c[1], c[2], 255); return a; };
  const data = {
    tilesize: ts,
    tiles: [
      { name: 'a', symmetry: 'X', weight: 2, bitmap: flat([10, 20, 30]) },
      { name: 'b', symmetry: 'X', weight: 1, bitmap: flat([200, 10, 10]) },
    ],
    neighbors: [{ left: 'a', right: 'a' }, { left: 'a', right: 'b' }, { left: 'b', right: 'b' }],
  };
  const m1 = new bundle.WFC.SimpleTiledModel(data, null, 12, 12, false);
  const m2 = new pristine.SimpleTiledModel(data, null, 12, 12, false);
  const r1 = RNG.mulberry32(42), r2 = RNG.mulberry32(42);
  const ok1 = m1.generate(r1), ok2 = m2.generate(r2);
  ok(ok1 && ok2, 'bundle and pristine both generate');
  ok(JSON.stringify(Array.from(m1.observed)) === JSON.stringify(Array.from(m2.observed)),
    'bundle output identical to pristine CJS sources');
}

// ---- 3. layout determinism ----
{
  const L1 = WFC.generateLayout(templeRs, { width: 24, height: 18, seed: 777 });
  const L2 = WFC.generateLayout(templeRs, { width: 24, height: 18, seed: 777 });
  ok(L1.success && L2.success, 'temple layout succeeds');
  ok(JSON.stringify(L1.names) === JSON.stringify(L2.names), 'same seed -> identical layout');
  const L3 = WFC.generateLayout(templeRs, { width: 24, height: 18, seed: 778 });
  ok(JSON.stringify(L1.names) !== JSON.stringify(L3.names), 'different seed -> different layout');
}

// ---- 4. ruleset conversion sanity ----
{
  const expanded = WFC._debug.expandTiles(templeRs);
  ok(expanded.length >= templeRs.tiles.length, 'expandTiles produces oriented variants');
  // every oriented variant must have >=1 compatible right-neighbor (else dead tile)
  let dead = 0;
  for (const v of expanded) {
    const has = expanded.some((u) => v.edges[1] === u.edges[3]);
    if (!has) dead++;
  }
  ok(dead === 0, 'no dead oriented variants (' + expanded.length + ' variants checked)');
  const names = new Set(expanded.map((v) => v.name));
  ok(names.size === expanded.length, 'oriented names unique');
}

// ---- 5. profile-size generation succeeds ----
{
  const z1 = WG.generateZone({ kind: 'temple-courtyard', seed: 1337 });
  ok(z1.layout.success, 'temple-courtyard profile succeeds, attempts=' + z1.layout.attempts);
  ok(z1.layout.width === 40 && z1.layout.height === 28, 'temple profile size 40x28');
  const z2 = WG.generateZone({ kind: 'hmw-forest', seed: 2026 });
  ok(z2.layout.success, 'hmw-forest profile succeeds, attempts=' + z2.layout.attempts);
  ok(z2.heightmap.width === 96 && z2.heightmap.height === 96, 'forest terrain 96x96');
  ok(z2.caveMask && z2.caveMask.openFraction > 0 && z2.caveMask.openFraction < 1, 'cave mask sane');
  ok(Array.isArray(z2.props) && z2.props.length > 0, 'props scattered');
}

// ---- 6. terrain determinism + async parity ----
{
  const h1 = TER.sampleHeightmap({ width: 48, height: 48, seed: 5 });
  const h2 = TER.sampleHeightmap({ width: 48, height: 48, seed: 5 });
  ok(h1.data.length === 48 * 48, 'heightmap size');
  let same = true;
  for (let i = 0; i < h1.data.length; i++) if (h1.data[i] !== h2.data[i]) { same = false; break; }
  ok(same, 'heightmap deterministic');
  ok(h1.min < h1.max && h1.min >= -20 && h1.max <= 20, 'heightmap range sane');
  const ha = await TER.sampleHeightmapAsync({ width: 48, height: 48, seed: 5 });
  let sameA = ha.data.length === h1.data.length;
  for (let i = 0; i < h1.data.length && sameA; i++) if (ha.data[i] !== h1.data[i]) sameA = false;
  ok(sameA, 'async heightmap == sync heightmap');
  const bio = TER.classifyBiomes(h1);
  ok(bio.length === h1.data.length && bio instanceof Uint8Array, 'biome classification');
  const cm1 = TER.sampleCaveMask({ width: 32, height: 32, seed: 9 });
  const cm2 = TER.sampleCaveMask({ width: 32, height: 32, seed: 9 });
  ok(cm1.openFraction === cm2.openFraction, 'cave mask deterministic');
}

// ---- 7. props determinism ----
{
  const z = WG.generateZone({ kind: 'temple-courtyard', seed: 1337 });
  const p1 = PRP.scatterProps({ seed: 1, layout: z.layout, defs: PRP.PROP_SETS['temple-courtyard'] });
  const p2 = PRP.scatterProps({ seed: 1, layout: z.layout, defs: PRP.PROP_SETS['temple-courtyard'] });
  ok(JSON.stringify(p1) === JSON.stringify(p2), 'props deterministic');
  ok(p1.every((p) => p.x >= 0 && p.y >= 0), 'props in bounds');
}

// ---- 8. zone meta ----
{
  const z = WG.generateZone({ kind: 'temple-courtyard', seed: 1337 });
  ok(typeof z.meta.generatedMs === 'number' && z.meta.generatedMs > 0, 'meta.generatedMs');
  ok(z.meta.layoutSuccess === true, 'meta.layoutSuccess');
  ok(z.seed === 1337 && z.kind === 'temple-courtyard', 'zone kind/seed echo');
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);

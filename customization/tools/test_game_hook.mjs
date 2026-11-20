/* test_game_hook.mjs — Node smoke test for the Creation Suite game hook.
 *
 * Verifies, without a browser:
 *   1. game/js/assets.js loads as ESM (bare 'three' specifiers are rewritten
 *      to the vendored copies under game/vendor/ in a temp sandbox).
 *   2. MODEL_URLS is populated (roster loads).
 *   3. With the real generated registry (game/js/attire-customizations.js),
 *      every override value resolves to a real file relative to game/.
 *   4. With a synthetic registry entry, the override actually replaces the
 *      base MODEL_URLS entry (the Creation Suite Pass behaviour), and with an
 *      empty registry MODEL_URLS is untouched (exact no-op).
 *
 * Usage: node customization/tools/test_game_hook.mjs [repo-root]
 * Exit 0 = PASS, 1 = FAIL (reason on stderr).
 */
import { mkdtempSync, cpSync, writeFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const repo = resolve(process.argv[2] || '.');
const gameDir = join(repo, 'game');
const fail = (m) => { console.error('SMOKE FAIL:', m); process.exit(1); };

if (!existsSync(join(gameDir, 'js', 'assets.js'))) fail('game/js/assets.js not found under ' + repo);
if (!existsSync(join(gameDir, 'js', 'attire-customizations.js'))) fail('game/js/attire-customizations.js not found (run the bake emit)');

import { mkdirSync } from 'node:fs';
// Fresh sandbox per scenario: Node caches ES modules by URL, so a rewritten
// registry only takes effect in a fresh copy.
function makeSandbox(registrySource) {
  const sandbox = mkdtempSync(join(tmpdir(), 'cs-hook-'));
  cpSync(join(gameDir, 'js'), join(sandbox, 'js'), { recursive: true });
  if (registrySource != null)
    writeFileSync(join(sandbox, 'js', 'attire-customizations.js'), registrySource);
  // Expose the vendored three as a real node_modules package so assets.js is
  // imported byte-for-byte as the browser importmap would resolve it.
  mkdirSync(join(sandbox, 'node_modules', 'three'), { recursive: true });
  cpSync(join(gameDir, 'vendor', 'three.module.js'), join(sandbox, 'node_modules', 'three', 'three.module.js'));
  cpSync(join(gameDir, 'vendor', 'addons'), join(sandbox, 'node_modules', 'three', 'addons'), { recursive: true });
  writeFileSync(join(sandbox, 'node_modules', 'three', 'package.json'), JSON.stringify({
    name: 'three', version: '0.0.0-vendored', type: 'module',
    main: 'three.module.js',
    exports: { '.': './three.module.js', './addons/*': './addons/*' },
  }));
  writeFileSync(join(sandbox, 'package.json'), JSON.stringify({ type: 'module' }));
  return sandbox;
}
const sandbox = makeSandbox(null);
const assetsPath = join(sandbox, 'js', 'assets.js');

async function load(tag, registrySource) {
  if (registrySource === undefined) return import(pathToFileURL(assetsPath).href);
  const sb = makeSandbox(registrySource);
  return import(pathToFileURL(join(sb, 'js', 'assets.js')).href);
}

// Pristine baseline: assets.js with an EMPTY registry. Phase 4b must compare
// against this — comparing against the real-registry load would demand that
// an empty registry reproduce the override, which fails by construction as
// soon as any real override exists.
const pristine = await load('pristine', 'export const ATTIRE_CUSTOMIZATIONS = {};\n');

// 1+2: loads with the real registry; MODEL_URLS populated.
const real = await load('real');
if (!real.MODEL_URLS || typeof real.MODEL_URLS !== 'object') fail('MODEL_URLS not exported by assets.js');
const keys = Object.keys(real.MODEL_URLS);
if (keys.length < 50) fail(`MODEL_URLS suspiciously small: ${keys.length} keys`);
if (!real.MODEL_URLS['baek-master-white']) fail("MODEL_URLS missing 'baek-master-white'");
console.log(`SMOKE roster: ${keys.length} MODEL_URLS keys`);

// 3: every real registry override resolves to a real file.
const { ATTIRE_CUSTOMIZATIONS } = await import(pathToFileURL(join(sandbox, 'js', 'attire-customizations.js')).href);
for (const [k, v] of Object.entries(ATTIRE_CUSTOMIZATIONS)) {
  const p = join(gameDir, v);
  if (!existsSync(p)) fail(`registry override ${k} -> ${v} does not resolve to a file (${p})`);
  if (real.MODEL_URLS[k] !== v) fail(`override for ${k} not applied in MODEL_URLS`);
}
console.log(`SMOKE registry: ${Object.keys(ATTIRE_CUSTOMIZATIONS).length} override(s), all resolve + applied`);

// 4a: synthetic override replaces the base entry.
const base = pristine.MODEL_URLS['baek-master-white'];
const over = await load('override',
  "export const ATTIRE_CUSTOMIZATIONS = { 'baek-master-white': '../roster/baek/attires/master-white/model-custom.glb' };\n");
if (over.MODEL_URLS['baek-master-white'] !== '../roster/baek/attires/master-white/model-custom.glb')
  fail('synthetic override did not replace MODEL_URLS entry');
if (!existsSync(join(gameDir, over.MODEL_URLS['baek-master-white'])))
  fail('override target file missing: ' + over.MODEL_URLS['baek-master-white']);
console.log(`SMOKE override: baek-master-white ${base} -> ${over.MODEL_URLS['baek-master-white']} (file exists)`);

// 4b: empty registry = exact no-op.
const noop = await load('noop', 'export const ATTIRE_CUSTOMIZATIONS = {};\n');
if (noop.MODEL_URLS['baek-master-white'] !== base) fail('empty registry was not a no-op');
console.log('SMOKE no-op: empty registry leaves MODEL_URLS untouched');
console.log('SMOKE PASS');

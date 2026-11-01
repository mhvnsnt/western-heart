// Every library the game imports by name resolves through game/index.html's importmap (2026-11-01). Node, no browser.
// Run: node --test test/importmap-integrations.test.mjs
// Why: cannon-es, three-mesh-bvh, three-nebula, troika-three-text and camera-controls were vendored under game/vendor/
// and wired by game/js/integration.js, but the importmap mapped only "three", so every `import('cannon-es')` failed and
// physics, BVH hit detection, nebula hit FX, 3D labels and the camera director were silently off in every build
// (WHIntegration.failed). With the map: 15/15 systems ready, 0 failed (docs/proof/2026-11-01/importmap/).
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const GAME = join(ROOT, 'game');

function importmap() {
  const html = readFileSync(join(GAME, 'index.html'), 'utf8');
  const m = html.match(/<script type="importmap">([\s\S]*?)<\/script>/);
  assert.ok(m, 'index.html has an importmap');
  return JSON.parse(m[1]).imports;
}

function walk(dir, out = []) {
  for (const n of readdirSync(dir)) {
    const p = join(dir, n);
    if (statSync(p).isDirectory()) { if (n !== 'vendor') walk(p, out); } else if (/\.m?js$/.test(n)) out.push(p);
  }
  return out;
}

// bare specifiers in real import statements (comment lines skipped); node:* only runs in Node tool paths
function bareImports(file) {
  const out = [];
  for (const line of readFileSync(file, 'utf8').split('\n')) {
    const t = line.trim();
    if (t.startsWith('//') || t.startsWith('*') || t.startsWith('/*')) continue;
    for (const re of [/import\(\s*['"]([^'"./][^'"]*)['"]\s*\)/g, /(?:^|\s)(?:import|export)\b[^'"]*\bfrom\s+['"]([^'"./][^'"]*)['"]/g,
      /^import\s+['"]([^'"./][^'"]*)['"]/g]) {
      for (const m of t.matchAll(re)) if (!m[1].startsWith('node:')) out.push(m[1]);
    }
  }
  return out;
}

test('every bare import in game/js resolves through the importmap to a file that exists', () => {
  const map = importmap();
  const resolve = (spec) => {
    if (map[spec]) return map[spec];
    const pre = Object.keys(map).filter((k) => k.endsWith('/') && spec.startsWith(k)).sort((a, b) => b.length - a.length)[0];
    return pre ? map[pre] + spec.slice(pre.length) : null;
  };
  const missing = [];
  for (const f of walk(join(GAME, 'js'))) {
    for (const spec of bareImports(f)) {
      const target = resolve(spec);
      if (!target) missing.push(`${f.slice(ROOT.length + 1)}: '${spec}' has no importmap entry`);
      else if (!existsSync(join(GAME, target))) missing.push(`${f.slice(ROOT.length + 1)}: '${spec}' -> ${target} does not exist`);
    }
  }
  assert.deepEqual(missing, []);
});

test('the integration systems\' libraries are mapped to their vendored builds', () => {
  const map = importmap();
  for (const [spec, file] of [['cannon-es', './vendor/cannon-es/cannon-es.js'], ['three-mesh-bvh', './vendor/three-mesh-bvh/index.module.js'],
    ['three-nebula', './vendor/three-nebula/three-nebula.mjs'], ['troika-three-text', './vendor/troika-three-text/troika-three-text.esm.js'],
    ['camera-controls', './vendor/camera-controls/camera-controls.module.js']]) {
    assert.equal(map[spec], file, spec);
    assert.ok(existsSync(join(GAME, file)), file);
  }
  // troika-three-text's own imports
  for (const dep of ['troika-three-utils', 'troika-worker-utils', 'webgl-sdf-generator', 'bidi-js']) assert.ok(map[dep], dep);
});

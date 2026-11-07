// A model response must be a model (2026-11-07). The live Cloudflare build served index.html (HTTP 200) for Demonio's
// 28.8 MB model; the loader cached the HTML and its parse failed the whole fight load. looksLikeModel() gates every
// cache write and parse in assets.js. Run: node --test test/model-response-guard.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const { looksLikeModel } = await import(join(ROOT, 'game/js/asset-config.js'));
const bytes = (s) => new TextEncoder().encode(s).buffer;

test('a GLB (magic glTF) and a .gltf (JSON) are models', () => {
  const glb = new Uint8Array([0x67, 0x6C, 0x54, 0x46, 2, 0, 0, 0, 20, 0, 0, 0]).buffer;
  assert.equal(looksLikeModel(glb), true);
  assert.equal(looksLikeModel(bytes('{"asset":{"version":"2.0"}}')), true);
  assert.equal(looksLikeModel(bytes('\n  {"asset":{}}')), true, 'leading whitespace');
  assert.equal(looksLikeModel(new Uint8Array([0xEF, 0xBB, 0xBF, 0x7B, 0x7D]).buffer), true, 'UTF-8 BOM');
});

test('an HTML page, an error body or nothing is not a model', () => {
  assert.equal(looksLikeModel(bytes('<!doctype html><html><head>')), false);
  assert.equal(looksLikeModel(bytes('Package size exceeded the configured limit of 50 MB.')), false);
  assert.equal(looksLikeModel(bytes('abc')), false);
  assert.equal(looksLikeModel(null), false);
  assert.equal(looksLikeModel(new ArrayBuffer(0)), false);
});

test('the model loader checks the bytes before caching or parsing, and a parse failure tries the next candidate', () => {
  const src = readFileSync(join(ROOT, 'game/js/assets.js'), 'utf8');
  assert.match(src, /if \(cached && !signal\.aborted && looksLikeModel\(cached\)\)/, 'cached HTML is skipped');
  const net = src.slice(src.indexOf('if (!looksLikeModel(buf)) {'));
  assert.ok(net.indexOf('if (!looksLikeModel(buf)) {') === 0, 'network bytes are checked');
  assert.ok(net.indexOf('putCachedBuffer(cand, buf)') > 0, 'the check comes before the cache write');
  assert.match(net.slice(0, 1600), /try \{\s*return await _sharedGLTFLoader\(\)\.parseAsync\(buf, cand\);\s*\} catch \(e\) \{[\s\S]{0,200}continue;/);
});

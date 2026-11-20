/* asset-cache.test.mjs — load-times lane (2026-11-01).
 * WHAT THIS GUARDS: game/js/asset-cache.js must (a) treat the remote
 * asset base's cross-origin model URLs as cacheable (they were refused,
 * so every non-bundled fighter re-downloaded 20-92 MB on EVERY session),
 * (b) keep refusing blob:/data:/etc. URLs, (c) bound every entry with
 * the 48 h freshness stamp (model files are replaced in place at the
 * same URL when a rig is re-done, so an unbounded cache would serve a
 * replaced model stale forever), and (d) roundtrip bytes through a
 * Cache API store under a cross-origin key.
 * Run: node --test game/tests/asset-cache.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {
  isCacheableUrl, isFreshCacheStamp, ASSET_CACHE_MAX_AGE_MS,
  getCachedBuffer, putCachedBuffer,
} from '../js/asset-cache.js';

test('remote-base (cross-origin) model URLs are cacheable', () => {
  assert.equal(isCacheableUrl('https://western-heart-assets.mhvnsnt.workers.dev/roster/purplerain/attires/attire1/model-rerig.glb'), true);
  assert.equal(isCacheableUrl('https://cdn.jsdelivr.net/gh/mhvnsnt/western-heart@main/roster/x/model.glb'), true);
  assert.equal(isCacheableUrl('https://mhvnsnt.github.io/western-heart/roster/x/model.glb'), true);
});

test('relative URLs stay cacheable; dangerous schemes stay refused', () => {
  assert.equal(isCacheableUrl('assets/models/pantera.glb'), true);
  assert.equal(isCacheableUrl('../roster/demonio/attires/attire1/model.glb'), true);
  assert.equal(isCacheableUrl('blob:https://example.com/abc'), false);
  assert.equal(isCacheableUrl('data:model/gltf-binary;base64,AAAA'), false);
  assert.equal(isCacheableUrl('javascript:alert(1)'), false);
  assert.equal(isCacheableUrl(''), false);
  assert.equal(isCacheableUrl(null), false);
  assert.equal(isCacheableUrl(undefined), false);
});

test('freshness stamp: fresh inside 48 h, stale after, garbage is stale', () => {
  const now = 1_700_000_000_000;
  assert.equal(isFreshCacheStamp(now, now), true);
  assert.equal(isFreshCacheStamp(now - ASSET_CACHE_MAX_AGE_MS + 1, now), true);
  assert.equal(isFreshCacheStamp(now - ASSET_CACHE_MAX_AGE_MS - 1, now), false);
  assert.equal(isFreshCacheStamp(0, now), false);
  assert.equal(isFreshCacheStamp(NaN, now), false);
  assert.equal(isFreshCacheStamp(now + 60 * 60 * 1000, now), false); // >5 min future skew
  assert.equal(isFreshCacheStamp(now + 60 * 1000, now), true); // small clock skew tolerated
});

/* In-memory Cache API stand-in: match() returns a FRESH Response each
 * call (a real Response body can only be consumed once). */
function installFakeCaches() {
  const store = new Map();
  const cache = {
    async match(url) {
      const e = store.get(url);
      if (!e) return undefined;
      return new Response(e.bytes.slice(0), { headers: e.headers });
    },
    async put(url, res) {
      const bytes = new Uint8Array(await res.arrayBuffer());
      const headers = {};
      res.headers.forEach((v, k) => { headers[k] = v; });
      store.set(url, { bytes, headers });
    },
    async delete(url) { return store.delete(url); },
  };
  globalThis.caches = { open: async () => cache };
  return store;
}

test('cross-origin put/get roundtrip returns the exact bytes', async () => {
  const store = installFakeCaches();
  try {
    const url = 'https://western-heart-assets.mhvnsnt.workers.dev/roster/x/model.glb';
    const bytes = new Uint8Array([1, 2, 3, 4, 5, 250, 0, 99]);
    await putCachedBuffer(url, bytes.buffer);
    assert.equal(store.has(url), true);
    const got = await getCachedBuffer(url);
    assert.ok(got);
    assert.deepEqual([...new Uint8Array(got)], [...bytes]);
  } finally { delete globalThis.caches; }
});

test('a stale entry is a miss and gets evicted', async () => {
  const store = installFakeCaches();
  try {
    const url = 'https://western-heart-assets.mhvnsnt.workers.dev/roster/y/model.glb';
    store.set(url, {
      bytes: new Uint8Array([9, 9, 9]),
      headers: { 'content-type': 'application/octet-stream', 'x-wh-cached-at': String(Date.now() - ASSET_CACHE_MAX_AGE_MS - 1000) },
    });
    const got = await getCachedBuffer(url);
    assert.equal(got, null);
    assert.equal(store.has(url), false);
  } finally { delete globalThis.caches; }
});

test('a pre-stamp legacy entry (no header) is treated as stale', async () => {
  const store = installFakeCaches();
  try {
    const url = 'assets/models/pantera.glb';
    store.set(url, { bytes: new Uint8Array([7]), headers: { 'content-type': 'application/octet-stream' } });
    assert.equal(await getCachedBuffer(url), null);
    assert.equal(store.has(url), false);
  } finally { delete globalThis.caches; }
});

test('without a Cache API the module is a silent no-op', async () => {
  delete globalThis.caches;
  assert.equal(await getCachedBuffer('assets/models/pantera.glb'), null);
  await putCachedBuffer('assets/models/pantera.glb', new Uint8Array([1]).buffer); // must not throw
});

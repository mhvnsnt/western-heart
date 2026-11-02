/* ============================================================
   WESTERN HEART — persistent asset cache (Lane 5: loading)
   Thin Cache API wrapper for model / stage bytes. First visit
   downloads over the network as before; later visits read from
   the Cache API instead of re-downloading multi-MB GLBs, so a
   warmed fight stays warm across sessions.

   LOADSPEED (2026-11-01): cross-origin REMOTE model URLs are
   cacheable now too. The old same-origin-only rule assumed the
   Cache API would store remote responses "opaque and unusable";
   that hazard belongs to cache.add() of a no-cors fetch, which
   this module never does — putCachedBuffer only ever stores a
   buffer the game already downloaded (through the normal CORS
   fetch in assets.js; the asset Worker sends
   Access-Control-Allow-Origin: *), wrapped in a synthetic
   Response. A synthetic response has no origin taint, and the
   cache key is just the URL string, so a model fetched from the
   remote base persists exactly like a same-origin one. Before
   this change every non-bundled fighter (most of the roster,
   20-92 MB each) re-downloaded on EVERY session, and stage GLBs
   warmed by preloadStage were thrown away and fetched again by
   the arena builder.

   Safety rules (all failures are silent no-ops, never a load
   failure): blob: / data: / javascript: / about: URLs are never
   cached; entries are capped at 100 MB (a single fighter GLB is
   tens of MB at most); entries older than ASSET_CACHE_MAX_AGE_MS
   are treated as misses and deleted — model files are replaced
   in place at the SAME URL when a rig is re-done, so an
   unbounded cache would serve a replaced model stale forever;
   every call is guarded so environments without `caches`
   (Node tests, old browsers) behave exactly like no cache.
   Nothing here changes WHAT loads — assets.js / stages.js still
   own the fetch, parse and fallback paths; this only answers
   "do we already have these bytes?".
   ============================================================ */

export const ASSET_CACHE_NAME = 'wh-assets-v1';
export const ASSET_CACHE_MAX_BYTES = 100 * 1024 * 1024;
/* Freshness bound for every entry (see header): 48 h of
   network-free repeat sessions, and a replaced model reaches a
   returning player within two days at the worst. */
export const ASSET_CACHE_MAX_AGE_MS = 48 * 60 * 60 * 1000;
const STAMP_HEADER = 'x-wh-cached-at';

export function isCacheableUrl(url) {
  if (typeof url !== 'string' || !url) return false;
  if (/^(blob|data|javascript|about):/i.test(url)) return false;
  if (/^https?:\/\//i.test(url)) return true; // same-origin OR remote base: buffer puts are origin-free
  return !/^[a-z][a-z0-9+.-]*:/i.test(url); // relative path: cacheable
}

/* Pure freshness check (unit-tested): a stamp is fresh only when
   it exists, is not in the future (clock skew beyond 5 min is
   rejected), and is no older than ASSET_CACHE_MAX_AGE_MS.
   Entries stored before stamps existed have no header -> NaN ->
   stale, so they refresh once instead of living forever. */
export function isFreshCacheStamp(stampMs, nowMs) {
  if (!Number.isFinite(stampMs) || stampMs <= 0) return false;
  if (stampMs > nowMs + 5 * 60 * 1000) return false;
  return nowMs - stampMs <= ASSET_CACHE_MAX_AGE_MS;
}

async function _open() {
  if (typeof caches === 'undefined') return null;
  try { return await caches.open(ASSET_CACHE_NAME); } catch { return null; }
}

/* Stored bytes for a URL, or null on any miss / stale / error. */
export async function getCachedBuffer(url) {
  if (!isCacheableUrl(url)) return null;
  const cache = await _open();
  if (!cache) return null;
  try {
    const res = await cache.match(url);
    if (!res) return null;
    if (!isFreshCacheStamp(Number(res.headers.get(STAMP_HEADER)), Date.now())) {
      try { await cache.delete(url); } catch { /* already gone: fine */ }
      return null;
    }
    const buf = await res.arrayBuffer();
    return buf.byteLength ? buf : null;
  } catch { return null; }
}

/* Store bytes for a URL. Fire-and-forget safe: never throws. */
export async function putCachedBuffer(url, buffer) {
  if (!isCacheableUrl(url)) return;
  if (!buffer || buffer.byteLength === 0 || buffer.byteLength > ASSET_CACHE_MAX_BYTES) return;
  const cache = await _open();
  if (!cache) return;
  try {
    await cache.put(url, new Response(buffer.slice(0), {
      headers: { 'Content-Type': 'application/octet-stream', [STAMP_HEADER]: String(Date.now()) },
    }));
  } catch { /* quota / private mode: network path still works */ }
}

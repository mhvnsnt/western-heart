/* ============================================================
   WESTERN HEART — persistent asset cache (Lane 5: loading)
   Thin Cache API wrapper for model / stage bytes. First visit
   downloads over the network as before; later visits read from
   the Cache API instead of re-downloading multi-MB GLBs, so a
   warmed fight stays warm across sessions.

   Safety rules (all failures are silent no-ops, never a load
   failure): only same-origin or relative http(s) URLs are cached
   (blob: / data: / cross-origin URLs are skipped — the Cache API
   would store them opaque and unusable for parse); entries are
   capped at 100 MB (a single fighter GLB is tens of MB at most);
   every call is guarded so environments without `caches`
   (Node tests, old browsers) behave exactly like no cache.
   Nothing here changes WHAT loads — assets.js / stages.js still
   own the fetch, parse and fallback paths; this only answers
   "do we already have these bytes?".
   ============================================================ */

export const ASSET_CACHE_NAME = 'wh-assets-v1';
export const ASSET_CACHE_MAX_BYTES = 100 * 1024 * 1024;

export function isCacheableUrl(url) {
  if (typeof url !== 'string' || !url) return false;
  if (/^(blob|data|javascript|about):/i.test(url)) return false;
  if (/^https?:\/\//i.test(url)) {
    try {
      if (typeof location !== 'undefined' && location.origin) {
        return new URL(url).origin === location.origin;
      }
    } catch { return false; }
    return false; // absolute URL with no location to compare: skip
  }
  return !/^[a-z][a-z0-9+.-]*:/i.test(url); // relative path: cacheable
}

async function _open() {
  if (typeof caches === 'undefined') return null;
  try { return await caches.open(ASSET_CACHE_NAME); } catch { return null; }
}

/* Stored bytes for a URL, or null on any miss / error. */
export async function getCachedBuffer(url) {
  if (!isCacheableUrl(url)) return null;
  const cache = await _open();
  if (!cache) return null;
  try {
    const res = await cache.match(url);
    if (!res) return null;
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
      headers: { 'Content-Type': 'application/octet-stream' },
    }));
  } catch { /* quota / private mode: network path still works */ }
}

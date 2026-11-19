/* WESTERN HEART service worker: persistent model/texture cache
   (docs/tech/ASSET-PIPELINE-2026.md §4).
   GitHub Pages sends max-age=600 and we can't change headers, so after
   10 minutes every revisit re-downloads megabytes of models. This
   worker keeps binary assets (glb/ktx2/bin/images/audio/wasm) in Cache
   Storage with stale-while-revalidate: a repeat load is served from disk
   at once and refreshed in the background. HTML/JS/JSON are NOT touched
   (always network), so code deploys are never stuck behind a stale cache. */
const CACHE = 'wh-assets-v1';
const BIN = /\.(glb|gltf|bin|ktx2|png|jpe?g|webp|wasm|mp3|ogg|wav|m4a)$/i;

self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (k.startsWith('wh-assets-') && k !== CACHE) await caches.delete(k);
    await self.clients.claim();
  })());
});

// The page posts the live deploy commit; a new deploy empties the cache so
// a changed model is never served stale against new code.
self.addEventListener('message', (e) => {
  const d = e.data || {};
  if (d.type !== 'wh-deploy' || !d.commit) return;
  e.waitUntil((async () => {
    const meta = await caches.open('wh-meta');
    const prev = await meta.match('deploy');
    const was = prev ? await prev.text() : '';
    if (was !== d.commit) {
      await caches.delete(CACHE);
      await meta.put('deploy', new Response(d.commit));
    }
  })());
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET' || req.headers.has('range')) return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin || !BIN.test(url.pathname) || url.search.includes('raw')) return;
  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const hit = await cache.match(req);
    const net = fetch(req).then((res) => {
      if (res.ok && res.status === 200) cache.put(req, res.clone()).catch(() => {});
      return res;
    });
    if (hit) { e.waitUntil(net.catch(() => {})); return hit; }
    return net;
  })());
});

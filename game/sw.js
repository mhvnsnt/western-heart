/* Western Heart PWA shell worker.
   Modeled on OpenKumite v0.1.2 web/sw.js ideas (MIT): cache the HTML/CSS/JS
   shell for offline boot; do NOT cache game/assets anim packs or large GLBs
   here — those stay network/OPFS. Android APK packaging comes later, modeled
   on OpenKumite packaging/android (NativeActivity / cargo-ndk pattern) once
   the PWA shell is proven. */
const CACHE = 'western-heart-shell-v1';
const SHELL = [
  './',
  './index.html',
  './manifest.webmanifest',
  './styles.css',
  './menus.css',
  './mainmenu.css',
];

self.addEventListener('install', (e) => {
  e.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    await Promise.all(SHELL.map(async (path) => {
      try {
        const r = await fetch(path, { cache: 'no-store' });
        if (r.ok) await cache.put(path, r);
      } catch (_) { /* optional shell piece */ }
    }));
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  // Never intercept large asset / anim / model traffic.
  if (/\/assets\//.test(url.pathname) || /\.(glb|pack\.json|bin|wasm|mp3|ogg|wav)(\?|$)/i.test(url.pathname)) return;
  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    try {
      const net = await fetch(req);
      if (net.ok && net.type === 'basic' && !/\/assets\//.test(url.pathname)) {
        const shellHit = SHELL.some((p) => url.pathname.endsWith(p.replace(/^\.\//, '')) || url.pathname.endsWith('/game/') || url.pathname.endsWith('/game/index.html'));
        if (shellHit) await cache.put(req, net.clone());
      }
      return net;
    } catch (_) {
      const hit = await cache.match(req);
      if (hit) return hit;
      const fallback = await cache.match('./index.html');
      if (fallback) return fallback;
      throw _;
    }
  })());
});

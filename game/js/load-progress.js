/* ============================================================
   WESTERN HEART — real loading progress (owner pt134u, 2026-10-23:
   "the loading bar doesn't even visibly move ... you can't tell it's loading").
   Before: menus.showLoading() set the bar to 8% and nothing ever advanced it
   (setLoadingProgress had zero callers). Now:
   - every GLTFLoader / TextureLoader uses THREE.DefaultLoadingManager, so its
     loaded/total item counts are the real asset progress;
   - a slow creep fills the gap inside one large file, capped just above the
     last real milestone, so the bar never looks frozen and never lies past it;
   - shows percent + the asset file currently loading.
   Watches #wh-loading's .show class, so no menu file is edited.
   ============================================================ */
import * as THREE from 'three';

let real = 0, shown = 0, asset = '', creep = null, active = false, preloadNote = '';
const t = { start: 0 };

function paint() {
  const o = document.getElementById('wh-loading');
  if (!o) return;
  const f = o.querySelector('.wh-load-fill');
  if (f) f.style.width = `${Math.round(Math.max(0.03, Math.min(1, shown)) * 100)}%`;
  let pct = o.querySelector('.wh-load-pct');
  if (!pct && f && f.parentElement) {
    pct = document.createElement('div');
    pct.className = 'wh-load-pct';
    pct.style.cssText = 'margin-top:8px;font:700 13px/1.3 monospace;color:#ffe9a8;text-align:center;word-break:break-all;';
    f.parentElement.insertAdjacentElement('afterend', pct);
  }
  if (pct) pct.textContent = `${Math.round(shown * 100)}%${asset ? ' · ' + asset : ''}${(o.classList.contains('show') && preloadNote) ? ' · ' + preloadNote : ''}`;
}

const M = THREE.DefaultLoadingManager;
const prev = M.onProgress;
M.onProgress = function (url, loaded, total) {
  if (prev) prev.apply(this, arguments);
  // Item counts jump (total grows as files are discovered), so they only
  // name the asset here; the bar itself is driven by real model bytes below.
  const u = String(url || '');
  if (active && !u.startsWith('blob:') && !u.startsWith('data:')) { asset = u.split('/').pop().split('?')[0].slice(0, 48); paint(); }
};

/* Byte-level model progress from assets.loadModels (main.js startFight).
   Models are the bulk of a match load, so they map to 0..90%. */
/* Rematch-preload status (2026-10-24): lazy.preloadNextFight reports the
   ids it warmed so the next loading overlay can show them. Cleared when a
   real load begins (begin() below) — the note describes the VS/outro
   window, never the load itself. */
window.__whPreloadNote = function (ids) {
  preloadNote = (ids && ids.length) ? `preloading rematch: ${ids.join(', ')}` : '';
  paint();
};

window.__whLoadProgress = function (p, loaded, total) {
  if (!active) return;
  const frac = (loaded && total) ? loaded / total : (p || 0);
  real = Math.max(real, Math.min(0.85, 0.05 + frac * 0.8)); shown = Math.max(shown, real);
  if (loaded && total) asset = `fighters ${(loaded / 1048576).toFixed(1)}/${(total / 1048576).toFixed(1)} MB`;
  paint();
};

function begin() {
  active = true; real = 0; shown = 0.03; asset = ''; preloadNote = ''; t.start = performance.now();
  clearInterval(creep);
  creep = setInterval(() => {
    const cap = Math.min(0.97, real + (real >= 0.85 ? 0.12 : 0.06));
    if (shown < cap) { shown += (cap - shown) * 0.05; paint(); }
  }, 100);
  paint();
}
function end() {
  if (!active) return;
  active = false; clearInterval(creep); shown = 1; paint();
  window.__whLastLoadMs = Math.round(performance.now() - t.start);
  console.info(`[WH-load] match load ${window.__whLastLoadMs} ms`);
}

function watch() {
  const o = document.getElementById('wh-loading');
  if (!o) { setTimeout(watch, 250); return; } // built later by menus.initMenus
  new MutationObserver(() => { o.classList.contains('show') ? (active || begin()) : end(); })
    .observe(o, { attributes: true, attributeFilter: ['class'] });
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', watch); else watch();

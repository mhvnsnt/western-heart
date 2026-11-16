/* ============================================================
   WESTERN HEART — lazy: deferred module loading (loadspeed lane)
   TEKKEN 3 LESSON (teardown/tekken3/docs/TEKKEN3-ARCHITECTURE.md):
   "the BNS table is an index — the game loads specific records on
   demand." The boot bundle used to statically import every system
   (fighter rigs, T3 anim banks, movesets, mode controllers) before
   first paint. Now the menu shell boots on a minimal graph and
   these modules load on demand — warmed during idle so the first
   real use rarely waits.

   Each importer is cached: the module evaluates once, however many
   call sites await it. Import specifiers are static strings
   relative to THIS module, so native ESM resolves them exactly
   like the static imports they replace.
   ============================================================ */
const _cache = {};
function _cached(name, path) {
  return () => {
    // A FAILED import is not cached here (2026-11-01): the idle warm-up's rejected promise used to stay in _cache for
    // the life of the page, so one dropped request at boot failed every later fight until a manual reload. A retry now
    // imports again; where the browser's own module map also kept the failure, main.js reloadIntoFight takes over.
    if (!_cache[name]) _cache[name] = import(path).catch((e) => { delete _cache[name]; throw e; });
    return _cache[name];
  };
}

export const lazy = {
  /** fighter.js — bankIdFor/loadRealMovesets (fight + select preview) */
  fighter: _cached('fighter', './fighter.js'),
  /** movesets.js — index + per-fight moveset JSON (fight + movelist) */
  movesets: _cached('movesets', './movesets.js'),
  /** t3anims.js — decoded T3 animation banks (fight + select preview) */
  t3anims: _cached('t3anims', './t3anims.js'),
  /** modes.js — ModeController + records (first mode tap) */
  modes: _cached('modes', './modes.js'),
  /** heartmind.js — The Heart and Mind Inside (its mode tap) */
  heartmind: _cached('heartmind', './heartmind.js'),
  /** episodes.js — Character Episodes (its mode tap) */
  episodes: _cached('episodes', './episodes.js'),
  /** ranks.js — rank ladder, rank battle, rank hall (worker 30) */
  ranks: _cached('ranks', './ranks.js'),
};

/* Drop a cached lazy import (2026-11-15, modes-import-timeout): a HUNG
   import stays in _cache forever — the rejection path in _cached only
   runs when the promise settles, and a hang never settles, so every
   later call would share the same hung promise (observed live
   2026-11-15: the first mode tap's modes.js import hung, __modes
   never became true, and re-clicks never helped). Dropping the entry
   makes the next call import again. NOTE: the browser's own module
   map dedupes fetches by URL, so a re-import while the first fetch is
   still in flight awaits the same fetch — the drop guarantees a FRESH
   PROMISE and a FRESH TIMEOUT, not a second network fetch. The
   un-wedge is the timeout bounding every wait, not the re-fetch. */
export function dropLazy(name) {
  delete _cache[name];
}

/* Race a promise against a timeout: the timeout rejects, the timer is
   cleared whichever side settles first. A hung inner promise stays
   pending (one dangling promise per timed-out attempt); the underlying
   import may still resolve later into the browser's module map, which
   is fine — the next attempt then resolves at once. */
function raceWithTimeout(promise, ms, label) {
  let timer = null;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error(`[WH] ${label} timed out after ${ms}ms`)), ms);
  });
  return Promise.race([promise, timeout]).finally(() => { if (timer !== null) clearTimeout(timer); });
}

/* Run loader() with a timeout, retrying once (default) on timeout OR
   rejection, then throw the last error. Each attempt calls loader()
   fresh — callers that need a fresh import between attempts do the
   cache drop inside loader(). A rejection settles the race at once, so
   a fast failure (404, syntax error) does not burn the whole timeout. */
export async function loadWithRetry(loader, { timeoutMs, retryDelayMs = 0, retries = 1, label = 'load' } = {}) {
  let lastErr;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      return await raceWithTimeout(loader(), timeoutMs, label);
    } catch (e) {
      lastErr = e;
      if (attempt < retries && retryDelayMs > 0) {
        await new Promise((resolve) => setTimeout(resolve, retryDelayMs));
      }
    }
  }
  throw lastErr;
}

/* Warm the modules the select screen and first fight need, but only
   when the browser is idle — never at the expense of first paint.
   Called once at the end of boot (main.js). */
export function warmIdle() {
  const ric = (typeof window !== 'undefined' && window.requestIdleCallback)
    ? window.requestIdleCallback.bind(window)
    : (fn) => setTimeout(fn, 1500);
  ric(() => {
    lazy.fighter().catch(() => {});
    lazy.t3anims().catch(() => {});
    lazy.modes().catch(() => {});
    // The moveset index (fighters -> anim bank) backs the select
    // screen's stance preview; load it as soon as the module lands.
    lazy.movesets()
      .then((m) => m.loadFighterMovesets().catch(() => {}))
      .catch(() => {});
  });
}

/* ---------------- Next-fight preload (2026-10-24, streaming lane) ----
   While the VS screen breathes and again at the fight outro (wired in
   menus.js hookStartMatch), warm the rematch pair through assets.prefetch
   — the existing fail-silent, deduping lane. A FIGHT press never
   re-fetches a warming model: assets.loadModels joins the in-flight
   promise for the same id. Only MODEL_URLS ids are ever fetched, so a
   stale roster id can never send a bad path at the Netlify /roster/*
   proxy (game/_redirects + game/netlify.toml, 200 rewrites, unchanged).
   Stage variants: stages stream through arena.setStage, not MODEL_URLS,
   so there is nothing to prefetch for a stage here — fighter models are
   the bulk of a match load (see load-progress.js). */
export async function preloadNextFight(fighters, opts = {}) {
  try {
    const mod = opts.assetsModule || await import('./assets.js');
    const urls = (mod && mod.MODEL_URLS) || {};
    const prefetch = mod && mod.assets && mod.assets.prefetch;
    if (typeof prefetch !== 'function') return [];
    const ids = [];
    for (const f of (fighters || [])) {
      const cands = [typeof f === 'string' ? f : null,
        f && f.id, f && f.model, f && f.attireId, f && f.modelId];
      for (const c of cands) {
        if (c && urls[c] && !ids.includes(c)) ids.push(c);
      }
    }
    for (const id of ids) {
      try { prefetch.call(mod.assets, id); } catch (e) { /* fail-silent lane */ }
    }
    try {
      if (typeof window !== 'undefined' && typeof window.__whPreloadNote === 'function') {
        window.__whPreloadNote(ids);
      }
    } catch (e) { /* status note is optional */ }
    return ids;
  } catch (e) { return []; }
}

/* Progressive-LOD pattern (2026-10-24): warm a caller-supplied low-LOD
   file in the HTTP cache first, then prefetch the full model in the
   background. No -lod1 variant ships yet, so lowUrl is never assumed:
   without one this is exactly preloadNextFight([id]). When the asset
   pipeline (tools/asset-pipeline/) starts emitting -lod1 variants, the
   caller passes that URL here — no loader change needed. */
export async function preloadLowFirst(id, lowUrl, opts = {}) {
  try {
    if (lowUrl && typeof fetch === 'function') {
      await fetch(lowUrl, { cache: 'force-cache' }).catch(() => {});
    }
  } catch (e) { /* low-LOD warm is best-effort */ }
  return preloadNextFight([id], opts);
}

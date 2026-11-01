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

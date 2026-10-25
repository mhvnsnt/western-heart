/* ============================================================
   WESTERN HEART — preload: instant select cards + warm fights
   (Kaggle-GPU load lane, 2026-10-24).

   HONEST ARCHITECTURE — read this before claiming speedups:
   - Kaggle's GPU is a cloud notebook GPU. It CANNOT accelerate
     the phone game at runtime: the phone browser never talks to
     Kaggle's GPU. What Kaggle GPU CAN do is build-time work
     (see tools/kaggle-gpu-pipeline/): pre-rendered cards and
     optimized models committed INTO the repo, which the shipped
     game then loads fast. That pipeline is build-time; THIS file
     is runtime, and it runs on the phone's own browser + GPU.
   - What THIS file does: preloads every select-screen CARD IMAGE
     (2D, small) once the select screen has painted, so tapping any
     fighter shows its card from cache instead of waiting on a
     lazy fetch. It does NOT bulk-warm all 55+ fighter GLBs:
     the old preloadAll() did exactly that (~26MB of base GLBs
     the instant select opened) and saturated the pipe the user's
     first preview tap needed (loadspeed lane, 2026-10-22). GLBs
     still warm per highlight (select-screen.js) and per lock
     (warmFight below) — the two moments the user has already
     told the game which fighters matter.
   - Card source today is the existing portrait file
     (assets/portraits/<id>.png), the same URL the card DOM
     already uses — so a preloaded card is a cache hit, not a
     second source of truth. When the Kaggle factory lands
     pre-rendered cards under assets/cards/, the DOM portrait
     source and cardUrl() below switch together in one PR.
   - Nothing here ever rejects on a missing image: a fighter
     with no portrait yet gets the monogram plate (existing
     select-screen behaviour), never a broken card or a crash.
   - No THREE import: this module is dependency-free so the
     Node test can import it without a browser.
   ============================================================ */

export const CARD_DIR = 'assets/portraits';

/* The URL the select card DOM actually renders for a fighter. */
export function cardUrl(id) {
  return `${CARD_DIR}/${id}.png`;
}

const _cardCache = new Map(); // id -> HTMLImageElement (loaded or failed)

/* How many card images are currently cached (loaded). */
export function cardCacheSize() {
  let n = 0;
  for (const v of _cardCache.values()) if (v && v.__whPreloaded) n++;
  return n;
}

export function isCardCached(id) {
  const v = _cardCache.get(id);
  return !!(v && v.__whPreloaded);
}

/* Test hook: clear the cache between test cases. */
export function _resetCardCache() {
  _cardCache.clear();
}

function _markLoadperf(name) {
  try {
    if (typeof window !== 'undefined' && window.__loadperf && typeof window.__loadperf.mark === 'function') {
      window.__loadperf.mark(name);
    }
  } catch (_) { /* loadperf is instrumentation, never load-bearing */ }
}

/* Preload every card image in ids. Resolves ALWAYS (never rejects):
   { total, loaded, failed, cached } where cached counts images that
   were already in cache before this call. onProgress(done, total, id, ok)
   fires per image when given. imageCtor is injectable for tests
   (defaults to the browser Image constructor). */
export function preloadCards(ids, opts = {}) {
  const unique = [...new Set((ids || []).filter(Boolean))];
  const imageCtor = opts.imageCtor
    || (typeof Image !== 'undefined' ? Image : null);
  const onProgress = typeof opts.onProgress === 'function' ? opts.onProgress : null;
  let cached = 0;
  const jobs = unique.map((id) => {
    const existing = _cardCache.get(id);
    if (existing && existing.__whPreloaded) {
      cached++;
      if (onProgress) onProgress(0, unique.length, id, true);
      return Promise.resolve(true);
    }
    if (!imageCtor) {
      _cardCache.set(id, { __whPreloaded: false });
      if (onProgress) onProgress(0, unique.length, id, false);
      return Promise.resolve(false);
    }
    return new Promise((resolve) => {
      let img;
      try {
        img = new imageCtor();
      } catch (_) {
        _cardCache.set(id, { __whPreloaded: false });
        if (onProgress) onProgress(0, unique.length, id, false);
        return resolve(false);
      }
      let settled = false;
      const done = (ok) => {
        if (settled) return;
        settled = true;
        img.__whPreloaded = !!ok;
        _cardCache.set(id, img);
        if (onProgress) onProgress(0, unique.length, id, !!ok);
        resolve(!!ok);
      };
      img.onload = () => done(true);
      img.onerror = () => done(false);
      try {
        img.src = cardUrl(id);
      } catch (_) {
        done(false);
      }
    });
  });
  return Promise.all(jobs).then((results) => {
    const loaded = results.filter(Boolean).length;
    return { total: unique.length, loaded, failed: unique.length - loaded, cached };
  });
}

/* Warm the select screen: every card image, in the background, after
   the screen has painted. Call from select-screen onShow, never from
   boot or build — boot must paint first (loadspeed lane). */
export function warmSelect(ids, opts = {}) {
  const t0 = (typeof performance !== 'undefined' && performance.now)
    ? performance.now() : Date.now();
  return preloadCards(ids, opts).then((r) => {
    _markLoadperf('cards-preloaded');
    try {
      if (typeof window !== 'undefined') {
        const t1 = (typeof performance !== 'undefined' && performance.now)
          ? performance.now() : Date.now();
        window.__whCardsPreloaded = { ...r, ms: Math.round(t1 - t0) };
      }
    } catch (_) {}
    return r;
  });
}

/* Warm the fighters for an imminent fight: prefetch each model id
   through the caller-supplied prefetch (assets.prefetch in game).
   Fire-and-forget by design — prefetch itself dedups + swallows
   aborts — so this returns the deduped id list synchronously.
   Call it when fighters lock (select confirm) and again on stage
   show, so stage-screen dwell time warms the fight GLBs. It must
   NOT be called with the whole roster: that is preloadAll again. */
export function warmFight(modelIds, prefetch) {
  const ids = [...new Set((modelIds || []).filter(Boolean))];
  if (typeof prefetch === 'function') {
    for (const id of ids) {
      try { prefetch(id); } catch (_) { /* prefetch is best-effort */ }
    }
  }
  _markLoadperf('fight-warmed');
  return ids;
}

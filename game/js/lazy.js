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
    if (!_cache[name]) _cache[name] = import(path);
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

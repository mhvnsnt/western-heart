/* ============================================================
   WESTERN HEART — Custom Fighter loader (v0.3)
   Reads created fighters from the CAW suite and converts to
   roster-compatible fighter objects for character select and matches.

   Save slots: localStorage 'wh_create_fighter_slots' (array of
   {slot, saved, fighter}). Legacy single save 'wh_create_fighter_v1'
   is read as slot 0 (backward compatible).

   Moveset: the fighter's Tekken-input move assignments
   (fighter.moveset: input -> move_id) resolve against the derived
   library (customization/create-fighter/data/TEKKEN-LIBRARY.json)
   and register as window.WH_MOVESETS['custom'] — the same shape
   Lane F's per-fighter files use, so getRealMove('custom', notation)
   works with zero game-code changes.

   Performance: fighter.performance {intro, victory, victory_alignment,
   taunt, signature, finisher} rides on the roster object for the
   match intro/victory/taunt systems.
   ============================================================ */

// Body type presets (must match customization/create-fighter/js/app.js)
const BODY_TYPES = {
  'Skinny 1': { h: 1.02, w: 0.86 }, 'Skinny 2': { h: 0.98, w: 0.88 },
  'Medium 1': { h: 1.00, w: 1.00 }, 'Medium 2': { h: 1.01, w: 1.04 },
  'Thick 1': { h: 0.99, w: 1.14 }, 'Thick 2': { h: 1.00, w: 1.20 },
  'Fat 1': { h: 0.97, w: 1.30 }, 'Fat 2': { h: 0.96, w: 1.38 },
  'Austin': { h: 1.00, w: 1.12 }, 'HBK': { h: 0.99, w: 1.02 },
  'Rikishi': { h: 1.02, w: 1.42 }, 'Rock': { h: 1.01, w: 1.16 },
  'Hairy 1': { h: 1.00, w: 1.08 }, 'Hairy 2': { h: 1.01, w: 1.10 },
  'King Frame': { h: 1.04, w: 1.14 }, 'Ganryu Frame': { h: 0.96, w: 1.34 },
};

const LS_KEY = 'wh_create_fighter_v1';          // legacy single save
const LS_SLOTS = 'wh_create_fighter_slots';     // v0.3 multi-slot saves
const LIB_URL = '../customization/create-fighter/data/TEKKEN-LIBRARY.json';
const MAX_SLOTS = 4;

let _libCache = null;
let _libPromise = null;

function readJson(key) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : null;
  } catch (e) { return null; }
}

/**
 * Load a saved custom fighter. slot 0 falls back to the legacy key.
 * Returns null if none exists or data is invalid.
 */
export function getCustomFighter(slot = 0) {
  const slots = readJson(LS_SLOTS);
  if (Array.isArray(slots) && slots[slot] && slots[slot].fighter) {
    return slots[slot].fighter;
  }
  if (slot === 0) {
    const F = readJson(LS_KEY);
    if (F && F.profile) return F;
  }
  return null;
}

/** List all save slots: [{slot, saved, name}]. */
export function listCustomFighterSlots() {
  const out = [];
  const slots = readJson(LS_SLOTS);
  for (let i = 0; i < MAX_SLOTS; i++) {
    const s = Array.isArray(slots) ? slots[i] : null;
    if (s && s.fighter) {
      out.push({ slot: i, saved: s.saved || null, name: s.fighter.profile?.name || 'CUSTOM' });
    } else if (i === 0) {
      const legacy = readJson(LS_KEY);
      if (legacy && legacy.profile) {
        out.push({ slot: 0, saved: null, name: legacy.profile.name || 'CUSTOM', legacy: true });
      }
    }
  }
  return out;
}

/** Save a fighter JSON to a slot (used by the suite; game page is read-only). */
export function saveCustomFighter(F, slot = 0) {
  let slots = readJson(LS_SLOTS);
  if (!Array.isArray(slots)) slots = [];
  slots[slot] = { slot, saved: new Date().toISOString(), fighter: F };
  try {
    localStorage.setItem(LS_SLOTS, JSON.stringify(slots));
    return true;
  } catch (e) { return false; }
}

/** Fetch (cached) the derived Tekken move library. */
function loadLibrary() {
  if (_libCache) return Promise.resolve(_libCache);
  if (_libPromise) return _libPromise;
  _libPromise = fetch(LIB_URL)
    .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
    .then(lib => {
      const byId = {};
      (lib.moves || []).forEach(m => { byId[m.move_id] = m; });
      _libCache = { ...lib, byId };
      return _libCache;
    })
    .catch(e => {
      console.warn('[WH] custom fighter library unavailable:', e.message || e);
      _libCache = { moves: [], byId: {} };
      return _libCache;
    });
  return _libPromise;
}

/**
 * Resolve a fighter's Tekken-input move assignments into a WH_MOVESETS-shaped
 * object and register it as window.WH_MOVESETS['custom'].
 * Async (fetches the derived library once, then cached). Safe to call repeatedly.
 */
export async function resolveCustomMoveset(F) {
  if (!F || !F.moveset) return null;
  const lib = await loadLibrary();
  const moves = {};
  for (const [input, moveId] of Object.entries(F.moveset)) {
    const m = lib.byId[moveId];
    if (!m) continue;
    const heavy = /[34]/.test((m.limb || '')) || (typeof m.damage === 'number' && m.damage >= 20);
    moves[input] = {
      name: m.move_name,
      input: m.input,
      t3_source: m.source_fighter || m.source,
      t3_row: m.t3_row,
      t3_command: m.t3_command,
      startup: m.startup ?? 0.15,
      active: 0.05,
      recovery: 0.55,
      damage: typeof m.damage === 'number' ? m.damage : 10,
      limb: m.limb || 'armR',
      heavy,
      knock: heavy ? 4.2 : 2.2,
      soulGain: 8,
      federation: !!m.federation,
    };
  }
  const ms = { fighter: 'custom', display: F.profile?.name || 'CUSTOM', moves };
  try {
    const g = typeof window !== 'undefined' ? window : globalThis;
    g.WH_MOVESETS = g.WH_MOVESETS || {};
    g.WH_MOVESETS['custom'] = ms;   // getRealMove('custom', notation) now works
  } catch (e) { /* non-browser */ }
  console.log(`[WH] custom moveset resolved: ${Object.keys(moves).length} inputs`);
  return ms;
}

/**
 * Convert CAW fighter JSON to a roster-compatible fighter object.
 * Kicks off async moveset resolution (cached); the roster object is
 * usable immediately, moves resolve before match start.
 */
export function customFighterToRoster(F) {
  if (!F || !F.profile) return null;

  const bodyType = BODY_TYPES[F.body?.body_type] || BODY_TYPES['Medium 1'];
  const skinTone = F.body?.skin_tone || '#c98d5e';
  const name = (F.profile.name || 'CUSTOM').toUpperCase();
  const suitColor = parseInt(skinTone.replace('#', ''), 16) || 0xc98d5e;

  // Resolve the real moveset in the background (cached after first load).
  // Until it lands, getRealMove falls back to base MOVES — same as before.
  resolveCustomMoveset(F);

  const perf = F.performance || {};

  return {
    id: 'custom',
    name: name,
    title: F.profile.alias || 'Created Fighter',
    base: 'Custom',
    moveset: 'custom',   // v0.3: real resolved moveset, no longer hardcoded 'jin'
    model: 'custom',
    tintStrength: 0.3,
    colors: { suit: suitColor, trim: 0xe8b64c },
    style: F.fighting_style?.archetype || 'Balanced',
    archetype: 'Custom',
    bodyScale: bodyType.h,
    bodyWidth: bodyType.w,
    stats: {
      speed: 2.8,
      jump: 7.2,
      power: 1.0 + (F.parameters?.arms?.offense || 5) * 0.04,
      defense: 1.0 + (F.parameters?.body?.defense || 5) * 0.04,
    },
    ai: {
      aggression: (F.fighting_style?.aggression || 5) / 10,
      grabBias: 0.15,
      reaction: 0.55,
    },
    // Performance picks (intro/victory/taunt) for the match presentation systems
    performance: {
      intro: perf.intro || 't3_walk_fwd',
      victory: perf.victory || 't3_win_rp',
      victory_alignment: perf.victory_alignment || 'Face',
      taunt: perf.taunt || 't3_stance',
      signature: perf.signature || '',
      finisher: perf.finisher || '',
    },
    decals: Array.isArray(F.decals) ? F.decals : [],
    _caw: F,
  };
}

/** Check if any custom fighter exists and is valid. */
export function hasCustomFighter() {
  return listCustomFighterSlots().length > 0;
}

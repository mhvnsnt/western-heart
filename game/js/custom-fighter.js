/* ============================================================
   WESTERN HEART — Custom Fighter loader
   Reads created fighters from the CAW suite (localStorage
   'wh_create_fighter_v1') and converts to roster-compatible
   fighter objects for character select and matches.

   Moveset wiring: maps game attack inputs (punch/kick/grab)
   to CAW moveset slots, resolves move_id -> MOVE-DATABASE.json
   data, scales damage by power grade. Unassigned slots fall
   back to Jin/T3 defaults. Soul Surge is WH-original and
   never customizable.
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

const LS_KEY = 'wh_create_fighter_v1';

/* Game attack input -> CAW moveset slot mapping.
   Slots from customization/create-fighter/data/MOVE-SLOTS.json.
   surge is intentionally absent: Soul Surge is WH-original. */
const ATTACK_SLOT_MAP = {
  punch: 'weakArmStrikeSlot1',   // standing.weak_arm_strike.tap_strike
  kick:  'weakLegStrikeSlot1',   // standing.weak_leg_strike.tap_strike
  grab:  'frontWeakGrappleSlot1', // grappling.front_weak_grapple.grapple
};

/* Power grade -> damage multiplier. MOVE-DATABASE.json uses
   letter grades (E weakest). Unlisted grades default to 1.0. */
const POWER_MULT = { 'E': 0.8, 'D': 0.9, 'C': 1.0, 'B': 1.15, 'A': 1.3, 'S': 1.5 };

/* Cached move database (loaded once from the CAW data dir). */
let _moveDb = null;
let _moveDbPromise = null;

async function loadMoveDatabase() {
  if (_moveDb) return _moveDb;
  if (_moveDbPromise) return _moveDbPromise;
  _moveDbPromise = (async () => {
    try {
      const urls = [
        '../customization/create-fighter/data/MOVE-DATABASE.json',
        'customization/create-fighter/data/MOVE-DATABASE.json',
      ];
      for (const u of urls) {
        try {
          const r = await fetch(u);
          if (r.ok) { _moveDb = await r.json(); return _moveDb; }
        } catch (e) { /* try next */ }
      }
      console.warn('[WH] Custom moveset DB not found, using fallback');
      _moveDb = { sample_moves: [] };
    } catch (e) {
      console.warn('[WH] Move DB load failed:', e.message);
      _moveDb = { sample_moves: [] };
    }
    return _moveDb;
  })();
  return _moveDbPromise;
}

function findMove(db, moveId) {
  if (!db || !moveId) return null;
  const moves = db.sample_moves || db.moves || [];
  return moves.find(m => m.move_id === moveId) || null;
}

function applyCustomMove(move, baseMove) {
  const mult = POWER_MULT[move.power] ?? 1.0;
  const custom = { ...baseMove };
  custom.damage = Math.round(baseMove.damage * mult);
  custom._customName = move.move_name;
  custom._customId = move.move_id;
  custom._customSource = move.source;
  const props = move.properties || [];
  if (props.includes('unblockable')) { custom.unblockable = true; custom.isGrab = true; }
  return custom;
}

/**
 * Resolve a custom move for a CAW fighter's attack input.
 * Returns a game-format move object, or null if the slot is
 * unassigned (caller falls back to Jin/T3 defaults).
 */
export async function resolveCustomMove(F, attackName, baseMove) {
  const slot = ATTACK_SLOT_MAP[attackName];
  if (!slot || !F?.moveset) return null;
  const moveId = F.moveset[slot];
  if (!moveId) return null;
  const db = await loadMoveDatabase();
  const move = findMove(db, moveId);
  if (!move) {
    console.warn(`[WH] Custom move ${moveId} not in database`);
    return null;
  }
  return applyCustomMove(move, baseMove);
}

/**
 * Synchronous version for hot-path use when DB is already cached.
 */
export function resolveCustomMoveSync(F, attackName, baseMove) {
  if (!_moveDb) return null;
  const slot = ATTACK_SLOT_MAP[attackName];
  if (!slot || !F?.moveset) return null;
  const moveId = F.moveset[slot];
  if (!moveId) return null;
  const move = findMove(_moveDb, moveId);
  if (!move) return null;
  return applyCustomMove(move, baseMove);
}

/** Preload the move DB (call at game boot for custom fighters). */
export function preloadMoveDatabase() {
  return loadMoveDatabase();
}

/**
 * Load the saved custom fighter from localStorage.
 * Returns null if none exists or data is invalid.
 */
export function getCustomFighter() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (!raw) return null;
    const F = JSON.parse(raw);
    if (!F || !F.profile) return null;
    return F;
  } catch (e) {
    console.warn('[WH] Failed to load custom fighter:', e.message);
    return null;
  }
}

/**
 * Convert CAW fighter JSON to a roster-compatible fighter object.
 */
export function customFighterToRoster(F) {
  if (!F || !F.profile) return null;

  const bodyType = BODY_TYPES[F.body?.body_type] || BODY_TYPES['Medium 1'];
  const skinTone = F.body?.skin_tone || '#c98d5e';
  const name = (F.profile.name || 'CUSTOM').toUpperCase();
  const suitColor = parseInt(skinTone.replace('#', ''), 16) || 0xc98d5e;
  const assignedSlots = F.moveset ? Object.keys(F.moveset).length : 0;

  return {
    id: 'custom',
    name: name,
    title: F.profile.alias || 'Created Fighter',
    base: 'Custom',
    moveset: 'custom',
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
    customMovesetSlots: assignedSlots,
    _caw: F,
  };
}

/**
 * Check if a custom fighter exists and is valid.
 */
export function hasCustomFighter() {
  return getCustomFighter() !== null;
}

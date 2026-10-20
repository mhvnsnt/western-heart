/* ============================================================
   WESTERN HEART — Custom Fighter loader
   Reads created fighters from the CAW suite (localStorage
   'wh_create_fighter_v1') and converts to roster-compatible
   fighter objects for character select and matches.
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
// Stream 4: the flagship Creation Suite (customization/creation-suite-ui)
// saves under its own key with a compatible profile/body shape.
const LS_KEY_SUITE = 'wh_creation_suite_v1';

/**
 * Load the saved custom fighter from localStorage.
 * Reads the flagship Creation Suite format first (`wh_creation_suite_v1`),
 * then falls back to the legacy create-fighter format (`wh_create_fighter_v1`).
 * Returns null if none exists or data is invalid.
 */
export function getCustomFighter() {
  for (const key of [LS_KEY_SUITE, LS_KEY]) {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) continue;
      const F = JSON.parse(raw);
      if (!F || !F.profile) continue;
      return F;
    } catch (e) { /* try next key */ }
  }
  console.warn('[WH] No custom fighter found in either suite slot');
  return null;
}

/**
 * Convert CAW fighter JSON to a roster-compatible fighter object.
 * Uses Soldier.glb base model with saved appearance applied.
 */
export function customFighterToRoster(F) {
  if (!F || !F.profile) return null;

  const bodyType = BODY_TYPES[F.body?.body_type] || BODY_TYPES['Medium 1'];
  const skinTone = F.body?.skin_tone || '#c98d5e';
  const name = (F.profile.name || 'CUSTOM').toUpperCase();
  // Title: legacy `alias` string, or flagship suite `title: [A, B]` pair.
  const title = F.profile.alias ||
    (Array.isArray(F.profile.title) ? F.profile.title.filter(Boolean).join(' ') : '') ||
    'Created Fighter';

  // Convert hex skin tone to integer for the game's color system
  const suitColor = parseInt(skinTone.replace('#', ''), 16) || 0xc98d5e;

  return {
    id: 'custom',
    name: name,
    title: title,
    base: 'Custom',
    moveset: 'jin', // Default; TODO: wire custom moveset slots
    model: 'custom',
    tintStrength: 0.3,
    colors: { suit: suitColor, trim: 0xe8b64c },
    style: F.fighting_style?.archetype || 'Balanced',
    archetype: 'Custom',
    // Body type affects scale
    bodyScale: bodyType.h,
    bodyWidth: bodyType.w,
    // Custom stats from CAW parameters
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
    // Raw CAW data for appearance application
    _caw: F,
  };
}

/**
 * Check if a custom fighter exists and is valid.
 */
export function hasCustomFighter() {
  return getCustomFighter() !== null;
}

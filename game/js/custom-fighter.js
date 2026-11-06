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

import { selectFittedParts } from './fitted-parts.js';

const LS_KEY = 'wh_create_fighter_v1';
// Stream 4: the flagship Creation Suite (customization/creation-suite-ui)
// saves under its own key with a compatible profile/body shape.
const LS_KEY_SUITE = 'wh_creation_suite_v1';

// Phase 4b (2026-11-02): the 9 template ids in
// customization/templates/body-templates.json. The game-side allowlist
// mirrors that file; a template id outside this list is never trusted
// into a model key (it would 404 the fight load).
const TEMPLATE_IDS = [
  'super-heavyweight', 'powerhouse', 'showman',
  'technician', 'highflyer', 'luchador',
  'powerhouse-w', 'athletic-w', 'striker-w',
];
// The suite's default template (customization/creation-suite-ui/js/suite.js
// DEFAULT_TEMPLATE_ID), also the suite's own migration target for saved
// fighters that still sit on the legacy Soldier base (migrateLegacy).
const DEFAULT_TEMPLATE_ID = 'technician';

/**
 * Resolve a saved fighter to its in-fight model key (Phase 4b).
 * Blank-mode saves (the CREATE flow) carry `template` + `baseGlb`
 * (customization/templates/meshes/<id>.glb); either field resolves
 * to `custom-template-<id>` (game/js/assets.js MODEL_URLS), so the
 * fighter fights on its own template body with its morphs, never
 * on the stock Soldier model. A save with neither field (legacy
 * create-fighter format) follows the suite's own migration and
 * defaults to the technician template.
 * Roster-mode saves (editing an existing fighter) are NOT remapped
 * here: their baseGlb is that roster fighter's attire GLB, which
 * has no MODEL_URLS key of its own, so they keep the legacy
 * 'custom' (Soldier) slot until the edit-existing-fighters phase
 * (ORDER doc Phase 4) wires roster attire models into fights.
 * That remainder is still owed, stated here rather than papered
 * over with a wrong body.
 */
function templateModelFor(F) {
  if (F.mode === 'roster') return { template: F.template || null, model: 'custom' };
  let id = F.template || null;
  if (!id && typeof F.baseGlb === 'string') {
    const m = /customization\/templates\/meshes\/([a-z0-9-]+)\.glb$/.exec(F.baseGlb);
    if (m) id = m[1];
  }
  if (!id || !TEMPLATE_IDS.includes(id)) id = DEFAULT_TEMPLATE_ID;
  return { template: id, model: 'custom-template-' + id };
}

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
 * Phase 4b: the fighter fights on its chosen template body
 * (templateModelFor, above), with its saved morphs applied once
 * at build by Fighter._build (game/js/fighter.js _applyCharMorphs
 * runs in _build and after a transform model swap only — never
 * per-frame, so fights stay light on a phone).
 */
export function customFighterToRoster(F) {
  if (!F || !F.profile) return null;
  const { template, model } = templateModelFor(F);

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
    // MOVESET FALLBACK, explicit (Phase 4b): no custom moveset slots
    // are wired yet, so a created fighter falls back to the jin
    // bank for animation (fighter.js bankIdFor logs this fallback
    // once) and to the generic move table for frame data. Custom
    // moveset slots are still TODO — this placeholder is named
    // here and in bankIdFor, not hidden behind a silent default.
    moveset: 'jin',
    movesetFallback: 'jin',
    model: model,
    tintStrength: 0.3,
    colorize: true, // the CAW skin tone is applied as a tint (player's choice)
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
    // Phase 3 completion (2026-11-02): the suite's saved morph slider
    // values ride along instead of being silently dropped — Fighter._build
    // applies them to the built model via game/js/morph-apply.js.
    // Phase 4b: the template body itself now rides along too (the
    // `model` key above resolves to the template GLB), and morphs
    // are baked onto that instance once at build — the built
    // template carries real morph targets, so the values land.
    morphTargets: { ...(F.body?.morph_targets || {}) },
    // Which template body this fighter was created from (the
    // resolved template id; 'technician' for template-less legacy
    // saves, null only for roster-mode saves whose template field
    // was never set — see templateModelFor).
    template: template,
    baseGlb: F.baseGlb || null,
    // HAIR phase (2026-11-02): the suite's chosen template-fitted hair /
    // facial hair / brows / lashes for the active attire, with their
    // tints — Fighter._build parents each to the template's head bone
    // (game/js/fitted-parts.js). Roster-mode saves have no template body,
    // so they carry none (selectFittedParts returns [] off-template).
    fittedParts: F.mode === 'roster' ? [] : selectFittedParts(
      (Array.isArray(F.attires) && F.attires[F.attireIndex || 0]) || null, template),
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

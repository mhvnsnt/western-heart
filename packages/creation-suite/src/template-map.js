/* template-map.js — pure (DOM-free) body-type / template / proportions logic
   for the Creation Suite. Suite.js imports this; Node tests import this.
   Data sources (never invented):
   - Template proportions + skin tones + head shapes + base meshes:
     customization/templates/body-templates.json (9 MB-Lab-baked templates).
   - Legacy height/weight per body type: game/js/custom-fighter.js BODY_TYPES
     (the legacy create-fighter table; agrees with the template JSON on all
     6 overlapping types: Medium 1 1.00/1.00, Skinny 1 1.02/0.86, Austin
     1.00/1.12, HBK 0.99/1.02, Rikishi 1.02/1.42, Rock 1.01/1.16).
   - Body types WITHOUT a dedicated template use a FAMILY fallback: the
     nearest template family's muscle value + (for male types) the legacy
     height/weight. The `basis` field says exactly which — the UI shows it,
     so a family fallback is never presented as extracted data.
   - DNA slider semantics (packages/creation-suite/src/dna.js): "0 = model
     as authored" — DNA sliders are DELTAS, not multipliers. WMXIX PROPS are
     multipliers (0.85–1.30), so propsToDNA converts prop-1 and clamps to
     each slider's range. viewer.setProportions() already owns overall
     height/weight (uniform model scale), so propsToDNA maps ONLY the shape
     sliders the uniform scale ignores (muscle, shoulders, chest, waist,
     hips, arms, legs) — height/weight are deliberately excluded so they are
     never applied twice. Merge is ADDITIVE (template proportion delta +
     fine morph delta, clamped): morphs layer on top of props, they do not
     erase them. */

import { SLIDERS } from './dna.js';

export const DEFAULT_PROPS = {
  height: 1, weight: 1, muscle: 1, shoulder: 1, chest: 1,
  waist: 1, hips: 1, arms: 1, legs: 1,
};

/* game/js/custom-fighter.js BODY_TYPES, verbatim. */
export const LEGACY_HW = {
  'Skinny 1': { h: 1.02, w: 0.86 }, 'Skinny 2': { h: 0.98, w: 0.88 },
  'Medium 1': { h: 1.00, w: 1.00 }, 'Medium 2': { h: 1.01, w: 1.04 },
  'Thick 1': { h: 0.99, w: 1.14 }, 'Thick 2': { h: 1.00, w: 1.20 },
  'Fat 1': { h: 0.97, w: 1.30 }, 'Fat 2': { h: 0.96, w: 1.38 },
  'Austin': { h: 1.00, w: 1.12 }, 'HBK': { h: 0.99, w: 1.02 },
  'Rikishi': { h: 1.02, w: 1.42 }, 'Rock': { h: 1.01, w: 1.16 },
  'Hairy 1': { h: 1.00, w: 1.08 }, 'Hairy 2': { h: 1.01, w: 1.10 },
  'King Frame': { h: 1.04, w: 1.14 }, 'Ganryu Frame': { h: 0.96, w: 1.34 },
};

/* Body type -> nearest template family (template ids from body-templates.json).
   Only used when the type has NO dedicated template (dedicated = the
   template whose body_type field equals the type). */
export const BODY_TYPE_FAMILY = {
  'Skinny 2': 'luchador', 'Medium 2': 'technician',
  'Thick 1': 'powerhouse', 'Thick 2': 'powerhouse',
  'Fat 1': 'super-heavyweight', 'Fat 2': 'super-heavyweight',
  'Hairy 1': 'powerhouse', 'Hairy 2': 'powerhouse',
  'King Frame': 'showman', 'Ganryu Frame': 'super-heavyweight',
  'Skinny F': 'striker-w', 'Medium F': 'athletic-w', 'Thick F': 'powerhouse-w',
  'Fat F': 'powerhouse-w', 'Athletic F': 'athletic-w', 'Curvy F': 'powerhouse-w',
  'Petite F': 'striker-w', 'Tall F': 'athletic-w', 'Dancer F': 'striker-w',
};

/* Resolve a body type to proportions + (optionally) a template mesh.
   templates: the parsed body-templates.json templates array (may be empty
   when the JSON failed to load — then only the legacy table applies).
   Returns { proportions, templateId|null, basis } where basis is one of:
   'dedicated' (template.body_type === type), 'legacy+family' (male type:
   legacy h/w + family template muscle), 'family' (female type: whole family
   template proportions — no legacy h/w source exists for F types),
   'default' (unknown type: 1.0 everywhere). */
export function bodyTypeToDNA(bodyType, templates) {
  const list = Array.isArray(templates) ? templates : [];
  const dedicated = list.find(t => t.body_type === bodyType);
  if (dedicated) {
    return { proportions: { ...DEFAULT_PROPS, ...(dedicated.proportions || {}) },
             templateId: dedicated.id, basis: 'dedicated' };
  }
  const family = list.find(t => t.id === BODY_TYPE_FAMILY[bodyType]);
  const hw = LEGACY_HW[bodyType];
  if (hw && family) {
    return { proportions: { ...DEFAULT_PROPS, height: hw.h, weight: hw.w,
                            muscle: (family.proportions || {}).muscle ?? 1 },
             templateId: family.id, basis: 'legacy+family' };
  }
  if (family) {
    return { proportions: { ...DEFAULT_PROPS, ...(family.proportions || {}) },
             templateId: family.id, basis: 'family' };
  }
  if (hw) {
    return { proportions: { ...DEFAULT_PROPS, height: hw.h, weight: hw.w },
             templateId: null, basis: 'legacy-only' };
  }
  return { proportions: { ...DEFAULT_PROPS }, templateId: null, basis: 'default' };
}

/* WMXIX PROPS -> DNA slider deltas (prop - 1, clamped to each slider's
   range). Height/weight intentionally excluded: viewer.setProportions()
   owns those (uniform model scale). The DNA keys here are the
   packages/creation-suite/src/dna.js SLIDERS keys. */
export function propsToDNA(props) {
  const p = props || {};
  const out = {};
  const put = (dnaKey, propKey) => {
    if (p[propKey] === undefined) return;
    const s = SLIDERS[dnaKey];
    const d = (Number(p[propKey]) || 1) - 1;
    out[dnaKey] = s ? Math.min(s.range[1], Math.max(s.range[0], d)) : d;
  };
  put('muscle', 'muscle');
  put('shoulders', 'shoulder');
  put('chest', 'chest');
  put('belly', 'waist');
  put('hips', 'hips');
  put('arms', 'arms');
  put('legLen', 'legs');
  return out;
}

/* Merge two DNA slider delta maps ADDITIVELY, clamped to each slider's
   range (unknown keys pass through). Template/props deltas + fine morph
   deltas both survive; neither erases the other. */
export function mergeDNA(base, override) {
  const out = {};
  for (const k of new Set([...Object.keys(base || {}), ...Object.keys(override || {})])) {
    const sum = (Number((base || {})[k]) || 0) + (Number((override || {})[k]) || 0);
    const s = SLIDERS[k];
    out[k] = s ? Math.min(s.range[1], Math.max(s.range[0], sum)) : sum;
  }
  return out;
}

// closet-recipes.js — engine-agnostic closet recipe format (registry v2).
//
// One recipe = one saved closet state: character + preset + every slot
// toggle + colors + lighting + camera. A scene/episode names a recipe;
// the renderer/game loads it. Recipes are NEVER overwritten: saving
// under an existing name appends a new version, and the earlier version
// stays loadable. Pure module: no DOM, no Three.js, unit-testable.
//
// Shape (format_version 2):
//   { format_version: 2, name, version, character, preset,
//     toggles: { <slot>: { item: [<mesh names>] | null, visible: bool } },
//     colors: { <slot>: [<css colors>] }, lighting: 'studio'|'living_room'|'night',
//     camera: { yaw, pitch, dist, target: [x, y, z] } }

export const RECIPE_FORMAT_VERSION = 2;
export const RECIPE_LIGHTINGS = ['studio', 'living_room', 'night'];

export function createRecipe(input = {}) {
  const name = String(input.name || '').trim();
  if (!name) throw new Error('closet recipe needs a name');
  if (!input.character) throw new Error('closet recipe needs a character');
  const lighting = RECIPE_LIGHTINGS.includes(input.lighting) ? input.lighting : 'studio';
  return {
    format_version: RECIPE_FORMAT_VERSION,
    name,
    version: 0, // assigned by saveRecipe; 0 = unversioned draft, never stored
    character: input.character,
    preset: input.preset ?? null,
    toggles: input.toggles || {},
    colors: input.colors || {},
    lighting,
    camera: input.camera || null,
  };
}

export function validateRecipe(recipe) {
  if (!recipe || typeof recipe !== 'object') return 'not an object';
  if (recipe.format_version !== RECIPE_FORMAT_VERSION) return 'format_version must be 2';
  if (!recipe.name || typeof recipe.name !== 'string') return 'name required';
  if (!recipe.character || typeof recipe.character !== 'string') return 'character required';
  if (recipe.toggles == null || typeof recipe.toggles !== 'object') return 'toggles required';
  if (!RECIPE_LIGHTINGS.includes(recipe.lighting)) return 'lighting must be studio, living_room or night';
  return null;
}

/** Append a versioned copy; never mutates or overwrites an earlier recipe. */
export function saveRecipe(store, recipe) {
  const err = validateRecipe({ ...recipe, version: recipe.version || 0 });
  if (err) throw new Error(`invalid closet recipe: ${err}`);
  const list = Array.isArray(store) ? store.slice() : [];
  const sameName = list.filter((r) => r.name === recipe.name);
  const version = sameName.reduce((m, r) => Math.max(m, r.version || 0), 0) + 1;
  const stored = { ...recipe, version, toggles: { ...recipe.toggles }, colors: { ...recipe.colors } };
  list.push(stored);
  return list;
}

/** Latest version of a name, or the exact version when given; null if absent. */
export function loadRecipe(store, name, version = null) {
  const list = (Array.isArray(store) ? store : []).filter((r) => r.name === name);
  if (!list.length) return null;
  if (version != null) return list.find((r) => r.version === version) || null;
  return list.reduce((a, b) => ((b.version || 0) > (a.version || 0) ? b : a));
}

export function listRecipes(store) {
  return (Array.isArray(store) ? store : []).map((r) => ({ name: r.name, version: r.version, character: r.character }));
}

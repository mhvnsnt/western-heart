/* ============================================================
   WESTERN HEART — Clothing Layer System (worker 64, 2026-10-22)
   Owner directive: "Make it able to remove and change their clothes
   in the character creation suite and in game when I play it and
   preview it."

   Per-mesh visibility toggle engine over GLB mesh names. Clothing is a
   proper LAYER system, not a hack: every clothing mesh on an attire is
   a named, categorized, toggleable layer. Labels follow
   docs/CLOTHING-ACCESSORY-LABELING-STANDARD.md
   (<category>_<item>_<variant>, e.g. top_bra_01) — never the raw GLB
   mesh names (Bra (2), OBsuit, Gaunlet, …).

   Data-driven: game/data/clothing-layers.json maps model key ->
   layers. Each layer: { label, category, meshes: [raw GLB mesh names],
   default_visible }. Nothing is hardcoded here.

   Persistence: localStorage `wh_clothing_v1`:
     { "<modelKey>": { "<label>": true } }   (true = hidden)
   ============================================================ */

const LS_KEY = 'wh_clothing_v1';
const CONFIG_URL = 'data/clothing-layers.json';

/* The taxonomy (mirrors the labeling standard doc). Categories exist so
   pieces can be organized, filtered, and mixed/matched across characters
   in the creation suite library. */
export const CLOTHING_CATEGORIES = {
  hair: 'HAIR',
  headwear: 'HEADWEAR',
  facewear: 'FACEWEAR',
  top: 'TOPS',
  bottom: 'BOTTOMS',
  fullbody: 'FULL-BODY',
  underwear: 'UNDERWEAR',
  legwear: 'LEGWEAR',
  gloves: 'GLOVES',
  footwear: 'FOOTWEAR',
  accessory: 'ACCESSORIES',
};

let _config = null;
let _configPromise = null;

/** Load (and cache) the data-driven clothing config. Never rejects. */
export function loadClothingConfig() {
  if (_config) return Promise.resolve(_config);
  if (_configPromise) return _configPromise;
  _configPromise = (async () => {
    try {
      const res = await fetch(CONFIG_URL);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      _config = await res.json();
    } catch (e) {
      console.warn('[WH-CLOTHING] config unavailable, layers disabled:', (e && e.message) || e);
      _config = { version: 1, models: {} };
    }
    return _config;
  })();
  return _configPromise;
}

/** Layers registered for a model key (the MODEL_URLS key / attire). */
export function getLayers(modelKey) {
  const m = _config && _config.models && _config.models[modelKey];
  return (m && m.layers) || [];
}

/** Read the persisted hidden-set: { modelKey: { label: true } }. */
export function readClothingState() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    const o = raw ? JSON.parse(raw) : {};
    return o && typeof o === 'object' ? o : {};
  } catch { return {}; }
}

function writeClothingState(state) {
  try { localStorage.setItem(LS_KEY, JSON.stringify(state)); } catch { /* private mode */ }
}

/** A mesh belongs to a layer when its name matches any of the layer's
    raw GLB mesh names (case-insensitive, trimmed). Matching is by
    explicit list — never by substring — so `Bra` never catches `Bra (2)`
    unless the config lists it. */
export function meshMatchesLayer(meshName, layer) {
  const n = String(meshName || '').trim().toLowerCase();
  return (layer.meshes || []).some((m) => String(m).trim().toLowerCase() === n);
}

/** Apply saved clothing visibility to a loaded model instance (THREE
    Group). Idempotent; safe to call on any model. Returns the number of
    meshes toggled off. */
export function applyClothing(model, modelKey) {
  if (!model || !modelKey) return 0;
  const layers = getLayers(modelKey);
  if (!layers.length) return 0;
  const state = readClothingState();
  const hidden = state[modelKey] || {};
  let off = 0;
  model.traverse((o) => {
    if (!o.isMesh && !o.isSkinnedMesh) return;
    for (const layer of layers) {
      if (meshMatchesLayer(o.name, layer)) {
        const hide = hidden[layer.label] === true;
        // A layer explicitly saved as visible (false) beats the default too.
        const visible = layer.label in hidden ? !hidden[layer.label] : layer.default_visible !== false;
        o.visible = visible;
        if (!visible) off++;
        break;
      }
    }
  });
  return off;
}

/**
 * Toggle one layer on a live model instance. Persists the choice per
 * model key so it survives reloads, the suite, and the fight screen.
 * Returns { label, visible, meshes } — meshes = affected mesh names.
 */
export function setLayerVisible(model, modelKey, label, visible) {
  const layers = getLayers(modelKey);
  const layer = layers.find((l) => l.label === label);
  if (!layer) return { label, visible, meshes: [], error: 'unknown layer' };
  const affected = [];
  if (model) {
    model.traverse((o) => {
      if ((!o.isMesh && !o.isSkinnedMesh) || !meshMatchesLayer(o.name, layer)) return;
      o.visible = !!visible;
      affected.push(o.name);
    });
  }
  const state = readClothingState();
  const per = state[modelKey] || {};
  if (visible && layer.default_visible !== false) delete per[label];
  else per[label] = !visible;
  if (Object.keys(per).length) state[modelKey] = per; else delete state[modelKey];
  writeClothingState(state);
  return { label, visible: !!visible, meshes: affected };
}

/** Is this layer currently visible on the model (live read)? */
export function isLayerVisible(model, modelKey, label) {
  const layers = getLayers(modelKey);
  const layer = layers.find((l) => l.label === label);
  if (!layer) return null;
  let seen = 0, vis = 0;
  if (model) {
    model.traverse((o) => {
      if ((!o.isMesh && !o.isSkinnedMesh) || !meshMatchesLayer(o.name, layer)) return;
      seen++; if (o.visible) vis++;
    });
  }
  if (!seen) {
    const hidden = (readClothingState()[modelKey] || {})[label];
    return label in ((readClothingState()[modelKey]) || {}) ? !hidden : layer.default_visible !== false;
  }
  return vis > 0;
}

/**
 * One-call hook for assets.createInstance(): loads config (cached after
 * first call) and applies saved clothing. Fire-and-forget safe — the
 * instance is fully usable before this resolves; visibility applies as
 * soon as the config arrives.
 */
export function applyClothingToInstance(model, modelKey) {
  try {
    loadClothingConfig().then(() => {
      try { applyClothing(model, modelKey); } catch (e) {
        console.warn('[WH-CLOTHING] apply failed:', (e && e.message) || e);
      }
    });
  } catch (e) {
    console.warn('[WH-CLOTHING] hook failed:', (e && e.message) || e);
  }
}

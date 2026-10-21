/* ============================================================
   WESTERN HEART — Attire picker (Stream 4 parity push, item 3)
   Every fighter's attires browsable and selectable, mobile touch.
   Attires are model variants (MODEL_URLS keys in assets.js).
   Selection persists per-fighter in localStorage `wh_attires_v1`
   and is applied when the fighter is confirmed for a match.
   ============================================================ */

const LS_KEY = 'wh_attires_v1';

/* model base -> [{ model, label }]. Labels from owner notes / CANON.md.
   Fighters not listed here get a single default (their base model). */
export const ATTIRE_VARIANTS = {
  // RAVE / Kiko Tanaka — roster/TRIPO-REGISTRY.md slot order
  'kiko-tanaka': [
    { model: 'kiko-tanaka', label: 'ATTIRE 1 · HOODED' },
    { model: 'kiko-tanaka_alt1', label: 'ATTIRE 2 · GHOST TANAKA' },
    { model: 'rave', label: 'ATTIRE 3 · MUTA' },
  ],
  'thor': [
    { model: 'thor', label: 'ATTIRE 1' },
    { model: 'thor-attire2', label: 'ATTIRE 2 · ONI MASK' },
  ],
  'demonio': [
    { model: 'demonio', label: 'BASE' },
    { model: 'demonio-a1', label: 'ATTIRE 1' },
    { model: 'demonio-winged', label: 'WINGED DEVIL' },
    { model: 'demonio-human', label: 'HUMAN' },
    { model: 'demonio-bloodline-ember', label: 'BLOODLINE EMBER' },
  ],
  'doc-frank': [
    { model: 'doc-frank', label: 'BASE' },
    { model: 'doc-frank-big', label: 'TRANSFORMED' },
    { model: 'doc-frank-wowomomo', label: 'WOWOMOMO' },
    { model: 'doc-frank-wowomomo-big', label: 'WOWOMOMO XL' },
    { model: 'doc-frank-hood', label: 'HOOD SCIENTIST' },
    { model: 'doc-frank-hood-big', label: 'HOOD XL' },
    { model: 'doc-frank-machine-shop', label: 'MACHINE SHOP' },
  ],
  'mariposa': [
    { model: 'mariposa', label: 'ATTIRE 1 · BUTTERFLY' },
    { model: 'mariposa-slot2', label: 'SLOT 2' },
    { model: 'mariposa-monarch', label: 'MONARCH' },
  ],
  'burger': [
    { model: 'burger', label: 'ATTIRE 1 · DEMON' },
    { model: 'burger-attire2', label: 'ATTIRE 2' },
    { model: 'burger-attire3', label: 'ATTIRE 3' },
    { model: 'burger-attire4', label: 'ATTIRE 4' },
    { model: 'burger-attire5', label: 'ATTIRE 5' },
    { model: 'burger-attire6', label: 'ATTIRE 6' },
    { model: 'burger-attire7', label: 'ATTIRE 7' },
  ],
  'cain-elias': [
    { model: 'cain-elias', label: 'ATTIRE 1 · BIKER' },
    { model: 'cain-elias-attire2', label: 'ATTIRE 2 · FIGHT GEAR' },
  ],
  'dxmmii': [
    { model: 'dxmmii', label: 'BASE' },
    { model: 'dxmmii-a2', label: 'ATTIRE 2' },
    { model: 'dxmmii-patchwork', label: 'PATCHWORK' },
  ],
  /* KEVIN's ladder (owner 2026-10-20): A1 = kevin-tripo (his face, pending
     rig/wiring), A2 = original Baek model, A3 = Master White (PARKED).
     Keyed by fighter id so Kevin's entry finds it. */
  'baek-master-white': [
    { model: 'baek', label: 'KEVIN · A2 BAEK MODEL' },
    { model: 'baek-master-white', label: 'MASTER WHITE (PARKED)' },
  ],
  'purple-rain': [
    { model: 'purple-rain', label: 'BASE' },
    { model: 'purple-rain-main', label: 'MAIN' },
  ],
  'saku-ra': [
    { model: 'saku-ra', label: 'BASE' },
    { model: 'saku-ra-main', label: 'MAIN' },
  ],
  'phantom': [
    { model: 'phantom', label: 'BASE' },
    { model: 'phantom-t8', label: 'T8' },
  ],
  'kinpo': [
    { model: 'kinpo', label: 'BASE' },
    { model: 'kinpo-t8', label: 'T8' },
  ],
  'pantera': [
    { model: 'pantera', label: 'ATTIRE 1' },
    { model: 'pantera-leoman', label: 'ATTIRE 2 · LEO MAN' },
  ],
};

function loadMap() {
  try { return JSON.parse(localStorage.getItem(LS_KEY) || '{}'); }
  catch (e) { return {}; }
}
function saveMap(m) {
  try { localStorage.setItem(LS_KEY, JSON.stringify(m)); } catch (e) {}
}

/** Attires available for a roster fighter (by model, falls back to roster id). */
export function attiresFor(fighter) {
  if (!fighter) return [];
  const list = ATTIRE_VARIANTS[fighter.model] || ATTIRE_VARIANTS[fighter.id];
  if (list && list.length) return list;
  // Default: single attire = the fighter's own model
  return [{ model: fighter.model || 'pantera', label: 'ATTIRE 1' }];
}

/** The persisted attire model id for this fighter (or their base). */
export function selectedAttireModel(fighter) {
  const map = loadMap();
  const list = attiresFor(fighter);
  const saved = map[fighter.id];
  if (saved && list.some(a => a.model === saved)) return saved;
  return list[0].model;
}

/** Persist the attire choice for a fighter. */
export function setAttire(fighter, modelId) {
  const map = loadMap();
  map[fighter.id] = modelId;
  saveMap(map);
}

/** The label for a model id within a fighter's attire list. */
export function attireLabel(fighter, modelId) {
  const a = attiresFor(fighter).find(x => x.model === modelId);
  return a ? a.label : 'ATTIRE 1';
}

/**
 * Resolve a roster fighter to the version used in a match:
 * a shallow copy with `model` swapped to the selected attire.
 * The original roster entry is never mutated.
 */
export function resolveFighterAttire(fighter) {
  if (!fighter) return fighter;
  return { ...fighter, model: selectedAttireModel(fighter) };
}

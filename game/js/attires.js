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
  'deathfang': [
    { model: 'deathfang', label: 'ATTIRE 1 · CHAINED PRISONER' },
    { model: 'deathfang-werewolf', label: 'ATTIRE 2 · WEREWOLF' },
  ],
  'doc-frank': [
  /* DOC FRANK's ladder — keyed by fighter id ('docfrank'), same pattern as
     Kevin's ladder below: attiresFor() looks up fighter.model, then
     fighter.id — and the main entry's model is 'doc-frank-machine-shop',
     so keying this list 'doc-frank' left his attires unreachable from his
     own picker (model-key audit, docs/MODEL-KEY-AUDIT-2026-10-21.md).
     Frankenstein pair added: Attire 4 was missing from the list entirely.
     Every entry is one of Doc Frank's own wired models. */
  'docfrank': [
    { model: 'doc-frank', label: 'BASE' },
    { model: 'doc-frank-big', label: 'TRANSFORMED' },
    { model: 'doc-frank-wowomomo', label: 'WOWOMOMO' },
    { model: 'doc-frank-wowomomo-big', label: 'WOWOMOMO XL' },
    { model: 'doc-frank-hood', label: 'HOOD SCIENTIST' },
    { model: 'doc-frank-hood-big', label: 'HOOD XL' },
    { model: 'doc-frank-frankenstein', label: 'FRANKENSTEIN' },
    { model: 'doc-frank-frankenstein-big', label: 'FRANKENSTEIN XL' },
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
  'vainabel': [
    { model: 'vainabel-attire2', label: 'ATTIRE 2' },
    { model: 'vainabel-attire3', label: 'ATTIRE 3 · MASKED DEMON OF THE PURPLE HAZE' },
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
  /* DIABLO's ladder (fighter-completeness audit 2026-10-21): Attire 2
     "Devil God" was wired as a MODEL_URLS key + GLB (PR #419) but had no
     variant list, so the picker only ever offered Attire 1. Labels from
     roster/diablo/ATTIRE-SLOTS.md. First entry stays the current default. */
  'diablo': [
    { model: 'diablo', label: 'ATTIRE 1 · FANTASY DEMON' },
    { model: 'diablo-attire2', label: 'ATTIRE 2 · DEVIL GOD' },
  ],
  /* KRONOS's ladder (fighter-completeness audit 2026-10-21): Attires 2
     "Timberwolf" and 3 "TimberWolf Fully Suited" keys + GLBs existed
     (roster/kronos/ATTIRE-SLOTS.md marks them wired) but no variant list
     reached them. First entry stays the current default. */
  'kronos': [
    { model: 'kronos', label: 'ATTIRE 1' },
    { model: 'kronos-attire2', label: 'ATTIRE 2 · TIMBERWOLF' },
    { model: 'kronos-attire3', label: 'ATTIRE 3 · TIMBERWOLF FULLY SUITED' },
  ],
  /* AWA POP's ladder (fighter-completeness audit 2026-10-21): Attire 2's
     GLB sat in roster/awa-pop/attires/attire2/ with no MODEL_URLS key and
     no variant list. Key added in assets.js. First entry = current default. */
  'awa-pop': [
    { model: 'awa-pop', label: 'ATTIRE 1' },
    { model: 'awa-pop-attire2', label: 'ATTIRE 2' },
  ],
  'pantera': [
    { model: 'pantera', label: 'ATTIRE 1' },
    { model: 'pantera-leoman', label: 'ATTIRE 2 · LEO MAN' },
  ],
  /* ZUI's ladder (model-key audit follow-up, 2026-10-21): A1 = Drunken Monk
     Tripo (DEFAULT), A2 = Rework v2 Tripo; the steve-fox canon base and the
     T7 Steve reskins (zui_alt1/zui_alt2) ladder back as alternates. Keyed by
     fighter id — his roster model is 'zui-attire1', so attiresFor's id
     fallback is what finds this list (same pattern as Kevin's entry above). */
  'zui': [
    { model: 'zui-attire1', label: 'ATTIRE 1 · DRUNKEN MONK (TRIPO)' },
    { model: 'zui-attire2', label: 'ATTIRE 2 · REWORK V2' },
    { model: 'steve-fox', label: 'BASE · STEVE FOX (CANON)' },
    { model: 'zui_alt1', label: 'ALT 1 · T7 STEVE RESKIN' },
    { model: 'zui_alt2', label: 'ALT 2 · T7 STEVE RESKIN' },
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

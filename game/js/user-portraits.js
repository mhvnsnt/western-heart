/* ============================================================
   WESTERN HEART — User portraits (on-device select-screen cards)

   Portraits the player takes in the Creation Suite's POSE & PICTURE
   tab live on THIS device only, in localStorage, and override the
   repo card (game/assets/portraits/<id>.png) on the character
   select screen and the versus plates. Nothing is uploaded: clear
   the stored portrait and the repo card is back.

   STORAGE CONTRACT (the Creation Suite writes the same keys — it
   imports savePortrait from this module, so there is one writer
   implementation and one key scheme):

     key   = "wh.portrait." + <fighterId> + "." + <attireId>
     value = a PNG data URL ("data:image/png;base64,...")

     fighterId : the roster id ("pantera"), or "custom-<slug>" for a
                 suite-created fighter.
     attireId  : "attire1" .. "attire4" — normalizeAttireId() maps
                 1 -> "attire1", "Attire 2" -> "attire2", and an
                 omitted attire -> "attire1" (the default card).

   All reads go through the global localStorage at call time, so the
   module works in the game page, the suite page (same origin on the
   live build) and the node test harness with a stubbed store.
   ============================================================ */

export const USER_PORTRAIT_PREFIX = 'wh.portrait.';
export const DEFAULT_ATTIRE_ID = 'attire1';

/** Normalize an attire reference to the canonical "attireN" id. */
export function normalizeAttireId(attireId) {
  if (attireId == null || attireId === '') return DEFAULT_ATTIRE_ID;
  if (typeof attireId === 'number' && Number.isFinite(attireId)) return 'attire' + Math.max(1, Math.trunc(attireId));
  const s = String(attireId).trim().toLowerCase().replace(/\s+/g, '');
  if (/^attire\d+$/.test(s)) return s;
  if (/^\d+$/.test(s)) return 'attire' + s;
  return s; // named attire slots (e.g. "leomon") keep their own id
}

/** The localStorage key for one fighter + attire portrait. */
export function portraitKey(fighterId, attireId) {
  return USER_PORTRAIT_PREFIX + String(fighterId) + '.' + normalizeAttireId(attireId);
}

function store() {
  try { return globalThis.localStorage || null; } catch { return null; }
}

function isPortraitDataUrl(v) {
  return typeof v === 'string' && /^data:image\/(png|jpeg|webp);base64,/.test(v);
}

/**
 * Save a portrait taken in the suite. Returns true on success,
 * false when storage is unavailable, full, or the value is not an
 * image data URL (a rejected save never clobbers an existing card).
 */
export function savePortrait(fighterId, attireId, dataUrl) {
  const ls = store();
  if (!ls || !fighterId || !isPortraitDataUrl(dataUrl)) return false;
  try { ls.setItem(portraitKey(fighterId, attireId), dataUrl); return true; }
  catch { return false; } // quota exceeded / private mode: the repo card stays
}

/** The stored portrait data URL for a fighter + attire, or null. */
export function getPortrait(fighterId, attireId) {
  const ls = store();
  if (!ls || !fighterId) return null;
  try {
    const v = ls.getItem(portraitKey(fighterId, attireId));
    return isPortraitDataUrl(v) ? v : null;
  } catch { return null; }
}

export function hasPortrait(fighterId, attireId) {
  return getPortrait(fighterId, attireId) !== null;
}

/** Remove a stored portrait (the repo card shows again). Returns true if one existed. */
export function clearPortrait(fighterId, attireId) {
  const ls = store();
  if (!ls || !fighterId) return false;
  const k = portraitKey(fighterId, attireId);
  let had = false;
  try { had = ls.getItem(k) !== null; ls.removeItem(k); } catch { return false; }
  return had;
}

/**
 * The src a portrait <img> should use: the on-device portrait when
 * one is stored, otherwise the given fallback (the repo card path).
 * This is the one call the select screen and versus plates make.
 */
export function portraitSrcFor(fighterId, attireId, fallbackSrc) {
  return getPortrait(fighterId, attireId) || fallbackSrc;
}

/** Every stored user portrait: [{ fighterId, attireId, key }] (foreign keys ignored). */
export function listPortraits() {
  const ls = store();
  const out = [];
  if (!ls) return out;
  try {
    for (let i = 0; i < ls.length; i++) {
      const k = ls.key(i);
      if (!k || !k.startsWith(USER_PORTRAIT_PREFIX)) continue;
      const rest = k.slice(USER_PORTRAIT_PREFIX.length);
      const dot = rest.lastIndexOf('.');
      if (dot <= 0) continue;
      out.push({ fighterId: rest.slice(0, dot), attireId: rest.slice(dot + 1), key: k });
    }
  } catch { /* store not enumerable here: no portraits to list */ }
  return out;
}

export default {
  USER_PORTRAIT_PREFIX, DEFAULT_ATTIRE_ID,
  normalizeAttireId, portraitKey,
  savePortrait, getPortrait, hasPortrait, clearPortrait,
  portraitSrcFor, listPortraits,
};

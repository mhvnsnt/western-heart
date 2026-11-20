/* ============================================================
   WESTERN HEART — Unlockables (reward hooks)

   Minimal unlockable registry that daily challenges pay out into.
   This is the hook surface; the full catalog (attires, arenas,
   palettes) drops in later without changing this API.

   Kinds (v1):
     title -- lobby/menu nameplate titles ("WAR GOD")
     frame -- portrait frame flourishes (ember/flame/inferno...)

   Storage: localStorage 'wh_unlocks_v1' = { unlocked: {id: timestamp} }.
   DOM-free except for the optional toast hook (wired by online.js).
   ============================================================ */

export const UNLOCKABLES = {
  // titles
  title_firstblood: { kind: 'title', name: 'FIRST BLOOD' },
  title_grappler:   { kind: 'title', name: 'GRAPPLER' },
  title_surged:     { kind: 'title', name: 'SURGED' },
  title_survivor:   { kind: 'title', name: 'SURVIVOR' },
  title_suneater:   { kind: 'title', name: 'SUN EATER' },
  title_stormfist:  { kind: 'title', name: 'STORMFIST' },
  title_relentless: { kind: 'title', name: 'RELENTLESS' },
  title_noshield:   { kind: 'title', name: 'NO SHIELD' },
  title_channeler:  { kind: 'title', name: 'CHANNELER' },
  title_waverider:  { kind: 'title', name: 'WAVE RIDER' },
  title_swift:      { kind: 'title', name: 'SWIFT' },
  title_ladder:     { kind: 'title', name: 'LADDER CLIMBER' },
  title_untouched:  { kind: 'title', name: 'UNTOUCHED' },
  title_fleshy:     { kind: 'title', name: 'FLESH IS ARMOR' },
  title_immortal:   { kind: 'title', name: 'IMMORTAL' },
  title_ninesouls:  { kind: 'title', name: 'NINE SOULS' },
  title_suneater2:  { kind: 'title', name: 'SUN DEVOURER' },
  title_pantera:    { kind: 'title', name: "KING'S TRIBUTE" },
  title_torch:      { kind: 'title', name: 'TRIAL BY FIRE' },
  title_dorowani:   { kind: 'title', name: 'MUD AMBUSH' },
  // frames
  frame_ember:     { kind: 'frame', name: 'Ember Frame' },
  frame_flame:     { kind: 'frame', name: 'Flame Frame' },
  frame_grapple:   { kind: 'frame', name: 'Grapple Frame' },
  frame_inferno:   { kind: 'frame', name: 'Inferno Frame' },
  frame_lightning: { kind: 'frame', name: 'Lightning Frame' },
};

const STORE_KEY = 'wh_unlocks_v1';

function loadStore() {
  try { return JSON.parse(localStorage.getItem(STORE_KEY)) || { unlocked: {} }; }
  catch { return { unlocked: {} }; }
}
function saveStore(s) {
  try { localStorage.setItem(STORE_KEY, JSON.stringify(s)); } catch { /* private mode */ }
}

/** Grant an unlockable. Returns true if newly unlocked. */
export function grantUnlockable(id) {
  const def = UNLOCKABLES[id];
  if (!def) return false;
  const s = loadStore();
  if (s.unlocked[id]) return false;
  s.unlocked[id] = Date.now();
  saveStore(s);
  _notify(def);
  return true;
}

export function hasUnlockable(id) {
  return !!loadStore().unlocked[id];
}

/** All unlocked, newest first: [{ id, kind, name, at }]. */
export function unlockedList() {
  const s = loadStore();
  return Object.entries(s.unlocked)
    .map(([id, at]) => ({ id, at, ...(UNLOCKABLES[id] || { kind: '?', name: id }) }))
    .sort((a, b) => b.at - a.at);
}

/** Titles the player can equip on their lobby nameplate. */
export function unlockedTitles() {
  return unlockedList().filter((u) => u.kind === 'title');
}

/* Active title (nameplate). */
const TITLE_KEY = 'wh_active_title';
export function activeTitle() {
  try { return localStorage.getItem(TITLE_KEY) || null; } catch { return null; }
}
export function setActiveTitle(id) {
  if (id && !hasUnlockable(id)) return false;
  try {
    if (id) localStorage.setItem(TITLE_KEY, id);
    else localStorage.removeItem(TITLE_KEY);
  } catch { /* private mode */ }
  return true;
}

/* ---- reward hook: UI toast on unlock (online.js registers the renderer) ---- */
let _onUnlock = null;
export function onUnlock(fn) { _onUnlock = fn; }
function _notify(def) {
  try { _onUnlock && _onUnlock(def); } catch (e) { console.error(e); }
}

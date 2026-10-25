/* ============================================================
   WESTERN HEART — shared tissue quality store

   One quality setting for every soft-body backend (Jolt XPBD in
   game/js/softbody.js, MPM-lite in game/js/mpm-tissue.js, FEMFX in
   game/js/femfx-adapter.js): 'off' | 'low' | 'high', persisted in
   localStorage `wh_softbody_v1`.

   NEXTGEN-2026-10-23: previously each backend kept its own module-level
   quality variable, so changing quality through one backend's setter was
   invisible to the others mid-session (and to the X-ray gate, which reads
   SoftBody.globalQuality). Now all backends delegate here; a change via
   ANY backend's setGlobalQuality updates every live instance of every
   backend through the listener fan-out below.

   Dependency-free: no three.js, no WASM, no DOM. Safe to import from the
   zero-boot-cost physics modules and from node tests.
   ============================================================ */

const QUALITIES = ['off', 'low', 'high'];
const STORE = 'wh_softbody_v1';

let _quality = 'low'; // conservative default
try {
  const saved = (typeof localStorage !== 'undefined') && localStorage.getItem(STORE);
  if (QUALITIES.indexOf(saved) >= 0) _quality = saved;
} catch (e) { /* private mode / node: keep default */ }

const _listeners = (typeof Set !== 'undefined') ? new Set() : { add() {}, forEach() {} };

export function getTissueQuality() { return _quality; }

export function setTissueQuality(q) {
  if (QUALITIES.indexOf(q) < 0 || q === _quality) return false;
  _quality = q;
  try {
    if (typeof localStorage !== 'undefined') localStorage.setItem(STORE, q);
  } catch (e) {}
  _listeners.forEach((fn) => { try { fn(q); } catch (e) {} });
  return true;
}

// Backends register one module-level listener that fans out to their
// live instances (e.g. SoftBody.setQuality / MpmTissue.setQuality).
export function onTissueQuality(fn) {
  _listeners.add(fn);
  return () => { try { _listeners.delete(fn); } catch (e) {} };
}

export const TISSUE_QUALITIES = QUALITIES;
export const TISSUE_QUALITY_STORE = STORE;

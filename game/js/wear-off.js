/* ============================================================
   WESTERN HEART — decal wear-off (tattoos / scars / face paint)
   (2026-11-02, scars + tattoos + face-paint lane)

   WHAT THE LEGACY DATA ACTUALLY SHOWS (do not over-claim):
   - Western Heart's legacy wrestling teardown data holds NO scar-labeled asset
     and NO wear-off mechanism. Legacy face overlays (Face_op, 208
     files) are static layered textures — masks, face-paint patterns
     and facial marks — and legacy MAKE_UP (64gara, ty2_*) are static
     logo/tattoo decals. A legacy title's 597 DDS textures are hash-named
     with no scar/face-paint labels. Nothing in the repo data fades,
     rubs off, or wears away during a match.
   - So wear-off here is a NEW Western Heart system, modeled on the
     layered-decal idea the data does show (a decal layer on top of
     a base face/body texture, with an editable opacity — the
     catalog's tattoo entries already list "opacity" as editable),
     NOT a copied legacy feature. The rates below are WH design
     defaults, chosen so the three kinds behave differently:
     face paint sits ON the skin and disappears; tattoos and scars
     are IN the skin and only fade to a floor, never vanish.

   DESIGN (pure logic, no THREE import at module top level, so
   Node tests can import it directly — same pattern as
   game/js/frame-step.js and game/js/fx/decals.js):
   - A layer is { id, kind, zone, opacity }.
     kind: 'facepaint' | 'tattoo' | 'scar'
     zone: 'face' | 'upper' | 'lower' | 'any'
   - applyHit(layer, { zone, strength=1 }): only a hit to the
     layer's zone (or an 'any' zone on either side) wears it.
   - applyTime(layer, minutes, sweat=0): sweat is 0..1; it speeds
     face-paint wear only (tattoos/scars do not sweat off).
   - Floors: facepaint 0 (gone), tattoo 0.55 (faded, never gone),
     scar 0.85 (barely fades — a scar is not paint).
   - setMaterialOpacity(material, opacity): the THREE bridge.
     Sets transparent=true, opacity, needsUpdate=true. Returns
     false (and touches nothing) for a material without an
     opacity property, so a bad call never breaks a fight.
   ============================================================ */

export const WEAR_FLOORS = Object.freeze({
  facepaint: 0,
  tattoo: 0.55,
  scar: 0.85,
});

/* Per-hit wear (at strength 1) and per-minute time wear. */
export const WEAR_RATES = Object.freeze({
  facepaint: Object.freeze({ hit: 0.20, time: 0.10, sweat: 0.10 }),
  tattoo: Object.freeze({ hit: 0.05, time: 0.01, sweat: 0 }),
  scar: Object.freeze({ hit: 0.01, time: 0, sweat: 0 }),
});

const clamp01 = (v) => Math.min(1, Math.max(0, v));

export function createLayer({ id, kind, zone = 'any', opacity = 1 } = {}) {
  if (!WEAR_RATES[kind]) throw new Error(`wear-off: unknown kind "${kind}"`);
  if (!id) throw new Error('wear-off: layer needs an id');
  return { id, kind, zone, opacity: clamp01(opacity) };
}

function zoneMatches(layerZone, hitZone) {
  if (!hitZone || hitZone === 'any' || layerZone === 'any') return true;
  return layerZone === hitZone;
}

function wear(layer, amount) {
  const floor = WEAR_FLOORS[layer.kind];
  layer.opacity = Math.max(floor, clamp01(layer.opacity - amount));
  return layer.opacity;
}

export function applyHit(layer, { zone, strength = 1 } = {}) {
  if (!zoneMatches(layer.zone, zone)) return layer.opacity;
  return wear(layer, WEAR_RATES[layer.kind].hit * Math.max(0, strength));
}

export function applyTime(layer, minutes = 0, sweat = 0) {
  const r = WEAR_RATES[layer.kind];
  const s = clamp01(sweat);
  return wear(layer, (r.time + r.sweat * s) * Math.max(0, minutes));
}

export function isGone(layer) {
  return layer.opacity <= 0;
}

export function setMaterialOpacity(material, opacity) {
  if (!material || typeof material.opacity !== 'number') return false;
  material.opacity = clamp01(opacity);
  material.transparent = true;
  material.needsUpdate = true;
  return true;
}

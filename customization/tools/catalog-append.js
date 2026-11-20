
/* ---- Universal parts registry wiring (2026-10-18) ----
   The new universal libraries (eye-library, decal-library/pantera,
   parts/pantera-eyes, parts/superhero) are wired into the suite via
   customization/PARTS-REGISTRY.json (see packages/creation-suite/src/parts.js).
   Their entries land in the parts index under the slots below, so the
   existing Catalog picks them up untouched — this only ADDS categories.
   Eye/decal texture swaps are universal (character_mappings); superhero mesh
   pieces attach at bone sockets on any character. */
export const UNIVERSAL_CATEGORIES = [
  { key:'eyes',   icon:'👁️', label:'Eyes',           slotId:'eyes',   anchor:'Head' },
  { key:'decals', icon:'🏷️', label:'Decals & Logos', slotId:'decals', anchor:'Hips' },
  { key:'masks',  icon:'🎭', label:'Masks & Pieces', slotId:'masks',  anchor:'Head' },
];
// Merged view: teardown-index categories + universal-library categories.
export const ALL_CATEGORIES = [...CATEGORIES, ...UNIVERSAL_CATEGORIES];

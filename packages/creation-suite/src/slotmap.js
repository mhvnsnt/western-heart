// slotmap.js — Tekken-spine classification for Creation Suite catalogs.
//
// Phase 1 (catalogs.js) merges every source catalog into one entry list, but
// most entries carry only a SOURCE slot (WMXIX "UPPER", No Mercy "skins",
// Def Jam "upper_body") and no suite_slot — a slot-keyed UI would see almost
// nothing. This module maps every merged entry onto the Tekken slot spine
// (docs/CREATION-SUITE-UI-SCHEMA-2026-10-21.md §1.2/§1.6/§5) deterministically
// and grades its readiness from the entry's own data. catalogs.js is NOT
// modified; this is an additive layer over it.
//
// An entry is never dropped and never guessed into a slot the data does not
// support: what cannot be classified lands in the explicit UNMAPPED bucket.

// The spine: Tekken 7 slot IDs in SlotGroupID menu order (REPORT.md §2),
// with the Tekken 6 sub-slots restored (extraction log §2) and the two
// Western Heart extensions (eyes = placeable mesh parts, ink = decal layers).
export const SPINE = [
  { id: 'head',       t7: 1,    title: 'Head',           group: -254 },
  { id: 'hair',       t7: 2,    title: 'Hairstyle',      group: -253 },
  { id: 'full_head',  t7: 3,    title: 'Full Head',      group: -252 },
  { id: 'hair_acc',   t7: 4,    title: 'Hair Accessory', group: -251 },
  { id: 'gla',        t7: 5,    title: 'Glasses',        group: -250 },
  { id: 'face',       t7: 6,    title: 'Face',           group: -249 },
  { id: 'face_hair',  t7: 7,    title: 'Facial Hair',    group: -248 },
  { id: 'eyes',       t7: null, title: 'Eyes (mesh parts)', group: -248, wh: 'D5' },
  { id: 'make_up',    t7: 8,    title: 'Face Paint',     group: -247 },
  { id: 'upper',      t7: 9,    title: 'Upper Body',     group: -246 },
  { id: 'upper_inner', t7: '9a', title: 'Upper · Inner (T6)', group: -246 },
  { id: 'upper_outer', t7: '9b', title: 'Upper · Outer (T6)', group: -246 },
  { id: 'full_body',  t7: 10,   title: 'Full Body',      group: -245 },
  { id: 'lower',      t7: 11,   title: 'Lower Body',     group: -244 },
  { id: 'hands',      t7: 'H',  title: 'Hands (T6)',     group: -244 },
  { id: 'feet',       t7: 'F',  title: 'Feet (T6)',      group: -244 },
  { id: 'upper_acc',  t7: 12,   title: 'Upper Accessory', group: -243 },
  { id: 'lower_acc',  t7: 13,   title: 'Lower Accessory', group: -242 },
  { id: 'waist',      t7: 'WL/R', title: 'Waist L/R (T6)', group: -242 },
  { id: 'extra',      t7: 14,   title: 'Extra',          group: -241 },
  { id: 'effect',     t7: 15,   title: 'Effects',        group: -240 },
  { id: 'aura',       t7: 17,   title: 'Aura',           group: -238 },
  { id: 'ink',        t7: null, title: 'Tattoos / Images (layers)', group: -237, wh: 'D6' },
];
export const SPINE_BY_ID = Object.fromEntries(SPINE.map((s) => [s.id, s]));
export const UNMAPPED = 'unmapped';

// suite_slot values (registry / No Mercy catalog vocabulary) -> spine id.
const BY_SUITE_SLOT = {
  head: 'head', hair: 'hair', full_head: 'full_head', hair_acc: 'hair_acc',
  gla: 'gla', glasses: 'gla', eye_lenses: 'gla', face: 'face',
  face_hair: 'face_hair', eye: 'eyes', eyes: 'eyes', mask: 'full_head',
  cowl: 'head', make_up: 'make_up', upper_body: 'upper', top: 'upper',
  full_body: 'full_body', attire: 'full_body', outfit: 'full_body',
  lower_body: 'lower', tights: 'lower', pants: 'lower', gloves: 'hands',
  gauntlets: 'hands', shoes: 'feet', accessory: 'upper_acc', gear: 'extra',
  scarf: 'extra', effect: 'effect', aura: 'aura', decal_logo: 'ink',
  decal: 'ink',
  // Spine ids are valid suite_slot keys too (the UI equips by spine slot;
  // entries without a source suite_slot are keyed by their spine id).
  upper: 'upper', lower: 'lower', hands: 'hands', feet: 'feet',
  extra: 'extra', upper_acc: 'upper_acc', lower_acc: 'lower_acc',
  waist: 'waist', ink: 'ink', eyes: 'eyes', upper_inner: 'upper_inner',
  upper_outer: 'upper_outer',
};
// Tekken slot titles (converted catalogs already speak these) -> spine id.
const BY_T7_TITLE = {
  HEAD: 'head', HAIR: 'hair', FULL_HEAD: 'full_head', HAIR_ACC: 'hair_acc',
  GLA: 'gla', FACE: 'face', FACE_HAIR: 'face_hair', MAKE_UP: 'make_up',
  UPPER: 'upper', FULL_BODY: 'full_body', LOWER: 'lower',
  UPPER_ACC: 'upper_acc', LOWER_ACC: 'lower_acc', EXTRA: 'extra',
  EFFECT: 'effect', AURA: 'aura',
};

// Source taxonomies -> spine id. Keyed `${source}:${slot-or-category}`.
const BY_SOURCE = {
  // No Mercy catalog slots
  'no-mercy:skins': 'full_body', 'no-mercy:bodies': 'full_body',
  'no-mercy:faces': 'face', 'no-mercy:accessories': 'extra',
  'no-mercy:attire': 'full_body',
  // Def Jam census slots (converted catalog)
  'defjam:head': 'head', 'defjam:upper_body': 'upper',
  'defjam:lower_body': 'lower', 'defjam:accessories': 'upper_acc',
  // WMXIX categories (converted catalog) refine its Tekken-title slots
  'wmxix:gears': 'extra', 'wmxix:weapon': 'extra', 'wmxix:shoes': 'feet',
  'wmxix:gloves': 'hands', 'wmxix:skins': 'full_body',
  'wmxix:body_parts': 'full_body', 'wmxix:faces': 'face',
  'wmxix:accessories': 'upper_acc', 'wmxix:textures': 'make_up',
};

// kind fallback (registry vocabulary)
const BY_KIND = {
  eye: 'eyes', decal_logo: 'ink', skin_texture: 'full_body',
  body_mesh: 'full_body', face_texture: 'face', face_mesh: 'face',
  hair: 'hair', mask: 'full_head', cowl: 'head', eye_lenses: 'gla',
  full_reskin: 'full_body', tights: 'lower', pants: 'lower', top: 'upper',
  gauntlets: 'hands', scarf: 'extra',
};

export function spineSlotOf(entry) {
  if (!entry) return UNMAPPED;
  if (entry.suite_slot && BY_SUITE_SLOT[entry.suite_slot]) return BY_SUITE_SLOT[entry.suite_slot];
  const slot = entry.slot || '';
  if (BY_T7_TITLE[slot]) {
    // WMXIX category refines the title (shoes/gloves/gears live inside
    // LOWER_ACC / UPPER_ACC / EXTRA titles in the converted catalog).
    const refined = BY_SOURCE[`wmxix:${entry.category}`];
    if (refined && entry.source_game === 'wmxix') return refined;
    return BY_T7_TITLE[slot];
  }
  const src = entry.source_game || entry.library || '';
  if (BY_SOURCE[`${src}:${slot}`]) return BY_SOURCE[`${src}:${slot}`];
  if (BY_SOURCE[`${src}:${entry.category}`]) return BY_SOURCE[`${src}:${entry.category}`];
  if (entry.kind && BY_KIND[entry.kind]) return BY_KIND[entry.kind];
  return UNMAPPED;
}

// Readiness, from the entry's own data only (schema doc §5). Blocked
// statuses are the converters' own stamps; POINTS pools are Def Jam's
// unproven-vertex-order conversions (#411) — preview data, not meshes.
const BLOCKED = new Set([
  'blocked_ymg_decode', 'blocked_dumy_placeholder', 'no_valid_refpack_record',
  'compiled_variant', 'pose_palette_only', 'not_converted', 'palette_only',
]);
const GLB_RE = /\.gl(b|tf)$/i, IMG_RE = /\.(png|jpe?g|webp)$/i;
export function readinessOf(entry) {
  const status = entry.status || entry.conversion?.status || '';
  if (BLOCKED.has(status)) return 'blocked';
  if (entry.conversion?.status === 'failed' || status === 'failed') return 'blocked';
  // A GLB path in any of the asset fields wins — even over a stale
  // geometryPending stamp (the registry's index-derived twin of the
  // spidergirl eye lenses carries one, contradicted by the real GLB on disk).
  const glbPath = entry.glb
    || (GLB_RE.test(entry.asset || '') ? entry.asset : null)
    || (GLB_RE.test(entry.file || '') ? entry.file : null);
  if (glbPath) return entry.glb_primitive === 'POINTS' ? 'preview-only' : 'ready-mesh';
  if (entry.texture || entry.image) return 'ready-texture';
  if (IMG_RE.test(entry.asset || '') || IMG_RE.test(entry.file || '')) return 'ready-texture';
  // No usable asset on disk: geometry-pending binaries (.ymg & friends)
  // are blocked, not record-only — they are the same blocked population
  // the converted catalog stamps explicitly.
  if (entry.geometryPending) return 'blocked';
  if (entry.part_class === 'mesh_part') return 'blocked'; // claims mesh, no GLB on disk
  if (entry.part_class === 'texture_part' || status === 'texture_part') return 'ready-texture';
  return 'record-only';
}
export const EQUIPPABLE = new Set(['ready-mesh', 'ready-texture']);
export function isEquippable(entry) { return EQUIPPABLE.has(readinessOf(entry)); }

// Counts the UI header and the schema doc report: per-spine-slot totals by
// readiness, the unmapped bucket, and the grand totals.
export function spineCounts(entries) {
  const per = {};
  for (const s of SPINE) per[s.id] = { total: 0, ready: 0, preview: 0, blocked: 0, record: 0 };
  const out = { total: entries.length, mapped: 0, unmapped: 0, ready: 0, preview: 0, blocked: 0, record: 0, per };
  for (const e of entries) {
    const slot = spineSlotOf(e), r = readinessOf(e);
    const bucket = r === 'ready-mesh' || r === 'ready-texture' ? 'ready' : r === 'preview-only' ? 'preview' : r;
    out[bucket === 'record-only' ? 'record' : bucket]++;
    if (slot === UNMAPPED) { out.unmapped++; continue; }
    out.mapped++;
    per[slot].total++;
    per[slot][bucket === 'record-only' ? 'record' : bucket]++;
  }
  return out;
}

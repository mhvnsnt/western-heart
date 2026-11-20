// t7layout.js — Tekken 7 customization STRUCTURE (no game data).
//
// Derived by tools/extract/t7/t7_customize.py from the owner's Steam copy
// (customize_item_data.bin, 23,548 item records). Every slot code below is
// named from the mesh-name token its records carry in that file, with the
// record count as evidence; the raw tables themselves live only in the
// private repo (game-reverse-engineering tekken7/customization/).
//
// The codes line up 1:1 with slotmap.js SPINE.t7 (written earlier from the
// UI SlotGroupID research), so this file also proves that spine against
// real item data.

export const T7_SLOTS = [
  // code, mesh token, spine id, records in customize_item_data.bin
  { code: 1,  token: 'hed',  spine: 'head',      records: 1260 },
  { code: 2,  token: 'har',  spine: 'hair',      records: 883 },
  { code: 3,  token: 'hef',  spine: 'full_head', records: 514 },
  { code: 4,  token: 'oph',  spine: 'hair_acc',  records: 2200 },
  { code: 5,  token: 'gla',  spine: 'gla',       records: 1660 },
  { code: 6,  token: 'fac',  spine: 'face',      records: 58 },
  { code: 7,  token: 'fah',  spine: 'face_hair', records: 85 },
  { code: 8,  token: 'fam',  spine: 'make_up',   records: 459 },
  { code: 9,  token: 'bdu',  spine: 'upper',     records: 2103 },
  { code: 10, token: 'bdf',  spine: 'full_body', records: 311 },
  { code: 11, token: 'bdl',  spine: 'lower',     records: 1150 },
  { code: 12, token: 'opu',  spine: 'upper_acc', records: 4984 },
  { code: 13, token: 'opl',  spine: 'lower_acc', records: 1487 },
  { code: 14, token: 'exp',  spine: 'extra',     records: 10 },
  { code: 15, token: 'unique', spine: 'effect',  records: 3534 },
  { code: 17, token: 'aura', spine: 'aura',      records: 2652 },
  // Present in the data, not in the slot spine yet: body-wide toggles.
  { code: 18, token: 'suntan', spine: 'skin_tone', records: 44 },
  { code: 19, token: 'mirror', spine: 'mirror',    records: 52 },
];
export const T7_SLOT_BY_CODE = Object.fromEntries(T7_SLOTS.map((s) => [s.code, s]));
export const T7_SLOT_BY_TOKEN = Object.fromEntries(T7_SLOTS.map((s) => [s.token, s]));

// Menu flow, top to bottom, as T7's customize mode walks it:
// character -> preset/attire slot -> body region tab -> item slot ->
// item list -> colour layers -> pattern/position -> equip (replace/cancel).
export const T7_REGION_TABS = [
  { id: 'head',  title: 'Head',       codes: [1, 2, 3, 4, 5, 6, 7, 8] },
  { id: 'upper', title: 'Upper Body', codes: [9, 10, 12] },
  { id: 'lower', title: 'Lower Body', codes: [11, 13] },
  { id: 'body',  title: 'Body',       codes: [18, 19] },
  { id: 'fx',    title: 'Effects',    codes: [14, 15, 17] },
];
export const T7_FLOW = ['fighter', 'attire', 'region', 'slot', 'item', 'color', 'pattern', 'equip'];

// Colour layers: T7 items expose up to 3 colourable regions (base, sub,
// trim), each picked from the 144-swatch palette grid
// (customize_palette_color.bin, 3 bytes/swatch) and clamped by
// customize_color_rules.bin (lo/hi brightness per rule). Pattern sits on
// top as a decal layer (layering.js handles the compositing).
export const T7_COLOR_LAYERS = ['base', 'sub', 'trim'];
export const T7_PALETTE_SIZE = 144;
export const T7_PALETTE_GRID = { cols: 12, rows: 12 };

export function regionTabOf(spineId) {
  const s = T7_SLOTS.find((x) => x.spine === spineId);
  return s ? (T7_REGION_TABS.find((t) => t.codes.includes(s.code)) || null) : null;
}

/** Group catalog entries the way T7's menu does: region tab -> slot -> entries. */
export function groupForMenu(entries, spineOf) {
  const out = T7_REGION_TABS.map((t) => ({ ...t, slots: t.codes.map((c) => ({ ...T7_SLOT_BY_CODE[c], entries: [] })) }));
  for (const e of entries) {
    const sp = spineOf(e); if (!sp) continue;
    for (const t of out) for (const s of t.slots) if (s.spine === sp) s.entries.push(e);
  }
  return out;
}

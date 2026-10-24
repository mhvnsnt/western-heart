// profile.js — Creation Suite profile state (pure, no DOM).
//
// One state object -> two serializations that can never drift:
//   toCustomizationJson()  the per-attire customization.json v1 (bake truth)
//   toSuiteRecord()        the localStorage "wh_creation_suite_v1" record the
//                          game consumer (game/js/custom-fighter.js) reads
// Both carry the v1 fields; the suite record adds the consumer's
// profile/parameters/fighting_style blocks, and the v1 JSON carries the
// additive extension keys (docs/CREATION-SUITE-UI-SCHEMA-2026-10-21.md §7).
//
// Equips are keyed by Tekken spine slot (src/slotmap.js). Conflicts follow
// Tekken's own rules (REPORT.md): FULL_HEAD excludes HEAD/HAIR/FACE/
// HAIR_ACC/GLA/FACE_HAIR (+ Face Paint per UNIFIED-UI-SPEC §7); FULL_BODY
// excludes UPPER (incl. T6 sub-slots) and LOWER. A conflicting equip does
// NOT apply until the caller re-issues it with { force: true } — the UI
// shows Tekken's Replace / Cancel sheet in between.
import { BODY_MORPHS, FACE_SHAPE_MORPHS } from '../src/morphs.js';

const MORPH_BY_ID = Object.fromEntries(
  [...BODY_MORPHS, ...FACE_SHAPE_MORPHS].map((m) => [m.id, m]),
);

// The 16 body-type labels the game consumer reads (game/js/custom-fighter.js
// BODY_TYPES — order and spelling are the consumer's contract).
export const BODY_TYPE_NAMES = [
  'Skinny 1', 'Skinny 2', 'Medium 1', 'Medium 2', 'Thick 1', 'Thick 2',
  'Fat 1', 'Fat 2', 'Austin', 'HBK', 'Rikishi', 'Rock', 'Hairy 1', 'Hairy 2',
  'King Frame', 'Ganryu Frame',
];
// Suite skin-tone swatches (the profile stores a hex either way; the row
// includes the consumer default #c98d5e and the canon #e5b28c).
export const SKIN_TONES = ['#f6d7b8', '#eec39b', '#e5b28c', '#c98d5e', '#a06a3f', '#7c4b28', '#5a341c', '#3d2314'];
export const ARCHETYPES = ['Balanced', 'Striker', 'Grappler', 'Powerhouse', 'Speedster', 'Technical', 'Brawler', 'All-Rounder'];

export const SPINE_CONFLICTS = {
  full_head: ['head', 'hair', 'face', 'hair_acc', 'gla', 'face_hair', 'make_up'],
  full_body: ['upper', 'upper_inner', 'upper_outer', 'lower'],
  upper: ['full_body'], upper_inner: ['full_body'], upper_outer: ['full_body'],
  lower: ['full_body'],
  head: ['full_head'], hair: ['full_head'], face: ['full_head'],
  hair_acc: ['full_head'], gla: ['full_head'], face_hair: ['full_head'],
  make_up: ['full_head'],
};

const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, Number(v) || 0));
const HEX = /^#[0-9a-fA-F]{6}$/;
const clone = (o) => JSON.parse(JSON.stringify(o));

export function createState({ fighter = 'custom', attire = 'attire1', name = 'CUSTOM', base_glb = null } = {}) {
  return {
    fighter, attire, name, base_glb,
    body: { body_type: 'Medium 1', skin_tone: '#c98d5e' },
    morphs: {},                       // morphs.js id -> -1..1 (absent = neutral)
    equipped: {},                     // spine id -> { part_id, suite_slot, glb, name, source, placement }
    textures: [],                     // v1 texture layers (eyes/decals/hair)
    colors: {},                       // { hair?, skin? } hex
    item_colors: {},                  // suite_slot -> [hex, ...<=5]
    finishes: {},                     // suite_slot -> { roughness, metalness, tint }
    mirrored: {},                     // suite_slot -> true
    title: ['', ''],
    fighting_style: { archetype: 'Balanced', aggression: 5 },
    parameters: { arms_offense: 50, body_defense: 50 },
    wardrobe: {},                     // "1".."10" -> snapshot
  };
}

export function setBodyType(s, label) {
  if (!BODY_TYPE_NAMES.includes(label)) throw new Error(`unknown body type ${label}`);
  s.body.body_type = label; return s;
}
export function setSkinTone(s, hex) {
  if (!HEX.test(hex)) throw new Error(`bad hex ${hex}`);
  s.body.skin_tone = hex; s.colors.skin = hex; return s;
}
export function setColor(s, which, hex) {
  if (!HEX.test(hex)) throw new Error(`bad hex ${hex}`);
  s.colors[which] = hex; if (which === 'skin') s.body.skin_tone = hex; return s;
}
export function setMorph(s, id, v) {
  const def = MORPH_BY_ID[id];
  if (!def) throw new Error(`unknown morph ${id}`);
  const [lo, hi] = def.range;
  const val = clamp(v, lo, hi);
  if (val === 0) delete s.morphs[id]; else s.morphs[id] = val;
  return s;
}

function defaultPlacement(entry) {
  const p = entry.placement || {};
  if ('px' in p || 'py' in p || 'pz' in p) {
    return { px: p.px || 0, py: p.py || 0, pz: p.pz || 0, rx: p.rx || 0, ry: p.ry || 0, rz: p.rz || 0, s: p.s ?? 1 };
  }
  const o = entry.offset || [0, 0, 0], r = entry.rotation || [0, 0, 0];
  return { px: o[0] || 0, py: o[1] || 0, pz: o[2] || 0, rx: r[0] || 0, ry: r[1] || 0, rz: r[2] || 0, s: entry.scale ?? 1 };
}

// Equip a catalog entry at a spine slot. Returns { ok: true, removed: [...] }
// or { ok: false, conflicts: [{ spine, part_id, name }] } without applying.
export function equip(s, entry, spine, { force = false } = {}) {
  const victims = [];
  for (const bad of SPINE_CONFLICTS[spine] || []) {
    if (s.equipped[bad] && bad !== spine) victims.push({ spine: bad, ...s.equipped[bad] });
  }
  if (victims.length && !force) return { ok: false, conflicts: victims };
  for (const v of victims) delete s.equipped[v.spine];
  const replaced = s.equipped[spine] || null;
  s.equipped[spine] = {
    part_id: entry.id || entry.part_id,
    suite_slot: entry.suite_slot || spine,
    glb: entry.glb || entry.asset || entry.file || null,
    name: entry.name || entry.id || entry.part_id,
    source: entry.source_game || entry.library || null,
    placement: defaultPlacement(entry),
  };
  return { ok: true, removed: victims, replaced };
}
export function unequip(s, spine) { delete s.equipped[spine]; return s; }

export function setPlacement(s, spine, partial) {
  const cur = s.equipped[spine]; if (!cur) throw new Error(`nothing equipped at ${spine}`);
  const p = { ...cur.placement };
  for (const k of ['px', 'py', 'pz']) if (k in partial) p[k] = clamp(partial[k], -0.5, 0.5);
  for (const k of ['rx', 'ry', 'rz']) if (k in partial) p[k] = clamp(partial[k], -180, 180);
  if ('s' in partial) p.s = clamp(partial.s, 0.25, 2.5);
  cur.placement = p; return s;
}
export function setItemColors(s, spine, colors) {
  const cur = s.equipped[spine]; if (!cur) throw new Error(`nothing equipped at ${spine}`);
  const list = (colors || []).filter((c) => HEX.test(c)).slice(0, 5);
  if (list.length) s.item_colors[cur.suite_slot] = list; else delete s.item_colors[cur.suite_slot];
  return s;
}
export function setFinish(s, spine, finish) {
  const cur = s.equipped[spine]; if (!cur) throw new Error(`nothing equipped at ${spine}`);
  const f = { ...(s.finishes[cur.suite_slot] || {}) };
  if (finish.roughness != null) f.roughness = clamp(finish.roughness, 0, 1);
  if (finish.metalness != null) f.metalness = clamp(finish.metalness, 0, 1);
  if (finish.tint && HEX.test(finish.tint)) f.tint = finish.tint;
  s.finishes[cur.suite_slot] = f; return s;
}
export function setMirrored(s, spine, on) {
  const cur = s.equipped[spine]; if (!cur) throw new Error(`nothing equipped at ${spine}`);
  if (on) s.mirrored[cur.suite_slot] = true; else delete s.mirrored[cur.suite_slot];
  return s;
}

// Tattoo / image layers (v1 textures[]). kind follows the v1 enum.
export function addLayer(s, entry, { rect = null, material = null } = {}) {
  const image = entry.texture || entry.image || entry.asset || entry.file;
  if (!image) throw new Error(`entry ${entry.id} has no image asset`);
  const kind = entry.kind === 'eye' ? 'eye' : entry.kind === 'hair' ? 'hair' : 'decal';
  const layer = { part_id: entry.id || entry.part_id, kind, image };
  if (material) layer.material = material;
  if (rect) layer.rect = rect.map((n) => clamp(n, 0, 1));
  s.textures.push(layer); return layer;
}
export function removeLayer(s, idx) { s.textures.splice(idx, 1); return s; }

// Wardrobe snapshots (DOA model): a snapshot is the whole look minus identity.
function lookOf(s) {
  return clone({
    body: s.body, morphs: s.morphs, equipped: s.equipped, textures: s.textures,
    colors: s.colors, item_colors: s.item_colors, finishes: s.finishes, mirrored: s.mirrored,
  });
}
export function saveSnapshot(s, n) {
  if (!(n >= 1 && n <= 10)) throw new Error('wardrobe slots are 1..10');
  s.wardrobe[String(n)] = lookOf(s); return s;
}
export function loadSnapshot(s, n) {
  const snap = s.wardrobe[String(n)]; if (!snap) throw new Error(`wardrobe slot ${n} is empty`);
  Object.assign(s, clone(snap)); return s;
}

export function toCustomizationJson(s) {
  const parts = {};
  for (const rec of Object.values(s.equipped)) {
    parts[rec.suite_slot] = { part_id: rec.part_id, glb: rec.glb, placement: { ...rec.placement } };
  }
  const out = {
    version: 1, app: 'wh-creation-suite', fighter: s.fighter, attire: s.attire,
    base_glb: s.base_glb, out_glb: null,
    body: { ...s.body }, morphs: { ...s.morphs }, parts,
    textures: clone(s.textures), colors: { ...s.colors },
  };
  if (Object.keys(s.item_colors).length) out.item_colors = clone(s.item_colors);
  if (Object.keys(s.finishes).length) out.finishes = clone(s.finishes);
  if (Object.keys(s.mirrored).length) out.mirrored = clone(s.mirrored);
  if (s.title.some(Boolean) || Object.keys(s.wardrobe).length) {
    out.wardrobe = { title: [...s.title], snapshots: clone(s.wardrobe) };
  }
  out.layers = Object.keys(s.equipped);
  return out;
}

export function toSuiteRecord(s) {
  return {
    ...toCustomizationJson(s),
    profile: { name: s.name, title: [...s.title] },
    parameters: { arms: { offense: s.parameters.arms_offense }, body: { defense: s.parameters.body_defense } },
    fighting_style: { ...s.fighting_style },
  };
}

export function fromSuiteRecord(rec) {
  const s = createState({
    fighter: rec.fighter || 'custom', attire: rec.attire || 'attire1',
    name: rec.profile?.name || 'CUSTOM', base_glb: rec.base_glb ?? null,
  });
  if (rec.body) s.body = { body_type: rec.body.body_type || 'Medium 1', skin_tone: rec.body.skin_tone || '#c98d5e' };
  s.morphs = { ...(rec.morphs || {}) };
  s.textures = clone(rec.textures || []);
  s.colors = { ...(rec.colors || {}) };
  s.item_colors = clone(rec.item_colors || {});
  s.finishes = clone(rec.finishes || {});
  s.mirrored = clone(rec.mirrored || {});
  s.title = rec.profile?.title || rec.wardrobe?.title || ['', ''];
  s.wardrobe = clone(rec.wardrobe?.snapshots || {});
  if (rec.parameters) {
    s.parameters = { arms_offense: rec.parameters.arms?.offense ?? 50, body_defense: rec.parameters.body?.defense ?? 50 };
  }
  if (rec.fighting_style) s.fighting_style = { archetype: rec.fighting_style.archetype || 'Balanced', aggression: rec.fighting_style.aggression ?? 5 };
  // parts are keyed by suite_slot in the file; re-key by spine for state.
  // The caller passes a resolver (part_id -> spine) because the mapping
  // lives in slotmap.js; without one, the suite_slot is its own key.
  s._pendingParts = rec.parts || {};
  return s;
}
export function attachParts(s, resolver) {
  for (const [suiteSlot, rec] of Object.entries(s._pendingParts || {})) {
    const spine = resolver ? resolver(rec.part_id) : suiteSlot;
    s.equipped[spine || suiteSlot] = {
      part_id: rec.part_id, suite_slot: suiteSlot, glb: rec.glb ?? null,
      name: rec.part_id, source: null,
      placement: rec.placement || { px: 0, py: 0, pz: 0, rx: 0, ry: 0, rz: 0, s: 1 },
    };
  }
  delete s._pendingParts; return s;
}

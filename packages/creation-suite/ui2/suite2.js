// suite2.js — Creation Suite v2 front end (DOM + navigation).
//
// Presentation rebuilt per the owner's correction (2026-10-21): the
// fighter is ALWAYS on the live stage; every control lives in nested
// overlay submenus (Tekken's drill-down: fighter -> attire slot ->
// category -> subset -> item -> try-on -> equip, with the Replace /
// Cancel conflict sheet), skinned through theme/theme.json asset slots
// bound to real extracted front-end files. The data layer is v1's,
// untouched: profile.js state, src/catalogs.js merge, src/slotmap.js
// spine, and the game's own consumer attach path in viewer.js.
import { loadCatalog, mergeCatalogs, getEntry, sourceOf } from '../src/catalogs.js';
import { SPINE, SPINE_BY_ID, spineSlotOf, readinessOf, isEquippable, spineCounts } from '../src/slotmap.js';
import { BODY_MORPHS, FACE_SHAPE_MORPHS } from '../src/morphs.js';
import { T7_REGION_TABS, T7_SLOT_BY_CODE } from '../src/t7layout.js';
import * as P from '../ui/profile.js';
import { Viewer } from './viewer.js';
import { loadTheme, themeIconUrl, themeSlotUrl } from './theme.js';
import { effectivePlacement } from '../../../game/js/customization-consumer.js';

const CATALOG_URLS = [
  '../../../customization/PARTS-REGISTRY.json',
  '../../../customization/parts/no-mercy/CATALOG.json',
  '../../../customization/parts-converted/CATALOG.json',
  '../../../customization/parts-converted/defjam/CATALOG.json',
  '../../../customization/parts/tekken7/CATALOG.json',
  '../../../customization/parts/tekken6/CATALOG.json',
  '../../../customization/parts/tekken5/CATALOG.json',
  '../../../customization/parts/wmxix/CATALOG.json',
  // private builds only (see game/js/customization-consumer.js)
  ...(globalThis.__WH_PRIVATE_ASSETS ? ['../../../game/assets/private/t7/CATALOG.json'] : []),
];
const LS_SUITE = 'wh_creation_suite_v1';
const LS_STASH = 'wh_csui_attires_v1';
const CAP = 120;

// Fighters: model keys + GLB paths exactly as game/js/assets.js
// MODEL_URLS resolves them (game-relative paths gain the game/ prefix;
// ../roster paths are repo-root relative already).
export const FIGHTERS = [
  { id: 'pantera', name: 'PANTERA', glb: 'game/assets/models/pantera.glb' },
  { id: 'demonio', name: 'DEMONIO', glb: 'game/assets/models/demonio.glb' },
  { id: 'diablo', name: 'DIABLO', glb: 'roster/diablo/attires/attire1/model.glb' },
  { id: 'slice', name: 'SLICE', glb: 'roster/slice/attires/attire1/model.glb' },
  { id: 'zui', name: 'ZUI', glb: 'roster/zui/attires/attire1/model.glb' },
  { id: 'phantom', name: 'PHANTOM', glb: 'roster/phantom/attires/attire1/model.glb' },
  { id: 'skull', name: 'SKULL', glb: 'roster/skull/attires/attire1/model.glb' },
  { id: 'saku-ra', name: 'SAKU RA', glb: 'roster/sakura/attires/attire1/model.glb' },
];

const SRC_LABEL = {
  'no-mercy': 'No Mercy', wmxix: 'WMXIX', defjam: 'Def Jam', tekken7: 'Tekken 7',
  tekken6: 'Tekken 6', tekken5: 'Tekken 5',
  'western-heart-library': 'WH Library', 'eye-library': 'Eye Library',
  'cc0-hair': 'CC0 Hair', superhero: 'Superhero',
};
const RD_LABEL = {
  'ready-mesh': 'MESH · READY', 'ready-texture': 'TEXTURE · READY',
  'preview-only': 'PREVIEW · POINTS ONLY', blocked: 'BLOCKED', 'record-only': 'RECORD ONLY',
};
const RD_RANK = { 'ready-mesh': 0, 'ready-texture': 1, 'preview-only': 2, blocked: 3, 'record-only': 4 };

let ENTRIES = [], REGISTRY = null, COUNTS = null;
let viewer = null;
let fighter = FIGHTERS[0];
let attireNo = 1;
const states = {};                    // `${fighterId}:${attireNo}` -> profile state
let S = null;                         // active profile state
const nav = { screen: 'root', spine: null, src: 'all', search: '' };
let preview = null;                   // try-on: { entry, spine, placement, colors, finish, mirrored }
let detail = null;                    // detail sheet: { mode:'preview'|'equipped'|'info', spine, entry }

const $ = (sel) => document.querySelector(sel);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const srcLabel = (e) => SRC_LABEL[sourceOf(e)] || sourceOf(e) || '—';
const entryName = (e) => e.name || e.id || e.part_id || '(unnamed)';
const resolver = (partId) => { const e = getEntry(ENTRIES, partId); return e ? spineSlotOf(e) : null; };
const stateKey = () => `${fighter.id}:${attireNo}`;

function toast(msg) {
  const t = $('#toast'); t.textContent = msg; t.classList.remove('hidden');
  clearTimeout(toast._h); toast._h = setTimeout(() => t.classList.add('hidden'), 2400);
}

/* ---------------- state + save (v1 contract, unchanged) --------------- */
function stashAll() {
  const all = {};
  try { Object.assign(all, JSON.parse(localStorage.getItem(LS_STASH) || '{}')); } catch { /* fresh */ }
  for (const [k, st] of Object.entries(states)) all[k] = P.toSuiteRecord(st);
  try { localStorage.setItem(LS_STASH, JSON.stringify(all)); } catch { /* session still works */ }
}
function save() {
  stashAll();
  try { localStorage.setItem(LS_SUITE, JSON.stringify(P.toSuiteRecord(S))); } catch { /* see stashAll */ }
  toast(`Saved ${S.name} · Attire ${attireNo} — the game reads this profile`);
  renderTop();
}
function stateFor(id, n) {
  const k = `${id}:${n}`;
  if (!states[k]) {
    const f = FIGHTERS.find((x) => x.id === id) || FIGHTERS[0];
    states[k] = P.createState({ fighter: id, attire: `attire${n}`, name: f.name, base_glb: f.glb });
  }
  return states[k];
}
async function syncViewer() {
  viewer.entries = ENTRIES; viewer.registry = REGISTRY;
  // ORDER MATTERS: morph proxies SET bone scales, and the shared attach
  // cancels the socket's CURRENT world scale. Morphs first, then attach
  // (the in-fight consumer attaches once against final bone scales —
  // the editor must present the same result).
  viewer.applyMorphs(S, P.toSuiteRecord(S));
  await viewer.applyRecord(P.toCustomizationJson(S));
  viewer.applyMorphs(S, P.toSuiteRecord(S));
}
async function switchFighter(f, n = 1) {
  fighter = f; attireNo = n;
  S = stateFor(f.id, n);
  renderTop();
  try {
    await viewer.setFighter(f.glb, f.id);
    await syncViewer();
  } catch (e) {
    toast(`Model not available in this tree: ${f.name}`);
    console.warn('[CS2] fighter load failed', f.glb, e.message || e);
  }
  go('root');
}

/* ---------------- top plate + prompt bar ------------------------------ */
function renderTop() {
  $('#plateName').textContent = fighter.name;
  const eq = Object.keys(S?.equipped || {}).length;
  $('#plateMeta').textContent = `Attire ${attireNo} · ${eq} parts · ${S?.textures.length || 0} ink`;
  $('#attireChips').innerHTML = [1, 2, 3, 4].map((n) =>
    `<button type="button" data-attire="${n}" class="${n === attireNo ? 'on' : ''}">A${n}</button>`).join('');
  if (COUNTS) $('#catalogLine').textContent =
    `${COUNTS.total.toLocaleString()} parts · ${COUNTS.ready.toLocaleString()} equippable · ${COUNTS.mapped.toLocaleString()} on the Tekken spine`;
}

/* ---------------- navigation ------------------------------------------ */
const TITLES = { root: 'CUSTOMIZE', body: 'BODY', face: 'FACE', ink: 'INK — TATTOOS / IMAGES', wardrobe: 'WARDROBE', profile: 'PROFILE', fighters: 'SELECT FIGHTER' };
function go(screen, opts = {}) {
  nav.screen = screen;
  if (opts.spine !== undefined) nav.spine = opts.spine;
  if (screen !== 'items') { nav.search = ''; }
  renderMenu();
}
function goBack() {
  if (detail) return closeDetail();
  if (preview) return cancelPreview();
  if (nav.screen !== 'root') return go('root');
}
function renderMenu() {
  const body = $('#menuBody');
  const title = nav.screen === 'items' ? (SPINE_BY_ID[nav.spine]?.title || 'ITEMS').toUpperCase() : (TITLES[nav.screen] || 'CUSTOMIZE');
  $('#menuTitle').textContent = title;
  $('#menuCrumb').textContent = '';
  $('#menuBack').style.visibility = nav.screen === 'root' && !preview && !detail ? 'hidden' : 'visible';
  body.scrollTop = 0;
  ({ root: renderRoot, items: renderItems, body: renderBody, face: renderFace, ink: renderInk, wardrobe: renderWardrobe, profile: renderProfile, fighters: renderFighters }[nav.screen] || renderRoot)();
}
function row({ action, id, main, sub = '', badge = '', cls = '', attrs = '', icon = '' }) {
  const iconUrl = icon ? themeIconUrl(icon) : null;
  return `<button type="button" class="mrow ${cls}" data-action="${action}" ${id ? `data-id="${esc(id)}"` : ''} ${attrs}>
    ${iconUrl ? `<img class="mrow-icon" src="${iconUrl}" alt="">` : ''}
    <span class="mrow-main">${esc(main)}${sub ? `<span class="mrow-sub">${esc(sub)}</span>` : ''}</span>
    ${badge ? `<span class="mrow-badge">${badge}</span>` : ''}<span class="mrow-arrow" aria-hidden="true">›</span></button>`;
}
function sectionLabel(t, icon = '') {
  const iconUrl = icon ? themeIconUrl(icon) : null;
  return `<div class="msection">${iconUrl ? `<img class="msection-icon" src="${iconUrl}" alt="">` : ''}${esc(t)}</div>`;
}

/* ---------------- root: the Tekken category list ----------------------- */
function renderRoot() {
  const el = $('#menuBody');
  let h = row({ action: 'screen', id: 'fighters', main: 'FIGHTER', sub: fighter.name, badge: 'CHANGE' });
  h += sectionLabel('Body & Face — the tools');
  h += row({ action: 'screen', id: 'body', main: 'BODY', sub: `${S.body.body_type} · ${Object.keys(S.morphs).length} morphs`, icon: 'appearance' });
  h += row({ action: 'screen', id: 'face', main: 'FACE', sub: 'Face morphs · Eyes · Face Paint', icon: 'appearance' });
  // Tekken 7 customize flow: region tab -> item slot (t7layout.js, codes
  // proven against customize_item_data.bin), then the WH-only slots.
  const slotRow = (sp) => {
    const eqRec = S.equipped[sp.id];
    const c = COUNTS?.per?.[sp.id];
    return row({
      action: 'items', id: sp.id, main: sp.title.toUpperCase(),
      sub: eqRec ? eqRec.name : '', badge: c ? `${c.ready} ready` : '',
      cls: eqRec ? 'has-eq' : '',
    });
  };
  const shown = new Set(['ink', 'skin_tone', 'mirror']);
  for (const tab of T7_REGION_TABS) {
    const sps = tab.codes.map((c) => SPINE_BY_ID[T7_SLOT_BY_CODE[c].spine]).filter((sp) => sp && !shown.has(sp.id));
    if (!sps.length) continue;
    h += sectionLabel(`${tab.title} — Tekken 7 slots`);
    for (const sp of sps) { shown.add(sp.id); h += slotRow(sp); }
  }
  const extra = SPINE.filter((sp) => !shown.has(sp.id));
  if (extra.length) { h += sectionLabel('Western Heart extra slots'); for (const sp of extra) h += slotRow(sp); }
  h += sectionLabel('Physics');
  h += row({ action: 'physics', id: 'physics', main: 'BODY PHYSICS', sub: `size-adaptive springs: ${viewer?.physicsCount ?? 0} (chest · glutes · belly · thighs)`, badge: viewer?.physicsEnabled === false ? 'OFF' : 'ON' });
  h += row({ action: 'screen', id: 'body', main: 'SKIN TONE', sub: S.body.skin_tone, badge: 'TOOL' });
  h += sectionLabel('Layers & Looks');
  h += row({ action: 'screen', id: 'ink', main: 'INK — TATTOOS / IMAGES', sub: `${S.textures.length} layer(s)` });
  h += row({ action: 'screen', id: 'wardrobe', main: 'WARDROBE', sub: `title: ${S.title.filter(Boolean).join(' ') || '—'} · ${Object.keys(S.wardrobe).length}/10 looks`, icon: 'profileMusic' });
  h += row({ action: 'screen', id: 'profile', main: 'PROFILE', sub: `${S.fighting_style.archetype} · aggression ${S.fighting_style.aggression}`, icon: 'parameter' });
  h += `<button type="button" class="mrow save-row" data-action="save"><span class="mrow-main">SAVE PROFILE<span class="mrow-sub">writes wh_creation_suite_v1 — the game reads it in the fight</span></span></button>`;
  el.innerHTML = h;
}

/* ---------------- items: subset filter + list -------------------------- */
function filteredEntries(spine) {
  let list = ENTRIES.filter((e) => spineSlotOf(e) === spine);
  if (nav.src !== 'all') list = list.filter((e) => sourceOf(e) === nav.src);
  if (nav.search) {
    const q = nav.search.toLowerCase();
    list = list.filter((e) => entryName(e).toLowerCase().includes(q) || (e.id || '').toLowerCase().includes(q));
  }
  list.sort((a, b) => RD_RANK[readinessOf(a)] - RD_RANK[readinessOf(b)] || entryName(a).localeCompare(entryName(b)));
  return list;
}
function badge(e) {
  const r = readinessOf(e);
  return `<span class="badge ${r}">${RD_LABEL[r]}</span> <span class="badge src">${esc(srcLabel(e))}</span>`;
}
function renderItems() {
  const spine = nav.spine;
  const el = $('#menuBody');
  const all = ENTRIES.filter((e) => spineSlotOf(e) === spine);
  const sources = [...new Set(all.map((e) => sourceOf(e)).filter(Boolean))];
  let h = `<div class="subset-bar" role="tablist" aria-label="Source subsets">
    <button type="button" data-src="all" class="${nav.src === 'all' ? 'on' : ''}">ALL</button>
    ${sources.map((s) => `<button type="button" data-src="${esc(s)}" class="${nav.src === s ? 'on' : ''}">${esc(SRC_LABEL[s] || s).toUpperCase()}</button>`).join('')}
  </div>`;
  h += `<input id="itemSearch" class="search" type="search" placeholder="Search ${all.length} parts…" value="${esc(nav.search)}" />`;
  const list = filteredEntries(spine);
  h += `<div class="list-note">Showing ${Math.min(CAP, list.length)} of ${list.length}. Tap a part to try it on the fighter.</div>`;
  h += list.slice(0, CAP).map((e) => {
    const eq = S.equipped[spine]?.part_id === (e.id || e.part_id);
    const marker = eq ? themeSlotUrl('cursor') : null;
    return `<button type="button" class="irow ${eq ? 'equipped' : ''}" data-action="item" data-id="${esc(e.id || e.part_id)}">
      <span class="irow-main"><span class="irow-name">${esc(entryName(e))}</span><span class="irow-id">${esc(e.id || e.part_id)}${eq ? ' · EQUIPPED' : ''}</span><span class="irow-badges">${badge(e)}</span></span>${marker ? `<img class="eq-marker" src="${marker}" alt="equipped">` : ''}</button>`;
  }).join('');
  el.innerHTML = h;
  const si = $('#itemSearch');
  si.addEventListener('input', () => { nav.search = si.value; renderItemsKeep(si); });
}
function renderItemsKeep(input) {
  const pos = input.selectionStart;
  renderItems();
  const ni = $('#itemSearch'); ni.focus(); ni.setSelectionRange(pos, pos);
}

/* ---------------- try-on (Tekken hover try-on, committed by EQUIP) ----- */
function defaultPlacementOf(entry) {
  const p = entry.placement || {};
  if ('px' in p || 'py' in p || 'pz' in p) return { px: p.px || 0, py: p.py || 0, pz: p.pz || 0, rx: p.rx || 0, ry: p.ry || 0, rz: p.rz || 0, s: p.s ?? 1 };
  const o = entry.offset || p.offset || [0, 0, 0], r = entry.rotation || p.rotation || [0, 0, 0];
  return { px: o[0] || 0, py: o[1] || 0, pz: o[2] || 0, rx: r[0] || 0, ry: r[1] || 0, rz: r[2] || 0, s: entry.scale ?? p.scale ?? 1 };
}
function previewRecord() {
  const rec = P.toCustomizationJson(S);
  if (!preview) return rec;
  const key = preview.entry.suite_slot || preview.spine;
  rec.parts[key] = { part_id: preview.entry.id || preview.entry.part_id, glb: preview.entry.glb || preview.entry.asset || preview.entry.file || null, placement: { ...preview.placement } };
  const cols = preview.colors.filter(Boolean);
  if (cols.length) { rec.item_colors ||= {}; rec.item_colors[key] = cols; }
  if (preview.finish && Object.keys(preview.finish).length) { rec.finishes ||= {}; rec.finishes[key] = { ...preview.finish }; }
  return rec;
}
async function applyPreview() { await viewer.applyRecord(previewRecord()); }
async function startPreview(entry, spine) {
  if (!isEquippable(entry)) { openInfo(entry, spine); return; }
  preview = {
    entry, spine,
    placement: defaultPlacementOf(entry),
    colors: [...(S.item_colors[entry.suite_slot || spine] || [])],
    finish: { ...(S.finishes[entry.suite_slot || spine] || {}) },
    mirrored: !!S.mirrored[entry.suite_slot || spine],
  };
  $('#tryonName').textContent = entryName(entry);
  $('#tryonBar').classList.remove('hidden');
  $('#menuStack').classList.add('collapsed');
  await applyPreview();
}
async function cancelPreview() {
  preview = null; detail = null;
  $('#tryonBar').classList.add('hidden');
  $('#detailSheet').classList.add('hidden');
  $('#menuStack').classList.remove('collapsed');
  await syncViewer();
  renderMenu();
}
async function commitPreview(force = false) {
  const { entry, spine } = preview;
  const res = P.equip(S, entry, spine, { force });
  if (!res.ok) { openConflict(res.conflicts); return; }
  const key = entry.suite_slot || spine;
  P.setPlacement(S, spine, preview.placement);
  P.setItemColors(S, spine, preview.colors);
  if (Object.keys(preview.finish).length) P.setFinish(S, spine, preview.finish);
  P.setMirrored(S, spine, preview.mirrored);
  preview = null;
  $('#tryonBar').classList.add('hidden');
  $('#detailSheet').classList.add('hidden');
  $('#menuStack').classList.remove('collapsed');
  await syncViewer();
  toast(`Equipped ${entryName(entry)}`);
  renderTop(); renderMenu();
}

/* ---------------- conflict sheet (Replace / Cancel) -------------------- */
function openConflict(conflicts) {
  const sh = $('#conflictSheet');
  sh.innerHTML = `<div class="sheet-title">REPLACE?</div>
    <p class="sheet-text">Equipping <b>${esc(entryName(preview.entry))}</b> removes:</p>
    ${conflicts.map((c) => `<div class="conflict-row">${esc(SPINE_BY_ID[c.spine]?.title || c.spine)} — ${esc(c.name || c.part_id)}</div>`).join('')}
    <div class="sheet-actions">
      <button type="button" class="prompt primary" data-conflict="replace">REPLACE</button>
      <button type="button" class="prompt" data-conflict="cancel">CANCEL</button>
    </div>`;
  sh.classList.remove('hidden');
  sh.querySelectorAll('[data-conflict]').forEach((b) => b.addEventListener('click', async () => {
    sh.classList.add('hidden');
    if (b.dataset.conflict === 'replace') await commitPreview(true);
  }));
}

/* ---------------- detail sheet: placement / colors / finish ------------ */
function sliderRow(kind, id, label, value, min, max, step) {
  return `<div class="slider-row"><label for="dsl-${kind}-${id}">${esc(label)}</label>
    <input type="range" id="dsl-${kind}-${id}" data-kind="${kind}" data-id="${id}" min="${min}" max="${max}" step="${step}" value="${value}">
    <output id="dout-${kind}-${id}">${Number(value).toFixed(step >= 1 ? 0 : 2)}</output></div>`;
}
function openDetail(mode, spine, entry) {
  detail = { mode, spine, entry };
  const sh = $('#detailSheet');
  if (mode === 'preview') $('#tryonBar').classList.add('hidden');
  const work = mode === 'preview' ? preview : {
    placement: { ...S.equipped[spine].placement },
    colors: [...(S.item_colors[entry.suite_slot || spine] || [])],
    finish: { ...(S.finishes[entry.suite_slot || spine] || {}) },
    mirrored: !!S.mirrored[entry.suite_slot || spine],
  };
  detail.work = work;
  const r = readinessOf(entry);
  let h = `<div class="sheet-title">${esc(entryName(entry))}</div>
    <div class="sheet-badges">${badge(entry)}</div>
    <div class="sheet-meta">id ${esc(entry.id || entry.part_id)} · slot ${esc(SPINE_BY_ID[spine]?.title || spine)} · status ${esc(entry.status || entry.conversion?.status || 'converted')}</div>`;
  if (mode !== 'info') {
    h += `<div class="sheet-sec">PLACEMENT (bone-socket editor)</div>`;
    h += sliderRow('pl', 'px', 'Pos X (m)', work.placement.px, -0.5, 0.5, 0.01);
    h += sliderRow('pl', 'py', 'Pos Y (m)', work.placement.py, -0.5, 0.5, 0.01);
    h += sliderRow('pl', 'pz', 'Pos Z (m)', work.placement.pz, -0.5, 0.5, 0.01);
    h += sliderRow('pl', 'rx', 'Pitch °', work.placement.rx, -180, 180, 1);
    h += sliderRow('pl', 'ry', 'Yaw °', work.placement.ry, -180, 180, 1);
    h += sliderRow('pl', 'rz', 'Roll °', work.placement.rz, -180, 180, 1);
    h += sliderRow('pl', 's', 'Scale', work.placement.s, 0.25, 2.5, 0.05);
    h += `<div class="toggle-row"><span>Mirror L/R</span><button type="button" id="mirrorBtn" class="toggle ${work.mirrored ? 'on' : ''}">${work.mirrored ? 'ON' : 'OFF'}</button></div>`;
    h += `<div class="sheet-sec">COLOR CHANNELS (up to 5 — channel 1 tints live)</div>`;
    for (let i = 0; i < 5; i++) {
      h += `<div class="color-row"><span>CH ${i + 1}</span><input type="color" data-kind="chan" data-id="${i}" value="${work.colors[i] || '#ffffff'}"></div>`;
    }
    h += `<div class="sheet-sec">FINISH</div>`;
    h += sliderRow('fin', 'roughness', 'Roughness', work.finish.roughness ?? 0.5, 0, 1, 0.05);
    h += sliderRow('fin', 'metalness', 'Metalness', work.finish.metalness ?? 0, 0, 1, 0.05);
    h += `<div class="sheet-actions">
      ${mode === 'preview' ? '<button type="button" class="prompt primary" id="detailEquip">EQUIP</button>' : ''}
      ${mode === 'equipped' ? '<button type="button" class="prompt danger" id="detailUnequip">REMOVE PART</button>' : ''}
      <button type="button" class="prompt" id="detailDone">DONE</button></div>`;
  } else {
    h += `<p class="sheet-text">This part is <b>${esc(RD_LABEL[r])}</b> — it cannot be equipped yet. Its record stays visible so nothing is silently dropped.</p>
      <div class="sheet-actions"><button type="button" class="prompt" id="detailDone">DONE</button></div>`;
  }
  sh.innerHTML = h;
  sh.classList.remove('hidden');
  wireDetail();
}
function detailLive() {
  // Push the working placement/colors/finish onto the model via the
  // shared live-edit path (applyEdit under the hood). The working
  // placement is in profile dialect — run it through the consumer's
  // effectivePlacement so scale/offset share the attach basis (unit
  // scale included), never a forked conversion.
  const key = detail.entry.suite_slot || detail.spine;
  const w = detail.work;
  const eff = effectivePlacement({ ...w.placement }, detail.entry, key);
  viewer.liveEdit(key, {
    offset: eff.offset || [0, 0, 0],
    rotation: eff.rotation || [0, 0, 0],
    scale: eff.scale ?? 1,
    tint: w.colors.find((c) => c && c.toLowerCase() !== '#ffffff') || w.finish.tint || undefined,
    roughness: w.finish.roughness, metalness: w.finish.metalness,
  });
}
function wireDetail() {
  const sh = $('#detailSheet');
  sh.querySelectorAll('input[type=range]').forEach((inp) => {
    inp.addEventListener('input', () => {
      const out = sh.querySelector(`#dout-${inp.dataset.kind}-${inp.dataset.id}`);
      if (out) out.textContent = Number(inp.value).toFixed(inp.step >= 1 ? 0 : 2);
      const w = detail.work;
      if (inp.dataset.kind === 'pl') w.placement[inp.dataset.id] = Number(inp.value);
      if (inp.dataset.kind === 'fin') w.finish[inp.dataset.id] = Number(inp.value);
      detailLive();
    });
    inp.addEventListener('change', async () => {
      // Commit exact values to state on release (sliders stay live meanwhile).
      if (detail.mode === 'equipped') {
        P.setPlacement(S, detail.spine, detail.work.placement);
        P.setFinish(S, detail.spine, detail.work.finish);
        await syncViewer();
      }
    });
  });
  sh.querySelectorAll('input[type=color]').forEach((inp) => {
    inp.addEventListener('input', () => {
      detail.work.colors[Number(inp.dataset.id)] = inp.value;
      detailLive();
    });
    inp.addEventListener('change', async () => {
      if (detail.mode === 'equipped') {
        P.setItemColors(S, detail.spine, detail.work.colors);
        await syncViewer();
      }
    });
  });
  const mb = sh.querySelector('#mirrorBtn');
  if (mb) mb.addEventListener('click', () => {
    detail.work.mirrored = !detail.work.mirrored;
    detail.work.placement.px = -(detail.work.placement.px || 0);
    if (detail.mode === 'equipped') P.setMirrored(S, detail.spine, detail.work.mirrored);
    openDetail(detail.mode, detail.spine, detail.entry);
    detailLive();
  });
  const de = sh.querySelector('#detailEquip');
  if (de) de.addEventListener('click', async () => { closeDetail(true); await commitPreview(false); });
  const du = sh.querySelector('#detailUnequip');
  if (du) du.addEventListener('click', async () => {
    P.unequip(S, detail.spine);
    closeDetail(true);
    await syncViewer(); renderTop(); renderMenu();
    toast('Part removed');
  });
  sh.querySelector('#detailDone').addEventListener('click', () => closeDetail(false));
}
function closeDetail(silent) {
  detail = null;
  $('#detailSheet').classList.add('hidden');
  if (preview) $('#tryonBar').classList.remove('hidden');
  $('#menuStack').classList.remove('collapsed');
  if (nav.screen) renderMenu();
}
function openInfo(entry, spine) { openDetail('info', spine, entry); }

/* ---------------- BODY: type / skin tone tool / morph subsets ---------- */
function morphSlider(kind, m) {
  return sliderRow(kind, m.id, m.label, S.morphs[m.id] || 0, m.range[0], m.range[1], 0.05);
}
function renderBody() {
  const el = $('#menuBody');
  let h = sectionLabel('Body Type');
  h += `<div class="chip-grid">${P.BODY_TYPE_NAMES.map((t) =>
    `<button type="button" data-bodytype="${esc(t)}" class="${S.body.body_type === t ? 'on' : ''}">${esc(t)}</button>`).join('')}</div>`;
  h += sectionLabel('Skin Tone — Tekken tool row (−237)');
  h += `<div class="swatch-row">${P.SKIN_TONES.map((c) =>
    `<button type="button" data-skin="${c}" class="swatch ${S.body.skin_tone === c ? 'on' : ''}" style="background:${c}" aria-label="skin ${c}"></button>`).join('')}
    <input type="color" id="skinCustom" value="${S.body.skin_tone}"></div>
    <p class="fineprint">Stored in the profile and applied by the game's CAW path; a roster fighter's authored textures are never re-tinted (the consumer's contract).</p>`;
  h += sectionLabel('Body Morphs — live proxy preview (bake is truth)');
  h += BODY_MORPHS.map((m) => morphSlider('morph', m)).join('');
  el.innerHTML = h;
  wireToolSliders();
  el.querySelectorAll('[data-bodytype]').forEach((b) => b.addEventListener('click', () => {
    P.setBodyType(S, b.dataset.bodytype); viewer.applyMorphs(S, P.toSuiteRecord(S)); renderBody(); renderTop();
  }));
  el.querySelectorAll('[data-skin]').forEach((b) => b.addEventListener('click', () => {
    P.setSkinTone(S, b.dataset.skin); renderBody(); renderTop();
  }));
  const sc = el.querySelector('#skinCustom');
  if (sc) sc.addEventListener('change', () => { P.setSkinTone(S, sc.value); renderBody(); renderTop(); });
}
function renderFace() {
  const el = $('#menuBody');
  let h = sectionLabel('Face Morphs — live proxy preview (bake is truth)');
  h += FACE_SHAPE_MORPHS.map((m) => morphSlider('morph', m)).join('');
  h += sectionLabel('Face Parts');
  for (const spid of ['eyes', 'make_up', 'face_hair', 'gla']) {
    const sp = SPINE_BY_ID[spid];
    const c = COUNTS?.per?.[spid];
    h += row({ action: 'items', id: spid, main: sp.title.toUpperCase(), sub: S.equipped[spid]?.name || '', badge: c ? `${c.ready} ready` : '', cls: S.equipped[spid] ? 'has-eq' : '' });
  }
  el.innerHTML = h;
  wireToolSliders();
}
function wireToolSliders() {
  $('#menuBody').querySelectorAll('input[type=range][data-kind="morph"]').forEach((inp) => {
    inp.addEventListener('input', () => {
      const out = document.querySelector(`#dout-morph-${inp.dataset.id}`);
      if (out) out.textContent = Number(inp.value).toFixed(2);
      P.setMorph(S, inp.dataset.id, Number(inp.value));
      viewer.applyMorphs(S, P.toSuiteRecord(S));
    });
    // On release, re-attach parts against the new bone scales (attach
    // cancels world scale — it must be recomputed when scales change).
    inp.addEventListener('change', () => { syncViewer(); });
  });
}

/* ---------------- INK: texture layers + rect placement ------------------ */
function renderInk() {
  const el = $('#menuBody');
  let h = sectionLabel(`Layers (${S.textures.length})`);
  h += S.textures.map((l, i) => `<div class="layer-row"><span>${esc(l.part_id)}<span class="mrow-sub">${esc(l.kind)}</span></span>
    <button type="button" class="mini danger" data-layer-del="${i}">REMOVE</button></div>`).join('') || '<p class="fineprint">No layers yet.</p>';
  h += sectionLabel('Add a layer — tap to place');
  const pool = ENTRIES.filter((e) => spineSlotOf(e) === 'ink' && readinessOf(e) === 'ready-texture')
    .sort((a, b) => entryName(a).localeCompare(entryName(b)));
  h += `<div class="list-note">${pool.length} ink-ready textures. Placement rect is set in the profile (the consumer applies layers in-fight).</div>`;
  h += pool.slice(0, CAP).map((e) => `<button type="button" class="irow" data-action="ink-add" data-id="${esc(e.id || e.part_id)}">
    <span class="irow-main"><span class="irow-name">${esc(entryName(e))}</span><span class="irow-id">${esc(e.id || e.part_id)}</span><span class="irow-badges">${badge(e)}</span></span></button>`).join('');
  el.innerHTML = h;
  el.querySelectorAll('[data-layer-del]').forEach((b) => b.addEventListener('click', async () => {
    P.removeLayer(S, Number(b.dataset.layerDel)); await syncViewer(); renderInk(); renderTop();
  }));
}

/* ---------------- WARDROBE: title + 10 look snapshots ------------------- */
function renderWardrobe() {
  const el = $('#menuBody');
  let h = sectionLabel('Fighter Title (pair)');
  h += `<div class="title-inputs"><input id="titleA" type="text" placeholder="RAGING" value="${esc(S.title[0] || '')}">
    <input id="titleB" type="text" placeholder="BEAST" value="${esc(S.title[1] || '')}"></div>`;
  h += sectionLabel('Looks — options stack, never overwritten');
  for (let n = 1; n <= 10; n++) {
    const has = !!S.wardrobe[String(n)];
    h += `<div class="look-row"><span>LOOK ${n}<span class="mrow-sub">${has ? 'saved look' : 'empty'}</span></span>
      <span class="look-actions"><button type="button" class="mini" data-look-store="${n}">STORE</button>
      <button type="button" class="mini" data-look-apply="${n}" ${has ? '' : 'disabled'}>APPLY</button></span></div>`;
  }
  el.innerHTML = h;
  el.querySelector('#titleA').addEventListener('change', (e) => { S.title[0] = e.target.value.toUpperCase(); });
  el.querySelector('#titleB').addEventListener('change', (e) => { S.title[1] = e.target.value.toUpperCase(); });
  el.querySelectorAll('[data-look-store]').forEach((b) => b.addEventListener('click', () => {
    P.saveSnapshot(S, Number(b.dataset.lookStore)); toast(`Look ${b.dataset.lookStore} stored`); renderWardrobe();
  }));
  el.querySelectorAll('[data-look-apply]').forEach((b) => b.addEventListener('click', async () => {
    try { P.loadSnapshot(S, Number(b.dataset.lookApply)); await syncViewer(); toast(`Look ${b.dataset.lookApply} applied`); renderTop(); renderWardrobe(); }
    catch (e) { toast(e.message); }
  }));
}

/* ---------------- PROFILE ------------------------------------------------ */
function renderProfile() {
  const el = $('#menuBody');
  let h = sectionLabel('Identity');
  h += `<div class="field"><label>Name</label><input id="profName" type="text" value="${esc(S.name)}"></div>`;
  h += sectionLabel('Fighting Style', 'fightingStyle');
  h += `<div class="chip-grid">${P.ARCHETYPES.map((a) =>
    `<button type="button" data-arch="${esc(a)}" class="${S.fighting_style.archetype === a ? 'on' : ''}">${esc(a)}</button>`).join('')}</div>`;
  h += sliderRow('param', 'aggression', 'Aggression', S.fighting_style.aggression, 0, 10, 1);
  h += sectionLabel('Parameters');
  h += sliderRow('param', 'arms_offense', 'Arms Offense', S.parameters.arms_offense, 0, 100, 1);
  h += sliderRow('param', 'body_defense', 'Body Defense', S.parameters.body_defense, 0, 100, 1);
  h += `<div class="sheet-actions">
    <button type="button" class="prompt primary" data-action="save">SAVE PROFILE</button>
    <button type="button" class="prompt" id="exportBtn">EXPORT JSON</button></div>
    <p class="fineprint">Save writes the wh_creation_suite_v1 record the game reads (plus the per-attire stash). Export downloads the per-attire customization.json v1.</p>`;
  el.innerHTML = h;
  el.querySelector('#profName').addEventListener('change', (e) => { S.name = e.target.value.toUpperCase() || S.name; renderTop(); });
  el.querySelectorAll('[data-arch]').forEach((b) => b.addEventListener('click', () => { S.fighting_style.archetype = b.dataset.arch; renderProfile(); }));
  el.querySelectorAll('input[type=range][data-kind="param"]').forEach((inp) => {
    inp.addEventListener('input', () => {
      const out = document.querySelector(`#dout-param-${inp.dataset.id}`);
      if (out) out.textContent = inp.value;
      if (inp.dataset.id === 'aggression') S.fighting_style.aggression = Number(inp.value);
      else S.parameters[inp.dataset.id] = Number(inp.value);
    });
  });
  el.querySelector('#exportBtn').addEventListener('click', () => {
    const blob = new Blob([JSON.stringify(P.toCustomizationJson(S), null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `${fighter.id}-${S.attire}-customization.json`;
    a.click(); URL.revokeObjectURL(a.href);
  });
}

/* ---------------- fighters (Tekken entry: fighter first) ----------------- */
function renderFighters() {
  const el = $('#menuBody');
  const art = themeSlotUrl('keyArt');
  el.innerHTML = (art ? `<div class="select-banner" role="img" aria-label="Tekken 6 key art (extracted PIC1)"></div>` : '')
    + FIGHTERS.map((f) => `<button type="button" class="mrow ${f.id === fighter.id ? 'has-eq' : ''}" data-fighter="${f.id}">
    <span class="mrow-main">${esc(f.name)}<span class="mrow-sub">${f.id === fighter.id ? 'current fighter' : 'tap to load'}</span></span>
    <span class="mrow-arrow" aria-hidden="true">›</span></button>`).join('');
  el.querySelectorAll('[data-fighter]').forEach((b) => b.addEventListener('click', async () => {
    const f = FIGHTERS.find((x) => x.id === b.dataset.fighter);
    if (f && f.id !== fighter.id) await switchFighter(f, 1);
    else go('root');
  }));
}

/* ---------------- global wiring + boot ----------------------------------- */
document.addEventListener('click', async (e) => {
  const t = e.target.closest('[data-action],[data-attire],[data-src]');
  if (!t) return;
  if (t.dataset.attire) {
    attireNo = Number(t.dataset.attire);
    S = stateFor(fighter.id, attireNo);
    await syncViewer(); renderTop(); renderMenu();
    return;
  }
  if (t.dataset.src !== undefined && nav.screen === 'items') { nav.src = t.dataset.src; renderItems(); return; }
  const a = t.dataset.action;
  if (!a) return;
  if (a === 'screen') go(t.dataset.id);
  else if (a === 'items') go('items', { spine: t.dataset.id });
  else if (a === 'save') save();
  else if (a === 'physics' && viewer) { viewer.physicsEnabled = viewer.physicsEnabled === false; viewer.rebuildPhysics(); renderMenu(); }
  else if (a === 'item') {
    const entry = getEntry(ENTRIES, t.dataset.id);
    if (!entry) return;
    if (S.equipped[nav.spine]?.part_id === (entry.id || entry.part_id) && isEquippable(entry)) openDetail('equipped', nav.spine, entry);
    else startPreview(entry, nav.spine);
  } else if (a === 'ink-add') {
    const entry = getEntry(ENTRIES, t.dataset.id);
    if (!entry) return;
    try { P.addLayer(S, entry, { rect: [0.1, 0.1, 0.3, 0.3] }); await syncViewer(); toast(`Layer added: ${entryName(entry)}`); renderInk(); renderTop(); }
    catch (err) { toast(err.message); }
  }
});
$('#menuBack').addEventListener('click', goBack);
$('#promptBack').addEventListener('click', goBack);
$('#promptSave').addEventListener('click', () => save());
$('#tryonEquip').addEventListener('click', () => commitPreview(false));
$('#tryonBack').addEventListener('click', () => cancelPreview());
$('#tryonAdjust').addEventListener('click', () => { if (preview) openDetail('preview', preview.spine, preview.entry); });

async function boot() {
  const themeInfo = await loadTheme();
  console.log('[CS2] theme bound:', themeInfo.bound.join(',') || 'none', '| reconstruction fallback:', themeInfo.fallback.join(','));
  viewer = new Viewer($('#stage3d'));
  // catalogs: registry first (it wins dedupe), per-game catalogs fill in —
  // exactly the game's consumer merge.
  const fetcher = (u) => fetch(new URL(u, new URL('./', location.href)));
  let registry = { parts: [] };
  const cats = [];
  for (const [i, u] of CATALOG_URLS.entries()) {
    try {
      const c = await loadCatalog(u, fetcher);
      if (i === 0) registry = c; else cats.push(c);
    } catch (e) { console.warn('[CS2] catalog skipped', u, e.message || e); }
  }
  REGISTRY = registry;
  ENTRIES = mergeCatalogs(registry, ...cats);
  COUNTS = spineCounts(ENTRIES);
  // restore a saved suite record for its fighter when one exists
  S = stateFor(fighter.id, attireNo);
  try {
    const raw = localStorage.getItem(LS_SUITE);
    if (raw) {
      const rec = JSON.parse(raw);
      // The consumer's own belonging rule (customization-consumer.js):
      // a record with fighter 'custom' belongs by profile.name match.
      const f = FIGHTERS.find((x) => x.id === rec.fighter)
        || FIGHTERS.find((x) => rec.fighter === 'custom' && x.name === (rec.profile?.name || '').toUpperCase());
      if (f) {
        fighter = f; attireNo = Number((rec.attire || 'attire1').replace('attire', '')) || 1;
        const st = P.fromSuiteRecord(rec);
        P.attachParts(st, resolver);
        states[stateKey()] = st; S = st;
      }
    }
  } catch (e) { /* fresh state is fine */ }
  renderTop();
  go('root');
  await viewer.setFighter(fighter.glb, fighter.id);
  await syncViewer();
  window.__cs2 = { viewer, get state() { return S; }, get entries() { return ENTRIES; }, counts: COUNTS };
  console.log(`[CS2] STATE entries=${ENTRIES.length} ready=${COUNTS.ready} fighter=${fighter.id} physics=${viewer?.physicsCount ?? 0} t7=${ENTRIES.filter((e) => e.source_game === "tekken7").length}`);
}
boot().catch((e) => {
  const el = $('#bootError');
  el.textContent = `Creation Suite failed to start: ${e.message || e}`;
  el.classList.remove('hidden');
  console.error('[CS2] boot failed', e);
});

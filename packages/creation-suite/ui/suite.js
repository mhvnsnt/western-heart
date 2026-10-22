// suite.js — the mobile-first Creation Suite front end (DOM).
//
// Tekken's menu shape (docs/CREATION-SUITE-UI-SCHEMA-2026-10-21.md), laid out
// for a phone: fighter stage pinned on top, section sheet beneath, tab bar in
// the thumb zone. Tap -> scroll -> TAP to assign; no drag-and-drop anywhere.
// All state lives in profile.js (pure); this file only renders and routes.
import { mergeCatalogs, getEntry, sourceOf } from '../src/catalogs.js';
import { SPINE, SPINE_BY_ID, spineSlotOf, readinessOf, isEquippable, spineCounts } from '../src/slotmap.js';
import { BODY_MORPHS, FACE_SHAPE_MORPHS } from '../src/morphs.js';
import * as P from './profile.js';

const CATALOG_URLS = [
  '../../../customization/PARTS-REGISTRY.json',
  '../../../customization/parts/no-mercy/CATALOG.json',
  '../../../customization/parts-converted/CATALOG.json',
  '../../../customization/parts-converted/defjam/CATALOG.json',
  '../../../customization/parts/tekken7/CATALOG.json',
];
const LS_SUITE = 'wh_creation_suite_v1';       // the game's consumer record
const LS_STASH = 'wh_csui_attires_v1';         // per-attire stash (stacking)
const CAP = 120;

const SRC_LABEL = {
  'no-mercy': 'No Mercy', wmxix: 'WMXIX', defjam: 'Def Jam', tekken7: 'Tekken 7',
  'western-heart-library': 'WH Library', 'eye-library': 'Eye Library',
  'cc0-hair': 'CC0 Hair', superhero: 'Superhero',
};
const RD_LABEL = {
  'ready-mesh': 'MESH · READY', 'ready-texture': 'TEXTURE · READY',
  'preview-only': 'PREVIEW · POINTS ONLY', blocked: 'BLOCKED', 'record-only': 'RECORD ONLY',
};
const RD_RANK = { 'ready-mesh': 0, 'ready-texture': 1, 'preview-only': 2, blocked: 3, 'record-only': 4 };

let ENTRIES = [], COUNTS = null;
let attireNo = 1;
const attires = {};                 // 1..4 -> profile state
let S = null;                       // active profile state
const ui = { tab: 'body', cat: null, search: '', src: 'all', inkPick: false, inkEntry: null, inkRect: [0.1, 0.1, 0.3, 0.3], swapRegion: null, swapSearch: '' };
let SWAP_SOURCES = [];
const REGION_LABEL = { head: 'HEAD', torso: 'TORSO', arm_l: 'ARM · LEFT', arm_r: 'ARM · RIGHT', legs: 'LEGS' };

const $ = (sel) => document.querySelector(sel);
const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const srcLabel = (e) => SRC_LABEL[sourceOf(e)] || sourceOf(e) || '—';
const entryName = (e) => e.name || e.id || e.part_id || '(unnamed)';
const resolver = (partId) => { const e = getEntry(ENTRIES, partId); return e ? spineSlotOf(e) : null; };

function toast(msg) {
  const t = $('#toast'); t.textContent = msg; t.classList.remove('hidden');
  setTimeout(() => t.classList.add('hidden'), 2200);
}
function stash() {
  const all = {};
  for (const [n, st] of Object.entries(attires)) all[n] = P.toSuiteRecord(st);
  try { localStorage.setItem(LS_STASH, JSON.stringify(all)); } catch { /* storage full/blocked: session still works */ }
}
function save() {
  stash();
  try { localStorage.setItem(LS_SUITE, JSON.stringify(P.toSuiteRecord(S))); } catch { /* see stash */ }
  toast(`Saved ${S.name} · ${S.attire} — the game reads this profile`);
  renderAll();
}

/* ---------------- top bar + stage ---------------- */
function renderTop() {
  $('#fighterName').textContent = S.name;
  $('#attireChips').innerHTML = [1, 2, 3, 4].map((n) =>
    `<button type="button" data-action="attire" data-n="${n}" class="${n === attireNo ? 'on' : ''}">A${n}</button>`).join('');
  if (COUNTS) {
    $('#catalogLine').textContent =
      `${COUNTS.total.toLocaleString()} parts wired · ${COUNTS.ready.toLocaleString()} equippable · ${COUNTS.mapped.toLocaleString()} on the Tekken spine · 5 catalogs`;
  }
}
function renderStage() {
  $('#medallion').textContent = (S.name || 'C').trim().charAt(0).toUpperCase() || 'C';
  $('#stageTitle').textContent = `${S.name} — ${S.attire.replace('attire', 'Attire ')}`;
  const chips = SPINE.filter((sp) => S.equipped[sp.id]).map((sp) =>
    `<span class="chip"><b>${esc(sp.title)}:</b> ${esc(S.equipped[sp.id].name)}</span>`).join('');
  $('#equippedChips').innerHTML = chips || '<span class="chip empty">Nothing equipped yet — open ATTIRE</span>';
  const morphed = Object.entries(S.morphs).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1])).slice(0, 4);
  $('#morphBars').innerHTML = morphed.map(([id, v]) => {
    const def = [...BODY_MORPHS, ...FACE_SHAPE_MORPHS].find((m) => m.id === id);
    const pct = Math.round(((v + 1) / 2) * 100);
    return `<div class="morph-bar"><span>${esc(def?.label || id)}</span><span class="track"><span class="fill" style="left:${v < 0 ? pct : 50}%;width:${Math.abs(pct - 50)}%"></span></span><span>${v > 0 ? '+' : ''}${v.toFixed(2)}</span></div>`;
  }).join('');
  const dots = [S.body.skin_tone, S.colors.hair].filter(Boolean)
    .map((c) => `<span class="dot" style="background:${esc(c)}"></span>`).join('');
  $('#stageMeta').innerHTML =
    `${dots} ${esc(S.body.body_type)} · ${Object.keys(S.equipped).length} parts equipped · ${S.region_swaps.length} piece swap(s) · ${S.textures.length} ink layer(s) · wardrobe ${Object.keys(S.wardrobe).length}/10`;
}

/* ---------------- shared bits ---------------- */
function sliderRow(kind, id, label, value, min, max, step) {
  return `<div class="slider-row"><label for="sl-${kind}-${id}">${esc(label)}</label>` +
    `<input type="range" id="sl-${kind}-${id}" data-kind="${kind}" data-id="${id}" min="${min}" max="${max}" step="${step}" value="${value}">` +
    `<output id="out-${kind}-${id}">${Number(value).toFixed(step >= 1 ? 0 : 2)}</output></div>`;
}
function morphSliders(list) {
  return list.map((m) => sliderRow('morph', m.id, m.label, S.morphs[m.id] || 0, m.range[0], m.range[1], 0.05)).join('');
}
function badge(e) {
  const r = readinessOf(e);
  return `<span class="badge ${r}">${RD_LABEL[r]}</span> <span class="badge src">${esc(srcLabel(e))}</span>`;
}
function itemRow(e) {
  const spine = spineSlotOf(e);
  const equipped = S.equipped[spine]?.part_id === (e.id || e.part_id);
  return `<button type="button" class="item ${equipped ? 'equipped' : ''}" data-action="detail" data-id="${esc(e.id || e.part_id)}">` +
    `<span class="nm">${esc(entryName(e))}<span class="id">${esc(e.id || e.part_id)}${equipped ? ' · EQUIPPED' : ''}</span></span>${badge(e)}</button>`;
}
function filteredEntries(spine) {
  let list = ENTRIES.filter((e) => spineSlotOf(e) === spine);
  if (ui.src !== 'all') list = list.filter((e) => sourceOf(e) === ui.src);
  if (ui.search) {
    const q = ui.search.toLowerCase();
    list = list.filter((e) => entryName(e).toLowerCase().includes(q) || (e.id || '').toLowerCase().includes(q));
  }
  list.sort((a, b) => RD_RANK[readinessOf(a)] - RD_RANK[readinessOf(b)] || entryName(a).localeCompare(entryName(b)));
  return list;
}

/* ---------------- BODY ---------------- */
function renderBody() {
  $('#sheet').innerHTML = `
    <h2>BODY TYPE</h2>
    <div class="row">${P.BODY_TYPE_NAMES.map((t) =>
      `<button type="button" class="pick ${S.body.body_type === t ? 'on' : ''}" data-action="bodytype" data-v="${esc(t)}">${esc(t)}</button>`).join('')}</div>
    <h2>SKIN TONE</h2>
    <div class="swatches">${P.SKIN_TONES.map((c) =>
      `<button type="button" class="swatch ${S.body.skin_tone === c ? 'on' : ''}" style="background:${c}" data-action="skin" data-v="${c}" aria-label="Skin tone ${c}"></button>`).join('')}
      <input type="color" id="skinCustom" value="${esc(S.body.skin_tone)}" aria-label="Custom skin tone"></div>
    <p class="note">Skin tone is Tekken's group −237 settings row — a single tap, like No Mercy's 8 tones.</p>
    <h2>BODY MORPHS</h2>
    ${morphSliders(BODY_MORPHS)}
    <h2>COLORS</h2>
    <div class="slider-row"><label for="hairColor">Hair color</label><input type="color" id="hairColor" value="${esc(S.colors.hair || '#201409')}"><output></output></div>
    <div class="slider-row"><label for="skinColor">Skin (exact)</label><input type="color" id="skinColor" value="${esc(S.body.skin_tone)}"><output></output></div>`;
}

/* ---------------- FACE ---------------- */
function renderFace() {
  const eyes = ENTRIES.filter((e) => spineSlotOf(e) === 'eyes');
  $('#sheet').innerHTML = `
    <h2>FACE MORPHS</h2>
    ${morphSliders(FACE_SHAPE_MORPHS)}
    <h2>EYES</h2>
    <p class="note">Eyes are real parts in this suite (owner law — never painted-on decals). The mesh eye lenses live under ATTIRE → Glasses today; the variants below are the legacy texture eyes, labeled as such, and apply as eye layers.</p>
    <div class="item-list">${eyes.map((e) => `
      <div class="item"><span class="nm">${esc(entryName(e))}<span class="id">${esc(e.id)} · legacy texture variant</span></span>${badge(e)}
      <button type="button" class="pick" data-action="eyelayer" data-id="${esc(e.id)}">ADD</button></div>`).join('')}</div>
    <h2>HAIR</h2>
    <p class="note">Hairstyles are parts: ATTIRE → Hairstyle (${COUNTS?.per.hair.ready ?? 0} ready today). Hair color is on the BODY tab.</p>`;
}

/* ---------------- ATTIRE ---------------- */
function renderAttire() {
  if (!ui.cat) {
    $('#sheet').innerHTML = `<h2>ATTIRE — TEKKEN SLOT SPINE</h2>
      <p class="note">Tekken's 16 slots in menu order, T6 sub-slots restored, every teardown source mixed in. Tap a slot to browse its real catalog parts.</p>
      <div class="cat-list">${SPINE.map((sp) => {
        const c = COUNTS.per[sp.id];
        const eq = S.equipped[sp.id];
        return `<button type="button" class="cat-btn" data-action="cat" data-v="${sp.id}">
          <span class="t">${esc(sp.title)}${eq ? ` — ${esc(eq.name)}` : ''}</span>
          <span class="c">${c.total} parts · <b>${c.ready} ready</b>${c.preview ? ` · ${c.preview} preview` : ''}${c.blocked ? ` · ${c.blocked} blocked` : ''}</span></button>`;
      }).join('')}</div>
      <p class="note">${COUNTS.unmapped.toLocaleString()} more cataloged parts (Def Jam unknown family + WMXIX palettes) are not on the spine yet — their family codes are still being decoded. They are counted, never hidden.</p>`;
    return;
  }
  const sp = SPINE_BY_ID[ui.cat];
  const list = filteredEntries(ui.cat);
  // Source filters only for sources that meaningfully populate this slot —
  // the long tail of per-fighter libraries stays reachable via All + search.
  const srcCounts = {};
  for (const e of ENTRIES) if (spineSlotOf(e) === ui.cat) srcCounts[sourceOf(e)] = (srcCounts[sourceOf(e)] || 0) + 1;
  const sources = Object.entries(srcCounts).filter(([, n]) => n >= 5).sort((a, b) => b[1] - a[1]).map(([s]) => s);
  $('#sheet').innerHTML = `
    <button type="button" class="pick" data-action="back-cat">‹ ALL SLOTS</button>
    <h2>${esc(sp.title).toUpperCase()}</h2>
    <div class="toolbar">
      <input type="search" id="partSearch" placeholder="Search ${list.length} parts…" value="${esc(ui.search)}">
      <div class="filters">
        <button type="button" data-action="src" data-v="all" class="${ui.src === 'all' ? 'on' : ''}">All sources</button>
        ${sources.map((s) => `<button type="button" data-action="src" data-v="${esc(s)}" class="${ui.src === s ? 'on' : ''}">${esc(SRC_LABEL[s] || s)}</button>`).join('')}
      </div>
    </div>
    <p class="note">Showing ${Math.min(CAP, list.length)} of ${list.length}. Tap a part to preview its record, then EQUIP — conflicts ask first, like Tekken.</p>
    <div class="item-list">${list.slice(0, CAP).map(itemRow).join('') || '<p class="note">No parts match.</p>'}</div>`;
  const inp = $('#partSearch');
  inp?.addEventListener('input', () => { ui.search = inp.value; renderSheetKeepScroll(); });
}

/* ---------------- PIECES (round 2: Tekken-style region swaps) ---------------- */
function renderPieces() {
  if (ui.swapRegion) {
    const region = ui.swapRegion;
    let list = SWAP_SOURCES.filter((x) => x.path && x.path !== S.base_glb);
    if (ui.swapSearch) {
      const q = ui.swapSearch.toLowerCase();
      list = list.filter((x) => x.path.toLowerCase().includes(q));
    }
    list.sort((a, b) => a.path.localeCompare(b.path));
    $('#sheet').innerHTML = `
      <button type="button" class="pick" data-action="swap-back">‹ REGIONS</button>
      <h2>${REGION_LABEL[region]} — PICK A SOURCE</h2>
      <div class="toolbar"><input type="search" id="swapSearch" placeholder="Search ${list.length} roster models…" value="${esc(ui.swapSearch)}"></div>
      <p class="note">Tap a fighter's model to take its ${REGION_LABEL[region]} — Tekken cuts at the bone: the region is cut from them and from you, fit to your neck/anchor point, and re-skinned onto your skeleton at bake. Your original comes back by removing the swap and re-baking.</p>
      <div class="item-list">${list.slice(0, CAP).map((x) => `
        <button type="button" class="item" data-action="swap-pick" data-path="${esc(x.path)}" data-fighter="${esc(x.fighter || '')}" data-attire="${esc(x.attire || '')}">
        <span class="nm">${esc(x.fighter || '?')} · ${esc(x.attire || '')}<span class="id">${esc(x.file)}${x.skinned === false ? ' · unskinned (head only)' : ''}${x.skinned ? ` · ${x.bones} bones` : ''}</span></span></button>`).join('') || '<p class="note">No sources loaded — region-sources.json missing?</p>'}</div>`;
    const inp = $('#swapSearch');
    inp?.addEventListener('input', () => { ui.swapSearch = inp.value; renderSheetKeepScroll(); });
    return;
  }
  $('#sheet').innerHTML = `
    <h2>PIECE SWAPS — CUT &amp; GRAFT</h2>
    <p class="note">Tekken-style: take a whole region from another fighter. WWE calls it body-part swapping; here it saves into this attire's record and the bake does the cut. One source per region.</p>
    <div class="item-list">${P.SWAP_REGIONS.map((r) => {
      const cur = S.region_swaps.find((x) => x.region === r);
      return `<div class="item"><span class="nm">${REGION_LABEL[r]}<span class="id">${cur ? `${esc(cur.from_fighter || '')} · ${esc(cur.from_attire || '')} — ${esc(cur.from_glb.split('/').pop())}` : 'original (yours)'}</span></span>
      <button type="button" class="pick" data-action="swap-open" data-region="${r}">${cur ? 'CHANGE' : 'SWAP'}</button>
      ${cur ? `<button type="button" class="pick" data-action="swap-remove" data-region="${r}">RESTORE</button>` : ''}</div>`;
    }).join('')}</div>
    <h2>BASE MODEL</h2>
    <div class="slider-row"><label for="hideHairChk">Hide base hair (bake)</label>
    <input type="checkbox" id="hideHairChk" ${S.hide_base_hair ? 'checked' : ''} style="width:32px;height:32px"><output></output></div>
    <p class="note">For models whose own hair is a separate named mesh: the bake leaves it out of the game model so an attached hairstyle sits clean. Your base file is never touched.</p>`;
  $('#hideHairChk')?.addEventListener('change', (e) => { P.setHideBaseHair(S, e.target.checked); renderStage(); });
}

/* ---------------- INK ---------------- */
function inkPool() {
  let list = ENTRIES.filter((e) => ['ink', 'eyes'].includes(spineSlotOf(e)) && (e.texture || e.image || e.asset));
  if (ui.search) {
    const q = ui.search.toLowerCase();
    list = list.filter((e) => entryName(e).toLowerCase().includes(q) || (e.id || '').toLowerCase().includes(q));
  }
  list.sort((a, b) => RD_RANK[readinessOf(a)] - RD_RANK[readinessOf(b)] || entryName(a).localeCompare(entryName(b)));
  return list;
}
function renderInk() {
  if (ui.inkPick) {
    const list = inkPool();
    $('#sheet').innerHTML = `
      <button type="button" class="pick" data-action="ink-back">‹ LAYERS</button>
      <h2>PICK AN IMAGE</h2>
      <div class="toolbar"><input type="search" id="inkSearch" placeholder="Search decals & eye images…" value="${esc(ui.search)}"></div>
      <p class="note">Decal-library images and eye images. Bigger texture sets (WMXIX's 1,477 face-paint textures) apply from ATTIRE → Face Paint as parts.</p>
      <div class="item-list">${list.slice(0, CAP).map((e) => `
        <button type="button" class="item" data-action="ink-pick" data-id="${esc(e.id)}">
        <span class="nm">${esc(entryName(e))}<span class="id">${esc(e.id)}</span></span>${badge(e)}</button>`).join('')}</div>`;
    const inp = $('#inkSearch');
    inp?.addEventListener('input', () => { ui.search = inp.value; renderSheetKeepScroll(); });
    return;
  }
  const sel = ui.inkEntry ? getEntry(ENTRIES, ui.inkEntry) : null;
  $('#sheet').innerHTML = `
    <h2>TATTOOS / IMAGE LAYERS</h2>
    <p class="note">Layers stack in order — each is placed with a rectangle on the part's texture (the decal canvas, extension D6). They save into the profile's texture list.</p>
    <div class="item-list">${S.textures.map((t, i) => `
      <div class="item"><span class="nm">${esc(t.part_id)}<span class="id">${esc(t.kind)} · ${esc(t.image)}${t.rect ? ` · rect ${t.rect.map((n) => n.toFixed(2)).join(', ')}` : ''}</span></span>
      <button type="button" class="pick" data-action="layer-del" data-i="${i}">REMOVE</button></div>`).join('') || '<p class="note">No layers yet.</p>'}</div>
    <div class="actions"><button type="button" class="btn" data-action="ink-open">+ ADD LAYER</button></div>
    ${sel ? `<h2>PLACE: ${esc(entryName(sel))}</h2>
      ${['X', 'Y', 'Width', 'Height'].map((lbl, i) => sliderRow('rect', String(i), lbl, ui.inkRect[i], 0, 1, 0.01)).join('')}
      <div class="actions"><button type="button" class="btn primary" data-action="ink-add" data-id="${esc(sel.id)}">ADD THIS LAYER</button></div>` : ''}`;
}

/* ---------------- WARDROBE ---------------- */
function renderWardrobe() {
  $('#sheet').innerHTML = `
    <h2>TITLE</h2>
    <div class="row" style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
      <input type="text" id="titleA" placeholder="Title A — e.g. RAGING" value="${esc(S.title[0])}">
      <input type="text" id="titleB" placeholder="Title B — e.g. BEAST" value="${esc(S.title[1])}">
    </div>
    <h2>WARDROBE — 10 LOOK SLOTS</h2>
    <p class="note">DOA-style snapshots on top of No Mercy's attire slots: 4 attires × 10 looks = 40 saved looks per fighter. Saving writes the selected slot only — nothing is ever overwritten silently.</p>
    <div class="slotgrid">${[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => S.wardrobe[String(n)]
      ? `<button type="button" class="pick on" data-action="ward-load" data-n="${n}">LOOK ${n} ✓</button>`
      : `<button type="button" class="pick" data-action="ward-save" data-n="${n}">SAVE → ${n}</button>`).join('')}</div>
    <p class="note">Tap a filled look to load it. Overwriting is always an explicit tap on the slot it replaces:</p>
    <div class="row">${[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].filter((n) => S.wardrobe[String(n)])
      .map((n) => `<span style="display:flex;gap:6px"><button type="button" class="pick" data-action="ward-save" data-n="${n}">Overwrite ${n}</button><button type="button" class="pick" data-action="ward-clear" data-n="${n}">Clear ${n}</button></span>`).join('') || '<span class="note">No looks saved yet.</span>'}</div>`;
  $('#titleA').addEventListener('input', (e) => { S.title[0] = e.target.value.toUpperCase(); renderStage(); });
  $('#titleB').addEventListener('input', (e) => { S.title[1] = e.target.value.toUpperCase(); renderStage(); });
}

/* ---------------- PROFILE ---------------- */
function renderProfile() {
  const rec = P.toSuiteRecord(S);
  $('#sheet').innerHTML = `
    <h2>PROFILE</h2>
    <div class="slider-row"><label for="nameInput">Name</label><input type="text" id="nameInput" value="${esc(S.name)}"><output></output></div>
    <div class="slider-row"><label for="archSel">Style</label>
      <select id="archSel">${P.ARCHETYPES.map((a) => `<option ${S.fighting_style.archetype === a ? 'selected' : ''}>${a}</option>`).join('')}</select><output></output></div>
    ${sliderRow('param', 'aggression', 'Aggression', S.fighting_style.aggression, 0, 10, 1)}
    ${sliderRow('param', 'arms_offense', 'Arm offense', S.parameters.arms_offense, 0, 100, 1)}
    ${sliderRow('param', 'body_defense', 'Body defense', S.parameters.body_defense, 0, 100, 1)}
    <h2>SAVE / EXPORT</h2>
    <div class="actions" style="display:grid;gap:8px">
      <button type="button" class="btn primary" data-action="save">SAVE PROFILE</button>
      <button type="button" class="btn" data-action="export">EXPORT customization.json</button>
    </div>
    <p class="note">SAVE writes the record the game reads (<i>wh_creation_suite_v1</i>) plus the per-attire stash. EXPORT downloads the per-attire file the bake path consumes — the same object, two shapes, never drifting.</p>
    <details class="jsonbox"><summary>Saved profile (live)</summary><pre>${esc(JSON.stringify(rec, null, 1))}</pre></details>`;
  $('#nameInput').addEventListener('input', (e) => { S.name = e.target.value.toUpperCase() || 'CUSTOM'; renderTop(); renderStage(); });
  $('#archSel').addEventListener('change', (e) => { S.fighting_style.archetype = e.target.value; });
}

/* ---------------- part detail sheet ---------------- */
let detailEntry = null;
function openDetail(entry) {
  detailEntry = entry;
  const spine = spineSlotOf(entry);
  const sp = SPINE_BY_ID[spine];
  const r = readinessOf(entry);
  const eq = S.equipped[spine];
  const isEq = eq?.part_id === (entry.id || entry.part_id);
  const asset = entry.glb || entry.texture || entry.image || entry.asset || entry.file || '';
  const statusLine = entry.status || entry.conversion?.status || entry.conversion || '';
  const suiteSlot = eq?.suite_slot || entry.suite_slot || spine;
  const chans = S.item_colors[suiteSlot] || [];
  const fin = S.finishes[suiteSlot] || {};
  $('#detail').innerHTML = `
    <h3>${esc(entryName(entry))}</h3>
    <div>${badge(entry)} ${sp ? `<span class="badge src">${esc(sp.title)}</span>` : '<span class="badge src">UNMAPPED</span>'}</div>
    <p class="meta">id ${esc(entry.id || entry.part_id)}<br>
    ${asset ? `asset ${esc(asset)}<br>` : ''}${entry.origin_file ? `origin ${esc(entry.origin_file)}<br>` : ''}
    ${statusLine ? `status ${esc(statusLine)}<br>` : ''}${entry.rarity != null ? `rarity ${esc(entry.rarity)} · cost ${esc(entry.ItemCost ?? entry.cost ?? '—')}<br>` : ''}</p>
    ${r === 'preview-only' ? '<p class="note">This part converted as a POINTS pool — its vertex order is not proven yet, so it cannot be equipped. It stays visible and counted until the mesh proof lands.</p>' : ''}
    ${r === 'blocked' ? `<p class="note">Blocked: ${esc(statusLine || 'conversion pending')}. Shown for depth — it equips automatically the day its conversion lands.</p>` : ''}
    ${isEq ? `
      <h2>PLACEMENT (PartPoser-style)</h2>
      ${sliderRow('place', 'px', 'Pos X (m)', eq.placement.px, -0.5, 0.5, 0.01)}
      ${sliderRow('place', 'py', 'Pos Y (m)', eq.placement.py, -0.5, 0.5, 0.01)}
      ${sliderRow('place', 'pz', 'Pos Z (m)', eq.placement.pz, -0.5, 0.5, 0.01)}
      ${sliderRow('place', 'rx', 'Pitch °', eq.placement.rx, -180, 180, 1)}
      ${sliderRow('place', 'ry', 'Yaw °', eq.placement.ry, -180, 180, 1)}
      ${sliderRow('place', 'rz', 'Roll °', eq.placement.rz, -180, 180, 1)}
      ${sliderRow('place', 's', 'Scale', eq.placement.s, 0.25, 2.5, 0.05)}
      ${sliderRow('place', 'sx', 'Scale X', eq.placement.sx ?? eq.placement.s, 0.25, 2.5, 0.05)}
      ${sliderRow('place', 'sy', 'Scale Y', eq.placement.sy ?? eq.placement.s, 0.25, 2.5, 0.05)}
      ${sliderRow('place', 'sz', 'Scale Z', eq.placement.sz ?? eq.placement.s, 0.25, 2.5, 0.05)}
      <h2>NUDGE (tap — fine steps)</h2>
      <div class="row">${[['px', 'X', 0.01], ['py', 'Y', 0.01], ['pz', 'Z', 0.01]].map(([k, lbl, st]) =>
        `<span style="display:flex;gap:4px;align-items:center"><b>${lbl}</b><button type="button" class="pick" data-action="nudge" data-nudge="${k}:${-st}">−</button><button type="button" class="pick" data-action="nudge" data-nudge="${k}:${st}">+</button></span>`).join('')}</div>
      <div class="row">${[['rx', 'Pitch', 1], ['ry', 'Yaw', 1], ['rz', 'Roll', 1]].map(([k, lbl, st]) =>
        `<span style="display:flex;gap:4px;align-items:center"><b>${lbl}</b><button type="button" class="pick" data-action="nudge" data-nudge="${k}:${-st}">−</button><button type="button" class="pick" data-action="nudge" data-nudge="${k}:${st}">+</button></span>`).join('')}</div>
      <div class="actions"><button type="button" class="btn" data-action="place-reset">RESET PLACEMENT</button></div>
      <p class="note">Placement is bone-local and exact: what you set here is what the bake applies — 0 is the part's native seat on the bone.</p>
      <div class="slider-row"><label for="mirrorChk">Mirror L/R</label><input type="checkbox" id="mirrorChk" ${S.mirrored[suiteSlot] ? 'checked' : ''} style="width:32px;height:32px"><output></output></div>
      <h2>COLOR CHANNELS (Tekken: up to 5)</h2>
      <div class="row">${[0, 1, 2, 3, 4].map((i) =>
        `<input type="color" data-chan="${i}" value="${esc(chans[i] || '#ffffff')}" aria-label="Color channel ${i + 1}">`).join('')}</div>
      <h2>FINISH (extension D2)</h2>
      ${sliderRow('finish', 'roughness', 'Roughness', fin.roughness ?? 0.5, 0, 1, 0.05)}
      ${sliderRow('finish', 'metalness', 'Metalness', fin.metalness ?? 0, 0, 1, 0.05)}
      <div class="slider-row"><label for="finishTint">Tint</label><input type="color" id="finishTint" value="${esc(fin.tint || '#ffffff')}"><output></output></div>` : ''}
    <div class="actions" id="detailActions">
      ${isEq ? `<button type="button" class="btn danger" data-action="remove-part">REMOVE PART</button>`
             : `<button type="button" class="btn primary" data-action="equip" ${isEquippable(entry) ? '' : 'disabled'}>${isEquippable(entry) ? 'EQUIP' : 'NOT EQUIPPABLE YET'}</button>`}
      <button type="button" class="btn" data-action="detail-close">CLOSE</button>
    </div>
    <div id="conflictBox"></div>`;
  $('#overlay').classList.remove('hidden');
}
function closeDetail() { detailEntry = null; $('#overlay').classList.add('hidden'); }
function tryEquip(force) {
  const spine = spineSlotOf(detailEntry);
  const res = P.equip(S, detailEntry, spine, { force });
  if (!res.ok) {
    $('#conflictBox').innerHTML = `
      <p class="note"><b>CONFLICTS WITH:</b> ${res.conflicts.map((c) => `${esc(c.name)} (${esc(SPINE_BY_ID[c.spine]?.title || c.spine)})`).join(', ')}</p>
      <div class="actions"><button type="button" class="btn danger" data-action="equip-force">REPLACE</button>
      <button type="button" class="btn" data-action="conflict-cancel">CANCEL</button></div>`;
    return;
  }
  toast(`Equipped ${entryName(detailEntry)}`);
  closeDetail(); renderAll();
}

/* ---------------- render dispatch ---------------- */
function renderSheet() {
  ({ body: renderBody, face: renderFace, attire: renderAttire, pieces: renderPieces, ink: renderInk, wardrobe: renderWardrobe, profile: renderProfile })[ui.tab]();
}
function renderSheetKeepScroll() {
  const active = document.activeElement;
  const id = active?.id, pos = active?.selectionStart;
  renderSheet();
  if (id) { const n = document.getElementById(id); if (n) { n.focus(); try { n.setSelectionRange(pos, pos); } catch { /* not a text field */ } } }
}
function renderAll() { renderTop(); renderStage(); renderSheet(); }

/* ---------------- events ---------------- */
document.addEventListener('click', (ev) => {
  const b = ev.target.closest('[data-action]');
  if (b) {
    const a = b.dataset.action;
    if (a === 'attire') { stash(); attireNo = Number(b.dataset.n); S = attires[attireNo]; renderAll(); }
    else if (a === 'bodytype') { P.setBodyType(S, b.dataset.v); renderAll(); }
    else if (a === 'skin') { P.setSkinTone(S, b.dataset.v); renderAll(); }
    else if (a === 'cat') { ui.cat = b.dataset.v; ui.search = ''; ui.src = 'all'; renderSheet(); }
    else if (a === 'back-cat') { ui.cat = null; renderSheet(); }
    else if (a === 'src') { ui.src = b.dataset.v; renderSheetKeepScroll(); }
    else if (a === 'detail') { const e = getEntry(ENTRIES, b.dataset.id); if (e) openDetail(e); }
    else if (a === 'detail-close' || a === 'conflict-cancel') closeDetail();
    else if (a === 'equip') tryEquip(false);
    else if (a === 'equip-force') tryEquip(true);
    else if (a === 'remove-part') { P.unequip(S, spineSlotOf(detailEntry)); closeDetail(); renderAll(); }
    else if (a === 'eyelayer') { const e = getEntry(ENTRIES, b.dataset.id); P.addLayer(S, e, {}); toast('Eye layer added — see INK'); renderAll(); }
    else if (a === 'swap-open') { ui.swapRegion = b.dataset.region; ui.swapSearch = ''; renderSheet(); }
    else if (a === 'swap-back') { ui.swapRegion = null; renderSheet(); }
    else if (a === 'swap-remove') { P.removeRegionSwap(S, b.dataset.region); toast('Swap removed — re-bake restores the original'); renderAll(); }
    else if (a === 'swap-pick') {
      P.setRegionSwap(S, { region: ui.swapRegion, from_glb: b.dataset.path, from_fighter: b.dataset.fighter || null, from_attire: b.dataset.attire || null });
      toast(`${REGION_LABEL[ui.swapRegion]} swap set — applies at bake`);
      ui.swapRegion = null; renderAll();
    }
    else if (a === 'nudge' && detailEntry) {
      const [k, d] = b.dataset.nudge.split(':');
      const spine = spineSlotOf(detailEntry);
      const cur = S.equipped[spine]?.placement?.[k] ?? (k === 's' ? 1 : 0);
      P.setPlacement(S, spine, { [k]: Math.round((cur + Number(d)) * 1000) / 1000 });
      openDetail(detailEntry); renderStage();
    }
    else if (a === 'place-reset' && detailEntry) {
      const spine = spineSlotOf(detailEntry);
      P.setPlacement(S, spine, { px: 0, py: 0, pz: 0, rx: 0, ry: 0, rz: 0, s: 1, sx: 1, sy: 1, sz: 1 });
      openDetail(detailEntry); renderStage();
    }
    else if (a === 'ink-open') { ui.inkPick = true; ui.search = ''; renderSheet(); }
    else if (a === 'ink-back') { ui.inkPick = false; renderSheet(); }
    else if (a === 'ink-pick') { ui.inkEntry = b.dataset.id; ui.inkPick = false; renderSheet(); }
    else if (a === 'ink-add') { const e = getEntry(ENTRIES, b.dataset.id); P.addLayer(S, e, { rect: [...ui.inkRect] }); ui.inkEntry = null; toast('Layer added'); renderAll(); }
    else if (a === 'layer-del') { P.removeLayer(S, Number(b.dataset.i)); renderAll(); }
    else if (a === 'ward-save') { P.saveSnapshot(S, Number(b.dataset.n)); toast(`Look ${b.dataset.n} saved`); renderAll(); }
    else if (a === 'ward-load') { P.loadSnapshot(S, Number(b.dataset.n)); toast(`Look ${b.dataset.n} loaded`); renderAll(); }
    else if (a === 'ward-clear') { delete S.wardrobe[b.dataset.n]; renderAll(); }
    else if (a === 'save') save();
    else if (a === 'export') {
      const blob = new Blob([JSON.stringify(P.toCustomizationJson(S), null, 1)], { type: 'application/json' });
      const aEl = document.createElement('a');
      aEl.href = URL.createObjectURL(blob);
      aEl.download = `customization-${S.fighter}-${S.attire}.json`;
      aEl.click(); URL.revokeObjectURL(aEl.href);
      toast('Exported customization.json');
    }
  }
  if (ev.target.id === 'overlay') closeDetail();
});
document.addEventListener('input', (ev) => {
  const t = ev.target;
  if (t.id === 'skinCustom' || t.id === 'skinColor') { P.setSkinTone(S, t.value); renderStage(); return; }
  if (t.id === 'hairColor') { P.setColor(S, 'hair', t.value); renderStage(); return; }
  const kind = t.dataset?.kind, id = t.dataset?.id;
  if (!kind) return;
  const v = Number(t.value);
  const out = document.getElementById(`out-${kind}-${id}`);
  if (out) out.textContent = v.toFixed(Number(t.step) >= 1 ? 0 : 2);
  if (kind === 'morph') { P.setMorph(S, id, v); renderStage(); }
  else if (kind === 'rect') { ui.inkRect[Number(id)] = v; }
  else if (kind === 'param') {
    if (id === 'aggression') S.fighting_style.aggression = v;
    else S.parameters[id] = v;
  } else if (kind === 'place' && detailEntry) {
    P.setPlacement(S, spineSlotOf(detailEntry), { [id]: v }); renderStage();
  } else if (kind === 'finish' && detailEntry) {
    P.setFinish(S, spineSlotOf(detailEntry), { [id]: v });
  }
});
document.addEventListener('change', (ev) => {
  const t = ev.target;
  if (t.id === 'mirrorChk' && detailEntry) { P.setMirrored(S, spineSlotOf(detailEntry), t.checked); }
  if (t.id === 'finishTint' && detailEntry) { P.setFinish(S, spineSlotOf(detailEntry), { tint: t.value }); }
  if (t.dataset?.chan != null && detailEntry) {
    const spine = spineSlotOf(detailEntry);
    const inputs = [...document.querySelectorAll('#detail [data-chan]')].map((i) => i.value);
    P.setItemColors(S, spine, inputs);
    toast('Color channels saved to the profile');
  }
});
$('#tabbar').addEventListener('click', (ev) => {
  const b = ev.target.closest('[data-tab]'); if (!b) return;
  ui.tab = b.dataset.tab;
  document.querySelectorAll('#tabbar button').forEach((x) => x.classList.toggle('on', x === b));
  renderSheet();
});
$('#saveBtn').addEventListener('click', save);

/* ---------------- boot ---------------- */
(async function boot() {
  try {
    const datas = await Promise.all(CATALOG_URLS.map(async (u) => {
      const r = await fetch(u);
      if (!r.ok) throw new Error(`${u} -> ${r.status}`);
      return r.json();
    }));
    ENTRIES = mergeCatalogs(...datas);
    try {
      const rs = await fetch('../../../customization/region-sources.json');
      if (rs.ok) SWAP_SOURCES = (await rs.json()).sources || [];
    } catch { /* swaps tab explains itself when the index is missing */ }
    COUNTS = spineCounts(ENTRIES);
    let stashRecs = null;
    try { stashRecs = JSON.parse(localStorage.getItem(LS_STASH) || 'null'); } catch { /* fresh */ }
    for (const n of [1, 2, 3, 4]) {
      attires[n] = stashRecs?.[n]
        ? P.attachParts(P.fromSuiteRecord(stashRecs[n]), resolver)
        : P.createState({ attire: `attire${n}` });
    }
    if (!stashRecs) {
      try {
        const rec = JSON.parse(localStorage.getItem(LS_SUITE) || 'null');
        if (rec) {
          const n = Math.min(4, Math.max(1, Number(String(rec.attire || 'attire1').replace('attire', '')) || 1));
          attires[n] = P.attachParts(P.fromSuiteRecord(rec), resolver);
          attireNo = n;
        }
      } catch { /* fresh */ }
    }
    S = attires[attireNo];
    renderAll();
  } catch (err) {
    $('#catalogLine').textContent = `Catalog load failed: ${err.message} — serve the repo over HTTP (the suite reads the real catalog JSONs).`;
  }
})();

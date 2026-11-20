/* ============================================================
   WESTERN HEART — Moveset Editor screen (in-game)
   SKELETON — 2026-11-20. EDITOR-SPEC §2 (lane-c-design/EDITOR-SPEC.md).

   S1 editor main · S2 library modal · S3 slot detail / input-edit ·
   S4 save sheet + named-document store. Portrait-first, phone layout
   (B §4: 480px panels, >=44px targets, safe-area insets, 12px
   scroll-drag guard via delegated clicks, lists scroll inside a
   fixed card).

   GROUNDED IN (nothing here is invented):
   - Screen hook: the #screen-movelist pattern (B §2, B §5a) — a
     .screen section + screens-map entry + delegated data-action.
     The section is created at import time by ensureScreen() (the
     menus.js buildOverlays() precedent: overlays are injected by JS,
     not static in index.html), so no index.html edit is needed.
     Styles ride in an injected <style> (the movelist-ui.js
     _ensureStyle precedent), so no styles.css edit is needed.
   - Slot list: one row per INPUT, resolved by resolveMoveKey() —
     loadout > default slots (main.js renderMovelist, B §5a), grouped
     in MOVESET_GROUPS order (main.js:1067, copied here — main.js
     cannot export it without a module cycle).
   - Swap flow: the Creation Suite MOVESET tab, ported verbatim
     (suite.js renderMoveset :2727 / openMoveLibrary :2830): slot-first,
     SAME INPUT / ALL MOVES / OTHER FIGHTER tabs, MS_CATS chips,
     search, 40/page MORE, per-slot RESET TO DEFAULT, RESET ALL EDITS,
     assign via setLoadoutSlot(fid, n, srcId===fid ? k : srcId+'::'+k),
     BASE MOVESET selector defaulting to 'demonio' for the custom
     fighter, RESET ALL deleting every loadout entry except __base.
   - Positions: the resolver prefix list (A §3a/§3b) via the rebuilt
     moveset-editor.js engine. Positions with data but no resolver
     path (GROUNDED./FUFT./CH./TACKLE. etc.) get no chip (A §8.1).
   - Save: ONE canonical save (wh_moveset_loadout_v1, the only thing
     a fight reads) + the named-document store (wh_moveset_editor_v1,
     EDITOR-SPEC §3). A named moveset plays ONLY by compiling into
     the loadout (compileToLoadout). toManifest()->assembleFighter()
     is RETIRED and never called here.

   WHAT IS HONESTLY EMPTY IN THIS SKELETON (waits on the fix):
   - S2 library CONTENT: the modal shell (tabs/chips/search/40-page)
     is built, but it reads ONLY the REGENERATED library index
     (game/data/moveset-library/index.json, EDITOR-SPEC §4b — header
     counts block + moves keyed by fighter::key). The index on disk
     today is the pre-fix banks index (moveset-library/v1, built
     2026-10-22), so S2 shows an honest empty state and NEVER lists
     moves from pre-fix files. When the fix regenerates the index,
     S2 lights up with no code change.
   - Live move preview: v1 shows move DATA in S3 (B §7.5). No preview
     surface exists in-game; the suite viewport pattern is follow-up.
   - Demonio form switching: the four form files are four separate
     fighters in the picker (A §6); no in-editor form switch.
   - The 8 owner decisions (EDITOR-SPEC §6d) are NOT decided here:
     no rename/duplicate in S4, no select-screen EDIT affordance,
     no VF/DOA __base, no UNMAPPED assignability call, no movelist
     canon name, movelist-ui.js is left untouched.

   Usage (main.js): import { openMovesetEditor, closeMovesetEditor }
     from './moveset-editor-ui.js' — the import itself creates the
     screen section before main.js builds its screens map.
   Usage (menus.js pause menu): dynamic import('./moveset-editor-ui.js')
     then openMovesetEditor(p1id, {fromPause:true, reveal:'toggle'}).
   ============================================================ */

import {
  LS_KEY as EDITOR_LS_KEY,
  SLOT_INPUTS,
  RESOLVER_POSITIONS,
  SOUL_STATES,
  DEMONIO_FORMS,
  createCustomMoveset,
  assignMove,
  removeMove,
  validateNotation,
  positionOfNotation,
  layerOfKey,
  isGrabMove,
  listNamedMovesets,
  loadNamedMoveset,
  saveNamedMoveset,
  deleteNamedMoveset,
  getAppliedName,
  setAppliedName,
  compileToLoadout,
} from './moveset-editor.js';

export const EDITOR_VERSION = 'skeleton-2026-11-20';

/* Group order — main.js MOVESET_GROUPS (:1067), copied here because
   main.js cannot export it to this module without a module cycle. */
const MOVESET_GROUPS = [
  ['signature', 'SIGNATURE'],
  ['throw', 'THROWS'],
  ['special', 'SPECIALS'],
  ['string', 'STRINGS'],
  ['strike', 'STRIKES'],
];

/* Category chips — suite.js MS_CATS (:2627-2629), verbatim. */
const MS_CATS = [
  ['all', 'ALL'], ['stand', 'STANDING'], ['string', 'STRINGS'],
  ['crouch', 'CROUCH / WS'], ['stance', 'STANCES'], ['motion', 'MOTIONS'],
  ['throw', 'THROWS'], ['rage', 'RAGE / HEAT'], ['sig', 'SIGNATURE'],
  ['edited', 'EDITED'],
];

const LAST_PICK_KEY = 'wh.select.last.v1';
const SUITE_KEY = 'wh_creation_suite_v1';
const LIBRARY_INDEX_URL = new URL('../data/moveset-library/index.json', import.meta.url).href;
const PAGE_SIZE = 40;

const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const f2f = (s) => Math.round((s || 0) * 60);

/* ---- suite ports (suite.js, cited per function) ---- */

/* msSrc (suite.js:2649-2669): which layer a move came from. */
function msSrc(m) {
  if (!m) return '';
  if (m.wh_original || m.move_class === 'signature') return 'WH';
  const s = m.merge_source || '';
  if (m.t8_id || s.startsWith('t8')) return 'T8';
  if (m.t7_move_id || s.startsWith('t7')) return 'T7';
  if (s.startsWith('donor')) return 'DONOR';
  if (m.t3_source) return 'T3';
  for (const k of Object.keys(m)) if (/^(sf6|sfv|sf4|doa|ur|vf|nomercy)_/.test(k)) return k.split('_')[0].toUpperCase();
  return 'WH';
}

/* msInfo (suite.js:2671-2679): `i<startup>f · <hit word> · <damage> dmg`. */
const WORD_NAME = { 0x412: 'high', 0x217: 'mid', 0x10f: 'low', 0x31f: 's.mid', 0x607: 'unblk', 0x706: 'unblk', 0x800: 'throw' };
function msInfo(ms, key, m) {
  const w = ms && ms.hit_words ? ms.hit_words[key] : undefined;
  return `i${f2f(m.startup)} · ${WORD_NAME[w] || '—'} · ${Math.round(m.damage || 0)} dmg`;
}

/* msCat (suite.js:2681-2701): category of a notation+move. parseMotion
   comes from the dynamically imported movesets module. */
function msCat(n, m, parseMotion) {
  if (!m) return 'stand';
  if (m.wh_original || m.move_class === 'signature') return 'sig';
  if (m.move_class === 'throw' || m.isGrab) return 'throw';
  if (/^(R|H)\./.test(n)) return 'rage';
  if (/^(FC|WS)\./.test(n) || /^d\+/.test(n)) return 'crouch';
  if (/^[A-Za-z_][A-Za-z0-9_]*\./.test(n)) return 'stance';
  if (parseMotion && parseMotion(n)) return 'motion';
  if (n.includes(',')) return 'string';
  return 'stand';
}

/* msNotations (suite.js:2703-2709): the fighter's slot notations — the
   slots dict when it has one, else filtered move keys. VF/DOA files
   have NO slots dict (A §7); their moves are borrowable, not editable
   as slots, and the header says so. */
function msNotations(ms) {
  if (!ms) return [];
  if (ms.slots) return Object.keys(ms.slots);
  return Object.keys(ms.moves).filter((k) => /^[A-Za-z0-9_./+,~:*]+$/.test(k) && !/__|~|_t\d$|_r\d|_c\d/.test(k));
}

/* msAlternates (suite.js:2711-2725): every layer variant of one input. */
function msAlternates(ms, n) {
  const out = [];
  for (const [k, m] of Object.entries(ms.moves || {})) {
    const base = k.split(/__|~|_t\d$|_r\d|_c\d/)[0];
    if (k === n || base === n || m.input === n) out.push([k, m]);
  }
  return out;
}

/* Animation status of a move (EDITOR-SPEC §4b anim_status). */
function animStatus(m) {
  if (!m) return 'null';
  if (m.anim_ref === null || m.anim_ref === undefined) return 'null';
  if (String(m.anim_ref).startsWith('UNMAPPED')) return 'UNMAPPED';
  return 'mapped';
}

/* ---- state ---- */
const S = {
  fid: null,
  position: 'ALL', // resolver position id, or 'ALL'
  stanceSub: null, // stance code sub-filter when position === 'STANCE'
  sel: null, // selected notation (S3 open)
  preview: null, // named doc being previewed (S4 LOAD), else null
  ms: null, // loaded moveset (playedMoveset)
  idx: null, // moveset index fighters dict
  fromPause: false,
  fromMenu: false,
  lawError: null,
  applyReport: null,
  arm: null, // two-tap confirm arming: 'reset-all' | 'delete:<name>'
  lib: { open: false, notation: null, tab: 'same', other: null, q: '', cat: 'all', page: 0 },
  save: { open: false, name: '', base: '', error: null },
  libIndex: null, // fetched library index JSON (or null)
  libIndexState: 'unknown', // 'ready' | 'stale' | 'missing' | 'unknown'
};

let _MS = null;
async function movesets() {
  if (!_MS) _MS = await import('./movesets.js');
  return _MS;
}

/* ---- screen + styles (created at import; precedents in header) ---- */
function ensureStyle() {
  if (typeof document === 'undefined' || document.getElementById('msed-style')) return;
  const st = document.createElement('style');
  st.id = 'msed-style';
  st.textContent = `
#screen-moveset-editor .msed-panel{width:100%;max-width:480px;margin:0 auto;max-height:92vh;max-height:92dvh;overflow-y:auto;touch-action:pan-y;padding:calc(10px + env(safe-area-inset-top)) 12px calc(16px + env(safe-area-inset-bottom));}
.msed-title{font-size:20px;letter-spacing:.08em;margin:2px 0 0;}
.msed-sub{opacity:.75;font-size:13px;margin:2px 0 10px;}
.msed-field{margin:8px 0;}
.msed-field label{display:block;font-size:11px;letter-spacing:.12em;opacity:.7;margin-bottom:4px;}
.msed-field select,.msed-field input{width:100%;min-height:44px;font-size:16px;background:#241038;color:#f4eaff;border:1px solid #4a2a6e;border-radius:8px;padding:8px 10px;box-sizing:border-box;}
.msed-chips{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0;}
.msed-chip{min-height:44px;min-width:44px;padding:8px 10px;border-radius:999px;border:1px solid #4a2a6e;background:#1e0b2e;color:#e8d5ff;font-size:13px;cursor:pointer;}
.msed-chip.on{background:#ffb14d;color:#14091f;border-color:#ffb14d;font-weight:700;}
.msed-chip .c{opacity:.7;font-size:11px;}
.msed-group h3{font-size:13px;letter-spacing:.12em;color:#ffb14d;margin:14px 0 6px;}
.msed-row{display:flex;align-items:center;gap:8px;width:100%;min-height:48px;text-align:left;background:#1e0b2e;color:#f4eaff;border:1px solid #33204d;border-radius:8px;padding:8px 10px;margin:4px 0;cursor:pointer;box-sizing:border-box;}
.msed-row.edited{border-color:#ffb14d;}
.msed-row.dangling{border-color:#c0392b;}
.msed-in{font-family:ui-monospace,Menlo,Consolas,monospace;color:#9fd8ff;font-size:14px;min-width:64px;flex-shrink:0;}
.msed-name{flex:1;font-size:14px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.msed-tag{font-size:11px;color:#ffb14d;flex-shrink:0;}
.msed-fd{font-size:12px;opacity:.8;flex-shrink:0;}
.msed-dot{color:#ffb14d;font-weight:700;}
.msed-break{color:#ffb14d;font-size:12px;}
.msed-detail{border:1px solid #4a2a6e;border-radius:8px;padding:10px;margin:4px 0 8px;background:#160a24;font-size:14px;}
.msed-detail table{width:100%;border-collapse:collapse;}
.msed-detail td{padding:3px 4px;vertical-align:top;}
.msed-detail td:first-child{opacity:.65;font-size:12px;width:34%;}
.msed-note{font-size:13px;opacity:.8;margin:8px 0;}
.msed-warn{font-size:13px;color:#ff9a7a;margin:8px 0;}
.msed-actions{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0;}
.msed-btn{min-height:44px;padding:10px 14px;border-radius:8px;border:1px solid #4a2a6e;background:#2a1250;color:#f4eaff;font-size:14px;cursor:pointer;}
.msed-btn.primary{background:#ffb14d;color:#14091f;border-color:#ffb14d;font-weight:700;}
.msed-btn.danger{border-color:#c0392b;color:#ff9a7a;}
.msed-btn:disabled{opacity:.45;cursor:default;}
.msed-modal{position:fixed;inset:0;background:rgba(8,4,14,.85);z-index:230;display:flex;align-items:flex-start;justify-content:center;padding:calc(12px + env(safe-area-inset-top)) 10px calc(12px + env(safe-area-inset-bottom));box-sizing:border-box;}
.msed-modal-card{width:100%;max-width:480px;max-height:86vh;max-height:86dvh;overflow-y:auto;touch-action:pan-y;background:#160a24;border:1px solid #4a2a6e;border-radius:12px;padding:14px;box-sizing:border-box;}
.msed-banner{border:1px solid #ffb14d;border-radius:8px;padding:8px 10px;margin:8px 0;font-size:13px;}
.msed-empty{font-size:14px;line-height:1.5;margin:12px 0;}
.msed-kv{display:flex;justify-content:space-between;gap:8px;font-size:14px;padding:6px 0;border-bottom:1px solid #2a1840;}
.msed-kv b{text-align:right;}
`;
  document.head.appendChild(st);
}

function ensureScreen() {
  if (typeof document === 'undefined') return null;
  ensureStyle();
  let sec = document.getElementById('screen-moveset-editor');
  if (sec) return sec;
  sec = document.createElement('section');
  sec.className = 'screen';
  sec.id = 'screen-moveset-editor';
  sec.setAttribute('aria-label', 'Moveset editor');
  sec.innerHTML = '<div class="panel msed-panel" id="msed-panel"></div><div id="msed-modal"></div>';
  document.body.appendChild(sec);
  sec.addEventListener('click', onSectionClick);
  return sec;
}

const _section = ensureScreen();
if (typeof window !== 'undefined') {
  window.__movesetEditor = { open: openMovesetEditor, close: closeMovesetEditor, version: EDITOR_VERSION };
}

/* ---- helpers ---- */

function p1FighterId() {
  try {
    const g = typeof window !== 'undefined' ? window.__game : null;
    return (g && g.p1 && g.p1.char && g.p1.char.id) || null;
  } catch { return null; }
}

function lastPickedId() {
  try { return localStorage.getItem(LAST_PICK_KEY) || null; } catch { return null; }
}

function stanceCodesOf(ms) {
  const out = [];
  for (const v of Object.values((ms && ms.stance_after) || {})) {
    if (typeof v === 'string' && !out.includes(v)) out.push(v);
  }
  return out;
}

/* The loadout-or-resolved value a notation fires (for move/swap/add):
   the loadout entry when edited, else the resolved key (fighter::key
   when borrowed). */
function resolvedValue(m, fid, notation) {
  const lo = m.getLoadout(fid);
  if (lo[notation]) return lo[notation];
  const r = m.resolveMove(fid, notation);
  if (!r) return null;
  return r.from === fid ? r.key : `${r.from}::${r.key}`;
}

/* Source-law check at assign time (EDITOR-SPEC §2e.6): the engine's
   checkSourceLaw over the move's anim_ref (the t3: pull behind the
   assignment). The suite tab does not call it (B §7.8) — this editor
   must, and shows the engine's refusal reason, not a generic error.
   When the claimed map cannot load, the check is skipped (suite parity)
   and the skip is logged, never faked as a pass. */
async function lawCheck(fid, notation, moveKey, move) {
  try {
    const lib = await import('./moveset-library.js');
    const claimed = await lib.loadClaimedMap();
    const manifest = {
      fighter: fid,
      moves: [{ library_id: (move && move.anim_ref) || moveKey, slot: notation }],
    };
    const law = lib.checkSourceLaw(manifest, claimed);
    return law.passed ? { ok: true } : { ok: false, reason: law.issues.join('; ') };
  } catch (e) {
    console.warn('[moveset-editor] source-law check unavailable, proceeding (suite parity):', e && e.message);
    return { ok: true, skipped: true };
  }
}

/* Fetch the library index (EDITOR-SPEC §4b) and classify it. Only the
   REGENERATED shape counts as ready: a header counts block + moves
   keyed by fighter::key. The pre-fix banks index (moveset-library/v1,
   built 2026-10-22) is 'stale'; anything else is 'missing'. */
async function fetchLibraryIndex() {
  if (S.libIndexState !== 'unknown') return S.libIndexState;
  try {
    const r = await fetch(LIBRARY_INDEX_URL);
    if (!r.ok) { S.libIndexState = 'missing'; return 'missing'; }
    const idx = await r.json();
    S.libIndex = idx;
    if (idx && idx.header && idx.header.counts && idx.moves && typeof idx.moves === 'object') {
      S.libIndexState = 'ready';
    } else if (idx && Array.isArray(idx.banks)) {
      S.libIndexState = 'stale';
    } else {
      S.libIndexState = 'missing';
    }
  } catch {
    S.libIndexState = 'missing';
  }
  return S.libIndexState;
}

/* ---- open / close ---- */

export async function openMovesetEditor(fid, opts = {}) {
  const m = await movesets();
  await m.loadFighterMovesets();
  const idx = (m.getMovesetIndex() || {}).fighters || {};
  const ids = Object.keys(idx).sort();
  if (!ids.length) throw new Error('moveset index failed to load');
  const id = fid || p1FighterId() || lastPickedId() || ids[0];
  if (id === 'custom') {
    // Suite parity (suite.js:2745): the custom fighter's base kit
    // defaults to demonio when no __base is set.
    if (!m.getLoadout('custom').__base) m.setLoadoutSlot('custom', '__base', 'demonio');
  }
  await m.ensureMovesets([id]);
  const ms = m.playedMoveset(id);
  S.fid = id;
  S.ms = ms;
  S.idx = idx;
  S.position = 'ALL';
  S.stanceSub = null;
  S.sel = null;
  S.preview = null;
  S.lawError = null;
  S.applyReport = null;
  S.arm = null;
  S.lib.open = false;
  S.save.open = false;
  S.fromPause = !!opts.fromPause;
  S.fromMenu = !!opts.fromMenu;
  render();
  const sec = ensureScreen();
  if (sec && opts.reveal !== 'show') sec.classList.add('active');
  return { fid: id };
}

export function closeMovesetEditor() {
  const sec = document.getElementById('screen-moveset-editor');
  if (sec) sec.classList.remove('active');
  const origin = { fromMenu: S.fromMenu, fromPause: S.fromPause };
  // Closing from pause returns to the pause menu when the fight is
  // still paused (main.js toggleMovelist close behaviour, B §5a).
  if (S.fromPause) {
    const g = typeof window !== 'undefined' ? window.__game : null;
    const p = document.getElementById('wh-pause');
    if (g && (g.running || g.brawler) && g.paused && p && !p.classList.contains('show')) p.classList.add('show');
  }
  S.lib.open = false;
  S.save.open = false;
  S.fromPause = false;
  S.fromMenu = false;
  return origin;
}

/* ---- S1 render ---- */

function positionCounts(m, fid, stanceCodes) {
  const counts = {};
  for (const p of RESOLVER_POSITIONS) counts[p.id] = 0;
  const notations = S.preview ? Object.keys(S.preview.slots || {}) : msNotations(m);
  for (const n of notations) {
    const pos = positionOfNotation(n, stanceCodes);
    if (pos.id === 'QUARANTINE') continue;
    counts[pos.id] = (counts[pos.id] || 0) + 1;
  }
  return { counts, total: notations.length };
}

function render() {
  const panel = document.getElementById('msed-panel');
  if (!panel) return;
  const m = _MS;
  const fid = S.fid;
  const ms = S.ms;
  const idx = S.idx || {};
  const entry = idx[fid] || {};
  const display = fid === 'custom' ? 'YOUR CREATED FIGHTER' : (entry.display || fid);
  const lo = m ? m.getLoadout(fid) : {};
  const editedCount = Object.keys(lo).filter((n) => n !== '__base').length;

  if (!ms) {
    panel.innerHTML = `<h2 class="msed-title">MOVESET EDITOR</h2>
      <p class="msed-sub">No moveset loaded for ${esc(fid)} yet.</p>
      <div class="msed-actions"><button class="msed-btn primary" data-ms="close">BACK</button></div>`;
    renderModal();
    return;
  }

  const stanceCodes = stanceCodesOf(ms);
  const { counts, total } = positionCounts(ms, fid, stanceCodes);
  const moveCount = Object.keys(ms.moves || {}).length;

  // Position chips in resolver order (EDITOR-SPEC §2d). RD shows 0
  // honestly (synthesized, no data keys); SSL/SSR show 0 honestly
  // when the fighter has no keys there (A §8.2).
  const chip = (id, label) => `<button class="msed-chip ${S.position === id ? 'on' : ''}" data-ms="chip" data-pos="${id}">${esc(label)} <span class="c">${counts[id] || 0}</span></button>`;
  let chips = `<button class="msed-chip ${S.position === 'ALL' ? 'on' : ''}" data-ms="chip" data-pos="ALL">ALL <span class="c">${total}</span></button>`;
  for (const p of RESOLVER_POSITIONS) chips += chip(p.id, p.label);
  let stanceRow = '';
  if (S.position === 'STANCE' && stanceCodes.length) {
    stanceRow = '<div class="msed-chips">' + stanceCodes.map((c) => {
      const n = msNotations(ms).filter((x) => positionOfNotation(x, stanceCodes).stance === c).length;
      return `<button class="msed-chip ${S.stanceSub === c ? 'on' : ''}" data-ms="stance-sub" data-code="${esc(c)}">${esc(c)} <span class="c">${n}</span></button>`;
    }).join('') + '</div>';
  }

  // Base-kit line. Demonio forms are separate fighters (A §6) — the
  // editor says so on their screens; there is no form switch.
  let baseLine = '';
  if (fid === 'custom') {
    const base = lo.__base || 'demonio';
    baseLine = `<div class="msed-field"><label>BASE MOVESET — the whole moveset this custom fighter starts from</label>
      <select id="msed-base">${Object.keys(idx).sort().map((i) => `<option value="${esc(i)}" ${i === base ? 'selected' : ''}>${esc((idx[i] || {}).display || i)} — ${esc((idx[i] || {}).tekken_base || '')}</option>`).join('')}</select></div>`;
  } else {
    baseLine = `<p class="msed-sub">Base kit: ${esc(ms.tekken_base || entry.tekken_base || '')}${DEMONIO_FORMS.includes(fid) ? ' · Demonio form file — edited as its own fighter; no form switch in the editor (transform wiring untraced).' : ''}${!ms.slots ? ' · This fighter’s file has no slots map — its moves are borrowable from OTHER FIGHTER, not editable as slots here.' : ''}</p>`;
  }

  const previewBanner = S.preview
    ? `<div class="msed-banner">Previewing <b>${esc(S.preview.name)}</b> — these are that saved moveset’s slots, not the live loadout. APPLY it in the save sheet to play it. <button class="msed-btn" data-ms="exit-preview">EXIT PREVIEW</button></div>`
    : '';

  panel.innerHTML = `<h2 class="msed-title">MOVESET EDITOR — ${esc(display)}</h2>
    <p class="msed-sub">${total} inputs · ${moveCount} moves · ${esc(ms.tekken_base || '')}${editedCount ? ` · ${editedCount} edited` : ''}</p>
    ${previewBanner}
    <div class="msed-field"><label>FIGHTER</label><select id="msed-fid">
      <option value="custom" ${fid === 'custom' ? 'selected' : ''}>YOUR CREATED FIGHTER</option>
      ${Object.keys(idx).sort().map((i) => `<option value="${esc(i)}" ${i === fid ? 'selected' : ''}>${esc((idx[i] || {}).display || i)} — ${esc((idx[i] || {}).tekken_base || '')}</option>`).join('')}
    </select></div>
    ${baseLine}
    <div class="msed-chips">${chips}</div>
    ${stanceRow}
    ${S.lawError ? `<p class="msed-warn">Not assigned — ${esc(S.lawError)}</p>` : ''}
    ${S.applyReport ? `<p class="msed-note">${esc(S.applyReport)}</p>` : ''}
    <div id="msed-list">${renderSlotList()}</div>
    <div class="msed-actions">
      <button class="msed-btn primary" data-ms="open-save">SAVE / NAMED MOVESETS</button>
      <button class="msed-btn danger" data-ms="reset-all">${S.arm === 'reset-all' ? 'TAP AGAIN TO CONFIRM RESET' : 'RESET ALL EDITS'}</button>
      <button class="msed-btn" data-ms="close">BACK</button>
    </div>`;

  const fidSel = panel.querySelector('#msed-fid');
  if (fidSel) fidSel.onchange = () => { openMovesetEditor(fidSel.value, { fromPause: S.fromPause, fromMenu: S.fromMenu, reveal: S.fromMenu ? 'show' : 'toggle' }).catch(() => {}); };
  const baseSel = panel.querySelector('#msed-base');
  if (baseSel) {
    baseSel.onchange = async () => {
      const mm = await movesets();
      mm.setLoadoutSlot('custom', '__base', baseSel.value);
      await mm.ensureMovesets([baseSel.value]);
      S.ms = mm.playedMoveset('custom');
      render();
    };
  }
  renderModal();
}

function slotRowsForPosition(m, fid, stanceCodes) {
  const lo = m.getLoadout(fid);
  const notations = S.preview ? Object.keys(S.preview.slots || {}) : msNotations(m);
  const rows = [];
  for (const n of notations) {
    if (S.position !== 'ALL') {
      const pos = positionOfNotation(n, stanceCodes);
      if (pos.id !== S.position) continue;
      if (S.position === 'STANCE' && S.stanceSub && pos.stance !== S.stanceSub) continue;
    }
    let r = null;
    let value = null;
    if (S.preview) {
      value = S.preview.slots[n];
      const [from, key] = String(value).includes('::') ? String(value).split('::') : [fid, value];
      const src = from === fid ? m.playedMoveset(fid) : m.getFighterMoveset(from);
      const move = src && src.moves ? src.moves[key] : null;
      if (move) r = { move, key, ms: src, from };
    } else {
      r = m.resolveMove(fid, n);
      value = lo[n] || null;
    }
    if (!r) {
      // Dangling slot: the loadout (or preview doc) points at a move
      // that no longer exists — flag it, never crash, never silently
      // delete it (EDITOR-SPEC §4e.3). Slots with no resolve and no
      // edit are skipped (suite parity: `if(!r) continue`).
      if (value || S.preview) rows.push({ notation: n, dangling: true, value });
      continue;
    }
    rows.push({ notation: n, r, edited: !!lo[n] && !S.preview });
  }
  return rows;
}

function renderSlotList() {
  const m = _MS;
  const fid = S.fid;
  const ms = S.ms;
  if (!ms) return '';
  const stanceCodes = stanceCodesOf(ms);
  const rows = slotRowsForPosition(m, fid, stanceCodes);
  if (!rows.length) {
    const posLabel = S.position === 'ALL' ? '' : ` in ${S.position}`;
    const rdNote = S.position === 'RD' ? ' Rage Drive is synthesized at runtime — no moves to assign.' : '';
    const sslNote = (S.position === 'SSL' || S.position === 'SSR') ? ' The resolver tries this sidestep side, but this fighter has no moves keyed for it.' : '';
    return `<p class="msed-empty">No moves${esc(posLabel)} yet.${esc(rdNote)}${esc(sslNote)}</p>`;
  }
  const byClass = {};
  for (const row of rows) {
    const cls = row.dangling ? 'dangling' : (row.r.move.move_class || (row.r.move.throw ? 'throw' : 'strike'));
    (byClass[cls] = byClass[cls] || []).push(row);
  }
  let html = '';
  const group = (cls, label) => {
    const list = byClass[cls];
    if (!list || !list.length) return;
    html += `<div class="msed-group"><h3>${label} (${list.length})</h3>`;
    for (const row of list) {
      if (row.dangling) {
        html += `<div class="msed-row dangling"><span class="msed-in">${esc(row.notation)}</span><span class="msed-name">Move removed — reset to default?</span><button class="msed-btn danger" data-ms="reset-slot" data-n="${esc(row.notation)}">RESET</button></div>`;
        continue;
      }
      const mv = row.r.move;
      const brk = mv.throw_break
        ? `<span class="msed-break">break ${mv.throw_break === '1' ? 'LP' : mv.throw_break === '2' ? 'RP' : 'LP+RP'}</span>` : '';
      html += `<button class="msed-row ${row.edited ? 'edited' : ''}" data-ms="slot" data-n="${esc(row.notation)}">
        <span class="msed-in">${esc(row.notation)}</span><span class="msed-name">${esc(mv.name || '')} ${brk}</span>
        <span class="msed-tag">${esc(msSrc(mv))}</span><span class="msed-fd">${f2f(mv.startup)}f/${f2f(mv.active)}f/${f2f(mv.recovery)}f · ${mv.damage ?? '?'}dmg</span>${row.edited ? '<span class="msed-dot">●</span>' : ''}</button>`;
      if (S.sel === row.notation) html += renderSlotDetail(row);
    }
    html += '</div>';
  };
  for (const [cls, label] of MOVESET_GROUPS) group(cls, label);
  const rest = Object.entries(byClass).filter(([c]) => !MOVESET_GROUPS.some(([g]) => g === c) && c !== 'dangling').flatMap(([, l]) => l);
  if (rest.length) {
    html += '<div class="msed-group"><h3>OTHER (' + rest.length + ')</h3>';
    for (const row of rest) {
      const mv = row.r.move;
      html += `<button class="msed-row ${row.edited ? 'edited' : ''}" data-ms="slot" data-n="${esc(row.notation)}">
        <span class="msed-in">${esc(row.notation)}</span><span class="msed-name">${esc(mv.name || '')}</span>
        <span class="msed-tag">${esc(msSrc(mv))}</span><span class="msed-fd">${f2f(mv.startup)}f/${f2f(mv.active)}f/${f2f(mv.recovery)}f · ${mv.damage ?? '?'}dmg</span>${row.edited ? '<span class="msed-dot">●</span>' : ''}</button>`;
      if (S.sel === row.notation) html += renderSlotDetail(row);
    }
    html += '</div>';
  }
  const dang = byClass.dangling || [];
  if (dang.length) {
    html += '<div class="msed-group"><h3>NEEDS ATTENTION (' + dang.length + ')</h3>';
    for (const row of dang) {
      html += `<div class="msed-row dangling"><span class="msed-in">${esc(row.notation)}</span><span class="msed-name">Move removed — reset to default?</span><button class="msed-btn danger" data-ms="reset-slot" data-n="${esc(row.notation)}">RESET</button></div>`;
    }
    html += '</div>';
  }
  return html;
}

/* ---- S3 slot detail / input-edit (inline expand in S1) ---- */

function renderSlotDetail(row) {
  const m = _MS;
  const fid = S.fid;
  const mv = row.r.move;
  const key = row.r.key;
  const from = row.r.from;
  const lo = m.getLoadout(fid);
  const edited = !!lo[row.notation] && !S.preview;
  const status = animStatus(mv);
  const statusText = status === 'mapped' ? 'animation mapped' : status === 'UNMAPPED' ? 'NO ANIMATION — clip pending' : 'NO ANIMATION — anim_ref null';
  const brk = mv.throw_break ? mv.throw_break : (isGrabMove(mv) ? 'unknown — this throw carries no break input (VF class-only throws have none, A §5)' : '—');
  const path = Array.isArray(mv.input_slots) ? mv.input_slots.join(' → ') : (mv.input || key);
  const notations = S.preview ? Object.keys(S.preview.slots || {}) : msNotations(S.ms);
  const addOptions = SLOT_INPUTS.filter((n) => !notations.includes(n));
  const detail = `<div class="msed-detail"><table>
    <tr><td>Move</td><td><b>${esc(mv.name || key)}</b></td></tr>
    <tr><td>Move key</td><td><span class="msed-in">${esc(key)}</span>${from !== fid ? ` · borrowed from ${esc(from)}` : ''}</td></tr>
    <tr><td>Layer</td><td>${esc(layerOfKey(key).layer)} · source ${esc(msSrc(mv))}</td></tr>
    <tr><td>Class</td><td>${esc(mv.move_class || 'strike')}${isGrabMove(mv) ? ' · throw' : ''}</td></tr>
    <tr><td>Frames</td><td>${f2f(mv.startup)}f startup / ${f2f(mv.active)}f active / ${f2f(mv.recovery)}f recovery · ${mv.damage ?? '?'} dmg</td></tr>
    <tr><td>Hit level</td><td>${esc(mv.hit_level || '—')}</td></tr>
    <tr><td>On block / hit / CH</td><td>${esc(mv.on_block ?? '—')} / ${esc(mv.on_hit ?? '—')} / ${esc(mv.on_ch ?? '—')}</td></tr>
    <tr><td>Throw break</td><td>${esc(brk)}</td></tr>
    <tr><td>Animation</td><td><span class="msed-in">${esc(mv.anim_ref ?? 'null')}</span> · ${esc(statusText)}</td></tr>
    <tr><td>String path</td><td><span class="msed-in">${esc(path)}</span></td></tr>
  </table>
  <p class="msed-note">No live move preview in v1 — this panel shows the move’s data instead (B §7.5).</p>
  ${isGrabMove(mv) ? '<p class="msed-note">Swapping a throw swaps the attacker’s move only — the victim pair lives outside the moveset file (reactions + t3-throw.js, A §5).</p>' : ''}
  ${S.preview ? '<p class="msed-note">Previewing a saved moveset — edits apply to the live loadout, not to the preview.</p>' : ''}
  <div class="msed-actions">
    <button class="msed-btn primary" data-ms="open-library" data-n="${esc(row.notation)}">BROWSE LIBRARY</button>
    ${edited ? `<button class="msed-btn" data-ms="reset-slot" data-n="${esc(row.notation)}">RESET TO DEFAULT</button>` : ''}
  </div>
  <div class="msed-field"><label>MOVE TO — another notation (the old input keeps its default move unless it was edited)</label>
    <select id="msed-move-to">${notations.filter((n) => n !== row.notation).map((n) => `<option value="${esc(n)}">${esc(n)}</option>`).join('')}</select></div>
  <div class="msed-actions"><button class="msed-btn" data-ms="do-move-to" data-n="${esc(row.notation)}">MOVE HERE</button></div>
  <div class="msed-field"><label>SWAP WITH — another slot (two loadout writes)</label>
    <select id="msed-swap-with">${notations.filter((n) => n !== row.notation).map((n) => `<option value="${esc(n)}">${esc(n)}</option>`).join('')}</select></div>
  <div class="msed-actions"><button class="msed-btn" data-ms="do-swap" data-n="${esc(row.notation)}">SWAP</button></div>
  <div class="msed-field"><label>ADD NOTATION — from the engine’s fixed input set (no free-text notations)</label>
    <select id="msed-add-notation">${addOptions.map((n) => `<option value="${esc(n)}">${esc(n)}</option>`).join('') || '<option value="">— no free inputs —</option>'}</select></div>
  <div class="msed-actions"><button class="msed-btn" data-ms="do-add-notation" data-n="${esc(row.notation)}" ${addOptions.length ? '' : 'disabled'}>ADD THIS MOVE HERE</button></div>
  </div>`;
  return detail;
}

/* S3 write actions — all through setLoadoutSlot (the only path a fight
   reads), each preceded by the source-law check. */
async function doMoveTo(notation) {
  const m = await movesets();
  const target = document.getElementById('msed-move-to');
  if (!target || !target.value) return;
  const value = resolvedValue(m, S.fid, notation);
  if (!value) return;
  const r = m.resolveMove(S.fid, notation);
  S.lawError = null;
  const law = await lawCheck(S.fid, target.value, value, r && r.move);
  if (!law.ok) { S.lawError = law.reason; render(); return; }
  try { validateNotation(target.value); } catch (e) { S.lawError = e.message; render(); return; }
  m.setLoadoutSlot(S.fid, target.value, value);
  m.setLoadoutSlot(S.fid, notation, null);
  S.sel = target.value;
  render();
}

async function doSwap(notation) {
  const m = await movesets();
  const target = document.getElementById('msed-swap-with');
  if (!target || !target.value) return;
  const valueA = resolvedValue(m, S.fid, notation);
  const valueB = resolvedValue(m, S.fid, target.value);
  if (!valueA || !valueB) return;
  const rA = m.resolveMove(S.fid, notation);
  const rB = m.resolveMove(S.fid, target.value);
  S.lawError = null;
  const lawA = await lawCheck(S.fid, target.value, valueA, rA && rA.move);
  if (!lawA.ok) { S.lawError = lawA.reason; render(); return; }
  const lawB = await lawCheck(S.fid, notation, valueB, rB && rB.move);
  if (!lawB.ok) { S.lawError = lawB.reason; render(); return; }
  m.setLoadoutSlot(S.fid, target.value, valueA);
  m.setLoadoutSlot(S.fid, notation, valueB);
  render();
}

async function doAddNotation(notation) {
  const m = await movesets();
  const target = document.getElementById('msed-add-notation');
  if (!target || !target.value) return;
  const value = resolvedValue(m, S.fid, notation);
  if (!value) return;
  const r = m.resolveMove(S.fid, notation);
  S.lawError = null;
  const law = await lawCheck(S.fid, target.value, value, r && r.move);
  if (!law.ok) { S.lawError = law.reason; render(); return; }
  try { validateNotation(target.value); } catch (e) { S.lawError = e.message; render(); return; }
  m.setLoadoutSlot(S.fid, target.value, value);
  S.sel = target.value;
  render();
}

async function doResetSlot(notation) {
  const m = await movesets();
  // Per-slot RESET TO DEFAULT = delete that loadout entry; the slot
  // falls back to the file's slots dict (A §1g, suite parity).
  m.setLoadoutSlot(S.fid, notation, null);
  if (S.sel === notation) S.sel = null;
  S.lawError = null;
  render();
}

async function doResetAll() {
  const m = await movesets();
  // RESET ALL EDITS = delete the fighter's loadout object entries
  // except __base (suite parity, suite.js:2783).
  for (const n of Object.keys(m.getLoadout(S.fid))) {
    if (n !== '__base') m.setLoadoutSlot(S.fid, n, null);
  }
  S.sel = null;
  S.arm = null;
  render();
}

/* ---- S2 library modal ---- */

async function openLibrary(notation) {
  S.lib.open = true;
  S.lib.notation = notation;
  S.lib.tab = 'same';
  S.lib.other = null;
  S.lib.q = '';
  S.lib.cat = 'all';
  S.lib.page = 0;
  await fetchLibraryIndex();
  renderModal();
}

function libraryEmptyHTML() {
  const state = S.libIndexState;
  const built = S.libIndex && S.libIndex.built ? ` (built ${esc(S.libIndex.built)})` : '';
  const body = state === 'stale'
    ? `The library index on disk is the pre-fix banks index${built} — it is not the regenerated fixed-moveset index, so the library stays empty until the fix regenerates it.`
    : 'The move library is generated from the fixed movesets — the moveset fix is still landing, so there is nothing to browse yet.';
  return `<p class="msed-empty"><b>No library content yet — index pending the fix.</b></p>
    <p class="msed-empty">${body}</p>
    <p class="msed-empty">The editor never lists moves from pre-fix files. Slot viewing, input edits and named saves in this editor already work; browsing and swapping from the library light up when the regenerated index lands.</p>`;
}

function libraryRows() {
  const idx = S.libIndex;
  const entries = Object.values((idx && idx.moves) || {});
  const fid = S.fid;
  const n = S.lib.notation;
  let rows = entries.filter((e) => {
    if (S.lib.tab === 'same') return e.fighter === fid && e.input === n;
    if (S.lib.tab === 'all') return e.fighter === fid;
    return e.fighter === (S.lib.other || '');
  });
  const ql = S.lib.q.toLowerCase();
  if (ql) rows = rows.filter((e) => String(e.input || '').toLowerCase().includes(ql) || String(e.name || '').toLowerCase().includes(ql));
  if (S.lib.cat !== 'all') {
    if (S.lib.cat === 'edited') {
      // EDITED in the library = moves currently assigned somewhere in
      // this fighter's live loadout (the suite's slot-list meaning,
      // applied to library entries).
      const loVals = new Set(Object.values((_MS ? _MS.getLoadout(S.fid) : {}) || {}));
      rows = rows.filter((e) => loVals.has(e.fighter === S.fid ? (e.key || '') : `${e.fighter}::${e.key || ''}`));
    } else {
      rows = rows.filter((e) => msCat(e.input || '', e, _MS && _MS.parseMotion) === S.lib.cat);
    }
  }
  rows.sort((a, b) => String(a.input || '').localeCompare(String(b.input || '')) || String(a.name || '').localeCompare(String(b.name || '')));
  return rows;
}

function renderLibraryModal() {
  const m = _MS;
  const fid = S.fid;
  const n = S.lib.notation;
  const cur = m ? m.resolveMove(fid, n) : null;
  const idx = S.idx || {};
  const tabs = [['same', 'SAME INPUT'], ['all', 'ALL MOVES'], ['other', 'OTHER FIGHTER']];
  let body = `<div class="kv"><span>Input</span><b>${esc(n)}</b></div>
    <div class="kv"><span>Now</span><b>${esc(cur ? (cur.move.name || cur.key) : '—')}${cur ? ` · ${msSrc(cur.move)} · ${msInfo(cur.ms, cur.key, cur.move)}` : ''}</b></div>
    <div class="msed-chips">${tabs.map(([k, l]) => `<button class="msed-chip ${S.lib.tab === k ? 'on' : ''}" data-ms="lib-tab" data-t="${k}">${l}</button>`).join('')}</div>`;
  if (S.lib.tab === 'other') {
    const otherId = S.lib.other || Object.keys(idx).find((i) => i !== fid);
    body += `<div class="msed-field"><label>BORROW FROM</label><select id="msed-lib-fid">${Object.keys(idx).sort().map((i) => `<option value="${esc(i)}" ${i === otherId ? 'selected' : ''}>${esc((idx[i] || {}).display || i)} — ${esc((idx[i] || {}).tekken_base || '')}</option>`).join('')}</select></div>`;
  }
  body += `<div class="msed-chips">${MS_CATS.map(([k, l]) => `<button class="msed-chip ${S.lib.cat === k ? 'on' : ''}" data-ms="lib-cat" data-c="${k}">${l}</button>`).join('')}</div>
    <div class="msed-field"><input id="msed-lib-q" type="search" placeholder="search name or input" value="${esc(S.lib.q)}"></div>`;
  if (S.libIndexState !== 'ready') {
    body += libraryEmptyHTML();
  } else {
    const rows = libraryRows();
    const shown = rows.slice(0, PAGE_SIZE * (S.lib.page + 1));
    body += `<p class="msed-note">${rows.length} moves${rows.length > shown.length ? ` (first ${shown.length}; search to narrow)` : ''}. Tap one to assign it to <b>${esc(n)}</b>.</p>
    <div>${shown.map((e) => {
      const key = e.key || String(e.id || '').split('::')[1] || '';
      return `<button class="msed-row" data-ms="lib-pick" data-f="${esc(e.fighter || '')}" data-k="${esc(key)}">
        <span class="msed-in">${esc(e.input || key)}</span><span class="msed-name">${esc(e.name || key)}</span>
        <span class="msed-tag">${esc((e.source && e.source[0]) || msSrc(e))}</span><span class="msed-fd">${f2f(e.startup)}f/${f2f(e.active)}f/${f2f(e.recovery)}f · ${e.damage ?? '?'}dmg</span></button>`;
    }).join('')}</div>
    ${rows.length > shown.length ? '<div class="msed-actions"><button class="msed-btn" data-ms="lib-more">MORE</button></div>' : ''}`;
  }
  body += `<div class="msed-actions">
    <button class="msed-btn danger" data-ms="reset-slot" data-n="${esc(n)}">RESET TO DEFAULT</button>
    <button class="msed-btn primary" data-ms="lib-close">CLOSE</button></div>`;
  return `<div class="msed-modal"><div class="msed-modal-card">
    <h2 class="msed-title">MOVE LIBRARY — ${esc(n)}</h2>${body}</div></div>`;
}

async function doLibraryPick(srcFighter, key) {
  const m = await movesets();
  const fid = S.fid;
  const n = S.lib.notation;
  const value = srcFighter === fid ? key : `${srcFighter}::${key}`;
  const src = srcFighter === fid ? m.playedMoveset(fid) : m.getFighterMoveset(srcFighter);
  const move = src && src.moves ? src.moves[key] : null;
  S.lawError = null;
  const law = await lawCheck(fid, n, value, move);
  if (!law.ok) { S.lib.open = false; S.lawError = law.reason; render(); return; }
  m.setLoadoutSlot(fid, n, value);
  if (srcFighter !== fid) await m.ensureMovesets([srcFighter]);
  S.lib.open = false;
  S.sel = n;
  render();
}

/* ---- S4 save sheet ---- */

function baseInfoFor(baseTemplate) {
  const e = (S.idx || {})[baseTemplate] || {};
  return { bank: e.anim_bank || null, character: e.tekken_base || null };
}

function openSave() {
  const m = _MS;
  S.save.open = true;
  S.save.name = '';
  S.save.error = null;
  S.save.base = (m && m.getLoadout(S.fid).__base) || (S.fid === 'custom' ? 'demonio' : S.fid);
  S.applyReport = null;
  renderModal();
}

/* moveset_custom becomes an APPLIED-DOCUMENT POINTER (EDITOR-SPEC §3a):
   {schema, name, baseTemplate, fighterId} — no full document, no slots.
   customFighterToRoster() still reads moveset: 'custom:<baseTemplate>'
   off it. Best-effort: the loadout is the playable save; the pointer
   only helps the custom fighter re-apply on load. */
function writeAppliedPointer(doc) {
  if (doc.fighterId !== 'custom') return;
  try {
    const raw = localStorage.getItem(SUITE_KEY);
    if (!raw) return;
    const F = JSON.parse(raw);
    if (!F || !F.profile) return;
    F.moveset_custom = { schema: 'wh.custom-moveset.v1', name: doc.name, baseTemplate: doc.baseTemplate, fighterId: 'custom' };
    localStorage.setItem(SUITE_KEY, JSON.stringify(F));
  } catch { /* pointer is best-effort */ }
}

async function doSaveNamed() {
  const m = await movesets();
  const nameInput = document.getElementById('msed-save-name');
  const baseSel = document.getElementById('msed-save-base');
  const name = nameInput ? nameInput.value.trim() : '';
  if (!name) { S.save.error = 'Name the moveset first.'; renderModal(); return; }
  const baseTemplate = baseSel ? baseSel.value : S.save.base;
  const doc = createCustomMoveset({ name, fighterId: S.fid, baseTemplate, base: baseInfoFor(baseTemplate) });
  const lo = m.getLoadout(S.fid);
  for (const [notation, value] of Object.entries(lo)) {
    if (notation === '__base') continue;
    try { validateNotation(notation); doc.slots[notation] = value; } catch { /* skip unassignable notations */ }
  }
  saveNamedMoveset(doc);
  setAppliedName(S.fid, name);
  writeAppliedPointer(doc);
  S.save.name = name;
  S.save.error = null;
  S.applyReport = `Saved “${name}” — ${Object.keys(doc.slots).length} edited slots on a ${baseTemplate} base. It is APPLIED: the loadout already plays it.`;
  renderModal();
}

async function doApplyNamed(name) {
  const m = await movesets();
  const doc = loadNamedMoveset(name);
  if (!doc) return;
  const skipped = [];
  const clean = { ...doc, slots: {} };
  for (const [notation, value] of Object.entries(doc.slots || {})) {
    const [from, key] = String(value).includes('::') ? String(value).split('::') : [doc.fighterId, value];
    const src = from === doc.fighterId ? m.playedMoveset(doc.fighterId) : m.getFighterMoveset(from);
    if (src && src.moves && src.moves[key]) clean.slots[notation] = value;
    else skipped.push(notation);
  }
  // Apply compiles the doc into the loadout (EDITOR-SPEC §3a bridge):
  // clear the fighter's current slot entries first so APPLY replaces
  // the kit instead of merging stale entries over it.
  const current = Object.keys(m.getLoadout(doc.fighterId)).filter((n) => n !== '__base');
  const res = compileToLoadout(clean, { setLoadoutSlot: m.setLoadoutSlot.bind(m), clearNotations: current });
  setAppliedName(doc.fighterId, name);
  writeAppliedPointer(clean);
  const report = skipped.length
    ? `Applied “${name}” (${res.applied} slots, base ${res.base}). Skipped ${skipped.length} slot(s) whose moves no longer exist: ${skipped.join(', ')} — reset them to default.`
    : `Applied “${name}” (${res.applied} slots, base ${res.base}).`;
  if (doc.fighterId !== S.fid) {
    await openMovesetEditor(doc.fighterId, { fromPause: S.fromPause, fromMenu: S.fromMenu, reveal: S.fromMenu ? 'show' : 'toggle' });
    S.applyReport = report;
    render();
    return;
  }
  // The doc's base may differ from the fighter's old one — load its deps
  // (the __base fighter) before re-reading the played moveset.
  await m.ensureMovesets([doc.fighterId]);
  S.applyReport = report;
  S.ms = m.playedMoveset(S.fid);
  S.preview = null;
  render();
}

function doLoadPreview(name) {
  const doc = loadNamedMoveset(name);
  if (!doc) return;
  S.preview = doc;
  S.save.open = false;
  S.sel = null;
  if (doc.fighterId !== S.fid) {
    openMovesetEditor(doc.fighterId, { fromPause: S.fromPause, fromMenu: S.fromMenu, reveal: S.fromMenu ? 'show' : 'toggle' }).then(async () => {
      // Preload the preview's borrowed fighters so its rows resolve.
      const deps = new Set([doc.baseTemplate]);
      for (const v of Object.values(doc.slots || {})) if (String(v).includes('::')) deps.add(String(v).split('::')[0]);
      const mm = await movesets();
      await mm.ensureMovesets([...deps].filter(Boolean));
      S.preview = doc;
      render();
    }).catch(() => {});
    return;
  }
  render();
}

function renderSaveSheet() {
  const m = _MS;
  const fid = S.fid;
  const idx = S.idx || {};
  const lo = m ? m.getLoadout(fid) : {};
  const editedCount = Object.keys(lo).filter((n) => n !== '__base').length;
  const total = msNotations(S.ms).length;
  const docs = listNamedMovesets();
  const applied = getAppliedName(fid);
  const list = docs.length ? docs.map((d) => {
    const isApplied = applied === d.name;
    return `<div class="msed-kv"><span><b>${esc(d.name)}</b><br><span style="opacity:.7;font-size:12px;">${esc(d.fighterId)} · base ${esc(d.baseTemplate)} · ${d.slots} slots · ${esc((d.created || '').slice(0, 10))}</span></span>
      <span>${isApplied ? '<b>APPLIED</b>' : 'DRAFT'}<br>
      <button class="msed-btn" data-ms="apply-named" data-name="${esc(d.name)}">APPLY</button>
      <button class="msed-btn" data-ms="load-named" data-name="${esc(d.name)}">LOAD</button>
      <button class="msed-btn danger" data-ms="delete-named" data-name="${esc(d.name)}">${S.arm === `delete:${d.name}` ? 'SURE?' : 'DELETE'}</button></span></div>`;
  }).join('') : '<p class="msed-empty">No named movesets saved yet.</p>';
  return `<div class="msed-modal"><div class="msed-modal-card">
    <h2 class="msed-title">SAVE MOVESET</h2>
    <p class="msed-note">${editedCount} edited slots / ${total} total slots for ${esc(fid)}. Saving captures the live loadout as a named moveset; applying one compiles it back into the loadout — the only thing a fight reads. Saving with an existing name overwrites it. (Rename / duplicate are owner decisions owed, not offered here.)</p>
    <div class="msed-field"><label>NAME THIS MOVESET</label><input id="msed-save-name" type="text" maxlength="48" placeholder="Name this moveset" value="${esc(S.save.name)}"></div>
    <div class="msed-field"><label>BASE KIT</label><select id="msed-save-base">${Object.keys(idx).sort().map((i) => `<option value="${esc(i)}" ${i === S.save.base ? 'selected' : ''}>${esc((idx[i] || {}).display || i)} — ${esc((idx[i] || {}).tekken_base || '')}</option>`).join('')}</select></div>
    ${S.save.error ? `<p class="msed-warn">${esc(S.save.error)}</p>` : ''}
    ${S.applyReport ? `<p class="msed-note">${esc(S.applyReport)}</p>` : ''}
    <div class="msed-actions"><button class="msed-btn primary" data-ms="do-save-named">SAVE + APPLY</button>
    <button class="msed-btn" data-ms="save-close">CLOSE</button></div>
    <h3 style="font-size:13px;letter-spacing:.12em;color:#ffb14d;">SAVED MOVESETS</h3>
    ${list}
    </div></div>`;
}

function renderModal() {
  const host = document.getElementById('msed-modal');
  if (!host) return;
  if (S.lib.open) host.innerHTML = renderLibraryModal();
  else if (S.save.open) host.innerHTML = renderSaveSheet();
  else host.innerHTML = '';
  const libQ = host.querySelector('#msed-lib-q');
  if (libQ) libQ.oninput = () => { S.lib.q = libQ.value; S.lib.page = 0; renderModal(); };
  const libFid = host.querySelector('#msed-lib-fid');
  if (libFid) libFid.onchange = () => { S.lib.other = libFid.value; S.lib.page = 0; renderModal(); };
  const saveName = host.querySelector('#msed-save-name');
  if (saveName) saveName.oninput = () => { S.save.name = saveName.value; };
  const saveBase = host.querySelector('#msed-save-base');
  if (saveBase) saveBase.onchange = () => { S.save.base = saveBase.value; };
}

/* ---- delegated clicks (B §4: delegated document-style clicks, no
   per-element onclick on re-rendered rows) ---- */

async function onSectionClick(e) {
  const t = e.target;
  const el = (t instanceof Element) ? t.closest('[data-ms]') : null;
  if (!el) return;
  const a = el.dataset.ms;
  if (a === 'close') { closeMovesetEditor(); return; }
  if (a === 'chip') {
    S.position = el.dataset.pos;
    S.stanceSub = null;
    S.sel = null;
    render();
    return;
  }
  if (a === 'stance-sub') {
    S.stanceSub = S.stanceSub === el.dataset.code ? null : el.dataset.code;
    render();
    return;
  }
  if (a === 'slot') {
    S.sel = S.sel === el.dataset.n ? null : el.dataset.n;
    S.lawError = null;
    render();
    return;
  }
  if (a === 'open-library') { openLibrary(el.dataset.n); return; }
  if (a === 'lib-close') { S.lib.open = false; renderModal(); return; }
  if (a === 'lib-tab') { S.lib.tab = el.dataset.t; S.lib.page = 0; renderModal(); return; }
  if (a === 'lib-cat') { S.lib.cat = el.dataset.c; S.lib.page = 0; renderModal(); return; }
  if (a === 'lib-more') { S.lib.page += 1; renderModal(); return; }
  if (a === 'lib-pick') { doLibraryPick(el.dataset.f, el.dataset.k); return; }
  if (a === 'do-move-to') { doMoveTo(el.dataset.n); return; }
  if (a === 'do-swap') { doSwap(el.dataset.n); return; }
  if (a === 'do-add-notation') { doAddNotation(el.dataset.n); return; }
  if (a === 'reset-slot') { doResetSlot(el.dataset.n); return; }
  if (a === 'reset-all') {
    if (S.arm === 'reset-all') { doResetAll(); return; }
    S.arm = 'reset-all';
    render();
    setTimeout(() => { if (S.arm === 'reset-all') { S.arm = null; render(); } }, 4000);
    return;
  }
  if (a === 'open-save') { openSave(); return; }
  if (a === 'save-close') { S.save.open = false; renderModal(); return; }
  if (a === 'do-save-named') { doSaveNamed(); return; }
  if (a === 'apply-named') { doApplyNamed(el.dataset.name); return; }
  if (a === 'load-named') { doLoadPreview(el.dataset.name); return; }
  if (a === 'delete-named') {
    const name = el.dataset.name;
    if (S.arm === `delete:${name}`) {
      deleteNamedMoveset(name);
      S.arm = null;
      renderModal();
      return;
    }
    S.arm = `delete:${name}`;
    renderModal();
    setTimeout(() => { if (S.arm === `delete:${name}`) { S.arm = null; renderModal(); } }, 4000);
    return;
  }
  if (a === 'exit-preview') { S.preview = null; render(); return; }
}

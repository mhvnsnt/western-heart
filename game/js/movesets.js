/* ============================================================
   WESTERN HEART — Movesets (LANE 3: moveset wiring)
   Per-fighter Tekken movelists built from REAL T3 teardown data
   (teardown/tekken3/movesets/moveset_{king,jin,bryan,heihachi,
   xiaoyu,yoshimitsu,gunjack}.json — decoded motion banks).

   Tekken input language: 1=left punch, 2=right punch,
   3=left kick, 4=right kick. Throws: 1+3, 2+4. Strings: 1,2.
   Specials: motion inputs (qcf+2, f,F+1 ...).

   Data files: game/assets/movesets/{fighter_id}.json (45 fighters).
   Every move carries t3_source/t3_row/t3_command provenance.
   Fighters whose Tekken base has no T3 bank use the closest
   archetype proxy — marked "proxy": true with an honest note.
   (T7/TTT2 per-character banks are gapfill lane's extraction work).

   SCHEMA v2 (moveset-editor contract, docs/movesets/MOVESET-SCHEMA.md):
   each move also carries:
     anim_ref    — preview-animation clip ref for the editor's live preview
                   ("t3:king:row:44", "doa:bass:palm-jab", ...)
     input_slots — Tekken input slots the move can occupy in the editor
                   (canonical first; strings also list component inputs)
     move_class  — "strike" | "throw" | "string" | "special" (editor filters)
   Top level: schema_version: 2, plus per-game provenance fields and the
   honest "proxy" flag. v2 is additive — no v1 field was renamed/removed.
   ============================================================ */

// All fighter ids with a wired moveset file (36 playable + 9 staged for lane 2)
import { installAddedMoves } from './full-movelist.js';
export const MOVESET_IDS = [
  'pantera', 'demonio', 'phantom', 'diablo', 'skull', 'samura1', 'sakura',
  'rin', 'byou', 'tou', 'sha', 'kai', 'jin_soul', 'retsu', 'zen', 'gyou',
  'zui', 'kinpo', 'waterfall', 'kingtyrant', 'burger', 'awapop', 'scimitar',
  'purplerain', 'nightwolf', 'dio', 'cyborgx', 'michiko', 'star', 'torch',
  'bruno', 'negativo', 'thor', 'yukihyo', 'slice', 'docfrank',
  'sunra', 'dxmmii', 'realizzt', 'rave', 'kutz', 'chordz', 'vainabel',
  'lili', 'baek',
  // SmutBase 6 pipeline fighters 5-6 (owner 2026-10-23): MEGAMI (Jun Kazama
  // TTT2 kit, Tekken inputs) and MENAJERII (Roger Jr. TTT2 kit, fresh Tekken
  // inputs per owner directive — no Injustice 2 input system).
  'megami', 'menajerii',
  // DOA/VF federation (owner 2026-10-19): converted movelists, Tekken-notation
  'doa-kasumi', 'doa-bass', 'doa-hayabusa',
  'doa-ayane', 'doa-tina', 'doa-jannlee',
  'vf-akira', 'vf-sarah', 'vf-kage',
  // Reskin wave (2026-10-19): first custom attires as selectable fighters.
  'demonio-bloodline-ember', 'doc-frank-machine-shop', 'baek-master-white',
  'mariposa-monarch', 'dxmmii-patchwork',
  // T7 full-moveset wave (2026-10-19): base Mariposa (Zafina) file added.
  'mariposa',
  // Wave 2 (2026-10-19): Demonio winged devil form.
  'demonio-winged',
  // Stream 6 (2026-10-19): Cain Elias (Undertaker archetype, new fighter).
  'cainelias',
  // Burger Kusaregedo kit (owner 2026-10-19): per-form movesets.
  'burger-demon', 'burger-speed-demon', 'burger-the-mouth',
  // Sketchfab intake (owner 2026-10-19): working names, WH names pending.
  'zangief', 'blanka', 'vega', 'iori', 'armor-king',
  // CHARGER (owner 2026-10-20): Blanka replacement — full set in charger.json.
  'charger',
  'dorowani',
  // BUFFALO BILL (2026-10-23, landing wave 1): his per-fighter file
  // (game/assets/movesets/buffalo-bill.json, 228 moves, Law base) existed on
  // main but the id was never listed, so the loader never loaded it.
  'buffalo-bill',
  // CHATUR (owner 2026-10-23): True Ogre's WH replacement — chatur.json
  // (True Ogre T3 kit + four-armed canon specials).
  'chatur',
  // POND (owner 2026-10-23): Raven's WH replacement — pond.json
  // (T7 Raven kit + still-water canon specials).
  'pond',
  // DEATHFANG (owner 2026-10-19): proprietary, Iori-based — full Iori kit in deathfang.json.
  'deathfang',
  // DEATHFANG werewolf form (owner 2026-10-20): full kit + beast mix-ins, Iori stance kept.
  'deathfang-werewolf',
  // Custom fighters (owner 2026-10-19): KRONOS — Zangief base + Golem (Urban Reign) mix.
  'kronos',
  // Fighter-completeness audit (2026-10-21, docs/FIGHTER-COMPLETENESS-AUDIT-2026-10-21.md):
  // per-id files that EXISTED but were never loaded — the loader keys by roster
  // id, so these fighters silently fought on the legacy T3 aggregate instead of
  // their own sets. kronos-attire2 = his own Timberwolf set (142 moves);
  // demonio-human = Demonio's human-form set (102 moves); charger-attire2 =
  // Charger Attire 2's set (charger-attire2.json, his roster entry's declared
  // moveset 'charger').
  'kronos-attire2', 'demonio-human', 'charger-attire2',
  // Ryuji Yamazaki x The Rock hybrid (owner 2026-10-19): 22 moves, King-proxy
  // throws incl. ROCK BOTTOM (frame data from T3 King chain row 281). Model
  // pending the owner's Tripo link — roster-full.js entry lands with model.glb.
  'ryuji-rock',
  // Intake wave 2 (owner 2026-10-19): remaining four intake movesets.
  'hugo', 'raiden', 'marduk', 'bob',
  // Custom fighters (owner 2026-10-19): KORESHI (owner creation).
  // (deathfang already listed above; not duplicated.)
  'koreshi',
  // Doc Frank Frankenstein attire (moveset lane 2026-10-21): full gunjack set,
  // sibling attire of doc-frank-hood (identical T3 source data, same DOC FRANK).
  'doc-frank-frankenstein',
  // T3 round-2 banks (worker 36, 2026-10-22): per-bank moveset files from
  // tools/gen-movesets-t3.py — 2,528 moves across 13 banks. Banks with WH
  // fighters (eddy, lei, bosconovitch) already merged via merge_sources.py;
  // these are the standalone bank files.
  't3-paul', 't3-law', 't3-lei', 't3-nina', 't3-hwoarang', 't3-eddy',
  't3-julia', 't3-kuma', 't3-ogre', 't3-anna', 't3-bosconovitch',
  't3-gon', 't3-forestlaw',
  // SmutBase intake wave 6 (owner 2026-10-23): RYUSAN (Lucky Chloe T7 kit,
  // game/assets/movesets/ryusan.json) + TOBI (Hwoarang T3 kit,
  // game/assets/movesets/tobi.json). Canon: roster/mina-ashido + roster/miruko.
  'ryusan', 'tobi',
  // Landing wave 3 (2026-10-23, docs/CATCHUP-AUDIT-2026-10-23.md): the last
  // three audit fighters whose pieces are complete — GASHADOKURO (Kuma's
  // proprietary successor; gashadokuro.json = the T3 Kuma bank as his own
  // file), AOTSUKI (Panda's proprietary successor; aotsuki.json rides the
  // same T3 bear bank, proxy-flagged in-file), SILVERTONGUE (Lili re-owned;
  // silvertongue.json = her full kit authored as her own file).
  'gashadokuro', 'aotsuki', 'silvertongue',
];

const _movesets = {};
const _loading = {};
let _index = null;
let MS_BASE = 'assets/movesets/'; // relative to the page; the creation suite points it at ../../game/assets/movesets/
export function setMovesetBase(url) { MS_BASE = url.endsWith('/') ? url : url + '/'; }
// Browser global mirror (fighter.js reads window.WH_MOVESETS); guarded for Node tests.
const _g = (typeof window !== 'undefined') ? window : (typeof globalThis !== 'undefined' ? globalThis : {});

/* LAZY LOADING (2026-10-21). The merged movesets (T8 + T7 + T3 + history, docs/movesets/
   SOURCE-MERGE-2026-10-21.md) total ~30 MB; boot loads only assets/movesets/index.json
   (id -> display, base, t3_source, anim_bank, counts) and a fight loads its own fighters
   through ensureMovesets() before the Fighter objects are built. */
export async function loadFighterMovesets() {
  _g.WH_MOVESETS = _g.WH_MOVESETS || {};
  try {
    const t = await fetch(MS_BASE + 't3_input_tables.json');
    if (t.ok) setInputTables(await t.json());
  } catch (e) { /* decoded defaults below */ }
  try {
    const r = await fetch(MS_BASE + 'index.json');
    if (r.ok) _index = await r.json();
    console.log(`[WH] Moveset index: ${_index ? Object.keys(_index.fighters || {}).length : 0} fighters (full sets load per fight)`);
  } catch (e) {
    console.warn('[WH] Could not load moveset index:', e);
  }
}

function _fetchOne(id) {
  if (!id) return Promise.resolve(null);
  if (_movesets[id]) return Promise.resolve(_movesets[id]);
  if (_index && _index.fighters && !_index.fighters[id]) return Promise.resolve(null);
  if (!_loading[id]) {
    _loading[id] = fetch(`${MS_BASE}${id}.json`)
      .then(r => (r.ok ? r.json() : null))
      .then(d => { if (d) registerMoveset(id, d); return d; })
      .catch(e => { console.warn(`[WH] moveset ${id} failed to load:`, e); return null; });
  }
  return _loading[id];
}

/** Load the full movesets for these fighter ids (call before building Fighters), plus the
    movesets their editor loadouts borrow from (base moveset / other fighters' moves). */
export async function ensureMovesets(ids) {
  const list = [...new Set((ids || []).filter(Boolean))];
  const deps = [];
  for (const id of list) deps.push(...loadoutDeps(id));
  const all = [...new Set(list.concat(deps))];
  await Promise.all(all.map(_fetchOne));
  return list.map(id => _movesets[id] || null);
}

/** Index of every fighter moveset (null until loadFighterMovesets resolves). */
export function getMovesetIndex() { return _index; }

/** Synchronous accessor: the FULL moveset (null until ensureMovesets/registerMoveset). */
/** Chain-throw stage tag (Tekken multi-part throws, e.g. King's Arm Breaker chain).
 *  A throw named 'Arm Breaker (AB1)' opens stage AB1; its follow-ups are keyed 'AB1.<buttons>'.
 *  A T7 throw without a code ('Arm Breaker') opens ARM_BREAKER ('(During Arm Breaker) 1+2,1+2'). */
export function throwStageTag(name) {
  const n = String(name || ''); const m = /\(([A-Z]+\d+[a-z]?)\)/.exec(n);
  return m ? m[1] : n.toUpperCase().replace(/[^A-Z0-9]+/g, '_').replace(/^_+|_+$/g, '') || null;
}
/** Moveset keys of one chain-throw stage ('AB1.1,1+2', ...). */
export function throwStageKeys(fighterId, tag) {
  const ms = getFighterMoveset(fighterId); if (!ms || !tag) return [];
  const c = ms._stageKeys || (ms._stageKeys = {});
  return c[tag] || (c[tag] = Object.keys(ms.moves).filter((k) => k.startsWith(tag + '.')));
}

/* KOF XV system actions (moveset sweep 2026-10-29): the row's qualifier names the engine
   system that owns it. Dream Cancel wiki, KOF XV Defense / Offense / Meters pages. */
export function systemTagOf(input) {
  const s = String(input || '');
  if (/\(guard\)/i.test(s)) return 'guard';
  if (/\(MAX\)/.test(s)) return 'max';
  if (/\(taunt\)/i.test(s)) return 'taunt';
  if (/\(throw escape\)/i.test(s)) return 'throw_escape';
  if (/\(roll\)/i.test(s)) return 'roll';
  if (/\(backdash\)/i.test(s)) return 'backdash';
  if (/\(dash\)/i.test(s)) return 'dash';
  return null;
}
/** This fighter's system rows: [{ key, sys, input (canonical) }]. Cached. */
export function systemRows(fighterId) {
  const ms = getFighterMoveset(fighterId);
  if (!ms || !ms.moves) return [];
  if (ms._sysRows) return ms._sysRows;
  const out = [];
  for (const [k, mv] of Object.entries(ms.moves)) {
    const sys = mv && systemTagOf(mv.input);
    if (sys) { mv.system = sys; out.push({ key: k, sys, input: canonNotation(mv.input) }); }
  }
  return (ms._sysRows = out);
}
export function getFighterMoveset(fighterId) {
  const m = _movesets[fighterId] || _g.WH_MOVESETS?.[fighterId] || null;
  return m && m.moves ? m : null;
}

/** Full moveset if loaded, else its index entry ({display, tekken_base, t3_source, anim_bank, ...}). */
export function getMovesetInfo(fighterId) {
  return _movesets[fighterId] || (_index && _index.fighters && _index.fighters[fighterId]) || null;
}

/** Register a moveset object directly (fetch path + Node test harness). */
export function registerMoveset(fighterId, data) {
  installAddedMoves(fighterId, data); // pt217u: EMWH additions (additive, never overwrites a slot)
  _prepare(data);
  _movesets[fighterId] = data;
  _g.WH_MOVESETS = _g.WH_MOVESETS || {};
  _g.WH_MOVESETS[fighterId] = data; // full per-fighter moveset wins over the legacy aggregate
}

/* ---- Notation tables ----------------------------------------------------------------
   `slots` (tools/moveset-merge/merge_sources.py) maps every Tekken notation to the move key
   it fires by default; keys that are themselves notations map to themselves (files without
   slots keep working). Motion notations are pre-parsed for the buffer. */
const STATE_PREFIX = /^((?:[A-Za-z][A-Za-z0-9_]*\.)+)(.*)$/;
const DIR_TOKEN = /^(d\/f|d\/b|u\/f|u\/b|f|b|u|d|n|D\/F|D\/B|U\/F|U\/B|F|B|U|D|N)$/;
const MOTION_DIRS = {
  qcf: ['d', 'd/f', 'f'], qcb: ['d', 'd/b', 'b'],
  hcf: ['b', 'd/b', 'd', 'd/f', 'f'], hcb: ['f', 'd/f', 'd', 'd/b', 'b'],
};

/* DECODED T3 INPUT TIMING (tools/moveset-merge/t3_input_tables.py -> t3_input_tables.json):
   motion windows come from the USA EXE sequence tables (frames), the dash from FUN_8002CB08
   (direction, neutral, direction within 0x13 frames), history = 60 one-frame entries.
   TIMEBASE (input-timing fix 2026-10-24): every frame count here is a T3 frame of 1/60 s, but
   the fight loop ticks at FIXED_DT = 1/120 (game.js) and fed one history entry per tick, so each
   window was half as long as decoded (qcf 208 ms instead of 417, f,f ~160 ms, "held" after 67 ms
   instead of 133). Now noteDirection(dir, dt) stores each entry's length in frames (dt * 60) and
   the history walks below measure TIME in frames, not entries, at any tick rate. A call without
   dt is one whole frame (tests / tools feed the history frame by frame). */
const INPUT_FPS = 60;      // T3 frames per second: the unit of every frame constant here
let DOUBLE_TAP_BUDGET = 0x13;
/* Running state (Tekken WR / 'while running'; TekkenDocs, wavu wiki): a forward dash that keeps
   the stick held forward for RUN_HOLD_FRAMES, or a third forward tap inside the dash, turns into a
   run. Releasing forward leaves RUN_GRACE_FRAMES to press the running move. */
const RUN_HOLD_FRAMES = 15, RUN_GRACE_FRAMES = 8;
let DASH_FRAMES = { 'f,f': 30, 'b,b': 32 }; // decoded: every bank's dash row is 30 frames, backdash 30-35
const HIST_FRAMES = 60;    // history span in frames (fight_sim HISTORY)
const CHARGE_FRAMES = 40;  // charge motions: frames held in the charge direction (APPROXIMATE, SF/KOF ~40-45f)
const CHARGE_RELEASE = 10; // frames allowed between leaving the charge and the motion's last step
const HIST_LEN = 512;      // ring entries: HIST_FRAMES of time at any tick rate up to ~500 Hz
const T_EPS = 1e-6;        // float slack when summing entry lengths
const MOTION_HOLD = 4; // v2: final motion step held this long = capital spelling (f,f,F)
const HOLD_FRAMES = 8; // v2: a direction held this long reads as the HELD spelling (D/F+2)
const STRING_PENDING = 1500; // v2: ms a partial string stays open (legacy continuation window; batch 2026-10-24: 800 -> 1500 for touch cadence)
let _seqWindows = null; // 'd,d/f,f' -> frames (directions without neutral steps)
export function setInputTables(t) {
  if (!t) return;
  if (t.double_tap_budget) DOUBLE_TAP_BUDGET = t.double_tap_budget;
  if (t.dash_frames) DASH_FRAMES = Object.assign({}, DASH_FRAMES, t.dash_frames);
  _seqWindows = {};
  const byLen = {};
  for (const sq of t.sequences || []) {
    const d = sq.dirs.filter(x => x !== 'n');
    if (!d.length) continue;
    const k = d.join(',');
    _seqWindows[k] = Math.max(_seqWindows[k] || 0, sq.window);
    (byLen[d.length] = byLen[d.length] || []).push(sq.window);
  }
  _seqWindows.__byLen = {};
  for (const [n, ws] of Object.entries(byLen)) { ws.sort((a, b) => a - b); _seqWindows.__byLen[n] = ws[ws.length >> 1]; }
}
function motionWindow(dirs) {
  dirs = dirs.filter(d => d !== 'n'); // table keys are the direction steps without neutrals
  const k = dirs.join(',');
  if (_seqWindows && _seqWindows[k]) return _seqWindows[k];
  if (_seqWindows && _seqWindows.__byLen[dirs.length]) return _seqWindows.__byLen[dirs.length];
  return 25; // qcf's decoded window (n,d,d/f,f = 25 frames) when the table is not loaded
}

export function splitNotation(n) {
  const m = STATE_PREFIX.exec(n);
  return m ? { prefix: m[1], body: m[2] } : { prefix: '', body: n };
}

/** 'f,F+2' -> {prefix:'', dirs:['f','f'], btn:'2', neutral:false}; null if not a motion input. */
/* KOF/SF close-normal range (m, root to root): a plain button within it fires the close normal,
   beyond it the far normal. Standing bodies never get nearer than 1.45 m (fighter.js push
   minDist); KOF close range is a short step past body contact, inside far-jab reach. */
export const CLOSE_RANGE = 1.65;

export function parseMotion(n) {
  const { prefix, body } = splitNotation(n);
  const parts = body.split(',');
  const last = parts[parts.length - 1];
  const lm = /^(?:(qcf|qcb|hcf|hcb|d\/f|d\/b|u\/f|u\/b|f|b|u|d|D\/F|D\/B|U\/F|U\/B|F|B|U|D)\+)?([1-4](?:\+[1-4])*)\*?$/.exec(last);
  if (!lm) return null;
  const head = parts.slice(0, -1);
  /* SF/KOF charge motions ('charge_b,f+1', 'charge_d,u+3', 'charge_db,f+3'): hold the charge
     direction CHARGE_FRAMES, then the rest of the motion. Before (moveset sweep 2026-10-29)
     'charge_X' was no direction token, so these moves were unreachable in a fight. */
  let charge = null;
  const cm = head.length ? /^charge_(b|d|db|d\/b|u|f)$/i.exec(head[0]) : null;
  if (cm) { charge = _DIAG[cm[1].toLowerCase()] || cm[1].toLowerCase(); head.shift(); }
  // KOF/SF heads may chain named motions ('hcb,f+1', 'qcf,qcf+1', 'qcb,qcf+3'): expand them.
  if (head.some(p => !DIR_TOKEN.test(p) && !MOTION_DIRS[p])) return null; // a button earlier = string, not motion
  let dirs = [].concat(...head.map(d => MOTION_DIRS[d] || [d.toLowerCase()]));
  // 'f,n,2': the stick returns to neutral and the button comes with NO direction. 'd/b,n,f+2':
  // the n is a real step between directions — T3's sequences carry explicit neutral steps
  // (n,d/f,n,d/f = tap d/f twice), so inner n's stay; only leading/trailing ones go.
  const neutral = !lm[1] && dirs.length > 0 && dirs[dirs.length - 1] === 'n';
  while (dirs.length && dirs[0] === 'n') dirs.shift();
  if (neutral) while (dirs.length && dirs[dirs.length - 1] === 'n') dirs.pop(); // 'f,n,2' only
  if (lm[1]) {
    if (MOTION_DIRS[lm[1]]) dirs = dirs.concat(MOTION_DIRS[lm[1]]);
    else dirs.push(lm[1].toLowerCase());
  }
  // 'b,3' / 'd,1' (moveset sweep 2026-10-28): ONE direction tap, release, then the bare
  // button. Returned as a neutral-ending motion so V2 matches tap -> neutral -> press;
  // before, it was dropped here as a 'plain directional' and only the plain 3 ever fired.
  if (charge) return dirs.length ? { prefix, dirs, btn: lm[2], neutral, charge } : null;
  // 'f,n,1' / 'u/f,n,4' are the same tap with the release written out (sweep 2026-10-29: 427 rows
  // fired the plain button because the explicit n made head.length 2).
  if (!lm[1] && dirs.length === 1 && dirs[0] !== 'n' && head.filter(p => p.toLowerCase() !== 'n').length === 1) return { prefix, dirs, btn: lm[2], neutral: true };
  if (dirs.filter(d => d !== 'n').length < 2 && !(lm[1] && MOTION_DIRS[lm[1]])) return null; // plain directional
  return { prefix, dirs, btn: lm[2], neutral };
}

export function legacyAlias(key) {
  const m = /^((?:qcf|qcb|hcf|hcb|dp|[udfbUDFB](?:\/[udfbUDFB])?)\+)?([PK])$/.exec(key);
  return m ? (m[1] || '') + (m[2] === 'P' ? '1' : '4') : null;
}
/* Display spellings the input buffer never emits ('df+1', 'ws1', 'WS 1', 'SAV b+2', 'FC 1',
   '(d/f+1)', 'uf+4') -> the canonical notation it does ('d/f+1', 'WS.1', 'SAV.b+2', ...). Moves
   keyed in those spellings were unreachable in a fight; _prepare slots them on the canonical
   input too (when nothing else owns it). Returns the input unchanged if nothing applies. */
const _DIAG = { df: 'd/f', db: 'd/b', uf: 'u/f', ub: 'u/b', DF: 'D/F', DB: 'D/B', UF: 'U/F', UB: 'U/B' };
/** Named move state ('Bad Stomach') -> stance code ('BAD_STOMACH'). */
export function stateCode(name) { return String(name).trim().toUpperCase().replace(/[^A-Z0-9]+/g, '_').replace(/^_|_$/g, ''); }
const TILDE_WINDOW = 0.1; // s (6 frames): '~' = pressed immediately after the previous input
// Separator order for a follow-up: inside TILDE_WINDOW the '~' branch wins over ',' (wavu wiki).
const sepOrder = (ctx) => (ctx && ctx.attackT != null && ctx.attackT <= TILDE_WINDOW ? ['~', ',', ':'] : [',', '~', ':']);
export function canonNotation(n) {
  if (typeof n !== 'string') return n;
  let s = n.trim().replace(/\s*\((?:first|second|third|\d+(?:st|nd|rd|th)) hits? only\)\s*$/i, ''); // T7 per-hit row annotation, same input
  s = s.replace(/\s*\(only during hit from front\)\s*$/i, ''); // T7 hit-condition annotation (sweep 2026-10-30, Pantera t7.king_110 'b+2, 4 (only during hit from front)'): the 4 follow-up fires only when b+2 hits the foe from the front — and the sweep's default setup IS front-facing (foe standing facing the attacker), so the bare input 'b+2,4' is the stated situation, not a strip that changes the input. TRAILING-ONLY, anchored to the literal phrase, and placed here before the final paren-to-words rule below, which would otherwise turn the note into bare words parse() rejects.
  s = s.replace(/[\u200B\u200C\u200D\uFEFF]/g, ''); // scraped-list invisible separators (cyborgx back-to-wall key carries \u200b between steps); they carry no notation meaning
  /* Trailing spin-count annotations (sweep 2026-10-30, Cyborg X t7 rows): 'WS 1+2*
     (one spin)' / 'WS 1+2 (two spins)' / '(During Clockwork) 3 (more than a single
     spin)' carry the spin count as an animation descriptor, not an extra input — the
     two WS rows stay distinct after stripping via the hold mark ('WS.1+2*' vs
     'WS.1+2', 14 dmg/-4 vs 16 dmg/0), the same pattern as the JGS spin rule's
     comment ('the spin count is a repeat of the stance entry, same input') and the
     trailing-note strips below ('(close)', '(rush)'). This MUST run before the
     whole-string paren rule below: '(During Clockwork) 3 (more than a single spin)'
     both starts with '(' and ends with ')', so that rule's greedy capture would eat
     the outer parens and the during rule would never fire. Without this strip, the
     final paren rule turns the note into bare words ('WS.1+2* one spin') and
     parse() rejects the row as 'unparsed'. TRAILING-ONLY: a spin paren mid-string
     ('CLK(Two spins).3') is a different row from 'CLK.3' (22 dmg/+0 vs 20 dmg/-9)
     and is left untouched, as are the non-trailing JGS spin rows. */
  s = s.replace(/\s*\([^()]*\bspins?\b[^()]*\)\s*$/i, '');
  s = s.replace(/^\((.*)\)$/, '$1').trim();
  /* Direction alternatives in a single step (sweep 2026-10-30, Pantera 'ss2+4,b/db'):
     a step written '<cardinal>/<diagonal>' ('b/db', 'f/df') lists two directions for one
     step — the first listed is the playable one, the same first-listed rule the alternatives
     rule below already applies to '1+3_2+4' / 'd/b+1/2/3' / 'U/F or U/B'. This MUST run
     before the diagonal expansions below: without it the later diagonal rule turns 'db'
     into 'd/b' and the step becomes the unparseable 'b/d/b'. The row's own T8 id settles
     which alternative is first: the move (name 'Reverse Special Stretch Bomb (Cancel)')
     carries t8_id 'King-ss2+4,b', and T8 ids in this moveset are 'King-' + the full T8
     input with commas preserved (e.g. 'King-1,2,1,d+2+4'), so a sequence reading 'b,d/b'
     would have read 'King-ss2+4,b,d/b'. NOT a diagonal: a lone diagonal ('d/f', 'u/b')
     has a single letter after the slash and is untouched, as is 'b/f+X' (WR. rule below).
     Blast radius in the core-8 movesets: exactly this one row (key, input and slot are
     the same string). */
  s = s.replace(/(^|[.,~:])([bBfFuUdD])\/(df|db|uf|ub|DF|DB|UF|UB)(?=$|[,+~:])/g, '$1$2');
  /* FGC numpad-letter shorthand (moveset sweep 2026-10-29): 'df' / 'db' / 'UF' as a step of the
     input are Tekken's d/f / d/b / U/F ('f,n,d,df' crouch dash, 'f,f,db', 'FLE.db'). Before, the
     whole row was unparseable for every fighter that carries one. */
  s = s.replace(/(^|[.,~:])(df|db|uf|ub|DF|DB|UF|UB)(?=$|[,+~:#])/g, (m, p, t) => p + _DIAG[t]);
  // Tekken 'back to opponent, X' (TekkenDocs / wavu wiki: BT X) -> BT.X
  s = s.replace(/^back to (?:the )?opponent\s*,\s*/i, 'BT.');
  /* Back-to-wall rows (sweep 2026-10-30, r17 core-8): '(back to wall).b,b,UB' /
     '(Back to wall).b,b,UB' (Pantera / Cyborg X / Burger) are wall-jump attacks whose
     input has no button — the sweep's own taxonomy classes buttonless inputs as movement
     (n/a), not failures, so the context becomes the WALL. prefix and the row leaves the
     failing list on the next sweep. Wall-position witnessing (press the motion with the
     back actually at the wall) is the recorded residual, not hidden. */
  s = s.replace(/^\(?back to wall\)?\s*\.\s*/i, 'WALL.');
  /* Approach-crouching rows (sweep 2026-10-30, Pantera t7.king_229/230/268):
     Tekken crouch throws, pressed only when the foe is crouching and the attacker has
     closed in: 'Approach crouching enemy... d+1+3' -> 'CROUCHFOE.d+1+3'. The sweep's
     setup('CROUCHFOE') plays exactly that situation (foe crouching, close), the way
     condSetup already plays a crouching foe for T3 condition rows — not an n/a, because
     the crouching-foe state exists and is playable, unlike the ground-orientation state
     behind the enemy-on-back n/a. Timing rows ('Time with enemy...') and the wall-stun
     row ('During enemy wall stun...') were deliberately NOT covered here: they needed a
     timed-opponent-attack setup and a wall-stun state respectively, and each got its own
     chunk after this one (TIMERP/TIMELK/TIMERK, then WALLSTUN). */
  s = s.replace(/^approach crouching enemy\.\.\.\s*(?=[udfbnUDFB1-4])/i, 'CROUCHFOE.');
  /* Timing throws (sweep 2026-10-30, Pantera t7.king_295-297): Tekken reversal throws,
     pressed while the foe is attacking with the stated limb — 'Time with enemy right
     punch... b+1+3' (Arm Whip) -> 'TIMERP.b+1+3', 'Time with enemy left kick... b+2+4'
     (Spinning Heel Hold) -> 'TIMELK.b+2+4', 'Time with enemy right kick... b+2+4' (Leg
     Screw) -> 'TIMERK.b+2+4'. The sweep's setup() plays exactly that situation (foe
     attacking with 2/3/4, close), the way condSetup already plays an attacking opponent
     for T3 condition rows — not an n/a, because the attacking-foe state exists and is
     playable, and not a canon strip, which would attempt reversal throws against a
     standing, non-attacking foe. Limb-anchored, so the generic 'Time with enemy
     attack...' prose on Cyborg X / Demonio REV rows (which lives only in
     t7_command/input_note, never in the input field) is untouched. The wall-stun
     row ('During enemy wall stun...') is covered by the WALLSTUN rule below, its own
     chunk. Button map 1 = left punch, 2 = right punch,
     3 = left kick, 4 = right kick, per this file's Tekken input language header. */
  s = s.replace(/^time with enemy (right punch|left kick|right kick)\.\.\.\s*(?=[udfbnUDFB1-4])/i, (m, limb) => ({ 'right punch': 'TIMERP.', 'left kick': 'TIMELK.', 'right kick': 'TIMERK.' })[limb.toLowerCase()]);
  /* Wall-stun row (sweep 2026-10-30, Pantera t7.king_247): Tekken wall-splat throw,
     pressed while the foe is stuck to the wall — 'During enemy wall stun... f, hcf+1'
     (Shining Torpedo) -> 'WALLSTUN.f,hcf+1'. The sweep's setup() plays exactly that
     situation (foe in the engine's 'wallsplat' state with the WALL_SPLAT_STUN window,
     close), the way setup('CROUCHFOE') plays a crouching foe and setup('TIMER*') plays
     an attacking foe — not an n/a, because the wallsplat state exists in fighter.js
     (entered at the arena wall, 0.55 s stun), and not a canon strip, which would
     attempt a wall throw against a standing foe. Blast radius: exactly this one row
     across the core-8 movesets (the rule is anchored to the literal prose prefix). */
  s = s.replace(/^during enemy wall stun\.\.\.\s*(?=[udfbnUDFB1-4])/i, 'WALLSTUN.');
  /* Running moves (TekkenDocs / wavu wiki 'WR', 'while running'): 'WR+2', 'WR 2', 'while running 2'
     -> 'WR.2'. T3's running rows carry the command '4/6+X' (any horizontal while in the run),
     imported as 'b/f+X' — never a real stick direction — so they are WR rows too (True Ogre / Chatur). */
  s = s.replace(/^(?:WR|wr)\s*[.+]?\s*(?=[1-4])/, 'WR.').replace(/^\(?while[- ]running\)?\s*,?\s*(?=[1-4])/i, 'WR.').replace(/^b\/f\+(?=[1-4])/, 'WR.');
  // 'n+1' / 'n+1+2' (stick explicitly neutral) is the plain button: the input buffer reads a
  // neutral press as '1', so a move slotted on 'n+1' could never be pressed (sweep 2026-10-29, donor banks).
  s = s.replace(/(^|\.)n\+(?=[1-4])/i, "$1");
  /* State-gated rows (sweep 2026-10-29): Tekken ground states and named custom states become
     stance prefixes the input buffer already resolves. 'while on back, feet towards opponent, 3'
     -> 'FUFT.3' (face up, feet towards; plain 'while on back' is the same lying state),
     'while on back, head towards opponent, 4' -> 'FUHT.4'; 'during Bad Stomach, 1+2' /
     'during Elbow Drop 1+4' -> 'BAD_STOMACH.1+2' / 'ELBOW_DROP.1+4' (stateCode). _prepare maps
     the move that enters the state (same name) to it in stance_after. */
  s = s.replace(/^while on back(?:\s*,\s*(feet|head) towards opponent)?\s*,\s*(?=[udfbnUDFB1-4](?:[\/+,]|\s*,|$))/i,
    (m, w) => (w && w.toLowerCase() === 'head' ? 'FUHT.' : 'FUFT.'));
  /* 'during X' rows whose follow-up starts with a motion (sweep 2026-10-30, Deathfang
     saika): 'during Ya Otome, qcf,qcf,qcf,qcf+1+2' used to fall through this rule because
     its lookahead accepted only direction/button starts, leaving an unparseable
     'during Ya Otome,qcf,...' row. Motion starts (qcf/qcb/hcf/hcb/dp) now qualify, so
     the row canonicalises to 'YA_OTOME.qcf,qcf,qcf,qcf+1+2' — the same stance-prefix
     pattern the sweep's setup() already plays (default case sets f.stance = pre) and
     _prepare already slots on its prefixed input. Direction/button starts unchanged. */
  s = s.replace(/^during\s+([A-Za-z][A-Za-z' ]*?[A-Za-z](?: \d(?=\s*,))?)\s*,?\s*(?=(?:qcf|qcb|hcf|hcb|dp)(?:[+,~:]|$)|[udfbnUDFB]?(?:\/[fbFB])?\+?[1-4](?:[+,~:]|$))/, (m, name) => (/vertical/i.test(name) ? m : /^(forward or backward jump|forward jump peak|forward jump|jump)$/i.test(name) ? 'AIR.' : stateCode(name) + '.'));
  s = s.replace(/(?:\s*\((?:KOFXV|KOF\s*XV|SFV|sfv|SF6|sf6|T7|T8)\))+\s*$/, ''); // source-game tag on imported rows, same input
  s = s.replace(/^(d(?:\/[fb])?\+[1-4](?:\+[1-4])*)\s*\(crouch(?:ing)?\)$/i, '$1'); // KOF '(crouch)' note on a d+ button, same input
  s = s.replace(/^fc\s*\+?\s*(?=[1-4udfbnUDFB])/i, 'FC.'); // 'fc+1' / 'FC 1' -> FC.1 (full-crouch state)
  s = s.replace(/^\(During Rage\)\s*/i, 'R.');
  /* KOF context notes on imported rows (moveset sweep 2026-10-29, ryuji-rock): the input is the
     same, the note is a distance / auto-combo / opponent-state condition. 'far 1', '1 (close)',
     '1 (Rush)', 'hop u/f+1', 'hcb,hcb+1+2 near', 'f,n,d,d/f+1 downed' -> the bare input;
     'qcb+3 hold' -> 'qcb+3*' (button held). */
  s = s.replace(/^(?:far|close|cl\.?|st\.?|hop|jump|j\.)\s+(?=[udfbnUDFB1-4])/i, '');
  s = s.replace(/\s*\((?:close|far|rush|near|hop|downed|grounded|air|midair)\)\s*$/i, '');
  s = s.replace(/\s+(?:near|close|far|downed|grounded|on downed opponent|rush)$/i, '');
  s = s.replace(/^(?:grounded|downed)\s+(?=[udfbnUDFB1-4])/i, '');
  s = s.replace(/^(.*[1-4])\s+hold$/i, '$1*');
  s = s.replace(/^(.*[1-4])\s*\((?:hold|held|keep)\)$/i, '$1*');
  s = s.replace(/^\((BT|FC|WS|SS)\)\s*(?=[udfbnUDFB1-4])/, '$1.'); // '(BT) 2' -> BT.2
  s = s.replace(/^\((?:grounded|downed|ground)\)\s*/i, '');
  // KOF mash follow-up: 'hcb,hcb+1+2 (near), tap 1x3' -> 'hcb,hcb+1+2,1,1,1'
  s = s.replace(/,\s*tap\s+([1-4](?:\+[1-4])*)(?:\s*x\s*(\d))?$/i, (m, btn, n) => ','.concat(Array(+(n || 1)).fill(btn).join(',')));
  // T7 stance list spelling: 'JGS, 1' / 'JGS* (3 spins), 1' -> 'JGS.1' (press from the stance;
  // the spin count is a repeat of the stance entry, same input)
  s = s.replace(/^([A-Z][A-Z0-9_]{1,})\*?(?:\s*\(\d+\s*spins?\))?\s*,\s*(?=[udfbUDFB]?(?:\/[udfbUDFB])?\+?[1-4])/, '$1.');
  // descriptive note words in parentheses after a button: '(guard)', '(knife)', '(gedan)', '(max)'...
  s = s.replace(/([1-4*])\s*\((?:near|far|close|rush|knife|gedan|max|MAX|tap|guard|ground|blowback|Irish-whip variant|throw escape|taunt)\)/g, '$1'); // T7 list spelling of the rage state prefix
  s = s.replace(/^([fb]),\1\s*\((?:roll|dash|backdash)\)$/i, '$1,$1'); // KOF system rows: double tap
  /* Annotated notations (sweep class 2, 2026-10-29): the note is a mode / variant / meter tag on
     the same input. '3+4 (cyclone1)', 'n+1+2 (claw)', 'n+1 (nc)', '2+4 (vs2)', '3+4 (vshift, break)',
     '1 (DF)' -> the bare input; a ', hold' / '(charge)' note means the button is held -> '*'.
     '1+2_od' (SF6 OD / KOF EX version on the same buttons) -> '1+2'.  'air_charge_b,f+1' -> 'charge_b,f+1'
     (air is the context, the motion is the same). '360+2' -> 'f,d,b,u+2' (full circle, any start).
     'fc,f+1+3' -> 'FC.f+1+3'. */
  s = s.replace(/\s*\((?:cyclone\d*|claw|nc|vs\d|vshift|vrev|vt\d|gsr|neutral|DF|sfv|parry|break|charge|hold)(?:\s*,\s*(?:hold|break|charge))*\)/gi,
    (m) => (/(?:hold|charge)\s*\)$/i.test(m) ? '*' : ''));
  s = s.replace(/([1-4])_od\b/gi, '$1');
  s = s.replace(/^air_(?=charge_)/i, '');
  s = s.replace(/^360\+(?=[1-4])/, 'f,d,b,u+');
  s = s.replace(/^fc\s*,\s*(?=[udfbUDFB])/i, 'FC.');
  s = s.replace(/\b(df|db|uf|ub|DF|DB|UF|UB)(?=\+|,|$|~|:)/g, (m) => _DIAG[m]);
  s = s.replace(/^(ws|WS)\s*(?=[1-4])/, 'WS.');
  /* Batch 4 (FGC / TekkenDocs list spellings, moveset sweep 2026-10-29): 'ws+2' / 'WS+1,3' /
     'BT+1' / 'FC+3' / 'SS+1+2' write the state as a direction-like prefix; the input is the
     state's press -> 'WS.2', 'BT.1', 'FC.3', 'SS.1+2'. '3,4>3' ('>' = next hit with no delay,
     RBNorway/T7 lists) is the same string press -> '3,4,3'. HTML-escaped separators from scraped
     lists ('df+1,&amp;#58;2*') decode to their character; a frame-count note on a hold
     ('1+2* (40f)') is the same held input. */
  s = s.replace(/&amp;/g, '&').replace(/&#(\d+);/g, (m, c) => String.fromCharCode(+c));
  /* Just-frame marker (sweep 2026-10-30, Demonio 'CD.df#1' / 'CD.df#2'): '#' between a
     diagonal direction and a button is Tekken's just-frame mark — the rows' own t8_id
     spells the same slot '${justFrame}' ('Jin-CD.df${justFrame}1'), and the same move
     already exists in this moveset in the ':' spelling ('CD.d/f:1', same name, same
     anim_ref, same on-block -13), where ':' is the codebase's just-frame separator
     (the sweep's parse() splits on ':' and presses ':' steps on a 6-frame cadence vs
     9 for ','). So 'CD.df#1' -> 'CD.d/f:1'. This MUST run after the entity decode
     above: '&amp;#58;' must decode to ':' first, or a '#' rule here would corrupt it
     into ':58;'. Narrow: only a diagonal direction immediately followed by '#' and a
     button — prose '#' elsewhere is untouched, and the ':' row keeps its own slot
     (_prepare only adds a canon slot when not already present), so the sweep equips
     the # row on its canonical notation through the loadout. Residual, stated plainly:
     parse + loadout attempt, not a witnessed frame-perfect just-frame pass — the ':'
     cadence is the codebase's existing just-frame representation, not a frame-perfect
     timing gate. Blast radius across the core-8 movesets: exactly these two rows. */
  s = s.replace(/((?:[dD]\/[fFbB]|[uU]\/[fFbB])|(?:df|db|uf|ub|DF|DB|UF|UB))#(?=[1-4])/g, (m, t) => (_DIAG[t] || t) + ':');
  s = s.replace(/^(ws|WS|fc|FC|bt|BT|ss|SS)\+(?=[1-4udfbUDFB])/, (m, st) => st.toUpperCase() + '.');
  s = s.replace(/([1-4*])\s*\(\d+\s*f\)/gi, '$1');
  s = s.replace(/,:/g, ':');
  s = s.replace(/([1-4])>(?=[udfbUDFB]?(?:\/[udfbUDFB])?\+?[1-4])/g, '$1,');
  s = s.replace(/^([A-Z][A-Z0-9_]{1,})\s+(?=[1-4udfbnUDFB(])/, '$1.');
  /* DES.BT two-word stance (Cyborg X t7.alisa_235 'DES BT 1 (or 2)', sweep 2026-10-30):
     the stance-space rule above dots only the first word, leaving 'DES.BT 1'
     unparseable; join the second word before a button, as the existing DES.BT.1
     row already spells it. That row is the same move (Hertz Blade - Flare,
     6x4 multi-hit, startup 0.317, -9/KND), not a different row — the t7 row's
     'damage 14' is the mod-source figure, its damage_raw is 24. */
  s = s.replace(/^DES\.BT\s+(?=[1-4])/, 'DES.BT.');
  /* Batch 8 (core 8, TekkenDocs / wavu / T7 list spellings, sweep 2026-10-29):
     - positional throws: 'Left throw' / '(Left side throw)' / 'Right Throw' / 'Back throw' /
       '(Behind 2 throw)' / 'Back Throw.2+4' are the throw chord pressed from the opponent's
       side or back -> 'FLANK_L.1+3', 'FLANK_R.2+4', 'FLANK_B.1+3' / 'FLANK_B.2+4' (the input
       buffer resolves the FLANK_ prefix from where the opponent is facing, fighter._inputCtx).
     - alternatives: '1+3_2+4' / '1_2' (T7 data: either), 'AIR.1+3 / AIR.f+1+3', '(or 2)',
       'U/F or U/B', 'd/b+1/2/3' -> the first listed input.
     - cancel notes '(hold B to cancel)' / '(b, b to cancel)' and per-hit notes
       '(second and third hits only)' are notes on the same input.
     - '(During Hisenkyaku) qcf+1+2' -> 'HISENKYAKU.qcf+1+2' (as 'during X, ...');
       'While Down (Facing Up) 1+2' -> 'FUFT.1+2'; 'ss2' / 'bt1' -> 'SS.2' / 'BT.1';
       a stray '+' after a state ('FUFT.+3+4') and a doubled hold mark ('1+2**') are dropped. */
  {
    const th = /^\(?\s*(left|right)(?:\s+side)?\s+throw\s*\)?$/i.exec(s);
    if (th) return th[1].toLowerCase() === 'left' ? 'FLANK_L.1+3' : 'FLANK_R.2+4';
    const tb = /^\(?\s*(?:back|behind)(?:\s+([12]))?\s+throw\s*\)?(?:\s*[.,]\s*(1\+3|2\+4))?$/i.exec(s);
    if (tb) return 'FLANK_B.' + (tb[2] || (tb[1] === '2' ? '2+4' : '1+3'));
  }
  s = s.replace(/\s*\((?:hold\s+)?[^()]*\bto cancel\)\s*$/i, '');
  s = s.replace(/\s*\((?:(?:first|second|third|fourth|fifth|\d+(?:st|nd|rd|th))\s*(?:,|and)?\s*)+hits?\s+only\)\s*$/i, '');
  /* Jump contexts come BEFORE the alternatives rule below: the 'or' in '(During Forward
     or Backward Jump)' is part of the context name, not an either/or input list — the
     alternatives rule would otherwise cut the row to '(During Forward'. Vertical jump is
     excluded here so the u+ rule below still claims it. */
  s = s.replace(/^\(during\s+(forward or backward jump|forward jump peak|forward jump|jump)\)\s*(?=[udfbnUDFB1-4qh])/i, 'AIR.');
  s = s.replace(/\s*\(or [^()]*\)/gi, '');
  s = s.replace(/\s*\/\s+.*$/, '').replace(/\s+or\s+.*$/i, '');
  s = s.replace(/([1-4](?:\+[1-4])*)_[1-4](?:\+[1-4])*(?![\w])/g, '$1');
  s = s.replace(/^(.*\+)([1-4])(?:\/[1-4])+$/, '$1$2');
  /* T7 jump attacks (moveset sweep 2026-10-29, Dio's 12): '(During Jump) qcf+1',
     '(During Forward or Backward Jump) 1', '(During Forward Jump Peak) d+3' are the
     attack pressed while airborne — Tekken's jump direction does not change the move, so
     they canonicalise to the AIR. prefix the input buffer resolves from ctx.airborne
     (same pattern as R. for rage, FC./WS./SS./BT. for their states). The vertical-jump
     form is left alone here so the u+ rule below still claims it (those rows pass). */
  s = s.replace(/^\(during\s+([A-Za-z][A-Za-z' ]*[A-Za-z])\)\s*(?=[udfbnUDFB1-4qh])/i, (m, name) => (/vertical/i.test(name) ? m : /^(forward or backward jump|forward jump peak|forward jump|jump)$/i.test(name) ? 'AIR.' : stateCode(name) + '.'));
  s = s.replace(/^while down\s*\(?facing up\)?\s*/i, 'FUFT.');
  // T7 list jump attacks: '(During Vertical Jump) 1' is u+1 (Tekken jumps attack on the jump input)
  s = s.replace(/^\(?during vertical jump\)?\s*(?=[1-4])/i, 'u+');
  // leading stance token then comma ('JGS, 1+4' T7 king list) -> 'JGS.1+4'.
  // Neutral follow-up (sweep 2026-10-30, Pantera t7.king_158 'JGS, N'): N (stick at
  // neutral) joins the lookahead, so the row canonicalises to 'JGS.N' — the sweep's
  // parse() already treats N as a direction step, so the row reads as motion-only
  // (no button), the sweep's own movement class, not a failure. The row's own data
  // confirms it has no attack to witness (name '*', damage 0, hit level '-'), unlike
  // Dio's 'DFLIP N' (space form, Hyakkigozan, 23 dmg / low / KND), which this rule
  // deliberately does NOT touch: that row is a real strike whose entry input is not
  // established, and it stays open. Blast radius across the fresh-main core-8
  // movesets: exactly this one row — it is the only leading-stance-comma-N input.
  s = s.replace(/^([A-Z]{2,5}),\s*(?=[udfbUDFN1-4(])/, (m, st) => (/^(?:[UDFB]|UF|UB|DF|DB|WS|FC|SS|BT)$/.test(st) ? m : st + '.'));
  s = s.replace(/^(ss|bt|fc)(?=[1-4])/i, (m) => m.toUpperCase() + '.');
  s = s.replace(/^([A-Z][A-Z0-9_]*)\.\+(?=[1-4])/, '$1.');
  s = s.replace(/\*\*$/, '*');
  /* Clockwork back step (sweep 2026-10-30, Cyborg X t7.alisa_186 '(Clockwork Spring Middle) B'):
     Tekken's B is a held-back direction, not a button (buttons are 1-4) — and this row
     carries no attack to witness (t7 damage 0, hit level '-'), unlike Dio's 'DFLIP N'
     (space form, Hyakkigozan, 23 dmg / low / KND, a real strike, deliberately untouched).
     The paren names the move the step is taken during: 'Clockwork Spring Middle' is the
     name of the CLOCKWORK.3 row in this same moveset, and the t7 Clockwork rows already
     use the CLOCKWORK. prefix ('(During Clockwork) 3' -> 'CLOCKWORK.3'), so the row
     canonicalises to 'CLOCKWORK.B' — the t7-dataset twin of the existing 'CLK.B'
     Clockwork Cancel row. The sweep's parse() treats B as a direction step, so the row
     reads as motion-only (no button), the sweep's own movement class, not a failure and
     not a pass. This MUST run before the final paren-to-words rule below, which would
     otherwise turn the move name into bare words parse() rejects. Residual, stated
     plainly: mechanism proof (canon + parse), not a witnessed full-fight pass — what
     holding back during Spring Middle actually does in play (cancel/transition) is what
     the next sweep reports, and entering Clockwork itself is not witnessed by this chunk. */
  s = s.replace(/^\(clockwork spring middle\)\s+(?=[B])/i, 'CLOCKWORK.');
  s = s.replace(/\(([^()]*)\)/g, '$1');
  s = s.replace(/\s*([,~:+])\s*/g, '$1');
  return s;
}
const _NUMPAD = { 1: 'd/b', 2: 'd', 3: 'd/f', 4: 'b', 5: 'n', 6: 'f', 7: 'u/b', 8: 'u', 9: 'u/f' };
const _T3BTN = { LP: '1', RP: '2', LK: '3', RK: '4' };
/** T3 source command ('6/9+LK+RK', '2/1/3+LP') -> playable notations, one per listed direction,
 *  in source order ('f+3+4', 'u/f+3+4'). Commands with 'any' buttons give none. */
export function t3CommandNotations(cmd) {
  const m = /^([1-9](?:\/[1-9])*)((?:\+(?:LP|RP|LK|RK))+)$/.exec(String(cmd || '').trim());
  if (!m) return [];
  const btn = m[2].slice(1).split('+').map((b) => _T3BTN[b]).sort().join('+');
  return m[1].split('/').map((d) => (d === '5' ? btn : `${_NUMPAD[d]}+${btn}`));
}
function _prepare(ms) {
  if (!ms || !ms.moves || ms._slots) return;
  const slots = Object.assign({}, ms.slots || {});
  for (const k of Object.keys(ms.moves)) if (!(k in slots)) slots[k] = k;
  /* WH legacy letter notation (P = punch, K = kick): a move keyed 'u+P' / 'd/f+K' / 'qcf+P'
     is also reachable on the numeric input (P -> 1, K -> 4) when no other move owns it. */
  for (const k of Object.keys(ms.moves)) { const a = legacyAlias(k); if (a && !(a in slots)) slots[a] = k; }
  for (const k of Object.keys(ms.moves)) { const c = canonNotation(k); if (c && c !== k && !(c in slots)) slots[c] = k; }
  /* Variants (2026-10-29): KOF/SF close and far normals ('1 (close)' / 'far 1') and T7 stance
     spin counts ('JGS* (3 spins), 1') share the plain input; press() picks them by the fight
     context (distance, spins). Other name-keyed moves (rush_l2 '1,1 (Rush)', hop_1 'hop u/f+1')
     are slotted on their canonical input when no other move owns it. */
  const variants = {};
  for (const [k, mv] of Object.entries(ms.moves)) {
    const raw = mv && mv.input;
    { const sys = systemTagOf(raw); if (sys) mv.system = sys; }
    if (typeof raw !== 'string' || raw === k) continue;
    const c = canonNotation(raw);
    if (!c) continue;
    let kind = null, n = 0;
    if (/^far\s+/i.test(raw) || /\(far\)/i.test(raw)) kind = 'far';
    else if (/^(?:close|cl\.?)\s+/i.test(raw) || /\(close\)/i.test(raw)) kind = 'close';
    else { const sm = /^[A-Z][A-Z0-9_]*\*\s*\((\d+)\s*spins?\)/.exec(raw); if (sm) { kind = 'spins'; n = +sm[1]; } }
    if (kind) (variants[c] = variants[c] || []).push({ key: k, kind, n });
    else if (!(c in slots) && (systemTagOf(raw) || (!(ms.slots && k in ms.slots && ms.slots[k] !== k) && /^(?:[a-z][a-z0-9]*_|\d+$)/i.test(k))) && !/[,~:+.]/.test(k)) slots[c] = k; // KOF system rows (maxmode, taunt) too; numeric/name keys whose only slot is themselves (string heads like qcb+1 -> '15')
  }
  ms._variants = variants;
  ms._variantBase = {};
  for (const [n, list] of Object.entries(variants)) for (const x of list) ms._variantBase[x.key] = n;
  /* T3 clip-variant rows (sweep 2026-10-29): raw direction keys like 'b_c36_r46' carry no button;
     the source command (t3_command '4/7+LP') does. Slot the first free spelling of it
     ('b+1', then 'u/b+1'), never overwriting an existing slot. */
  for (const k of Object.keys(ms.moves)) {
    if (!/^[udfbn](?:\/[fb])?(?:_[rc]\d+)+$/i.test(k)) continue;
    for (const c of t3CommandNotations(ms.moves[k] && ms.moves[k].t3_command)) if (!(c in slots)) { slots[c] = k; break; }
  }
  /* State entries: a 'during <Name>, X' row is pressed from stance <NAME> (canonNotation); the
     move named <Name> that is not itself a state row enters it. Existing stance_after kept. */
  { const byName = {};
    for (const [k, mv] of Object.entries(ms.moves)) if (mv && mv.name && !/^(?:during|while)\s/i.test(mv.input || '')) (byName[stateCode(mv.name)] ||= k);
    for (const [k, mv] of Object.entries(ms.moves)) {
      if (!mv || typeof mv.input !== 'string' || !/^(?:during\s|while on back\b)/i.test(mv.input)) continue;
      const c = canonNotation(mv.input), m = /^([A-Z][A-Z0-9_]+)\./.exec(c || '');
      if (!m) continue;
      if (!(c in slots)) slots[c] = k; // the state row on its prefixed input, never over a slot
      ms.stance_after = ms.stance_after || {};
      if (byName[m[1]]) {
        if (!(byName[m[1]] in ms.stance_after)) ms.stance_after[byName[m[1]]] = m[1];
      } else {
        // Suffix fallback (sweep 2026-10-30, Deathfang saika): the during-row's prefix is a
        // short state name ('YA_OTOME') while the entering move's name carries its full KOF
        // title ('DEATHFANG — Kin 1211 Shiki: Ya Otome' -> stateCode ends '_YA_OTOME'), so no
        // exact byName entry exists and pressing Ya Otome itself never set the YA_OTOME stance
        // in real play (the sweep sets the stance directly, which hid it). Every move whose
        // stateCode ends with '_' + prefix enters that state; existing stance_after entries
        // are kept, and a prefix with no suffix match (e.g. WALLSTUN, a sweep setup, not a
        // stance) gains nothing.
        for (const [sc, ek] of Object.entries(byName))
          if (sc.endsWith('_' + m[1]) && !(ek in ms.stance_after)) ms.stance_after[ek] = m[1];
      }
    } }
  ms._slots = slots;
  const motions = [];
  for (const n of Object.keys(slots)) {
    const m = parseMotion(n);
    if (m) motions.push({ n, ...m });
  }
  motions.sort((a, b) => b.dirs.length - a.dirs.length); // longest motion wins (qcf+1 over f+1)
  ms._motions = motions;
  // v2: every proper prefix of a string ('d/f+2,1' of 'd/f+2,1,3,2') — lets a string whose
  // intermediate steps are not standalone moves (chain throws, long strings) still be typed.
  const pre = new Set();
  for (const n of Object.keys(slots)) {
    const cuts = []; for (let j = 0; j < n.length; j++) if (',~:'.includes(n[j])) cuts.push(j);
    for (const j of cuts) pre.add(n.slice(0, j));
  }
  ms._strPrefixes = pre;
  // A string whose opening step is a motion with no standalone move ('f,n,1' of 'f,n,1,2,1,2,3'):
  // the motion opens the string cursor (sweep 2026-10-29: it fired the plain '1' string instead).
  for (const n of pre) if (!(n in slots)) { const m = parseMotion(n); if (m) motions.push({ n, ...m, opener: true }); }
  motions.sort((a, b) => b.dirs.length - a.dirs.length);
}

/* Motion inputs this fighter can perform: the moveset's own slots plus every motion notation
   the moveset editor's loadout equipped (moveset sweep 2026-10-29: loadout slots like
   'qcf+3+4' / 'hcb+1' / 'd/b,d/b+1+2' resolved but were never in _motions, so the buffer
   could not perform them and the plain button fired instead). Cached per loadout object. */
const _loMotionCache = new WeakMap();
export function motionsFor(fighterId, ms) {
  const lo = getLoadout(fighterId);
  const keys = Object.keys(lo).filter(n => n !== '__base' && !(ms._slots && n in ms._slots));
  if (!keys.length) return ms._motions;
  let per = _loMotionCache.get(ms); if (!per) _loMotionCache.set(ms, per = new Map());
  const sig = fighterId + '|' + keys.join('\u0001');
  let out = per.get(sig);
  if (!out) {
    out = ms._motions.slice();
    for (const n of keys) { const m = parseMotion(n); if (m) out.push({ n, ...m }); }
    out.sort((a, b) => b.dirs.length - a.dirs.length);
    per.clear(); per.set(sig, out);
  }
  return out;
}

/* String prefixes of loadout-equipped strings (moveset editor: rush_l3 on '1,1,1'), so their
   intermediate steps open the string cursor like a moveset's own strings do. */
const _loPrefCache = new Map();
/** Is `c` the opening part of one of this fighter's strings ('1+2,f' of '1+2,f,f')? */
export function hasStrPrefix(fighterId, c) { const ms = playedMoveset(fighterId); return !!(ms && strPrefixesHas(fighterId, ms, c)); }
export function strPrefixesHas(fighterId, ms, c) {
  if (ms._strPrefixes && ms._strPrefixes.has(c)) return true;
  const lo = getLoadout(fighterId);
  const keys = Object.keys(lo).filter(n => n !== '__base' && /[,~:]/.test(n));
  if (!keys.length) return false;
  const sig = fighterId + '|' + keys.join('\u0001');
  let set = _loPrefCache.get(fighterId);
  if (!set || set.sig !== sig) {
    set = new Set(); set.sig = sig;
    for (const n of keys) for (let j = 0; j < n.length; j++) if (',~:'.includes(n[j])) set.add(n.slice(0, j));
    _loPrefCache.set(fighterId, set);
  }
  return set.has(c);
}

/* Player loadouts from the moveset editor: localStorage wh_moveset_loadout_v1
   = { fighterId: { notation: moveKey } }. Read live so edits apply next press. */
const LOADOUT_KEY = 'wh_moveset_loadout_v1';
let _loadouts = null; // in-memory copy; every input lookup reads it
function _allLoadouts() {
  if (_loadouts) return _loadouts;
  try { _loadouts = JSON.parse(localStorage.getItem(LOADOUT_KEY) || '{}') || {}; } catch (e) { _loadouts = {}; }
  return _loadouts;
}
if (typeof window !== 'undefined' && window.addEventListener) {
  window.addEventListener('storage', (e) => { if (e.key === LOADOUT_KEY) _loadouts = null; }); // editor in another tab
}
/** The plain notation a close/far or spin variant key fires from ('far_1' → '1'), else null. */
export function variantBase(fighterId, key) {
  const ms = playedMoveset(fighterId);
  return (ms && ms._variantBase && ms._variantBase[key]) || null;
}

export function getLoadout(fighterId) {
  return _allLoadouts()[fighterId] || {};
}
export function setLoadoutSlot(fighterId, notation, moveKey) {
  const all = _allLoadouts();
  all[fighterId] = all[fighterId] || {};
  if (moveKey) all[fighterId][notation] = moveKey; else delete all[fighterId][notation];
  try { localStorage.setItem(LOADOUT_KEY, JSON.stringify(all)); return true; } catch (e) { return false; }
}

/* Loadout values (moveset editor, creation suite MOVESET tab):
     'key'            a move of this fighter's own moveset
     'otherId::key'   a move borrowed from another fighter (WWE-style move library)
   and the reserved entry '__base': 'otherId' = start from another fighter's whole moveset
   (custom fighters with no moveset file of their own). */
export function loadoutDeps(fighterId) {
  const lo = getLoadout(fighterId), out = [];
  if (lo.__base) out.push(lo.__base);
  for (const [n, v] of Object.entries(lo)) if (n !== '__base' && typeof v === 'string' && v.includes('::')) out.push(v.split('::')[0]);
  return out;
}

/** The moveset a fighter plays: its own file, else its loadout's __base. */
export function playedMoveset(fighterId) {
  return getFighterMoveset(fighterId) || (getLoadout(fighterId).__base ? getFighterMoveset(getLoadout(fighterId).__base) : null);
}

/** notation -> { move, key, ms, from } this fighter fires (loadout > default slots > exact key). */
export function resolveMove(fighterId, notation, opts) {
  if (!notation) return null;
  const custom = opts && opts.noLoadout ? null : getLoadout(fighterId)[notation];
  if (custom) {
    const [from, key] = custom.includes('::') ? custom.split('::') : [fighterId, custom];
    const src = from === fighterId ? playedMoveset(fighterId) : getFighterMoveset(from);
    if (src && src.moves[key]) return { move: src.moves[key], key, ms: src, from };
  }
  const ms = playedMoveset(fighterId);
  if (!ms) return null;
  _prepare(ms);
  const k = ms._slots[notation];
  return k && ms.moves[k] ? { move: ms.moves[k], key: k, ms, from: fighterId } : null;
}

/** notation -> move key this fighter fires (null if none). */
export function resolveMoveKey(fighterId, notation) {
  const r = resolveMove(fighterId, notation);
  return r ? r.key : null;
}

/** Notation lookup: '1', '2', '1+3', 'f+1', '1,2', 'qcf+2', 'WS.4', 'SNK.1' ... */
export function getMove(fighterId, notation) {
  const r = resolveMove(fighterId, notation);
  return r ? r.move : null;
}

/** Split a special's input into {dirs:[...], button:'2'}.
 *  'qcf+2' -> {dirs:['d','d/f','f'], button:'2'}.
 *  'b,n,f+1+2' -> {dirs:['b','f'], button:'1+2'} (chain-throw chords). */
export function parseSpecialInput(input) {
  // Trailing '+1/+2/...' runs are the button chord; the rest is the motion.
  const parts = input.split('+');
  const btnParts = [];
  while (parts.length && /^[1234]$/.test(parts[parts.length - 1])) btnParts.unshift(parts.pop());
  const motion = parts.join('+');
  const button = btnParts.join('+') || null;
  let dirs;
  if (MOTION_DIRS[motion]) {
    dirs = MOTION_DIRS[motion];
  } else {
    dirs = motion.split(',').map(s => s.trim()).filter(s => s && s !== 'n' && s !== 'any');
    dirs = dirs.flatMap(d => (d === 'f,F' ? ['f', 'f'] : d === 'b,B' ? ['b', 'b'] : [d]));
  }
  return { dirs, button };
}

/* ------------------------------------------------------------
   TekkenBuffer — per-fighter input history for strings, motion
   specials and directional attacks. Lives on the Fighter.
   ------------------------------------------------------------ */
/** Resolver flag: V2 (deterministic) is ON by default; 'legacy' keeps the old one reachable. */
export function inputResolverV2() {
  let v = (typeof globalThis !== 'undefined' && globalThis.WH_INPUT_RESOLVER) || null;
  if (!v) { try { v = localStorage.getItem('wh_input_resolver'); } catch (e) { /* no storage */ } }
  return v !== 'legacy';
}

export class TekkenBuffer {
  constructor(fighterId) {
    this.fighterId = fighterId;
    this.dirEvents = [];   // [{dir, t}] facing-relative: f,b,u,d,d/f,d/b,u/f,u/b
    this.lastDir = 'n';
    this.lastMove = null;  // notation of last executed attack
    this.lastMoveT = 0;
    // T3 input history: one facing-relative direction per fixed step (game.js calls
    // noteDirection every update with its dt), newest at this.hi. hdur[i] = that entry's length
    // in 60 Hz frames (0.5 at the 1/120 tick); the walks sum it, so the decoded windows
    // (fight_sim HISTORY = 60 frames) stay real-time whatever the tick rate.
    this.hist = new Array(HIST_LEN).fill('n');
    this.hdur = new Array(HIST_LEN).fill(1);
    this.hi = 0;
  }

  /** Feed the facing-relative direction for one fixed step of `dt` seconds (game.js passes its
      tick). Without dt the entry is one 60 Hz frame (tests / tools feed frame by frame). */
  noteDirection(dir, dt) {
    this.hi = (this.hi + 1) % HIST_LEN;
    this.hist[this.hi] = dir || 'n';
    this.hdur[this.hi] = dt > 0 ? Math.round(dt * INPUT_FPS * 1e6) / 1e6 : 1;
    // T3 enters the dash row on the frame double_tap matches; a button during that row is a
    // dash move (f,F+2). The latch is WALL-CLOCK (decoded row = 30f @60fps = 500ms):
    // a step-counted latch lasts seconds on slow devices and misfires dash moves on
    // plain f+1 presses (input-fidelity bug, 2026-10-22).
    const _now = performance.now();
    if (this._dash && _now >= this._dash.until) this._dash = null;
    if (this._doubleTap('f')) {
      if (this._dash && this._dash.dir === 'f') this._runNow = true; // third tap: f,f,f
      this._runStart = _now;
      this._dash = { dir: 'f', until: _now + DASH_FRAMES['f,f'] / 60 * 1000 };
    }
    else if (this._doubleTap('b')) this._dash = { dir: 'b', until: _now + DASH_FRAMES['b,b'] * 1000 / 60 };
    if (dir === 'f' && this._runStart && (this._runNow || _now - this._runStart >= RUN_HOLD_FRAMES / 60 * 1000)) { this._runNow = true; this._runUntil = _now + RUN_GRACE_FRAMES / 60 * 1000; }
    else if (dir !== 'f') { this._runStart = 0; this._runNow = false; }
    if (dir === this.lastDir) return;
    this.lastDir = dir;
    if (dir === 'n') return;
    const now = performance.now();
    this.dirEvents.push({ dir, t: now });
    if (this.dirEvents.length > 24) this.dirEvents.shift();
  }

  /** Tekken running state (WR): see RUN_HOLD_FRAMES. */
  running() { return !!this._runUntil && performance.now() < this._runUntil; }
  /** This fighter's move key for a notation, if it owns one. */
  resolveKey(k) { return resolveMoveKey(this.fighterId, k); }

  _prev(i) { return i > 0 ? i - 1 : HIST_LEN - 1; }

  /** T3 double tap (FUN_8002CB08 / FUN_8002CBF0, fight_sim.double_tap): the newest frame is
      `dir`, the frame before it neutral, then within DOUBLE_TAP_BUDGET frames an earlier `dir`.
      T3 spends the budget on every neutral frame after the first and every frame of the first
      tap after its first: (neutral - 1) + (first tap - 1) < budget, measured here in time. */
  _doubleTap(dir) {
    const h = this.hist, w = this.hdur; let k = this.hi;
    if (h[k] !== dir) return false;
    k = this._prev(k);
    if (h[k] !== 'n') return false;
    let budget = DOUBLE_TAP_BUDGET + 2 - w[k]; // +2: the first neutral and first tap frames are free
    for (let n = 2; ; n++) {
      if (budget <= T_EPS || n >= HIST_LEN) return false;
      k = this._prev(k);
      if (h[k] !== 'n') { if (h[k] !== dir) return false; break; }
      budget -= w[k];
    }
    for (let n = 0; ; n++) { // k = newest entry of the first tap
      budget -= w[k];
      if (budget <= T_EPS) return false;
      const m = this._prev(k);
      if (h[m] !== dir || n >= HIST_LEN) break;
      k = m;
    }
    return true;
  }

  /** T3 InputSequenceMatch (0x8002CCD8, fight_sim.sequence_match) over the direction history:
      the newest frame must be the last step, earlier steps are found walking back within
      `window` frames. (Button entries in the T3 history abort a match; WH records buttons as
      events, so that clause has no counterpart here.) */
  _seqMatch(steps, window) {
    const h = this.hist; let k = steps.length - 1;
    if (h[this.hi] !== steps[k]) return false;
    k--; if (k < 0) return true;
    let want = steps[k], pos = this.hi, t = 0;
    for (let n = 1; n < HIST_LEN; n++) {
      t += this.hdur[pos]; pos = this._prev(pos); // t = frames from entry `pos` to the newest
      if (t > window + T_EPS) break;
      if (h[pos] === want) { k--; if (k < 0) return true; want = steps[k]; }
    }
    return false;
  }

  /** Does the history hold this motion (decoded T3 timing)? */
  _motionHeld(dirs) {
    // Any all-identical f/b run ('f,F', 'f,f,F', 'b,b,B' ...) is a DASH motion:
    // it fires only inside the dash row (double-tap latch), never from merely
    // holding the direction — otherwise 'f,f,F+2' would match a plain f+2 hold
    // via _seqMatch on an all-f history (input-fidelity bug, 2026-10-22).
    if (dirs.length >= 2 && dirs.every(d => d === dirs[0]) && (dirs[0] === 'f' || dirs[0] === 'b')) {
      return !!(this._dash && this._dash.dir === dirs[0]) || this._doubleTap(dirs[0]);
    }
    return this._seqMatch(dirs, motionWindow(dirs));
  }

  /** Recent direction events within ms. */
  _recentDirs(ms = 600) {
    const now = performance.now();
    while (this.dirEvents.length && now - this.dirEvents[0].t > ms) this.dirEvents.shift();
    return this.dirEvents.map(e => e.dir);
  }

  /** Does the recent direction history contain `seq` in order? */
  _matchMotion(seq, ms = 650) {
    const hist = this._recentDirs(ms);
    let i = 0;
    for (const d of hist) {
      if (d === seq[i]) { i++; if (i >= seq.length) return true; }
    }
    return false;
  }

  /**
   * Resolve a button ('1'..'4') or chord ('1+2', '1+3' ...) to the Tekken notation this
   * fighter fires, from its moveset's notation table (slots / loadout) — no per-move code.
   * `ctx` (Fighter._inputCtx): { stance, crouching, rising, sidestep, backturned, rage, airborne }.
   * Order (Tekken): string continuation > state/stance prefix (stance code, R. rage art,
   * BT., SS., FC., WS., AIR. while airborne) > motion (qcf, f,F, b,f, d,d/f,f ...) > direction+button > button.
   * Returns the notation, or null if this fighter has nothing on that input.
   */
  press(input, ctx = {}) {
    const ms = playedMoveset(this.fighterId);
    if (!ms || !ms.moves) return input; // no data — raw passthrough
    _prepare(ms);
    const r = inputResolverV2() ? this._pressV2(input, ctx, ms) : this._pressLegacy(input, ctx, ms);
    return this._variant(r, ctx, ms);
  }

  /* Close/far normals and stance spin counts (see _prepare variants). The returned move KEY is
     fired; lastMove keeps the plain notation so strings continue from it ('1' then ',2'). A
     moveset-editor loadout entry on the notation always wins (the player chose that move). */
  _variant(r, ctx, ms) {
    const v = r && ms._variants && ms._variants[r];
    if (!v || getLoadout(this.fighterId)[r]) return r;
    if (ctx.stanceSpins >= 2) {
      const sp = v.filter(x => x.kind === 'spins' && x.n <= ctx.stanceSpins).sort((a, b) => b.n - a.n)[0];
      if (sp) return sp.key;
    }
    if (ctx.dist != null) {
      const want = ctx.dist <= CLOSE_RANGE ? 'close' : 'far';
      const hit = v.find(x => x.kind === want);
      if (hit) return hit.key;
    }
    return r;
  }

  /* INPUT RESOLVER V2 (owner t116u, 2026-10-23 — "presses give random moves, neutral 3 fires a
     crouching kick"). Deterministic Tekken priority from the stick ACTUALLY held at press time:
       1) string continuation (only while the previous hit plays)
       2) for each state prefix, most specific first (stance, R., BT., SS., FC. only while
          crouching, WS. only in the rising window): motion > held direction + button
       3) only then the plain button, again most specific prefix first.
     So a held direction always beats a stance-neutral move, a neutral stick never reaches a
     directional / FC move (FC needs a real crouch), and no input ever picks a move at random.
     Old resolver: _pressLegacy, reachable with localStorage wh_input_resolver='legacy' or
     window.WH_INPUT_RESOLVER='legacy'. Test: test/input-determinism.test.mjs (CI). */
  _pressV2(input, ctx, ms) {
    const has = (n) => (resolveMoveKey(this.fighterId, n) ? n : null);
    // Soul Urge lane (T8 Heat), as in _pressLegacy: while the urge gauge is live, 2+3 is the
    // Urge Burst (fresh gauge) or the Urge Smash (urging) before any normal move on the chord.
    // Neutral 2+3 only (T8 Heat Burst is neutral) — b+2+3 / d/f+2+3 stay the fighter's own moves.
    if (input === '2+3' && (!this.lastDir || this.lastDir === 'n') && !(ctx.running && has('WR.2+3'))) { // a running 2+3 (WR.2+3) outranks the urge
      // a live soul-state finisher on 2+3 (SPIRIT / SOUL9 / REIHOU / SEAL / KESSHOU) outranks the urge
      for (const sp of ctx.soulStates || []) { const k = has(sp + '.2+3'); if (k) return this._recordMove(k); }
      if (ctx.urgeOn) { const sm = has('US.2+3'); if (sm) return this._recordMove(sm); }
      else if (ctx.urgeAvailable) { const bu = has('UB.2+3'); if (bu) return this._recordMove(bu); }
    }
    const dir = this.lastDir && this.lastDir !== 'n' ? this.lastDir : '';
    const withDir = dir ? `${dir}+${input}` : input;
    const holdDir = dir ? `${dir.toUpperCase()}+${input}` : null;
    const now = performance.now();
    const contOk = ctx.inMove !== undefined ? ctx.inMove : (now - this.lastMoveT < STRING_PENDING);
    // String cursor: the notation typed so far — the last move, or a pending partial string
    // (an intermediate step that is not a standalone move) for STRING_PENDING ms.
    const pendingOk = this._strPath && now - this._strPathT < STRING_PENDING;
    const bases = [];
    // BATCH: strip ~shadow suffixes here too (see continuation()) — a pending
    // path or last move of '1~t8.king' must also try '1' as its chain base.
    const strip = (b) => { const t = b ? b.indexOf('~') : -1; return t > 0 ? b.slice(0, t) : null; };
    if (pendingOk) { bases.push(this._strPath); const s = strip(this._strPath); if (s) bases.push(s); }
    if (this.lastMove && contOk) { bases.push(this.lastMove); const s = strip(this.lastMove); if (s) bases.push(s); }
    // A direction tapped just before the press still counts as the string's direction step:
    // the sweep releases to neutral before the button for motion-only steps, and pad players
    // do the same. Only the most recent non-neutral direction within a few neutral frames
    // counts, so a stale walk from seconds ago can never hijack a press.
    let stepDir = dir;
    if (!stepDir) {
      let pos = this.hi, neutral = 0;
      for (let n = 0; n < HIST_LEN; n++) {
        const d = this.hist[pos];
        if (d !== 'n') { stepDir = d; break; }
        neutral += this.hdur[pos];
        if (neutral > 10) break;
        pos = this._prev(pos);
      }
    }
    for (const base of bases) {
      for (const sep of sepOrder(ctx)) {
        // Bare direction step in a string ('R.1,1,f,3,2': the row's own input_slots carry
        // '...1,1,f' as its own comma step, not f+3). The attached-direction candidates never
        // match such a step, so the continuation broke at the direction and the button fell
        // through to a standalone move (r16: the Rage row fired ["3"] only). Bare candidates
        // are tried last, so every string that resolves the old way is untouched.
        const cands = dir ? [`${base}${sep}${withDir}`, `${base}${sep}${holdDir}`] : [`${base}${sep}${input}`];
        if (stepDir) cands.push(`${base}${sep}${stepDir}${sep}${input}`, `${base}${sep}${stepDir.toUpperCase()}${sep}${input}`);
        for (const c of cands) if (has(c)) { this._strPath = null; return this._recordMove(c); }
        for (const c of cands) if (strPrefixesHas(this.fighterId, ms, c)) { this._strPath = c; this._strPathT = now; return null; }
      }
    }
    this._strPath = null;
    // Batch 8: a throw chord pressed at the opponent's side or back is that fighter's side/back
    // throw (TekkenDocs 'Left throw' / 'Back throw'); canonNotation keys them FLANK_L/R/B.
    // A copy the player equipped in the moveset editor on the chord or a string opened by it
    // (a T3 situation row on 2+4,1) keeps the chord: its own condition decides.
    const eqChord = Object.keys(getLoadout(this.fighterId) || {}).some((n) => n === input || n.startsWith(input + ','));
    if (ctx.foeFlank && !dir && (input === '1+3' || input === '2+4') && !eqChord) {
      const fl = 'FLANK_' + ctx.foeFlank + '.';
      const k = has(fl + input) || has(fl + (input === '1+3' ? '2+4' : '1+3'));
      if (k) return this._recordMove(k);
    }
    // Opening step of a string that has no standalone move: open the string cursor, fire nothing.
    const opener = (c) => (strPrefixesHas(this.fighterId, ms, c) ? (this._strPath = c, this._strPathT = now, true) : false);
    const prefixes = [];
    if (ctx.running) prefixes.push('WR.'); // Tekken while running
    for (const sp of ctx.soulStates || []) prefixes.push(sp + '.'); // pt217u soul systems
    if (ctx.stance) prefixes.push(ctx.stance + '.');
    if (ctx.rage) prefixes.push('R.');
    // Rage lane (T7), as in _pressLegacy: the rage drive lives on 3+4 while raging (synthesized RD.).
    if (ctx.rage) prefixes.push('RD.');
    if (ctx.backturned) prefixes.push('BT.');
    if (ctx.sidestep) prefixes.push('SS.');
    if (ctx.crouching) prefixes.push('FC.');
    if (ctx.rising) prefixes.push('WS.');
    if (ctx.airborne) prefixes.push('AIR.'); // Tekken jump attacks: an AIR. move outranks its ground namesake while airborne
    prefixes.push('');
    for (const p of prefixes) {
      // Final step HELD (>= MOTION_HOLD frames) prefers the capital spelling (f,f,F+3), a quick
      // final tap the lowercase one (f,f,f+3); each still falls back to the other.
      const capFirst = this._heldFrames() >= MOTION_HOLD;
      const cap = (mo) => /[A-Z]/.test(mo.n.split(',').pop().split('+')[0]);
      const motions = motionsFor(this.fighterId, ms).slice().sort((a, b) => (b.dirs.length - a.dirs.length) || ((cap(b) === capFirst) - (cap(a) === capFirst)));
      for (const mo of motions) {
        if (mo.prefix !== p || mo.btn !== input) continue;
        // neutral-ending motions ('f,n,2') need the stick released; the rest need the last
        // step still held at the press (f,F+2 = f held).
        // pt217u: 'b,1' / 'd,1' (comma, then a bare button) = tap the direction, RELEASE, press —
        // so a released stick reaches it and a held one still gets b+1 / d+1 first.
        const tapRel = !mo.neutral && !dir && /,[1-4](?:\+[1-4])*\*?$/.test(mo.n) && !/^(f|b)(,\1)+$/i.test(mo.dirs.join(','));
        if (!tapRel && (mo.neutral ? dir : dir !== mo.dirs[mo.dirs.length - 1])) continue;
        // Batch 7 (sweep 2026-10-29): rising from a crouch IS a released d tap, so the tap-release
        // motion 'd,4' matched every while-standing press: WS.4 came out as d,4. Tekken gives the
        // WS move there (TekkenDocs/wavu: while standing = rising from crouch).
        if ((tapRel || mo.neutral) && ctx.rising && /^d/.test(mo.dirs[mo.dirs.length - 1]) && (has('WS.' + input) || has('WS.' + input + '*'))) continue;
        if (this._motionHeldV2(mo) && (!mo.charge || this._chargeHeld(mo))) {
          if (has(mo.n)) return this._recordMove(mo.n);
          if (mo.opener && opener(mo.n)) return null;
        }
      }
      if (dir) {
        // Held spelling ('D/F+2') when the direction has been held >= HOLD_FRAMES, tap otherwise.
        const held = this._heldFrames() >= HOLD_FRAMES;
        const order = held ? [p + holdDir, p + withDir] : [p + withDir, p + holdDir];
        for (const c of order) if (has(c)) return this._recordMove(c);
        for (const c of order) if (opener(c)) return null;
        // Full crouch holds d / d/b: in Tekken a button there is the FC move (FC.2 = crouch
        // jab), not the standing d+2 (moveset sweep 2026-10-28: FC 2/3/4/1+2 fired d+2...).
        if (p === 'FC.' && (dir === 'd' || dir === 'd/b')) {
          if (has('FC.' + input)) return this._recordMove('FC.' + input);
          if (opener('FC.' + input)) return null;
        }
      }
    }
    for (const p of prefixes) {
      if (has(p + input)) return this._recordMove(p + input);
      if (has(p + input + '*')) return this._recordMove(p + input + '*');
      if (p && opener(p + input)) return null; // stance chain opener ('SLEEPER.1' of 'SLEEPER.1,1,1+2')
    }
    return null;
  }

  /** Frames the current direction has been held (newest history run). */
  _heldFrames() { // in 60 Hz frames of time (entry lengths summed), capped at HIST_FRAMES
    const h = this.hist, d = h[this.hi]; let f = 0, i = this.hi;
    for (let n = 0; n < HIST_LEN && h[i] === d && f < HIST_FRAMES - T_EPS; n++) { f += this.hdur[i]; i = this._prev(i); }
    return Math.round(f * 1e6) / 1e6;
  }

  /** V2 motion match: like _seqMatch, but two identical consecutive steps ('d/f,d/f', 'f,f,F')
      need the stick to leave that direction in between (a real second tap) — the legacy match
      let one long hold satisfy every repeated step, so a held d/f+1 came out as d/f,d/f+1. */
  /** Charge motion: within the motion's window (+ CHARGE_RELEASE) before the newest entry, the
      stick sat in the charge direction (its diagonals count: b = b, d/b, u/b) for CHARGE_FRAMES
      in a row. APPROXIMATE: SF/KOF charge is ~40-45f depending on the game; 40f here. */
  _chargeHeld(mo) {
    const set = { b: ['b', 'd/b', 'u/b'], f: ['f', 'd/f', 'u/f'], d: ['d', 'd/b', 'd/f'], u: ['u', 'u/b', 'u/f'], 'd/b': ['d/b'] }[mo.charge] || [mo.charge];
    const h = this.hist, limit = motionWindow(mo.dirs) + CHARGE_RELEASE;
    let pos = this.hi, t = 0;
    while (!set.includes(h[pos])) { t += this.hdur[pos]; pos = this._prev(pos); if (t > limit + T_EPS || pos === this.hi) return false; }
    let held = 0;
    for (let n = 0; n < HIST_LEN && set.includes(h[pos]); n++) { held += this.hdur[pos]; if (held >= CHARGE_FRAMES - T_EPS) return true; pos = this._prev(pos); }
    return false;
  }

  _motionHeldV2(mo) {
    const steps = mo.dirs; // inner n's are real steps (d/b,n,f != d/b,f); leading/trailing were stripped
    const h = this.hist; let pos = this.hi;
    let k = steps.length - 1;
    // Window in frames of TIME, counted from the newest entry like T3's sequence match. For a
    // neutral-ending motion ('f,f,n,1+2') the trailing neutral counts too: an uncounted skip let
    // an f,f from seconds ago turn a plain 1+2 into the motion move.
    const window = motionWindow(mo.dirs);
    let t = 0;
    if (!mo.neutral) { if (h[pos] !== steps[k]) return false; }
    else {
      while (h[pos] === 'n') { t += this.hdur[pos]; pos = this._prev(pos); if (pos === this.hi || t > window + T_EPS) return false; }
      if (h[pos] !== steps[k]) return false;
    }
    let cur = steps[k], left = false;
    k--;
    for (let n = 1; k >= 0 && n < HIST_LEN; n++) {
      t += this.hdur[pos]; pos = this._prev(pos);
      if (t > window + T_EPS) break;
      const d = h[pos];
      if (d !== cur) left = true;
      if (d === steps[k] && (steps[k] !== cur || left) && (d !== cur || left)) {
        if (d === cur && !left) continue;
        cur = d; left = false; k--;
      }
    }
    return k < 0;
  }

  _pressLegacy(input, ctx, ms) {
    const has = (n) => (resolveMoveKey(this.fighterId, n) ? n : null);
    // Soul Urge lane (T8 Heat): while the urge gauge is live, 2+3 is
    // reserved — the Urge Burst (fresh gauge) or the Urge Smash (urging)
    // wins over any normal move on the chord, exactly like T8 Heat.
    // Neutral 2+3 only (T8 Heat Burst is neutral) — b+2+3 / d/f+2+3 stay the fighter's own moves.
    if (input === '2+3' && (!this.lastDir || this.lastDir === 'n') && !(ctx.running && has('WR.2+3'))) { // a running 2+3 (WR.2+3) outranks the urge
      // a live soul-state finisher on 2+3 (SPIRIT / SOUL9 / REIHOU / SEAL / KESSHOU) outranks the urge
      for (const sp of ctx.soulStates || []) { const k = has(sp + '.2+3'); if (k) return this._recordMove(k); }
      if (ctx.urgeOn) { const sm = has('US.2+3'); if (sm) return this._recordMove(sm); }
      else if (ctx.urgeAvailable) { const bu = has('UB.2+3'); if (bu) return this._recordMove(bu); }
    }
    const dir = this.lastDir && this.lastDir !== 'n' ? this.lastDir : '';
    const withDir = dir ? `${dir}+${input}` : input;
    const holdDir = dir ? `${dir.toUpperCase()}+${input}` : null;

    // 1) string continuation. In a fight (ctx.inMove defined) T3 rules: only while the previous
    //    hit is still playing (Fighter.tryAttack buffers it into that move). Legacy callers
    //    without ctx (tests) keep the old 800 ms window.
    const contOk = ctx.inMove !== undefined ? ctx.inMove : (performance.now() - this.lastMoveT < STRING_PENDING);
    if (this.lastMove && contOk) {
      // Tekken '~' (wavu wiki / TekkenDocs: "immediately after"): a press inside the first
      // TILDE_WINDOW of the hit takes the tilde branch before the ',' string ('f+2,1~2' vs 'f+2,1,2').
      const seps = sepOrder(ctx);
      /* Mid-string state (Tekken notation '1,NSS.1', 'f+2,R.1+2'; TekkenDocs / wavu wiki): the next
         hit is pressed from the stance the string put the fighter in, or while raging. Before
         (sweep 2026-10-29), the plain ',1' continuation always won and the stance hit never came out. */
      const mid = [ctx.stance, ctx.rage ? 'R' : null].filter(Boolean);
      for (const sep of seps) {
        for (const c of [...mid.map((m) => `${this.lastMove}${sep}${m}.${withDir}`), ...mid.map((m) => `${this.lastMove}${sep}${m}.${input}`), `${this.lastMove}${sep}${withDir}`, `${this.lastMove}${sep}${input}`]) {
          if (has(c)) return this._recordMove(c);
        }
      }
    }
    const prefixes = [];
    if (ctx.running) prefixes.push('WR.'); // Tekken while running
    for (const sp of ctx.soulStates || []) prefixes.push(sp + '.'); // pt217u soul systems
    if (ctx.stance) prefixes.push(ctx.stance + '.');
    if (ctx.rage) prefixes.push('R.');
    // Rage lane (T7): rage drive lives on 3+4 while raging (synthesized RD.).
    if (ctx.rage) prefixes.push('RD.');
    if (ctx.backturned) prefixes.push('BT.');
    if (ctx.sidestep) prefixes.push('SS.');
    if (ctx.crouching) prefixes.push('FC.');
    if (ctx.rising) prefixes.push('WS.');
    if (ctx.airborne) prefixes.push('AIR.'); // Tekken jump attacks: an AIR. move outranks its ground namesake while airborne
    prefixes.push('');
    for (const p of prefixes) {
      // 2) motion inputs on this button, longest first
      for (const mo of motionsFor(this.fighterId, ms)) {
        if (mo.prefix !== p || mo.btn !== input) continue;
        if (mo.neutral && dir) continue; // 'f,n,2' wants the stick back in neutral
        if (this._motionHeld(mo.dirs) && (!mo.charge || this._chargeHeld(mo)) && has(mo.n)) return this._recordMove(mo.n);
      }
      // 3) direction + button (tap, then hold spelling 'D/B+2'), 4) button
      if (dir && has(p + withDir)) return this._recordMove(p + withDir);
      if (holdDir && has(p + holdDir)) return this._recordMove(p + holdDir);
      if (dir && has(p + withDir + '*')) return this._recordMove(p + withDir + '*');
      if (has(p + input)) return this._recordMove(p + input);
      if (has(p + input + '*')) return this._recordMove(p + input + '*');
    }
    return null;
  }

  /** Legacy API (tests + older callers): single buttons fall back to the raw button. */
  pressButton(btn, ctx = {}) {
    const ms = playedMoveset(this.fighterId);
    if (!ms || !ms.moves) return btn;
    return this.press(btn, ctx);
  }

  /**
   * Resolve a button CHORD ('1+2', '1+3', '1+4', '2+3', '2+4', '3+4') to the
   * Tekken notation this fighter fires. Resolution order (Tekken):
   *   1. motion specials: the direction history holds the special's motion and
   *      the chord completes it (King's chain throws, Anna's db+1+2 ...).
   *      The motion wins over the plain chord — exactly like Tekken.
   *   2. the moveset's notation table (slots / player loadout) with state
   *      prefixes (FC./WS./SS./BT./R./stance codes) — canon mapping wins.
   *   3. directional chord against the current facing-relative direction
   *      (d/b+1+3 ...).
   * Returns the notation, or null when this fighter has nothing on the chord.
   * (2026-10-22: unified the two pressChord definitions — the second shadowed
   * the first, so chord resolution ignored ctx, the slots table, loadouts and
   * __base movesets. There is exactly one pressChord now.)
   */
  /** No dead chords (owner 2026-11-01: "all the different combinations of button inputs ... so I'm not limited or
      blocked"): the chord's own move first (unchanged); else its best two-button sub-chord (strikes before the 1+3 /
      2+4 throws); else its first button that resolves (direction included); else its first button, whose neutral
      move fires. Extra buttons never block a move, as in Tekken. tools/input-verify/input_matrix_audit.mjs. */
  pressChordLenient(chord, ctx = {}) {
    const own = this.pressChord(chord, ctx);
    if (own) return own;
    const b = chord.split('+');
    if (b.length > 2) {
      const subs = [];
      for (let i = 0; i < b.length; i++) for (let j = i + 1; j < b.length; j++) subs.push(b[i] + '+' + b[j]);
      const throwChord = (x) => (/^(1\+3|2\+4)$/.test(x) ? 1 : 0);
      subs.sort((x, y) => throwChord(x) - throwChord(y));
      for (const sc of subs) { const r = this.pressChord(sc, ctx); if (r) return r; }
    }
    for (const x of b) { const r = this.pressButton(x, ctx); if (r) return r; }
    return b[0];
  }

  pressChord(chord, ctx = {}) {
    const ms = playedMoveset(this.fighterId);
    if (!ms || !ms.moves) return chord; // no data — raw passthrough
    _prepare(ms);
    if (inputResolverV2()) {
      // V2: the notation table with the real stance/stick decides first (stance chords like
      // REV.b+1+3 used to lose to a context-blind legacy special); legacy specials are the fallback.
      const v = this.press(chord, ctx);
      if (v) return v;
    }
    // 1) motion specials (legacy ms.specials entries, incl. ones the slots
    //    table doesn't cover): motion in the direction history + this chord.
    for (const sp of ms.specials || []) {
      if (!sp || typeof sp.input !== 'string') continue; // v2 fix: specials without an input crashed every chord press
      const { dirs, button } = parseSpecialInput(sp.input);
      if (button !== chord || !dirs.length) continue;
      if (this._matchMotion(dirs) && resolveMoveKey(this.fighterId, sp.input)) {
        return this._recordMove(sp.input);
      }
    }
    // 2) notation table (loadout > slots), state prefixes from ctx
    const viaTable = this.press(chord, ctx);
    if (viaTable) return viaTable;
    // 3) directional chord: current facing-relative dir + chord
    const dir = this.lastDir;
    if (dir && dir !== 'n' && resolveMoveKey(this.fighterId, `${dir}+${chord}`)) {
      return this._recordMove(`${dir}+${chord}`);
    }
    return null;
  }

  /** Would `input` continue the current string? (lets a press during a move buffer the next hit) */
  continuation(input, ctx = {}) {
    if (!this.lastMove) return null;
    const dir = this.lastDir && this.lastDir !== 'n' ? this.lastDir : '';
    // BATCH STRING FIX (2026-10-24): slots redirect singles to ~shadow keys
    // ('1' -> '1~t8.king' for MOD damage), so lastMove carries the shadow suffix
    // and '1~t8.king,2' never exists — the chain broke at step 1 and the user
    // could only do 1-2 (two separate jabs, never the '1,2' string). Try the
    // stripped base too, so '1' + '2' -> '1,2' and '1,2' + '1' -> '1,2,1'.
    // Moveset sweep 2026-10-29: a pending partial string (an intermediate step with no
    // standalone move, e.g. 'WS.1+2,4' of 'WS 1+2,4,1,...') is the base while it is open,
    // exactly as in _pressV2; a press that only extends the partial keeps it open
    // (this._strPending = true) and fires nothing.
    this._strPending = false;
    const now = performance.now();
    const bases = [];
    if (this._strPath && now - this._strPathT < STRING_PENDING) bases.push(this._strPath);
    bases.push(this.lastMove);
    const tilde = this.lastMove.indexOf('~');
    if (tilde > 0) bases.push(this.lastMove.slice(0, tilde));
    const ms = playedMoveset(this.fighterId);
    for (const base of bases) {
      for (const sep of sepOrder(ctx)) {
        const mid = [ctx.stance, ctx.rage ? 'R' : null].filter(Boolean); // mid-string state ('1,NSS.1'), see _pressV2
        const cands = [...mid.flatMap((m) => [dir ? `${base}${sep}${m}.${dir}+${input}` : null, `${base}${sep}${m}.${input}`]), dir ? `${base}${sep}${dir}+${input}` : null, `${base}${sep}${input}`];
        for (const c of cands) if (c && resolveMoveKey(this.fighterId, c)) { this._strPath = null; return c; }
        for (const c of cands) if (c && ms && strPrefixesHas(this.fighterId, ms, c)) {
          this._strPath = c; this._strPathT = now; this._strPending = true; return null;
        }
      }
    }
    return null;
  }

  _recordMove(notation) {
    this.lastMove = notation;
    this.lastMoveT = performance.now();
    return notation;
  }

  /** Throws / explicit notations bypass the buffer. */
  recordExplicit(notation) {
    this._recordMove(notation);
  }

}

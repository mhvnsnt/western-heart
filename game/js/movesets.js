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
export const MOVESET_IDS = [
  'pantera', 'demonio', 'phantom', 'diablo', 'skull', 'samura1', 'sakura',
  'rin', 'byou', 'tou', 'sha', 'kai', 'jin_soul', 'retsu', 'zen', 'gyou',
  'zui', 'kinpo', 'waterfall', 'kingtyrant', 'burger', 'awapop', 'scimitar',
  'purplerain', 'nightwolf', 'dio', 'cyborgx', 'michiko', 'star', 'torch',
  'bruno', 'negativo', 'thor', 'yukihyo', 'slice', 'docfrank',
  'sunra', 'dxmmii', 'realizzt', 'rave', 'kutz', 'chordz', 'vainabel',
  'lili', 'baek',
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
   (direction, neutral, direction within 0x13 frames), history = 60 one-frame entries. */
let DOUBLE_TAP_BUDGET = 0x13;
let DASH_FRAMES = { 'f,f': 30, 'b,b': 32 }; // decoded: every bank's dash row is 30 frames, backdash 30-35
const HIST_LEN = 60;
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
export function parseMotion(n) {
  const { prefix, body } = splitNotation(n);
  const parts = body.split(',');
  const last = parts[parts.length - 1];
  const lm = /^(?:(qcf|qcb|hcf|hcb|d\/f|d\/b|u\/f|u\/b|f|b|u|d|D\/F|D\/B|U\/F|U\/B|F|B|U|D)\+)?([1-4](?:\+[1-4])*)\*?$/.exec(last);
  if (!lm) return null;
  const head = parts.slice(0, -1);
  if (head.some(p => !DIR_TOKEN.test(p))) return null; // a button earlier = string, not motion
  let dirs = head.map(d => d.toLowerCase());
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
  if (dirs.filter(d => d !== 'n').length < 2 && !(lm[1] && MOTION_DIRS[lm[1]])) return null; // plain directional
  return { prefix, dirs, btn: lm[2], neutral };
}

function _prepare(ms) {
  if (!ms || !ms.moves || ms._slots) return;
  const slots = Object.assign({}, ms.slots || {});
  for (const k of Object.keys(ms.moves)) if (!(k in slots)) slots[k] = k;
  ms._slots = slots;
  const motions = [];
  for (const n of Object.keys(slots)) {
    const m = parseMotion(n);
    if (m) motions.push({ n, ...m });
  }
  motions.sort((a, b) => b.dirs.length - a.dirs.length); // longest motion wins (qcf+1 over f+1)
  ms._motions = motions;
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
export function resolveMove(fighterId, notation) {
  if (!notation) return null;
  const custom = getLoadout(fighterId)[notation];
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
export class TekkenBuffer {
  constructor(fighterId) {
    this.fighterId = fighterId;
    this.dirEvents = [];   // [{dir, t}] facing-relative: f,b,u,d,d/f,d/b,u/f,u/b
    this.lastDir = 'n';
    this.lastMove = null;  // notation of last executed attack
    this.lastMoveT = 0;
    // T3 input history: one facing-relative direction per fixed 1/60 s step (game.js calls
    // noteDirection every update), 60 entries, newest at this.hi (fight_sim HISTORY / HIST_LEN).
    this.hist = new Array(HIST_LEN).fill('n');
    this.hi = 0;
  }

  /** Feed the current facing-relative direction (call when it changes). */
  noteDirection(dir) {
    this.hi = (this.hi + 1) % HIST_LEN;
    this.hist[this.hi] = dir || 'n';
    // T3 enters the dash row on the frame double_tap matches; a button during that row is a
    // dash move (f,F+2). Latch it for the decoded row length.
    if (this._dash && --this._dash.left <= 0) this._dash = null;
    if (this._doubleTap('f')) this._dash = { dir: 'f', left: DASH_FRAMES['f,f'] };
    else if (this._doubleTap('b')) this._dash = { dir: 'b', left: DASH_FRAMES['b,b'] };
    if (dir === this.lastDir) return;
    this.lastDir = dir;
    if (dir === 'n') return;
    const now = performance.now();
    this.dirEvents.push({ dir, t: now });
    if (this.dirEvents.length > 24) this.dirEvents.shift();
  }

  _prev(i) { return i > 0 ? i - 1 : HIST_LEN - 1; }

  /** T3 double tap (FUN_8002CB08 / FUN_8002CBF0, fight_sim.double_tap): the newest frame is
      `dir`, the frame before it neutral, then within DOUBLE_TAP_BUDGET frames an earlier `dir`. */
  _doubleTap(dir) {
    const h = this.hist; let i = this.hi;
    if (h[i] !== dir) return false;
    let j = this._prev(i);
    if (h[j] !== 'n') return false;
    let budget = DOUBLE_TAP_BUDGET, k = j;
    for (;;) {
      k = this._prev(j);
      const d = h[k];
      if (d !== 'n') { if (d !== dir) return false; break; }
      budget--; j = k;
      if (budget <= 0) break;
    }
    if (budget <= 0) return false;
    for (;;) {
      const m = this._prev(k);
      if (h[m] !== dir) break;
      budget--; k = m;
      if (budget <= 0) break;
    }
    return budget > 0;
  }

  /** T3 InputSequenceMatch (0x8002CCD8, fight_sim.sequence_match) over the direction history:
      the newest frame must be the last step, earlier steps are found walking back within
      `window` frames. (Button entries in the T3 history abort a match; WH records buttons as
      events, so that clause has no counterpart here.) */
  _seqMatch(steps, window) {
    const h = this.hist; let k = steps.length - 1;
    if (h[this.hi] !== steps[k]) return false;
    k--; if (k < 0) return true;
    let want = steps[k], pos = this.hi;
    while (window >= 1) {
      pos = this._prev(pos);
      if (h[pos] === want) { k--; if (k < 0) return true; want = steps[k]; }
      window--;
    }
    return false;
  }

  /** Does the history hold this motion (decoded T3 timing)? */
  _motionHeld(dirs) {
    if (dirs.length === 2 && dirs[0] === dirs[1] && (dirs[0] === 'f' || dirs[0] === 'b')) {
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
   * `ctx` (Fighter._inputCtx): { stance, crouching, rising, sidestep, backturned, rage }.
   * Order (Tekken): string continuation > state/stance prefix (stance code, R. rage art,
   * BT., SS., FC., WS.) > motion (qcf, f,F, b,f, d,d/f,f ...) > direction+button > button.
   * Returns the notation, or null if this fighter has nothing on that input.
   */
  press(input, ctx = {}) {
    const ms = playedMoveset(this.fighterId);
    if (!ms || !ms.moves) return input; // no data — raw passthrough
    _prepare(ms);
    const has = (n) => (resolveMoveKey(this.fighterId, n) ? n : null);
    const dir = this.lastDir && this.lastDir !== 'n' ? this.lastDir : '';
    const withDir = dir ? `${dir}+${input}` : input;
    const holdDir = dir ? `${dir.toUpperCase()}+${input}` : null;

    // 1) string continuation. In a fight (ctx.inMove defined) T3 rules: only while the previous
    //    hit is still playing (Fighter.tryAttack buffers it into that move). Legacy callers
    //    without ctx (tests) keep the old 800 ms window.
    const contOk = ctx.inMove !== undefined ? ctx.inMove : (performance.now() - this.lastMoveT < 800);
    if (this.lastMove && contOk) {
      for (const sep of [',', '~', ':']) {
        for (const c of [`${this.lastMove}${sep}${withDir}`, `${this.lastMove}${sep}${input}`]) {
          if (has(c)) return this._recordMove(c);
        }
      }
    }
    const prefixes = [];
    if (ctx.stance) prefixes.push(ctx.stance + '.');
    if (ctx.rage) prefixes.push('R.');
    if (ctx.backturned) prefixes.push('BT.');
    if (ctx.sidestep) prefixes.push('SS.');
    if (ctx.crouching) prefixes.push('FC.');
    if (ctx.rising) prefixes.push('WS.');
    prefixes.push('');
    for (const p of prefixes) {
      // 2) motion inputs on this button, longest first
      for (const mo of ms._motions) {
        if (mo.prefix !== p || mo.btn !== input) continue;
        if (mo.neutral && dir) continue; // 'f,n,2' wants the stick back in neutral
        if (this._motionHeld(mo.dirs) && has(mo.n)) return this._recordMove(mo.n);
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

  /** Legacy API: chords resolve through the same table. */
  pressChord(chord, ctx = {}) {
    const ms = playedMoveset(this.fighterId);
    if (!ms || !ms.moves) return chord;
    return this.press(chord, ctx);
  }

  /** Would `input` continue the current string? (lets a press during a move buffer the next hit) */
  continuation(input) {
    if (!this.lastMove) return null;
    const dir = this.lastDir && this.lastDir !== 'n' ? this.lastDir : '';
    for (const sep of [',', '~', ':']) {
      for (const c of [dir ? `${this.lastMove}${sep}${dir}+${input}` : null, `${this.lastMove}${sep}${input}`]) {
        if (c && resolveMoveKey(this.fighterId, c)) return c;
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

  /**
   * Resolve a button CHORD ('1+2', '1+3', '1+4', '2+3', '2+4', '3+4') to a
   * Tekken notation. Motion specials whose chord matches fire when their
   * motion is in the direction history (King's chain throws). Directional
   * chords ('d/b+1+3') resolve against the current direction (Stream 6).
   * Plain chords ('1+3','2+4',...) resolve to themselves.
   * Returns the notation or null.
   */
  pressChord(chord) {
    const ms = getFighterMoveset(this.fighterId);
    if (!ms || !ms.moves) return chord;
    const moves = ms.moves;
    for (const sp of ms.specials || []) {
      const { dirs, button } = parseSpecialInput(sp.input);
      if (button !== chord) continue;
      if (dirs.length && this._matchMotion(dirs) && moves[sp.input]) {
        this._recordMove(sp.input);
        return sp.input;
      }
    }
    // directional chord: current facing-relative dir + chord (d/b+1+3 ...)
    const dir = this.lastDir;
    if (dir && dir !== 'n') {
      const dchord = `${dir}+${chord}`;
      if (moves[dchord]) {
        this._recordMove(dchord);
        return dchord;
      }
    }
    // plain chord with no motion attached
    if (moves[chord]) {
      this._recordMove(chord);
      return chord;
    }
    return null;
  }
}

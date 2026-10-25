// Moveset reachability (lane B, 2026-10-24; owner: "get all the combos and different moves working
// ... the different move inputs from the move lists aren't working ... random stuff is happening",
// "8 or 10 button strings, some 16-hit", "can't attack while crouching, jumping, or moving").
//
// For EVERY fighter in game/assets/movesets/index.json and EVERY playable notation in its notation
// table (ms._slots: the slots table + every move key that is itself a notation), press that
// notation the way a player does and assert that exactly its move plays:
//   - real code: the fight's own Fighter.tryAttack / _tryAttackFresh / _tickState / _drainPressBuffer
//     (fighter.js, imported headless; 'three' resolves to the vendored build) on top of the real
//     TekkenBuffer resolver (movesets.js) and the real input.js chord logic (InputManager._tekken),
//     stepped at the fight loop's FIXED_DT = 1/120 with a virtual clock, in game.js order (stick,
//     walk, the 200 ms up/down hold -> jump / crouch, direction history, presses, update);
//   - realistic timing: taps 2 frames, holds 10 frames (HOLD_FRAMES = 8), motions 2 frames per step,
//     a chord's two buttons 8 ms apart, every later string step pressed ~100 ms into the hit before
//     it, '~' steps 55 ms after the previous press — and, reported, a steady 150 ms rhythm and the
//     touch rhythms 120 / 180 / 250 ms per tap for every 4+ press string;
//   - state prefixes get the state the game gives them: FC = hold d past the 200 ms crouch, WS =
//     release that crouch, SS = sidestep, R./RD. = <=25% hp, UB./US./H. = Soul Urge, BT./stance codes
//     = that stance (game-reachable only when some move transitions into it).
// Per fighter: playable notations, resolved correctly, ambiguous (two moves on one physical input),
// unreachable (with the reason), wrong (a resolver bug: the gate). Data problems are listed, not
// fixed (moveset JSONs belong to the moveset lanes). Rules: docs/input/INPUT-RESOLVER-V2.md.
//
// Run: node --test test/moveset-reachability.test.mjs
//      node test/moveset-reachability.test.mjs [--report out.json] [--fighter skull] [--verbose]
//      REACH_TRACE='<notation>' prints every press of that notation.
import test from 'node:test';
import assert from 'node:assert/strict';
import { register } from 'node:module';
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const JS = join(ROOT, 'game', 'js');
const MS_DIR = join(ROOT, 'game', 'assets', 'movesets');
const argv = process.argv.slice(2);
const arg = (k) => (argv.includes(k) ? argv[argv.indexOf(k) + 1] : null);
const ONLY = arg('--fighter');
const REPORT = arg('--report') || process.env.REACH_REPORT || null;
const VERBOSE = argv.includes('--verbose');

// ---- headless browser shims ------------------------------------------------------------------
register('data:text/javascript,' + encodeURIComponent(`
const THREE_URL = ${JSON.stringify(pathToFileURL(join(ROOT, 'game', 'vendor', 'three.module.js')).href)};
const ADDONS = ${JSON.stringify(pathToFileURL(join(ROOT, 'game', 'vendor', 'addons') + '/').href)};
export async function resolve(spec, ctx, next) {
  if (spec === 'three') return { url: THREE_URL, shortCircuit: true };
  if (spec.startsWith('three/addons/')) return { url: ADDONS + spec.slice(13), shortCircuit: true };
  return next(spec, ctx);
}`));
let CLOCK = 10000; // ms — every performance.now() in the resolver / fighter / input reads this
Object.defineProperty(globalThis, 'performance', { value: { now: () => CLOCK }, configurable: true, writable: true });
globalThis.window = globalThis.window || { addEventListener() {}, WH_MOVESETS: {} };
globalThis.document = globalThis.document || { createElement: () => ({ getContext: () => null, style: {} }), addEventListener() {} };
const _ls = {};
globalThis.localStorage = { getItem: k => _ls[k] ?? null, setItem: (k, v) => { _ls[k] = String(v); }, removeItem: k => { delete _ls[k]; } };

const M = await import(pathToFileURL(join(JS, 'movesets.js')).href);
const { Fighter } = await import(pathToFileURL(join(JS, 'fighter.js')).href);
const { ensureRageMoves } = await import(pathToFileURL(join(JS, 'rage.js')).href);
const { ensureUrgeMoves } = await import(pathToFileURL(join(JS, 'soulurge.js')).href);
const { InputManager } = await import(pathToFileURL(join(JS, 'input.js')).href);
try { M.setInputTables(JSON.parse(readFileSync(join(MS_DIR, 't3_input_tables.json'), 'utf8'))); } catch (e) { /* decoded defaults */ }
const msApi = { playedMoveset: M.playedMoveset, getFighterMoveset: M.getFighterMoveset };

// ---- notation grammar ------------------------------------------------------------------------
const DIRS = 'd/f|d/b|u/f|u/b|f|b|u|d|n|D/F|D/B|U/F|U/B|F|B|U|D|N';
const BTN = '[1-4](?:\\+[1-4])*\\*?';
const RX_PRESS = new RegExp(`^(?:(qcf|qcb|hcf|hcb|${DIRS})\\+)?(${BTN})$`);
const RX_DIR = new RegExp(`^(?:qcf|qcb|hcf|hcb|${DIRS})$`);
const RX_PFX = /^((?:[A-Za-z][A-Za-z0-9_]*\.)+)(.*)$/;
const ENGINE_STATES = new Set(['FC', 'WS', 'SS', 'BT', 'R', 'RD', 'UB', 'US', 'H']); // H = Soul Urge (T8 Heat)
const MERGE_KEY = /~[a-z][a-z0-9_-]*\./; // '1~t8.bryan', 'b+3,2~t7.bryan.2': merge-source move keys

/** notation -> { steps:[{text, prefix, body, sep, upto}], why } ; why set = not playable. */
function parseNotation(n) {
  if (MERGE_KEY.test(n)) return { why: 'merge-source key (not an input)' };
  if (/^[A-Z]+:/.test(n)) return { steps: [], why: `side condition '${n.split(':')[0]}:' (opponent front / back, T7 parser data) is not an input` };
  const parts = []; let cur = '', seps = [];
  for (const ch of n) { if (',~:'.includes(ch)) { parts.push(cur); seps.push(ch); cur = ''; } else cur += ch; }
  parts.push(cur);
  const steps = []; let acc = [], accSep = null, pos = 0;
  for (let i = 0; i < parts.length; i++) {
    const t = parts[i];
    pos += t.length + (i ? 1 : 0);
    const pm = RX_PFX.exec(t);
    const body = pm ? pm[2] : t;
    if (!RX_PRESS.test(body) && !RX_DIR.test(body)) return { why: `not a notation (token '${t}')` };
    if (pm && acc.length) return { why: `state prefix inside a motion ('${t}')` };
    if (!acc.length) accSep = i ? seps[i - 1] : null;
    acc.push(t);
    if (RX_PRESS.test(body)) { steps.push({ text: acc.join(','), sep: accSep, upto: n.slice(0, pos) }); acc = []; }
  }
  if (acc.length) return { steps, why: `direction-only step '${acc.join(',')}' (no button to press)` };
  const big = steps.find(s => /[1-4]\+[1-4]\+[1-4]/.test(s.text));
  if (big) return { steps, why: `3+ button chord '${big.text}' (input.js forms two-button chords only)` };
  if (new RegExp(`(^|[,.])(${DIRS})~(${DIRS})(\\+|$)`).test(n)) return { steps, why: `'~' between two directions (SF charge notation '${n}') is not a Tekken input the resolver parses` };
  for (const s of steps) {
    const pm = RX_PFX.exec(s.text);
    s.prefix = pm ? pm[1] : ''; s.body = pm ? pm[2] : s.text;
  }
  return { steps };
}

/** Same physical input in WH (JF ':' / '~' read like ','; qcf = d,d/f,f; 'f,n,f' dash = 'f,f';
    'n+1' / 'n,1' = '1'; crouching FC.d+1 = FC.1; RD. = R.; Heat H. dropped). */
const EXPAND = { qcf: 'd,d/f,f', qcb: 'd,d/b,b', hcf: 'b,d/b,d,d/f,f', hcb: 'f,d/f,d,d/b,b' };
function physical(n) {
  const pm = RX_PFX.exec(n); const pre = pm ? pm[1].replace(/^RD\./, 'R.').replace(/(^|\.)H\./, '$1') : ''; let b = pm ? pm[2] : n;
  if (/(^|\.)FC\.$/.test(pre)) b = b.replace(/^d\+(?=[1-4])/, ''); // crouching IS holding d: FC.d+1 = FC.1
  b = b.replace(/,n[,~:](?=[1-4])/g, ',').replace(/(^|,)n[,~:](?=[1-4])/g, '$1').replace(/([a-zA-Z/]):(?=[1-4])/g, '$1+').replace(/[~:]/g, ',').replace(/,[A-Z][A-Z0-9_]*\./g, ',')
    .replace(/(^|,)H\./g, '$1').replace(/([a-zA-Z/]),(?=[1-4])/g, '$1+')
    .replace(/\*/g, '').replace(/(^|,)(qcf|qcb|hcf|hcb)\+/g, (m, a, k) => `${a}${EXPAND[k]}+`)
    .replace(/(^|,)(qcf|qcb|hcf|hcb)(?=,|$)/g, (m, a, k) => a + EXPAND[k]);
  const t = b.split(',').map(x => x.replace(/^n\+(?=[1-4])/, '')); const out = [];
  const dirOf = (x) => (x || '').split('+')[0];
  for (let i = 0; i < t.length; i++) {
    if (t[i] === 'n' && (!out.length || dirOf(out[out.length - 1]) === dirOf(t[i + 1]))) continue; // f,n,f = f,f
    out.push(t[i]);
  }
  return pre + out.join(',');
}

// ---- headless fight ----------------------------------------------------------------------------
const DT = 1 / 120; // game.js FIXED_DT
const F60 = 1000 / 60;
function makeFighter(id) {
  const f = Object.create(Fighter.prototype);
  Object.assign(f, {
    char: { id }, _movesetId: id, isPlayer: true, facing: 1,
    stats: { speed: 2.8, jump: 7.2, power: 1.1, defense: 1.05 },
    maxHp: 100, hp: 100, meter: 0, maxMeter: 100, vx: 0, vy: 0, vz: 0, onGround: true,
    state: 'idle', stateT: 0, attack: null, attackName: null, _attackPhase: 'startup', hasHit: false,
    stun: 0, invuln: 0, dead: false, combo: 0, _comboTimer: 0,
    tekken: new M.TekkenBuffer(id), stance: null, stanceT: 0, _risingT: 0, _stickDir: 'n',
    _juggle: 0, _rageUsed: false, _queuedNext: null, _rageOn: false, _stringGraceUntil: 0,
    _urgeOn: false, _urgeUsed: true, _urgeT: 0, _urgePips: 0, _urgeDashT: 0, // urge spent: 2+3 is the fighter's own
    root: { position: { x: 0, y: 0, z: 0 } }, _attackId: 0,
  });
  return f;
}
function makeInput() {
  const inp = Object.create(InputManager.prototype);
  Object.assign(inp, { enabled: true, _queue: [], _lastT: { 1: 0, 2: 0, 3: 0, 4: 0 }, _udDir: null, _udHeld: false, _udUsed: false, up: false, down: false });
  return inp;
}

class Sim {
  constructor(id) {
    this.id = id; this.f = makeFighter(id); this.inp = makeInput();
    this.stick = 'n'; this.crouch = false; this.fired = []; this.lastId = 0; this.pinStance = null; this.t = 0;
  }
  _log() { const f = this.f; if ((f._attackId || 0) !== this.lastId) { this.lastId = f._attackId; this.fired.push({ n: f.attackName, t: Math.round(this.t) }); } }
  /** One fixed tick in game.js order. */
  tick(buttons = []) {
    const f = this.f;
    f.setStick(this.stick);
    // tryMove(axisX) every tick (walk); up/down held past input.js's 200 ms tap window = jump /
    // crouch (inp.up / inp.down); tryCrouch(down && !up)
    const vert = /^u/.test(this.stick) ? 'u' : /^d/.test(this.stick) ? 'd' : null;
    if (vert !== this._vert) { this._vert = vert; this._vertT = 0; } else if (vert) this._vertT += DT * 1000;
    const vHeld = vert && this._vertT >= 200;
    f.tryMove(/(^|\/)f$/.test(this.stick) ? 1 : /(^|\/)b$/.test(this.stick) ? -1 : 0);
    if (vert === 'u' && vHeld) f.tryJump();
    f.tryCrouch(this.crouch || (vert === 'd' && vHeld));
    f.tekken.noteDirection(this.stick, DT);
    for (const b of buttons) this.inp._tekken(b);
    for (const act of this.inp.consume()) {
      const ok = f.tryAttack(act); this._log();
      if (this.trace) console.log(`  t=${Math.round(this.t)} stick=${this.stick} press ${act} -> ${ok} now=${f.attackName} st=${f.state} stateT=${f.stateT.toFixed(3)} q=${f._queuedNext} more=${(f._queuedMore || []).join('|')} path=${f.tekken._strPath}`);
    }
    f.stateT += DT; f._clock = (f._clock || 0) + DT; // update(): the PressBuffer clock
    if (f.stun > 0) f.stun -= DT;
    if (f._risingT > 0) f._risingT -= DT;
    if (this.pinStance && f.state !== 'attack') { f.stance = this.pinStance; f.stanceT = 1; }
    else if (f.stanceT > 0) { f.stanceT -= DT; if (f.stanceT <= 0) f.stance = null; }
    if (f.state === 'jump' && f.stateT > 0.6) f.onGround = true; // land (no physics here)
    if (!f.onGround && f.state !== 'jump' && f.state !== 'attack') f.onGround = true;
    f._tickState(); this._log();
    if (f._drainPressBuffer) { f._drainPressBuffer(); this._log(); } // a buffered press fires on the first actionable frame
    CLOCK += DT * 1000; this.t += DT * 1000;
  }
  run(ms, buttons) { const n = Math.max(1, Math.round(ms / (DT * 1000))); for (let i = 0; i < n; i++) this.tick(i === 0 && buttons ? buttons : []); }
  press(btns, skewMs = 8) { // a chord: input.js sees the two buttons skewMs apart (inside CHORD_WINDOW_MS)
    const bs = btns.split('+');
    if (bs.length === 1) return this.tick(bs);
    this.tick([bs[0]]);
    for (let k = 1; k < bs.length; k++) { CLOCK += skewMs - DT * 1000; this.tick([bs[k]]); }
  }
  idleUntilDone(maxMs = 5000) { for (let t = 0; t < maxMs && (this.f.state === 'attack' || this.f._queuedNext); t += DT * 1000) this.tick(); }
}

/** Feed the stick for a press body ('d/f+1', 'D/F+1', 'f,F+2', 'qcf+1', 'd,4', '1'); returns the button(s). */
function stickFor(sim, body, crouched) {
  const tr = new RegExp(`^(?:(${DIRS}),)?(?:n,)?(${BTN})$`).exec(body); // tap-release: 'd,4' 'f,n,4' 'n,4'
  if (tr && body.includes(',')) {
    if (tr[1] && tr[1] !== 'n') { sim.stick = tr[1].toLowerCase(); sim.run(2 * F60); }
    sim.stick = 'n'; sim.run(2 * F60);
    return tr[2].replace(/\*$/, '');
  }
  const mo = M.parseMotion(body);
  if (mo) {
    const steps = mo.dirs;
    for (let i = 0; i < steps.length; i++) {
      sim.stick = steps[i]; sim.run(2 * F60);
      if (steps[i + 1] === steps[i]) { sim.stick = 'n'; sim.run(2 * F60); }
    }
    const fin = body.split(',').pop().split('+')[0];
    if (!mo.neutral && /^[A-Z]/.test(fin)) sim.run(4 * F60); // capital final step = held (MOTION_HOLD)
    if (mo.neutral) { sim.stick = 'n'; sim.run(2 * F60); }
    return mo.btn;
  }
  const m = new RegExp(`^(?:(${DIRS})\\+)?(${BTN})$`).exec(body);
  if (!m) return null;
  const d = m[1];
  if (!d) { sim.stick = crouched ? 'd' : 'n'; return m[2].replace(/\*$/, ''); }
  const lower = d.toLowerCase();
  if (sim.stick !== lower) { sim.stick = lower; sim.run((d === lower ? 2 : 10) * F60); }
  else if (d !== lower) sim.run(10 * F60);
  return m[2].replace(/\*$/, '');
}

/** Put the fighter into the state a prefix needs. Returns { ok, crouched, gameReachable, why }. */
function enterState(sim, prefix, stanceSet) {
  const toks = prefix.split('.').filter(Boolean);
  const f = sim.f; let crouched = false, rising = false;
  const notes = [];
  const stances = toks.filter(t => !ENGINE_STATES.has(t) || t === 'BT');
  if (stances.length > 1) return { ok: false, why: `two stances at once (${stances.join('+')}): the engine holds one stance` };
  for (const t of toks) {
    if (t === 'FC') crouched = true;
    else if (t === 'WS') rising = true;
    else if (t === 'R' || t === 'RD') f.hp = 20;
    else if (t === 'UB') { f._urgeUsed = false; f._urgeOn = false; }
    else if (t === 'US' || t === 'H') { f._urgeUsed = true; f._urgeOn = true; f._urgePips = 2; }
    else if (t === 'SS') { /* below */ }
    else { sim.pinStance = t; f.stance = t; f.stanceT = 1; if (t !== 'BT' && !stanceSet.has(t)) notes.push(t); }
    if (t === 'BT' && !stanceSet.has('BT')) notes.push('BT');
  }
  if (crouched || rising) { sim.stick = 'd'; sim.crouch = true; sim.run(260); } // hold d past input.js's 200 ms crouch
  if (rising) { sim.stick = 'n'; sim.crouch = false; sim.run(2 * F60); }
  if (toks.includes('SS')) { if (!f.trySidestep(1)) return { ok: false }; sim.run(200); }
  return { ok: true, crouched, gameReachable: !notes.length, why: notes.length ? `stance ${notes.join('+')} is never entered (no move's stance_after leads there)` : null };
}

const sameMove = (ms, a, b) => {
  if (!a || !b) return false;
  if (a === b) return true;
  const x = ms.moves[a], y = ms.moves[b];
  return !!(x && y && x.name === y.name && x.startup === y.startup && x.damage === y.damage);
};

/** Press notation `n` on a fresh fighter. rhythm: 'hit' (press ~100 ms into the previous hit) | ms per tap */
function play(id, n, parsed, stanceSet, rhythm = 'hit') {
  const sim = new Sim(id);
  sim.trace = process.env.REACH_TRACE === n && rhythm === 'hit';
  sim.run(10 * F60);
  const st = enterState(sim, parsed.steps[0].prefix, stanceSet);
  if (!st.ok) return { fired: [], unreachable: st.why || 'could not enter the state' };
  for (const s of parsed.steps.slice(1)) { // a mid-string Heat / rage step needs that state too
    if (/(^|\.)H\.$/.test(s.prefix)) { sim.f._urgeOn = true; sim.f._urgeUsed = true; sim.f._urgePips = 2; }
    if (/(^|\.)R\.$/.test(s.prefix)) sim.f.hp = 20;
  }
  let lastPressT = null, idAtPress = 0;
  for (let i = 0; i < parsed.steps.length; i++) {
    const s = parsed.steps[i];
    if (i > 0) {
      const prev = parsed.steps[i - 1].upto; // the notation typed so far
      if (s.sep === '~') { while (sim.t - lastPressT < 55) sim.tick(); } // '~' = immediately: 55 ms (past the 50 ms chord window, inside the 4-frame '~' window)
      else if (rhythm === 'hit') {
        if (M.resolveMoveKey(id, prev)) { // its move should be playing: press ~100 ms into it
          let waited = 0; // (the hit this press produced, under any spelling: qcb+1+3 for d,d/b,b+1+3)
          const playing = () => sim.f.state === 'attack' && (sim.f._attackId || 0) > idAtPress && !sim.f._queuedNext;
          while (!playing() && waited < 4000) { sim.tick(); waited += DT * 1000; } // multi-hit 'active' can run 2+ s
          while (playing() && sim.f.stateT < 0.1) sim.tick();
        }
        while (sim.t - lastPressT < 130) sim.tick(); // a string step with no move: next press 130+ ms later
      } else while (sim.t - lastPressT < rhythm) sim.tick();
    }
    const body = s.body; // mid-string prefixes ('3+4,SNE.2') are typed as the bare press
    if (i > 0 && !/[a-zA-Z]/.test(body.replace(/\*$/, ''))) sim.stick = 'n';
    const btn = stickFor(sim, body, i === 0 && st.crouched);
    if (!btn) return { fired: sim.fired.map(x => x.n), unreachable: `step '${s.text}' has no press` };
    lastPressT = sim.t; idAtPress = sim.f._attackId || 0;
    sim.press(btn);
    if (/[a-zA-Z]/.test(body) && !M.parseMotion(body) && !body.includes(',')) { sim.run(2 * F60); sim.stick = st.crouched && i === 0 ? 'd' : 'n'; }
  }
  sim.stick = 'n'; sim.crouch = false; sim.pinStance = null;
  sim.idleUntilDone();
  return { fired: sim.fired.map(x => x.n), gameReachable: st.gameReachable, stateWhy: st.why, stuckQueue: sim.f.state !== 'attack' ? sim.f._queuedNext : null };
}

// ---- per-fighter sweep -------------------------------------------------------------------------
const index = JSON.parse(readFileSync(join(MS_DIR, 'index.json'), 'utf8'));
const ids = Object.keys(index.fighters || {}).filter(id => !ONLY || id === ONLY);
const report = { generated: new Date().toISOString(), tick: DT, fighters: {}, totals: {} };

function sweep(id) {
  const data = JSON.parse(readFileSync(join(MS_DIR, `${id}.json`), 'utf8'));
  M.registerMoveset(id, data);
  ensureRageMoves(id, msApi); ensureUrgeMoves(id, msApi);
  const ms = M.getFighterMoveset(id);
  const stanceSet = new Set(Object.values(ms.stance_after || {}).filter(Boolean));
  const r = {
    playable: 0, ok: 0, okFixedRhythm: 0, ambiguous: [], unreachable: [], wrong: [], notNotation: 0, notNotationEx: [],
    stanceNeverEntered: new Set(), shadowed: 0, shadowedEx: [], stringStepsWithoutMove: 0, stringStepsWithoutMoveEx: [],
    neutral: {}, system: {},
  };
  // shadowed: moves whose own `input` is a notation that the slots table binds to another move
  for (const [k, mv] of Object.entries(ms.moves)) {
    const inp = mv && typeof mv.input === 'string' ? mv.input : null;
    if (!inp || inp === k) continue;
    const tgt = ms._slots[inp];
    if (tgt && tgt !== k && !sameMove(ms, tgt, k)) { r.shadowed++; if (r.shadowedEx.length < 8) r.shadowedEx.push(`${inp}: '${ms.moves[k].name}' (${k}) loses to '${ms.moves[tgt].name}' (${tgt})`); }
  }
  for (const n of Object.keys(ms._slots)) {
    const key = ms._slots[n];
    if (!ms.moves[key]) continue;
    const p = parseNotation(n);
    if (p.why && !p.steps) { r.notNotation++; if (r.notNotationEx.length < 8) r.notNotationEx.push(n); continue; }
    r.playable++;
    if (p.why) { r.unreachable.push({ n, why: p.why }); continue; }
    // string steps with no move of their own (data): reachable, but those presses play nothing
    for (let i = 1; i < p.steps.length; i++) {
      const pre = p.steps[i - 1].upto;
      if (!M.resolveMoveKey(id, pre)) { r.stringStepsWithoutMove++; if (r.stringStepsWithoutMoveEx.length < 6) r.stringStepsWithoutMoveEx.push(`${pre} (of ${n})`); break; }
    }
    const res = play(id, n, p, stanceSet);
    const last = res.fired.length ? res.fired[res.fired.length - 1] : null;
    const gotKey = last ? M.resolveMoveKey(id, last) : null;
    if (res.stateWhy) r.stanceNeverEntered.add(res.stateWhy.replace(/^stance (\S+).*/, '$1'));
    const mergeFired = res.fired.find(x => MERGE_KEY.test(x || ''));
    const pre = res.fired.filter(x => x && n.length > x.length && ',~:'.includes(n[x.length]) && n.startsWith(x)).sort((a, b) => b.length - a.length)[0];
    const stopAt = pre ? M.getMove(id, pre) : null;
    if (mergeFired) {
      r.wrong.push({ n, want: ms.moves[key].name, fired: res.fired, firedMove: 'MERGE-SOURCE KEY ' + mergeFired });
    } else if (last === n || sameMove(ms, gotKey, key)) {
      r.ok++;
      const fx = play(id, n, p, stanceSet, 150);
      const fl = fx.fired.length ? fx.fired[fx.fired.length - 1] : null;
      if (fl === n || sameMove(ms, fl && M.resolveMoveKey(id, fl), key)) r.okFixedRhythm++;
      if (!res.gameReachable) r.unreachable.push({ n, why: res.stateWhy, resolverOk: true });
    } else if (last && physical(last).toLowerCase() === physical(n).toLowerCase()) { // same input (tap/hold or just-frame spelling)
      r.ambiguous.push({ n, move: ms.moves[key].name, winner: last, winnerMove: ms.moves[gotKey] ? ms.moves[gotKey].name : null });
    } else if (/^(H\.)?2\+3(,|$)/.test(n) && res.fired.some(x => /^U[SB]\.2\+3$/.test(x || ''))) {
      r.unreachable.push({ n, why: '2+3 is the Soul Urge button while the gauge is live (T8 Heat rule): the system Urge Burst / Urge Smash plays', system: true });
    } else if (res.unreachable) {
      r.unreachable.push({ n, why: res.unreachable });
    } else if (res.stuckQueue && M.resolveMoveKey(id, res.stuckQueue)) {
      const playing = M.getMove(id, last) || {};
      r.unreachable.push({ n, why: `buffered '${res.stuckQueue}' never fired: '${last}' has recovery ${playing.recovery}`, engine: 'recovery0' });
    } else if (stopAt && !(stopAt.recovery > 0)) {
      r.unreachable.push({ n, why: `string parent '${pre}' has recovery 0`, engine: 'recovery0' });
    } else if (!res.gameReachable) {
      r.unreachable.push({ n, why: `${res.stateWhy}; forced-state run fired ${res.fired.join(' > ') || 'nothing'}`, forcedStateMiss: true });
    } else {
      r.wrong.push({ n, want: ms.moves[key].name, fired: res.fired, firedMove: gotKey && ms.moves[gotKey] ? ms.moves[gotKey].name : null });
    }
  }
  // neutral 1/2/3/4 and the system chords (Soul Urge HEAT = 2+3, rage drive 3+4)
  for (const b of ['1', '2', '3', '4']) {
    const res = play(id, b, parseNotation(b), stanceSet);
    const slot = M.resolveMoveKey(id, b);
    r.neutral[b] = { fired: res.fired[0] || null, ok: slot ? sameMove(ms, res.fired[0] && M.resolveMoveKey(id, res.fired[0]), slot) : !res.fired.length || res.fired[0] === b };
  }
  const sys = (setup, btn) => { const sim = new Sim(id); sim.run(10 * F60); setup(sim.f); sim.press(btn); sim.idleUntilDone(); const x = sim.fired[sim.fired.length - 1]; return x ? x.n : null; };
  r.system.heatFresh = sys(f => { f._urgeUsed = false; }, '2+3');
  r.system.heatUrging = sys(f => { f._urgeOn = true; f._urgePips = 2; }, '2+3');
  r.system.rageDrive = sys(f => { f.hp = 20; }, '3+4');
  r.system.rageArt = sys(f => { f.hp = 20; }, '1+2');
  // Crouched (d held past the 200 ms crouch) then the stick at d/f or d/b: the exact held spelling
  // (D/F+1) when the moveset has it, else FC.d/f+1, else FC.1.
  r.heldOverFC = {};
  for (const d of ['d/f', 'd/b']) for (const b of ['1', '2', '3', '4']) {
    const held = `${d.toUpperCase()}+${b}`;
    const want = [held, `FC.${d}+${b}`, `FC.${held}`, `FC.${b}`].find(x => M.resolveMoveKey(id, x));
    if (!want || !M.resolveMoveKey(id, `FC.${b}`)) continue; // only fighters with both families matter
    const sim = new Sim(id); sim.run(10 * F60);
    sim.stick = 'd'; sim.crouch = true; sim.run(260); sim.stick = d; sim.run(4 * F60);
    sim.press(b); sim.stick = 'n'; sim.crouch = false; sim.idleUntilDone();
    const got = sim.fired.length ? sim.fired[sim.fired.length - 1].n : null;
    r.heldOverFC[`crouch,${d}+${b}`] = { want, got, ok: got === want || sameMove(ms, got && M.resolveMoveKey(id, got), M.resolveMoveKey(id, want)) };
  }
  // Owner (phone): "can't attack while crouching, jumping, or moving forward/back". Every button
  // out of each of those states must start a move.
  r.stateAttack = {};
  for (const [label, stick, holdMs] of [['walk f', 'f', 400], ['walk b', 'b', 400], ['crouch d', 'd', 400], ['crouch d/b', 'd/b', 400], ['jump u', 'u', 260], ['jump u/f', 'u/f', 260]]) {
    for (const b of ['1', '2', '3', '4']) {
      const sim = new Sim(id); sim.run(10 * F60);
      sim.stick = stick; sim.run(holdMs);
      const st = sim.f.state;
      sim.press(b); sim.run(4 * F60);
      const got = sim.fired.length ? sim.fired[sim.fired.length - 1].n : null;
      sim.stick = 'n'; sim.idleUntilDone();
      r.stateAttack[`${label}+${b}`] = { state: st, got };
    }
  }
  // Owner: "the only combo that works is 1,2 or 2,1 ... 8 or 10 button strings, some 16-hit".
  // Every string of 4+ presses, tapped at a fixed touch rhythm (a tap every 120 / 180 / 250 ms,
  // regardless of the hits): how many of its presses played.
  r.longStrings = [];
  for (const n of Object.keys(ms._slots)) {
    const key = ms._slots[n]; if (!ms.moves[key]) continue;
    const p = parseNotation(n);
    if (p.why || p.steps.length < 4) continue;
    const row = { n, steps: p.steps.length, allStepsHaveMoves: p.steps.every(s => !!M.resolveMoveKey(id, s.upto)),
      // data with no active / recovery: the hit ends at its startup, so a 250 ms tap misses it
      timed: p.steps.every(s => { const m = M.getMove(id, s.upto); return !m || (Number.isFinite(m.active) && Number.isFinite(m.recovery)); }) };
    for (const rh of [120, 180, 250]) {
      const res = play(id, n, p, stanceSet, rh);
      const keys = res.fired.map(x => x && M.resolveMoveKey(id, x));
      let reached = 0;
      for (let i = 0; i < p.steps.length; i++) { const k = M.resolveMoveKey(id, p.steps[i].upto); if (!k || keys.includes(k) || res.fired.includes(p.steps[i].upto)) reached = i + 1; else break; }
      const last = res.fired[res.fired.length - 1];
      row['t' + rh] = (last === n || sameMove(ms, last && M.resolveMoveKey(id, last), key)) ? p.steps.length : Math.min(reached, p.steps.length - 1);
    }
    r.longStrings.push(row);
  }
  r.longStrings.sort((a, b) => b.steps - a.steps);
  r.stanceNeverEntered = [...r.stanceNeverEntered];
  return r;
}

const t0 = Date.now();
for (const id of ids) {
  try { report.fighters[id] = sweep(id); } catch (e) { report.fighters[id] = { error: String(e && e.stack || e) }; }
}
const tot = { fighters: 0, playable: 0, ok: 0, okFixedRhythm: 0, ambiguous: 0, unreachable: 0, unreachableResolverOk: 0, wrong: 0, notNotation: 0, shadowed: 0, stringStepsWithoutMove: 0, neutralFail: 0, systemFail: 0, stateAttackFail: 0, longStrings: 0, longOk120: 0, longOk180: 0, longOk250: 0, errors: 0 };
const rows = [];
for (const [id, r] of Object.entries(report.fighters)) {
  if (r.error) { tot.errors++; rows.push(`${id.padEnd(24)} ERROR ${r.error.split('\n')[0]}`); continue; }
  tot.fighters++; tot.playable += r.playable; tot.ok += r.ok; tot.okFixedRhythm += r.okFixedRhythm;
  tot.ambiguous += r.ambiguous.length; tot.unreachable += r.unreachable.filter(u => !u.resolverOk).length;
  tot.unreachableResolverOk += r.unreachable.filter(u => u.resolverOk).length; tot.wrong += r.wrong.length;
  tot.notNotation += r.notNotation; tot.shadowed += r.shadowed; tot.stringStepsWithoutMove += r.stringStepsWithoutMove;
  tot.neutralFail += Object.values(r.neutral).filter(x => !x.ok).length;
  tot.stateAttackFail += Object.values(r.stateAttack || {}).filter(x => !x.got).length;
  for (const L of r.longStrings || []) { tot.longStrings++; for (const rh of [120, 180, 250]) if (L['t' + rh] === L.steps) tot['longOk' + rh]++; }
  const sysOk = r.system.heatFresh === 'UB.2+3' && r.system.heatUrging === 'US.2+3' && /^RD?\.3\+4$/.test(r.system.rageDrive || '') // a fighter's own R.3+4 is its rage 3+4
    && Object.values(r.heldOverFC || {}).every(x => x.ok);
  if (!sysOk) tot.systemFail++;
  const L0 = (r.longStrings || [])[0];
  rows.push(`${id.padEnd(24)} ${String(r.ok).padStart(4)}/${String(r.playable).padEnd(4)} ok  amb ${String(r.ambiguous.length).padStart(2)}  unreach ${String(r.unreachable.length).padStart(3)}  wrong ${String(r.wrong.length).padStart(2)}  neutral ${Object.entries(r.neutral).map(([b, x]) => b + (x.ok ? '✓' : '✗')).join('')}  HEAT ${r.system.heatFresh}/${r.system.heatUrging} RD ${r.system.rageDrive}` +
    (L0 ? `  longest ${L0.steps}-press ${L0.t180}/${L0.steps}@180ms` : '  longest -') +
    (r.wrong.length && (VERBOSE || ONLY) ? '\n    wrong: ' + r.wrong.slice(0, VERBOSE ? 99 : 6).map(w => `${w.n} -> ${w.fired.join(' > ')}`).join(' | ') : ''));
}
report.totals = { ...tot, seconds: Math.round((Date.now() - t0) / 1000) };
if (!process.env.NODE_TEST_CONTEXT || VERBOSE || REPORT) { for (const row of rows) console.log(row); }
console.log('TOTALS', JSON.stringify(report.totals));
if (REPORT) writeFileSync(REPORT, JSON.stringify(report, (k, v) => (v instanceof Set ? [...v] : v), 1));

test('every fighter loads and sweeps', () => { assert.equal(tot.errors, 0, rows.filter(r => r.includes('ERROR')).join('\n')); });
test('neutral 1/2/3/4 fire exactly their own move on every fighter', () => { assert.equal(tot.neutralFail, 0); });
test('Soul Urge HEAT 2+3 = Urge Burst / Urge Smash, rage 3+4 = Rage Drive (system moves restored)', () => { assert.equal(tot.systemFail, 0); });
test('no notation resolves to a different move (resolver correctness over every playable notation)', () => {
  const ex = Object.entries(report.fighters).flatMap(([id, r]) => (r.wrong || []).slice(0, 3).map(w => `${id}: ${w.n} -> ${w.fired.join(' > ')}`));
  assert.equal(tot.wrong, 0, ex.slice(0, 40).join('\n'));
});

// ---- named regressions (owner: "pressing 1 gives a THROW instead of a jab") ---------------------
function ensure(id) { if (!M.getFighterMoveset(id)) { M.registerMoveset(id, JSON.parse(readFileSync(join(MS_DIR, `${id}.json`), 'utf8'))); ensureRageMoves(id, msApi); ensureUrgeMoves(id, msApi); } }
function pressSeq(id, seq) { // seq: [[stick, button, gapMs], ...]
  const sim = new Sim(id); sim.run(10 * F60);
  for (const [stick, btn, gap] of seq) { sim.stick = stick; sim.run(gap); sim.press(btn); }
  sim.stick = 'n'; sim.idleUntilDone();
  return sim.fired.map(x => x.n);
}
test('Pantera: 1 = the T8 Jab, never a throw; 1 then 3 never fires a merge-source T3 row (1~t3.king.N)', () => {
  ensure('pantera');
  assert.deepEqual(pressSeq('pantera', [['n', '1', 30]]), ['1']);
  const mv = M.getMove('pantera', '1');
  assert.ok(mv && !mv.isGrab && mv.move_class !== 'throw', `1 resolves to ${mv && mv.name}`);
  for (const gap of [60, 100, 160, 250]) {
    const f = pressSeq('pantera', [['n', '1', 30], ['n', '3', gap]]);
    assert.ok(f.every(n => !MERGE_KEY.test(n) && !/~/.test(n)), `1 then 3 after ${gap} ms fired ${f.join(' > ')}`);
    for (const n of f) { const m = M.getMove('pantera', n); assert.ok(m && !m.isGrab && m.move_class !== 'throw', `1 then 3 (${gap} ms) fired a throw: ${n}`); }
  }
});
test('duplicate physical input: the fighter\'s T7/T8 move beats a merged T3 row (Pantera qcf+1 = Pile Driver, not n,d,d/f,f+1 r282)', () => {
  ensure('pantera');
  const sim = new Sim('pantera'); sim.run(10 * F60);
  for (const d of ['d', 'd/f', 'f']) { sim.stick = d; sim.run(2 * F60); }
  sim.press('1'); sim.stick = 'n'; sim.idleUntilDone();
  const got = sim.fired.map(x => x.n);
  assert.deepEqual(got, ['qcf+1'], `qcf+1 fired ${got.join(' > ')}`);
  assert.ok(M.getMove('pantera', 'qcf+1').t8_id, 'qcf+1 is the T8 move');
});
test('crouched at d/f or d/b: the exact held spelling (D/F+1) beats FC.x when the moveset has it, else FC.x', () => {
  const bad = Object.entries(report.fighters).flatMap(([id, r]) => Object.entries(r.heldOverFC || {}).filter(([, v]) => !v.ok).map(([k, v]) => `${id} ${k}: want ${v.want} got ${v.got}`));
  const checked = Object.values(report.fighters).reduce((a, r) => a + Object.keys(r.heldOverFC || {}).length, 0);
  assert.ok(ONLY || checked > 0, 'no fighter had both held-diagonal and FC moves to check');
  assert.equal(bad.length, 0, bad.slice(0, 20).join('\n'));
});
test('no button press ever fires a merge-source key (\'1~t3.king\', \'b+3,2~t7.bryan.2\')', () => {
  const bad = Object.entries(report.fighters).flatMap(([id, r]) => (r.wrong || []).filter(w => /MERGE/.test(w.firedMove || '')).map(w => `${id}: ${w.n} -> ${w.fired.join(' > ')}`));
  assert.equal(bad.length, 0, bad.join('\n'));
});
test('every button comes out of walk forward / back, crouch and jump (owner: "can\'t attack while crouching, jumping, or moving")', () => {
  const bad = Object.entries(report.fighters).flatMap(([id, r]) => Object.entries(r.stateAttack || {}).filter(([, v]) => !v.got).map(([k, v]) => `${id} ${k} (state ${v.state}): nothing`));
  assert.equal(bad.length, 0, bad.slice(0, 30).join('\n'));
});
test('long strings (4 to 16 presses) play press by press at touch-tap rhythm (a tap every 120 / 180 / 250 ms)', () => {
  const miss = [];
  let all = 0, ok180 = 0;
  for (const [id, r] of Object.entries(report.fighters)) {
    const Ls = (r.longStrings || []).filter(L => L.allStepsHaveMoves && L.timed && !/[~:]/.test(L.n)); // '~' / ':' need their own timing
    all += Ls.length; ok180 += Ls.filter(L => L.t180 === L.steps).length;
    if (!Ls.length) continue;
    const top = Math.max(...Ls.map(L => L.steps));
    const best = Ls.filter(L => L.steps === top);
    if (!best.some(L => L.t180 === L.steps && L.t250 === L.steps)) miss.push(`${id}: longest ${best.map(L => `${L.n} (${L.t120}/${L.t180}/${L.t250} of ${L.steps})`).join(', ')}`);
  }
  assert.equal(miss.length, 0, 'longest string not completed at 180 and 250 ms:\n' + miss.join('\n'));
  assert.ok(ok180 / Math.max(1, all) >= 0.98, `only ${ok180}/${all} long strings complete at a 180 ms tap rhythm`);
});

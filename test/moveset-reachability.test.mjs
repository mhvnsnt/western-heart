// Moveset reachability (lane B, 2026-10-24; owner: "get all the combos and different moves working
// ... the different move inputs from the move lists aren't working ... random stuff is happening").
//
// For EVERY fighter in game/assets/movesets/index.json and EVERY playable notation in its notation
// table (ms._slots: the slots table + every move key that is itself a notation), press that
// notation the way a player does and assert that exactly its move plays:
//   - real code: the fight's own Fighter.tryAttack / _tryAttackFresh / _tickState (fighter.js,
//     imported headless; 'three' resolves to the vendored build) on top of the real TekkenBuffer
//     resolver (movesets.js) and the real input.js chord logic (InputManager._tekken), stepped at
//     the fight loop's FIXED_DT = 1/120 with a virtual clock;
//   - realistic timing: taps 2 frames, holds 10 frames (HOLD_FRAMES = 8), motions 2 frames per
//     step, a chord's two buttons 8 ms apart, every later string step pressed ~100 ms into the
//     hit before it (the rhythm a player follows) — and, reported, a steady 150 ms rhythm;
//   - state prefixes get the state the game gives them: FC = hold d past the 200 ms crouch,
//     WS = release that crouch, SS = sidestep, R./RD. = <=25% hp, UB./US. = Soul Urge,
//     BT./stance codes = that stance (game-reachable only when some move transitions into it).
// Per fighter: playable notations, resolved correctly, ambiguous (two moves on one physical input),
// unreachable (with the reason), wrong (a resolver bug: the gate). Data problems are listed, not
// fixed (moveset JSONs belong to the moveset lanes).
//
// Run: node --test test/moveset-reachability.test.mjs
//      node test/moveset-reachability.test.mjs [--report out.json] [--fighter skull] [--verbose]
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
const ENGINE_STATES = new Set(['FC', 'WS', 'SS', 'BT', 'R', 'RD', 'UB', 'US']);

/** notation -> { steps:[{text, prefix, sep}], why } ; why set = not a playable notation. */
const MERGE_KEY = /~[a-z][a-z0-9_-]*\./; // '1~t8.bryan', 'b+3,2~t7.bryan.2': merge-source move keys
function parseNotation(n) {
  if (MERGE_KEY.test(n)) return { why: 'merge-source key (not an input)' };
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
  const big = steps.find(s => (s.text.match(/[1-4]/g) || []).length > 2 && /[1-4]\+[1-4]\+[1-4]/.test(s.text));
  if (big) return { steps, why: `3+ button chord '${big.text}' (input.js forms two-button chords only)` };
  for (const s of steps) {
    const pm = RX_PFX.exec(s.text);
    s.prefix = pm ? pm[1] : ''; s.body = pm ? pm[2] : s.text;
  }
  return { steps };
}

/** Same physical input in WH (JF ':' / '~' read like ','; qcf = d,d/f,f; 'f,n,f' dash = 'f,f'). */
const EXPAND = { qcf: 'd,d/f,f', qcb: 'd,d/b,b', hcf: 'b,d/b,d,d/f,f', hcb: 'f,d/f,d,d/b,b' };
function physical(n) {
  const pm = RX_PFX.exec(n); const pre = pm ? pm[1] : ''; let b = pm ? pm[2] : n;
  b = b.replace(/[~:]/g, ',').replace(/\*/g, '').replace(/(^|,)(qcf|qcb|hcf|hcb)\+/g, (m, a, k) => `${a}${EXPAND[k]}+`)
    .replace(/(^|,)(qcf|qcb|hcf|hcb)(?=,|$)/g, (m, a, k) => a + EXPAND[k]);
  const t = b.split(','); const out = [];
  for (let i = 0; i < t.length; i++) {
    if (t[i] === 'n' && (!out.length || (out[out.length - 1] === t[i + 1]))) continue;
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
    _juggle: 0, _rageUsed: false, _queuedNext: null, _rageOn: false,
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
  /** One fixed tick: game.js order — stick, crouch, direction history, queued presses, update. */
  tick(buttons = []) {
    const f = this.f;
    f.setStick(this.stick);
    f.tryCrouch(this.crouch);
    f.tekken.noteDirection(this.stick, DT);
    for (const b of buttons) this.inp._tekken(b);
    for (const act of this.inp.consume()) {
      const ok = f.tryAttack(act); this._log();
      if (this.trace) console.log(`  t=${Math.round(this.t)} stick=${this.stick} press ${act} -> ${ok} now=${f.attackName} st=${f.state} stateT=${f.stateT.toFixed(3)} q=${f._queuedNext} path=${f.tekken._strPath}`);
    }
    f.stateT += DT;
    if (f.stun > 0) f.stun -= DT;
    if (f._risingT > 0) f._risingT -= DT;
    if (this.pinStance && f.state !== 'attack') { f.stance = this.pinStance; f.stanceT = 1; }
    else if (f.stanceT > 0) { f.stanceT -= DT; if (f.stanceT <= 0) f.stance = null; }
    f._tickState(); this._log();
    CLOCK += DT * 1000; this.t += DT * 1000;
  }
  /** Run `ms` of real time (whole ticks). */
  run(ms, buttons) { const n = Math.max(1, Math.round(ms / (DT * 1000))); for (let i = 0; i < n; i++) this.tick(i === 0 && buttons ? buttons : []); }
  press(btns, skewMs = 8) { // a chord: input.js sees the two buttons skewMs apart (inside CHORD_WINDOW_MS)
    const bs = btns.split('+');
    if (bs.length === 1) return this.tick(bs);
    this.tick([bs[0]]);
    for (let k = 1; k < bs.length; k++) { CLOCK += skewMs - DT * 1000; this.tick([bs[k]]); }
  }
  idleUntilDone(maxMs = 3000) { for (let t = 0; t < maxMs && (this.f.state === 'attack' || this.f._queuedNext); t += DT * 1000) this.tick(); }
}

/** Feed the stick for a press body ('d/f+1', 'D/F+1', 'f,F+2', 'qcf+1', '1'); returns the button(s). */
function stickFor(sim, body, crouched) {
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

/** Put the fighter into the state a prefix needs. Returns { ok, gameReachable, why }. */
function enterState(sim, prefix, stanceSet) {
  const toks = prefix.split('.').filter(Boolean);
  const f = sim.f; let crouched = false, rising = false;
  const notes = [];
  for (const t of toks) {
    if (t === 'FC') crouched = true;
    else if (t === 'WS') rising = true;
    else if (t === 'R' || t === 'RD') f.hp = 20;
    else if (t === 'UB') { f._urgeUsed = false; f._urgeOn = false; }
    else if (t === 'US') { f._urgeUsed = true; f._urgeOn = true; f._urgePips = 2; }
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

/** Press notation `n` on a fresh fighter; returns { fired:[...], final, sequence }. rhythm: 'hit' | ms */
function play(id, n, parsed, stanceSet, rhythm = 'hit') {
  const sim = new Sim(id);
  sim.trace = process.env.REACH_TRACE === n;
  sim.run(10 * F60);
  const st = enterState(sim, parsed.steps[0].prefix, stanceSet);
  if (!st.ok) return { fired: [], unreachable: 'could not enter the state' };
  let lastPressT = null;
  for (let i = 0; i < parsed.steps.length; i++) {
    const s = parsed.steps[i];
    if (i > 0) {
      // Next string step: a player presses in rhythm with the hits — ~100 ms into the previous hit
      // (or 150 ms after the previous press when it only typed a step / fixed-rhythm mode).
      const prev = parsed.steps[i - 1].upto; // the notation typed so far
      if (rhythm === 'hit') {
        if (M.resolveMoveKey(id, prev)) { // its move should be playing: press ~100 ms into it
          let waited = 0;
          const playing = () => sim.f.state === 'attack' && sim.f.attackName === prev && !sim.f._queuedNext;
          while (!playing() && waited < 1500) { sim.tick(); waited += DT * 1000; }
          while (playing() && sim.f.stateT < 0.1) sim.tick();
        }
        while (sim.t - lastPressT < 130) sim.tick(); // a string step with no move: next press 130+ ms later
      } else while (sim.t - lastPressT < rhythm) sim.tick();
    }
    // the stick for this step: neutral between steps unless the step carries a direction
    const body = i === 0 ? s.body : s.body; // mid-string prefixes ('3+4,SNE.2') are typed as the bare press
    if (i > 0 && !/[a-zA-Z]/.test(body.replace(/\*$/, ''))) sim.stick = 'n';
    const btn = stickFor(sim, body, i === 0 && st.crouched);
    if (!btn) return { fired: sim.fired.map(x => x.n), unreachable: `step '${s.text}' has no press` };
    lastPressT = sim.t;
    sim.press(btn);
    if (/[a-zA-Z]/.test(body) && !M.parseMotion(body)) { /* keep the direction a frame, then release */ sim.run(2 * F60); sim.stick = st.crouched && i === 0 ? 'd' : 'n'; }
  }
  sim.stick = 'n'; sim.crouch = false; sim.pinStance = null;
  sim.idleUntilDone();
  return { fired: sim.fired.map(x => x.n), gameReachable: st.gameReachable, stateWhy: st.why };
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
    neutral: {}, system: {}, showcase: {},
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
    if (last === n || sameMove(ms, gotKey, key)) {
      r.ok++;
      const fx = play(id, n, p, stanceSet, 150);
      const fl = fx.fired.length ? fx.fired[fx.fired.length - 1] : null;
      if (fl === n || sameMove(ms, fl && M.resolveMoveKey(id, fl), key)) r.okFixedRhythm++;
      if (!res.gameReachable) r.unreachable.push({ n, why: res.stateWhy, resolverOk: true });
    } else if (last && physical(last) === physical(n)) {
      r.ambiguous.push({ n, move: ms.moves[key].name, winner: last, winnerMove: ms.moves[gotKey] ? ms.moves[gotKey].name : null });
    } else if (res.unreachable) {
      r.unreachable.push({ n, why: res.unreachable });
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
  r.stanceNeverEntered = [...r.stanceNeverEntered];
  return r;
}

const t0 = Date.now();
for (const id of ids) {
  try { report.fighters[id] = sweep(id); } catch (e) { report.fighters[id] = { error: String(e && e.stack || e) }; }
}
const tot = { fighters: 0, playable: 0, ok: 0, okFixedRhythm: 0, ambiguous: 0, unreachable: 0, unreachableResolverOk: 0, wrong: 0, notNotation: 0, shadowed: 0, stringStepsWithoutMove: 0, neutralFail: 0, systemFail: 0, errors: 0 };
const rows = [];
for (const [id, r] of Object.entries(report.fighters)) {
  if (r.error) { tot.errors++; rows.push(`${id.padEnd(24)} ERROR ${r.error.split('\n')[0]}`); continue; }
  tot.fighters++; tot.playable += r.playable; tot.ok += r.ok; tot.okFixedRhythm += r.okFixedRhythm;
  tot.ambiguous += r.ambiguous.length; tot.unreachable += r.unreachable.filter(u => !u.resolverOk).length;
  tot.unreachableResolverOk += r.unreachable.filter(u => u.resolverOk).length; tot.wrong += r.wrong.length;
  tot.notNotation += r.notNotation; tot.shadowed += r.shadowed; tot.stringStepsWithoutMove += r.stringStepsWithoutMove;
  const nf = Object.values(r.neutral).filter(x => !x.ok).length; tot.neutralFail += nf;
  const sysOk = r.system.heatFresh === 'UB.2+3' && r.system.heatUrging === 'US.2+3' && r.system.rageDrive === 'RD.3+4';
  if (!sysOk) tot.systemFail++;
  rows.push(`${id.padEnd(24)} ${String(r.ok).padStart(4)}/${String(r.playable).padEnd(4)} ok  amb ${String(r.ambiguous.length).padStart(2)}  unreach ${String(r.unreachable.length).padStart(3)}  wrong ${String(r.wrong.length).padStart(2)}  neutral ${Object.entries(r.neutral).map(([b, x]) => b + (x.ok ? '✓' : '✗')).join('')}  HEAT ${r.system.heatFresh}/${r.system.heatUrging} RD ${r.system.rageDrive}` +
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

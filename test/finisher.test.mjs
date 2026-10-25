// Node test for game/js/finisher.js — no DOM, no three.js.
// Run: node test/finisher.test.mjs
// Exercises the gates, the synthesized per-fighter finisher blow
// (strongest-strike pattern from rage.js), the INTRO_OUTRO context
// save/restore, and the X-ray hook fallback when xray.js is absent.
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const here = dirname(fileURLToPath(import.meta.url));

// ---- localStorage shim (mirrors test/ranks.test.mjs) ----
const _ls = {};
globalThis.localStorage = {
  getItem: (k) => (_ls[k] ?? null),
  setItem: (k, v) => { _ls[k] = String(v); },
  removeItem: (k) => { delete _ls[k]; },
};

// ---- deterministic setTimeout shim: records, doesn't fire ----
const realSetTimeout = globalThis.setTimeout;
let scheduled = [];
globalThis.setTimeout = (fn, ms) => { scheduled.push({ fn, ms }); return scheduled.length; };
const runScheduled = () => { const q = scheduled; scheduled = []; for (const s of q) s.fn(); };

const fin = await import(join(here, '..', 'game', 'js', 'finisher.js'));
const gate = await import(join(here, '..', 'game', 'js', 'anim-gate.js'));

let pass = 0, fail = 0;
function ok(cond, name) {
  if (cond) { pass++; }
  else { fail++; console.log('FAIL -', name); }
}

// ---- fixtures ----
function mkGame(over = {}) {
  const p1 = Object.assign({
    dead: false, soulMeter: 1, soulMeterMax: 1,
    tryAttack: (b) => { p1._attacked = b; },
    playPose: (p) => { p1._posed = p; },
  }, over.p1 || {});
  const p2 = Object.assign({ dead: false, hp: 20, maxHp: 100 }, over.p2 || {});
  const ui = { banner: (t) => { ui._banner = t; } };
  return { p1, p2, ui };
}
const DEF = { name: 'TEST', beats: [{ btn: '1', dur: 0.5 }], meterCost: 1.0, victimHpGate: 0.25 };

// ---- gatesOpen ----
ok(fin.gatesOpen(mkGame(), DEF) === true, 'gates open: meter full + victim < 25%');
ok(fin.gatesOpen(mkGame({ p1: { soulMeter: 0.5 } }), DEF) === false, 'gates closed: meter not full');
ok(fin.gatesOpen(mkGame({ p2: { hp: 30 } }), DEF) === false, 'gates closed: victim above 25%');
ok(fin.gatesOpen(mkGame({ p2: { dead: true, hp: 0 } }), DEF) === false, 'gates closed: victim dead');
ok(fin.gatesOpen(mkGame({ p1: { dead: true } }), DEF) === false, 'gates closed: attacker dead');

// ---- ensureFinisherMoves: strongest strike, grabs excluded ----
const stableMs = {
  moves: {
    jab:   { name: 'jab', damage: 10, move_class: 'strike', limb: 'armL', input_slots: ['1'] },
    throw: { name: 'throw', damage: 50, isGrab: true, limb: 'armR' },
    hay:   { name: 'haymaker', damage: 25, move_class: 'strike', limb: 'legR', input_slots: ['4'] },
  },
};
const msApi = { playedMoveset: (id) => stableMs };
const syn = fin.ensureFinisherMoves('pantera', msApi);
ok(!!syn, 'ensureFinisherMoves returns a def');
ok(syn.name.includes('HAYMAKER'), 'finisher blow = strongest strike (grab excluded)');
ok(syn.source.move === 'hay', 'source move recorded');
ok(syn.beats.length === 1 && syn.beats[0].btn === '4', 'blow beat fires the heavy button');
ok(syn.beats[0].xray && syn.beats[0].xray.limb === 'legR', 'killing-blow beat carries the xray flash');
ok(syn.beats[0].xray.power >= 0.3 && syn.beats[0].xray.power <= 1, 'xray power clamped 0.3..1');

// idempotent: same object back, safe to call every match
const syn2 = fin.ensureFinisherMoves('pantera', msApi);
ok(syn2 === syn, 'ensureFinisherMoves idempotent (cached on moveset)');

// null-safe
ok(fin.ensureFinisherMoves('x', null) === null, 'no msApi -> null');
ok(fin.ensureFinisherMoves('x', { playedMoveset: () => null }) === null, 'no moveset -> null');

// fallback when the fighter has no moves at all
const empty = fin.ensureFinisherMoves('z', { playedMoveset: () => ({ moves: {} }) });
ok(!!empty && empty.beats[0].xray.power === 0.45, 'fallback base when moveset empty');

// ---- tryFinisher: beats, lock, banner, INTRO_OUTRO context save/restore ----
scheduled = [];
gate.setAnimContext('FIGHT');
const g = mkGame();
const fired = fin.tryFinisher(g, { name: 'BEAT', beats: [{ btn: '2', dur: 0.5, xray: { limb: 'armR', power: 0.8 } }], meterCost: 1.0, victimHpGate: 0.25 });
ok(fired === true, 'tryFinisher fires when gates open');
ok(g.p1.soulMeter === 0, 'finisher spends the Nine-Soul meter');
ok(g.p2._finisherLock === true, 'victim rooted during beats');
ok(g.ui._banner === 'FINISHER — BEAT', 'banner announced');
ok(gate.getAnimContext() === 'INTRO_OUTRO', 'beats run in INTRO_OUTRO context');
ok(scheduled.length === 2, 'beat + release scheduled');

runScheduled(); // beat fires, then release: lock off + context restored
ok(g.p1._attacked === '2', 'beat played as attack');
ok(g.p2._finisherLock === false, 'victim lock released after beats');
ok(gate.getAnimContext() === 'FIGHT', 'anim context restored to FIGHT after finisher');

// tryFinisher refuses when gates closed
ok(fin.tryFinisher(mkGame({ p2: { hp: 90 } }), DEF) === false, 'no fire when gates closed');
ok(fin.tryFinisher(mkGame(), null) === false, 'no fire without a def');

// ---- getCustomFinisher ----
ok(fin.getCustomFinisher() === null, 'no authored finisher -> null');
_ls.wh_create_fighter_v1 = JSON.stringify({ finisher: { name: 'MINE', beats: [{ btn: '1', dur: 0.5 }] } });
const custom = fin.getCustomFinisher();
ok(custom && custom.name === 'MINE', 'suite-authored finisher read from localStorage');
delete _ls.wh_create_fighter_v1;

// ---- X-ray hook: must never throw when xray.js is absent (parallel module) ----
globalThis.setTimeout = realSetTimeout; // back to real timers for the async import
scheduled = [];
const g2 = mkGame();
fin.tryFinisher(g2, { name: 'X', beats: [{ btn: '1', dur: 0.05, xray: { limb: 'armR', power: 1 } }], meterCost: 1.0, victimHpGate: 0.25 });
await new Promise((r) => realSetTimeout(r, 450)); // beat fires, import rejects, release restores
ok(g2.p1._attacked === '1', 'finisher completes without xray.js present');
ok(gate.getAnimContext() === 'FIGHT', 'context restored even with xray hook active');

console.log(`\nfinisher.test.mjs: ${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);

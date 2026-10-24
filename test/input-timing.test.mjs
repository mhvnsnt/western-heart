/* input-timing.test.mjs — input TIMING regression (owner 2026-10-24: "press buttons and just
 * random stuff is happening"). Node, no DOM.
 *
 * Drives the REAL InputManager keyboard handlers (game/js/input.js) and the REAL TekkenBuffer
 * (game/js/movesets.js) with SIMULATED time: a display rAF loop feeds a fixed-step accumulator
 * exactly like game.js _loop (FIXED_DT and _tekkenDir are read from game.js itself), key events
 * land at human timings in ms, and performance.now / setTimeout run on the simulated clock.
 * test/input-determinism.test.mjs feeds history STEPS; this test feeds TIME, which is what it
 * takes to catch: the 140 ms chord window (1,2 -> 1+2, 1,3 -> throw) and the 120 Hz direction
 * history whose windows counted 60 fps frames (qcf / f,f / held spellings at half length).
 * Every scenario runs at two display rates and three tick rates (game.js FIXED_DT, 1/60, 1/240),
 * so the timing must hold if FIXED_DT changes.
 *
 * Run: node --test test/input-timing.test.mjs
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const JS = join(ROOT, 'game', 'js');
const MS_DIR = join(ROOT, 'game', 'assets', 'movesets');

// ---- browser shims: only what InputManager / movesets touch ----
const _ls = {};
globalThis.localStorage = {
  getItem: (k) => (_ls[k] ?? null),
  setItem: (k, v) => { _ls[k] = String(v); },
  removeItem: (k) => { delete _ls[k]; },
};
const listeners = {};
globalThis.window = globalThis.window || {};
globalThis.window.addEventListener = (type, fn) => { (listeners[type] = listeners[type] || []).push(fn); };

const { InputManager, CHORD_WINDOW_MS } = await import(join(JS, 'input.js'));
const M = await import(join(JS, 'movesets.js'));
M.setInputTables(JSON.parse(readFileSync(join(MS_DIR, 't3_input_tables.json'), 'utf8')));
for (const id of ['pantera', 'skull', 'jin_soul']) {
  M.registerMoveset(id, JSON.parse(readFileSync(join(MS_DIR, `${id}.json`), 'utf8')));
}

// ---- the game loop's own pieces, read from game.js (no three.js import) ----
const gameSrc = readFileSync(join(JS, 'game.js'), 'utf8');
const FIXED_DT = Function(`return (${/const FIXED_DT\s*=\s*([^;]+);/.exec(gameSrc)[1]});`)();
const tdm = /\n\s*_tekkenDir\(inp, facing\) \{\n([\s\S]*?)\n  \}\n/.exec(gameSrc);
const tekkenDir = tdm ? new Function('inp', 'facing', tdm[1]) : null;

// ---- simulated clock: performance.now + setTimeout/clearTimeout (input.js 200 ms tap/hold) ----
let NOW = 0, timers = [], timerId = 0;
const realNow = performance.now, realST = globalThis.setTimeout, realCT = globalThis.clearTimeout;
function simClock(on) {
  if (on) {
    performance.now = () => NOW;
    globalThis.setTimeout = (fn, ms) => { timers.push({ id: ++timerId, due: NOW + (ms || 0), fn }); return timerId; };
    globalThis.clearTimeout = (id) => { timers = timers.filter(t => t.id !== id); };
  } else {
    performance.now = realNow; globalThis.setTimeout = realST; globalThis.clearTimeout = realCT;
  }
}
function advance(t) {
  for (;;) {
    timers.sort((a, b) => a.due - b.due);
    if (!timers.length || timers[0].due > t) break;
    const tm = timers.shift(); NOW = tm.due; tm.fn();
  }
  NOW = t;
}

const CODE = { d: 'KeyS', u: 'KeyW', f: 'KeyD', b: 'KeyA', 1: 'Digit1', 2: 'Digit2', 3: 'Digit3', 4: 'Digit4' };
const LIMB = /^[1-4](\+[1-4])*$/;
const MOVE_BUSY_MS = 450; // a started move keeps the fighter busy (strings buffer, other presses drop)

/**
 * Play key events [[ms, 'down'|'up', key]] (key: d/u/f/b/1-4, facing right) through a display at
 * `hz` feeding the fixed-step loop at `dt` s, like game.js: each step reads the stick with
 * _tekkenDir, calls tekken.noteDirection(stick, dt), then resolves the queued presses the way
 * Fighter.tryAttack does (string continuation while a move plays, chord upgrade of a single that
 * just started, otherwise pressButton / pressChord with the crouch context).
 * Returns { queue: InputManager actions in order, fired: notations started }.
 */
function play(fighterId, events, { hz = 60, dt = FIXED_DT } = {}) {
  for (const k of Object.keys(listeners)) if (k !== 'storage') listeners[k] = [];
  timers = []; NOW = 0;
  simClock(true);
  try {
    const inp = new InputManager();
    inp._bindKeyboard();
    inp.enable(true);
    const buf = new M.TekkenBuffer(fighterId);
    const queue = [], fired = [];
    let moveEnd = -1, last = null;
    const t0 = 1000; // the round has been running for a second (neutral history)
    const evs = events.map(([t, kind, key]) => [t0 + t, kind, CODE[key]]).sort((a, b) => a[0] - b[0]);
    const end = evs[evs.length - 1][0] + 300;
    const frame = 1000 / hz;
    let acc = 0, ei = 0;
    const step = () => {
      const stick = tekkenDir(inp, 1);
      buf.noteDirection(stick, dt);
      for (const act of inp.consume()) {
        queue.push(act);
        if (!LIMB.test(act)) continue; // sidesteps etc. are not part of this check
        const inMove = NOW < moveEnd;
        const ctx = { crouching: !!(inp.down && !inp.up), inMove };
        let n = inMove ? buf.continuation(act) : null;
        if (n) buf.recordExplicit(n);
        else {
          const upgrade = inMove && act.includes('+') && last && /^[1-4]$/.test(last.input) &&
            act.split('+').includes(last.input) && NOW - last.t <= 140;
          if (inMove && !upgrade) continue; // fighter busy: press dropped
          if (upgrade) { buf.lastMove = last.base; fired.pop(); }
          const base = buf.lastMove;
          n = act.includes('+') ? buf.pressChord(act, ctx) : (buf.pressButton(act, ctx) || act);
          if (!n) continue;
          last = { input: act, t: NOW, base };
        }
        fired.push(n); moveEnd = NOW + MOVE_BUSY_MS;
      }
    };
    for (let T = 0; T <= end; T += frame) {
      // input events that happened since the last rAF; each handler runs at its own time
      while (ei < evs.length && evs[ei][0] <= T) {
        const [t, kind, code] = evs[ei++];
        advance(t);
        for (const fn of listeners[kind === 'down' ? 'keydown' : 'keyup'] || []) fn({ code, preventDefault() {} });
      }
      advance(T);
      acc += frame / 1000;
      while (acc >= dt) { step(); acc -= dt; }
    }
    return { queue, fired };
  } finally {
    simClock(false);
  }
}

const RATES = [
  { hz: 60, dt: FIXED_DT }, { hz: 144, dt: FIXED_DT },
  { hz: 60, dt: 1 / 60 }, { hz: 144, dt: 1 / 60 },
  { hz: 60, dt: 1 / 240 }, { hz: 144, dt: 1 / 240 },
];
const rateName = (r) => `${r.hz} Hz display, tick 1/${Math.round(1 / r.dt)}`;
const motionOf = (n) => { const mo = n && M.parseMotion(n); return mo ? `${mo.dirs.filter(d => d !== 'n').join(',')}+${mo.btn}` : null; };
const lastFired = (r) => r.fired[r.fired.length - 1] || null;
const show = (r) => `queue=${JSON.stringify(r.queue)} fired=${JSON.stringify(r.fired)}`;

test('wiring: game.js feeds the tick length to the direction history; chord window is 2-3 frames', () => {
  assert.ok(tekkenDir, 'game.js _tekkenDir(inp, facing) not found');
  assert.ok(FIXED_DT > 0 && FIXED_DT <= 1 / 30, `FIXED_DT=${FIXED_DT}`);
  assert.match(gameSrc, /tekken\.noteDirection\(\s*stick\s*,\s*dt\s*\)/,
    'game.js must call noteDirection(stick, dt): the history windows are 60 Hz frames of TIME');
  assert.ok(CHORD_WINDOW_MS >= 33 && CHORD_WINDOW_MS <= 50, `CHORD_WINDOW_MS=${CHORD_WINDOW_MS}`);
});

test('qcf+1 done in 250-350 ms resolves as the motion move (pantera Pile Driver)', () => {
  // keyboard qcf: d, then f joins (d/f), then d lets go (f), then 1 with f still held
  const shapes = [[0, 100, 210, 250], [0, 110, 220, 300], [0, 120, 240, 350]];
  for (const r of RATES) for (const [d, df, f, p] of shapes) {
    const res = play('pantera', [[d, 'down', 'd'], [df, 'down', 'f'], [f, 'up', 'd'], [p, 'down', '1'], [p + 60, 'up', 'f']], r);
    assert.equal(motionOf(lastFired(res)), 'd,d/f,f+1', `qcf+1 in ${p} ms @ ${rateName(r)}: ${show(res)}`);
  }
});

test('a slow qcf (~700 ms, d left > 25 frames before the press) is NOT the motion', () => {
  for (const r of RATES) {
    const res = play('pantera', [[0, 'down', 'd'], [200, 'down', 'f'], [500, 'up', 'd'], [700, 'down', '1']], r);
    assert.notEqual(motionOf(lastFired(res)), 'd,d/f,f+1', `slow qcf @ ${rateName(r)}: ${show(res)}`);
    assert.equal(lastFired(res), 'f+1', `slow qcf -> f+1 @ ${rateName(r)}: ${show(res)}`);
  }
});

test('f,f+2 within ~250 ms is the dash move (pantera f,F+2 Beast Elbow)', () => {
  const shapes = [[0, 60, 120, 200], [0, 70, 140, 250]];
  for (const r of RATES) for (const [f1, up, f2, p] of shapes) {
    const res = play('pantera', [[f1, 'down', 'f'], [up, 'up', 'f'], [f2, 'down', 'f'], [p, 'down', '2']], r);
    assert.equal(motionOf(lastFired(res)), 'f,f+2', `f,f+2 in ${p} ms @ ${rateName(r)}: ${show(res)}`);
  }
});

test('f, then f again 600 ms later + 2 is a plain f+2 (dash window is bounded in time)', () => {
  for (const r of RATES) {
    const res = play('pantera', [[0, 'down', 'f'], [70, 'up', 'f'], [640, 'down', 'f'], [750, 'down', '2']], r);
    assert.equal(lastFired(res), 'f+2', `late second f @ ${rateName(r)}: ${show(res)}`);
  }
});

test('neutral-ending motions are timed too: f,f,n,1+2 right away is the motion, 1.4 s later a plain 1+2', () => {
  const ff = [[0, 'down', 'f'], [60, 'up', 'f'], [120, 'down', 'f'], [180, 'up', 'f']];
  for (const r of RATES) {
    const now = play('pantera', [...ff, [240, 'down', '1'], [248, 'down', '2']], r);
    assert.equal(lastFired(now), 'f,f,n,1+2', `f,f,n,1+2 @ ${rateName(r)}: ${show(now)}`);
    const late = play('pantera', [...ff, [1600, 'down', '1'], [1608, 'down', '2']], r);
    assert.deepEqual(late.fired, ['1+2'], `stale f,f then 1+2 @ ${rateName(r)}: ${show(late)}`);
  }
});

test('1 then 2 pressed 80-120 ms apart is the string 1,2, never the chord 1+2', () => {
  for (const r of RATES) for (const gap of [80, 100, 120]) {
    const res = play('pantera', [[0, 'down', '1'], [gap, 'down', '2']], r);
    assert.deepEqual(res.queue, ['1', '2'], `1,2 (${gap} ms) @ ${rateName(r)}: ${show(res)}`);
    assert.deepEqual(res.fired, ['1', '1,2'], `1,2 (${gap} ms) @ ${rateName(r)}: ${show(res)}`);
  }
});

test('fast 1,3 / 2,4 / 3,4 (80-120 ms) stay two presses: no throw, no 3+4', () => {
  for (const r of RATES.slice(0, 2)) for (const [a, b] of [['1', '3'], ['2', '4'], ['3', '4'], ['2', '1']]) for (const gap of [80, 120]) {
    const res = play('pantera', [[0, 'down', a], [gap, 'down', b]], r);
    assert.deepEqual(res.queue, [a, b], `${a},${b} (${gap} ms) @ ${rateName(r)}: ${show(res)}`);
  }
});

test('a true simultaneous press (0-16 ms apart, and 2-frame leniency) is the chord', () => {
  for (const r of RATES) for (const gap of [0, 8, 16, 33]) {
    const res = play('pantera', [[0, 'down', '1'], [gap, 'down', '2']], r);
    assert.ok(res.queue.includes('1+2') && !res.queue.includes('2'), `1+2 (${gap} ms) queue @ ${rateName(r)}: ${show(res)}`);
    assert.deepEqual(res.fired, ['1+2'], `1+2 (${gap} ms) @ ${rateName(r)}: ${show(res)}`);
    const thr = play('pantera', [[0, 'down', '1'], [gap, 'down', '3']], r);
    assert.ok(thr.queue.includes('1+3'), `1+3 (${gap} ms) @ ${rateName(r)}: ${show(thr)}`);
  }
});

test('holding d/f ~200 ms then pressing reads the HELD spelling; a quick d/f tap reads the tap one', () => {
  const heldDF1 = M.resolveMoveKey('skull', 'D/F+1'), tapDF1 = M.resolveMoveKey('skull', 'd/f+1');
  const heldDB2 = M.resolveMoveKey('jin_soul', 'D/B+2'), tapDB2 = M.resolveMoveKey('jin_soul', 'd/b+2');
  assert.ok(heldDF1 && tapDF1 && heldDF1 !== tapDF1 && heldDB2 && tapDB2 && heldDB2 !== tapDB2, 'fixture movesets changed');
  for (const r of RATES) {
    const held = play('skull', [[0, 'down', 'd'], [0, 'down', 'f'], [210, 'down', '1']], r);
    assert.equal(M.resolveMoveKey('skull', lastFired(held)), heldDF1, `skull hold d/f 210 ms +1 @ ${rateName(r)}: ${show(held)}`);
    const tap = play('skull', [[0, 'down', 'd'], [0, 'down', 'f'], [70, 'down', '1']], r);
    assert.equal(M.resolveMoveKey('skull', lastFired(tap)), tapDF1, `skull d/f+1 tapped (70 ms) @ ${rateName(r)}: ${show(tap)}`);
    const heldB = play('jin_soul', [[0, 'down', 'd'], [0, 'down', 'b'], [210, 'down', '2']], r);
    assert.equal(M.resolveMoveKey('jin_soul', lastFired(heldB)), heldDB2, `jin_soul hold d/b 210 ms +2 @ ${rateName(r)}: ${show(heldB)}`);
    const tapB = play('jin_soul', [[0, 'down', 'd'], [0, 'down', 'b'], [70, 'down', '2']], r);
    assert.equal(M.resolveMoveKey('jin_soul', lastFired(tapB)), tapDB2, `jin_soul d/b+2 tapped (70 ms) @ ${rateName(r)}: ${show(tapB)}`);
  }
});

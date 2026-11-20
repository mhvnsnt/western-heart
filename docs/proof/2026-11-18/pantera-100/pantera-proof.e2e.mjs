// Lane D — Pantera live proof capture (main 43d29bf, local serve of the main checkout).
// Method: repo's own e2e pattern (test/e2e/combat-inputs.e2e.mjs) + Nov 3 canvas-read
// method (docs/proof/2026-11-03/pantera-wiring/VIDEO-README-2026-11-03.md):
// game paused, hand-stepped _update at 60 Hz, frames read from the renderer's own
// canvas (arena.render() + toDataURL in the same task — compositor screenshots
// effectively never present on this VM).
// BASE is the LOCAL serve (127.0.0.1:8811) because headless Chromium in this
// environment cannot reach the live site: net::ERR_TUNNEL_CONNECTION_FAILED for
// all https via the egress proxy (see CHECKPOINT.md step 3). The served tree is
// main 43d29bf, verified byte-identical to the live build's fighter.js.
// Run: node pantera-proof.e2e.mjs [shotsDir]
import { chromium } from 'playwright-core';
import fs from 'node:fs';
const BASE = process.env.WH_URL || 'http://127.0.0.1:8811';
const SHOTS = process.argv[2] || 'pantera-proof-shots';
const P1 = 'pantera', OPP = 'demonio'; // Demonio: repo's play-verify pair with Pantera; demonio.glb is SHELL-BUNDLED (local-first). Zen is NOT bundled: its first candidate is the remote Worker, which headless Chromium cannot reach (proxy), and the 45 s stall abort fires before the local candidate is tried — fight load retries forever (see CHECKPOINT.md).
fs.mkdirSync(SHOTS, { recursive: true });
const log = { p1: P1, p2: OPP, base: BASE, commit: '43d29bf6bcc6919aff35c025f01e0a7e9aea69c5',
  note: 'local serve of main 43d29bf (live-site capture blocked: headless Chromium ERR_TUNNEL_CONNECTION_FAILED via egress proxy); opponent Demonio, not Zen: Zen is not shell-bundled so its load tries the unreachable remote Worker first and the 45 s stall abort fires before the local copy is tried (fight load retries forever); Demonio is the repo play-verify pair with Pantera and loads local-first',
  phases: [] };
const fails = []; let passes = 0;
const ok = (c, m) => { if (c) { passes++; console.log('PASS', m); } else { fails.push(m); console.log('FAIL', m); } };
const b = await chromium.launch({ executablePath: process.env.HOME + '/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome',
  // Nov 3 method: Mesa/llvmpipe via --use-angle=gl under Xvfb (run under xvfb-run -a).
  // SwiftShader costs 40-160 s per presented frame on this VM and the fight load stalls.
  args: ['--use-gl=angle', '--use-angle=gl', '--ignore-gpu-blocklist', '--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 960, height: 720 } });
p.on('pageerror', (e) => { fails.push('pageerror ' + String(e).slice(0, 200)); console.log('PAGEERROR', String(e).slice(0, 200)); });
const t0 = Date.now();
const prog = (m) => { const line = `[${((Date.now() - t0) / 1000).toFixed(0)}s] ${m}`; fs.appendFileSync('capture-progress.log', line + '\n'); console.log(line); };
await p.goto(BASE + '/game/index.html', { timeout: 120000 });
prog('page loaded');
await p.waitForFunction(() => window.__startFight, null, { timeout: 300000 });
prog('__startFight ready');
await p.evaluate(([a, c]) => window.__startFight(a, c, {}), [P1, OPP]);
prog('__startFight called, waiting for fight state');
// Hard guard: the fight-load recovery can reload the page on a failed model
// load, which can keep a bare waitForFunction waiting past its timeout.
await Promise.race([
  p.waitForFunction(() => { const g = window.__game; return g && g.roundState === 'fight' && g.p1 && g.p2; }, null, { timeout: 300000, polling: 500 }),
  new Promise((_, rej) => setTimeout(() => rej(new Error('FIGHT-WAIT hard timeout 420s: roundState never reached fight')), 420000)),
]);
console.log('FIGHT in', ((Date.now() - t0) / 1000).toFixed(1), 's');
prog('FIGHT state reached');
await p.evaluate(() => {
  const g = window.__game; g.running = false; g.ai.update = () => {}; g.timer = 9999; g._hitStop = 0;
  window.__vt = 1e6; g.input._pressT = () => window.__vt;
  const KEY = { 1: 'Digit1', 2: 'Digit2', 3: 'Digit3', 4: 'Digit4', f: 'KeyD', b: 'KeyA', u: 'KeyW', d: 'KeyS' };
  window.__key = (codes, type = 'keydown') => { for (const c of [].concat(codes)) window.dispatchEvent(new KeyboardEvent(type, { code: KEY[c] || c, key: c, bubbles: true })); };
  const s = (f) => ({ st: f.state, an: f.attackName, bt: !!f._bt, clip: f._t3current ? f._t3current.getClip().name : null, x: +f.root.position.x.toFixed(2), hp: f.hp });
  window.__snap = () => ({ p1: s(g.p1), p2: s(g.p2), rs: g.roundState });
  window.__step = (n) => { const out = []; for (let i = 0; i < n; i++) { window.__vt += 1000 / 60;
    if (g._hitStop > 0) g._hitStop -= 1 / 60; else g._update(1 / 60); out.push(window.__snap()); } return out; };
  window.__reset = (gap) => {
    for (const f of [g.p1, g.p2]) { f.hp = f.maxHp || f.hp; f._enter('idle'); f.attack = null; f.attackName = null; f._throwPair = null;
      f.lockT = 0; f.lockMove = null; f.tekken.lastMove = null; f.tekken._strPath = null; f._stringGraceUntil = 0; f._queuedNext = null; f._queuedAfter = []; f._urgeOn = false; f._urgeT = 0;
      f.vx = 0; f.stun = 0; f.invuln = 0; f._pressBuf && f._pressBuf.clear(); }
    g.p1.root.position.set(-gap / 2, 0, 0); g.p2.root.position.set(gap / 2, 0, 0);
    g.roundState = 'fight'; g.timer = 9999;
    g.input._queue.length = 0; g.p1.facing = 1; window.__step(30); window.__vt += 1000; };
});
// Frame grab from the renderer canvas (Nov 3 method). Free camera framed on both fighters.
let frameNo = 0;
async function grab(tag) {
  const data = await p.evaluate(() => {
    const g = window.__game, a = g.arena, c = a.camera, m = (g.p1.root.position.x + g.p2.root.position.x) / 2;
    a.setFreeCamera(true);
    c.position.set(m, 2.9, 3.6); c.lookAt(m, 0.9, 0); c.updateMatrixWorld(); a.render();
    return a.renderer.domElement.toDataURL('image/png');
  });
  const name = `frame-${String(++frameNo).padStart(3, '0')}-${tag}.png`;
  fs.writeFileSync(`${SHOTS}/${name}`, Buffer.from(data.split(',')[1], 'base64'));
  return name;
}
async function phase(name, fn) {
  const ph = { phase: name, frames: [], shots: [] };
  log.phases.push(ph);
  const t = Date.now();
  prog(`phase START ${name}`);
  await fn(ph);
  ph.secs = +((Date.now() - t) / 1000).toFixed(1);
  prog(`phase END ${name}: ${ph.frames.length} logged frames, ${ph.shots.length} shots, ${ph.secs}s wall`);
  console.log(`-- ${name}: ${ph.frames.length} logged frames, ${ph.shots.length} shots, ${ph.secs}s wall`);
  return ph;
}
const snap = () => p.evaluate(() => window.__snap());
const step = (n) => p.evaluate((n) => window.__step(n), n);
// Press one hit: '1', '1+3', 'f+2', 'd/f+1'. Directions held 15 frames, buttons pressed, all released.
const press = (hit, gap = 1.2, reset = true, after = 9) => p.evaluate(([hit, gap, reset, after]) => {
  if (reset) window.__reset(gap);
  const m = /^(?:([udfbn/]+)\+)?([1234](?:\+[1234])*)$/.exec(hit); if (!m) return null;
  const dirs = m[1] ? m[1].split('/').filter((d) => d !== 'n') : []; const btns = m[2].split('+');
  let fr = [];
  if (dirs.length) { window.__key(dirs); fr = fr.concat(window.__step(15)); }
  window.__key(btns); fr = fr.concat(window.__step(1)); window.__key(btns, 'keyup'); window.__key(dirs, 'keyup');
  return fr.concat(window.__step(after));
}, [hit, gap, reset, after]);
const seq = (frames) => { const o = []; let last = null; for (const f of frames) { const s = f.p1; if (s.st === 'attack' && s.an) { if (s.an !== last) o.push(s.an); last = s.an; } else last = null; } return o; };
// Press a multi-hit string: hits pressed one at a time, reset only before the first.
const pressSeq = async (hits, gap = 1.2, afterLast = 9) => {
  let fr = [];
  for (let i = 0; i < hits.length; i++) {
    const r = await press(hits[i], gap, i === 0, i === hits.length - 1 ? afterLast : 9);
    if (!r) return null;
    fr = fr.concat(r);
  }
  return fr;
};

// ---- Phase 1: idle baseline
await phase('idle-pose', async (ph) => {
  await p.evaluate(() => window.__reset(1.6));
  ph.frames = await step(12);
  ph.shots.push(await grab('idle'));
  ok(ph.frames.every((f) => f.p1.st === 'idle'), 'idle holds stance');
});

// ---- Phase 2: KBD loop (b,b -> d/b cancel, 3 cycles)
await phase('kbd-loop', async (ph) => {
  await p.evaluate(() => window.__reset(1.6));
  const xs = [];
  for (let c = 0; c < 3; c++) {
    // b,b backdash
    await p.evaluate(() => { window.__key(['b']); window.__step(2); window.__key(['b'], 'keyup'); window.__step(2); window.__key(['b']); window.__step(1); window.__key(['b'], 'keyup'); });
    let fr = await step(4);
    ph.frames.push(...fr);
    const mid = await snap();
    if (c === 0) { ph.shots.push(await grab('kbd-backdash')); ok(mid.p1.st === 'tekdash', `KBD cycle 1: backdash state=${mid.p1.st}`); }
    // d/b cancel into crouch
    await p.evaluate(() => { window.__key(['d', 'b']); window.__step(1); window.__key(['d', 'b'], 'keyup'); });
    fr = await step(6);
    ph.frames.push(...fr);
    const s2 = await snap();
    xs.push(s2.p1.x);
    if (c === 0) ok(s2.p1.st === 'crouch', `KBD cycle 1: d/b cancels to crouch (state=${s2.p1.st})`);
  }
  ph.xs = xs;
  ok(xs[2] < xs[0] - 0.01, `KBD travels back across cycles (x ${xs.join(' -> ')})`);
});

// ---- Phase 3: f,f dash
await phase('dash-ff', async (ph) => {
  await p.evaluate(() => window.__reset(1.6));
  await p.evaluate(() => { window.__key(['f']); window.__step(2); window.__key(['f'], 'keyup'); window.__step(2); window.__key(['f']); window.__step(1); window.__key(['f'], 'keyup'); });
  ph.frames = await step(15);
  const mid = await snap();
  ph.shots.push(await grab('dash-mid'));
  ok(mid.p1.st === 'tekdash', `f,f dash state=${mid.p1.st}`);
  const end = await step(25);
  ph.frames.push(...end);
  const e = await snap();
  ph.travel = +(e.p1.x - (-0.8)).toFixed(2);
  ok(e.p1.st === 'idle' && e.p1.x > 0.5, `dash ends idle, travelled forward (x=${e.p1.x})`);
});

// ---- Phase 4: run (f,f hold f) + run attack WR 4
await phase('run', async (ph) => {
  await p.evaluate(() => window.__reset(2.5));
  await p.evaluate(() => { window.__key(['f']); window.__step(2); window.__key(['f'], 'keyup'); window.__step(2); window.__key(['f']); });
  ph.frames = await step(20); // held f through dash frame 12 -> run
  const mid = await snap();
  ph.shots.push(await grab('run-mid'));
  ph.runState = mid.p1.st;
  ok(/run/i.test(mid.p1.st), `run state after f,f hold f: ${mid.p1.st}`);
  // run attack: press 4 while running (f still held)
  await p.evaluate(() => { window.__key(['4']); window.__step(1); window.__key(['4'], 'keyup'); });
  const atk = await step(20);
  ph.frames.push(...atk);
  const a = await snap();
  ph.runAttack = a.p1.an;
  ph.shots.push(await grab('run-attack'));
  await p.evaluate(() => { window.__key(['f'], 'keyup'); });
  ok(a.p1.an && /^(WR|f,f,F)/.test(a.p1.an), `run attack fired: ${a.p1.an}`);
});

// ---- Phase 5: turnaround -> BT attack (Turn Around b+1+2,1+2 ends BT, then BT.1)
await phase('turnaround-bt', async (ph) => {
  await p.evaluate(() => window.__reset(1.0));
  const fr = await pressSeq(['b+1+2', '1+2'], 1.0, 90);
  ph.frames = fr || [];
  const s = await snap();
  ph.btAfterTurnaround = s.p1.bt;
  ok(s.p1.bt === true, `Turn Around ends back-turned (_bt=${s.p1.bt}, state=${s.p1.st})`);
  if (s.p1.bt) {
    const fr2 = await press('1', 1.0, false, 40);
    ph.frames.push(...(fr2 || []));
    const s2 = await snap();
    ph.btAttack = s2.p1.an;
    ph.shots.push(await grab('bt-1'));
    ok(s2.p1.an === 'BT.1', `BT attack fired: ${s2.p1.an}`);
  }
});

// ---- Phase 6: 2+4 paired throw (the Nov 3 gap)
await phase('throw-2+4', async (ph) => {
  const fr = await press('2+4', 1.0, true, 260);
  ph.frames = fr || [];
  const p1 = new Set(ph.frames.map((f) => f.p1.st)), p2 = new Set(ph.frames.map((f) => f.p2.st));
  ph.throwerStates = [...p1]; ph.victimStates = [...p2];
  ok(p1.has('throwing') && p1.has('throwExec'), `2+4 thrower states ${[...p1]}`);
  ok(p2.has('thrown') && p2.has('thrownExec'), `2+4 victim states ${[...p2]}`);
  const ex = ph.frames.filter((f) => f.p2.st === 'thrownExec');
  const far = Math.max(0, ...ex.map((f) => Math.abs(f.p2.x - f.p1.x)));
  ph.thrownExecFrames = ex.length; ph.maxVictimDist = +far.toFixed(2);
  ok(ex.length && ex.every((f) => f.p2.clip), '2+4 thrownExec frames all have a victim clip');
  ok(far < 2.2, `2+4 victim stays close (max ${far.toFixed(2)} m)`);
  // frame sheet: before + four moments
  await p.evaluate(() => window.__reset(1.0));
  for (const [i, n] of [[0, 0], [1, 4], [2, 20], [3, 30], [4, 40]]) {
    await p.evaluate((n) => { const g = window.__game; if (n === 4) { window.__key(['2', '4']); window.__step(1); window.__key(['2', '4'], 'keyup'); } window.__step(n); }, n);
    ph.shots.push(await grab(`throw24-${i}`));
  }
});

// ---- Phase 7: kick string 3,2,2
await phase('kick-string-3-2-2', async (ph) => {
  // No mid-string grab: string grace is 500 ms of REAL time and a render
  // between hits would expire it. Mid-string state is in ph.frames (per-frame log).
  let fr = await pressSeq(['3', '2', '2'], 1.6, 60);
  if (!fr) { ph.bad = 'press failed'; fr = []; }
  ph.frames = fr;
  const s = seq(fr);
  ph.fired = s;
  ph.shots.push(await grab('kickstring-end'));
  ok(JSON.stringify(s) === JSON.stringify(['3', '3,2', '3,2,2']), `kick string fired ${JSON.stringify(s)}`);
});

// ---- Phase 8: 1+3 paired throw (control — video-proven Nov 3)
await phase('throw-1+3', async (ph) => {
  const fr = await press('1+3', 1.0, true, 260);
  ph.frames = fr || [];
  const p1 = new Set(ph.frames.map((f) => f.p1.st)), p2 = new Set(ph.frames.map((f) => f.p2.st));
  ph.throwerStates = [...p1]; ph.victimStates = [...p2];
  ok(p1.has('throwing') && p1.has('throwExec'), `1+3 thrower states ${[...p1]}`);
  ok(p2.has('thrown') && p2.has('thrownExec'), `1+3 victim states ${[...p2]}`);
  const ex = ph.frames.filter((f) => f.p2.st === 'thrownExec');
  ph.thrownExecFrames = ex.length;
  ok(ex.length && ex.every((f) => f.p2.clip), '1+3 thrownExec frames all have a victim clip');
});

// ---- Phase 9: grapple chain probe (PILE_DRIVER.1+2,1+2 — chain runtime?)
await phase('chain-probe', async (ph) => {
  const fr = await press('1+3', 1.0, true, 120);
  ph.frames = fr || [];
  // During the throw, try the chain follow input from the strings list.
  const mid = await p.evaluate(() => {
    const g = window.__game; const out = { before: window.__snap() };
    window.__key(['1', '2']); window.__step(1); window.__key(['1', '2'], 'keyup');
    window.__step(60); out.after = window.__snap();
    return out;
  });
  ph.chainProbe = mid;
  const chainFired = mid.after.p1.an && mid.after.p1.an !== mid.before.p1.an && /throw/i.test(mid.after.p1.st + mid.after.p1.an);
  ph.chainExecuted = !!chainFired;
  console.log('CHAIN probe:', JSON.stringify(mid));
});

await p.evaluate(() => window.__game.arena.setFreeCamera(false));
fs.writeFileSync(`${SHOTS}/video-pantera-log.json`, JSON.stringify(log, null, 1));
console.log(`${passes} passed, ${fails.length} failed`);
await b.close();
process.exit(fails.length ? 1 : 0);

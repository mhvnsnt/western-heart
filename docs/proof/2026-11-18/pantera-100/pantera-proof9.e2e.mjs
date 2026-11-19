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
p.on('pageerror', (e) => { console.log('PAGEERROR (logged, not counted)', String(e).slice(0, 200)); });
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
    c.position.set(m, 4.5, 6.5); c.lookAt(m, 0.8, 0); c.updateMatrixWorld(); a.render();
    return a.renderer.domElement.toDataURL('image/png');
  });
  const name = `frame-${String(++frameNo).padStart(3, '0')}-${tag}.png`;
  fs.writeFileSync(`${SHOTS}/${name}`, Buffer.from(data.split(',')[1], 'base64'));
  return name;
}
// Back-side grab: same framing from -z (runs 7/8's +z grabs sat inside the
// shrine rock pile once the midpoint drifted to x~2).
async function grabTop(tag) {
  const data = await p.evaluate(() => {
    const g = window.__game, a = g.arena, c = a.camera, m = (g.p1.root.position.x + g.p2.root.position.x) / 2;
    a.setFreeCamera(true);
    c.position.set(m, 7.5, 2.0); c.lookAt(m, 0.6, 0); c.updateMatrixWorld(); a.render();
    return a.renderer.domElement.toDataURL('image/png');
  });
  const name = `frame-${String(++frameNo).padStart(3, '0')}-${tag}.png`;
  fs.writeFileSync(`${SHOTS}/${name}`, Buffer.from(data.split(',')[1], 'base64'));
  return name;
}
// P1-framed grab: camera tracks Pantera (x~-0.2, clear of the mound at x~2).
async function grabP1(tag) {
  const data = await p.evaluate(() => {
    const g = window.__game, a = g.arena, c = a.camera, x = g.p1.root.position.x;
    a.setFreeCamera(true);
    c.position.set(x, 2.9, 3.6); c.lookAt(x, 0.9, 0); c.updateMatrixWorld(); a.render();
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
  // Incremental checkpoint: the per-phase log is written after EVERY phase, so a
  // runtime restart loses at most the in-progress phase (run 5 was killed this way).
  fs.writeFileSync(`${SHOTS}/video-pantera-log.json`, JSON.stringify(log, null, 1));
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

// ---- Phase C1: grapple chain 1+3,1 (Lane C merged df0e900 — chain runtime
// executes; the link is the string continuation '1' pressed mid-throw, fired
// on completion by the batch-string fix). Expect '1+3,1' + ~40 total dmg.
await phase('chain-13-1', async (ph) => {
  let fr = await press('1+3', 1.2, true, 9);
  ph.frames.push(...fr);
  fr = await step(25);
  ph.frames.push(...fr);
  fr = await press('1', 1.2, false, 40);
  ph.frames.push(...fr);
  fr = await step(40);
  ph.frames.push(...fr);
  ph.shots.push(await grabP1('chain-13-1-link'));
  fr = await step(100);
  ph.frames.push(...fr);
  const s = await snap();
  const ans = [...new Set(ph.frames.map((f) => f.p1.an).filter(Boolean))];
  ph.attackSeq = ans; ph.p2hp = s.p2.hp;
  ok(ans.includes('1+3,1'), `chain 1+3,1: link fired (attacks=${JSON.stringify(ans)})`);
  ok(s.p2.hp <= 142, `chain 1+3,1: total damage (p2 hp 180 -> ${s.p2.hp})`);
});

// ---- Phase C2: grapple chain 2+4,1 (same shape, the Nov 3 gap throw).
await phase('chain-24-1', async (ph) => {
  let fr = await press('2+4', 1.2, true, 9);
  ph.frames.push(...fr);
  fr = await step(25);
  ph.frames.push(...fr);
  fr = await press('1', 1.2, false, 40);
  ph.frames.push(...fr);
  fr = await step(40);
  ph.frames.push(...fr);
  ph.shots.push(await grabP1('chain-24-1-link'));
  fr = await step(100);
  ph.frames.push(...fr);
  const s = await snap();
  const ans = [...new Set(ph.frames.map((f) => f.p1.an).filter(Boolean))];
  ph.attackSeq = ans; ph.p2hp = s.p2.hp;
  ok(ans.includes('2+4,1'), `chain 2+4,1: link fired (attacks=${JSON.stringify(ans)})`);
  ok(s.p2.hp <= 142, `chain 2+4,1: total damage (p2 hp 180 -> ${s.p2.hp})`);
});

// ---- Phase B4: BT.4 with a P1-framed grab (runs 7-10's midpoint grabs all
// sat inside the shrine debris mound once FC.1+2 knockback drifted the
// midpoint to x~2; Pantera stays near x~-0.2, clear of it).
await phase('bt-4-p1cam', async (ph) => {
  await p.evaluate(() => window.__reset(0.5));
  await p.evaluate(() => { window.__key(['d']); });
  await new Promise((r) => setTimeout(r, 300));
  await p.evaluate(() => { window.__step(15); });
  const c = await snap();
  ok(c.p1.st === 'crouch', `BT4-p1cam: crouch entered (state=${c.p1.st})`);
  // Release d FIRST, then press 1+2 inside the 0.25 s fresh-crouch window:
  // holding d makes df0e900 resolve d+1+2 instead of FC.1+2 (Lane B fix).
  await p.evaluate(() => { window.__key(['d'], 'keyup'); });
  await p.evaluate(() => { window.__key(['1', '2']); window.__step(1); window.__key(['1', '2'], 'keyup'); });
  let btAt = -1;
  for (let k = 0; k < 20; k++) {
    const fr = await step(5);
    ph.frames.push(...fr);
    const s = await snap();
    if (s.p1.bt) { btAt = k; break; }
  }
  ok(btAt >= 0, `BT4-p1cam: back-turned reached (chunk=${btAt})`);
  const hpBefore = (await snap()).p2.hp;
  ph.hpBeforeBt4 = hpBefore;
  await p.evaluate(() => { window.__key(['4']); window.__step(1); window.__key(['4'], 'keyup'); });
  const fr2 = await step(11);
  ph.frames.push(...fr2);
  ph.shots.push(await grabP1('bt-4-p1cam-mid'));
  const fr3 = await step(31);
  ph.frames.push(...fr3);
  const s2 = await snap();
  const ans = [...new Set(ph.frames.map((f) => f.p1.an).filter(Boolean))];
  ph.attackSeq = ans; ph.p2hpAfter = s2.p2.hp;
  ok(ans.includes('BT.4'), `BT4-p1cam: BT.4 fired (attacks=${JSON.stringify(ans)})`);
  ph.bt4Hit = s2.p2.hp < hpBefore;
});

// ---- Phase D1: Lane B kick-string fix — d/f+4,3 (was resolving FC.d/f+4,
// 8 dmg, and the continuation was hijacked; now d/f+4, 13 dmg T7 king_76).
await phase('df-string', async (ph) => {
  const fr = await pressSeq(['d/f+4', '3'], 1.2, 40);
  ph.frames = fr;
  const s = await snap();
  const ans = seq(fr);
  ph.attackSeq = ans; ph.p2hp = s.p2.hp;
  ok(ans.includes('d/f+4'), `d/f+4,3: d/f+4 fired (attacks=${JSON.stringify(ans)})`);
  ok(ans.includes('d/f+4,3'), `d/f+4,3: continuation fired (attacks=${JSON.stringify(ans)})`);
  ok(s.p2.hp < 180, `d/f+4,3: damage dealt (p2 hp 180 -> ${s.p2.hp})`);
});

// ---- Phase W1: Lane B WR fix — WR.1+2 from a real run (was losing to f+1+2;
// running() latch fired 250 ms after f,f so ctx.running was false at entry).
await phase('wr-12', async (ph) => {
  await p.evaluate(() => window.__reset(1.2));
  await p.evaluate(() => { window.__key(['f']); window.__step(2); window.__key(['f'], 'keyup'); window.__step(2); window.__key(['f']); });
  let ran = false;
  for (let k = 0; k < 12; k++) {
    const fr = await step(5);
    ph.frames.push(...fr);
    const s = await snap();
    if (s.p1.st === 'tekrun') { ran = true; break; }
  }
  ok(ran, 'WR.1+2: run entered (tekrun)');
  await p.evaluate(() => { window.__key(['1', '2']); window.__step(1); window.__key(['1', '2'], 'keyup'); window.__key(['f'], 'keyup'); });
  const fr = await step(40);
  ph.frames.push(...fr);
  const s = await snap();
  const ans = [...new Set(ph.frames.map((f) => f.p1.an).filter(Boolean))];
  ph.attackSeq = ans; ph.p2hp = s.p2.hp;
  ph.shots.push(await grabP1('wr-12-mid'));
  ok(ans.includes('WR.1+2'), `WR.1+2: fired from run (attacks=${JSON.stringify(ans)})`);
  ok(s.p2.hp < 180, `WR.1+2: damage dealt (p2 hp 180 -> ${s.p2.hp})`);
});

await p.evaluate(() => window.__game.arena.setFreeCamera(false));
fs.writeFileSync(`${SHOTS}/video-pantera-log.json`, JSON.stringify(log, null, 1));
console.log(`${passes} passed, ${fails.length} failed`);
await b.close();
process.exit(fails.length ? 1 : 0);

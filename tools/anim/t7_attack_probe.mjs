// tools/anim/t7_attack_probe.mjs — make P1 perform moves by notation in the real game and photograph each one
// FROZEN AT ITS ACTIVE FRAMES (front + side close-ups), logging the attack plan the fighter picked.
//
// Why: a rig is judged in motion, not in the stance. Negativo's refit (2026-11-01) is checked here: arms, chest,
// neck and face mid-punch / mid-kick. Plays like the player: fighter.tryAttack(notation), the same entry the
// input layer uses; the AI is stubbed so P2 stands still; the game is paused (game.pause) only for the photo.
//
// usage: NO_REMOTE=1 node tools/anim/t7_attack_probe.mjs <game-url> <outdir> <p1> <p2> <move,move,...> [stage]
//   e.g. NO_REMOTE=1 node tools/anim/t7_attack_probe.mjs http://127.0.0.1:8765/game/index.html out negativo pantera "b+2,d/f+1,1,3,4"
//   NO_REMOTE=1 blocks the B2 Worker so models load from this checkout (asset-config tries the remote first:
//   without it you photograph the LIVE model, not your change). Needs playwright (pre-installed Chromium).
import { createRequire } from 'module';
import fs from 'fs';
const { chromium } = createRequire(import.meta.url)('playwright');
const [,, base, out, p1, p2, list, stage = 'shrine'] = process.argv;
if (!list) { console.error('usage: node t7_attack_probe.mjs <game-url> <outdir> <p1> <p2> <move,move,...> [stage]'); process.exit(2); }
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 900, height: 900 } });
const logs = [];
if (process.env.NO_REMOTE) await page.route(/workers\.dev/, r => r.abort());
// ATTIRES='{"negativo":"negativo-attire2"}' seeds the saved attire choice (game/js/attires.js wh_attires_v1) before load
if (process.env.ATTIRES) await page.addInitScript((v) => { try { localStorage.setItem('wh_attires_v1', v); } catch (e) { /* none */ } }, process.env.ATTIRES);
page.on('console', m => { const t = m.text(); if (/WH-T7|pageerror|Error|fight load failed/.test(t)) logs.push(`[${m.type()}] ${t}`); });
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
await page.goto(`${base}?quick=${p1},${p2},${stage}`, { waitUntil: 'load', timeout: 120000 });
const t0 = Date.now();
let ready = false;
while (Date.now() - t0 < 180000) {
  ready = await page.evaluate(() => { const g = window.__game; return !!(g && g.p1 && g.p1.t3actions && Object.keys(g.p1.t3actions).length && g.roundState === 'fight'); }).catch(() => false);
  if (ready) break;
  await page.waitForTimeout(1000);
}
console.log('READY', ready);
await page.evaluate(() => { const g = window.__game; g.ai = { update() {}, reset() {} }; });
await page.waitForTimeout(1500);
const cdp = await page.context().newCDPSession(page);
const shot = async (file) => {
  try {
    const r = await Promise.race([cdp.send('Page.captureScreenshot', { format: 'png' }), new Promise((_, rej) => setTimeout(() => rej(new Error('shot timeout')), 90000))]);
    fs.writeFileSync(file, Buffer.from(r.data, 'base64'));
  } catch (e) { logs.push('SHOT ' + file + ' ' + e.message); }
};
const results = [];
for (const mv of list.split(',')) {
  const r = await page.evaluate(async (mv) => {
    const g = window.__game, f = g.p1;
    // software WebGL runs the game far below 60 fps: wait on GAME state with real-time budgets, never by loop count
    const until = async (cond, ms) => { const tEnd = Date.now() + ms; while (!cond() && Date.now() < tEnd) await new Promise(res => setTimeout(res, 20)); };
    await until(() => f.state === 'idle', 40000);
    // a press inside the post-move string grace (fighter._stringGraceUntil, 500 ms) continues the last string:
    // wait it out so each listed notation is pressed fresh, the way a player starts a new move
    await until(() => performance.now() > (f._stringGraceUntil || 0) + 50, 3000);
    const x0 = f.root.position.x;
    const oldId = f._atkPlan && f._atkPlan.id;
    const ok = f.tryAttack(mv);
    await until(() => f._atkPlan && f._atkPlan.name && f._atkPlan.id !== oldId, 20000);  // THIS move's plan
    const p = f._atkPlan || {};
    const act = p.name && f.t3actions && f.t3actions[p.name];
    // wait for the active window (plan t0..t1 in clip seconds), then freeze the whole game for the photos
    const tm = p.timing || {};
    const tMid = (Number.isFinite(tm.t0) && Number.isFinite(tm.t1)) ? (tm.t0 + tm.t1) / 2 : 0.25;
    if (act) await until(() => act.time >= tMid || f.state === 'idle', 30000);
    g.pause(true);
    return { mv, ok, state: f.state, moveKey: f.attack && f.attack.moveKey, plan: { name: p.name, kind: p.kind, why: p.why, src: tm.src, t0: tm.t0, t1: tm.t1 },
             frozenAt: act ? +act.time.toFixed(3) : null, actW: act ? +act.getEffectiveWeight().toFixed(2) : null, x0 };
  }, mv);
  for (const view of ['front', 'side']) {
    await page.evaluate(([view]) => {
      const g = window.__game, f = g.p1, cam = g.arena.camera;
      const V = f.root.position.constructor, rp = new V();
      f.root.getWorldPosition(rp);
      const dir = f.facing || 1;
      g.arena.setFreeCamera(true);
      if (view === 'front') cam.position.set(rp.x + dir * 2.6, 1.3, rp.z + 0.35);
      else cam.position.set(rp.x + dir * 0.3, 1.3, rp.z + 2.7);
      cam.lookAt(rp.x + dir * 0.25, 1.0, rp.z);
      cam.updateMatrixWorld();
      try { g.arena.render(); } catch (e) { /* render once for the shot */ }
    }, [view]);
    await page.waitForTimeout(300);
    await shot(`${out}/${mv.replace(/[^\w]+/g, '_')}_${view}.png`);
  }
  const travel = await page.evaluate(async (x0) => {
    const g = window.__game, f = g.p1;
    g.arena.setFreeCamera(false);
    g.pause(false);
    const tEnd = Date.now() + 40000;
    while (f.state !== 'idle' && Date.now() < tEnd) await new Promise(res => setTimeout(res, 20));
    return +(f.root.position.x - x0).toFixed(2);
  }, r.x0);
  r.travel = travel;
  delete r.x0;
  results.push(r);
  console.log('ATTACK', JSON.stringify(r));
}
fs.writeFileSync(`${out}/attacks.json`, JSON.stringify(results, null, 1));
fs.writeFileSync(`${out}/console.log`, logs.join('\n'));
console.log(logs.slice(0, 12).join('\n'));
await browser.close();

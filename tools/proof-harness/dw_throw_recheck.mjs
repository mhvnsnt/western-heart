// dw_throw_recheck.mjs — Surge Form throw pair-binding live re-check.
// Owed from the DW retarget pilot + rollout: the Surge Form 1+3 throw fired
// as the T3 throw and the pair never formed in the observation windows.
// This probe answers CONNECTED / NOT CONNECTED with the exact observation:
//   LIVE: up to 3 Surge Form 1+3 attempts, polling f._throwPair every 200 ms
//     for 30 s real time per attempt (software rendering runs the game in
//     slow motion, so the window is long). A formed pair reports its
//     throwerAction: 'dw:1+3' = CONNECTED as DW, 'throw:0x…' = T3 pair only.
//   DIRECT (in-page diagnostics, after the live attempts): calls the real
//     internals to name the blocker when the pair never forms —
//     WH_T3_REACTIONS loaded? _throwPairFor(move, victim) pair vs reason?
//     _dwThrowAction() with attackName '1+3' + surgeForm on? _bindThrowPair
//     on the resolved pair (does the DW override swap throwerAction)?
// Frames are captured only around the throw window (12 per attempt);
// the verdict is the polled state, the frames are visual confirmation.
// usage: CHROME_PATH=... NODE_PATH=/tmp/probe-env/node_modules node dw_throw_recheck.mjs <game-url> <outdir>
//   game-url: the served game, e.g. http://127.0.0.1:8765/game/index.html
//   The game is served by tools/proof-harness/dw_server.mjs (Node static
//   server — python http.server drops concurrent module fetches).
import { createRequire } from 'module';
import fs from 'fs';
const { chromium } = createRequire(import.meta.url)('playwright-core');

const [,, base, out] = process.argv;
if (!base || !out) { console.error('usage: node dw_throw_recheck.mjs <game-url> <outdir>'); process.exit(2); }
fs.mkdirSync(out, { recursive: true });
const logs = [];
const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || '/var/tmp/ms-playwright/chromium-1254/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'],
});
const page = await browser.newPage({ viewport: { width: 900, height: 900 } });
page.on('console', m => { const t = m.text(); if (/WH-DW|WH-T7|WH-THROW|pageerror|Error|fight load failed/.test(t)) logs.push(`[${m.type()}] ${t}`); });
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
await page.route(/workers\.dev/, r => r.abort());
await page.goto(`${base}?quick=pantera,demonio,shrine`, { waitUntil: 'domcontentloaded', timeout: 300000 });
// NOTE: 'load' is NOT the gate here — on a contended box the page's big
// GLBs parse slowly under software WebGL and 'load' can time out even
// though the game itself becomes playable. The READY poll below is the
// real readiness signal (same as the trigger probe's).
const t0 = Date.now();
let ready = false;
// READY window is 900 s real time: on a contended box (load avg 10+,
// software WebGL) the game can take 7+ minutes from menu to a loaded
// fight — the 240 s window that sufficed at ~13:00 (READY 41–52 s) now
// times out with t3actions still 0 and roundState still 'idle' (diag
// 2026-11-08 ~18:40: HUD reached only at ~t+407 s). The READY poll is
// the gate; a slow box must not read as a game failure.
while (Date.now() - t0 < 900000) {
  ready = await page.evaluate(() => { const g = window.__game; return !!(g && g.p1 && g.p1.t3actions && Object.keys(g.p1.t3actions).length && g.roundState === 'fight'); }).catch(() => false);
  if (ready) break;
  await page.waitForTimeout(2000);
}
console.log('READY', ready, `after ${((Date.now() - t0) / 1000).toFixed(0)}s`);
if (!ready) { console.log('LOGS:\n' + logs.join('\n')); await browser.close(); process.exit(1); }
await page.evaluate(() => { const g = window.__game; g.ai = { update() {}, reset() {} }; });
await page.waitForTimeout(1500);

const cdp = await page.context().newCDPSession(page);
const shot = async (file) => {
  try {
    const r = await Promise.race([cdp.send('Page.captureScreenshot', { format: 'png' }), new Promise((_, rej) => setTimeout(() => rej(new Error('shot timeout')), 60000))]);
    fs.writeFileSync(file, Buffer.from(r.data, 'base64'));
    return true;
  } catch (e) { logs.push('SHOT ' + file + ' ' + e.message); return false; }
};
const state = () => page.evaluate(() => {
  const g = window.__game, f = g.p1, v = g.p2;
  const pair = f._throwPair;
  return {
    p1state: f.state, p1attack: f.attackName, p1surge: !!f.surgeForm, p1meter: f.meter,
    p2state: v.state, pair: pair ? { throwerAction: pair.throwerAction || null, victimAction: pair.victimAction || null,
      code: pair.code || null, thrower: pair.thrower ? pair.thrower.char.id : null } : null,
    dwActions: Object.keys(f.t3actions || {}).filter(n => n.startsWith('dw:')),
    dist: Math.hypot(v.root.position.x - f.root.position.x, v.root.position.z - f.root.position.z),
  };
});

const verdict = { livePair: null, attempts: [] };
for (let attempt = 1; attempt <= 3; attempt++) {
  const dir = `${out}/attempt${attempt}`;
  fs.mkdirSync(dir, { recursive: true });
  const start = await page.evaluate(() => {
    const g = window.__game, f = g.p1, v = g.p2;
    return (async () => {
      const until = async (cond, ms) => { const tEnd = Date.now() + ms; while (!cond() && Date.now() < tEnd) await new Promise(res => setTimeout(res, 20)); };
      await until(() => f.state === 'idle', 60000);
      f.meter = f.maxMeter;
      if (!f.surgeForm) f.startSurgeForm();
      await until(() => f.state === 'idle', 60000);
      v.root.position.set(f.root.position.x + f.facing * 1.2, v.root.position.y, f.root.position.z);
      v.facing = -f.facing;
      const ok = f.tryAttack('1+3');
      return { ok, attackName: f.attackName, state: f.state, surgeForm: f.surgeForm };
    })();
  });
  console.log(`ATTEMPT ${attempt} START`, JSON.stringify(start));
  // Poll for 30 s real time: the pair forms (or the legacy lock ends) in here.
  const timeline = [];
  let sawPair = null, sawThrowing = false, sawIdleAfter = false;
  for (let i = 0; i < 150; i++) {
    await page.waitForTimeout(200);
    const s = await state();
    if (s.p1state === 'throwing') sawThrowing = true;
    if (sawThrowing && s.p1state === 'idle') sawIdleAfter = true;
    if (s.pair && !sawPair) {
      sawPair = s.pair;
      console.log(`ATTEMPT ${attempt} PAIR at poll ${i} (${(i * 0.2).toFixed(1)}s):`, JSON.stringify(s.pair));
      for (let k = 0; k < 12; k++) { await page.waitForTimeout(300); await shot(`${dir}/frame_${String(k).padStart(3, '0')}.png`); }
      break;
    }
    if (i % 25 === 0) timeline.push({ t: (i * 0.2).toFixed(1), p1: s.p1state, atk: s.p1attack, surge: s.p1surge, p2: s.p2state, dist: +s.dist.toFixed(2) });
    if (sawIdleAfter && !s.pair) break; // attack ended with no pair: legacy lock path
  }
  const end = await state();
  console.log(`ATTEMPT ${attempt} END`, JSON.stringify({ sawThrowing, sawPair, end }));
  console.log(`ATTEMPT ${attempt} TIMELINE`, JSON.stringify(timeline));
  verdict.attempts.push({ attempt, start, sawThrowing, sawPair, end });
  if (sawPair) { verdict.livePair = sawPair; break; }
  if (!sawPair && !verdict.attempts[attempt - 1].sawThrowing) {
    console.log(`ATTEMPT ${attempt}: the throw never entered 'throwing' — grab did not connect; re-positioning next attempt`);
  }
}

// Direct diagnostics: name the blocker when the live pair never formed.
const diag = await page.evaluate(() => {
  const g = window.__game, f = g.p1, v = g.p2;
  const d = { reactionsLoaded: !!globalThis.WH_T3_REACTIONS,
    p1bank: f._t3 && f._t3.bank, p1dir: f._t3 && f._t3.dir,
    p2bank: v._t3 && v._t3.bank, p2dir: v._t3 && v._t3.dir,
    p1surge: !!f.surgeForm, p1attackName: f.attackName };
  try {
    f.attackName = '1+3';
    if (!f.surgeForm) { f.meter = f.maxMeter; f.startSurgeForm(); }
    d.surgeFormForDiag = !!f.surgeForm;
    const pf = f._throwPairFor(f.attack || { isGrab: true }, v);
    d.pairFor = pf.pair ? { code: pf.pair.code, branch: pf.pair.branch,
      throwerBank: pf.pair.clips.throwerBank, victimBank: pf.pair.clips.victimBank,
      throwerSlot: pf.pair.clips.throwerSlot, victimSlot: pf.pair.clips.victimSlot } : null;
    d.pairForReason = pf.reason || null;
    if (pf.pair) {
      const bound = f._bindThrowPair(pf.pair, v);
      d.bindThrowPair = bound;
      d.boundThrowerAction = pf.pair.throwerAction || null;
      d.boundVictimAction = pf.pair.victimAction || null;
    }
    d.dwThrowAction = f._dwThrowAction ? f._dwThrowAction() : null;
    d.dwActions = Object.keys(f.t3actions || {}).filter(n => n.startsWith('dw:'));
  } catch (e) { d.error = String(e && e.message || e); }
  return d;
});
console.log('DIAG', JSON.stringify(diag, null, 1));
const connected = !!(verdict.livePair && verdict.livePair.throwerAction === 'dw:1+3');
console.log('VERDICT', connected ? 'CONNECTED as DW (live pair, throwerAction dw:1+3)'
  : verdict.livePair ? `T3-PAIR ONLY (live pair formed, throwerAction ${verdict.livePair.throwerAction})`
  : 'NOT-FORMED (no pair in any live attempt; see DIAG for the blocker)');
console.log('LOGS:\n' + logs.join('\n'));
await browser.close();
console.log('DONE', out);

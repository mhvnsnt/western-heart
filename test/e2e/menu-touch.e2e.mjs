// t122u: mobile touch regression test for the main menu.
// iPhone-13 profile (hasTouch, 390x844). Serve the repo root on $WH_URL
// (default http://127.0.0.1:8811). Run: node test/e2e/menu-touch.e2e.mjs [shotsDir]
// 1) every visible main-menu item is the topmost element at its centre (nothing eats taps)
// 2) same check with a boot module forced to fail (the owner's untappable case)
// 3) real taps: VERSUS -> char select -> P1 + P2 -> stage -> fight HUD
// 4) classic result-screen REMATCH (PR #1255 follow-up): a ?quick= fight runs
//    Pairing is pantera vs phantom deliberately: both models are inside CI's
//    sparse checkout (roster/pantera, and phantom BASE = roster/phantom/
//    attires/attire1/model-rerig.glb). Bruno was the first pairing and failed
//    in CI: bruno's default attire is attire2, whose GLB is outside checkout.
//    outside modes, so its result screen takes the classic fallback. KO the foe
//    twice via the __game hook (best of 3, 3s round lock), tap REMATCH, and check
//    the replayed fight is the SAME pairing — the old bug replayed selectedChar
//    vs a random enemy.
// Taps allow 90s: headless CI renders the live-3D select panes on software GL (~600ms frames).
import { chromium, devices } from 'playwright';
import fs from 'node:fs';
const BASE = process.env.WH_URL || 'http://127.0.0.1:8811';
const SHOTS = process.argv[2] || 'menu-touch-shots';
fs.mkdirSync(SHOTS, { recursive: true });
const fails = [];
const b = await chromium.launch();
async function page(breakModule) {
  const ctx = await b.newContext({ ...devices['iPhone 13'], viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
  const p = await ctx.newPage();
  if (breakModule) await p.route('**/packages/creation-suite/src/parts.js', r => r.fulfill({ status: 404, body: '' }));
  // M1 core roster hides CI's checked-out light fighters; ?roster=all keeps
  // the same cards this test has always tapped (core-set.js).
  await p.goto(BASE + '/game/index.html?roster=all');
  await p.waitForSelector('#screen-menu [data-mm]', { state: 'visible', timeout: 30000 });
  await p.waitForTimeout(5000); // past the tap-hint and failsafe timers
  // Diagnostic: record every delegated data-action click so a dead tap can be
  // distinguished from a tap whose handler never ran.
  await p.evaluate(() => {
    window.__clicks = [];
    document.addEventListener('click', (e) => {
      const el = e.target.closest && e.target.closest('[data-action]');
      if (el) window.__clicks.push(el.dataset.action + (e.isTrusted ? ':trusted' : ':synth'));
    }, true);
  });
  p.on('pageerror', (e) => console.log('PAGEERROR:', String(e).slice(0, 300)));
  return p;
}
async function hitCheck(p, tag) {
  const items = await p.evaluate(() => [...document.querySelectorAll('#screen-menu [data-mm]')]
    .filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && r.top < innerHeight; })
    .map(e => { const r = e.getBoundingClientRect(); const t = document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2);
      return { id: e.dataset.mm, h: Math.round(r.height), hit: !!t && (t === e || e.contains(t)), top: t ? (t.id || t.className || t.tagName) : null }; }));
  if (!items.length) fails.push(`${tag}: no menu items visible`);
  for (const i of items) {
    if (!i.hit) fails.push(`${tag}: ${i.id} covered by ${i.top}`);
    if (i.h < 44) fails.push(`${tag}: ${i.id} hit area ${i.h}px < 44px`);
  }
  console.log(`${tag}: ${items.length} items, ${items.filter(i => i.hit).length} tappable`);
  await p.screenshot({ path: `${SHOTS}/${tag}.png` });
}
let p = await page(false);
await hitCheck(p, '01-menu');
const scr = () => p.evaluate(() => ['screen-menu', 'screen-select', 'screen-stage', 'hud'].filter(id => { const e = document.getElementById(id); return e && getComputedStyle(e).display !== 'none' && !e.classList.contains('hidden'); }));
const step = async (sel, want, shot, waitMs = 60000) => {
  await p.tap(sel, { timeout: 90000 }); await p.waitForTimeout(800);
  if (want) {
    try { await p.waitForFunction((id) => { const e = document.getElementById(id); return e && getComputedStyle(e).display !== 'none' && !e.classList.contains('hidden'); }, want, { timeout: waitMs }); }
    catch { fails.push(`tap ${sel}: expected ${want}, on ${await scr()}`); }
  }
  if (shot) await p.screenshot({ path: `${SHOTS}/${shot}.png` });
};
try {
  // The versus flow needs modes.js (lazy). Wait for the boot warm to finish
  // it before tapping: under software GL the import and input queue are slow,
  // and a tap before __modes lands looks like a dead tap.
  await p.waitForFunction(() => !!window.__modes, null, { timeout: 120000 });
  // Versus opens the T8-style submenu (main, PR #932); its 1V1 VERSUS card
  // opens the PR #841 versus-setup screen -> choose fighters -> select.
  await step('[data-mm="versus"]', null, '02-versus-submenu');
  await step('.mm-card >> nth=0', 'screen-vssetup', '02b-vssetup');
  await step('#screen-vssetup [data-action="mode-versus"]', 'screen-select', '02-select', 180000);
  // TTT2 team battle (worker 24, PR #668): versus now asks for a battle format
  // INSIDE the select screen (1V1 FIGHT | TEAM BATTLE) before the grid is
  // tappable — the submenu overlay covers the cards until a format is chosen.
  await step('#vs-submenu [data-format="solo"]');
  await step('.char-card >> nth=0'); await step('#confirm-fighter');
  await step('.char-card >> nth=2'); await step('#confirm-fighter', 'screen-stage', '03-stage');
  await p.tap('#confirm-stage');
  await p.waitForFunction(() => { const h = document.getElementById('hud'); return h && getComputedStyle(h).display !== 'none' && !h.classList.contains('hidden'); }, null, { timeout: 60000 });
  await p.waitForTimeout(2000); await p.screenshot({ path: `${SHOTS}/04-fight.png` });
  console.log('flow: menu -> select -> stage -> fight OK');
} catch (e) { fails.push('flow: ' + e.message.split('\n')[0]); }
try { console.log('FLOW CLICKS:', await p.evaluate(() => JSON.stringify(window.__clicks))); } catch {}
if (fails.length) console.log('FLOW FAILS:\n' + fails.join('\n'));
await p.close(); // free the flow page's 3D renderer before the second page
try {
  p = await page(true);
  await hitCheck(p, '05-menu-module-failed');
} catch (e) { fails.push('broken-module page: ' + e.message.split('\n')[0]); }
// 4) Classic result-screen REMATCH (PR #1255 follow-up, see header).
try {
  const rp = await b.newPage({ viewport: { width: 960, height: 540 } });
  rp.on('pageerror', (e) => console.log('REMATCH PAGEERROR:', String(e).slice(0, 300)));
  await rp.goto(BASE + '/game/index.html?quick=pantera,phantom,shrine');
  await rp.waitForFunction(() => { const g = window.__game; return g && g.roundState === 'fight' && g.p1 && g.p2; }, null, { timeout: 300000, polling: 500 });
  const pair = () => rp.evaluate(() => ({ p1: window.__game.p1.char.id, p2: window.__game.p2.char.id }));
  const resultVisible = () => rp.evaluate(() => { const e = document.getElementById('screen-result'); return e && getComputedStyle(e).display !== 'none' && !e.classList.contains('hidden'); });
  const first = await pair();
  console.log('rematch: first fight', JSON.stringify(first));
  if (first.p1 !== 'pantera' || first.p2 !== 'phantom') fails.push(`rematch: first fight resolved to ${first.p1} vs ${first.p2}, not pantera vs phantom (model fallback — no rematch verdict possible)`);
  else {
    // KO loop: best of 3, so two KOs end the match. Zero the foe only while a
    // round is live; _endRound guards roundState === 'fight', and _startRound
    // restores hp, so a zero landing during intro/over would be lost, not harmful.
    for (let round = 0; round < 3; round++) {
      if (await resultVisible()) break;
      await rp.waitForFunction(() => window.__game && window.__game.roundState === 'fight', null, { timeout: 120000, polling: 500 });
      await rp.evaluate(() => { window.__game.p2.hp = 0; });
      try {
        await rp.waitForFunction(() => { const g = window.__game; const e = document.getElementById('screen-result');
          return g.roundState === 'over' || (e && getComputedStyle(e).display !== 'none' && !e.classList.contains('hidden')); }, null, { timeout: 120000, polling: 500 });
      } catch { fails.push(`rematch: round ${round + 1} did not end after KO`); break; }
    }
    if (!(await resultVisible())) fails.push('rematch: result screen never appeared after 2 KOs');
    else {
      await rp.screenshot({ path: `${SHOTS}/06-result.png` });
      await rp.click('[data-action="rematch"]');
      await rp.waitForFunction(() => { const g = window.__game; const h = document.getElementById('hud');
        return g && g.roundState === 'fight' && h && getComputedStyle(h).display !== 'none' && !h.classList.contains('hidden'); }, null, { timeout: 300000, polling: 500 });
      const second = await pair();
      console.log('rematch: replayed fight', JSON.stringify(second));
      if (second.p1 !== 'pantera' || second.p2 !== 'phantom') fails.push(`rematch: replayed ${second.p1} vs ${second.p2}, not the pantera vs phantom just played`);
      await rp.screenshot({ path: `${SHOTS}/07-rematch-fight.png` });
      console.log('rematch: result -> REMATCH -> same pairing OK');
    }
  }
  await rp.close();
} catch (e) { fails.push('rematch: ' + e.message.split('\n')[0]); }
await b.close();
if (fails.length) { console.error('FAIL\n' + fails.join('\n')); process.exit(1); }
console.log('PASS');

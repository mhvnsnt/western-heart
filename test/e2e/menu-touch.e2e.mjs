// t122u: mobile touch regression test for the main menu.
// iPhone-13 profile (hasTouch, 390x844). Serve the repo root on $WH_URL
// (default http://127.0.0.1:8811). Run: node test/e2e/menu-touch.e2e.mjs [shotsDir]
// 1) every visible main-menu item is the topmost element at its centre (nothing eats taps)
// 2) same check with a boot module forced to fail (the owner's untappable case)
// 3) real taps: VERSUS -> char select -> P1 + P2 -> stage -> fight HUD
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
  await p.goto(BASE + '/game/index.html');
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
  await step('.char-card[data-id="pantera"]'); await step('#confirm-fighter');
  await step('.char-card[data-id="pantera"]'); await step('#confirm-fighter', 'screen-stage', '03-stage');
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
await b.close();
if (fails.length) { console.error('FAIL\n' + fails.join('\n')); process.exit(1); }
console.log('PASS');

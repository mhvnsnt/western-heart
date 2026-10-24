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
const step = async (sel, want, shot) => {
  await p.tap(sel, { timeout: 90000 }); await p.waitForTimeout(800);
  if (want) {
    try { await p.waitForFunction((id) => { const e = document.getElementById(id); return e && getComputedStyle(e).display !== 'none' && !e.classList.contains('hidden'); }, want, { timeout: 20000 }); }
    catch { fails.push(`tap ${sel}: expected ${want}, on ${await scr()}`); }
  }
  if (shot) await p.screenshot({ path: `${SHOTS}/${shot}.png` });
};
try {
  // T7 mode select (PR #932): a rail item opens its submenu; tap its first mode card.
  await step('[data-mm="versus"]');
  await step('#mm-cards .mm-card[data-action] >> nth=0', 'screen-select', '02-select');
  await step('.char-card >> nth=0'); await step('#confirm-fighter');
  await step('.char-card >> nth=2'); await step('#confirm-fighter', 'screen-stage', '03-stage');
  await p.tap('#confirm-stage');
  await p.waitForFunction(() => { const h = document.getElementById('hud'); return h && getComputedStyle(h).display !== 'none' && !h.classList.contains('hidden'); }, null, { timeout: 60000 });
  await p.waitForTimeout(2000); await p.screenshot({ path: `${SHOTS}/04-fight.png` });
  console.log('flow: menu -> select -> stage -> fight OK');
} catch (e) { fails.push('flow: ' + e.message.split('\n')[0]); }
p = await page(true);
await hitCheck(p, '05-menu-module-failed');
await b.close();
if (fails.length) { console.error('FAIL\n' + fails.join('\n')); process.exit(1); }
console.log('PASS');

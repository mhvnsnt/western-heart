// tools/proof-harness/fight_entry_probe.mjs — play the real menu flow on a phone viewport (VERSUS -> 1V1 -> fighter
// select -> stage select -> CONFIRM) and report whether it reaches the fight or bounces back to the stage screen
// (owner 2026-11-01: "when you pick an arena ... it keeps kicking me back out to the arena select menu and then I
// have to end up reloading the game ... the loading screens take too long").
// Records per attempt: seconds per phase, the stage-screen hint after CONFIRM (the game writes "Failed to load
// fighters: <why>" there), console errors / warnings, failed requests, and the outcome (FIGHT | BOUNCED | TIMEOUT).
//
// usage: node tools/proof-harness/fight_entry_probe.mjs <game-url> <out-dir> <p1> <p2> [attempts=1]
import { createRequire } from 'module';
import fs from 'fs';
const req = createRequire(import.meta.url);
const { chromium, devices } = req('playwright');
const [,, url, out, p1, p2, attempts = '1'] = process.argv;
if (!p2) { console.error('usage: node fight_entry_probe.mjs <game-url> <out-dir> <p1> <p2> [attempts]'); process.exit(2); }
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const ctx = await browser.newContext({ ...devices['iPhone 13'], viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
const page = await ctx.newPage();
const ev = [];
const t0 = Date.now();
const at = () => ((Date.now() - t0) / 1000).toFixed(1);
page.on('console', (m) => { const t = m.text(); if (m.type() === 'error' || /fight load failed|Failed to load|WH-T7|unavailable|abort|timeout/i.test(t)) ev.push(`${at()}s [${m.type()}] ${t.slice(0, 260)}`); });
page.on('pageerror', (e) => ev.push(`${at()}s [pageerror] ${e.message.slice(0, 260)}`));
page.on('requestfailed', (r) => ev.push(`${at()}s [requestfailed] ${r.url().slice(0, 140)} ${r.failure() && r.failure().errorText}`));
page.on('response', (r) => { if (r.status() >= 400) ev.push(`${at()}s [http ${r.status()}] ${r.url().slice(0, 160)}`); });
const visible = (id) => page.evaluate((id) => { const e = document.getElementById(id); return !!e && getComputedStyle(e).display !== 'none' && !e.classList.contains('hidden'); }, id);
const waitScreen = async (id, ms) => { try { await page.waitForFunction((id) => { const e = document.getElementById(id); return e && getComputedStyle(e).display !== 'none' && !e.classList.contains('hidden'); }, id, { timeout: ms, polling: 250 }); return true; } catch { return false; } };
const tap = async (sel) => { await page.tap(sel, { timeout: 120000 }); await page.waitForTimeout(600); };
const phases = {};
const mark = (k) => { phases[k] = +at(); };
await page.goto(url + (url.includes('?') ? '&' : '?') + 'roster=all', { waitUntil: 'load', timeout: 180000 });
mark('page_load');
await page.waitForSelector('#screen-menu [data-mm]', { state: 'visible', timeout: 120000 });
await page.waitForFunction(() => !!window.__modes, null, { timeout: 180000 });
mark('menu_ready');
await tap('[data-mm="versus"]');
await tap('.mm-card >> nth=0');
await waitScreen('screen-vssetup', 60000);
await tap('#screen-vssetup [data-action="mode-versus"]');
await waitScreen('screen-select', 180000);
mark('select_ready');
await tap('#vs-submenu [data-format="solo"]').catch(() => {});
await tap(`.char-card[data-id="${p1}"]`); await tap('#confirm-fighter');
await tap(`.char-card[data-id="${p2}"]`); await tap('#confirm-fighter');
await waitScreen('screen-stage', 120000);
mark('stage_ready');
const results = [];
for (let i = 0; i < +attempts; i++) {
  const s = Date.now();
  await tap('#confirm-stage');
  let outcome = 'TIMEOUT', hint = '';
  const end = Date.now() + 600000;
  while (Date.now() < end) {
    if (await visible('hud')) { outcome = 'FIGHT'; break; }
    const h = await page.evaluate(() => { const e = document.querySelector('#screen-stage .stage-hint, #stage-hint, #screen-stage [class*=hint]'); return e ? e.textContent : ''; }).catch(() => '');
    const loading = await page.evaluate(() => { const o = document.getElementById('load-overlay') || document.querySelector('.load-overlay'); return !!o && getComputedStyle(o).display !== 'none'; }).catch(() => false);
    const stageBtn = await page.evaluate(() => { const b = document.getElementById('confirm-stage'); return b && !b.disabled; }).catch(() => false);
    if (/fail/i.test(h) && stageBtn && !loading) { outcome = 'BOUNCED'; hint = h; break; }
    await page.waitForTimeout(500);
  }
  results.push({ attempt: i + 1, outcome, seconds: +((Date.now() - s) / 1000).toFixed(1), hint: hint.slice(0, 300) });
  console.log('ATTEMPT', JSON.stringify(results[results.length - 1]));
  if (outcome === 'FIGHT') break;
}
try { await page.screenshot({ path: `${out}/final.png`, timeout: 60000 }); } catch (e) { /* slow renderer */ }
fs.writeFileSync(`${out}/fight_entry.json`, JSON.stringify({ url, p1, p2, phases, results, events: ev }, null, 1));
console.log('PHASES', JSON.stringify(phases));
console.log(ev.slice(0, 40).join('\n'));
await browser.close();

// dw_diag.mjs — diagnose why the quick fight never reaches READY.
// Samples window.__game state every 10 s for ~180 s and dumps the timeline.
// No captures, no clicks — just state. Run:
//   CHROME_PATH=... NODE_PATH=/tmp/probe-env/node_modules node dw_diag.mjs <game-url>
import { createRequire } from 'module';
const { chromium } = createRequire(import.meta.url)('playwright-core');
const [,, base] = process.argv;
if (!base) { console.error('usage: node dw_diag.mjs <game-url>'); process.exit(2); }
const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || '/var/tmp/ms-playwright/chromium-1254/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'],
});
const page = await browser.newPage({ viewport: { width: 900, height: 900 } });
const errs = [];
page.on('pageerror', e => errs.push(`[pageerror] ${e.message}`));
page.on('console', m => { const t = m.text(); if (/pageerror|Error|fight load failed|WH-DW|WH-T7/.test(t)) errs.push(`[${m.type()}] ${t}`); });
await page.route(/workers\.dev/, r => r.abort());
await page.goto(`${base}?quick=pantera,demonio,shrine`, { waitUntil: 'load', timeout: 120000 });
const t0 = Date.now();
for (let i = 0; i < 18; i++) {
  await page.waitForTimeout(10000);
  const s = await page.evaluate(() => {
    const g = window.__game;
    if (!g) return { game: false, screen: document.querySelector('.screen.active, [id^="screen-"].active')?.id || document.title, bodyText: (document.body.innerText || '').slice(0, 200) };
    return {
      game: true,
      roundState: g.roundState,
      p1: g.p1 ? { id: g.p1.id || g.p1.charId, t3actions: g.p1.t3actions ? Object.keys(g.p1.t3actions).length : 'none', model: !!g.p1.model } : null,
      p2: g.p2 ? { id: g.p2.id || g.p2.charId, t3actions: g.p2.t3actions ? Object.keys(g.p2.t3actions).length : 'none', model: !!g.p2.model } : null,
      screen: document.querySelector('.screen.active, [id^="screen-"].active')?.id || null,
      bodyText: (document.body.innerText || '').slice(0, 150),
    };
  }).catch(e => ({ evalError: String(e) }));
  console.log(`t+${((Date.now() - t0) / 1000).toFixed(0)}s`, JSON.stringify(s));
}
console.log('ERRORS:\n' + (errs.join('\n') || '(none)'));
await browser.close();

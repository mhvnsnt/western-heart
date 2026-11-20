// Character select capture
//
// node tools/proof-harness/select.mjs OUTDIR id1,id2,...
// Opens the select screen, hovers each id, captures the preview model + HTTP/console errors.
//
// Proof harness from the 2026-10-20/21 Claude session (tools/TOOLS-INDEX.md). Serve the repo
// first:  python3 -m http.server 8765   (from the repo root), then run with node 18+.
// PLAYWRIGHT_MODULE / CHROMIUM_PATH override the defaults below (cloud container layout).
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright/index.mjs');
import fs from 'fs';
const [,, out='sel', ids='pantera,rin'] = process.argv;
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
const logs = [];
page.on('console', m => logs.push(`[${m.type()}] ${m.text()}`));
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
page.on('requestfailed', r => logs.push(`[reqfail] ${r.url()}`));
page.on('response', r => { if (r.status() >= 400) logs.push(`[http ${r.status()}] ${r.url()}`); });
await page.goto('http://127.0.0.1:8765/game/index.html', { waitUntil: 'load' });
await page.waitForTimeout(1200);
await page.click('[data-action="mode-versus"]');
await page.waitForTimeout(800);
const cdp = await page.context().newCDPSession(page);
let i = 0;
for (const id of ids.split(',')) {
  await page.evaluate((x) => window.__selectScreen.selectById(x), id);
  await page.waitForTimeout(6000);
  const s = await cdp.send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(`${out}/${String(i++).padStart(2,'0')}_${id}.png`, Buffer.from(s.data, 'base64'));
}
fs.writeFileSync(`${out}/console.log`, logs.join('\n'));
await browser.close();

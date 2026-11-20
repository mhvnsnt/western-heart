// Rest-pose renders
//
// node tools/proof-harness/rest.mjs OUTDIR list.json
// Renders each model id at rest (no animation) - the evidence for model-facing.json.
//
// Proof harness from the 2026-10-20/21 Claude session (tools/TOOLS-INDEX.md). Serve the repo
// first:  python3 -m http.server 8765   (from the repo root), then run with node 18+.
// PLAYWRIGHT_MODULE / CHROMIUM_PATH override the defaults below (cloud container layout).
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright/index.mjs');
import fs from 'fs';
const [,, out, list] = process.argv;
fs.mkdirSync(out, { recursive: true });
const models = JSON.parse(fs.readFileSync(list, 'utf8'));
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1200, height: 960 } });
await page.goto('http://127.0.0.1:8765/game/poselab.html', { waitUntil: 'load' });
await page.waitForFunction(() => window.__poselab);
const cdp = await page.context().newCDPSession(page);
for (const m of models) {
  try {
    await page.evaluate((x) => window.__poselab.rest(x), m);
    const s = await cdp.send('Page.captureScreenshot', { format: 'png', clip: { x: 0, y: 0, width: 1200, height: 900, scale: 0.5 } });
    fs.writeFileSync(`${out}/${m}.png`, Buffer.from(s.data, 'base64'));
  } catch (e) { console.log('ERR', m, e.message.slice(0, 120)); }
}
await browser.close();

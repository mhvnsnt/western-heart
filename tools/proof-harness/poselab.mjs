// Pose lab close-ups
//
// node tools/proof-harness/poselab.mjs OUTDIR list.json
// Drives game/poselab.html (window.__poselab.show/showFighter) for close-up pose checks.
//
// Proof harness from the 2026-10-20/21 Claude session (tools/TOOLS-INDEX.md). Serve the repo
// first:  python3 -m http.server 8765   (from the repo root), then run with node 18+.
// PLAYWRIGHT_MODULE / CHROMIUM_PATH override the defaults below (cloud container layout).
// node poselab.mjs <outdir> <json list of {model,bank,clip,t}>
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright/index.mjs');
import fs from 'fs';
const [,, out, list] = process.argv;
fs.mkdirSync(out, { recursive: true });
const jobs = JSON.parse(list);
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1200, height: 960 } });
const logs = [];
page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') logs.push(`[${m.type()}] ${m.text()}`); });
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
await page.goto('http://127.0.0.1:8765/game/poselab.html', { waitUntil: 'load' });
await page.waitForFunction(() => window.__poselab, null, { timeout: 30000 });
const cdp = await page.context().newCDPSession(page);
const results = [];
for (const j of jobs) {
  try {
    const r = await page.evaluate((a) => a.id ? window.__poselab.showFighter(a) : window.__poselab.show(a), j);
    results.push(r);
    const shot = await cdp.send('Page.captureScreenshot', { format: 'png', clip: { x: 0, y: 0, width: 1200, height: 900, scale: 1 } });
    fs.writeFileSync(`${out}/${j.id || (j.model + '_' + j.bank)}_${j.clip.replace(':', '')}_${String(j.t).replace('.', 'p')}.png`, Buffer.from(shot.data, 'base64'));
  } catch (e) { results.push({ ...j, error: e.message }); }
}
fs.writeFileSync(`${out}/results.json`, JSON.stringify(results, null, 1));
fs.writeFileSync(`${out}/console.log`, logs.join('\n'));
console.log(JSON.stringify(results.map(r => ({ id: r.id, m: r.model, c: r.clip, t: r.time, maxErr: r.maxErr, sh: r.srcHeadAboveHips, th: r.tgtHeadAboveHips, err: r.error }))));
await browser.close();

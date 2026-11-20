// Pose lab console probe
//
// node tools/proof-harness/dbg.mjs MODEL
// Prints retarget analysis for one model from inside poselab.html.
//
// Proof harness from the 2026-10-20/21 Claude session (tools/TOOLS-INDEX.md). Serve the repo
// first:  python3 -m http.server 8765   (from the repo root), then run with node 18+.
// PLAYWRIGHT_MODULE / CHROMIUM_PATH override the defaults below (cloud container layout).
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright/index.mjs');
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'] });
const page = await browser.newPage();
page.on('pageerror', e => console.log('pageerror', e.message));
await page.goto('http://127.0.0.1:8765/game/poselab.html', { waitUntil: 'load' });
await page.waitForFunction(() => window.__poselab);
const r = await page.evaluate(async () => {
  const THREE = await import('three');
  const res = await window.__poselab.show({ model: 'pantera', bank: 'king', clip: 'stance', t: 0.6 });
  // find scenes via renderer? poselab keeps them module-private; re-derive via the DOM-less path:
  return res;
});
console.log(JSON.stringify(r));
await browser.close();

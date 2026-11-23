// Tunnel title logo shot — one game (koc2), long wait after prompt dismissal
// so the glowing KING OF COLOSSEUM II logo has time to fade in.
const puppeteer = require('puppeteer');
const fs = require('fs');
const OUT = '/dev/shm/tunnel-test/title';
fs.mkdirSync(OUT, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const TUNNEL = 'https://powerseller-success-requesting-evanescence.trycloudflare.com';

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    userDataDir: '/dev/shm/tunnel-test/profile-logo',
    args: [
      '--no-sandbox',
      '--disable-dev-shm-usage',
      '--use-angle=swiftshader',
      '--enable-unsafe-swiftshader',
      '--autoplay-policy=no-user-gesture-required',
      '--window-size=800,760',
      '--no-first-run',
      '--disable-default-apps',
      '--crash-dumps-dir=/dev/shm/tunnel-test',
    ],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 800, height: 760 });
  page.on('pageerror', (e) => console.log(`[pageerror] ${e.message}`));
  await page.goto(`${TUNNEL}/play-ps2.html?game=koc2&autotest=1`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  const t0 = Date.now();
  let state = 'init';
  while (Date.now() - t0 < 180000) {
    const t = await page.evaluate(() => window.__ps2test).catch(() => null);
    if (t) state = t.state;
    if (state === 'running' || state === 'error' || state === 'no-sab') break;
    await sleep(3000);
  }
  console.log(`state=${state} after ${Math.round((Date.now() - t0) / 1000)}s`);
  await sleep(25000);
  await page.evaluate(() => window.__ps2press('ArrowUp', 300));
  await sleep(1500);
  await page.evaluate(() => window.__ps2press('KeyX', 300));
  await sleep(45000);
  await page.screenshot({ path: `${OUT}/koc2-logo-45s.png` });
  await sleep(45000);
  await page.screenshot({ path: `${OUT}/koc2-logo-90s.png` });
  const t = await page.evaluate(() => window.__ps2test).catch(() => null);
  console.log(`final state=${t && t.state} fps=${t && t.fps.length} reads=${t && t.discReads} bytes=${t && t.discBytes} errors=${JSON.stringify(t && t.errors)}`);
  await browser.close();
  console.log('DONE');
})().catch((e) => { console.error('FATAL ' + e.stack); process.exit(1); });

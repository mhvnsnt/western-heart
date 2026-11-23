// Extended title check for the FIXED player: boot on mobile emulation,
// dismiss the memcard prompt, then wait for the title / attract FMV and
// screenshot it. The game takes ~60-90s past the prompt to reach the title.
// Runs from /dev/shm/mobile-repro (puppeteer-core + cached Chrome 157).
const puppeteer = require('puppeteer-core');
const OUT = '/dev/shm/mobile-repro';
const CHROME = '/home/ubuntu/.cache/puppeteer/chrome/linux-157.0.8103.78/chrome-linux64/chrome';
const TUNNEL = 'https://powerseller-success-requesting-evanescence.trycloudflare.com';
const MOBILE_UA = 'Mozilla/5.0 (Linux; Android 15; motorola edge 2025) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROME,
    timeout: 180000, // VM load is very high (14+); Chrome needs longer to spawn
    userDataDir: OUT + '/profile3',
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--window-size=800,760', '--no-first-run', '--disable-default-apps', '--crash-dumps-dir=' + OUT],
  });
  const page = await browser.newPage();
  page.on('pageerror', (e) => console.log('[pageerror] ' + String(e).slice(0, 200)));
  await page.setUserAgent(MOBILE_UA);
  await page.setViewport({ width: 412, height: 915, deviceScaleFactor: 2.5, isMobile: true, hasTouch: true, isLandscape: false });
  await page.goto(`${TUNNEL}/play-ps2.html?game=koc2`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForSelector('#start-btn', { visible: true, timeout: 30000 });
  await (await page.$('#start-btn')).tap();
  console.log('[boot] tapped Play');
  const t0 = Date.now();
  let dismissed = false;
  const shotTargets = [30, 90, 120, 150, 180];
  const takenShots = {};
  for (let s = 5; s <= 180; s += 5) {
    await sleep(5000);
    const t = await page.evaluate(() => window.__ps2test).catch(() => null);
    const el = Math.round((Date.now() - t0) / 1000);
    if (s % 30 === 0 || s === 5) {
      console.log(`[t=${el}s] state=${t && t.state} frames=${t && t.framesTotal} fpsLast=${t && t.fps.slice(-3)} reads=${t && t.discReads} gl=${t && t.glState} err=${t && t.lastError}`);
    }
    if (!dismissed && el >= 30) {
      await page.evaluate(() => { window.__ps2press('ArrowUp', 150); });
      await sleep(700);
      await page.evaluate(() => { window.__ps2press('KeyX', 150); });
      dismissed = true;
      console.log(`[t=${el}s] dismissed memcard prompt (Up + Circle)`);
    }
    for (const target of shotTargets) {
      if (el >= target && !takenShots[target]) {
        takenShots[target] = true;
        await page.screenshot({ path: `${OUT}/fixed-title-t${target}.png` });
        console.log(`[t=${el}s] screenshot saved (target ${target}s)`);
      }
    }
  }
  await browser.close();
  console.log('DONE');
})().catch((e) => { console.error('FATAL ' + e.stack); process.exit(1); });

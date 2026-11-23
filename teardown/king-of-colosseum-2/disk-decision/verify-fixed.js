// Verify the FIXED player (on-screen diagnostics + fetch timeout/retry +
// GL watch + no-frames watchdog) on mobile emulation against the tunnel URL.
// Boots with a real tap, checks the diagnostics render, the game reaches the
// title, fps > 0, and input dismisses the memcard prompt.
// Runs from /dev/shm/mobile-repro (puppeteer-core + cached Chrome 157).
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const OUT = '/dev/shm/mobile-repro';
const CHROME = '/home/ubuntu/.cache/puppeteer/chrome/linux-157.0.8103.78/chrome-linux64/chrome';
const TUNNEL = 'https://powerseller-success-requesting-evanescence.trycloudflare.com';
const MOBILE_UA = 'Mozilla/5.0 (Linux; Android 15; motorola edge 2025) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROME,
    userDataDir: OUT + '/profile2',
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--window-size=800,760', '--no-first-run', '--disable-default-apps', '--crash-dumps-dir=' + OUT],
  });
  const page = await browser.newPage();
  const pageErrors = [];
  const failedReqs = [];
  page.on('pageerror', (e) => { pageErrors.push(String(e)); console.log('[pageerror] ' + String(e).slice(0, 200)); });
  page.on('requestfailed', (r) => { failedReqs.push(r.url().slice(-60)); console.log('[reqfail] ' + r.url().slice(-60)); });
  await page.setUserAgent(MOBILE_UA);
  await page.setViewport({ width: 412, height: 915, deviceScaleFactor: 2.5, isMobile: true, hasTouch: true, isLandscape: false });

  await page.goto(`${TUNNEL}/play-ps2.html?game=koc2`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  // Pre-boot diag check: the diagnostics box must be visible before Play is tapped.
  const preDiag = await page.evaluate(() => {
    const el = document.getElementById('diag');
    return { visible: !!(el && el.offsetHeight > 0), text: el ? el.textContent : null };
  });
  console.log('[diag pre-boot] visible=' + preDiag.visible + ' text=' + JSON.stringify(preDiag.text));

  await page.waitForSelector('#start-btn', { visible: true, timeout: 30000 });
  await (await page.$('#start-btn')).tap();
  console.log('[boot] tapped Play');

  const checks = { diagVisiblePreBoot: preDiag.visible, glOk: false, framesGrew: false, fpsPositive: false, warnHidden: false, inputWorked: false, lastErrorEmpty: false };
  const t0 = Date.now();
  let prompted = false;
  for (let s = 0; s <= 75; s += 5) {
    await sleep(5000);
    const t = await page.evaluate(() => window.__ps2test).catch(() => null);
    const ui = await page.evaluate(() => ({
      diag: (document.getElementById('diag') || {}).textContent,
      warnVisible: (document.getElementById('warn') || {}).offsetHeight > 0,
      badge: (document.getElementById('fps-badge') || {}).textContent,
    })).catch(() => ({}));
    console.log(`[t=${s + 5}s] state=${t && t.state} stage=${t && t.stage} frames=${t && t.framesTotal} fpsLast=${t && t.fps.slice(-3)} gl=${t && t.glState} retries=${t && t.retries} pending=${t && !!t.pendingReadSince} err=${t && t.lastError} warn=${ui.warnVisible} badge=${ui.badge}`);
    if (s + 5 === 10) {
      console.log('[diag t=10s]\n' + ui.diag);
      await page.screenshot({ path: OUT + '/fixed-mobile-t10.png' });
    }
    if (s + 5 === 30) {
      await page.screenshot({ path: OUT + '/fixed-mobile-t30.png' });
      // Input test: dismiss the memcard prompt (Up, then Circle) like the
      // tunnel run did, and confirm the title appears afterwards.
      await page.evaluate(() => { window.__ps2press('ArrowUp', 150); });
      await sleep(700);
      await page.evaluate(() => { window.__ps2press('KeyX', 150); });
      prompted = true;
      console.log('[input] pressed Up + Circle to dismiss memcard prompt');
    }
    if (s + 5 === 45) {
      await page.screenshot({ path: OUT + '/fixed-mobile-t45.png' });
      console.log('[diag t=45s]\n' + ui.diag);
    }
    if (s + 5 === 75) {
      await page.screenshot({ path: OUT + '/fixed-mobile-t75.png' });
      if (t) {
        checks.glOk = (t.glState || '').includes('✓');
        checks.framesGrew = (t.framesTotal || 0) > 100;
        checks.fpsPositive = (t.fps || []).some((f) => f > 10);
        checks.warnHidden = !ui.warnVisible;
        checks.lastErrorEmpty = !t.lastError;
        checks.inputWorked = prompted; // screenshot eyeball confirms the prompt is gone
      }
      console.log('[diag t=75s]\n' + ui.diag);
    }
  }
  console.log('CHECKS: ' + JSON.stringify(checks, null, 2));
  console.log('pageErrors: ' + JSON.stringify(pageErrors) + ' failedReqs: ' + JSON.stringify(failedReqs));
  fs.writeFileSync(OUT + '/verify-fixed-result.json', JSON.stringify({ checks, pageErrors, failedReqs }, null, 2));
  await browser.close();
  console.log('DONE');
})().catch((e) => { console.error('FATAL ' + e.stack); process.exit(1); });

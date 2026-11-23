// Tunnel title shots — dismiss the memcard prompt and capture the title screen
// over the Cloudflare quick tunnel (public HTTPS). Adapted from phase5-title.js.
const puppeteer = require('puppeteer');
const fs = require('fs');
const OUT = '/dev/shm/tunnel-test/title';
fs.mkdirSync(OUT, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const TUNNEL = 'https://powerseller-success-requesting-evanescence.trycloudflare.com';

async function titleShot(browser, gameId) {
  const page = await browser.newPage();
  await page.setViewport({ width: 800, height: 760 });
  page.on('pageerror', (e) => console.log(`[${gameId} pageerror] ${e.message}`));
  await page.goto(`${TUNNEL}/play-ps2.html?game=${gameId}&autotest=1`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  const t0 = Date.now();
  let state = 'init';
  while (Date.now() - t0 < 180000) {
    const t = await page.evaluate(() => window.__ps2test).catch(() => null);
    if (t) state = t.state;
    if (state === 'running' || state === 'error' || state === 'no-sab') break;
    await sleep(3000);
  }
  console.log(`[${gameId}] state=${state} after ${Math.round((Date.now() - t0) / 1000)}s`);
  if (state !== 'running') {
    await page.screenshot({ path: `${OUT}/${gameId}-notrunning.png` });
    await page.close();
    return { game: gameId, state };
  }
  await sleep(25000); // reach the memcard prompt
  await page.screenshot({ path: `${OUT}/${gameId}-prompt.png` });
  console.log(`[${gameId}] pressing Up then Circle to dismiss the prompt`);
  await page.evaluate(() => window.__ps2press('ArrowUp', 300));
  await sleep(1500);
  await page.evaluate(() => window.__ps2press('KeyX', 300));
  await sleep(10000);
  await page.screenshot({ path: `${OUT}/${gameId}-title1.png` });
  await sleep(15000);
  await page.screenshot({ path: `${OUT}/${gameId}-title2.png` });
  const t = await page.evaluate(() => window.__ps2test).catch(() => null);
  const log = await page.evaluate(() => { const el = document.getElementById('testlog'); return el ? el.textContent : ''; }).catch(() => '');
  console.log(`[${gameId}] final state=${t && t.state} fps=${t && t.fps.length} reads=${t && t.discReads} bytes=${t && t.discBytes} errors=${JSON.stringify(t && t.errors)}`);
  fs.writeFileSync(`${OUT}/${gameId}-title.json`, JSON.stringify({ ps2test: t, debugLog: log }, null, 2));
  await page.close();
  return { game: gameId, state: t && t.state };
}

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    userDataDir: '/dev/shm/tunnel-test/profile-title',
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
  const results = [];
  for (const g of ['koc2', 'koc2hybrid']) {
    try { results.push(await titleShot(browser, g)); }
    catch (e) { console.error(`[${g}] FATAL ${e.stack}`); results.push({ game: g, state: 'harness-error' }); }
  }
  fs.writeFileSync(OUT + '/title-results.json', JSON.stringify(results, null, 2));
  await browser.close();
  console.log('DONE');
})().catch((e) => { console.error('FATAL ' + e.stack); process.exit(1); });

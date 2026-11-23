// Tunnel verify — PS2 player over the Cloudflare quick tunnel (public HTTPS).
// Adapted from phase5-verify.js: same checks, tunnel URL instead of localhost.
// Runs from /dev/shm/tunnel-test with NODE_PATH=/home/ubuntu/ps2test/node_modules
const puppeteer = require('puppeteer');
const fs = require('fs');
const OUT = '/dev/shm/tunnel-test';
fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync(OUT + '/tmp', { recursive: true });

const TUNNEL = 'https://powerseller-success-requesting-evanescence.trycloudflare.com';
const GAMES = ['koc2', 'koc2hybrid'];
const BOOT_TIMEOUT_MS = 240000;   // max wait for state === 'running'
const POLL_MS = 5000;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function testGame(browser, gameId) {
  const page = await browser.newPage();
  await page.setViewport({ width: 800, height: 760 });
  const net = { manifest: [], pieces206: 0, piecesOther: [], other206: 0, tunnelStatus: null };
  page.on('response', (res) => {
    const u = res.url();
    if (u.startsWith(TUNNEL + '/play-ps2.html') && net.tunnelStatus === null) net.tunnelStatus = res.status();
    if (u.includes('raw.githubusercontent.com')) {
      const s = res.status();
      if (u.includes('.manifest.json')) net.manifest.push(s);
      else if (u.includes('.part')) { if (s === 206) net.pieces206++; else net.piecesOther.push(s + ' ' + u.slice(-60)); }
      else if (s === 206) net.other206++;
    }
  });
  page.on('pageerror', (e) => console.log(`[${gameId} pageerror] ${e.message}`));

  const url = `${TUNNEL}/play-ps2.html?game=${gameId}&autotest=1`;
  console.log(`[${gameId}] goto ${url}`);
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });

  // Gate check: is the "Secure connection required" message visible?
  const gateVisible = await page.evaluate(() => {
    const t = document.body ? document.body.innerText : '';
    return t.includes('Secure connection required');
  }).catch(() => null);

  let state = 'init';
  const t0 = Date.now();
  while (Date.now() - t0 < BOOT_TIMEOUT_MS) {
    const t = await page.evaluate(() => window.__ps2test).catch(() => null);
    if (t) {
      if (t.state !== state) {
        state = t.state;
        console.log(`[${gameId}] state=${state} at ${((Date.now() - t0) / 1000).toFixed(0)}s reads=${t.discReads} bytes=${t.discBytes}`);
      }
      if (state === 'running' || state === 'error' || state === 'no-sab') break;
    }
    await sleep(POLL_MS);
  }

  const result = { game: gameId, state, gateVisible, bootSecs: Math.round((Date.now() - t0) / 1000) };
  const dump = async (tag) => {
    const t = await page.evaluate(() => window.__ps2test).catch(() => null);
    const log = await page.evaluate(() => { const el = document.getElementById('testlog'); return el ? el.textContent : ''; }).catch(() => '');
    if (t) { result.ps2test = t; }
    result.debugLog = log;
    await page.screenshot({ path: `${OUT}/${gameId}-${tag}.png` });
    return t;
  };

  if (state === 'running') {
    await sleep(10000); await dump('t10');
    await sleep(20000); await dump('t30');
    await sleep(30000); await dump('t60');
    await sleep(30000);
    const t = await dump('t90');
    result.net = net;
    if (t) {
      const fps = t.fps || [];
      result.fpsCount = fps.length;
      result.fpsLast = fps.slice(-5);
      result.fpsAvg = fps.length ? +(fps.reduce((a, b) => a + b, 0) / fps.length).toFixed(1) : null;
      result.discReads = t.discReads;
      result.discBytes = t.discBytes;
      result.errors = t.errors;
    }
    console.log(`[${gameId}] RUNNING fps=${result.fpsCount} avg=${result.fpsAvg} last=${JSON.stringify(result.fpsLast)} reads=${result.discReads} bytes=${result.discBytes} errors=${JSON.stringify(result.errors)} net206pieces=${net.pieces206} manifest=${JSON.stringify(net.manifest)} tunnelStatus=${net.tunnelStatus} gateVisible=${gateVisible}`);
  } else {
    await dump('fail');
    result.net = net;
    const t = result.ps2test;
    if (t) { result.errors = t.errors; result.discReads = t.discReads; result.discBytes = t.discBytes; }
    console.log(`[${gameId}] FAILED state=${state} gateVisible=${gateVisible} errors=${JSON.stringify(result.errors)} tunnelStatus=${net.tunnelStatus}`);
  }
  await page.close();
  return result;
}

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    userDataDir: OUT + '/profile',
    args: [
      '--no-sandbox',
      '--disable-dev-shm-usage',
      '--use-angle=swiftshader',
      '--enable-unsafe-swiftshader',
      '--autoplay-policy=no-user-gesture-required',
      '--window-size=800,760',
      '--no-first-run',
      '--disable-default-apps',
      '--crash-dumps-dir=' + OUT,
    ],
  });
  const results = [];
  for (const g of GAMES) {
    try { results.push(await testGame(browser, g)); }
    catch (e) { console.error(`[${g}] FATAL ${e.stack}`); results.push({ game: g, state: 'harness-error', error: String(e) }); }
  }
  fs.writeFileSync(OUT + '/tunnel-results.json', JSON.stringify(results, null, 2));
  await browser.close();
  console.log('DONE');
})().catch((e) => { console.error('FATAL ' + e.stack); process.exit(1); });

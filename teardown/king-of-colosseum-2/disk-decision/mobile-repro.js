// Mobile repro — KoC2 black screen / 0 fps on Mars's phone.
// Emulates Motorola Edge 2025 (mobile viewport + touch + mobile UA) against the
// live tunnel URL, boots with a REAL TAP on the Play button (like Mars does),
// and captures console errors, network, boot-stage timing, rAF liveness,
// WebGL support, and __ps2test over 120s.
// Two arms: A = mobile emulation + tap; B = desktop viewport + tap (control).
// Runs from /dev/shm/mobile-repro with puppeteer-core + cached Chrome 157
// (/home/ubuntu/ps2test was cleared by the VM sweep lane 2026-11-21).
const puppeteer = require('puppeteer-core');
const CHROME = '/home/ubuntu/.cache/puppeteer/chrome/linux-157.0.8103.78/chrome-linux64/chrome';
const fs = require('fs');
const OUT = '/dev/shm/mobile-repro';
fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync(OUT + '/tmp', { recursive: true });

const TUNNEL = 'https://powerseller-success-requesting-evanescence.trycloudflare.com';
const GAME = 'koc2';
const RUN_SECS = 120;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const MOBILE_UA = 'Mozilla/5.0 (Linux; Android 15; motorola edge 2025) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36';

async function runArm(browser, arm) {
  const tag = arm.name;
  console.log(`\n===== ARM ${tag}: ${arm.desc} =====`);
  const page = await browser.newPage();
  const consoleLines = [];
  const pageErrors = [];
  const failedReqs = [];
  const net = { manifest: [], pieces206: 0, piecesOther: [], playJs: null, wasm: null, tunnelStatus: null };
  page.on('console', (m) => {
    const t = `[${m.type()}] ${m.text()}`;
    consoleLines.push(t);
    if (m.type() === 'error' || m.type() === 'warning') console.log(`[${tag} console] ${t.slice(0, 300)}`);
  });
  page.on('pageerror', (e) => { pageErrors.push(String(e && e.stack || e)); console.log(`[${tag} pageerror] ${String(e).slice(0, 300)}`); });
  page.on('requestfailed', (r) => { failedReqs.push(`${r.url().slice(-80)} :: ${r.failure() && r.failure().errorText}`); console.log(`[${tag} reqfail] ${r.url().slice(-80)} :: ${r.failure() && r.failure().errorText}`); });
  page.on('response', (res) => {
    const u = res.url();
    if (u.startsWith(TUNNEL + '/play-ps2.html') && net.tunnelStatus === null) net.tunnelStatus = res.status();
    if (u.endsWith('/play/Play.js')) net.playJs = res.status();
    if (u.endsWith('/play/Play.wasm')) net.wasm = res.status();
    if (u.includes('raw.githubusercontent.com')) {
      const s = res.status();
      if (u.includes('.manifest.json')) net.manifest.push(s);
      else if (u.includes('.part')) { if (s === 206) net.pieces206++; else net.piecesOther.push(s + ' ' + u.slice(-60)); }
    }
  });

  if (arm.mobile) {
    await page.setUserAgent(MOBILE_UA);
    await page.setViewport({ width: 412, height: 915, deviceScaleFactor: 2.5, isMobile: true, hasTouch: true, isLandscape: false });
  } else {
    await page.setViewport({ width: 800, height: 760 });
  }

  // rAF liveness probe: count frames in the page itself, independent of the emulator.
  await page.evaluateOnNewDocument(() => {
    window.__rafCount = 0;
    const tick = () => { window.__rafCount++; requestAnimationFrame(tick); };
    requestAnimationFrame(tick);
    window.__glProbe = null;
    window.addEventListener('load', () => {
      try {
        const c = document.createElement('canvas');
        const gl2 = c.getContext('webgl2');
        window.__glProbe = {
          webgl2: !!gl2,
          renderer: gl2 ? gl2.getParameter(gl2.RENDERER) : null,
          vendor: gl2 ? gl2.getParameter(gl2.VENDOR) : null,
          webgl1: !!c.getContext('webgl'),
        };
      } catch (e) { window.__glProbe = { error: String(e) }; }
    });
  });

  const url = `${TUNNEL}/play-ps2.html?game=${GAME}`;
  console.log(`[${tag}] goto ${url}`);
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });

  const env = await page.evaluate(() => ({
    sab: typeof SharedArrayBuffer !== 'undefined',
    isolated: !!window.crossOriginIsolated,
    ua: navigator.userAgent,
    hw: navigator.hardwareConcurrency,
    mem: (performance && performance.memory) ? { jsHeap: Math.round(performance.memory.jsHeapSizeLimit / 1048576) + 'MB limit' } : null,
    hidden: document.hidden,
    visibility: document.visibilityState,
    gl: window.__glProbe,
    raf: window.__rafCount,
  }));
  console.log(`[${tag}] env: ${JSON.stringify(env)}`);

  // Wait for the Play button and TAP it like Mars does (real touch gesture).
  await page.waitForSelector('#start-btn', { visible: true, timeout: 30000 });
  const btn = await page.$('#start-btn');
  const tBoot = Date.now();
  if (arm.mobile) await btn.tap();
  else await btn.click();
  console.log(`[${tag}] tapped Play at t=0`);

  const result = { arm: tag, env, net, pageErrors, failedReqs, samples: [] };
  const t0 = Date.now();
  let lastState = 'init';
  for (let s = 0; s <= RUN_SECS; s += 2) {
    await sleep(2000);
    const t = await page.evaluate(() => window.__ps2test).catch(() => null);
    const extra = await page.evaluate(() => ({
      raf: window.__rafCount,
      badge: (document.getElementById('fps-badge') || {}).textContent,
      status: (document.getElementById('status') || {}).textContent,
      hasModule: !!window.__ps2PlayModule,
      visibility: document.visibilityState,
    })).catch(() => ({}));
    if (t && t.state !== lastState) {
      lastState = t.state;
      console.log(`[${tag}] state=${t.state} at ${((Date.now() - t0) / 1000).toFixed(0)}s reads=${t.discReads} bytes=${t.discBytes} raf=${extra.raf}`);
    }
    if (s % 10 === 0 || s === RUN_SECS) {
      const fps = (t && t.fps) || [];
      const sample = { at: s, state: t && t.state, fpsLast5: fps.slice(-5), fpsLen: fps.length, reads: t && t.discReads, bytes: t && t.discBytes, errors: t && t.errors, raf: extra.raf, badge: extra.badge, hasModule: extra.hasModule, visibility: extra.visibility };
      result.samples.push(sample);
      console.log(`[${tag}] t=${s}s state=${sample.state} fps=${JSON.stringify(sample.fpsLast5)} reads=${sample.reads} raf=${sample.raf} badge=${sample.badge}`);
    }
    if (s === 10 || s === 30 || s === 60 || s === 120) {
      await page.screenshot({ path: `${OUT}/${tag}-t${s}.png` });
    }
  }
  // Final probes: try getFrames directly, dump the debug log, check canvas pixels.
  const final = await page.evaluate(() => {
    const out = {};
    try { out.getFrames = window.__ps2PlayModule ? window.__ps2PlayModule.getFrames() : 'no-module'; } catch (e) { out.getFrames = 'THREW: ' + e.message; }
    try {
      const c = document.getElementById('outputCanvas');
      out.canvas = { w: c.width, h: c.height, cw: c.clientWidth, ch: c.clientHeight };
      // Read back pixels via a 2D canvas (works only if preserveDrawingBuffer;
      // if black here it may just mean the buffer was cleared — screenshot is truth).
      const c2 = document.createElement('canvas'); c2.width = 64; c2.height = 48;
      const ctx = c2.getContext('2d'); ctx.drawImage(c, 0, 0, 64, 48);
      const d = ctx.getImageData(0, 0, 64, 48).data;
      let nonBlack = 0; for (let i = 0; i < d.length; i += 4) { if (d[i] > 10 || d[i + 1] > 10 || d[i + 2] > 10) nonBlack++; }
      out.canvasPixelsNonBlack = nonBlack + '/' + (64 * 48);
    } catch (e) { out.canvas = 'ERR ' + e.message; }
    const el = document.getElementById('testlog');
    out.debugLog = el ? el.textContent : '';
    return out;
  }).catch((e) => ({ error: String(e) }));
  result.final = final;
  result.consoleLines = consoleLines;
  console.log(`[${tag}] FINAL getFrames=${final.getFrames} canvasPixelsNonBlack=${final.canvasPixelsNonBlack} canvas=${JSON.stringify(final.canvas)}`);
  console.log(`[${tag}] debugLog tail:\n${(final.debugLog || '').split('\n').slice(-25).join('\n')}`);
  await page.close();
  return result;
}

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: CHROME,
    userDataDir: OUT + '/profile',
    args: [
      '--no-sandbox',
      '--disable-dev-shm-usage',
      '--use-angle=swiftshader',
      '--enable-unsafe-swiftshader',
      // NOTE: deliberately NO --autoplay-policy flag — match the phone's default policy.
      '--window-size=800,760',
      '--no-first-run',
      '--disable-default-apps',
      '--crash-dumps-dir=' + OUT,
    ],
  });
  const results = [];
  for (const arm of [
    { name: 'A-mobile-tap', mobile: true, desc: 'mobile emulation + tap boot (Mars repro)' },
    { name: 'B-desktop-tap', mobile: false, desc: 'desktop viewport + click boot (control)' },
  ]) {
    try { results.push(await runArm(browser, arm)); }
    catch (e) { console.error(`[${arm.name}] FATAL ${e.stack}`); results.push({ arm: arm.name, state: 'harness-error', error: String(e) }); }
  }
  fs.writeFileSync(OUT + '/mobile-repro-results.json', JSON.stringify(results, null, 2));
  await browser.close();
  console.log('DONE');
})().catch((e) => { console.error('FATAL ' + e.stack); process.exit(1); });

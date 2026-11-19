// Boot test + load metrics in headless Chromium (docs/tech/ASSET-PIPELINE-2026.md §6).
//   node tools/perf/load_metrics.mjs <base-url> [out.json]
// base-url e.g. http://127.0.0.1:8765/western-heart/  or the live site.
// For each mode (raw = original GLBs via ?raw, cooked = default) on a
// simulated phone 4G link (12 Mbps down, 70 ms RTT, 4x CPU slowdown), cold cache:
//   - boot: navigation -> menu-interactive (loadperf mark), console errors
//   - fight models: time + bytes to load the fighter models below
// Needs playwright-core (or playwright) and a Chrome/Chromium (CHROME env or /usr/bin/google-chrome).
import { writeFileSync } from 'node:fs';
let pw;
try { pw = await import('playwright-core'); } catch { pw = await import('playwright'); }
const base = process.argv[2] || 'http://127.0.0.1:8765/western-heart/';
const out = process.argv[3];
const MODELS = (process.env.WH_MODELS || 'pantera,demonio,steve-fox,diablo').split(',');
const browser = await pw.chromium.launch({
  executablePath: process.env.CHROME || '/usr/bin/google-chrome',
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
});
async function run(mode) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true,
    serviceWorkers: 'block' });
  const page = await ctx.newPage();
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  const failed = [];
  page.on('response', (r) => { if (r.status() >= 400) failed.push(r.status() + ' ' + r.url()); });
  const cdp = await ctx.newCDPSession(page);
  await cdp.send('Network.enable');
  await cdp.send('Network.setCacheDisabled', { cacheDisabled: true });
  if (!process.env.WH_NO_THROTTLE) {
    await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 70,
      downloadThroughput: 12e6 / 8, uploadThroughput: 4e6 / 8 });
    await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
  }
  let bytes = 0;
  cdp.on('Network.loadingFinished', (e) => { bytes += e.encodedDataLength; });
  const url = base + 'game/index.html' + (mode === 'raw' ? '?raw' : '');
  const t0 = Date.now();
  await page.goto(url, { waitUntil: 'load', timeout: 300000 });
  await page.waitForFunction(() => window.__loadperf && window.__loadperf.marks && window.__loadperf.marks['menu-interactive'],
    null, { timeout: 300000 }).catch(() => {});
  const boot = await page.evaluate(() => {
    const m = (window.__loadperf && window.__loadperf.marks) || {};
    return m['menu-interactive'] ? Math.round(m['menu-interactive'] - (m['boot-start'] || 0)) : null;
  });
  const bootBytes = bytes;
  bytes = 0;
  const fight = await page.evaluate(async (ids) => {
    const { assets, MODEL_URLS } = await import(new URL('js/assets.js', location.href).href);
    const ok = ids.filter((i) => MODEL_URLS[i]);
    const t = performance.now();
    await assets.loadModels(ok);
    return { ms: Math.round(performance.now() - t), ids: ok };
  }, MODELS).catch((e) => ({ error: String(e) }));
  const res = { mode, boot_ms: boot, boot_bytes: bootBytes, fight_models: fight, fight_bytes: bytes,
    wall_ms: Date.now() - t0, console_errors: errors, failed_requests: failed };
  await ctx.close();
  return res;
}
const results = [];
for (const m of (process.env.WH_MODES || 'raw,cooked').split(',')) {
  const r = await run(m);
  console.log(JSON.stringify(r));
  results.push(r);
}
await browser.close();
if (out) writeFileSync(out, JSON.stringify({ base, models: MODELS, network: process.env.WH_NO_THROTTLE ? 'unthrottled' : '12Mbps/70ms RTT, CPU x4', results }, null, 1));

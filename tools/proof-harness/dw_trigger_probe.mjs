// dw_trigger_probe.mjs — trigger-only probe: does ozhe_power read as a
// grounded power-up (crouch-then-rise, feet on the floor) when it replaces
// dwup00 as Pantera's surge-trigger? Run against a server serving the
// OVERLAY pantera pack (surge-trigger -> ozhe_power) — the repo pack still
// points at dwup00. Captures 12 frames of the trigger only.
// usage: CHROME_PATH=... NODE_PATH=/tmp/probe-env/node_modules node dw_trigger_probe.mjs <game-url> <outdir>
import { createRequire } from 'module';
import fs from 'fs';
const { chromium } = createRequire(import.meta.url)('playwright-core');
const [,, base, out] = process.argv;
if (!base || !out) { console.error('usage: node dw_trigger_probe.mjs <game-url> <outdir>'); process.exit(2); }
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || '/var/tmp/ms-playwright/chromium-1254/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'],
});
const page = await browser.newPage({ viewport: { width: 900, height: 900 } });
const logs = [];
page.on('console', m => { const t = m.text(); if (/WH-DW|WH-T7|pageerror|Error|fight load failed/.test(t)) logs.push(`[${m.type()}] ${t}`); });
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
await page.route(/workers\.dev/, r => r.abort());
await page.goto(`${base}?quick=pantera,demonio,shrine`, { waitUntil: 'load', timeout: 120000 });
const t0 = Date.now();
let ready = false;
while (Date.now() - t0 < 240000) {
  ready = await page.evaluate(() => { const g = window.__game; return !!(g && g.p1 && g.p1.t3actions && Object.keys(g.p1.t3actions).length && g.roundState === 'fight'); }).catch(() => false);
  if (ready) break;
  await page.waitForTimeout(2000);
}
console.log('READY', ready, `after ${((Date.now() - t0) / 1000).toFixed(0)}s`);
if (!ready) { console.log('LOGS:\n' + logs.join('\n')); await browser.close(); process.exit(1); }
await page.evaluate(() => { const g = window.__game; g.ai = { update() {}, reset() {} }; });
await page.waitForTimeout(1500);
const cdp = await page.context().newCDPSession(page);
const shot = async (file) => {
  try {
    const r = await Promise.race([cdp.send('Page.captureScreenshot', { format: 'png' }), new Promise((_, rej) => setTimeout(() => rej(new Error('shot timeout')), 60000))]);
    fs.writeFileSync(file, Buffer.from(r.data, 'base64'));
    return true;
  } catch (e) { logs.push('SHOT ' + file + ' ' + e.message); return false; }
};
// Which clip is the trigger pointing at? (proves the overlay pack is live)
const trig = await page.evaluate(async () => {
  const g = window.__game, f = g.p1;
  f.meter = f.maxMeter;
  if (!f.surgeForm) f.startSurgeForm();
  return { surgeForm: f.surgeForm, triggerAction: f._dwTriggerAction ? f._dwTriggerAction() : null, dwActions: Object.keys(f.t3actions || {}).filter(n => n.startsWith('dw:')) };
});
console.log('TRIGGER', JSON.stringify(trig));
for (let i = 0; i < 12; i++) {
  await page.waitForTimeout(150);
  await shot(`${out}/frame_${String(i).padStart(3, '0')}.png`);
}
const plan = await page.evaluate(() => { const f = window.__game.p1; return { state: f.state, surgeForm: f.surgeForm, meter: f.meter, actions: Object.keys(f.t3actions || {}).filter(n => n.startsWith('dw:')) }; });
console.log('PLAN', JSON.stringify(plan));
console.log('LOGS:\n' + logs.join('\n'));
await browser.close();
console.log('DONE', out);

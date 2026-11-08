// dw_probe.mjs — Devil Within retarget pilot proof probe.
// Captures Pantera's three DW pilot moves in the live game (headless Chromium
// + software WebGL) and prints the attack plans so the retarget can be checked
// against the game state, not just files:
//   beam    — the surge attack (costs 100 meter; the probe sets it full first)
//   trigger — Soul Surge Bloom trigger, plays once when Surge Form starts
//   throw   — Surge Form front throw 1+3 (the DW thrower clip replaces the
//             T3 thrower action in _bindThrowPair; the victim keeps the T3
//             reaction and the pair root still follows the pack anchors)
// Two probe-setup faults the first runs hit, fixed here:
//   (1) the surge attack costs 100 meter — tryAttack('surge') returns false
//       without it; set f.meter = f.maxMeter first.
//   (2) startSurgeForm() TOGGLES: calling it while the form is already on
//       turns it OFF. Only call it when surgeForm is false. (Software
//       rendering runs the game in slow motion, so the 25 s form outlasts
//       minutes of real time.)
// The screenshots are slow under software WebGL (~25 s each); the game runs
// in slow motion, so a throw may not connect within the capture window —
// the plan + the dw: action list are the check, and the frames are watched
// afterwards (contact sheets via ffmpeg tile). Assemble a clip with:
//   ffmpeg -framerate 8 -i <dir>/frame_%03d.png -c:v libx264 -pix_fmt yuv420p <dir>.mp4
// usage: node dw_probe.mjs <game-url> <outdir> [p1] [p2] [stage]
//   game-url: the served game, e.g. http://127.0.0.1:8765/game/index.html
//   Requires: playwright-core + a Chrome for Testing binary (set
//   CHROME_PATH, or edit the executablePath below). The overlay is served by
//   tools/proof-harness/dw_server.mjs (a Node static server — python
//   http.server drops concurrent module fetches: HTTP/1.0 + a 5-deep listen
//   backlog RSTs connections when the game's ~100-file module graph loads,
//   surfacing as "Failed to fetch dynamically imported module").
//   The game also needs game/vendor/ + game/css/ + game/netplay/ present
//   (a sparse checkout lacks them) and packages/creation-suite/ (statically
//   imported by game/js/customization-consumer.js) — fetch them into the
//   overlay or the module graph fails to load and window.__game never sets.
import { createRequire } from 'module';
import fs from 'fs';
const { chromium } = createRequire(import.meta.url)('playwright-core');

const [,, base, out, p1 = 'pantera', p2 = 'demonio', stage = 'shrine'] = process.argv;
if (!base || !out) { console.error('usage: node dw_probe.mjs <game-url> <outdir> [p1] [p2] [stage]'); process.exit(2); }
fs.mkdirSync(out, { recursive: true });
const logs = [];
const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || '/var/tmp/ms-playwright/chromium-1254/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'],
});
const page = await browser.newPage({ viewport: { width: 900, height: 900 } });
page.on('console', m => { const t = m.text(); if (/WH-DW|WH-T7|pageerror|Error|fight load failed/.test(t)) logs.push(`[${m.type()}] ${t}`); });
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
await page.route(/workers\.dev/, r => r.abort());
await page.goto(`${base}?quick=${p1},${p2},${stage}`, { waitUntil: 'load', timeout: 120000 });
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
async function captureMove(tag, triggerFn, frames, stepMs) {
  const dir = `${out}/${tag}`;
  fs.mkdirSync(dir, { recursive: true });
  const info = await page.evaluate(triggerFn);
  for (let i = 0; i < frames; i++) {
    await page.waitForTimeout(stepMs);
    await shot(`${dir}/frame_${String(i).padStart(3, '0')}.png`);
  }
  const plan = await page.evaluate(() => { const f = window.__game.p1; return { plan: f._atkPlan, state: f.state, surgeForm: f.surgeForm, meter: f.meter, actions: Object.keys(f.t3actions || {}).filter(n => n.startsWith('dw:')) }; });
  console.log(tag, 'TRIGGER', JSON.stringify(info), 'PLAN', JSON.stringify(plan));
  return plan;
}
const untilFn = `const until = async (cond, ms) => { const tEnd = Date.now() + ms; while (!cond() && Date.now() < tEnd) await new Promise(res => setTimeout(res, 20)); };`;
// 1) SURGE BEAM — full meter first (the surge attack costs 100).
await captureMove('beam', () => {
  const g = window.__game, f = g.p1;
  return (async () => {
    const until = async (cond, ms) => { const tEnd = Date.now() + ms; while (!cond() && Date.now() < tEnd) await new Promise(res => setTimeout(res, 20)); };
    await until(() => f.state === 'idle', 40000);
    f.meter = f.maxMeter;
    const ok = f.tryAttack('surge');
    return { ok, attackName: f.attackName, state: f.state, meter: f.meter };
  })();
}, 12, 100);
// 2) SURGE BLOOM TRIGGER — full meter, start Surge Form (only if off — it toggles).
await captureMove('trigger', () => {
  const g = window.__game, f = g.p1;
  return (async () => {
    f.meter = f.maxMeter;
    if (!f.surgeForm) f.startSurgeForm();
    return { surgeForm: f.surgeForm, meter: f.meter };
  })();
}, 12, 150);
// 3) SURGE FORM THROW — re-enter the form only if off, wait out the 1.03 s
//    trigger clip, then press front throw 1+3 with P2 in range.
await captureMove('throw', () => {
  const g = window.__game, f = g.p1, v = g.p2;
  return (async () => {
    const until = async (cond, ms) => { const tEnd = Date.now() + ms; while (!cond() && Date.now() < tEnd) await new Promise(res => setTimeout(res, 20)); };
    await until(() => f.state === 'idle', 40000);
    f.meter = f.maxMeter;
    if (!f.surgeForm) f.startSurgeForm();
    await until(() => f.state === 'idle', 30000);
    v.root.position.set(f.root.position.x + f.facing * 1.2, v.root.position.y, f.root.position.z);
    v.facing = -f.facing;
    const ok = f.tryAttack('1+3');
    return { ok, attackName: f.attackName, state: f.state, surgeForm: f.surgeForm };
  })();
}, 16, 150);
console.log('LOGS:\n' + logs.join('\n'));
await browser.close();
console.log('DONE', out);

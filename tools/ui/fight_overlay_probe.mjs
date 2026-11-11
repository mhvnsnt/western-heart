// tools/ui/fight_overlay_probe.mjs — screenshot a fight while hits land, in a normal fight and in practice, and list
// every visible overlay element over the fight (owner 2026-11-11: no debug / practice data on screen in normal fights).
//
// usage: NO_REMOTE=1 node tools/ui/fight_overlay_probe.mjs <game-url> <out-dir> [p1] [p2] [w] [h]
// writes <out-dir>/normal.png, <out-dir>/practice.png, <out-dir>/overlays.json
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
const { chromium } = createRequire(import.meta.url)('playwright');
const [,, base, outDir, p1 = 'pantera', p2 = 'thor', wArg = '960', hArg = '540'] = process.argv;
fs.mkdirSync(outDir, { recursive: true });
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: +wArg, height: +hArg }, deviceScaleFactor: 1 });
if (process.env.NO_REMOTE) await page.route(/workers\.dev/, (r) => r.abort());
await page.goto(`${base}?quick=${p1},${p2},shrine`, { waitUntil: 'load', timeout: 180000 });
const t0 = Date.now();
while (Date.now() - t0 < 300000) {
  if (await page.evaluate(() => { const g = window.__game; return !!(g && g.p1 && g.p1.t3actions && Object.keys(g.p1.t3actions).length && g.roundState === 'fight'); }).catch(() => false)) break;
  await page.waitForTimeout(1000);
}
// land hits: P2 stands still, P1 jabs from close range; HP held so the round never ends
const landHits = async (training) => page.evaluate(async (training) => {
  const g = window.__game;
  g.ai = { update() {}, reset() {} }; g.roundTime = 0; g.timer = Infinity;
  if (training) { g.training = true; if (g.ui.attackDataClear) g.ui.attackDataClear(true); }
  const keep = setInterval(() => { g.p1.hp = g.p1.maxHp; if (g.p2.hp < g.p2.maxHp * 0.6) g.p2.hp = g.p2.maxHp; }, 100);
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  let hits = 0;
  for (let i = 0; i < 6; i++) {
    g.p2.root.position.x = g.p1.root.position.x + (g.p1.facing || 1) * 0.9;
    const before = g.p2.hp;
    for (let k = 0; k < 400 && g.p1.state !== 'idle'; k++) await wait(25);
    g.p1.tryAttack(['1', '2', '1', '4', '3', '2'][i]);
    for (let k = 0; k < 400 && g.p2.hp === before; k++) await wait(25);
    if (g.p2.hp !== before) hits++;
  }
  clearInterval(keep);
  return hits;
}, training);
// every fixed-position overlay element that is visible right now (not the canvas, not touch controls)
const overlays = () => page.evaluate(() => {
  const out = [];
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el);
    if (cs.position !== 'fixed' && cs.position !== 'absolute') continue;
    if (el.closest('#touch-controls') || el.tagName === 'CANVAS') continue;
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2 || cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity < 0.05) continue;
    const txt = (el.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 80);
    if (!txt) continue;
    out.push({ id: el.id || null, cls: String(el.className || '').slice(0, 40), text: txt });
  }
  return out;
});
// mean render() time over the next frames, the render scale and the fighters' clip prewarm state
const frameStats = () => page.evaluate(async () => {
  const g = window.__game, A = g.arena; const t = []; const r0 = A.render.bind(A);
  A.render = function () { const s = performance.now(); r0(); t.push(performance.now() - s); };
  await new Promise((res) => { let n = 0; const f = () => (++n >= 6 ? res() : requestAnimationFrame(f)); requestAnimationFrame(f); });
  A.render = r0;
  return { renderMs: t.map((x) => +x.toFixed(1)), scale: A.renderer.getPixelRatio(), composerScale: A.composer._pixelRatio,
    warm: [g.p1, g.p2].map((f) => f && { left: f.prewarmLeft, done: !!f._warmDone }) };
});
const report = {};
report.normalHits = await landHits(false);
await page.waitForTimeout(150);
report.normal = await overlays();
report.normalFrame = await frameStats();
await page.screenshot({ path: path.join(outDir, 'normal.png'), timeout: 180000 });
report.practiceHits = await landHits(true);
await page.waitForTimeout(150);
report.practice = await overlays();
report.practiceFrame = await frameStats();
await page.screenshot({ path: path.join(outDir, 'practice.png'), timeout: 180000 });
fs.writeFileSync(path.join(outDir, 'overlays.json'), JSON.stringify(report, null, 1));
console.log(JSON.stringify(report, null, 1));
await browser.close();

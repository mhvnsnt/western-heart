// Lane H: isolate why the select preview drops parts. node probe.mjs URL OUTDIR id
//   env ATTIRES='{"negativo":"n3g4tiv0"}' presets the saved attire map.
const { chromium } = await import('/opt/node22/lib/node_modules/playwright/index.mjs');
import fs from 'fs';
const [,, URL, out, id = 'negativo'] = process.argv;
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const ctx = await browser.newContext({ viewport: { width: +(process.env.VW || 844), height: +(process.env.VH || 390) }, deviceScaleFactor: +(process.env.DPR || 2), isMobile: true, hasTouch: true,
  userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' });
if (process.env.ATTIRES) await ctx.addInitScript((a) => { try { if (!sessionStorage.getItem('lh')) { localStorage.setItem('wh_attires_v1', a); sessionStorage.setItem('lh', '1'); } } catch (_) {} }, process.env.ATTIRES);
const page = await ctx.newPage();
const logs = [];
page.on('console', m => logs.push(`[${m.type()}] ${m.text()}`));
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
await page.goto(URL, { waitUntil: 'load', timeout: 120000 });
await page.waitForFunction(() => window.__modes && window.__selectScreen, null, { timeout: 120000 });
await sleep(1000);
await page.evaluate(() => window.__modes.startMode('versus'));
await sleep(2500);
await page.evaluate((i) => window.__selectScreen.selectById(i), id);
await sleep(300);
await page.waitForFunction(() => !window.__selectScreen._panes.p1._loading, null, { timeout: 120000 });
await page.waitForFunction(() => !!window.__selectScreen._panes.p1.model, null, { timeout: 30000 })
  .catch(() => { console.log(logs.filter(l => /WH|error/i.test(l)).slice(-15).join('\n')); process.exit(3); });
await sleep(1500);
const shot = async (n) => { const el = await page.$('#pane-p1'); await el.screenshot({ path: `${out}/${id}_${n}.png` }); };
const ev = (f) => page.evaluate(f);
await shot('0_asis');
// A: no frustum culling at all
await ev(() => { window.__selectScreen._panes.p1.model.traverse(o => { if (o.isMesh) o.frustumCulled = false; }); });
await sleep(600); await shot('A_nocull');
// A2: culling back on, skinned spheres recomputed from the live pose
await ev(() => { window.__selectScreen._panes.p1.model.traverse(o => { if (o.isMesh) { o.frustumCulled = true; if (o.isSkinnedMesh) o.computeBoundingSphere(); } }); });
await sleep(600); await shot('A2_resphere');
// C: every material opaque
await ev(() => { const p = window.__selectScreen._panes.p1; p._tr = []; p.model.traverse(o => { if (o.isMesh) for (const m of [].concat(o.material)) { p._tr.push([m, m.transparent, m.depthWrite]); m.transparent = false; m.depthWrite = true; m.needsUpdate = true; } }); });
await sleep(900); await shot('C_opaque');
await ev(() => { const p = window.__selectScreen._panes.p1; for (const [m, t, d] of p._tr) { m.transparent = t; m.depthWrite = d; m.needsUpdate = true; } });
// D: opaque clear
await ev(() => { window.__selectScreen._panes.p1.renderer.setClearColor(0x303030, 1); });
await sleep(800); await shot('D_opaqueclear');
await ev(() => { window.__selectScreen._panes.p1.renderer.setClearColor(0x000000, 0); });
// E: only the face mesh, everything else hidden
await ev(() => { const p = window.__selectScreen._panes.p1; p.model.traverse(o => { if (o.isMesh) o.visible = /Face|Mesh004/.test(o.material.name || '') ; }); });
await sleep(800); await shot('E_faceonly');
await ev(() => { const p = window.__selectScreen._panes.p1; p.model.traverse(o => { if (o.isMesh) o.visible = true; }); });
// B: stop the stance (bind pose)
await ev(() => { const p = window.__selectScreen._panes.p1; p.mixer.stopAllAction(); p.aim = null; p.model.traverse(o => { if (o.isSkinnedMesh) o.skeleton.pose(); }); p.mixer = null; p.hasStance = true; });
await sleep(800); await shot('B_bindpose');
fs.writeFileSync(`${out}/${id}_logs.txt`, logs.join('\n'));
await browser.close();

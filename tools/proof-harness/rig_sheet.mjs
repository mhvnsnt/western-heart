// Roster rig sweep: rest pose + T3 stance for every game model key
//
// node tools/proof-harness/rig_sheet.mjs OUTDIR [key1,key2,...|all] [bank]
// For each model key (default: every MODEL_URLS key in game/js/assets.js) drives game/poselab.html:
//   rest_<key>.png    the game's own instance at rest, cameras on +Z (left) and +X (right) (after the game's facing
//                     correction): the face must be visible, or the game has the facing wrong;
//   stance_<key>.png  the T3 stance retargeted by the game (front + side, target column only);
// and writes results.json (game facing, swapLR, per-bone direction error vs the source, errors).
// Tile the PNGs into labelled sheets with tools/model-audit/tile_sheet.py.
//
// Owner 2026-10-22: "Need to get the bind pose overlays and heat mapping and skinning and rigging
// ... fully done for every character every glb model". Proof harness, Claude session 2026-10-22.
// Serve the repo first:  python3 -m http.server 8765  (from the repo root).
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright/index.mjs');
import fs from 'fs';
const [,, out = 'rig_sheet', which = 'all', bank = 'king'] = process.argv;
fs.mkdirSync(out, { recursive: true });
let keys;
if (which === 'all') {
  const src = fs.readFileSync(new URL('../../game/js/assets.js', import.meta.url), 'utf8');
  const body = src.match(/export const MODEL_URLS = \{([\s\S]*?)\n\};/)[1];
  keys = [...new Set([...body.matchAll(/^\s*'?([\w-]+)'?\s*:/gm)].map(m => m[1]))];
} else keys = which.split(',');
const PER_PAGE = 8; // fresh page every few models: the asset cache keeps every GLB in memory
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const results = [];
const resFile = `${out}/results.json`;
for (let i = 0; i < keys.length; i += PER_PAGE) {
  const page = await browser.newPage({ viewport: { width: 1200, height: 960 } });
  const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  await page.goto(`http://127.0.0.1:${process.env.PORT || 8765}/game/poselab.html`, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__poselab, null, { timeout: 60000 });
  const cdp = await page.context().newCDPSession(page);
  const shot = async (file, clip) => {
    const r = await cdp.send('Page.captureScreenshot', { format: 'png', clip: { ...clip, scale: 1 } });
    fs.writeFileSync(file, Buffer.from(r.data, 'base64'));
  };
  for (const key of keys.slice(i, i + PER_PAGE)) {
    const rec = { key };
    const t0 = Date.now();
    try {
      const r = await page.evaluate((k) => window.__poselab.rest(k), key);
      rec.facing = r.facing;
      await shot(`${out}/rest_${key}.png`, { x: 0, y: 0, width: 1200, height: 900 }); // left: camera on +Z, right: camera on +X
    } catch (e) { rec.restError = e.message.split('\n')[0]; }
    try {
      const r = await page.evaluate((a) => window.__poselab.show(a), { model: key, bank, clip: 'stance', t: 0.3 });
      Object.assign(rec, { swapLR: r.swapLR, maxErr: r.maxErr, dirErrDeg: r.dirErrDeg, headAboveHips: r.tgtHeadAboveHips, srcHeadAboveHips: r.srcHeadAboveHips });
      rec.footYaw = await page.evaluate(() => window.__poselab.footYaw());
      await shot(`${out}/stance_${key}.png`, { x: 600, y: 0, width: 600, height: 900 });
    } catch (e) { rec.stanceError = e.message.split('\n')[0]; }
    rec.ms = Date.now() - t0;
    if (errs.length) rec.pageErrors = errs.splice(0);
    results.push(rec);
    fs.writeFileSync(resFile, JSON.stringify(results, null, 1));
    console.log(JSON.stringify({ key, facing: rec.facing, swapLR: rec.swapLR, maxErr: rec.maxErr, err: rec.restError || rec.stanceError, ms: rec.ms }));
  }
  await page.close();
}
await browser.close();

// Creation suite MOVESET tab proof: node tools/proof-harness/suite_moveset.mjs OUTDIR [width height]
// Opens customization/creation-suite-ui, picks a fighter in the MOVESET tab, opens one input's move
// library, assigns an alternate move, and checks the saved loadout is what the fight engine reads
// (game/js/movesets.js resolveMove via localStorage wh_moveset_loadout_v1). Screens are captured
// at each step. Proof harness from the 2026-10-21 Claude session (tools/TOOLS-INDEX.md).
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright/index.mjs');
import fs from 'fs';
const [, , out = 'suite', w = '1280', h = '720', FID = 'rave', INPUT = '1'] = process.argv;
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: +w, height: +h }, isMobile: +w < 600, hasTouch: +w < 600 });
const errs = [];
page.on('pageerror', e => errs.push(e.message));
page.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text().slice(0, 160)); });
await page.goto(`http://127.0.0.1:${process.env.PORT || 8765}/customization/creation-suite-ui/index.html`, { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(3000);
await page.evaluate(() => document.querySelector('.rail-btn[data-tab="moveset"]').click());
await page.waitForFunction(() => document.querySelector('#ms-fid'), null, { timeout: 30000 });
await page.evaluate((fid) => { const s = document.querySelector('#ms-fid'); s.value = fid; s.dispatchEvent(new Event('change')); }, FID);
await page.waitForFunction(() => document.querySelectorAll('.ms-row').length > 0, null, { timeout: 30000 });
await page.screenshot({ path: `${out}/1_moveset_tab_${w}.png` });
const count = await page.evaluate(() => document.querySelector('#ms-count').textContent);
await page.evaluate((n) => document.querySelector(`.ms-row[data-n="${CSS.escape(n)}"]`).click(), INPUT);
await page.waitForFunction(() => document.querySelectorAll('#modal-body .ms-row').length > 0, null, { timeout: 30000 });
await page.screenshot({ path: `${out}/2_library_${w}.png` });
const picked = await page.evaluate(() => {
  const rows = [...document.querySelectorAll('#modal-body .ms-row')];
  const r = rows[rows.length - 1]; const key = r.dataset.k; const name = r.querySelector('.ms-name').textContent; r.click(); return { key, name };
});
await page.waitForTimeout(800);
await page.screenshot({ path: `${out}/3_assigned_${w}.png` });
const check = await page.evaluate(async ([fid, n]) => {
  const MS = await import('/game/js/movesets.js');
  const lo = JSON.parse(localStorage.getItem('wh_moveset_loadout_v1') || '{}')[fid] || {};
  MS.setMovesetBase('/game/assets/movesets/');
  await MS.ensureMovesets([fid]);
  const r = MS.resolveMove(fid, n);
  return { saved: lo[n], engineFires: r && r.key, engineName: r && r.move.name };
}, [FID, INPUT]);
const res = { fighter: FID, input: INPUT, list: count, picked, check, errors: errs };
fs.writeFileSync(`${out}/result.json`, JSON.stringify(res, null, 1));
console.log(JSON.stringify(res, null, 1));
await browser.close();

// Moveset editor e2e (Grok, 2026-10-28). Serve the repo root on $WH_URL.
// Run: node test/e2e/moveset-editor.e2e.mjs <outDir> [fighter ...]
// For every fighter in game/assets/movesets/index.json, in the real Creation Suite UI:
// OPEN the MOVESET tab and pick the fighter (input rows render), EDIT: tap the first input,
// open ALL MOVES and tap a move other than the current one, SAVE: the loadout in
// localStorage wh_moveset_loadout_v1 holds it and the fight engine (movesets.js resolveMove)
// resolves that input to it, RELOAD: after a page reload the edit is still there and the row
// is marked edited, then RESET TO DEFAULT puts the input back. Writes <outDir>/editor.json
// and a screenshot of the editor for the first few fighters.
import { chromium } from 'playwright';
import fs from 'node:fs';
const BASE = process.env.WH_URL || 'http://127.0.0.1:8811';
const OUT = process.argv[2] || 'moveset-editor-out';
const SHOTS = +(process.env.WH_EDITOR_SHOTS || 4);
fs.mkdirSync(OUT, { recursive: true });
const idx = JSON.parse(fs.readFileSync(new URL('../../game/assets/movesets/index.json', import.meta.url), 'utf8'));
let FIGHTERS = process.argv.slice(3); if (!FIGHTERS.length) FIGHTERS = Object.keys(idx.fighters);
const b = await chromium.launch({ executablePath: process.env.CHROME || undefined, args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader'] });
const p = await b.newPage({ viewport: { width: 1280, height: 860 } });
const errs = []; p.on('pageerror', (e) => errs.push(String(e).slice(0, 200)));
const URL_ = BASE + '/customization/creation-suite-ui/index.html';
const LO = 'wh_moveset_loadout_v1';
async function openTab() {
  await p.goto(URL_); await p.waitForSelector('.rail-btn[data-tab="moveset"]', { timeout: 120000 });
  await p.click('.rail-btn[data-tab="moveset"]'); await p.waitForSelector('#ms-fid', { timeout: 120000 });
}
async function pick(fid) {
  await p.selectOption('#ms-fid', fid);
  await p.waitForFunction((f) => { const s = document.querySelector('#ms-fid'); return s && s.value === f && document.querySelectorAll('#ms-list .ms-row').length > 0; }, fid, { timeout: 60000 });
}
const rows = []; let n = 0;
await openTab();
for (const fid of FIGHTERS) {
  const r = { fighter: fid, open: false, edit: false, save: false, reload: false, reset: false };
  try {
    await pick(fid); r.open = true;
    r.inputs = await p.$$eval('#ms-list .ms-row', (e) => e.length);
    const input = await p.$eval('#ms-list .ms-row', (e) => e.dataset.n); r.input = input;
    await p.click('#ms-list .ms-row');
    await p.waitForSelector('#modal-body .ms-tab[data-t="all"]'); await p.click('#modal-body .ms-tab[data-t="all"]');
    await p.waitForSelector('#modal-body .ms-lib .ms-row');
    const cur = await p.evaluate(async ([f, i]) => { const MS = await import('/game/js/movesets.js'); const x = MS.resolveMove(f, i); return x && x.key; }, [fid, input]);
    const keys = await p.$$eval('#modal-body .ms-lib .ms-row', (e) => e.map((x) => x.dataset.k));
    const want = keys.find((k) => k !== cur && k !== input); r.from = cur; r.to = want;
    if (n < SHOTS) await p.screenshot({ path: `${OUT}/editor-${fid}-library.png` });
    await p.click(`#modal-body .ms-lib .ms-row[data-k="${want.replace(/["\\]/g, '\\$&')}"]`); r.edit = true;
    const saved = await p.evaluate(([k, f, i]) => (JSON.parse(localStorage.getItem(k) || '{}')[f] || {})[i], [LO, fid, input]);
    r.save = saved === want;
    await openTab(); await pick(fid);
    const after = await p.evaluate(async ([f, i]) => { const MS = await import('/game/js/movesets.js'); await MS.ensureMovesets([f]); const x = MS.resolveMove(f, i); return x && x.key; }, [fid, input]);
    const marked = await p.$eval(`#ms-list .ms-row[data-n="${input.replace(/["\\]/g, '\\$&')}"]`, (e) => e.classList.contains('edited')).catch(() => false);
    r.reload = after === want && marked; r.resolvedAfterReload = after;
    if (n < SHOTS) await p.screenshot({ path: `${OUT}/editor-${fid}-edited.png` });
    await p.click(`#ms-list .ms-row[data-n="${input.replace(/["\\]/g, '\\$&')}"]`);
    await p.click('#modal-actions button:has-text("RESET TO DEFAULT"), .modal button:has-text("RESET TO DEFAULT")');
    const back = await p.evaluate(([k, f, i]) => (JSON.parse(localStorage.getItem(k) || '{}')[f] || {})[i], [LO, fid, input]);
    r.reset = back === undefined;
  } catch (e) { r.error = String(e).slice(0, 200); }
  r.ok = r.open && r.edit && r.save && r.reload && r.reset;
  rows.push(r); n++;
  console.log(`${r.ok ? 'PASS' : 'FAIL'} ${fid} ${r.error || ''}`);
}
const sum = { fighters: rows.length, pass: rows.filter((r) => r.ok).length, pageErrors: errs.slice(0, 10) };
fs.writeFileSync(`${OUT}/editor.json`, JSON.stringify({ ...sum, rows }, null, 1));
console.log(`== editor: ${sum.pass}/${sum.fighters} open/edit/save/reload/reset`);
await b.close();

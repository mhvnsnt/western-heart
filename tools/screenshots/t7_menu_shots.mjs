import { chromium } from 'playwright';
// Usage: node tools/screenshots/t7_menu_shots.mjs BASE_URL OUTDIR TAG [private]
// Main menu, mode select (VERSUS submenu), options, select (fresh open + a pick) at the 4 phone sizes.
const [base, outdir, tag, priv] = process.argv.slice(2);
const b = await chromium.launch({ channel: 'chrome', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const sizes = (process.env.SIZES || '390x844,844x390,412x915,915x412').split(',').map(s => s.split('x').map(Number));
for (const [w, h] of sizes) {
  const sn = `${w}x${h}`;
  const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1, isMobile: true, hasTouch: true });
  if (priv) await p.addInitScript(() => { globalThis.__WH_PRIVATE_ASSETS = true; });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto(base, { waitUntil: 'load', timeout: 90000 });
  await p.waitForSelector('#screen-menu [data-mm]', { state: 'visible', timeout: 60000 });
  await p.waitForTimeout(4000);
  const shot = (n) => p.screenshot({ path: `${outdir}/${tag}-${n}-${sn}.png` });
  await shot('menu');
  const m = await p.evaluate(() => { const l = document.getElementById('mm-list').getBoundingClientRect(); const its = [...document.querySelectorAll('#mm-list .mm-item')]; const fit = its.every(e => { const r = e.getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight; }); return { listW: Math.round(l.width), listX: Math.round(l.x), allItemsOnScreen: fit }; });
  await p.evaluate(() => document.querySelector('#mm-list [data-mm="arcade"]').click()); await p.waitForTimeout(900);
  await shot('modes');
  await p.evaluate(() => document.getElementById('mm-sub-back').click()); await p.waitForTimeout(500);
  await p.evaluate(() => { document.querySelector('#mm-list [data-mm="options"]').click(); } ); await p.waitForTimeout(700); await p.evaluate(() => { const b = document.querySelector('[data-action="mode-options"]'); if (b) b.click(); }); await p.waitForTimeout(900);
  const o = await p.evaluate(() => { const s = document.querySelector('#wh-options .wh-sheet'); if (!s) return null; const r = s.getBoundingClientRect(); return { w: Math.round(r.width), h: Math.round(r.height), fits: r.bottom <= innerHeight + 1 }; });
  await shot('options');
  await p.evaluate(() => { document.querySelector('#wh-options')?.classList.remove('show'); });
  await p.evaluate(() => { localStorage.removeItem('wh.select.last.v1'); document.querySelector('#mm-list [data-mm="versus"]').click(); });
  await p.waitForTimeout(600);
  await p.evaluate(() => { const c = document.querySelector('#mm-cards .mm-card[data-action]'); c && c.click(); });
  await p.waitForSelector('#screen-select.active', { timeout: 30000 }).catch(() => {});
  await p.waitForTimeout(7000);
  const first = await p.evaluate(() => ({ first: document.querySelector('#char-grid .char-card')?.dataset.id, cursor: document.querySelector('#char-grid .char-card.cursor-p1')?.dataset.id || null }));
  await shot('select-open');
  await p.evaluate(() => document.querySelector('#char-grid .char-card[data-id="demonio"]')?.click()); await p.waitForTimeout(9000);
  const fig = await p.evaluate(() => { const c = document.getElementById('pane-canvas-p1'); if (!c) return null; const r = c.getBoundingClientRect(); return { w: Math.round(r.width), h: Math.round(r.height) }; });
  await shot('select-pick');
  console.log(sn, JSON.stringify({ menu: m, options: o, select: first, p1pane: fig, errors: [...new Set(errs)].slice(0, 5) }));
  await p.close();
}
await b.close();

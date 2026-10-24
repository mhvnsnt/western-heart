// node capture.js <baseUrl> <outDir> [ids,comma]  — every roster card at 390x844:
// card crop + 3D hero pane crop + probe metrics -> outDir/<id>-card.png, <id>-hero.png, results.jsonl
const pp = require(process.env.PUPPETEER || 'puppeteer-core');
const fs = require('fs'), path = require('path');
const [base, out, only] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const probe = fs.readFileSync(path.join(__dirname, 'probe.js'), 'utf8');
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
async function openSelect(b) {
  const pg = await b.newPage();
  await pg.setViewport({ width: 390, height: 844, hasTouch: true, isMobile: true, deviceScaleFactor: 1 });
  await pg.evaluateOnNewDocument(probe);
  // Older deploys lack the window.__whSelectPanes proof hook: patch it in at fetch time (read-only, in-browser).
  await pg.setRequestInterception(true);
  pg.on('request', async (rq) => {
    if (!/\/js\/select-screen\.js(\?|$)/.test(rq.url())) return rq.continue();
    try {
      const r = await fetch(rq.url()); let t = await r.text();
      if (!t.includes('__whSelectPanes')) t = t.replace(/(const panes = \{[\s\S]*?\n  \};)/, '$1\n  window.__whSelectPanes = panes;');
      rq.respond({ status: 200, contentType: 'application/javascript', body: t });
    } catch (e) { rq.continue(); }
  });
  await pg.goto(base + 'game/index.html', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await sleep(12000);
  await pg.evaluate(() => { document.querySelector('[data-mm="versus"]')?.click(); });
  await sleep(1500);
  await pg.evaluate(() => { [...document.querySelectorAll('[data-action="mode-versus"]')].find(e => e.offsetParent)?.click(); });
  await sleep(4000);
  return pg;
}
(async () => {
  const launch = () => pp.launch({ executablePath: process.env.CHROME || '/usr/bin/google-chrome', headless: 'new',
    args: ['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--mute-audio'] });
  let b = await launch();
  let pg = await openSelect(b);
  let ids = await pg.evaluate(() => [...document.querySelectorAll('#char-grid .char-card')].map(c => c.dataset.id).filter(x => x && x !== '__random'));
  if (only) ids = ids.filter(i => only.split(',').includes(i));
  if (!only) fs.writeFileSync(path.join(out, 'ids.txt'), ids.join('\n'));
  const res = fs.createWriteStream(path.join(out, 'results.jsonl'), { flags: 'a' });
  await pg.close();
  for (const id of ids) {
    const rec = { id };
    try { await b.close(); } catch (e) {}
    b = await launch();
    try { pg = await openSelect(b); } catch (e) { rec.error = 'open: ' + String(e).slice(0, 120); res.write(JSON.stringify(rec) + '\n'); continue; }
    try {
      await pg.evaluate((id) => { const c = document.querySelector(`#char-grid .char-card[data-id="${id}"]`); c.scrollIntoView({ block: 'center' }); c.click(); }, id);
      const t0 = Date.now();
      await sleep(1500);
      while (Date.now() - t0 < 45000) {
        const ok = await pg.evaluate(() => { const p = window.__whSelectPanes.p1; return !!p.model && !p._loading; });
        if (ok) break; await sleep(500);
      }
      await sleep(3000); // let idle settle
      const card = await pg.$(`#char-grid .char-card[data-id="${id}"]`);
      if (card) await card.screenshot({ path: path.join(out, id + '-card.png') });
      const pane = await pg.$('#pane-canvas-p1');
      if (pane) await pane.screenshot({ path: path.join(out, id + '-hero.png') });
      Object.assign(rec, await pg.evaluate(() => window.__whProbe('p1')));
    } catch (e) { rec.error = String(e).slice(0, 200); }
    try { await pg.close(); } catch (e) {}
    res.write(JSON.stringify(rec) + '\n'); console.log(id, rec.error || `arm ${rec.armL}/${rec.armR} bbox ${rec.bboxRatio} zero ${rec.zeroFrac} far ${rec.farFrac} str ${rec.stretchFrac} edge ${rec.edgeFrac} dev ${rec.maxBoneDevDeg}`);
  }
  res.end(); await b.close();
})();

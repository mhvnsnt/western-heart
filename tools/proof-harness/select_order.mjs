// Select-screen order proof: node tools/proof-harness/select_order.mjs OUTDIR [width height]
// Opens the character select (arcade), captures it and lists the tiers in order, so the
// Tripo-first rule (game/data/tripo-fighters.json) can be checked by eye and by data.
// Proof harness from the 2026-10-20/21 Claude session (tools/TOOLS-INDEX.md). Serve the repo
// first: python3 -m http.server 8765 (from the repo root).
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright/index.mjs');
import fs from 'fs';
const [, , out = 'select', w = '1280', h = '720'] = process.argv;
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: +w, height: +h }, isMobile: +w < 600, hasTouch: +w < 600 });
const errs = [];
page.on('pageerror', e => errs.push(e.message));
await page.goto(`http://127.0.0.1:${process.env.PORT || 8765}/game/index.html`, { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(2500);
await page.evaluate(() => window.__modes.startMode('arcade'));
await page.waitForTimeout(4000);
const tiers = await page.evaluate(() => {
  const out = []; let cur = null;
  for (const el of document.querySelectorAll('#char-grid > *')) {
    if (el.classList.contains('strip-tier')) { cur = { tier: el.textContent, ids: [] }; out.push(cur); }
    else if (cur && el.dataset.id) cur.ids.push(el.dataset.id);
  }
  return out;
});
await page.screenshot({ path: `${out}/select_${w}x${h}.png` });
fs.writeFileSync(`${out}/tiers.json`, JSON.stringify({ tiers, errors: errs }, null, 1));
for (const t of tiers) console.log(`${t.tier} (${t.ids.length}): ${t.ids.join(', ')}`);
console.log('page errors:', errs.length);
await browser.close();

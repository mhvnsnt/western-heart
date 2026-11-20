// Phone menu check (Claude 2026-10-23): load the game like a phone (touch, 390x844), screenshot the main menu, tap each visible
// menu button and record whether the screen changed. node menu_tap.mjs <url> <outdir>
const { chromium } = await import('/opt/node22/lib/node_modules/playwright/index.mjs');
import fs from 'fs';
const [,, url, out] = process.argv;
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true,
  userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' });
const page = await ctx.newPage();
const logs = [];
page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') logs.push(`[${m.type()}] ${m.text()}`); });
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
page.on('requestfailed', r => logs.push(`[requestfailed] ${r.url()} ${r.failure() && r.failure().errorText}`));
const t0 = Date.now();
await page.goto(url, { waitUntil: 'load', timeout: 120000 });
await page.waitForTimeout(8000);
await page.screenshot({ path: `${out}/01_menu.png` });
const info = await page.evaluate(() => {
  const vis = (el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0.05; };
  const act = document.querySelector('.screen.active') || document.querySelector('.screen:not(.hidden)');
  const btns = [...document.querySelectorAll('button, [role=button], a, .menu-item, [data-mode], [data-action]')].filter(vis);
  const sheets = [...document.styleSheets].map(s => { try { return s.href || 'inline'; } catch (e) { return 'x'; } });
  return { active: act && act.id, buttons: btns.slice(0, 30).map(b => ({ tag: b.tagName, id: b.id, cls: b.className && String(b.className).slice(0, 40),
    text: (b.innerText || '').trim().slice(0, 30), x: Math.round(b.getBoundingClientRect().x), y: Math.round(b.getBoundingClientRect().y),
    w: Math.round(b.getBoundingClientRect().width), h: Math.round(b.getBoundingClientRect().height),
    top: (() => { const r = b.getBoundingClientRect(); const e = document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2); return e === b || b.contains(e); })() })),
    sheets, title: document.title };
});
fs.writeFileSync(`${out}/menu_info.json`, JSON.stringify(info, null, 1));
console.log('loaded in', Date.now() - t0, 'ms; active screen', info.active, '; buttons', info.buttons.length, '; stylesheets', info.sheets.length);
for (const b of info.buttons) console.log(JSON.stringify(b));
// tap the first few visible buttons that are on top, one at a time from a fresh menu
let n = 0;
for (const b of info.buttons.filter(b => b.top && b.text).slice(0, 4)) {
  await page.goto(url, { waitUntil: 'load' }); await page.waitForTimeout(6000);
  const before = await page.evaluate(() => (document.querySelector('.screen.active') || {}).id);
  await page.touchscreen.tap(b.x + b.w / 2, b.y + b.h / 2);
  await page.waitForTimeout(2500);
  const after = await page.evaluate(() => (document.querySelector('.screen.active') || {}).id);
  await page.screenshot({ path: `${out}/tap_${++n}.png` });
  console.log(`tap "${b.text}" -> screen ${before} => ${after}`);
}
fs.writeFileSync(`${out}/console.log`, logs.join('\n'));
console.log('console errors/warnings:', logs.length);
await browser.close();

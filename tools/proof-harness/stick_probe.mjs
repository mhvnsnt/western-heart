// Joystick touch probe (Claude 2026-10-24): starts a fight in a phone-landscape touch context and drags the
// on-screen stick (nipplejs) with real CDP touch events, then prints what the game read (axisX, up/down, stickDir,
// P1 state) and what a tap on LP recorded. Owner: "any touch to the joystick makes it go down".
//   URL=https://mhvnsnt.github.io/western-heart/game/index.html node tools/proof-harness/stick_probe.mjs
const { chromium } = await import('/opt/node22/lib/node_modules/playwright/index.mjs');
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=angle', '--use-angle=swiftshader'] });
const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 1, isMobile: true, hasTouch: true });
const page = await ctx.newPage(); const cdp = await ctx.newCDPSession(page);
await page.goto(process.env.URL, { waitUntil: 'load' });
await page.waitForFunction(() => window.__modes, null, { timeout: 120000 });
await page.evaluate(() => window.__modes.startMode('arcade'));
await page.evaluate(() => { const a = window.__game.arena; a.render = () => {}; });
await page.evaluate(async () => { await window.__modes.startFight('pantera', 'skull', { mode: 'arcade' }); });
await page.waitForFunction(() => window.__game && window.__game.roundState === 'fight', null, { timeout: 180000 });
await page.evaluate(() => { const g = window.__game; g.ai.update = () => {}; g.timer = 999; });
const info = await page.evaluate(() => {
  const m = window.__game.input._joyManager; const n = m && (m.get ? m.get(0) : null) || (m && m[0]);
  const zone = document.getElementById('joystick').getBoundingClientRect();
  const el = n && n.el ? n.el.getBoundingClientRect() : null;
  return { stored: n && n.position, zoneCentre: { x: zone.x + zone.width / 2, y: zone.y + zone.height / 2 }, nippleEl: el && { x: el.x, y: el.y, w: el.width, h: el.height }, dynamicPage: m && m.options && m.options.dynamicPage };
});
console.log('NIPPLE', JSON.stringify(info));
const z = info.zoneCentre;
const st = () => page.evaluate(() => { const g = window.__game, i = g.input; return { axisX: +(+i.axisX).toFixed(2), down: i.down, up: i.up, udDir: i._udDir, stickDir: i.stickDir, p1: g.p1.state }; });
async function drag(dx, dy, label, hold = 450) {
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: z.x, y: z.y, id: 0 }] });
  await page.waitForTimeout(40);
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: z.x + dx, y: z.y + dy, id: 0 }] });
  await page.waitForTimeout(hold);
  const s = await st();
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  await page.waitForTimeout(300);
  console.log(label.padEnd(34), JSON.stringify(s));
}
await drag(2, 2, 'thumb rests on centre (+2,+2 px)');
await drag(45, 0, 'drag RIGHT 45 px');
await drag(-45, 0, 'drag LEFT 45 px');
await drag(0, 45, 'drag DOWN 45 px (held)');
await drag(0, -45, 'drag UP 45 px (held)', 150);
await drag(40, 8, 'drag right with natural thumb dip');
const rec = await page.evaluate(() => { const tb = window.__game.p1.tekken, r = tb._recordMove.bind(tb); window.__rec = []; tb._recordMove = (n) => { window.__rec.push(n); return r(n); }; const b = document.querySelector('.act-btn[data-btn="1"]').getBoundingClientRect(); return { x: b.x + b.width / 2, y: b.y + b.height / 2 }; });
await page.waitForTimeout(800);
await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: rec.x, y: rec.y, id: 1 }] }); await page.waitForTimeout(60);
await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] }); await page.waitForTimeout(500);
console.log('tap LP (1), stick untouched     ', JSON.stringify(await page.evaluate(() => window.__rec)));
const n2 = await page.evaluate(() => { const m = window.__game.input._joyManager; const n = m.get ? m.get(0) : m[0]; return n && n.position; });
console.log('stored centre after touches:', JSON.stringify(n2));
await browser.close();

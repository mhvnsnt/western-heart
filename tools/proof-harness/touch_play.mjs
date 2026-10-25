// Touch play test (Claude 2026-10-24). Owner: "you're probably using cheat inputs ... instead of tapping the screen and
// playing it like how I play it like a mobile game and with phone taps".
//
// Plays the game the way the owner does on a phone: an iPhone-sized landscape viewport with touch only (no mouse, no
// keyboard), menus reached by TAPS, and the fight driven by real multi-touch events sent through Chrome's touch
// emulation (CDP Input.dispatchTouchEvent): finger 0 drags the on-screen joystick (nipplejs), finger 1 taps the
// 1/2/3/4 / HEAT / RAGE buttons, both at human thumb timing. Nothing calls the game's input or move code directly.
// The page is only READ: which notations P1's move buffer recorded, which animation clip played, P2's HP.
//
//   python3 -m http.server 8765          (repo root)
//   node tools/proof-harness/touch_play.mjs OUTDIR [p1=pantera] [p2=skull]      (PORT=... or URL=... to retarget)
//
// Writes OUTDIR/results.json, OUTDIR/results.txt (one line per case) and a PNG per menu step and per case.
// Every case is a fresh approach from neutral; the CPU is told to stand still during the scripted cases only
// (so a case's result is the owner's input, not the CPU's), then a 20 s free fight runs against the live CPU.
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright/index.mjs');
import fs from 'fs';
const [,, out = 'touch_play', p1 = 'pantera', p2 = 'skull'] = process.argv;
const URL = process.env.URL || `http://127.0.0.1:${process.env.PORT || 8765}/game/index.html`;
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const ctx = await browser.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true,
  userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' });
const page = await ctx.newPage();
const cdp = await ctx.newCDPSession(page);
const logs = [], steps = [];
page.on('console', m => { if (m.type() === 'error') logs.push(`[error] ${m.text()}`); });
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
let shot = 0;
const snap = async (name) => { // a slow software-GL frame must not abort the run: a missed shot is logged, not fatal
  const f = `${out}/${String(++shot).padStart(2, '0')}_${name.replace(/[^a-z0-9+,/.-]+/gi, '_').replace(/\//g, '')}.png`;
  try { await page.screenshot({ path: f, timeout: 90000 }); return f; } catch (e) { logs.push(`[shot] ${name}: ${e.message.split('\n')[0]}`); return null; }
};

// ---- multi-touch: every active finger is sent on every event (CDP semantics) ----
const fingers = new Map(); // id -> {x, y}
const pts = () => [...fingers.entries()].map(([id, p]) => ({ x: p.x, y: p.y, id, radiusX: 8, radiusY: 8, force: 1 }));
async function down(id, x, y) { fingers.set(id, { x, y }); await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: pts() }); }
async function move(id, x, y) { fingers.set(id, { x, y }); await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: pts() }); }
async function up(id) {
  fingers.delete(id);
  if (fingers.size) await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: pts() }); // a missing point = released
  else await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
}
async function boxOf(sel) {
  return page.evaluate((s) => {
    const el = typeof s === 'string' ? document.querySelector(s) : null; if (!el) return null;
    const r = el.getBoundingClientRect(); const st = getComputedStyle(el);
    if (r.width < 2 || r.height < 2 || st.display === 'none' || st.visibility === 'hidden') return null;
    const cx = r.x + r.width / 2, cy = r.y + r.height / 2, top = document.elementFromPoint(cx, cy);
    return { x: cx, y: cy, w: r.width, h: r.height, top: !!top && (top === el || el.contains(top)) };
  }, sel);
}
async function tap(sel, hold = 70) {
  const b = await boxOf(sel); if (!b) return { ok: false, why: 'not visible' };
  await down(9, b.x, b.y); await sleep(hold); await up(9);
  return { ok: true, top: b.top };
}
const activeScreen = () => page.evaluate(() => (document.querySelector('.screen.active') || {}).id || null);
async function waitScreen(id, ms = 30000) {
  const t = Date.now(); while (Date.now() - t < ms) { if (await activeScreen() === id) return true; await sleep(250); } return false;
}

// ---- menus, by taps only ----
await page.goto(URL, { waitUntil: 'load', timeout: 120000 });
await page.waitForFunction(() => window.__modes, null, { timeout: 90000 });
await sleep(2500);
steps.push({ step: 'main menu', screen: await activeScreen(), shot: await snap('menu') });
// a first tap anywhere unlocks audio on phones (the "tap to enable sound" pill)
await tap('#screen-menu', 40); await sleep(400);
let r = await tap('.mm-item[data-mm="arcade"]');
steps.push({ step: 'tap ARCADE', ...r, select: await waitScreen('screen-select', 30000), shot: await snap('after_arcade_tap') });
await page.waitForFunction((id) => !!document.querySelector(`.char-card[data-id="${id}"]`), p1, { timeout: 60000 }).catch(() => {});
await page.evaluate((id) => { const c = document.querySelector(`.char-card[data-id="${id}"]`); if (c) c.scrollIntoView({ block: 'center', inline: 'center' }); }, p1);
await sleep(300);
r = await tap(`.char-card[data-id="${p1}"]`);
await sleep(600);
steps.push({ step: `tap card ${p1}`, ...r, shot: await snap('card_tapped') });
r = await tap('#confirm-fighter');
await sleep(800);
steps.push({ step: 'tap CONFIRM', ...r, screen: await activeScreen(), shot: await snap('confirm_tapped') });
// arcade may pick the opponent and/or show the stage screen: tap through whatever is up
for (let i = 0; i < 6; i++) {
  const s = await activeScreen();
  if (await page.evaluate(() => window.__game && window.__game.roundState)) break;
  if (s === 'screen-stage') {
    const st = await page.evaluate(() => { const c = document.querySelector('#stage-grid [data-id], #stage-grid button, #stage-grid .stage-card'); if (!c) return null; c.setAttribute('data-touch-pick', '1'); return true; });
    if (st) { r = await tap('[data-touch-pick="1"]'); steps.push({ step: 'tap stage', ...r }); await sleep(500); }
    r = await tap('#confirm-stage'); steps.push({ step: 'tap CONFIRM STAGE', ...r, shot: await snap('stage') });
  } else if (s === 'screen-select') {
    r = await tap('#confirm-fighter'); steps.push({ step: 'tap CONFIRM again (P2 / opponent)', ...r });
  }
  await sleep(1500);
}
let reached = await page.waitForFunction(() => window.__game && window.__game.roundState === 'fight', null, { timeout: 120000 }).then(() => true).catch(() => false);
steps.push({ step: 'fight reached by taps', ok: reached, screen: await activeScreen(), shot: await snap('fight_start') });
if (!reached) {
  fs.writeFileSync(`${out}/results.json`, JSON.stringify({ url: URL, steps, logs, error: 'menus did not reach a fight by taps' }, null, 1));
  console.log('FAILED to reach a fight by taps; see', out); await browser.close(); process.exit(2);
}
const opp = await page.evaluate(() => window.__game.p2 && (window.__game.p2.charId || window.__game.p2.id || (window.__game.p2.char && window.__game.p2.char.id)));

// ---- observation only: what P1 recorded, which clip runs, P2 HP ----
await page.evaluate(() => {
  const g = window.__game, tb = g.p1.tekken, rec = tb._recordMove.bind(tb);
  window.__rec = []; tb._recordMove = (n) => { window.__rec.push(n); return rec(n); };
  const q = g.input._push.bind(g.input); window.__q = []; g.input._push = (a) => { window.__q.push(a); return q(a); };
  window.__clips = () => { const m = g.p1.mixer; if (!m || !m._actions) return [];
    return m._actions.filter(a => a.isRunning() && a.getEffectiveWeight() > 0.2).map(a => a.getClip().name); };
  window.__aiUpdate = g.ai.update.bind(g.ai);
});
const joy = await boxOf('#joystick');
const btn = {};
for (const b of ['1', '2', '3', '4', '2+3', '1+2']) btn[b] = await boxOf(`.act-btn[data-btn="${b}"]`);
const R = joy ? Math.min(joy.w, joy.h) * 0.42 : 50;
const DIR = { f: [1, 0], b: [-1, 0], u: [0, -1], d: [0, 1], 'd/f': [0.72, 0.72], 'd/b': [-0.72, 0.72], 'u/f': [0.72, -0.72], 'u/b': [-0.72, -0.72] };
const facingSign = () => page.evaluate(() => { const g = window.__game; return g.p1.root.position.x <= g.p2.root.position.x ? 1 : -1; });
async function stick(dir) { // finger 0 on the stick; dir null = lift
  if (!joy) return;
  if (!dir) { if (fingers.has(0)) await up(0); return; }
  const s = await facingSign(); const [dx, dy] = DIR[dir];
  const x = joy.x + dx * s * R, y = joy.y + dy * R;
  if (!fingers.has(0)) { await down(0, joy.x, joy.y); await sleep(16); }
  await move(0, x, y);
}
async function press(b, hold = 60) { const k = btn[b]; if (!k) return; const id = 1 + Object.keys(btn).indexOf(b); await down(id, k.x, k.y); await sleep(hold); await up(id); }
async function reset() { // both fighters back to neutral at close range, CPU standing still, full HP
  await stick(null); for (const id of [...fingers.keys()]) await up(id);
  await page.evaluate(() => { const g = window.__game; g.ai.update = () => {}; g.timer = 999; g.p1.hp = g.p1.maxHp; g.p2.hp = g.p2.maxHp; window.__rec.length = 0; window.__q.length = 0; });
  await sleep(700);
  // walk in with the stick until close (a fresh approach each case, like a player closing distance)
  for (let i = 0; i < 40; i++) {
    const d = await page.evaluate(() => { const g = window.__game; return Math.abs(g.p1.root.position.x - g.p2.root.position.x); });
    if (d < 1.6) break; await stick('f'); await sleep(80);
  }
  await stick(null); await sleep(500);
  await page.evaluate(() => { window.__rec.length = 0; window.__q.length = 0; });
}
const cases = [
  ['1 (jab)', async () => { await press('1'); }],
  ['2', async () => { await press('2'); }],
  ['3', async () => { await press('3'); }],
  ['4', async () => { await press('4'); }],
  ['1,2 string (taps 150 ms apart)', async () => { await press('1'); await sleep(90); await press('2'); }],
  ['1,1,2 / 1,2,1 style (3 taps)', async () => { await press('1'); await sleep(110); await press('2'); await sleep(110); await press('1'); }],
  ['1 then 3 fast thumb roll (~60 ms)', async () => { await press('1', 40); await sleep(20); await press('3', 40); }],
  ['1+2 (two thumbs together)', async () => { const a = btn['1'], b = btn['2']; await down(1, a.x, a.y); await sleep(12); await down(2, b.x, b.y); await sleep(60); await up(1); await up(2); }],
  ['d/f+1', async () => { await stick('d/f'); await sleep(60); await press('1'); await stick(null); }],
  ['d+4 (low kick)', async () => { await stick('d'); await sleep(90); await press('4'); await stick(null); }],
  ['b+1', async () => { await stick('b'); await sleep(60); await press('1'); await stick(null); }],
  ['f+2', async () => { await stick('f'); await sleep(60); await press('2'); await stick(null); }],
  ['qcf+1 (d, d/f, f + 1 over ~300 ms)', async () => { await stick('d'); await sleep(100); await stick('d/f'); await sleep(90); await stick('f'); await sleep(60); await press('1'); await stick(null); }],
  ['f,f+2 (dash)', async () => { await stick('f'); await sleep(60); await stick(null); await sleep(60); await stick('f'); await sleep(50); await press('2'); await stick(null); }],
  ['1+3 throw (two thumbs together)', async () => { const a = btn['1'], b = btn['3']; await down(1, a.x, a.y); await sleep(10); await down(3, b.x, b.y); await sleep(60); await up(1); await up(3); }],
  ['HEAT button', async () => { await press('2+3'); }],
];
const rows = [];
for (const [name, run] of cases) {
  await reset();
  const hp0 = await page.evaluate(() => window.__game.p2.hp);
  await run();
  await sleep(230);
  const mid = await page.evaluate(() => ({ clips: window.__clips(), state: window.__game.p1.state }));
  const png = await snap(name);
  await sleep(700);
  const res = await page.evaluate(() => ({ q: [...window.__q], rec: [...window.__rec], hp: window.__game.p2.hp }));
  rows.push({ case: name, queue: res.q, recorded: res.rec, clips: mid.clips, state: mid.state, p2_damage: +(hp0 - res.hp).toFixed(1), png });
}
// ---- free fight vs the live CPU: a human-ish mix of approach, pokes, strings, lows ----
await stick(null);
await page.evaluate(() => { const g = window.__game; g.ai.update = window.__aiUpdate; g.p1.hp = g.p1.maxHp; g.p2.hp = g.p2.maxHp; g.timer = 60; window.__rec.length = 0; });
const free = { p1_moves: 0, hp_start: null, hp_end: null };
free.hp_start = await page.evaluate(() => [window.__game.p1.hp, window.__game.p2.hp]);
const plan = [['f', null, 300], [null, '1', 150], [null, '2', 150], ['d/f', '1', 200], [null, '1', 120], [null, '2', 120], ['d', '4', 250], ['f', null, 250], [null, '3', 150], [null, '4', 200], ['b', null, 300], ['f', '2', 200]];
const t0 = Date.now(); let k = 0;
while (Date.now() - t0 < 20000) {
  const st = await page.evaluate(() => window.__game.roundState);
  if (st !== 'fight') { await sleep(400); continue; }
  const [d, b, w] = plan[k++ % plan.length];
  if (d) await stick(d); if (b) await press(b); await sleep(w); if (d) await stick(null);
  if (k % 12 === 0) await snap(`free_${k}`);
}
free.hp_end = await page.evaluate(() => [window.__game.p1.hp, window.__game.p2.hp]);
free.p1_moves = await page.evaluate(() => window.__rec.length);
await snap('free_end');
const result = { url: URL, p1, p2: opp || p2, viewport: '844x390 touch (iPhone landscape)', steps, joystick: !!joy, buttons: Object.fromEntries(Object.entries(btn).map(([k, v]) => [k, !!v && v.top])), cases: rows, free, pageErrors: logs.filter(l => l.startsWith('[pageerror]')), errors: logs.slice(0, 40) };
fs.writeFileSync(`${out}/results.json`, JSON.stringify(result, null, 1));
const lines = rows.map(r => `${r.case.padEnd(38)} recorded=${JSON.stringify(r.recorded).padEnd(34)} clips=${JSON.stringify(r.clips).slice(0, 60).padEnd(60)} dmg=${r.p2_damage}`);
lines.push(`free fight 20 s: P1 moves ${free.p1_moves}, HP p1/p2 ${free.hp_start} -> ${free.hp_end}`, `page errors: ${result.pageErrors.length}`);
fs.writeFileSync(`${out}/results.txt`, lines.join('\n') + '\n');
console.log(lines.join('\n'));
await browser.close();

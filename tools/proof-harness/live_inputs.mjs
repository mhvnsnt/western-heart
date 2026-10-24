// Live input-timing proof (lane A, 2026-10-24): drives the REAL InputManager (window keydown /
// keyup listeners, game/js/input.js) in a running arcade fight with human-timed keyboard events
// and logs what P1's TekkenBuffer records for each: qcf+1, fast qcf (no sidestep), f,f+2 dash,
// 1,2 string vs 1+2 chord, 1 then 3 (no throw), held vs tapped d/f+1. The CPU is frozen.
//
// Run (repo root): serve the repo first, e.g.  python3 -m http.server 8765  then
//   node tools/proof-harness/live_inputs.mjs OUTDIR [p1=pantera] [p2=skull]
// Writes OUTDIR/results.json (per case: key events as sent, InputManager queue, notations
// recorded, the 120 Hz stick samples) and one PNG per case. PORT / PLAYWRIGHT_MODULE /
// CHROMIUM_PATH override the defaults (cloud container layout).
// Events are scheduled IN the page (setTimeout offsets), so gaps are real ms, not CDP round
// trips. A case is flagged "[STALL ... timing invalid]" when the page was too busy to keep the
// schedule (events > 15 ms late, or a game-loop gap > 40 ms): on a loaded machine rerun it.
// Synthetic events carry their dispatch time as e.timeStamp, so this harness cannot show the
// e.timeStamp chord fix; test/input-timing.test.mjs covers that.
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright/index.mjs');
import fs from 'fs';
const [,, out = 'live', p1 = 'pantera', p2 = 'skull'] = process.argv;
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 960, height: 540 } });
const logs = [];
page.on('console', m => { if (/error/i.test(m.text())) logs.push(`[${m.type()}] ${m.text()}`); });
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
await page.goto(`http://127.0.0.1:${process.env.PORT || 8765}/game/index.html`, { waitUntil: 'load' });
await page.waitForTimeout(1500);
await page.waitForFunction(() => window.__modes, null, { timeout: 60000 });
await page.evaluate(() => window.__modes.startMode('arcade'));
// software GL is too slow to draw every frame here; logic runs unchanged, arena renders for shots only
await page.evaluate(() => { const a = window.__game.arena; a.__render = a.render.bind(a); a.render = () => {}; });
await page.evaluate(async ([a, b]) => { await window.__modes.startFight(a, b, { mode: 'arcade' }); }, [p1, p2]);
await page.waitForFunction(() => window.__game && window.__game.roundState === 'fight', null, { timeout: 120000 });
await page.waitForTimeout(800);
await page.evaluate(() => {
  const g = window.__game; g.ai.update = () => {}; g.timer = 999;
  const tb = g.p1.tekken, rec = tb._recordMove.bind(tb);
  window.__rec = [];
  tb._recordMove = (n) => { window.__rec.push({ n, t: Math.round(performance.now()) }); return rec(n); };
  const q = g.input._push.bind(g.input);
  window.__q = [];
  g.input._push = (a) => { window.__q.push(a); return q(a); };
  // measure the real fixed-step rate the history sees
  const nd = tb.noteDirection.bind(tb); window.__ticks = { n: 0, dt: 0 };
  tb.noteDirection = (d, dt) => { const t = performance.now(); const T = window.__ticks; if (T.last && t - T.last > T.maxGap) T.maxGap = t - T.last; T.last = t; T.n++; T.dt = dt; T.dirs.push(d); return nd(d, dt); };
  window.__ticks.maxGap = 0; window.__ticks.dirs = [];
});
const D = 'ArrowDown';
const mk = (fwd) => [
  ['qcf+1 in 300 ms', [[0, 'down', D], [100, 'down', fwd], [210, 'up', D], [300, 'down', 'Digit1'], [360, 'up', 'Digit1'], [380, 'up', fwd]]],
  ['qcf+1 in 350 ms', [[0, 'down', D], [120, 'down', fwd], [240, 'up', D], [350, 'down', 'Digit1'], [410, 'up', 'Digit1'], [430, 'up', fwd]]],
  ['fast qcf+1 in 180 ms', [[0, 'down', D], [60, 'down', fwd], [130, 'up', D], [180, 'down', 'Digit1'], [240, 'up', 'Digit1'], [260, 'up', fwd]]],
  ['f,f+2 in 250 ms', [[0, 'down', fwd], [70, 'up', fwd], [140, 'down', fwd], [250, 'down', 'Digit2'], [310, 'up', 'Digit2'], [330, 'up', fwd]]],
  ['1 then 2, 100 ms apart', [[0, 'down', 'Digit1'], [60, 'up', 'Digit1'], [100, 'down', 'Digit2'], [160, 'up', 'Digit2']]],
  ['1 then 3, 90 ms apart', [[0, 'down', 'Digit1'], [60, 'up', 'Digit1'], [90, 'down', 'Digit3'], [150, 'up', 'Digit3']]],
  ['1+2 (10 ms apart)', [[0, 'down', 'Digit1'], [10, 'down', 'Digit2'], [70, 'up', 'Digit1'], [70, 'up', 'Digit2']]],
  ['d/f held 210 ms + 1', [[0, 'down', D], [0, 'down', fwd], [210, 'down', 'Digit1'], [270, 'up', 'Digit1'], [300, 'up', fwd], [300, 'up', D]]],
  ['d/f tapped (70 ms) + 1', [[0, 'down', D], [0, 'down', fwd], [70, 'down', 'Digit1'], [130, 'up', 'Digit1'], [150, 'up', fwd], [150, 'up', D]]],
];
const rows = [];
for (let ci = 0; ci < mk('ArrowRight').length; ci++) {
  await page.evaluate(() => { const g = window.__game; g.p1.hp = 100; g.p2.hp = 100; g.p1._enter('idle'); g.p2._enter('idle'); g.p2.stun = 0;
    g.p2.root.position.x = g.p1.root.position.x + 1.15 * g.p1.facing; g.p1.tekken.lastMove = null; g.input.reset(); });
  await page.waitForTimeout(400);
  const fwd = await page.evaluate(() => (window.__game.p1.facing > 0 ? 'ArrowRight' : 'ArrowLeft'));
  const [label, evs] = mk(fwd)[ci];
  const r = await page.evaluate((evs) => new Promise((res) => {
    window.__rec = []; window.__q = []; window.__ticks.maxGap = 0; window.__ticks.last = 0; window.__ticks.dirs = [];
    const t0 = performance.now() + 20, sent = [];
    for (const [t, kind, code] of evs) setTimeout(() => {
      sent.push([Math.round(performance.now() - t0), kind, code]);
      window.dispatchEvent(new KeyboardEvent(kind === 'down' ? 'keydown' : 'keyup', { code, bubbles: true }));
    }, 20 + t);
    setTimeout(() => res({ sent, queue: window.__q.slice(), recorded: window.__rec.map(x => ({ n: x.n, at: Math.round(x.t - t0) })),
      p1: window.__game.p1.attackName, state: window.__game.p1.state, loopGap: Math.round(window.__ticks.maxGap), dirs: window.__ticks.dirs.reduce((a, d) => (a.length && a[a.length - 1][0] === d ? (a[a.length - 1][1]++, a) : (a.push([d, 1]), a)), []).map(([d, n]) => d + 'x' + n).join(' ') }), 20 + evs[evs.length - 1][0] + 250);
  }), evs);
  const shot = `${out}/${label.replace(/[^a-z0-9]+/gi, '_')}.png`;
  await page.evaluate(() => window.__game.arena.__render());
  await page.screenshot({ path: shot });
  const drift = Math.max(...r.sent.map((s, i) => Math.abs(s[0] - [...evs].sort((a, b) => a[0] - b[0])[i][0])));
  r.stalled = drift > 15 || r.loopGap > 40; r.drift = drift;
  rows.push({ label, ...r, shot });
  console.log(`${label.padEnd(24)} queue=${JSON.stringify(r.queue).padEnd(22)} recorded=${JSON.stringify(r.recorded.map(x => x.n))} state=${r.state}${r.stalled ? `  [STALL events ${r.drift} ms, loop gap ${r.loopGap} ms: timing invalid]` : ''}`);
}
const ticks = await page.evaluate(() => window.__ticks);
console.log('noteDirection dt seen:', ticks.dt, 'calls:', ticks.n);
fs.writeFileSync(`${out}/results.json`, JSON.stringify({ p1, p2, ticks, rows, logs }, null, 1));
console.log(`page errors: ${logs.filter(l => l.startsWith('[pageerror]')).length}`);
await browser.close();

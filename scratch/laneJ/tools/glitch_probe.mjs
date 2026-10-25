// Lane J glitch probe: deterministic AI-vs-AI fight, stepped with game._update(1/120).
// node glitch_probe.mjs OUT P1 P2 [seconds=90] [shotEvery=4]
// Logs both fighters every 6 ticks (20 Hz): state, stun, pos, facing, yaw, ground, hp, vx/vy, round.
// Screenshots every shotEvery game-seconds (renders the arena first).
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright/index.mjs');
import fs from 'fs';
const [,, out = 'probe', p1 = 'pantera', p2 = 'skull', secs = '90', shotEvery = '4'] = process.argv;
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 960, height: 540 } });
const logs = [];
page.on('console', m => { if (/error|warn/i.test(m.type())) logs.push(`[${m.type()}] ${m.text()}`); });
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
await page.goto(`http://127.0.0.1:${process.env.PORT || 8797}/game/index.html?demo=1`, { waitUntil: 'load' });
await page.waitForFunction(() => window.__modes, null, { timeout: 90000 });
await page.evaluate(() => window.__modes.startMode('arcade'));
await page.waitForTimeout(500);
await page.evaluate(async ([a, b]) => { await window.__modes.startFight(a, b, { mode: 'arcade' }); }, [p1, p2])
  .catch(e => logs.push('startFight err ' + e.message));
await page.waitForFunction(() => window.__game && window.__game.p1 && window.__game.p2, null, { timeout: 120000 });
// wait for the intro's setTimeout to flip to 'fight' (real time), then freeze the RAF sim
await page.waitForFunction(() => window.__game.roundState === 'fight', null, { timeout: 60000 }).catch(() => {});
await page.evaluate(() => { window.__game.paused = true; });
const cdp = await page.context().newCDPSession(page);
const rows = [];
const total = Math.round(+secs * 120);
let shot = 0;
for (let t = 0; t < total; t += 120) {
  const chunk = await page.evaluate((n) => {
    const g = window.__game, out = [];
    const f = (x) => ({ st: x.state, stun: +(x.stun || 0).toFixed(3), x: +x.root.position.x.toFixed(3),
      y: +x.root.position.y.toFixed(3), z: +x.root.position.z.toFixed(3), fc: x.facing,
      yaw: typeof x._faceYaw === 'number' ? +x._faceYaw.toFixed(3) : null, g: x.onGround ? 1 : 0,
      hp: +x.hp.toFixed(2), vx: +(x.vx || 0).toFixed(2), vy: +(x.vy || 0).toFixed(2), atk: x.attackName || null,
      stT: +(x.stateT || 0).toFixed(2), dead: x.dead ? 1 : 0, juggle: x._juggle || 0,
      rs: x._reactionSel ? x._reactionSel.code : null });
    for (let i = 0; i < n; i++) {
      // the intro / between-round setTimeout runs on real time; keep stepping regardless
      if (g.running) g._update(1 / 120);
      if (i % 6 === 0) out.push({ rs: g.roundState, round: g.round, timer: +(g.timer || 0).toFixed(2),
        wins: `${g.wins.p1}-${g.wins.p2}`, p1: f(g.p1), p2: f(g.p2), running: !!g.running });
    }
    return out;
  }, 120);
  for (const r of chunk) { r.t = +(rows.length / 20).toFixed(2); rows.push(r); }
  if ((t / 120) % (+shotEvery) === 0) {
    await page.evaluate(() => { const g = window.__game; g.arena.update(0.016, g.p1, g.p2); g.arena.render(); });
    const r = await cdp.send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(`${out}/s${String(shot++).padStart(3, '0')}_t${(t / 120).toFixed(0)}.png`, Buffer.from(r.data, 'base64'));
  }
  // let real time pass a little so the round intro setTimeouts fire
  await page.waitForTimeout(30);
}
fs.writeFileSync(`${out}/rows.json`, JSON.stringify(rows));
fs.writeFileSync(`${out}/console.log`, logs.join('\n'));
await browser.close();
console.log('rows', rows.length, 'errors', logs.filter(l => /pageerror/.test(l)).length);

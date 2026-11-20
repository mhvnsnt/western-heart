// tools/perf/hit_hitch_probe.mjs — measure where frame time goes in a real fight, and what spikes when hits land.
//
// Why (owner 2026-11-11): "the game is really laggy ... it lags a lot when you trying to fight her when you're
// making contact with the hits ... fix that so it plays smoothly". This plays the real game headless, makes P1 attack
// a standing P2 at close range, and records per rendered frame: the sim (_update steps), hit effects, arena update,
// render, plus whether a hit landed. A CDP CPU profile over the same run names the functions behind the time.
//
// usage: node tools/perf/hit_hitch_probe.mjs <game-url> <out.json> <p1> <p2> [moves] [stage]
//   e.g. node tools/perf/hit_hitch_probe.mjs http://127.0.0.1:8765/game/index.html out.json pantera megami "1,2,3,4,1,2"
//   NO_REMOTE=1 blocks the B2 Worker (assets from this checkout). Software WebGL makes absolute render times large;
//   compare frames WITH a hit against frames without, and read the profile's self times.
import { createRequire } from 'module';
import fs from 'fs';
const { chromium } = createRequire(import.meta.url)('playwright');
const [,, base, out, p1 = 'pantera', p2 = 'thor', list = '1,2,3,4,1,2,d/f+1,4', stage = 'shrine'] = process.argv;
if (!out) { console.error('usage: node hit_hitch_probe.mjs <game-url> <out.json> <p1> <p2> [moves] [stage]'); process.exit(2); }
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 960, height: 540 } });
if (process.env.NO_REMOTE) await page.route(/workers\.dev/, (r) => r.abort());
const logs = [];
page.on('pageerror', (e) => logs.push('[pageerror] ' + e.message));
await page.goto(`${base}?quick=${p1},${p2},${stage}`, { waitUntil: 'load', timeout: 180000 });
const t0 = Date.now();
while (Date.now() - t0 < 240000) {
  const ok = await page.evaluate(() => { const g = window.__game; return !!(g && g.p1 && g.p1.t3actions && Object.keys(g.p1.t3actions).length && g.roundState === 'fight'); }).catch(() => false);
  if (ok) break;
  await page.waitForTimeout(1000);
}
// instrument: per-frame buckets, filled by wrappers around the game's own per-frame methods
await page.evaluate(() => {
  const g = window.__game;
  g.ai = { update() {}, reset() {} }; g.roundTime = 0; g.timer = Infinity;
  const hp = g.p2.maxHp; setInterval(() => { if (g.p2.hp < hp) g.p2.hp = hp; }, 100);
  // close range so the hits connect
  g.p2.root.position.x = g.p1.root.position.x + (g.p1.facing || 1) * 0.95;
  const P = window.__perf = { frames: [], cur: null };
  const begin = () => { P.cur = { t: performance.now(), update: 0, steps: 0, hitfx: 0, arena: 0, render: 0, hits: 0, spawns: 0, links: 0 }; };
  // shader programs linked this frame (a link inside render is a synchronous compile: the hitch)
  try { const gl = g.arena.renderer.getContext(); const lp = gl.linkProgram.bind(gl); gl.linkProgram = (pr) => { if (P.cur) P.cur.links++; return lp(pr); }; } catch (e) { /* no GL */ }
  const wrap = (obj, name, key, onCall) => {
    const f = obj[name].bind(obj);
    obj[name] = function (...a) { const s = performance.now(); try { return f(...a); } finally { if (P.cur) { P.cur[key] += performance.now() - s; if (onCall) onCall(); } } };
  };
  wrap(g, '_update', 'update', () => { P.cur.steps++; });
  wrap(g.hitfx, 'update', 'hitfx');
  wrap(g.arena, 'update', 'arena');
  wrap(g.arena, 'render', 'render');
  const sp = g.hitfx.spawn.bind(g.hitfx);
  g.hitfx.spawn = (...a) => { const s = performance.now(); try { return sp(...a); } finally { if (P.cur) { P.cur.spawns++; P.cur.hitfx += performance.now() - s; } } };
  let lastHp = null;
  const tick = () => {
    if (P.cur) {
      const hpNow = g.p2.hp; // reset to full by the interval above, so detect hits by the hitfx spawns instead
      P.cur.total = performance.now() - P.cur.t;
      P.cur.hitstop = g._hitStop > 0;
      P.frames.push(P.cur);
    }
    begin();
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
});
const cdp = await page.context().newCDPSession(page);
await cdp.send('Profiler.enable');
await cdp.send('Profiler.setSamplingInterval', { interval: 500 });
await cdp.send('Profiler.start');
const results = [];
for (const mv of list.split(',')) {
  const r = await page.evaluate(async (mv) => {
    const g = window.__game, f = g.p1;
    const until = async (c, ms) => { const e = Date.now() + ms; while (!c() && Date.now() < e) await new Promise((r) => setTimeout(r, 20)); };
    await until(() => f.state === 'idle', 30000);
    g.p2.root.position.x = f.root.position.x + (f.facing || 1) * 0.95;
    const n0 = window.__perf.frames.length;
    const ok = f.tryAttack(mv);
    await until(() => f.state !== 'idle', 5000);
    await until(() => f.state === 'idle', 30000);
    return { mv, ok, frames: window.__perf.frames.length - n0 };
  }, mv);
  results.push(r);
}
const { profile } = await cdp.send('Profiler.stop');
const P = await page.evaluate(() => window.__perf.frames);
await browser.close();

// frame statistics: frames where hit effects spawned vs the rest
const med = (a) => { const s = [...a].sort((x, y) => x - y); return s.length ? s[Math.floor(s.length / 2)] : 0; };
const pct = (a, q) => { const s = [...a].sort((x, y) => x - y); return s.length ? s[Math.min(s.length - 1, Math.floor(s.length * q))] : 0; };
const hitF = P.filter((f) => f.spawns > 0), rest = P.filter((f) => f.spawns === 0);
const sum = (fs, k) => ({ median: +med(fs.map((f) => f[k] || 0)).toFixed(2), p95: +pct(fs.map((f) => f[k] || 0), 0.95).toFixed(2), max: +Math.max(0, ...fs.map((f) => f[k] || 0)).toFixed(2) });
const keys = ['total', 'update', 'steps', 'hitfx', 'arena', 'render', 'links'];
const stats = {
  frames: P.length, hitFrames: hitF.length, linksTotal: P.reduce((a, f) => a + (f.links || 0), 0), linksOnHitFrames: hitF.reduce((a, f) => a + (f.links || 0), 0),
  normal: Object.fromEntries(keys.map((k) => [k, sum(rest, k)])),
  onHit: Object.fromEntries(keys.map((k) => [k, sum(hitF, k)])),
  // the frames right after a hit (effects alive, reactions starting)
  afterHit: (() => { const idx = new Set(); P.forEach((f, i) => { if (f.spawns) for (let j = 1; j <= 6; j++) idx.add(i + j); }); const fs = [...idx].map((i) => P[i]).filter(Boolean); return Object.fromEntries(keys.map((k) => [k, sum(fs, k)])); })(),
};
// CPU profile: self time per function (top 40)
const self = new Map();
const byId = new Map(profile.nodes.map((n) => [n.id, n]));
const dt = profile.timeDeltas;
profile.samples.forEach((id, i) => {
  const n = byId.get(id); if (!n) return;
  const cf = n.callFrame; const key = `${cf.functionName || '(anon)'} ${cf.url.split('/').slice(-2).join('/')}:${cf.lineNumber + 1}`;
  self.set(key, (self.get(key) || 0) + (dt[i] || 0) / 1000);
});
const totalMs = [...self.values()].reduce((a, b) => a + b, 0);
const top = [...self.entries()].sort((a, b) => b[1] - a[1]).slice(0, 40).map(([k, v]) => ({ fn: k, ms: +v.toFixed(1), pct: +(100 * v / totalMs).toFixed(1) }));
const report = { p1, p2, stage, moves: results, stats, profileMs: +totalMs.toFixed(0), topSelf: top, logs: logs.slice(0, 20) };
fs.writeFileSync(out, JSON.stringify(report, null, 1));
console.log(JSON.stringify({ stats, top: top.slice(0, 15) }, null, 1));

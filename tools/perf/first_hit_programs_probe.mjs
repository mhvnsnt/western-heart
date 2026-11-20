// tools/perf/first_hit_programs_probe.mjs — list every shader program the renderer creates around hits in a real
// fight (by program object, so a recompile of an existing cache key counts too). A program created on a hit frame
// is a synchronous compile inside render: the hitch the owner felt ("it lags a lot ... when you're making contact
// with the hits", 2026-11-11). After the lag fix the list after the start line must be empty.
// usage: node tools/perf/first_hit_programs_probe.mjs <game-url> <p1> <p2> "1,2,1"
import { createRequire } from 'module';
const { chromium } = createRequire(import.meta.url)('playwright');
const [,, base, p1, p2, list] = process.argv;
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await b.newPage({ viewport: { width: 640, height: 360 } });
await page.route(/workers\.dev/, (r) => r.abort());
await page.goto(`${base}?quick=${p1},${p2},shrine`, { waitUntil: 'load', timeout: 180000 });
const t0 = Date.now();
while (Date.now() - t0 < 240000) { if (await page.evaluate(() => { const g = window.__game; return !!(g && g.p1 && g.p1.t3actions && Object.keys(g.p1.t3actions).length && g.roundState === 'fight'); }).catch(() => false)) break; await page.waitForTimeout(1000); }
const r = await page.evaluate(async (list) => {
  const g = window.__game; g.ai = { update() {}, reset() {} }; g.roundTime = 0; g.timer = Infinity;
  const R = g.arena.renderer, info = R.info;
  const hp = g.p2.maxHp; setInterval(() => { if (g.p2.hp < hp) g.p2.hp = hp; }, 100);
  const seen = new Set(info.programs || []);
  const ev = []; let hitAt = null, frameNo = 0;
  const sp = g.hitfx.spawn.bind(g.hitfx); g.hitfx.spawn = (...a) => { hitAt = frameNo; ev.push({ frame: frameNo, hit: a[0] }); return sp(...a); };
  const tick = () => { frameNo++; for (const p of info.programs || []) if (!seen.has(p)) { seen.add(p); ev.push({ frame: frameNo, sinceHitFrames: hitAt == null ? null : frameNo - hitAt, prog: p.name, key: String(p.cacheKey).slice(0, 220) }); } requestAnimationFrame(tick); };
  requestAnimationFrame(tick);
  const until = async (c, ms) => { const e = Date.now() + ms; while (!c() && Date.now() < e) await new Promise((r) => setTimeout(r, 20)); };
  const f = g.p1;
  ev.push({ start: true, programs: (info.programs || []).length });
  for (const mv of list.split(',')) {
    await until(() => f.state === 'idle', 30000);
    g.p2.root.position.x = f.root.position.x + (f.facing || 1) * 0.95;
    f.tryAttack(mv);
    await until(() => f.state !== 'idle', 5000);
    await until(() => f.state === 'idle', 30000);
  }
  return ev;
}, list);
for (const e of r) console.log(JSON.stringify(e));
await b.close();

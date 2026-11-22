// tools/perf/program_link_probe.mjs — every GPU shader program linked AFTER a fight starts, and which code linked it.
//
// Why (owner 2026-11-11: "it's mostly in hits and inputs it's getting slow"): a shader compiled mid-fight stalls that
// frame (tens to hundreds of ms on a phone). three.js's renderer.info.programs only sees three's own programs; this
// wraps WebGL(2)RenderingContext.linkProgram before any page script runs, so it also catches effect libraries with
// their own shaders (Effekseer, particle systems). Plays a fight (P2's AI fights, P1 attacks every 0.7 s, HP held up)
// and lists each link after the round turned to 'fight' with its time and the first game / library frames of its
// call stack, plus what the fighters were doing at that moment.
//
// usage: NO_REMOTE=1 node tools/perf/program_link_probe.mjs <game-url> <out.json> [p1] [p2] [seconds] [stage]
import { createRequire } from 'module';
import fs from 'fs';
const { chromium } = createRequire(import.meta.url)('playwright');
const [,, base, out, p1 = 'pantera', p2 = 'thor', secArg = '90', stage = 'shrine'] = process.argv;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 640, height: 360 } });
if (process.env.NO_REMOTE) await page.route(/workers\.dev/, (r) => r.abort());
await page.addInitScript(() => {
  const links = window.__links = [];
  for (const C of [window.WebGL2RenderingContext, window.WebGLRenderingContext]) {
    if (!C) continue;
    const orig = C.prototype.linkProgram;
    C.prototype.linkProgram = function (p) {
      const st = (new Error().stack || '').split('\n').slice(2)
        .map((l) => l.trim().replace(/^at /, ''))
        .filter((l) => !/three\.module\.js/.test(l))
        .slice(0, 4).map((l) => l.replace(/\(?https?:\/\/[^/]+\//, '').replace(/\)$/, ''));
      const g = window.__game;
      links.push({ t: performance.now(), round: g ? g.roundState : null, stack: st,
        p1: g && g.p1 ? `${g.p1.state}:${g.p1.attackName || ''}` : null, p2: g && g.p2 ? `${g.p2.state}:${g.p2.attackName || ''}` : null });
      return orig.call(this, p);
    };
  }
});
await page.goto(`${base}?quick=${p1},${p2},${stage}`, { waitUntil: 'load', timeout: 180000 });
const t0 = Date.now();
while (Date.now() - t0 < 300000) {
  if (await page.evaluate(() => { const g = window.__game; return !!(g && g.p1 && g.p1.t3actions && Object.keys(g.p1.t3actions).length && g.roundState === 'fight'); }).catch(() => false)) break;
  await page.waitForTimeout(1000);
}
const fightT = await page.evaluate(() => {
  const g = window.__game;
  g.roundTime = 0; g.timer = Infinity;
  setInterval(() => { for (const f of [g.p1, g.p2]) if (f.hp < f.maxHp * 0.35) f.hp = f.maxHp; }, 200);
  const notes = ['1', '2', '3', '4', '1,2', 'd/f+1', 'f+4', 'b+2', 'd+3', '1+2', 'u/f+4', 'f,F+2'];
  let i = 0;
  setInterval(() => { try { g.p1.tryAttack(notes[i++ % notes.length]); } catch (e) { /* none */ } }, 700);
  window.__fightT = performance.now();
  return window.__fightT;
});
await page.waitForTimeout(+secArg * 1000);
const res = await page.evaluate(() => {
  const g = window.__game, R = g.arena.renderer;
  return { links: window.__links, fightT: window.__fightT, threePrograms: (R.info.programs || []).length,
    threeNames: (R.info.programs || []).map((p) => p.name) };
});
await browser.close();
const before = res.links.filter((l) => l.t < res.fightT).length;
const during = res.links.filter((l) => l.t >= res.fightT).map((l) => ({ atS: +((l.t - res.fightT) / 1000).toFixed(2), round: l.round, p1: l.p1, p2: l.p2, stack: l.stack }));
const bySite = {};
for (const l of during) { const k = l.stack.slice(0, 2).join(' < '); bySite[k] = (bySite[k] || 0) + 1; }
const report = { p1, p2, stage, seconds: +secArg, linksBeforeFight: before, linksDuringFight: during.length, bySite, during, threePrograms: res.threePrograms };
fs.writeFileSync(out, JSON.stringify(report, null, 1));
console.log(JSON.stringify({ linksBeforeFight: before, linksDuringFight: during.length, bySite, first: during.slice(0, 25) }, null, 1));

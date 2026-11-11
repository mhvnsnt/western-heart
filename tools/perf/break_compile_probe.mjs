// tools/perf/break_compile_probe.mjs — does a stage break (floor / wall) compile shaders or add lights at the hit?
//
// Why (owner 2026-11-11: "it's mostly in hits and inputs it's getting slow"): a break used to build its visuals at
// the hit (new lights -> every lit shader in the scene recompiled; new materials -> new shaders). This plays the real
// game, then forces each breakable the stage has (through StageBreaks.checkHit, the path a heavy hit takes) and records
// for each: shader programs and scene lights before / after, the CPU time of the break call, and the next rendered
// frame's render() time. Also reports how far the move-clip prewarm (Fighter.prewarmAttackClips) has got.
//
// usage: NO_REMOTE=1 [OLD_FILES=game/js/stagebreaks.js] node tools/perf/break_compile_probe.mjs <game-url> <out.json> [p1] [p2] [stage]
import { createRequire } from 'module';
import fs from 'fs';
import { execFileSync } from 'child_process';
const { chromium } = createRequire(import.meta.url)('playwright');
const [,, base, out, p1 = 'pantera', p2 = 'thor', stage = 'shrine'] = process.argv;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 640, height: 360 } });
if (process.env.NO_REMOTE) await page.route(/workers\.dev/, (r) => r.abort());
// A/B: OLD_FILES=game/js/stagebreaks.js,... serves those files as they are in git HEAD (the code before this branch's
// change), everything else from the working tree, so one machine measures both.
for (const rel of (process.env.OLD_FILES || '').split(',').filter(Boolean)) {
  const body = execFileSync('git', ['show', 'HEAD:' + rel], { encoding: 'utf8', maxBuffer: 64 << 20 });
  const tail = rel.replace(/^game\//, '');
  await page.route((u) => u.pathname.endsWith('/' + tail), (r) => r.fulfill({ status: 200, contentType: 'text/javascript', body }));
}
await page.goto(`${base}?quick=${p1},${p2},${stage}`, { waitUntil: 'load', timeout: 180000 });
const t0 = Date.now();
while (Date.now() - t0 < 300000) {
  if (await page.evaluate(() => { const g = window.__game; return !!(g && g.p1 && g.p1.t3actions && Object.keys(g.p1.t3actions).length && g.roundState === 'fight'); }).catch(() => false)) break;
  await page.waitForTimeout(1000);
}
const fightAt = Date.now();
// let the fight run a little so the round-start prewarm and stage streaming settle
await page.waitForTimeout(8000);
const report = await page.evaluate(async () => {
  const g = window.__game, A = g.arena, R = A.renderer, sb = g.stageBreaks;
  const lights = () => { let n = 0; A.scene.traverseVisible((o) => { if (o.isLight) n++; }); return n; };
  const progs = () => (R.info.programs || []).length;
  const warm = (f) => ({ left: f.prewarmLeft, done: !!f._warmDone, actions: Object.keys(f.t3actions || {}).length });
  const out = { stage: sb && sb.stageDef && sb.stageDef.id, defs: sb ? sb.defs.map((d) => d.type) : [], warmP1: warm(g.p1), warmP2: warm(g.p2), breaks: [] };
  if (!sb) return out;
  g.ai = { update() {}, reset() {} };
  const nextFrame = () => new Promise((r) => requestAnimationFrame(() => r()));
  // time the arena's render on the next frames
  const rt = []; const r0 = A.render.bind(A); A.render = function () { const s = performance.now(); r0(); rt.push(performance.now() - s); };
  for (const def of sb.defs) {
    const id = sb._id(def);
    if (sb.broken.has(id)) continue;
    const atk = g.p1, dfn = g.p2;
    // place the defender where this break triggers
    if (def.type === 'wall') { dfn.root.position.x = def.x - Math.sign(def.x) * 0.3; dfn.root.position.z = 0; }
    else { dfn.root.position.x = def.x || 0; dfn.root.position.z = def.z || 0; }
    const before = { programs: progs(), lights: lights() };
    await nextFrame(); rt.length = 0;
    const s = performance.now();
    sb.checkHit(atk, dfn, { knock: 7, launch: true, knockdown: true }, 'hit');
    const breakMs = performance.now() - s;
    await nextFrame(); await nextFrame();
    const after = { programs: progs(), lights: lights() };
    out.breaks.push({ type: def.type, broke: sb.broken.has(id), breakCallMs: +breakMs.toFixed(2), before, after,
      renderMsNext: rt.slice(0, 2).map((x) => +x.toFixed(1)) });
    dfn.hp = dfn.maxHp;
  }
  A.render = r0;
  return out;
});
report.secondsSinceFight = Math.round((Date.now() - fightAt) / 1000);
fs.writeFileSync(out, JSON.stringify(report, null, 1));
console.log(JSON.stringify(report, null, 1));
await browser.close();

// tools/perf/frame_budget_probe.mjs — where a real fight's frame time goes (owner 2026-11-11: "U gotta get the game
// less laggy and slow it's running too slow").
//
// Plays a quick fight (P2's AI fights, P1 throws an attack every second) and reports:
//   static load: pixel ratio, canvas size, shadow map type/size, lights (type, shadow casters), triangles and bones per
//                fighter, skinned meshes, materials by type, textures, composer passes;
//   per frame:   sim time (_update) and fixed steps, render() time, draw calls and triangles, and how much game time
//                the frame advanced vs the wall clock (slow motion = the fixed-step cap hit);
//   CPU profile: self time per function and per file.
// Software WebGL inflates GPU-side cost, so read the JS numbers and the static load, not absolute fps.
//
// usage: node tools/perf/frame_budget_probe.mjs <game-url> <out.json> [p1] [p2] [frames]
import { createRequire } from 'module';
import fs from 'fs';
const { chromium } = createRequire(import.meta.url)('playwright');
const [,, base, out, p1 = 'pantera', p2 = 'megami', framesArg = '400', stage = 'shrine'] = process.argv;
const N = +framesArg;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 412, height: 915 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true,
  userAgent: 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36' });
if (process.env.NO_REMOTE) await page.route(/workers\.dev/, (r) => r.abort());
await page.goto(`${base}?quick=${p1},${p2},${stage}`, { waitUntil: 'load', timeout: 180000 });
const t0 = Date.now();
while (Date.now() - t0 < 300000) {
  if (await page.evaluate(() => { const g = window.__game; return !!(g && g.p1 && g.p1.t3actions && Object.keys(g.p1.t3actions).length && g.roundState === 'fight'); }).catch(() => false)) break;
  await page.waitForTimeout(1000);
}
const staticLoad = await page.evaluate(() => {
  const g = window.__game, A = g.arena, R = A.renderer;
  const lights = {}; let shadowCasters = 0, shadowLights = [];
  const mats = {}; let meshes = 0, skinned = 0;
  A.scene.traverse((o) => {
    if (o.isLight) { lights[o.type] = (lights[o.type] || 0) + 1; if (o.castShadow) shadowLights.push({ type: o.type, map: o.shadow && o.shadow.mapSize ? o.shadow.mapSize.x : null }); }
    if (o.isMesh) { meshes++; if (o.isSkinnedMesh) skinned++; if (o.castShadow) shadowCasters++;
      for (const m of [].concat(o.material || [])) mats[m.type] = (mats[m.type] || 0) + 1; }
  });
  const fighter = (f) => { let tris = 0, bones = 0, sk = 0; f.root.traverse((o) => { if (o.isMesh && o.geometry) { const gi = o.geometry.index; tris += (gi ? gi.count : o.geometry.attributes.position.count) / 3; } if (o.isSkinnedMesh) { sk++; bones = Math.max(bones, o.skeleton.bones.length); } }); return { tris: Math.round(tris), skinnedMeshes: sk, bones }; };
  const c = R.domElement;
  return { pixelRatio: R.getPixelRatio(), canvas: [c.width, c.height], shadowType: R.shadowMap.type, shadowEnabled: R.shadowMap.enabled,
    lights, shadowLights, shadowCasters, meshes, skinned, materials: mats, p1: fighter(g.p1), p2: fighter(g.p2),
    textures: R.info.memory.textures, geometries: R.info.memory.geometries, programs: (R.info.programs || []).length,
    passes: (A.composer && A.composer.passes || []).map((p) => p.constructor.name), isMobile: A.isMobile };
});
// per-frame instrumentation
await page.evaluate((N) => {
  const g = window.__game, A = g.arena, R = A.renderer;
  g.roundTime = 0; g.timer = Infinity;
  setInterval(() => { for (const f of [g.p1, g.p2]) if (f.hp < f.maxHp * 0.5) f.hp = f.maxHp; }, 200);
  setInterval(() => { try { g.p1.tryAttack(['1', '2', '3', '4', 'd/f+1', '1,2'][Math.floor(Math.random() * 6)]); } catch (e) { /* none */ } }, 900);
  const P = window.__fb = { frames: [], cur: null };
  const wrap = (obj, name, key) => { const f = obj[name].bind(obj); obj[name] = function (...a) { const s = performance.now(); try { return f(...a); } finally { if (P.cur) { P.cur[key] += performance.now() - s; if (key === 'update') P.cur.steps++; } } }; };
  wrap(g, '_update', 'update'); wrap(A, 'render', 'render');
  R.info.autoReset = true;
  let simT = 0; const su = g._update; g._update = function (dt) { simT += dt; return su.call(this, dt); };
  let lastWall = performance.now(), lastSim = 0;
  const tick = () => {
    const now = performance.now();
    if (P.cur) { P.cur.wall = now - lastWall; P.cur.sim = (simT - lastSim) * 1000; P.cur.calls = R.info.render.calls; P.cur.tris = R.info.render.triangles; P.frames.push(P.cur); }
    lastWall = now; lastSim = simT;
    if (P.frames.length < N) { P.cur = { update: 0, steps: 0, render: 0 }; requestAnimationFrame(tick); } else P.cur = null;
  };
  requestAnimationFrame(tick);
}, N);
const cdp = await page.context().newCDPSession(page);
await cdp.send('Profiler.enable'); await cdp.send('Profiler.setSamplingInterval', { interval: 500 }); await cdp.send('Profiler.start');
const tEnd = Date.now() + 15 * 60 * 1000;
while (Date.now() < tEnd) { if (await page.evaluate((N) => window.__fb.frames.length >= N, N)) break; await page.waitForTimeout(2000); }
const { profile } = await cdp.send('Profiler.stop');
const F = await page.evaluate(() => window.__fb.frames);
await browser.close();
const med = (a) => { const s = [...a].sort((x, y) => x - y); return s.length ? +s[Math.floor(s.length / 2)].toFixed(2) : 0; };
const p95 = (a) => { const s = [...a].sort((x, y) => x - y); return s.length ? +s[Math.min(s.length - 1, Math.floor(s.length * 0.95))].toFixed(2) : 0; };
const col = (k) => F.map((f) => f[k] || 0);
const perFrame = Object.fromEntries(['wall', 'sim', 'update', 'steps', 'render', 'calls', 'tris'].map((k) => [k, { median: med(col(k)), p95: p95(col(k)) }]));
const sumWall = col('wall').reduce((a, b) => a + b, 0), sumSim = col('sim').reduce((a, b) => a + b, 0);
const self = new Map(), byFile = new Map();
const byId = new Map(profile.nodes.map((n) => [n.id, n]));
profile.samples.forEach((id, i) => {
  const n = byId.get(id); if (!n) return; const cf = n.callFrame; const ms = (profile.timeDeltas[i] || 0) / 1000;
  const file = cf.url ? cf.url.split('/').slice(-2).join('/') : `(${cf.functionName || 'native'})`;
  const key = `${cf.functionName || '(anon)'} ${file}:${cf.lineNumber + 1}`;
  self.set(key, (self.get(key) || 0) + ms); byFile.set(file, (byFile.get(file) || 0) + ms);
});
const total = [...self.values()].reduce((a, b) => a + b, 0);
const top = (m, n) => [...m.entries()].sort((a, b) => b[1] - a[1]).slice(0, n).map(([k, v]) => ({ k, ms: +v.toFixed(0), pct: +(100 * v / total).toFixed(1) }));
const report = { p1, p2, stage, frames: F.length, staticLoad, perFrame, gameSpeed: +(sumSim / sumWall).toFixed(3), topFunctions: top(self, 35), topFiles: top(byFile, 20) };
fs.writeFileSync(out, JSON.stringify(report, null, 1));
console.log(JSON.stringify({ staticLoad, perFrame, gameSpeed: report.gameSpeed, topFiles: report.topFiles.slice(0, 14), topFunctions: report.topFunctions.slice(0, 18) }, null, 1));

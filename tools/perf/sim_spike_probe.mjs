// tools/perf/sim_spike_probe.mjs — what a fight's SIMULATION costs per frame, and which inputs and hits make it spike.
//
// Why (owner 2026-11-11: "it's mostly in hits and inputs it's getting slow"): software WebGL makes render time
// meaningless here, so this probe takes rendering out (arena.render becomes a no-op while it measures), stops the
// game's own loop, and steps the sim exactly as game.js _loop does at 60 fps (2 fixed 1/120 s steps per frame;
// hitstop counts down per frame) on a simulated clock (performance.now replaced, as tools/anim/string_sim_probe.mjs).
// P2's AI fights; P1 presses a move from its own move list every PRESS_MS. Every frame records the real CPU time
// of its sim steps plus what happened in it (P1/P2 move starts, hits, blocks). Reports median / p95 / max, the
// worst frames with their events, cost of a move's FIRST use vs later uses, and a CPU profile of the sim.
//
// usage: NO_REMOTE=1 [ATTRIB=1] [PREWARM=1] node tools/perf/sim_spike_probe.mjs <game-url> <out.json> [p1] [p2] [frames] [pressMs] [stage]
//   ATTRIB=1 wraps the Fighter / Game / helper methods with inclusive timers and lists, for every frame over 3 ms,
//   the calls it spent its time in (adds overhead: read the attribution, not the absolute times).
import { createRequire } from 'module';
import fs from 'fs';
const { chromium } = createRequire(import.meta.url)('playwright');
const [,, base, out, p1 = 'pantera', p2 = 'thor', framesArg = '1800', pressArg = '450', stage = 'shrine'] = process.argv;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 480, height: 300 } });
if (process.env.NO_REMOTE) await page.route(/workers\.dev/, (r) => r.abort());
await page.goto(`${base}?quick=${p1},${p2},${stage}`, { waitUntil: 'load', timeout: 180000 });
const t0 = Date.now();
while (Date.now() - t0 < 300000) {
  if (await page.evaluate(() => { const g = window.__game; return !!(g && g.p1 && g.p1.t3actions && Object.keys(g.p1.t3actions).length && g.roundState === 'fight'); }).catch(() => false)) break;
  await page.waitForTimeout(1000);
}
const cdp = await page.context().newCDPSession(page);
await cdp.send('Profiler.enable'); await cdp.send('Profiler.setSamplingInterval', { interval: 200 });
await page.evaluate(() => { window.__simProbeReady = true; });
await cdp.send('Profiler.start');
const res = await page.evaluate(async ({ N, pressMs, attrib, prewarm }) => {
  const g = window.__game, f1 = g.p1, f2 = g.p2;
  const prewarmMs = [];
  g.roundTime = 0; g.timer = Infinity;
  // --attrib: wrap every method of the Fighter and Game prototypes (and the game's helper objects) with an
  // inclusive timer, so a spike frame lists which calls it spent its time in (inclusive: nested calls overlap).
  const acc = new Map();
  if (attrib) {
    const wrapAll = (obj, label) => {
      if (!obj) return;
      for (const k of Object.getOwnPropertyNames(obj)) {
        if (k === 'constructor' || k === 'update' && label === 'Game') continue;
        const d = Object.getOwnPropertyDescriptor(obj, k);
        if (!d || typeof d.value !== 'function' || d.get || d.set) continue;
        const f = d.value, name = label + '.' + k;
        obj[k] = function (...a) { const s = performance.__real(); try { return f.apply(this, a); } finally { acc.set(name, (acc.get(name) || 0) + performance.__real() - s); } };
      }
    };
    performance.__real = performance.now.bind(performance);
    wrapAll(Object.getPrototypeOf(f1), 'Fighter');
    wrapAll(Object.getPrototypeOf(g), 'Game');
    for (const [k, o] of Object.entries({ hitfx: g.hitfx, stageBreaks: g.stageBreaks, rage: g.rage, soulurge: g.soulurge, soul: g.soul, ai: g.ai, arena: g.arena, ui: g.ui }))
      if (o) wrapAll(Object.getPrototypeOf(o) === Object.prototype ? o : Object.getPrototypeOf(o), k);
  }
  // PREWARM=1: run both fighters' move-clip prewarm to completion first, as the round intro does in the real loop
  // (game.js _prewarmTick); the run then shows what a first press costs once the warm list is bound.
  if (prewarm) for (const f of [f1, f2]) if (f && f.prewarmAttackClips) { const s = performance.now(); let k = 0; while (!f.prewarmAttackClips(50) && k++ < 400); prewarmMs.push(+(performance.now() - s).toFixed(1)); }
  const realRender = g.arena.render.bind(g.arena);
  g.arena.render = () => {};                       // measure the sim only
  g.paused = true;                                 // the rAF loop no longer steps the sim
  const real = performance.now.bind(performance);
  let simT = real();
  performance.now = () => simT;
  // P1's own move list: every key its moveset can fire (fall back to the four buttons)
  let keys = [];
  try { keys = Object.keys((f1.moveset && (f1.moveset.moves || f1.moveset)) || {}).filter((k) => /^[a-z/+0-9,~.:_ -]+$/i.test(k) && k.length < 24); } catch (e) { /* none */ }
  if (keys.length < 4) keys = ['1', '2', '3', '4', '1,2', 'd/f+1', 'b+2', 'f+4', 'd+3', '1+2'];
  let ki = 0, nextPress = 0;
  const frames = [];
  const seen = new Set();
  let last1 = null, last2 = null, hp1 = f1.hp, hp2 = f2.hp;
  for (let i = 0; i < N; i++) {
    const ev = [];
    if (simT >= nextPress && f1.state !== 'attack') {
      const k = keys[ki++ % keys.length];
      const ok = (() => { try { return !!f1.tryAttack(k); } catch (e) { return false; } })();
      ev.push((ok ? 'press ' : 'press-refused ') + k);
      nextPress = simT + pressMs;
    }
    const s = real();
    simT += 1000 / 60;
    if (g._hitStop > 0) g._hitStop -= 1 / 60;
    else { g._update(1 / 120); g._update(1 / 120); }
    const ms = real() - s;
    let top = null;
    if (attrib && ms > 3) top = [...acc.entries()].filter(([k]) => !/^Game\._update$|^Fighter\.update$/.test(k)).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([k, v]) => `${k} ${v.toFixed(1)}`);
    acc.clear();
    const a1 = f1.state === 'attack' ? (f1.attack && f1.attack.moveKey) || f1.attackName : null;
    const a2 = f2.state === 'attack' ? (f2.attack && f2.attack.moveKey) || f2.attackName : null;
    if (a1 && a1 !== last1) { const first = !seen.has('p1:' + a1); seen.add('p1:' + a1); ev.push(`p1 move ${a1}${first ? ' (first)' : ''}`); }
    if (a2 && a2 !== last2) { const first = !seen.has('p2:' + a2); seen.add('p2:' + a2); ev.push(`p2 move ${a2}${first ? ' (first)' : ''}`); }
    last1 = a1; last2 = a2;
    if (f2.hp < hp2) ev.push(`p1 hit ${(hp2 - f2.hp).toFixed(1)} ${f2.state}${f2._reaction ? ' ' + f2._reaction : ''}`);
    if (f1.hp < hp1) ev.push(`p2 hit ${(hp1 - f1.hp).toFixed(1)} ${f1.state}${f1._reaction ? ' ' + f1._reaction : ''}`);
    if (f1.hp < f1.maxHp * 0.4) f1.hp = f1.maxHp;
    if (f2.hp < f2.maxHp * 0.4) f2.hp = f2.maxHp;
    hp1 = f1.hp; hp2 = f2.hp;
    if (g.roundState !== 'fight') { ev.push('round ' + g.roundState); }
    frames.push(top ? { i, ms: +ms.toFixed(3), ev, top } : { i, ms: +ms.toFixed(3), ev });
    // let the browser breathe now and then (GC, timers) without advancing the sim clock
    if (i % 120 === 119) await new Promise((r) => setTimeout(r, 0));
  }
  performance.now = real; g.arena.render = realRender; g.paused = false;
  return { frames, keys: keys.length, prewarmMs };
}, { N: +framesArg, pressMs: +pressArg, attrib: !!process.env.ATTRIB, prewarm: !!process.env.PREWARM });
const { profile } = await cdp.send('Profiler.stop');
await browser.close();
const F = res.frames;
const sorted = F.map((f) => f.ms).sort((a, b) => a - b);
const q = (p) => +sorted[Math.min(sorted.length - 1, Math.floor(sorted.length * p))].toFixed(2);
// attribute: frames with events vs quiet frames, first use vs repeat
const cls = (f) => f.ev.some((e) => / \(first\)/.test(e)) ? 'move-first-use'
  : f.ev.some((e) => /^p[12] move /.test(e)) ? 'move-repeat'
  : f.ev.some((e) => /^p[12] hit /.test(e)) ? 'hit'
  : f.ev.some((e) => /^press/.test(e)) ? 'press-only' : 'quiet';
const groups = {};
for (const f of F) { const c = cls(f); (groups[c] = groups[c] || []).push(f.ms); }
const stats = Object.fromEntries(Object.entries(groups).map(([k, v]) => { const s = [...v].sort((a, b) => a - b); return [k, { n: v.length, median: +s[Math.floor(s.length / 2)].toFixed(2), max: +s[s.length - 1].toFixed(2), mean: +(v.reduce((a, b) => a + b, 0) / v.length).toFixed(2) }]; }));
const worst = [...F].sort((a, b) => b.ms - a.ms).slice(0, 25);
const self = new Map(), byFile = new Map();
const byId = new Map(profile.nodes.map((n) => [n.id, n]));
profile.samples.forEach((id, i) => {
  const n = byId.get(id); if (!n) return; const cf = n.callFrame; const ms = (profile.timeDeltas[i] || 0) / 1000;
  const file = cf.url ? cf.url.split('/').slice(-2).join('/') : `(${cf.functionName || 'native'})`;
  const key = `${cf.functionName || '(anon)'} ${file}:${cf.lineNumber + 1}`;
  self.set(key, (self.get(key) || 0) + ms); byFile.set(file, (byFile.get(file) || 0) + ms);
});
for (const k of ['((idle))', '((program))']) byFile.delete(k);
const total = [...byFile.values()].reduce((a, b) => a + b, 0);
const top = (m, n) => [...m.entries()].filter(([k]) => !/^\(idle\)|^\(program\)/.test(k)).sort((a, b) => b[1] - a[1]).slice(0, n).map(([k, v]) => ({ k, ms: +v.toFixed(0), pct: +(100 * v / total).toFixed(1) }));
const report = { p1, p2, stage, frames: F.length, movesPressedFrom: res.keys, prewarmMs: res.prewarmMs,
  perFrameMs: { median: q(0.5), p90: q(0.9), p95: q(0.95), p99: q(0.99), max: q(1) },
  byKind: stats, worst, topFunctions: top(self, 40), topFiles: top(byFile, 20) };
fs.writeFileSync(out, JSON.stringify(report, null, 1));
console.log(JSON.stringify({ perFrameMs: report.perFrameMs, byKind: stats, worst: worst.slice(0, 12), topFiles: report.topFiles.slice(0, 15), topFunctions: report.topFunctions.slice(0, 25) }, null, 1));

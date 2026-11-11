// tools/anim/string_sim_probe.mjs — press a fighter's strings at EXACT real-time spacing, independent of render speed.
//
// Why (2026-11-11, owner on Pantera: "only the punch combos are working ... the kick strings and [grapple] combos ...
// aren't working"): software WebGL runs the game ~15x slower than the wall clock, so a key-press probe
// (string_input_probe.mjs) presses 220 ms apart while the game sees ~15 ms. Input timing then lies. This probe stops
// the game's own loop, replaces performance.now() with a simulated clock, and steps the game exactly as game.js
// _loop does at 60 fps (2 fixed 1/120 s steps per frame; hitstop counts down per frame), pressing buttons through
// the InputManager's own entry points (_tekken / _stick8, as test/t7-graph-adapter-pantera.test.mjs does) at exact
// simulated times. Nothing is rendered per step, so it is fast and deterministic.
//
// usage: NO_REMOTE=1 node tools/anim/string_sim_probe.mjs <game-url> <out.json> <p1> <p2> "<s1>|<s2>|..." [gapMs] [holdMs]
//   each step: [dir+]buttons ('3', 'b+1', 'd/f+3', '1+2'); gapMs = press-to-press spacing (default 150), holdMs = how
//   long each button is held (default 50).
import { createRequire } from 'module';
import fs from 'fs';
const { chromium } = createRequire(import.meta.url)('playwright');
const [,, base, out, p1 = 'pantera', p2 = 'thor', list = '1,2|3,4', gapArg = '150', holdArg = '50', stage = 'shrine'] = process.argv;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 480, height: 300 } });
if (process.env.NO_REMOTE) await page.route(/workers\.dev/, (r) => r.abort());
await page.goto(`${base}?quick=${p1},${p2},${stage}`, { waitUntil: 'load', timeout: 180000 });
const t0 = Date.now();
while (Date.now() - t0 < 240000) {
  if (await page.evaluate(() => { const g = window.__game; return !!(g && g.p1 && g.p1.t3actions && Object.keys(g.p1.t3actions).length && g.roundState === 'fight'); }).catch(() => false)) break;
  await page.waitForTimeout(1000);
}
const results = await page.evaluate(async ({ list, gap, hold }) => {
  const g = window.__game, f = g.p1, inp = g.input;
  g.ai = { update() {}, reset() {} }; g.roundTime = 0; g.timer = Infinity;
  g.paused = true;                                   // the rAF loop keeps rendering but no longer steps the sim
  const real = performance.now.bind(performance);
  let simT = real();
  performance.now = () => simT;                       // every window in input.js / movesets.js / fighter.js reads this
  const DIRV = { n: [0, 0], f: [1, 0], b: [-1, 0], d: [0, -1], u: [0, 1], 'd/f': [0.8, -0.8], 'd/b': [-0.8, -0.8], 'u/f': [0.8, 0.8], 'u/b': [-0.8, 0.8] };
  const log = []; let lastPlan = null;
  const ta = f.tryAttack.bind(f);
  f.tryAttack = (n, ...a) => { const r = ta(n, ...a); log.push({ t: simT, ev: 'press', n, ok: !!r, state: f.state }); return r; };
  const frame = () => {  // one 60 Hz frame exactly as game.js _loop: hitstop counts down, else 2 fixed steps
    simT += 1000 / 60;
    if (g._hitStop > 0) g._hitStop -= 1 / 60;
    else { g._update(1 / 120); g._update(1 / 120); }
    const p = f._atkPlan; const id = p && p.id != null ? p.id : null;
    if (id != null && id !== lastPlan) { lastPlan = id; log.push({ t: simT, ev: 'move', plan: p.name, kind: p.kind, key: f.attack && f.attack.moveKey }); }
    g.p2.hp = g.p2.maxHp;
  };
  const run = (ms) => { for (let i = 0; i < Math.round(ms / (1000 / 60)); i++) frame(); };
  const stick = (d) => { const v = DIRV[d || 'n']; if (!d || d === 'n') inp.stickNeutral(); else inp._stick8(v[0], v[1]); };
  const out = [];
  for (const s of list.split('|')) {
    for (let i = 0; i < 600 && f.state !== 'idle'; i++) frame();
    run(800);                                          // past every string / grace window
    f.root.position.x = 0; g.p2.root.position.x = (f.facing || 1) * 1.0;
    const from = log.length;
    const steps = s.split(',');
    const RE = /^(?:(d\/f|d\/b|u\/f|u\/b|[fbud])\+)?([1-4](?:\+[1-4])*)$/;
    for (let si = 0; si < steps.length; si++) {
      const step = steps[si];
      const m = RE.exec(step.trim());
      if (!m) { log.push({ ev: 'bad-step', step }); break; }
      if (m[1]) { stick(m[1]); run(34); }             // the direction lands a couple of frames before the button
      const btns = m[2].split('+');
      for (const b of btns) { inp.held[b] = true; inp._tekken(b, simT); }
      run(hold);
      for (const b of btns) inp.held[b] = false;
      stick('n');
      // press-to-press spacing is exactly gap: the NEXT step's direction lead-in comes out of this rest
      const nx = si + 1 < steps.length ? RE.exec(steps[si + 1].trim()) : null;
      run(Math.max(0, gap - hold - (nx && nx[1] ? 34 : 0)));
    }
    run(1500);
    const ev = log.slice(from);
    out.push({ string: s, pressed: ev.filter((e) => e.ev === 'press').map((e) => e.n + (e.ok ? '' : ` (refused, ${e.state})`)),
      moves: ev.filter((e) => e.ev === 'move').map((e) => `${e.key || '?'} [${e.kind}] ${e.plan}`) });
  }
  performance.now = real; g.paused = false;
  return out;
}, { list, gap: +gapArg, hold: +holdArg });
for (const r of results) console.log(JSON.stringify(r));
fs.writeFileSync(out, JSON.stringify(results, null, 1));
await browser.close();

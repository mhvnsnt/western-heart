// tools/anim/string_input_probe.mjs — type a fighter's strings with REAL key presses and record how far each one gets.
//
// Why (owner 2026-11-11, on Pantera): "only the punch combos are working ... the kick strings and [grapple] combos
// and ... a lot of different combos aren't working". tools/anim/t7_attack_probe.mjs calls fighter.tryAttack(notation)
// and so skips the input path entirely. This presses the keyboard the way a player does (Digit1..4 = 1..4, arrows =
// directions, P1 faces right so ArrowRight is forward), one string step every STEP_MS, and logs every move the fighter
// actually starts (attack plan name + resolved move key), so a string that breaks shows exactly where.
//
// usage: NO_REMOTE=1 node tools/anim/string_input_probe.mjs <game-url> <out.json> <p1> <p2> "<s1>|<s2>|..." [stepMs]
//   e.g. "1,2|3,2|b+1,4|b+2,4|1+3,1|2+4,1"   (each step: [dir+]buttons, chords with '+': 1+2, d/f+1)
import { createRequire } from 'module';
import fs from 'fs';
const { chromium } = createRequire(import.meta.url)('playwright');
const [,, base, out, p1 = 'pantera', p2 = 'thor', list = '1,2|3,2', stepMsArg = '220', stage = 'shrine'] = process.argv;
const STEP_MS = +stepMsArg;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 640, height: 400 } });
if (process.env.NO_REMOTE) await page.route(/workers\.dev/, (r) => r.abort());
await page.goto(`${base}?quick=${p1},${p2},${stage}`, { waitUntil: 'load', timeout: 180000 });
const t0 = Date.now();
while (Date.now() - t0 < 240000) {
  if (await page.evaluate(() => { const g = window.__game; return !!(g && g.p1 && g.p1.t3actions && Object.keys(g.p1.t3actions).length && g.roundState === 'fight'); }).catch(() => false)) break;
  await page.waitForTimeout(1000);
}
await page.evaluate(() => {
  const g = window.__game; g.ai = { update() {}, reset() {} }; g.roundTime = 0; g.timer = Infinity;
  const hp = g.p2.maxHp; setInterval(() => { if (g.p2.hp < hp) g.p2.hp = hp; if (g.p1.hp < g.p1.maxHp) g.p1.hp = g.p1.maxHp; }, 100);
  window.__whStart = { p1: g.p1.root.position.clone(), p2: g.p2.root.position.clone() };
  // log every move start: the attack plan the fighter picked and the move key it resolved
  const L = window.__whMoves = [];
  let last = null;
  const watch = () => {
    const f = g.p1, p = f._atkPlan, key = f.attack && f.attack.moveKey;
    const sig = p && p.id != null ? p.id : null;
    if (sig != null && sig !== last) { last = sig; L.push({ t: performance.now(), plan: p.name, kind: p.kind, key: key || null, attackName: f.attackName || null }); }
    requestAnimationFrame(watch);
  };
  requestAnimationFrame(watch);
});
const DIR = { f: ['ArrowRight'], b: ['ArrowLeft'], d: ['ArrowDown'], u: ['ArrowUp'], 'd/f': ['ArrowDown', 'ArrowRight'], 'd/b': ['ArrowDown', 'ArrowLeft'], 'u/f': ['ArrowUp', 'ArrowRight'], 'u/b': ['ArrowUp', 'ArrowLeft'] };
const results = [];
for (const s of list.split('|')) {
  // reset spacing and wait for neutral
  await page.evaluate(async () => {
    const g = window.__game, f = g.p1;
    const until = async (c, ms) => { const e = Date.now() + ms; while (!c() && Date.now() < e) await new Promise((r) => setTimeout(r, 20)); };
    await until(() => f.state === 'idle', 20000);
    await new Promise((r) => setTimeout(r, 700));  // past any string grace window
    if (window.__whStart) { f.root.position.copy(window.__whStart.p1); g.p2.root.position.x = f.root.position.x + (f.facing || 1) * 1.0; }
  });
  const n0 = await page.evaluate(() => window.__whMoves.length);
  for (const step of s.split(',')) {
    const m = /^(?:(d\/f|d\/b|u\/f|u\/b|[fbud])\+)?([1-4](?:\+[1-4])*)$/.exec(step.trim());
    if (!m) { results.push({ string: s, error: 'cannot type step ' + step }); break; }
    const dirs = m[1] ? DIR[m[1]] : [];
    for (const k of dirs) await page.keyboard.down(k);
    if (dirs.length) await page.waitForTimeout(40);
    const btns = m[2].split('+').map((b) => 'Digit' + b);
    for (const k of btns) await page.keyboard.down(k);   // a chord: all buttons inside input.js's 50 ms chord window
    await page.waitForTimeout(45);
    for (const k of btns) await page.keyboard.up(k);
    for (const k of dirs) await page.keyboard.up(k);
    await page.waitForTimeout(Math.max(0, STEP_MS - 85));
  }
  await page.waitForTimeout(2500);
  const moves = await page.evaluate((n) => window.__whMoves.slice(n), n0);
  const r = { string: s, steps: s.split(',').length, started: moves.length, moves: moves.map((x) => `${x.key || x.attackName || '?'} [${x.kind}]`) };
  results.push(r);
  console.log(JSON.stringify(r));
}
fs.writeFileSync(out, JSON.stringify(results, null, 1));
await browser.close();

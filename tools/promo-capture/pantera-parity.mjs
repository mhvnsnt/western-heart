// Pantera vs King T7 parity: for every damaging input in King's moves pack (tests from parity-tests.json), press the
// real keys, step 30 fps virtual frames, record every HP drop on Zen (per hit) and every clip Pantera's mixer runs.
// usage: node pantera-parity.mjs <outDir> <shard> <nShards>
import { launch, startFight, frame, key, ensureDir } from './lib.mjs';
import fs from 'node:fs';
const OUT = ensureDir(process.argv[2]); const SH = +(process.argv[3] || 0), NS = +(process.argv[4] || 1);
const DIR = { f: ['KeyD'], b: ['KeyA'], d: ['KeyS'], u: ['KeyW'], 'd/f': ['KeyS', 'KeyD'], 'd/b': ['KeyS', 'KeyA'], 'u/f': ['KeyW', 'KeyD'], 'u/b': ['KeyW', 'KeyA'] };
const BTN = { 1: 'Digit1', 2: 'Digit2', 3: 'Digit3', 4: 'Digit4' };
const TESTS = JSON.parse(fs.readFileSync(new URL('./parity-tests.json', import.meta.url))).filter((t, i) => i % NS === SH);
const done = new Set(fs.existsSync(`${OUT}/rows-${SH}.jsonl`) ? fs.readFileSync(`${OUT}/rows-${SH}.jsonl`, 'utf8').trim().split('\n').filter(Boolean).map(l => JSON.parse(l).input) : []);
const { browser, page, errors } = await launch({ width: 640, height: 360 });
await startFight(page, 'pantera', 'zen');
const clipsNow = () => page.evaluate(() => { const f = window.__game.p1, m = f.mixer; const out = [];
  if (m && m._actions) for (const a of m._actions) if (a.isRunning() && a.getEffectiveWeight() > 0.05) out.push(a.getClip().name);
  if (f._t3current) out.push(f._t3current.getClip().name); if (f.state === 'tekgraph' && f._t7gRec) out.push('T7G:' + f._t7gRec.name);
  return { clips: out, atk: f.attackName || null, plan: f._atkPlan ? { kind: f._atkPlan.kind, why: f._atkPlan.why, t7damage: f._atkPlan.t7damage } : null }; });
const S = { dist: 3.4, yaw: 0.35 };
for (const t of TESTS) {
  if (done.has(t.input)) continue;
  await page.evaluate(() => { const g = window.__game; g.p1.root.position.x = -0.75; g.p2.root.position.x = 0.75; g.p2.hp = g.p2.maxHp; g.p1.hp = g.p1.maxHp; g.p1.vx = g.p2.vx = 0; });
  for (let i = 0; i < 90; i++) { // settle: both fighters back to neutral before the next input
    const r = await frame(page, S);
    if (i >= 8 && r.p1.state === 'idle' && r.p2.state === 'idle' && !r.p1.atk) break;
  }
  await page.evaluate(() => { const g = window.__game; g.p1.root.position.x = -0.75; g.p2.root.position.x = 0.75; g.p2.hp = g.p2.maxHp; g.p1.vx = g.p2.vx = 0; });
  for (let i = 0; i < 4; i++) await frame(page, S);
  let hp = (await frame(page, S)).p2.hp; const hits = []; const clips = new Set(), plans = new Set(), atks = new Set();
  const step = async () => { const r = await frame(page, S); if (r.p2.hp < hp - 1e-6) hits.push(+(hp - r.p2.hp).toFixed(2)); hp = r.p2.hp;
    const c = await clipsNow(); c.clips.forEach(x => clips.add(x)); if (c.atk) atks.add(c.atk); if (c.plan && c.plan.why) plans.add(`${c.plan.kind}|${c.plan.why}|${c.plan.t7damage}`); };
  for (let si = 0; si < t.steps.length; si++) {
    const m = t.steps[si].match(/^(?:(d\/f|d\/b|u\/f|u\/b|f|b|d|u)\+)?([1-4](?:\+[1-4])*)$/);
    const dirs = m[1] ? DIR[m[1]] : [], btns = m[2].split('+').map(x => BTN[x]);
    for (const k of dirs) await key(page, k, true);
    if (dirs.length) await step();
    for (const k of btns) await key(page, k, true);
    await step();
    for (const k of btns) await key(page, k, false);
    for (const k of dirs) await key(page, k, false);
    const hold = si < t.steps.length - 1 ? 4 : 30;
    for (let i = 0; i < hold; i++) await step();
  }
  const row = { input: t.input, expect: t.expect, hits, total: +hits.reduce((a, b) => a + b, 0).toFixed(2), clips: [...clips].filter(c => !/stance|walk|idle|Kg_sKAM|loco/i.test(c)), atks: [...atks], plans: [...plans] };
  fs.appendFileSync(`${OUT}/rows-${SH}.jsonl`, JSON.stringify(row) + '\n'); console.log(t.input, JSON.stringify(hits), row.clips.join(' '));
}
fs.appendFileSync(`${OUT}/errors-${SH}.txt`, errors.join('\n') + '\n');
await browser.close();
console.log('SHARD DONE');

// Pantera vs King T7 parity: for every damaging input in King's moves pack (tests from parity-tests.json), press the
// real keys, step 30 fps virtual frames, record every HP drop on Zen (per hit) and every clip Pantera's mixer runs.
// Stance tests (BT/FC/SS/WS) enter the named set-up state first, the same way test/e2e/moveset-sweep.page.js does.
// usage: node pantera-parity.mjs <outDir> <shard> <nShards>
import { launch, startFight, frame, key, ensureDir } from './lib.mjs';
import fs from 'node:fs';
const OUT = ensureDir(process.argv[2]); const SH = +(process.argv[3] || 0), NS = +(process.argv[4] || 1);
const DIR = { f: ['KeyD'], b: ['KeyA'], d: ['KeyS'], u: ['KeyW'], 'd/f': ['KeyS', 'KeyD'], 'd/b': ['KeyS', 'KeyA'], 'u/f': ['KeyW', 'KeyD'], 'u/b': ['KeyW', 'KeyA'] };
const BTN = { 1: 'Digit1', 2: 'Digit2', 3: 'Digit3', 4: 'Digit4' };
const TESTS = JSON.parse(fs.readFileSync(new URL('./parity-tests.json', import.meta.url))).filter((t, i) => i % NS === SH)
  .filter((t) => !process.env.PARITY_ONLY || process.env.PARITY_ONLY.split(';').includes(t.input));
const done = new Set(fs.existsSync(`${OUT}/rows-${SH}.jsonl`) ? fs.readFileSync(`${OUT}/rows-${SH}.jsonl`, 'utf8').trim().split('\n').filter(Boolean).map(l => JSON.parse(l).input) : []);
const { browser, page, errors } = await launch({ width: 640, height: 360 });
await startFight(page, 'pantera', 'zen');
if (process.env.PARITY_TRACE) await page.evaluate(() => { const g = window.__game; const P = Object.getPrototypeOf(g.p2); const orig = P.receiveHit; window.__hits = [];
  P.receiveHit = function (move, attacker, ...rest) { const p = attacker && attacker._atkPlan; const hp0 = this.hp; const st = this.state; const r = orig.call(this, move, attacker, ...rest);
    window.__hits.push({ dmg: +(hp0 - this.hp).toFixed(2), r, defState: st, moveDamage: move && move.damage, moveKey: move && move.moveKey, planOk: !!p && p.id === attacker._attackId, kind: p && p.kind, t7damage: p && p.t7damage, maxT: attacker._maxT, vt: attacker._vtriggerT, vb: attacker._vbreakT, kindle: !!attacker.kindle, onGround: this.onGround }); return r; }; });
const clipsNow = () => page.evaluate(() => { const f = window.__game.p1, m = f.mixer; const out = [];
  if (m && m._actions) for (const a of m._actions) if (a.isRunning() && a.getEffectiveWeight() > 0.05) out.push(a.getClip().name);
  if (f._t3current) out.push(f._t3current.getClip().name); if (f.state === 'tekgraph' && f._t7gRec) out.push('T7G:' + f._t7gRec.name);
  return { clips: out, atk: f.attackName || null, plan: f._atkPlan ? { kind: f._atkPlan.kind, why: f._atkPlan.why, t7damage: f._atkPlan.t7damage } : null }; });
const S = { dist: 3.4, yaw: 0.35 };
const held = new Set();
const down = async (k) => { if (!held.has(k)) { await key(page, k, true); held.add(k); } };
const up = async (k) => { if (held.has(k)) { await key(page, k, false); held.delete(k); } };
const upAll = async () => { for (const k of [...held]) await up(k); };
for (const t of TESTS) {
  if (done.has(t.input)) continue;
  await upAll();
  await page.evaluate(() => { const g = window.__game; g.p1.root.position.x = -0.75; g.p2.root.position.x = 0.75; g.p2.hp = g.p2.maxHp; g.p1.hp = g.p1.maxHp; g.p1.vx = g.p2.vx = 0; g.p1._bt = false; g.p1.stance = null; g.p1.stanceT = 0; g.p1._risingT = 0; });
  for (let i = 0; i < 90; i++) { // settle: both fighters back to neutral before the next input
    const r = await frame(page, S);
    if (i >= 8 && r.p1.state === 'idle' && r.p2.state === 'idle' && !r.p1.atk) break;
  }
  await page.evaluate(() => { const g = window.__game; g.p1.root.position.x = -0.75; g.p2.root.position.x = 0.75; g.p2.hp = g.p2.maxHp; g.p1.vx = g.p2.vx = 0; g.p1._bt = false; g.p1.stance = null; g.p1.stanceT = 0; g.p1._risingT = 0; });
  for (let i = 0; i < 4; i++) await frame(page, S);
  let hp = (await frame(page, S)).p2.hp; const hits = []; const clips = new Set(), plans = new Set(), atks = new Set();
  const step = async () => { const r = await frame(page, S); if (r.p2.hp < hp - 1e-6) hits.push(+(hp - r.p2.hp).toFixed(2)); hp = r.p2.hp;
    const c = await clipsNow(); c.clips.forEach(x => clips.add(x)); if (c.atk) atks.add(c.atk); if (c.plan && c.plan.why) plans.add(`${c.plan.kind}|${c.plan.why}|${c.plan.t7damage}`); };
  if (t.setup === 'FC') { await down('KeyS'); for (let i = 0; i < 20; i++) await step(); }
  else if (t.setup === 'WS') { await down('KeyS'); for (let i = 0; i < 20; i++) await step(); await up('KeyS'); for (let i = 0; i < 2; i++) await step(); }
  else if (t.setup === 'SS') { await page.evaluate(() => window.__game.p1.trySidestep(-1)); for (let i = 0; i < 12; i++) await step(); }
  else if (t.setup === 'BT') { await page.evaluate(() => { const f = window.__game.p1; f.stance = 'BT'; f.stanceT = 0; f._bt = true; }); }
  for (let si = 0; si < t.steps.length; si++) {
    const m = t.steps[si].match(/^(?:(d\/f|d\/b|u\/f|u\/b|f|b|d|u)\+)?([1-4](?:\+[1-4])*)$/);
    const dirs = m[1] ? DIR[m[1]] : [], btns = m[2].split('+').map(x => BTN[x]);
    for (const k of dirs) await down(k);
    if (dirs.length) await step();
    for (const k of btns) await down(k);
    await step();
    for (const k of btns) await up(k);
    for (const k of dirs) await up(k);
    const hold = si < t.steps.length - 1 ? 4 : 30;
    for (let i = 0; i < hold; i++) await step();
  }
  await upAll();
  const trace = process.env.PARITY_TRACE ? await page.evaluate(() => window.__hits && window.__hits.splice(0)) : undefined;
  const row = { trace, input: t.input, expect: t.expect, hits, total: +hits.reduce((a, b) => a + b, 0).toFixed(2), clips: [...clips].filter(c => !/stance|walk|idle|Kg_sKAM|loco/i.test(c)), atks: [...atks], plans: [...plans] };
  if (!trace) delete row.trace;
  fs.appendFileSync(`${OUT}/rows-${SH}.jsonl`, JSON.stringify(row) + '\n'); console.log(t.input, JSON.stringify(hits), row.clips.join(' '));
}
fs.appendFileSync(`${OUT}/errors-${SH}.txt`, errors.join('\n') + '\n');
await browser.close();
console.log('SHARD DONE');

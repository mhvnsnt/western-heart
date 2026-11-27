// Real-input hit test: Pantera vs Zen. For each King T7 input, press real keys, step 30fps virtual frames,
// record damage dealt, the clip(s) Pantera's mixer actually plays, and a peak-frame still.
import { launch, startFight, frame, key, ensureDir } from './lib.mjs';
import fs from 'node:fs';
const OUT = ensureDir(process.argv[2] || '/workspace/focus-nov27/pantera-hits');
const DIR = { f: ['KeyD'], b: ['KeyA'], d: ['KeyS'], u: ['KeyW'], 'd/f': ['KeyS', 'KeyD'], 'd/b': ['KeyS', 'KeyA'], 'u/f': ['KeyW', 'KeyD'], n: [] };
const BTN = { 1: 'Digit1', 2: 'Digit2', 3: 'Digit3', 4: 'Digit4' };
// [input, King T7 graph target from Kg_sKAM00_ / follow-up state (game/assets/anim/t7/king/graph.commands.json)]
const TESTS = [
  ['1', 'Kg_lp00F'], ['2', 'Kg_rp00'], ['3', 'Kg_lk00'], ['4', 'Kg_rk00'],
  ['f+1', 'Kg_lp00F'], ['f+2', 'Kg_rp00F'], ['f+3', 'Kg_lk00F'], ['f+4', 'Kg_rsbt'],
  ['b+1', 'Kg_lp00B'], ['b+2', 'Kg_rp00B'], ['b+3', 'Kg_turas'], ['b+4', 'Kg_Yakuza'],
  ['d/f+1', 'Kg_t_slpF'], ['d/f+2', 'Kg_t_srpF'], ['d/f+3', 'Kg_t_slkF'], ['d/f+4', 'Kg_t_srkF'],
  ['d+1', 'Kg_t_slp00'], ['d+2', 'Co_t_srp00'], ['d+3', 'Kg_t_slk'], ['d+4', 'Kg_t_srk'],
  ['d/b+3', 'Kg_gyakuAri'], ['d/b+4', 'Kg_loDropN'], ['u/f+4', 'Kg_jprk00F'], ['1+2', 'Kg_hiziru'],
  ['1,2', 'Kg_lprpF'], ['2,1', 'Kg_rplu4t'], ['f+2,1', 'Kg_6rplp'], ['b+1,2', 'Kg_rpTap00'], ['b+1,4', 'Kg_rpheel00'],
  ['b+2,1', 'Kg_4rplp'], ['b+2,4', 'Kg_AmericaRK'], ['d/f+3,4', 'Kg_t_slkFA'], ['d+3,4', 'Kg_Ari_kick'],
];
const only = process.argv[3] ? process.argv[3].split(';') : null;
const { browser, page, errors } = await launch({ width: 960, height: 540 });
await startFight(page, 'pantera', 'zen');
const clipsNow = () => page.evaluate(() => { const m = window.__game.p1.mixer; if (!m || !m._actions) return [];
  const f = window.__game.p1; const out = m._actions.filter(a => a.isRunning() && a.getEffectiveWeight() > 0.05).map(a => a.getClip().name + '@' + a.getEffectiveWeight().toFixed(2));
  if (f._t3current) out.push(f._t3current.getClip().name + '@cur'); if (f.state === 'tekgraph' && f._t7gRec) out.push('T7G:' + f._t7gRec.name + '@g'); return out; });
const results = [];
for (const [input, t7] of TESTS) {
  if (only && !only.includes(input)) continue;
  await page.evaluate(() => { const g = window.__game; g.p1.root.position.x = -0.75; g.p2.root.position.x = 0.75; g.p2.hp = g.p2.maxHp; g.p1.hp = g.p1.maxHp; g.p1.vx = g.p2.vx = 0; });
  for (let i = 0; i < 25; i++) await frame(page, { dist: 3.4, yaw: 0.35 });
  const hp0 = (await frame(page, { dist: 3.4, yaw: 0.35 })).p2.hp;
  const parts = input.split(',');
  const seenClips = new Set(), atks = new Set(); const states = new Set(); let shot = false;
  for (let pi = 0; pi < parts.length; pi++) {
    const p = parts[pi]; const m = p.match(/^(?:(n|f|b|d|u|d\/f|d\/b|u\/f)\+)?([1-4](?:\+[1-4])*)$/);
    const dirs = m[1] ? DIR[m[1]] : []; const btns = m[2].split('+').map(x => BTN[x]);
    for (const k of dirs) await key(page, k, true);
    if (dirs.length) await frame(page, { dist: 3.4, yaw: 0.35 });
    for (const k of btns) await key(page, k, true);
    await frame(page, { dist: 3.4, yaw: 0.35 });
    for (const k of btns) await key(page, k, false);
    for (const k of dirs) await key(page, k, false);
    const hold = pi < parts.length - 1 ? 9 : 34;
    for (let i = 0; i < hold; i++) {
      const r = await frame(page, { dist: 3.4, yaw: 0.35 });
      if (r.p1.atk) atks.add(r.p1.atk); states.add(r.p1.state);
      if (i % 3 === 0) for (const c of await clipsNow()) seenClips.add(c.split('@')[0]);
      if (!shot && pi === parts.length - 1 && i === 7) { await page.screenshot({ path: `${OUT}/${input.replace(/[\/+,]/g, '_')}.png` }); shot = true; }
    }
  }
  const end = await frame(page, { dist: 3.4, yaw: 0.35 });
  const row = { input, t7_target: t7, game_atk: [...atks], states: [...states], clips: [...seenClips].filter(c => !/idle|walk|stance|loco|Kg_sKAM/i.test(c)).slice(0, 6), all_clips: [...seenClips].slice(0, 10), damage: +(hp0 - end.p2.hp).toFixed(1), p2_state: end.p2.state };
  console.log(JSON.stringify(row)); results.push(row); fs.appendFileSync(`${OUT}/rows.jsonl`, JSON.stringify(row) + '\n');
}
fs.writeFileSync(`${OUT}/results.json`, JSON.stringify({ when: new Date().toISOString(), build: 'https://western-heart.pages.dev', results, errors }, null, 1));
await browser.close();

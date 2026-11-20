// tools/anim/plan_coverage_audit.mjs — which moves of every fighter would play NO clip (owner 2026-11-01: "his
// animations are falling back to T pose ... need to get solved for all the characters in the game starting with the
// easiest one first having full 100% of their move list and animation playing in the fight").
//
// A move whose attack plan has no clip name draws the fighter's BIND POSE (the T-pose) for its whole duration. The
// browser probes (move_coverage_probe.mjs, input-verify/input_coverage_probe.mjs) see this one fighter at a time at
// ~15 min each; this asks the game's own planner (Fighter._attackClipPlan, built exactly as test/attack-anim.test.mjs
// builds a fighter in Node) for EVERY move of EVERY roster fighter in seconds. In Node the real T7 per-move clips are
// not loaded, so this is conservative: a move it lists may still be covered by a T7 clip in the browser, but a move the
// browser T-poses on is always listed here. Fighters are ranked easiest first (fewest no-clip moves).
//
//   node tools/anim/plan_coverage_audit.mjs [--json out.json] [--md out.md] [fighter ...]
import fs from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const THREE = await import('three');
const M = await import(join(ROOT, 'game/js/movesets.js'));
const T = await import(join(ROOT, 'game/js/t3anims.js'));
const F = await import(join(ROOT, 'game/js/fighter.js'));
const { FULL_ROSTER } = await import(join(ROOT, 'game/js/roster-full.js'));

const args = process.argv.slice(2);
const opt = (k) => { const i = args.indexOf(k); return i >= 0 ? args.splice(i, 2)[1] : null; };
const jsonOut = opt('--json'), mdOut = opt('--md');
const quiet = { log: console.log, warn: console.warn };
console.log = () => {}; console.warn = () => {};
await M.loadFighterMovesets();
const IDS = args.length ? args : FULL_ROSTER.map((c) => c.id);
await M.ensureMovesets(IDS);
console.log = quiet.log; console.warn = quiet.warn;

async function fighter(id) {
  const bank = F.bankIdFor(id, id);
  const save = console.log; console.log = () => {};
  const clips = bank ? await T.loadT3Clips(THREE, bank) : null;
  console.log = save;
  const f = Object.create(F.Fighter.prototype);
  f.char = { id }; f._movesetId = id; f.t3actions = {};
  f._t3 = bank ? { bank, clips } : null;
  return f;
}

const report = [];
for (const id of IDS) {
  const ms = M.getFighterMoveset(id);
  if (!ms || !ms.moves) continue;
  const f = await fighter(id);
  const rows = { total: 0, noclip: [], kinds: {} };
  const save = console.log; console.log = () => {};
  for (const n of Object.keys(ms.slots || ms.moves)) {
    let mv = null;
    try { mv = F.getRealMove(id, n); } catch { mv = null; }
    if (!mv) continue;
    rows.total++;
    let p = null;
    try { p = f._t3 ? f._attackClipPlan(mv, n) : null; } catch { p = null; }
    const kind = p ? (p.kind || 'plan') : (f._t3 ? 'none' : 'no-bank');
    rows.kinds[kind] = (rows.kinds[kind] || 0) + 1;
    if (!p || !p.name) rows.noclip.push(n);
  }
  console.log = save;
  report.push({ fighter: id, bank: f._t3 ? f._t3.bank : null, total: rows.total, noclip: rows.noclip.length,
    pct: rows.total ? +(100 * (rows.total - rows.noclip.length) / rows.total).toFixed(1) : 0, kinds: rows.kinds,
    examples: rows.noclip.slice(0, 12) });
}
report.sort((a, b) => a.noclip - b.noclip || b.total - a.total);
const tot = report.reduce((a, r) => a + r.total, 0), bad = report.reduce((a, r) => a + r.noclip, 0);
const md = [
  '# Move clip coverage, every fighter (`tools/anim/plan_coverage_audit.mjs`)', '',
  `${report.length} fighters, ${tot} moves: **${bad} would play no clip** (bind pose = T-pose) by the game's own planner (Node; real T7 clips not loaded, so conservative). Easiest first.`, '',
  '| fighter | bank | moves | with a clip | no clip | examples |', '|---|---|---|---|---|---|',
  ...report.map((r) => `| ${r.fighter} | ${r.bank || '—'} | ${r.total} | ${r.pct}% | ${r.noclip} | ${r.examples.slice(0, 6).map((e) => '`' + e + '`').join(' ')} |`),
].join('\n') + '\n';
if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify(report, null, 1));
if (mdOut) fs.writeFileSync(mdOut, md);
console.log(md.split('\n').slice(0, 3).join('\n'));
console.log(report.slice(0, 60).map((r) => `${r.fighter}:${r.noclip}/${r.total}`).join('  '));

// tools/input-verify/stance_reachability_audit.mjs — which STATE / STANCE-PREFIXED moves can a player actually reach?
// (owner 2026-11-01: "you said many of the moves need a state or stance prefix to fire then set that up set all that up
// with all the moves ... for all the characters to have playing move animation to all of their moves").
//
// A move keyed 'P.<input>' (WS.1, FC.d+3, BT.3, JGR.2, FUFT.3, AB1.1,1+2 ...) only resolves while the fighter is in
// state / stance P (game/js/movesets.js TekkenBuffer prefixes, fighter.js _inputCtx). For every roster fighter this
// classifies every prefix by the way into it, against the game's own code:
//   engine    a context the engine sets itself: WS (rising), FC (crouch), SS (sidestep), AIR (airborne), WR (running),
//             R / RD (rage), FLANK_L/R/B (at the foe's side / back), soul systems (SPIRIT, SOUL9, ...), and the
//             ground states the knockdown leaves (FUFT, plus FUHT when the moveset has it);
//   stance    a stance some move of this fighter enters (moveset stance_after: b+1+2 -> JGR);
//   throw     a chain-throw stage a throw of this fighter opens (movesets.js throwStageTag: 'Arm Breaker (AB1)' -> AB1);
//   NO ENTRY  nothing in the game puts the fighter there: those moves can never fire.
//
//   node tools/input-verify/stance_reachability_audit.mjs [--json out.json] [--md out.md] [fighter ...]
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
await import(path.join(ROOT, 'tools/anim/node_game_env.mjs'));
const M = await import(path.join(ROOT, 'game/js/movesets.js'));
const FML = await import(path.join(ROOT, 'game/js/full-movelist.js'));

const args = process.argv.slice(2);
const opt = (k) => { const i = args.indexOf(k); return i >= 0 ? args.splice(i, 2)[1] : null; };
const jsonOut = opt('--json'), mdOut = opt('--md');

// contexts fighter.js _inputCtx / movesets.js TekkenBuffer resolve on their own (read from the code, 2026-11-01)
export const ENGINE = {
  WS: 'while rising (release down)', FC: 'full crouch (hold down)', SS: 'sidestep', AIR: 'airborne (jump)',
  WR: 'while running (f,f,F)', R: 'rage (25% health)', RD: 'rage drive', FUFT: 'on the ground after a knockdown',
  FLANK_L: "at the foe's left side", FLANK_R: "at the foe's right side", FLANK_B: "at the foe's back",
};
for (const s of FML.SOUL_SYSTEMS) ENGINE[s.prefix] = `soul system: ${s.en}`;

const MS_DIR = path.join(ROOT, 'game/assets/movesets');
const rosterMap = JSON.parse(fs.readFileSync(path.join(ROOT, 'game/data/roster_map.json'), 'utf8'));
let fighters = (rosterMap.fighters || []).map((f) => f.id).filter((id) => fs.existsSync(path.join(MS_DIR, id + '.json')));
if (args.length) fighters = args;

export const prefixOf = (k) => { const m = /^([A-Za-z_][A-Za-z0-9_]*)\.(?=.)/.exec(k); return m ? m[1] : null; };

function audit(fid) {
  const data = JSON.parse(fs.readFileSync(path.join(MS_DIR, fid + '.json'), 'utf8'));
  M.registerMoveset(fid, data);
  const moves = data.moves || {};
  const keys = Object.keys(data.slots || moves);
  const stances = new Set(Object.values(data.stance_after || {}).filter(Boolean));
  // FUHT is set by the knockdown only when the moveset has it (fighter.js _hasGroundMoves)
  const throwTags = new Set();
  for (const [k, m] of Object.entries(moves)) {
    const grab = m && (m.isGrab || m.move_class === 'throw' || /throw/i.test(String(m.hit_level || m.note || '')));
    if (grab) { const t = M.throwStageTag(m.name); if (t) throwTags.add(t); }
    void k;
  }
  const by = {};
  for (const k of keys) {
    const p = prefixOf(k);
    if (!p) continue;
    const e = by[p] || (by[p] = { prefix: p, moves: 0, examples: [] });
    e.moves++;
    if (e.examples.length < 4) e.examples.push(k);
  }
  for (const e of Object.values(by)) {
    const p = e.prefix;
    e.way = ENGINE[p] || (p === 'FUHT' ? 'ground (head towards)' : null) ? 'engine'
      : stances.has(p) ? 'stance'
        : throwTags.has(p) ? 'throw'
          : 'NO ENTRY';
    if (p === 'BT' && stances.has('BT')) e.way = 'stance';
  }
  const list = Object.values(by).sort((a, b) => b.moves - a.moves);
  const sum = (w) => list.filter((e) => e.way === w).reduce((a, e) => a + e.moves, 0);
  return { fighter: fid, total: keys.length, prefixed: list.reduce((a, e) => a + e.moves, 0),
    engine: sum('engine'), stance: sum('stance'), throw: sum('throw'), noEntry: sum('NO ENTRY'), prefixes: list };
}

const report = [];
for (const fid of fighters) {
  try { report.push(audit(fid)); } catch (e) { report.push({ fighter: fid, error: String(e && e.message || e).slice(0, 200) }); }
}
const ok = report.filter((r) => !r.error);
const tot = (k) => ok.reduce((a, r) => a + r[k], 0);
const noEntryAll = {};
for (const r of ok) for (const e of r.prefixes) if (e.way === 'NO ENTRY') (noEntryAll[e.prefix] = noEntryAll[e.prefix] || { prefix: e.prefix, moves: 0, fighters: [] }), noEntryAll[e.prefix].moves += e.moves, noEntryAll[e.prefix].fighters.push(r.fighter);
const md = [
  '# State / stance reachability audit (`tools/input-verify/stance_reachability_audit.mjs`)', '',
  `${ok.length} fighters, ${tot('total')} move inputs, ${tot('prefixed')} of them state / stance-prefixed: ` +
  `engine context ${tot('engine')}, stance entered by a move ${tot('stance')}, chain-throw stage ${tot('throw')}, **NO ENTRY ${tot('noEntry')}** (can never fire).`, '',
  '## Prefixes nothing in the game enters, by moves affected', '',
  '| prefix | moves | fighters |', '|---|---|---|',
  ...Object.values(noEntryAll).sort((a, b) => b.moves - a.moves).map((e) => `| ${e.prefix} | ${e.moves} | ${e.fighters.slice(0, 12).join(', ')}${e.fighters.length > 12 ? ` +${e.fighters.length - 12}` : ''} |`), '',
  '## Per fighter', '',
  '| fighter | inputs | prefixed | engine | stance | throw | NO ENTRY | no-entry prefixes |', '|---|---|---|---|---|---|---|---|',
  ...report.map((r) => r.error ? `| ${r.fighter} | error: ${r.error} | | | | | | |`
    : `| ${r.fighter} | ${r.total} | ${r.prefixed} | ${r.engine} | ${r.stance} | ${r.throw} | ${r.noEntry} | ${r.prefixes.filter((e) => e.way === 'NO ENTRY').map((e) => `${e.prefix} (${e.moves})`).join(', ')} |`),
].join('\n') + '\n';
if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify(report, null, 1));
if (mdOut) fs.writeFileSync(mdOut, md);
console.log(md.split('\n').slice(0, 3).join('\n'));
console.log(Object.values(noEntryAll).sort((a, b) => b.moves - a.moves).slice(0, 40).map((e) => `${e.prefix}:${e.moves}(${e.fighters.length})`).join('  '));

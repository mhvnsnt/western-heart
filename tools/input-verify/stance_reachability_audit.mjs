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
//             a prefix the moveset itself declares a spelling alias of an entered stance
//             (moveset stance_alias, roster-100 S9 2026-11-05: phantom INS -> IND, cyborgx
//             BKP -> BACKUP) also counts — _prepare slots those rows on the canonical spelling;
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
  SIDE_L: "at the foe's left side (FLANK_KEYS)", SIDE_R: "at the foe's right side (FLANK_KEYS)", BACK: "at the foe's back (FLANK_KEYS)",
  H: 'Soul Urge on (the heat state)',
  // 2026-11-02: ground states by how the fighter fell (fighter.js knockdown), the grounded foe, the wall behind, T8 hFC
  FDFA: 'on the ground, face down, head towards (hit in the back / screw)', FUFA: 'on the ground, face up, head towards',
  FDFT: 'on the ground, face down, feet towards', FUHT: 'on the ground, head towards',
  OTG: 'the opponent is on the ground', WALL: 'own back to the wall', hFC: 'crouching (T8 hFC)',
  SSL: 'sidestep toward the foe\'s left (engine ssSide, roster-100 L5)', SSR: 'sidestep toward the foe\'s right (engine ssSide, roster-100 L5)',
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
  // fighter.js stanceAfterFromNotes (2026-11-02): a frame-data / note mention of a stance this moveset has moves for
  // ('-5 (BT)', '+3 (MNT)', 'Transition to NSS', '> DEW') enters it
  const prefixesHere = new Set([...Object.keys(moves), ...Object.keys(data.slots || {})].map((k) => (/^([A-Za-z_][A-Za-z0-9_]*)\./.exec(k) || [])[1]).filter(Boolean));
  for (const [k, m] of Object.entries(moves)) {
    if (!m) continue;
    const texts = [];
    for (const f of ['on_block', 'on_hit', 'on_ch', 't7_on_block', 't7_on_hit', 't7_on_ch', 'note', 'notes'])
      for (const x of [m[f], m.t7 && m.t7[f], m.t8 && m.t8[f]]) if (x) texts.push(String(x));
    for (const t of texts) {
      for (const mm of [...t.matchAll(/\(([A-Z][A-Za-z0-9_]{1,6})\)/g), ...t.matchAll(/(?:[Tt]ransitions? (?:to|into)|[Ee]nters?|[Gg]o(?:es)? (?:to|into)|>)\s*([A-Z][A-Z0-9_]{1,6})\b/g)])
        if (prefixesHere.has(mm[1]) && !(k.startsWith('BT.') && mm[1] === 'BT')) stances.add(mm[1]);
    }
  }
  // FUHT is set by the knockdown only when the moveset has it (fighter.js _hasGroundMoves)
  const throwTags = new Set();
  for (const [k, m] of Object.entries(moves)) {
    // engine grab test (fighter.js getRealMove isGrab): isGrab / move_class 'throw' / a T3 throw-situation
    // condition (2..0x17); the audit's older note-text test is kept as a superset for the seed set.
    const grab = m && (m.isGrab || m.move_class === 'throw' || (m.t3_condition >= 2 && m.t3_condition <= 0x17) || /throw/i.test(String(m.hit_level || m.note || '')));
    if (grab) { const t = M.throwStageTag(m.name); if (t) throwTags.add(t); if (/tackle/i.test(m.name || '')) throwTags.add('TACKLE'); }
    void k;
  }
  // Chain-throw stage graph (fighter.js _throwChainPress / _startThrowChain, 2026-11-02 audit close-out):
  // a stage row that executes becomes the current throw (its attack is forced isGrab), so the NEXT stage is
  // opened by that row's own name tag — reachability is the closure over rows keyed by a reachable tag,
  // not just the tags of raw-data grab-flagged moves. Before this pass the audit undercounted every
  // mid-chain stage (e.g. King's BACKDROP / POWER_BOMB stages, reached from inside ARM_BREAKER chains).
  let grew = true;
  while (grew) {
    grew = false;
    for (const [k, m] of Object.entries(moves)) {
      if (!m) continue;
      const p = prefixOf(k);
      if (!p || !throwTags.has(p)) continue;
      const t = M.throwStageTag(m.name);
      if (t && !throwTags.has(t)) { throwTags.add(t); grew = true; }
      if (/tackle/i.test(m.name || '') && !throwTags.has('TACKLE')) { throwTags.add('TACKLE'); grew = true; }
    }
  }
  const by = {};
  for (const k of keys) {
    const p = prefixOf(k);
    if (!p) continue;
    const e = by[p] || (by[p] = { prefix: p, moves: 0, examples: [] });
    e.moves++;
    if (e.examples.length < 4) e.examples.push(k);
  }
  const aliases = data.stance_alias || {};
  for (const e of Object.values(by)) {
    const p = e.prefix;
    e.way = ENGINE[p] ? 'engine'
      : (p === 'CD' && data.cd_entry) ? 'engine' // roster-100 L5: CD resolves only where the file declares its cd_entry
      : stances.has(p) ? 'stance'
        : (aliases[p] && stances.has(aliases[p])) ? 'stance'
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

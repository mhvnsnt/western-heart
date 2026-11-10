#!/usr/bin/env node
// t7_graph_commands.mjs: the fighter's command list GENERATED from its imported T7 graph (wh-t7-graph/2) with the
// game's own interpreter semantics (game/js/t7graph.js), one entry per source cancel row of every reachable move.
// Each row is classified by what the runtime can actually decide today, so the source reachability graph and the
// playable command set are reported separately:
//   evaluable      every requirement condition is known to the runtime and true in a neutral game state
//                  (makeEvalCond with Pantera's context), the input mode / timing / special has a proven meaning;
//   known-false    a known condition is false in WH (practice demo, story battle, assist button, basic combo);
//   unknown        blocked by >= 1 requirement condition the runtime cannot evaluate (listed);
//   timing         cancel frame past the move's animation (meaning unproven);
//   seq-mode       input sequence with a mode-0 button element (meaning unproven);
//   special        engine special other than 0x8001 / 0x8002 (meaning unproven).
// usage: node tools/anim/t7_graph_commands.mjs game/assets/anim/t7/king [--out graph.commands.json]
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
const HERE = fileURLToPath(new URL('.', import.meta.url));
const G = await import(pathToFileURL(join(HERE, '../../game/js/t7graph.js')).href);
const dir = process.argv[2]; if (!dir) { console.error('usage: t7_graph_commands.mjs <t7 fighter dir> [--out file]'); process.exit(2); }
const oi = process.argv.indexOf('--out'); const out = oi > 0 ? process.argv[oi + 1] : join(dir, 'graph.commands.json');
const g = JSON.parse(readFileSync(join(dir, 'graph.json'), 'utf8'));
const cov = JSON.parse(readFileSync(join(dir, 'graph.coverage.json'), 'utf8'));
const ix = JSON.parse(readFileSync(join(dir, 'graph-clips/index.json'), 'utf8'));
const NAMES = Object.entries(G.DIR_BITS);
const dirs = (m) => (m ? NAMES.filter(([, b]) => m & b).map(([n]) => n).join('|') : '*');
const btns = (m) => [1, 2, 4, 8, 16].filter((b) => m & b).map((b) => (b === 16 ? 'RA' : String(Math.log2(b) + 1))).join('+');
const CTX = { dead: false, charId: 2, controller: 0 }; // Pantera's runtime context (fighter.js t7gAttach)
const ev = G.makeEvalCond(CTX);
const nameOf = (id) => (g.moves[id] ? g.moves[id].name : `0x${id.toString(16)}`);
const len = (m) => (m.clip != null && ix.clips[`${m.bank}_${m.clip}`] ? ix.clips[`${m.bank}_${m.clip}`].frames : 0);
const F = G.F; const rows = []; const counts = {}; const unknownConds = {};
for (const id of cov.reachable_moves) {
  const m = g.moves[id]; const L = len(m);
  m.cancels.forEach((r, i) => {
    const cmd = r[F.cmd]; if (cmd === G.GROUP_END) return;
    let kind, notation, status = null;
    if (cmd === G.AUTO) { kind = 'auto'; notation = 'AUTO'; }
    else if (cmd >= G.SEQ0 && cmd <= G.SEQ_MAX) {
      const s = g.sequences[r[F.seq]]; kind = 'sequence';
      notation = s.inputs.map((e) => dirs(e[0]) + (e[1] ? '+' + btns(e[1]) : '')).join(',');
      if (s.inputs.some((e) => e[2] === 0 && e[1])) status = 'seq-mode';
    } else if (cmd > G.AUTO) { kind = 'special'; notation = G.KNOWN_SPECIALS[cmd] || `special 0x${cmd.toString(16)}`; if (!G.KNOWN_SPECIALS[cmd]) status = 'special'; }
    else {
      const pp = r[F.buttons], mode = r[F.mode];
      kind = pp ? 'press' : 'state';
      notation = dirs(r[F.dir]) + (pp ? (mode === G.MODE_ANY ? '+(any of ' + btns(pp) + ')' : '+' + btns(pp)) : '') +
        (r[F.held] ? ' [held ' + btns(r[F.held]) + ']' : '') + (r[F.notHeld] ? ' [not held ' + btns(r[F.notHeld]) + ']' : '');
      if (pp && mode !== G.MODE_AT_LEAST && mode !== G.MODE_ANY) status = 'mode';
    }
    if (!status && kind !== 'auto') { const sf = r[F.sf]; if (sf !== 0 && L && sf > L) status = 'timing'; }
    let unk = [];
    if (!status) {
      for (const [c, p] of g.requirements[String(r[F.req])] || []) {
        if (c === 0) continue; const v = ev(c, p);
        if (v === null) unk.push(c); else if (v === false) { status = 'known-false'; break; }
      }
      if (!status) status = unk.length ? 'unknown' : 'evaluable';
    }
    counts[status] = (counts[status] || 0) + 1;
    for (const c of new Set(unk)) unknownConds[c] = (unknownConds[c] || 0) + 1;
    rows.push({ from: m.name, from_id: id, row: i, kind, notation, window: [r[F.start], r[F.end]], cancel_frame: r[F.sf],
      to: nameOf(G.resolveMoveId(g, r[F.to])), req: r[F.req], status, ...(unk.length ? { unknown: [...new Set(unk)] } : {}) });
  });
}
const stance = g.moves[g.stance].name;
const stanceCommands = rows.filter((x) => x.from === stance && x.kind === 'press' && x.status === 'evaluable')
  .map((x) => { const t = g.moves[G.moveByName(g, x.to)] || {}; const w = t.damage > 0 ? t.hitlevel & 0xFFF : null;
    return { notation: x.notation, row: x.row, to: x.to, damage: t.damage || 0, first_active: t.first_active || 0, hitlevel_raw: t.hitlevel }; });
const rep = { format: 'wh-t7-graph-commands/1', graph_sha256: ix.graph_sha256, generated_by: 'tools/anim/t7_graph_commands.mjs',
  semantics: 'game/js/t7graph.js (same interpreter as the game)', neutral_state: 'makeEvalCond(' + JSON.stringify(CTX) + ')',
  reachable_moves: cov.reachable_moves.length, rows: rows.length, by_status: counts,
  unknown_condition_rows: Object.fromEntries(Object.entries(unknownConds).sort((a, b) => b[1] - a[1])),
  stance: stance, stance_press_commands_evaluable: stanceCommands, all: rows };
writeFileSync(out, JSON.stringify(rep));
console.log('GRAPH_COMMANDS rows', rows.length, JSON.stringify(counts), 'stance evaluable press commands', stanceCommands.length, '->', out);

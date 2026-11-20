// tools/input-verify/input_matrix_audit.mjs — every fighter x every Tekken input combination, through the game's own
// input code (owner 2026-11-01: "all the different combinations of button inputs ... for every character ... so I'm
// not limited or blocked ... anything that you can do in base Tekken").
//
// For each fighter moveset, each held direction (n f b u d u/f u/b d/f d/b) and each button set (1 2 3 4 and every
// chord 1+2 3+4 1+3 2+4 1+4 2+3 1+2+3 1+2+4 1+3+4 2+3+4 1+2+3+4), it does what game/js/fighter.js _tryAttackFresh
// does: TekkenBuffer.noteDirection(dir), then pressButton (one button) or pressChord (a chord), then the move key the
// resolved notation fires (resolveMoveKey). Outcomes:
//   own      the fighter's own move for exactly that input (d/f+1 fires a d/f+1 move);
//   neutral  a direction + button with no directional move: the game fires the neutral button's move (Tekken does);
//   generic  no move in the moveset at all: the base WH punch / kick (fighter.js MOVES fallback);
//   fallback a chord with no move of its own fires its best sub-chord / first button (TekkenBuffer.pressChordLenient,
//            2026-11-01; before that fighter.js did nothing: "whiff, no action");
//   DEAD     nothing happens.
//
//   node tools/input-verify/input_matrix_audit.mjs [--json out.json] [--md out.md] [fighter ...]
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
await import(path.join(ROOT, 'tools/anim/node_game_env.mjs'));
const M = await import(path.join(ROOT, 'game/js/movesets.js'));

const DIRS = ['n', 'f', 'b', 'u', 'd', 'u/f', 'u/b', 'd/f', 'd/b'];
const SINGLES = ['1', '2', '3', '4'];
const CHORDS = ['1+2', '3+4', '1+3', '2+4', '1+4', '2+3', '1+2+3', '1+2+4', '1+3+4', '2+3+4', '1+2+3+4'];

const args = process.argv.slice(2);
const opt = (k) => { const i = args.indexOf(k); return i >= 0 ? args.splice(i, 2)[1] : null; };
const jsonOut = opt('--json'), mdOut = opt('--md');

// the roster: fighters in game/data/roster_map.json that have a moveset file
const MS_DIR = path.join(ROOT, 'game/assets/movesets');
const rosterMap = JSON.parse(fs.readFileSync(path.join(ROOT, 'game/data/roster_map.json'), 'utf8'));
let fighters = (rosterMap.fighters || []).map((f) => f.id).filter((id) => fs.existsSync(path.join(MS_DIR, id + '.json')));
if (args.length) fighters = args;

function audit(fid) {
  const data = JSON.parse(fs.readFileSync(path.join(MS_DIR, fid + '.json'), 'utf8'));
  M.registerMoveset(fid, data);
  const rows = [];
  for (const d of DIRS) {
    for (const btn of [...SINGLES, ...CHORDS]) {
      const buf = new M.TekkenBuffer(fid);
      if (d !== 'n') buf.noteDirection(d);
      let r, outcome, key = null;
      if (btn.length === 1) {
        r = buf.pressButton(btn, {});
        const notation = r || btn;            // _tryAttackFresh keeps the raw button when nothing resolves
        key = M.resolveMoveKey(fid, notation);
        outcome = !key ? 'generic' : (d === 'n' || (r && r !== btn)) ? 'own' : 'neutral';
      } else {
        const own = new M.TekkenBuffer(fid);
        if (d !== 'n') own.noteDirection(d);
        const r0 = own.pressChord(btn, {});                     // the chord's own move (if any)
        r = buf.pressChordLenient(btn, {});                     // what fighter.js fires (2026-11-01)
        key = r ? M.resolveMoveKey(fid, r) : null;
        outcome = !key ? 'DEAD' : (r0 && r === r0) ? 'own' : 'fallback';
      }
      rows.push({ dir: d, input: btn, resolved: r || null, key, outcome });
    }
  }
  return rows;
}

const report = {};
for (const fid of fighters) {
  try { report[fid] = audit(fid); } catch (e) { report[fid] = { error: String(e && e.message || e).slice(0, 200) }; }
}
const tally = (rows, o) => rows.filter((r) => r.outcome === o).length;
const lines = [];
let totDead = 0, totInputs = 0;
for (const [fid, rows] of Object.entries(report)) {
  if (!Array.isArray(rows)) { lines.push(`| ${fid} | error: ${rows.error} | | | | |`); continue; }
  const dead = rows.filter((r) => r.outcome === 'DEAD');
  totDead += dead.length; totInputs += rows.length;
  lines.push(`| ${fid} | ${tally(rows, 'own')} | ${tally(rows, 'neutral')} | ${tally(rows, 'fallback')} | ${tally(rows, 'generic')} | ${dead.length} | ${dead.slice(0, 8).map((r) => (r.dir === 'n' ? '' : r.dir + '+') + r.input).join(' ')}${dead.length > 8 ? ' ...' : ''} |`);
}
const md = [
  '# Input matrix audit (`tools/input-verify/input_matrix_audit.mjs`)', '',
  `${Object.keys(report).length} fighters x ${DIRS.length} directions x ${SINGLES.length + CHORDS.length} button sets = ${totInputs} inputs through the game's own TekkenBuffer. **DEAD (nothing happens): ${totDead}.**`, '',
  'own = the fighter\'s move for that exact input; neutral = direction + button with no directional move fires the neutral button\'s move (as Tekken does); fallback = a chord with no move of its own fires its best sub-chord / first button (no dead chords); generic = the base WH punch / kick; DEAD = nothing happens.', '',
  '| fighter | own | neutral | fallback | generic | DEAD | dead inputs (first 8) |', '|---|---|---|---|---|---|---|', ...lines,
].join('\n') + '\n';
if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify(report, null, 1));
if (mdOut) fs.writeFileSync(mdOut, md);
console.log(md.split('\n').slice(0, 4).join('\n'));

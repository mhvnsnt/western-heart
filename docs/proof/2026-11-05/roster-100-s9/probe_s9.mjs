// Roster-100 S9 probe — duplicate-spelling stance rows + Megami IZU entry,
// through the game's own moveset registry and TekkenBuffer (the same calls
// fighter.js makes in a fight). Run from the repo root:
//   node docs/proof/2026-11-05/roster-100-s9/probe_s9.mjs
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..', '..');
await import(path.join(ROOT, 'tools/anim/node_game_env.mjs'));
const M = await import(path.join(ROOT, 'game/js/movesets.js'));
const F = await import(path.join(ROOT, 'game/js/fighter.js'));

const load = (fid) => {
  const d = JSON.parse(fs.readFileSync(path.join(ROOT, 'game/assets/movesets', fid + '.json'), 'utf8'));
  M.registerMoveset(fid, d);
  return d;
};
let pass = 0, fail = 0;
const check = (label, got, want) => {
  const ok = got === want;
  if (ok) pass++; else fail++;
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${label}: got ${JSON.stringify(got)}${ok ? '' : ` want ${JSON.stringify(want)}`}`);
};
load('phantom'); load('cyborgx'); load('megami');

// --- phantom: INS is the T7-layer spelling of the wired IND (Indian Stance) ---
check('phantom resolve IND.1 (canonical T8 row keeps the slot)', M.resolveMoveKey('phantom', 'IND.1'), 'IND.1');
check('phantom resolve IND.2 (canonical row keeps the slot)', M.resolveMoveKey('phantom', 'IND.2'), 'IND.2');
check('phantom resolve IND.2,D/B+2 (INS-only string chain, alias slot)', M.resolveMoveKey('phantom', 'IND.2,D/B+2'), 'INS.2,D/B+2');
check('phantom resolve IND.2,D/B+2,2 (chain step 2)', M.resolveMoveKey('phantom', 'IND.2,D/B+2,2'), 'INS.2,D/B+2,2');
check('phantom resolve IND.2,D/B+2,2,2 (chain step 3)', M.resolveMoveKey('phantom', 'IND.2,D/B+2,2,2'), 'INS.2,D/B+2,2,2');
check('phantom resolve IND.2,D/B+2,2,2,2 (chain step 4)', M.resolveMoveKey('phantom', 'IND.2,D/B+2,2,2,2'), 'INS.2,D/B+2,2,2,2');
check('phantom resolve IND.3+4* (INS-only row, alias slot)', M.resolveMoveKey('phantom', 'IND.3+4*'), 'INS.3+4*');
check('phantom resolve POI.1+2 (POISON_WIND-only row, alias slot)', M.resolveMoveKey('phantom', 'POI.1+2'), 'POISON_WIND.1+2');
check('phantom entry move d+3+4 stanceAfter', F.getRealMove('phantom', 'd+3+4').stanceAfter, 'IND');
// buffer presses in the stance, the way a fight drives them
check('phantom buffer: press 2 in IND stance fires the canonical IND.2', new M.TekkenBuffer('phantom').pressButton('2', { stance: 'IND' }), 'IND.2');
{
  // The full INS string chain, driven the way fighter.js drives a string:
  // each played step is recorded (recordExplicit) before the next press.
  const b = new M.TekkenBuffer('phantom');
  b.pressButton('2', { stance: 'IND' });
  let step = b.continuation('D/B+2', { stance: 'IND' });
  check('phantom buffer: IND.2 -> D/B+2 continues into the aliased chain row', step, 'IND.2,D/B+2');
  b.recordExplicit(step);
  step = b.continuation('2', { stance: 'IND' });
  check('phantom buffer: chain step ,2', step, 'IND.2,D/B+2,2');
  b.recordExplicit(step);
  step = b.continuation('2', { stance: 'IND' });
  check('phantom buffer: chain step ,2,2', step, 'IND.2,D/B+2,2,2');
  b.recordExplicit(step);
  step = b.continuation('2', { stance: 'IND' });
  check('phantom buffer: chain step ,2,2,2', step, 'IND.2,D/B+2,2,2,2');
}

// --- cyborgx: BKP is the T8 spelling of the wired BACKUP; CLOCKWORK of CLK ---
check('cyborgx resolve BACKUP.1 (canonical T7 row keeps the slot)', M.resolveMoveKey('cyborgx', 'BACKUP.1'), 'BACKUP.1');
check('cyborgx resolve BACKUP.1+2 (BKP-only Rocket Punch, alias slot)', M.resolveMoveKey('cyborgx', 'BACKUP.1+2'), 'BKP.1+2');
check('cyborgx resolve CLK.3 (canonical row keeps the slot; CLOCKWORK.3 stays shadowed)', M.resolveMoveKey('cyborgx', 'CLK.3'), 'CLK.3');
check('cyborgx buffer: press 1+2 chord in BACKUP stance fires Rocket Punch via the alias slot',
  new M.TekkenBuffer('cyborgx').pressChord('1+2', { stance: 'BACKUP' }), 'BACKUP.1+2');

// --- megami: f+1+2 "Izumo (stance)" now enters IZU (her own stance_after line) ---
check('megami f+1+2 stanceAfter', F.getRealMove('megami', 'f+1+2').stanceAfter, 'IZU');
check('megami buffer: press 1 in IZU stance fires IZU.1', new M.TekkenBuffer('megami').pressButton('1', { stance: 'IZU' }), 'IZU.1');
check('megami buffer: press 1+3 chord in IZU stance fires IZU.1+3', new M.TekkenBuffer('megami').pressChord('1+3', { stance: 'IZU' }), 'IZU.1+3');

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);

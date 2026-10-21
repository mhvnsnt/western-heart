#!/usr/bin/env node
/* LANE 3 test: every wired moveset must actually execute in game logic.
 * 1. Schema-validate all 45 moveset JSONs (1/2/3/4, throws, strings, specials,
 *    sane frame data, T3 row provenance points at real bank rows).
 * 2. Simulate the TekkenBuffer resolver per fighter: raw buttons, string
 *    continuation, throw chords, directional attacks, motion specials.
 * 3. Verify getRealMove-equivalent output is executable (startup/active/
 *    recovery/damage all > 0).
 */
import { readFileSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const ROOT = dirname(fileURLToPath(import.meta.url));
const MS_DIR = join(ROOT, '..', 'game', 'assets', 'movesets');
const T3_DIR = join(ROOT, 't3');
const { TekkenBuffer, parseSpecialInput, registerMoveset } = await import('../game/js/movesets.js');
// register all moveset JSONs (browser would fetch them via loadFighterMovesets)
for (const f of readdirSync(MS_DIR).filter(f => f.endsWith('.json'))) {
  registerMoveset(f.replace('.json', ''), JSON.parse(readFileSync(join(MS_DIR, f), 'utf8')));
}

const t3banks = {};
for (const n of ['king', 'jin', 'bryan', 'heihachi', 'xiaoyu', 'yoshimitsu', 'gunjack']) {
  t3banks[n] = JSON.parse(readFileSync(join(T3_DIR, `moveset_${n}.json`), 'utf8'));
}

let pass = 0, fail = 0;
const failures = [];
function check(cond, msg) {
  if (cond) { pass++; }
  else { fail++; failures.push(msg); }
}

// game-equivalent move resolution (mirrors fighter.js getRealMove new-shape branch)
function toGameMove(mv) {
  return {
    startup: mv.startup, active: mv.active, recovery: mv.recovery,
    damage: mv.damage, knock: mv.knock ?? 2.2,
    soulGain: mv.soulGain ?? 8, cost: 0,
    limb: mv.limb || 'armR', heavy: !!mv.heavy,
    unblockable: !!mv.unblockable, isGrab: !!mv.isGrab,
  };
}
function executable(m, label) {
  return m && m.startup > 0 && m.active > 0 && m.recovery > 0 && m.damage > 0 &&
    ['startup', 'active', 'recovery', 'damage'].every(k => Number.isFinite(m[k]));
}

const files = readdirSync(MS_DIR).filter(f => f.endsWith('.json'));
check(files.length === 45, `expected 45 moveset files, found ${files.length}`);

for (const f of files.sort()) {
  const fid = f.replace('.json', '');
  const d = JSON.parse(readFileSync(join(MS_DIR, f), 'utf8'));
  const tag = `[${fid}]`;
  check(d.fighter === fid, `${tag} fighter id matches filename`);
  check(d.t3_source && t3banks[d.t3_source], `${tag} t3_source valid`);
  const bank = t3banks[d.t3_source].moves;

  // 1/2/3/4 basics
  for (const b of ['1', '2', '3', '4']) {
    const mv = d.moves[b];
    check(!!mv, `${tag} has basic attack ${b}`);
    if (mv) {
      check(executable(toGameMove(mv)), `${tag} move ${b} executable (startup/active/recovery/damage>0)`);
      const row = bank[mv.t3_row];
      check(!!row, `${tag} move ${b} t3_row ${mv.t3_row} exists in ${d.t3_source} bank`);
      if (row) check(row.damage > 0 && row.active_first > 0, `${tag} move ${b} t3_row is a real strike`);
    }
  }
  // throws
  for (const t of ['1+3', '2+4']) {
    const mv = d.moves[t];
    check(!!mv, `${tag} has throw ${t}`);
    if (mv) {
      check(mv.throw === true && mv.unblockable === true && mv.isGrab === true, `${tag} throw ${t} flagged throw/unblockable/isGrab`);
      check(executable(toGameMove(mv)), `${tag} throw ${t} executable`);
      const row = bank[mv.t3_row];
      check(!!row && row.attack_class === 1 && row.damage === 0 && row.active_first > 0, `${tag} throw ${t} t3_row is a real T3 throw move`);
    }
  }
  // strings chain correctly
  for (const s of d.strings || []) {
    const hits = s.input.split(',');
    check(hits.length >= 2 && hits.length <= 3, `${tag} string ${s.input} length 2-3`);
    check(!!d.moves[s.input], `${tag} string ${s.input} has move entry`);
    for (let i = 1; i < hits.length; i++) {
      const prefix = hits.slice(0, i + 1).join(',');
      check(!!d.moves[prefix], `${tag} string prefix ${prefix} has move entry`);
    }
  }
  // specials parse + executable
  for (const sp of d.specials || []) {
    const { dirs, button } = parseSpecialInput(sp.input);
    const okBtn = button && button.split('+').every(b => ['1','2','3','4'].includes(b));
    check(dirs.length > 0 && okBtn, `${tag} special ${sp.input} parses to dirs+button`);
    check(!!d.moves[sp.input] && executable(toGameMove(d.moves[sp.input])), `${tag} special ${sp.input} executable`);
  }
  check((d.specials || []).length >= 1, `${tag} has >=1 special`);

  // --- resolver simulation ---
  const buf = new TekkenBuffer(fid);
  const r1 = buf.pressButton('1');
  check(r1 === '1' && !!d.moves[r1], `${tag} buffer: press 1 -> '${r1}'`);
  const r2 = buf.pressButton('2');
  const expectStr = d.moves['1,2'] ? '1,2' : '2';
  check(r2 === expectStr, `${tag} buffer: press 2 after 1 -> '${r2}' (expect '${expectStr}')`);
  // directional: face-forward + button
  const buf2 = new TekkenBuffer(fid);
  buf2.noteDirection('f');
  const rd = buf2.pressButton('1');
  const expectDir = d.moves['f+1'] ? 'f+1' : '1';
  check(rd === expectDir, `${tag} buffer: f+1 -> '${rd}' (expect '${expectDir}')`);
  // motion special: feed its direction sequence then the button
  if ((d.specials || []).length) {
    const sp = d.specials[0];
    const { dirs, button } = parseSpecialInput(sp.input);
    const buf3 = new TekkenBuffer(fid);
    for (const dd of dirs) buf3.noteDirection(dd);
    // ensure the final direction registers (noteDirection skips repeats)
    buf3.noteDirection('n'); buf3.noteDirection(dirs[dirs.length - 1]);
    const rs = button.includes('+') ? buf3.pressChord(button) : buf3.pressButton(button);
    check(rs === sp.input, `${tag} buffer: motion ${sp.input} -> '${rs}'`);
  }
  // throw explicit
  const gm = toGameMove(d.moves['1+3']);
  check(executable(gm) && gm.isGrab && gm.unblockable, `${tag} game-move 1+3 executable as unblockable grab`);
}

console.log(`\n==== LANE 3 MOVESET TEST ====`);
console.log(`PASS: ${pass}  FAIL: ${fail}`);
if (failures.length) {
  console.log('\nFailures:');
  for (const m of failures.slice(0, 40)) console.log('  -', m);
  if (failures.length > 40) console.log(`  ... and ${failures.length - 40} more`);
  process.exit(1);
} else {
  console.log('ALL MOVESETS EXECUTE ✔');
}

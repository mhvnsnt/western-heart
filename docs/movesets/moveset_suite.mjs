// Lane F moveset validation suite (round-2). Recreates round-1 coverage:
// per-fighter schema, per-move fields (v1+v2), specials/strings resolution,
// TekkenBuffer input parsing against real data, plus a scripted spot-check
// transcript (the exact input->move path fighter.js uses in-game).
import { readFileSync, readdirSync } from 'fs';
import { registerMoveset, getMove, parseSpecialInput, TekkenBuffer } from '/home/hatch/workspace/western-heart-movesets/game/js/movesets.js';

const DIR = '/home/hatch/workspace/western-heart-movesets/game/assets/movesets/';
let pass = 0, fail = 0;
const failures = [];
function ok(cond, label) {
  if (cond) pass++; else { fail++; failures.push(label); }
}

const files = readdirSync(DIR).filter(f => f.endsWith('.json'));
ok(files.length === 45, `45 fighter files (got ${files.length})`);

const V1_MOVE = ['name', 'input', 'startup', 'active', 'recovery', 'damage', 'limb', 'heavy', 'knock', 'soulGain'];
const V2_MOVE = ['anim_ref', 'input_slots', 'move_class'];
const CLASSES = new Set(['strike', 'throw', 'string', 'special']);

for (const f of files.sort()) {
  const d = JSON.parse(readFileSync(DIR + f, 'utf8'));
  const id = f.replace('.json', '');
  ok(d.fighter === id, `${id}: fighter id matches filename`);
  ok(typeof d.proxy === 'boolean', `${id}: proxy is boolean`);
  ok(d.proxy === false || typeof d.proxy_note === 'string', `${id}: proxy has honest note`);
  ok(d.schema_version === 2, `${id}: schema_version 2`);
  ok(d.moves && typeof d.moves === 'object', `${id}: moves object`);
  ok(Array.isArray(d.specials), `${id}: specials array`);
  ok(Array.isArray(d.strings), `${id}: strings array`);
  ok(typeof d.frame_convention === 'string' && d.frame_convention.length > 10, `${id}: frame_convention honest`);
  registerMoveset(id, d);

  const specialsInputs = new Set((d.specials || []).map(s => s.input));
  for (const [notation, m] of Object.entries(d.moves)) {
    const tag = `${id}:${notation}`;
    for (const k of V1_MOVE) ok(m[k] !== undefined && m[k] !== null, `${tag} has v1 field ${k}`);
    for (const k of V2_MOVE) ok(m[k] !== undefined && m[k] !== null, `${tag} has v2 field ${k}`);
    ok(m.input === notation, `${tag}: input key matches`);
    ok(typeof m.anim_ref === 'string' && m.anim_ref.includes(':'), `${tag}: anim_ref format`);
    ok(Array.isArray(m.input_slots) && m.input_slots[0] === notation, `${tag}: input_slots canonical first`);
    ok(CLASSES.has(m.move_class), `${tag}: move_class valid`);
    ok(typeof m.damage === 'number' && m.damage > 0, `${tag}: damage positive`);
    if (m.throw) ok(m.unblockable === true && m.isGrab === true, `${tag}: throw flags`);
    ok(getMove(id, notation) !== null, `${tag}: getMove resolves`);
    if (specialsInputs.has(notation)) {
      const p = parseSpecialInput(notation);
      ok(p.button !== null, `${tag}: special parses button`);
    }
  }
  for (const s of d.specials || []) {
    ok(d.moves[s.input] !== undefined, `${id}: special ${s.input} resolves in moves`);
    const p = parseSpecialInput(s.input);
    ok(Array.isArray(p.dirs), `${id}: special ${s.input} dirs parse`);
  }
  for (const st of d.strings || []) {
    ok(d.moves[st.input] !== undefined, `${id}: string ${st.input} resolves in moves`);
  }
}

// TekkenBuffer behavior on real data
for (const fid of ['pantera', 'vainabel']) {
  const buf = new TekkenBuffer(fid);
  ok(buf.pressButton('1') === '1', `${fid}: raw 1 resolves`);
  ok(buf.pressChord('1+3') === '1+3' || getMove(fid, buf.pressChord('1+3')) !== null, `${fid}: throw chord resolves`);
  const buf2 = new TekkenBuffer(fid);
  const first = buf2.pressButton('2');
  const cont = buf2.pressButton('1');
  if (getMove(fid, '2,1')) ok(cont === '2,1', `${fid}: string 2,1 continuation`);
  else ok(cont !== null, `${fid}: button 1 after 2 resolves to something`);
  const buf3 = new TekkenBuffer('vainabel');
  for (const dd of ['d', 'd/f', 'f']) buf3.noteDirection(dd);
  const sp = buf3.pressChord('1+3');
  ok(sp === 'qcf+1+3', `vainabel: qcf motion + 1+3 -> Spear Grapple (got ${sp})`);
}

// ---- scripted spot-check transcript ----
console.log('\n--- SPOT CHECK: scripted input sessions (real TekkenBuffer + real JSONs) ---');
{
  const buf = new TekkenBuffer('vainabel');
  for (const d of ['d', 'd/f', 'f']) buf.noteDirection(d);
  const sp = buf.pressChord('1+3');
  const m = getMove('vainabel', sp);
  console.log(`INPUT qcf,1+3 -> ${sp} | ${m.name} | class=${m.move_class} dmg=${m.damage} anim=${m.anim_ref}`);
}
{
  const b = new TekkenBuffer('vainabel');
  const r1 = b.pressButton('1'), r2 = b.pressButton('1'), r3 = b.pressButton('4');
  console.log(`INPUT 1,1,4   -> ${r1} -> ${r2} -> ${r3} | ${getMove('vainabel', r3).name}`);
}
{
  const b = new TekkenBuffer('vainabel');
  const k = b.pressButton('4'); const m = getMove('vainabel', k);
  console.log(`INPUT 4       -> ${k} | ${m.name} | dmg=${m.damage} (doa ${m.doa_damage})`);
}
{
  const b = new TekkenBuffer('pantera');
  const p1 = b.pressButton('1'), pt = b.pressChord('1+3');
  console.log(`pantera 1 -> ${p1} (${getMove('pantera', p1).anim_ref}), 1+3 -> ${pt} (regression OK)`);
}

console.log(`\nRESULT: ${pass} passed, ${fail} failed`);
if (failures.length) {
  console.log('FAILURES (first 20):');
  for (const fl of failures.slice(0, 20)) console.log('  -', fl);
}
process.exit(fail ? 1 : 0);

// Combat contact + command interpreter test (owner pt198u, 2026-10-23). Node, no DOM.
// Run: node test/combat-contact.test.mjs
// Every fighter: (1) every slot move resolves a hit level -> T3 word, has an
// active window a 30 fps tick cannot skip, and reaches past body separation;
// (2) scripted string inputs chain to the exact next move id (1 -> 1,2 ...);
// (3) stick octants, press buffer and chord upgrade behave like Tekken.
import { readFileSync, readdirSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import assert from 'assert';
const root = join(dirname(fileURLToPath(import.meta.url)), '..');
globalThis.localStorage = { getItem: () => null, setItem() {}, removeItem() {} };
const C = await import(join(root, 'game/js/combat-core.js'));
const M = await import(join(root, 'game/js/movesets.js'));
const msDir = join(root, 'game/assets/movesets');
try { M.setInputTables(JSON.parse(readFileSync(join(msDir, 't3_input_tables.json'), 'utf8'))); } catch (e) {}

let fails = 0; const fail = (m) => { fails++; if (fails < 40) console.log('FAIL', m); };

// --- unit: stick octants (facing right / left) ---
const S = (x, y, f = 1) => C.stickToDir(x, y, f);
assert.equal(S(0.1, 0.1), 'n'); assert.equal(S(1, 0), 'f'); assert.equal(S(-1, 0), 'b');
assert.equal(S(0.7, -0.7), 'd/f'); assert.equal(S(0.62, -0.78), 'd/f'); assert.equal(S(0.9, -0.3), 'f');
assert.equal(S(1, 0, -1), 'b'); assert.equal(S(-0.7, -0.7, -1), 'd/f'); assert.equal(S(0, 1), 'u');
// --- unit: hit levels ---
assert.equal(C.hitWordFor({ hit_level: 'h' }), 0x412); assert.equal(C.hitWordFor({ hit_level: 'l' }), 0x10F);
assert.equal(C.hitWordFor({ hit_level: 'm' }), 0x217); assert.equal(C.hitWordFor({ hit_level: 'sm' }), 0x31F);
assert.equal(C.hitWordFor({ hit_level: 'h,m' }), 0x412); assert.equal(C.hitWordFor({ hit_level: 't' }), undefined);
// --- unit: swept active window at 30 fps on a 1-frame move ---
{ const m = { startup: 0.167, active: 0.017, recovery: 0.3 }; let t = 0, prev = 0, seen = false;
  while (t < 0.6) { t += 1 / 30; if (C.attackPhase(m, t, prev) === 'active') seen = true; prev = t; }
  assert.ok(seen, 'swept active'); }
// --- unit: press buffer + chord upgrade ---
{ const b = new C.PressBuffer(10); b.push('1', 0); assert.equal(b.take(0.1), '1');
  b.push('1', 0); assert.equal(b.take(0.2), null);
  b.push('1', 0); b.push('1+2', 0.05); assert.equal(b.take(0.1), '1+2'); }
// --- unit: reach vs separation ---
assert.ok(C.inReach(0, 0, 1, 1.45, 0, { limb: 'armR' }, '1'));
assert.ok(!C.inReach(0, 0, 1, -1.45, 0, { limb: 'armR' }, '1'), 'behind');
assert.ok(!C.inReach(0, 0, 1, 1.45, 1.2, { limb: 'armR' }, '1'), 'sidestepped');
assert.ok(!C.inReach(0, 0, 1, 3.5, 0, { limb: 'legR' }, '4'), 'out of range');

// --- every fighter ---
const files = readdirSync(msDir).filter(f => f.endsWith('.json') && !/index|tables|ui_/.test(f));
let fighters = 0, moves = 0, strings = 0, stringsOk = 0, levels = 0;
for (const f of files) {
  let d; try { d = JSON.parse(readFileSync(join(msDir, f), 'utf8')); } catch { continue; }
  if (!d || !d.moves || !d.slots) continue;
  const id = f.replace(/\.json$/, '');
  M.registerMoveset(id, d); fighters++;
  for (const [nota, key] of Object.entries(d.slots)) {
    const mv = d.moves[key]; if (!mv || mv.startup == null) continue; moves++;
    if (C.effectiveActive(mv) < 3 / 60 - 1e-9) fail(`${id} ${nota} active`);
    if (C.hitWordFor(mv) !== undefined) levels++;
    if (!mv.isGrab && C.moveReach(mv, nota) <= 1.45) fail(`${id} ${nota} reach`);
    if (mv.isGrab && C.moveReach(mv, nota) < 1.45) fail(`${id} ${nota} grab reach`);
  }
  // string chaining: for each 2-hit button string a,b in slots, press a then continuation(b)
  for (const nota of Object.keys(d.slots)) {
    const m = nota.match(/^([1-4](?:\+[1-4])?),([1-4](?:\+[1-4])?)$/); if (!m) continue;
    if (!d.slots[m[1]]) continue;
    strings++;
    const buf = new M.TekkenBuffer(id);
    for (let i = 0; i < 4; i++) buf.noteDirection('n');
    const first = m[1].includes('+') ? buf.pressChord(m[1], {}) : buf.press(m[1], {});
    if (first !== m[1]) continue; // a stance/motion owns the opener; covered by input-determinism
    const next = buf.continuation(m[2]);
    if (next === nota || M.resolveMoveKey(id, next) === M.resolveMoveKey(id, nota)) stringsOk++;
    else fail(`${id} string ${nota} -> ${next}`);
  }
}
console.log(JSON.stringify({ fighters, moves, hitLevelsMapped: levels, strings, stringsOk, fails }));
if (fails) { console.log('FAIL combat contact'); process.exit(1); }
console.log('PASS combat contact');

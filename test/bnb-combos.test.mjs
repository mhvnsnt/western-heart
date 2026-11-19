// BnB combo input scripts (owner t231u: "I can't do combos"). For the 10 reference fighters
// (Tekken-base equivalents in our roster) and then roster-wide: every launcher-led combo route
// from the fighter's own data is TYPED frame-by-frame through the real resolver (TekkenBuffer,
// 60 Hz), must resolve to exactly the route's moves, and must connect launch -> juggle(s) ->
// ender in the combat sim (combat-systems resolveHit: juggle states, screw, wall splat).
// Run: node test/bnb-combos.test.mjs [--report out.json]
import { readFileSync, readdirSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const _ls = {}; globalThis.localStorage = { getItem: k => _ls[k] ?? null, setItem: (k, v) => { _ls[k] = String(v); } };
let clock = 0; globalThis.performance = { now: () => clock };
const M = await import(join(root, 'game/js/movesets.js'));
const FL = await import(join(root, 'game/js/full-movelist.js'));
const CS = await import(join(root, 'game/js/combat-systems.js'));
const msDir = join(root, 'game/assets/movesets');
try { M.setInputTables(JSON.parse(readFileSync(join(msDir, 't3_input_tables.json'), 'utf8'))); } catch (e) {}
const REF = { Jin: 'rin', Kazuya: 'demonio', Paul: 'tou', King: 'pantera', Law: 'buffalo-bill', Hwoarang: 'gyou', Bob: 'burger', Steve: 'zui', Bryan: 'skull', Lars: 'chordz' };
const DIRT = /^(d\/f|d\/b|u\/f|u\/b|f|b|u|d|n|D\/F|D\/B|U\/F|U\/B|F|B|U|D)$/;
function step(buf, d) { clock += 1000 / 60; buf.noteDirection(d); }
/** Type one notation as a fresh press (after the previous move recovered). */
function typeMove(buf, nota) {
  const { prefix, body } = M.splitNotation(nota);
  const ctx = prefix === 'WS.' ? { rising: true } : prefix === 'FC.' ? { crouching: true } : prefix === 'SS.' ? { sidestep: true } : prefix === 'BT.' ? { backturned: true } : prefix ? { stance: prefix.slice(0, -1) } : {};
  for (let i = 0; i < 20; i++) step(buf, 'n');
  const mo = M.parseMotion(nota);
  if (mo) { // motion move (qcb+4, f,n,d,d/f:1, b,1): type the decoded direction steps
    mo.dirs.forEach((d, i) => { for (let k = 0; k < 2; k++) step(buf, d); if (mo.dirs[i + 1] === d) for (let k = 0; k < 2; k++) step(buf, 'n'); });
    if (!mo.neutral && /[A-Z]/.test(nota.split(',').pop().split('+')[0])) for (let k = 0; k < 2; k++) step(buf, mo.dirs[mo.dirs.length - 1]);
    if (mo.neutral) for (let k = 0; k < 2; k++) step(buf, 'n');
    return { got: mo.btn.includes('+') ? buf.pressChord(mo.btn, ctx) : buf.press(mo.btn, ctx) };
  }
  const toks = body.split(/[,~:]/).map(t => t.replace(/\*$/, '')); let got = null, motion = [];
  for (const [i, t] of toks.entries()) {
    if (DIRT.test(t)) { motion.push(t); continue; }
    const m = /^(?:(d\/f|d\/b|u\/f|u\/b|f|b|u|d|D\/F|D\/B|U\/F|U\/B|F|B|U|D)\+)?([1-4](?:\+[1-4])*)$/.exec(t);
    if (!m) return { skip: true };
    let prev = null;
    for (const d of motion) { const lo = d.toLowerCase(); if (prev === lo) for (let k = 0; k < 2; k++) step(buf, 'n'); for (let k = 0; k < (d !== lo ? 6 : 2); k++) step(buf, lo); prev = lo; }
    if (m[1]) { const lo = m[1].toLowerCase(); if (prev === lo) for (let k = 0; k < 2; k++) step(buf, 'n'); for (let k = 0; k < (m[1] !== lo ? 10 : 2); k++) step(buf, lo); }
    else for (let k = 0; k < 2; k++) step(buf, 'n');
    const c = { ...ctx, inMove: i > 0 && !motion.length ? true : i > 0 };
    got = m[2].includes('+') ? buf.pressChord(m[2], c) : buf.press(m[2], c);
    motion = [];
  }
  return { got };
}
function runRoute(id, route) {
  let def = { x: 1.45, state: 'stand', airY: 0 }, juggle = 0, screwUsed = false; const log = [];
  const buf = new M.TekkenBuffer(id);
  for (const [i, nota] of route.entries()) {
    const t = typeMove(buf, nota);
    if (t.skip) return { ok: false, why: `${nota} not typeable`, log };
    if (t.got !== nota && M.resolveMoveKey(id, t.got) !== M.resolveMoveKey(id, nota)) return { ok: false, why: `typed ${nota} fired ${t.got}`, log };
    const mv = M.resolveMove(id, nota).move;
    const res = CS.resolveHit({ x: 0, facing: 1, airY: 0 }, def, mv, nota, { juggleHits: juggle, screwUsed, nearWall: i === route.length - 1 && def.state === 'air' ? false : false });
    log.push(`${nota}:${res.connected ? res.reaction : 'WHIFF'}`);
    if (!res.connected) return { ok: false, why: `${nota} whiffed`, log };
    if (i === 0 && mv.launch && res.reaction !== 'launch') return { ok: false, why: `launcher played ${res.reaction}`, log };
    if (def.state === 'air' && !['juggle', 'screw', 'floor_bound', 'wall_splat', 'knockdown'].includes(res.reaction)) return { ok: false, why: `${nota} air reaction ${res.reaction}`, log };
    if (['launch', 'juggle', 'floor_bound'].includes(res.reaction)) { def = { ...def, state: 'air', airY: Math.max(0.2, 0.9 - juggle * 0.15) }; juggle++; }
    if (res.reaction === 'screw') screwUsed = true;
  }
  return { ok: true, log, hits: route.length };
}
const report = { reference: {}, roster: { fighters: 0, routes: 0, ok: 0 } }; let refFail = 0;
const ids = readdirSync(msDir).filter(f => f.endsWith('.json') && !/index|tables|ui_/.test(f)).map(f => f.slice(0, -5));
const data = {};
for (const id of ids) { try { const d = JSON.parse(readFileSync(join(msDir, id + '.json'), 'utf8')); if (d && d.moves && d.slots) { M.registerMoveset(id, d); data[id] = d; } } catch (e) {} }
for (const [who, id] of Object.entries(REF)) {
  const routes = data[id] ? FL.comboRoutes(data[id], 4) : [];
  const rs = routes.map(r => ({ route: r.join(' > '), ...runRoute(id, r) }));
  const ok = rs.filter(r => r.ok).length; if (!routes.length || ok < routes.length) refFail++;
  report.reference[who] = { fighter: id, routes: rs.length, ok, combos: rs };
  console.log(`${(who + ' (' + id + ')').padEnd(24)} ${ok}/${rs.length} combos typed+connected  e.g. ${rs[0] ? rs[0].route + ' => ' + (rs[0].log || []).join(' ') : '-'}${rs.find(r => !r.ok) ? '  FAIL ' + rs.find(r => !r.ok).why : ''}`);
}
for (const id of Object.keys(data)) { const routes = FL.comboRoutes(data[id], 4); report.roster.fighters++; for (const r of routes) { report.roster.routes++; if (runRoute(id, r).ok) report.roster.ok++; } }
console.log('roster', JSON.stringify(report.roster));
const args = process.argv.slice(2); if (args.includes('--report')) writeFileSync(args[args.indexOf('--report') + 1], JSON.stringify(report, null, 1));
if (refFail || report.roster.ok < report.roster.routes) { console.log('FAIL bnb combos'); process.exit(1); }
console.log('PASS bnb combos');

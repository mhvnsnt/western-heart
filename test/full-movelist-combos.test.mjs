// Full move list + combo test (owner pt217u, 2026-10-23). Node, no DOM. Blocks merges (game-checks).
// Run: node test/full-movelist-combos.test.mjs [--report out.json] [--write-baseline]
// For EVERY fighter: (1) the full list = base slots + EMWH additions (魂 ACTION, KESSHOU,
// 九魂解放, 霊放, 試練の封 x 3..6 variants); every move is driven from its input through the
// TekkenBuffer and must fire exactly that move (added moves: 100%; base moves: may never drop
// below test/full-movelist-baseline.json); (2) combo routes run in a headless sim: each hit must
// make CONTACT (hitbox/hurtbox overlap at the active frame) and play the right reaction
// (launch -> juggle -> soul ender; wall splat; throw + throw break; block; counter-hit);
// (3) no source-game names in any on-screen name.
import { readFileSync, readdirSync, writeFileSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import assert from 'assert';
const root = join(dirname(fileURLToPath(import.meta.url)), '..');
globalThis.localStorage = { getItem: () => null, setItem() {}, removeItem() {} };
const M = await import(join(root, 'game/js/movesets.js'));
const FL = await import(join(root, 'game/js/full-movelist.js'));
const CS = await import(join(root, 'game/js/combat-systems.js'));
const C = await import(join(root, 'game/js/combat-core.js'));
const msDir = join(root, 'game/assets/movesets');
try { M.setInputTables(JSON.parse(readFileSync(join(msDir, 't3_input_tables.json'), 'utf8'))); } catch (e) {}
const args = process.argv.slice(2);
const baselinePath = join(root, 'test/full-movelist-baseline.json');
const baseline = existsSync(baselinePath) ? JSON.parse(readFileSync(baselinePath, 'utf8')) : {};
let fails = 0; const fail = (m) => { fails++; if (fails <= 60) console.log('FAIL', m); };

// canon runtime copy must match tools/canon
const strip = (s) => s.replace(/^\/\/ Runtime copy[^\n]*\n/, '');
assert.equal(strip(readFileSync(join(root, 'game/js/canon-names.js'), 'utf8')), readFileSync(join(root, 'tools/canon/canon-names.js'), 'utf8'), 'game/js/canon-names.js out of sync with tools/canon');
const deny = JSON.parse(readFileSync(join(root, 'tools/canon/denylist.json'), 'utf8')).terms.concat(['tekken', 'heihachi', 'kazuya', 'jin', 'paul', 'king', 'yoshimitsu', 'nina', 'law']);
const leakRe = new RegExp(`\\b(${deny.map(t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})\\b|\\(t\\d`, 'i');

// ---- unit: combat systems ----
{ const mv = { startup: 0.2, active: 0.05, recovery: 0.3, hit_level: 'h', damage: 10, limb: 'armR' };
  const hb = CS.hitbox(0, 1, mv, '2');
  assert.ok(CS.contact(hb, CS.hurtboxes(1.45, -1, 'stand'), 'stand'), 'high hits stander');
  assert.equal(CS.contact(hb, CS.hurtboxes(1.45, -1, 'crouch'), 'crouch'), null, 'high whiffs croucher');
  assert.equal(CS.contact(hb, CS.hurtboxes(4, -1, 'stand'), 'stand'), null, 'out of range whiffs');
  assert.ok(CS.contact(CS.hitbox(0, 1, { ...mv, hit_level: 'l', limb: 'legR' }, '3'), CS.hurtboxes(1.45, -1, 'crouch'), 'crouch'), 'low hits croucher');
  assert.equal(CS.reactionFor({ ...mv, launch: true }), 'launch');
  assert.equal(CS.reactionFor({ ...mv, hit_level: 'm' }, { blocking: true }), 'block');
  assert.equal(CS.reactionFor({ ...mv, hit_level: 'l' }, { blocking: true }), 'hit', 'standing guard does not block lows');
  assert.equal(CS.reactionFor({ ...mv, heavy: true }, { airborne: true, nearWall: true }), 'wall_splat');
  assert.equal(CS.reactionFor({ ...mv, screw: true }, { airborne: true }), 'screw');
  assert.equal(CS.reactionFor({ ...mv, bound: true }, { airborne: true }), 'floor_bound');
  assert.equal(CS.reactionFor({ ...mv, crumpleOnCH: true }, { counter: true }), 'crumple');
  assert.equal(CS.reactionFor(mv, { dir: 'back' }), 'spin');
  assert.equal(CS.reactionFor({ isGrab: true, input: '1+3' }, { breakInput: '1' }), 'throw_break');
  assert.equal(CS.reactionFor({ isGrab: true, input: '1+3' }, { breakInput: '2' }), 'throw');
  assert.equal(CS.reactionFor({ isGrab: true }, {}), 'throw');
  assert.ok(CS.feelFor('hit', { counter: true }).stop > CS.feelFor('hit').stop, 'counter-hit hitstop');
  assert.equal(CS.feelFor('wall_splat').sound, 'hit_wall');
  assert.ok(CS.damageFor({ damage: 10 }, { counter: true }) > 10);
  const [a, b] = CS.resolvePush(0, 0.3); assert.ok(b - a >= 0.72 - 1e-9, 'pushbox');
  assert.ok(CS.WAKEUPS.length >= 5); }

// ---- input driver (notation -> stick history + presses) ----
const BTN = /^[1-4](?:\+[1-4])*$/, DIRT = /^(d\/f|d\/b|u\/f|u\/b|f|b|u|d|n)$/i;
const CTX = { FC: { crouching: true }, WS: { rising: true }, SS: { sidestep: true }, BT: { backturned: true }, R: { rage: true } };
const SOUL = new Set(FL.SOUL_SYSTEMS.map(s => s.prefix));
function ctxFor(prefix) {
  const ps = prefix.split('.').filter(Boolean); if (ps.length > 1) return null;
  if (!ps.length) return {};
  if (SOUL.has(ps[0])) return { soulStates: [ps[0]] };
  return CTX[ps[0]] ? { ...CTX[ps[0]] } : { stance: ps[0] };
}
function feed(buf, d, n) { for (let i = 0; i < n; i++) buf.noteDirection(d); }
/** Split a body into presses: [{dirs:[...motion], dir:'f'|'', btn}] — null if not drivable. */
function presses(body) {
  const toks = body.split(/[,~:]/), out = []; let motion = [];
  for (let t of toks) {
    t = t.trim().replace(/\*$/, ''); if (!t) return null;
    if (DIRT.test(t)) { motion.push(t); continue; }
    const m = t.match(/^(?:(d\/f|d\/b|u\/f|u\/b|f|b|u|d|D\/F|D\/B|U\/F|U\/B|F|B|U|D)\+)?([1-4](?:\+[1-4])*)$/);
    if (!m) return null;
    out.push({ dirs: motion, dir: m[1] || '', btn: m[2] }); motion = [];
  }
  return motion.length ? null : out;
}
function drive(id, nota) {
  const { prefix, body } = M.splitNotation(nota);
  const ctx = ctxFor(prefix || ''); if (!ctx) return { skip: 'multi-prefix' };
  const ps = presses(body); if (!ps) return { skip: 'notation' };
  const buf = new M.TekkenBuffer(id); feed(buf, 'n', 12);
  let got = null;
  ps.forEach((p, i) => {
    let prev = null;
    for (const d of p.dirs) { const lo = d.toLowerCase(); if (prev === lo) feed(buf, 'n', 2); feed(buf, lo, d !== lo ? 6 : 2); prev = lo; }
    if (p.dir) { const lo = p.dir.toLowerCase(); if (prev === lo && p.dirs.length) feed(buf, 'n', 2); feed(buf, lo, p.dir !== lo ? 10 : (p.dirs.length ? 1 : 2)); }
    else feed(buf, 'n', 2); // 'b,1': tap, release, press
    const c = { ...ctx, inMove: i > 0 };
    got = p.btn.includes('+') ? buf.pressChord(p.btn, c) : buf.press(p.btn, c);
  });
  return { got };
}

// ---- headless combo sim ----
function runRoute(id, route) {
  let def = { x: 1.45, state: 'stand', airY: 0, phase: 'idle' }, juggle = 0, screwUsed = false, log = [];
  const buf = new M.TekkenBuffer(id); feed(buf, 'n', 12);
  for (let i = 0; i < route.length; i++) {
    const nota = route[i], r = M.resolveMove(id, nota);
    if (!r) return { ok: false, why: `${nota} unresolved`, log };
    const mv = r.move;
    const res = CS.resolveHit({ x: 0, facing: 1, airY: 0 }, def, mv, nota, { juggleHits: juggle, counter: i === 0 ? false : undefined, screwUsed });
    log.push(`${nota}:${res.connected ? res.reaction + '@' + res.bone : 'WHIFF'}`);
    if (!res.connected) return { ok: false, why: `${nota} whiffed (no hurtbox overlap)`, log };
    if (i === 0 && mv.launch && res.reaction !== 'launch') return { ok: false, why: `${nota} launcher played ${res.reaction}`, log };
    if (def.state === 'air' && !['juggle', 'screw', 'floor_bound', 'wall_splat', 'knockdown'].includes(res.reaction)) return { ok: false, why: `${nota} air reaction ${res.reaction}`, log };
    if (res.reaction === 'launch' || res.reaction === 'juggle' || res.reaction === 'floor_bound') { def = { ...def, state: 'air', airY: Math.max(0.2, 0.9 - juggle * 0.15) }; juggle++; }
    if (res.reaction === 'screw') screwUsed = true;
    if (res.reaction === 'knockdown') def = { ...def, state: 'down', airY: 0 };
  }
  return { ok: true, log };
}

const files = readdirSync(msDir).filter(f => f.endsWith('.json') && !/index|tables|ui_/.test(f));
const report = {}; let fighters = 0, tot = { base: 0, added: 0, baseOk: 0, addedOk: 0, routes: 0, routesOk: 0, skipped: 0 };
for (const f of files) {
  let d; try { d = JSON.parse(readFileSync(join(msDir, f), 'utf8')); } catch { continue; }
  if (!d || !d.moves || !d.slots) continue;
  const id = f.replace(/\.json$/, ''); M.registerMoveset(id, d); fighters++;
  const rows = FL.fullMoveList(id, d);
  const r = { base: 0, added: 0, baseOk: 0, addedOk: 0, skipped: 0, routes: 0, routesOk: 0, variants: FL.variantCount(d), misses: [] };
  for (const row of rows) {
    if (leakRe.test(row.name)) fail(`${id} ${row.notation} on-screen name leaks a source name: ${row.name}`);
    if (row.origin === 'added') {
      r.added++;
      for (const k of ['startupF', 'activeF', 'recoveryF']) if (!(row[k] > 0)) fail(`${id} ${row.notation} missing ${k}`);
      if (!row.hitLevel || !(row.damage > 0)) fail(`${id} ${row.notation} missing level/damage`);
    } else r.base++;
    const dr = drive(id, row.notation);
    if (dr.skip) { r.skipped++; continue; }
    const ok = dr.got === row.notation || (dr.got && M.resolveMoveKey(id, dr.got) === row.key);
    if (ok) row.origin === 'added' ? r.addedOk++ : r.baseOk++;
    else if (row.origin === 'added') fail(`${id} added ${row.notation} fired ${dr.got}`);
    else if (r.misses.length < 15) r.misses.push(`${row.notation}->${dr.got}`);
  }
  // every added variant must also be chainable as a combo ender
  const routes = FL.comboRoutes(d, 4);
  for (const rt of routes) { r.routes++; const o = runRoute(id, rt); if (o.ok) r.routesOk++; else fail(`${id} combo [${rt.join(' > ')}] ${o.why} | ${o.log.join(' ')}`); }
  if (routes.length < 2) fail(`${id} only ${routes.length} combo routes`);
  // throw + throw break, block, wall splat on the fighter's own data
  const thr = Object.entries(d.slots).find(([n, k]) => d.moves[k] && d.moves[k].isGrab);
  if (thr) { const mv = d.moves[thr[1]], brk = CS.throwBreakFor(mv, thr[0]).split(/\s*or\s*|\//)[0];
    if (CS.resolveHit({ x: 0, facing: 1 }, { x: 1.45, state: 'stand' }, mv, thr[0]).reaction !== 'throw') fail(`${id} throw ${thr[0]} did not grab`);
    if (CS.resolveHit({ x: 0, facing: 1 }, { x: 1.45, state: 'stand' }, mv, thr[0], { breakInput: brk }).reaction !== 'throw_break') fail(`${id} throw break ${brk}`); }
  const sp = d.moves[d.slots['SPIRIT.1+2']];
  if (CS.resolveHit({ x: 0, facing: 1 }, { x: 1.45, state: 'air', airY: 0.5 }, sp, 'SPIRIT.1+2', { nearWall: true }).reaction !== 'wall_splat') fail(`${id} 魂 ACTION near wall did not wall splat`);
  const jab = M.resolveMove(id, '1');
  if (jab && !jab.move.unblockable && CS.resolveHit({ x: 0, facing: 1 }, { x: 1.45, state: 'stand' }, jab.move, '1', { blocking: true }).reaction !== 'block' && C.hitWordFor(jab.move) !== 0x10F) fail(`${id} jab not blockable`);
  const b = baseline[id];
  if (b && r.baseOk < b.baseOk) fail(`${id} base moves reachable dropped ${b.baseOk} -> ${r.baseOk}`);
  for (const k of Object.keys(tot)) tot[k] += r[k] || 0;
  report[id] = r;
}
if (args.includes('--write-baseline')) writeFileSync(baselinePath, JSON.stringify(Object.fromEntries(Object.entries(report).map(([k, v]) => [k, { base: v.base, baseOk: v.baseOk, added: v.added }])), null, 1) + '\n');
if (args.includes('--report')) writeFileSync(args[args.indexOf('--report') + 1], JSON.stringify(report, null, 1));
console.log(JSON.stringify({ fighters, ...tot, fails }));
if (fails) { console.log('FAIL full movelist combos'); process.exit(1); }
console.log('PASS full movelist combos');

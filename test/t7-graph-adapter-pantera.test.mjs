// Pantera <- King T7 FULL-GRAPH adapter (development integration), 2026-11-10. Node only: no browser, no touchscreen,
// no model / visual proof. Run: node --test test/t7-graph-adapter-pantera.test.mjs
// The replay harness drives the REAL path: input.js InputManager (the same press / hold / release / chord code the
// keyboard handlers and the on-screen buttons call) -> t7-graph-input.js feedT7GraphInput (what game.js calls) ->
// Fighter.t7gFeed -> T7GraphDriver -> t7graph.stepCancel, on the shipped graph + clip shards.
// Expectations come from independent facts (T7 frame data for King's jab: i10, high; the 1,2 string's second hit
// starts after the jab's active frame) or from the raw source table rows (window / cancel frame / held mask), never
// from the interpreter's own output.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, statSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const KING = join(ROOT, 'game/assets/anim/t7/king/');
const q = console.log, qw = console.warn; console.log = () => {}; console.warn = () => {};
const M = await import(join(ROOT, 'game/js/movesets.js'));
const T = await import(join(ROOT, 'game/js/t3anims.js'));
const F = await import(join(ROOT, 'game/js/fighter.js'));
const IN = await import(join(ROOT, 'game/js/input.js'));
const GI = await import(join(ROOT, 'game/js/t7-graph-input.js'));
const G = await import(join(ROOT, 'game/js/t7graph.js'));
await M.loadFighterMovesets(); await M.ensureMovesets(['pantera']);
const readJson = async (rel) => JSON.parse(readFileSync(join(ROOT, 'game', rel), 'utf8'));
const bank = await T.ensureT7Graph('pantera', null, { fetchJson: readJson }); // THREE null: logic only, no clip build
console.log = q; console.warn = qw;
const g = bank.graph, ix = bank.index;
const cov = JSON.parse(readFileSync(join(KING, 'graph.coverage.json'), 'utf8'));
const mid = (n) => G.moveByName(g, n);
const DT = 1 / 120; // the game's fixed tick; the driver steps every second tick (60 Hz source frames), so tick(n) = n/2 source frames

// The input -> row -> clip MECHANICS tests below run in the labelled PERMISSIVE dev mode (precedence UNVERIFIED): under the
// game default (STRICT) the stance is blocked by its unknown row #0 (conds 809/361), see the strict tests at the end.
function pantera(strict = false) {
  const f = Object.create(F.Fighter.prototype);
  Object.assign(f, { char: { id: 'pantera' }, _movesetId: 'pantera', t3actions: {}, root: { position: { x: 0, y: 0, z: 0 } },
    facing: 1, dead: false, stun: 0, onGround: true, brawler: false, state: 'idle', stateT: 0, vx: 0, vz: 0, isPlayer: true,
    bones: {}, stats: { reachMult: 1 }, hasHit: false });
  f.tekken = new M.TekkenBuffer('pantera');
  f.t7gAttach(bank);
  f._t7g.strict = strict;
  return f;
}
// The shared input layer, exactly as the handlers use it (keyboard keydown/keyup and the touch limb buttons now do the
// same thing: held[b] + _tekken(b, t) on press, held[b] = false on release; the stick through _stick8 / stickNeutral).
function rig(strict = false, { opponent = null } = {}) {
  const inp = new IN.InputManager(); inp.enabled = true;
  const f = pantera(strict); let t = 1000; const log = [];
  const tick = (n = 1) => { for (let i = 0; i < n; i++) { t += DT * 1000; GI.feedT7GraphInput(f, inp, DT, { opponent }); if (f._t7gRec) log.push(f._t7gRec); } };
  const stick = (d) => {
    const v = { n: [0, 0], f: [1, 0], b: [-1, 0], d: [0, -1], u: [0, 1], 'd/f': [0.8, -0.8], 'd/b': [-0.8, -0.8], 'u/f': [0.8, 0.8], 'u/b': [-0.8, 0.8] }[d];
    if (d === 'n') inp.stickNeutral(); else inp._stick8(v[0], v[1]);
  };
  const press = (...b) => { for (const x of b) { inp.held[x] = true; inp._tekken(x, t); } };
  const release = (...b) => { for (const x of b) inp.held[x] = false; };
  return { inp, f, tick, stick, press, release, log, frames: () => log.filter((r, i) => i === 0 || r !== log[i - 1]) };
}
const recs = (r) => r.frames();
const firstTick = (r, name) => recs(r).find((x) => x.name === name);

test('clip bank: every reachable clip shipped once, deterministic shards under the host per-file limits, sha256 verified', () => {
  assert.equal(ix.format, 'wh-t7-graph-clips/1');
  const want = new Set(cov.reachable_clips.map(([b, c]) => `${b}_${c}`));
  assert.equal(ix.clip_count, want.size); assert.equal(Object.keys(ix.clips).length, want.size);
  for (const k of want) assert.ok(ix.clips[k], k);
  assert.deepEqual(bank.missing, []);
  let total = 0;
  for (const sh of ix.shards) {
    const p = join(KING, 'graph-clips', sh.file); const buf = readFileSync(p);
    assert.equal(buf.length, sh.bytes); total += buf.length;
    assert.equal(createHash('sha256').update(buf).digest('hex'), sh.sha256, sh.file);
    assert.ok(buf.length <= 6000000, `${sh.file} ${buf.length} B <= 6 MB (Cloudflare Pages 25 MiB, jsDelivr 20 MB per file)`);
  }
  assert.equal(total, ix.total_bytes);
  assert.equal(ix.graph_sha256, createHash('sha256').update(readFileSync(join(KING, 'graph.json'))).digest('hex'));
});

test('reused bake: the 50 clips also baked independently for the shipped moves pack are identical (rotations, root, raw root channel)', () => {
  const pack = JSON.parse(readFileSync(join(KING, 'moves.pack.json'), 'utf8'));
  const shardData = {}; for (const sh of ix.shards) Object.assign(shardData, JSON.parse(readFileSync(join(KING, 'graph-clips', sh.file), 'utf8')).clips);
  let n = 0;
  for (const c of Object.values(pack.clips)) {
    const s = c.t7_source; const b = /rotsm/.test(s.file) ? 'rotsm' : /common/.test(s.file) ? 'common' : 'motbin';
    const d = shardData[`${b}_${s.clip}`]; if (!d) continue;
    assert.deepEqual(d.rot_xyzw, c.rot_xyzw, s.anim); assert.deepEqual(d.root_t, c.root_t, s.anim);
    assert.deepEqual(d.root_motion_fwd_m, c.root_motion_fwd_m, s.anim); n++;
  }
  assert.ok(n >= 45, `${n} shared clips compared`);
});

test('real input path: neutral stands in the source stance; 1 -> Kg_lp00F (i10 high, T7 frame data), back to the stance at its AUTO frame', () => {
  const r = rig(); r.tick(20);
  assert.equal(r.f.state, 'tekgraph'); assert.equal(r.f._t7gRec.name, 'Kg_sKAM00_');
  r.press('1'); r.tick(2); r.release('1'); r.tick(80);
  const jab = recs(r).filter((x) => x.name === 'Kg_lp00F');
  assert.equal(jab[0].frame, 1);
  const act = jab.filter((x) => x.active).map((x) => x.frame);
  assert.deepEqual(act, [10], 'active on frame 10 only (first/last active 10)');
  const row = g.moves[mid('Kg_lp00F')].cancels.find((c) => c[0] === G.AUTO);
  assert.equal(jab[jab.length - 1].frame, row[G.F.start], 'the jab ends at its own AUTO frame (source window start)');
  assert.equal(recs(r).at(-1).name, 'Kg_sKAM00_');
});

test('combat state: the jab produces a hitbox only on its active frame, high (T3 attack-word layout on the source hit level)', () => {
  const r = rig(); r.tick(4); r.press('1'); r.tick(2); r.release('1');
  const seen = [];
  for (let i = 0; i < 60; i++) { r.tick(1); const hb = r.f.getHitbox(); if (hb) seen.push([r.f._t7gRec.frame, hb.move.level, hb.move.damage]); }
  assert.ok(seen.length >= 1 && seen.every(([fr]) => fr === 10), JSON.stringify(seen));
  assert.equal(seen[0][1], 'high'); assert.equal(seen[0][2], g.moves[mid('Kg_lp00F')].damage);
  r.f.registerHit(); r.tick(1); assert.equal(r.f.getHitbox(), null, 'one hit per move instance');
});

test('buffered string 1,2: the 2 pressed on jab frame ~4 waits for the cancel frame (10), so the jab reaches its hit first', () => {
  const r = rig(); r.tick(4); r.press('1'); r.tick(2); r.release('1'); r.tick(6); r.press('2'); r.tick(2); r.release('2'); r.tick(60);
  const row = g.moves[mid('Kg_lp00F')].cancels.find((c) => c[0] < G.AUTO && c[G.F.buttons] === 2 && c[G.F.dir] === 0);
  assert.equal(g.moves[G.resolveMoveId(g, row[G.F.to])].name, 'Kg_lprpF');
  const jabFrames = recs(r).filter((x) => x.name === 'Kg_lp00F').map((x) => x.frame);
  assert.equal(Math.max(...jabFrames), row[G.F.sf], 'jab plays through its cancel frame');
  assert.ok(jabFrames.includes(10), 'the jab hit frame plays before the follow-up');
  assert.ok(firstTick(r, 'Kg_lprpF'), 'the follow-up comes out');
});

test('hold vs release (source held-mask rows): 3+4 -> Kg_fstep; HOLD 3+4 -> Kg_fstep01 at frame 20; released early -> stance at the AUTO', () => {
  const held = rig(); held.tick(4); held.press('3', '4'); held.tick(90);
  assert.ok(firstTick(held, 'Kg_fstep'), 'n+3+4 -> Kg_fstep');
  const fs = recs(held).filter((x) => x.name === 'Kg_fstep');
  assert.equal(fs.at(-1).frame, 20); assert.ok(firstTick(held, 'Kg_fstep01'), 'held through frame 20');
  const rel = rig(); rel.tick(4); rel.press('3', '4'); rel.tick(4); rel.release('3', '4'); rel.tick(120);
  assert.equal(firstTick(rel, 'Kg_fstep01'), undefined, 'released before 20: no held follow-up');
  const fr = recs(rel).filter((x) => x.name === 'Kg_fstep');
  assert.equal(fr.at(-1).frame, 34, 'ends at its AUTO (window start 34)'); assert.equal(recs(rel).at(-1).name, 'Kg_sKAM00_');
});

test('double tap f through the shared buffer -> Kg_sDASHF; f held at dash frame 12 -> run (source), raw-root travel forward', () => {
  const r = rig(); r.tick(4);
  r.stick('f'); r.tick(4); r.stick('n'); r.tick(4); r.stick('f'); r.tick(80);
  const dash = recs(r).filter((x) => x.name === 'Kg_sDASHF');
  assert.ok(dash.length, 'dash'); assert.equal(dash.at(-1).frame, 12, 'leaves the dash on frame 12');
  assert.ok(firstTick(r, 'sRUN__00F'), 'run'); assert.ok(r.f.root.position.x > 1.0, `travel ${r.f.root.position.x}`);
  const n = rig(); n.tick(4); n.stick('f'); n.tick(4); n.stick('n'); n.tick(4); n.stick('f'); n.tick(2); n.stick('n'); n.tick(60);
  assert.equal(firstTick(n, 'sRUN__00F'), undefined, 'released before frame 12: no run');
});

test('context: f+3 from the stance is Kg_lk00F; the run attack Kg_666lk never comes out of the stance', () => {
  const r = rig(); r.tick(4); r.stick('f'); r.press('3'); r.tick(2); r.release('3'); r.stick('n'); r.tick(40);
  const fired = recs(r).map((x) => x.name);
  assert.ok(fired.includes('Kg_lk00F'), fired.join(','));
  assert.ok(!fired.includes('Kg_666lk'));
});

test('unknown requirements are never satisfied: every fire across a long replay has an all-known, all-true requirement list', () => {
  const r = rig(); const seq = ['1', '2', '3', '4', '1+2', '3+4', '1+3', '2+4', '2+3', '1+4'];
  const dirs = ['n', 'f', 'b', 'd', 'd/f', 'd/b', 'u', 'u/f', 'u/b'];
  for (let i = 0; i < 400; i++) {
    r.stick(dirs[(i * 7) % dirs.length]); r.tick(3);
    if (i % 3 === 0) { const b = seq[(i * 5) % seq.length].split('+'); r.press(...b); r.tick(2); r.release(...b); }
    r.tick(5);
  }
  const ev = G.makeEvalCond({ dead: false, charId: 2, controller: 0 }); // the fighter's own context (fighter.js t7gAttach)
  let fires = 0;
  for (const x of r.log) {
    if (!x.fired || x.fired.via !== 'cancel') continue;
    const row = g.moves[x.moveId].cancels[x.fired.index]; fires++;
    for (const [c, p] of g.requirements[String(row[G.F.req])] || []) {
      if (c === 0) continue;
      assert.ok(G.KNOWN_CONDITIONS[c], `fired row needs only known conditions (got ${c})`);
      assert.equal(ev(c, p), true);
    }
  }
  assert.ok(fires > 50, `${fires} source cancels fired`);
  assert.ok(r.f._t7g.stats.skipped.requirement > 0, 'rows with unknown conditions were skipped, not taken');
});

test('negatives: unknown condition 72 stays unknown in the game; cond 35/36 unknown without a T7-unit distance; mode-0 sequence elements unproven', () => {
  const ev = G.makeEvalCond({ dead: false });
  assert.equal(ev(72, 0), null); assert.equal(ev(35, 1800), null); assert.equal(ev(124, 0), null);
  const s = g.sequences.findIndex((x) => x.inputs.some((e) => e[2] === 0 && e[1]));
  assert.ok(s >= 0); assert.equal(G.matchSequence(g, s, [{ dir: 'n', down: 1, held: 1 }]), null);
});

test('dev integration is opt-in: without the flag the default game is unchanged (no graph attached at bind)', () => {
  assert.equal(F.t7GraphDevEnabled(), false);
  globalThis.WH_T7GRAPH = true; assert.equal(F.t7GraphDevEnabled(), true); delete globalThis.WH_T7GRAPH;
});

test('generated command list: EVERY evaluable stance press command replays through the real input path into its source move', () => {
  // (a direction held BEFORE the press is checked separately below)
  const C = JSON.parse(readFileSync(join(KING, 'graph.commands.json'), 'utf8'));
  assert.equal(C.graph_sha256, ix.graph_sha256);
  const stanceRows = C.all.filter((x) => x.from === C.stance && x.kind === 'press');
  const BIT = G.DIR_BITS;
  const okRows = stanceRows.filter((x) => x.status === 'evaluable');
  assert.equal(okRows.length, C.stance_press_commands_evaluable.length);
  let tested = 0; const bad = [];
  for (const cmd of okRows) {
    if (/RA/.test(cmd.notation)) continue; // WH has no rage-art button
    const [d0, rest] = cmd.notation.split('+(any of ')[0].split(/\+(.*)/s);
    const dir = d0 === '*' ? 'n' : d0.split('|')[0];
    const pressed = (cmd.notation.includes('(any of') ? cmd.notation.split('(any of ')[1].replace(')', '').split('+').slice(0, 1) : rest.split(' ')[0].split('+'));
    // Independent expectation: the first evaluable stance row (table order) this exact input satisfies.
    const pm = G.buttonsMask(pressed);
    const exp = okRows.find((x) => {
      const r = g.moves[g.stance].cancels[x.row];
      return (r[G.F.dir] === 0 || (r[G.F.dir] & BIT[dir])) &&
        (r[G.F.mode] === G.MODE_ANY ? (r[G.F.buttons] & pm) !== 0 : (r[G.F.buttons] & pm) === r[G.F.buttons]);
    });
    // Stick and limbs on the same source frame (a stick held earlier is a state input of its own: e.g. d/f alone takes
    // the stance's d/f state row into the crouch transition first, exactly as the table orders it).
    const r = rig(); r.tick(6); r.stick(dir); r.press(...pressed); r.tick(2); r.release(...pressed); r.tick(2);
    const got = recs(r).find((x) => x.name !== C.stance);
    tested++;
    if (!got || got.name !== exp.to) bad.push(`${cmd.notation}: expected ${exp.to}, got ${got && got.name}`);
  }
  assert.deepEqual(bad, []);
  assert.ok(tested >= 60, `${tested} stance commands replayed`);
});

test('a direction held before the press is its own state input (d/f -> the stance d/f state row, crouch transition), per table order', () => {
  const r = rig(); r.tick(6); r.stick('d/f'); r.tick(6);
  const C = JSON.parse(readFileSync(join(KING, 'graph.commands.json'), 'utf8'));
  const rows = C.all.filter((x) => x.from === C.stance && x.kind === 'state' && !x.notation.includes('[') &&
    x.notation.split('|').includes('d/f'));
  assert.ok(rows.findIndex((x) => x.status === 'unknown') < rows.findIndex((x) => x.status === 'evaluable'),
    'earlier d/f rows are blocked by unknown conditions (72 / 35 / 68 / 103) and are skipped, not taken');
  const st = rows.find((x) => x.status === 'evaluable');
  const got = recs(r).find((x) => x.name !== 'Kg_sKAM00_');
  assert.equal(got.name, st.to);
  const fire = recs(r).find((x) => x.fired && x.fired.toName === st.to);
  assert.ok(fire.fired.precedenceUnknown.length > 0, 'flagged: an unknown-condition row outranked it in table order');
});

test('the graph input reads the stick with the SAME function body as game.js _tekkenDir (no drift)', () => {
  const src = readFileSync(join(ROOT, 'game/js/game.js'), 'utf8');
  const m = /\n\s*_tekkenDir\(inp, facing\) \{\n([\s\S]*?)\n  \}\n/.exec(src);
  const mod = readFileSync(join(ROOT, 'game/js/t7-graph-input.js'), 'utf8');
  const k = /export function tekkenDirOf\(inp, facing\) \{\n([\s\S]*?)\n\}\n/.exec(mod);
  assert.ok(m && k);
  const norm = (t) => t.split('\n').map((l) => l.trim()).join('\n');
  assert.equal(norm(k[1]), norm(m[1]));
});

/* Exe-decoded requirements (docs/proof/2026-11-10/t7-requirements/README.md). The expectations are the exe's
   comparisons, written out by hand from the disassembly, and are checked against the shipped evaluator. */
test('exe-decoded requirements: 217 own chara_id (+ exe group params), 225 controller, 609 items, 72/73 backturn; fail closed without context', () => {
  const none = G.makeEvalCond({});
  for (const c of [72, 73, 217, 225, 609]) assert.equal(none(c, 0), null, `cond ${c} without context stays UNKNOWN`);
  const king = G.makeEvalCond({ charId: 2, controller: 0 });
  assert.equal(king(217, 2), true); assert.equal(king(217, 10), false); assert.equal(king(217, 75), false);
  assert.equal(king(217, 83), false, 'param 83 tests chara_id 5 (exe jump table)');
  assert.equal(G.makeEvalCond({ charId: 5 })(217, 83), true);
  assert.equal(G.makeEvalCond({ charId: 0x21 })(217, 76), true);
  assert.equal(king(225, 0), true); assert.equal(king(225, 1), false); assert.equal(king(225, 3), false);
  assert.equal(G.makeEvalCond({ controller: 1 })(225, 0), null, 'CPU + param 0 depends on unmodelled exe flags');
  assert.equal(king(609, 146), null, 'the equipped T7 item set is not known for Pantera');
  assert.equal(G.makeEvalCond({ items: [146] })(609, 146), true);
  assert.equal(king(72, 0), null); assert.equal(king(73, 0), null);
  assert.equal(G.makeEvalCond({ relHeading16: 0 })(73, 0), true);
});

test('real fighter: the attached driver carries King\'s chara_id 2 and the player controller; rows for other chara_ids never fire', () => {
  const r = rig(); r.tick(4);
  assert.equal(r.f._t7g.evalState.charId, 2); assert.equal(r.f._t7g.evalState.controller, 0);
  assert.equal(r.f._t7g.evalState.items, undefined, 'items stay unknown');
  const seq = ['1', '2', '3', '4', '1+2', '3+4', '1+3', '2+4'];
  const dirs = ['n', 'f', 'b', 'd', 'd/f', 'f', 'f'];
  for (let i = 0; i < 300; i++) {
    r.stick(dirs[(i * 3) % dirs.length]); r.tick(2);
    if (i % 2 === 0) { const b = seq[(i * 5) % seq.length].split('+'); r.press(...b); r.tick(2); r.release(...b); }
    r.tick(4);
  }
  let gated = 0;
  for (const x of r.log) {
    if (!x.fired || x.fired.via !== 'cancel') continue;
    const row = g.moves[x.moveId].cancels[x.fired.index];
    for (const [c, p] of g.requirements[String(row[G.F.req])] || []) {
      if (c !== 217) continue; gated++;
      const want = G.T7_CHAR_GROUPS[p] ?? p;
      assert.equal(want, 2, `fired ${x.name} row ${x.fired.index} is gated to chara_id ${want}, not King`);
    }
  }
  assert.ok(gated > 0, `${gated} fires were gated on King's own chara_id`);
});

/* Facing family, decoded from exe 0x1406ebfe0 (writes [+0x1c2] = own yaw - bearing to opponent, [+0x1c4] = folded) and
   the evaluator cases 72/73/80/81. Boundary values are the exe's own comparisons. */
test('exe facing decode: 72/73 on the folded angle (> / <= 0x4000), 80 = rel in [0x3fff,0x7fff], 81 = rel in [0x8000,0xbfff]; null without relHeading16', () => {
  const at = (rel) => G.makeEvalCond({ relHeading16: rel });
  const none = G.makeEvalCond({ charId: 2, controller: 0 });
  for (const c of [72, 73, 80, 81]) assert.equal(none(c, 0), null);
  assert.equal(G.t7FacingFold({ relHeading16: 0xC000 }), 0x3fff); assert.equal(G.t7FacingFold({ relHeading16: 0x8000 }), 0x7fff);
  assert.equal(at(0)(72, 0), false); assert.equal(at(0)(73, 0), true);
  assert.equal(at(0x4000)(72, 0), false); assert.equal(at(0x4001)(72, 0), true);
  assert.equal(at(0xBFFF)(72, 0), false); assert.equal(at(0xBFFE)(72, 0), true); assert.equal(at(0xBFFE)(73, 0), false);
  assert.equal(at(0x3ffe)(80, 0), false); assert.equal(at(0x3fff)(80, 0), true); assert.equal(at(0x7fff)(80, 0), true); assert.equal(at(0x8000)(80, 0), false);
  assert.equal(at(0x7fff)(81, 0), false); assert.equal(at(0x8000)(81, 0), true); assert.equal(at(0xbfff)(81, 0), true); assert.equal(at(0xc000)(81, 0), false);
});

test('real fighter, stance n+1+2: the source BT row (stance row 280, req [72] -> Kg_Tnrpsp) is skipped as UNKNOWN in the game, never taken; it fires only under an injected backturned heading and is known-false when facing', () => {
  const row = g.moves[g.stance].cancels[280];
  assert.deepEqual(g.requirements[String(row[G.F.req])], [[72, 0]]);
  assert.equal(G.moveByName(g, 'Kg_Tnrpsp'), G.resolveMoveId(g, row[G.F.to]));
  const run = (rel) => {
    const r = rig(); if (rel !== undefined) r.f._t7gHeadingOverride = rel; // TEST INJECTION, not a runtime source
    r.tick(6); r.press('1', '2'); r.tick(2); r.release('1', '2'); r.tick(4);
    const fire = r.log.find((x) => x.fired && x.moveId === g.stance && x.fired.via === 'cancel');
    const sk = r.log.flatMap((x) => (x.moveId === g.stance ? x.skipped || [] : []));
    return { fire, sk, r };
  };
  const game = run();
  assert.equal(game.r.f._t7g.evalState.relHeading16, null, 'no opponent geometry: no heading');
  assert.ok(game.sk.some((k) => k.index === 280 && k.reason === 'requirement' && k.unknown && k.unknown.includes(72)), 'skipped as unknown 72');
  assert.ok(game.fire && game.fire.fired.index !== 280 && game.fire.fired.toName !== 'Kg_Tnrpsp');
  assert.ok(game.fire.fired.precedenceUnknown.length > 0, 'flagged: an unknown row outranked the fired row');
  const bt = run(0x8000);
  assert.equal(bt.fire.fired.index, 280); assert.equal(bt.fire.fired.toName, 'Kg_Tnrpsp');
  const facing = run(0);
  assert.ok(facing.fire.fired.index !== 280);
  assert.ok(!facing.sk.some((k) => k.index === 280 && k.unknown), 'facing the opponent: 72 is known-false, not unknown');
});

test('throws are visibly UNSUPPORTED: a throw-class source move plays its clip only, never a hitbox, and is counted and labelled', () => {
  const C = JSON.parse(readFileSync(join(KING, 'graph.commands.json'), 'utf8'));
  const thr = C.all.find((x) => x.from === C.stance && x.kind === 'press' && x.status === 'evaluable' &&
    g.moves[G.moveByName(g, x.to)].damage === 0x4000 && /^Thrmv/.test(x.to));
  assert.ok(thr, 'an evaluable stance throw command exists');
  const [d0, rest] = thr.notation.split(/\+(.*)/s); const btn = rest.split(' ')[0].split('+');
  const r = rig(); r.tick(6); r.stick(d0 === '*' ? 'n' : d0.split('|')[0]); r.press(...btn); r.tick(2); r.release(...btn);
  let sawHitbox = false; let inThrow = 0;
  for (let i = 0; i < 120; i++) { r.tick(1); const x = r.f._t7gRec; if (x && x.unsupported) inThrow++; if (x && x.unsupported && r.f.attack) sawHitbox = true; }
  assert.ok(recs(r).some((x) => x.name === thr.to), `${thr.notation} -> ${thr.to}`);
  assert.ok(inThrow > 0); assert.equal(sawHitbox, false, 'no hitbox: there is no grab');
  assert.ok(r.f._t7gStatus.throwNoGrab >= 1);
  assert.match(recs(r).find((x) => x.name === thr.to).unsupported, /NO GRAB/);
  assert.match(r.f._t7gStatus.assumptions, /posture: standing \(source posture undecoded\) \| facing: tracked source yaw \(entry turn\/flip from the exe, live bearing\); per-frame tracking \+ entry continuity correction \+ \[0xdb4\] modes unmodelled/);
  const marked = g.moves.filter((m) => m.damage === 0x4000);
  assert.equal(marked.length, 43, 'source hit conditions with the 0x4000 throw marker');
});

/* Source-accurate selection: exe requirement lists are a plain AND (0x1406f4750: acc = acc && eval, until 0x371), and the
   cancel walk takes the first row that holds. STRICT is the game default under the dev flag. */
test('exe list semantics: any known-false entry makes the list false even after an unknown one; ids with bit 0x8000 are true', () => {
  const ctx = { charId: 2, controller: 0, relHeading16: 0 };
  const ev = G.makeEvalCond(ctx);
  const req221 = g.moves[g.stance].cancels[221][G.F.req];
  assert.deepEqual(g.requirements[String(req221)], [[609, 146], [72, 0]]);
  const r = G.evalRequirements(g, req221, ctx, ev);
  assert.equal(r.ok, false); assert.deepEqual(r.unknown, [], 'facing the opponent: 72 false decides the list, 609 does not matter');
  const r2 = G.evalRequirements(g, req221, {}, G.makeEvalCond({ charId: 2, controller: 0 }));
  assert.deepEqual(r2.unknown, [609, 72], 'without a heading both stay unknown');
  assert.equal(ev(0x8106, 0), true); assert.equal(ev(0x8414, 3), true);
});

test('STRICT, real Fighter, NO opponent geometry (heading unknown): no input fires; every block is a facing (72/80) or item (609) row; neutral no longer blocks (exe walker: button-less rows are non-stopping or known-false)', () => {
  assert.equal(F.t7GraphStrict(), true, 'strict unless the labelled permissive diagnostic is requested');
  globalThis.WH_T7GRAPH = 'permissive'; assert.equal(F.t7GraphStrict(), false); delete globalThis.WH_T7GRAPH;
  const st = g.moves[g.stance].cancels;
  assert.deepEqual(g.requirements[String(st[132][G.F.req])], [[815, 16], [359, 655361], [553, 800], [33816, 655660], [33030, 655360], [33446, 0]]);
  for (const [dir, btn] of [['n', []], ['n', ['1']], ['f', []], ['d/f', []], ['n', ['3', '4']], ['f', ['1', '3']]]) {
    const r = rig(true); assert.equal(r.f._t7g.strict, true);
    r.tick(4); r.stick(dir); if (btn.length) r.press(...btn); r.tick(2); if (btn.length) r.release(...btn); r.tick(150);
    const cf = r.frames().filter((x) => x.fired && x.fired.via === 'cancel' && g.moves[x.moveId].cancels[x.fired.index][G.F.cmd] !== G.AUTO);
    assert.equal(cf.length, 0, `${dir}+${btn.join('+')}: no cancel fires (${cf.map((x) => x.name + '#' + x.fired.index + '->' + x.fired.toName)})`);
    assert.equal(r.f._t7g.evalState.playerFlags[10], 0, 'exe init 0x140759a50 zeroes the flag words');
    const amb = r.log.filter((x) => x.ambiguous);
    const why = new Set(amb.flatMap((x) => x.ambiguous.unknown));
    assert.ok([...why].every((c) => [72, 80, 609].includes(c)), `only facing / item block: ${[...why]}`);
    if (dir === 'n' && !btn.length) assert.equal(amb.length, 0, 'neutral: nothing outranks, nothing blocks');
    assert.ok(!r.f.attack);
  }
});

/* End to end under the exe walker semantics, STRICT, with the opponent straight ahead (the round-start geometry: exe
   0x1406e5623 sets yaw = bearing, so [self+0x1c2] = 0). The driver tracks the source yaw across move entries (entry
   turn/flip, exe 0x14074ff8c..0x1407500a5) and recomputes rel = yaw - live bearing every frame, so the heading stays
   resolved after every source move and continued play is no longer blocked on facing. */
test('STRICT end to end, opponent ahead: neutral -> 1 = Kg_lp00F; 1,2 string -> Kg_lprpF; f -> walk; heading stays resolved after every source move', () => {
  const opp = { root: { position: { x: 3, y: 0, z: 0 } } };
  let r = rig(true, { opponent: opp }); r.tick(4);
  assert.equal(r.f._t7g.evalState.relHeading16, 0);
  r.press('1'); r.tick(2); r.release('1'); r.tick(8); r.press('2'); r.tick(2); r.release('2'); r.tick(60);
  const fires = r.frames().filter((x) => x.fired && x.fired.via === 'cancel').map((x) => x.fired.toName);
  assert.deepEqual(fires.slice(0, 2), ['Kg_lp00F', 'Kg_lprpF'], `fired ${fires}`);
  // After the 1,2 string the heading is still resolved (tracked yaw 0, opponent ahead): the stance is not blocked.
  assert.equal(r.f._t7g.yaw, 0); assert.equal(r.f._t7g.evalState.relHeading16, 0);
  assert.ok(!r.frames().some((x) => x.ambiguous), 'no ambiguous block after the string');
  r = rig(true, { opponent: opp }); r.tick(400);
  assert.ok(r.frames().some((x) => x.fired && x.fired.toName === 'Kg_sKAM00_'), 'the stance looped through its AUTO row');
  assert.equal(r.f._t7g.yaw, 0, 'idle loop (same move, turn word 0, no flip) keeps the tracked yaw');
  assert.equal(r.f._t7g.evalState.relHeading16, 0);
  r.press('1'); r.tick(2); r.release('1'); r.tick(4);
  assert.equal(r.frames().filter((x) => x.fired && x.fired.via === 'cancel').map((x) => x.fired.toName).pop(), 'Kg_lp00F');
  r = rig(true, { opponent: opp }); r.tick(4); r.stick('f'); r.tick(6);
  assert.equal(r.log.filter((x) => x.fired && x.fired.via === 'cancel')[0].fired.toName, 'Kg_sWALKF');
  // The opponent walks behind mid-fight (bearing flips to pi, the tracked yaw stays 0): backturned, 72 true.
  const opp2 = { root: { position: { x: 3, y: 0, z: 0 } } };
  r = rig(true, { opponent: opp2 }); r.tick(4);
  assert.equal(r.f._t7g.evalState.relHeading16, 0);
  opp2.root.position.x = -3; r.tick(2);
  assert.equal(r.f._t7g.evalState.relHeading16, 0x8000, 'opponent behind: tracked yaw 0 - bearing pi -> rel 0x8000');
  assert.equal(G.makeEvalCond(r.f._t7g.evalState)(72, 0), true, 'backturned: 72 true');
  assert.equal(G.makeEvalCond(r.f._t7g.evalState)(73, 0), false, 'backturned: 73 false');
});

/* Heading regression (lane B, 2026-11-10): after any source move the heading stays resolved and continued play works
   through a full sequence — jab, 1,2 string, walk, dash, dash-loop, dashing punch — with no facing block and no
   stall. Before the fix the 2nd jab / walk / dash never fired (the stance was blocked by row #306/#467 cond 80). */
test('STRICT heading regression, opponent ahead: 1,2 -> walk -> dash -> dash-loop -> dashing punch completes; heading resolves after every move, zero facing blocks, zero stalls', () => {
  const opp = { root: { position: { x: 3, y: 0, z: 0 } } };
  const r = rig(true, { opponent: opp }); r.tick(4);
  r.press('1'); r.tick(2); r.release('1'); r.tick(8); r.press('2'); r.tick(2); r.release('2'); r.tick(60);
  r.stick('f'); r.tick(20); r.stick('n'); r.tick(4); r.stick('f'); r.tick(30);
  r.stick('n'); r.tick(10); r.press('1'); r.tick(2); r.release('1'); r.tick(60);
  const fires = r.frames().filter((x) => x.fired && x.fired.via === 'cancel').map((x) => x.fired.toName);
  for (const n of ['Kg_lp00F', 'Kg_lprpF', 'Kg_sWALKF', 'Kg_sDASHF']) assert.ok(fires.includes(n), `fired ${fires}`);
  assert.ok(fires.length >= 5, `5+ consecutive moves: ${fires}`);
  assert.ok(!r.frames().some((x) => x.ambiguous && x.ambiguous.unknown.some((c) => [72, 73, 80, 81].includes(c))), 'no facing block at any point');
  assert.ok(!r.frames().some((x) => x.stalled), 'no stall at any point');
  assert.ok(r.frames().every((x) => x.relHeading16 !== null && x.relHeading16 !== undefined), 'heading resolved on every frame');
  assert.equal(r.f._t7g.evalState.relHeading16, 0);
});

/* Foundation fixtures transcribed from the exe (not expectations of blocking): loader-derived cancel_option, matcher. */
test('exe loader cancel_option (0x140714f5e): cmd 0 -> 0x01; ids >= 0x32C -> 0x02; extradata&0x3C00 == 0x2800 -> non-stopping; the packed data carries 0', () => {
  const st = g.moves[g.stance].cancels;
  assert.ok(g.moves.every((m) => m.cancels.every((c) => c[G.F.option] === 0)), 'every packed cancel_option is 0 (derived at load)');
  assert.equal(G.t7CancelOption(g, st[322]) & 0x41, 0x01, '#322: command 0, extradata 0x2800 -> matches always, never stops');
  assert.equal(st[322][G.F.extradata], 0x2800);
  assert.ok(G.t7CancelOption(g, st[132]) & 0x02, '#132 holds 815 (>= 0x32C): secondary walk only');
  assert.ok(G.t7CancelOption(g, st[461]) & 0x40, 'jab row stops the walk');
  assert.equal(g.moves[G.resolveMoveId(g, st[461][G.F.to])].name, 'Kg_lp00F');
  const ev = G.makeEvalCond({ charId: 2, controller: 0, relHeading16: 0, playerVars: { [0x938]: 0, [0x964]: 0 }, playerFlags: new Array(100).fill(0) });
  assert.equal(ev(0, 0), true, 'requirement 0: exe case 0 -> mov bl,1');
});
test('exe matcher (0x140742de0 / 0x140743d40): button word 0 matches with or without presses; 0x40 mode = one pressed + all held; 0x20 = any pressed', () => {
  const ctx = (dir, down, held) => ({ frame: 1, moveLen: 60, dir, down, held, history: [{ dir, down: G.buttonsMask(down), held: G.buttonsMask(held) }],
    evalCond: () => true, strict: true });
  const fake = (cmd, raw, xd = 0) => ({ aliases: [], requirements: { 0: [] }, moves: [{ cancels: [[cmd, cmd, raw & 0x1f, raw >>> 24, -1, 0, 1, 32767, 1, 0, 0, xd, -1, 0, 0, raw]] }] });
  assert.ok(G.stepCancel(fake(0, 0), 0, ctx('n', ['1'], ['1'])).row, 'all-zero command takes a press frame too');
  assert.ok(G.stepCancel(fake(0x20, 0x40000003), 0, ctx('n', ['1'], ['1', '2'])).row, '1 pressed, 2 held -> 0x40 match');
  assert.ok(!G.stepCancel(fake(0x20, 0x40000003), 0, ctx('n', ['1'], ['1'])).row, '2 not held -> no match');
  assert.ok(G.stepCancel(fake(0x20, 0x20000003), 0, ctx('n', ['2'], ['2'])).row, '0x20: any of 1/2 pressed');
  assert.ok(!G.stepCancel(fake(0x20, 0x00000001), 0, ctx('f', ['1'], ['1'])).row, 'direction n only');
  const side = fake(0, 0, 0x2800); side.moves[0].cancels.push([0x8000, 0, 0, 0, -1, 0, 1, 32767, 1, 0, 0, 0, -1, 0, 0, 0]);
  const r = G.stepCancel(side, 0, ctx('n', [], []));
  assert.equal(r.index, 1, 'a passing non-stopping row (extradata 0x2800) does not end the walk');
});

test('player variables: King\'s extra-property lists never write them; his cancel requirement lists do (fail closed after such a row fires); suspension makes them unknown', () => {
  const P = JSON.parse(readFileSync(join(KING, 'graph.props.json'), 'utf8'));
  assert.equal(P.format, 'wh-t7-graph-props/1'); assert.equal(P.moves.length, g.moves.length);
  assert.equal(P.counts.extra_rows, 12227);
  const W = new Set(Object.keys(G.T7_VAR_WRITERS).map(Number));
  assert.equal(P.moves.flatMap((m) => [...m.extra, ...m.start, ...m.end]).filter((x) => W.has(x[2])).length, 0);
  const rowsWithWriters = [];
  g.moves.forEach((m, mi) => m.cancels.forEach((r, ri) => {
    if ((g.requirements[String(r[G.F.req])] || []).some(([c]) => W.has(c))) rowsWithWriters.push([mi, ri]);
  }));
  assert.equal(rowsWithWriters.length, 667);
  const r = rig(true); const D = r.f._t7g;
  const [mi, ri] = rowsWithWriters.find(([mi, ri]) => g.requirements[String(g.moves[mi].cancels[ri][G.F.req])].some(([c]) => c === 0x8414));
  D._varWriters(ri, g.moves[mi]);
  assert.equal(D.evalState.playerVars[0x938], null); assert.equal(G.makeEvalCond(D.evalState)(809, 15), null);
  const r2 = rig(true); r2.f._t7gSuspended = true; r2.f.state = 'idle'; r2.tick(2);
  assert.deepEqual(r2.f._t7g.evalState.playerVars, { [0x938]: null, [0x964]: null });
});

test('PERMISSIVE diagnostic (labelled UNVERIFIED): without heading the same press fires a lower row and is flagged with the outranking unknown facing conditions', () => {
  const r = rig(false); r.tick(4); r.press('1'); r.tick(2); r.release('1'); r.tick(4);
  const fire = r.log.find((x) => x.fired && x.fired.via === 'cancel');
  assert.equal(fire.fired.toName, 'Kg_lp00F');
  assert.ok(fire.fired.precedenceUnknown.includes(80), 'facing rows outrank the jab row and were skipped');
});

/* Foundations validated against the shipping exe (fixtures extracted from the binary, not from expectations of blocking). */
test('exe default case: 329 requirement ids whose jump-table slot is the default (xor bl,bl) are ALWAYS false; decoded ids are not in it', () => {
  assert.equal(G.T7_EXE_DEFAULT_FALSE.size, 329);
  for (const c of [1, 167, 254, 739, 742, 568]) assert.equal(G.makeEvalCond({})(c, 0), false, `${c}`);
  for (const c of [35, 36, 72, 73, 80, 81, 135, 217, 225, 356, 359, 361, 553, 609, 809, 815]) assert.ok(!G.T7_EXE_DEFAULT_FALSE.has(c), `${c} has its own case`);
  assert.equal(G.makeEvalCond({})(0x36c, 0), false, 'above the table: ja -> default');
  assert.equal(G.makeEvalCond({})(0x8001, 0), true, 'bit 0x8000 still returns 1 first');
});

test('player flags (359): idx = param>>16 (<= 0x63), value = sign-extended low word; init zero; a flag writer (0x8106-8) in a fired list or an entered move\'s properties makes that flag UNKNOWN, never a guessed value', () => {
  const ev = (fl) => G.makeEvalCond({ playerFlags: fl });
  const z = new Array(100).fill(0);
  assert.equal(ev(z)(359, (10 << 16) | 1), false); assert.equal(ev(z)(359, 10 << 16), true);
  assert.equal(ev(z)(359, (0x64 << 16) | 0), false, 'idx > 0x63 -> false (exe bound)');
  assert.equal(ev(z)(359, (3 << 16) | 0xffff), false, 'value -1 never equals an unsigned word');
  const u = z.slice(); u[10] = null; assert.equal(ev(u)(359, (10 << 16) | 1), null);
  assert.equal(ev(null)(359, 0), null, 'untracked -> unknown');
  const r = rig(true); const D = r.f._t7g;
  D._applyWriters([[0x8106, (10 << 16) | 1]]); assert.equal(D.evalState.playerFlags[10], null);
  assert.equal(D.evalState.playerFlags[11], 0);
  const P = bank.props; assert.equal(P.format, 'wh-t7-graph-props/1');
  const mi = P.moves.findIndex((m) => m.extra.some((x) => x[2] === 0x8106));
  assert.ok(mi >= 0); const k = P.moves[mi].extra.find((x) => x[2] === 0x8106)[3] >>> 16;
  const r2 = rig(true); r2.f._t7g._enter(mi); assert.equal(r2.f._t7g.evalState.playerFlags[k], null, 'entered move with a flag writer');
});

test('STRICT, opponent ahead: f,n,f double tap reaches Kg_sDASHF through source rows; the run is held back by undecoded cond 124 (dash re-fire row), NOT by facing anymore', () => {
  const opp = { root: { position: { x: 3, y: 0, z: 0 } } };
  const r = rig(true, { opponent: opp }); r.tick(4);
  r.stick('f'); r.tick(4); r.stick('n'); r.tick(4); r.stick('f'); r.tick(80);
  const names = new Set(recs(r).map((x) => x.name));
  assert.ok(names.has('Kg_sWALKF') && names.has('Kg_sDASHF'), [...names].join(','));
  // Heading is resolved throughout (tracked yaw 0, rel 0): no facing condition blocks anything.
  assert.ok(!recs(r).some((x) => x.ambiguous && x.ambiguous.unknown.some((c) => [72, 73, 80, 81].includes(c))), 'no facing block');
  assert.equal(r.f._t7g.evalState.relHeading16, 0);
  // The run is held back by the dash re-fire row 478 (req 1085 = [[124,0]]): cond 124 (exe evaluator 0x1406f5490,
  // case 0x1406f60e4 — true iff a float at [fighter+0x12d0/0x12d4/0x12d8] is nonzero) is undecoded, its field untraced,
  // so it stays unknown and the stopping row blocks the run row 479 at dash frame 12. The dash then falls through
  // to the walk with no stall. The run still fires in PERMISSIVE (mechanics test above).
  const why = new Set(recs(r).filter((x) => x.ambiguous).flatMap((x) => x.ambiguous.unknown));
  assert.ok(why.has(124), `cond 124 blocks the run: ${[...why]}`);
  assert.ok(!recs(r).some((x) => x.stalled), 'no stall: the dash falls through to the walk');
});

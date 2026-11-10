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

function pantera() {
  const f = Object.create(F.Fighter.prototype);
  Object.assign(f, { char: { id: 'pantera' }, _movesetId: 'pantera', t3actions: {}, root: { position: { x: 0, y: 0, z: 0 } },
    facing: 1, dead: false, stun: 0, onGround: true, brawler: false, state: 'idle', stateT: 0, vx: 0, vz: 0, isPlayer: true,
    bones: {}, stats: { reachMult: 1 }, hasHit: false });
  f.tekken = new M.TekkenBuffer('pantera');
  f.t7gAttach(bank);
  return f;
}
// The shared input layer, exactly as the handlers use it (keyboard keydown/keyup and the touch limb buttons now do the
// same thing: held[b] + _tekken(b, t) on press, held[b] = false on release; the stick through _stick8 / stickNeutral).
function rig() {
  const inp = new IN.InputManager(); inp.enabled = true;
  const f = pantera(); let t = 1000; const log = [];
  const tick = (n = 1) => { for (let i = 0; i < n; i++) { t += DT * 1000; GI.feedT7GraphInput(f, inp, DT); if (f._t7gRec) log.push(f._t7gRec); } };
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
  const ev = G.makeEvalCond({ dead: false });
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

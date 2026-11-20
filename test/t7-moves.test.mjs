// Real Tekken 7 per-move clips (2026-10-31): Negativo plays Negan's own T7 attacks. Node, no browser.
// Run: node --test test/t7-moves.test.mjs
// Data: game/assets/anim/t7/negan/moves.pack.json, baked by tools/anim/t7_move_bake.py from the rows
// tools/anim/t7_move_resolve.py maps exactly (input path from Negan's stance through the motbin cancel graph AND
// exact T7 frame data). Checks: well-formed FIGHT-only pack with provenance; frame data preserved; every clip a
// physically plausible move; raw-channel root motion present; wiring (loader, attack plan, retarget through the
// stance skeleton's bind-time rest pose, root motion) and a load through the real module in node.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const src = (f) => readFileSync(join(ROOT, f), 'utf8');
const DIR = 'game/assets/anim/t7/negan/';
const pack = JSON.parse(src(DIR + 'moves.pack.json'));
const skel = JSON.parse(src(DIR + 'skeleton.json'));
const moveset = JSON.parse(src('game/assets/movesets/negativo.json')).moves;
const firstInt = (s) => { const m = String(s ?? '').match(/-?\d+/); return m ? +m[0] : null; };

const qmul = (a, b) => [a[3] * b[0] + a[0] * b[3] + a[1] * b[2] - a[2] * b[1], a[3] * b[1] - a[0] * b[2] + a[1] * b[3] + a[2] * b[0],
  a[3] * b[2] + a[0] * b[1] - a[1] * b[0] + a[2] * b[3], a[3] * b[3] - a[0] * b[0] - a[1] * b[1] - a[2] * b[2]];
const qrot = (q, v) => { const [x, y, z, w] = q, tx = 2 * (y * v[2] - z * v[1]), ty = 2 * (z * v[0] - x * v[2]), tz = 2 * (x * v[1] - y * v[0]);
  return [v[0] + w * tx + (y * tz - z * ty), v[1] + w * ty + (z * tx - x * tz), v[2] + w * tz + (x * ty - y * tx)]; };
const REST = {}, PAR = {};
for (const j of skel.joints) { REST[j.name] = j.rest; PAR[j.name] = j.parent; }
const pose = (clip, f) => {
  const G = {}, X = {};
  for (const j of skel.joints.map(k => k.name)) {
    const q = clip.rot_xyzw[j][f], p = PAR[j];
    if (!p) { G[j] = q; X[j] = clip.root_t[f]; continue; }
    G[j] = qmul(G[p], q);
    const o = qrot(G[p], [REST[j][0] - REST[p][0], REST[j][1] - REST[p][1], REST[j][2] - REST[p][2]]);
    X[j] = [X[p][0] + o[0], X[p][1] + o[1], X[p][2] + o[2]];
  }
  return X;
};

test('moves pack: FIGHT-only, provenance, multi-hit rows kept out', () => {
  assert.equal(pack.format, 'wh-t7-moves/1');
  assert.equal(pack.fighter, 'negativo');
  assert.equal(pack.anim_set, 'FIGHT');
  assert.equal(pack.skeleton, 'skeleton.json');
  assert.ok(Object.keys(pack.moves).length >= 20, `${Object.keys(pack.moves).length} moves`);
  for (const k of ['d/f+1+2__main', '1+2_t7']) assert.match(pack.skipped[k], /multi-hit/, k);
  for (const [cname, c] of Object.entries(pack.clips)) {
    assert.equal(c.format, 'wh-anim/1', cname);
    assert.equal(c.fps, 60, cname);
    assert.equal(c.anim_set, 'FIGHT', cname);
    assert.equal(c.loop, false, cname);
    assert.equal(c.t7_source.format, '0xC8', cname);
    assert.ok(c.fk_selfcheck_max_m <= 1e-5, `${cname} FK ${c.fk_selfcheck_max_m}`);
    assert.equal(c.applier.commit, 'bebb3d8bc5c4c2c58778ac6af4f87f3dc80062b1');
    assert.equal(c.root_motion_fwd_m.length, c.root_t.length, `${cname} root motion per frame`);
    assert.equal(c.root_motion_fwd_m[0], 0, `${cname} root motion starts at 0`);
  }
});

test('every mapped row keeps its exact T7 frame data and plays a real clip', () => {
  for (const [key, m] of Object.entries(pack.moves)) {
    const row = moveset[key];
    assert.ok(row, `${key} is a negativo.json row`);
    assert.ok(row.t7_damage_raw != null, `${key} has T7 frame data`);
    assert.equal(m.active_frames[0], firstInt(row.t7_startup_frames), `${key}: first active frame = T7 startup`);
    assert.ok(pack.clips[m.clip], `${key} -> ${m.clip}`);
    assert.match(m.verified, /input path from Na_sKAM00_ \+ exact T7 frame data/);
    assert.ok(!row.isGrab && !row.throw, `${key} is a strike`);
  }
});

test('every clip is a plausible fight move (feet never under the floor, never upside down)', () => {
  for (const [cname, c] of Object.entries(pack.clips)) {
    for (let f = 0; f < c.root_t.length; f++) {
      const X = pose(c, f);
      const low = Math.min(...Object.values(X).map(p => p[1]));
      assert.ok(low > -0.02, `${cname} f${f}: lowest joint ${low.toFixed(3)}`);
      assert.ok(X.Head[1] > X.Hips[1] - 0.05, `${cname} f${f}: head above hips`);
    }
  }
});

test('wiring: per-fighter loader, t7 pick ahead of bank rows, stance-skeleton retarget, raw root motion', () => {
  const t3 = src('game/js/t3anims.js'), fi = src('game/js/fighter.js');
  const mv = t3.match(/export const T7_MOVES = \{([\s\S]*?)\n\};/);
  assert.ok(mv, 'T7_MOVES');
  assert.match(mv[1], /negativo: \{ bank: 'bryan', dir: 'assets\/anim\/t7\/negan\/' \}/);
  assert.match(t3, /negativo: \{ bank: 'bryan', dir: 'assets\/anim\/t7\/negan\/' \}/, 'stance and moves share the skeleton dir');
  assert.match(t3, /export function t7MoveRetarget\(/);
  assert.match(t3, /if \(model\) \{ const pm = _retargetCache\.get\(model\); if \(!pm \|\| !pm\.get\(t\.skelId\)\) return null; \}/,
    'never retarget a move for a model whose stance rest pose was not captured');
  assert.match(fi, /ensureT7Moves\(this\.char\.id, THREE\)/);
  const plan = fi.slice(fi.indexOf('  _attackClipPlan(move, attackName) {'));
  assert.ok(plan.indexOf('t7MoveClip(') < plan.indexOf('this._resolveStepPlan('), 'T7 pick before step plans and bank rows');
  assert.match(fi, /name\.startsWith\('t7:'\)[\s\S]{0,200}t7MoveRetarget\(/);
  assert.match(fi, /const rt = isT7 \? \(clip && clip\.userData && clip\.userData\.rootMotionT\) : \(raw && raw\.root_t\);/);
});

test('the real loader builds Negan move clips with forward root motion', async () => {
  await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
  const THREE = await import('three');
  const T = await import(join(ROOT, 'game/js/t3anims.js'));
  const r = await T.ensureT7Moves('negativo', THREE);
  assert.ok(r, 'pack loaded');
  const mc = T.t7MoveClip('negativo', 'bryan', 'b+2__main');
  assert.ok(mc && mc.clip, 'b+2 clip');
  assert.equal(mc.name, 't7:b+2__main');
  assert.deepEqual(mc.active, pack.moves['b+2__main'].active_frames);
  const rm = mc.clip.userData.rootMotionT;
  assert.ok(Array.isArray(rm) && rm.length > 2, 'root motion track');
  assert.ok(rm[rm.length - 1][2] > 0.5, `b+2 travels forward (${rm[rm.length - 1][2]} m)`);
  assert.equal(T.t7MoveClip('negativo', 'king', 'b+2__main'), null, 'only on its own bound bank');
  assert.equal(T.t7MoveClip('skull', 'bryan', 'b+2__main'), null, 'never for another fighter on the same bank');
});

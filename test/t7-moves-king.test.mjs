// Real Tekken 7 per-move clips for Pantera <- King (2026-11-01). Node, no browser.
// Run: node --test test/t7-moves-king.test.mjs
// King's attacks are 0x64 (compressed) clips. tools/anim/t7_anim64_to_c8.py converts each one with the game's OWN
// sampler (read from TekkenGame-Win64-Shipping.exe; docs/anim/T7-0x64-FRAME-RESEARCH-2026-10-30.md) into 0xC8 values,
// then tools/anim/t7_move_bake.py bakes it through the same proven 0xC8 path as the stances, for the rows
// tools/anim/t7_move_resolve.py maps exactly (input path from King's stance AND exact T7 frame data).
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const src = (f) => readFileSync(join(ROOT, f), 'utf8');
const DIR = 'game/assets/anim/t7/king/';
const pack = JSON.parse(src(DIR + 'moves.pack.json'));
const skel = JSON.parse(src(DIR + 'skeleton.json'));
const moveset = JSON.parse(src('game/assets/movesets/pantera.json')).moves;
const firstInt = (s) => { const m = String(s ?? '').match(/-?\d+/); return m ? +m[0] : null; };
const EXE_SHA = '7f2b68727023ce9f4554b47f5442dad9dfb38c8a9b778f2aa758469e2c2d60ed';

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

test('King moves pack: FIGHT-only, 0x64 clips converted by the game sampler, FK exact', () => {
  assert.equal(pack.format, 'wh-t7-moves/1');
  assert.equal(pack.fighter, 'pantera');
  assert.equal(pack.anim_set, 'FIGHT');
  assert.equal(pack.skeleton, 'skeleton.json');
  assert.ok(Object.keys(pack.moves).length >= 15, `${Object.keys(pack.moves).length} moves`);
  for (const [cname, c] of Object.entries(pack.clips)) {
    assert.equal(c.format, 'wh-anim/1', cname);
    assert.equal(c.fps, 60, cname);
    assert.equal(c.anim_set, 'FIGHT', cname);
    assert.equal(c.loop, false, cname);
    assert.equal(c.t7_source.format, '0x64', cname);
    assert.equal(c.t7_source.conversion.tool, 'tools/anim/t7_anim64_to_c8.py', cname);
    assert.equal(c.t7_source.conversion.exe_sha256, EXE_SHA, cname);
    assert.ok(c.fk_selfcheck_max_m <= 1e-5, `${cname} FK ${c.fk_selfcheck_max_m}`);
    assert.equal(c.applier.commit, 'bebb3d8bc5c4c2c58778ac6af4f87f3dc80062b1');
    assert.equal(c.root_motion_fwd_m.length, c.root_t.length, `${cname} root motion per frame`);
    assert.equal(c.root_motion_fwd_m[0], 0, `${cname} root motion starts at 0`);
  }
});

test('every mapped King row keeps its exact T7 frame data and plays a real clip', () => {
  for (const [key, m] of Object.entries(pack.moves)) {
    const row = moveset[key];
    assert.ok(row, `${key} is a pantera.json row`);
    assert.ok(row.t7_damage_raw != null, `${key} has T7 frame data`);
    assert.equal(m.active_frames[0], firstInt(row.t7_startup_frames), `${key}: first active frame = T7 startup`);
    assert.ok(pack.clips[m.clip], `${key} -> ${m.clip}`);
    assert.match(m.verified, /input path from Kg_sKAM00_ \+ exact T7 frame data/);
    assert.ok(!row.isGrab && !row.throw, `${key} is a strike`);
  }
});

// King is not Negan: his real moves include a flip kick, a drop kick that ends on the floor and ground elbows, and
// Tekken impacts snap in 1-2 frames (kick 3 chambers the knee to 108 deg on frames 13-15 and extends it fully on
// frame 16; the game's own sampler and the community decoder agree). So the guard is what a broken conversion would
// break: every move starts upright from the stance, contact with the floor stays within mannequin tolerance, and no
// joint jumps more than a limb flip would make it (a 180 deg flip of a thigh moves the foot ~2 leg lengths).
test('every King clip is physically plausible (upright start, floor contact, no limb flips)', () => {
  for (const [cname, c] of Object.entries(pack.clips)) {
    const X0 = pose(c, 0);
    assert.ok(X0.Head[1] > X0.Hips[1] + 0.2, `${cname}: starts upright (head ${(X0.Head[1] - X0.Hips[1]).toFixed(2)} m above hips)`);
    let prev = null;
    for (let f = 0; f < c.root_t.length; f++) {
      const X = pose(c, f);
      const low = Math.min(...Object.values(X).map(p => p[1]));
      assert.ok(low > -0.08, `${cname} f${f}: lowest joint ${low.toFixed(3)}`);
      if (prev) {
        for (const j of Object.keys(X)) {
          if (j === 'Hips') continue;
          const d = Math.hypot(X[j][0] - X.Hips[0] - (prev[j][0] - prev.Hips[0]), X[j][1] - X.Hips[1] - (prev[j][1] - prev.Hips[1]),
            X[j][2] - X.Hips[2] - (prev[j][2] - prev.Hips[2]));
          assert.ok(d < 1.5, `${cname} f${f}: ${j} jumps ${d.toFixed(2)} m in one frame`);
        }
      }
      prev = X;
    }
  }
});

test('wiring: Pantera loads King moves from the stance skeleton dir', () => {
  const t3 = src('game/js/t3anims.js');
  const mv = t3.match(/export const T7_MOVES = \{([\s\S]*?)\n\};/);
  assert.ok(mv, 'T7_MOVES');
  assert.match(mv[1], /pantera: \{ bank: 'king', dir: 'assets\/anim\/t7\/king\/' \}/);
  assert.match(t3, /pantera: \{ bank: 'king', dir: 'assets\/anim\/t7\/king\/' \}/, 'stance and moves share the skeleton dir');
});

test('the real loader builds King move clips for Pantera only', async () => {
  await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
  const THREE = await import('three');
  const T = await import(join(ROOT, 'game/js/t3anims.js'));
  const r = await T.ensureT7Moves('pantera', THREE);
  assert.ok(r, 'pack loaded');
  const key = Object.keys(pack.moves)[0];
  const mc = T.t7MoveClip('pantera', 'king', key);
  assert.ok(mc && mc.clip, `${key} clip`);
  assert.equal(mc.name, 't7:' + key);
  assert.deepEqual(mc.active, pack.moves[key].active_frames);
  assert.ok(Array.isArray(mc.clip.userData.rootMotionT), 'root motion track');
  assert.equal(T.t7MoveClip('pantera', 'bryan', key), null, 'only on its own bound bank');
  assert.equal(T.t7MoveClip('negativo', 'king', key), null, 'never for another fighter');
  // the rows the game actually plays for these inputs (probe 2026-11-01) reach King's T7 clips by their input
  for (const [played, input, packKey] of [['1~t8.king', '1', '1~t7.king'], ['df+1', 'df+1', 'd/f+1~t7.king'],
    ['uf+3', 'uf+3', 'u/f+3~t7.king'], ['f+4', 'f+4', 'f+4~t7.king'], ['b+2', 'b+2', 'b+2~t7.king']]) {
    if (!pack.moves[packKey]) continue;
    const m = T.t7MoveClip('pantera', 'king', played, null, input);
    assert.ok(m, `${played} (${input}) -> ${packKey}`);
    assert.equal(m.name, 't7:' + packKey);
  }
  assert.equal(T.t7MoveClip('pantera', 'king', '1,2', null, '1,2'), null, 'strings never take a single-input clip');
});

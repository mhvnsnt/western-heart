// Root motion (2026-10-24). Node, no browser.
// Run: node --test test/root-motion.test.mjs
// Owner playtest 2026-10-24: "Animations that should make him TRAVEL
// different distances aren't making him move. He's stuck in place,
// fighting kind of stuck." fighter.js had zero rootMotion references:
// attacks decayed vx to ~0 in _physics and the decoded root_t travel
// in every T3 clip was never read horizontally. This test simulates
// attack playback tick-by-tick (60 fps, touch-tick equivalent) through
// the SAME code the game runs (_attackClipPlan + _rootMotionApply)
// on Pantera's real bank, and asserts the distance each move travels.
// LP1/RP2/LK3/RK4 button names per owner directive 2026-10-24.
import test from 'node:test';
import assert from 'node:assert/strict';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const THREE = await import('three');
const M = await import(join(ROOT, 'game/js/movesets.js'));
const T = await import(join(ROOT, 'game/js/t3anims.js'));
const F = await import(join(ROOT, 'game/js/fighter.js'));
const FT = await import(join(ROOT, 'game/js/frame-tables.js'));
// Production determinism: fighter.js reads the T8 frame table (game/data)
// synchronously at plan time, but the table loads async at import. Without
// this await, plans race the fetch — Konvict Kick (tgt '(t)') flips between
// strike (table absent) and throw-class (table present) mid-file. The live
// game boots with the table loaded, so the test awaits it too.
await FT.frameTablesReady;
const quiet = { log: console.log, warn: console.warn };
console.log = () => {}; console.warn = () => {};
await M.loadFighterMovesets();
await M.ensureMovesets(['pantera']);
console.log = quiet.log; console.warn = quiet.warn;

async function fighter() {
  const bank = F.bankIdFor('pantera', 'pantera');
  const save = console.log; console.log = () => {};
  const clips = await T.loadT3Clips(THREE, bank);
  console.log = save;
  const f = Object.create(F.Fighter.prototype);
  f.char = { id: 'pantera' }; f._movesetId = 'pantera'; f.t3actions = {};
  f._t3 = { bank, clips };
  f.root = { position: { x: 0, y: 0, z: 0 } };
  f.facing = 1; f.dead = false; f.stun = 0;
  return f;
}

// Simulate one attack at 60 fps ticks through _rootMotionApply only
// (the position half of _physics; _physics itself adds the same call
// before its arena clamp + pushout — see the wall test below).
function simulate(f, notation, facing = 1) {
  const mv = F.getRealMove('pantera', notation);
  assert.ok(mv, `no move for ${notation}`);
  const plan = f._attackClipPlan(mv, notation);
  assert.ok(plan && plan.name, `${notation}: no clip plan`);
  f.state = 'attack'; f.attackName = notation; f.attack = mv;
  f._attackId = (f._attackId || 0) + 1;
  f._atkPlan = { id: f._attackId, move: mv, name: plan.name, kind: plan.kind, timing: plan.timing };
  f.facing = facing; f._rmPrev = null;
  f.root.position.x = 0; f.root.position.z = 0;
  const total = (mv.startup || 0) + (mv.active || 0) + (mv.recovery || 0);
  const dt = 1 / 60;
  let peakX = 0;
  for (let t = 0; t <= total + 1e-9; t += dt) { f.stateT = t; f._rootMotionApply(); peakX = Math.max(peakX, f.root.position.x); }
  return { plan, mv, x: f.root.position.x, z: f.root.position.z, peakX };
}

test('rootMotionSample: frame-0 baseline, linear interpolation, end clamp', () => {
  const rt = [[0, 1, 0], [0.1, 1, 0.2], [0.2, 1, 0.5]];
  const close = (a, b) => Math.abs(a.fwd - b.fwd) < 1e-9 && Math.abs(a.lat - b.lat) < 1e-9;
  assert.ok(close(F.rootMotionSample(rt, 2, 0), { fwd: 0, lat: 0 }));
  assert.ok(close(F.rootMotionSample(rt, 2, 0.5), { fwd: 0.2, lat: 0.1 }));
  assert.ok(close(F.rootMotionSample(rt, 2, 0.75), { fwd: 0.35, lat: 0.15 }));
  assert.ok(close(F.rootMotionSample(rt, 2, 99), { fwd: 0.5, lat: 0.2 }));
  assert.ok(close(F.rootMotionSample(null, 30, 0.5), { fwd: 0, lat: 0 }));
});

test('Pantera LP1 jab (1) plays row:110 (T3 f+1) and steps forward ~0.11 m', async () => {
  const f = await fighter();
  const r = simulate(f, '1');
  // Row 44 was a jumping-1 clip (feet 0.75/0.78 m off the ground at frame 0),
  // not a standing jab. Row 110 is T3 f+1: a standing armL jab, active 10 =
  // T7 i10. Measured through _rootMotionApply: steps in to a 0.265 m peak
  // and settles at 0.106 m forward, -0.028 m lateral (PR #1022 audit).
  assert.equal(r.plan.name, 'row:110', `LP1 plan: ${r.plan.name} (${r.plan.kind})`);
  assert.ok(r.x > 0.09 && r.x < 0.12, `LP1 travelled ${r.x} m, expected 0.09-0.12`);
  assert.ok(r.z < -0.01 && r.z > -0.05, `LP1 lateral ${r.z} m, expected ~-0.03`);
  assert.ok(r.peakX > 0.25 && r.peakX < 0.28, `LP1 peak ${r.peakX} m, expected 0.25-0.28`);
});

test('Pantera RP2 (2) plays row:99 (T3 b+2) and travels forward ~0.15 m, mirrored when facing left', async () => {
  const f = await fighter();
  const r = simulate(f, '2', 1);
  // Row 203 was a lunging ducking straight (0.95 m travel, hips dipping to
  // 0.61 m), not a jab. Row 99 is T3 b+2: a standing armR jab, active 10 =
  // T7 i10. Measured through _rootMotionApply: 0.151 m forward, -0.138 m
  // lateral, peak 0.301 m (PR #1022 audit).
  assert.equal(r.plan.name, 'row:99', `RP2 plan: ${r.plan.name} (${r.plan.kind})`);
  assert.ok(r.x > 0.13 && r.x < 0.17, `RP2 travelled ${r.x} m, expected 0.13-0.17`);
  assert.ok(r.z < -0.12 && r.z > -0.16, `RP2 lateral ${r.z} m, expected ~-0.14`);
  const m = simulate(f, '2', -1);
  assert.ok(m.x < -0.13 && m.x > -0.17, `RP2 mirrored travelled ${m.x} m`);
});

test('Pantera f,F+2 Beast Elbow (RP2 dash elbow): donor clip row:111 travels forward (0.15 m net, 0.30 m peak)', async () => {
  const f = await fighter();
  const r = simulate(f, 'f,F+2');
  assert.equal(r.plan.name, 'row:111', `Beast Elbow plan: ${r.plan.name} (${r.plan.kind})`);
  assert.equal(r.plan.kind, 'donor', 'Beast Elbow has no own T3 row; the donor is King\'s own f+2 row (same direction + RP2 button)');
  // Decoded row:111 travel (measured from rows.pack.json root_t): forward
  // 0.30 m at peak, settling to 0.15 m at clip end; lateral 0.138 m.
  assert.ok(r.x > 0.13 && r.x < 0.17, `Beast Elbow travelled ${r.x} m, expected 0.13-0.17`);
  assert.ok(r.peakX > 0.28 && r.peakX < 0.32, `Beast Elbow peak ${r.peakX} m, expected 0.28-0.32`);
  assert.ok(r.z < -0.12 && r.z > -0.16, `Beast Elbow lateral ${r.z} m, expected ~-0.14`);
  // Whiff vs hit: root motion never reads hasHit, so both travel identically.
  f.hasHit = true;
  const hit = simulate(f, 'f,F+2');
  assert.ok(Math.abs(hit.x - r.x) < 1e-9, `hit (${hit.x}) != whiff (${r.x})`);
});

test('Pantera f,F+4 Konvict Kick (RK4): donor clip row:114 travels forward ~0.48 m', async () => {
  const f = await fighter();
  const r = simulate(f, 'f,F+4');
  // Konvict Kick has no own T3 row; the donor is King's own f+4 row
  // (same direction + RK4 button). Classification: the hitbox lane
  // (main, 2026-10-24) reads the level from T7 hit_level 'mid' when
  // the move carries no top-level hit_level or decoded hit_words
  // entry, so this is a mid kick, not a throw — the T8 table's tgt
  // '(t)' (throw transition on counter-hit) no longer misclassifies
  // the base kick, because the decoded/T7 level wins first.
  assert.equal(r.plan.name, 'row:114', `Konvict Kick plan: ${r.plan.name} (${r.plan.kind})`);
  assert.equal(r.plan.kind, 'donor', 'Konvict Kick has no own T3 row; the donor is King\'s own f+4 row (same direction + RK4 button)');
  assert.ok(r.x > 0.46 && r.x < 0.50, `Konvict Kick travelled ${r.x} m, expected 0.46-0.50`);
  assert.ok(r.z < -0.20 && r.z > -0.25, `Konvict Kick lateral ${r.z} m, expected ~-0.225`);
});

test('Generic fallback clips get NO root motion (heavy/grab are the row:230 throw-execution clip)', async () => {
  const f = await fighter();
  f.state = 'attack'; f._attackId = 1; f.facing = 1; f.stateT = 0; f._rmPrev = null;
  f._atkPlan = { id: 1, name: 'heavy', kind: 'generic', timing: null };
  f.root.position.x = 0; f.root.position.z = 0;
  for (let t = 0; t <= 1; t += 1 / 60) { f.stateT = t; f._rootMotionApply(); }
  assert.equal(f.root.position.x, 0);
  assert.equal(f.root.position.z, 0);
});

test('Root motion never runs outside attack/vskill/vreversal (block, sidestep)', async () => {
  const f = await fighter();
  const mv = F.getRealMove('pantera', '2');
  const plan = f._attackClipPlan(mv, '2');
  f._attackId = 1; f.facing = 1; f.stateT = 0.5;
  f._atkPlan = { id: 1, move: mv, name: plan.name, kind: plan.kind, timing: plan.timing };
  for (const st of ['block', 'sidestep', 'idle', 'jump']) {
    f.state = st; f._rmPrev = null; f.root.position.x = 0; f.root.position.z = 0;
    f._rootMotionApply();
    assert.equal(f.root.position.x, 0, `${st}: root motion applied`);
    assert.equal(f._rmPrev, null, `${st}: cursor not reset`);
  }
});

test('Wall: _physics clamps root-motion travel to ARENA_LIMIT (8.4) instead of leaving the stage', async () => {
  const f = await fighter();
  const mv = F.getRealMove('pantera', '2');
  const plan = f._attackClipPlan(mv, '2');
  f.state = 'attack'; f.attackName = '2'; f.attack = mv;
  f._attackId = 1; f.facing = 1; f._rmPrev = null;
  f._atkPlan = { id: 1, move: mv, name: plan.name, kind: plan.kind, timing: plan.timing };
  f.vx = 0; f.vy = 0; f.vz = 0; f.onGround = true;
  f.root.position.x = 8.3; f.root.position.y = 0; f.root.position.z = 0;
  f.blob = { position: { y: 0 }, scale: { set() {} }, material: { opacity: 0 } };
  const total = (mv.startup || 0) + (mv.active || 0) + (mv.recovery || 0);
  let peakX = 8.3;
  for (let t = 0; t <= total + 1e-9; t += 1 / 60) { f.stateT = t; f._physics(1 / 60, null); peakX = Math.max(peakX, f.root.position.x); }
  assert.ok(f.root.position.x <= 8.4 + 1e-9, `wall: x=${f.root.position.x}`);
  // Row 99 (T3 b+2, PR #1022) peaks at 0.300 m mid-clip then settles to
  // 0.151 m; at the wall the clamp discards the overshoot above 8.4, so the
  // clip's natural settle-back lands at 8.4 - (0.300 - 0.151) = 8.251 —
  // inside the stage, not lost. The old x >= 8.3 assertion assumed row 203's
  // monotonic 0.85 m travel and is wrong for a peak-and-settle clip.
  assert.ok(peakX > 8.39, `wall: peak x=${peakX} (clamp never engaged)`);
  assert.ok(f.root.position.x > 8.24 && f.root.position.x < 8.26, `wall: x=${f.root.position.x}, expected 8.24-8.26`);
});

test('Fixed bank (bosconovitch, #497 baked facing +Z at source): no runtime flip, root motion reads the canonical frame', async () => {
  const save = console.log; console.log = () => {};
  const clips = await T.loadT3Clips(THREE, 'bosconovitch');
  console.log = save;
  assert.ok(clips && clips['row:4'], 'bosconovitch row:4 loaded');
  const facing = T.getT3BankFacing('bosconovitch');
  // PR #497 fixed the bank AT THE SOURCE (skeleton + rows re-baked 180 deg
  // about Y, Left/Right relabelled), so the runtime detector must NOT flag
  // it turned anymore — the 180 deg root_t flip in loadT3Clips is now a
  // no-op for this bank. (Before #497 the bank was baked facing -Z and the
  // test asserted turned=true; that premise is obsolete.)
  assert.ok(facing && !facing.turned, `bosconovitch still flagged turned after #497: ${JSON.stringify(facing)}`);
  // On disk, row:4 now ends at (x -0.325, z -0.802) — pre-flipped by the
  // #497 re-bake. No runtime flip is applied, so root motion reads the
  // same canonical frame (+Z forward, +X left) as every bank.
  const rt = clips['row:4'].userData.raw.root_t;
  const s = F.rootMotionSample(rt, 30, 99);
  assert.ok(Math.abs(s.fwd - (-0.802)) < 0.01, `bosconovitch row:4 fwd ${s.fwd}, expected -0.802`);
  assert.ok(Math.abs(s.lat - (-0.325)) < 0.01, `bosconovitch row:4 lat ${s.lat}, expected -0.325`);
});

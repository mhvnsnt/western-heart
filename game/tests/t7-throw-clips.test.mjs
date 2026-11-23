/* t7-throw-clips.test.mjs — T7 throw-pair wiring guard (Lane E, 2026-11-21).
 *
 * WHAT THIS GUARDS: game/js/t7-throw-clips.js is the single source of
 * truth for Pantera's real T7 throw pair — the roles were WRONG until
 * 2026-11-21 (the `_n` throw motions were labelled the victim and the
 * victim's `_y` receivers were missing entirely). A regression here
 * silently plays the thrower's motion on the victim (upside down,
 * feet 2 m up) or drops the receiver back to the T3 fallback.
 *
 * COVERAGE:
 *   - table roles: grab = 40f attempt, throwMotion = `_n` throw
 *     motion, victim = `_y` fixed receiver, hold = move 554
 *   - damages are the property-33307 set (2135=40, 2274=30 — the
 *     old table had both as 0)
 *   - resolvers return null on unknown input/situation (never invent)
 *   - quadrant gate stays front/back only (side mapping unproven,
 *     air has no signal) even though the side/air data is complete
 *   - receiver resolver: front/side breakable to Esc_* in the real
 *     windows; back/air UNBREAKABLE (zero cancel rows in the file)
 *   - validateT7ThrowClip accepts every real clip the table names,
 *     and throws/index.json agrees with the table + the files
 *     (frames, bytes, sha256) — no stale manifest
 *   - king-throw-triple.json receiver is RESOLVED (2126/2130)
 *   - FK shape at f0 (skeleton.json): front receivers upright with
 *     feet on the floor; the hold dangles (feet ~0.33 m, held pose)
 *
 * Run: node --test game/tests/t7-throw-clips.test.mjs (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import {
  T7_THROW_PAIRS,
  resolveT7ThrowPair,
  resolveT7ThrowReceiver,
  t7SituationForQuadrant,
  validateT7ThrowClip,
} from '../js/t7-throw-clips.js';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..'); // game/tests -> repo root
const throwsDir = join(root, 'game/assets/anim/t7/king/throws');
const readClip = (key) => JSON.parse(readFileSync(join(throwsDir, `${key}.json`), 'utf8'));
const index = JSON.parse(readFileSync(join(throwsDir, 'index.json'), 'utf8'));
const triple = JSON.parse(readFileSync(join(root, 'tools/anim/tkmovesets2/king-throw-triple.json'), 'utf8'));

/** Every clip key the table names (grab + throwMotion + hold + victim + escapes). */
function allTableKeys() {
  const keys = [];
  for (const p of Object.values(T7_THROW_PAIRS)) {
    keys.push(p.grab.key, p.hold.key);
    for (const c of Object.values(p.throwMotion)) keys.push(c.key);
    for (const v of Object.values(p.victim)) {
      keys.push(v.key);
      if (v.escape) keys.push(v.escape.key);
    }
  }
  return [...new Set(keys)];
}

test('roles: grab is the 40f attempt, throwMotion is the _n motion, victim is the _y fixed receiver', () => {
  const p13 = resolveT7ThrowPair('1+3', 'front');
  assert.equal(p13.grab.key, 'common_709');
  assert.equal(p13.grab.move, 1785);
  assert.equal(p13.grab.frames, 40);
  assert.equal(p13.thrower.key, 'rotsm_574');
  assert.equal(p13.thrower.move, 2125);
  assert.equal(p13.victim.key, 'rotsm_575-fixed');
  assert.equal(p13.victim.move, 2126);
  assert.equal(p13.hold.key, 'hold_554');
  assert.equal(p13.hold.move, 554);
  const p24 = resolveT7ThrowPair('2+4', 'front');
  assert.equal(p24.grab.key, 'rotsm_534');
  assert.equal(p24.thrower.key, 'rotsm_578');
  assert.equal(p24.thrower.move, 2129);
  assert.equal(p24.victim.key, 'rotsm_579-fixed');
  assert.equal(p24.victim.move, 2130);
  // No table entry still calls a _n motion the victim.
  for (const p of Object.values(T7_THROW_PAIRS)) {
    for (const v of Object.values(p.victim)) assert.ok(v.key.endsWith('-fixed'), `${v.key} is not a fixed receiver`);
    for (const t of Object.values(p.throwMotion)) assert.ok(!t.key.endsWith('-fixed'), `${t.key} is not a throw motion`);
  }
});

test('damages are the property-33307 set (2135=40, 2274=30 — the old table had both as 0)', () => {
  const dmg = {};
  for (const p of Object.values(T7_THROW_PAIRS)) {
    for (const t of Object.values(p.throwMotion)) dmg[t.move] = t.damage;
  }
  assert.deepEqual(dmg, { 2125: 35, 2129: 35, 2135: 40, 2137: 42, 2139: 60, 2141: 60, 2274: 30, 2276: 30 });
});

test('resolvers return null on unknown input/situation — never invent', () => {
  assert.equal(resolveT7ThrowPair('1+2'), null);
  assert.equal(resolveT7ThrowPair('1+3', 'crouch'), null);
  assert.equal(resolveT7ThrowPair('1+3', 'ground'), null);
  assert.equal(resolveT7ThrowReceiver('2+4', 'crouch'), null);
  assert.equal(resolveT7ThrowReceiver('1+2'), null);
});

test('quadrant gate stays front/back only (side mapping unproven, air has no signal)', () => {
  assert.equal(t7SituationForQuadrant(0), 'front');
  assert.equal(t7SituationForQuadrant(2), 'back');
  assert.equal(t7SituationForQuadrant(1), null);
  assert.equal(t7SituationForQuadrant(3), null);
  // ...even though the side/air DATA is complete in the table.
  assert.equal(resolveT7ThrowPair('1+3', 'left').victim.key, 'rotsm_589-fixed');
  assert.equal(resolveT7ThrowPair('1+3', 'air').victim.key, 'rotsm_719-fixed');
  assert.equal(resolveT7ThrowPair('2+4', 'air').victim.key, 'rotsm_717-fixed');
});

test('receiver resolver: front/side breakable to Esc_* in the real windows; back/air unbreakable', () => {
  const f13 = resolveT7ThrowReceiver('1+3', 'front');
  assert.equal(f13.hold.move, 554);
  assert.equal(f13.receiver.key, 'rotsm_575-fixed');
  assert.deepEqual(f13.breakWindowFrames, [1, 15]);
  assert.equal(f13.breakStartFrame, 15);
  assert.equal(f13.escape.key, 'esc_2127');
  const f24 = resolveT7ThrowReceiver('2+4', 'front');
  assert.equal(f24.escape.key, 'esc_2133');
  assert.deepEqual(f24.breakWindowFrames, [1, 15]);
  const left = resolveT7ThrowReceiver('1+3', 'left');
  assert.deepEqual(left.breakWindowFrames, [1, 10]);
  assert.equal(left.breakStartFrame, 1);
  assert.equal(left.escape.key, 'esc_237');
  const right = resolveT7ThrowReceiver('2+4', 'right');
  assert.equal(right.escape.key, 'esc_239');
  // Back and air have ZERO cancel rows in the real file — unbreakable.
  for (const [input, situation] of [['1+3', 'back'], ['2+4', 'back'], ['1+3', 'air'], ['2+4', 'air']]) {
    const r = resolveT7ThrowReceiver(input, situation);
    assert.equal(r.breakWindowFrames, null, `${input} ${situation} must have no break window`);
    assert.equal(r.breakStartFrame, null);
    assert.equal(r.escape, null);
  }
  // The hold itself breaks to 1423 (Kg_sKAM00_, 60f).
  assert.equal(T7_THROW_PAIRS['1+3'].hold.breaksTo, 1423);
  assert.deepEqual(T7_THROW_PAIRS['1+3'].hold.breakWindowFrames, [1, 2]);
});

test('validateT7ThrowClip accepts every real clip the table names, and the index agrees with the files', () => {
  const keys = allTableKeys();
  assert.ok(keys.length >= 20, `expected >= 20 table keys, got ${keys.length}`);
  for (const key of keys) {
    const rec = readClip(key);
    const v = validateT7ThrowClip(key, rec);
    assert.ok(v.ok, `${key}: ${v.errors.join('; ')}`);
    const entry = index.clips[key];
    assert.ok(entry, `${key} missing from throws/index.json`);
    assert.equal(entry.frames, rec.root_t.length, `${key} index frames != file`);
    const bytes = readFileSync(join(throwsDir, `${key}.json`));
    assert.equal(entry.bytes, bytes.length, `${key} index bytes != file`);
    assert.equal(entry.sha256, createHash('sha256').update(bytes).digest('hex'), `${key} index sha256 != file`);
  }
  // No _n clip is still labelled victim in the index.
  for (const k of ['rotsm_574', 'rotsm_578', 'rotsm_588', 'rotsm_590', 'rotsm_592', 'rotsm_594', 'rotsm_716', 'rotsm_718']) {
    assert.equal(index.clips[k].role, 'thrower', `${k} index role is not thrower`);
  }
  assert.equal(index.total_bytes, Object.values(index.clips).reduce((a, c) => a + c.bytes, 0));
});

test('king-throw-triple.json receiver is RESOLVED with the corrected damages', () => {
  const byInput = Object.fromEntries(triple.throws.map((t) => [t.input, t]));
  assert.equal(byInput['1+3'].receiver.status, 'RESOLVED');
  assert.equal(byInput['1+3'].receiver.move_id, 2126);
  assert.equal(byInput['1+3'].receiver.clip, 'rotsm_575-fixed');
  assert.equal(byInput['2+4'].receiver.move_id, 2130);
  assert.equal(byInput['2+4'].receiver.clip, 'rotsm_579-fixed');
  assert.equal(byInput['1+3'].receiver.hold.move_id, 554);
  assert.equal(byInput['1+3'].receiver.break.escape_move_id, 2127);
  assert.equal(byInput['2+4'].receiver.break.escape_move_id, 2133);
  assert.equal(byInput['1+3'].throw_motion.left.damage, 40);
  assert.equal(byInput['2+4'].throw_motion.left.damage, 40);
  assert.equal(byInput['2+4'].throw_motion.air_forward_face_up.damage, 30);
  assert.equal(triple.repo_label_correction.status.startsWith('MADE'), true);
});

/* ---- FK shape at f0 (spine-identity torso pitch, feet/head Y) ---- */
function qmul(a, b) {
  const [ax, ay, az, aw] = a, [bx, by, bz, bw] = b;
  return [ax * bw + aw * bx + ay * bz - az * by, ay * bw + aw * by + az * bx - ax * bz, az * bw + aw * bz + ax * by - ay * bx, aw * bw - ax * bx - ay * by - az * bz];
}
function qrot(q, v) {
  const [x, y, z, w] = q;
  const tx = 2 * (y * v[2] - z * v[1]), ty = 2 * (z * v[0] - x * v[2]), tz = 2 * (x * v[1] - y * v[0]);
  return [v[0] + w * tx + (y * tz - z * ty), v[1] + w * ty + (z * tx - x * tz), v[2] + w * tz + (x * ty - y * tx)];
}
const skel = JSON.parse(readFileSync(join(root, 'game/assets/anim/t7/king/skeleton.json'), 'utf8'));
const REST = Object.fromEntries(skel.joints.map((j) => [j.name, j.rest]));
const PARENT = Object.fromEntries(skel.joints.map((j) => [j.name, j.parent]));
const ORDER = skel.joints.map((j) => j.name);
function f0Pose(rec) {
  const G = {}, X = {};
  for (const j of ORDER) {
    let q = rec.rot_xyzw[j][0];
    if (j === 'Spine') q = [0, 0, 0, 1]; // spine-identity: the approximate Spine must not drive the shape gate
    const p = PARENT[j];
    if (p && p in G) { G[j] = qmul(G[p], q); X[j] = X[p].map((v, i) => v + qrot(G[p], REST[j].map((r, k) => r - REST[p][k]))[i]); }
    else { G[j] = q; X[j] = [...REST[j]]; }
  }
  const rt = rec.root_t[0];
  const W = Object.fromEntries(ORDER.map((j) => [j, X[j].map((v, i) => v - REST[skel.root][i] + rt[i])]));
  const t = [W.Head[0] - W.Hips[0], W.Head[1] - W.Hips[1], W.Head[2] - W.Hips[2]];
  const len = Math.hypot(...t);
  const pitch = Math.acos(Math.max(-1, Math.min(1, t[1] / len))) * 180 / Math.PI;
  return { pitch, headY: W.Head[1], hipsY: W.Hips[1], feetY: Math.min(W.LeftFoot[1], W.RightFoot[1]) };
}

test('FK f0 shape: front receivers upright with feet on the floor; the hold dangles', () => {
  for (const key of ['rotsm_575-fixed', 'rotsm_579-fixed']) {
    const { pitch, headY, hipsY, feetY } = f0Pose(readClip(key));
    assert.ok(feetY < 0.2, `${key} f0 feet ${feetY.toFixed(2)} m — not on the floor`);
    assert.ok(headY > 1.4, `${key} f0 head ${headY.toFixed(2)} m — not upright`);
    assert.ok(headY > hipsY, `${key} f0 head below hips`);
    assert.ok(pitch < 20, `${key} f0 spine-identity pitch ${pitch.toFixed(1)} deg — still flipped`);
  }
  const hold = f0Pose(readClip('hold_554'));
  assert.ok(hold.feetY > 0.2 && hold.feetY < 0.45, `hold_554 f0 feet ${hold.feetY.toFixed(2)} m — not the dangling held pose`);
  assert.ok(hold.headY > hold.hipsY, 'hold_554 f0 head below hips');
  assert.ok(hold.pitch < 40, `hold_554 f0 pitch ${hold.pitch.toFixed(1)} deg — not a held lean`);
});

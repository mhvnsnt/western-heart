// Pantera T7 throw clips: standalone wh-anim/1 files + resolver (Lane 3, 2026-11-20).
// Node only: no browser, no THREE, no model proof. Run: node --test test/t7-throw-clips.test.mjs
// Proves the extracted clips are the real T7 motion from the graph bank (byte
// provenance via throws/index.json), decode clean, and shaped like the
// verified source: throwers stay on their feet (chest-up ~33.5 deg Suplex /
// ~38.7 deg Winding Nut, never horizontal); front victims go inverted.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const KING = join(ROOT, 'game/assets/anim/t7/king');
const THROWS = join(KING, 'throws');
const M = await import(join(ROOT, 'game/js/t7-throw-clips.js'));

const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');
const readJson = (p) => JSON.parse(readFileSync(p, 'utf8'));
const manifest = readJson(join(THROWS, 'index.json'));
const skel = readJson(join(KING, 'skeleton.json'));

// ---- FK (same math as tools/anim/t3_bank_facing.py + Lane M probe) ----
const qmul = (a, b) => [a[3] * b[0] + a[0] * b[3] + a[1] * b[2] - a[2] * b[1],
  a[3] * b[1] - a[0] * b[2] + a[1] * b[3] + a[2] * b[0],
  a[3] * b[2] + a[0] * b[1] - a[1] * b[0] + a[2] * b[3],
  a[3] * b[3] - a[0] * b[0] - a[1] * b[1] - a[2] * b[2]];
const qrot = (q, v) => { const [x, y, z, w] = q; const tx = 2 * (y * v[2] - z * v[1]), ty = 2 * (z * v[0] - x * v[2]), tz = 2 * (x * v[1] - y * v[0]); return [v[0] + w * tx + (y * tz - z * ty), v[1] + w * ty + (z * tx - x * tz), v[2] + w * tz + (x * ty - y * tx)]; };
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const norm = (a) => { const l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
const deg = (r) => r * 180 / Math.PI;
const P = {}, par = {}, order = skel.joints.map((j) => j.name);
for (const j of skel.joints) { P[j.name] = j.rest; par[j.name] = j.parent; }
function fkShape(rec) {
  let maxPitch = 0, maxPitchF = -1, maxChestUp = 0, maxChestUpF = -1;
  const n = rec.root_t.length;
  for (let f = 0; f < n; f++) {
    const G = {}, X = {};
    for (const j of order) {
      const arr = rec.rot_xyzw[j];
      const q = arr && arr.length ? arr[Math.min(f, arr.length - 1)] : [0, 0, 0, 1];
      const p = par[j];
      if (p && G[p]) { G[j] = qmul(G[p], q); const o = qrot(G[p], [P[j][0] - P[p][0], P[j][1] - P[p][1], P[j][2] - P[p][2]]); X[j] = [X[p][0] + o[0], X[p][1] + o[1], X[p][2] + o[2]]; }
      else { G[j] = q; X[j] = P[j].slice(); }
    }
    const torso = norm(sub(X.Head, X.Hips));
    const pitch = deg(Math.acos(Math.max(-1, Math.min(1, torso[1]))));
    if (pitch > maxPitch) { maxPitch = pitch; maxPitchF = f; }
    const cu = deg(Math.acos(Math.max(-1, Math.min(1, qrot(G.Chest, [0, 1, 0])[1]))));
    if (cu > maxChestUp) { maxChestUp = cu; maxChestUpF = f; }
  }
  const ys = rec.root_t.map((t) => t[1]);
  return { n, maxPitch, maxPitchF, maxChestUp, maxChestUpF, rootYmin: Math.min(...ys), rootYmax: Math.max(...ys) };
}

const ALL_KEYS = Object.values(M.T7_THROW_PAIRS).flatMap((p) => [p.thrower.key, ...Object.values(p.victim).map((v) => v.key)]);
const UNIQUE_KEYS = [...new Set(ALL_KEYS)];

test('manifest: format + provenance hashes tie the clips to the shipped graph bank', () => {
  assert.equal(manifest.format, 'wh-t7-throw-clips/1');
  assert.equal(manifest.fighter, 'pantera');
  assert.equal(manifest.graph_sha256, sha256(readFileSync(join(KING, 'graph.json'))));
  assert.equal(manifest.bank_index_sha256, sha256(readFileSync(join(KING, 'graph-clips/index.json'))));
  assert.equal(Object.keys(manifest.clips).length, UNIQUE_KEYS.length);
  for (const k of UNIQUE_KEYS) assert.ok(manifest.clips[k], `manifest missing ${k}`);
});

test('standalone files: every table clip exists, parses, validates, matches the manifest', () => {
  for (const k of UNIQUE_KEYS) {
    const buf = readFileSync(join(THROWS, `${k}.json`));
    const rec = JSON.parse(buf.toString('utf8'));
    const v = M.validateT7ThrowClip(k, rec);
    assert.ok(v.ok, `${k}: ${v.errors.join('; ')}`);
    assert.equal(sha256(buf), manifest.clips[k].sha256, `${k}: sha256 mismatch vs manifest`);
    assert.equal(buf.length, manifest.clips[k].bytes, `${k}: byte size mismatch vs manifest`);
    assert.equal(rec.root_t.length, manifest.clips[k].frames, `${k}: frames mismatch vs manifest`);
    assert.equal(rec.format, 'wh-anim/1');
    assert.equal(rec.fps, 60);
  }
});

test('thrower shape (FK): Suplex chest-up ~33.5 deg, Winding Nut ~38.7 deg, never horizontal, root stays up', () => {
  const s534 = fkShape(readJson(join(THROWS, 'rotsm_534.json')));
  assert.equal(s534.n, 40);
  assert.ok(Math.abs(s534.maxChestUp - 33.5) < 0.6, `rotsm_534 chest-up max ${s534.maxChestUp.toFixed(1)} != 33.5`);
  assert.equal(s534.maxChestUpF, 17);
  assert.ok(s534.maxPitch < 45, `rotsm_534 torso pitch max ${s534.maxPitch.toFixed(1)} >= 45 (horizontal)`);
  assert.ok(s534.rootYmin >= 0.99, `rotsm_534 rootY min ${s534.rootYmin}`);
  const s709 = fkShape(readJson(join(THROWS, 'common_709.json')));
  assert.equal(s709.n, 40);
  assert.ok(Math.abs(s709.maxChestUp - 38.7) < 0.6, `common_709 chest-up max ${s709.maxChestUp.toFixed(1)} != 38.7`);
  assert.ok(s709.maxPitch < 45, `common_709 torso pitch max ${s709.maxPitch.toFixed(1)} >= 45 (horizontal)`);
  assert.ok(s709.rootYmin >= 0.98, `common_709 rootY min ${s709.rootYmin}`);
});

test('victim shape (FK): front victims go inverted, as a thrown victim should', () => {
  for (const [key, wantPitch] of [['rotsm_574', 116.3], ['rotsm_578', 108.6]]) {
    const s = fkShape(readJson(join(THROWS, `${key}.json`)));
    assert.ok(s.maxPitch > 90, `${key} torso pitch max ${s.maxPitch.toFixed(1)} <= 90 (victim never goes over)`);
    assert.ok(Math.abs(s.maxPitch - wantPitch) < 1.0, `${key} pitch max ${s.maxPitch.toFixed(1)} != ${wantPitch}`);
    assert.ok(s.rootYmin < 0.2, `${key} rootY min ${s.rootYmin} (victim never reaches the floor)`);
  }
});

test('resolver: both throws resolve in all five situations; unknown input/situation -> null', () => {
  const p13 = M.resolveT7ThrowPair('1+3', 'front');
  assert.equal(p13.thrower.key, 'common_709');
  assert.equal(p13.victim.key, 'rotsm_574');
  assert.equal(p13.thrower.move, 1785);
  assert.equal(p13.victim.move, 2125);
  const p24 = M.resolveT7ThrowPair('2+4', 'front');
  assert.equal(p24.thrower.key, 'rotsm_534');
  assert.equal(p24.victim.key, 'rotsm_578');
  assert.equal(p24.thrower.move, 1787);
  assert.equal(p24.victim.move, 2129);
  assert.equal(M.resolveT7ThrowPair('1+3').victim.key, 'rotsm_574'); // default situation is front
  for (const input of ['1+3', '2+4']) {
    for (const sit of M.T7_THROW_SITUATIONS) {
      const r = M.resolveT7ThrowPair(input, sit);
      assert.ok(r, `${input}/${sit} did not resolve`);
      assert.equal(r.situation, sit);
    }
  }
  assert.equal(M.resolveT7ThrowPair('1+3', 'left').victim.key, 'rotsm_588');
  assert.equal(M.resolveT7ThrowPair('2+4', 'back').victim.key, 'rotsm_594');
  assert.equal(M.resolveT7ThrowPair('2+4', 'air').victim.key, 'rotsm_716');
  assert.equal(M.resolveT7ThrowPair('1+2', 'front'), null);
  assert.equal(M.resolveT7ThrowPair('1+3', 'sideways'), null);
  assert.equal(M.resolveT7ThrowPair('', 'front'), null);
  assert.equal(M.resolveT7ThrowPair(null), null);
});

test('loader: stub fetch loads both records of a pair; missing/invalid -> null (T3 fallback contract)', async () => {
  const stubFetch = async (path) => ({ ok: true, json: async () => readJson(join(ROOT, 'game', path)) });
  const pair = await M.loadT7ThrowPair('2+4', 'front', stubFetch);
  assert.ok(pair);
  assert.equal(pair.throwerRecord.root_t.length, 40);
  assert.equal(pair.victimRecord.root_t.length, 138);
  const failFetch = async () => ({ ok: false, json: async () => null });
  // '1+3' front (common_709 + rotsm_574) has not been cached yet, so the
  // failing fetch is really exercised here — not the cache.
  assert.equal(await M.loadT7ThrowPair('1+3', 'front', failFetch), null);
  assert.equal(await M.loadT7ThrowClip('rotsm_99999', stubFetch), null);
  // rotsm_590 has not been cached yet either, so the bad record is really validated.
  const badFetch = async () => ({ ok: true, json: async () => ({ format: 'nope' }) });
  assert.equal(await M.loadT7ThrowClip('rotsm_590', badFetch), null);
});

test('validator: rejects bad records instead of passing them through', () => {
  const good = readJson(join(THROWS, 'rotsm_534.json'));
  assert.ok(M.validateT7ThrowClip('rotsm_534', good).ok);
  const nan = JSON.parse(JSON.stringify(good));
  nan.rot_xyzw.Hips[0] = [0, 0, 0, NaN];
  assert.ok(!M.validateT7ThrowClip('rotsm_534', nan).ok);
  const wrongFrames = JSON.parse(JSON.stringify(good));
  wrongFrames.root_t = wrongFrames.root_t.slice(0, 39);
  assert.ok(!M.validateT7ThrowClip('rotsm_534', wrongFrames).ok);
  assert.ok(!M.validateT7ThrowClip('rotsm_534', null).ok);
  assert.ok(!M.validateT7ThrowClip('rotsm_534', { format: 'wh-anim/1' }).ok);
});

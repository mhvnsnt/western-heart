// dw-retarget.test.mjs — Devil Within retarget pilot tests.
// Verifies the baked DW bank (wh-dw-moves/1) and the DW wiring in t3anims.js
// / fighter.js: the bank loads, the skeleton is the 21-joint canonical rig
// facing +Z with left at +X, the pilot moves resolve, and the DW retarget
// functions exist and behave (beam / throws / byInput fallback / nulls).
// Run: node --test game/tests/dw-retarget.test.mjs
// The test imports the REAL t3anims.js (Node-safe: it only imports
// anim-gate.js + asset-config.js) with fetch stubbed to the on-disk bank,
// and a minimal THREE stub (QuaternionKeyframeTrack + AnimationClip) for
// jsonToClip. fighter.js is checked at source level (it is not Node-safe).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '..', '..');
const BANK_DIR = path.join(REPO, 'game', 'assets', 'anim', 'dw');

// Minimal THREE stub: only what jsonToClip needs.
const THREE = {
  QuaternionKeyframeTrack: class {
    constructor(name, times, values) { this.name = name; this.times = times; this.values = values; }
  },
  VectorKeyframeTrack: class {
    constructor(name, times, values) { this.name = name; this.times = times; this.values = values; }
  },
  AnimationClip: class {
    constructor(name, duration, tracks) {
      this.name = name; this.duration = duration; this.tracks = tracks;
      this.userData = {};
    }
  },
};

function readJson(p) { return JSON.parse(fs.readFileSync(p, 'utf8')); }

test('DW bank files exist on disk', () => {
  for (const f of ['skeleton.json', 'moves.pantera.pack.json', 'DW-BAKE-LOG.md']) {
    assert.ok(fs.existsSync(path.join(BANK_DIR, f)), `missing ${f}`);
  }
});

test('DW skeleton is the 21-joint canonical rig, faces +Z, left at +X', () => {
  const skel = readJson(path.join(BANK_DIR, 'skeleton.json'));
  assert.equal(skel.format, 'wh-anim-skel/1');
  assert.equal(skel.root, 'Hips');
  assert.equal(skel.joints.length, 21);
  const byName = Object.fromEntries(skel.joints.map(j => [j.name, j]));
  // Canonical parents.
  assert.equal(byName.Spine.parent, 'Hips');
  assert.equal(byName.Chest.parent, 'Spine');
  assert.equal(byName.Head.parent, 'Neck');
  assert.equal(byName.LeftFoot.parent, 'LeftLeg');
  assert.equal(byName.RightToeBase.parent, 'RightFoot');
  // Faces +Z, left at +X (the DW guard-stance rest: shoulders/feet split in X).
  assert.ok(byName.LeftShoulder.rest[0] > 0, 'LeftShoulder must be at +X');
  assert.ok(byName.RightShoulder.rest[0] < 0, 'RightShoulder must be at -X');
  assert.ok(byName.LeftFoot.rest[0] > 0, 'LeftFoot must be at +X');
  assert.ok(byName.RightFoot.rest[0] < 0, 'RightFoot must be at -X');
  // Hips height is the reference guard-stance height.
  assert.ok(skel.root_rest_y > 0.5 && skel.root_rest_y < 1.2, `root_rest_y ${skel.root_rest_y} out of range`);
});

test('DW pack format, moves, and clip shapes', () => {
  const pack = readJson(path.join(BANK_DIR, 'moves.pantera.pack.json'));
  const curves = readJson(path.join(REPO, 'teardown', 'tekken5', 'dw-motion-curves.json'));
  const bySrc = Object.fromEntries(curves.clips.map(c => [c.source_file, c]));
  assert.equal(pack.format, 'wh-dw-moves/1');
  assert.equal(pack.fighter, 'pantera');
  // The four pilot moves.
  for (const key of ['surge', 'surge-trigger', '1+3', '2+4']) {
    assert.ok(pack.moves[key], `missing move ${key}`);
    assert.equal(pack.moves[key].active_frames, null, `${key} active_frames must be an honest null`);
  }
  // Kit-pack mapping (follow-ups, 2026-11-08): every clip is a move now —
  // skipped is empty. The four nage clips are the mapped moves
  // surge:b-nage-f/y and surge:ppp-nage-f/y; the 46 remaining Surge Kit
  // clips are mapped moves too (see game/assets/anim/dw/DW-MOVE-MAP-LOG.md).
  assert.equal(pack.skipped.length, 0);
  assert.equal(Object.keys(pack.moves).length, 54);
  for (const key of ['surge:b-nage-f', 'surge:b-nage-y', 'surge:ppp-nage-f', 'surge:ppp-nage-y']) {
    assert.ok(pack.moves[key], `missing mapped nage move ${key}`);
  }
  // Every clip: 21 bones, fps follows the source step (60 for step-1,
  // 30 for step-2), rot lengths == root_t lengths, unit quats.
  for (const [cname, c] of Object.entries(pack.clips)) {
    assert.equal(c.format, 'wh-anim/1');
    assert.equal(c.bones.length, 21, `${cname} must have 21 bones`);
    assert.equal(c.fps, bySrc[c.dw_source].step === 1 ? 60 : 30, `${cname} fps must follow step`);
    assert.equal(c.root_t.length, c.rot_xyzw[c.bones[0]].length, `${cname} rot/root_t length mismatch`);
    for (const b of c.bones) {
      assert.equal(c.rot_xyzw[b].length, c.root_t.length, `${cname}:${b} length mismatch`);
      for (const q of c.rot_xyzw[b]) {
        const n = Math.sqrt(q[0] ** 2 + q[1] ** 2 + q[2] ** 2 + q[3] ** 2);
        assert.ok(Math.abs(n - 1) < 1e-4, `${cname}:${b} quat not unit (${n})`);
      }
    }
    // root_t Y (hips height) stays in the measured band for DW motion:
    // min 0.109 m (a throw low point) to max 8.000 m (the flying boss's
    // fire attack, kob2_fly2fire). The band catches unit/sign errors,
    // not jumps — DW motion includes real leaps and a flying boss.
    for (const r of c.root_t) assert.ok(r[1] > 0.05 && r[1] < 8.5, `${cname} root_t Y ${r[1]} out of range`);
  }
  // Durations are keyframe counts: dwhadoh00 23/30 s, ozhe_power 23/30 s
  // (the trigger was repointed from dwup00 to ozhe_power 2026-11-08 —
  // dwup00 leaps to 2.375 m and ends prone; ozhe_power is grounded,
  // crouch-then-rise, watched in-game the same day).
  assert.equal(pack.clips.dwhadoh00.root_t.length, 23);
  assert.equal(pack.clips.ozhe_power.root_t.length, 23);
  assert.ok(!pack.clips.dwup00, 'dwup00 must be out of the pantera pack (trigger is ozhe_power now)');
});

test('DW_MOVES + ensureDwMoves loads the pack (fetch stubbed to disk)', async () => {
  const t3 = await import(path.join(REPO, 'game', 'js', 't3anims.js'));
  assert.ok(t3.DW_MOVES && t3.DW_MOVES.pantera, 'DW_MOVES.pantera missing');
  assert.equal(typeof t3.ensureDwMoves, 'function');
  assert.equal(typeof t3.dwMoveClip, 'function');
  assert.equal(typeof t3.dwMoveRetarget, 'function');
  // Stub fetch so the pack + skeleton load from disk.
  const origFetch = globalThis.fetch;
  globalThis.fetch = async (url) => {
    const rel = String(url).replace(/^.*assets\/anim\/dw\//, '');
    const p = path.join(BANK_DIR, rel.split('?')[0]);
    if (!fs.existsSync(p)) return { ok: false, status: 404, json: async () => { throw new Error('404'); } };
    return { ok: true, status: 200, json: async () => readJson(p) };
  };
  try {
    const rec = await t3.ensureDwMoves('pantera', THREE);
    assert.ok(rec, 'ensureDwMoves returned null');
    assert.equal(Object.keys(rec.clips).length, 54, 'expected 54 DW clips (8 pilot + 46 Surge Kit rollout)');
    // Durations: dwhadoh00 23 keyframes @ 30 fps, ozhe_power 23 @ 30.
    assert.ok(Math.abs(rec.clips.dwhadoh00.duration - 23 / 30) < 1e-6);
    assert.ok(Math.abs(rec.clips.ozhe_power.duration - 23 / 30) < 1e-6);
    // Cached on the second call.
    const rec2 = await t3.ensureDwMoves('pantera', THREE);
    assert.equal(rec2, rec, 'ensureDwMoves must cache');
    // Unknown fighter returns null.
    assert.equal(await t3.ensureDwMoves('no-such-fighter', THREE), null);
  } finally {
    globalThis.fetch = origFetch;
  }
});

test('dwMoveClip resolves beam / throws / byInput, and nulls', async () => {
  const t3 = await import(path.join(REPO, 'game', 'js', 't3anims.js'));
  const origFetch = globalThis.fetch;
  globalThis.fetch = async (url) => {
    const rel = String(url).replace(/^.*assets\/anim\/dw\//, '');
    const p = path.join(BANK_DIR, rel.split('?')[0]);
    if (!fs.existsSync(p)) return { ok: false, status: 404, json: async () => { throw new Error('404'); } };
    return { ok: true, status: 200, json: async () => readJson(p) };
  };
  try {
    await t3.ensureDwMoves('pantera', THREE);
    const beam = t3.dwMoveClip('pantera', 'surge', null);
    assert.ok(beam && beam.name === 'dw:surge', 'beam must resolve to dw:surge');
    assert.equal(beam.active, null);
    const t1 = t3.dwMoveClip('pantera', '1+3', null);
    assert.ok(t1 && t1.name === 'dw:1+3');
    const t2 = t3.dwMoveClip('pantera', '2+4', null);
    assert.ok(t2 && t2.name === 'dw:2+4');
    // byInput fallback: the surge input 1+2+3+4 resolves without a moveKey.
    const byInput = t3.dwMoveClip('pantera', null, null, '1+2+3+4');
    assert.ok(byInput && byInput.name === 'dw:surge', 'byInput 1+2+3+4 must resolve to dw:surge');
    // Nulls: unknown moveKey, null moveKey with no input, unknown fighter.
    assert.equal(t3.dwMoveClip('pantera', 'no-such-move', null), null);
    assert.equal(t3.dwMoveClip('pantera', null, null, null), null);
    assert.equal(t3.dwMoveClip('no-such-fighter', 'surge', null), null);
  } finally {
    globalThis.fetch = origFetch;
  }
});

test('dwMoveRetarget returns null without a loaded pack', async () => {
  const t3 = await import(path.join(REPO, 'game', 'js', 't3anims.js'));
  // A fresh import would share the module cache (and the loaded pack), so
  // test the null path on an unloaded fighter id instead.
  assert.equal(t3.dwMoveRetarget('no-such-fighter', 'surge', null, THREE, 'k'), null);
});

test('fighter.js carries the dw: hooks (source-level check)', () => {
  const src = fs.readFileSync(path.join(REPO, 'game', 'js', 'fighter.js'), 'utf8');
  for (const needle of [
    'ensureDwMoves, dwMoveClip, dwMoveRetarget',
    "attackName === 'surge'",
    "name.startsWith('dw:')",
    '_dwThrowAction',
    '_dwTriggerAction',
    '_dwTriggerPending',
    'thrower.surgeForm',
  ]) {
    assert.ok(src.includes(needle), `fighter.js missing DW hook: ${needle}`);
  }
  const t3src = fs.readFileSync(path.join(REPO, 'game', 'js', 't3anims.js'), 'utf8');
  assert.ok(t3src.includes('export const DW_MOVES'), 't3anims.js missing DW_MOVES');
  assert.ok(t3src.includes('export function ensureDwMoves'), 't3anims.js missing ensureDwMoves');
});

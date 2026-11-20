// dw-followups.test.mjs — Devil Within follow-up tests (branch dw-followups).
// Verifies the kit-pack move mappings + the Warden/brawler-kind binding:
//   1. every packed clip has a `moves` entry whose key is the moveset-library
//      move id minus 'dw:', whose dw_source is the clip's gym file, and whose
//      input / active_frames are honest nulls (the library carries no DW
//      input or hit timing) with verified false — except the pilot's 4
//      pantera moves, which keep their inputs.
//   2. DW_KIND_MOVES binds 'warden' (and only 'warden'); ensureDwKindMoves
//      loads the warden pack, dwKindMoveClip resolves a mapped warden move,
//      and an unbound kind returns null.
//   3. fighter.js / brawler.js carry the kind hooks (source-level checks —
//      fighter.js is not Node-safe, same convention as dw-retarget.test.mjs).
// Run: node --test game/tests/dw-followups.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '..', '..');
const BANK_DIR = path.join(REPO, 'game', 'assets', 'anim', 'dw');

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

const PACK_FILES = [
  'moves.pantera.pack.json',
  'moves.warden.pack.json',
  'moves.unmasked.pack.json',
  'moves.drowned-ogre.pack.json',
  'moves.wave-echo.pack.json',
];

// The pilot's 4 pantera moves keep their inputs (the game drives the beam
// and the throws by input); every mapped move is input-null.
const PILOT_MOVES = {
  surge: { clip: 'dwhadoh00', input: '1+2+3+4' },
  'surge-trigger': { clip: 'ozhe_power', input: null },
  '1+3': { clip: 'ikdv_36_nage_f', input: '1+3' },
  '2+4': { clip: 'ikdv_36_nage_y', input: '2+4' },
};

test('move map log exists and names the mapping script', () => {
  const log = path.join(BANK_DIR, 'DW-MOVE-MAP-LOG.md');
  assert.ok(fs.existsSync(log), 'DW-MOVE-MAP-LOG.md missing');
  const text = fs.readFileSync(log, 'utf8');
  assert.ok(text.includes('dw_map_kit_moves.py'), 'map log must name the mapping script');
  assert.ok(text.includes('Library moves with no baked clip'), 'map log must list the unbaked library moves');
});

test('every packed clip maps to a library move (honest nulls)', () => {
  const bank = readJson(path.join(REPO, 'game', 'data', 'moveset-library', 'banks', 'dw.json'));
  const byClip = {};
  for (const mv of bank.moves) {
    const m = /gym_([a-z0-9_]+)\.dat/.exec(mv.provenance.note);
    assert.ok(m, `bank move ${mv.id} has no gym_ source file`);
    assert.ok(!byClip[m[1]], `bank has two moves for clip ${m[1]}`);
    byClip[m[1]] = mv;
  }
  let totalMoves = 0;
  for (const file of PACK_FILES) {
    const pack = readJson(path.join(BANK_DIR, file));
    assert.equal(pack.skipped.length, 0, `${file} skipped must be empty`);
    const moved = new Set();
    for (const [key, mv] of Object.entries(pack.moves)) {
      assert.ok(pack.clips[mv.clip], `${file} move ${key} names unbaked clip ${mv.clip}`);
      assert.ok(!moved.has(mv.clip), `${file} clip ${mv.clip} mapped twice`);
      moved.add(mv.clip);
      assert.equal(mv.dw_source, 'gym_' + mv.clip + '.dat', `${file}:${key} dw_source must be the clip file`);
      assert.equal(mv.active_frames, null, `${file}:${key} active_frames must be an honest null`);
      assert.equal(mv.verified, false, `${file}:${key} verified must be false until watched`);
      if (PILOT_MOVES[key]) {
        // Pilot move: kept as-is, input included.
        assert.equal(mv.clip, PILOT_MOVES[key].clip, `${file}:${key} pilot clip changed`);
        assert.equal(mv.input, PILOT_MOVES[key].input, `${file}:${key} pilot input changed`);
        continue;
      }
      assert.equal(mv.input, null, `${file}:${key} input must be null — no measured DW input`);
      const lib = byClip[mv.clip];
      assert.ok(lib, `${file}:${key} clip ${mv.clip} has no library move`);
      assert.equal(key, lib.id.replace(/^dw:/, ''), `${file}:${key} must be the library id minus 'dw:'`);
    }
    assert.equal(moved.size, Object.keys(pack.clips).length, `${file} every clip must have a move`);
    totalMoves += Object.keys(pack.moves).length;
  }
  assert.equal(totalMoves, 152, '152 moves total across the 5 packs (151 unique clips + ozhe_power twice)');
});

test('DW_KIND_MOVES binds warden only; kind pack loads and resolves', async () => {
  const t3 = await import(path.join(REPO, 'game', 'js', 't3anims.js'));
  assert.deepEqual(t3.DW_KIND_MOVES, { warden: 'warden' }, 'only warden is kind-bound');
  assert.equal(typeof t3.ensureDwKindMoves, 'function');
  assert.equal(typeof t3.dwKindMoveClip, 'function');
  assert.equal(typeof t3.dwKindMoveRetarget, 'function');
  // An unbound kind resolves nothing.
  assert.equal(await t3.ensureDwKindMoves('ogre', THREE), null);
  assert.equal(t3.dwKindMoveClip('ogre', 'ogre:anything', null), null);
  assert.equal(t3.dwKindMoveRetarget('ogre', 'ogre:anything', null, THREE, 'k'), null);
  const origFetch = globalThis.fetch;
  globalThis.fetch = async (url) => {
    const rel = String(url).replace(/^.*assets\/anim\/dw\//, '');
    const p = path.join(BANK_DIR, rel.split('?')[0]);
    if (!fs.existsSync(p)) return { ok: false, status: 404, json: async () => { throw new Error('404'); } };
    return { ok: true, status: 200, json: async () => readJson(p) };
  };
  try {
    const rec = await t3.ensureDwKindMoves('warden', THREE);
    assert.ok(rec, 'ensureDwKindMoves(warden) returned null');
    assert.equal(Object.keys(rec.clips).length, 39, 'warden kind pack must load 39 clips');
    assert.equal(Object.keys(rec.moves).length, 39, 'warden kind pack must load 39 moves');
    assert.equal(await t3.ensureDwKindMoves('warden', THREE), rec, 'kind load must cache');
    const slam = t3.dwKindMoveClip('warden', 'warden:bakutyu', null);
    assert.ok(slam && slam.name === 'dw:warden:bakutyu', 'warden:bakutyu must resolve');
    assert.equal(slam.anim, 'kmb1_bakutyu', 'warden:bakutyu must point at kmb1_bakutyu');
    assert.equal(t3.dwKindMoveClip('warden', 'no-such-move', null), null);
    // The fid path and the kind path agree on the warden pack.
    const fid = await t3.ensureDwMoves('warden', THREE);
    assert.equal(fid, rec, 'ensureDwMoves(warden) and ensureDwKindMoves(warden) must share the record');
  } finally {
    globalThis.fetch = origFetch;
  }
});

test('fighter.js / brawler.js carry the kind hooks (source-level check)', () => {
  const fsrc = fs.readFileSync(path.join(REPO, 'game', 'js', 'fighter.js'), 'utf8');
  for (const needle of [
    'dwKindMoveClip, dwKindMoveRetarget',
    '_dwKind',
    '_dwSlamNext',
    'warden:bakutyu',
    'DW warden explosion attack (kmb1_bakutyu)',
    'dwKindMoveRetarget(this._dwKind',
  ]) {
    assert.ok(fsrc.includes(needle), `fighter.js missing Warden hook: ${needle}`);
  }
  const bsrc = fs.readFileSync(path.join(REPO, 'game', 'js', 'brawler.js'), 'utf8');
  for (const needle of [
    'ensureDwKindMoves',
    "f._dwKind = 'warden'",
    "ensureDwKindMoves('warden'",
    'f._dwSlamNext = true',
    "if (!f.tryAttack('2')) f._dwSlamNext = false",
  ]) {
    assert.ok(bsrc.includes(needle), `brawler.js missing Warden hook: ${needle}`);
  }
  // The kind binding must NOT force the Warden onto a fighter id: no code
  // may call ensureDwMoves('warden') as if 'warden' were a fighter.
  assert.ok(!/ensureDwMoves\('warden'/.test(fsrc), 'fighter.js must not treat warden as a fighter id');
});

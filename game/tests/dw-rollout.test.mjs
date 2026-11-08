// dw-rollout.test.mjs — Devil Within retarget rollout tests.
// Verifies the rollout packs (the remaining wireable 35-bone clips, baked
// the same way as the pilot): every pack loads through the real ensureDwMoves
// path, clip shapes hold (21 bones, 30 fps, unit quats, sane root_t), and
// every packed clip has a mapped move (dw-followups, 2026-11-08:
// tools/anim/dw_map_kit_moves.py mapped all 152 clips from the measured
// moveset library; the kit packs were DATA (moves = {}) until then).
// The position round-trip (FK rebuilt vs true DW positions) is NOT in this
// file — it runs in Python (teardown/tekken5/tools/dw_roundtrip.py) and its
// numbers are recorded in the bake logs + DW-DECODE-LOG.md §23.
// Run: node --test game/tests/dw-rollout.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '..', '..');
const BANK_DIR = path.join(REPO, 'game', 'assets', 'anim', 'dw');

// pack file -> [fighter, expected clips, expected moves]
const PACKS = {
  'moves.pantera.pack.json': ['pantera', 54, 54],
  'moves.warden.pack.json': ['warden', 39, 39],
  'moves.unmasked.pack.json': ['unmasked', 29, 29],
  'moves.drowned-ogre.pack.json': ['drowned-ogre', 25, 25],
  'moves.wave-echo.pack.json': ['wave-echo', 5, 5],
};

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

test('rollout pack files exist on disk', () => {
  for (const f of Object.keys(PACKS)) {
    assert.ok(fs.existsSync(path.join(BANK_DIR, f)), `missing ${f}`);
  }
  for (const f of ['DW-BAKE-LOG.md', 'DW-BAKE-LOG-warden.md', 'DW-BAKE-LOG-unmasked.md',
    'DW-BAKE-LOG-drowned-ogre.md', 'DW-BAKE-LOG-wave-echo.md']) {
    assert.ok(fs.existsSync(path.join(BANK_DIR, f)), `missing ${f}`);
  }
});

test('rollout pack shapes: format, fighter, clip geometry', () => {
  const curves = readJson(path.join(REPO, 'teardown', 'tekken5', 'dw-motion-curves.json'));
  const bySrc = Object.fromEntries(curves.clips.map(c => [c.source_file, c]));
  for (const [file, [fighter, nClips, nMoves]] of Object.entries(PACKS)) {
    const pack = readJson(path.join(BANK_DIR, file));
    assert.equal(pack.format, 'wh-dw-moves/1', `${file} format`);
    assert.equal(pack.fighter, fighter, `${file} fighter`);
    assert.equal(Object.keys(pack.clips).length, nClips, `${file} clip count`);
    assert.equal(Object.keys(pack.moves).length, nMoves, `${file} move count`);
    // Every packed clip has exactly one mapped move now (dw-followups);
    // nothing is left in skipped. A move entry names a baked clip.
    assert.equal(pack.skipped.length, 0, `${file} skipped must be empty — every clip is mapped`);
    assert.equal(Object.keys(pack.moves).length, nClips, `${file} must map every clip`);
    for (const [key, m] of Object.entries(pack.moves)) {
      assert.ok(pack.clips[m.clip], `${file} move ${key} names clip ${m.clip}, which is not baked`);
    }
    assert.equal(new Set(Object.values(pack.moves).map((m) => m.clip)).size, nClips,
      `${file} two moves must not share one clip`);
    for (const [cname, c] of Object.entries(pack.clips)) {
      assert.equal(c.format, 'wh-anim/1', `${file}:${cname} format`);
      assert.equal(c.bones.length, 21, `${file}:${cname} must have 21 bones`);
      // fps follows the source step: 60 for step-1 clips (every frame),
      // 30 for step-2 clips (every 2nd frame). 10 rollout clips are step-1.
      const step = bySrc[c.dw_source].step;
      assert.equal(c.fps, step === 1 ? 60 : 30, `${file}:${cname} fps must follow step ${step}`);
      assert.equal(c.root_t.length, c.rot_xyzw[c.bones[0]].length, `${file}:${cname} rot/root_t length mismatch`);
      for (const b of c.bones) {
        assert.equal(c.rot_xyzw[b].length, c.root_t.length, `${file}:${cname}:${b} length mismatch`);
        for (const q of c.rot_xyzw[b]) {
          const n = Math.sqrt(q[0] ** 2 + q[1] ** 2 + q[2] ** 2 + q[3] ** 2);
          assert.ok(Math.abs(n - 1) < 1e-4, `${file}:${cname}:${b} quat not unit (${n})`);
        }
      }
      // root_t Y (hips height) stays in the measured band for DW motion:
      // min 0.109 m (a throw low point) to max 8.000 m (the flying boss's
      // fire attack, kob2_fly2fire). The band catches unit/sign errors,
      // not jumps — DW motion includes real leaps and a flying boss.
      for (const r of c.root_t) assert.ok(r[1] > 0.05 && r[1] < 8.5, `${file}:${cname} root_t Y ${r[1]} out of range`);
    }
  }
});

test('DW_MOVES has one entry per rollout pack', async () => {
  const t3 = await import(path.join(REPO, 'game', 'js', 't3anims.js'));
  for (const [file, [fighter]] of Object.entries(PACKS)) {
    assert.ok(t3.DW_MOVES[fighter], `DW_MOVES.${fighter} missing`);
    assert.equal(t3.DW_MOVES[fighter].pack, file, `DW_MOVES.${fighter} pack`);
  }
});

test('ensureDwMoves loads every rollout pack (fetch stubbed to disk)', async () => {
  const t3 = await import(path.join(REPO, 'game', 'js', 't3anims.js'));
  const origFetch = globalThis.fetch;
  globalThis.fetch = async (url) => {
    const rel = String(url).replace(/^.*assets\/anim\/dw\//, '');
    const p = path.join(BANK_DIR, rel.split('?')[0]);
    if (!fs.existsSync(p)) return { ok: false, status: 404, json: async () => { throw new Error('404'); } };
    return { ok: true, status: 200, json: async () => readJson(p) };
  };
  try {
    for (const [file, [fighter, nClips]] of Object.entries(PACKS)) {
      const rec = await t3.ensureDwMoves(fighter, THREE);
      assert.ok(rec, `ensureDwMoves(${fighter}) returned null`);
      assert.equal(Object.keys(rec.clips).length, nClips, `ensureDwMoves(${fighter}) clip count`);
      // Cached on the second call.
      assert.equal(await t3.ensureDwMoves(fighter, THREE), rec, `ensureDwMoves(${fighter}) must cache`);
      // Every pack's moves resolve through dwMoveClip (a known key per pack).
      const probeKey = { pantera: 'surge', warden: 'warden:bakutyu', unmasked: 'unmasked:360',
        'drowned-ogre': 'drowned_ogre:180', 'wave-echo': 'unmasked:ozhe-power' }[fighter];
      const probe = t3.dwMoveClip(fighter, probeKey, null);
      assert.ok(probe && probe.name === 'dw:' + probeKey, `dwMoveClip(${fighter}, ${probeKey}) must resolve`);
      assert.equal(t3.dwMoveClip(fighter, 'no-such-move', null), null);
    }
  } finally {
    globalThis.fetch = origFetch;
  }
});

test('rollout totals: 152 clips baked, exclusions recorded with measured reasons', () => {
  let total = 0;
  for (const [file] of Object.entries(PACKS)) {
    total += Object.keys(readJson(path.join(BANK_DIR, file)).clips).length;
  }
  assert.equal(total, 152, 'rollout must bake 152 clips (54 pantera + 39 warden + 29 unmasked + 25 drowned-ogre + 5 wave-echo)');
  // The exclusions (non-bakeable skeletons) are listed in the kit bake logs.
  const wardenLog = fs.readFileSync(path.join(BANK_DIR, 'DW-BAKE-LOG-warden.md'), 'utf8');
  assert.ok(wardenLog.includes('(none — every decoded clip of this group is baked)'), 'warden log must record zero exclusions');
  const unmaskedLog = fs.readFileSync(path.join(BANK_DIR, 'DW-BAKE-LOG-unmasked.md'), 'utf8');
  assert.ok(unmaskedLog.includes('4-bone appendage part-clip'), 'unmasked log must name the 4-bone exclusion');
  const ogreLog = fs.readFileSync(path.join(BANK_DIR, 'DW-BAKE-LOG-drowned-ogre.md'), 'utf8');
  assert.ok(ogreLog.includes('4-bone appendage part-clip'), 'drowned-ogre log must name the 4-bone exclusion');
  const echoLog = fs.readFileSync(path.join(BANK_DIR, 'DW-BAKE-LOG-wave-echo.md'), 'utf8');
  assert.ok(echoLog.includes('ozhe_1ckj66a: missing file'), 'wave-echo log must name the missing-file exclusion');
});

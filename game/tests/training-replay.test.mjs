/* training-replay.test.mjs — Regression tests for the deterministic
 * replay data layer (worker 29, 2026-10-22).
 *
 * Covers js/replay-codec.js (pure module, zero imports):
 *  1. Fighter snapshot / restore round-trips every captured field.
 *  2. Recorded-call indexing by tick is lossless.
 *  3. Continuous-input change detection (sameArgs) dedups ticks.
 *  4. Replay library CRUD: save newest-first, cap eviction, delete.
 *
 * Run: node --test game/tests/training-replay.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const codecUrl = pathToFileURL(
  join(dirname(fileURLToPath(import.meta.url)), '..', 'js', 'replay-codec.js')
).href;
const codec = await import(codecUrl);

/* ---- fake fighter: the fields snapFighter reads ---- */
function fakeFighter() {
  return {
    root: { position: { x: 2.5, y: 0, z: -0.3, set(x, y, z) { this.x = x; this.y = y; this.z = z; } } },
    facing: -1,
    _faceY: -Math.PI / 2,
    lean: { rotation: { y: -Math.PI / 2 } },
    state: 'attack',
    stateT: 0.37,
    hp: 62.5,
    meter: 44,
    vx: 1.2,
    stun: 0.15,
    dead: false,
    invuln: 0,
    attackName: '1,2',
    _attackPhase: 'active',
    hasHit: true,
    attack: { moveKey: '1,2' },
    combo: 3,
    stance: null,
    stanceT: 0,
    _rageUsed: false,
    _queuedNext: '1,2,1',
    _movesetId: 'pantera',
    tekken: { lastMove: '1,2' },
  };
}
const resolveMove = (id, notation) => ({ moveKey: notation, resolvedFor: id });

test('snapshot/restore round-trips every field', () => {
  const f = fakeFighter();
  const s = codec.snapFighter(f);
  // JSON-safe (the library persists snapshots)
  const s2 = JSON.parse(JSON.stringify(s));
  const g = fakeFighter();
  // scramble the target first
  g.root.position.set(0, 9, 0); g.hp = 1; g.state = 'idle'; g.attackName = null;
  codec.restoreFighter(g, s2, resolveMove);
  assert.equal(g.root.position.x, 2.5);
  assert.equal(g.root.position.z, -0.3);
  assert.equal(g.facing, -1);
  assert.equal(g.lean.rotation.y, -Math.PI / 2);
  assert.equal(g.state, 'attack');
  assert.equal(g.stateT, 0.37);
  assert.equal(g.hp, 62.5);
  assert.equal(g.meter, 44);
  assert.equal(g.vx, 1.2);
  assert.equal(g.attackName, '1,2');
  assert.equal(g._attackPhase, 'active');
  assert.equal(g.hasHit, true);
  assert.equal(g.attack.moveKey, '1,2');
  assert.equal(g.attack.resolvedFor, 'pantera');
  assert.equal(g.combo, 3);
  assert.equal(g._queuedNext, '1,2,1');
  assert.equal(g.tekken.lastMove, '1,2');
});

test('restore with null attack clears the attack object', () => {
  const f = fakeFighter();
  const s = codec.snapFighter(f);
  s.attackNotation = null;
  s.attackName = null;
  const g = fakeFighter();
  codec.restoreFighter(g, s, resolveMove);
  assert.equal(g.attack, null);
  assert.equal(g.attackName, null);
});

test('call indexing by tick is lossless and ordered', () => {
  const calls = [
    [0, 'p1', 'setStick', 'n'],
    [5, 'p1', 'tryAttack', '1', 1, '1'],
    [5, 'p2', 'setStick', 'b'],
    [120, 'p1', 'tryMove', 1],
  ];
  const map = codec.indexCallsByTick(calls);
  assert.equal(map.size, 3);
  assert.deepEqual(map.get(5), [calls[1], calls[2]]);
  assert.deepEqual(map.get(0), [calls[0]]);
  assert.equal(map.get(999), undefined);
});

test('sameArgs dedups continuous inputs (with float epsilon)', () => {
  assert.ok(codec.sameArgs(['n'], ['n']));
  assert.ok(codec.sameArgs([1], [1.0005])); // joystick epsilon
  assert.ok(!codec.sameArgs([1], [1.5]));
  assert.ok(!codec.sameArgs(['n'], ['b']));
  assert.ok(!codec.sameArgs([true], [false]));
  assert.ok(!codec.sameArgs(undefined, ['n']));
  assert.ok(codec.sameArgs([1, 'a'], [1, 'a']));
  assert.ok(!codec.sameArgs([1], [1, 2]));
});

/* ---- in-memory storage mock ---- */
function mockStorage() {
  const m = new Map();
  return {
    getItem: (k) => (m.has(k) ? m.get(k) : null),
    setItem: (k, v) => { m.set(k, String(v)); },
    removeItem: (k) => { m.delete(k); },
  };
}
function replayData(id, n = `rp_${id}`) {
  return {
    v: 1,
    meta: {
      id: n, date: new Date().toISOString(),
      p1id: 'pantera', p2id: 'demonio', p1name: 'PANTERA', p2name: 'DEMONIO',
      stageId: 'shrine', stageName: 'SHRINE', mode: 'versus', winner: 'p1',
    },
    rounds: [{ round: 1, tick0: 0, endTick: 120, snapshot: {}, calls: [] }],
  };
}

test('library: save newest-first, get, delete', () => {
  const st = mockStorage();
  assert.deepEqual(codec.listReplays(st), []);
  codec.saveReplay(st, replayData(1));
  codec.saveReplay(st, replayData(2));
  const list = codec.listReplays(st);
  assert.equal(list.length, 2);
  assert.equal(list[0].id, 'rp_2'); // newest first
  assert.equal(list[1].id, 'rp_1');
  assert.ok(codec.getReplay(st, 'rp_1'));
  assert.equal(codec.getReplay(st, 'nope'), null);
  assert.ok(codec.deleteReplay(st, 'rp_2'));
  assert.equal(codec.listReplays(st).length, 1);
  assert.equal(codec.listReplays(st)[0].id, 'rp_1');
});

test('library: capped at LIB_MAX, oldest evicted', () => {
  const st = mockStorage();
  for (let i = 0; i < codec.LIB_MAX + 4; i++) codec.saveReplay(st, replayData(i));
  const list = codec.listReplays(st);
  assert.equal(list.length, codec.LIB_MAX);
  assert.equal(list[0].id, `rp_${codec.LIB_MAX + 3}`);
  assert.equal(codec.getReplay(st, 'rp_0'), null); // evicted
});

test('library: corrupt storage reads as empty, never throws', () => {
  const st = mockStorage();
  st.setItem(codec.LIB_KEY, '{not json');
  assert.deepEqual(codec.listReplays(st), []);
});

test('makeMeta stamps required fields', () => {
  const m = codec.makeMeta({
    p1id: 'a', p2id: 'b', p1name: 'A', p2name: 'B',
    stageId: 's', stageName: 'S', mode: 'versus', winner: 'p2',
  });
  assert.ok(m.id.startsWith('rp_'));
  assert.ok(m.date);
  assert.equal(m.winner, 'p2');
  assert.equal(m.p1name, 'A');
});

// Attack animation selection + timing (lane D, 2026-10-24). Node, no browser.
// Run: node --test test/attack-anim.test.mjs
// Owner: "the different move inputs from the move lists ... aren't working ... just random stuff is
// happening ... I need them to be able to actually make contact". The move that resolves must play
// ITS clip (own decoded T3 row, else the closest real clip of the fighter's own bank by limb and
// height), and the clip's hit frame must land on the move's first active frame.
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
const { FULL_ROSTER } = await import(join(ROOT, 'game/js/roster-full.js'));
const quiet = { log: console.log, warn: console.warn };
console.log = () => {}; console.warn = () => {};
await M.loadFighterMovesets();
const IDS = FULL_ROSTER.map(c => c.id);
await M.ensureMovesets(IDS);
console.log = quiet.log; console.warn = quiet.warn;

async function fighter(id) {
  const bank = F.bankIdFor(id, id);
  const save = console.log; console.log = () => {};
  const clips = bank ? await T.loadT3Clips(THREE, bank) : null;
  console.log = save;
  const f = Object.create(F.Fighter.prototype);
  f.char = { id }; f._movesetId = id; f.t3actions = {};
  f._t3 = bank ? { bank, clips } : null;
  return f;
}
const plan = (f, n) => f._attackClipPlan(F.getRealMove(f._movesetId, n), n);

test('attackClipTime: hit window lands on the first active frame, recovery fills the move', () => {
  const tm = { S: 0.2, A: 0.05, R: 0.5, t0: 0.4, t1: 0.45, D: 1.2 };
  assert.equal(T.attackClipTime(tm, 0), 0);
  assert.ok(Math.abs(T.attackClipTime(tm, 0.2) - 0.4) < 1e-9, 'startup -> clip hit frame');
  assert.ok(Math.abs(T.attackClipTime(tm, 0.25) - 0.45) < 1e-9, 'end of active -> end of hit window');
  assert.ok(T.attackClipTime(tm, 0.75) > 1.19, 'move end -> clip end');
  let prev = -1;
  for (let g = 0; g <= 0.8; g += 0.01) { const c = T.attackClipTime(tm, g); assert.ok(c >= prev - 1e-9); prev = c; }
});

test('decoded attack levels', () => {
  assert.equal(T.attackLevelOfWord(0x412), 'h');
  assert.equal(T.attackLevelOfWord(0x217), 'm');
  assert.equal(T.attackLevelOfWord(0x10f), 'l');
  assert.equal(T.attackLevelOfWord(0x31f), 's');
  assert.equal(T.attackLevelOfWord(0x607), 'u');
  assert.equal(F.Fighter.attackLimb({ limb: 'both' }, '3'), 'legL');
  assert.equal(F.Fighter.attackLimb({}, 'd/f+2'), 'armR');
});

test('Skull: different inputs play different clips of his own bank, own rows first', async () => {
  const f = await fighter('skull');
  assert.equal(f._t3.bank, 'bryan');
  const names = {};
  for (const n of ['1', '2', '3', '4', 'd/f+1', 'd/b+4', 'f+2', 'd/f+2']) {
    const p = plan(f, n);
    assert.ok(p && p.name, `${n}: no clip`);
    assert.notEqual(p.kind, 'generic', `${n}: generic clip`);
    assert.ok(p.name.startsWith('row:'), `${n}: ${p.name}`);
    names[n] = p.name;
  }
  assert.equal(new Set(Object.values(names)).size, Object.keys(names).length, JSON.stringify(names));
  const df1 = plan(f, 'd/f+1');
  assert.equal(df1.kind, 'own');
  assert.equal(df1.limb, 'armL');
});

test('every bound fighter: non-throw moves never fall back to a generic clip when the bank has a matching row', async () => {
  for (const id of IDS) {
    const ms = M.getFighterMoveset(id);
    if (!ms || !ms.moves) continue;
    const f = await fighter(id);
    if (!f._t3) continue;
    const pool = T.bankAttackPool(f._t3.bank);
    for (const n of Object.keys(ms.slots || ms.moves)) {
      const mv = F.getRealMove(id, n);
      const p = f._attackClipPlan(mv, n);
      assert.ok(p && p.name && f._t3.clips[p.name], `${id} ${n}: no clip`);
      if (p.kind === 'generic' && !(mv && mv.isGrab) && p.level !== 't' && !/^(1\+3|2\+4)$/.test(n))
        assert.ok(!pool.some(c => c.limb === p.limb), `${id} ${n}: generic ${p.name} though the bank has ${p.limb} rows`);
    }
  }
});

test('timing: the clip hit frame lands on the move startup (decoded T3 active frame)', async () => {
  let checked = 0;
  for (const id of ['skull', 'pantera', 'chatur', 'buffalo-bill', 'demonio']) {
    const f = await fighter(id);
    const ms = M.getFighterMoveset(id);
    for (const n of Object.keys(ms.slots || ms.moves)) {
      const mv = F.getRealMove(id, n);
      const p = f._attackClipPlan(mv, n);
      if (!p || !p.timing || p.timing.src !== 'decoded') continue;
      const tm = p.timing;
      assert.ok(Math.abs(T.attackClipTime(tm, tm.S) - Math.min(tm.t0, tm.D - 1e-4)) < 1e-6, `${id} ${n}`);
      const endWant = tm.R > 1e-4 ? tm.D - 2e-4 : Math.min(tm.t1, tm.D - 1e-4) - 1e-6; // no recovery: the move ends on its hit
      assert.ok(T.attackClipTime(tm, tm.S + tm.A + tm.R) >= endWant, `${id} ${n}: clip not finished at move end`);
      checked++;
    }
  }
  assert.ok(checked > 500, `only ${checked} decoded timings`);
});

test('pressing 1 never plays a throw: Pantera Jab skips its anim_t3 row 290 (King throw attempt)', async () => {
  const f = await fighter('pantera');
  const mv = F.getRealMove('pantera', '1');
  assert.equal(mv.animRow, 290, 'data premise changed: Pantera 1 no longer points at row 290');
  assert.ok(T.clipIsThrow(f._t3.clips['row:290']), 'row 290 is a decoded throw row');
  const p = plan(f, '1');
  assert.ok(!T.clipIsThrow(f._t3.clips[p.name]), `Pantera 1 plays throw row ${p.name}`);
  assert.equal(p.limb, 'armL');
  assert.equal(p.name, 'row:44', 'King\'s own T3 1 (i10 jab, decoded hit frame 7)');
  // Even with no same-input row to fall back on, the throw row is rejected, never played.
  const q = f._attackClipPlan({ ...mv, tekkenInput: 'zz', moveKey: null }, 'zz');
  assert.ok(q.rejected.some(r => r.includes('row:290')), JSON.stringify(q.rejected));
  assert.ok(!T.clipIsThrow(f._t3.clips[q.name]), q.name);
});

test('every bound fighter: no strike plays a throw row and no throw plays a strike row', async () => {
  const bad = [];
  for (const id of IDS) {
    const ms = M.getFighterMoveset(id);
    if (!ms || !ms.moves) continue;
    const f = await fighter(id);
    if (!f._t3) continue;
    for (const n of Object.keys(ms.slots || ms.moves)) {
      const mv = F.getRealMove(id, n);
      if (!mv) continue;
      const p = f._attackClipPlan(mv, n);
      const c = f._t3.clips[p.name], h = c.userData.hit;
      if (!p.grab && T.clipIsThrow(c)) bad.push(`${id} ${n}: strike -> throw ${p.name}`);
      if (p.grab && h && h[0] > 0 && !h[4]) bad.push(`${id} ${n}: throw -> strike ${p.name}`);
    }
  }
  assert.deepEqual(bad.slice(0, 20), [], `${bad.length} strike/throw clip mismatches`);
});

test('string moves listing one row per hit play the hit the key fires (chatur b+2,1 -> row 63)', async () => {
  const f = await fighter('chatur');
  const p = plan(f, 'b+2,1');
  assert.equal(p.kind, 'own');
  assert.equal(p.name, 'row:63');
});

test('every row a moveset references in its bound bank is baked into rows.pack.json', async () => {
  const missing = [];
  for (const id of IDS) {
    const ms = M.getFighterMoveset(id);
    if (!ms || !ms.moves) continue;
    const f = await fighter(id);
    if (!f._t3) continue;
    const last = r => (Array.isArray(r) ? r[r.length - 1] : r);
    for (const n of Object.keys(ms.slots || ms.moves)) {
      const mv = F.getRealMove(id, n);
      if (!mv) continue;
      const sb = mv.t3source ? T.SOURCE_TO_BANK[mv.t3source] : f._t3.bank;
      if (mv.t3row != null && sb === f._t3.bank && !f._t3.clips['row:' + last(mv.t3row)]) missing.push(`${id} ${n} t3_row ${last(mv.t3row)}`);
      const ab = T.SOURCE_TO_BANK[mv.animBank] || mv.animBank;
      if (mv.animRow != null && ab === f._t3.bank && !f._t3.clips['row:' + last(mv.animRow)]) missing.push(`${id} ${n} anim_t3 ${last(mv.animRow)}`);
    }
  }
  assert.deepEqual(missing.slice(0, 20), [], `${missing.length} referenced rows not baked (python3 tools/anim/t3_row_bake.py --merge --bank <b>)`);
});

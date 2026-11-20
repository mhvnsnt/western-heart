// Roster-100 S8 (docs/movesets/DEMONIO-D1-S8-DIAGNOSIS-2026-11-05.md):
// Demonio d+1 was bound to the T8-derived record the 2026-10-21 source
// merge had reclassed as a throw (move_class throw / isGrab / unblockable
// / throw_break — none of which exist in the T7, T8, or T3 source data
// for this move). His own Corpse Thrust strike record sat unslotted
// beside it in every Demonio file (key 'd+1~t7.jin', human form:
// 'd+1~donor.demonio'; anim_t3 Jin row 188, hit word 535). The repair
// re-points slots['d+1'] at that strike record in all four files — the
// same slotting class S1 fixed. No fight datum changed: the
// throw-classed record stays in moves untouched (it is the data of
// record for the T8 strike->attack-throw transition the engine does
// not model — diagnosis deviation 1).
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const _ls = {}; globalThis.localStorage = { getItem: (k) => _ls[k] ?? null, setItem: (k, v) => { _ls[k] = String(v); }, removeItem: (k) => { delete _ls[k]; } };
const M = await import('../game/js/movesets.js');
const load = (id) => {
  const raw = fs.readFileSync(new URL(`../game/assets/movesets/${id}.json`, import.meta.url), 'utf8');
  M.registerMoveset(id, JSON.parse(raw));
  return JSON.parse(raw);
};
const CASES = [
  ['demonio', 'd+1~t7.jin', 24],
  ['demonio-bloodline-ember', 'd+1~t7.jin', 14],
  ['demonio-human', 'd+1~donor.demonio', 14],
  ['demonio-winged', 'd+1~t7.jin', 14],
];
for (const [id, strikeKey, dmg] of CASES) {
  test(`${id} d+1 fires his own Corpse Thrust strike (Jin row 188)`, () => {
    const data = load(id);
    assert.equal(data.slots['d+1'], strikeKey);
    assert.equal(M.resolveMoveKey(id, 'd+1'), strikeKey);
    const mv = M.getFighterMoveset(id).moves[strikeKey];
    assert.equal(mv.name, 'Corpse Thrust');
    assert.equal(mv.move_class, 'strike');
    assert.ok(!mv.isGrab);
    assert.equal(mv.damage, dmg);
    assert.equal(mv.anim_t3.bank, 'jin');
    assert.equal(mv.anim_t3.row, 188);
    assert.equal(data.hit_words[strikeKey], 535);
  });

  test(`${id}: the throw-classed d+1 record stays in moves, unedited and unslotted`, () => {
    const data = load(id);
    const rec = data.moves['d+1'];
    assert.ok(rec, 'T8-derived record must remain as data of record');
    assert.equal(rec.move_class, 'throw');
    assert.equal(rec.isGrab, true);
    assert.notEqual(data.slots['d+1'], 'd+1');
    // genuine throw inputs still resolve to throws
    const t = M.getFighterMoveset(id).moves[M.resolveMoveKey(id, '1+3')];
    assert.equal(t.move_class, 'throw');
  });
}

test('demonio neighbours untouched by the re-point', () => {
  load('demonio');
  assert.equal(M.resolveMoveKey('demonio', '1'), '1~t8.jin');
  assert.equal(M.resolveMoveKey('demonio', '2'), '2~t8.jin');
  assert.equal(M.resolveMoveKey('demonio', 'd+2'), 'd+2');
  assert.equal(M.resolveMoveKey('demonio', '1+3'), '1+3~t8.jin');
  assert.equal(M.resolveMoveKey('demonio', '2+4'), '2+4~t8.jin');
  load('demonio-human');
  assert.equal(M.resolveMoveKey('demonio-human', '1'), '1');
  assert.equal(M.resolveMoveKey('demonio-human', 'd+2'), 'd+2');
  assert.equal(M.resolveMoveKey('demonio-human', '1+3'), '1+3');
});

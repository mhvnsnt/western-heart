// Pantera wiring fix (2026-11-03). Node, no browser. Run: node --test test/pantera-wiring.test.mjs
// Owner playtest: grapple clips fire mid-combo on strike inputs, and deliberate
// 1+3 / 2+4 grapples feel unreachable. Root causes covered here:
//  (1) getRealMove derived isGrab from t3_condition 2..0x17 — but those codes mark
//      throw-SITUATION branch rows (the executions a connected grab branches into),
//      not standalone grabs. Every move that was a grab by that term alone is classed
//      'strike' or 'special' in its own moveset data (955 repo-wide, 0 classed throw).
//  (2) The step-plan branch of _attackClipPlan returned verified step rows with no
//      strike/throw class check, so a throw-flagged row played as a string hit.
//  (3) genericBankAction was dead code: its only step-plan call site indexed the
//      flat clips map by bank name (this._t3.clips[bank] === undefined, always).
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
const quiet = { log: console.log, warn: console.warn };
console.log = () => {}; console.warn = () => {};
await M.loadFighterMovesets();
await M.ensureMovesets(['pantera', 'kronos', 'cainelias']);
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

test('situation-condition strikes are not grabs (pantera 1,1 / d/b+1)', () => {
  // '1,1' is "KING 1,1_c2" — move_class 'strike', t3_condition 2, in his own data.
  assert.equal(F.getRealMove('pantera', '1,1').isGrab, false);
  assert.equal(F.getRealMove('pantera', 'd/b+1').isGrab, false);
  assert.equal(F.getRealMove('pantera', 'd/f+3+4,1').isGrab, false);
});

test('real throws stay throws', () => {
  assert.equal(F.getRealMove('pantera', '1+3').isGrab, true);
  assert.equal(F.getRealMove('pantera', '2+4').isGrab, true);
  assert.equal(F.getRealMove('pantera', 'f+1+3').isGrab, true);
  assert.equal(F.getRealMove('pantera', 'd/b+1+3').isGrab, true);
});

test('step-plan class guard: pantera 1,1 never plays throw row 584', async () => {
  const f = await fighter('pantera');
  const plan = f._attackClipPlan(F.getRealMove('pantera', '1,1'), '1,1');
  assert.equal(plan.grab, false);
  assert.notEqual(plan.name, 'row:584');
  if (plan.name && f._t3.clips[plan.name]) {
    assert.equal(T.clipIsThrow(f._t3.clips[plan.name]), false,
      `strike step presented a throw clip: ${plan.name}`);
  }
  if (plan.name === 'row:584' || (plan.rejected || []).length) {
    assert.ok((plan.rejected || []).some(r => /584|throw row/.test(r)),
      'a rejected throw step row must be recorded in plan.rejected');
  }
});

test('genericBankAction reads the flat clips map (the PR #1458 tier lives)', async () => {
  const f = await fighter('pantera');
  const clips = f._t3.clips;
  const strike = F.genericBankAction('king', clips, 'armR', false);
  assert.ok(strike, 'generic strike action exists in the king bank');
  assert.equal(T.clipIsThrow(clips[strike]), false, 'generic for a strike is never a throw clip');
  // The king bank has NO throw-flagged generic (its 'grab' action carries a
  // strike-typed hit record), so a throw gets null here — never a strike clip —
  // and the caller falls through to the fighter's own-button throw clip.
  const grab = F.genericBankAction('king', clips, 'armR', true);
  assert.equal(grab, null, 'no class-matching generic for a throw in the king bank');
});

test('king-bank fighters: the jab string is not a grab', () => {
  for (const id of ['kronos', 'cainelias']) {
    const mv = F.getRealMove(id, '1,1');
    if (mv) assert.equal(mv.isGrab, false, `${id} 1,1`);
  }
});

/* Burger Batch 4 step plans (triples/quads/rest strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/BURGER-BATCH4-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on burger Batch 3 (feat/burger-batch3-step-plans-20261025,
 * PR #1105), which stacks on burger Batch 2 (feat/burger-batch2-step-plans-20261025,
 * PR #1104), which stacks on burger Batch 1 (feat/burger-batch1-step-plans-20261025,
 * PR #1103), which stacks on #1096 (feat/batch1-step-plans-pantera-20261024,
 * the step-playback engine). It does NOT stack on any Pantera plan branch:
 * burger.json plans do not conflict with pantera.json plans.
 * It does NOT include #1097's Pantera Batch 1 follow-up fills (Pantera-specific,
 * and its row-49 SOFT fill is still unapproved); no SOFT fill is inherited here.
 * Batch 4 wires ZERO Job 3 fills (the one exact+FULL candidate, row 119 for the
 * rest-key f,n,d,d/f+4 family, is never wired because rest keys get no plan;
 * soft candidates rows 41/42/43 for u/f+1+2 and rows 60/61/62/96 for u/f+2 are
 * soft/row-only and never wired) and ZERO Job 4 promotions (no Batch 4 prefix
 * carries a bryan Job 4 candidate as an own row). 0 steps are SUSPENDED-DRIFT
 * (no Batch 4 string carries prefix 3 or b_c36_r65). 52 rest canonicals get NO
 * plan at all: their non-attack prefix steps have no attack row, and planning
 * them needs engine support for non-attack prefix steps (future work, named,
 * not guessed).
 * This PR does not touch `fighter.js`: #1096's merge onto post-#1078 main must
 * reconcile #1078's `fighter.js` changes with #1096's engine branch, and that
 * belongs to #1096's merge, not this PR.
 * Rules asserted here (all data-level, no THREE needed):
 *   1. burger.json still has 552 moves / 107 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 219 keys (88 Batch 1 + 67 Batch 2 + 49 Batch 3 + 15 Batch 4).
 *   3. Batch 4 verified steps always carry a row, and no verified row is 35 or 220;
 *      review/unmapped steps carry row null. No Batch 4 step carries a soft flag
 *      (Batch 4 wires zero Job 3 fills and zero Job 4 promotions).
 *   4. 2,1,4 flagship: partial on rows 100/153/null (steps 1-2 verified, step 3 unmapped).
 *   5. u+1+2,4 flagship: step 1 unmapped row null, step 2 verified row 183 (jump context, SOFT waived).
 *   6. u/f+1+2,4 flagship: step 1 unmapped row null, step 2 verified row 183 (jump context, SOFT waived).
 *   7. u/f+2,3,3+4,4 flagship: steps 1-3 unmapped row null, step 4 verified row 183 (jump context, SOFT waived).
 *   8. Rest keys (f,F+2, f,n,d,d/f+4, WALL.b,b,u/b, ...) have NO plan key.
 *   9. The verified-last-step Batch 4 keys are exactly the 4 listed below,
 *      and verified rows carry the step buttons in the repo Bryan hit_frames.json.
 *  10. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Run: node --test game/tests/burger-batch4-step-plans.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const burger = JSON.parse(readFileSync(join(ROOT, 'game/assets/movesets/burger.json'), 'utf8'));
const fighterSrc = readFileSync(join(ROOT, 'game/js/fighter.js'), 'utf8');
const hfPath = join(ROOT, 'game/assets/anim/t3/bryan/hit_frames.json');
const hf = JSON.parse(readFileSync(hfPath, 'utf8')).rows;

const plans = burger.string_step_plans.plans;
const B3 = ["1,3", "1,3~t7.bob", "1,3,3", "1,3,3~t7.bob", "1,3,3~t7.bob.2", "1,4", "1,4~t7.bob", "1,4~t7.bob.2", "1,d+4", "1,d+4~t7.bob", "1,d+4~t7.bob.2", "2,4", "3,1", "3,1,1", "3,2", "BAL.1,H.4", "FC.d/f+2,4", "FC.d/f+2,4~t7.bob", "WS.1,3", "WS.1,3~t7.bob", "b+2,2,4", "b+2,2,4~t7.bob", "b+2,2,4~t7.bob.2", "b+2,2,4~t7.bob.3", "b+2,2,4,4", "b+2,2,4,4~t7.bob", "b+2,2,4,4~t7.bob.2", "b+2,2,4,4~t7.bob.3", "b+2,2,4,4~t7.bob.4", "b+4,1", "b+4,1~t7.bob", "d+2,3", "d+2,3~t7.bob", "d+2,3~t7.bob.2", "d+2,4", "d+2,4~t7.bob", "d+2,4~t7.bob.2", "d/f+3,1", "d/f+3,1~t7.bob", "d/f+3,1,1", "d/f+3,1,1~t7.bob", "d/f+3,1,1~t7.bob.2", "d/f+3,2", "d/f+3,2~t7.bob", "f+2,3", "f+2,3~t7.bob", "f+2,3~t7.bob.2", "ub+4,1", "ws1,3"];
const B4 = ["1+2+3+4,1+2", "1+2+3+4,4", "2,1,4", "2,1,4~t7.bob", "2,1,4~t7.bob.2", "2,1,4~t7.bob.3", "3+4,4,2", "FC.d/f+2,4,1+2", "FC.d/f+2,4,1+2~t7.bob", "FC.d/f+2,4,1+2~t7.bob.2", "u+1+2,4", "u/f+1+2,4", "u/f+1+2,4~t7.bob", "u/f+2,1,2,2,1,1+2,3,1,2,3+4", "u/f+2,3,3+4,4"];
const B1 = ["1+2,1+2", "1+2,1+2~t7.bob", "1+2,1+2~t7.bob.2", "1,1", "1,1,2", "1,1,2~t7.bob", "1,1,2~t7.bob.2", "1,1,2~t7.bob.3", "1,1~t7.bob", "1,1~t7.bob.2", "1,2", "1,2,1+2", "1,2,1+2~t7.bob", "1,2,1+2~t7.bob.2", "1,2,2", "1,2~t7.bob", "1,2~t7.bob.2", "2,1", "2,1,2", "2,1~t7.bob", "2,1~t7.bob.2", "2,1~t8.bob", "BAL.1,2", "FC.d/f+2,1", "FC.d/f+2,1,1+2", "FC.d/f+2,1,1+2~t7.bob", "FC.d/f+2,1,1+2~t7.bob.2", "FC.d/f+2,1~t7.bob", "FC.df+2,1", "FC.df+2,1,1+2", "WS.1,2", "WS.1,2~t7.bob", "WS.2,1", "WS.2,1~t7.bob", "WS.2,2", "WS.2,2~t7.bob", "b+1+2,1", "b+1+2,1,2", "b+1+2,1,2~t7.bob", "b+1+2,1,2~t7.bob.2", "b+1+2,1,2~t7.bob.3", "b+1+2,1~t7.bob", "b+1+2,1~t7.bob.2", "b+1,2", "b+1,2~t7.bob", "b+1,2~t7.bob.2", "b+2,1", "b+2,2", "b+2,2~t7.bob", "b+2,2~t7.bob.2", "d+1+2,2", "d+1+2,2,1", "d+1+2,2,1~t7.bob", "d+1+2,2,1~t7.bob.2", "d+1+2,2,1~t7.bob.3", "d+1+2,2,1~t7.bob.4", "d+1+2,2~t7.bob", "d+1+2,2~t7.bob.2", "d+1+2,2~t7.bob.3", "d+2,1", "d+2,1,2", "d+2,1,2,2", "d+2,1,2,2~t7.bob", "d+2,1,2,2~t7.bob.2", "d+2,1,2,2~t7.bob.3", "d+2,1,2,2~t7.bob.4", "d+2,1,2~t7.bob", "d+2,1,2~t7.bob.2", "d+2,1,2~t7.bob.3", "d+2,1~t7.bob", "d+2,1~t7.bob.2", "d/f+1,1+2", "d/f+1,1+2~t7.bob", "d/f+1,2", "d/f+1,2~t7.bob", "df+1,2", "df+1,d+1", "f+2,H.1+2", "f+2,H.1+2,1", "u+1+2,1", "u+1+2,1+2", "u/f+1+2,1+2", "u/f+1+2,1+2~t7.bob", "uf+1,2", "uf+1,2,H.2", "ws1,2", "ws2,1", "ws2,2"];
const B2 = ["3+4,4", "3,3", "3,4", "3,4~t7.bob", "4,3", "4,3,3+4", "4,3,3+4~t7.bob", "4,3,3+4~t7.bob.2", "4,3,4", "4,3~t7.bob", "4,3~t7.bob.2", "4,4", "WS.3,3+4", "WS.3,3+4~t7.bob", "b+4,3", "b+4,4", "b+4,4~t7.bob", "b+4,4~t7.bob.2", "d+3,4", "d+3,4~t7.bob", "d+3,4~t7.bob.2", "d+4,3", "d+4,3,4", "d+4,3,4~t7.bob", "d+4,3,4~t7.bob.2", "d+4,3,4~t7.bob.3", "d+4,3~t7.bob", "d+4,3~t7.bob.2", "d/b+3+4,4", "d/b+3+4,4~t7.bob", "d/b+4,4", "d/b+4,4,3", "d/b+4,4,3,3", "d/b+4,4,3,3~t7.bob", "d/b+4,4,3,3~t7.bob.2", "d/b+4,4,3,3~t7.bob.3", "d/b+4,4,3~t7.bob", "d/b+4,4,3~t7.bob.2", "d/b+4,4,4", "d/b+4,4,4~t7.bob", "d/b+4,4,4~t7.bob.2", "d/b+4,4~t7.bob", "d/f+3+4,4", "d/f+3+4,4~t7.bob", "d/f+3+4,4~t7.bob.2", "d/f+3,4", "d/f+3,4,4", "d/f+3,4,4~t7.bob", "d/f+3,4,4~t7.bob.2", "d/f+3,4~t7.bob", "db+3+4,4", "db+4,4", "db+4,4,3", "db+4,4,3,3", "df+4,3", "df+4,4", "f+3,4", "f+3,4~t7.bob", "f+3,4~t7.bob.2", "u/f+3+4,4", "u/f+3+4,4~t7.bob", "u/f+3+4,4~t7.bob.2", "u/f+4,4", "u/f+4,4~t7.bob", "ub+3+4,4", "uf+3+4,4", "ws3,3+4"];
const B4_VERIFIED_LAST = ["u+1+2,4", "u/f+1+2,4", "u/f+1+2,4~t7.bob", "u/f+2,3,3+4,4"];
const VERIFIED_BUTTONS = {"100": 2, "153": 1, "183": 8};

test('burger move/string counts unchanged by the additive plans block', () => {
  assert.equal(Object.keys(burger.moves).length, 552);
  assert.equal(burger.strings.length, 107);
  assert.equal(Object.keys(plans).length, 219);
});

test('Batch 4 keys are exactly the documented 15; Batch 1 + Batch 2 + Batch 3 keys all present', () => {
  assert.equal(B4.length, 15);
  for (const key of B4) assert.ok(plans[key], `Batch 4 key ${key} missing`);
  for (const key of B1) assert.ok(plans[key], `Batch 1 key ${key} missing (Batch 1 plans must be preserved)`);
  for (const key of B3) assert.ok(plans[key], `Batch 3 key ${key} missing (Batch 3 plans must be preserved)`);
  for (const key of B2) assert.ok(plans[key], `Batch 2 key ${key} missing (Batch 2 plans must be preserved)`);
  const extra = Object.keys(plans).filter((k) => !B4.includes(k) && !B3.includes(k) && !B1.includes(k) && !B2.includes(k));
  assert.deepEqual(extra, []);
});

test('Batch 4 verified steps carry rows (never 35/220); review/unmapped carry row null; no soft flags', () => {
  for (const key of B4) {
    for (const s of plans[key].steps) {
      assert.ok(!('soft' in s) || s.soft !== true, `${key} step ${s.step} carries a soft flag`);
      if (s.status === 'verified') {
        assert.notEqual(s.row, null, `${key} step ${s.step} verified but row null`);
        assert.ok(s.row !== 35 && s.row !== 220, `${key} step ${s.step} verified on jumping row ${s.row}`);
        assert.equal(hf[String(s.row)][5], VERIFIED_BUTTONS[String(s.row)], `${key} step ${s.step} row ${s.row} button mismatch`);
        assert.equal(hf[String(s.row)][4], 0, `${key} step ${s.step} row ${s.row} is a throw row`);
      } else {
        assert.equal(s.row, null, `${key} step ${s.step} ${s.status} must not carry a playable row`);
      }
    }
  }
});

test('2,1,4 flagship: partial on rows 100/153/null (steps 1-2 verified, step 3 unmapped)', () => {
  const p = plans['2,1,4'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [100, 153, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified', 'unmapped']);
  assert.equal(p.string_status, 'partial');
});

test('u+1+2,4 flagship: step 1 unmapped row null, step 2 verified row 183 (jump context, SOFT waived)', () => {
  const p = plans['u+1+2,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, 183]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'verified']);
});

test('u/f+1+2,4 flagship: step 1 unmapped row null, step 2 verified row 183 (jump context, SOFT waived)', () => {
  const p = plans['u/f+1+2,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, 183]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'verified']);
});

test('u/f+2,3,3+4,4 flagship: steps 1-3 unmapped row null, step 4 verified row 183 (jump context, SOFT waived)', () => {
  const p = plans['u/f+2,3,3+4,4'];
  assert.equal(p.steps.length, 4);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null, null, 183]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'unmapped', 'unmapped', 'verified']);
});

test('rest keys have NO plan key (f,F+2, f,n,d,d/f+4, WALL.b,b,u/b)', () => {
  for (const key of ['f,F+2', 'f,n,d,d/f+4', 'WALL.b,b,u/b', 'f,f,F', 'b,B+1+4', 'uf,n,4']) {
    assert.equal(plans[key], undefined, `rest key ${key} must not have a plan`);
  }
});

test('verified-last-step Batch 4 keys are exactly the documented 4', () => {
  assert.equal(B4_VERIFIED_LAST.length, 4);
  for (const key of B4_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B4.filter((k) => !B4_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

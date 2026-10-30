/* Burger Batch 2 step plans (LK3/RK4-only strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/BURGER-BATCH2-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on burger Batch 1 (feat/burger-batch1-step-plans-20261025,
 * PR #1103), which stacks on #1096 (feat/batch1-step-plans-pantera-20261024,
 * the step-playback engine). It does NOT stack on any Pantera plan branch:
 * burger.json plans do not conflict with pantera.json plans.
 * It does NOT include #1097's Pantera Batch 1 follow-up fills (Pantera-specific,
 * and its row-49 SOFT fill is still unapproved); no SOFT fill is inherited here,
 * and Batch 2 wires ZERO Job 3 fills (the single exact+FULL candidate, b+4 row 136,
 * is HELD at review on SOFT proxy fail and never wired).
 * This PR does not touch `fighter.js`: #1096's merge onto post-#1078 main must
 * reconcile #1078's `fighter.js` changes with #1096's engine branch, and that
 * belongs to #1096's merge, not this PR.
 * Rules asserted here (all data-level, no THREE needed):
 *   1. burger.json still has 552 moves / 107 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 155 keys (88 Batch 1 preserved + 67 Batch 2).
 *   3. Batch 2 verified steps always carry a row, and no verified row is 35 or 220;
 *      review/unmapped steps carry row null. No Batch 2 step carries a soft flag
 *      (Batch 2 wires zero SOFT fills).
 *   4. u/f+3+4,4 flagship: verified-all on rows 61/183 (jump context, SOFT waived).
 *   5. u/f+4,4 flagship: verified-all on rows 183/183 (same prefix-move row twice —
 *      that is what the files say: u/f+4 and u/f+4,4 both carry t3_row 183).
 *   6. b+4,3 flagship: step 1 review row null (gate row 111 ground-row rejected;
 *      Job 3 exact+FULL row 136 HELD at review on SOFT proxy fail, never wired).
 *   7. 3,3 flagship: step 1 suspended-drift row null (prefix move 3, row 65 -> None
 *      between #1096 and current main; never wired on stale data).
 *   8. The verified-last-step Batch 2 keys are exactly the 7 listed below,
 *      and verified rows carry the step buttons in the repo Bryan hit_frames.json.
 *   9. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Run: node --test game/tests/burger-batch2-step-plans.test.mjs   (from repo root)
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
const B2 = ["3+4,4", "3,3", "3,4", "3,4~t7.bob", "4,3", "4,3,3+4", "4,3,3+4~t7.bob", "4,3,3+4~t7.bob.2", "4,3,4", "4,3~t7.bob", "4,3~t7.bob.2", "4,4", "WS.3,3+4", "WS.3,3+4~t7.bob", "b+4,3", "b+4,4", "b+4,4~t7.bob", "b+4,4~t7.bob.2", "d+3,4", "d+3,4~t7.bob", "d+3,4~t7.bob.2", "d+4,3", "d+4,3,4", "d+4,3,4~t7.bob", "d+4,3,4~t7.bob.2", "d+4,3,4~t7.bob.3", "d+4,3~t7.bob", "d+4,3~t7.bob.2", "d/b+3+4,4", "d/b+3+4,4~t7.bob", "d/b+4,4", "d/b+4,4,3", "d/b+4,4,3,3", "d/b+4,4,3,3~t7.bob", "d/b+4,4,3,3~t7.bob.2", "d/b+4,4,3,3~t7.bob.3", "d/b+4,4,3~t7.bob", "d/b+4,4,3~t7.bob.2", "d/b+4,4,4", "d/b+4,4,4~t7.bob", "d/b+4,4,4~t7.bob.2", "d/b+4,4~t7.bob", "d/f+3+4,4", "d/f+3+4,4~t7.bob", "d/f+3+4,4~t7.bob.2", "d/f+3,4", "d/f+3,4,4", "d/f+3,4,4~t7.bob", "d/f+3,4,4~t7.bob.2", "d/f+3,4~t7.bob", "db+3+4,4", "db+4,4", "db+4,4,3", "db+4,4,3,3", "df+4,3", "df+4,4", "f+3,4", "f+3,4~t7.bob", "f+3,4~t7.bob.2", "u/f+3+4,4", "u/f+3+4,4~t7.bob", "u/f+3+4,4~t7.bob.2", "u/f+4,4", "u/f+4,4~t7.bob", "ub+3+4,4", "uf+3+4,4", "ws3,3+4"];
const B1 = ["1+2,1+2", "1+2,1+2~t7.bob", "1+2,1+2~t7.bob.2", "1,1", "1,1,2", "1,1,2~t7.bob", "1,1,2~t7.bob.2", "1,1,2~t7.bob.3", "1,1~t7.bob", "1,1~t7.bob.2", "1,2", "1,2,1+2", "1,2,1+2~t7.bob", "1,2,1+2~t7.bob.2", "1,2,2", "1,2~t7.bob", "1,2~t7.bob.2", "2,1", "2,1,2", "2,1~t7.bob", "2,1~t7.bob.2", "2,1~t8.bob", "BAL.1,2", "FC.d/f+2,1", "FC.d/f+2,1,1+2", "FC.d/f+2,1,1+2~t7.bob", "FC.d/f+2,1,1+2~t7.bob.2", "FC.d/f+2,1~t7.bob", "FC.df+2,1", "FC.df+2,1,1+2", "WS.1,2", "WS.1,2~t7.bob", "WS.2,1", "WS.2,1~t7.bob", "WS.2,2", "WS.2,2~t7.bob", "b+1+2,1", "b+1+2,1,2", "b+1+2,1,2~t7.bob", "b+1+2,1,2~t7.bob.2", "b+1+2,1,2~t7.bob.3", "b+1+2,1~t7.bob", "b+1+2,1~t7.bob.2", "b+1,2", "b+1,2~t7.bob", "b+1,2~t7.bob.2", "b+2,1", "b+2,2", "b+2,2~t7.bob", "b+2,2~t7.bob.2", "d+1+2,2", "d+1+2,2,1", "d+1+2,2,1~t7.bob", "d+1+2,2,1~t7.bob.2", "d+1+2,2,1~t7.bob.3", "d+1+2,2,1~t7.bob.4", "d+1+2,2~t7.bob", "d+1+2,2~t7.bob.2", "d+1+2,2~t7.bob.3", "d+2,1", "d+2,1,2", "d+2,1,2,2", "d+2,1,2,2~t7.bob", "d+2,1,2,2~t7.bob.2", "d+2,1,2,2~t7.bob.3", "d+2,1,2,2~t7.bob.4", "d+2,1,2~t7.bob", "d+2,1,2~t7.bob.2", "d+2,1,2~t7.bob.3", "d+2,1~t7.bob", "d+2,1~t7.bob.2", "d/f+1,1+2", "d/f+1,1+2~t7.bob", "d/f+1,2", "d/f+1,2~t7.bob", "df+1,2", "df+1,d+1", "f+2,H.1+2", "f+2,H.1+2,1", "u+1+2,1", "u+1+2,1+2", "u/f+1+2,1+2", "u/f+1+2,1+2~t7.bob", "uf+1,2", "uf+1,2,H.2", "ws1,2", "ws2,1", "ws2,2"];
const B2_VERIFIED_LAST = ["u/f+3+4,4", "u/f+3+4,4~t7.bob", "u/f+3+4,4~t7.bob.2", "u/f+4,4", "u/f+4,4~t7.bob", "ub+3+4,4", "uf+3+4,4"];
const VERIFIED_BUTTONS = {"61": 12, "87": 8, "104": 8, "183": 8, "191": 4};

test('burger move/string counts unchanged by the additive plans block', () => {
  assert.equal(Object.keys(burger.moves).length, 552);
  assert.equal(burger.strings.length, 107);
  assert.equal(Object.keys(plans).length, 155);
});

test('Batch 2 keys are exactly the documented 67; Batch 1 keys all present', () => {
  assert.equal(B2.length, 67);
  for (const key of B2) assert.ok(plans[key], `Batch 2 key ${key} missing`);
  for (const key of B1) assert.ok(plans[key], `Batch 1 key ${key} missing (Batch 1 plans must be preserved)`);
  const extra = Object.keys(plans).filter((k) => !B2.includes(k) && !B1.includes(k));
  assert.deepEqual(extra, []);
});

test('Batch 2 verified steps carry rows (never 35/220); review/unmapped carry row null; no soft flags', () => {
  for (const key of B2) {
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

test('u/f+3+4,4 flagship: verified-all on rows 61/183 (jump context)', () => {
  const p = plans['u/f+3+4,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [61, 183]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('u/f+4,4 flagship: verified-all on rows 183/183', () => {
  const p = plans['u/f+4,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [183, 183]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('b+4,3 flagship: step 1 review row null (row 111 rejected, row 136 held, neither wired)', () => {
  const p = plans['b+4,3'];
  assert.equal(p.steps[0].status, 'review');
  assert.equal(p.steps[0].row, null);
  assert.equal(p.steps[1].status, 'unmapped');
  assert.equal(p.steps[1].row, null);
});

test('3,3 flagship: step 1 suspended-drift row null (prefix move 3, row 65 -> None)', () => {
  const p = plans['3,3'];
  assert.equal(p.steps[0].row, null);
  assert.ok(p.steps[0].reasons.join(' ').includes('SUSPENDED-DRIFT'), '3,3 step 1 must carry the SUSPENDED-DRIFT reason');
});

test('verified-last-step Batch 2 keys are exactly the documented 7', () => {
  assert.equal(B2_VERIFIED_LAST.length, 7);
  for (const key of B2_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B2.filter((k) => !B2_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

/* Burger Batch 1 step plans (LP1/RP2-only strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/BURGER-BATCH1-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on #1096 (feat/batch1-step-plans-pantera-20261024,
 * the step-playback engine). It does NOT stack on the Pantera plan branches
 * (#1099/#1101/#1102): burger.json plans do not conflict with pantera.json plans.
 * It does NOT include #1097's Pantera Batch 1 follow-up fills (Pantera-specific,
 * and its row-49 SOFT fill is still unapproved); no SOFT fill is inherited here.
 * This PR does not touch `fighter.js`: #1096's merge onto post-#1078 main must
 * reconcile #1078's `fighter.js` changes with #1096's engine branch, and that
 * belongs to #1096's merge, not this PR.
 * Rules asserted here (all data-level, no THREE needed):
 *   1. burger.json still has 552 moves / 107 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 155 keys (88 Batch 1 preserved + 67 Batch 2).
 *      (Batch 2 update: this file's exact-88 / no-extra-keys assertions were
 *      replaced by cumulative assertions below. Every Batch 1 CONTENT assertion
 *      — flagships, verified-last-step set, row/button checks — is preserved
 *      verbatim; only the total and the extra-keys set changed, because
 *      Batch 2 keys now legitimately exist. See docs/movesets/
 *      BURGER-BATCH2-STEP-PLANS-2026-10-25.md, test-evolution note.)
 *   3. Batch 1 verified steps always carry a row, and no verified row is 35 or 220;
 *      review/unmapped steps carry row null. No Batch 1 step carries a soft flag
 *      (Batch 1 wires zero SOFT fills — the only Job 3 fill, row 132, is exact
 *      level + FULL provenance + HARD gates + SOFT proxy pass).
 *   4. 2,1 flagship: verified-all on rows 152/153 (recorded-path).
 *   5. 2,1,2 flagship: verified-all on rows 152/153/151 (recorded-path).
 *   6. 1,2,1+2 flagship: step 1 verified row 172, step 2 unmapped row null,
 *      last step verified row 132 (Job 3 fill, exact+FULL).
 *   7. TACKLE.1,1 family (grapple label) has NO plan key.
 *   8. The verified-last-step Batch 1 keys are exactly the 8 listed below,
 *      and verified rows carry the step buttons in the repo Bryan hit_frames.json.
 *   9. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Run: node --test game/tests/burger-batch1-step-plans.test.mjs   (from repo root)
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
const B1 = ["1+2,1+2", "1+2,1+2~t7.bob", "1+2,1+2~t7.bob.2", "1,1", "1,1,2", "1,1,2~t7.bob", "1,1,2~t7.bob.2", "1,1,2~t7.bob.3", "1,1~t7.bob", "1,1~t7.bob.2", "1,2", "1,2,1+2", "1,2,1+2~t7.bob", "1,2,1+2~t7.bob.2", "1,2,2", "1,2~t7.bob", "1,2~t7.bob.2", "2,1", "2,1,2", "2,1~t7.bob", "2,1~t7.bob.2", "2,1~t8.bob", "BAL.1,2", "FC.d/f+2,1", "FC.d/f+2,1,1+2", "FC.d/f+2,1,1+2~t7.bob", "FC.d/f+2,1,1+2~t7.bob.2", "FC.d/f+2,1~t7.bob", "FC.df+2,1", "FC.df+2,1,1+2", "WS.1,2", "WS.1,2~t7.bob", "WS.2,1", "WS.2,1~t7.bob", "WS.2,2", "WS.2,2~t7.bob", "b+1+2,1", "b+1+2,1,2", "b+1+2,1,2~t7.bob", "b+1+2,1,2~t7.bob.2", "b+1+2,1,2~t7.bob.3", "b+1+2,1~t7.bob", "b+1+2,1~t7.bob.2", "b+1,2", "b+1,2~t7.bob", "b+1,2~t7.bob.2", "b+2,1", "b+2,2", "b+2,2~t7.bob", "b+2,2~t7.bob.2", "d+1+2,2", "d+1+2,2,1", "d+1+2,2,1~t7.bob", "d+1+2,2,1~t7.bob.2", "d+1+2,2,1~t7.bob.3", "d+1+2,2,1~t7.bob.4", "d+1+2,2~t7.bob", "d+1+2,2~t7.bob.2", "d+1+2,2~t7.bob.3", "d+2,1", "d+2,1,2", "d+2,1,2,2", "d+2,1,2,2~t7.bob", "d+2,1,2,2~t7.bob.2", "d+2,1,2,2~t7.bob.3", "d+2,1,2,2~t7.bob.4", "d+2,1,2~t7.bob", "d+2,1,2~t7.bob.2", "d+2,1,2~t7.bob.3", "d+2,1~t7.bob", "d+2,1~t7.bob.2", "d/f+1,1+2", "d/f+1,1+2~t7.bob", "d/f+1,2", "d/f+1,2~t7.bob", "df+1,2", "df+1,d+1", "f+2,H.1+2", "f+2,H.1+2,1", "u+1+2,1", "u+1+2,1+2", "u/f+1+2,1+2", "u/f+1+2,1+2~t7.bob", "uf+1,2", "uf+1,2,H.2", "ws1,2", "ws2,1", "ws2,2"];
const B1_VERIFIED_LAST = ["1,2,1+2", "1,2,1+2~t7.bob", "1,2,1+2~t7.bob.2", "2,1", "2,1,2", "2,1~t7.bob", "2,1~t7.bob.2", "2,1~t8.bob"];
const VERIFIED_BUTTONS = {"172": 1, "132": 3, "152": 2, "153": 1, "151": 2, "146": 1, "150": 2};

test('burger move/string counts unchanged by the additive plans block', () => {
  assert.equal(Object.keys(burger.moves).length, 552);
  assert.equal(burger.strings.length, 107);
  assert.equal(Object.keys(plans).length, 155);
});

test('Batch 1 keys are all present; extra keys are exactly the documented Batch 2 67', () => {
  assert.equal(B1.length, 88);
  for (const key of B1) assert.ok(plans[key], `Batch 1 key ${key} missing`);
  const B2 = ["3+4,4", "3,3", "3,4", "3,4~t7.bob", "4,3", "4,3,3+4", "4,3,3+4~t7.bob", "4,3,3+4~t7.bob.2", "4,3,4", "4,3~t7.bob", "4,3~t7.bob.2", "4,4", "WS.3,3+4", "WS.3,3+4~t7.bob", "b+4,3", "b+4,4", "b+4,4~t7.bob", "b+4,4~t7.bob.2", "d+3,4", "d+3,4~t7.bob", "d+3,4~t7.bob.2", "d+4,3", "d+4,3,4", "d+4,3,4~t7.bob", "d+4,3,4~t7.bob.2", "d+4,3,4~t7.bob.3", "d+4,3~t7.bob", "d+4,3~t7.bob.2", "d/b+3+4,4", "d/b+3+4,4~t7.bob", "d/b+4,4", "d/b+4,4,3", "d/b+4,4,3,3", "d/b+4,4,3,3~t7.bob", "d/b+4,4,3,3~t7.bob.2", "d/b+4,4,3,3~t7.bob.3", "d/b+4,4,3~t7.bob", "d/b+4,4,3~t7.bob.2", "d/b+4,4,4", "d/b+4,4,4~t7.bob", "d/b+4,4,4~t7.bob.2", "d/b+4,4~t7.bob", "d/f+3+4,4", "d/f+3+4,4~t7.bob", "d/f+3+4,4~t7.bob.2", "d/f+3,4", "d/f+3,4,4", "d/f+3,4,4~t7.bob", "d/f+3,4,4~t7.bob.2", "d/f+3,4~t7.bob", "db+3+4,4", "db+4,4", "db+4,4,3", "db+4,4,3,3", "df+4,3", "df+4,4", "f+3,4", "f+3,4~t7.bob", "f+3,4~t7.bob.2", "u/f+3+4,4", "u/f+3+4,4~t7.bob", "u/f+3+4,4~t7.bob.2", "u/f+4,4", "u/f+4,4~t7.bob", "ub+3+4,4", "uf+3+4,4", "ws3,3+4"];
  assert.equal(B2.length, 67);
  for (const key of B2) assert.ok(plans[key], `Batch 2 key ${key} missing`);
  const extra = Object.keys(plans).filter((k) => !B1.includes(k) && !B2.includes(k));
  assert.deepEqual(extra, []);
});

test('Batch 1 verified steps carry rows (never 35/220); review/unmapped carry row null; no soft flags', () => {
  for (const key of B1) {
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

test('2,1 flagship: verified-all on rows 152/153 (recorded-path)', () => {
  const p = plans['2,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [152, 153]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('2,1,2 flagship: verified-all on rows 152/153/151 (recorded-path)', () => {
  const p = plans['2,1,2'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [152, 153, 151]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('1,2,1+2 flagship: step 1 verified row 172, step 2 unmapped, last step verified row 132 (Job 3 fill)', () => {
  const p = plans['1,2,1+2'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [172, null, 132]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'unmapped', 'verified']);
  assert.equal(p.last_step_status, 'verified');
  assert.equal(p.last_step_row, 132);
});

test('TACKLE.1,1 family (grapple label) has NO plan key', () => {
  assert.ok(!plans['TACKLE.1,1']);
  assert.ok(!plans['TACKLE.1,1,1']);
  assert.ok(!plans['TACKLE.1,1,1,1']);
});

test('verified-last-step Batch 1 keys are exactly the documented 8', () => {
  assert.equal(B1_VERIFIED_LAST.length, 8);
  for (const key of B1_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B1.filter((k) => !B1_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

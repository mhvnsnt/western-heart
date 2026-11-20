/* Batch 2 step plans (Pantera LK3/RK4 strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/BATCH2-STEP-PLANS-2026-10-25.md.
 * Stack: originally stacked on #1096 (feat/batch1-step-plans-pantera-20261024).
 * Landed 2026-10-30 by the step-plan dependents wave, rebased onto main AFTER
 * #1232 (Real-Moves Batch 1 fills) and #1236 (the #1097 follow-up: b+2,1+2
 * family -> verified/97, u/b+1,1 and u/b+1,2 first steps -> verified-SOFT/49)
 * had merged, exactly as this header originally instructed. The Batch 1 guard
 * map below is therefore CURRENT MAIN's record, not #1096's: the guard's
 * intent is unchanged (Batch 2 must not alter any Batch 1 key).
 * Rules asserted here (all data-level, no THREE needed):
 *   1. pantera.json still has 874 moves / 81 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 87 keys (60 Batch 1 + 27 Batch 2).
 *   3. Every Batch 1 key keeps its current-main last_step_status (Batch 2 adds keys only).
 *   4. Batch 2 verified steps always carry a row, and no verified row is 35 or 220;
 *      review/unmapped steps carry row null. No Batch 2 step carries a soft flag
 *      (Batch 2 wires zero SOFT fills).
 *   5. d/f+4,4 flagship: step 1 review candidate 135 row null; step 2 verified row 197.
 *   6. d+3+4,4~t3.king: the variant's own row 197 never enters its steps (whole-string
 *      rows are not step rows); its plan is unmapped-all, inherited from d+3+4,4.
 *   7. The verified-last-step Batch 2 keys are exactly ['d/f+4,4'], and verified row
 *      197 has button 8 (RK4) in the repo King hit_frames.json.
 *   8. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by Batch 2; behaviour is play-verified).
 * Run: node --test game/tests/batch2-step-plans.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const pantera = JSON.parse(readFileSync(join(ROOT, 'game/assets/movesets/pantera.json'), 'utf8'));
const fighterSrc = readFileSync(join(ROOT, 'game/js/fighter.js'), 'utf8');
const hfPath = join(ROOT, 'game/assets/anim/t3/king_on_pantera_leoman/hit_frames.json');
const hf = JSON.parse(readFileSync(hfPath, 'utf8')).rows;

const plans = pantera.string_step_plans.plans;
// Current-main record (post-#1232 + post-#1236): last_step_status per Batch 1 plan key.
const B1 = {"1+2,1":"review","1+2,1~t7.king":"review","1+2,1~t7.king.2":"review","1,1":"unmapped","1,2":"review","1,2,1":"review","1,2,1~t7.king":"review","1,2,1~t7.king.2":"review","1,2,1~t7.king.3":"review","1,2~t7.king":"review","1,2~t7.king.2":"review","2,1":"unmapped","2,1~t7.king":"unmapped","2,1~t7.king.2":"unmapped","2,1~t8.king":"unmapped","FC.1,2":"review","FC.1,2~t7.king":"review","WS.2,2":"unmapped","WS.2,2~t7.king":"unmapped","b+1+2,1+2":"unmapped","b+1+2,2":"verified","b+1,2":"unmapped","b+1,2~t7.king":"unmapped","b+1,2~t7.king.2":"unmapped","b+2,1":"review","b+2,1+2":"verified","b+2,1+2~t7.king":"verified","b+2,1+2~t7.king.2":"verified","b+2,1~t7.king":"review","b+2,1~t7.king.2":"review","d+1+2,2":"verified","d+1+2,2,1":"verified","d+1+2,2,1,1":"review","d+1+2,2,1,1,2":"review","d+1,2":"unmapped","d/b+1+2,2":"verified","d/f+1,2":"unmapped","d/f+1,2~t7.king":"unmapped","d/f+2,1":"unmapped","d/f+2,1~t7.king":"unmapped","df+1,2":"unmapped","df+2,1":"unmapped","f+2,1":"review","f+2,1,1":"review","f+2,1,1,2":"review","f+2,1~t3.king":"verified","f+2,1~t7.king":"review","f+2,1~t7.king.2":"review","f+2,d+1":"unmapped","f+2,d+1,2":"unmapped","f+2,d+1,2~t7.king":"unmapped","f+2,d+1,2~t7.king.2":"unmapped","f+2,d+1,2~t7.king.3":"unmapped","u+1,1":"verified","u+1,2":"verified","u/b+1,1":"verified","u/b+1,2":"verified","u/f+1,1":"verified","u/f+1,2":"verified","ws2,2":"unmapped"};
const B2 = ['CH.d+3+4,4,4,4', 'FC.d/f+4,4', 'FC.d/f+4,4,4', 'd+3+4,4', 'd+3+4,4,4', 'd+3+4,4,4,4', 'd+3+4,4,4~t7.king', 'd+3+4,4,4~t7.king.2', 'd+3+4,4,4~t7.king.3', 'd+3+4,4~t3.king', 'd+3+4,4~t7.king', 'd+3+4,4~t7.king.2', 'd/f+3,4', 'd/f+3,4~t7.king', 'd/f+4,3', 'd/f+4,3,4', 'd/f+4,3,4~t7.king', 'd/f+4,3,4~t7.king.2', 'd/f+4,3,d+4', 'd/f+4,3,d+4~t7.king', 'd/f+4,3,d+4~t7.king.2', 'd/f+4,3~t7.king', 'd/f+4,4', 'df+3,4', 'df+4,3', 'df+4,3,4', 'df+4,3,d+4'];

test('pantera move/string counts unchanged by the additive plans block', () => {
  assert.equal(Object.keys(pantera.moves).length, 874);
  assert.equal(pantera.strings.length, 81);
  assert.equal(Object.keys(plans).length, 87);
});

test('Batch 1 keys keep their current-main last_step_status', () => {
  assert.equal(Object.keys(B1).length, 60);
  for (const [key, want] of Object.entries(B1)) {
    assert.ok(plans[key], `Batch 1 key ${key} missing`);
    assert.equal(plans[key].last_step_status, want, `${key} last step changed from current main`);
  }
});

test('Batch 2 keys are exactly the documented 27', () => {
  assert.equal(B2.length, 27);
  for (const key of B2) assert.ok(plans[key], `Batch 2 key ${key} missing`);
  const extra = Object.keys(plans).filter((k) => !(k in B1) && !B2.includes(k));
  assert.deepEqual(extra, []);
});

test('Batch 2 verified steps carry rows (never 35/220); review/unmapped carry row null; no soft flags', () => {
  for (const key of B2) {
    for (const s of plans[key].steps) {
      assert.ok(!('soft' in s) || s.soft !== true, `${key} step ${s.step} carries a soft flag`);
      if (s.status === 'verified') {
        assert.notEqual(s.row, null, `${key} step ${s.step} verified but row null`);
        assert.ok(s.row !== 35 && s.row !== 220, `${key} step ${s.step} verified on jumping row ${s.row}`);
      } else {
        assert.equal(s.row, null, `${key} step ${s.step} ${s.status} must not carry a playable row`);
      }
    }
  }
});

test('d/f+4,4 flagship: step 1 review candidate 135 row null; step 2 verified row 197', () => {
  const p = plans['d/f+4,4'];
  assert.equal(p.steps.length, 2);
  assert.equal(p.steps[0].status, 'review');
  assert.equal(p.steps[0].candidate_row, 135);
  assert.equal(p.steps[0].row, null);
  assert.equal(p.steps[1].status, 'verified');
  assert.equal(p.steps[1].row, 197);
  assert.equal(p.last_step_status, 'verified');
  assert.equal(p.last_step_row, 197);
});

test('d+3+4,4~t3.king: own row 197 never enters its steps; plan unmapped-all', () => {
  assert.equal(pantera.moves['d+3+4,4~t3.king'].t3_row, 197);
  const p = plans['d+3+4,4~t3.king'];
  assert.equal(p.string_status, 'unmapped-all');
  assert.equal(p.last_step_status, 'unmapped');
  assert.equal(p.last_step_row, null);
  assert.equal(p.twin_of, 'd+3+4,4');
});

test('verified-last-step Batch 2 keys are exactly [d/f+4,4]; row 197 button is 8 (RK4)', () => {
  const got = B2.filter((k) => plans[k].last_step_status === 'verified').sort();
  assert.deepEqual(got, ['d/f+4,4']);
  // hit_frames row format: [active_first, active_last, stream_frames, attack_word, throw, button]
  assert.equal(hf['197'][5], 8);
  assert.equal(hf['197'][4], 0);
});

test('fighter.js step-plan branch markers exist (engine inherited from #1096)', () => {
  assert.ok(fighterSrc.includes('_resolveStepPlan'), 'missing _resolveStepPlan');
  assert.ok(fighterSrc.includes('_stepChain'), 'missing _stepChain');
  assert.ok(fighterSrc.includes('[WH-STEP-PLAN]'), 'missing unmapped flag log');
});

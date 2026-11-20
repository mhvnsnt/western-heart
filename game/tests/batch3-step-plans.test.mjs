/* Batch 3 step plans (Pantera mixed-pair strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/BATCH3-STEP-PLANS-2026-10-25.md.
 * Stack: originally stacked on #1099 (feat/batch2-step-plans-pantera-20261025).
 * Landed 2026-10-30 by the step-plan dependents wave, rebased onto main AFTER
 * #1232 (Real-Moves Batch 1 fills), #1236 (the #1097 follow-up: b+2,1+2 family
 * -> verified, u/b+1,1 and u/b+1,2 first steps -> verified-SOFT) and #1099
 * (Batch 2) had merged, as this header originally instructed. The Batch 1 guard
 * map below is therefore CURRENT MAIN's record, not #1096's; the Batch 2 guard
 * map is #1099's record as landed. Guard intent unchanged: Batch 3 alters no
 * earlier key.
 * Rules asserted here (all data-level, no THREE needed):
 *   1. pantera.json still has 874 moves / 81 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 136 keys (60 Batch 1 + 27 Batch 2 + 49 Batch 3).
 *   3. Every Batch 1 key keeps its current-main last_step_status and every Batch 2 key
 *      keeps its #1099 last_step_status (Batch 3 adds keys only).
 *   4. Batch 3 verified steps always carry a row, and no verified row is 35 or 220;
 *      review/unmapped steps carry row null. No Batch 3 step carries a soft flag
 *      (Batch 3 wires zero SOFT fills — the u/b+1 Job 3 soft candidates are
 *      documented, never wired, and nothing is inherited from #1097).
 *   5. 3,2 flagship: step 1 verified row 264 (the single LK3 move's own row,
 *      gate-verified for the LK3 step); step 2 unmapped row null (the 3,2
 *      string itself is T8-sourced with no T3 row); the old donor row 99
 *      plays for neither step.
 *   6. u/f+1,3 flagship: verified-all, step 1 row 36, step 2 row 55.
 *   7. u/b+1,3 step 1 is unmapped row null with candidate 37 — the Job 3 soft
 *      candidates 36/47/48/49 are NOT wired here (no SOFT inheritance from #1097).
 *   8. d/f+4,2 review-only: step 1 review candidate 135 row null; step 2 review
 *      candidate 196 row null.
 *   9. AB1.2,4,2+4 (throw class) has NO plan key.
 *  10. The verified-last-step Batch 3 keys are exactly the 24 jump-string keys,
 *      and verified rows 264/54/55/56/72/73/74/36 carry the step buttons
 *      (4/4/4/4/8/8/8/1) in the repo King hit_frames.json.
 *  11. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096 via #1099, not changed by Batch 3; behaviour is play-verified).
 * Run: node --test game/tests/batch3-step-plans.test.mjs   (from repo root)
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
const B1 = {"1+2,1": "review", "1+2,1~t7.king": "review", "1+2,1~t7.king.2": "review", "1,1": "unmapped", "1,2": "review", "1,2,1": "review", "1,2,1~t7.king": "review", "1,2,1~t7.king.2": "review", "1,2,1~t7.king.3": "review", "1,2~t7.king": "review", "1,2~t7.king.2": "review", "2,1": "unmapped", "2,1~t7.king": "unmapped", "2,1~t7.king.2": "unmapped", "2,1~t8.king": "unmapped", "FC.1,2": "review", "FC.1,2~t7.king": "review", "WS.2,2": "unmapped", "WS.2,2~t7.king": "unmapped", "b+1+2,1+2": "unmapped", "b+1+2,2": "verified", "b+1,2": "unmapped", "b+1,2~t7.king": "unmapped", "b+1,2~t7.king.2": "unmapped", "b+2,1": "review", "b+2,1+2": "verified", "b+2,1+2~t7.king": "verified", "b+2,1+2~t7.king.2": "verified", "b+2,1~t7.king": "review", "b+2,1~t7.king.2": "review", "d+1+2,2": "verified", "d+1+2,2,1": "verified", "d+1+2,2,1,1": "review", "d+1+2,2,1,1,2": "review", "d+1,2": "unmapped", "d/b+1+2,2": "verified", "d/f+1,2": "unmapped", "d/f+1,2~t7.king": "unmapped", "d/f+2,1": "unmapped", "d/f+2,1~t7.king": "unmapped", "df+1,2": "unmapped", "df+2,1": "unmapped", "f+2,1": "review", "f+2,1,1": "review", "f+2,1,1,2": "review", "f+2,1~t3.king": "verified", "f+2,1~t7.king": "review", "f+2,1~t7.king.2": "review", "f+2,d+1": "unmapped", "f+2,d+1,2": "unmapped", "f+2,d+1,2~t7.king": "unmapped", "f+2,d+1,2~t7.king.2": "unmapped", "f+2,d+1,2~t7.king.3": "unmapped", "u+1,1": "verified", "u+1,2": "verified", "u/b+1,1": "verified", "u/b+1,2": "verified", "u/f+1,1": "verified", "u/f+1,2": "verified", "ws2,2": "unmapped"};
// #1099 record: last_step_status per Batch 2 plan key.
const B2 = {"CH.d+3+4,4,4,4": "unmapped", "FC.d/f+4,4": "unmapped", "FC.d/f+4,4,4": "unmapped", "d+3+4,4": "unmapped", "d+3+4,4,4": "unmapped", "d+3+4,4,4,4": "unmapped", "d+3+4,4,4~t7.king": "unmapped", "d+3+4,4,4~t7.king.2": "unmapped", "d+3+4,4,4~t7.king.3": "unmapped", "d+3+4,4~t3.king": "unmapped", "d+3+4,4~t7.king": "unmapped", "d+3+4,4~t7.king.2": "unmapped", "d/f+3,4": "unmapped", "d/f+3,4~t7.king": "unmapped", "d/f+4,3": "unmapped", "d/f+4,3,4": "unmapped", "d/f+4,3,4~t7.king": "unmapped", "d/f+4,3,4~t7.king.2": "unmapped", "d/f+4,3,d+4": "unmapped", "d/f+4,3,d+4~t7.king": "unmapped", "d/f+4,3,d+4~t7.king.2": "unmapped", "d/f+4,3~t7.king": "unmapped", "d/f+4,4": "verified", "df+3,4": "unmapped", "df+4,3": "unmapped", "df+4,3,4": "unmapped", "df+4,3,d+4": "unmapped"};
const B3 = ["1+3,1", "1+3,1~t3.king", "1+4,1", "1+4,1,1", "1+4,1,1~t3.king", "1+4,1~t3.king", "1+4,1~t3.king.2", "1+4,1~t3.king.3", "1+4,1~t3.king.4", "3,2", "3,2,2", "3,2,2*", "JGS.3,2+3", "b+1,4", "b+1,4~t7.king", "b+1,4~t7.king.2", "b+2,4", "b+2,4~t7.king", "d+1+3,1", "d/b+1+3,1", "d/b+1+3,1~t3.king", "d/b+1+3,1~t3.king.2", "d/b+1+3,1~t3.king.3", "d/b+1+3,1~t3.king.4", "d/f+4,2", "u+1,3", "u+1,3~t3.king", "u+1,3~t3.king.2", "u+1,3~t3.king.3", "u+1,4", "u+1,4~t3.king", "u+1,4~t3.king.2", "u+1,4~t3.king.3", "u/b+1,3", "u/b+1,3~t3.king", "u/b+1,3~t3.king.2", "u/b+1,3~t3.king.3", "u/b+1,4", "u/b+1,4~t3.king", "u/b+1,4~t3.king.2", "u/b+1,4~t3.king.3", "u/f+1,3", "u/f+1,3~t3.king", "u/f+1,3~t3.king.2", "u/f+1,3~t3.king.3", "u/f+1,4", "u/f+1,4~t3.king", "u/f+1,4~t3.king.2", "u/f+1,4~t3.king.3"];

test('pantera move/string counts unchanged by the additive plans block', () => {
  assert.equal(Object.keys(pantera.moves).length, 874);
  assert.equal(pantera.strings.length, 81);
  assert.equal(Object.keys(plans).length, 136);
});

test('Batch 1 keys keep their current-main last_step_status', () => {
  assert.equal(Object.keys(B1).length, 60);
  for (const [key, want] of Object.entries(B1)) {
    assert.ok(plans[key], `Batch 1 key ${key} missing`);
    assert.equal(plans[key].last_step_status, want, `${key} last step changed from current main`);
  }
});

test('Batch 2 keys keep their #1099 last_step_status', () => {
  assert.equal(Object.keys(B2).length, 27);
  for (const [key, want] of Object.entries(B2)) {
    assert.ok(plans[key], `Batch 2 key ${key} missing`);
    assert.equal(plans[key].last_step_status, want, `${key} last step changed from #1099`);
  }
});

test('Batch 3 keys are exactly the documented 49', () => {
  assert.equal(B3.length, 49);
  for (const key of B3) assert.ok(plans[key], `Batch 3 key ${key} missing`);
  const extra = Object.keys(plans).filter((k) => !(k in B1) && !(k in B2) && !B3.includes(k));
  assert.deepEqual(extra, []);
});

test('Batch 3 verified steps carry rows (never 35/220); review/unmapped carry row null; no soft flags', () => {
  for (const key of B3) {
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

test('3,2 flagship: step 1 verified row 264; step 2 unmapped row null; donor 99 retired', () => {
  const p = plans['3,2'];
  assert.equal(p.steps.length, 2);
  assert.equal(p.steps[0].status, 'verified');
  assert.equal(p.steps[0].row, 264);
  assert.equal(p.steps[0].candidate_source, 'prefix-move');
  assert.equal(p.steps[1].status, 'unmapped');
  assert.equal(p.steps[1].row, null);
  assert.equal(p.last_step_status, 'unmapped');
  assert.equal(p.last_step_row, null);
  assert.equal(pantera.moves['3'].t3_row, 264);
  assert.ok(pantera.moves['3,2'].t3_row == null, '3,2 has no T3 row (key absent)');
});

test('u/f+1,3 flagship: verified-all, rows 36/55', () => {
  const p = plans['u/f+1,3'];
  assert.equal(p.string_status, 'verified-all');
  assert.equal(p.steps.length, 2);
  assert.equal(p.steps[0].row, 36);
  assert.equal(p.steps[1].row, 55);
  assert.equal(p.last_step_status, 'verified');
  assert.equal(p.last_step_row, 55);
});

test('u/b+1,3 step 1 unmapped with candidate 37 — Job 3 soft candidates NOT wired', () => {
  const p = plans['u/b+1,3'];
  assert.equal(p.steps[0].status, 'unmapped');
  assert.equal(p.steps[0].row, null);
  assert.equal(p.steps[0].candidate_row, 37);
  assert.ok(!('soft' in p.steps[0]) || p.steps[0].soft !== true);
  assert.ok(p.steps[0].reasons.join(' ').includes('NOT wired (soft-filed'));
});

test('d/f+4,2 review-only: candidates 135/196, rows null', () => {
  const p = plans['d/f+4,2'];
  assert.equal(p.string_status, 'review-only');
  assert.equal(p.steps[0].status, 'review');
  assert.equal(p.steps[0].candidate_row, 135);
  assert.equal(p.steps[0].row, null);
  assert.equal(p.steps[1].status, 'review');
  assert.equal(p.steps[1].candidate_row, 196);
  assert.equal(p.steps[1].row, null);
});

test('AB1.2,4,2+4 (throw class) has no plan key', () => {
  assert.equal(plans['AB1.2,4,2+4'], undefined);
  assert.equal(pantera.moves['AB1.2,4,2+4'].move_class, 'throw');
});

test('verified-last-step Batch 3 keys are exactly the 24 jump keys; verified rows carry step buttons', () => {
  const got = B3.filter((k) => plans[k].last_step_status === 'verified').sort();
  assert.deepEqual(got, ["u+1,3", "u+1,3~t3.king", "u+1,3~t3.king.2", "u+1,3~t3.king.3", "u+1,4", "u+1,4~t3.king", "u+1,4~t3.king.2", "u+1,4~t3.king.3", "u/b+1,3", "u/b+1,3~t3.king", "u/b+1,3~t3.king.2", "u/b+1,3~t3.king.3", "u/b+1,4", "u/b+1,4~t3.king", "u/b+1,4~t3.king.2", "u/b+1,4~t3.king.3", "u/f+1,3", "u/f+1,3~t3.king", "u/f+1,3~t3.king.2", "u/f+1,3~t3.king.3", "u/f+1,4", "u/f+1,4~t3.king", "u/f+1,4~t3.king.2", "u/f+1,4~t3.king.3"]);
  // hit_frames row format: [active_first, active_last, stream_frames, attack_word, throw, button]
  assert.equal(hf['264'][5], 4);
  assert.equal(hf['264'][4], 0);
  assert.equal(hf['54'][5], 4);
  assert.equal(hf['55'][5], 4);
  assert.equal(hf['56'][5], 4);
  assert.equal(hf['72'][5], 8);
  assert.equal(hf['73'][5], 8);
  assert.equal(hf['74'][5], 8);
  assert.equal(hf['36'][5], 1);
  assert.equal(hf['36'][4], 0);
});

test('fighter.js step-plan branch markers exist (engine inherited from #1096 via #1099)', () => {
  assert.ok(fighterSrc.includes('_resolveStepPlan'), 'missing _resolveStepPlan');
  assert.ok(fighterSrc.includes('_stepChain'), 'missing _stepChain');
  assert.ok(fighterSrc.includes('[WH-STEP-PLAN]'), 'missing unmapped flag log');
});

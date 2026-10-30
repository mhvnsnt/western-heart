/* Batch 4 step plans (Pantera triples/quads/rest strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/BATCH4-STEP-PLANS-2026-10-25.md.
 * Stack: originally stacked on #1101 (feat/batch3-step-plans-pantera-20261025).
 * Landed 2026-10-30 by the step-plan dependents wave, rebased onto main AFTER
 * #1232 (Real-Moves Batch 1 fills), #1236 (the #1097 follow-up: b+2,1+2 family
 * -> verified, u/b+1,1 and u/b+1,2 first steps -> verified-SOFT), #1099 and
 * #1101 had merged, as this header originally instructed. The Batch 1 guard map
 * below is therefore CURRENT MAIN's record, not #1096's; Batch 2 is #1099's
 * record and Batch 3 is #1101's record, both as landed. This PR does not touch
 * `fighter.js`: #1096's merge onto
 * post-#1078 main must reconcile #1078's `fighter.js` changes with #1096's
 * engine branch, and that belongs to #1096's merge, not this PR.
 * Rules asserted here (all data-level, no THREE needed):
 *   1. pantera.json still has 874 moves / 81 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 208 keys (60 Batch 1 + 27 Batch 2 + 49 Batch 3 + 72 Batch 4).
 *   3. Every Batch 1/2/3 key keeps its earlier last_step_status (Batch 4 adds keys only).
 *   4. Batch 4 verified steps always carry a row, and no verified row is 35 or 220;
 *      review/unmapped steps carry row null. No Batch 4 step carries a soft flag
 *      (Batch 4 wires zero SOFT fills — the u/b+1 Job 3 soft candidates are
 *      documented, never wired, and nothing is inherited from #1097).
 *   5. u+1,2+4 flagship: step 1 unmapped row null; step 2 verified row 243 (jump context, SOFT waived).
 *   6. d+1+2,2,1,1,2,4 flagship: steps verified on rows 97/98/198, steps 4-5 review (257/258),
 *      last step verified row 259 (recorded-dest).
 *   7. PILE_DRIVER.1+2,3,4,1+2 (grapple label) and f,F+1 (rest) have NO plan key.
 *   8. The verified-last-step Batch 4 keys are exactly the 12 listed below,
 *      and verified rows carry the step buttons in the repo King hit_frames.json.
 *   9. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096 via #1099/#1101, not changed by Batch 4; behaviour is play-verified).
 * Run: node --test game/tests/batch4-step-plans.test.mjs   (from repo root)
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
// #1101 record: last_step_status per Batch 3 plan key.
const B3 = {"1+3,1": "unmapped", "1+3,1~t3.king": "unmapped", "1+4,1": "unmapped", "1+4,1,1": "unmapped", "1+4,1,1~t3.king": "unmapped", "1+4,1~t3.king": "unmapped", "1+4,1~t3.king.2": "unmapped", "1+4,1~t3.king.3": "unmapped", "1+4,1~t3.king.4": "unmapped", "3,2": "unmapped", "3,2,2": "unmapped", "3,2,2*": "unmapped", "JGS.3,2+3": "unmapped", "b+1,4": "unmapped", "b+1,4~t7.king": "unmapped", "b+1,4~t7.king.2": "unmapped", "b+2,4": "unmapped", "b+2,4~t7.king": "unmapped", "d+1+3,1": "unmapped", "d/b+1+3,1": "unmapped", "d/b+1+3,1~t3.king": "unmapped", "d/b+1+3,1~t3.king.2": "unmapped", "d/b+1+3,1~t3.king.3": "unmapped", "d/b+1+3,1~t3.king.4": "unmapped", "d/f+4,2": "review", "u+1,3": "verified", "u+1,3~t3.king": "verified", "u+1,3~t3.king.2": "verified", "u+1,3~t3.king.3": "verified", "u+1,4": "verified", "u+1,4~t3.king": "verified", "u+1,4~t3.king.2": "verified", "u+1,4~t3.king.3": "verified", "u/b+1,3": "verified", "u/b+1,3~t3.king": "verified", "u/b+1,3~t3.king.2": "verified", "u/b+1,3~t3.king.3": "verified", "u/b+1,4": "verified", "u/b+1,4~t3.king": "verified", "u/b+1,4~t3.king.2": "verified", "u/b+1,4~t3.king.3": "verified", "u/f+1,3": "verified", "u/f+1,3~t3.king": "verified", "u/f+1,3~t3.king.2": "verified", "u/f+1,3~t3.king.3": "verified", "u/f+1,4": "verified", "u/f+1,4~t3.king": "verified", "u/f+1,4~t3.king.2": "verified", "u/f+1,4~t3.king.3": "verified"};
const B4 = ["1+2,3", "1+2,3~t7.king", "1+2,3~t7.king.2", "1,2,1,1,2,4,4,4,1,3", "1,2,1,1,3,3,4,3,2,1+2", "2+3,1", "2+4,1", "2+4,1~t3.king", "2+4,1~t3.king.2", "BACKDROP.1+2,3,4,1+3", "BACKDROP.1+2,4,1+2,1+2+3", "BACKDROP.3+4,1+2", "BURNING_HAMMER.2+4,3+4,1+3,1+2,1+2+3", "CANNONBALL_BUSTER.3+4,1+2,1+2+4", "CHICKEN_WING_FACE_LOCK.1+3,3+4,2+4,1+2,1+2+3", "CHICKEN_WING_FACE_LOCK.2,1,3,1+2+4,1+2+4", "COBRA_CLUTCH.1,4,2,3", "COBRA_CLUTCH.2+4,1+2,1+2", "COBRA_CLUTCH.3+4,3+4,1+2", "COBRA_TWIST.2,1,1+3", "DOUBLE_HEEL_HOLD.2,1,3,4", "GERMAN_SUPLEX.1,2,3+4", "HEAD_JAMMER.4,3,4,3+4,1+2", "INDIAN_DEATH_LOCK.1,3,4,1+2,3+4", "MANHATTAN_DROP.1,2,3+4,1+2", "POWER_BOMB.2,1,3,4", "POWER_BOMB.3,1,2,3+4,1+2+3+4", "REVERSE_DDT.1+2,1,2,1+2+3", "REVERSE_DDT.2,3,1,1+2", "REVERSE_SPECIAL_STRETCH_BOMB.3+4,1+2", "SLEEPER.3,4,1+2,3+4", "STANDING_HEEL_HOLD.1+2,1,3,1+2", "STANDING_HEEL_HOLD.1+2,3,1,1+3", "STANDING_HEEL_HOLD.1,2,3,1+2", "VICTORY_BOMB.2,1,3,4", "VICTORY_BOMB.3,1,2,3+4,1+2+3+4", "b+1+2,1,1+3", "b+1+2,1,2+4", "b+1+2,1,3+4", "d+1+2,2,1,1,2,4", "d+1+2,2,1,1,3", "d+1+2,2,1,1,3,3", "d+3+4,2", "d+3+4,2,1", "d+3+4,4,1", "d+3+4,4,1,4", "d+3+4,4,1,4,4", "d+3+4,4,1,4,4,1", "d+3+4,4,1,4~t3.king", "d+3+4,4,1~t3.king", "d+3+4,4,4,2", "d/b+2+4,1", "d/b+2+4,d/b+1", "d/f+2+3,1", "d/f+3+4,1", "db+1+2,3+4", "f+2,1,1,2,4", "f+2,1,1,2,4,4", "f+2,1,1,2,4,4,4", "f+2,1,1,2,4,4,4,1", "f+2,1,1,2,4,4,4,1,1", "f+2,1,1,2,4,4,4,1,3", "f+2,1,1,3", "f+2,1,1,3,3", "f+2,1,1,3,3,4", "f+2,1,1,3,3,4,3", "f+2,1,1,3,3,4,3,2", "f+2,1,1,3,3,4,3,2,1+2", "f+2,1,1,3,3,4,3,2,1+2,1", "f+2,1,1,3,3,4,3,2,1+2~t3.king", "u+1,2+4", "u/b+1,2+4"];
const B4_VERIFIED_LAST = ["d+1+2,2,1,1,2,4", "d+1+2,2,1,1,3", "d+3+4,4,1,4", "d+3+4,4,1,4,4", "d+3+4,4,1,4~t3.king", "f+2,1,1,2,4,4,4,1", "f+2,1,1,3", "f+2,1,1,3,3,4,3,2", "f+2,1,1,3,3,4,3,2,1+2", "f+2,1,1,3,3,4,3,2,1+2~t3.king", "u+1,2+4", "u/b+1,2+4"];
const VERIFIED_BUTTONS = {"97": 3, "98": 2, "110": 1, "198": 1, "212": 8, "214": 8, "243": 10, "246": 10, "259": 8, "262": 1, "264": 4, "268": 2, "269": 3};

test('pantera move/string counts unchanged by the additive plans block', () => {
  assert.equal(Object.keys(pantera.moves).length, 874);
  assert.equal(pantera.strings.length, 81);
  assert.equal(Object.keys(plans).length, 208);
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

test('Batch 3 keys keep their #1101 last_step_status', () => {
  assert.equal(Object.keys(B3).length, 49);
  for (const [key, want] of Object.entries(B3)) {
    assert.ok(plans[key], `Batch 3 key ${key} missing`);
    assert.equal(plans[key].last_step_status, want, `${key} last step changed from #1101`);
  }
});

test('Batch 4 keys are exactly the documented 72', () => {
  assert.equal(B4.length, 72);
  for (const key of B4) assert.ok(plans[key], `Batch 4 key ${key} missing`);
  const extra = Object.keys(plans).filter((k) => !(k in B1) && !(k in B2) && !(k in B3) && !B4.includes(k));
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
      } else {
        assert.equal(s.row, null, `${key} step ${s.step} ${s.status} must not carry a playable row`);
      }
    }
  }
});

test('u+1,2+4 flagship: step 1 unmapped row null; step 2 verified row 243', () => {
  const p = plans['u+1,2+4'];
  assert.equal(p.steps.length, 2);
  assert.equal(p.steps[0].status, 'unmapped');
  assert.equal(p.steps[0].row, null);
  assert.equal(p.steps[1].status, 'verified');
  assert.equal(p.steps[1].row, 243);
  assert.equal(p.last_step_status, 'verified');
  assert.equal(p.last_step_row, 243);
});

test('d+1+2,2,1,1,2,4 flagship: steps 97/98/198 verified, steps 4-5 review, last step verified row 259', () => {
  const p = plans['d+1+2,2,1,1,2,4'];
  assert.equal(p.steps.length, 6);
  assert.deepEqual(p.steps.map((s) => s.row), [97, 98, 198, null, null, 259]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified', 'verified', 'review', 'review', 'verified']);
  assert.equal(p.last_step_status, 'verified');
  assert.equal(p.last_step_row, 259);
});

test('f+2,1,1,3,3,4,3,2,1+2 flagship: verified steps 264/268/269 present', () => {
  const p = plans['f+2,1,1,3,3,4,3,2,1+2'];
  const rows = p.steps.filter((s) => s.status === 'verified').map((s) => s.row);
  assert.deepEqual(rows, [264, 268, 269]);
  assert.equal(p.last_step_status, 'verified');
  assert.equal(p.last_step_row, 269);
});

test('PILE_DRIVER.1+2,3,4,1+2 (grapple label) and f,F+1 (rest) have NO plan key', () => {
  assert.ok(!plans['PILE_DRIVER.1+2,3,4,1+2']);
  assert.ok(!plans['f,F+1']);
});

test('verified-last-step Batch 4 keys are exactly the documented 12', () => {
  assert.equal(B4_VERIFIED_LAST.length, 12);
  assert.deepEqual(B4_VERIFIED_LAST, ["d+1+2,2,1,1,2,4", "d+1+2,2,1,1,3", "d+3+4,4,1,4", "d+3+4,4,1,4,4", "d+3+4,4,1,4~t3.king", "f+2,1,1,2,4,4,4,1", "f+2,1,1,3", "f+2,1,1,3,3,4,3,2", "f+2,1,1,3,3,4,3,2,1+2", "f+2,1,1,3,3,4,3,2,1+2~t3.king", "u+1,2+4", "u/b+1,2+4"]);
  for (const key of B4_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B4.filter((k) => !B4_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

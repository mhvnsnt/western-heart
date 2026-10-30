/* Demonio Batch 1 step plans (LP1/RP2-only strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/DEMONIO-BATCH1-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on #1096 (feat/batch1-step-plans-pantera-20261024,
 * the step-playback engine). It does NOT stack on the Pantera plan branches
 * (#1099/#1101/#1102) or the burger plan branches (#1103/#1104/#1105/#1107):
 * demonio.json plans do not conflict with pantera.json or burger.json plans.
 * It does NOT include #1097's Pantera Batch 1 follow-up fills (Pantera-specific,
 * and its row-49 SOFT fill is still unapproved); no SOFT fill is inherited here.
 * This PR does not touch `fighter.js`: #1096's merge onto post-#1078 main must
 * reconcile #1078's `fighter.js` changes with #1096's engine branch, and that
 * belongs to #1096's merge, not this PR.
 * Bank (verified, not assumed): demonio's T3 bank is JIN (t3_source jin,
 * t3_bank moveset_jin.json, t3/ directory listing, Job 1/2/4 all jin).
 * Jin-bank rule change vs king/bryan batches (documented in the doc): jin row
 * 220 is a STANDING RP2 row, not king's jumping chord row or bryan's button-0
 * row, so it is NOT blanket-banned — it is adjudicated by the normal gates
 * and verifies for the 2,1 family step 1. Jin row 35 IS starts-airborne, so
 * the row-35 rejection for ground steps stands (it verifies only in jump
 * context: u+1,1 step 2).
 * Rules asserted here (all data-level, no THREE needed):
 *   1. demonio.json still has 764 moves / 156 strings entries (plans are additive only).
 *   2. CUMULATIVE (Batch 2 lane, 2026-10-25; updated by the Batch 3 lane,
 *      2026-10-25; updated by the Batch 4 lane, 2026-10-25): string_step_plans has exactly 271 keys (59 Batch 1 +
 *      25 Batch 2 + 87 Batch 3 + 100 Batch 4: 68 planned canonicals + 32 twins). Every Batch 1
 *      content assertion below is preserved verbatim from the Batch 1 test; only
 *      the plan-count assertion and the extra-keys assertion changed (burger
 *      Batches 2-4 test-evolution rule — plans accumulate in one block, so the
 *      Batch 1 test file is updated cumulatively, never left asserting a stale
 *      count). Batch 2's own assertions live in demonio-batch2-step-plans.test.mjs;
 *      Batch 3's in demonio-batch3-step-plans.test.mjs;
 *      Batch 4's in demonio-batch4-step-plans.test.mjs.
 *   3. Batch 1 verified steps always carry a row whose jin hit_frames button
 *      equals the step bits and whose throw flag is 0; no verified
 *      ground-context step uses row 35; review/unmapped steps carry row null.
 *      No Batch 1 step carries a soft flag (Batch 1 wires zero Job 3 fills
 *      and zero SOFT fills).
 *   4. 2,1 flagship: verified-all on rows 220/221 (recorded-path).
 *   5. 2,1,2,2 flagship: verified-all on rows 220/221/222/223.
 *   6. d+1+2,2 flagship: verified-all on rows 92/93 (crouch context, standing
 *      rows — burger Batch 1 precedent: d/f+1 steps verified row 146, standing).
 *   7. u+1,1 flagship: step 2 verified row 35 (jump context only).
 *   8. 1,1 flagship: step 1 SUSPENDED-DRIFT (prefix move 1 ROW-CHANGED 41->None),
 *      row null, never wired on stale data.
 *   9. d/f+1,2 flagship: step 2 review (SOFT proxy fail), row null.
 *  10. TACKLE family (6 keys) + b+2,1:u/f (own move_class throw) have NO plan key.
 *  11. The verified-last-step Batch 1 keys are exactly the 32 listed below,
 *      and verified rows carry the step buttons in the repo Jin hit_frames.json.
 *  12. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Run: node --test game/tests/demonio-batch1-step-plans.test.mjs   (from repo root)
 * (Cumulative: this file now also asserts the Batch 2 + Batch 3 + Batch 4 key sets; Batch 2
 *  content assertions live in game/tests/demonio-batch2-step-plans.test.mjs,
 *  Batch 3 content assertions in game/tests/demonio-batch3-step-plans.test.mjs,
 *  Batch 4 content assertions in game/tests/demonio-batch4-step-plans.test.mjs.)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const demonio = JSON.parse(readFileSync(join(ROOT, 'game/assets/movesets/demonio.json'), 'utf8'));
const fighterSrc = readFileSync(join(ROOT, 'game/js/fighter.js'), 'utf8');
const hfPath = join(ROOT, 'game/assets/anim/t3/jin/hit_frames.json');
const hf = JSON.parse(readFileSync(hfPath, 'utf8')).rows;

const plans = demonio.string_step_plans.plans;
const B1 = ["1+2,2", "1+2,2~t3.jin", "1,1", "1,1,2", "1,2", "1,2,1", "1,2,2", "1,2~t7.jin", "1,2~t7.jin.2", "2,1", "2,1,2", "2,1,2,2", "2,1,2,2~t3.jin", "2,1,2~t3.jin", "2,1~t3.jin", "2,1~t7.jin", "2,1~t7.jin.2", "2,1~t8.jin", "2,2", "MCR.2,2", "WS.1,1", "WS.1,2", "WS.1,2~t7.jin", "ZEN.1,2", "ZEN.1,2~t7.jin", "ZEN.1,2~t7.jin.2", "b+1+2,1", "b+1+2,1,2", "b+1+2,2", "b+1+2,2,2", "b+1,2", "b+2,1", "b+2,1~t7.jin", "b+2,1~t7.jin.2", "d+1+2,1", "d+1+2,1,2", "d+1+2,2", "d/b+2,2", "d/b+2,2~t7.jin", "d/f+1,2", "d/f+1,2~t3.jin", "db+2,2", "df+2,H.1+2", "u+1,1", "u+1,1~t3.jin", "u+1,1~t3.jin.2", "u+1,1~t3.jin.3", "u+1,2", "u/b+1,1", "u/b+1,1~t3.jin", "u/b+1,1~t3.jin.2", "u/b+1,1~t3.jin.3", "u/b+1,2", "u/f+1,1", "u/f+1,1~t3.jin", "u/f+1,1~t3.jin.2", "u/f+1,1~t3.jin.3", "u/f+1,2", "ws1,2"];
const B1_VERIFIED_LAST = ["1+2,2", "1+2,2~t3.jin", "2,1", "2,1,2", "2,1,2,2", "2,1,2,2~t3.jin", "2,1,2~t3.jin", "2,1~t3.jin", "2,1~t7.jin", "2,1~t7.jin.2", "2,1~t8.jin", "2,2", "b+1+2,1,2", "b+1+2,2", "b+1+2,2,2", "d+1+2,1,2", "d+1+2,2", "u+1,1", "u+1,1~t3.jin", "u+1,1~t3.jin.2", "u+1,1~t3.jin.3", "u+1,2", "u/b+1,1", "u/b+1,1~t3.jin", "u/b+1,1~t3.jin.2", "u/b+1,1~t3.jin.3", "u/b+1,2", "u/f+1,1", "u/f+1,1~t3.jin", "u/f+1,1~t3.jin.2", "u/f+1,1~t3.jin.3", "u/f+1,2"];
const B2 = ["DVS.4,4", "WS.4,4", "d+3,3", "d+3,3~t7.jin", "d+3,4", "d+3,4,3", "d+3,4~4", "d/f+3,3", "d/f+3,3~t7.jin", "d/f+4,4", "d/f+4,4~t3.jin", "f+3,3", "f+3~3,d/f+3", "f+3~3,d/f+3~t7.jin", "f+4,3", "u+4,4", "u/f+4,3", "u/f+4,3~t3.jin", "u/f+4,4", "u/f+4,4,4", "u/f+4,4,4,4", "u/f+4,4,4,4~t3.jin", "u/f+4,4,4~t3.jin", "u/f+4,4~t3.jin", "ws4,4"];
const B3 = ["1+4,1", "1+4,b+1", "1,3", "1,3~3", "1,3~3,d/f+3", "1,3~3,d/f+3~t7.jin", "1,3~3,d/f+3~t7.jin.2", "1,3~3~t7.jin", "1,3~t3.jin", "1,3~t7.jin", "1,3~t7.jin.2", "1,3~t7.jin.3", "1,3~t7.jin.4", "1,4", "1,d+3", "1,d+3~t7.jin", "2,4", "2,4~t3.jin", "2,4~t3.jin.2", "2,4~t7.jin", "2,4~t7.jin.2", "3,1", "3,1~t7.jin", "3,1~t7.jin.2", "4,1", "CD.DF+4,2", "FLY.4,1", "FLY.4,2", "MCR.4,1", "MCR.4,2", "WS.1,3", "WS.1,3~3", "WS.1,4", "b+2,3", "b+2,4", "b+2,4,2", "b+2,4,4", "b+2,4,4,4", "b+2,4,4,4,4", "b+2,4,4,4,4,2", "b+3,2", "d/b+2,2,3", "d/b+2,2,3~t7.jin", "d/b+2,2,3~t7.jin.2", "d/b+2,3", "d/b+2,3~t7.jin", "d/f+1,3", "d/f+1,4", "d/f+1,4~4", "d/f+1,4~4~t7.jin", "d/f+1,4~t7.jin", "d/f+1,4~t7.jin.2", "d/f+3,2", "db+2,2,3", "db+2,3", "df+1,4", "df+1,4~4", "df+2,4", "f+2,4", "f+3,1", "u+1,3", "u+1,3~t3.jin", "u+1,3~t3.jin.2", "u+1,3~t3.jin.3", "u+1,4", "u+1,4~t3.jin", "u+1,4~t3.jin.2", "u+1,4~t3.jin.3", "u/b+1,3", "u/b+1,3~t3.jin", "u/b+1,3~t3.jin.2", "u/b+1,3~t3.jin.3", "u/b+1,4", "u/b+1,4~t3.jin", "u/b+1,4~t3.jin.2", "u/b+1,4~t3.jin.3", "u/f+1,3", "u/f+1,3~t3.jin", "u/f+1,3~t3.jin.2", "u/f+1,3~t3.jin.3", "u/f+1,4", "u/f+1,4~t3.jin", "u/f+1,4~t3.jin.2", "u/f+1,4~t3.jin.3", "u/f+4,4,1", "ws1,3", "ws1,3~3"];
const B4 = ["1+4,2", "1+4,2,1", "1+4,2,1,4", "1+4,2,4", "1+4,2,d+4", "1,2,3", "1,2,3,4", "1,2,3~t7.jin", "1,2,3~t7.jin.2", "1,2,3~t7.jin.3", "1,2,4", "1,2,4~t7.jin", "1,2,4~t7.jin.2", "1,2,4~t7.jin.3", "1,3,2", "1,3,2,1", "1,3,2,1,4", "1,3,2,1,4~t7.jin", "1,3,2,1,4~t7.jin.2", "1,3,2,1,4~t7.jin.3", "1,3,2,1,4~t7.jin.4", "1,3,2,1~t7.jin", "1,3,2,1~t7.jin.2", "1,3,2,1~t7.jin.3", "1,3,2~t7.jin", "1,3,2~t7.jin.2", "1,3,4", "1,d+3,d+4", "1,d+3,d+4~t7.jin", "1,d+3,d+4~t7.jin.2", "2,1,2,2,3", "2,1,2,2,3,4", "2,1,2,2,3,4,4", "2,1,2,2,3,4,4,1", "2,1,2,2,3,4,4,1,2", "2,1,2,2,3,4,4,1,2,1", "2,1,2,2,3,4,4,3", "2,1,2,2,3,4,4,3,2", "2,1,2,2,3,4~t3.jin", "2,1,2,2,3~t3.jin", "2,1,4", "2,1,4,4", "2,1,4,4,2", "2,1,4,4,2,4", "2,1,4,4,2,4,3", "2,1,4,4,2,4,3,2", "2,1,4,4,2,4,3,2,1", "2,1,4,4,2,4~t3.jin", "2,1,4,4,2~t3.jin", "2,1,4,4~t3.jin", "2,1,4__main", "2,1,4~4", "2,1,4~4~t7.jin", "2,1,4~4~t7.jin.2", "2,1,4~4~t7.jin.3", "2,1,4~t3.jin", "2,1,4~t7.jin", "2,1,4~t7.jin.2", "2,1,4~t7.jin.3", "3,1,2", "3,1,4", "3,1,4~t7.jin", "3,1,4~t7.jin.2", "3,1,4~t7.jin.3", "3,2,4,3,1+4,1,2,1,2", "4,1,2", "4~3,H.1+2", "FLY.4,2,1", "FLY.4,2,1+2", "H.2+3,4", "MCR.4,2,1", "MCR.4,2,1+2", "WS.1,3,2", "WS.1,3,2,1", "WS.1,3,2,1,4", "WS.1,3,2,1,4,2", "b+1+2,2,3", "b+1+2,2,3,4", "b+1+2,2,3,f+4", "b+2,4,2,1", "b+2,4,4,1+2+3", "b+2,4,4,4,4,2,1+4", "b+2,4,4,4,4,2,1+4,1", "b+2,4,4,4,4,2,1+4,1,2", "b+2,4,4,4,4,2,1+4,1,2,1", "b+2,4,4,4,4,2,1+4,1,2,3+4", "b+3+4,2", "b+3+4,2,1", "b+3+4,2,1,4", "d+3+4,1", "d/f+3,2,4", "f+2,3,3,3,2,1,2,3,4,2", "u+1,2+4", "u/b+1,2+4", "u/f+1,2+4", "u/f+2+4,1", "ws1,3,2", "ws1,3,2,1", "ws1,3,2,1,4", "ws1,3,2,1,4,2"];
const VERIFIED_BUTTONS = {"35": 1, "36": 1, "37": 1, "47": 2, "48": 2, "49": 2, "92": 3, "93": 2, "94": 2, "180": 2, "181": 2, "183": 2, "220": 2, "221": 1, "222": 2, "223": 2};

function stepBits(step) {
  const seg = step.split('.').pop();
  let b = 0;
  for (const c of seg) if ('1234'.includes(c)) b |= 1 << (Number(c) - 1);
  return b;
}

test('demonio move/string counts unchanged by the additive plans block', () => {
  assert.equal(Object.keys(demonio.moves).length, 764);
  assert.equal(demonio.strings.length, 156);
  assert.equal(Object.keys(plans).length, 271); // 59 Batch 1 + 25 Batch 2 + 87 Batch 3 + 100 Batch 4 (cumulative)
});

test('Batch 1 keys are all present; extra keys are exactly the Batch 2 25 + Batch 3 87 + Batch 4 100 (cumulative)', () => {
  assert.equal(B1.length, 59);
  for (const key of B1) assert.ok(plans[key], `Batch 1 key ${key} missing`);
  const extra = Object.keys(plans).filter((k) => !B1.includes(k));
  assert.equal(extra.length, 212);
  assert.equal(B2.length, 25);
  assert.equal(B3.length, 87);
  assert.equal(B4.length, 100);
  for (const key of B2) assert.ok(extra.includes(key), `Batch 2 key ${key} missing from extra keys`);
  for (const key of B3) assert.ok(extra.includes(key), `Batch 3 key ${key} missing from extra keys`);
  for (const key of B4) assert.ok(extra.includes(key), `Batch 4 key ${key} missing from extra keys`);
  for (const key of extra) assert.ok(B2.includes(key) || B3.includes(key) || B4.includes(key), `unexpected extra key ${key}`);
});

test('Batch 1 verified steps carry rows (button == step bits, throw 0, never row 35 on ground); review/unmapped carry row null; no soft flags', () => {
  for (const key of B1) {
    for (const s of plans[key].steps) {
      assert.ok(!('soft' in s) || s.soft !== true, `${key} step ${s.step} carries a soft flag`);
      if (s.status === 'verified') {
        assert.notEqual(s.row, null, `${key} step ${s.step} verified but row null`);
        if (!plans[key].jumping_context) assert.notEqual(s.row, 35, `${key} step ${s.step} verified on starts-airborne row 35 for a ground step`);
        assert.equal(hf[String(s.row)][5], stepBits(s.step), `${key} step ${s.step} row ${s.row} button mismatch`);
        assert.equal(hf[String(s.row)][5], VERIFIED_BUTTONS[String(s.row)], `${key} step ${s.step} row ${s.row} button mismatch (map)`);
        assert.equal(hf[String(s.row)][4], 0, `${key} step ${s.step} row ${s.row} is a throw row`);
      } else {
        assert.equal(s.row, null, `${key} step ${s.step} ${s.status} must not carry a playable row`);
      }
    }
  }
});

test('2,1 flagship: verified-all on rows 220/221 (recorded-path)', () => {
  const p = plans['2,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [220, 221]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('2,1,2,2 flagship: verified-all on rows 220/221/222/223', () => {
  const p = plans['2,1,2,2'];
  assert.equal(p.steps.length, 4);
  assert.deepEqual(p.steps.map((s) => s.row), [220, 221, 222, 223]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified', 'verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('d+1+2,2 flagship: verified-all on rows 92/93 (crouch context)', () => {
  const p = plans['d+1+2,2'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [92, 93]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('u+1,1 flagship: step 2 verified row 35 (jump context only)', () => {
  const p = plans['u+1,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, 35]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'verified']);
  assert.equal(p.jumping_context, true);
});

test('1,1 flagship: step 1 SUSPENDED-DRIFT (prefix move 1 ROW-CHANGED 41->None), row null', () => {
  const p = plans['1,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.equal(p.steps[0].status, 'unmapped');
  assert.ok(p.steps[0].reasons.join(' ').includes('SUSPENDED-DRIFT'), 'step 1 must carry the SUSPENDED-DRIFT reason');
});

test('d/f+1,2 flagship: step 2 review (SOFT proxy fail), row null', () => {
  const p = plans['d/f+1,2'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.equal(p.steps[1].status, 'review');
});

test('TACKLE family + b+2,1:u/f (throw class) have NO plan key', () => {
  for (const k of ['TACKLE.1,1', 'TACKLE.1,1,1', 'TACKLE.1,1,1,1', 'TACKLE.2,2', 'TACKLE.2,2,2', 'TACKLE.2,2,2,2', 'b+2,1:u/f']) assert.ok(!plans[k], `${k} must have no plan`);
});

test('verified-last-step Batch 1 keys are exactly the documented 32', () => {
  assert.equal(B1_VERIFIED_LAST.length, 32);
  for (const key of B1_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B1.filter((k) => !B1_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

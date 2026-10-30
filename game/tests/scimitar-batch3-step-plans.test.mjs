/* Scimitar Batch 3 step plans (mixed-pair strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/SCIMITAR-BATCH3-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on the Scimitar Batch 2 branch
 * (feat/scimitar-batch2-step-plans-20261025, PR #1126), which is stacked on
 * the Scimitar Batch 1 branch (feat/scimitar-batch1-step-plans-20261025,
 * PR #1125), which is stacked on #1096 (feat/batch1-step-plans-pantera-20261024,
 * the step-playback engine).
 * It does NOT stack on the Pantera plan branches (#1099/#1101/#1102), the
 * burger plan branches (#1103/#1104/#1105/#1107), the demonio plan branches
 * (#1108/#1110/#1111/#1112), the diablo plan branches (#1113/#1114/#1115/#1116),
 * the kinpo plan branches (#1117/#1118/#1119/#1120), or the phantom plan
 * branches (#1121/#1122/#1123/#1124): scimitar.json plans do not conflict with
 * pantera.json, burger.json, demonio.json, diablo.json, kinpo.json, or
 * phantom.json plans.
 * It does NOT include #1097's Pantera Batch 1 follow-up fills (Pantera-specific,
 * and its row-49 SOFT fill is still unapproved); no SOFT fill is inherited here.
 * This PR does not touch `fighter.js`: #1096's merge onto post-#1078 main must
 * reconcile #1078's `fighter.js` changes with #1096's engine branch, and that
 * belongs to #1096's merge, not this PR.
 * Bank (verified, not assumed): scimitar's T3 bank is JIN (t3_source jin,
 * t3_bank moveset_jin.json, on BOTH the Batch 2 branch and main; t3/ directory
 * listing; Job 1 bank jin (220 rows); Job 2 scimitar entries all bank jin (362);
 * Job 4 jin candidates (47)). Bank resolution, documented not assumed:
 * scimitar's T7/T8 base is Shaheen (tekken_base Shaheen, merge_sources
 * t8/t7 shaheen) and Shaheen debuted in Tekken 7, so NO shaheen dir exists
 * under t3/ — this bank is a FALLBACK, not native (the kinpo pattern:
 * Asuka -> jin; contrast phantom Yoshimitsu -> yoshimitsu native, burger
 * Bob -> bryan). The pack dir does NOT differ from the moveset bank name
 * here (unlike diablo's heihachi/heihachi_on_jin split).
 * Jin-bank rules, per-bank evidence (never a cross-bank blanket ban):
 * row 35 EXISTS as a starts-airborne LP1 row (hit_frames [11,12,39,535,0,1])
 * — ground-rejected, jump-context only; row 220 is a STANDING RP2 row
 * (hit_frames [12,12,41,1042,0,2], Job 1 standing) — NOT king's jumping
 * chord row, NOT bryan's button-0 row, NOT heihachi's jump RK4 row; row 216
 * is a JUMP row (hit_frames [63,64,117,1543,0,0], button 0) — it fails every
 * single-button gate; row 41 is a starts-airborne LP1 row. Jin duck-dip rows
 * (16): 123, 189, 192, 210, 211, 212, 213, 235, 257, 367, 377, 381, 385, 387,
 * 389, 397 — handled like crouch: STANCE-SOFT (review) for non-crouch contexts.
 * The file's ONLY row-changed move is 1 (184->None) — NOT a Batch 3 step
 * prefix (no Batch 3 string starts with plain 1), so Batch 3 has ZERO
 * suspended-drift steps.
 * Canonicalization is the CORRECTED rule (demonio Batch 2 finding): strip ONLY
 * a trailing ~t[378].[a-z]+(.N)?$ source-variant suffix; input-~ is Tekken
 * cancel notation, part of the move. Scimitar Batch 3 contains ZERO input-~
 * canonicals — and scimitar is INERT file-wide on this axis: every ~ in the
 * file is a trailing source-variant suffix (~t7.shaheen / ~t8.shaheen, with
 * .2/.3), so old canonical == corrected canonical for all 114 comma keys.
 * Spelling quirks kept: d/f+1,4 vs df+4,1 are distinct canonicals, never merged.
 * Rules asserted here (all data-level, no THREE needed):
 *   1. scimitar.json still has 362 moves / 50 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 62 keys (39 Batches 1-2 + 23 Batch 3).
 *   3. Batch 3 verified steps always carry a row whose jin hit_frames
 *      button equals the step bits and whose throw flag is 0; verified rows
 *      always exist in the jin hit_frames; review/unmapped steps carry row
 *      null. No Batch 3 step carries a soft flag (Batch 3 wires zero Job 3
 *      fills — no exact+FULL Job 3 candidate exists for any verified step —
 *      and zero SOFT fills).
 *   4. 2,3 flagship: partial, step 1 verified row 220 (standing RP2), step 2 unmapped.
 *   5. 4,1 flagship: partial, step 1 review (candidate row 199 SOFT fail), step 2 unmapped.
 *   6. d/f+1,3 flagship: unmapped-all, steps 1-2 airborne-rejected rows 179/197.
 *   7. d/f+1,4 flagship: unmapped-all, steps 1-2 airborne-rejected rows 179/204.
 *   8. The verified-last-step Batch 3 keys are exactly NONE (empty list below):
 *      no Batch 3 plan key ends on a verified step.
 *   9. No Batch 3 step carries a SUSPENDED-DRIFT reason (the file's only
 *      row-changed move, 1, is not a Batch 3 step prefix).
 *  10. Batches 1-2 flagships undisturbed: 2,1 [220,221], 2,1,2,2 [220,221,222,223],
 *      d+1+2,2 [92,93], u/f+4,3 [80,193], d/f+4,4 [205,null].
 *  11. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Run: node --test game/tests/scimitar-batch3-step-plans.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const scimitar = JSON.parse(readFileSync(join(ROOT, 'game/assets/movesets/scimitar.json'), 'utf8'));
const fighterSrc = readFileSync(join(ROOT, 'game/js/fighter.js'), 'utf8');
const hfPath = join(ROOT, 'game/assets/anim/t3/jin/hit_frames.json');
const hf = JSON.parse(readFileSync(hfPath, 'utf8')).rows;

const plans = scimitar.string_step_plans.plans;
const B3 = ["2,3", "2,3~t7.shaheen", "2,3~t7.shaheen.2", "4,1", "4,1~t7.shaheen", "4,1~t7.shaheen.2", "FC.df+4,1", "R.d/b+2,4", "R.d/b+2,4~t7.shaheen", "SNK.df+1,3", "d/f+1,3", "d/f+1,4", "df+4,1", "f+2,3", "f+2,3~t7.shaheen", "f+2,3~t7.shaheen.2", "f+2,4", "f+2,4,4", "f+2,4,4~t7.shaheen", "f+2,4,4~t7.shaheen.2", "f+2,4,4~t7.shaheen.3", "f+2,4~t7.shaheen", "f+2,4~t7.shaheen.2"];
const B12 = ["1,2", "1,2~t7.shaheen", "1,2~t7.shaheen.2", "1,2~t8.shaheen", "1,2,2", "1,2,2~t7.shaheen", "1,2,2~t7.shaheen.2", "1,2,2~t7.shaheen.3", "2,1", "2,1~t7.shaheen", "2,1~t7.shaheen.2", "2,1~t8.shaheen", "2,1,2", "2,1,2,2", "SNK.df+1,2", "d+1+2,1", "d+1+2,1,2", "d+1+2,2", "d/b+2,1", "d/b+2,1~t7.shaheen", "db+2,1", "4,3", "4,3~t7.shaheen", "4,3~t7.shaheen.2", "4,4", "4,4~t7.shaheen", "4,4~t7.shaheen.2", "WS.3,3", "WS.3,3~t7.shaheen", "d/b+3,4", "d/b+3,4~t7.shaheen", "d/f+4,4", "db+3,4", "df+4,3", "u/f+4,3", "u/f+4,4", "u/f+4,4,4", "u/f+4,4,4,4", "ws3,3"];
const B3_VERIFIED_LAST = [];
const VERIFIED_BUTTONS = {"220": 2};

function stepBits(step) {
  const seg = step.split('.').pop();
  let b = 0;
  for (const c of seg) if ('1234'.includes(c)) b |= 1 << (Number(c) - 1);
  return b;
}

test('scimitar move/string counts unchanged by the additive plans block', () => {
  assert.equal(Object.keys(scimitar.moves).length, 362);
  assert.equal(scimitar.strings.length, 50);
  assert.equal(Object.keys(plans).length, 62);
});

test('Batch 3 keys are exactly the documented 23', () => {
  assert.equal(B3.length, 23);
  for (const key of B3) assert.ok(plans[key], `Batch 3 key ${key} missing`);
  const extra = Object.keys(plans).filter((k) => !B3.includes(k));
  assert.deepEqual(extra, B12, 'non-Batch-3 plans must be exactly the 39 Batches 1-2 keys, in order');
});

test('Batch 3 verified steps carry rows (button == step bits, throw 0, row exists in jin hit_frames); review/unmapped carry row null; no soft flags', () => {
  for (const key of B3) {
    for (const s of plans[key].steps) {
      assert.ok(!('soft' in s) || s.soft !== true, `${key} step ${s.step} carries a soft flag`);
      if (s.status === 'verified') {
        assert.notEqual(s.row, null, `${key} step ${s.step} verified but row null`);
        assert.ok(hf[String(s.row)], `${key} step ${s.step} verified on row ${s.row} which does not exist in the jin hit_frames`);
        assert.equal(hf[String(s.row)][5], stepBits(s.step), `${key} step ${s.step} row ${s.row} button mismatch`);
        assert.equal(hf[String(s.row)][5], VERIFIED_BUTTONS[String(s.row)], `${key} step ${s.step} row ${s.row} button mismatch (map)`);
        assert.equal(hf[String(s.row)][4], 0, `${key} step ${s.step} row ${s.row} is a throw row`);
      } else {
        assert.equal(s.row, null, `${key} step ${s.step} ${s.status} must not carry a playable row`);
      }
    }
  }
});

test('2,3 flagship: partial, step 1 verified row 220 (standing RP2), step 2 unmapped (no candidate)', () => {
  const p = plans['2,3'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [220, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'unmapped']);
  assert.equal(p.string_status, 'partial');
  assert.ok(p.steps[1].reasons.join(' ').includes('no candidate row'), 'step 2 must record no candidate');
});

test('4,1 flagship: partial, step 1 review (candidate row 199 SOFT fail), step 2 unmapped (no candidate)', () => {
  const p = plans['4,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['review', 'unmapped']);
  assert.equal(p.string_status, 'partial');
  assert.ok(p.steps[0].reasons.join(' ').includes('SOFT limb-peak proxy fail'), 'step 1 must record the SOFT fail');
  assert.ok(p.steps[1].reasons.join(' ').includes('no candidate row'), 'step 2 must record no candidate');
});

test('d/f+1,3 flagship: unmapped-all, steps 1-2 airborne-rejected rows 179/197', () => {
  const p = plans['d/f+1,3'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'unmapped']);
  assert.equal(p.string_status, 'unmapped-all');
  assert.equal(p.steps[0].candidate_row, 179);
  assert.equal(p.steps[1].candidate_row, 197);
  assert.ok(p.steps[0].reasons.join(' ').includes('airborne row'), 'step 1 must record the airborne rejection');
  assert.ok(p.steps[1].reasons.join(' ').includes('airborne row'), 'step 2 must record the airborne rejection');
});

test('d/f+1,4 flagship: unmapped-all, steps 1-2 airborne-rejected rows 179/204', () => {
  const p = plans['d/f+1,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'unmapped']);
  assert.equal(p.string_status, 'unmapped-all');
  assert.equal(p.steps[0].candidate_row, 179);
  assert.equal(p.steps[1].candidate_row, 204);
  assert.ok(p.steps[0].reasons.join(' ').includes('airborne row'), 'step 1 must record the airborne rejection');
  assert.ok(p.steps[1].reasons.join(' ').includes('airborne row'), 'step 2 must record the airborne rejection');
});

test('verified-last-step Batch 3 keys are exactly NONE', () => {
  assert.equal(B3_VERIFIED_LAST.length, 0);
  for (const key of B3) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('no Batch 3 step carries a SUSPENDED-DRIFT reason', () => {
  for (const key of B3) {
    for (const s of plans[key].steps) {
      assert.ok(!s.reasons.join(' ').includes('SUSPENDED-DRIFT'), `${key} step ${s.step} unexpectedly suspended`);
    }
  }
});

test('Batches 1-2 flagships undisturbed', () => {
  assert.deepEqual(plans['2,1'].steps.map((s) => s.row), [220, 221]);
  assert.deepEqual(plans['2,1,2,2'].steps.map((s) => s.row), [220, 221, 222, 223]);
  assert.deepEqual(plans['d+1+2,2'].steps.map((s) => s.row), [92, 93]);
  assert.deepEqual(plans['u/f+4,3'].steps.map((s) => s.row), [80, 193]);
  assert.deepEqual(plans['d/f+4,4'].steps.map((s) => s.row), [205, null]);
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

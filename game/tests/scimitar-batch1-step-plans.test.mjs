/* Scimitar Batch 1 step plans (LP1/RP2-only strings, 2026-10-25) — data + engine-marker guard.
 * Batch 3 update (2026-10-25): this file is now CUMULATIVE for Batches 1-3 — it asserts 62 total plans
 * (21 Batch 1 + 18 Batch 2 + 23 Batch 3 keys listed in B3 below); every Batch 1 + Batch 2 content assertion is
 * preserved verbatim; only the header note, the B3 const, the plan count, and the
 * extra-keys assertion changed. Batch 3's own assertions live in
 * game/tests/scimitar-batch3-step-plans.test.mjs.
 * Batch 2 update (2026-10-25): this file is now CUMULATIVE — it asserts 39 total plans
 * (21 Batch 1 + 18 Batch 2 keys listed in B2 below); every Batch 1 content assertion is
 * preserved verbatim; only the header note, the B2 const, the plan count, and the
 * extra-keys assertion changed. Batch 2's own assertions live in
 * game/tests/scimitar-batch2-step-plans.test.mjs.
 * Docs: docs/movesets/SCIMITAR-BATCH1-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on #1096 (feat/batch1-step-plans-pantera-20261024,
 * the step-playback engine). It does NOT stack on the Pantera plan branches
 * (#1099/#1101/#1102), the burger plan branches (#1103/#1104/#1105/#1107), the
 * demonio plan branches (#1108/#1110/#1111/#1112), the diablo plan branches
 * (#1113/#1114/#1115/#1116), the kinpo plan branches (#1117/#1118/#1119/#1120),
 * or the phantom plan branches (#1121/#1122/#1123/#1124): scimitar.json plans
 * do not conflict with pantera.json, burger.json, demonio.json, diablo.json,
 * kinpo.json, or phantom.json plans.
 * It does NOT include #1097's Pantera Batch 1 follow-up fills (Pantera-specific,
 * and its row-49 SOFT fill is still unapproved); no SOFT fill is inherited here.
 * This PR does not touch `fighter.js`: #1096's merge onto post-#1078 main must
 * reconcile #1078's `fighter.js` changes with #1096's engine branch, and that
 * belongs to #1096's merge, not this PR.
 * Bank (verified, not assumed): scimitar's T3 bank is JIN (t3_source jin,
 * t3_bank moveset_jin.json, on BOTH #1096 and main; t3/ directory listing;
 * Job 1 bank jin (220 rows); Job 2 scimitar entries all bank jin (362);
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
 * single-button gate; row 41 is a starts-airborne LP1 row. Scimitar's own
 * LP1 move 1 carries t3_row 184 on #1096 (standing LP1 row) and its RP2 move
 * 2 carries t3_row 220 (the standing RP2 row) — but move 1 IS row-changed on
 * current main (184->None, anim_ref None), so both Batch 1 steps with prefix
 * 1 are SUSPENDED-DRIFT. The file's ONLY row-changed move is 1.
 * Canonicalization is the CORRECTED rule (demonio Batch 2 finding): strip ONLY
 * a trailing ~t[378].[a-z]+(.N)?$ source-variant suffix; input-~ is Tekken
 * cancel notation, part of the move. Scimitar Batch 1 contains ZERO input-~
 * canonicals — and scimitar is INERT file-wide on this axis: every ~ in the
 * file is a trailing source-variant suffix (~t7.shaheen / ~t8.shaheen, with
 * .2/.3), so old canonical == corrected canonical for all 114 comma keys.
 * Spelling quirks kept: d/b+2,1 vs db+2,1 are distinct canonicals, never merged.
 * Rules asserted here (all data-level, no THREE needed):
 *   1. scimitar.json still has 362 moves / 50 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 62 keys (21 Batch 1 + 18 Batch 2 + 23 Batch 3: 11 planned canonicals + 12 twins).
 *   3. Batch 1 verified steps always carry a row whose jin hit_frames
 *      button equals the step bits and whose throw flag is 0; verified rows
 *      always exist in the jin hit_frames; review/unmapped steps carry row
 *      null. No Batch 1 step carries a soft flag (Batch 1 wires zero Job 3
 *      fills — all Job 3 candidates are ROW-ONLY or soft — and zero SOFT fills).
 *   4. 2,1 flagship: verified-all on rows 220/221 (standing RP2/LP1).
 *   5. 2,1,2,2 flagship: verified-all on rows 220/221/222/223.
 *   6. d+1+2,2 flagship: verified-all on rows 92/93 (crouch context,
 *      GATE-NOTE: standing rows for crouch steps, demonio Batch 1 precedent).
 *   7. 1,2 flagship: step 1 SUSPENDED-DRIFT (prefix move 1 ROW-CHANGED
 *      184->None), row null, never wired on stale data; step 2 verified row 186.
 *   8. d+1+2,1 flagship: step 2 unmapped (candidate row 177 button 12 !=
 *      step bits 1, chord row rejected).
 *   9. The verified-last-step Batch 1 keys are exactly the 12 listed below,
 *      and verified rows carry the step buttons in the repo jin
 *      hit_frames.json.
 *  10. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Run: node --test game/tests/scimitar-batch1-step-plans.test.mjs   (from repo root)
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
const B1 = ["1,2", "1,2,2", "1,2,2~t7.shaheen", "1,2,2~t7.shaheen.2", "1,2,2~t7.shaheen.3", "1,2~t7.shaheen", "1,2~t7.shaheen.2", "1,2~t8.shaheen", "2,1", "2,1,2", "2,1,2,2", "2,1~t7.shaheen", "2,1~t7.shaheen.2", "2,1~t8.shaheen", "SNK.df+1,2", "d+1+2,1", "d+1+2,1,2", "d+1+2,2", "d/b+2,1", "d/b+2,1~t7.shaheen", "db+2,1"];
const B2 = ["4,3", "4,3~t7.shaheen", "4,3~t7.shaheen.2", "4,4", "4,4~t7.shaheen", "4,4~t7.shaheen.2", "WS.3,3", "WS.3,3~t7.shaheen", "d/b+3,4", "d/b+3,4~t7.shaheen", "d/f+4,4", "db+3,4", "df+4,3", "u/f+4,3", "u/f+4,4", "u/f+4,4,4", "u/f+4,4,4,4", "ws3,3"];
const B3 = ["2,3", "2,3~t7.shaheen", "2,3~t7.shaheen.2", "4,1", "4,1~t7.shaheen", "4,1~t7.shaheen.2", "FC.df+4,1", "R.d/b+2,4", "R.d/b+2,4~t7.shaheen", "SNK.df+1,3", "d/f+1,3", "d/f+1,4", "df+4,1", "f+2,3", "f+2,3~t7.shaheen", "f+2,3~t7.shaheen.2", "f+2,4", "f+2,4~t7.shaheen", "f+2,4~t7.shaheen.2", "f+2,4,4", "f+2,4,4~t7.shaheen", "f+2,4,4~t7.shaheen.2", "f+2,4,4~t7.shaheen.3"];
const B1_VERIFIED_LAST = ["1,2", "1,2~t7.shaheen", "1,2~t7.shaheen.2", "1,2~t8.shaheen", "2,1", "2,1,2", "2,1,2,2", "2,1~t7.shaheen", "2,1~t7.shaheen.2", "2,1~t8.shaheen", "d+1+2,1,2", "d+1+2,2"];
const VERIFIED_BUTTONS = {"92": 3, "93": 2, "183": 2, "186": 2, "220": 2, "221": 1, "222": 2, "223": 2};

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

test('Batch 1 keys are exactly the documented 21', () => {
  assert.equal(B1.length, 21);
  for (const key of B1) assert.ok(plans[key], `Batch 1 key ${key} missing`);
  const extra = Object.keys(plans).filter((k) => !B1.includes(k));
  assert.deepEqual(extra, [...B2, ...B3]);
});

test('Batch 1 verified steps carry rows (button == step bits, throw 0, row exists in jin hit_frames); review/unmapped carry row null; no soft flags', () => {
  for (const key of B1) {
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

test('2,1 flagship: verified-all on rows 220/221 (standing RP2/LP1)', () => {
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

test('d+1+2,2 flagship: verified-all on rows 92/93 (crouch context, GATE-NOTE)', () => {
  const p = plans['d+1+2,2'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [92, 93]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
  assert.ok(p.steps[0].reasons.join(' ').includes('GATE-NOTE'), 'crouch step on standing row must carry the GATE-NOTE');
  assert.ok(p.steps[1].reasons.join(' ').includes('GATE-NOTE'), 'crouch step on standing row must carry the GATE-NOTE');
});

test('1,2 flagship: step 1 SUSPENDED-DRIFT (prefix move 1 ROW-CHANGED 184->None), row null; step 2 verified row 186', () => {
  const p = plans['1,2'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, 186]);
  assert.equal(p.steps[0].status, 'unmapped');
  assert.ok(p.steps[0].reasons.join(' ').includes('SUSPENDED-DRIFT'), 'step 1 must carry the SUSPENDED-DRIFT reason');
  assert.equal(p.steps[1].status, 'verified');
});

test('d+1+2,1 flagship: partial, step 2 unmapped (candidate row 177 button 12 != step bits 1)', () => {
  const p = plans['d+1+2,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [92, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'unmapped']);
  assert.equal(p.string_status, 'partial');
  assert.ok(p.steps[1].reasons.join(' ').includes('button 12'), 'step 2 must record the button-12 rejection');
});

test('TACKLE family gets no plan (CSV-only, narrow grapple label)', () => {
  for (const key of ['TACKLE.1,1', 'TACKLE.1,1,1', 'TACKLE.1,1,1,1']) {
    assert.equal(plans[key], undefined, `${key} must not gain a plan`);
  }
});

test('verified-last-step Batch 1 keys are exactly the documented 12', () => {
  assert.equal(B1_VERIFIED_LAST.length, 12);
  for (const key of B1_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B1.filter((k) => !B1_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

/* Skull Batch 1 step plans (LP1/RP2-only strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/SKULL-BATCH1-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on #1096 (feat/batch1-step-plans-pantera-20261024,
 * the step-playback engine). It does NOT stack on the Pantera plan branches
 * (#1099/#1101/#1102), the burger plan branches (#1103/#1104/#1105/#1107), the
 * demonio plan branches (#1108/#1110/#1111/#1112), the diablo plan branches
 * (#1113/#1114/#1115/#1116), the kinpo plan branches (#1117/#1118/#1119/#1120),
 * the phantom plan branches (#1121/#1122/#1123/#1124), or the scimitar plan
 * branches (#1125/#1126/#1127/#1128): skull.json plans do not conflict with
 * pantera.json, burger.json, demonio.json, diablo.json, kinpo.json,
 * phantom.json, or scimitar.json plans.
 * It does NOT include #1097's Pantera Batch 1 follow-up fills (Pantera-specific,
 * and its row-49 SOFT fill is still unapproved); no SOFT fill is inherited here.
 * This PR does not touch `fighter.js`: #1096's merge onto post-#1078 main must
 * reconcile #1078's `fighter.js` changes with #1096's engine branch, and that
 * belongs to #1096's merge, not this PR.
 * Bank (verified, not assumed): skull's T3 bank is BRYAN (t3_source bryan,
 * t3_bank moveset_bryan.json, on BOTH #1096 and main; t3/ directory listing;
 * Job 1 bank bryan (160 rows); Job 2 skull entries all bank bryan (688);
 * Job 4 bryan candidates (27)). Bank resolution, documented not assumed:
 * skull's T7/T8 base is Bryan Fury (tekken_base Bryan Fury, merge_sources
 * t8/t7/t3 bryan) and Bryan debuted in Tekken 3, so a native bryan dir
 * exists under t3/ — this bank is NATIVE, not a fallback (contrast kinpo
 * Asuka -> jin, scimitar Shaheen -> jin; same bank as burger's fallback,
 * but here it is the character's own T3 bank, and its row identities were
 * re-derived from the files, not copied from burger). The pack dir does NOT
 * differ from the moveset bank name here (unlike diablo's
 * heihachi/heihachi_on_jin split). Pack bank: divmot12_bryan.bin.
 * Bryan-bank rules, per-bank evidence (never a cross-bank blanket ban):
 * row 35 does NOT EXIST in this bank (absent from hit_frames AND Job 1);
 * row 220 EXISTS in hit_frames ([25,26,65,271,0,0], button 0) but is ABSENT
 * from Job 1 — it fails every single-button gate; row 216 EXISTS in
 * hit_frames ([20,21,30,271,0,0], button 0) but is ABSENT from Job 1 —
 * same treatment. Skull's own LP1 move 1 carries t3_row 172 on #1096
 * (standing LP1 row) and its RP2 move 2 carries t3_row 100 — BOTH
 * unchanged on current main (damage-only drift 11->9 and 12->13), NOT
 * suspending. The file's row-changed moves are exactly 3, 3_c36, u+1,3
 * (all 63->None, the jump-clip LK3 row), none a Batch 1 step prefix, so
 * suspended-drift steps are 0.
 * Canonicalization is the CORRECTED rule (demonio Batch 2 finding): strip ONLY
 * a trailing ~t[378].[a-z]+(.N)?$ source-variant suffix; input-~ is Tekken
 * cancel notation, part of the move. Skull Batch 1 contains ZERO input-~
 * canonicals — and skull is INERT file-wide on this axis: every ~ in the
 * file is a trailing source-variant suffix (~t3.bryan[.2/.3/.4] /
 * ~t7.bryan[.2/.3/.4/.5]), so old canonical == corrected canonical for all
 * 372 comma keys.
 * Spelling quirks kept: D/F+1,1 family vs DF+1,1 family are distinct
 * canonicals (both unmapped-all); FC.d/f+2,1 vs FC.df+2,1 are distinct
 * canonicals (both unmapped-all).
 * Rules asserted here (all data-level, no THREE needed):
 *   1. skull.json still has 688 moves / 109 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 91 keys (54 planned canonicals + 37 twins).
 *   3. Batch 1 verified steps always carry a row whose bryan hit_frames
 *      button equals the step bits and whose throw flag is 0; verified rows
 *      always exist in the bryan hit_frames; review/unmapped steps carry row
 *      null. No Batch 1 step carries a soft flag (Batch 1 wires zero Job 3
 *      fills — all Job 3 candidates are ROW-ONLY or soft — and zero SOFT fills).
 *   4. 2,1 flagship: verified-all on rows 152/153 (recorded-path standing RP2/LP1).
 *   5. 2,1,2 flagship: verified-all on rows 152/153/151.
 *   6. d/f+1+2,2 flagship: verified-all on rows 113/149 (crouch context,
 *      GATE-NOTE on step 2: standing row for a crouch step, demonio Batch 1
 *      precedent; step 1 row 113 is a crouch row, so it carries no GATE-NOTE).
 *   7. 1,2 flagship: step 1 VERIFIED row 172 (skull's own LP1 row, unchanged
 *      on main — NOT suspended, unlike scimitar's row-changed move 1);
 *      step 2 unmapped (no candidate row at all).
 *   8. b+1+2,1 flagship: partial, step 1 review (candidate row 167,
 *      STANCE-SOFT crouch row for a standing-context step), step 2 unmapped
 *      (candidate row 168 button 0 != step bits 1).
 *   9. b+2,1 flagship: partial, step 1 review (candidate row 158,
 *      STANCE-SOFT duck-dip row for a standing-context step), step 2 unmapped.
 *  10. The verified-last-step Batch 1 keys are exactly the 26 listed below,
 *      and verified rows carry the step buttons in the repo bryan
 *      hit_frames.json.
 *  11. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Run: node --test game/tests/skull-batch1-step-plans.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const skull = JSON.parse(readFileSync(join(ROOT, 'game/assets/movesets/skull.json'), 'utf8'));
const fighterSrc = readFileSync(join(ROOT, 'game/js/fighter.js'), 'utf8');
const hfPath = join(ROOT, 'game/assets/anim/t3/bryan/hit_frames.json');
const hf = JSON.parse(readFileSync(hfPath, 'utf8')).rows;

const plans = skull.string_step_plans.plans;
const B1 = ["1+2,1", "1+2,2", "1+2,2~t7.bryan", "1+2,2~t7.bryan.2", "1,2", "1,2,1", "1,2,1~t7.bryan", "1,2,1~t7.bryan.2", "1,2,1~t7.bryan.3", "1,2~t3.bryan", "1,2~t7.bryan", "1,2~t7.bryan.2", "2,1", "2,1,2", "D/F+1,1", "D/F+1,1,1", "D/F+1,1,1,1", "D/F+1,1,1,1~t7.bryan", "D/F+1,1,1,1~t7.bryan.2", "D/F+1,1,1,1~t7.bryan.3", "D/F+1,1,1~t7.bryan", "D/F+1,1,1~t7.bryan.2", "D/F+1,1~t7.bryan", "DF+1,1", "DF+1,1,1", "DF+1,1,1,1", "DF+1,2", "FC.d/f+2,1", "FC.d/f+2,1~t7.bryan", "FC.df+2,1", "SLS.2,1", "SLS.2,2", "SS.2,1", "b+1+2,1", "b+1,2", "b+2,1", "b+2,1,2", "b+2,1,2~t7.bryan", "b+2,1,2~t7.bryan.2", "b+2,1,2~t7.bryan.3", "b+2,1~t7.bryan", "b+2,1~t7.bryan.2", "b+2,f+1", "b+2,f+1,2", "b+2,f+1~t3.bryan", "d/f+1+2,2", "d/f+1+2,d/f+1", "d/f+1+2,d/f+1,d/f+1", "d/f+1+2,d/f+1,d/f+1,d/f+1", "d/f+1,2", "d/f+1,2~t7.bryan", "d/f+2,1", "d/f+2,1~t7.bryan", "df+2,1", "f+1,2", "f+1,2~t3.bryan", "f+1,2~t3.bryan.2", "f+2,1", "f+2,1,SNE.2", "f+2,1~t7.bryan", "f+2,1~t7.bryan.2", "qcf+2,1", "qcf+2,1~t7.bryan", "u+1,1", "u+1,1~t3.bryan", "u+1,1~t3.bryan.2", "u+1,1~t3.bryan.3", "u+1,2", "u/b+1,1", "u/b+1,1~t3.bryan", "u/b+1,1~t3.bryan.2", "u/b+1,1~t3.bryan.3", "u/b+1,2", "u/f+1,1", "u/f+1,1~t3.bryan", "u/f+1,1~t3.bryan.2", "u/f+1,1~t3.bryan.3", "u/f+1,2", "ub+1+2,1", "ub+1+2,1,2", "ub+1+2,1,2,1", "ub+1+2,1,2,1,2", "ub+1+2,1,2,1,2,1", "ub+1+2,1,2,1,2,1,2", "ub+1+2,1,2,1,2,1,2,1", "ub+1+2,1,2,1,2,1,2,1,2", "ub+1+2,1,2,1,2,1,2,1,2,1", "uf+2,2", "uf+2,2,2", "uf+2,2,2,SNE.2", "uf+2,2,2,SNE.2,2"];
const B1_VERIFIED_LAST = ["2,1", "2,1,2", "b+1,2", "b+2,f+1,2", "d/f+1+2,2", "d/f+1+2,d/f+1", "d/f+1+2,d/f+1,d/f+1", "d/f+1+2,d/f+1,d/f+1,d/f+1", "f+1,2", "f+1,2~t3.bryan", "f+1,2~t3.bryan.2", "u+1,1", "u+1,1~t3.bryan", "u+1,1~t3.bryan.2", "u+1,1~t3.bryan.3", "u+1,2", "u/b+1,1", "u/b+1,1~t3.bryan", "u/b+1,1~t3.bryan.2", "u/b+1,1~t3.bryan.3", "u/b+1,2", "u/f+1,1", "u/f+1,1~t3.bryan", "u/f+1,1~t3.bryan.2", "u/f+1,1~t3.bryan.3", "u/f+1,2"];
const VERIFIED_BUTTONS = {"44": 1, "45": 1, "46": 1, "56": 2, "57": 2, "58": 2, "113": 3, "145": 2, "146": 1, "147": 1, "148": 1, "149": 2, "150": 2, "151": 2, "152": 2, "153": 1, "172": 1, "173": 2};

function stepBits(step) {
  const seg = step.split('.').pop();
  let b = 0;
  for (const c of seg) if ('1234'.includes(c)) b |= 1 << (Number(c) - 1);
  return b;
}

test('skull move/string counts unchanged by the additive plans block', () => {
  assert.equal(Object.keys(skull.moves).length, 688);
  assert.equal(skull.strings.length, 109);
  assert.equal(Object.keys(plans).length, 91);
});

test('Batch 1 keys are exactly the documented 91', () => {
  assert.equal(B1.length, 91);
  for (const key of B1) assert.ok(plans[key], `Batch 1 key ${key} missing`);
  const extra = Object.keys(plans).filter((k) => !B1.includes(k));
  assert.deepEqual(extra, []);
});

test('Batch 1 verified steps carry rows (button == step bits, throw 0, row exists in bryan hit_frames); review/unmapped carry row null; no soft flags', () => {
  for (const key of B1) {
    for (const s of plans[key].steps) {
      assert.ok(!('soft' in s) || s.soft !== true, `${key} step ${s.step} carries a soft flag`);
      if (s.status === 'verified') {
        assert.notEqual(s.row, null, `${key} step ${s.step} verified but row null`);
        assert.ok(hf[String(s.row)], `${key} step ${s.step} verified on row ${s.row} which does not exist in the bryan hit_frames`);
        assert.equal(hf[String(s.row)][5], stepBits(s.step), `${key} step ${s.step} row ${s.row} button mismatch`);
        assert.equal(hf[String(s.row)][5], VERIFIED_BUTTONS[String(s.row)], `${key} step ${s.step} row ${s.row} button mismatch (map)`);
        assert.equal(hf[String(s.row)][4], 0, `${key} step ${s.step} row ${s.row} is a throw row`);
      } else {
        assert.equal(s.row, null, `${key} step ${s.step} ${s.status} must not carry a playable row`);
      }
    }
  }
});

test('2,1 flagship: verified-all on rows 152/153 (recorded-path standing RP2/LP1)', () => {
  const p = plans['2,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [152, 153]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('2,1,2 flagship: verified-all on rows 152/153/151', () => {
  const p = plans['2,1,2'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [152, 153, 151]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('d/f+1+2,2 flagship: verified-all on rows 113/149 (crouch context, GATE-NOTE on step 2 only)', () => {
  const p = plans['d/f+1+2,2'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [113, 149]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
  assert.ok(!p.steps[0].reasons.join(' ').includes('GATE-NOTE'), 'step 1 row 113 is a crouch row, so it must NOT carry the GATE-NOTE');
  assert.ok(p.steps[1].reasons.join(' ').includes('GATE-NOTE'), 'step 2 standing row for a crouch step must carry the GATE-NOTE');
});

test('1,2 flagship: step 1 VERIFIED row 172 (own LP1 row, unchanged on main — NOT suspended), step 2 unmapped (no candidate)', () => {
  const p = plans['1,2'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [172, null]);
  assert.equal(p.steps[0].status, 'verified');
  assert.ok(!p.steps[0].reasons.join(' ').includes('SUSPENDED-DRIFT'), 'skull move 1 is not row-changed, so step 1 must NOT be suspended');
  assert.equal(p.steps[1].status, 'unmapped');
});

test('b+1+2,1 flagship: partial, step 1 review (candidate 167 STANCE-SOFT crouch), step 2 unmapped (candidate 168 button 0)', () => {
  const p = plans['b+1+2,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['review', 'unmapped']);
  assert.equal(p.string_status, 'partial');
  assert.equal(p.steps[0].candidate_row, 167);
  assert.ok(p.steps[0].reasons.join(' ').includes('STANCE-SOFT'), 'step 1 must record the STANCE-SOFT review');
  assert.equal(p.steps[1].candidate_row, 168);
  assert.ok(p.steps[1].reasons.join(' ').includes('button 0'), 'step 2 must record the button-0 rejection');
});

test('b+2,1 flagship: partial, step 1 review (candidate 158 STANCE-SOFT duck-dip), step 2 unmapped', () => {
  const p = plans['b+2,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['review', 'unmapped']);
  assert.equal(p.string_status, 'partial');
  assert.equal(p.steps[0].candidate_row, 158);
  assert.ok(p.steps[0].reasons.join(' ').includes('STANCE-SOFT'), 'step 1 must record the STANCE-SOFT review');
});

test('TACKLE family gets no plan (CSV-only, narrow grapple label)', () => {
  for (const key of ['TACKLE.1,1', 'TACKLE.1,1,1', 'TACKLE.1,1,1,1']) {
    assert.equal(plans[key], undefined, `${key} must not gain a plan`);
  }
});

test('verified-last-step Batch 1 keys are exactly the documented 26', () => {
  assert.equal(B1_VERIFIED_LAST.length, 26);
  for (const key of B1_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B1.filter((k) => !B1_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

/* Skull Batch 3 step plans (mixed-pair strings, 2026-10-25) — cumulative with Batches 1–2 — data + engine-marker guard.
 * Docs: docs/movesets/SKULL-BATCH3-STEP-PLANS-2026-10-25.md (Batch 1 doc: SKULL-BATCH1-STEP-PLANS-2026-10-25.md; Batch 2 doc: SKULL-BATCH2-STEP-PLANS-2026-10-25.md).
 * Stack: this branch is stacked on skull Batch 2 (feat/skull-batch2-step-plans-20261025, which is stacked on skull Batch 1 (feat/skull-batch1-step-plans-20261025, which is stacked on #1096 (feat/batch1-step-plans-pantera-20261024,
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
 *   2. string_step_plans has exactly 198 keys (91 Batch 1 + 29 Batch 2 + 78 Batch 3: 31 planned canonicals + 47 twins). Batch 1–2 keys and content are preserved verbatim; Batch 3 adds only its own keys.
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
 * Batch 3 summary (mixed pairs, 31 canonicals: 30 pure + 1 chord-involved):
 *   71 planned steps: 12 verified / 2 review / 57 unmapped (48 no-candidate /
 *   6 rejected-candidate / 3 suspended-drift). Canonical status: 1 verified-all
 *   (f+1,4 [172,187]) / 11 partial / 19 unmapped-all / 0 review-only.
 *   Plan-key last-step: 21 verified / 1 review / 56 unmapped.
 *   Verified rows: 172 (standing LP1), 100 (standing RP2), 104 (standing RK4),
 *   149 (standing RP2, GATE-NOTE: standing row for a crouch step), 187
 *   (standing RK4), 76/78/77 (starts-airborne RK4, jump, SOFT waived),
 *   65/64 (jump LK3, SOFT waived). Review rows held: 182 (SOFT fail) and
 *   158 (STANCE-SOFT duck-dip). Suspended: 3,2 step 1, 3,3,2 step 1
 *   (prefix move 3, 63->None) and u+1,3 step 2 (prefix move u+1,3 itself,
 *   63->None). Rejected: 137 (throw), 351 (button 0 + throw), 43 (u/b+1),
 *   42 (u/f+1). Job 3: 0 fills (6 entries, all ROW-ONLY/soft). Job 4:
 *   3 joins (351 REJECTED, 182/158 CANDIDATE-not-wired), 0 promotions.
 *   Pair split: {LP1,RK4} 11, {RP2,LK3} 11, {RP2,RK4} 5, {LP1,LK3} 4.
 *   0 input-~ canonicals, 0 corrupted keys, 0 __main canonicals,
 *   0 CSV-only keys in Batch 3 scope. d/f+2,3 vs df+2,3 kept distinct.
 * Run: node --test game/tests/skull-batch3-step-plans.test.mjs   (from repo root)
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
const B2 = ["3,3", "3,3,4", "3,3,4~t7.bryan", "3,3,4~t7.bryan.2", "3,3,4~t7.bryan.3", "3,3~t7.bryan", "3,3~t7.bryan.2", "4,3", "4,3,4", "4,3,4*", "4,3,4*~t7.bryan", "4,3,4~t7.bryan", "4,3,4~t7.bryan.2", "4,3,4~t7.bryan.3", "4,3,f+4", "4,3,f+4~t7.bryan", "4,3,f+4~t7.bryan.2", "4,3,f+4~t7.bryan.3", "4,3~t7.bryan", "4,3~t7.bryan.2", "WS.3,4", "b+3+4,4", "b+3,4", "b+3,4~t7.bryan", "b+3,4~t7.bryan.2", "d/f+3+4,3", "f+4,3", "f+4,3,4", "ws3,4"];
const B2_VERIFIED_LAST = ["f+4,3", "f+4,3,4"];
const B2_VERIFIED_BUTTONS = {"103": 12, "104": 8, "193": 4, "194": 8, "199": 12};
const B3 = ["1+3,1", "1+3,1~t3.bryan", "1+3,1~t3.bryan.2", "1+3,1~t3.bryan.3", "1+3,1~t3.bryan.4", "1,4", "1,4~t7.bryan", "1,4~t7.bryan.2", "2,3", "2,3~t7.bryan", "2,3~t7.bryan.2", "2,4", "3,2", "3,2~t7.bryan", "3,2~t7.bryan.2", "3,3,2", "3,3,2~t7.bryan", "3,3,2~t7.bryan.2", "3,3,2~t7.bryan.3", "4,1", "SLS.2,4", "SLS.4,1", "SLS.4,1,4", "SS.2,3", "SS.2,3~t7.bryan", "SWA.2,4", "b+2,4", "b+2,4~t7.bryan", "b+2,4~t7.bryan.2", "b+3,2", "b+3,2~t7.bryan", "b+3,2~t7.bryan.2", "d+2,3", "d+2,3~t7.bryan", "d+2,3~t7.bryan.2", "d+3,2", "d+3,2~t7.bryan", "d+3,2~t7.bryan.2", "d/f+2,3", "d/f+2,3~t7.bryan", "df+2,3", "f+1,4", "f+4,1", "f+4,1~t7.bryan", "f+4,1~t7.bryan.2", "qcb+2,4", "qcb+2,4~t7.bryan", "qcf+4,1", "qcf+4,1,4", "qcf+4,1,4~t7.bryan", "qcf+4,1,4~t7.bryan.2", "qcf+4,1~t7.bryan", "u+1,3", "u+1,3~t3.bryan", "u+1,3~t3.bryan.2", "u+1,3~t3.bryan.3", "u+1,4", "u+1,4~t3.bryan", "u+1,4~t3.bryan.2", "u+1,4~t3.bryan.3", "u/b+1,3", "u/b+1,3~t3.bryan", "u/b+1,3~t3.bryan.2", "u/b+1,3~t3.bryan.3", "u/b+1,4", "u/b+1,4~t3.bryan", "u/b+1,4~t3.bryan.2", "u/b+1,4~t3.bryan.3", "u/f+1,3", "u/f+1,3~t3.bryan", "u/f+1,3~t3.bryan.2", "u/f+1,3~t3.bryan.3", "u/f+1,4", "u/f+1,4~t3.bryan", "u/f+1,4~t3.bryan.2", "u/f+1,4~t3.bryan.3", "uf+2,2,2,3", "uf+2,2,2,SNE.2,2,3"];
const B3_VERIFIED_LAST = ["f+1,4", "u+1,4", "u+1,4~t3.bryan", "u+1,4~t3.bryan.2", "u+1,4~t3.bryan.3", "u/b+1,3", "u/b+1,3~t3.bryan", "u/b+1,3~t3.bryan.2", "u/b+1,3~t3.bryan.3", "u/b+1,4", "u/b+1,4~t3.bryan", "u/b+1,4~t3.bryan.2", "u/b+1,4~t3.bryan.3", "u/f+1,3", "u/f+1,3~t3.bryan", "u/f+1,3~t3.bryan.2", "u/f+1,3~t3.bryan.3", "u/f+1,4", "u/f+1,4~t3.bryan", "u/f+1,4~t3.bryan.2", "u/f+1,4~t3.bryan.3"];
const B3_VERIFIED_BUTTONS = {"64": 4, "65": 4, "76": 8, "77": 8, "78": 8, "100": 2, "104": 8, "149": 2, "172": 1, "187": 8};
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
  assert.equal(Object.keys(plans).length, 198);
});

test('Batch 1 keys are exactly the documented 91 (cumulative: extra keys are exactly the Batch 2 + Batch 3 keys)', () => {
  assert.equal(B1.length, 91);
  for (const key of B1) assert.ok(plans[key], `Batch 1 key ${key} missing`);
  const extra = Object.keys(plans).filter((k) => !B1.includes(k));
  assert.deepEqual(extra.sort(), [...B2, ...B3].sort());
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

test('Batch 2 keys are exactly the documented 29 (cumulative: extra keys are exactly the Batch 3 keys)', () => {
  assert.equal(B2.length, 29);
  for (const key of B2) assert.ok(plans[key], `Batch 2 key ${key} missing`);
  const b1only = Object.keys(plans).filter((k) => !B1.includes(k) && !B2.includes(k));
  assert.deepEqual(b1only.sort(), B3);
});

test('Batch 2 verified steps carry rows (button == step bits, throw 0, row exists in bryan hit_frames); review/unmapped carry row null; no soft flags', () => {
  for (const key of B2) {
    for (const s of plans[key].steps) {
      assert.ok(!('soft' in s) || s.soft !== true, `${key} step ${s.step} carries a soft flag`);
      if (s.status === 'verified') {
        assert.notEqual(s.row, null, `${key} step ${s.step} verified but row null`);
        assert.ok(hf[String(s.row)], `${key} step ${s.step} verified on row ${s.row} which does not exist in the bryan hit_frames`);
        assert.equal(hf[String(s.row)][5], stepBits(s.step), `${key} step ${s.step} row ${s.row} button mismatch`);
        assert.equal(hf[String(s.row)][5], B2_VERIFIED_BUTTONS[String(s.row)], `${key} step ${s.step} row ${s.row} button mismatch (map)`);
        assert.equal(hf[String(s.row)][4], 0, `${key} step ${s.step} row ${s.row} is a throw row`);
      } else {
        assert.equal(s.row, null, `${key} step ${s.step} ${s.status} must not carry a playable row`);
      }
    }
  }
});

test('f+4,3 flagship: partial, step 1 unmapped (no candidate), step 2 VERIFIED row 193 (own standing LK3 row)', () => {
  const p = plans['f+4,3'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, 193]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'verified']);
  assert.equal(p.string_status, 'partial');
});

test('f+4,3,4 flagship: partial, step 1 unmapped, steps 2-3 VERIFIED rows 193/194', () => {
  const p = plans['f+4,3,4'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [null, 193, 194]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'verified', 'verified']);
  assert.equal(p.string_status, 'partial');
});

test('3,3 flagship: step 1 SUSPENDED-DRIFT (prefix move 3 ROW-CHANGED 63->None; stale jump row 63 never wired), step 2 unmapped (no candidate)', () => {
  const p = plans['3,3'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.equal(p.steps[0].status, 'unmapped');
  assert.ok(p.steps[0].reasons.join(' ').includes('SUSPENDED-DRIFT'), 'step 1 must record the suspension');
  assert.equal(p.steps[0].candidate_row, 63);
  assert.equal(p.steps[1].status, 'unmapped');
});

test('b+3+4,4 flagship: partial, step 1 VERIFIED row 199 (standing LK3+RK4 chord), step 2 review (candidate 200 SOFT fail; Job 4 join never promotes)', () => {
  const p = plans['b+3+4,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [199, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'review']);
  assert.equal(p.string_status, 'partial');
  assert.equal(p.steps[1].candidate_row, 200);
  assert.ok(p.steps[1].reasons.join(' ').includes('SOFT'), 'step 2 must record the SOFT review');
});

test('d/f+3+4,3 flagship: partial, step 1 VERIFIED row 103 (GATE-NOTE: standing row for a crouch step), step 2 review (candidate 192 SOFT fail)', () => {
  const p = plans['d/f+3+4,3'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [103, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'review']);
  assert.equal(p.string_status, 'partial');
  assert.ok(p.steps[0].reasons.join(' ').includes('GATE-NOTE'), 'step 1 standing row for a crouch step must carry the GATE-NOTE');
  assert.equal(p.steps[1].candidate_row, 192);
  assert.ok(p.steps[1].reasons.join(' ').includes('SOFT'), 'step 2 must record the SOFT review');
});

test('verified-last-step Batch 2 keys are exactly f+4,3 and f+4,3,4', () => {
  assert.equal(B2_VERIFIED_LAST.length, 2);
  for (const key of B2_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B2.filter((k) => !B2_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('Batch 2 has no CSV-only keys: every Batch 2 canonical has a plan', () => {
  for (const key of ['3,3', '3,3,4', '4,3', '4,3,4', '4,3,f+4', 'WS.3,4', 'b+3+4,4', 'b+3,4', 'd/f+3+4,3', 'f+4,3', 'f+4,3,4', 'ws3,4']) {
    assert.ok(plans[key], `${key} must have a plan`);
  }
});

test('Batch 3 keys are exactly the documented 78', () => {
  assert.equal(B3.length, 78);
  for (const key of B3) assert.ok(plans[key], `Batch 3 key ${key} missing`);
  const others = Object.keys(plans).filter((k) => !B1.includes(k) && !B2.includes(k) && !B3.includes(k));
  assert.deepEqual(others, []);
});

test('Batch 3 verified steps carry rows (button == step bits, throw 0, row exists in bryan hit_frames); review/unmapped carry row null; no soft flags', () => {
  for (const key of B3) {
    for (const s of plans[key].steps) {
      assert.ok(!('soft' in s) || s.soft !== true, `${key} step ${s.step} carries a soft flag`);
      if (s.status === 'verified') {
        assert.notEqual(s.row, null, `${key} step ${s.step} verified but row null`);
        assert.ok(hf[String(s.row)], `${key} step ${s.step} verified on row ${s.row} which does not exist in the bryan hit_frames`);
        assert.equal(hf[String(s.row)][5], stepBits(s.step), `${key} step ${s.step} row ${s.row} button mismatch`);
        assert.equal(hf[String(s.row)][5], B3_VERIFIED_BUTTONS[String(s.row)], `${key} step ${s.step} row ${s.row} button mismatch (map)`);
        assert.equal(hf[String(s.row)][4], 0, `${key} step ${s.step} row ${s.row} is a throw row`);
      } else {
        assert.equal(s.row, null, `${key} step ${s.step} ${s.status} must not carry a playable row`);
      }
    }
  }
});

test('f+1,4 flagship: verified-all on rows 172/187 (own standing LP1 + own standing RK4)', () => {
  const p = plans['f+1,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [172, 187]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('3,2 flagship: step 1 SUSPENDED-DRIFT (prefix move 3 ROW-CHANGED 63->None; stale jump row 63 never wired), step 2 unmapped (no candidate)', () => {
  const p = plans['3,2'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.equal(p.steps[0].status, 'unmapped');
  assert.ok(p.steps[0].reasons.join(' ').includes('SUSPENDED-DRIFT'), 'step 1 must record the suspension');
  assert.equal(p.steps[0].candidate_row, 63);
  assert.equal(p.steps[1].status, 'unmapped');
});

test('u+1,3 flagship: step 1 unmapped (no candidate), step 2 SUSPENDED-DRIFT (prefix move u+1,3 itself ROW-CHANGED 63->None)', () => {
  const p = plans['u+1,3'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.equal(p.steps[0].status, 'unmapped');
  assert.equal(p.steps[1].status, 'unmapped');
  assert.ok(p.steps[1].reasons.join(' ').includes('SUSPENDED-DRIFT'), 'step 2 must record the suspension');
  assert.equal(p.steps[1].candidate_row, 63);
});

test('2,4 flagship: partial, step 1 VERIFIED row 100, step 2 review (candidate 182 recorded-dest SOFT fail; Job 4 join never promotes)', () => {
  const p = plans['2,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [100, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'review']);
  assert.equal(p.string_status, 'partial');
  assert.equal(p.steps[1].candidate_row, 182);
  assert.ok(p.steps[1].reasons.join(' ').includes('SOFT'), 'step 2 must record the SOFT review');
});

test('b+2,4 flagship: partial, step 1 review (candidate 158 STANCE-SOFT duck-dip; Job 4 join never promotes), step 2 unmapped', () => {
  const p = plans['b+2,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['review', 'unmapped']);
  assert.equal(p.string_status, 'partial');
  assert.equal(p.steps[0].candidate_row, 158);
});

test('d/f+2,3 flagship: partial, step 1 VERIFIED row 149 (GATE-NOTE: standing row for a crouch step), step 2 unmapped', () => {
  const p = plans['d/f+2,3'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [149, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'unmapped']);
  assert.equal(p.string_status, 'partial');
  assert.ok(p.steps[0].reasons.join(' ').includes('GATE-NOTE'), 'step 1 standing row for a crouch step must carry the GATE-NOTE');
});

test('jump-last flagships: u+1,4 [NO row,76], u/b+1,3 [NO row,65], u/b+1,4 [NO row,78], u/f+1,3 [NO row,64], u/f+1,4 [NO row,77] (step 1 rejected rows 42/43 must NOT play)', () => {
  assert.deepEqual(plans['u+1,4'].steps.map((s) => s.row), [null, 76]);
  assert.deepEqual(plans['u/b+1,3'].steps.map((s) => s.row), [null, 65]);
  assert.deepEqual(plans['u/b+1,4'].steps.map((s) => s.row), [null, 78]);
  assert.deepEqual(plans['u/f+1,3'].steps.map((s) => s.row), [null, 64]);
  assert.deepEqual(plans['u/f+1,4'].steps.map((s) => s.row), [null, 77]);
  assert.equal(plans['u/b+1,3'].steps[0].candidate_row, 43);
  assert.equal(plans['u/f+1,3'].steps[0].candidate_row, 42);
});

test('1+3,1 flagship: NO row any step (throw rows 137/351 must NOT play)', () => {
  const p = plans['1+3,1'];
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'unmapped']);
  assert.equal(p.steps[0].candidate_row, 137);
  assert.equal(p.steps[1].candidate_row, 351);
});

test('verified-last-step Batch 3 keys are exactly the documented 21', () => {
  assert.equal(B3_VERIFIED_LAST.length, 21);
  for (const key of B3_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B3.filter((k) => !B3_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('Batch 3 has no CSV-only keys: every Batch 3 canonical has a plan', () => {
  for (const key of ['1+3,1', '1,4', '2,3', '2,4', '3,2', '3,3,2', '4,1', 'SLS.2,4', 'SLS.4,1', 'SLS.4,1,4', 'SS.2,3', 'SWA.2,4', 'b+2,4', 'b+3,2', 'd+2,3', 'd+3,2', 'd/f+2,3', 'df+2,3', 'f+1,4', 'f+4,1', 'qcb+2,4', 'qcf+4,1', 'qcf+4,1,4', 'u+1,3', 'u+1,4', 'u/b+1,3', 'u/b+1,4', 'u/f+1,3', 'u/f+1,4', 'uf+2,2,2,3', 'uf+2,2,2,SNE.2,2,3']) {
    assert.ok(plans[key], `${key} must have a plan`);
  }
});

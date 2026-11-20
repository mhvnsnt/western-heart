/* Diablo Batch 4 step plans (triples/quads/rest strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/DIABLO-BATCH4-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on diablo Batch 3 (feat/diablo-batch3-step-plans-20261025,
 * PR #1115), which is stacked on diablo Batch 2 (feat/diablo-batch2-step-plans-20261025,
 * PR #1114), which is stacked on diablo Batch 1 (feat/diablo-batch1-step-plans-20261025,
 * PR #1113), which is stacked on #1096 (feat/batch1-step-plans-pantera-20261024, the
 * step-playback engine). It does NOT stack on the Pantera plan branches
 * (#1099/#1101/#1102), the burger plan branches (#1103/#1104/#1105/#1107), or the
 * demonio plan branches (#1108/#1110/#1111/#1112): diablo.json plans do not conflict
 * with pantera.json, burger.json, or demonio.json plans.
 * It does NOT include #1097's Pantera Batch 1 follow-up fills (Pantera-specific,
 * and its row-49 SOFT fill is still unapproved); no SOFT fill is inherited here.
 * This PR does not touch `fighter.js`: #1096's merge onto post-#1078 main must
 * reconcile #1078's `fighter.js` changes with #1096's engine branch, and that
 * belongs to #1096's merge, not this PR.
 * Bank (verified, not assumed — carried from diablo Batches 1–3 four-way proof):
 * diablo's T3 bank is HEIHACHI (t3_source heihachi, t3_bank moveset_heihachi.json,
 * on BOTH the Batch 3 branch and main; t3/ directory listing; Job 1/Job 4 bank
 * heihachi_on_jin; Job 2 bank heihachi). Bank resolution: moveset/Job 2 bank
 * heihachi <-> Job 1/Job 4/pack bank heihachi_on_jin <-> divmot13_heihachi.bin
 * on the jin rig (the heihachi/ dir carries hit_frames + skeleton but NO
 * rows.pack.json, the known 404 gap; the playable pack lives under
 * heihachi_on_jin, and the two hit_frames.json files are the SAME blob
 * a87184616...). Gap-1 for Batch 4: main heihachi hit_frames blob a87184616…,
 * heihachi_on_jin rows.pack blob 9e59dfe5… (= #1109 baked pack),
 * heihachi_on_jin skeleton blob 7fa83b40…, main diablo.json blob ad22b2d8… —
 * all IDENTICAL to the Batch 1 baseline.
 * Heihachi-bank rules, per-bank evidence (never a cross-bank blanket ban):
 * row 35 does NOT EXIST in this bank (absent from both hit_frames and Job 1),
 * so no row-35 rule applies; row 220 is a JUMP RK4 row here (hit_frames
 * [39,39,88,535,0,8], Job 1 stance jump), gate-adjudicated like any row, NOT
 * jin's standing RP2 row, NOT king's jumping chord row, NOT bryan's button-0
 * row; heihachi_on_jin row 216 is a DUCK-DIP row, NOT jin row 216's jump row
 * and NOT king row 216's dash Konvict Kick.
 * Canonicalization is the CORRECTED rule (demonio Batch 2 finding): strip ONLY
 * a trailing ~t[378].[a-z]+(.N)?$ source-variant suffix; input-~ is Tekken
 * cancel notation, part of the move. Batch 4 contains 4 input-~ canonicals,
 * ALL rest/CSV-only (1,2,2~1+2,u, 2,2~1+2,u, b+1,2~1+2,u, f+2~1+2,u) and NO
 * __main records. Suspended-drift: 2 steps — 1,2,4 step 1 and 1,b+2,4 step 1
 * (prefix move 1 ROW-CHANGED 46->None; stale candidate row 46 documented,
 * never wired). The third row-changed move (1_r46, u+1,1~t3.heihachi.2) is not
 * a Batch 4 step prefix. Spelling quirks kept as stored keys: WS.3,1+2 vs
 * ws3,1+2 and the d/f+3 vs df+3 families are distinct canonicals — not merged,
 * not smoothed over. Corrupted key df+1,&amp;#58;2* is NOT Batch 4 scope: it
 * lives in Batch 1 scope (LP1/RP2 union) and is quarantined-only on main.
 * Standing rows verified for crouch-context steps (d/f+3,2,2,4-family steps
 * with rows 226, 227, 230, 231, 232, 235, 236) follow the demonio Batch 1 /
 * diablo Batch 1 / diablo Batch 3 precedent: the pipeline stance gate flags
 * crouch rows for non-crouch steps, not standing rows for crouch steps; if
 * the gate is ever tightened these steps must be re-adjudicated. Rows 228
 * (crouch), 233 and 237 (duck-dip) pass for crouch context outright — NOT
 * gate-note cases.
 * Rules asserted here (all data-level, no THREE needed):
 *   1. diablo.json still has 661 moves / 90 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 217 keys (175 Batches 1–3 + 42 Batch 4).
 *   3. Batch 4 keys are exactly the documented 42 (28 planned canonicals + 14 twins).
 *   4. Batch 4 verified steps always carry a row whose heihachi hit_frames
 *      button equals the step bits and whose throw flag is 0; no verified
 *      ground-context step uses row 35 (row 35 does not exist in this bank);
 *      review/unmapped steps carry row null. No Batch 4 step carries a soft
 *      flag (Batch 4 wires zero Job 3 fills and zero SOFT fills).
 *   5. 2,1,2,2,3 flagship: verified-all on rows 157/158/159/160/161 (standing).
 *   6. f+1+2,b+2,4 flagship: partial on rows [223, null, null] (step 1 verified,
 *      steps 2–3 review: STANCE-SOFT duck-dip rows 207/214 for standing steps).
 *   7. u/f+4,3,1 flagship: partial on rows [86, 150, null] (jump first steps verified).
 *   8. 1,2,4 flagship: unmapped-all on rows [null, null, null], step 1
 *      SUSPENDED-DRIFT (prefix move 1 ROW-CHANGED 46->None).
 *   9. d/f+3,2,2,4,4,1,2,1,2,1 flagship: partial on rows
 *      [null, 226, 227, 228, null, 230, 235, 236, 237, null] (crouch context).
 *  10. The verified-last-step Batch 4 keys are exactly the 13 listed below,
 *      and verified rows carry the step buttons in the repo heihachi
 *      hit_frames.json.
 *  11. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Run: node --test game/tests/diablo-batch4-step-plans.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const diablo = JSON.parse(readFileSync(join(ROOT, 'game/assets/movesets/diablo.json'), 'utf8'));
const fighterSrc = readFileSync(join(ROOT, 'game/js/fighter.js'), 'utf8');
const hfPath = join(ROOT, 'game/assets/anim/t3/heihachi/hit_frames.json');
const hf = JSON.parse(readFileSync(hfPath, 'utf8')).rows;

const plans = diablo.string_step_plans.plans;
const B4 = ["1,2,4", "1,2,4*", "1,2,4~t7.heihachi", "1,2,4~t7.heihachi.2", "1,2,4~t7.heihachi.3", "1,b+2,4", "1,b+2,4~t7.heihachi", "1,b+2,4~t7.heihachi.2", "1,b+2,4~t7.heihachi.3", "2+4,1", "2+4,1~t3.heihachi", "2,1,2,2,3", "2,1,2,2,3,4", "2,1,2,2,3,4,4", "2,1,2,2,3,4,4,1", "2,1,2,2,3,4,4,1,2", "2,1,2,2,3,4,4,1,2,1", "2,1,2,2,3,4~t3.heihachi", "2,1,2,2,3~t3.heihachi", "WS.3,1+2", "WS.3,1+2~t7.heihachi", "d/f+3,2,2,4", "d/f+3,2,2,4,4", "d/f+3,2,2,4,4,1", "d/f+3,2,2,4,4,1,2", "d/f+3,2,2,4,4,1,2,1", "d/f+3,2,2,4,4,1,2,1,2", "d/f+3,2,2,4,4,1,2,1,2,1", "d/f+3,2,2,4,4,1,2,1,2,1~t3.heihachi", "d/f+3,2,2,4,4,1,4", "d/f+3,2,2,4,4,1,4,1", "d/f+3,2,2,4,4,1,4,1,2", "d/f+3,2,2,4,4,1,4,1,2,1", "d/f+3,2,2,4,4,1,4,1,2,4", "d/f+3,2,2,4,4,1,4,1,2,4~t3.heihachi", "df+3,1+2", "df+3,1+2,1", "f+1+2,b+2,4", "f+1+2,b+2,4,1", "f+1+2,b+2,4~t3.heihachi", "u/f+4,3,1", "ws3,1+2"];
const B4_VERIFIED_LAST = ["2,1,2,2,3", "2,1,2,2,3,4,4", "2,1,2,2,3,4,4,1", "2,1,2,2,3,4,4,1,2", "2,1,2,2,3~t3.heihachi", "d/f+3,2,2,4", "d/f+3,2,2,4,4,1", "d/f+3,2,2,4,4,1,2", "d/f+3,2,2,4,4,1,2,1", "d/f+3,2,2,4,4,1,2,1,2", "d/f+3,2,2,4,4,1,4", "d/f+3,2,2,4,4,1,4,1", "d/f+3,2,2,4,4,1,4,1,2"];
const VERIFIED_BUTTONS = {"86": 8, "150": 4, "157": 2, "158": 1, "159": 2, "160": 2, "161": 4, "163": 8, "164": 1, "165": 2, "223": 3, "226": 2, "227": 2, "228": 8, "230": 1, "231": 8, "232": 1, "233": 2, "235": 2, "236": 1, "237": 2};

function stepBits(step) {
  const seg = step.split('.').pop();
  let b = 0;
  for (const c of seg) if ('1234'.includes(c)) b |= 1 << (Number(c) - 1);
  return b;
}

test('diablo move/string counts unchanged by the additive plans block', () => {
  assert.equal(Object.keys(diablo.moves).length, 661);
  assert.equal(diablo.strings.length, 90);
  assert.equal(Object.keys(plans).length, 217);
});

test('Batch 4 keys are exactly the documented 42', () => {
  assert.equal(B4.length, 42);
  for (const key of B4) assert.ok(plans[key], `Batch 4 key ${key} missing`);
  const earlier = Object.keys(plans).filter((k) => !B4.includes(k));
  assert.equal(earlier.length, 175);
});

test('Batch 4 verified steps carry rows (button == step bits, throw 0, never row 35 on ground); review/unmapped carry row null; no soft flags', () => {
  for (const key of B4) {
    for (const s of plans[key].steps) {
      assert.ok(!('soft' in s) || s.soft !== true, `${key} step ${s.step} carries a soft flag`);
      if (s.status === 'verified') {
        assert.notEqual(s.row, null, `${key} step ${s.step} verified but row null`);
        if (!plans[key].jumping_context) assert.notEqual(s.row, 35, `${key} step ${s.step} verified on row 35 for a ground step (row 35 does not exist in the heihachi bank)`);
        assert.equal(hf[String(s.row)][5], stepBits(s.step), `${key} step ${s.step} row ${s.row} button mismatch`);
        assert.equal(hf[String(s.row)][5], VERIFIED_BUTTONS[String(s.row)], `${key} step ${s.step} row ${s.row} button mismatch (map)`);
        assert.equal(hf[String(s.row)][4], 0, `${key} step ${s.step} row ${s.row} is a throw row`);
      } else {
        assert.equal(s.row, null, `${key} step ${s.step} ${s.status} must not carry a playable row`);
      }
    }
  }
});

test('2,1,2,2,3 flagship: verified-all on rows 157/158/159/160/161 (standing)', () => {
  const p = plans['2,1,2,2,3'];
  assert.equal(p.steps.length, 5);
  assert.deepEqual(p.steps.map((s) => s.row), [157, 158, 159, 160, 161]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified', 'verified', 'verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('f+1+2,b+2,4 flagship: partial on rows [223, null, null] (steps 2–3 review: STANCE-SOFT rows 207/214)', () => {
  const p = plans['f+1+2,b+2,4'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [223, null, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'review', 'review']);
  assert.equal(p.string_status, 'partial');
});

test('u/f+4,3,1 flagship: partial on rows [86, 150, null] (jump first steps verified)', () => {
  const p = plans['u/f+4,3,1'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [86, 150, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified', 'unmapped']);
  assert.equal(p.string_status, 'partial');
  assert.equal(p.jumping_context, true);
});

test('1,2,4 flagship: unmapped-all on rows [null, null, null], step 1 SUSPENDED-DRIFT', () => {
  const p = plans['1,2,4'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'unmapped', 'unmapped']);
  assert.equal(p.string_status, 'unmapped-all');
  assert.ok(p.steps[0].reasons.join(' ').includes('SUSPENDED-DRIFT'), 'step 1 must carry the SUSPENDED-DRIFT reason');
});

test('d/f+3,2,2,4,4,1,2,1,2,1 flagship: partial on rows [null, 226, 227, 228, null, 230, 235, 236, 237, null] (crouch)', () => {
  const p = plans['d/f+3,2,2,4,4,1,2,1,2,1'];
  assert.equal(p.steps.length, 10);
  assert.deepEqual(p.steps.map((s) => s.row), [null, 226, 227, 228, null, 230, 235, 236, 237, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'verified', 'verified', 'verified', 'review', 'verified', 'verified', 'verified', 'verified', 'unmapped']);
  assert.equal(p.string_status, 'partial');
});

test('verified-last-step Batch 4 keys are exactly the documented 13', () => {
  assert.equal(B4_VERIFIED_LAST.length, 13);
  for (const key of B4_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B4.filter((k) => !B4_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

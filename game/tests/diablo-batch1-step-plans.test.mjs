/* Diablo Batch 1 step plans (LP1/RP2-only strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/DIABLO-BATCH1-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on #1096 (feat/batch1-step-plans-pantera-20261024,
 * the step-playback engine). It does NOT stack on the Pantera plan branches
 * (#1099/#1101/#1102), the burger plan branches (#1103/#1104/#1105/#1107), or
 * the demonio plan branches (#1108/#1110/#1111/#1112): diablo.json plans do
 * not conflict with pantera.json, burger.json, or demonio.json plans.
 * It does NOT include #1097's Pantera Batch 1 follow-up fills (Pantera-specific,
 * and its row-49 SOFT fill is still unapproved); no SOFT fill is inherited here.
 * This PR does not touch `fighter.js`: #1096's merge onto post-#1078 main must
 * reconcile #1078's `fighter.js` changes with #1096's engine branch, and that
 * belongs to #1096's merge, not this PR.
 * Bank (verified, not assumed): diablo's T3 bank is HEIHACHI (t3_source
 * heihachi, t3_bank moveset_heihachi.json, on BOTH #1096 and main; t3/
 * directory listing; Job 1/Job 4 bank heihachi_on_jin; Job 2 bank heihachi).
 * Bank resolution, documented not assumed: moveset/Job 2 bank heihachi <->
 * Job 1/Job 4/pack bank heihachi_on_jin <-> divmot13_heihachi.bin on the jin
 * rig (the heihachi/ dir carries hit_frames + skeleton but NO rows.pack.json,
 * the known 404 gap; the playable pack lives under heihachi_on_jin, and the
 * two hit_frames.json files are the SAME blob a87184616...).
 * Heihachi-bank rules, per-bank evidence (never a cross-bank blanket ban):
 * row 35 does NOT EXIST in this bank (absent from both hit_frames and Job 1),
 * so no row-35 rule applies; row 220 is a JUMP RK4 row here, gate-adjudicated
 * like any row, NOT jin's standing RP2 row, NOT king's jumping chord row,
 * NOT bryan's button-0 row; heihachi_on_jin row 216 is a DUCK-DIP row, NOT
 * jin row 216's jump row and NOT king row 216's dash Konvict Kick.
 * Diablo's own LP1 move carries t3_row 46, and Job 1 row 46 is STARTS-AIRBORNE
 * (y0 1.695 vs standingY 0.955) — the same class as Pantera LP1->king row 38
 * (jumping) — so every ground-context step with candidate row 46 fails the
 * stance gate; prefix move 1 is ALSO ROW-CHANGED 46->None (#1096 vs current
 * main), so all 13 1-family step 1s are SUSPENDED-DRIFT.
 * Canonicalization is the CORRECTED rule (demonio Batch 2 finding): strip ONLY
 * a trailing ~t[378].[a-z]+(.N)?$ source-variant suffix; input-~ is Tekken
 * cancel notation, part of the move. Diablo DOES contain input-~ canonicals
 * (6 own canonicals: 1,2,2~1, 1,2,2~1+2, 1,2,2~1,1+2, 2,2~1+2, b+1,2~1+2,
 * f+2~1,1+2) — unlike Pantera/burger, whose inventories were provably inert.
 * Under the old split('~')[0] rule this batch would have had 61 canonicals
 * including a bogus single 'f+2', with cancel strings misfiled as variants
 * of 1,2,2 / 2,2 / b+1,2; the corrected universe has 66. No verified row is
 * affected by the correction (all misfiled strings are unmapped-all either
 * way); the only plan-status effect is the f+2~1,1+2 family (old: review via
 * bogus 'f+2'; corrected: unmapped-all).
 * Rules asserted here (all data-level, no THREE needed):
 *   1. diablo.json still has 661 moves / 90 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 111 keys (60 planned canonicals + 51 twins).
 *   3. Batch 1 verified steps always carry a row whose heihachi hit_frames
 *      button equals the step bits and whose throw flag is 0; no verified
 *      ground-context step uses row 35 (row 35 does not exist in this bank);
 *      review/unmapped steps carry row null. No Batch 1 step carries a soft
 *      flag (Batch 1 wires zero Job 3 fills and zero SOFT fills).
 *   4. 2,1 flagship: verified-all on rows 157/158 (recorded-path).
 *   5. 2,1,2,2 flagship: verified-all on rows 157/158/159/160.
 *   6. b+1+2,2 flagship: verified-all on rows 98/99.
 *   7. d/f+1+2,2 flagship: verified-all on rows 110/204 (crouch context).
 *   8. u+1,1 flagship: step 2 verified row 40 (jump context only).
 *   9. 1,1 flagship: step 1 SUSPENDED-DRIFT (prefix move 1 ROW-CHANGED 46->None),
 *      row null, never wired on stale data.
 *  10. b+2,1 flagship: step 1 review (STANCE-SOFT duck-dip row 207), row null.
 *  11. TACKLE family (6 keys) have NO plan key.
 *  12. The verified-last-step Batch 1 keys are exactly the 29 listed below,
 *      and verified rows carry the step buttons in the repo heihachi
 *      hit_frames.json.
 *  13. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Cumulative update (Diablo Batch 2, 2026-10-25): plan count 111 -> 132; extra-keys
 * assertion now expects exactly the 21 Batch 2 keys; all Batch 1 content assertions
 * preserved verbatim (burger test-evolution rule; Pantera's latent break NOT copied).
 * Cumulative update (Diablo Batch 3, 2026-10-25): plan count 132 -> 175; extra-keys
 * assertion now expects exactly the 21 Batch 2 keys + the 43 Batch 3 keys; all Batch 1
 * content assertions preserved verbatim (burger test-evolution rule; Pantera's latent
 * break NOT copied).
 * Cumulative update (Diablo Batch 4, 2026-10-25): plan count 175 -> 217; extra-keys
 * assertion now expects exactly the 21 Batch 2 keys + the 43 Batch 3 keys + the 42
 * Batch 4 keys; all Batch 1 content assertions preserved verbatim (burger
 * test-evolution rule; Pantera's latent break NOT copied).
 * Run: node --test game/tests/diablo-batch1-step-plans.test.mjs   (from repo root)
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
const B1 = ["1,1", "1,1,1", "1,1,2", "1,1,2~t7.heihachi", "1,1,2~t7.heihachi.2", "1,1,2~t7.heihachi.3", "1,1,WAR.2", "1,1~t3.heihachi", "1,1~t3.heihachi.2", "1,1~t3.heihachi.3", "1,1~t7.heihachi", "1,1~t7.heihachi.2", "1,2", "1,2,2", "1,2,2~1", "1,2,2~1+2", "1,2,2~1+2~t7.heihachi", "1,2,2~1+2~t7.heihachi.2", "1,2,2~1,1+2", "1,2,2~t7.heihachi", "1,2,2~t7.heihachi.2", "1,2,2~t7.heihachi.3", "1,2~t7.heihachi", "1,2~t7.heihachi.2", "1,b+2", "1,b+2,1", "1,b+2,1~t7.heihachi", "1,b+2,1~t7.heihachi.2", "1,b+2,1~t7.heihachi.3", "1,b+2,2", "1,b+2,WAR.2", "1,b+2~t7.heihachi", "1,b+2~t7.heihachi.2", "2,1", "2,1,2", "2,1,2,2", "2,1,2,2~t3.heihachi", "2,1,2~t3.heihachi", "2,1~t3.heihachi", "2,2", "2,2~1+2", "2,2~1+2~t7.heihachi", "2,2~t7.heihachi", "2,2~t7.heihachi.2", "FUJ.1,1", "FUJ.1,2", "R.1,b+2,1+2", "R.1,b+2,1+2~t7.heihachi", "R.1,b+2,1+2~t7.heihachi.2", "R.b+2,1+2", "R.b+2,1+2~t7.heihachi", "RAI.2,1", "RAI.2,1~t7.heihachi", "SS.2,1", "SS.2,1~t7.heihachi", "b+1+2,1", "b+1+2,1+2", "b+1+2,1+2~t7.heihachi", "b+1+2,1,2", "b+1+2,2", "b+1+2,2,2", "b+1+2,2,2,1", "b+1,2", "b+1,2~1+2", "b+1,2~1+2~t7.heihachi", "b+1,2~t7.heihachi", "b+2,1", "b+2,2", "d+1,2", "d+1,2__main", "d+1,2~t3.heihachi", "d+1,2~t7.heihachi", "d+1,2~t7.heihachi.2", "d/f+1+2,2", "d/f+1,1", "d/f+1,1~t7.heihachi", "d/f+1,2", "d/f+1,2~t7.heihachi", "df+1,&amp;#58;2", "df+1,&amp;#58;2*", "df+1,1", "df+1,2", "df+1,2*", "df+2,1", "df+2,WAR.1", "f+1+2,1", "f+1+2,1,2", "f+1+2,2", "f+1+2,2,2", "f+1+2,b+2", "f+1+2,b+2,1", "f+1+2,b+2,1~t3.heihachi", "f+2,1", "f+2,2", "f+2~1,1+2", "u+1,1", "u+1,1~t3.heihachi", "u+1,1~t3.heihachi.2", "u+1,1~t3.heihachi.3", "u+1,2", "u/b+1,1", "u/b+1,1~t3.heihachi", "u/b+1,1~t3.heihachi.2", "u/b+1,1~t3.heihachi.3", "u/b+1,2", "u/f+1,1", "u/f+1,1~t3.heihachi", "u/f+1,1~t3.heihachi.2", "u/f+1,1~t3.heihachi.3", "u/f+1,2", "uf+2,1"];
const B2 = ["3,4", "3,4~t7.heihachi", "FUJ.3,4", "WS.4,4", "WS.4,4~t7.heihachi", "b+3,3", "b+3,3~t7.heihachi", "b+3,3~t7.heihachi.2", "d/f+4,4", "d/f+4,4,4", "u/f+3,4", "u/f+3,4~t3.heihachi", "u/f+3,4~t3.heihachi.2", "u/f+3,4~t3.heihachi.3", "u/f+4,3", "u/f+4,3~t3.heihachi", "u/f+4,4", "u/f+4,4~t3.heihachi", "u/f+4,4~t3.heihachi.2", "uf+3,4", "ws4,4"];
const B3 = ["1+3,1", "1+3,1~t3.heihachi", "3,2", "b+1,4", "b+2,4", "b+3,2", "b+3,3,H.2", "d+3,H.2", "d/f+3,2", "d/f+3,2,2", "d/f+4,1", "d/f+4,1~t3.heihachi", "d/f+4,2", "df+4,2", "f+1+4,1", "f+1+4,1,1", "f+2,3", "f+2,3~t7.heihachi", "u+1,3", "u+1,3~t3.heihachi", "u+1,3~t3.heihachi.2", "u+1,3~t3.heihachi.3", "u+1,4", "u+1,4~t3.heihachi", "u+1,4~t3.heihachi.2", "u+1,4~t3.heihachi.3", "u/b+1,3", "u/b+1,3~t3.heihachi", "u/b+1,3~t3.heihachi.2", "u/b+1,3~t3.heihachi.3", "u/b+1,4", "u/b+1,4~t3.heihachi", "u/b+1,4~t3.heihachi.2", "u/b+1,4~t3.heihachi.3", "u/f+1,3", "u/f+1,3~t3.heihachi", "u/f+1,3~t3.heihachi.2", "u/f+1,3~t3.heihachi.3", "u/f+1,4", "u/f+1,4~t3.heihachi", "u/f+1,4~t3.heihachi.2", "u/f+1,4~t3.heihachi.3", "uf+4,H.1"];
const B4 = ["1,2,4", "1,2,4*", "1,2,4~t7.heihachi", "1,2,4~t7.heihachi.2", "1,2,4~t7.heihachi.3", "1,b+2,4", "1,b+2,4~t7.heihachi", "1,b+2,4~t7.heihachi.2", "1,b+2,4~t7.heihachi.3", "2+4,1", "2+4,1~t3.heihachi", "2,1,2,2,3", "2,1,2,2,3,4", "2,1,2,2,3,4,4", "2,1,2,2,3,4,4,1", "2,1,2,2,3,4,4,1,2", "2,1,2,2,3,4,4,1,2,1", "2,1,2,2,3,4~t3.heihachi", "2,1,2,2,3~t3.heihachi", "WS.3,1+2", "WS.3,1+2~t7.heihachi", "d/f+3,2,2,4", "d/f+3,2,2,4,4", "d/f+3,2,2,4,4,1", "d/f+3,2,2,4,4,1,2", "d/f+3,2,2,4,4,1,2,1", "d/f+3,2,2,4,4,1,2,1,2", "d/f+3,2,2,4,4,1,2,1,2,1", "d/f+3,2,2,4,4,1,2,1,2,1~t3.heihachi", "d/f+3,2,2,4,4,1,4", "d/f+3,2,2,4,4,1,4,1", "d/f+3,2,2,4,4,1,4,1,2", "d/f+3,2,2,4,4,1,4,1,2,1", "d/f+3,2,2,4,4,1,4,1,2,4", "d/f+3,2,2,4,4,1,4,1,2,4~t3.heihachi", "df+3,1+2", "df+3,1+2,1", "f+1+2,b+2,4", "f+1+2,b+2,4,1", "f+1+2,b+2,4~t3.heihachi", "u/f+4,3,1", "ws3,1+2"];
const B1_VERIFIED_LAST = ["2,1", "2,1,2", "2,1,2,2", "2,1,2,2~t3.heihachi", "2,1,2~t3.heihachi", "2,1~t3.heihachi", "b+1+2,1,2", "b+1+2,2", "b+1+2,2,2", "b+2,2", "d/f+1+2,2", "f+1+2,1,2", "f+1+2,2", "f+1+2,2,2", "u+1,1", "u+1,1~t3.heihachi", "u+1,1~t3.heihachi.2", "u+1,1~t3.heihachi.3", "u+1,2", "u/b+1,1", "u/b+1,1~t3.heihachi", "u/b+1,1~t3.heihachi.2", "u/b+1,1~t3.heihachi.3", "u/b+1,2", "u/f+1,1", "u/f+1,1~t3.heihachi", "u/f+1,1~t3.heihachi.2", "u/f+1,1~t3.heihachi.3", "u/f+1,2"];
const VERIFIED_BUTTONS = {"40": 1, "41": 1, "42": 1, "52": 2, "53": 2, "54": 2, "98": 3, "99": 2, "110": 3, "123": 1, "146": 2, "147": 2, "149": 2, "157": 2, "158": 1, "159": 2, "160": 2, "204": 2, "223": 3};

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

test('Batch 1 keys are exactly the documented 111', () => {
  assert.equal(B1.length, 111);
  for (const key of B1) assert.ok(plans[key], `Batch 1 key ${key} missing`);
  const extra = Object.keys(plans).filter((k) => !B1.includes(k));
  assert.deepEqual(extra.sort(), [...B2, ...B3, ...B4].sort());
});

test('Batch 1 verified steps carry rows (button == step bits, throw 0, never row 35 on ground); review/unmapped carry row null; no soft flags', () => {
  for (const key of B1) {
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

test('2,1 flagship: verified-all on rows 157/158 (recorded-path)', () => {
  const p = plans['2,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [157, 158]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('2,1,2,2 flagship: verified-all on rows 157/158/159/160', () => {
  const p = plans['2,1,2,2'];
  assert.equal(p.steps.length, 4);
  assert.deepEqual(p.steps.map((s) => s.row), [157, 158, 159, 160]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified', 'verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('b+1+2,2 flagship: verified-all on rows 98/99', () => {
  const p = plans['b+1+2,2'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [98, 99]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('d/f+1+2,2 flagship: verified-all on rows 110/204 (crouch context)', () => {
  const p = plans['d/f+1+2,2'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [110, 204]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('u+1,1 flagship: step 2 verified row 40 (jump context only)', () => {
  const p = plans['u+1,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, 40]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'verified']);
  assert.equal(p.jumping_context, true);
});

test('1,1 flagship: step 1 SUSPENDED-DRIFT (prefix move 1 ROW-CHANGED 46->None), row null', () => {
  const p = plans['1,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.equal(p.steps[0].status, 'unmapped');
  assert.ok(p.steps[0].reasons.join(' ').includes('SUSPENDED-DRIFT'), 'step 1 must carry the SUSPENDED-DRIFT reason');
});

test('b+2,1 flagship: step 1 review (STANCE-SOFT duck-dip row 207), row null', () => {
  const p = plans['b+2,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.equal(p.steps[0].status, 'review');
});

test('TACKLE family (throw class) have NO plan key', () => {
  for (const k of ['TACKLE.1,1', 'TACKLE.1,1,1', 'TACKLE.1,1,1,1', 'TACKLE.2,2', 'TACKLE.2,2,2', 'TACKLE.2,2,2,2']) assert.ok(!plans[k], `${k} must have no plan`);
});

test('verified-last-step Batch 1 keys are exactly the documented 29', () => {
  assert.equal(B1_VERIFIED_LAST.length, 29);
  for (const key of B1_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B1.filter((k) => !B1_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

/* Kinpo Batch 4 step plans (triples/quads + rest, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/KINPO-BATCH4-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on kinpo Batch 3 (feat/kinpo-batch3-step-plans-20261025,
 * PR #1119), which stacks on kinpo Batch 2 (PR #1118), which stacks on kinpo Batch 1
 * (PR #1117), which stacks on #1096 (feat/batch1-step-plans-pantera-20261024, the
 * step-playback engine). It does NOT stack on the Pantera plan branches
 * (#1099/#1101/#1102), the burger plan branches (#1103/#1104/#1105/#1107), the demonio
 * plan branches (#1108/#1110/#1111/#1112), or the diablo plan branches
 * (#1113/#1114/#1115/#1116): kinpo.json plans do not conflict with pantera.json,
 * burger.json, demonio.json, or diablo.json plans.
 * It does NOT include #1097's Pantera Batch 1 follow-up fills (Pantera-specific,
 * and its row-49 SOFT fill is still unapproved); no SOFT fill is inherited here.
 * This PR does not touch `fighter.js`: #1096's merge onto post-#1078 main must
 * reconcile #1078's `fighter.js` changes with #1096's engine branch, and that
 * belongs to #1096's merge, not this PR.
 * Bank (verified, not assumed): kinpo's T3 bank is JIN (t3_source jin, t3_bank
 * moveset_jin.json, on BOTH the Batch 3 branch and main; t3/ directory listing;
 * Job 1 bank jin (220 rows); Job 2 kinpo entries all bank jin (525); Job 4 jin
 * candidates (47)). Bank resolution, documented not assumed: kinpo's T7/T8 base
 * IS Asuka (tekken_base Asuka, merge_sources t8/t7 asuka), but Asuka debuted in
 * Tekken 5 and has NO T3 bank in this repo (no asuka dir under t3/), so the
 * file's T3 fallback bank is jin — the burger pattern (Bob -> bryan). The
 * T7-Asuka re-match is future work; this batch adjudicates against jin as the
 * file declares.
 * Jin-bank rules, per-bank evidence (never a cross-bank blanket ban): row 35
 * EXISTS here (hit_frames [11,12,39,535,0,1], Job 1 stance starts-airborne) —
 * NOT blanket-banned by number, but the stance gate rejects it for ground
 * steps; kinpo's own LP1 move 1 carries t3_row 35 and is ALSO ROW-CHANGED
 * 35->None (Batch 3 branch vs current main) — Batch 4's two suspended-drift
 * steps are exactly the step-1s whose prefix is move 1 (1,2,3 / 1,2,4). Row 220
 * is a STANDING RP2 row here (hit_frames [12,12,41,1042,0,2], Job 1 standing) —
 * gate-adjudicated like any row, NOT king's jumping chord row, NOT bryan's
 * button-0 row, NOT heihachi's jump RK4 row. Jin row 216 is a JUMP row, NOT
 * king row 216's dash Konvict Kick.
 * Canonicalization is the CORRECTED rule (demonio Batch 2 finding): strip ONLY
 * a trailing ~t[378].[a-z]+(.N)?$ source-variant suffix; input-~ is Tekken
 * cancel notation, part of the move. Kinpo Batch 4 contains exactly ONE
 * input-~ canonical: 3~4,D/F, the file's ONLY old-vs-corrected diff, filed as
 * its own rest canonical with NO plan (never a variant of 3). Spelling quirks
 * kept: WS.2 vs ws2 families, u/b,b vs ub,b, d/f vs df spellings are distinct
 * canonicals, never merged.
 * Rules asserted here (all data-level, no THREE needed):
 *   1. kinpo.json still has 525 moves / 101 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 177 keys (115 Batches 1-3 + 62 Batch 4); the
 *      Batch 4 keys are exactly the documented 62; all Batches 1-3 keys present.
 *   3. Batch 4 verified steps always carry a row whose jin hit_frames
 *      button equals the step bits and whose throw flag is 0; no verified
 *      ground-context step uses row 35 (starts-airborne per jin Job 1);
 *      review/unmapped steps carry row null. No Batch 4 step carries a soft
 *      flag (Batch 4 wires one Job 3 fill — row 92, exact + FULL — and zero
 *      SOFT fills; the fill itself carries no soft flag).
 *   4. 2,1,2,2,3 flagship: verified-all [220,221,222,223,224].
 *   5. 2,1,4 flagship: verified-all [220,221,230].
 *   6. 2,1,4,4,2,4 flagship: partial [220,221,230,None,232,233] — step 4
 *      candidate 231 rejected (button 12 != step bits 8 — kick-chord row for
 *      a single RK4 step; same row, same result as demonio Batch 4's
 *      2,1,4,4 step 4 gate failure).
 *   7. 2,1,2,2,3,4 flagship: partial [220,221,222,223,224,review] — last step
 *      candidate 225 recorded-dest SOFT-held (window [16.5,21.5], legR peak 6).
 *   8. 4,1,2 flagship: partial [review,unmapped,186] — step 1 candidate 199
 *      SOFT-held (window [3.5,7.5], legR peak 3 — same row, same result as
 *      Batch 3's 4,1 step 1); step 2 candidate 184 chord-rejected
 *      (button 9 != step bits 1); step 3 row 186 recorded-path verified.
 *   9. b+2,1+2,4 flagship: partial [unmapped,92,unmapped] — step 1+2 is the
 *      batch's only Job 3 fill (row 92, exact + FULL provenance incl.
 *      moveset_kinpo:d+1+2, timing 1.5, SOFT pass window [3.0,7.0]).
 *  10. Suspended-drift: 1,2,3 / 1,2,4 step 1 — prefix move 1 ROW-CHANGED
 *      35->None; stale row 35 documented, never wired.
 *  11. The verified-last-step Batch 4 keys are exactly the 5 documented
 *      (2,1,2,2,3 / 2,1,4 / 2,1,4,4,2 / 2,1,4,4,2,4 / 4,1,2); the review
 *      last-step key is exactly 2,1,2,2,3,4.
 *  12. Batch 4 CSV-only keys (42 canonicals: 41 rest + 1 throw triple-quad)
 *      have NO plan — asserted for every one, including 3~4,D/F (rest, never
 *      a variant of 3) and CHARGE.d/f+3+4,3+4,1+2 (move_class throw).
 *  13. Coverage-complete: Batch 4's 70 canonicals + Batches 1-3's 65 = 135
 *      canonical comma keys, with zero overlap between batch universes
 *      (proved in the derivation; the plan-key partition here is the
 *      test-level mirror: 47 + 20 + 48 + 62 = 177 keys, no key in two batches).
 *  14. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Run: node --test game/tests/kinpo-batch4-step-plans.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const kinpo = JSON.parse(readFileSync(join(ROOT, 'game/assets/movesets/kinpo.json'), 'utf8'));
const fighterSrc = readFileSync(join(ROOT, 'game/js/fighter.js'), 'utf8');
const hfPath = join(ROOT, 'game/assets/anim/t3/jin/hit_frames.json');
const hf = JSON.parse(readFileSync(hfPath, 'utf8')).rows;

const plans = kinpo.string_step_plans.plans;
const B1 = ["1,1", "1,1~t7.asuka", "1,1~t7.asuka.2", "1,2", "1,2~t7.asuka", "1,2~t7.asuka.2", "2,1", "2,1,1+2", "2,1,1+2~t7.asuka", "2,1,1+2~t7.asuka.2", "2,1,2", "2,1,2,2", "2,1,2~t8.asuka", "2,1,d+1+2", "2,1,d+1+2~t7.asuka", "2,1,d+1+2~t7.asuka.2", "2,1,d+1+2~t7.asuka.3", "2,1~t7.asuka", "2,1~t7.asuka.2", "2,1~t8.asuka", "NANIWA_ULTIMATE_TACKLE.2,1,1,2", "NANIWA_ULTIMATE_TACKLE.2,1,2,1", "Tackle.2,1,2,1", "WS.2,1", "WS.2,1~t7.asuka", "b+2,1", "b+2,1+2", "b+2,1+2~t7.asuka", "b+2,1+2~t7.asuka.2", "b+2,1~t7.asuka", "b+2,1~t7.asuka.2", "d+1+2,1", "d+1+2,1,2", "d+1+2,2", "d/b+1,2", "d/b+1,2~t7.asuka", "d/f+1,2", "d/f+1,2~t7.asuka", "db+1,2", "f+2,NWG.1+2", "uf+1,2", "uf+1,NWG.2", "ws2,1", "ws2,1,1", "ws2,1,1,1", "ws2,1,1,1,2", "ws2,1,1,1,2,1"];
const B2 = ["FC.3+4,3", "FC.3+4,3~t7.asuka", "FC.3+4,3~t7.asuka.2", "FC.3+4,3~t7.asuka.3", "b+3,4", "b+3,4~t7.asuka", "b+3,4~t7.asuka.2", "d/b+4,4", "d/b+4,4,4", "d/b+4,4,4~t7.asuka", "d/b+4,4,4~t7.asuka.2", "d/b+4,4~t7.asuka", "d/f+4,4", "db+4,3", "db+4,4", "db+4,4,4", "u/f+4,3", "u/f+4,4", "u/f+4,4,4", "u/f+4,4,4,4"];
const B3 = ["1,1,3", "1,3", "1,3~t7.asuka", "1,3~t7.asuka.2", "1,4", "1,4~t7.asuka", "2,3", "2,3~t7.asuka", "2,3~t7.asuka.2", "3,1", "3,1~t7.asuka", "3,1~t7.asuka.2", "4,1", "WS.1,4", "WS.1,4~t7.asuka", "b+1+4,4", "b+1+4,4~t7.asuka", "b+1+4,4~t7.asuka.2", "b+1+4,4~t7.asuka.3", "b+2,4", "b+2,4~t7.asuka", "b+2,4~t7.asuka.2", "b+3,2", "b+3,2~t7.asuka", "b+3,2~t7.asuka.2", "b+4,2", "b+4,2~t7.asuka", "b+4,2~t7.asuka.2", "d/f+1,3", "d/f+1,4", "d/f+1,4~t7.asuka", "d/f+1,4~t7.asuka.2", "db+1,4", "db+4,1+4", "df+1,4", "f+1,3", "f+1,3,1", "f+1,3,1~t7.asuka", "f+1,3,1~t7.asuka.2", "f+1,3~t7.asuka", "f+1,3~t7.asuka.2", "f+1,4", "f+1,4~t7.asuka", "f+1,4~t7.asuka.2", "f+1,4~t7.asuka.3", "f+1,d+4", "f+1,d+4~t7.asuka", "ws1,4"];
const B4 = ["1+2+3+4,1+2", "1+4,2", "1+4,2,1", "1+4,2,1~t7.asuka", "1+4,2,1~t7.asuka.2", "1+4,2,1~t7.asuka.3", "1+4,2,4", "1+4,2,4~t7.asuka", "1+4,2,4~t7.asuka.2", "1+4,2,4~t7.asuka.3", "1+4,2,4~t7.asuka.4", "1+4,2,d+4", "1+4,2,d+4~t7.asuka", "1+4,2,d+4~t7.asuka.2", "1+4,2,d+4~t7.asuka.3", "1+4,2,d+4~t7.asuka.4", "1+4,2~t7.asuka", "1+4,2~t7.asuka.2", "1+4,2~t7.asuka.3", "1+4,3", "1+4,3~t7.asuka", "1+4,3~t7.asuka.2", "1+4,3~t7.asuka.3", "1,2,3", "1,2,3*", "1,2,3*~t7.asuka", "1,2,3~t7.asuka", "1,2,3~t7.asuka.2", "1,2,3~t7.asuka.3", "1,2,4", "1,2,4~t7.asuka", "1,2,4~t7.asuka.2", "1,2,4~t7.asuka.3", "2,1,2,2,3", "2,1,2,2,3,4", "2,1,4", "2,1,4,4", "2,1,4,4,2", "2,1,4,4,2,4", "4,1,2", "WS.2,1,1,1,2,1+4,1,3+4", "WS.2,1,1,1,2,1,4,3,3+4", "WS.2,1,1,3", "b+1+4,3", "b+1+4,3~t7.asuka", "b+1+4,3~t7.asuka.2", "b+1+4,3~t7.asuka.3", "b+2,1+2,4", "b+2,1+2,4~t7.asuka", "b+2,1+2,4~t7.asuka.2", "b+2,1+2,4~t7.asuka.3", "b+4,2,3", "b+4,2,3~t7.asuka", "b+4,2,3~t7.asuka.2", "b+4,2,3~t7.asuka.3", "ws2,1,1,1,2,1+4", "ws2,1,1,1,2,1+4,1", "ws2,1,1,1,2,1+4,1,3+4", "ws2,1,1,1,2,1,4", "ws2,1,1,1,2,1,4,3", "ws2,1,1,1,2,1,4,3,3+4", "ws2,1,1,3"];
const B4_VERIFIED_LAST = ["2,1,2,2,3", "2,1,4", "2,1,4,4,2", "2,1,4,4,2,4", "4,1,2"];
const B4_CSV_ONLY = ["(Back to wall).b,b,UB", "1+4,3,B", "1,2,3*,B", "1,4,D", "3+4,D", "3~4,D/F", "CHARGE.d/f+3+4,3+4,1+2", "FC.3+4,3,D", "FC.3+4,D", "FC.d/f,d,d/f+1+2", "NWG.f,F+1+2", "NWG.f,f,F+1+2", "R.f,F+1+2", "WALL.b,b,u/b", "WS.1+2,D", "b+2,1+2,D", "b+2,4,D", "b+3,2,D/F", "d,d/b,d,d/b+1+2", "d/b+4,4,4,D", "d/b+4,4,D", "d/b+4,D", "f+1,d+4,D/B", "f+2,D", "f+3*,B", "f,F+1", "f,F+1+2", "f,F+2", "f,F+2,1", "f,F+2,1+2", "f,F+2,3", "f,F+3", "f,F+4", "f,f,F", "f,f,F+1+2", "f,f,F+3", "f,f,f+3", "n,b,n,f+2", "n,d/f,n,d/f+1", "n,f,n,f+1+2", "u/b,b", "ub,b"];
const VERIFIED_BUTTONS = {"92": 3, "186": 2, "220": 2, "221": 1, "222": 2, "223": 2, "224": 4, "230": 8, "232": 2, "233": 8};

function stepBits(step) {
  const seg = step.split('.').pop();
  let b = 0;
  for (const c of seg) if ('1234'.includes(c)) b |= 1 << (Number(c) - 1);
  return b;
}

test('kinpo move/string counts unchanged by the additive plans block', () => {
  assert.equal(Object.keys(kinpo.moves).length, 525);
  assert.equal(kinpo.strings.length, 101);
  assert.equal(Object.keys(plans).length, 177); // 115 Batches 1-3 + 62 Batch 4 (cumulative)
});

test('Batch 4 keys are exactly the documented 62; all Batches 1-3 keys present', () => {
  assert.equal(B4.length, 62);
  for (const key of B4) assert.ok(plans[key], `Batch 4 key ${key} missing`);
  for (const key of B1) assert.ok(plans[key], `Batch 1 key ${key} missing`);
  for (const key of B2) assert.ok(plans[key], `Batch 2 key ${key} missing`);
  for (const key of B3) assert.ok(plans[key], `Batch 3 key ${key} missing`);
  const extra = Object.keys(plans).filter((k) => !B1.includes(k) && !B2.includes(k) && !B3.includes(k) && !B4.includes(k));
  assert.deepEqual(extra, []);
});

test('Batch 4 verified steps carry rows (button == step bits, throw 0, never row 35 on ground); review/unmapped carry row null; no soft flags', () => {
  for (const key of B4) {
    for (const s of plans[key].steps) {
      assert.ok(!('soft' in s) || s.soft !== true, `${key} step ${s.step} carries a soft flag`);
      if (s.status === 'verified') {
        assert.notEqual(s.row, null, `${key} step ${s.step} verified but row null`);
        if (!plans[key].jumping_context) assert.notEqual(s.row, 35, `${key} step ${s.step} verified on row 35 for a ground step (row 35 is starts-airborne in the jin bank)`);
        assert.equal(hf[String(s.row)][5], stepBits(s.step), `${key} step ${s.step} row ${s.row} button mismatch`);
        assert.equal(hf[String(s.row)][5], VERIFIED_BUTTONS[String(s.row)], `${key} step ${s.step} row ${s.row} button mismatch (map)`);
        assert.equal(hf[String(s.row)][4], 0, `${key} step ${s.step} row ${s.row} is a throw row`);
      } else {
        assert.equal(s.row, null, `${key} step ${s.step} ${s.status} must not carry a playable row`);
      }
    }
  }
});

test('2,1,2,2,3 flagship: verified-all [220,221,222,223,224]', () => {
  const p = plans['2,1,2,2,3'];
  assert.equal(p.steps.length, 5);
  assert.deepEqual(p.steps.map((s) => s.row), [220, 221, 222, 223, 224]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified', 'verified', 'verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('2,1,4 flagship: verified-all [220,221,230]', () => {
  const p = plans['2,1,4'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [220, 221, 230]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('2,1,4,4,2,4 flagship: partial [220,221,230,None,232,233] — step 4 candidate 231 chord-rejected', () => {
  const p = plans['2,1,4,4,2,4'];
  assert.equal(p.steps.length, 6);
  assert.deepEqual(p.steps.map((s) => s.row), [220, 221, 230, null, 232, 233]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified', 'verified', 'unmapped', 'verified', 'verified']);
  assert.equal(p.string_status, 'partial');
  assert.ok(p.steps[3].reasons.join(' ').includes('button 12 != step bits 8'), 'step 4 must record the button-12 chord-row rejection on row 231');
});

test('2,1,2,2,3,4 flagship: partial [220,221,222,223,224,review] — last step candidate 225 SOFT-held', () => {
  const p = plans['2,1,2,2,3,4'];
  assert.equal(p.steps.length, 6);
  assert.deepEqual(p.steps.map((s) => s.row), [220, 221, 222, 223, 224, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified', 'verified', 'verified', 'verified', 'review']);
  assert.equal(p.string_status, 'partial');
  assert.ok(p.steps[5].reasons.join(' ').includes('SOFT limb-peak proxy fail'), 'last step must record the SOFT proxy fail on row 225');
});

test('4,1,2 flagship: partial [review,unmapped,186] — step 1 candidate 199 SOFT-held, step 2 candidate 184 chord-rejected, step 3 row 186 verified', () => {
  const p = plans['4,1,2'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null, 186]);
  assert.deepEqual(p.steps.map((s) => s.status), ['review', 'unmapped', 'verified']);
  assert.equal(p.string_status, 'partial');
  assert.ok(p.steps[0].reasons.join(' ').includes('SOFT limb-peak proxy fail'), 'step 1 must record the SOFT proxy fail on row 199');
  assert.ok(p.steps[1].reasons.join(' ').includes('button 9 != step bits 1'), 'step 2 must record the button-9 chord-row rejection on row 184');
});

test('b+2,1+2,4 flagship: partial [unmapped,92,unmapped] — step 1+2 is the batch\'s only Job 3 fill (row 92, exact + FULL)', () => {
  const p = plans['b+2,1+2,4'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [null, 92, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'verified', 'unmapped']);
  assert.equal(p.string_status, 'partial');
  assert.ok(p.steps[1].reasons.join(' ').includes('Job 3 fill row 92'), 'step 1+2 must record the Job 3 fill on row 92');
  assert.ok(p.steps[1].reasons.join(' ').includes('moveset_kinpo:d+1+2'), 'Job 3 fill provenance must include moveset_kinpo:d+1+2');
});

test('suspended-drift: 1,2,3 / 1,2,4 step 1 — prefix move 1 ROW-CHANGED 35->None, stale row 35 never wired', () => {
  for (const key of ['1,2,3', '1,2,4']) {
    const p = plans[key];
    assert.equal(p.steps[0].status, 'unmapped');
    assert.equal(p.steps[0].row, null);
    assert.ok(p.steps[0].reasons.join(' ').includes('SUSPENDED-DRIFT'), `${key} step 1 must record SUSPENDED-DRIFT`);
    assert.equal(p.steps[0].candidate_row, 35, `${key} step 1 stale candidate must be row 35`);
  }
});

test('verified-last-step Batch 4 keys are exactly the 5 documented; review last-step key exactly 2,1,2,2,3,4', () => {
  assert.equal(B4_VERIFIED_LAST.length, 5);
  for (const key of B4_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step must be verified`);
  for (const key of B4) {
    if (!B4_VERIFIED_LAST.includes(key)) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
  }
  assert.equal(plans['2,1,2,2,3,4'].last_step_status, 'review');
});

test('Batch 4 CSV-only keys (42 canonicals: 41 rest + 1 throw triple-quad) have NO plan', () => {
  assert.equal(B4_CSV_ONLY.length, 42);
  for (const k of B4_CSV_ONLY) assert.ok(!plans[k], `${k} must have no plan`);
  assert.ok(!plans['3~4,D/F'], '3~4,D/F must have no plan (rest key, never a variant of 3)');
  assert.ok(!plans['CHARGE.d/f+3+4,3+4,1+2'], 'CHARGE.d/f+3+4,3+4,1+2 must have no plan (move_class throw)');
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

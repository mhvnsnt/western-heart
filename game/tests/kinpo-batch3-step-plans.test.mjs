/* Kinpo Batch 3 step plans (mixed-pair strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/KINPO-BATCH3-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on kinpo Batch 2 (feat/kinpo-batch2-step-plans-20261025,
 * PR #1118), which stacks on kinpo Batch 1 (PR #1117), which stacks on #1096
 * (feat/batch1-step-plans-pantera-20261024, the step-playback engine). It does NOT stack
 * on the Pantera plan branches (#1099/#1101/#1102), the burger plan branches
 * (#1103/#1104/#1105/#1107), the demonio plan branches (#1108/#1110/#1111/#1112), or the
 * diablo plan branches (#1113/#1114/#1115/#1116): kinpo.json plans do not conflict with
 * pantera.json, burger.json, demonio.json, or diablo.json plans.
 * It does NOT include #1097's Pantera Batch 1 follow-up fills (Pantera-specific,
 * and its row-49 SOFT fill is still unapproved); no SOFT fill is inherited here.
 * This PR does not touch `fighter.js`: #1096's merge onto post-#1078 main must
 * reconcile #1078's `fighter.js` changes with #1096's engine branch, and that
 * belongs to #1096's merge, not this PR.
 * Bank (verified, not assumed): kinpo's T3 bank is JIN (t3_source jin, t3_bank
 * moveset_jin.json, on BOTH the Batch 2 branch and main; t3/ directory listing;
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
 * 35->None (Batch 2 branch vs current main) — Batch 3's three suspended-drift
 * steps are exactly the step-1s whose prefix is move 1. Row 220 is a STANDING RP2
 * row here (hit_frames [12,12,41,1042,0,2], Job 1 standing) — gate-adjudicated
 * like any row, NOT king's jumping chord row, NOT bryan's button-0 row, NOT
 * heihachi's jump RK4 row. Jin row 216 is a JUMP row, NOT king row 216's dash
 * Konvict Kick.
 * Canonicalization is the CORRECTED rule (demonio Batch 2 finding): strip ONLY
 * a trailing ~t[378].[a-z]+(.N)?$ source-variant suffix; input-~ is Tekken
 * cancel notation, part of the move. Kinpo Batch 3 contains ZERO input-~
 * canonicals. The file's only old-vs-corrected diff, 3~4,D/F, is NOT Batch 3
 * scope (steps 3~4 + D/F; D/F buttonless -> rest/Batch 4 scope). Spelling
 * quirks kept: d/f+1,4 vs df+1,4 are distinct canonicals, never merged
 * (different step-1 evidence: jump row 179 rejected vs no candidate).
 * Rules asserted here (all data-level, no THREE needed):
 *   1. kinpo.json still has 525 moves / 101 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 115 keys (67 Batches 1-2 + 48 Batch 3); the
 *      Batch 3 keys are exactly the documented 48; all Batch 1 + Batch 2 keys present.
 *   3. Batch 3 verified steps always carry a row whose jin hit_frames
 *      button equals the step bits and whose throw flag is 0; no verified
 *      ground-context step uses row 35 (starts-airborne per jin Job 1);
 *      review/unmapped steps carry row null. No Batch 3 step carries a soft
 *      flag (Batch 3 wires zero Job 3 fills and zero SOFT fills).
 *   4. 2,3 flagship: partial [220, unmapped] — step 1 standing RP2 row 220
 *      (prefix-move own row, Job 2 CLEAN).
 *   5. 3,1 flagship: partial [195, unmapped] — step 1 standing LK3 row 195
 *      (prefix-move own row, Job 2 CLEAN).
 *   6. 4,1 flagship: partial [review, unmapped] — step 1 candidate 199
 *      (recorded-path, Job 2 CLEAN own row for move 4) held at review (SOFT
 *      limb-peak proxy fail, window [3.5,7.5], legR peak 3); step 2 candidate
 *      184 rejected (button 9 != step bits 1 — chord row for a single LP1 step).
 *   7. Suspended-drift: 1,3 / 1,4 / 1,1,3 step 1 — prefix move 1 ROW-CHANGED
 *      35->None; stale row 35 documented, never wired.
 *   8. Rejected-candidate: d/f+1,3 + d/f+1,4 step 1 row 179 airborne jump row
 *      (also Batch 1's only Job 4 join, rejected for the same reason);
 *      d/f+1,3 step 2 row 197, d/f+1,4 step 2 + df+1,4 step 2 row 204, all
 *      airborne jump rows.
 *   9. The verified-last-step Batch 3 keys are exactly NONE — Batch 3 wires
 *      first steps only; all 48 last steps are unmapped.
 *  10. Batch 3 has NO CSV-only keys: all 21 canonicals are strike class.
 *  11. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Run: node --test game/tests/kinpo-batch3-step-plans.test.mjs   (from repo root)
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
const B3_VERIFIED_LAST = [];
const VERIFIED_BUTTONS = {"195": 4, "220": 2};

function stepBits(step) {
  const seg = step.split('.').pop();
  let b = 0;
  for (const c of seg) if ('1234'.includes(c)) b |= 1 << (Number(c) - 1);
  return b;
}

test('kinpo move/string counts unchanged by the additive plans block', () => {
  assert.equal(Object.keys(kinpo.moves).length, 525);
  assert.equal(kinpo.strings.length, 101);
  assert.equal(Object.keys(plans).length, 115); // 67 Batches 1-2 + 48 Batch 3 (cumulative)
});

test('Batch 3 keys are exactly the documented 48; all Batch 1 + Batch 2 keys present', () => {
  assert.equal(B3.length, 48);
  for (const key of B3) assert.ok(plans[key], `Batch 3 key ${key} missing`);
  for (const key of B1) assert.ok(plans[key], `Batch 1 key ${key} missing`);
  for (const key of B2) assert.ok(plans[key], `Batch 2 key ${key} missing`);
  const extra = Object.keys(plans).filter((k) => !B1.includes(k) && !B2.includes(k) && !B3.includes(k));
  assert.deepEqual(extra, []);
});

test('Batch 3 verified steps carry rows (button == step bits, throw 0, never row 35 on ground); review/unmapped carry row null; no soft flags', () => {
  for (const key of B3) {
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

test('2,3 flagship: partial [220, unmapped] — step 1 standing RP2 row 220 (prefix-move own, Job 2 CLEAN)', () => {
  const p = plans['2,3'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [220, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'unmapped']);
  assert.equal(p.string_status, 'partial');
});

test('3,1 flagship: partial [195, unmapped] — step 1 standing LK3 row 195 (prefix-move own, Job 2 CLEAN)', () => {
  const p = plans['3,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [195, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'unmapped']);
  assert.equal(p.string_status, 'partial');
});

test('4,1 flagship: partial [review, unmapped] — step 1 candidate 199 SOFT-held, step 2 candidate 184 chord-rejected', () => {
  const p = plans['4,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['review', 'unmapped']);
  assert.equal(p.string_status, 'partial');
  assert.ok(p.steps[0].reasons.join(' ').includes('SOFT limb-peak proxy fail'), 'step 1 must record the SOFT proxy fail on row 199');
  assert.ok(p.steps[1].reasons.join(' ').includes('button 9 != step bits 1'), 'step 2 must record the button-9 chord-row rejection on row 184');
});

test('suspended-drift: 1,3 / 1,4 / 1,1,3 step 1 — prefix move 1 ROW-CHANGED 35->None, stale row 35 never wired', () => {
  for (const key of ['1,3', '1,4', '1,1,3']) {
    const p = plans[key];
    assert.equal(p.steps[0].status, 'unmapped');
    assert.equal(p.steps[0].row, null);
    assert.ok(p.steps[0].reasons.join(' ').includes('SUSPENDED-DRIFT'), `${key} step 1 must record SUSPENDED-DRIFT`);
    assert.equal(p.steps[0].candidate_row, 35, `${key} step 1 stale candidate must be row 35`);
  }
});

test('rejected-candidate: d/f+1,3 + d/f+1,4 step 1 row 179 airborne; step-2 rows 197/204 airborne', () => {
  assert.equal(plans['d/f+1,3'].steps[0].candidate_row, 179);
  assert.ok(plans['d/f+1,3'].steps[0].reasons.join(' ').includes('airborne row'));
  assert.equal(plans['d/f+1,4'].steps[0].candidate_row, 179);
  assert.ok(plans['d/f+1,4'].steps[0].reasons.join(' ').includes('airborne row'));
  assert.equal(plans['d/f+1,3'].steps[1].candidate_row, 197);
  assert.ok(plans['d/f+1,3'].steps[1].reasons.join(' ').includes('airborne row'));
  assert.equal(plans['d/f+1,4'].steps[1].candidate_row, 204);
  assert.ok(plans['d/f+1,4'].steps[1].reasons.join(' ').includes('airborne row'));
  assert.equal(plans['df+1,4'].steps[1].candidate_row, 204);
  assert.ok(plans['df+1,4'].steps[1].reasons.join(' ').includes('airborne row'));
});

test('verified-last-step Batch 3 keys are exactly NONE — Batch 3 wires first steps only', () => {
  assert.equal(B3_VERIFIED_LAST.length, 0);
  for (const key of B3) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('Batch 3 has no CSV-only keys: all 21 canonicals are strike class with plans', () => {
  for (const k of ["1,1,3", "1,3", "1,4", "2,3", "3,1", "4,1", "WS.1,4", "b+1+4,4", "b+2,4", "b+3,2", "b+4,2", "d/f+1,3", "d/f+1,4", "db+1,4", "db+4,1+4", "df+1,4", "f+1,3", "f+1,3,1", "f+1,4", "f+1,d+4", "ws1,4"]) assert.ok(plans[k], `${k} must have a plan`);
  assert.ok(!plans['3~4,D/F'], '3~4,D/F must have no plan (rest/Batch 4 scope, not Batch 3)');
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

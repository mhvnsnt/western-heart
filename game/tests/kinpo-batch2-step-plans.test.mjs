/* Kinpo Batch 2 step plans (LK3/RK4-only strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/KINPO-BATCH2-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on kinpo Batch 1 (feat/kinpo-batch1-step-plans-20261025,
 * PR #1117), which stacks on #1096 (feat/batch1-step-plans-pantera-20261024,
 * the step-playback engine). It does NOT stack on the Pantera plan branches
 * (#1099/#1101/#1102), the burger plan branches (#1103/#1104/#1105/#1107), the
 * demonio plan branches (#1108/#1110/#1111/#1112), or the diablo plan branches
 * (#1113/#1114/#1115/#1116): kinpo.json plans do not conflict with pantera.json,
 * burger.json, demonio.json, or diablo.json plans.
 * It does NOT include #1097's Pantera Batch 1 follow-up fills (Pantera-specific,
 * and its row-49 SOFT fill is still unapproved); no SOFT fill is inherited here.
 * This PR does not touch `fighter.js`: #1096's merge onto post-#1078 main must
 * reconcile #1078's `fighter.js` changes with #1096's engine branch, and that
 * belongs to #1096's merge, not this PR.
 * Bank (verified, not assumed): kinpo's T3 bank is JIN (t3_source jin, t3_bank
 * moveset_jin.json, on BOTH the Batch 1 branch and main; t3/ directory listing;
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
 * 35->None (Batch 1 branch vs current main), but it is NOT a Batch 2 step
 * prefix, so Batch 2 has ZERO suspended-drift steps. Row 220 is a STANDING RP2
 * row here (hit_frames [12,12,41,1042,0,2], Job 1 standing) — gate-adjudicated
 * like any row, NOT king's jumping chord row, NOT bryan's button-0 row, NOT
 * heihachi's jump RK4 row. Jin row 216 is a JUMP row, NOT king row 216's dash
 * Konvict Kick.
 * Canonicalization is the CORRECTED rule (demonio Batch 2 finding): strip ONLY
 * a trailing ~t[378].[a-z]+(.N)?$ source-variant suffix; input-~ is Tekken
 * cancel notation, part of the move. Kinpo Batch 2 contains ZERO input-~
 * canonicals. The file's only old-vs-corrected diff, 3~4,D/F, is NOT Batch 2
 * scope (steps 3~4 + D/F; D/F buttonless -> rest/Batch 4 scope). Spelling
 * quirks kept: d/b+4,4 vs db+4,4 and d/b+4,4,4 vs db+4,4,4 are distinct
 * canonicals, never merged.
 * CUMULATIVE UPDATE (Kinpo Batch 3, 2026-10-25): ONLY counts / extra-keys /
 * header notes changed for the cumulative block (total 115 = 67 Batches 1-2
 * + 48 Batch 3; extra keys exactly the Batch 3 keys). Every Batch 2 CONTENT
 * assertion below is preserved verbatim. The Batch 3 keys are asserted in
 * kinpo-batch3-step-plans.test.mjs.
 * Rules asserted here (all data-level, no THREE needed):
 *   1. kinpo.json still has 525 moves / 101 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 67 keys (47 Batch 1 + 20 Batch 2); the
 *      Batch 2 keys are exactly the documented 20; all 47 Batch 1 keys present.
 *   3. Batch 2 verified steps always carry a row whose jin hit_frames
 *      button equals the step bits and whose throw flag is 0; no verified
 *      ground-context step uses row 35 (starts-airborne per jin Job 1);
 *      review/unmapped steps carry row null. No Batch 2 step carries a soft
 *      flag (Batch 2 wires zero Job 3 fills and zero SOFT fills).
 *   4. u/f+4,3 flagship: verified-all on rows 80/193 (jump context, SOFT waived).
 *   5. u/f+4,4 flagship: verified-all on rows 80/207 (jump context, SOFT waived).
 *   6. d/f+4,4 flagship: partial [205, review] — step 1 crouch row 205 passes
 *      for crouch outright (NOT a gate-note case: row 205 Job 1 stance is
 *      crouch); step 2 candidate 212 held at review (SOFT limb-peak proxy
 *      fail, same row/result as demonio Batch 2's d/f+4,4 step 2).
 *   7. u/f+4,4,4 flagship: partial [80,207,review] — step 3 candidate 210
 *      (duck-dip row) STANCE-SOFT for a jump-context step, held at review.
 *   8. u/f+4,4,4,4 flagship: partial [80,207,review,review] — steps 3/4
 *      candidates 210/211 (duck-dip rows) STANCE-SOFT for jump-context steps.
 *   9. The verified-last-step Batch 2 keys are exactly the 2 listed below.
 *  10. Batch 2 has NO CSV-only keys: all 12 canonicals are strike class.
 *  11. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Run: node --test game/tests/kinpo-batch2-step-plans.test.mjs   (from repo root)
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
const B2_VERIFIED_LAST = ["u/f+4,3", "u/f+4,4"];
const VERIFIED_BUTTONS = {"80": 8, "193": 4, "205": 8, "207": 8};

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

test('Batch 2 keys are exactly the documented 20; all Batch 1 keys present; extra keys exactly the documented Batch 3 + Batch 4 keys (cumulative)', () => {
  assert.equal(B2.length, 20);
  for (const key of B2) assert.ok(plans[key], `Batch 2 key ${key} missing`);
  for (const key of B1) assert.ok(plans[key], `Batch 1 key ${key} missing`);
  const B3 = ["1,1,3", "1,3", "1,3~t7.asuka", "1,3~t7.asuka.2", "1,4", "1,4~t7.asuka", "2,3", "2,3~t7.asuka", "2,3~t7.asuka.2", "3,1", "3,1~t7.asuka", "3,1~t7.asuka.2", "4,1", "WS.1,4", "WS.1,4~t7.asuka", "b+1+4,4", "b+1+4,4~t7.asuka", "b+1+4,4~t7.asuka.2", "b+1+4,4~t7.asuka.3", "b+2,4", "b+2,4~t7.asuka", "b+2,4~t7.asuka.2", "b+3,2", "b+3,2~t7.asuka", "b+3,2~t7.asuka.2", "b+4,2", "b+4,2~t7.asuka", "b+4,2~t7.asuka.2", "d/f+1,3", "d/f+1,4", "d/f+1,4~t7.asuka", "d/f+1,4~t7.asuka.2", "db+1,4", "db+4,1+4", "df+1,4", "f+1,3", "f+1,3,1", "f+1,3,1~t7.asuka", "f+1,3,1~t7.asuka.2", "f+1,3~t7.asuka", "f+1,3~t7.asuka.2", "f+1,4", "f+1,4~t7.asuka", "f+1,4~t7.asuka.2", "f+1,4~t7.asuka.3", "f+1,d+4", "f+1,d+4~t7.asuka", "ws1,4"];
const B4 = ["1+2+3+4,1+2", "1+4,2", "1+4,2,1", "1+4,2,1~t7.asuka", "1+4,2,1~t7.asuka.2", "1+4,2,1~t7.asuka.3", "1+4,2,4", "1+4,2,4~t7.asuka", "1+4,2,4~t7.asuka.2", "1+4,2,4~t7.asuka.3", "1+4,2,4~t7.asuka.4", "1+4,2,d+4", "1+4,2,d+4~t7.asuka", "1+4,2,d+4~t7.asuka.2", "1+4,2,d+4~t7.asuka.3", "1+4,2,d+4~t7.asuka.4", "1+4,2~t7.asuka", "1+4,2~t7.asuka.2", "1+4,2~t7.asuka.3", "1+4,3", "1+4,3~t7.asuka", "1+4,3~t7.asuka.2", "1+4,3~t7.asuka.3", "1,2,3", "1,2,3*", "1,2,3*~t7.asuka", "1,2,3~t7.asuka", "1,2,3~t7.asuka.2", "1,2,3~t7.asuka.3", "1,2,4", "1,2,4~t7.asuka", "1,2,4~t7.asuka.2", "1,2,4~t7.asuka.3", "2,1,2,2,3", "2,1,2,2,3,4", "2,1,4", "2,1,4,4", "2,1,4,4,2", "2,1,4,4,2,4", "4,1,2", "WS.2,1,1,1,2,1+4,1,3+4", "WS.2,1,1,1,2,1,4,3,3+4", "WS.2,1,1,3", "b+1+4,3", "b+1+4,3~t7.asuka", "b+1+4,3~t7.asuka.2", "b+1+4,3~t7.asuka.3", "b+2,1+2,4", "b+2,1+2,4~t7.asuka", "b+2,1+2,4~t7.asuka.2", "b+2,1+2,4~t7.asuka.3", "b+4,2,3", "b+4,2,3~t7.asuka", "b+4,2,3~t7.asuka.2", "b+4,2,3~t7.asuka.3", "ws2,1,1,1,2,1+4", "ws2,1,1,1,2,1+4,1", "ws2,1,1,1,2,1+4,1,3+4", "ws2,1,1,1,2,1,4", "ws2,1,1,1,2,1,4,3", "ws2,1,1,1,2,1,4,3,3+4", "ws2,1,1,3"];
  const extra = Object.keys(plans).filter((k) => !B1.includes(k) && !B2.includes(k));
  assert.deepEqual(extra.sort(), B3.concat(B4).sort());
});

test('Batch 2 verified steps carry rows (button == step bits, throw 0, never row 35 on ground); review/unmapped carry row null; no soft flags', () => {
  for (const key of B2) {
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

test('u/f+4,3 flagship: verified-all on rows 80/193 (jump context, SOFT waived)', () => {
  const p = plans['u/f+4,3'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [80, 193]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('u/f+4,4 flagship: verified-all on rows 80/207 (jump context, SOFT waived)', () => {
  const p = plans['u/f+4,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [80, 207]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('d/f+4,4 flagship: partial [205, review] — step 1 crouch row 205 outright, step 2 candidate 212 SOFT-held', () => {
  const p = plans['d/f+4,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [205, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'review']);
  assert.equal(p.string_status, 'partial');
  assert.ok(p.steps[1].reasons.join(' ').includes('SOFT limb-peak proxy fail'), 'step 2 must record the SOFT proxy fail on row 212');
  assert.ok(!p.steps[0].reasons.join(' ').includes('GATE-NOTE'), 'step 1 crouch row 205 is NOT a gate-note case (row 205 stance is crouch)');
});

test('u/f+4,4,4 flagship: partial [80,207,review] — step 3 candidate 210 STANCE-SOFT duck-dip', () => {
  const p = plans['u/f+4,4,4'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [80, 207, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified', 'review']);
  assert.equal(p.string_status, 'partial');
});

test('u/f+4,4,4,4 flagship: partial [80,207,review,review] — steps 3/4 candidates 210/211 STANCE-SOFT duck-dip', () => {
  const p = plans['u/f+4,4,4,4'];
  assert.equal(p.steps.length, 4);
  assert.deepEqual(p.steps.map((s) => s.row), [80, 207, null, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified', 'review', 'review']);
  assert.equal(p.string_status, 'partial');
});

test('verified-last-step Batch 2 keys are exactly the documented 2', () => {
  assert.equal(B2_VERIFIED_LAST.length, 2);
  for (const key of B2_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B2.filter((k) => !B2_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('Batch 2 has no CSV-only keys: all 12 canonicals are strike class with plans', () => {
  for (const k of ["FC.3+4,3", "b+3,4", "d/b+4,4", "d/b+4,4,4", "d/f+4,4", "db+4,3", "db+4,4", "db+4,4,4", "u/f+4,3", "u/f+4,4", "u/f+4,4,4", "u/f+4,4,4,4"]) assert.ok(plans[k], `${k} must have a plan`);
  assert.ok(!plans['3~4,D/F'], '3~4,D/F must have no plan (rest/Batch 4 scope, not Batch 2)');
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

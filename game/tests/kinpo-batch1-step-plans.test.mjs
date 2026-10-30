/* Kinpo Batch 1 step plans (LP1/RP2-only strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/KINPO-BATCH1-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on #1096 (feat/batch1-step-plans-pantera-20261024,
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
 * moveset_jin.json, on BOTH #1096 and main; t3/ directory listing; Job 1 bank
 * jin (220 rows); Job 2 kinpo entries all bank jin (525); Job 4 jin candidates
 * (47)). Bank resolution, documented not assumed: kinpo's T7/T8 base IS Asuka
 * (tekken_base Asuka, merge_sources t8/t7 asuka), but Asuka debuted in Tekken 5
 * and has NO T3 bank in this repo (no asuka dir under t3/), so the file's T3
 * fallback bank is jin — the burger pattern (Bob -> bryan). The T7-Asuka
 * re-match is future work; this batch adjudicates against jin as the file
 * declares.
 * Jin-bank rules, per-bank evidence (never a cross-bank blanket ban): row 35
 * EXISTS here (hit_frames [11,12,39,535,0,1], Job 1 stance starts-airborne) —
 * NOT blanket-banned by number, but the stance gate rejects it for ground
 * steps; kinpo's own LP1 move 1 carries t3_row 35 (same class as Pantera
 * LP1->king row 38, jumping) and is ALSO ROW-CHANGED 35->None (#1096 vs
 * current main), so the 2 1-family step 1s are SUSPENDED-DRIFT. Row 220 is a
 * STANDING RP2 row here (hit_frames [12,12,41,1042,0,2], Job 1 standing) —
 * gate-adjudicated like any row, NOT king's jumping chord row, NOT bryan's
 * button-0 row, NOT heihachi's jump RK4 row. Jin row 216 is a JUMP row, NOT
 * king row 216's dash Konvict Kick.
 * Canonicalization is the CORRECTED rule (demonio Batch 2 finding): strip ONLY
 * a trailing ~t[378].[a-z]+(.N)?$ source-variant suffix; input-~ is Tekken
 * cancel notation, part of the move. Kinpo Batch 1 contains ZERO input-~
 * canonicals — the file's only old-vs-corrected diff is 3~4,D/F, outside
 * Batch 1 scope (LK3 cancel + buttonless direction step). Spelling quirks
 * kept: df+1,2 (throw, CSV-only) vs d/f+1,2 (planned), db+1,2 vs d/b+1,2,
 * WS.2,1 vs ws2,1 (both ws context) are distinct canonicals, never merged.
 * CUMULATIVE UPDATE (Kinpo Batch 2, 2026-10-25): this file is the Batch 1 test
 * with ONLY counts / extra-keys / header notes changed for the cumulative
 * block (total 67 = 47 Batch 1 + 20 Batch 2; extra keys exactly the Batch 2
 * keys). Every Batch 1 CONTENT assertion below is preserved verbatim — the
 * Batch 1 flagships, verified-row checks, CSV-only absences, and
 * verified-last-step set are asserted over the Batch 1 keys only and are
 * unchanged. The Batch 2 keys are asserted in kinpo-batch2-step-plans.test.mjs.
 * Rules asserted here (all data-level, no THREE needed):
 *   1. kinpo.json still has 525 moves / 101 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 47 keys (27 planned canonicals + 20 twins).
 *   3. Batch 1 verified steps always carry a row whose jin hit_frames
 *      button equals the step bits and whose throw flag is 0; no verified
 *      ground-context step uses row 35 (starts-airborne per jin Job 1);
 *      review/unmapped steps carry row null. No Batch 1 step carries a soft
 *      flag (Batch 1 wires one Job 3 fill — exact+FULL, HARD + SOFT proxy
 *      pass — and zero SOFT fills).
 *   4. 2,1 flagship: verified-all on rows 220/221 (recorded-path).
 *   5. 2,1,2,2 flagship: verified-all on rows 220/221/222/223.
 *   6. d+1+2,2 flagship: verified-all on rows 92/93 (crouch context, GATE-NOTE:
 *      standing rows for crouch steps, demonio Batch 1 precedent).
 *   7. b+2,1+2 flagship: partial, last step verified row 92 (Job 3 fill,
 *      exact+FULL provenance incl. moveset_kinpo:d+1+2).
 *   8. d+1+2,1,2 flagship: partial, last step verified row 183 (recorded-dest).
 *   9. 1,1 flagship: step 1 SUSPENDED-DRIFT (prefix move 1 ROW-CHANGED 35->None),
 *      row null, never wired on stale data.
 *  10. TACKLE family (3 keys) + throw-class df+1,2 + throw-class ws2,1+2 have
 *      NO plan key. Near-miss labels NANIWA_ULTIMATE_TACKLE / Tackle stay
 *      planned but unmapped-all (narrow rule), wiring no row.
 *  11. The verified-last-step Batch 1 keys are exactly the 12 listed below,
 *      and verified rows carry the step buttons in the repo jin
 *      hit_frames.json.
 *  12. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Run: node --test game/tests/kinpo-batch1-step-plans.test.mjs   (from repo root)
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
const B1_VERIFIED_LAST = ["2,1", "2,1,2", "2,1,2,2", "2,1,2~t8.asuka", "2,1~t7.asuka", "2,1~t7.asuka.2", "2,1~t8.asuka", "b+2,1+2", "b+2,1+2~t7.asuka", "b+2,1+2~t7.asuka.2", "d+1+2,1,2", "d+1+2,2"];
const VERIFIED_BUTTONS = {"92": 3, "93": 2, "183": 2, "220": 2, "221": 1, "222": 2, "223": 2};

function stepBits(step) {
  const seg = step.split('.').pop();
  let b = 0;
  for (const c of seg) if ('1234'.includes(c)) b |= 1 << (Number(c) - 1);
  return b;
}

test('kinpo move/string counts unchanged by the additive plans block', () => {
  assert.equal(Object.keys(kinpo.moves).length, 525);
  assert.equal(kinpo.strings.length, 101);
  assert.equal(Object.keys(plans).length, 67); // 47 Batch 1 + 20 Batch 2 (cumulative)
});

test('Batch 1 keys present; extra keys are exactly the documented Batch 2 keys (cumulative)', () => {
  assert.equal(B1.length, 47);
  for (const key of B1) assert.ok(plans[key], `Batch 1 key ${key} missing`);
  const extra = Object.keys(plans).filter((k) => !B1.includes(k));
  const B2 = ["FC.3+4,3", "FC.3+4,3~t7.asuka", "FC.3+4,3~t7.asuka.2", "FC.3+4,3~t7.asuka.3", "b+3,4", "b+3,4~t7.asuka", "b+3,4~t7.asuka.2", "d/b+4,4", "d/b+4,4,4", "d/b+4,4,4~t7.asuka", "d/b+4,4,4~t7.asuka.2", "d/b+4,4~t7.asuka", "d/f+4,4", "db+4,3", "db+4,4", "db+4,4,4", "u/f+4,3", "u/f+4,4", "u/f+4,4,4", "u/f+4,4,4,4"];
  assert.deepEqual(extra.sort(), B2.sort());
});

test('Batch 1 verified steps carry rows (button == step bits, throw 0, never row 35 on ground); review/unmapped carry row null; no soft flags', () => {
  for (const key of B1) {
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

test('d+1+2,2 flagship: verified-all on rows 92/93 (crouch context, GATE-NOTE)', () => {
  const p = plans['d+1+2,2'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [92, 93]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
  assert.ok(p.steps[0].reasons.join(' ').includes('GATE-NOTE'), 'crouch step on standing row must carry the GATE-NOTE');
});

test('b+2,1+2 flagship: partial, last step verified row 92 (Job 3 fill)', () => {
  const p = plans['b+2,1+2'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, 92]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'verified']);
  assert.equal(p.string_status, 'partial');
  assert.ok(p.steps[1].reasons.join(' ').includes('Job 3 fill row 92'), 'last step must record the Job 3 fill');
});

test('d+1+2,1,2 flagship: partial, last step verified row 183 (recorded-dest)', () => {
  const p = plans['d+1+2,1,2'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [92, null, 183]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'unmapped', 'verified']);
  assert.equal(p.string_status, 'partial');
});

test('1,1 flagship: step 1 SUSPENDED-DRIFT (prefix move 1 ROW-CHANGED 35->None), row null', () => {
  const p = plans['1,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.equal(p.steps[0].status, 'unmapped');
  assert.ok(p.steps[0].reasons.join(' ').includes('SUSPENDED-DRIFT'), 'step 1 must carry the SUSPENDED-DRIFT reason');
});

test('TACKLE family + throw-class df+1,2 + throw-class ws2,1+2 have NO plan key', () => {
  for (const k of ['TACKLE.1,1', 'TACKLE.1,1,1', 'TACKLE.1,1,1,1', 'df+1,2', 'ws2,1+2']) assert.ok(!plans[k], `${k} must have no plan`);
});

test('near-miss grapple labels stay planned but unmapped-all, wiring no row', () => {
  for (const k of ['NANIWA_ULTIMATE_TACKLE.2,1,1,2', 'NANIWA_ULTIMATE_TACKLE.2,1,2,1', 'Tackle.2,1,2,1']) {
    assert.equal(plans[k].string_status, 'unmapped-all', `${k} must be unmapped-all`);
    assert.ok(plans[k].steps.every((s) => s.row === null), `${k} must wire no row`);
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

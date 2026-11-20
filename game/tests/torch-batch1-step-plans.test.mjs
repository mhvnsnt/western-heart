/* Torch Batch 1 step plans (LP1/RP2-only strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/TORCH-BATCH1-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on #1096 (feat/batch1-step-plans-pantera-20261024,
 * the step-playback engine). It does NOT stack on the Pantera plan branches,
 * the burger plan branches, the demonio plan branches, the diablo plan
 * branches, the kinpo plan branches, the phantom plan branches, the scimitar
 * plan branches, or the skull plan branches: torch.json plans do not conflict
 * with any other fighter's plans.
 * It does NOT include #1097's Pantera Batch 1 follow-up fills (Pantera-specific,
 * and its row-49 SOFT fill is still unapproved); no SOFT fill is inherited here.
 * This PR does not touch `fighter.js`: #1096's merge onto post-#1078 main must
 * reconcile #1078's `fighter.js` changes with #1096's engine branch, and that
 * belongs to #1096's merge, not this PR.
 * DUAL BANK (verified, not assumed): torch's T3 moves carry t3_source jin (145)
 * and anna (224); file-level t3_source is jin, t3_bank moveset_jin.json, on
 * BOTH #1096 and main — NEVER assumed for all moves. Every step adjudicates
 * against ITS OWN move's bank. Torch is the FIRST dual-bank fighter in the
 * pipeline. Pack dir = bank name for both banks. Pack banks:
 * divmot09_jin.bin (jin), divmot17_anna.bin (anna).
 * BOUND BANK (engine fact, fighter.js #1096 FIGHTER_BANK torch->anna +
 * moveset anim_bank anna): torch plays from the ANNA bank in game. The #1096
 * step-plan branch resolves row:N against the bound bank ONLY, so jin-bank
 * gate-verified steps are BANK-BLOCKED (status review, row null,
 * bank_verified_row preserved) — wiring them would play anna row N, a
 * wrong-bank clip. Anna-bank gate-verified steps wire normally.
 * GATE-ONLY batch: Job 2 torch entries 0, Job 3 torch entries 0 — Job 3 fills
 * 0 and Job 4 joins 0 by data absence, not by failure.
 * Jin-bank rules, per-bank evidence (freshly derived here): row 35 EXISTS
 * (starts-airborne, btn 1); row 220 EXISTS (standing RP2, btn 2); row 216
 * EXISTS (jump, btn 0). Jin row 248 (torch LP1 move 1's own row) is STANDING
 * but button 12 — it FAILS every single-LP1 step under exact-equality.
 * Anna-bank rules, per-bank evidence (first-ever anna adjudication): row 35
 * EXISTS (starts-airborne, btn 1); row 220 EXISTS in hit_frames (button 0)
 * but is ABSENT from Job 1; row 216 EXISTS in hit_frames (button 0) but is
 * ABSENT from Job 1.
 * Torch basics (both files, unchanged): LP1 move 1 jin r248, RP2 move 2 jin
 * r220, LK3 move 3 jin r195, RK4 move 4 jin r199. Re-baseline #1096 vs main:
 * moves + strings deep-equal; row-changed 0, damage-only 0 — suspended 0.
 * Canonicalization is the CORRECTED rule: strip ONLY a trailing
 * ~t[378] source-variant suffix; input-~ is Tekken cancel notation, part of
 * the move. Torch Batch 1 contains ZERO input-~ canonicals. File-wide there
 * is exactly ONE input-~ comma key, d+4,1~4 (T8 Anna, LP1+RK4 — not Batch 1).
 * Rules asserted here (all data-level, no THREE needed):
 *   1. torch.json still has 892 moves / 155 strings entries (plans additive only).
 *   2. string_step_plans has exactly 79 keys (43 planned canonicals + 36 twins).
 *   3. Batch 1 verified steps always carry a row whose OWN-BANK (anna, the
 *      bound bank) hit_frames button equals the step bits and whose throw
 *      flag is 0; verified rows always exist in the anna hit_frames;
 *      review/unmapped steps carry row null. No Batch 1 step carries a soft
 *      flag (Batch 1 wires zero Job 3 fills — no torch Job 3 data exists —
 *      and zero SOFT fills). Every verified step's bank is anna; every
 *      BANK-BLOCKED step is review with row null and a bank_verified_row.
 *   4. 2,1 flagship: review-only, bank_verified_rows [220,221] (jin) — the
 *      famous jin chain is gate-verified but NOT playable via the #1096
 *      engine path (bound bank anna); rows are [null,null], never anna 220/221.
 *   5. b+1+2,1 flagship: partial, step 1 unmapped (no candidate), step 2
 *      VERIFIED anna row 355.
 *   6. u+1,1 flagship: partial, step 1 unmapped (no candidate), step 2
 *      VERIFIED anna row 32 (jump context, SOFT waived).
 *   7. d/f+1+2,2 flagship: partial, step 1 unmapped (jin row 117 is a throw
 *      row), step 2 VERIFIED anna row 174 with GATE-NOTE (standing row for
 *      a crouch-context step, demonio Batch 1 precedent).
 *   8. 1,2 flagship: partial, step 1 unmapped (jin row 248 button 12 !=
 *      step bits 1 — torch's own LP1 row is a multi-button clip, rejected
 *      for single-LP1 steps); step 2 BANK-BLOCKED (jin row 249).
 *   9. TACKLE family gets no plan (CSV-only, narrow grapple label).
 *  10. The verified-last-step Batch 1 keys are exactly the 19 listed below.
 *  11. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Run: node --test game/tests/torch-batch1-step-plans.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const torch = JSON.parse(readFileSync(join(ROOT, 'game/assets/movesets/torch.json'), 'utf8'));
const fighterSrc = readFileSync(join(ROOT, 'game/js/fighter.js'), 'utf8');
const hfAnna = JSON.parse(readFileSync(join(ROOT, 'game/assets/anim/t3/anna/hit_frames.json'), 'utf8')).rows;
const hfJin = JSON.parse(readFileSync(join(ROOT, 'game/assets/anim/t3/jin/hit_frames.json'), 'utf8')).rows;

const plans = torch.string_step_plans.plans;
const B1 = ["1,2", "1,2,1", "1,2,1,2", "1,2,1,H.2", "1,2,1~t7.anna", "1,2,1~t7.anna.2", "1,2,1~t7.anna.3", "1,2,2", "1,2,uf+1+2", "1,2~t7.anna", "1,2~t7.anna.2", "1,2~t8.anna", "2,1", "2,1,2", "2,1,2,2", "2,1~t3.anna", "2,1~t7.anna", "2,1~t7.anna.2", "2,2", "2,uf+1+2", "CJM.2,1", "CJM.2,1~t7.anna", "CJM.2,1~t7.anna.2", "FC.df+2,H.1", "HAM.2,1", "HAM.2,1,2", "HAM.2,2", "b+1+2,1", "b+1+2,1,1", "b+1,2", "b+1,2,2", "b+1,2,2~t7.anna", "b+1,2,2~t7.anna.2", "b+1,2,2~t7.anna.3", "b+1,2~t7.anna", "b+1,2~t7.anna.2", "b+2,2", "b+2,2~t3.anna", "b+2,2~t3.anna.2", "b+2,2~t7.anna", "b+2,2~t7.anna.2", "b+2,b+2", "b+2,f+2", "d+1+2,1", "d+1+2,1,2", "d+1+2,2", "d/f+1+2,2", "d/f+1,2", "d/f+1,2~t7.anna", "db+1,2", "df+1,2", "f+1+2,1", "f+2,1", "f+2,1,2", "f+2,1~t3.anna", "f+2,1~t3.anna.2", "f+2,1~t3.anna.3", "f+2,1~t3.anna.4", "f+2,f+1+2", "qcf+2,1", "qcf+2,1~t7.anna", "qcf+2,1~t7.anna.2", "u+1,1", "u+1,1~t3.anna", "u+1,1~t3.anna.2", "u+1,1~t3.anna.3", "u+1,2", "u/b+1,1", "u/b+1,1~t3.anna", "u/b+1,1~t3.anna.2", "u/b+1,1~t3.anna.3", "u/b+1,2", "u/f+1+2,1", "u/f+1,1", "u/f+1,1~t3.anna", "u/f+1,1~t3.anna.2", "u/f+1,1~t3.anna.3", "u/f+1,2", "ws1,2"];
const B1_VERIFIED_LAST = ["b+1+2,1", "b+1+2,1,1", "d/f+1+2,2", "f+2,1,2", "u+1,1", "u+1,1~t3.anna", "u+1,1~t3.anna.2", "u+1,1~t3.anna.3", "u+1,2", "u/b+1,1", "u/b+1,1~t3.anna", "u/b+1,1~t3.anna.2", "u/b+1,1~t3.anna.3", "u/b+1,2", "u/f+1,1", "u/f+1,1~t3.anna", "u/f+1,1~t3.anna.2", "u/f+1,1~t3.anna.3", "u/f+1,2"];
const VERIFIED_BUTTONS = {"32": 1, "33": 1, "34": 1, "44": 2, "45": 2, "46": 2, "171": 2, "174": 2, "355": 1, "356": 1};

function stepBits(step) {
  const seg = step.split('.').pop();
  let b = 0;
  for (const c of seg) if ('1234'.includes(c)) b |= 1 << (Number(c) - 1);
  return b;
}

test('torch move/string counts unchanged by the additive plans block', () => {
  assert.equal(Object.keys(torch.moves).length, 892);
  assert.equal(torch.strings.length, 155);
  assert.equal(Object.keys(plans).length, 79);
});

test('Batch 1 keys are exactly the documented 79', () => {
  assert.equal(B1.length, 79);
  for (const key of B1) assert.ok(plans[key], `Batch 1 key ${key} missing`);
  const extra = Object.keys(plans).filter((k) => !B1.includes(k));
  assert.deepEqual(extra, []);
});

test('Batch 1 verified steps carry anna rows (button == step bits, throw 0, row exists in anna hit_frames); review/unmapped carry row null; no soft flags; verified steps are anna-bank only', () => {
  for (const key of B1) {
    for (const s of plans[key].steps) {
      assert.ok(!('soft' in s) || s.soft !== true, `${key} step ${s.step} carries a soft flag`);
      if (s.status === 'verified') {
        assert.notEqual(s.row, null, `${key} step ${s.step} verified but row null`);
        assert.equal(s.bank, 'anna', `${key} step ${s.step} verified on non-anna bank ${s.bank} — bound bank is anna`);
        assert.ok(hfAnna[String(s.row)], `${key} step ${s.step} verified on row ${s.row} which does not exist in the anna hit_frames`);
        assert.equal(hfAnna[String(s.row)][5], stepBits(s.step), `${key} step ${s.step} row ${s.row} button mismatch`);
        assert.equal(hfAnna[String(s.row)][5], VERIFIED_BUTTONS[String(s.row)], `${key} step ${s.step} row ${s.row} button mismatch (map)`);
        assert.equal(hfAnna[String(s.row)][4], 0, `${key} step ${s.step} row ${s.row} is a throw row`);
      } else {
        assert.equal(s.row, null, `${key} step ${s.step} ${s.status} must not carry a playable row`);
        if (s.bank_verified_row != null) {
          assert.equal(s.status, 'review', `${key} step ${s.step} carries bank_verified_row but is not review`);
          assert.ok(s.reasons.join(' ').includes('BANK-BLOCKED'), `${key} step ${s.step} carries bank_verified_row without a BANK-BLOCKED reason`);
          assert.ok(hfJin[String(s.bank_verified_row)], `${key} step ${s.step} bank_verified_row ${s.bank_verified_row} missing from jin hit_frames`);
        }
      }
    }
  }
});

test('jin row 248 is a multi-button clip (button 12), so it can never verify a single-LP1 step', () => {
  assert.equal(hfJin['248'][5], 12);
  assert.equal(hfJin['248'][4], 0);
});

test('2,1 flagship: review-only, bank_verified_rows [220,221] (jin) — gate-verified but NOT wired, never anna 220/221', () => {
  const p = plans['2,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.deepEqual(p.steps.map((s) => s.bank_verified_row), [220, 221]);
  assert.deepEqual(p.steps.map((s) => s.status), ['review', 'review']);
  assert.equal(p.string_status, 'review-only');
});

test('b+1+2,1 flagship: partial, step 1 unmapped (no candidate), step 2 VERIFIED anna row 355', () => {
  const p = plans['b+1+2,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, 355]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'verified']);
  assert.equal(p.string_status, 'partial');
  assert.equal(p.steps[1].bank, 'anna');
});

test('u+1,1 flagship: partial, step 1 unmapped (no candidate), step 2 VERIFIED anna row 32 (jump context, SOFT waived)', () => {
  const p = plans['u+1,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, 32]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'verified']);
  assert.equal(p.string_status, 'partial');
  assert.ok(p.steps[1].reasons.join(' ').includes('waived (jump context)'), 'jump-context step must record the SOFT waiver');
});

test('d/f+1+2,2 flagship: partial, step 1 unmapped (jin row 117 is a throw row), step 2 VERIFIED anna row 174 with GATE-NOTE', () => {
  const p = plans['d/f+1+2,2'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, 174]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'verified']);
  assert.equal(p.string_status, 'partial');
  assert.ok(p.steps[0].reasons.join(' ').includes('throw flag 1'), 'step 1 must record the throw-row rejection');
  assert.ok(p.steps[1].reasons.join(' ').includes('GATE-NOTE'), 'step 2 standing row for a crouch step must carry the GATE-NOTE');
});

test('1,2 flagship: partial, step 1 unmapped (jin row 248 button 12 != bits 1), step 2 BANK-BLOCKED (jin row 249)', () => {
  const p = plans['1,2'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'review']);
  assert.equal(p.string_status, 'partial');
  assert.equal(p.steps[0].candidate_row, 248);
  assert.ok(p.steps[0].reasons.join(' ').includes('button 12'), 'step 1 must record the button-12 rejection');
  assert.equal(p.steps[1].bank_verified_row, 249);
  assert.ok(p.steps[1].reasons.join(' ').includes('BANK-BLOCKED'), 'step 2 must record BANK-BLOCKED');
});

test('TACKLE family gets no plan (CSV-only, narrow grapple label)', () => {
  for (const key of ['TACKLE.1,1', 'TACKLE.1,1,1', 'TACKLE.1,1,1,1']) {
    assert.equal(plans[key], undefined, `${key} must not gain a plan`);
  }
});

test('verified-last-step Batch 1 keys are exactly the documented 19', () => {
  assert.equal(B1_VERIFIED_LAST.length, 19);
  for (const key of B1_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B1.filter((k) => !B1_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

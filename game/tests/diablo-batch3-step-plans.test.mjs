/* Diablo Batch 3 step plans (mixed-pair strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/DIABLO-BATCH3-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on diablo Batch 2 (feat/diablo-batch2-step-plans-20261025,
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
 * Bank (verified, not assumed — carried from diablo Batches 1–2 four-way proof):
 * diablo's T3 bank is HEIHACHI (t3_source heihachi, t3_bank moveset_heihachi.json,
 * on BOTH the Batch 2 branch and main; t3/ directory listing; Job 1/Job 4 bank
 * heihachi_on_jin; Job 2 bank heihachi). Bank resolution: moveset/Job 2 bank
 * heihachi <-> Job 1/Job 4/pack bank heihachi_on_jin <-> divmot13_heihachi.bin
 * on the jin rig (the heihachi/ dir carries hit_frames + skeleton but NO
 * rows.pack.json, the known 404 gap; the playable pack lives under
 * heihachi_on_jin, and the two hit_frames.json files are the SAME blob
 * a87184616...). Gap-1 for Batch 3: main heihachi hit_frames blob a87184616…,
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
 * cancel notation, part of the move. Batch 3 contains NO input-~ canonicals
 * and NO __main records (diablo's cancel notation lives in LP1/RP2 strings,
 * as Batch 1 proved and Batch 2 confirmed for kick strings). Suspended-drift:
 * 0 — none of the 3 row-changed moves (1, 1_r46, u+1,1~t3.heihachi.2) is a
 * Batch 3 step prefix (1 is LP1 scope; 1_r46 is not a step prefix;
 * u+1,1~t3.heihachi.2 is a twin key whose canonical u+1,1 is Batch 1 scope).
 * Spelling quirks kept as stored keys: d/f+4,2 vs df+4,2 are distinct
 * canonicals with different step-1 evidence (row 183 vs no candidate) —
 * not merged, not smoothed over (diablo Batch 2 precedent: u/f+3,4 vs uf+3,4).
 * Standing rows verified for crouch-context steps (d/f+3,2 step 2 row 226,
 * d/f+3,2,2 steps 2–3 rows 226/227) follow the demonio Batch 1 / diablo
 * Batch 1 precedent: the pipeline stance gate flags crouch rows for
 * non-crouch steps, not standing rows for crouch steps; if the gate is ever
 * tightened these three steps must be re-adjudicated. Row 225 is duck-dip,
 * which passes for crouch context outright — NOT a gate-note case.
 * Rules asserted here (all data-level, no THREE needed):
 *   1. diablo.json still has 661 moves / 90 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 175 keys (132 Batches 1–2 + 43 Batch 3).
 *   3. Batch 3 keys are exactly the documented 43 (22 planned canonicals + 21 twins).
 *   4. Batch 3 verified steps always carry a row whose heihachi hit_frames
 *      button equals the step bits and whose throw flag is 0; no verified
 *      ground-context step uses row 35 (row 35 does not exist in this bank);
 *      review/unmapped steps carry row null. No Batch 3 step carries a soft
 *      flag (Batch 3 wires zero Job 3 fills and zero SOFT fills).
 *   5. d/f+4,2 flagship: verified-all on rows 183/225 (crouch context).
 *   6. 3,2 flagship: partial on rows [153, null] (standing LK3 step 1 verified).
 *   7. b+2,4 flagship: review-only on rows [null, null] (STANCE-SOFT duck-dip
 *      rows 207/214 for standing steps), both steps review.
 *   8. u/f+1,3 flagship: partial on rows [null, 60] (jump last step verified).
 *   9. uf+4,H.1 flagship: partial on rows [74, null] (jump first step verified).
 *  10. f+2,3 flagship: step 1 review (SOFT fail on row 178), row null.
 *  11. The verified-last-step Batch 3 keys are exactly the 28 listed below,
 *      and verified rows carry the step buttons in the repo heihachi
 *      hit_frames.json.
 *  12. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Cumulative update (Diablo Batch 4, 2026-10-25): plan count 175 -> 217; earlier-keys
 * count 132 -> 174 (111 Batch 1 + 21 Batch 2 + 42 Batch 4); all Batch 3 content
 * assertions preserved verbatim (burger test-evolution rule; Pantera's latent break
 * NOT copied).
 * Run: node --test game/tests/diablo-batch3-step-plans.test.mjs   (from repo root)
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
const B3 = ["1+3,1", "1+3,1~t3.heihachi", "3,2", "b+1,4", "b+2,4", "b+3,2", "b+3,3,H.2", "d+3,H.2", "d/f+3,2", "d/f+3,2,2", "d/f+4,1", "d/f+4,1~t3.heihachi", "d/f+4,2", "df+4,2", "f+1+4,1", "f+1+4,1,1", "f+2,3", "f+2,3~t7.heihachi", "u+1,3", "u+1,3~t3.heihachi", "u+1,3~t3.heihachi.2", "u+1,3~t3.heihachi.3", "u+1,4", "u+1,4~t3.heihachi", "u+1,4~t3.heihachi.2", "u+1,4~t3.heihachi.3", "u/b+1,3", "u/b+1,3~t3.heihachi", "u/b+1,3~t3.heihachi.2", "u/b+1,3~t3.heihachi.3", "u/b+1,4", "u/b+1,4~t3.heihachi", "u/b+1,4~t3.heihachi.2", "u/b+1,4~t3.heihachi.3", "u/f+1,3", "u/f+1,3~t3.heihachi", "u/f+1,3~t3.heihachi.2", "u/f+1,3~t3.heihachi.3", "u/f+1,4", "u/f+1,4~t3.heihachi", "u/f+1,4~t3.heihachi.2", "u/f+1,4~t3.heihachi.3", "uf+4,H.1"];
const B3_VERIFIED_LAST = ["d/f+3,2", "d/f+3,2,2", "d/f+4,2", "df+4,2", "u+1,3", "u+1,3~t3.heihachi", "u+1,3~t3.heihachi.2", "u+1,3~t3.heihachi.3", "u+1,4", "u+1,4~t3.heihachi", "u+1,4~t3.heihachi.2", "u+1,4~t3.heihachi.3", "u/b+1,3", "u/b+1,3~t3.heihachi", "u/b+1,3~t3.heihachi.2", "u/b+1,3~t3.heihachi.3", "u/b+1,4", "u/b+1,4~t3.heihachi", "u/b+1,4~t3.heihachi.2", "u/b+1,4~t3.heihachi.3", "u/f+1,3", "u/f+1,3~t3.heihachi", "u/f+1,3~t3.heihachi.2", "u/f+1,3~t3.heihachi.3", "u/f+1,4", "u/f+1,4~t3.heihachi", "u/f+1,4~t3.heihachi.2", "u/f+1,4~t3.heihachi.3"];
const VERIFIED_BUTTONS = {"59": 4, "60": 4, "61": 4, "74": 8, "75": 8, "76": 8, "153": 4, "183": 8, "225": 2, "226": 2, "227": 2};

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

test('Batch 3 keys are exactly the documented 43', () => {
  assert.equal(B3.length, 43);
  for (const key of B3) assert.ok(plans[key], `Batch 3 key ${key} missing`);
  const earlier = Object.keys(plans).filter((k) => !B3.includes(k));
  assert.equal(earlier.length, 174);
});

test('Batch 3 verified steps carry rows (button == step bits, throw 0, never row 35 on ground); review/unmapped carry row null; no soft flags', () => {
  for (const key of B3) {
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

test('d/f+4,2 flagship: verified-all on rows 183/225 (crouch context)', () => {
  const p = plans['d/f+4,2'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [183, 225]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('3,2 flagship: partial on rows [153, null] (standing LK3 step 1 verified)', () => {
  const p = plans['3,2'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [153, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'unmapped']);
  assert.equal(p.string_status, 'partial');
});

test('b+2,4 flagship: review-only on rows [null, null] (STANCE-SOFT duck-dip rows 207/214)', () => {
  const p = plans['b+2,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['review', 'review']);
  assert.equal(p.string_status, 'review-only');
});

test('u/f+1,3 flagship: partial on rows [null, 60] (jump last step verified)', () => {
  const p = plans['u/f+1,3'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, 60]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'verified']);
  assert.equal(p.string_status, 'partial');
  assert.equal(p.jumping_context, true);
});

test('uf+4,H.1 flagship: partial on rows [74, null] (jump first step verified)', () => {
  const p = plans['uf+4,H.1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [74, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'unmapped']);
  assert.equal(p.string_status, 'partial');
  assert.equal(p.jumping_context, true);
});

test('f+2,3 flagship: step 1 review (SOFT fail on row 178), row null', () => {
  const p = plans['f+2,3'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.equal(p.steps[0].status, 'review');
});

test('verified-last-step Batch 3 keys are exactly the documented 28', () => {
  assert.equal(B3_VERIFIED_LAST.length, 28);
  for (const key of B3_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B3.filter((k) => !B3_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

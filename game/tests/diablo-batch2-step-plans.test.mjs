/* Diablo Batch 2 step plans (LK3/RK4-only strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/DIABLO-BATCH2-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on diablo Batch 1 (feat/diablo-batch1-step-plans-20261025,
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
 * Bank (verified, not assumed — carried from diablo Batch 1's four-way proof):
 * diablo's T3 bank is HEIHACHI (t3_source heihachi, t3_bank moveset_heihachi.json,
 * on BOTH the Batch 1 branch and main; t3/ directory listing; Job 1/Job 4 bank
 * heihachi_on_jin; Job 2 bank heihachi). Bank resolution: moveset/Job 2 bank
 * heihachi <-> Job 1/Job 4/pack bank heihachi_on_jin <-> divmot13_heihachi.bin
 * on the jin rig (the heihachi/ dir carries hit_frames + skeleton but NO
 * rows.pack.json, the known 404 gap; the playable pack lives under
 * heihachi_on_jin, and the two hit_frames.json files are the SAME blob
 * a87184616...). Gap-1 for Batch 2: main heihachi hit_frames blob a87184616…,
 * heihachi_on_jin rows.pack blob 9e59dfe5… (= #1109 baked pack), heihachi_on_jin
 * skeleton blob 7fa83b40… — all IDENTICAL to the Batch 1 baseline.
 * Heihachi-bank rules, per-bank evidence (never a cross-bank blanket ban):
 * row 35 does NOT EXIST in this bank (absent from both hit_frames and Job 1),
 * so no row-35 rule applies; row 220 is a JUMP RK4 row here (hit_frames
 * [39,39,88,535,0,8], Job 1 stance jump), gate-adjudicated like any row, NOT
 * jin's standing RP2 row, NOT king's jumping chord row, NOT bryan's button-0
 * row; heihachi_on_jin row 216 is a DUCK-DIP row, NOT jin row 216's jump row
 * and NOT king row 216's dash Konvict Kick.
 * Canonicalization is the CORRECTED rule (demonio Batch 2 finding): strip ONLY
 * a trailing ~t[378].[a-z]+(.N)?$ source-variant suffix; input-~ is Tekken
 * cancel notation, part of the move. Batch 2 contains NO input-~ canonicals
 * and NO __main records (unlike Batch 1's 6 input-~ canonicals — diablo's
 * cancel notation lives in LP1/RP2 strings, not kick strings). Suspended-drift:
 * 0 — none of the 3 row-changed moves (1, 1_r46, u+1,1~t3.heihachi.2) is a
 * Batch 2 step prefix (1 is LP1 scope; 1_r46 is not a step prefix;
 * u+1,1~t3.heihachi.2 is a twin key whose canonical u+1,1 is Batch 1 scope).
 * Spelling quirks kept as stored keys: u/f+3,4 vs uf+3,4 are distinct
 * canonicals (own rows 60/None vs None/74) — not merged, not smoothed over.
 * Rules asserted here (all data-level, no THREE needed):
 *   1. diablo.json still has 661 moves / 90 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 132 keys (111 Batch 1 + 21 Batch 2).
 *   3. Batch 2 keys are exactly the documented 21 (11 planned canonicals + 10 twins).
 *   4. Batch 2 verified steps always carry a row whose heihachi hit_frames
 *      button equals the step bits and whose throw flag is 0; no verified
 *      ground-context step uses row 35 (row 35 does not exist in this bank);
 *      review/unmapped steps carry row null. No Batch 2 step carries a soft
 *      flag (Batch 2 wires zero Job 3 fills and zero SOFT fills).
 *   5. u/f+4,3 flagship: verified-all on rows 86/150 (jump context).
 *   6. u/f+4,4 flagship: verified-all on rows 86/195 (jump context).
 *   7. 3,4 flagship: partial on rows [153, null] (standing LK3 step 1 verified).
 *   8. d/f+4,4,4 flagship: step 3 review (SOFT fail on row 191), row null.
 *   9. d/f+4,4 flagship: step 2 unmapped (chord row 190 rejected for a
 *      single-RK4 step), row null — the whole-string own pick, correctly
 *      retired as a step row.
 *  10. uf+3,4 flagship: partial on rows [null, 74] (starts-airborne jump row).
 *  11. The verified-last-step Batch 2 keys are exactly the 6 listed below,
 *      and verified rows carry the step buttons in the repo heihachi
 *      hit_frames.json.
 *  12. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Run: node --test game/tests/diablo-batch2-step-plans.test.mjs   (from repo root)
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
const B2 = ["3,4", "3,4~t7.heihachi", "FUJ.3,4", "WS.4,4", "WS.4,4~t7.heihachi", "b+3,3", "b+3,3~t7.heihachi", "b+3,3~t7.heihachi.2", "d/f+4,4", "d/f+4,4,4", "u/f+3,4", "u/f+3,4~t3.heihachi", "u/f+3,4~t3.heihachi.2", "u/f+3,4~t3.heihachi.3", "u/f+4,3", "u/f+4,3~t3.heihachi", "u/f+4,4", "u/f+4,4~t3.heihachi", "u/f+4,4~t3.heihachi.2", "uf+3,4", "ws4,4"];
const B2_VERIFIED_LAST = ["u/f+4,3", "u/f+4,3~t3.heihachi", "u/f+4,4", "u/f+4,4~t3.heihachi", "u/f+4,4~t3.heihachi.2", "uf+3,4"];
const VERIFIED_BUTTONS = {"60": 4, "74": 8, "86": 8, "150": 4, "153": 4, "183": 8, "195": 8};

function stepBits(step) {
  const seg = step.split('.').pop();
  let b = 0;
  for (const c of seg) if ('1234'.includes(c)) b |= 1 << (Number(c) - 1);
  return b;
}

test('diablo move/string counts unchanged by the additive plans block', () => {
  assert.equal(Object.keys(diablo.moves).length, 661);
  assert.equal(diablo.strings.length, 90);
  assert.equal(Object.keys(plans).length, 132);
});

test('Batch 2 keys are exactly the documented 21', () => {
  assert.equal(B2.length, 21);
  for (const key of B2) assert.ok(plans[key], `Batch 2 key ${key} missing`);
  const b1 = Object.keys(plans).filter((k) => !B2.includes(k));
  assert.equal(b1.length, 111);
});

test('Batch 2 verified steps carry rows (button == step bits, throw 0, never row 35 on ground); review/unmapped carry row null; no soft flags', () => {
  for (const key of B2) {
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

test('u/f+4,3 flagship: verified-all on rows 86/150 (jump context)', () => {
  const p = plans['u/f+4,3'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [86, 150]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
  assert.equal(p.jumping_context, true);
});

test('u/f+4,4 flagship: verified-all on rows 86/195 (jump context)', () => {
  const p = plans['u/f+4,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [86, 195]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
  assert.equal(p.jumping_context, true);
});

test('3,4 flagship: partial on rows [153, null] (standing LK3 step 1 verified)', () => {
  const p = plans['3,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [153, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'unmapped']);
  assert.equal(p.string_status, 'partial');
});

test('d/f+4,4,4 flagship: step 3 review (SOFT fail on row 191), row null', () => {
  const p = plans['d/f+4,4,4'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [183, null, null]);
  assert.equal(p.steps[2].status, 'review');
});

test('d/f+4,4 flagship: step 2 unmapped (chord row 190 rejected for a single-RK4 step), row null', () => {
  const p = plans['d/f+4,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [183, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'unmapped']);
  assert.equal(p.string_status, 'partial');
});

test('uf+3,4 flagship: partial on rows [null, 74] (starts-airborne jump row)', () => {
  const p = plans['uf+3,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, 74]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'verified']);
  assert.equal(p.string_status, 'partial');
  assert.equal(p.jumping_context, true);
});

test('verified-last-step Batch 2 keys are exactly the documented 6', () => {
  assert.equal(B2_VERIFIED_LAST.length, 6);
  for (const key of B2_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B2.filter((k) => !B2_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

/* Demonio Batch 2 step plans (LK3/RK4-only strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/DEMONIO-BATCH2-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on demonio Batch 1 (feat/demonio-batch1-step-plans-20261025,
 * PR #1108), which is stacked on #1096 (the step-playback engine). It does NOT stack on
 * the Pantera plan branches (#1099/#1101/#1102) or the burger plan branches
 * (#1103/#1104/#1105/#1107): demonio.json plans do not conflict with pantera.json or
 * burger.json plans. It does NOT include #1097's Pantera Batch 1 follow-up fills
 * (Pantera-specific, and its row-49 SOFT fill is still unapproved); no SOFT fill is
 * inherited here. This PR does not touch `fighter.js`.
 * Bank (verified, not assumed): demonio's T3 bank is JIN (t3_source jin,
 * t3_bank moveset_jin.json, t3/ directory listing, Job 1/2/4 all jin).
 * Jin-bank rules (Batch 1's documented correction, carried forward): jin row 220 is a
 * STANDING RP2 row, NOT blanket-banned (no Batch 2 step uses it — Batch 2 is LK3/RK4
 * only); jin row 35 IS starts-airborne, so the row-35 rejection for ground steps stands
 * (no Batch 2 step uses row 35 at all: every verified Batch 2 step is jump-context
 * or crouch-context, and no ground-context step plays row 35).
 * Canonicalization correction vs Batch 1 (documented in the doc): only a trailing
 * source-variant suffix (~t3.jin, ~t7.jin[.N], ~t8.jin) is stripped. A '~' inside the
 * input is Tekken cancel notation, not a variant marker: "f+3~3,d/f+3" (Heat Seeker)
 * and "d+3,4~4" (Mid Sidekick) are their own canonicals, NOT variants of "f+3" /
 * "d+3,4", and no bogus single-move canonicals ("4", "f+3") are created. Batch 1 is
 * provably unaffected (no input-~ key old-canonicalizes into Batch 1's universe).
 * Rules asserted here (all data-level, no THREE needed):
 *   1. demonio.json still has 764 moves / 156 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 84 keys (59 Batch 1 + 25 Batch 2: 17 planned
 *      canonicals + 8 twins). Batch 1 keys are asserted in the cumulative Batch 1 test.
 *   3. Batch 2 verified steps always carry a row whose jin hit_frames button equals
 *      the step bits and whose throw flag is 0; no verified ground-context step uses
 *      row 35; review/unmapped steps carry row null. No Batch 2 step carries a soft
 *      flag (Batch 2 wires zero Job 3 fills and zero SOFT fills).
 *   4. u+4,4 flagship: verified-all on rows 79/209 (jump context).
 *   5. u/f+4,4 flagship: verified-all on rows 80/207 (jump context).
 *   6. d/f+4,4 flagship: partial — step 1 verified row 205 (crouch context), step 2
 *      review (SOFT limb-peak proxy fail), row null.
 *   7. f+4,3 flagship: step 1 review (SOFT limb-peak proxy fail), row null.
 *   8. d+3,4~4 flagship: unmapped-all (own canonical, NOT a variant of d+3,4; both
 *      steps unmapped, rows null — the intermediate prefixes are T8-sourced).
 *   9. f+3~3,d/f+3 flagship: unmapped-all (own canonical, NOT a variant of f+3; both
 *      steps unmapped, rows null).
 *  10. Bogus single-move canonicals "4" and "f+3" have NO plan key.
 *  11. The verified-last-step Batch 2 keys are exactly the 5 listed below, and
 *      verified rows carry the step buttons in the repo Jin hit_frames.json.
 *  12. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Run: node --test game/tests/demonio-batch2-step-plans.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const demonio = JSON.parse(readFileSync(join(ROOT, 'game/assets/movesets/demonio.json'), 'utf8'));
const fighterSrc = readFileSync(join(ROOT, 'game/js/fighter.js'), 'utf8');
const hfPath = join(ROOT, 'game/assets/anim/t3/jin/hit_frames.json');
const hf = JSON.parse(readFileSync(hfPath, 'utf8')).rows;

const plans = demonio.string_step_plans.plans;
const B2 = ["DVS.4,4", "WS.4,4", "d+3,3", "d+3,3~t7.jin", "d+3,4", "d+3,4,3", "d+3,4~4", "d/f+3,3", "d/f+3,3~t7.jin", "d/f+4,4", "d/f+4,4~t3.jin", "f+3,3", "f+3~3,d/f+3", "f+3~3,d/f+3~t7.jin", "f+4,3", "u+4,4", "u/f+4,3", "u/f+4,3~t3.jin", "u/f+4,4", "u/f+4,4,4", "u/f+4,4,4,4", "u/f+4,4,4,4~t3.jin", "u/f+4,4,4~t3.jin", "u/f+4,4~t3.jin", "ws4,4"];
const B2_VERIFIED_LAST = ["u+4,4", "u/f+4,3", "u/f+4,3~t3.jin", "u/f+4,4", "u/f+4,4~t3.jin"];
const VERIFIED_BUTTONS = {"79": 8, "80": 8, "193": 4, "205": 8, "207": 8, "209": 8};

function stepBits(step) {
  const seg = step.split('.').pop();
  let b = 0;
  for (const c of seg) if ('1234'.includes(c)) b |= 1 << (Number(c) - 1);
  return b;
}

test('demonio move/string counts unchanged by the additive plans block; 84 plans total', () => {
  assert.equal(Object.keys(demonio.moves).length, 764);
  assert.equal(demonio.strings.length, 156);
  assert.equal(Object.keys(plans).length, 84);
});

test('Batch 2 keys are exactly the documented 25', () => {
  assert.equal(B2.length, 25);
  for (const key of B2) assert.ok(plans[key], `Batch 2 key ${key} missing`);
});

test('Batch 2 verified steps carry rows (button == step bits, throw 0, never row 35 on ground); review/unmapped carry row null; no soft flags', () => {
  for (const key of B2) {
    for (const s of plans[key].steps) {
      assert.ok(!('soft' in s) || s.soft !== true, `${key} step ${s.step} carries a soft flag`);
      if (s.status === 'verified') {
        assert.notEqual(s.row, null, `${key} step ${s.step} verified but row null`);
        if (!plans[key].jumping_context) assert.notEqual(s.row, 35, `${key} step ${s.step} verified on starts-airborne row 35 for a ground step`);
        assert.equal(hf[String(s.row)][5], stepBits(s.step), `${key} step ${s.step} row ${s.row} button mismatch`);
        assert.equal(hf[String(s.row)][5], VERIFIED_BUTTONS[String(s.row)], `${key} step ${s.step} row ${s.row} button mismatch (map)`);
        assert.equal(hf[String(s.row)][4], 0, `${key} step ${s.step} row ${s.row} is a throw row`);
      } else {
        assert.equal(s.row, null, `${key} step ${s.step} ${s.status} must not carry a playable row`);
      }
    }
  }
});

test('u+4,4 flagship: verified-all on rows 79/209 (jump context)', () => {
  const p = plans['u+4,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [79, 209]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
  assert.equal(p.jumping_context, true);
});

test('u/f+4,4 flagship: verified-all on rows 80/207 (jump context)', () => {
  const p = plans['u/f+4,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [80, 207]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
  assert.equal(p.jumping_context, true);
});

test('d/f+4,4 flagship: partial — step 1 verified row 205 (crouch context), step 2 review (SOFT proxy fail), row null', () => {
  const p = plans['d/f+4,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [205, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'review']);
  assert.equal(p.string_status, 'partial');
});

test('f+4,3 flagship: step 1 review (SOFT proxy fail), row null', () => {
  const p = plans['f+4,3'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.equal(p.steps[0].status, 'review');
});

test('d+3,4~4 flagship: unmapped-all (own canonical, NOT a variant of d+3,4)', () => {
  const p = plans['d+3,4~4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.equal(p.string_status, 'unmapped-all');
  assert.ok(!('twin_of' in p), 'd+3,4~4 must not be a twin of d+3,4');
  assert.ok(plans['d+3,4'], 'd+3,4 keeps its own plan');
});

test('f+3~3,d/f+3 flagship: unmapped-all (own canonical, NOT a variant of f+3)', () => {
  const p = plans['f+3~3,d/f+3'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.equal(p.string_status, 'unmapped-all');
  assert.ok(!('twin_of' in p), 'f+3~3,d/f+3 must not be a twin of f+3');
  assert.ok(plans['f+3~3,d/f+3~t7.jin'], 'f+3~3,d/f+3~t7.jin is the twin');
});

test('bogus single-move canonicals 4 and f+3 have NO plan key', () => {
  assert.ok(!plans['4'], '4 must have no plan (it is not a string)');
  assert.ok(!plans['f+3'], 'f+3 must have no plan (it is not a string)');
});

test('verified-last-step Batch 2 keys are exactly the documented 5', () => {
  assert.equal(B2_VERIFIED_LAST.length, 5);
  for (const key of B2_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B2.filter((k) => !B2_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

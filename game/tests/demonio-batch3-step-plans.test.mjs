/* Demonio Batch 3 step plans (mixed-pair strings: one punch + one kick pair, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/DEMONIO-BATCH3-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on demonio Batch 2 (feat/demonio-batch2-step-plans-20261025,
 * PR #1110), which is stacked on Batch 1 (feat/demonio-batch1-step-plans-20261025, PR #1108),
 * which is stacked on #1096 (the step-playback engine). It does NOT stack on
 * the Pantera plan branches (#1099/#1101/#1102) or the burger plan branches
 * (#1103/#1104/#1105/#1107): demonio.json plans do not conflict with pantera.json or
 * burger.json plans. It does NOT include #1097's Pantera Batch 1 follow-up fills
 * (Pantera-specific, and its row-49 SOFT fill is still unapproved); no SOFT fill is
 * inherited here. This PR does not touch `fighter.js`.
 * Bank (verified, not assumed): demonio's T3 bank is JIN (t3_source jin,
 * t3_bank moveset_jin.json, t3/ directory listing, Job 1/2/4 all jin).
 * Jin-bank rules (Batch 1's documented correction, carried forward): jin row 220 is a
 * STANDING RP2 row, NOT blanket-banned — it is adjudicated by the normal gates
 * (button + throw + stance + SOFT) like any jin row, and verifies here for the 2,4
 * step 1 (standing RP2 step). Jin row 35 IS starts-airborne, so the row-35 rejection
 * for ground steps stands (no Batch 3 step uses row 35 at all).
 * Canonicalization correction (carried from Batch 2): only a trailing source-variant
 * suffix (~t3.jin, ~t7.jin[.N], ~t8.jin) is stripped. A '~' inside the input is Tekken
 * cancel notation, not a variant marker: "1,3~3", "1,3~3,d/f+3", "WS.1,3~3",
 * "ws1,3~3", "d/f+1,4~4" and "df+1,4~4" are all OWN Batch 3 canonicals, NOT variants
 * of "1", "WS.1", "ws1", "d/f+1" or "df+1". Batch 4 carry-forwards "2,1,4~4" and
 * "4~3,H.1+2" are correctly excluded (button-set union size 3 and 4).
 * Rules asserted here (all data-level, no THREE needed):
 *   1. demonio.json still has 764 moves / 156 strings entries (plans are additive only).
 *   2. CUMULATIVE (Batch 4 lane, 2026-10-25): string_step_plans has exactly 271 keys (59 Batch 1 + 25 Batch 2 + 87 Batch 3 +
 *      100 Batch 4: 68 planned canonicals + 32 twins). Batch 1 keys are asserted in the cumulative
 *      Batch 1 test; Batch 2 keys in the cumulative Batch 2 test; Batch 4's own assertions live
 *      in demonio-batch4-step-plans.test.mjs.
 *   3. Batch 3 verified steps always carry a row whose jin hit_frames button equals
 *      the step bits and whose throw flag is 0; no verified ground-context step uses
 *      row 35; review/unmapped steps carry row null. No Batch 3 step carries a soft
 *      flag (Batch 3 wires zero Job 3 fills and zero SOFT fills).
 *   4. 2,4 flagship: partial — step 1 verified row 220 (standing RP2 row), step 2
 *      unmapped (no candidate; Job 3 soft-filed row 138 documented, NOT wired).
 *   5. 3,1 flagship: partial — step 1 verified row 195, step 2 unmapped (Job 3
 *      ROW-ONLY rows 92/105 documented, NOT wired).
 *   6. b+2,4 flagship: partial — step 2 verified row 251 (RK4 step), step 1
 *      unmapped (b+2 prefix has no candidate).
 *   7. b+2,4,2 flagship: step 2 verified row 251, last step verified row 252.
 *   8. b+2,4,4,4,4,2 flagship: last step verified row 258.
 *   9. f+2,4 flagship: step 1 verified row 103, step 2 unmapped.
 *  10. u+1,3 flagship: step 1 unmapped, last step verified row 54 (jump context,
 *      SOFT waived per Batch 1 precedent).
 *  11. u/f+4,4,1 flagship: steps 1-2 verified rows 80/207 (same as Batch 2 u/f+4,4),
 *      last step unmapped — own row 208 REJECTED (throw row, button 0), never wired.
 *  12. 4,1 flagship: step 1 review (SOFT limb-peak proxy fail), row null.
 *  13. 1,3 flagship: step 1 SUSPENDED-DRIFT (prefix move 1 ROW-CHANGED 41->None),
 *      row null, never wired on stale data (stale row 41 is starts-airborne).
 *  14. 1,3~3 flagship: unmapped-all (own canonical, NOT a variant of 1).
 *  15. 1,3~3,d/f+3 flagship: unmapped-all (own canonical, NOT a variant of 1).
 *  16. ZEN.1,3 (throw class) and its twins have NO plan key; Batch 4
 *      carry-forwards 2,1,4~4 and 4~3,H.1+2 have NO plan key.
 *  17. The verified-last-step Batch 3 keys are exactly the 27 listed below, and
 *      verified rows carry the step buttons in the repo Jin hit_frames.json.
 *      The review-last-step Batch 3 key is exactly b+2,4,4,4,4.
 *  18. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Run: node --test game/tests/demonio-batch3-step-plans.test.mjs   (from repo root)
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
const B3 = ["1+4,1", "1+4,b+1", "1,3", "1,3~3", "1,3~3,d/f+3", "1,3~3,d/f+3~t7.jin", "1,3~3,d/f+3~t7.jin.2", "1,3~3~t7.jin", "1,3~t3.jin", "1,3~t7.jin", "1,3~t7.jin.2", "1,3~t7.jin.3", "1,3~t7.jin.4", "1,4", "1,d+3", "1,d+3~t7.jin", "2,4", "2,4~t3.jin", "2,4~t3.jin.2", "2,4~t7.jin", "2,4~t7.jin.2", "3,1", "3,1~t7.jin", "3,1~t7.jin.2", "4,1", "CD.DF+4,2", "FLY.4,1", "FLY.4,2", "MCR.4,1", "MCR.4,2", "WS.1,3", "WS.1,3~3", "WS.1,4", "b+2,3", "b+2,4", "b+2,4,2", "b+2,4,4", "b+2,4,4,4", "b+2,4,4,4,4", "b+2,4,4,4,4,2", "b+3,2", "d/b+2,2,3", "d/b+2,2,3~t7.jin", "d/b+2,2,3~t7.jin.2", "d/b+2,3", "d/b+2,3~t7.jin", "d/f+1,3", "d/f+1,4", "d/f+1,4~4", "d/f+1,4~4~t7.jin", "d/f+1,4~t7.jin", "d/f+1,4~t7.jin.2", "d/f+3,2", "db+2,2,3", "db+2,3", "df+1,4", "df+1,4~4", "df+2,4", "f+2,4", "f+3,1", "u+1,3", "u+1,3~t3.jin", "u+1,3~t3.jin.2", "u+1,3~t3.jin.3", "u+1,4", "u+1,4~t3.jin", "u+1,4~t3.jin.2", "u+1,4~t3.jin.3", "u/b+1,3", "u/b+1,3~t3.jin", "u/b+1,3~t3.jin.2", "u/b+1,3~t3.jin.3", "u/b+1,4", "u/b+1,4~t3.jin", "u/b+1,4~t3.jin.2", "u/b+1,4~t3.jin.3", "u/f+1,3", "u/f+1,3~t3.jin", "u/f+1,3~t3.jin.2", "u/f+1,3~t3.jin.3", "u/f+1,4", "u/f+1,4~t3.jin", "u/f+1,4~t3.jin.2", "u/f+1,4~t3.jin.3", "u/f+4,4,1", "ws1,3", "ws1,3~3"];
const B1 = ["1+2,2", "1+2,2~t3.jin", "1,1", "1,1,2", "1,2", "1,2,1", "1,2,2", "1,2~t7.jin", "1,2~t7.jin.2", "2,1", "2,1,2", "2,1,2,2", "2,1,2,2~t3.jin", "2,1,2~t3.jin", "2,1~t3.jin", "2,1~t7.jin", "2,1~t7.jin.2", "2,1~t8.jin", "2,2", "MCR.2,2", "WS.1,1", "WS.1,2", "WS.1,2~t7.jin", "ZEN.1,2", "ZEN.1,2~t7.jin", "ZEN.1,2~t7.jin.2", "b+1+2,1", "b+1+2,1,2", "b+1+2,2", "b+1+2,2,2", "b+1,2", "b+2,1", "b+2,1~t7.jin", "b+2,1~t7.jin.2", "d+1+2,1", "d+1+2,1,2", "d+1+2,2", "d/b+2,2", "d/b+2,2~t7.jin", "d/f+1,2", "d/f+1,2~t3.jin", "db+2,2", "df+2,H.1+2", "u+1,1", "u+1,1~t3.jin", "u+1,1~t3.jin.2", "u+1,1~t3.jin.3", "u+1,2", "u/b+1,1", "u/b+1,1~t3.jin", "u/b+1,1~t3.jin.2", "u/b+1,1~t3.jin.3", "u/b+1,2", "u/f+1,1", "u/f+1,1~t3.jin", "u/f+1,1~t3.jin.2", "u/f+1,1~t3.jin.3", "u/f+1,2", "ws1,2"];
const B2 = ["DVS.4,4", "WS.4,4", "d+3,3", "d+3,3~t7.jin", "d+3,4", "d+3,4,3", "d+3,4~4", "d/f+3,3", "d/f+3,3~t7.jin", "d/f+4,4", "d/f+4,4~t3.jin", "f+3,3", "f+3~3,d/f+3", "f+3~3,d/f+3~t7.jin", "f+4,3", "u+4,4", "u/f+4,3", "u/f+4,3~t3.jin", "u/f+4,4", "u/f+4,4,4", "u/f+4,4,4,4", "u/f+4,4,4,4~t3.jin", "u/f+4,4,4~t3.jin", "u/f+4,4~t3.jin", "ws4,4"];
const B4 = ["1+4,2", "1+4,2,1", "1+4,2,1,4", "1+4,2,4", "1+4,2,d+4", "1,2,3", "1,2,3,4", "1,2,3~t7.jin", "1,2,3~t7.jin.2", "1,2,3~t7.jin.3", "1,2,4", "1,2,4~t7.jin", "1,2,4~t7.jin.2", "1,2,4~t7.jin.3", "1,3,2", "1,3,2,1", "1,3,2,1,4", "1,3,2,1,4~t7.jin", "1,3,2,1,4~t7.jin.2", "1,3,2,1,4~t7.jin.3", "1,3,2,1,4~t7.jin.4", "1,3,2,1~t7.jin", "1,3,2,1~t7.jin.2", "1,3,2,1~t7.jin.3", "1,3,2~t7.jin", "1,3,2~t7.jin.2", "1,3,4", "1,d+3,d+4", "1,d+3,d+4~t7.jin", "1,d+3,d+4~t7.jin.2", "2,1,2,2,3", "2,1,2,2,3,4", "2,1,2,2,3,4,4", "2,1,2,2,3,4,4,1", "2,1,2,2,3,4,4,1,2", "2,1,2,2,3,4,4,1,2,1", "2,1,2,2,3,4,4,3", "2,1,2,2,3,4,4,3,2", "2,1,2,2,3,4~t3.jin", "2,1,2,2,3~t3.jin", "2,1,4", "2,1,4,4", "2,1,4,4,2", "2,1,4,4,2,4", "2,1,4,4,2,4,3", "2,1,4,4,2,4,3,2", "2,1,4,4,2,4,3,2,1", "2,1,4,4,2,4~t3.jin", "2,1,4,4,2~t3.jin", "2,1,4,4~t3.jin", "2,1,4__main", "2,1,4~4", "2,1,4~4~t7.jin", "2,1,4~4~t7.jin.2", "2,1,4~4~t7.jin.3", "2,1,4~t3.jin", "2,1,4~t7.jin", "2,1,4~t7.jin.2", "2,1,4~t7.jin.3", "3,1,2", "3,1,4", "3,1,4~t7.jin", "3,1,4~t7.jin.2", "3,1,4~t7.jin.3", "3,2,4,3,1+4,1,2,1,2", "4,1,2", "4~3,H.1+2", "FLY.4,2,1", "FLY.4,2,1+2", "H.2+3,4", "MCR.4,2,1", "MCR.4,2,1+2", "WS.1,3,2", "WS.1,3,2,1", "WS.1,3,2,1,4", "WS.1,3,2,1,4,2", "b+1+2,2,3", "b+1+2,2,3,4", "b+1+2,2,3,f+4", "b+2,4,2,1", "b+2,4,4,1+2+3", "b+2,4,4,4,4,2,1+4", "b+2,4,4,4,4,2,1+4,1", "b+2,4,4,4,4,2,1+4,1,2", "b+2,4,4,4,4,2,1+4,1,2,1", "b+2,4,4,4,4,2,1+4,1,2,3+4", "b+3+4,2", "b+3+4,2,1", "b+3+4,2,1,4", "d+3+4,1", "d/f+3,2,4", "f+2,3,3,3,2,1,2,3,4,2", "u+1,2+4", "u/b+1,2+4", "u/f+1,2+4", "u/f+2+4,1", "ws1,3,2", "ws1,3,2,1", "ws1,3,2,1,4", "ws1,3,2,1,4,2"];
const B3_VERIFIED_LAST = ["b+2,4", "b+2,4,2", "b+2,4,4,4,4,2", "u+1,3", "u+1,3~t3.jin", "u+1,3~t3.jin.2", "u+1,3~t3.jin.3", "u+1,4", "u+1,4~t3.jin", "u+1,4~t3.jin.2", "u+1,4~t3.jin.3", "u/b+1,3", "u/b+1,3~t3.jin", "u/b+1,3~t3.jin.2", "u/b+1,3~t3.jin.3", "u/b+1,4", "u/b+1,4~t3.jin", "u/b+1,4~t3.jin.2", "u/b+1,4~t3.jin.3", "u/f+1,3", "u/f+1,3~t3.jin", "u/f+1,3~t3.jin.2", "u/f+1,3~t3.jin.3", "u/f+1,4", "u/f+1,4~t3.jin", "u/f+1,4~t3.jin.2", "u/f+1,4~t3.jin.3"];
const VERIFIED_BUTTONS = {"54": 4, "55": 4, "56": 4, "67": 8, "68": 8, "69": 8, "80": 8, "103": 2, "195": 4, "207": 8, "220": 2, "251": 8, "252": 2, "258": 2};

function stepBits(step) {
  const seg = step.split('.').pop();
  let b = 0;
  for (const c of seg) if ('1234'.includes(c)) b |= 1 << (Number(c) - 1);
  return b;
}

test('demonio move/string counts unchanged by the additive plans block; 271 plans total (cumulative)', () => {
  assert.equal(Object.keys(demonio.moves).length, 764);
  assert.equal(demonio.strings.length, 156);
  assert.equal(Object.keys(plans).length, 271); // 59 Batch 1 + 25 Batch 2 + 87 Batch 3 + 100 Batch 4 (cumulative)
});

test('Batch 3 keys are exactly the documented 87', () => {
  assert.equal(B3.length, 87);
  for (const key of B3) assert.ok(plans[key], `Batch 3 key ${key} missing`);
});

test('Batch 3 keys are all present; extra keys are exactly the Batch 1 59 + Batch 2 25 + Batch 4 100 (cumulative)', () => {
  assert.equal(B3.length, 87);
  for (const key of B3) assert.ok(plans[key], `Batch 3 key ${key} missing`);
  const extra = Object.keys(plans).filter((k) => !B3.includes(k));
  assert.equal(extra.length, 184);
  assert.equal(B1.length, 59);
  assert.equal(B2.length, 25);
  assert.equal(B4.length, 100);
  for (const key of B1) assert.ok(extra.includes(key), `Batch 1 key ${key} missing from extra keys`);
  for (const key of B2) assert.ok(extra.includes(key), `Batch 2 key ${key} missing from extra keys`);
  for (const key of B4) assert.ok(extra.includes(key), `Batch 4 key ${key} missing from extra keys`);
  for (const key of extra) assert.ok(B1.includes(key) || B2.includes(key) || B4.includes(key), `unexpected extra key ${key}`);
});

test('Batch 3 verified steps carry rows (button == step bits, throw 0, never row 35 on ground); review/unmapped carry row null; no soft flags', () => {
  for (const key of B3) {
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

test('2,4 flagship: partial — step 1 verified row 220 (standing RP2 row), step 2 unmapped', () => {
  const p = plans['2,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [220, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'unmapped']);
  assert.equal(p.string_status, 'partial');
});

test('3,1 flagship: partial — step 1 verified row 195, step 2 unmapped', () => {
  const p = plans['3,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [195, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'unmapped']);
  assert.equal(p.string_status, 'partial');
});

test('b+2,4 flagship: partial — step 1 unmapped, step 2 verified row 251', () => {
  const p = plans['b+2,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, 251]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'verified']);
  assert.equal(p.string_status, 'partial');
});

test('b+2,4,2 flagship: step 2 verified row 251, last step verified row 252', () => {
  const p = plans['b+2,4,2'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [null, 251, 252]);
  assert.equal(p.string_status, 'partial');
});

test('b+2,4,4,4,4,2 flagship: last step verified row 258', () => {
  const p = plans['b+2,4,4,4,4,2'];
  assert.equal(p.steps.length, 6);
  assert.equal(p.steps[5].row, 258);
  assert.equal(p.steps[5].status, 'verified');
  assert.equal(p.last_step_status, 'verified');
});

test('f+2,4 flagship: step 1 verified row 103, step 2 unmapped', () => {
  const p = plans['f+2,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [103, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'unmapped']);
  assert.equal(p.string_status, 'partial');
});

test('u+1,3 flagship: step 1 unmapped, last step verified row 54 (jump context)', () => {
  const p = plans['u+1,3'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, 54]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'verified']);
  assert.equal(p.jumping_context, true);
});

test('u/f+4,4,1 flagship: steps 1-2 verified rows 80/207, last step unmapped (own row 208 is a throw row)', () => {
  const p = plans['u/f+4,4,1'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [80, 207, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified', 'unmapped']);
  assert.equal(p.string_status, 'partial');
  assert.equal(p.jumping_context, true);
});

test('4,1 flagship: step 1 review (SOFT proxy fail), row null', () => {
  const p = plans['4,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.equal(p.steps[0].status, 'review');
});

test('1,3 flagship: step 1 SUSPENDED-DRIFT (prefix move 1 ROW-CHANGED 41->None), row null', () => {
  const p = plans['1,3'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.equal(p.steps[0].status, 'unmapped');
  assert.ok(p.steps[0].reasons.join(' ').includes('SUSPENDED-DRIFT'), '1,3 step 1 must carry the SUSPENDED-DRIFT reason');
});

test('1,3~3 flagship: unmapped-all (own canonical, NOT a variant of 1)', () => {
  const p = plans['1,3~3'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.equal(p.string_status, 'unmapped-all');
  assert.ok(!('twin_of' in p), '1,3~3 must not be a twin of 1');
  assert.ok(plans['1,3~3~t7.jin'], '1,3~3~t7.jin is the twin');
});

test('1,3~3,d/f+3 flagship: unmapped-all (own canonical, NOT a variant of 1)', () => {
  const p = plans['1,3~3,d/f+3'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null, null]);
  assert.equal(p.string_status, 'unmapped-all');
  assert.ok(!('twin_of' in p), '1,3~3,d/f+3 must not be a twin of 1');
});

test('WS.1,3~3, ws1,3~3, d/f+1,4~4, df+1,4~4 are own canonicals (not variants)', () => {
  for (const key of ['WS.1,3~3', 'ws1,3~3', 'd/f+1,4~4', 'df+1,4~4']) {
    assert.ok(plans[key], `${key} missing`);
    assert.ok(!('twin_of' in plans[key]), `${key} must not be a twin`);
  }
});

test('ZEN.1,3 throw family has NO plan key (Batch 4 carry-forwards retired: Batch 4 now owns them)', () => {
  assert.ok(!plans['ZEN.1,3'], 'ZEN.1,3 must have no plan (throw class)');
  assert.ok(!plans['ZEN.1,3~t7.jin'], 'ZEN.1,3~t7.jin must have no plan');
  assert.ok(!plans['ZEN.1,3~t7.jin.2'], 'ZEN.1,3~t7.jin.2 must have no plan');
  // RETIRED by the Batch 4 lane (test-evolution rule): Batch 3's forward-scope
  // guard asserted 2,1,4~4 and 4~3,H.1+2 had NO plan because they were Batch 4
  // scope. Batch 4 is now filed, so those keys DO have plans — asserted in
  // demonio-batch4-step-plans.test.mjs (2,1,4~4 partial, 4~3,H.1+2 unmapped-all).
  // Retiring the guard is not a content change: every Batch 3 content assertion
  // (its 87 keys, verified steps, flagships) is preserved verbatim.
});

test('verified-last-step Batch 3 keys are exactly the documented 27; review-last is exactly b+2,4,4,4,4', () => {
  assert.equal(B3_VERIFIED_LAST.length, 27);
  for (const key of B3_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B3.filter((k) => !B3_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
  assert.equal(plans['b+2,4,4,4,4'].last_step_status, 'review', 'b+2,4,4,4,4 last step must be review');
  const reviewOthers = B3.filter((k) => k !== 'b+2,4,4,4,4');
  for (const key of reviewOthers) assert.notEqual(plans[key].last_step_status, 'review', `${key} last step unexpectedly review`);
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

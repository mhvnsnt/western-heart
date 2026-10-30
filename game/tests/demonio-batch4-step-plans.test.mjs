/* Demonio Batch 4 step plans (triples/quads/rest — LAST demonio batch, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/DEMONIO-BATCH4-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on demonio Batch 3 (feat/demonio-batch3-step-plans-20261025,
 * PR #1111), which is stacked on Batch 2 (feat/demonio-batch2-step-plans-20261025, PR #1110),
 * which is stacked on Batch 1 (feat/demonio-batch1-step-plans-20261025, PR #1108),
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
 * (button + throw + stance + SOFT) like any jin row, and verifies here for the 2,1
 * family steps. Jin row 35 IS starts-airborne, so the row-35 rejection for ground
 * steps stands (no Batch 4 verified step uses row 35 at all — asserted below).
 * Jin row 216 is a JUMP row (Batch 3 proved it for 1+4,b+1's last step) — NOT king
 * row 216 dash Konvict Kick; no Batch 4 verified step uses row 216 either.
 * Canonicalization correction (carried from Batches 2-3): only a trailing source-variant
 * suffix (~t3.jin, ~t7.jin[.N], ~t8.jin) is stripped. A '~' inside the input is Tekken
 * cancel notation, not a variant marker: "2,1,4~4" and "4~3,H.1+2" are OWN Batch 4
 * canonicals. CORRECTION to Batch 3's parenthetical: 2,1,4~4's button union is
 * {1,2,4} (a TRIPLE: steps 2 / 1 / 4~4), not a quad; 4~3,H.1+2's union is {1,2,3,4}
 * (a quad: steps 4~3 / H.1+2). Both are Batch 4 scope either way.
 * The __main duplicate key "2,1,4__main" is its OWN canonical, NOT a twin of "2,1,4":
 * __main is not a source-variant suffix under the corrected rule, and the __main entry
 * is a distinct record (different damage/anim_ref). Its plan is partial [220, 221, None]
 * — the shared 2,1 prefix rows verify, the __main last step has no T3 row of its own
 * and does NOT inherit row 230 from plain 2,1,4.
 * DEMONIO STRING COVERAGE COMPLETE: 271 canonical comma keys = Batch 1 41 + Batch 2 17
 * + Batch 3 49 + Batch 4 164 (69 triples/quads + 95 rest), uncovered [] extra [].
 * Rest keys (95) are CSV-audited only, never planned — planning them needs engine
 * support for non-attack prefix steps (future work, named, not guessed).
 * Rules asserted here (all data-level, no THREE needed):
 *   1. demonio.json still has 764 moves / 156 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 271 keys (59 Batch 1 + 25 Batch 2 + 87 Batch 3 +
 *      100 Batch 4: 68 planned canonicals + 32 twins). Batch 1 keys are asserted in the
 *      cumulative Batch 1 test; Batch 2 keys in the cumulative Batch 2 test; Batch 3
 *      keys in the cumulative Batch 3 test.
 *   3. Batch 4 verified steps always carry a row whose jin hit_frames button equals
 *      the step bits and whose throw flag is 0; no Batch 4 verified step uses row 35
 *      or row 216; review/unmapped steps carry row null. No Batch 4 step carries a soft
 *      flag (the one Job 3 fill, row 114, is exact+FULL with the SOFT proxy passed —
 *      it is a verified fill, not a soft fill).
 *   4. 2,1,4 flagship: verified-all rows 220/221/230.
 *   5. 2,1,4,4 flagship: verified-all rows 220/221/230/114 — step 4 is the ONE Job 3
 *      fill (gate candidate row 231 failed the button gate: button 12 LK3+RK4 chord row
 *      for a single-RK4 step; fill row 114 exact+FULL, SOFT proxy passed).
 *   6. 2,1,4,4,2,4 flagship: verified-all rows 220/221/230/114/232/233.
 *   7. 2,1,2,2,3 flagship: verified-all rows 220/221/222/223/224.
 *   8. 2,1,4__main flagship: partial rows 220/221/None, own canonical, NOT a twin.
 *   9. 2,1,4~4 flagship: partial rows 220/221/None (last step has no candidate: the
 *      2,1,4~4 move itself carries t3_row None, T8-sourced).
 *  10. 4~3,H.1+2 flagship: unmapped-all (quarantined-only on main, T8 Devil Jin
 *      sourced, no T3 row — clips come from #988 Step 2, never from a T3 row recorded
 *      as correct).
 *  11. 1,2,3 flagship: step 1 SUSPENDED-DRIFT (prefix move 1 ROW-CHANGED 41->None),
 *      row null, never wired on stale data (stale row 41 is starts-airborne).
 *  12. u+1,2+4 / u/b+1,2+4 flagships: last steps verified rows 170/172 (jump context,
 *      SOFT waived per Batch 1 precedent; button 10 LP1+RK4 chord).
 *  13. The 95 rest canonicals + the throw triple-quad u/f+3+4,H.1+2 have NO plan key.
 *  14. The verified-last-step Batch 4 keys are exactly the 25 listed below, and the
 *      review-last-step Batch 4 keys are exactly the 10 listed below; verified rows
 *      carry the step buttons in the repo Jin hit_frames.json.
 *  15. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Run: node --test game/tests/demonio-batch4-step-plans.test.mjs   (from repo root)
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
const B4 = ["1+4,2", "1+4,2,1", "1+4,2,1,4", "1+4,2,4", "1+4,2,d+4", "1,2,3", "1,2,3,4", "1,2,3~t7.jin", "1,2,3~t7.jin.2", "1,2,3~t7.jin.3", "1,2,4", "1,2,4~t7.jin", "1,2,4~t7.jin.2", "1,2,4~t7.jin.3", "1,3,2", "1,3,2,1", "1,3,2,1,4", "1,3,2,1,4~t7.jin", "1,3,2,1,4~t7.jin.2", "1,3,2,1,4~t7.jin.3", "1,3,2,1,4~t7.jin.4", "1,3,2,1~t7.jin", "1,3,2,1~t7.jin.2", "1,3,2,1~t7.jin.3", "1,3,2~t7.jin", "1,3,2~t7.jin.2", "1,3,4", "1,d+3,d+4", "1,d+3,d+4~t7.jin", "1,d+3,d+4~t7.jin.2", "2,1,2,2,3", "2,1,2,2,3,4", "2,1,2,2,3,4,4", "2,1,2,2,3,4,4,1", "2,1,2,2,3,4,4,1,2", "2,1,2,2,3,4,4,1,2,1", "2,1,2,2,3,4,4,3", "2,1,2,2,3,4,4,3,2", "2,1,2,2,3,4~t3.jin", "2,1,2,2,3~t3.jin", "2,1,4", "2,1,4,4", "2,1,4,4,2", "2,1,4,4,2,4", "2,1,4,4,2,4,3", "2,1,4,4,2,4,3,2", "2,1,4,4,2,4,3,2,1", "2,1,4,4,2,4~t3.jin", "2,1,4,4,2~t3.jin", "2,1,4,4~t3.jin", "2,1,4__main", "2,1,4~4", "2,1,4~4~t7.jin", "2,1,4~4~t7.jin.2", "2,1,4~4~t7.jin.3", "2,1,4~t3.jin", "2,1,4~t7.jin", "2,1,4~t7.jin.2", "2,1,4~t7.jin.3", "3,1,2", "3,1,4", "3,1,4~t7.jin", "3,1,4~t7.jin.2", "3,1,4~t7.jin.3", "3,2,4,3,1+4,1,2,1,2", "4,1,2", "4~3,H.1+2", "FLY.4,2,1", "FLY.4,2,1+2", "H.2+3,4", "MCR.4,2,1", "MCR.4,2,1+2", "WS.1,3,2", "WS.1,3,2,1", "WS.1,3,2,1,4", "WS.1,3,2,1,4,2", "b+1+2,2,3", "b+1+2,2,3,4", "b+1+2,2,3,f+4", "b+2,4,2,1", "b+2,4,4,1+2+3", "b+2,4,4,4,4,2,1+4", "b+2,4,4,4,4,2,1+4,1", "b+2,4,4,4,4,2,1+4,1,2", "b+2,4,4,4,4,2,1+4,1,2,1", "b+2,4,4,4,4,2,1+4,1,2,3+4", "b+3+4,2", "b+3+4,2,1", "b+3+4,2,1,4", "d+3+4,1", "d/f+3,2,4", "f+2,3,3,3,2,1,2,3,4,2", "u+1,2+4", "u/b+1,2+4", "u/f+1,2+4", "u/f+2+4,1", "ws1,3,2", "ws1,3,2,1", "ws1,3,2,1,4", "ws1,3,2,1,4,2"];
const B4_VERIFIED_LAST = ["1+4,2", "2,1,2,2,3", "2,1,2,2,3,4,4", "2,1,2,2,3,4,4,1", "2,1,2,2,3,4,4,1,2", "2,1,2,2,3,4,4,3", "2,1,2,2,3,4,4,3,2", "2,1,2,2,3~t3.jin", "2,1,4", "2,1,4,4", "2,1,4,4,2", "2,1,4,4,2,4", "2,1,4,4,2,4~t3.jin", "2,1,4,4,2~t3.jin", "2,1,4,4~t3.jin", "2,1,4~t3.jin", "2,1,4~t7.jin", "2,1,4~t7.jin.2", "2,1,4~t7.jin.3", "4,1,2", "b+1+2,2,3", "b+2,4,4,4,4,2,1+4", "b+3+4,2", "u+1,2+4", "u/b+1,2+4"];
const B4_REVIEW_LAST = ["1+4,2,1,4", "2,1,2,2,3,4", "2,1,2,2,3,4~t3.jin", "2,1,4,4,2,4,3", "2,1,4,4,2,4,3,2", "b+1+2,2,3,4", "b+1+2,2,3,f+4", "b+2,4,2,1", "b+2,4,4,4,4,2,1+4,1,2", "b+3+4,2,1,4"];
const B4_REST = ["1+4,2,1,d/b", "1,3,B", "1,3,F", "1,b", "1,d/b", "3,1,F", "3,1,f,F", "FLY.4,2,1,u/f", "H.f,F+1+2", "MCR.4,2,1,u/f", "R.f,n,d,d/f+1+2", "R.f,n,d,d/f+1+2,3", "R.f,n,d,d/f+1+2,3,1", "R.f,n,d,d/f+1+2,D/F", "R.f,n,d,d/f+4,3+4", "SS.2,U", "WALL.b,b,u/b", "WR.f,f,F", "WS.1,2,F", "b+1,2,B", "b+3,F", "b,2", "b,4", "b,f+1+2", "b,f+1+2,2", "b,f+2", "b,f+2,1", "b,f+2,1,2", "b,f+2,1,4", "b,f+2,1,4,H.1+2", "b,f+2,1,df+2", "b,f+2,3", "b,f+2,3,F", "d,4", "d,4,1", "d,d/b,b+1+3", "d,d/b,b+1+3,1", "d,d/b,d,d/b+1+2", "d/b,n,f+2", "d/b,n,f+2,1", "d/f+1,2,f,F", "d/f+3,2,4,U", "d/f+3,3,B", "d/f+3,3,F", "f+1+2,B", "f+4,3,U", "f+4,F", "f,F+2", "f,F+3", "f,F+3,1", "f,F+3,1,3", "f,F+3,1,3,2", "f,F+3,1,3,2,1", "f,F+3,1,3,2,1,4", "f,F+4", "f,b,d/b,d,d/f,f+1+2", "f,f+1+2", "f,f+3+4", "f,f+3,1,2", "f,f+3,1,4", "f,f+3,1,d/b+1+2", "f,f+3,1,f,F", "f,f,F", "f,f,F+3", "f,f,n,2", "f,f,n,2,1,2,2,3,4,4,1,2,1", "f,hcf+1+2", "f,n,d,D/F+1", "f,n,d,d/f", "f,n,d,d/f+1+2", "f,n,d,d/f+1+2,H.1+2", "f,n,d,d/f+1,3", "f,n,d,d/f+1,4", "f,n,d,d/f+1,u/f", "f,n,d,d/f+1:u/f", "f,n,d,d/f+2", "f,n,d,d/f+3", "f,n,d,d/f+4", "f,n,d,d/f+4,1+2", "f,n,d,d/f+4,3+4", "f,n,d,d/f+4,4", "f,n,d,d/f+4,H.3", "f,n,d,d/f,u/f", "f,n,d,d/f:1", "f,n,d,d/f:2", "f,n,d,df", "f,n,d,df,UF", "n,b,n,f+2", "n,b,n,f+2,1", "n,d/f,n,d/f+1", "n,f,n,f+1+2", "n,f,n,f+1+2,1", "u+4,U", "u/b+1+2,b,b", "uf,n,4"];
const VERIFIED_BUTTONS = {"103": 2, "114": 8, "170": 10, "172": 10, "186": 2, "195": 4, "196": 4, "220": 2, "221": 1, "222": 2, "223": 2, "224": 4, "226": 8, "227": 1, "228": 2, "230": 8, "232": 2, "233": 8, "237": 4, "238": 2, "239": 2, "251": 8, "252": 2, "258": 2, "259": 9, "94": 2};

function stepBits(step) {
  const seg = step.split('.').pop();
  let b = 0;
  for (const c of seg) if ('1234'.includes(c)) b |= 1 << (Number(c) - 1);
  return b;
}

test('demonio move/string counts unchanged by the additive plans block; 271 plans total', () => {
  assert.equal(Object.keys(demonio.moves).length, 764);
  assert.equal(demonio.strings.length, 156);
  assert.equal(Object.keys(plans).length, 271);
});

test('Batch 4 keys are exactly the documented 100', () => {
  assert.equal(B4.length, 100);
  for (const key of B4) assert.ok(plans[key], `Batch 4 key ${key} missing`);
});

test('Batch 4 verified steps carry rows (button == step bits, throw 0, never row 35 or 216); review/unmapped carry row null; no soft flags', () => {
  for (const key of B4) {
    for (const s of plans[key].steps) {
      assert.ok(!('soft' in s) || s.soft !== true, `${key} step ${s.step} carries a soft flag`);
      if (s.status === 'verified') {
        assert.notEqual(s.row, null, `${key} step ${s.step} verified but row null`);
        assert.notEqual(s.row, 35, `${key} step ${s.step} verified on starts-airborne row 35`);
        assert.notEqual(s.row, 216, `${key} step ${s.step} verified on jin jump row 216`);
        assert.equal(hf[String(s.row)][5], stepBits(s.step), `${key} step ${s.step} row ${s.row} button mismatch`);
        assert.equal(hf[String(s.row)][5], VERIFIED_BUTTONS[String(s.row)], `${key} step ${s.step} row ${s.row} button mismatch (map)`);
        assert.equal(hf[String(s.row)][4], 0, `${key} step ${s.step} row ${s.row} is a throw row`);
      } else {
        assert.equal(s.row, null, `${key} step ${s.step} ${s.status} must not carry a playable row`);
      }
    }
  }
});

test('2,1,4 flagship: verified-all rows 220/221/230', () => {
  const p = plans['2,1,4'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [220, 221, 230]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('2,1,4,4 flagship: verified-all rows 220/221/230/114 (step 4 is the Job 3 fill; gate candidate 231 failed the button gate)', () => {
  const p = plans['2,1,4,4'];
  assert.equal(p.steps.length, 4);
  assert.deepEqual(p.steps.map((s) => s.row), [220, 221, 230, 114]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified', 'verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
  assert.equal(p.steps[3].candidate_row, 231);
});

test('2,1,4,4,2,4 flagship: verified-all rows 220/221/230/114/232/233', () => {
  const p = plans['2,1,4,4,2,4'];
  assert.equal(p.steps.length, 6);
  assert.deepEqual(p.steps.map((s) => s.row), [220, 221, 230, 114, 232, 233]);
  assert.equal(p.string_status, 'verified-all');
});

test('2,1,2,2,3 flagship: verified-all rows 220/221/222/223/224', () => {
  const p = plans['2,1,2,2,3'];
  assert.equal(p.steps.length, 5);
  assert.deepEqual(p.steps.map((s) => s.row), [220, 221, 222, 223, 224]);
  assert.equal(p.string_status, 'verified-all');
});

test('2,1,4__main flagship: partial rows 220/221/None, own canonical, NOT a twin of 2,1,4', () => {
  const p = plans['2,1,4__main'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [220, 221, null]);
  assert.equal(p.string_status, 'partial');
  assert.ok(!('twin_of' in p), '2,1,4__main must not be a twin of 2,1,4');
});

test('2,1,4~4 flagship: partial rows 220/221/None (last step has no candidate: T8-sourced move, t3_row None)', () => {
  const p = plans['2,1,4~4'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [220, 221, null]);
  assert.equal(p.string_status, 'partial');
  assert.ok(!('twin_of' in p), '2,1,4~4 must not be a twin of 2,1,4');
});

test('4~3,H.1+2 flagship: unmapped-all (quarantined-only, T8 Devil Jin sourced, no T3 row)', () => {
  const p = plans['4~3,H.1+2'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.equal(p.string_status, 'unmapped-all');
  assert.ok(!('twin_of' in p), '4~3,H.1+2 must not be a twin');
});

test('1,2,3 flagship: step 1 SUSPENDED-DRIFT (prefix move 1 ROW-CHANGED 41->None), row null', () => {
  const p = plans['1,2,3'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null, null]);
  assert.equal(p.steps[0].status, 'unmapped');
  assert.ok(p.steps[0].reasons.join(' ').includes('SUSPENDED-DRIFT'), '1,2,3 step 1 must carry the SUSPENDED-DRIFT reason');
});

test('u+1,2+4 / u/b+1,2+4 flagships: last steps verified rows 170/172 (jump context, SOFT waived)', () => {
  const a = plans['u+1,2+4'];
  assert.deepEqual(a.steps.map((s) => s.row), [null, 170]);
  assert.equal(a.jumping_context, true);
  const b = plans['u/b+1,2+4'];
  assert.deepEqual(b.steps.map((s) => s.row), [null, 172]);
  assert.equal(b.jumping_context, true);
});

test('rest canonicals and the throw triple-quad have NO plan key', () => {
  assert.equal(B4_REST.length, 95);
  for (const key of B4_REST) assert.ok(!plans[key], `${key} must have no plan (rest key)`);
  assert.ok(!plans['u/f+3+4,H.1+2'], 'u/f+3+4,H.1+2 must have no plan (throw class)');
});

test('verified-last-step Batch 4 keys are exactly the documented 25; review-last exactly the 10', () => {
  assert.equal(B4_VERIFIED_LAST.length, 25);
  for (const key of B4_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B4.filter((k) => !B4_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
  assert.equal(B4_REVIEW_LAST.length, 10);
  for (const key of B4_REVIEW_LAST) assert.equal(plans[key].last_step_status, 'review', `${key} last step not review`);
  const reviewOthers = B4.filter((k) => !B4_REVIEW_LAST.includes(k));
  for (const key of reviewOthers) assert.notEqual(plans[key].last_step_status, 'review', `${key} last step unexpectedly review`);
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

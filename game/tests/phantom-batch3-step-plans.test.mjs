/* Phantom Batch 3 step plans (mixed-pair strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/PHANTOM-BATCH3-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on phantom Batch 2 (#1122,
 * feat/phantom-batch2-step-plans-20261025), which stacks on phantom Batch 1
 * (#1121, feat/phantom-batch1-step-plans-20261025), which stacks on #1096
 * (feat/batch1-step-plans-pantera-20261024, the step-playback engine). It does
 * NOT stack on the Pantera plan branches (#1099/#1101/#1102), the burger plan
 * branches (#1103/#1104/#1105/#1107), the demonio plan branches
 * (#1108/#1110/#1111/#1112), the diablo plan branches (#1113/#1114/#1115/#1116),
 * or the kinpo plan branches (#1117/#1118/#1119/#1120): phantom.json plans do
 * not conflict with pantera.json, burger.json, demonio.json, diablo.json, or
 * kinpo.json plans.
 * It does NOT include #1097's Pantera Batch 1 follow-up fills (Pantera-specific,
 * and its row-49 SOFT fill is still unapproved); no SOFT fill is inherited here.
 * This PR does not touch `fighter.js`: #1096's merge onto post-#1078 main must
 * reconcile #1078's `fighter.js` changes with #1096's engine branch, and that
 * belongs to #1096's merge, not this PR.
 * Bank (verified, not assumed): phantom's T3 bank is YOSHIMITSU (t3_source
 * yoshimitsu, t3_bank moveset_yoshimitsu.json, on BOTH the Batch 2 branch and
 * main; t3/ directory listing; Job 1 bank yoshimitsu (215 rows); Job 2 phantom
 * entries all bank yoshimitsu (1019); Job 4 yoshimitsu candidates (47)). Bank
 * resolution, documented not assumed: phantom's T7/T8 base IS Yoshimitsu
 * (tekken_base Yoshimitsu, merge_sources t8/t7/t3 yoshimitsu) — this bank is
 * NATIVE, not a fallback (contrast burger Bob -> bryan, kinpo Asuka -> jin).
 * The pack dir does NOT differ from the moveset bank name here (unlike
 * diablo's heihachi/heihachi_on_jin split).
 * Yoshimitsu-bank rules, per-bank evidence (never a cross-bank blanket ban):
 * rows 35 and 220 do NOT EXIST in this bank (absent from hit_frames AND Job 1)
 * — no row-35/row-220 rule applies at all; row 216 is a STANDING LP1 row here
 * (hit_frames [11,11,26,1042,0,1], Job 1 standing) — NOT king row 216's dash
 * Konvict Kick, NOT jin row 216's jump row; row 243 is a CHORD row (button 9
 * = LP1+RK4) — it fails every single-button gate. Phantom's own RP2 move 2
 * carries t3_row 307 on the Batch 2 branch and is ROW-CHANGED on current main
 * (2: 307->None), so the three Batch 3 steps with prefix 2 (2,2,4; 2,3; 2,d+3
 * step 1s) are SUSPENDED-DRIFT; phantom's own RK4 move 4 carries t3_row 243
 * and is ROW-CHANGED on current main (4: 243->None), so both Batch 3 steps
 * with prefix 4 (4,4,2; 4,4,2,2 step 1s) are SUSPENDED-DRIFT. The other
 * row-changed moves (1, 1_r62, u+1,1~t3.yoshimitsu.2) are NOT Batch 3 step
 * prefixes.
 * Canonicalization is the CORRECTED rule (demonio Batch 2 finding): strip ONLY
 * a trailing ~t[378].[a-z]+(.N)?$ source-variant suffix; input-~ is Tekken
 * cancel notation, part of the move. Phantom Batch 3 contains ZERO input-~
 * canonicals — the file's old-vs-corrected diffs (3~4,U; 4,4,2,2,1,~1;
 * 4,4,2,2,NSS.1,~1) are all outside Batch 3 scope (rest key with a buttonless
 * U step; triples with union {1,2,4}). Spelling quirks kept: d/f+3,1 vs
 * df+3,1; d/f+1,4 vs df+1,4; WS.3,2 vs ws3,2; B+1 vs b+1 families are
 * distinct canonicals, never merged.
 * Rules asserted here (all data-level, no THREE needed):
 *   1. phantom.json still has 1019 moves / 191 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 320 keys (186 Batch 1 + 49 Batch 2 +
 *      85 Batch 3: 48 planned canonicals + 37 twins).
 *   3. Batch 3 verified steps always carry a row whose yoshimitsu hit_frames
 *      button equals the step bits and whose throw flag is 0; verified rows
 *      always exist in the yoshimitsu hit_frames (rows 35/220 do not exist in
 *      this bank and can never be wired); review/unmapped steps carry row
 *      null. No Batch 3 step carries a soft flag (Batch 3 wires zero Job 3
 *      fills — all Job 3 candidates are ROW-ONLY or soft — and zero SOFT fills).
 *   4. u/f+1,3 flagship: verified-all on rows 66/74 (jump context, SOFT waived).
 *   5. u/b+1,4 flagship: verified-all on rows 55/90 (jump context, SOFT waived).
 *   6. 3,1 flagship: partial, step 1 verified row 123 (standing LK3).
 *   7. d/f+1,4 flagship: partial, step 1 verified row 223 (crouch context,
 *      GATE-NOTE: standing row for a crouch step, demonio Batch 1 precedent).
 *   8. f+4,4,2 flagship: partial, step 3 verified row 301 (standing RP2).
 *   9. 2,3 flagship: step 1 SUSPENDED-DRIFT (prefix move 2 ROW-CHANGED
 *      307->None), row null, never wired on stale data.
 *  10. 4,4,2 flagship: step 1 SUSPENDED-DRIFT (prefix move 4 ROW-CHANGED
 *      243->None), row null, never wired on stale data.
 *  11. The verified-last-step Batch 3 keys are exactly the documented 26.
 *  12. The review-last-step Batch 3 keys are exactly the documented 4.
 *  13. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Run: node --test game/tests/phantom-batch3-step-plans.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const phantom = JSON.parse(readFileSync(join(ROOT, 'game/assets/movesets/phantom.json'), 'utf8'));
const fighterSrc = readFileSync(join(ROOT, 'game/js/fighter.js'), 'utf8');
const hfPath = join(ROOT, 'game/assets/anim/t3/yoshimitsu/hit_frames.json');
const hf = JSON.parse(readFileSync(hfPath, 'utf8')).rows;

const plans = phantom.string_step_plans.plans;
const B3 = ["1+3,1", "1+3,1~t3.yoshimitsu", "1+3,1~t3.yoshimitsu.2", "2,2,4", "2,3", "2,3~t7.yoshimitsu", "2,3~t7.yoshimitsu.2", "2,d+3", "2,d+3~t7.yoshimitsu", "2,d+3~t7.yoshimitsu.2", "3,1", "3,1~t3.yoshimitsu", "3,2", "3,NSS.1", "4,4,2", "4,4,2,2", "BT.1,3", "BT.1,3~t7.yoshimitsu", "BT.1,3~t7.yoshimitsu.2", "DGF.2,4", "NSS.d/f+3,1", "NSS.d/f+3,1~t7.yoshimitsu", "WS.1,1,b+3", "WS.1,1,b+4", "WS.3,2", "WS.3,2~t7.yoshimitsu", "b+1,1,db+3", "b+1,1,db+3,3", "b+1,d/b+3", "b+1,d/b+3,d/b+3", "b+1,d/b+3,d/b+3,d/b+3", "b+2,3", "d+1+4,B+1", "d+1+4,B+1,1", "d+1+4,B+1,1,1", "d+1+4,B+1,1,1,1", "d+1+4,B+1,1,1,1,1", "d+1+4,B+1,1,1,1,1~t7.yoshimitsu", "d+1+4,B+1,1,1,1~t7.yoshimitsu", "d+1+4,B+1,1,1~t7.yoshimitsu", "d+1+4,B+1,1~t7.yoshimitsu", "d+1+4,B+1~t7.yoshimitsu", "d+1+4,b+1", "d+1+4,b+1,b+1", "d+1+4,b+1,b+1,b+1", "d+1+4,b+1,b+1,b+1,b+1", "d+1+4,b+1,b+1,b+1,b+1,b+1", "d+2,2,2+3", "d+2,2,2+3~t7.yoshimitsu", "d/f+1,4", "d/f+1,4~t7.yoshimitsu", "d/f+3,1", "d/f+3,1~t7.yoshimitsu", "df+1,4", "df+3,1", "df+3,NSS.1", "f+4,1", "f+4,4,2", "f+4,4,2,2", "f+4,4,2,2,4", "u+1,3", "u+1,3~t3.yoshimitsu", "u+1,3~t3.yoshimitsu.2", "u+1,3~t3.yoshimitsu.3", "u+1,4", "u+1,4~t3.yoshimitsu", "u+1,4~t3.yoshimitsu.2", "u+1,4~t3.yoshimitsu.3", "u/b+1,3", "u/b+1,3~t3.yoshimitsu", "u/b+1,3~t3.yoshimitsu.2", "u/b+1,3~t3.yoshimitsu.3", "u/b+1,4", "u/b+1,4~t3.yoshimitsu", "u/b+1,4~t3.yoshimitsu.2", "u/b+1,4~t3.yoshimitsu.3", "u/f+1,3", "u/f+1,3~t3.yoshimitsu", "u/f+1,3~t3.yoshimitsu.2", "u/f+1,3~t3.yoshimitsu.3", "u/f+1,4", "u/f+1,4~t3.yoshimitsu", "u/f+1,4~t3.yoshimitsu.2", "u/f+1,4~t3.yoshimitsu.3", "ws3,2"];
const B1 = ["1+2,2", "1+2,2,1", "1,1", "1,1~t3.yoshimitsu", "1,1~t7.yoshimitsu", "1,1~t7.yoshimitsu.2", "1,NSS.1", "1,d/b+2", "1,d/b+2,d/b+2", "1,d/b+2,d/b+2,d/b+2", "1,d/b+2,d/b+2,d/b+2,d/b+2", "2,1", "2,1~t3.yoshimitsu", "2,1~t7.yoshimitsu", "2,1~t7.yoshimitsu.2", "2,2", "2,2,1+2", "2,2~t7.yoshimitsu", "2,2~t7.yoshimitsu.2", "2,2~t8.yoshimitsu", "2,NSS.1", "BT.1,2", "BT.1,2~t7.yoshimitsu", "BT.1,2~t7.yoshimitsu.2", "BT.2,D/B+2,2", "BT.2,D/B+2,2,2", "BT.2,D/B+2,2,2,2", "BT.2,D/B+2,2,2,2,2", "BT.2,d/b+2", "D/B+2,2", "D/B+2,2,2", "D/B+2,2,2,2", "D/B+2,2,2,2,2", "D/B+2,2,2,2,2,2", "INS.2,D/B+2", "INS.2,D/B+2,2", "INS.2,D/B+2,2,2", "INS.2,D/B+2,2,2,2", "KIN.1,1", "KIN.1,1~t7.yoshimitsu", "KIN.1,1~t7.yoshimitsu.2", "KIN.1,NSS.1", "KIN.2,1+2", "KIN.2,1+2*", "KIN.2,1+2*~t7.yoshimitsu", "KIN.2,1+2~t7.yoshimitsu", "KIN.2,1+2~t7.yoshimitsu.2", "KIN.2,NSS.1+2", "KIN.2,NSS.1+2*", "KIN.b+2,1", "KIN.b+2,1~t7.yoshimitsu", "KIN.b+2,1~t7.yoshimitsu.2", "NSS.1+2,1", "NSS.1,2", "NSS.1,2,1", "NSS.1,2,1~t7.yoshimitsu", "NSS.1,2,1~t7.yoshimitsu.2", "NSS.1,2~t7.yoshimitsu", "NSS.2,1", "NSS.2,1~t7.yoshimitsu", "NSS.FC.DF+1,2", "NSS.b+2,2", "NSS.b+2,2~t7.yoshimitsu", "NSS.d+2,1", "NSS.d/f+1+2,2", "NSS.d/f+1+2,2~t7.yoshimitsu", "NSS.u/b+1+2,1", "NSS.u/b+1+2,1+2", "WS.1,1", "WS.1,1,1", "WS.1,1,1,1", "WS.1,2", "WS.1,2,D/B+2", "WS.1,2,D/B+2,2", "WS.1,2,D/B+2,2,2", "WS.1,2,D/B+2,2,2,2", "WS.1,2,D/B+2,2,2,2,2", "WS.1,2,D/B+2,2,2,2,2,2", "WS.1,2~t7.yoshimitsu", "WS.2,1", "WS.2,1~t7.yoshimitsu", "b+1,1", "b+1,1,1", "b+1,1,1,1", "b+1,1,1,1,1", "b+1,1,1,1,1,1", "b+1,1,1,1,1,1~t3.yoshimitsu", "b+1,1,1,1,1,1~t7.yoshimitsu", "b+1,1,1,1,1~t3.yoshimitsu", "b+1,1,1,1,1~t7.yoshimitsu", "b+1,1,1,1~t3.yoshimitsu", "b+1,1,1,1~t7.yoshimitsu", "b+1,1,1~t3.yoshimitsu", "b+1,1,1~t7.yoshimitsu", "b+1,1~t3.yoshimitsu", "b+1,1~t3.yoshimitsu.2", "b+1,1~t7.yoshimitsu", "b+2,1", "b+2,1+2", "b+2,1,1+2", "b+2,1~t7.yoshimitsu", "b+2,1~t7.yoshimitsu.2", "b+2,2", "b+2,2~t7.yoshimitsu", "b+2,2~t7.yoshimitsu.2", "b+2,NSS.1", "b+2,NSS.2", "d+2,1", "d+2,1~t7.yoshimitsu", "d+2,1~t7.yoshimitsu.2", "d+2,2", "d+2,2,1", "d+2,2,1~t7.yoshimitsu", "d+2,2,1~t7.yoshimitsu.2", "d+2,2,1~t7.yoshimitsu.3", "d+2,2,2", "d+2,2,NSS.1", "d+2,2,NSS.d+1", "d+2,2,d+1", "d+2,2,d+1~t7.yoshimitsu", "d+2,2,d+1~t7.yoshimitsu.2", "d+2,2,d+1~t7.yoshimitsu.3", "d+2,NSS.1", "d/b+1,1", "d/b+1,1~t3.yoshimitsu", "d/b+1,1~t7.yoshimitsu", "d/f+1+2,2", "d/f+1+2,2~t7.yoshimitsu", "d/f+1,1", "d/f+1,1,1", "d/f+1,1,1,1", "d/f+1,1,1,1~t3.yoshimitsu", "d/f+1,1,1~t3.yoshimitsu", "d/f+1,1~t3.yoshimitsu", "d/f+1,2", "d/f+1,2~t3.yoshimitsu", "d/f+1,2~t7.yoshimitsu", "d/f+1,2~t7.yoshimitsu.2", "db+1,2", "db+2,2", "db+2,2,2", "db+2,2,2,2", "db+2,2,2,2,2", "db+2,2,2,2,2,2", "df+1,2", "df+1,2,1", "df+1,2,NSS.1", "df+1,2,db+2", "f+2,1", "f+2,D/B+2", "f+2,D/B+2,2", "f+2,D/B+2,2,2", "f+2,D/B+2,2,2,2", "f+2,D/B+2,2,2,2,2", "f+2,D/B+2,2,2,2,2,2", "f+2,NSS.1", "f+2,d/b+2", "f+2,db+2", "u+1,1", "u+1,1~t3.yoshimitsu", "u+1,1~t3.yoshimitsu.2", "u+1,1~t3.yoshimitsu.3", "u+1,2", "u/b+1+2,1+2", "u/b+1,1", "u/b+1,1~t3.yoshimitsu", "u/b+1,1~t3.yoshimitsu.2", "u/b+1,1~t3.yoshimitsu.3", "u/b+1,2", "u/f+1+2,b+1", "u/f+1,1", "u/f+1,1~t3.yoshimitsu", "u/f+1,1~t3.yoshimitsu.2", "u/f+1,1~t3.yoshimitsu.3", "u/f+1,2", "uf+1,1", "uf+1,NSS.1", "ws1,1", "ws1,1,1", "ws1,1,1,1", "ws1,2", "ws1,2,1", "ws1,2,db+2", "ws2,1", "ws2,NSS.1", "ws2,NSS.1,2"];
const B2 = ["4,4", "4,4,4", "4,4,4~t7.yoshimitsu", "4,4~t7.yoshimitsu", "D/B+3,3", "D/B+3,3,3", "D/B+3,3,3,3", "D/B+3,3,3,3,3", "D/B+3,3,3,3,3,3", "IND.3,3+4", "INS.3,3+4", "INS.3,3+4~t7.yoshimitsu", "KIN.4,3+4", "SS.4,3+4", "b+3+4,b+3+4", "b+3+4,b+3+4,b+3+4", "b+3+4,b+3+4,b+3+4,b+3+4", "b+3+4,b+3+4,b+3+4,b+3+4,b+3+4", "b+3,3", "b+3,3,3", "b+3,3,3,3", "b+3,3,3,3,3", "b+3,3,3,3,3,3", "d/b+3,d/b+3", "d/b+3,d/b+3,4", "d/b+3,d/b+3,d/b+3", "d/b+3,d/b+3,d/b+3,d/b+3", "db+3,3", "db+3,3,3", "db+3,3,3,3", "db+3,3,3,3,3", "db+3,3,3,3,3,3", "db+3,3,3,3,3,4", "f+3+4,4", "f+3,3", "f+3,3,d+3+4", "f+3,3~t7.yoshimitsu", "f+3,4", "f+3,4~t7.yoshimitsu", "f+3,4~t7.yoshimitsu.2", "f+4,3", "f+4,4", "f+4,4,4", "u/f+3+4,3+4", "u/f+3+4,3+4~t7.yoshimitsu", "u/f+3+4,u+3+4", "u/f+3+4,u+3+4~t7.yoshimitsu", "uf+3+4,3", "uf+3+4,3+4"];
const B3_VERIFIED_LAST = ["b+2,3", "f+4,4,2", "u+1,3", "u+1,3~t3.yoshimitsu", "u+1,3~t3.yoshimitsu.2", "u+1,3~t3.yoshimitsu.3", "u+1,4", "u+1,4~t3.yoshimitsu", "u+1,4~t3.yoshimitsu.2", "u+1,4~t3.yoshimitsu.3", "u/b+1,3", "u/b+1,3~t3.yoshimitsu", "u/b+1,3~t3.yoshimitsu.2", "u/b+1,3~t3.yoshimitsu.3", "u/b+1,4", "u/b+1,4~t3.yoshimitsu", "u/b+1,4~t3.yoshimitsu.2", "u/b+1,4~t3.yoshimitsu.3", "u/f+1,3", "u/f+1,3~t3.yoshimitsu", "u/f+1,3~t3.yoshimitsu.2", "u/f+1,3~t3.yoshimitsu.3", "u/f+1,4", "u/f+1,4~t3.yoshimitsu", "u/f+1,4~t3.yoshimitsu.2", "u/f+1,4~t3.yoshimitsu.3"];
const B3_REVIEW_LAST = ["b+1,d/b+3", "b+1,d/b+3,d/b+3", "f+4,4,2,2", "f+4,4,2,2,4"];
const VERIFIED_BUTTONS = {"55": 1, "66": 1, "73": 4, "74": 4, "75": 4, "88": 8, "89": 8, "90": 8, "123": 4, "173": 4, "223": 1, "301": 2};

function stepBits(step) {
  const seg = step.split('.').pop();
  let b = 0;
  for (const c of seg) if ('1234'.includes(c)) b |= 1 << (Number(c) - 1);
  return b;
}

test('phantom move/string counts unchanged by the additive plans block', () => {
  assert.equal(Object.keys(phantom.moves).length, 1019);
  assert.equal(phantom.strings.length, 191);
  assert.equal(Object.keys(plans).length, 320);
});

test('Batch 3 keys are exactly the documented 85; complement is exactly Batches 1 + 2', () => {
  assert.equal(B3.length, 85);
  for (const key of B3) assert.ok(plans[key], `Batch 3 key ${key} missing`);
  const extra = Object.keys(plans).filter((k) => !B3.includes(k));
  assert.deepEqual(extra.sort(), [...B1, ...B2].sort());
});

test('Batch 3 verified steps carry rows (button == step bits, throw 0, row exists in yoshimitsu hit_frames); review/unmapped carry row null; no soft flags', () => {
  for (const key of B3) {
    for (const s of plans[key].steps) {
      assert.ok(!('soft' in s) || s.soft !== true, `${key} step ${s.step} carries a soft flag`);
      if (s.status === 'verified') {
        assert.notEqual(s.row, null, `${key} step ${s.step} verified but row null`);
        assert.ok(hf[String(s.row)], `${key} step ${s.step} verified on row ${s.row} which does not exist in the yoshimitsu hit_frames`);
        assert.equal(hf[String(s.row)][5], stepBits(s.step), `${key} step ${s.step} row ${s.row} button mismatch`);
        assert.equal(hf[String(s.row)][5], VERIFIED_BUTTONS[String(s.row)], `${key} step ${s.step} row ${s.row} button mismatch (map)`);
        assert.equal(hf[String(s.row)][4], 0, `${key} step ${s.step} row ${s.row} is a throw row`);
      } else {
        assert.equal(s.row, null, `${key} step ${s.step} ${s.status} must not carry a playable row`);
      }
    }
  }
});

test('u/f+1,3 flagship: verified-all on rows 66/74 (jump context, SOFT waived)', () => {
  const p = plans['u/f+1,3'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [66, 74]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
  assert.ok(p.steps[0].reasons.join(' ').includes('waived'), 'jump-context verified step must record the SOFT waiver');
});

test('u/b+1,4 flagship: verified-all on rows 55/90 (jump context, SOFT waived)', () => {
  const p = plans['u/b+1,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [55, 90]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('3,1 flagship: partial, step 1 verified row 123 (standing LK3)', () => {
  const p = plans['3,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [123, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'unmapped']);
  assert.equal(p.string_status, 'partial');
});

test('d/f+1,4 flagship: partial, step 1 verified row 223 (crouch context, GATE-NOTE)', () => {
  const p = plans['d/f+1,4'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [223, null]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'unmapped']);
  assert.equal(p.string_status, 'partial');
  assert.ok(p.steps[0].reasons.join(' ').includes('GATE-NOTE'), 'crouch step on standing row must carry the GATE-NOTE');
});

test('f+4,4,2 flagship: partial, step 3 verified row 301 (standing RP2)', () => {
  const p = plans['f+4,4,2'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null, 301]);
  assert.deepEqual(p.steps.map((s) => s.status), ['review', 'review', 'verified']);
  assert.equal(p.string_status, 'partial');
});

test('2,3 flagship: step 1 SUSPENDED-DRIFT (prefix move 2 ROW-CHANGED 307->None), row null', () => {
  const p = plans['2,3'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.equal(p.steps[0].status, 'unmapped');
  assert.ok(p.steps[0].reasons.join(' ').includes('SUSPENDED-DRIFT'), 'step 1 must carry the SUSPENDED-DRIFT reason');
});

test('4,4,2 flagship: step 1 SUSPENDED-DRIFT (prefix move 4 ROW-CHANGED 243->None), row null', () => {
  const p = plans['4,4,2'];
  assert.equal(p.steps.length, 3);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null, null]);
  assert.equal(p.steps[0].status, 'unmapped');
  assert.ok(p.steps[0].reasons.join(' ').includes('SUSPENDED-DRIFT'), 'step 1 must carry the SUSPENDED-DRIFT reason');
});

test('verified-last-step Batch 3 keys are exactly the documented 26', () => {
  assert.equal(B3_VERIFIED_LAST.length, 26);
  for (const key of B3_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B3.filter((k) => !B3_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('review-last-step Batch 3 keys are exactly the documented 4', () => {
  assert.equal(B3_REVIEW_LAST.length, 4);
  for (const key of B3_REVIEW_LAST) assert.equal(plans[key].last_step_status, 'review', `${key} last step not review`);
  const others = B3.filter((k) => !B3_REVIEW_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'review', `${key} last step unexpectedly review`);
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

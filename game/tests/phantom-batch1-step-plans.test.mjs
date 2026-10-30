/* Phantom Batch 1 step plans (LP1/RP2-only strings, 2026-10-25) — data + engine-marker guard.
 * Docs: docs/movesets/PHANTOM-BATCH1-STEP-PLANS-2026-10-25.md.
 * Stack: this branch is stacked on #1096 (feat/batch1-step-plans-pantera-20261024,
 * the step-playback engine). It does NOT stack on the Pantera plan branches
 * (#1099/#1101/#1102), the burger plan branches (#1103/#1104/#1105/#1107), the
 * demonio plan branches (#1108/#1110/#1111/#1112), the diablo plan branches
 * (#1113/#1114/#1115/#1116), or the kinpo plan branches (#1117/#1118/#1119/#1120):
 * phantom.json plans do not conflict with pantera.json, burger.json,
 * demonio.json, diablo.json, or kinpo.json plans.
 * It does NOT include #1097's Pantera Batch 1 follow-up fills (Pantera-specific,
 * and its row-49 SOFT fill is still unapproved); no SOFT fill is inherited here.
 * This PR does not touch `fighter.js`: #1096's merge onto post-#1078 main must
 * reconcile #1078's `fighter.js` changes with #1096's engine branch, and that
 * belongs to #1096's merge, not this PR.
 * Bank (verified, not assumed): phantom's T3 bank is YOSHIMITSU (t3_source
 * yoshimitsu, t3_bank moveset_yoshimitsu.json, on BOTH #1096 and main; t3/
 * directory listing; Job 1 bank yoshimitsu (215 rows); Job 2 phantom entries
 * all bank yoshimitsu (1019); Job 4 yoshimitsu candidates (47)). Bank
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
 * = LP1+RK4) — it fails every single-button gate. Phantom's own LP1 move 1
 * carries t3_row 62 on #1096 (Job 1 starts-airborne) and its RP2 move 2 carries
 * t3_row 307 (Job 1 crouch) — both confirmed from file evidence — and BOTH are
 * ALSO ROW-CHANGED on current main (1: 62->None, 2: 307->None), so all 10
 * Batch 1 steps with prefix 1 or 2 are SUSPENDED-DRIFT.
 * Canonicalization is the CORRECTED rule (demonio Batch 2 finding): strip ONLY
 * a trailing ~t[378].[a-z]+(.N)?$ source-variant suffix; input-~ is Tekken
 * cancel notation, part of the move. Phantom Batch 1 contains ZERO input-~
 * canonicals — the file's old-vs-corrected diffs (3~4,U; 4,4,2,2,1,~1;
 * 4,4,2,2,NSS.1,~1) are all outside Batch 1 scope (rest key with a buttonless
 * U step; triples with union {1,2,4}). Spelling quirks kept: d/f+1,2 vs
 * df+1,2; f+2,d/b+2 vs f+2,db+2; u/f+1,1 vs uf+1,1; WS.1,1 vs ws1,1; WS.1,1,1
 * vs ws1,1,1; WS.1,1,1,1 vs ws1,1,1,1; WS.1,2 vs ws1,2; WS.2,1 vs ws2,1 are
 * distinct canonicals, never merged.
 * Rules asserted here (all data-level, no THREE needed):
 *   1. phantom.json still has 1019 moves / 191 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 372 keys (186 Batch 1 + 49 Batch 2 +
 *      85 Batch 3 + 52 Batch 4: 48 planned canonicals + 4 twins). Batches 2-4 accumulate
 *      on this file: every Batch 1 CONTENT assertion below is preserved
 *      verbatim; only the plan count, the extra-keys assertion, the Batch 4
 *      key list, and this header note changed.
 *   3. Batch 1 verified steps always carry a row whose yoshimitsu hit_frames
 *      button equals the step bits and whose throw flag is 0; verified rows
 *      always exist in the yoshimitsu hit_frames (rows 35/220 do not exist in
 *      this bank and can never be wired); review/unmapped steps carry row
 *      null. No Batch 1 step carries a soft flag (Batch 1 wires zero Job 3
 *      fills — two exact+FULL row 160 candidates are HELD at review under the
 *      stricter fill rule — and zero SOFT fills).
 *   4. d/f+1,1 flagship: verified-all on rows 223/224 (crouch context,
 *      GATE-NOTE: standing rows for crouch steps, demonio Batch 1 precedent).
 *   5. d/f+1,1,1,1 flagship: verified-all on rows 223/224/225/226.
 *   6. u/b+1,1 flagship: verified-all on rows 55/58 (jump context, SOFT waived).
 *   7. u/f+1,2 flagship: verified-all on rows 66/70 (jump context, SOFT waived).
 *   8. f+2,d/b+2 flagship: partial, last step verified row 175 (prefix-move).
 *   9. 1,1 flagship: step 1 SUSPENDED-DRIFT (prefix move 1 ROW-CHANGED
 *      62->None), row null, never wired on stale data; step 2 review (Job 3
 *      exact+FULL row 160 HELD at review, SOFT fail).
 *  10. 2,2 flagship: step 1 SUSPENDED-DRIFT (prefix move 2 ROW-CHANGED
 *      307->None), row null; step 2 review (row 308 STANCE-SOFT crouch row
 *      for a standing-context step).
 *  11. The verified-last-step Batch 1 keys are exactly the 22 listed below,
 *      and verified rows carry the step buttons in the repo yoshimitsu
 *      hit_frames.json.
 *  12. fighter.js: the step-plan branch markers exist (static guard; the engine is
 *      inherited from #1096, not changed by this PR; behaviour is play-verified).
 * Run: node --test game/tests/phantom-batch1-step-plans.test.mjs   (from repo root)
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
const B1 = ["1+2,2", "1+2,2,1", "1,1", "1,1~t3.yoshimitsu", "1,1~t7.yoshimitsu", "1,1~t7.yoshimitsu.2", "1,NSS.1", "1,d/b+2", "1,d/b+2,d/b+2", "1,d/b+2,d/b+2,d/b+2", "1,d/b+2,d/b+2,d/b+2,d/b+2", "2,1", "2,1~t3.yoshimitsu", "2,1~t7.yoshimitsu", "2,1~t7.yoshimitsu.2", "2,2", "2,2,1+2", "2,2~t7.yoshimitsu", "2,2~t7.yoshimitsu.2", "2,2~t8.yoshimitsu", "2,NSS.1", "BT.1,2", "BT.1,2~t7.yoshimitsu", "BT.1,2~t7.yoshimitsu.2", "BT.2,D/B+2,2", "BT.2,D/B+2,2,2", "BT.2,D/B+2,2,2,2", "BT.2,D/B+2,2,2,2,2", "BT.2,d/b+2", "D/B+2,2", "D/B+2,2,2", "D/B+2,2,2,2", "D/B+2,2,2,2,2", "D/B+2,2,2,2,2,2", "INS.2,D/B+2", "INS.2,D/B+2,2", "INS.2,D/B+2,2,2", "INS.2,D/B+2,2,2,2", "KIN.1,1", "KIN.1,1~t7.yoshimitsu", "KIN.1,1~t7.yoshimitsu.2", "KIN.1,NSS.1", "KIN.2,1+2", "KIN.2,1+2*", "KIN.2,1+2*~t7.yoshimitsu", "KIN.2,1+2~t7.yoshimitsu", "KIN.2,1+2~t7.yoshimitsu.2", "KIN.2,NSS.1+2", "KIN.2,NSS.1+2*", "KIN.b+2,1", "KIN.b+2,1~t7.yoshimitsu", "KIN.b+2,1~t7.yoshimitsu.2", "NSS.1+2,1", "NSS.1,2", "NSS.1,2,1", "NSS.1,2,1~t7.yoshimitsu", "NSS.1,2,1~t7.yoshimitsu.2", "NSS.1,2~t7.yoshimitsu", "NSS.2,1", "NSS.2,1~t7.yoshimitsu", "NSS.FC.DF+1,2", "NSS.b+2,2", "NSS.b+2,2~t7.yoshimitsu", "NSS.d+2,1", "NSS.d/f+1+2,2", "NSS.d/f+1+2,2~t7.yoshimitsu", "NSS.u/b+1+2,1", "NSS.u/b+1+2,1+2", "WS.1,1", "WS.1,1,1", "WS.1,1,1,1", "WS.1,2", "WS.1,2,D/B+2", "WS.1,2,D/B+2,2", "WS.1,2,D/B+2,2,2", "WS.1,2,D/B+2,2,2,2", "WS.1,2,D/B+2,2,2,2,2", "WS.1,2,D/B+2,2,2,2,2,2", "WS.1,2~t7.yoshimitsu", "WS.2,1", "WS.2,1~t7.yoshimitsu", "b+1,1", "b+1,1,1", "b+1,1,1,1", "b+1,1,1,1,1", "b+1,1,1,1,1,1", "b+1,1,1,1,1,1~t3.yoshimitsu", "b+1,1,1,1,1,1~t7.yoshimitsu", "b+1,1,1,1,1~t3.yoshimitsu", "b+1,1,1,1,1~t7.yoshimitsu", "b+1,1,1,1~t3.yoshimitsu", "b+1,1,1,1~t7.yoshimitsu", "b+1,1,1~t3.yoshimitsu", "b+1,1,1~t7.yoshimitsu", "b+1,1~t3.yoshimitsu", "b+1,1~t3.yoshimitsu.2", "b+1,1~t7.yoshimitsu", "b+2,1", "b+2,1+2", "b+2,1,1+2", "b+2,1~t7.yoshimitsu", "b+2,1~t7.yoshimitsu.2", "b+2,2", "b+2,2~t7.yoshimitsu", "b+2,2~t7.yoshimitsu.2", "b+2,NSS.1", "b+2,NSS.2", "d+2,1", "d+2,1~t7.yoshimitsu", "d+2,1~t7.yoshimitsu.2", "d+2,2", "d+2,2,1", "d+2,2,1~t7.yoshimitsu", "d+2,2,1~t7.yoshimitsu.2", "d+2,2,1~t7.yoshimitsu.3", "d+2,2,2", "d+2,2,NSS.1", "d+2,2,NSS.d+1", "d+2,2,d+1", "d+2,2,d+1~t7.yoshimitsu", "d+2,2,d+1~t7.yoshimitsu.2", "d+2,2,d+1~t7.yoshimitsu.3", "d+2,NSS.1", "d/b+1,1", "d/b+1,1~t3.yoshimitsu", "d/b+1,1~t7.yoshimitsu", "d/f+1+2,2", "d/f+1+2,2~t7.yoshimitsu", "d/f+1,1", "d/f+1,1,1", "d/f+1,1,1,1", "d/f+1,1,1,1~t3.yoshimitsu", "d/f+1,1,1~t3.yoshimitsu", "d/f+1,1~t3.yoshimitsu", "d/f+1,2", "d/f+1,2~t3.yoshimitsu", "d/f+1,2~t7.yoshimitsu", "d/f+1,2~t7.yoshimitsu.2", "db+1,2", "db+2,2", "db+2,2,2", "db+2,2,2,2", "db+2,2,2,2,2", "db+2,2,2,2,2,2", "df+1,2", "df+1,2,1", "df+1,2,NSS.1", "df+1,2,db+2", "f+2,1", "f+2,D/B+2", "f+2,D/B+2,2", "f+2,D/B+2,2,2", "f+2,D/B+2,2,2,2", "f+2,D/B+2,2,2,2,2", "f+2,D/B+2,2,2,2,2,2", "f+2,NSS.1", "f+2,d/b+2", "f+2,db+2", "u+1,1", "u+1,1~t3.yoshimitsu", "u+1,1~t3.yoshimitsu.2", "u+1,1~t3.yoshimitsu.3", "u+1,2", "u/b+1+2,1+2", "u/b+1,1", "u/b+1,1~t3.yoshimitsu", "u/b+1,1~t3.yoshimitsu.2", "u/b+1,1~t3.yoshimitsu.3", "u/b+1,2", "u/f+1+2,b+1", "u/f+1,1", "u/f+1,1~t3.yoshimitsu", "u/f+1,1~t3.yoshimitsu.2", "u/f+1,1~t3.yoshimitsu.3", "u/f+1,2", "uf+1,1", "uf+1,NSS.1", "ws1,1", "ws1,1,1", "ws1,1,1,1", "ws1,2", "ws1,2,1", "ws1,2,db+2", "ws2,1", "ws2,NSS.1", "ws2,NSS.1,2"];
const B4 = ["1+2,2,1,4", "1+2,2,1,4,2", "1+2,2,1,4,2,2", "1+2,2,1,4,2,2,2", "1+2,2,1,4,2,2,2,4", "1+2,2,1,4,2,2,2,4,1", "1+2,2,1,4,2,2,2,4,1,1", "1+2,2,1,4,4", "1+2,2,1,4,4,4", "1+2,2,1,4,4,4,1", "1+2,2,1,4,4,4,1,1", "1+2,2,1,4,4,4,1,1,1", "1+2,2,1,4,4,4,1,1,1,1", "1+2,2,1,4,4,4,1,3+4", "1,2,1,4,2,2,2,4,1,1", "1,2,1,4,4,4,1,1,1,1", "2+4,1", "2+4,1~t3.yoshimitsu", "2,2,4,1", "2,2,4,1,1", "3+4,1+2", "3+4,1+2,3+4", "3+4,1+2,3+4,1", "3,2,1+2", "3,2,NSS.1+2", "4,4,2,2,1", "4,4,2,2,1,~1", "4,4,2,2,1~t7.yoshimitsu", "4,4,2,2,NSS.1", "4,4,2,2,NSS.1,~1", "KIN.4,1+2", "NSS.u/f+3+4,b+1", "NSS.u/f+3+4,b+1,4", "NSS.u/f+3+4,b+1,4,d+1", "NSS.ub+1+3,1+2", "SS.4,1+2", "f+4,4,2,2,1", "u+2+3,1", "u/f+3+4,1", "u/f+3+4,b+1", "u/f+3+4,b+1,3+4", "u/f+3+4,b+1,4", "u/f+3+4,b+1,4,d+1", "u/f+3+4,b+1,4~t3.yoshimitsu", "u/f+3+4,b+1~t3.yoshimitsu", "ub+1+3,1+2", "uf+3+4,1", "uf+3+4,1,3+4", "uf+3+4,1,4", "uf+3+4,1,4,1", "uf+3+4,1,4,NSS.1", "ws2,NSS.1,3"];
const B2 = ["4,4", "4,4,4", "4,4,4~t7.yoshimitsu", "4,4~t7.yoshimitsu", "D/B+3,3", "D/B+3,3,3", "D/B+3,3,3,3", "D/B+3,3,3,3,3", "D/B+3,3,3,3,3,3", "IND.3,3+4", "INS.3,3+4", "INS.3,3+4~t7.yoshimitsu", "KIN.4,3+4", "SS.4,3+4", "b+3+4,b+3+4", "b+3+4,b+3+4,b+3+4", "b+3+4,b+3+4,b+3+4,b+3+4", "b+3+4,b+3+4,b+3+4,b+3+4,b+3+4", "b+3,3", "b+3,3,3", "b+3,3,3,3", "b+3,3,3,3,3", "b+3,3,3,3,3,3", "d/b+3,d/b+3", "d/b+3,d/b+3,4", "d/b+3,d/b+3,d/b+3", "d/b+3,d/b+3,d/b+3,d/b+3", "db+3,3", "db+3,3,3", "db+3,3,3,3", "db+3,3,3,3,3", "db+3,3,3,3,3,3", "db+3,3,3,3,3,4", "f+3+4,4", "f+3,3", "f+3,3,d+3+4", "f+3,3~t7.yoshimitsu", "f+3,4", "f+3,4~t7.yoshimitsu", "f+3,4~t7.yoshimitsu.2", "f+4,3", "f+4,4", "f+4,4,4", "u/f+3+4,3+4", "u/f+3+4,3+4~t7.yoshimitsu", "u/f+3+4,u+3+4", "u/f+3+4,u+3+4~t7.yoshimitsu", "uf+3+4,3", "uf+3+4,3+4"];
const B3 = ["1+3,1", "1+3,1~t3.yoshimitsu", "1+3,1~t3.yoshimitsu.2", "2,2,4", "2,3", "2,3~t7.yoshimitsu", "2,3~t7.yoshimitsu.2", "2,d+3", "2,d+3~t7.yoshimitsu", "2,d+3~t7.yoshimitsu.2", "3,1", "3,1~t3.yoshimitsu", "3,2", "3,NSS.1", "4,4,2", "4,4,2,2", "BT.1,3", "BT.1,3~t7.yoshimitsu", "BT.1,3~t7.yoshimitsu.2", "DGF.2,4", "NSS.d/f+3,1", "NSS.d/f+3,1~t7.yoshimitsu", "WS.1,1,b+3", "WS.1,1,b+4", "WS.3,2", "WS.3,2~t7.yoshimitsu", "b+1,1,db+3", "b+1,1,db+3,3", "b+1,d/b+3", "b+1,d/b+3,d/b+3", "b+1,d/b+3,d/b+3,d/b+3", "b+2,3", "d+1+4,B+1", "d+1+4,B+1,1", "d+1+4,B+1,1,1", "d+1+4,B+1,1,1,1", "d+1+4,B+1,1,1,1,1", "d+1+4,B+1,1,1,1,1~t7.yoshimitsu", "d+1+4,B+1,1,1,1~t7.yoshimitsu", "d+1+4,B+1,1,1~t7.yoshimitsu", "d+1+4,B+1,1~t7.yoshimitsu", "d+1+4,B+1~t7.yoshimitsu", "d+1+4,b+1", "d+1+4,b+1,b+1", "d+1+4,b+1,b+1,b+1", "d+1+4,b+1,b+1,b+1,b+1", "d+1+4,b+1,b+1,b+1,b+1,b+1", "d+2,2,2+3", "d+2,2,2+3~t7.yoshimitsu", "d/f+1,4", "d/f+1,4~t7.yoshimitsu", "d/f+3,1", "d/f+3,1~t7.yoshimitsu", "df+1,4", "df+3,1", "df+3,NSS.1", "f+4,1", "f+4,4,2", "f+4,4,2,2", "f+4,4,2,2,4", "u+1,3", "u+1,3~t3.yoshimitsu", "u+1,3~t3.yoshimitsu.2", "u+1,3~t3.yoshimitsu.3", "u+1,4", "u+1,4~t3.yoshimitsu", "u+1,4~t3.yoshimitsu.2", "u+1,4~t3.yoshimitsu.3", "u/b+1,3", "u/b+1,3~t3.yoshimitsu", "u/b+1,3~t3.yoshimitsu.2", "u/b+1,3~t3.yoshimitsu.3", "u/b+1,4", "u/b+1,4~t3.yoshimitsu", "u/b+1,4~t3.yoshimitsu.2", "u/b+1,4~t3.yoshimitsu.3", "u/f+1,3", "u/f+1,3~t3.yoshimitsu", "u/f+1,3~t3.yoshimitsu.2", "u/f+1,3~t3.yoshimitsu.3", "u/f+1,4", "u/f+1,4~t3.yoshimitsu", "u/f+1,4~t3.yoshimitsu.2", "u/f+1,4~t3.yoshimitsu.3", "ws3,2"];
const B1_VERIFIED_LAST = ["d/f+1,1", "d/f+1,1,1", "d/f+1,1,1,1", "d/f+1,1,1,1~t3.yoshimitsu", "d/f+1,1,1~t3.yoshimitsu", "d/f+1,1~t3.yoshimitsu", "f+2,d/b+2", "u+1,1", "u+1,1~t3.yoshimitsu", "u+1,1~t3.yoshimitsu.2", "u+1,1~t3.yoshimitsu.3", "u+1,2", "u/b+1,1", "u/b+1,1~t3.yoshimitsu", "u/b+1,1~t3.yoshimitsu.2", "u/b+1,1~t3.yoshimitsu.3", "u/b+1,2", "u/f+1,1", "u/f+1,1~t3.yoshimitsu", "u/f+1,1~t3.yoshimitsu.2", "u/f+1,1~t3.yoshimitsu.3", "u/f+1,2"];
const VERIFIED_BUTTONS = {"55": 1, "56": 1, "57": 1, "58": 1, "66": 1, "69": 2, "70": 2, "71": 2, "175": 2, "223": 1, "224": 1, "225": 1, "226": 1, "261": 3};

function stepBits(step) {
  const seg = step.split('.').pop();
  let b = 0;
  for (const c of seg) if ('1234'.includes(c)) b |= 1 << (Number(c) - 1);
  return b;
}

test('phantom move/string counts unchanged by the additive plans block', () => {
  assert.equal(Object.keys(phantom.moves).length, 1019);
  assert.equal(phantom.strings.length, 191);
  assert.equal(Object.keys(plans).length, 372);
});

test('Batch 1 keys are exactly the documented 186', () => {
  assert.equal(B1.length, 186);
  for (const key of B1) assert.ok(plans[key], `Batch 1 key ${key} missing`);
  const extra = Object.keys(plans).filter((k) => !B1.includes(k));
  assert.deepEqual(extra.sort(), [...B2, ...B3, ...B4].sort());
});

test('Batch 1 verified steps carry rows (button == step bits, throw 0, row exists in yoshimitsu hit_frames); review/unmapped carry row null; no soft flags', () => {
  for (const key of B1) {
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

test('d/f+1,1 flagship: verified-all on rows 223/224 (crouch context, GATE-NOTE)', () => {
  const p = plans['d/f+1,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [223, 224]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
  assert.ok(p.steps[0].reasons.join(' ').includes('GATE-NOTE'), 'crouch step on standing row must carry the GATE-NOTE');
});

test('d/f+1,1,1,1 flagship: verified-all on rows 223/224/225/226', () => {
  const p = plans['d/f+1,1,1,1'];
  assert.equal(p.steps.length, 4);
  assert.deepEqual(p.steps.map((s) => s.row), [223, 224, 225, 226]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified', 'verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('u/b+1,1 flagship: verified-all on rows 55/58 (jump context, SOFT waived)', () => {
  const p = plans['u/b+1,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [55, 58]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('u/f+1,2 flagship: verified-all on rows 66/70 (jump context, SOFT waived)', () => {
  const p = plans['u/f+1,2'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [66, 70]);
  assert.deepEqual(p.steps.map((s) => s.status), ['verified', 'verified']);
  assert.equal(p.string_status, 'verified-all');
});

test('f+2,d/b+2 flagship: partial, last step verified row 175 (prefix-move)', () => {
  const p = plans['f+2,d/b+2'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, 175]);
  assert.deepEqual(p.steps.map((s) => s.status), ['unmapped', 'verified']);
  assert.equal(p.string_status, 'partial');
});

test('1,1 flagship: step 1 SUSPENDED-DRIFT (prefix move 1 ROW-CHANGED 62->None), row null; step 2 review (Job 3 row 160 HELD)', () => {
  const p = plans['1,1'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.equal(p.steps[0].status, 'unmapped');
  assert.ok(p.steps[0].reasons.join(' ').includes('SUSPENDED-DRIFT'), 'step 1 must carry the SUSPENDED-DRIFT reason');
  assert.equal(p.steps[1].status, 'review');
  assert.ok(p.steps[1].reasons.join(' ').includes('HELD at review'), 'step 2 must record the held Job 3 fill');
});

test('2,2 flagship: step 1 SUSPENDED-DRIFT (prefix move 2 ROW-CHANGED 307->None), row null; step 2 review (STANCE-SOFT)', () => {
  const p = plans['2,2'];
  assert.equal(p.steps.length, 2);
  assert.deepEqual(p.steps.map((s) => s.row), [null, null]);
  assert.equal(p.steps[0].status, 'unmapped');
  assert.ok(p.steps[0].reasons.join(' ').includes('SUSPENDED-DRIFT'), 'step 1 must carry the SUSPENDED-DRIFT reason');
  assert.equal(p.steps[1].status, 'review');
  assert.ok(p.steps[1].reasons.join(' ').includes('STANCE-SOFT'), 'step 2 must carry the STANCE-SOFT reason');
});

test('verified-last-step Batch 1 keys are exactly the documented 22', () => {
  assert.equal(B1_VERIFIED_LAST.length, 22);
  for (const key of B1_VERIFIED_LAST) assert.equal(plans[key].last_step_status, 'verified', `${key} last step not verified`);
  const others = B1.filter((k) => !B1_VERIFIED_LAST.includes(k));
  for (const key of others) assert.notEqual(plans[key].last_step_status, 'verified', `${key} last step unexpectedly verified`);
});

test('fighter.js: the step-plan branch markers exist', () => {
  assert.ok(fighterSrc.includes('_attackClipPlan'), 'fighter.js missing _attackClipPlan');
  assert.ok(fighterSrc.includes('string_step_plans') || fighterSrc.includes('_stepChain'), 'fighter.js missing step-plan markers');
});

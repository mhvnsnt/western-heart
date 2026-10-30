/* Batch 1 step plans (Pantera LP1/RP2 strings, 2026-10-24) — data + engine-marker guard.
 * Docs: docs/movesets/BATCH1-STEP-PLANS-2026-10-24.md.
 * Rules asserted here (all data-level, no THREE needed):
 *   1. pantera.json still has 874 moves / 81 strings entries (plans are additive only).
 *   2. string_step_plans has exactly 60 keys; every verified step has a row, and no
 *      verified step row is 35 or 220 (jumping rows, never for standing steps — and
 *      never verified anywhere in this batch).
 *   3. 2,1: step 1 verified row 203; step 2 UNMAPPED with rejected candidate 220, row null;
 *      every 2,1 twin shares an unmapped last step (row 220 plays for no 2,1 key).
 *   4. The 14 verified-last-step keys are exactly the documented set, and every verified
 *      row exists in the repo King hit_frames.json with the step's button bits.
 *   5. The throw-class twin b+1+2,1+2~t7.king is NOT planned.
 *   6. fighter.js: the step-plan branch resolves before the donor tier, and the chain
 *      driver + unmapped flagging markers exist (static guard; behaviour is play-verified).
 *   7. Follow-up Fill 1: b+2,1+2 family last step verified row 97 (Job 3 exact + full
 *      provenance; d+1+2 caveat in the doc).
 *   8. Follow-up Fill 2: u/b+1 steps verified-SOFT row 49 (soft flag + soft_note required;
 *      the soft-verified set is exactly these two steps, never verified-exact).
 *   9. FK promotion (2026-10-30): branch-graph REVIEW steps 98/99/111/199/209/223 promoted
 *      to verified by the bank-row FK soft-gate re-run (see test/pantera-fk-promotion.test.mjs);
 *      the verified-last-step set grows 14 -> 25 and the b+2,1+2 family first step is
 *      verified row 99 (no longer review). Later batches appended plan keys beyond the
 *      original 60, so Batch1 assertions below scope to the 60 Batch1 keys explicitly
 *      instead of asserting the total plan count.
 * Run: node --test game/tests/batch1-step-plans.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const pantera = JSON.parse(readFileSync(join(ROOT, 'game/assets/movesets/pantera.json'), 'utf8'));
const fighterSrc = readFileSync(join(ROOT, 'game/js/fighter.js'), 'utf8');
const hfPath = join(ROOT, 'game/assets/anim/t3/king_on_pantera_leoman/hit_frames.json');
const hf = JSON.parse(readFileSync(hfPath, 'utf8')).rows;

const plans = pantera.string_step_plans.plans;
const BATCH1 = ["1+2,1", "1,1", "1,2", "1,2,1", "2,1", "FC.1,2", "WS.2,2", "b+1+2,1+2", "b+1+2,2", "b+1,2", "b+2,1", "b+2,1+2", "d+1+2,2", "d+1+2,2,1", "d+1+2,2,1,1", "d+1+2,2,1,1,2", "d+1,2", "d/b+1+2,2", "d/f+1,2", "d/f+2,1", "f+2,1", "f+2,1,1", "f+2,1,1,2", "f+2,d+1", "f+2,d+1,2", "u+1,1", "u+1,2", "u/b+1,1", "u/b+1,2", "u/f+1,1", "u/f+1,2", "2,1~t8.king", "1,2~t7.king", "1,2~t7.king.2", "1,2,1~t7.king", "1,2,1~t7.king.2", "1,2,1~t7.king.3", "2,1~t7.king", "2,1~t7.king.2", "1+2,1~t7.king", "1+2,1~t7.king.2", "f+2,1~t7.king", "f+2,1~t7.king.2", "f+2,d+1,2~t7.king", "f+2,d+1,2~t7.king.2", "f+2,d+1,2~t7.king.3", "d/f+1,2~t7.king", "d/f+2,1~t7.king", "b+1,2~t7.king", "b+1,2~t7.king.2", "b+2,1~t7.king", "b+2,1~t7.king.2", "b+2,1+2~t7.king", "b+2,1+2~t7.king.2", "FC.1,2~t7.king", "WS.2,2~t7.king", "f+2,1~t3.king", "df+1,2", "df+2,1", "ws2,2"];
const BIT = (s) => {
  // Spelling variants use df+/ws2 forms; normalise to d/f+/WS. before stripping.
  const norm = String(s).replace(/^df\+/, 'd/f+').replace(/^ws/i, 'WS.');
  const t = norm.replace(/^(WS\.|FC\.|SS\.|BT\.|CD\.|R\.)/, '').replace(/^(d\/f|d\/b|u\/f|u\/b|f|b|d|u|D\/F|D\/B|U\/F|U\/B|F|B|D|U)\+/, '');
  if (!/^[1-4](\+[1-4])*$/.test(t)) return null;
  return t.split('+').reduce((a, b) => a + (1 << (Number(b) - 1)), 0);
};

test('pantera move/string counts unchanged by the additive plans block', () => {
  assert.equal(Object.keys(pantera.moves).length, 874);
  assert.equal(pantera.strings.length, 81);
  for (const k of BATCH1) assert.ok(k in plans, `Batch1 key ${k} missing from plans`);
});

test('verified steps always carry a row, and no verified row is 35 or 220', () => {
  for (const [key, plan] of Object.entries(plans)) {
    for (const s of plan.steps) {
      if (s.status === 'verified') {
        assert.notEqual(s.row, null, `${key} step ${s.step} verified but row null`);
        assert.ok(s.row !== 35 && s.row !== 220, `${key} step ${s.step} verified on jumping row ${s.row}`);
      } else {
        assert.equal(s.row, null, `${key} step ${s.step} ${s.status} must not carry a playable row`);
      }
    }
  }
});

test('2,1 flagship: step 1 verified row 203, step 2 unmapped with rejected candidate 220', () => {
  const p = plans['2,1'];
  assert.equal(p.steps[0].status, 'verified');
  assert.equal(p.steps[0].row, 203);
  assert.equal(p.steps[1].status, 'unmapped');
  assert.equal(p.steps[1].row, null);
  assert.equal(p.steps[1].candidate_row, 220);
  for (const twin of ['2,1~t8.king', '2,1~t7.king', '2,1~t7.king.2']) {
    assert.equal(plans[twin].last_step_status, 'unmapped', `${twin} last step must be unmapped`);
    assert.equal(plans[twin].last_step_row, null);
  }
});

test('verified-last-step keys are exactly the documented 25 (14 + 11 FK promotions)', () => {
  const got = BATCH1.filter((k) => plans[k].last_step_status === 'verified').sort();
  const want = ['1+2,1', '1+2,1~t7.king', '1+2,1~t7.king.2', '1,2', '1,2~t7.king', '1,2~t7.king.2', 'FC.1,2', 'FC.1,2~t7.king', 'b+1+2,2', 'b+2,1', 'b+2,1+2', 'b+2,1+2~t7.king', 'b+2,1+2~t7.king.2', 'b+2,1~t7.king', 'b+2,1~t7.king.2', 'd+1+2,2', 'd+1+2,2,1', 'd/b+1+2,2', 'f+2,1~t3.king', 'u+1,1', 'u+1,2', 'u/b+1,1', 'u/b+1,2', 'u/f+1,1', 'u/f+1,2'].sort();
  assert.deepEqual(got, want);
});

test('Fill 1 (follow-up): b+2,1+2 family last step verified row 97', () => {
  for (const key of ['b+2,1+2', 'b+2,1+2~t7.king', 'b+2,1+2~t7.king.2']) {
    const p = plans[key];
    assert.equal(p.steps[1].status, 'verified', `${key} step 1+2 must be verified`);
    assert.equal(p.steps[1].row, 97, `${key} step 1+2 must play row 97`);
    assert.equal(p.steps[1].candidate_source, 'job3-match_search');
    assert.equal(p.last_step_status, 'verified');
    assert.equal(p.last_step_row, 97);
    assert.equal(p.string_status, 'verified-all');
    assert.equal(p.steps[0].status, 'verified', `${key} step b+2 promoted 2026-10-30 by the bank-row FK gate (row 99)`);
    assert.equal(p.steps[0].row, 99, `${key} step b+2 must play row 99`);
  }
  // Row 97 is a standing LP1+RP2 chord row, never a jumping row.
  const row97 = hf['97'];
  assert.equal(row97[5], 3, 'row 97 button bits must be LP1+RP2 (3)');
  assert.equal(row97[4], 0, 'row 97 must not be throw-flagged');
});

test('Fill 2 (follow-up): u/b+1 steps verified-SOFT row 49, never verified-exact', () => {
  const softSteps = [];
  for (const [key, plan] of Object.entries(plans)) {
    for (const s of plan.steps) {
      if (s.soft === true) softSteps.push(`${key} step ${s.step}`);
    }
  }
  assert.deepEqual(softSteps.sort(), ['u/b+1,1 step u/b+1', 'u/b+1,2 step u/b+1'].sort());
  for (const key of ['u/b+1,1', 'u/b+1,2']) {
    const s = plans[key].steps[0];
    assert.equal(s.status, 'verified');
    assert.equal(s.row, 49);
    assert.equal(s.soft, true);
    assert.ok(typeof s.soft_note === 'string' && s.soft_note.length > 0, `${key} soft step must carry a soft_note`);
    assert.equal(s.candidate_source, 'job3-match_search');
    assert.equal(plans[key].string_status, 'verified-all');
  }
  const row49 = hf['49'];
  assert.equal(row49[5], 1, 'row 49 button bits must be LP1 (1)');
  assert.equal(row49[4], 0, 'row 49 must not be throw-flagged');
});

test('every verified row exists in the repo King hit_frames with the step button bits', () => {
  for (const [key, plan] of Object.entries(plans)) {
    for (const s of plan.steps) {
      if (s.status !== 'verified') continue;
      const row = hf[String(s.row)];
      assert.ok(row, `${key} step ${s.step}: verified row ${s.row} missing from hit_frames.json`);
      assert.equal(row[5], BIT(s.step), `${key} step ${s.step}: hit_frames button ${row[5]} != step bits ${BIT(s.step)}`);
      assert.equal(row[4], 0, `${key} step ${s.step}: verified row ${s.row} is throw-flagged`);
    }
  }
});

test('throw-class twin is excluded from plans', () => {
  assert.ok(!('b+1+2,1+2~t7.king' in plans));
  assert.equal(pantera.moves['b+1+2,1+2~t7.king'].move_class, 'throw');
});

test('fighter.js step-plan branch precedes the donor tier and chain markers exist', () => {
  const branchAt = fighterSrc.indexOf('const sp = this._resolveStepPlan(');
  const donorAt = fighterSrc.indexOf('const d = this._rowDonor(move)');
  assert.ok(branchAt > 0 && donorAt > 0 && branchAt < donorAt, 'step-plan branch must resolve before the donor tier');
  for (const marker of ['_resolveStepPlan', '_stepChain', '_advanceStepChain', '[WH-STEP-PLAN]', 'kind: \'step-plan\'']) {
    assert.ok(fighterSrc.includes(marker), `fighter.js missing marker ${marker}`);
  }
});

test('doc + audit entry exist and state the gate honestly', () => {
  const doc = readFileSync(join(ROOT, 'docs/movesets/BATCH1-STEP-PLANS-2026-10-24.md'), 'utf8');
  assert.ok(doc.includes('Switch-criteria checklist'));
  assert.ok(doc.includes('NOT LANDED'));
  assert.ok(doc.includes('NOT play-verified'));
  const audit = readFileSync(join(ROOT, 'docs/anim/PROCEDURAL_AUDIT.md'), 'utf8');
  assert.ok(audit.includes('Batch 1 step plans'));
  assert.ok(existsSync(hfPath));
});

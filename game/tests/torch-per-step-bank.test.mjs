/* Torch per-step-bank engine (2026-10-25) — data + engine-marker tests.
 * Docs: docs/movesets/TORCH-PER-STEP-BANK-ENGINE-2026-10-25.md.
 * Stack: stacked on #1096 (engine) only. It does NOT touch torch.json
 * plans, any other fighter's moveset file, or #988 files. The torch
 * fixture below is TEST DATA copied verbatim from the #1136 torch
 * Batch 1 plans for 7 keys (see the verbatim spot-check test); it is
 * not a moveset file and it never replaces torch.json.
 * Pure resolver tests need no THREE: they import step-plan-bank.js
 * directly. fighter.js integration (THREE retarget of a jin row onto
 * torch's rig) is covered by static markers here + play-verify after
 * merge + deploy — never claimed from these tests alone.
 * Bound bank for torch throughout: 'anna' (fighter.js #1096
 * FIGHTER_BANK torch->anna + moveset anim_bank anna).
 * Buttons: LP1/RP2/LK3/RK4. Tekken names are technical only.
 * Run: node --test game/tests/torch-per-step-bank.test.mjs (repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { effectiveStepPlay, oldRulePlay, playableStepPlay, stepActionName, stepPlanBanksFor } from '../js/step-plan-bank.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..', '..');
const fighterSrc = readFileSync(join(ROOT, 'game/js/fighter.js'), 'utf8');
const pantera = JSON.parse(readFileSync(join(ROOT, 'game/assets/movesets/pantera.json'), 'utf8'));
const fixture = JSON.parse(readFileSync(join(HERE, 'torch-per-step-bank-fixture.json'), 'utf8'));

const BOUND = 'anna';
// Cached source-clip rows per bank, from Batch 1 evidence. Anna row
// 220 EXISTS in anna hit_frames (button 0) — deliberately included:
// it is the trap the fail-safe tests must not fall into. Jin rows are
// the 8 distinct BANK-BLOCKED rows; anna rows are the 10 wired rows.
const CLIPS = {
  jin: new Set([92, 93, 183, 220, 221, 222, 223, 249]),
  anna: new Set([32, 33, 34, 44, 45, 46, 171, 174, 220, 355, 356]),
};
const hasClip = (bank, row) => !!(CLIPS[bank] && CLIPS[bank].has(row));
const playOf = (step) => playableStepPlay(step, BOUND, hasClip);
const nameOf = (step) => { const p = playOf(step); return p ? stepActionName(p, BOUND) : null; };

test('torch 2,1 chain resolves to jin rows through the new path (not anna rows)', () => {
  const p = fixture['2,1'];
  assert.deepEqual(p.steps.map((s) => playOf(s)), [
    { row: 220, bank: 'jin', via: 'bank-blocked' },
    { row: 221, bank: 'jin', via: 'bank-blocked' },
  ]);
  assert.deepEqual(p.steps.map((s) => nameOf(s)), ['row:jin:220', 'row:jin:221']);
});

test('torch 2,1,2 and 2,1,2,2 chains resolve step by step to jin rows', () => {
  assert.deepEqual(fixture['2,1,2'].steps.map((s) => nameOf(s)), ['row:jin:220', 'row:jin:221', 'row:jin:222']);
  assert.deepEqual(fixture['2,1,2,2'].steps.map((s) => nameOf(s)), ['row:jin:220', 'row:jin:221', 'row:jin:222', 'row:jin:223']);
});

test('torch anna steps still resolve via the bound bank, unchanged names', () => {
  assert.equal(nameOf(fixture['b+1+2,1'].steps[1]), 'row:355');
  assert.deepEqual(playOf(fixture['b+1+2,1'].steps[1]), { row: 355, bank: 'anna', via: 'verified' });
  assert.equal(nameOf(fixture['d/f+1+2,2'].steps[1]), 'row:174');
  assert.equal(nameOf(fixture['u+1,1'].steps[1]), 'row:32');
  // Their unmapped openers still play nothing.
  assert.equal(nameOf(fixture['b+1+2,1'].steps[0]), null);
  assert.equal(nameOf(fixture['d/f+1+2,2'].steps[0]), null);
  assert.equal(nameOf(fixture['u+1,1'].steps[0]), null);
});

test('mixed plan: an anna step and a jin step in one string play from their own banks', () => {
  const blocked = (prefix, row) => ({ step: prefix, prefix, bank: 'jin', bound_bank: 'anna', row: null,
    status: 'review', bank_verified_row: row, candidate_row: row, candidate_source: 'recorded-path',
    reasons: [`BANK-BLOCKED: gate-verified in jin bank (row ${row})`] });
  const mixed = [
    { step: 'b+1+2,1', prefix: 'b+1+2,1', bank: 'anna', bound_bank: 'anna', row: 355, status: 'verified', bank_verified_row: null, reasons: [] },
    blocked('x,1', 220),
  ];
  assert.deepEqual(mixed.map((s) => nameOf(s)), ['row:355', 'row:jin:220']);
  assert.deepEqual(mixed.map((s) => playOf(s).bank), ['anna', 'jin']);
});

test('fixture is verbatim Batch 1 evidence for 2,1 (guards fixture drift)', () => {
  const p = fixture['2,1'];
  assert.deepEqual(p.steps.map((s) => [s.prefix, s.status, s.row, s.bank_verified_row, s.bank]),
    [['2', 'review', null, 220, 'jin'], ['2,1', 'review', null, 221, 'jin']]);
  assert.ok(p.steps.every((s) => s.reasons.join(' ').includes('BANK-BLOCKED')));
});

test('single-bank regression: pantera plans (real #1096 file) resolve byte-identically to #1096', () => {
  const plans = pantera.string_step_plans.plans;
  assert.equal(Object.keys(plans).length, 60);
  let steps = 0;
  for (const plan of Object.values(plans)) {
    for (const s of plan.steps) {
      steps++;
      assert.ok(!s.bank, `pantera step ${s.prefix} unexpectedly carries bank ${s.bank}`);
      assert.equal(s.bank_verified_row ?? null, null, `pantera step ${s.prefix} unexpectedly carries bank_verified_row`);
      assert.deepEqual(effectiveStepPlay(s, 'king'), oldRulePlay(s, 'king'));
      assert.equal(stepActionName(effectiveStepPlay(s, 'king'), 'king'), oldRulePlay(s, 'king') ? `row:${oldRulePlay(s, 'king').row}` : null);
    }
  }
  assert.equal(steps, 137);
});

test('single-bank regression: synthetic bank-null/absent plans are untouched by the new path', () => {
  const steps = [
    { prefix: '1', status: 'verified', row: 50 },
    { prefix: '1,2', status: 'review', row: null },
    { prefix: '1,2,1', status: 'unmapped', row: null },
    { prefix: '2', status: 'verified', row: 51, bank: null },
  ];
  for (const s of steps) assert.deepEqual(effectiveStepPlay(s, BOUND), oldRulePlay(s, BOUND));
});

test('fail-safe: override bank with no such row plays NOTHING, even when the bound bank has that row number', () => {
  const step = { prefix: '2', bank: 'jin', bound_bank: 'anna', row: null, status: 'review',
    bank_verified_row: 220, reasons: ['BANK-BLOCKED: gate-verified in jin bank (row 220)'] };
  // Jin clips WITHOUT row 220, anna clips WITH row 220: the trap case.
  const trapHasClip = (bank, row) => bank === 'jin' ? false : (bank === 'anna' && row === 220);
  assert.equal(playableStepPlay(step, BOUND, trapHasClip), null);
  assert.equal(playableStepPlay(step, BOUND, () => false), null);
});

test('fail-safe: unknown bank, unloaded bank, missing reason, bound-bank review, bad row all play nothing', () => {
  const base = { prefix: '2', bound_bank: 'anna', row: null, status: 'review', bank_verified_row: 220,
    reasons: ['BANK-BLOCKED: gate-verified in jin bank (row 220)'] };
  assert.equal(playableStepPlay({ ...base, bank: 'mokujin' }, BOUND, hasClip), null);
  assert.equal(playableStepPlay({ ...base, bank: 'jin' }, BOUND, () => false), null);
  assert.equal(playableStepPlay({ ...base, bank: 'jin', reasons: ['gate-verified in jin bank'] }, BOUND, hasClip), null);
  assert.equal(playableStepPlay({ ...base, bank: 'jin', reasons: [] }, BOUND, hasClip), null);
  assert.equal(playableStepPlay({ ...base, bank: 'anna' }, BOUND, hasClip), null);
  assert.equal(playableStepPlay({ ...base, bank: 'jin', bank_verified_row: '220' }, BOUND, hasClip), null);
  assert.equal(playableStepPlay({ ...base, bank: 'jin', bank_verified_row: -1 }, BOUND, hasClip), null);
  assert.equal(playableStepPlay({ prefix: '1', status: 'verified', row: null }, BOUND, hasClip), null);
  assert.equal(playableStepPlay(null, BOUND, hasClip), null);
});

test('promotion rule, forward schema: verified + row + own bank resolves from that bank (no re-gate)', () => {
  // The mechanical promotion of a BANK-BLOCKED step: status verified,
  // row set from bank_verified_row, bank kept. Same rows, new status.
  const promoted = fixture['2,1'].steps.map((s) => ({ ...s, status: 'verified', row: s.bank_verified_row }));
  assert.deepEqual(promoted.map((s) => nameOf(s)), ['row:jin:220', 'row:jin:221']);
  assert.deepEqual(promoted.map((s) => playOf(s).via), ['verified-bank', 'verified-bank']);
});

test('stepPlanBanksFor: torch fixture needs jin preloaded; pantera needs nothing; no-plan moveset needs nothing', () => {
  assert.deepEqual(stepPlanBanksFor({ string_step_plans: { plans: fixture } }, BOUND), ['jin']);
  assert.deepEqual(stepPlanBanksFor(pantera, 'king'), []);
  assert.deepEqual(stepPlanBanksFor({}, BOUND), []);
  assert.deepEqual(stepPlanBanksFor(null, BOUND), []);
});

test('fighter.js: per-step-bank wiring markers exist; old bound-only formulas are gone', () => {
  for (const m of ['step-plan-bank.js', 'loadT3Clips', '_stepBankClips', 'getT3Clips(sp.playBank)',
    'stepBank: sp.playBank', 'stepBank: plan && plan.stepBank', 'stepRow: plan && plan.stepRow',
    'this._atkPlan.stepRow', "row:' + plan.stepRow", 'stepPlanBanksFor']) {
    assert.ok(fighterSrc.includes(m), `fighter.js missing marker: ${m}`);
  }
  assert.ok(!fighterSrc.includes("(st.status === 'verified' && st.row != null) ? 'row:' + st.row"),
    'fighter.js still carries the old chain-step bound-only formula');
  assert.ok(!fighterSrc.includes("(last.status === 'verified' && last.row != null) ? 'row:' + last.row"),
    'fighter.js still carries the old last-step bound-only formula');
  // The old bound-only clip check must not gate override names: the
  // step branch reads its source clip from the play bank.
  assert.ok(fighterSrc.includes("const srcClips = (sp.playBank === bank) ? clips : getT3Clips(sp.playBank)"),
    'fighter.js step branch does not read the play-bank source clip');
});

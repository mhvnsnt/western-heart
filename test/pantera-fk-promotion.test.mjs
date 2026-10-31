/* Pantera step-plan FK promotion (2026-10-30, takeover row 71 sub-step).
 * The #1232 branch-graph REVIEW steps promoted here passed the bank-row FK
 * soft gate re-run from repo data only: game/assets/anim/t3/king_on_pantera_leoman
 * rows.pack.json (decoded clips) + skeleton.json (rest pose) + hit_frames.json
 * (active windows). FK: Chest-to-end distance delta vs frame 0; exact active
 * window = hit_frames active stream frames / 2. Promotion rule: hard gates in
 * the plan record (button bits, throw 0) + correct limb dominant in-window +
 * in-window peak >= 85% of that limb's global clip peak (verified controls
 * 100%; recorded failures 117 at 70%, 257 wrong-limb, 258 at 4%).
 * This test is data-level (no THREE): it locks the promoted set, re-checks
 * the hit_frames hard gates for every promoted row, and guards the steps
 * that stay review (117/257/258) plus the all-plan tallies.
 * Run: node test/pantera-fk-promotion.test.mjs (from repo root, CI game-unit-tests)
 *
 * T7 CROSS-DECODE chunk (2026-10-31, lane B2): 19 further steps promoted on
 * Tekken 7 evidence instead of FK — King's kinmot cancel graph was
 * deciphered (alias table at motbin offset 0x28; GROUP delegation via
 * direction 0x800B) and walked group-correct (docs/movesets/
 * T7-CROSSDECODE-PANTERA-2026-10-31.md). PROMOTED_T7 below locks them:
 * row 198 enders (1,2,1 step 2; f+2,1 step 1 — the walk reaches the
 * clip-map-joined motbin moves 1685 Kg_rplu6 / 1594 Kg_6rplp at open tier)
 * and row 135 step-0 (d/f+4 family — the step is the move itself, T7
 * identity uniquely 1660 Kg_t_srkF). FK + play-verify remain owed for
 * these (their evidence notes say so). Row 117 (d/f+1,2 step 0) is NOT
 * among them: its T7 identity was confirmed (1652 Kg_t_slpF) but the
 * recorded FK failure above (70%) still blocks it — it stays in GUARDS.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const pantera = JSON.parse(readFileSync(join(ROOT, 'game/assets/movesets/pantera.json'), 'utf8'));
const plans = pantera.string_step_plans.plans;
const hf = JSON.parse(readFileSync(join(ROOT, 'game/assets/anim/t3/king_on_pantera_leoman/hit_frames.json'), 'utf8')).rows;

const BIT = (s) => {
  const norm = String(s).replace(/^df\+/, 'd/f+').replace(/^ws/i, 'WS.');
  const t = norm.replace(/^(WS\.|FC\.|SS\.|BT\.|CD\.|R\.)/, '').replace(/^(d\/f|d\/b|u\/f|u\/b|f|b|d|u|D\/F|D\/B|U\/F|U\/B|F|B|D|U)\+/, '');
  if (!/^[1-4](\+[1-4])*$/.test(t)) return null;
  return t.split('+').reduce((a, b) => a + (1 << (Number(b) - 1)), 0);
};

// [plan key, step index, step, row] — every step this chunk promotes (35).
const PROMOTED = [
  ['1+2,1', 0, '1+2', 223], ['1+2,1', 1, '1', 209],
  ['1+2,1~t7.king', 0, '1+2', 223], ['1+2,1~t7.king', 1, '1', 209],
  ['1+2,1~t7.king.2', 0, '1+2', 223], ['1+2,1~t7.king.2', 1, '1', 209],
  ['1,2', 1, '2', 98], ['1,2,1', 1, '2', 98], ['FC.1,2', 1, '2', 98],
  ['1,2~t7.king', 1, '2', 98], ['1,2~t7.king.2', 1, '2', 98],
  ['1,2,1~t7.king', 1, '2', 98], ['1,2,1~t7.king.2', 1, '2', 98], ['1,2,1~t7.king.3', 1, '2', 98],
  ['FC.1,2~t7.king', 1, '2', 98],
  ['b+2,1', 0, 'b+2', 99], ['b+2,1', 1, '1', 199],
  ['b+2,1+2', 0, 'b+2', 99],
  ['b+2,1~t7.king', 0, 'b+2', 99], ['b+2,1~t7.king', 1, '1', 199],
  ['b+2,1~t7.king.2', 0, 'b+2', 99], ['b+2,1~t7.king.2', 1, '1', 199],
  ['b+2,1+2~t7.king', 0, 'b+2', 99], ['b+2,1+2~t7.king.2', 0, 'b+2', 99],
  ['f+2,1', 0, 'f+2', 111], ['f+2,1,1', 0, 'f+2', 111], ['f+2,1,1,2', 0, 'f+2', 111],
  ['f+2,d+1', 0, 'f+2', 111], ['f+2,d+1,2', 0, 'f+2', 111],
  ['f+2,1~t7.king', 0, 'f+2', 111], ['f+2,1~t7.king.2', 0, 'f+2', 111],
  ['f+2,d+1,2~t7.king', 0, 'f+2', 111], ['f+2,d+1,2~t7.king.2', 0, 'f+2', 111],
  ['f+2,d+1,2~t7.king.3', 0, 'f+2', 111], ['f+2,1~t3.king', 0, 'f+2', 111],
];

test('promoted steps are verified on their candidate row with the FK note', () => {
  assert.equal(PROMOTED.length, 35);
  for (const [key, idx, step, row] of PROMOTED) {
    const s = plans[key].steps[idx];
    assert.equal(s.step, step, `${key} step ${idx}`);
    assert.equal(s.status, 'verified', `${key} step ${step} must be verified`);
    assert.equal(s.row, row, `${key} step ${step} must play row ${row}`);
    assert.equal(s.candidate_row, row, `${key} step ${step} candidate must be row ${row}`);
    assert.equal(s.candidate_source, 't3-branch-graph', `${key} step ${step} source`);
    assert.ok(s.reasons.some((r) => r.startsWith('FK PROMOTION 2026-10-30')), `${key} step ${step} must carry the FK evidence note`);
  }
});

test('promoted rows pass the hit_frames hard gates', () => {
  for (const [key, idx, step, row] of PROMOTED) {
    const h = hf[String(row)];
    assert.ok(h, `${key} row ${row} missing from hit_frames`);
    assert.equal(h[5], BIT(step), `${key} step ${step}: hit_frames button ${h[5]} != step bits ${BIT(step)}`);
    assert.equal(h[4], 0, `${key} row ${row} is throw-flagged`);
  }
});

test('recorded FK failures stay review with no playable row', () => {
  const GUARDS = [
    ['d/f+1,2', 0, 'd/f+1', 117], ['d/f+1,2~t7.king', 0, 'd/f+1', 117], ['df+1,2', 0, 'df+1', 117],
    ['d+1+2,2,1,1', 3, '1', 257], ['d+1+2,2,1,1,2', 3, '1', 257],
    ['f+2,1,1', 2, '1', 257], ['f+2,1,1,2', 2, '1', 257],
    ['d+1+2,2,1,1,2', 4, '2', 258], ['f+2,1,1,2', 3, '2', 258],
  ];
  for (const [key, idx, step, row] of GUARDS) {
    const s = plans[key].steps[idx];
    assert.equal(s.step, step, `${key} step ${idx}`);
    assert.equal(s.status, 'review', `${key} step ${step} must stay review`);
    assert.equal(s.row, null, `${key} step ${step} must not carry a playable row`);
    assert.equal(s.candidate_row, row, `${key} step ${step} candidate must stay row ${row}`);
  }
});

test('all-plan tallies after this promotion', () => {
  const counts = { verified: 0, review: 0, unmapped: 0 };
  for (const plan of Object.values(plans)) {
    for (const s of plan.steps) counts[s.status] += 1;
  }
  assert.deepEqual(counts, { verified: 174, review: 63, unmapped: 389 });
});

test('promoted keys carry consistent plan-level fields', () => {
  const VERIFIED_ALL = ['1+2,1', '1+2,1~t7.king', '1+2,1~t7.king.2', '1,2', '1,2~t7.king', '1,2~t7.king.2',
    'FC.1,2', 'FC.1,2~t7.king', 'b+2,1', 'b+2,1~t7.king', 'b+2,1~t7.king.2',
    'b+2,1+2', 'b+2,1+2~t7.king', 'b+2,1+2~t7.king.2', 'f+2,1~t3.king'];
  for (const key of VERIFIED_ALL) {
    assert.equal(plans[key].string_status, 'verified-all', `${key} must be verified-all`);
    assert.equal(plans[key].last_step_status, 'verified', `${key} last step must be verified`);
    assert.notEqual(plans[key].last_step_row, null, `${key} last step row must be set`);
  }
});

// [plan key, step index, step, row, candidate_source] — T7 cross-decode (19).
const PROMOTED_T7 = [
  ['1,2,1', 2, '1', 198, 't3-branch-graph'],
  ['1,2,1~t7.king', 2, '1', 198, 't3-branch-graph'],
  ['1,2,1~t7.king.2', 2, '1', 198, 't3-branch-graph'],
  ['1,2,1~t7.king.3', 2, '1', 198, 't3-branch-graph'],
  ['f+2,1', 1, '1', 198, 't3-branch-graph'],
  ['f+2,1,1', 1, '1', 198, 't3-branch-graph'],
  ['f+2,1,1,2', 1, '1', 198, 't3-branch-graph'],
  ['f+2,1~t7.king', 1, '1', 198, 't3-branch-graph'],
  ['f+2,1~t7.king.2', 1, '1', 198, 't3-branch-graph'],
  ['d/f+4,2', 0, 'd/f+4', 135, 'prefix-move'],
  ['d/f+4,3', 0, 'd/f+4', 135, 'prefix-move'],
  ['d/f+4,3,4', 0, 'd/f+4', 135, 'prefix-move'],
  ['d/f+4,3,4~t7.king', 0, 'd/f+4', 135, 'prefix-move'],
  ['d/f+4,3,4~t7.king.2', 0, 'd/f+4', 135, 'prefix-move'],
  ['d/f+4,3,d+4', 0, 'd/f+4', 135, 'prefix-move'],
  ['d/f+4,3,d+4~t7.king', 0, 'd/f+4', 135, 'prefix-move'],
  ['d/f+4,3,d+4~t7.king.2', 0, 'd/f+4', 135, 'prefix-move'],
  ['d/f+4,3~t7.king', 0, 'd/f+4', 135, 'prefix-move'],
  ['d/f+4,4', 0, 'd/f+4', 135, 'prefix-move'],
];

test('T7 cross-decode promoted steps are verified on their candidate row with the T7 note', () => {
  assert.equal(PROMOTED_T7.length, 19);
  for (const [key, idx, step, row, source] of PROMOTED_T7) {
    const s = plans[key].steps[idx];
    assert.equal(s.step, step, `${key} step ${idx}`);
    assert.equal(s.status, 'verified', `${key} step ${step} must be verified`);
    assert.equal(s.row, row, `${key} step ${step} must play row ${row}`);
    assert.equal(s.candidate_row, row, `${key} step ${step} candidate must be row ${row}`);
    assert.equal(s.candidate_source, source, `${key} step ${step} source`);
    assert.ok(s.reasons.some((r) => r.startsWith('T7 CROSS-DECODE PROMOTION 2026-10-31')), `${key} step ${step} must carry the T7 evidence note`);
  }
});

test('T7-promoted keys carry consistent plan-level fields', () => {
  const VERIFIED_ALL_T7 = ['1,2,1', '1,2,1~t7.king', '1,2,1~t7.king.2', '1,2,1~t7.king.3',
    'f+2,1', 'f+2,1~t7.king', 'f+2,1~t7.king.2', 'd/f+4,4'];
  for (const key of VERIFIED_ALL_T7) {
    assert.equal(plans[key].string_status, 'verified-all', `${key} must be verified-all`);
    assert.equal(plans[key].last_step_status, 'verified', `${key} last step must be verified`);
    assert.notEqual(plans[key].last_step_row, null, `${key} last step row must be set`);
  }
  assert.equal(plans['d/f+4,2'].string_status, 'partial', 'd/f+4,2 must be partial after its step-0 promotion');
});

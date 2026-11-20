/* hitstop-tekken-draft.test.mjs — Tekken-anchored hit-stop draft (2026-11-02).
 * Run: node test/hitstop-tekken-draft.test.mjs   (from repo root)
 * WHAT THIS GUARDS:
 *  (1) the draft table in game/js/hitstop-tekken-draft.js is internally
 *      consistent (frames -> ms at 60 fps, parry duration honestly null);
 *  (2) the draft is NOT wired — live combat still runs the current
 *      feelFor values, so this PR changes no gameplay. If someone wires
 *      the draft into combat-systems.js, the "draft is not wired" test
 *      below must be updated deliberately, with owner approval, not
 *      silently.
 * Tekken evidence: docs/handoffs/HITSTOP-TEKKEN-DRAFT-20261102.md.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { HITSTOP_TEKken_DRAFT, NOT_WIRED, draftStopMs } from '../game/js/hitstop-tekken-draft.js';
import { feelFor } from '../game/js/combat-systems.js';

test('draft is explicitly not wired', () => {
  assert.equal(NOT_WIRED, true);
});

const GENERIC = ['hit', 'block', 'juggle', 'spin', 'stagger', 'screw',
  'knockdown', 'guard_break', 'floor_bound', 'crumple', 'launch',
  'wall_splat', 'throw', 'throw_break', 'wakeup', 'counter_bonus'];

test('draft generic reactions are 0f (no published Tekken generic value)', () => {
  for (const r of GENERIC) {
    assert.equal(HITSTOP_TEKken_DRAFT[r], 0, `${r} draft must be 0f`);
    assert.equal(draftStopMs(r), 0, `${r} draft ms must be 0`);
  }
});

test('draft special-case timestop is 20f = 333.3 ms, parry duration is honestly null', () => {
  assert.equal(HITSTOP_TEKken_DRAFT.special_timestop, 20);
  assert.ok(Math.abs(draftStopMs('special_timestop') - 333.333) < 0.01);
  assert.equal(HITSTOP_TEKken_DRAFT.parry_success, null);
  assert.equal(draftStopMs('parry_success'), null);
});

test('live combat is unchanged by this draft PR', () => {
  // feelFor stop is in frames; stopSec = frames / 60.
  assert.equal(feelFor('hit').stop, 6);
  assert.equal(feelFor('block').stop, 4);
  assert.equal(feelFor('wall_splat').stop, 14);
  assert.equal(feelFor('launch').stop, 12);
  assert.equal(feelFor('hit', { counter: true }).stop, 9, 'live counter bonus is still +3f');
  assert.equal(feelFor('block', { counter: true }).stop, 4, 'counter bonus never applies on block');
});

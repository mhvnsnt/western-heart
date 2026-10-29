// Hit-reaction wiring tests (hit-reaction lane, 2026-10-24).
// Runs with: node --test test/t3-hit-reactions.test.mjs
// Reads the decoded file data in game/assets/anim/t3/reactions.json
// (633 EXE reaction records, 22 banks) and the King reaction pack.
// Nothing here hardcodes a guessed pairing: every expected slot is
// the value the file's own record field holds for that situation.
// The selector under test is game/js/t3-reaction-select.js, the
// module fighter.js calls on every confirmed hit.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { selectReactionSlot, reactionSlotBank } from '../game/js/t3-reaction-select.js';

const R = JSON.parse(readFileSync(
  new URL('../game/assets/anim/t3/reactions.json', import.meta.url), 'utf8'));
const KING = R.banks.king_on_pantera_leoman;

// King row 37: reaction record 211, class 0, no close entry.
// Record 211: front 2232, counter 2556, side1 2232, side3 2232,
// back 2556, guard 2693, down 2633, down_other 2636.
const ROW37 = KING.rows['37'];
// King row 50: reaction record 312 — front 2385, front_crouch 2522.
const ROW50 = KING.rows['50'];
// King row 115: reaction 325 with close entry 2 -> [412, 1100].
const ROW115 = KING.rows['115'];
// King row 21: class 0, reaction 4469 (0x1175, throw range).
const ROW21 = KING.rows['21'];
// King row 127: class 1 (zero-damage catch strike, never reacts).
const ROW127 = KING.rows['127'];

test('front stagger: record front field', () => {
  assert.deepEqual(ROW37, [211, 0, 0]);
  const sel = selectReactionSlot(R, ROW37, {});
  assert.equal(sel.slot, 2232);
  assert.equal(sel.field, 'front');
  assert.equal(sel.code, 0x2a);
  assert.equal(sel.record, 211);
});

test('crouch changes the stagger: front_crouch field', () => {
  assert.deepEqual(ROW50, [312, 0, 0]);
  assert.equal(selectReactionSlot(R, ROW50, {}).slot, 2385);
  const crouch = selectReactionSlot(R, ROW50, { crouch: true });
  assert.equal(crouch.slot, 2522);
  assert.equal(crouch.field, 'front_crouch');
});

test('counter, side and back reactions come from their own fields', () => {
  assert.equal(selectReactionSlot(R, ROW37, { counter: true }).slot, 2556);
  assert.equal(selectReactionSlot(R, ROW37, { counter: true }).code, 0x26);
  assert.equal(selectReactionSlot(R, ROW37, { quadrant: 1 }).slot, 2232);
  assert.equal(selectReactionSlot(R, ROW37, { quadrant: 1 }).code, 0x27);
  assert.equal(selectReactionSlot(R, ROW37, { quadrant: 2 }).slot, 2556);
  assert.equal(selectReactionSlot(R, ROW37, { quadrant: 2 }).code, 0x2b);
  assert.equal(selectReactionSlot(R, ROW37, { quadrant: 3 }).slot, 2232);
  assert.equal(selectReactionSlot(R, ROW37, { quadrant: 3 }).code, 0x28);
});

test('guard and down reactions come from their own fields', () => {
  const guard = selectReactionSlot(R, ROW37, { guarded: true });
  assert.equal(guard.slot, 2693);
  assert.equal(guard.field, 'guard');
  assert.equal(guard.code, 0x23);
  const down = selectReactionSlot(R, ROW37, { down: true });
  assert.equal(down.slot, 2633);
  assert.equal(down.field, 'down');
  assert.equal(down.code, 0x25);
});

test('airborne hits use the air kinds, not the ground record', () => {
  const air = selectReactionSlot(R, ROW37, { airborne: true });
  assert.equal(air.slot, 3414); // air_kinds[0]
  assert.equal(air.code, 0x24);
  assert.equal(selectReactionSlot(R, ROW37, { airborne: true, airKind: 4 }).slot, 3428);
});

test('close-range substitution uses the close_reactions table', () => {
  assert.deepEqual(ROW115, [325, 2, 0]);
  assert.deepEqual(R.close_reactions[2], [412, 1100]);
  assert.equal(selectReactionSlot(R, ROW115, {}).slot, 2573); // record 325 front
  // Close entry 2 names reaction record 412, whose front slot is 2597.
  assert.equal(selectReactionSlot(R, ROW115, { close: true }).slot, 2597);
});

test('no reaction: class 1, throw-range value, missing row, no tables', () => {
  assert.deepEqual(ROW127, [4469, 0, 1]);
  assert.equal(selectReactionSlot(R, ROW127, {}), null);
  assert.deepEqual(ROW21, [4469, 0, 0]);
  assert.equal(selectReactionSlot(R, ROW21, {}), null); // 0x1nnn acts only through a throw
  assert.equal(selectReactionSlot(R, null, {}), null);
  assert.equal(selectReactionSlot(null, ROW37, {}), null);
});

test('slot resolution is defender-bank-first, attacker-bank-second', () => {
  // 0x8b8 (slot 2232) is defined by both Paul and King: defender wins.
  assert.equal(reactionSlotBank(R, 'paul', 'king_on_pantera_leoman', 0x8b8), 'paul');
  // 0x198 is defined by King only: the attacker's bank supplies it.
  assert.equal(reactionSlotBank(R, 'paul', 'king_on_pantera_leoman', 0x198), 'king_on_pantera_leoman');
  // Undefined in both banks: no bank, so the caller keeps its fallback.
  assert.equal(reactionSlotBank(R, 'paul', 'king_on_pantera_leoman', 0x9999), null);
});

test('all 22 banks exist and every bank plans the KO collapse slot', () => {
  assert.equal(Object.keys(R.banks).length, 22);
  for (const [dir, bank] of Object.entries(R.banks)) {
    assert.ok(bank.slots['0xd66'], `${dir} plans collapse slot 0xd66`);
  }
  assert.equal(R.collapse_slot, 3430);
});

test('wall splat is UNMAPPED: the decoded records carry no wall field', () => {
  // If a future decode adds one, this test fails loudly and the
  // wiring can be extended from the file — until then no wall
  // reaction is invented.
  assert.ok(!R.record_fields.some((f) => f.includes('wall')));
});

test('King pack bakes the slots this test selects', () => {
  const packPath = new URL(
    '../game/assets/anim/t3/king_on_pantera_leoman/reactions.pack.json', import.meta.url);
  assert.ok(existsSync(packPath), 'King reactions.pack.json must be in the repo');
  const pack = JSON.parse(readFileSync(packPath, 'utf8'));
  for (const key of ['0x8b8', '0x9fc', '0xa85', '0xa49', '0xd66', '0x3']) {
    assert.ok(pack.rows[key], `King pack is missing slot ${key}`);
  }
  assert.equal(pack.rows['0x8b8'].slot, 2232);
});

/* T3 throw-pair selection tests (grapple lane, 2026-10-24).
   Run: node --test test/t3-throw.test.mjs
   Reads the real decoded tables in game/assets/anim/t3/reactions.json.
   Nothing here invents a pairing: every expected slot, window and
   damage frame is read from the file in the test itself or asserted
   against the file's own values (see docs/anim/T3-THROW-WIRING-2026-10-24.md). */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import {
  selectThrow, resolveThrowClips, throwBreaks, throwDamageTimeSec,
  throwPairDurationSec, escapePairFor, attemptRowForInput,
  situationCode, branchAccepts, anchorAt, sharedFramePos, hexSlot,
} from '../game/js/t3-throw.js';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const R = JSON.parse(readFileSync(join(root, 'game/assets/anim/t3/reactions.json'), 'utf8'));
const KING = 'king_on_pantera_leoman';
const JIN = 'jin';
const SCALE = 0.000829923; // King pack anchor_mm_to_rig_m (reactions.pack.json)

test('King LP1+LK3 front: attempt row 273 -> throw slot 2795, victim 3018', () => {
  assert.equal(attemptRowForInput(R, KING, '1+3'), 273);
  const sel = selectThrow(R, KING, 273, { posture: 'standing', quadrant: 0, distanceM: 1.0, anchorScale: SCALE });
  assert.equal(sel.throw.slot, 2795);
  assert.equal(sel.throw.damage, 35);
  assert.deepEqual(sel.throw.damage_frames, [61]);
  assert.equal(sel.throw.victim_slot, 3018);
  assert.equal(throwDamageTimeSec(sel.throw), 61 / 60);
  assert.equal(throwPairDurationSec(sel.throw), 131 / 60);
  const brk = throwBreaks(sel.throw);
  assert.deepEqual(brk, [{ input: '1', label: 'LP1', windowSec: [1 / 60, 15 / 60], escapeSlot: 2898 }]);
  const clips = resolveThrowClips(R, sel.throw, KING, JIN);
  assert.equal(clips.throwerBank, KING);
  assert.equal(clips.throwerSlot, 2795);
  // Jin's bank does not define victim slot 3018, so the victim clip
  // comes from the thrower's (King's) bank, per DivmotMergeSharedSlots.
  assert.equal(clips.victimBank, KING);
  assert.equal(clips.victimSlot, 3018);
});

test('King RP2+RK4 front: attempt row 274 -> throw slot 2797', () => {
  assert.equal(attemptRowForInput(R, KING, '2+4'), 274);
  const sel = selectThrow(R, KING, 274, { posture: 'standing', quadrant: 0, distanceM: 1.0, anchorScale: SCALE });
  assert.equal(sel.throw.slot, 2797);
});

test('situation branches: side and back pick different throws, crouch does not match a standing attempt', () => {
  const side = selectThrow(R, KING, 273, { posture: 'standing', quadrant: 1, distanceM: 1.0, anchorScale: SCALE });
  assert.equal(side.throw.slot, 2798);
  const back = selectThrow(R, KING, 273, { posture: 'standing', quadrant: 2, distanceM: 1.0, anchorScale: SCALE });
  assert.equal(back.throw.slot, 2800);
  const crouch = selectThrow(R, KING, 273, { posture: 'crouching', quadrant: 0, distanceM: 1.0, anchorScale: SCALE });
  assert.equal(crouch.throw, null);
  assert.match(crouch.reason, /UNMAPPED/);
});

test('distance gate: beyond the file param the throw does not connect', () => {
  const sel = selectThrow(R, KING, 273, { posture: 'standing', quadrant: 0, distanceM: 2.0, anchorScale: SCALE });
  assert.equal(sel.throw, null);
});

test('unknown attempt row is UNMAPPED, never a guessed pair', () => {
  const sel = selectThrow(R, KING, 999, { posture: 'standing', quadrant: 0, distanceM: 1.0, anchorScale: SCALE });
  assert.equal(sel.throw, null);
  assert.match(sel.reason, /UNMAPPED/);
});

test('escape pair: breaking 2795 starts slot 2898 with roles swapped', () => {
  const sel = selectThrow(R, KING, 273, { posture: 'standing', quadrant: 0, distanceM: 1.0, anchorScale: SCALE });
  const esc = escapePairFor(R, sel.throw, throwBreaks(sel.throw), KING, JIN);
  assert.equal(esc.throw.slot, 2898);
  assert.equal(esc.throw.damage, 0);
  assert.equal(esc.newThrowerDir, JIN);
  assert.equal(esc.newVictimDir, KING);
  assert.equal(esc.clips.victimSlot, 3063);
});

test('situation codes and 0x14-0x17 aliases', () => {
  assert.equal(situationCode('standing', 0), 2);
  assert.equal(situationCode('standing', 1), 4);
  assert.equal(situationCode('standing', 2), 3);
  assert.equal(situationCode('standing', 3), 5);
  assert.equal(situationCode('crouching', 0), 6);
  assert.equal(situationCode('lying', 0), 10);
  assert.equal(branchAccepts(20, 2), true);
  assert.equal(branchAccepts(20, 6), true);
  assert.equal(branchAccepts(20, 3), false);
  assert.equal(branchAccepts(2, 2), true);
  assert.equal(branchAccepts(2, 6), false);
});

test('shared-frame math: anchor at P, yaw rotation, frame clamping', () => {
  assert.equal(hexSlot(2795), '0xaeb');
  assert.deepEqual(sharedFramePos({ x: 0, z: 0 }, 0, { ax: 0, az: 0 }, SCALE), { x: 0, z: 0 });
  const p = sharedFramePos({ x: 1, z: 2 }, -Math.PI / 2, { ax: 1000, az: 0 }, 0.001);
  assert.ok(Math.abs(p.x - 1) < 1e-9);
  assert.ok(Math.abs(p.z - 3) < 1e-9);
  // Fake pack row: ax/az as base64 int16 [0, 1000, 2000]
  const b64 = (arr) => Buffer.from(new Int16Array(arr).buffer).toString('base64');
  const row = { ax: b64([0, 1000, 2000]), ay: b64([1000, 1000, 1000]), az: b64([0, 0, 0]) };
  assert.deepEqual(anchorAt(row, 1), { ax: 1000, ay: 1000, az: 0 });
  assert.deepEqual(anchorAt(row, 99), { ax: 2000, ay: 1000, az: 0 });
});

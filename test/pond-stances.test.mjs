// Roster-100 Wave 3 item 6 (2026-11-06): Pond stance entries, wired only
// where her own data declares the entry (S9 audit identification):
//  - LAB    via b+3+4 — her T7-layer row for b+3+4 is named "Labyrinth";
//           every playable spelling of the entry (canon / T7 layer / T8
//           layer) enters LAB.
//  - MIST   via 3+4 — her canon row for 3+4 is named "MIST" (move_class
//           stance); the T7-layer spelling is named "Haze" and the T8-layer
//           spelling "Soulzone". HAZ is unified into MIST by stance_alias
//           (the S9 duplicate-spelling mechanism): HAZ rows are renamed
//           duplicates of the canon MIST rows (same names, same data), so
//           the alias slots the two HAZ-only inputs (HAZ.F / HAZ.U) onto
//           MIST.F / MIST.U and leaves the canon MIST rows owning the
//           five shared strike inputs.
//  - STRIDE via qcf — her canon row for qcf is named "WATER STRIDE"
//           (the T7/T8 spellings are named "Shadow Sprint").
//  - SZN / DEEP / REV / RAGE declare NO entry anywhere in her data and
//    stay NO ENTRY (documented in the handoff record, not wired).
// Run: node --test test/pond-stances.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const M = await import(join(ROOT, 'game/js/movesets.js'));
const MS = join(ROOT, 'game/assets/movesets');
const load = (fid) => { const d = JSON.parse(fs.readFileSync(join(MS, fid + '.json'), 'utf8')); M.registerMoveset(fid, d); return d; };

const pond = load('pond');
const buf = () => new M.TekkenBuffer('pond');

test('pond declares exactly the S9-identified entries, keyed on every playable spelling', () => {
  assert.deepEqual(pond.stance_after, {
    'b+3+4': 'LAB', 'b+3+4~t7.masterraven': 'LAB', 'b+3+4~t8.raven': 'LAB',
    '3+4': 'MIST', '3+4~t7.masterraven': 'MIST', '3+4~t8.raven': 'MIST',
    qcf: 'STRIDE', 'qcf~t7.masterraven': 'STRIDE', 'qcf~t7.masterraven.2': 'STRIDE', 'qcf~t8.raven': 'STRIDE',
  });
  assert.deepEqual(pond.stance_alias, { HAZ: 'MIST' });
  for (const [key, stance] of Object.entries(pond.stance_after)) {
    assert.ok(buf().resolveKey(key), `entry key ${key} resolves to a real row`);
    assert.ok(Object.keys(pond.moves).some((k) => k.startsWith(stance + '.') || k.startsWith(stance + ' ')),
      `${stance} rows exist in her file`);
  }
});

test('the entry rows are the ones her data names as the entries', () => {
  assert.equal(pond.moves['b+3+4~t7.masterraven'].name, 'Labyrinth');
  assert.equal(pond.moves['3+4~t7.masterraven'].name, 'Haze');
  assert.equal(pond.moves['3+4'].name, 'MIST');
  assert.equal(pond.moves.qcf.name, 'WATER STRIDE');
  assert.equal(pond.moves['b+3+4'].move_class, 'stance');
  assert.equal(pond.moves['3+4'].move_class, 'stance');
  assert.equal(pond.moves.qcf.move_class, 'stance');
});

test('stance rows resolve through the buffer under their entered stance, and only there', () => {
  assert.equal(buf().press('1', { stance: 'LAB' }), 'LAB.1');
  assert.equal(buf().press('1', { stance: 'MIST' }), 'MIST.1');
  assert.equal(buf().press('1', { stance: 'STRIDE' }), 'STRIDE.1');
  assert.equal(buf().press('1', {}), '1', 'a neutral press stays the neutral jab (candidate)');
  assert.equal(buf().resolveKey('1'), '1~t8.raven', 'the neutral jab resolves to its own row, not a stance row');
});

test('HAZ alias: HAZ-only inputs slot onto MIST; canon MIST rows keep their own slots', () => {
  assert.equal(buf().resolveKey('MIST.F'), 'HAZ.F');
  assert.equal(buf().resolveKey('MIST.U'), 'HAZ.U');
  assert.equal(buf().resolveKey('MIST.1'), 'MIST 1', 'the canon MIST row owns MIST.1 (the HAZ twin does not overwrite it)');
  assert.equal(buf().resolveKey('HAZ.1'), 'HAZ.1', 'the HAZ spelling itself still resolves');
});

test('SZN / DEEP / REV / RAGE declare no entry and stay unwired', () => {
  const values = Object.values(pond.stance_after);
  for (const p of ['SZN', 'DEEP', 'REV', 'RAGE']) {
    assert.ok(!values.includes(p), `${p} is not entered by any declared entry`);
    assert.ok(Object.keys(pond.moves).some((k) => k.startsWith(p + '.') || k.startsWith(p + ' ')),
      `${p} rows still exist in her data (documented NO ENTRY, not deleted)`);
  }
  // SZN.B "Blind Labyrinth" is a FROM-SZN row (input 'SZN.B'): it cannot be an entry.
  assert.equal(pond.moves['SZN.B']?.input, 'SZN.B');
});

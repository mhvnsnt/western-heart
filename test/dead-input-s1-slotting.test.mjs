// Roster-100 S1 (docs/movesets/DEAD-INPUT-S1-DIAGNOSIS-2026-11-05.md):
// charger d/f+2 was a binding/label gap — bryan bank row 149 sits in
// charger.json (and charger-attire2.json) under the key '2_r149' with its
// direction dropped by the 2026-10-20 merge (recorded t3_command 'RP',
// input_slots ['2'], bound to no playable input). The repair gives the row
// back the bank's own identity for it: key, name, input and hit_words key
// become 'd/f+2' and t3_command '3+RP' — exactly the shape skull.json's
// record of the same bank row carries. No fight datum (damage / startup /
// active / recovery / anim_ref) changed.
// The other six S1 slots are documented data gaps (bank row absent from the
// fighter's merged file, or absent from the source bank entirely). The
// assertions below pin them UNRESOLVED so no future change can silently
// fabricate a row — filling them is the owner's import decision (the #1560
// class-D pattern), not a slotting fix.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const _ls = {}; globalThis.localStorage = { getItem: (k) => _ls[k] ?? null, setItem: (k, v) => { _ls[k] = String(v); }, removeItem: (k) => { delete _ls[k]; } };
const M = await import('../game/js/movesets.js');
const load = (id) => {
  const raw = fs.readFileSync(new URL(`../game/assets/movesets/${id}.json`, import.meta.url), 'utf8');
  M.registerMoveset(id, JSON.parse(raw));
};

test('charger d/f+2 fires the bryan r149 row already present in his file', () => {
  load('charger');
  assert.equal(M.resolveMoveKey('charger', 'd/f+2'), 'd/f+2');
  const mv = M.getFighterMoveset('charger').moves['d/f+2'];
  assert.equal(mv.t3_row, 149);
  assert.equal(mv.t3_command, '3+RP');
  assert.equal(mv.damage, 9);
  assert.equal(mv.move_class, 'strike');
  // neighbours untouched: the mislabeled row was bound to no playable input
  assert.equal(M.resolveMoveKey('charger', '2'), '2');
  assert.equal(M.resolveMoveKey('charger', 'd+1'), '7');
  assert.equal(M.resolveMoveKey('charger', 'd+2'), '8');
  assert.equal(M.resolveMoveKey('charger', 'd/f+1+2'), 'df+1+2');
  assert.equal(M.resolveMoveKey('charger', 'u/f+4'), 'f_c36_r86');
});

test('charger-attire2 d/f+2 fires the same row (identical mislabel, identical repair)', () => {
  load('charger-attire2');
  assert.equal(M.resolveMoveKey('charger-attire2', 'd/f+2'), 'd/f+2');
  assert.equal(M.resolveMoveKey('charger-attire2', 'd+1'), '7');
});

test('the six S1 data gaps stay unresolved — no fabricated rows', () => {
  load('charger');
  assert.equal(M.resolveMoveKey('charger', 'd/f+1'), null); // bryan r146 never entered his merge
  load('dorowani');
  assert.equal(M.resolveMoveKey('dorowani', 'd/f+2'), null); // gon bank has no 3+RP attack row
  assert.equal(M.resolveMoveKey('dorowani', 'u/f+4'), null); // gon bank has no 9+RK attack row
  assert.equal(M.resolveMoveKey('dorowani', 'd/f+1'), 'd/f+1'); // neighbour intact
  load('ryuji-rock');
  assert.equal(M.resolveMoveKey('ryuji-rock', 'd/f+1'), null); // king r117 not in his curated build
  assert.equal(M.resolveMoveKey('ryuji-rock', 'd/f+2'), null); // king r202 not in his curated build
  assert.equal(M.resolveMoveKey('ryuji-rock', 'd/f+1+2'), 'd/f+1+2'); // Rock Bottom throw intact
  load('deathfang');
  assert.equal(M.resolveMoveKey('deathfang', 'd/f+1'), null); // heihachi r109 not in his curated merge
  assert.equal(M.resolveMoveKey('deathfang', 'd/f+2'), '29'); // neighbour intact
});

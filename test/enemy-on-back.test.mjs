// Enemy-on-back ground throws (docs/proof/moveset-sweep-20261028/r17-core8-failing.json):
// Pantera t7.king_231-235 '(Enemy on back) by the feet/head/side... d/b+1+3 (or d/b+2+4)'
// are ground throws on a downed opponent lying on their back (face up) — the face-up
// mirror of king_236-239 '(Enemy face down)...', which the sweep already n/a's via its
// Face (Up|Down) pattern. The game has no face-up/face-down ground-orientation move state
// (the sweep page's own comment above the n/a list), so the honest treatment is the same
// n/a with the missing state named, never a pass and never a canon strip that would make
// the sweep attempt these throws standing, where they cannot fire.
// This test reads the REAL sweep page source and reconstructs its n/a patterns, so
// removing the pattern fails the test. Residual, stated plainly: this is an n/a
// reclassification, not a witnessed pass — the next sweep moves the 5 rows from the
// failing list to n/a, and a ground-orientation throw witness remains a follow-up.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const pageSrc = readFileSync(new URL('./e2e/moveset-sweep.page.js', import.meta.url), 'utf8');

function naEntries() {
  const start = pageSrc.indexOf('const NA = ');
  assert.notEqual(start, -1, 'sweep page has no n/a list');
  const end = pageSrc.indexOf(']];', start);
  assert.notEqual(end, -1, 'sweep page n/a list has no closing ] ];');
  const block = pageSrc.slice(start, end + 2);
  const entries = [];
  const re = /\/((?:\\.|[^\/])+)\/([a-z]*)\s*,\s*'([^']+)'/g;
  let m;
  while ((m = re.exec(block)) !== null) entries.push({ rx: new RegExp(m[1], m[2]), label: m[3] });
  assert.ok(entries.length >= 4, `expected at least the 4 original n/a entries, got ${entries.length}`);
  return { block, entries };
}

const ROWS = [
  ['t7.king_231', '(Enemy on back) by the feet... d/b+1+3 (or d/b+2+4)'],
  ['t7.king_232', '(Enemy on back) by the feet... D/B+1+3'],
  ['t7.king_233', '(Enemy on back) by the feet... D/B+2+4'],
  ['t7.king_234', '(Enemy on back) by the head... d/b+1+3 (or d/b+2+4)'],
  ['t7.king_235', "(Enemy on back) by enemy's side... d/b+1+3 (or d/b+2+4)"],
];

test('sweep page n/a list gains the parenthesised Enemy-on-back pattern with the face-up/face-down ground label', () => {
  const { entries } = naEntries();
  const eob = entries.find((e) => e.rx.source.includes('Enemy on back'));
  assert.ok(eob, 'no n/a entry matches Enemy on back');
  assert.equal(eob.label, 'face-up/face-down ground');
});

test('all five Enemy-on-back rows are caught by that pattern on key + input, as the sweep gate tests them', () => {
  const { entries } = naEntries();
  const eob = entries.find((e) => e.rx.source.includes('Enemy on back'));
  for (const [key, input] of ROWS) assert.ok(eob.rx.test(`${key} ${input}`), `${key} not matched`);
});

test('the n/a gate runs before the sweep parses a row, so a caught row never reaches parse', () => {
  const gate = pageSrc.indexOf('for (const [re, st] of NA)');
  const parse = pageSrc.indexOf('const P = parse(notation)');
  assert.ok(gate !== -1 && parse !== -1 && gate < parse, 'n/a gate must precede parse');
});

test('guards: the Enemy-on-back pattern does not swallow neighbouring classes', () => {
  const { entries } = naEntries();
  const eob = entries.find((e) => e.rx.source.includes('Enemy on back'));
  const notMatched = [
    't7.king_236 (Enemy face down) by the feet... d/b+1+3 (or d/b+2+4)',
    't7.king_110 b+2, 4 (only during hit from front)',
    't7.king_247 During enemy wall stun... f, hcf+1',
    't7.king_229 Approach crouching enemy... d+1+3',
    '(back to wall).b,b,UB',
  ];
  for (const t of notMatched) assert.ok(!eob.rx.test(t), `pattern wrongly matches: ${t}`);
  // ...while the face-down twin is still caught by the pre-existing Face pattern.
  const face = entries.find((e) => e.rx.source.includes('Face'));
  assert.ok(face && face.rx.test(notMatched[0]), 'face-down twin lost its Face-pattern n/a');
});

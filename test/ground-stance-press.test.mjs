// Ground-stance + GROUNDED resolver proof (Lane C, 2026-11-20). Node, no DOM.
// Run: node --test test/ground-stance-press.test.mjs
// What it proves, through the game's own TekkenBuffer (nothing stubbed):
//  - each of the four canonical grounded orientations (FUFT./FUFA./FDFT./FDFA.)
//    fires from the knockdown-exit stance window: the fighter leaves a knockdown,
//    fighter.js:4503-4517 sets ctx.stance to the orientation for 0.6 s, and
//    _pressV2's generic stance line (movesets.js:1279) resolves the row.
//    The test drives exactly that signal (ctx.stance), in V2 AND legacy.
//  - GROUNDED. (the generic getup-attack fallback, new guarded line in both
//    _pressV2 and _pressLegacy) fires when ctx.grounded is set, never fires
//    without it, and loses to the specific orientation when one matches
//    (most specific first) — but IS the fallback when no orientation row
//    matches. ctx.grounded itself is fed by Fighter._inputCtx (PROPOSED
//    fighter.js change, not yet live); this test proves the resolver half.
//  - REV.b+1+3 resolves through the same generic stance line when a REV
//    stance is ever entered (pressChord) — the mechanism, not a claim that
//    any moveset enters REV today (none does: no stance_after is 'REV').
//  - TACKLE. chain data is intact: throwStageKeys still returns the mount
//    follow-ups the throw chain (_throwChainPress) serves.
import test from 'node:test';
import assert from 'node:assert/strict';

const _ls = {};
globalThis.localStorage = { getItem: (k) => _ls[k] ?? null, setItem: (k, v) => { _ls[k] = String(v); }, removeItem: (k) => { delete _ls[k]; } };
globalThis.WH_INPUT_RESOLVER = 'v2';
const M = await import('../game/js/movesets.js');

const GROUND_MS = { moves: {
  '1': { name: 'Standing Jab', input: '1' },
  '3': { name: 'Standing Kick', input: '3' },
  '4': { name: 'Standing Kick 4', input: '4' },
  '1+3': { name: 'Standing Throw', input: '1+3' },
  'FUFT.3': { name: 'Ground Kick (face-up, feet-toward)', input: 'FUFT.3' },
  'FUFA.4': { name: 'Ground Throw (face-up, feet-away)', input: 'FUFA.4' },
  'FDFT.3': { name: 'Ground Throw (face-down, feet-toward)', input: 'FDFT.3' },
  'FDFA.4': { name: 'Ground Kick (face-down, feet-away)', input: 'FDFA.4' },
  'GROUNDED.3': { name: 'Getup Kick (generic)', input: 'GROUNDED.3' },
  'REV.b+1+3': { name: 'Parry', input: 'REV.b+1+3' },
  'TACKLE.1': { name: 'Mount Punch', input: 'TACKLE.1' },
  'TACKLE.1,1': { name: 'Mount Punch x2', input: 'TACKLE.1,1' },
} };
// No FUFT. row at all: the GROUNDED. fallback must catch the press.
const NO_FUFT_MS = { moves: {
  '3': { name: 'Standing Kick', input: '3' },
  'GROUNDED.3': { name: 'Getup Kick (generic)', input: 'GROUNDED.3' },
} };
M.registerMoveset('ground-test', GROUND_MS);
M.registerMoveset('ground-no-fuft', NO_FUFT_MS);

function feed(buf, dir, frames = 4) { for (let i = 0; i < frames; i++) buf.noteDirection(dir); }
function press(id, btn, ctx) { const buf = new M.TekkenBuffer(id); feed(buf, 'n'); return buf.press(btn, ctx); }
function withResolver(resolver, fn) {
  const prev = globalThis.WH_INPUT_RESOLVER;
  globalThis.WH_INPUT_RESOLVER = resolver;
  try { return fn(); } finally { globalThis.WH_INPUT_RESOLVER = prev; }
}

const ORIENTATIONS = [
  ['FUFT', '3', 'FUFT.3'],
  ['FUFA', '4', 'FUFA.4'],
  ['FDFT', '3', 'FDFT.3'],
  ['FDFA', '4', 'FDFA.4'],
];

test('ground orientations fire from the knockdown-exit stance window (V2)', () => {
  for (const [stance, btn, want] of ORIENTATIONS) {
    assert.equal(press('ground-test', btn, { stance }), want,
      `${stance}.${btn} must fire while ctx.stance is ${stance} (fighter.js:4515 window)`);
  }
});

test('ground orientations fire from the knockdown-exit stance window (legacy)', () => {
  withResolver('legacy', () => {
    for (const [stance, btn, want] of ORIENTATIONS) {
      assert.equal(press('ground-test', btn, { stance }), want,
        `${stance}.${btn} must fire under the legacy resolver too (same prefix list)`);
    }
  });
});

test('without the stance, the same buttons give the standing moves', () => {
  assert.equal(press('ground-test', '3', {}), '3');
  assert.equal(press('ground-test', '4', {}), '4');
  assert.equal(press('ground-test', '3', { stance: 'FUFT' }), 'FUFT.3');
  // a stance with no row for the button falls through to standing, not to GROUNDED.
  assert.equal(press('ground-test', '4', { stance: 'FUFT' }), '4');
});

test('GROUNDED. fires when ctx.grounded is set, never without it (V2 + legacy)', () => {
  for (const resolver of ['v2', 'legacy']) {
    withResolver(resolver, () => {
      assert.equal(press('ground-test', '3', { grounded: true }), 'GROUNDED.3',
        `GROUNDED.3 must fire with ctx.grounded under ${resolver}`);
      assert.equal(press('ground-test', '3', {}), '3',
        'GROUNDED.3 must never fire without ctx.grounded (guard holds)');
      assert.equal(press('ground-test', '3', { grounded: false }), '3');
    });
  }
});

test('specific orientation shadows GROUNDED.; GROUNDED. is the fallback when no row matches', () => {
  assert.equal(press('ground-test', '3', { stance: 'FUFT', grounded: true }), 'FUFT.3',
    'FUFT.3 (specific) must beat GROUNDED.3 (generic) for the same input');
  assert.equal(press('ground-no-fuft', '3', { stance: 'FUFT', grounded: true }), 'GROUNDED.3',
    'with no FUFT.3 row, the grounded press must fall back to GROUNDED.3');
});

test('REV.b+1+3 resolves through the generic stance line when a REV stance is entered', () => {
  const buf = new M.TekkenBuffer('ground-test');
  feed(buf, 'n'); feed(buf, 'b', 2);
  assert.equal(buf.pressChord('1+3', { stance: 'REV' }), 'REV.b+1+3',
    'REV chord must resolve via the stance line (mechanism only — no moveset enters REV today)');
  const plain = new M.TekkenBuffer('ground-test');
  feed(plain, 'n'); feed(plain, 'b', 2);
  assert.equal(plain.pressChord('1+3', {}), '1+3',
    'without the REV stance the same chord is the standing throw');
});

test('TACKLE. chain data intact: throwStageKeys still returns the mount follow-ups', () => {
  assert.deepEqual(M.throwStageKeys('ground-test', 'TACKLE'), ['TACKLE.1', 'TACKLE.1,1']);
});

// Pantera King T7 string steps (2026-11-10, t386u). Node, no browser.
// Run: node --test test/t7-king-strings.test.mjs
// tools/anim/t7_move_resolve.py --strings maps a T7 string-step row ('(1), 2' = the 2 of 1,2) by walking King's
// cancel graph from Kg_sKAM00_ and checking the step's own damage + first active frame; t7_move_bake.py baked those
// clips into game/assets/anim/t7/king/moves.pack.json. This asserts the game's own clip plan (Fighter._attackClipPlan,
// T7 pack loaded as at boot) plays each string's exact motbin move, and that nothing else is caught by the new map.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const THREE = await import('three');
const M = await import(join(ROOT, 'game/js/movesets.js'));
const T = await import(join(ROOT, 'game/js/t3anims.js'));
const F = await import(join(ROOT, 'game/js/fighter.js'));
const FT = await import(join(ROOT, 'game/js/frame-tables.js'));
await FT.frameTablesReady;
const q = console.log, qw = console.warn; console.log = () => {}; console.warn = () => {};
await M.loadFighterMovesets(); await M.ensureMovesets(['pantera']);
const bank = F.bankIdFor('pantera', 'pantera');
const clips = await T.loadT3Clips(THREE, bank);
await T.ensureT7Moves('pantera', THREE);
console.log = q; console.warn = qw;
const pack = JSON.parse(readFileSync(join(ROOT, 'game/assets/anim/t7/king/moves.pack.json'), 'utf8'));

function fighter() {
  const f = Object.create(F.Fighter.prototype);
  Object.assign(f, { char: { id: 'pantera' }, _movesetId: 'pantera', t3actions: {}, _t3: { bank, clips },
    root: { position: { x: 0, y: 0, z: 0 } }, facing: 1, dead: false, stun: 0 });
  return f;
}
const plan = (k) => { const ms = M.getFighterMoveset('pantera'); const mv = F.getRealMove('pantera', k) || ms.moves[k]; return fighter()._attackClipPlan(mv, k); };

// press -> exact motbin move (kinmot.json), per the resolver's verified mapping
const STRINGS = {
  '1,2': 'Kg_lprpF', '1,2,1': 'Kg_rplu6', '2,1': 'Kg_rplu4t', '1+2,1': 'Kg_hizilp', '1+2,3': 'Kg_hizilk',
  'f+2,1': 'Kg_6rplp', 'f+2,d+1,2': 'Kg_6rplprp', 'd/f+1,2': 'Kg_t_slpF03B', 'd/f+2,1': 'Kg_dhook_lp01',
  'd/f+4,3': 'Kg_t_srkF02', 'd/f+4,3,4': 'Kg_t_srkF03', 'd/f+4,3,d+4': 'Kg_t_srkF04', 'b+1,2': 'Kg_rpTap00',
  'b+2,1': 'Kg_4rplp', 'b+2,4': 'Kg_AmericaRK',
};

test('every string press plays its exact King T7 motbin move clip', () => {
  for (const [press, motbin] of Object.entries(STRINGS)) {
    const p = plan(press);
    assert.ok(p && String(p.name).startsWith('t7:'), `${press}: plan ${p && p.name} is not a King T7 clip`);
    const key = String(p.name).slice(3);
    assert.equal(pack.moves[key].motbin_move, motbin, `${press}: ${key}`);
    assert.equal(pack.moves[key].input, press);
  }
});

test('the 29 single-input King T7 moves are still in the pack unchanged in kind', () => {
  const singles = Object.keys(pack.moves).filter((k) => !pack.moves[k].input.includes(','));
  assert.equal(singles.length, 29);
});

test('string normalizer: motions, suffixed keys and single inputs never map', () => {
  for (const x of ['f,F+1', 'f,f,F+3', '1,2~t7.king', '1', 'WS.1,2', 'SS.1,2', 'qcf+1,2']) assert.equal(T.t7NormString(x), null, x);
  assert.equal(T.t7NormString('df+1, 2'), 'd/f+1,2');
});

test('a gated clip stays out with its reason (no substitute)', () => {
  assert.match(pack.skipped['d+3+4,4~t7.king.2'], /plausibility gate/);
  const p = plan('d+3+4,4');
  assert.ok(!p || !String(p.name).startsWith('t7:'));
});

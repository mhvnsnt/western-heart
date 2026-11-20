// Pantera throw victim clip (throw-fix Lane A, 2026-11-19).
// Run: node --test test/throw-victim-pair.test.mjs
// Node, no browser. Proves _throwPairFor selects the FILE's throw pair for
// Pantera's 1+3 / 2+4 even when the attack clip plan names the REACH clip's
// bank row — the shape the live browser has (retarget succeeds, so the plan
// name stays 'row:127' / 'row:128').
//
// REGRESSION (owner complaint 2026-11-19, 2+4 video): the victim played NO
// clip — frozen while the throw ran. Root cause, proven by
// lane-a-victimclip/probe-victimclip.mjs on the real tables at 01c95363:
// the plan's row is the reach clip's bank row (moveset t3_row 127/128), NOT
// the file's attempt row. Row 127 has NO throw branches (1+3 never pairs —
// legacy lock, victim frozen); row 128 selects a GENERIC throw (slot 398,
// row 150, jin-bank victim 399), not King's 2+4 (slot 2797, row 417,
// victim 3051). The file's own throw_inputs maps the pressed chord to the
// attempt row (1+3 -> 273, 2+4 -> 274); it is authoritative for these two
// chords, so _throwPairFor tries it FIRST.
//
// FIXTURE BOUNDARY (same as throw-chain.test.mjs): the throw STATE MACHINE
// runs for real (_throwPairFor / _bindThrowPair pack-row binding); the T3
// clip RETARGET step is stubbed by pre-seeding t3actions with the exact slot
// names _throwPairFor selected (selection itself is real; only the retarget
// of the clip onto a rig is skipped). The victim clip actually playing on
// screen is proven by the headless capture (Lane C), not here.
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
const { bankDirOf } = await import(join(ROOT, 'game/js/t3-throw.js'));

const quiet = { log: console.log, warn: console.warn };
console.log = () => {}; console.warn = () => {};
await M.loadFighterMovesets();
await M.ensureMovesets(['pantera', 'bf-cody']);
if (!M.getFighterMoveset('bf-cody')) {
  M.registerMoveset('bf-cody', JSON.parse(readFileSync(join(ROOT, 'game/assets/movesets/bf-cody.json'), 'utf8')));
}
globalThis.WH_T3_REACTIONS = JSON.parse(readFileSync(join(ROOT, 'game/assets/anim/t3/reactions.json'), 'utf8'));
const kingClips = await T.loadT3Clips(THREE, 'king');
const jinClips = await T.loadT3Clips(THREE, 'jin');
await T.loadReactionPack(THREE, 'king');
await T.loadReactionPack(THREE, 'jin');
console.log = quiet.log; console.warn = quiet.warn;

const hex = (s) => '0x' + Number(s).toString(16);

function makeFighter(id, { bank = null, x = 0 } = {}) {
  const clips = bank === 'king' ? kingClips : bank === 'jin' ? jinClips : null;
  const f = Object.create(F.Fighter.prototype);
  f.char = { id };
  f._movesetId = id;
  f.t3actions = {};
  f._t3 = bank ? { bank, clips, model: null, modelKey: 'probe', dir: bankDirOf(T.T3_BANKS[bank]) } : null;
  f.tekken = new M.TekkenBuffer(id);
  f.root = { position: { x, y: 0, z: 0 } };
  f.facing = 1; f.state = 'idle'; f.stateT = 0; f.stance = null; f.stanceT = 0;
  f.hp = 1000; f.maxHp = 1000; f.meter = 0; f.maxMeter = 100;
  f.stats = { power: 1, defense: 1 }; f.soulMeterMult = 1;
  f.attack = null; f.attackName = null; f._atkPlan = null; f._attackId = 0;
  f._clock = 0; f.lockT = 0; f.lockMove = null; f.lockPartner = null; f.lockVictim = null;
  f._throwPair = null; f._throwPairT = 0; f._throwHitDone = false; f._throwEscaped = false;
  f._throwFollow = null; f._chainFrom = null; f._chainNext = null; f._chainSeq = []; f._chainOpen = false;
  f._chainPressT = 0; f._stepChain = null; f._queuedNext = null; f._queuedAfter = null;
  f.hasHit = false; f.stun = 0; f.invuln = 0; f.vx = 0; f.vz = 0; f.vy = 0;
  f.onGround = true; f.dead = false; f._bt = false; f._risingT = 0;
  f._stringGraceUntil = 0; f._prevAtkT = 0; f._attackPhase = null;
  f._opp = null; f.brawler = false; f.surgeForm = false; f.equippedItems = [];
  f._t3Whiff = 0; f.combo = 0; f._throwVictim = null; f._throwMove = null;
  f._throwAttacker = null; f._pressBuf = null;
  f._animate = () => {};
  f.blob = { position: { x: 0, y: 0, z: 0 }, scale: { set() {} }, material: { opacity: 1 } };
  return f;
}

function versus() {
  const a = makeFighter('pantera', { bank: 'king', x: 0 }); a.facing = 1;
  const v = makeFighter('bf-cody', { bank: 'jin', x: 1.0 }); v.facing = -1;
  return [a, v];
}

// The browser-shaped plan: after a successful retarget the plan name stays
// 'row:<reach row>' (in node the retarget stub nulls it, which is why the
// old throw-chain tests passed while the live game never paired).
function browserPlan(attacker, input) {
  const move = F.getRealMove('pantera', input);
  const row = input === '1+3' ? 127 : 128;
  attacker.attack = move; attacker.attackName = input;
  attacker._atkPlan = { id: 1, move, name: 'row:' + row, kind: 'notation', stepBank: null, stepRow: null };
  return move;
}

function seedPairActions(thrower, victim, pair) {
  thrower.t3actions['throw:' + hex(pair.clips.throwerSlot)] = { stub: true };
  victim.t3actions['victim:' + hex(pair.clips.victimSlot)] = { stub: true };
}

test('1+3 with browser plan row:127 selects the file pair 2795 + victim clip 3018', () => {
  const [a, v] = versus();
  const move = browserPlan(a, '1+3');
  const res = a._throwPairFor(move, v);
  assert.ok(res.pair, `pair selected (got: ${res.reason || 'none'})`);
  assert.equal(res.pair.throw.slot, 2795);
  assert.equal(res.pair.throw.row, 415);
  assert.equal(res.pair.throw.victim_slot, 3018);
  assert.equal(res.pair.clips.throwerBank, 'king_on_pantera_leoman');
  assert.equal(res.pair.clips.victimBank, 'king_on_pantera_leoman');
  assert.equal(res.pair.clips.victimSlot, 3018);
  assert.deepEqual(res.pair.throw.damage_frames, [61]);
  assert.deepEqual(res.pair.breaks, [{ input: '1', label: 'LP1', windowSec: [1 / 60, 15 / 60], escapeSlot: 2898 }]);
  seedPairActions(a, v, res.pair);
  assert.equal(a._bindThrowPair(res.pair, v), true, 'pair binds');
  assert.equal(res.pair.throwerAction, 'throw:0xaeb');
  assert.equal(res.pair.victimAction, 'victim:0xbca', 'victim has a real clip action, never a frozen pose');
});

test('2+4 with browser plan row:128 selects the file pair 2797 + victim clip 3051 (not generic 398)', () => {
  const [a, v] = versus();
  const move = browserPlan(a, '2+4');
  const res = a._throwPairFor(move, v);
  assert.ok(res.pair, `pair selected (got: ${res.reason || 'none'})`);
  assert.equal(res.pair.throw.slot, 2797);
  assert.equal(res.pair.throw.row, 417);
  assert.equal(res.pair.throw.victim_slot, 3051);
  assert.equal(res.pair.clips.throwerBank, 'king_on_pantera_leoman');
  assert.equal(res.pair.clips.victimBank, 'king_on_pantera_leoman');
  assert.equal(res.pair.clips.victimSlot, 3051);
  assert.deepEqual(res.pair.throw.damage_frames, [65]);
  assert.deepEqual(res.pair.breaks, [{ input: '2', label: 'RP2', windowSec: [1 / 60, 15 / 60], escapeSlot: 2898 }]);
  seedPairActions(a, v, res.pair);
  assert.equal(a._bindThrowPair(res.pair, v), true, 'pair binds');
  assert.equal(res.pair.throwerAction, 'throw:0xaed');
  assert.equal(res.pair.victimAction, 'victim:0xbeb', 'victim has a real clip action, never a frozen pose');
});

test('pair durations are the file pair durations (victim clip runs the whole throw)', () => {
  const [a, v] = versus();
  const m1 = browserPlan(a, '1+3');
  const r1 = a._throwPairFor(m1, v);
  assert.equal(r1.pair.durationSec, Math.max(131, 130) / 60);
  const [a2, v2] = versus();
  const m2 = browserPlan(a2, '2+4');
  const r2 = a2._throwPairFor(m2, v2);
  assert.equal(r2.pair.durationSec, Math.max(108, 103) / 60);
});

test('non-1+3/2+4 throws keep the plan-row path (no over-broadening)', () => {
  // '1+3,1' has no throw_inputs entry: the plan row is still used, and a
  // plan row with no throw branches still reports UNMAPPED the old way.
  const [a, v] = versus();
  const move = F.getRealMove('pantera', '1+3,1');
  a.attack = move; a.attackName = '1+3,1';
  a._atkPlan = { id: 1, move, name: 'row:415', kind: 'notation', stepBank: null, stepRow: null };
  const res = a._throwPairFor(move, v);
  assert.equal(res.pair, null);
  assert.match(res.reason, /attempt row 415 has no throw branches/);
});

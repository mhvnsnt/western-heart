// Pantera grapple chains + opponent reactions (grapple lane, 2026-11-18).
// Run: node --test test/throw-chain.test.mjs
// Node, no browser. Proves the multi-throw chain runtime executes in-game
// (per-link damage, break windows, escape pairs, bankless fallback) on the
// clips that exist today (T3 pairs now; T7 when wired — see the T7 throw
// table in docs; no T3 clip is ever relabelled as T7 here).
//
// FIXTURE BOUNDARY (stated, not hidden):
// - The throw STATE MACHINE runs for real: _throwPairFor / _bindThrowPair /
//   _startThrowPair / _tickState pair clock / _throwPairDamage / tryThrowBreak /
//   _throwChainPress / _startThrowChain / legacy lock + completeThrow + slam.
// - VISUAL-ONLY stubs: fighter._animate is a no-op (no mixer/rig in node),
//   the shadow blob is a dummy object, and the T3 clip RETARGET step is
//   stubbed by pre-seeding t3actions with the exact slot names
//   _throwPairFor selected (selection itself is real; only the retarget of
//   the clip onto a rig is skipped). Pack-row binding, anchors, break
//   windows, damage frames and durations all come from the real files.
// - The test plays the game.js role: it calls startThrowLock/startThrowing
//   on connect and runs the lock-resolution loop (completeThrow when lockT
//   expires). No KO: hp is 1000 so damage assertions are exact.
// - Banked victim is bf-cody (T3 bank jin, the t3-throw.test.mjs King-vs-Jin
//   fixture). bf-cody.json exists but is NOT in game/assets/movesets/
//   index.json, so it is registered from its file when the index skips it.
// - Bankless victim is zen (bankIdFor returns null by owner decision
//   2026-10-24) — a real roster fighter with no T3 bank.
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
const { bankDirOf, escapePairFor } = await import(join(ROOT, 'game/js/t3-throw.js'));

const quiet = { log: console.log, warn: console.warn };
console.log = () => {}; console.warn = () => {};
await M.loadFighterMovesets();
await M.ensureMovesets(['pantera', 'bf-cody', 'zen']);
if (!M.getFighterMoveset('bf-cody')) {
  M.registerMoveset('bf-cody', JSON.parse(readFileSync(join(ROOT, 'game/assets/movesets/bf-cody.json'), 'utf8')));
}
globalThis.WH_T3_REACTIONS = JSON.parse(readFileSync(join(ROOT, 'game/assets/anim/t3/reactions.json'), 'utf8'));
const kingClips = await T.loadT3Clips(THREE, 'king');
const jinClips = await T.loadT3Clips(THREE, 'jin');
await T.loadReactionPack(THREE, 'king');
await T.loadReactionPack(THREE, 'jin');
console.log = quiet.log; console.warn = quiet.warn;

const DT = 1 / 60;
const hex = (s) => '0x' + Number(s).toString(16);
const dmg = (k) => F.getRealMove('pantera', k).damage;

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

function seedPairActions(thrower, victim, pair) {
  thrower.t3actions['throw:' + hex(pair.clips.throwerSlot)] = { stub: true };
  victim.t3actions['victim:' + hex(pair.clips.victimSlot)] = { stub: true };
}

function seedEscapeActions(victim, attacker, pair) {
  const esc = escapePairFor(globalThis.WH_T3_REACTIONS, pair.throw, pair.breaks, attacker._t3.dir, victim._t3.dir);
  if (!esc) return null;
  victim.t3actions['throw:' + hex(esc.clips.throwerSlot)] = { stub: true };
  attacker.t3actions['victim:' + hex(esc.clips.victimSlot)] = { stub: true };
  return esc;
}

// The game.js connect block (game.js:846-852), driven by the test.
function connectThrow(thrower, victim, notation) {
  assert.equal(thrower.tryAttack(notation), true, `${notation} fires`);
  thrower.hasHit = true;
  const pair = thrower._throwPairFor(thrower.attack, victim);
  if (pair && pair.pair) seedPairActions(thrower, victim, pair.pair);
  victim.startThrowLock(thrower.attack, thrower);
  if (!thrower._throwPair) thrower.startThrowing(victim);
  return pair;
}

// Game.js lock-resolution loop (Stream 6), replicated by the test.
function gameLockTick(atk) {
  if (atk.state === 'throwing' && !atk._throwPair && atk.lockT <= 0 && atk.lockMove) return atk.completeThrow();
  return null;
}

function tickPair(a, v, dt = DT) {
  a.update(dt, v);
  v.update(dt, a);
  gameLockTick(a);
  gameLockTick(v);
}

function versus(banked = true) {
  const a = makeFighter('pantera', { bank: 'king', x: 0 }); a.facing = 1;
  const v = banked
    ? makeFighter('bf-cody', { bank: 'jin', x: 1.0 })
    : makeFighter('zen', { bank: null, x: 1.0 });
  v.facing = -1;
  return [a, v];
}

test('paired 1+3 vs banked victim: damage at the file damage frame, ends idle/knockdown', () => {
  const [a, v] = versus(true);
  const hp0 = v.hp;
  const pair = connectThrow(a, v, '1+3');
  assert.ok(pair.pair, 'pair selected');
  assert.equal(pair.pair.throw.slot, 2795);
  assert.equal(pair.pair.throw.victim_slot, 3018);
  assert.deepEqual(pair.pair.throw.damage_frames, [61]);
  assert.equal(v.state, 'thrown');
  let dmgAt = null;
  for (let i = 0; i < 200; i++) {
    tickPair(a, v);
    if (dmgAt == null && v.hp < hp0) dmgAt = i * DT;
    if (v.state === 'knockdown' && a.state === 'idle') break;
  }
  assert.ok(dmgAt != null && dmgAt >= 0.95 && dmgAt <= 1.1, `damage at frame 61 (~1.017s), got t=${dmgAt}`);
  assert.equal(hp0 - v.hp, dmg('1+3'));
  assert.equal(a.state, 'idle');
  assert.equal(v.state, 'knockdown');
});

test('chain 1+3,1 executes with per-link damage (press 1 mid-throw)', () => {
  const [a, v] = versus(true);
  const hp0 = v.hp;
  connectThrow(a, v, '1+3');
  let pressed = false, startedAt = null, path = null;
  for (let i = 0; i < 400; i++) {
    const t = i * DT;
    if (!pressed && t >= 0.5) { assert.equal(a.tryAttack('1'), true); pressed = true; assert.equal(a._chainNext, '1+3,1'); }
    tickPair(a, v);
    if (startedAt == null && a._chainFrom === '1+3,1') { startedAt = t; path = a._throwPair ? 'pair' : 'legacy'; }
    if (startedAt != null && a.state === 'idle' && v.state === 'knockdown') break;
    if (startedAt == null && a.state === 'idle' && v.state === 'knockdown') break;
  }
  assert.notEqual(startedAt, null, 'chain link started');
  assert.equal(hp0 - v.hp, dmg('1+3') + dmg('1+3,1'), `per-link damage (link path: ${path})`);
  assert.equal(a.state, 'idle');
  assert.equal(v.state, 'knockdown');
});

test('chain 2+4,1 executes with per-link damage', () => {
  const [a, v] = versus(true);
  const hp0 = v.hp;
  const pair = connectThrow(a, v, '2+4');
  assert.equal(pair.pair.throw.slot, 2797);
  let pressed = false, startedAt = null;
  for (let i = 0; i < 400; i++) {
    const t = i * DT;
    if (!pressed && t >= 0.5) { a.tryAttack('1'); pressed = true; assert.equal(a._chainNext, '2+4,1'); }
    tickPair(a, v);
    if (startedAt == null && a._chainFrom === '2+4,1') startedAt = t;
    if (startedAt != null && a.state === 'idle' && v.state === 'knockdown') break;
    if (startedAt == null && a.state === 'idle' && v.state === 'knockdown') break;
  }
  assert.notEqual(startedAt, null, 'chain link started');
  assert.equal(hp0 - v.hp, dmg('2+4') + dmg('2+4,1'));
});

test('AB1 stage chain: first-link damage is NOT dropped when the chain starts (regression)', () => {
  // 2026-11-18: the legacy slam could only land via the thrownExec t>=0.9
  // fallback, and the thrower's chain start landed on the same tick first —
  // _startThrowChain reset the victim to idle, dropping link 1's damage
  // (CD.1+3 dealt 0 of 20). _startThrowChain now settles pending link
  // damage before the reset.
  const [a, v] = versus(true);
  const hp0 = v.hp;
  const m = F.getRealMove('pantera', 'CD.1+3');
  a.attack = { ...m, isGrab: true }; a.attackName = 'CD.1+3'; a._atkPlan = null;
  a.tekken._recordMove('CD.1+3'); a.hasHit = true;
  const pair = a._throwPairFor(a.attack, v);
  assert.equal(pair.pair, null, 'AB1 has no T3 pair (UNMAPPED) — legacy lock');
  v.startThrowLock(a.attack, a);
  if (!a._throwPair) a.startThrowing(v);
  let p1 = false, p2 = false, chainNext = null, startedAt = null;
  for (let i = 0; i < 400; i++) {
    const t = i * DT;
    if (!p1 && t >= 0.4) { a.tryAttack('1'); p1 = true; assert.deepEqual(a._chainSeq, ['1']); }
    if (p1 && !p2 && t >= 0.6) { a.tryAttack('1+2'); p2 = true; chainNext = a._chainNext; }
    tickPair(a, v);
    if (startedAt == null && a._chainFrom === 'AB1.1,1+2') startedAt = t;
    if (startedAt != null && a.state === 'idle' && v.state === 'knockdown') break;
    if (startedAt == null && a.state === 'idle' && v.state === 'knockdown') break;
  }
  assert.equal(chainNext, 'AB1.1,1+2');
  assert.notEqual(startedAt, null, 'AB1 chain link started');
  assert.equal(hp0 - v.hp, dmg('CD.1+3') + dmg('AB1.1,1+2'), 'both links dealt damage');
});

test('break inside the window starts the escape pair; no damage either side; thrower knocked down', () => {
  const [a, v] = versus(true);
  const hpA0 = a.hp, hpV0 = v.hp;
  connectThrow(a, v, '1+3');
  seedEscapeActions(v, a, a._throwPair);
  let broke = null;
  for (let i = 0; i < 300; i++) {
    const t = i * DT;
    if (broke == null && t >= 0.1) broke = v.tryThrowBreak('1');
    tickPair(a, v);
    if (broke && ((a.state === 'knockdown' || a.state === 'idle') && (v.state === 'idle' || v.state === 'knockdown'))) break;
  }
  assert.equal(broke, true, 'correct break inside [1/60, 15/60] succeeds');
  assert.equal(hpV0 - v.hp, 0, 'victim takes no damage after a break');
  // File fact: escape throw slot 2898 has damage 0, damage_frames [] — a
  // broken throw deals NO damage by design; the punish is the escape pair.
  assert.equal(hpA0 - a.hp, 0, 'thrower takes no damage from the escape (file damage 0)');
  assert.equal(a.state, 'knockdown', 'original thrower ends knocked down');
  assert.equal(v.state, 'idle', 'breaker ends idle');
});

test('wrong break input and correct input outside the window are rejected', () => {
  const [a, v] = versus(true);
  connectThrow(a, v, '1+3');
  assert.equal(v.tryThrowBreak('2'), false, 'wrong break input rejected');
  for (let i = 0; i < 25; i++) tickPair(a, v);
  assert.ok((v._throwPairT || 0) > 0.25, 'pair clock past the window end');
  assert.equal(v.tryThrowBreak('1'), false, 'correct input outside the window rejected');
});

test('bankless victim: legacy lock, full damage (never 0), victim visibly lifted', () => {
  const [a, v] = versus(false);
  const hp0 = v.hp;
  const pair = connectThrow(a, v, '1+3');
  assert.equal(pair.pair, null, 'no pair for a bankless victim');
  assert.match(pair.reason, /no T3 bank/);
  assert.equal(a._throwPair, null);
  let maxY = 0;
  for (let i = 0; i < 300; i++) {
    tickPair(a, v);
    if (v.root.position.y > maxY) maxY = v.root.position.y;
    if (v.state === 'knockdown' && a.state === 'idle') break;
  }
  assert.equal(hp0 - v.hp, dmg('1+3'), 'bankless victim takes full throw damage');
  assert.ok(maxY > 1.0, `victim visibly lifted (max Y=${maxY.toFixed(2)}, expect ~1.3)`);
  assert.equal(a.state, 'idle');
  assert.equal(v.state, 'knockdown');
});

test('wrong chain press queues nothing; single-throw damage only', () => {
  const [a, v] = versus(true);
  const hp0 = v.hp;
  connectThrow(a, v, '1+3');
  let pressed = false;
  for (let i = 0; i < 300; i++) {
    const t = i * DT;
    if (!pressed && t >= 0.5) { a.tryAttack('2'); pressed = true; assert.equal(a._chainNext, null); }
    tickPair(a, v);
    if (a.state === 'idle' && v.state === 'knockdown') break;
  }
  assert.equal(hp0 - v.hp, dmg('1+3'));
});

test('_reactionAction with no model bound returns null instead of crashing', () => {
  const f = makeFighter('pantera', { bank: 'king', x: 0 });
  assert.equal(f._t3.model, null);
  assert.equal(f._reactionAction('king', 2795, 'throw:0xaeb'), null);
});

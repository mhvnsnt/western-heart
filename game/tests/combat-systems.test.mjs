/* combat-systems.test.mjs — Simulation tests for the combat-system gaps
 * completed 2026-10-24: Power Crush, Screw/Tornado (once per combo),
 * Wall Splat (distinct from Wall Break), Recoverable Health (white
 * gauge), Soul Urge Engager lists + Dash cancel + timer fix, Item-move
 * gate. Button naming: LP1 = Tekken 1, RP2 = Tekken 2, LK3 = Tekken 3,
 * RK4 = Tekken 4.
 *
 * Pure rules are tested against the REAL combat-core.js (copied into a
 * sandbox so its ESM import resolves). Soul Urge list logic is tested
 * against the REAL soulurge.js with a stubbed audio module. Fighter /
 * game wiring is asserted by source anchor: fighter.js must actually
 * call these functions in receiveHit / _physics / update, because
 * fighter.js itself needs THREE + the full game and cannot be imported
 * headlessly — an anchor regression here means the wiring was dropped
 * even if the pure rule still passes.
 *
 * Run: node --test game/tests/combat-systems.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync, mkdtempSync, cpSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const sandbox = mkdtempSync(join(process.env.TMPDIR || '/tmp', 'wh-combat-systems-'));
cpSync(join(ROOT, 'game/js/combat-core.js'), join(sandbox, 'combat-core.js'));
cpSync(join(ROOT, 'game/js/soulurge.js'), join(sandbox, 'soulurge.js'));
writeFileSync(join(sandbox, 'audio.js'), 'export const audio = { urge() {} };\n');
writeFileSync(join(sandbox, 'package.json'), '{"type":"module"}');
const core = await import(pathToFileURL(join(sandbox, 'combat-core.js')).href);
const { listUrgeEngagers, ensureUrgeMoves, SoulUrge } = await import(pathToFileURL(join(sandbox, 'soulurge.js')).href);

const { hitLevelOf, powerCrushAbsorbs, spinMoveKind, canSpin, shouldWallSplat,
  addToRecoverable, greyRecover, itemMoveAvailable } = core;

// Hit words from combat-core: high 0x412, mid 0x217, low 0x10F, s.mid 0x31F.
const mid = { hitWord: 0x217, damage: 10 };
const high = { hitWord: 0x412, damage: 10 };
const low = { hitWord: 0x10F, damage: 10 };
const smid = { hitWord: 0x31F, damage: 10 };
const grab = { isGrab: true, damage: 20 };
const unblock = { unblockable: true, hitWord: 0x607, damage: 20 };
const pcMove = { powerCrush: true };
const plainMove = {};

test('Power Crush absorbs mid/high/special-mid, loses to low/throw/unblockable', () => {
  assert.equal(powerCrushAbsorbs(pcMove, mid), true);
  assert.equal(powerCrushAbsorbs(pcMove, high), true);
  assert.equal(powerCrushAbsorbs(pcMove, smid), true);
  assert.equal(powerCrushAbsorbs(pcMove, low), false, 'lows interrupt Power Crush (T7)');
  assert.equal(powerCrushAbsorbs(pcMove, grab), false, 'throws beat Power Crush (T7)');
  assert.equal(powerCrushAbsorbs(pcMove, unblock), false);
  assert.equal(powerCrushAbsorbs(plainMove, mid), false, 'unflagged moves do not crush');
  // Unknown level fails closed: it must interrupt, not be absorbed.
  assert.equal(powerCrushAbsorbs(pcMove, { damage: 5 }), false);
  assert.equal(hitLevelOf(mid), 'mid');
  assert.equal(hitLevelOf(low), 'low');
  assert.equal(hitLevelOf(grab), 'throw');
});

test('Screw fires once per combo, only vs an airborne victim; Tornado shares the slot', () => {
  const screw = { screw: true };
  const tornado = { tornado: true };
  assert.equal(spinMoveKind(screw), 'screw');
  assert.equal(spinMoveKind(tornado), 'tornado');
  assert.equal(canSpin(screw, true, false), true);
  assert.equal(canSpin(screw, false, false), false, 'screw needs an airborne victim (T7)');
  assert.equal(canSpin(screw, true, true), false, 'second flagged hit in a combo does not spin');
  assert.equal(canSpin(tornado, true, true), false, 'Tornado cannot follow a spent Screw in the same combo');
  assert.equal(canSpin(plainMove, true, false), false);
});

test('Wall splat triggers on wall contact with inward velocity, and differs from a break', () => {
  assert.equal(shouldWallSplat({ x: 8.4, limit: 8.4, vx: 3.0 }), true);
  assert.equal(shouldWallSplat({ x: -8.4, limit: 8.4, vx: -3.0 }), true);
  assert.equal(shouldWallSplat({ x: 8.4, limit: 8.4, vx: -3.0 }), false, 'moving away from the wall is not a splat');
  assert.equal(shouldWallSplat({ x: 5.0, limit: 8.4, vx: 3.0 }), false, 'mid-stage hits are not splats');
  assert.equal(shouldWallSplat({ x: 8.4, limit: 8.4, vx: 0.2 }), false, 'a crawl into the wall is not a splat');
  // Distinctness: a splat changes no bounds and breaks nothing — the
  // pure helper takes no breakable input at all, by design; the break
  // path lives in stagebreaks.js (checked by the wiring anchors below).
  const stagebreaks = readFileSync(join(ROOT, 'game/js/stagebreaks.js'), 'utf8');
  assert.match(stagebreaks, /_breakWall/);
  assert.doesNotMatch(stagebreaks, /wallsplat/);
});

test('Recoverable pool: chip/power-crush damage pools, attacks recover it, time does not', () => {
  // Blocked chip: hp 100 -> 90, pool 10, invariant hp + pool <= maxHp.
  let pool = addToRecoverable(90, 100, 0, 10);
  assert.equal(pool, 10);
  // Pool is capped by lost health, never exceeds it.
  assert.equal(addToRecoverable(90, 100, 8, 10), 10);
  // Dealing 6 damage recovers 6 of the pool; dealing more recovers the rest, no more.
  let r = greyRecover(90, 100, 10, 6);
  assert.deepEqual(r, { hp: 96, pool: 4, recovered: 6 });
  r = greyRecover(96, 100, 4, 99);
  assert.deepEqual(r, { hp: 100, pool: 0, recovered: 4 });
  // No time-recovery function exists in the pool API: the only way pool
  // shrinks is greyRecover (dealing damage) or the fighter's regen
  // invariant (healed hp eats pool) — both are dealing/healing, not time.
  assert.equal(typeof core.timeRecover, 'undefined');
});

test('Item-move gate: unflagged moves always available, flagged need the item', () => {
  assert.equal(itemMoveAvailable(plainMove, []), true);
  assert.equal(itemMoveAvailable({ requiresItem: 'oni-mask' }, []), false);
  assert.equal(itemMoveAvailable({ requiresItem: 'oni-mask' }, ['oni-mask']), true);
});

test('Soul Urge: per-character engager lists, auto fallback, timer signature', () => {
  const msApiFor = (ms) => ({ playedMoveset: () => ms, getFighterMoveset: () => ms });
  const listed = { moves: {
    'f+1': { damage: 10, knock: 2 }, 'df+2': { damage: 15, knock: 6, move_class: 'strike' },
    'b+4': { damage: 20, knock: 8, move_class: 'strike' } },
    urgeEngagers: ['df+2', 'b+4', 'missing-move'] };
  assert.deepEqual(listUrgeEngagers(listed), ['df+2', 'b+4'], 'explicit list wins, missing entries dropped');
  ensureUrgeMoves('x', msApiFor(listed));
  assert.equal(listed.moves['df+2'].urgeEngager, true);
  assert.equal(listed.moves['b+4'].urgeEngager, true);
  assert.equal(listed.moves['f+1'].urgeEngager, undefined);
  const auto = { moves: {
    '1': { damage: 8, knock: 2, move_class: 'strike' },
    'df+2': { damage: 15, knock: 6, move_class: 'strike' } } };
  ensureUrgeMoves('x', msApiFor(auto));
  assert.equal(auto.moves['df+2'].urgeEngager, true, 'no list -> highest-knock launcher fallback');
  // Timer: SoulUrge.update accepts update(dt) AND the old update(fighter, dt)
  // shape without NaN — the 2026-10-24 game.js double-call bug.
  const calls = [];
  const fakeUi = { setUrge: () => {}, updateUrge: () => {} };
  const game = { p1: { _urgeOn: true, _urgeT: 10, _urgePips: 1, setUrgeAura: () => {} },
    p2: { state: 'idle', onGround: true }, ui: fakeUi };
  const su = new SoulUrge(game);
  su.update(0.5);
  assert.equal(game.p1._urgeT, 9.5);
  game.p1._urgeT = 10;
  su.update(game.p1, 0.5); // old shape: fighter first, dt second
  assert.equal(game.p1._urgeT, 9.5, 'old update(fighter, dt) shape must still tick by dt, not NaN');
});

test('Fighter/game wiring anchors: the pure rules are actually called in the live paths', () => {
  const fighter = readFileSync(join(ROOT, 'game/js/fighter.js'), 'utf8');
  const game = readFileSync(join(ROOT, 'game/js/game.js'), 'utf8');
  const main = readFileSync(join(ROOT, 'game/js/main.js'), 'utf8');
  for (const a of [
    'powerCrushAbsorbs(this.attack, move)', "return 'powercrush'",
    'spinMoveKind(move)', 'canSpin(move, _wasAirborne',
    'shouldWallSplat({ x: this.root.position.x',
    "this._enter('wallsplat')", "case 'screw': case 'tornado': case 'wallsplat'",
    'recoverFromPool', '_recoverable', 'tryUrgeDash',
    "this._attackPhase === 'recovery'", 'itemMoveAvailable(move, this._equippedItems)',
    'powerCrush: !!mv.powerCrush, screw: !!mv.screw, tornado: !!mv.tornado',
  ]) assert.ok(fighter.includes(a), `fighter.js missing anchor: ${a}`);
  assert.ok(game.includes('this.soulurge.update(dt)'), 'game.js must tick Soul Urge once per frame');
  assert.ok(game.includes("result === 'powercrush'"), 'game.js must handle the powercrush result without a combo');
  assert.ok(main.includes('f._recoverable'), 'classic HUD must read the recoverable pool');
  const bridge = readFileSync(join(ROOT, 'game/js/ui-wh-bridge.js'), 'utf8');
  assert.ok(bridge.includes('recoverable'), 'ui-wh bridge must forward the recoverable pool');
});

test('Moveset wiring: only frame-data-proven Pantera moves are flagged', () => {
  const pantera = JSON.parse(readFileSync(join(ROOT, 'game/assets/movesets/pantera.json'), 'utf8'));
  const flagged = Object.entries(pantera.moves)
    .filter(([, m]) => m.powerCrush || m.screw || m.tornado)
    .map(([k]) => k);
  assert.deepEqual(flagged.sort(), ['SS.2', 'db+1+2', 'db+1+2,3+4', 'uf+3+4'].sort(),
    'only wavu-proven moves may be flagged; everything else stays UNMAPPED');
  assert.equal(pantera.moves['db+1+2'].powerCrush, true, 'Muscle Armor pc6~59');
  assert.equal(pantera.moves['SS.2'].screw, true, 'SS 2 Tailspin + on_hit/on_ch S!');
  assert.equal(pantera.moves['SS.2'].on_hit, 'S!');
  // Tornado: engine supports the flag, but no Pantera move has a proven
  // T8 Tornado tag in the data checked — zero tornado flags is correct.
  assert.equal(flagged.some((k) => pantera.moves[k].tornado), false);
  assert.ok(existsSync(join(ROOT, 'game/tests/combat-systems.test.mjs')));
});

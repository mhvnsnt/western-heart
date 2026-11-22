// Practice attack data: a normal fight shows NO hit data; practice shows the reference practice panel's fields.
// Run: node test/practice-attack-data.test.mjs  (plain node, no DOM, no network)
//
// Owner 2026-11-11: "stop adding stuff into the actual fights and combat that are only for debug and practice type
// shit like how much damage a hit is giving popping up big across the screen ... even if it did happen in practice
// u should do it like Tekken ... straight from the games source files". Evidence for the field list and for the
// battle HUD having no hit/damage counter: game/js/practice-attack-data.js header and
// docs/research/2026-11-11-in-fight-hud.md.
import assert from 'assert';
import { readFileSync, existsSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const AD = await import(join(ROOT, 'game/js/practice-attack-data.js'));

let fails = 0;
const check = (name, fn) => { try { fn(); console.log('ok', name); } catch (e) { fails++; console.log('FAIL', name, '-', e.message); } };

// ---------- A. the readout (pure) ----------
check('fields and lamps match the reference panel (5 numbers, 4 lamps)', () => {
  assert.deepEqual(AD.ATTACK_DATA_FIELDS, ['damage', 'comboDamage', 'hits', 'maxComboDamage', 'totalDamage']);
  assert.deepEqual(AD.ATTACK_DATA_LAMPS, ['clean', 'counter', 'wall', 'punish']);
});
check('a combo accumulates; a new combo restarts; max and total keep going', () => {
  const s = AD.newAttackDataSide();
  AD.recordAttackData(s, { kind: 'hit', dealt: 10, combo: 1 });
  assert.deepEqual([s.damage, s.comboDamage, s.hits, s.maxComboDamage, s.totalDamage], [10, 10, 1, 10, 10]);
  AD.recordAttackData(s, { kind: 'counter', dealt: 8.4, combo: 2 });
  assert.deepEqual([s.damage, s.comboDamage, s.hits, s.maxComboDamage, s.totalDamage], [8, 18, 2, 18, 18]);
  assert.equal(s.counter, true, 'counter lamp');
  AD.recordAttackData(s, { kind: 'hit', dealt: 5, combo: 1, wall: true });
  assert.deepEqual([s.damage, s.comboDamage, s.hits, s.maxComboDamage, s.totalDamage], [5, 5, 1, 18, 23]);
  assert.equal(s.counter, false, 'counter lamp is per hit');
  assert.equal(s.wall, true, 'wall lamp');
  assert.ok(s.changed.includes('damage') && s.changed.includes('comboDamage') && !s.changed.includes('maxComboDamage'));
});
check('a blocked hit: chip as damage, the combo resets, every lamp goes dark', () => {
  const s = AD.newAttackDataSide();
  AD.recordAttackData(s, { kind: 'counter', dealt: 12, combo: 1, punish: true });
  AD.recordAttackData(s, { kind: 'block', dealt: 1 });
  assert.deepEqual([s.damage, s.comboDamage, s.hits, s.maxComboDamage, s.totalDamage], [1, 0, 0, 12, 13]);
  assert.ok(!s.clean && !s.counter && !s.wall && !s.punish);
});
check('punish = hit while recovering from the SAME blocked attack use (move objects are shared between uses)', () => {
  const move = { damage: 10 };
  const f = { state: 'attack', _attackPhase: 'active', attack: move, _clock: 5.0, stateT: 0.2 };
  AD.markBlocked(f);                                   // blocked during active frames
  f._attackPhase = 'recovery'; f._clock = 5.3; f.stateT = 0.5;
  assert.equal(AD.isPunish(f), true, 'same use, now recovering');
  f._attackPhase = 'active';
  assert.equal(AD.isPunish(f), false, 'not recovering');
  // the same move used again later (new state start): not the blocked use
  Object.assign(f, { _attackPhase: 'recovery', _clock: 9.0, stateT: 0.4 });
  assert.equal(AD.isPunish(f), false, 'a later use of the same move');
  assert.equal(AD.isPunish({ state: 'idle' }), false);
});

// ---------- B. practice only ----------
check('a normal fight: nothing is computed or shown', () => {
  let calls = 0;
  const g = { training: false, p1: {}, p2: {}, ui: { attackData() { calls++; } } };
  assert.equal(AD.practiceAttackData(g, g.p1, g.p2, 10, { kind: 'hit', combo: 1 }), null);
  assert.equal(calls, 0);
  assert.equal(g._attackDataState, undefined);
});
check('practice: the attacker\'s side panel gets the data', () => {
  const seen = [];
  const g = { training: true, p1: {}, p2: {}, ui: { attackData(side, d) { seen.push([side, d.damage, d.hits]); } } };
  AD.practiceAttackData(g, g.p1, g.p2, 10, { kind: 'hit', combo: 1 });
  AD.practiceAttackData(g, g.p2, g.p1, 7, { kind: 'hit', combo: 1 });
  assert.deepEqual(seen, [['p1', 10, 1], ['p2', 7, 1]]);
});
check('match start clears the readouts; safe on a stub UI', () => {
  let cleared = null;
  const g = { training: true, _attackDataState: { p1: {}, p2: {} }, ui: { attackDataClear(p) { cleared = p; } } };
  AD.resetPracticeAttackData(g);
  assert.equal(g._attackDataState, null);
  assert.equal(cleared, true);
  AD.resetPracticeAttackData({ ui: {} });
  AD.resetPracticeAttackData(null);
});

// ---------- C. the fight code calls none of the old popups ----------
const gameSrc = readFileSync(join(ROOT, 'game/js/game.js'), 'utf8');
check('game.js: no hit counter, no damage popup, no failed-input notes in a fight', () => {
  assert.ok(!/ui\.attackData\(/.test(gameSrc), 'ui.attackData( must not be called from game.js');
  assert.ok(!/ui\.combo\(/.test(gameSrc), 'ui.combo( must not be called from game.js');
  assert.ok(!/NO OPENING|METER NOT FULL|CAN\\'T ACT NOW|CLEAN HIT'/.test(gameSrc), 'old debug labels');
});
check('game.js: throw-break prompt and escape text are practice aids only', () => {
  for (const m of gameSrc.matchAll(/ui\.throwBreakPrompt\(([^)]*)\)/g)) {
    if (/^false$/.test(m[1].trim())) continue;  // hiding it is always fine
    const line = gameSrc.slice(gameSrc.lastIndexOf('\n', m.index) + 1, m.index);
    assert.ok(/if \(this\.training\)/.test(line), 'throwBreakPrompt(show) outside a training guard: ' + line.trim());
  }
  for (const m of gameSrc.matchAll(/ui\.throwEscape\(/g)) {
    const line = gameSrc.slice(gameSrc.lastIndexOf('\n', m.index) + 1, m.index);
    assert.ok(/if \(this\.training\)/.test(line), 'throwEscape outside a training guard: ' + line.trim());
  }
});
const mainSrc = readFileSync(join(ROOT, 'game/js/main.js'), 'utf8');
check('main.js: start-of-fight control hints only in practice', () => {
  const i = mainSrc.indexOf("const hints = document.getElementById('control-hints');");
  assert.ok(i > 0);
  const block = mainSrc.slice(i, i + 400);
  assert.ok(/if \(game\.training\)/.test(block) && /else hints\.classList\.add\('fade'\)/.test(block), block);
});
const gapsSrc = readFileSync(join(ROOT, 'game/js/ui-gaps.js'), 'utf8');
check('ui-gaps.js: the frame-data option draws only in practice', () => {
  assert.ok(/!g\.training\) \{ el\.classList\.remove\('show'\); return; \}/.test(gapsSrc));
});
const html = readFileSync(join(ROOT, 'game/index.html'), 'utf8');
check('index.html: the old centre-left popup element is gone; two side panels exist', () => {
  assert.ok(!/id="attack-data-dmg"/.test(html) && !/id="attack-data-label"/.test(html));
  assert.ok(/id="attack-data-p1"/.test(html) && /id="attack-data-p2"/.test(html));
});

// ---------- D. the real Game._resolveCombat (when the full repo is present, as in test/hitbox.test.mjs) ----------
if (existsSync(join(ROOT, 'packages/creation-suite/src/catalogs.js'))) {
  await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
  const F = await import(join(ROOT, 'game/js/fighter.js'));
  const G = await import(join(ROOT, 'game/js/game.js'));
  const bone = (x, y, z) => ({ getWorldPosition(v) { v.set(x, y, z); return v; } });
  const standing = (x) => ({ Hips: bone(x, 0.92, 0), Spine: bone(x, 1.05, 0), Spine1: bone(x, 1.25, 0), Spine2: bone(x, 1.45, 0),
    Neck: bone(x, 1.55, 0), Head: bone(x, 1.70, 0), LeftArm: bone(x, 1.42, -0.24), LeftForeArm: bone(x, 1.12, -0.30), LeftHand: bone(x, 0.84, -0.32),
    RightArm: bone(x, 1.42, 0.24), RightForeArm: bone(x, 1.12, 0.30), RightHand: bone(x, 0.84, 0.32),
    LeftUpLeg: bone(x, 0.90, -0.14), LeftLeg: bone(x, 0.48, -0.15), LeftFoot: bone(x, 0.10, -0.15), LeftToeBase: bone(x + 0.12, 0.06, -0.15),
    RightUpLeg: bone(x, 0.90, 0.14), RightLeg: bone(x, 0.48, 0.15), RightFoot: bone(x, 0.10, 0.15), RightToeBase: bone(x + 0.12, 0.06, 0.15) });
  const fighter = (o) => Object.assign(Object.create(F.Fighter.prototype), {
    bones: o.bones, root: { position: { x: o.x, y: 0, z: 0 } }, facing: o.facing, state: o.state || 'idle', stance: null,
    _attackPhase: o.phase || 'startup', hasHit: false, attack: o.attack || null, attackName: o.attackName || null,
    stats: { power: 1.1, defense: 1.05 }, invuln: 0, dead: false, onGround: true, hp: 100, maxHp: 100, meter: 0, maxMeter: 100,
    isPlayer: false, _stickDir: 'n', _vtriggerT: 0, _vbreakT: 0, _juggle: 0, stun: 0, _t3: null, _reactionSel: null, combo: 0, _comboTimer: 0,
    addMeter(v) { this.meter += v; } });
  const LP1 = { startup: 0.1667, active: 0.017, recovery: 0.467, damage: 11, knock: 2.2, soulGain: 8, limb: 'armL', t3row: 44, hitWord: 0x217 };
  const hitOnce = (training) => {
    const b = standing(0); b.LeftForeArm = bone(0.25, 1.35, -0.30); b.LeftHand = bone(0.95, 1.35, -0.30);
    const a = fighter({ bones: b, x: 0, facing: 1, state: 'attack', phase: 'active', attack: { ...LP1 }, attackName: '1' });
    const d = fighter({ bones: standing(1.45), x: 1.45, facing: -1 });
    const shown = [];
    const forbid = (n) => () => { throw new Error(`ui.${n} called in a normal fight`); };
    const ui = training
      ? { vShiftBreak() {}, vParry() {}, throwBreakPrompt() {}, combo: forbid('combo'), attackData(side, s) { shown.push([side, s.damage, s.hits]); } }
      : { vShiftBreak() {}, vParry() {}, throwBreakPrompt() {}, combo: forbid('combo'), attackData: forbid('attackData') };
    const fake = { training, ui, feel: { hitstop: 1, shake: 1 }, hitfx: { spawn() {} }, arena: { shake() {} }, p1: a, p2: d,
      soulurge: null, rage: null, xray: null, stageBreaks: null, matchStats: null, _hitStop: 0, _slowMo: 0 };
    G.Game.prototype._resolveCombat.call(fake, a, d);
    return { d, shown, fake };
  };
  check('real _resolveCombat, normal fight: the hit lands and no UI hit data is touched', () => {
    const { d, fake } = hitOnce(false);
    assert.ok(d.hp < 100, 'hit landed');
    assert.equal(fake._attackDataState, undefined);
  });
  check('real _resolveCombat, practice: the hit lands and P1\'s panel shows it', () => {
    const { d, shown } = hitOnce(true);
    assert.ok(d.hp < 100, 'hit landed');
    assert.equal(shown.length, 1);
    assert.equal(shown[0][0], 'p1');
    assert.equal(shown[0][1], Math.round(100 - d.hp));
    assert.equal(shown[0][2], 1);
  });
} else {
  console.log('NOTE section D skipped: packages/creation-suite absent from this checkout (CI sparse checkout); sections A-C cover the gate.');
}

console.log(JSON.stringify({ fails }));
if (fails) { console.log('FAIL practice-attack-data'); process.exit(1); }
console.log('PASS practice-attack-data');

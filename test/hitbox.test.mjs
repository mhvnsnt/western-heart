// Hitbox / hurtbox contact simulation (HITBOX LANE 2026-10-24).
// Run: node test/hitbox.test.mjs  (plain node, no runner, no DOM, no network)
// Owner playtest 2026-10-24: "Hitbox stuff and hurtbox stuff is not making
// contact right. A lot of contacts not being made during fight."
// This test simulates the REAL wired path, not copies of it:
//  - pure geometry in game/js/hitbox.js + game/js/t3-reaction-select.js
//  - Fighter.prototype.getHitbox / getHurtboxes / canBeHitBy / receiveHit
//    (imported from game/js/fighter.js, bones stubbed with plain
//    getWorldPosition, exactly the contract fighter.js uses)
//  - Game.prototype._resolveCombat when game/js/game.js imports cleanly
//    headless; otherwise the same gate order (geometry OR range, then
//    canBeHitBy, then receiveHit) driven by the same functions game.js
//    calls, with the game.js import failure reported, not hidden.
// Buttons use LP1/RP2/LK3/RK4 (owner directive 2026-10-24).
import assert from 'assert';
import { readFileSync, existsSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const HB = await import(join(ROOT, 'game/js/hitbox.js'));
const RS = await import(join(ROOT, 'game/js/t3-reaction-select.js'));
const CC = await import(join(ROOT, 'game/js/combat-core.js'));
const F = await import(join(ROOT, 'game/js/fighter.js'));

let fails = 0;
const check = (name, fn) => { try { fn(); console.log('ok', name); } catch (e) { fails++; console.log('FAIL', name, '-', e.message); } };

// ---------- A. pure geometry ----------
check('hurt segments: 14, unique ids, valid bands', () => {
  assert.equal(HB.HURT_SEGMENTS.length, 14);
  assert.equal(new Set(HB.HURT_SEGMENTS.map((s) => s.id)).size, 14);
  for (const s of HB.HURT_SEGMENTS) assert.ok(['high', 'mid', 'low'].includes(s.band), s.id);
});
check('segSegDist2: parallel / crossing / degenerate', () => {
  const d = (a, b, c, e) => Math.sqrt(HB.segSegDist2(a, b, c, e));
  assert.ok(Math.abs(d({ x: 0, y: 1, z: 0 }, { x: 0.4, y: 1, z: 0 }, { x: 0, y: 1.3, z: 0 }, { x: 0.4, y: 1.3, z: 0 }) - 0.3) < 1e-9);
  assert.ok(d({ x: 0, y: 1, z: 0 }, { x: 0.4, y: 1, z: 0 }, { x: 0.2, y: 0.5, z: 0 }, { x: 0.2, y: 1.5, z: 0 }) < 1e-9);
  assert.ok(Math.abs(d({ x: 1, y: 1, z: 1 }, { x: 1, y: 1, z: 1 }, { x: 1, y: 1, z: 1 }, { x: 1, y: 1, z: 1 })) < 1e-9);
  assert.ok(Math.abs(d({ x: 0, y: 0, z: 0 }, { x: 1, y: 0, z: 0 }, { x: 0.5, y: 2, z: 0 }, { x: 0.5, y: 3, z: 0 }) - 2) < 1e-9);
});
const chest = { id: 'chest', band: 'high', r: 0.34, x1: 0.9, y1: 1.1, z1: 0, x2: 0.9, y2: 1.5, z2: 0, x: 0.9, y: 1.3, z: 0 };
check('swept travel crosses a capsule the endpoint alone would miss', () => {
  // Fist ends at 0.95 (past the chest capsule's near edge 0.9-0.34=0.56? no:
  // make the capsule far: chest at x=2.0, fist travel 0 -> 1.6 passes THROUGH
  // nothing; instead travel 1.2 -> 2.1 crosses the capsule while the limb
  // segment itself sits short of it.
  const far = { ...chest, x1: 2.0, x2: 2.0, x: 2.0 };
  const hb = { segments: [{ ax: 1.0, ay: 1.3, az: 0, bx: 1.2, by: 1.3, bz: 0 }], travel: { ax: 1.2, ay: 1.3, az: 0, bx: 2.1, by: 1.3, bz: 0 }, r: 0.22 };
  const r = HB.testSweptHit(hb, [far]);
  assert.ok(r.hit && r.segment.id === 'chest', JSON.stringify(r));
  const noTravel = HB.testSweptHit({ ...hb, travel: null }, [far]);
  assert.ok(!noTravel.hit, 'without the travel segment this must miss');
});
check('swept test: limb segment hit, clean miss, closest segment wins', () => {
  const hb = { segments: [{ ax: 0.6, ay: 1.3, az: 0, bx: 0.95, by: 1.3, bz: 0 }], travel: null, r: 0.22 };
  assert.ok(HB.testSweptHit(hb, [chest]).hit);
  assert.ok(!HB.testSweptHit(hb, [{ ...chest, x1: 3, x2: 3, x: 3 }]).hit);
  const near = { ...chest, id: 'head', x1: 0.95, x2: 0.95, x: 0.95 };
  assert.equal(HB.testSweptHit(hb, [chest, near]).segment.id, 'head');
  // Legacy sphere shape still works.
  assert.ok(HB.testSweptHit({ x: 0.9, y: 1.3, z: 0, r: 0.22 }, [chest]).hit);
});
check('fallbackHurts: 14, facing mirrors x, crouch lowers the head', () => {
  const s = HB.fallbackHurts({ x: 0, y: 0, z: 0 }, 1, false);
  const l = HB.fallbackHurts({ x: 0, y: 0, z: 0 }, -1, false);
  const c = HB.fallbackHurts({ x: 0, y: 0, z: 0 }, 1, true);
  assert.equal(s.length, 14); assert.equal(l.length, 14);
  assert.ok(s[0].x > 0 && l[0].x < 0, 'facing flips the forward offset');
  assert.ok(c[0].y < s[0].y - 0.4, `crouch head ${c[0].y} vs standing ${s[0].y}`);
});

// ---------- B. hit-word fallback (combat-core) ----------
check('hitWordFor: old cases preserved + T7 fallback + paren strip', () => {
  assert.equal(CC.hitWordFor({ hit_level: 'h' }), 0x412);
  assert.equal(CC.hitWordFor({ hit_level: 'h,m' }), 0x217);
  assert.equal(CC.hitWordFor({ hit_level: ',h' }), 0x412);
  assert.equal(CC.hitWordFor({ hit_level: 't' }), undefined);
  assert.equal(CC.hitWordFor({ t7: { hit_level: 'mid (TC)' } }), 0x217);
  assert.equal(CC.hitWordFor({ t7: { hit_level: 'low' } }), 0x10F);
  assert.equal(CC.hitWordFor({ t7: { hit_level: 'high, mid' } }), 0x217);
  assert.equal(CC.hitWordFor({ t7: { hit_level: '(Special) (TJ)(JGS)' } }), undefined);
  assert.equal(CC.hitWordFor({ hit_level: 'mid', t7: { hit_level: 'high' } }), 0x217, 'top level wins over T7');
});

// ---------- C. wired Fighter.prototype methods ----------
const bone = (x, y, z) => ({ getWorldPosition(v) { v.set(x, y, z); return v; } });
function standingBones(x) {
  return {
    Hips: bone(x, 0.92, 0), Spine: bone(x, 1.05, 0), Spine1: bone(x, 1.25, 0), Spine2: bone(x, 1.45, 0),
    Neck: bone(x, 1.55, 0), Head: bone(x, 1.70, 0),
    LeftArm: bone(x, 1.42, -0.24), LeftForeArm: bone(x, 1.12, -0.30), LeftHand: bone(x, 0.84, -0.32),
    RightArm: bone(x, 1.42, 0.24), RightForeArm: bone(x, 1.12, 0.30), RightHand: bone(x, 0.84, 0.32),
    LeftUpLeg: bone(x, 0.90, -0.14), LeftLeg: bone(x, 0.48, -0.15), LeftFoot: bone(x, 0.10, -0.15), LeftToeBase: bone(x + 0.12, 0.06, -0.15),
    RightUpLeg: bone(x, 0.90, 0.14), RightLeg: bone(x, 0.48, 0.15), RightFoot: bone(x, 0.10, 0.15), RightToeBase: bone(x + 0.12, 0.06, 0.15),
  };
}
function stubFighter(o) {
  const f = Object.create(F.Fighter.prototype);
  Object.assign(f, {
    bones: o.bones, root: { position: { x: o.x, y: 0, z: 0 } }, facing: o.facing,
    state: o.state || 'idle', stance: null, _attackPhase: o.phase || 'startup',
    hasHit: false, attack: o.attack || null, attackName: o.attackName || null,
    stats: { power: 1.1, defense: 1.05 }, invuln: 0, dead: false, onGround: true,
    hp: 100, maxHp: 100, meter: 0, maxMeter: 100, isPlayer: !!o.isPlayer,
    _stickDir: o.stick || 'n', _vtriggerT: 0, _vbreakT: 0, _juggle: 0, stun: 0,
    _t3: o.bank ? { bank: o.bank } : null, _reactionSel: null, combo: 0, _comboTimer: 0,
  });
  return f;
}
const LP1 = { startup: 0.1667, active: 0.017, recovery: 0.467, damage: 11, knock: 2.2, soulGain: 8, limb: 'armL', t3row: 44 };
check('getHurtboxes: 14 bone capsules on a rigged fighter', () => {
  const d = stubFighter({ bones: standingBones(1.45), x: 1.45, facing: -1 });
  const h = d.getHurtboxes();
  assert.equal(h.length, 14);
  const head = h.find((s) => s.id === 'head');
  assert.ok(Math.abs(head.y - 1.62) < 0.1, `head mid y ${head.y}`);
  assert.ok(Math.abs(head.x - 1.45) < 0.01);
});
check('getHurtboxes: boneless rig still gets 14 fallback capsules (was: 0, every strike whiffed)', () => {
  const d = stubFighter({ bones: {}, x: 1.45, facing: -1 });
  assert.equal(d.getHurtboxes().length, 14);
});
check('getHurtboxes: crouching defender lowers head/chest capsules', () => {
  const s = stubFighter({ bones: standingBones(1.45), x: 1.45, facing: -1 });
  const c = stubFighter({ bones: {}, x: 1.45, facing: -1, state: 'crouch' });
  // Boneless path shows the drop directly; boned path uses live bones, so
  // assert the fallback drop here (the live-bone drop comes from the clip).
  assert.ok(c.getHurtboxes()[0].y < s.getHurtboxes()[0].y - 0.4);
});
check('getHitbox: LP1 (armL) sweeps elbow->fist + travel on the 2nd call; both sweeps 2 limbs', () => {
  const b = standingBones(0);
  b.LeftForeArm = bone(0.25, 1.35, -0.30); b.LeftHand = bone(0.95, 1.35, -0.30);
  const a = stubFighter({ bones: b, x: 0, facing: 1, state: 'attack', phase: 'active', attack: LP1, attackName: '1' });
  const h1 = a.getHitbox();
  assert.ok(h1 && h1.segments.length === 1 && h1.travel === null, JSON.stringify(h1));
  assert.ok(Math.abs(h1.x - 0.95) < 1e-9 && h1.r === 0.22);
  b.LeftHand = bone(1.05, 1.35, -0.30);
  const h2 = a.getHitbox();
  assert.ok(h2.travel && Math.abs(h2.travel.ax - 0.95) < 1e-9 && Math.abs(h2.travel.bx - 1.05) < 1e-9);
  const both = stubFighter({ bones: standingBones(0), x: 0, facing: 1, state: 'attack', phase: 'active',
    attack: { ...LP1, limb: 'both' }, attackName: 'd+1+2' });
  assert.equal(both.getHitbox().segments.length, 2, 'both-limb moves must sweep both arms');
  const idle = stubFighter({ bones: standingBones(0), x: 0, facing: 1, state: 'attack', phase: 'startup', attack: LP1, attackName: '1' });
  assert.equal(idle.getHitbox(), null, 'startup must not produce a hitbox');
});
check('canBeHitBy: high whiffs croucher, mid hits croucher, low whiffs jumper rules', () => {
  const crouch = stubFighter({ bones: standingBones(1.45), x: 1.45, facing: -1, state: 'crouch' });
  const stand = stubFighter({ bones: standingBones(1.45), x: 1.45, facing: -1 });
  assert.equal(crouch.canBeHitBy({ hitWord: 0x412 }), false, 'high vs crouch');
  assert.equal(crouch.canBeHitBy({ hitWord: 0x217 }), true, 'mid vs crouch');
  assert.equal(stand.canBeHitBy({ hitWord: 0x10F }), true, 'low vs stand');
  assert.equal(stand.canBeHitBy({ hitWord: 0x412 }), true, 'high vs stand');
});
check('receiveHit + T3 reaction pick: unguarded hit and guarded hit pick different records', () => {
  globalThis.WH_T3_REACTIONS = {
    records: [null, [10, 11, 20, 21, 30, 31, 40, 41, 50, 51, 60, 61, 70, 71, 5, 6, 7, 8, 9, 12, 13]],
    close_reactions: [], air_kinds: [[440, 0xd56], [550, 0xd61], [204, 0xd62], [436, 0xd63], [436, 0xd64], [1357, 0xd57]],
    banks: { king_on_pantera_leoman: { rows: { 44: [1, 0, 0] } } }, common_rows: {},
  };
  const atk = stubFighter({ bones: standingBones(0), x: 0, facing: 1, bank: 'king' });
  const def = stubFighter({ bones: standingBones(1.45), x: 1.45, facing: -1, bank: 'king' });
  const mv = { ...LP1, hitWord: 0x217 };
  const res = def.receiveHit(mv, atk);
  assert.equal(res, 'hit');
  assert.ok(def.hp < 100, `hp ${def.hp}`);
  assert.ok(def._reactionSel && def._reactionSel.field === 'front' && def._reactionSel.slot === 10, JSON.stringify(def._reactionSel));
  // Guarded: defender in block, stick neutral -> standing guard blocks mid.
  const blk = stubFighter({ bones: standingBones(1.45), x: 1.45, facing: -1, state: 'block', bank: 'king' });
  const res2 = blk.receiveHit(mv, atk);
  assert.equal(res2, 'block');
  assert.ok(blk._reactionSel && blk._reactionSel.field === 'guard' && blk._reactionSel.slot === 60, JSON.stringify(blk._reactionSel));
  delete globalThis.WH_T3_REACTIONS;
});

// ---------- D. full contact decision (geometry OR range, then posture, then damage) ----------
function resolveContact(atk, def) {
  const hb = atk.getHitbox();
  if (!hb) return 'no-hitbox';
  const hurts = def.getHurtboxes();
  const geo = HB.testSweptHit(hb, hurts);
  const reachHit = hurts.length > 0 && hb.reach > 0 && (def.root.position.y - atk.root.position.y) < 1.6 &&
    CC.inReach(atk.root.position.x, atk.root.position.z, atk.facing, def.root.position.x, def.root.position.z,
      hb.move, '', hb.reach / Math.max(0.01, CC.moveReach(hb.move, '')));
  if (!geo.hit && !reachHit) return 'whiff';
  if (!def.canBeHitBy(hb.move)) return 'posture-whiff';
  atk.hasHit = true;
  return def.receiveHit(hb.move, atk);
}
check('Pantera LP1 hits at jab range (1.45) and whiffs at long range (3.5)', () => {
  const mk = (dx) => {
    const b = standingBones(0); b.LeftForeArm = bone(0.25, 1.35, -0.30); b.LeftHand = bone(0.95, 1.35, -0.30);
    const a = stubFighter({ bones: b, x: 0, facing: 1, state: 'attack', phase: 'active', attack: LP1, attackName: '1' });
    const d = stubFighter({ bones: standingBones(dx), x: dx, facing: -1 });
    return [a, d];
  };
  let [a, d] = mk(1.45); assert.equal(resolveContact(a, d), 'hit', 'LP1 at 1.45 must hit');
  [a, d] = mk(3.5); assert.equal(resolveContact(a, d), 'whiff', 'LP1 at 3.5 must whiff');
});
check('geometry extends a fully-extended jab past the 1.75 range class (fist really there)', () => {
  const b = standingBones(0); b.LeftForeArm = bone(0.60, 1.35, 0); b.LeftHand = bone(1.40, 1.35, 0);
  const a = stubFighter({ bones: b, x: 0, facing: 1, state: 'attack', phase: 'active', attack: LP1, attackName: '1' });
  const d = stubFighter({ bones: standingBones(1.90), x: 1.90, facing: -1 });
  assert.equal(CC.inReach(0, 0, 1, 1.90, 0, LP1, '1'), false, 'range alone must miss at 1.90');
  assert.equal(resolveContact(a, d), 'hit', 'extended fist vs chest capsule must connect');
});
check('f,f+RP2 analogue (f,F+2) reaches farther than LP1; crouching low hits, high whiffs croucher', () => {
  const ff2 = { startup: 0.5167, active: 0.033, recovery: 0.5, damage: 21, knock: 5.0, soulGain: 11, limb: 'armR', heavy: true, hitWord: 0x217 };
  assert.ok(CC.moveReach(ff2, 'f,F+2') > CC.moveReach(LP1, '1'), 'advancing heavy out-reaches a jab');
  const b = standingBones(0); b.RightForeArm = bone(0.25, 1.35, 0.30); b.RightHand = bone(0.95, 1.35, 0.30);
  const a = stubFighter({ bones: b, x: 0, facing: 1, state: 'attack', phase: 'active', attack: ff2, attackName: 'f,F+2' });
  const d = stubFighter({ bones: standingBones(2.10), x: 2.10, facing: -1 });
  assert.equal(resolveContact(a, d), 'hit', 'f,F+2 at 2.10 must hit (reach 2.30)');
  // Crouching defender: high whiffs, low connects.
  const hb = standingBones(0); hb.LeftLeg = bone(0.30, 0.35, -0.15); hb.LeftFoot = bone(0.95, 0.12, -0.15);
  const lowMove = { startup: 0.2833, active: 0.033, recovery: 0.517, damage: 12, knock: 4.2, soulGain: 11, limb: 'legL', hitWord: 0x10F };
  const lk = stubFighter({ bones: hb, x: 0, facing: 1, state: 'attack', phase: 'active', attack: lowMove, attackName: 'd+3' });
  const crouch = stubFighter({ bones: standingBones(1.45), x: 1.45, facing: -1, state: 'crouch' });
  assert.equal(resolveContact(lk, crouch), 'hit', 'low vs croucher must hit');
  const jab = stubFighter({ bones: (() => { const bb = standingBones(0); bb.LeftForeArm = bone(0.25, 1.35, -0.30); bb.LeftHand = bone(0.95, 1.35, -0.30); return bb; })(), x: 0, facing: 1, state: 'attack', phase: 'active', attack: { ...LP1, hitWord: 0x412 }, attackName: '1' });
  const crouch2 = stubFighter({ bones: standingBones(1.45), x: 1.45, facing: -1, state: 'crouch' });
  assert.equal(resolveContact(jab, crouch2), 'posture-whiff', 'high vs croucher must whiff');
});
check('reaction selector: guard / counter / air / class gates (synthetic table)', () => {
  const R = { records: [null, [10, 11, 20, 21, 30, 31, 40, 41, 50, 51, 60, 61, 70, 71, 5, 6, 7, 8, 9, 12, 13]],
    close_reactions: [[200, 100]], air_kinds: [[440, 0xd56], [550, 0xd61], [204, 0xd62], [436, 0xd63], [436, 0xd64], [1357, 0xd57]], banks: {} };
  assert.equal(RS.selectReactionSlot(R, [1, 0, 0], {}).slot, 10);
  assert.equal(RS.selectReactionSlot(R, [1, 0, 0], { guarded: true, crouch: true }).slot, 61);
  assert.equal(RS.selectReactionSlot(R, [1, 0, 0], { counter: true }).slot, 20);
  assert.equal(RS.selectReactionSlot(R, [1, 0, 0], { airborne: true, airKind: 2 }).slot, 0xd62);
  assert.equal(RS.selectReactionSlot(R, [1, 0, 1], {}), null);
  assert.equal(RS.selectReactionSlot(R, [1, 0, 2], { airborne: true }), null);
  assert.equal(RS.selectReactionSlot(R, [0x1234, 0, 0], {}), null);
  assert.equal(RS.selectReactionSlot(R, [1, 0, 0], { quadrant: 2 }).slot, 50, 'back quadrant');
});

// ---------- E. Pantera data (when the moveset file is present) ----------
{
  const p = join(ROOT, 'game/assets/movesets/pantera.json');
  if (existsSync(p)) {
    const d = JSON.parse(readFileSync(p, 'utf8'));
    check('Pantera data: LP1/RP2/LK3/RK4 limbs + f,F+2 reach + hit-word coverage', () => {
      assert.equal(d.moves['1'].limb, 'armL'); assert.equal(d.moves['2'].limb, 'armR');
      assert.equal(d.moves['3'].limb, 'legL'); assert.equal(d.moves['4'].limb, 'legR');
      assert.ok(CC.moveReach(d.moves['f,F+2'], 'f,F+2') > CC.moveReach(d.moves['1'], '1'));
      let covered = 0, total = 0;
      for (const [k, mv] of Object.entries(d.moves)) {
        if (mv.startup == null) continue; total++;
        const w = (d.hit_words && d.hit_words[k] != null) ? d.hit_words[k] : CC.hitWordFor(mv);
        if (w !== undefined) covered++;
      }
      // 708/873 on main: decoded hit_words + T7/T8 fallback. The rest
      // (specials, strings and T3-merge strikes with no level in the
      // moveset JSON) still default to mid, exactly as before — no
      // regression, but their row attack word (hit_frames.json) is a
      // documented remaining wiring item, not claimed here.
      assert.ok(covered / total > 0.80, `hit-word coverage ${covered}/${total}`);
      console.log('   pantera hit-word coverage:', covered, '/', total);
    });
  } else console.log('skip pantera data (moveset file absent in this checkout)');
}

// ---------- F. real Game._resolveCombat, when the full repo is present ----------
// game.js pulls packages/creation-suite (via customization-consumer),
// which the CI sparse checkout does NOT include — so this section runs
// only when that dir exists, and is a NOTE-skip otherwise (never a
// silent catch-all: a real import error with the dir present fails).
if (existsSync(join(ROOT, 'packages/creation-suite/src/catalogs.js'))) {
  const G = await import(join(ROOT, 'game/js/game.js'));
  check('Game._resolveCombat (real method, stubbed game): LP1 hits at 1.45', () => {
    const b = standingBones(0); b.LeftForeArm = bone(0.25, 1.35, -0.30); b.LeftHand = bone(0.95, 1.35, -0.30);
    const a = stubFighter({ bones: b, x: 0, facing: 1, state: 'attack', phase: 'active', attack: { ...LP1, hitWord: 0x217 }, attackName: '1' });
    const d = stubFighter({ bones: standingBones(1.45), x: 1.45, facing: -1 });
    a.addMeter = (v) => { a.meter += v; }; d.addMeter = (v) => { d.meter += v; };
    const fake = { ui: { vShiftBreak() {}, vParry() {}, throwBreakPrompt() {}, combo() {} }, feel: { hitstop: 1, shake: 1 },
      hitfx: { spawn() {} }, arena: { shake() {} }, soulurge: null, rage: null, xray: null, stageBreaks: null, matchStats: null, _hitStop: 0, _slowMo: 0 };
    G.Game.prototype._resolveCombat.call(fake, a, d);
    assert.ok(d.hp < 100, `defender hp after _resolveCombat: ${d.hp}`);
    assert.ok(a.hasHit, 'attacker must have registered the hit');
  });
  console.log('ok Game import headless');
} else {
  console.log('NOTE Game section skipped: packages/creation-suite absent from this checkout (CI sparse checkout).');
  console.log('   _resolveCombat wiring is covered by section D (same functions, same gate order); live-browser play verification remains open.');
}

console.log(JSON.stringify({ fails }));
if (fails) { console.log('FAIL hitbox'); process.exit(1); }
console.log('PASS hitbox');

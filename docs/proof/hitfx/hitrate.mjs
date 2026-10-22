#!/usr/bin/env node
/* Hit-rate proof: BEFORE (old prototype collision) vs AFTER (Tekken-style
   attack boxes from the edited game/js/fighter.js — functions extracted
   verbatim and run against stub bones at 120Hz fixed step).
   Scenario: attacker throws King's T3 jab '1' (startup 0.183s, active
   0.033s — real teardown frame data) at a standing defender D units away.
   Bone layout mirrors the game's Mixamo proportions. */
import { readFileSync } from 'fs';

const src = readFileSync('/home/hatch/workspace/fix3/hitfx/game/js/fighter.js', 'utf8');

function extractFn(name) {
  // grab "  name(...) { ... }" with balanced braces
  const start = src.indexOf(`  ${name}(`);
  if (start < 0) throw new Error('not found: ' + name);
  let i = src.indexOf('{', start), depth = 0, end = i;
  for (; i < src.length; i++) {
    if (src[i] === '{') depth++;
    else if (src[i] === '}') { depth--; if (depth === 0) { end = i + 1; break; } }
  }
  return src.slice(start, end);
}

// minimal THREE.Vector3 stand-in
const _v1 = { x: 0, y: 0, z: 0 };
function v3(x, y, z) { return { x, y, z }; }

function makeBones(rootX, pose) {
  // pose: hand/foot world offsets at full extension
  const B = {};
  const defs = {
    Hips: [0, 0.95, 0], Spine1: [0, 1.20, 0], Spine2: [0, 1.45, 0], Head: [0, 1.68, 0],
    RightHand: pose.hand, LeftHand: pose.hand, RightFoot: pose.foot, LeftFoot: pose.foot,
  };
  for (const [k, o] of Object.entries(defs)) {
    B[k] = { getWorldPosition(v) { v.x = rootX + o[0]; v.y = o[1]; v.z = o[2]; return v; } };
  }
  return B;
}

// ---- AFTER: real code from edited fighter.js ----
const getHitboxSrc = extractFn('getHitbox');
const getHurtboxesSrc = extractFn('getHurtboxes');
const weaponBoneSrc = extractFn('_weaponBone');
const attackStepSrc = extractFn('_attackStep');

function makeAfterFighter() {
  const F = {
    state: 'attack', _attackPhase: 'startup', hasHit: false, facing: 1,
    attackName: '1', attack: { limb: 'armL', knock: 2.2 }, stats: {},
    root: { position: { x: 0, y: 0, z: 0 } },
    invuln: 0, dead: false,
  };
  F.bones = makeBones(0, { hand: [0.88, 1.35, 0], foot: [0.95, 0.25, 0] });
  // rebind bones to live root position
  const B = {};
  for (const [k, b] of Object.entries(F.bones)) {
    B[k] = { getWorldPosition: (v) => b.getWorldPosition(v) };
  }
  // wrap: bones follow root
  F.bones = {};
  const defs = { Hips: [0, 0.95, 0], Spine1: [0, 1.20, 0], Spine2: [0, 1.45, 0], Head: [0, 1.68, 0],
                 RightHand: [0.88, 1.35, 0], LeftHand: [0.88, 1.35, 0],
                 RightFoot: [0.95, 0.25, 0], LeftFoot: [0.95, 0.25, 0] };
  for (const [k, o] of Object.entries(defs))
    F.bones[k] = { getWorldPosition(v) { v.x = F.root.position.x + o[0]; v.y = o[1]; v.z = o[2]; return v; } };
  const scope = { _v1 };
  F._weaponBone = eval(`(function(){ ${weaponBoneSrc.replace(/^  _weaponBone\(\)/, 'return function()')} })`).call({ ...scope });
  return F;
}

// Simpler: compile the three functions with `this` binding and _v1 in scope.
function compileFighter() {
  const F = {
    state: 'attack', _attackPhase: 'startup', hasHit: false, facing: 1,
    attackName: '1', attack: { limb: 'armL', knock: 2.2 }, stats: {},
    root: { position: { x: 0, y: 0, z: 0 } }, invuln: 0, dead: false,
  };
  const defs = { Hips: [0, 0.95, 0], Spine1: [0, 1.20, 0], Spine2: [0, 1.45, 0], Head: [0, 1.68, 0],
                 RightHand: [0.88, 1.35, 0], LeftHand: [0.88, 1.35, 0],
                 RightFoot: [0.95, 0.25, 0], LeftFoot: [0.95, 0.25, 0] };
  F.bones = {};
  for (const [k, o] of Object.entries(defs))
    F.bones[k] = { getWorldPosition(v) { v.x = F.root.position.x + o[0]; v.y = o[1]; v.z = o[2]; return v; } };
  const factory = new Function('_v1', `
    const _weaponBone = ${weaponBoneSrc.replace(/^  _weaponBone\(\)/, 'function()')};
    const _attackStep = ${attackStepSrc.replace(/^  _attackStep\(\)/, 'function()')};
    const getHitbox = ${getHitboxSrc.replace(/^  getHitbox\(\)/, 'function()')};
    const getHurtboxes = ${getHurtboxesSrc.replace(/^  getHurtboxes\(\)/, 'function()')};
    return { _weaponBone, _attackStep, getHitbox, getHurtboxes };
  `);
  const fns = factory(_v1);
  Object.assign(F, fns);
  return F;
}

// ---- BEFORE: the old prototype code, verbatim logic ----
function beforeHitbox(F) {
  if (F.state !== 'attack' || F._attackPhase !== 'active' || F.hasHit) return null;
  const hand = { x: F.root.position.x + 0.88, y: 1.35, z: 0 };
  return { x: hand.x, y: hand.y, z: hand.z, r: 0.5 };
}
function beforeHurtboxes(D) {
  return [{ x: D, y: 1.20, z: 0, r: 0.58 }, { x: D, y: 1.68, z: 0, r: 0.34 }];
}

const DT = 1 / 120;
const JAB = { startup: 0.183, active: 0.033, recovery: 0.45 };

function overlap(hb, hurts) {
  for (const hu of hurts) {
    const dx = hb.x - hu.x, dy = hb.y - hu.y, dz = hb.z - hu.z, rr = hb.r + hu.r;
    if (dx * dx + dy * dy + dz * dz <= rr * rr) return true;
  }
  return false;
}

function simAfter(D) {
  const F = compileFighter();
  let t = 0, hit = false;
  const total = JAB.startup + JAB.active + 0.05;
  const extendEnd = JAB.startup + JAB.active;
  while (t < total && !hit) {
    t += DT;
    F._attackPhase = t < JAB.startup ? 'startup' : t < JAB.startup + JAB.active ? 'active' : 'recovery';
    // Tekken step-in during startup/active (positional, from _physics)
    if (F._attackPhase === 'startup' || F._attackPhase === 'active')
      F.root.position.x += F.facing * F._attackStep() * DT;
    if (F._attackPhase !== 'active') continue;
    // procedural punch extension curve (fighter.js _animate): ramps 0->1
    // across startup+active, peaking at the END of the active window
    const ext = Math.min(1, t / extendEnd);
    const handX = 0.25 + 0.63 * ext; // shoulder base + arm reach * extension
    const defs = { Hips: [D, 0.95, 0], Spine1: [D, 1.20, 0], Spine2: [D, 1.45, 0], Head: [D, 1.68, 0] };
    const db = {};
    for (const [k, o] of Object.entries(defs))
      db[k] = { getWorldPosition(v) { v.x = o[0]; v.y = o[1]; v.z = o[2]; return v; } };
    // weapon bone at the animated extension (not full reach the whole time)
    F.bones.RightHand.getWorldPosition = F.bones.LeftHand.getWorldPosition =
      (v) => { v.x = F.root.position.x + handX; v.y = 1.35; v.z = 0; return v; };
    const hb = F.getHitbox();
    if (!hb) continue;
    const hurts = F.getHurtboxes.call({ bones: db, invuln: 0, dead: false, state: 'idle' });
    if (overlap(hb, hurts)) hit = true;
  }
  return hit;
}

function simBefore(D) {
  const F = { state: 'attack', _attackPhase: 'startup', hasHit: false, root: { position: { x: 0 } } };
  let t = 0, hit = false;
  const total = JAB.startup + JAB.active + 0.05;
  const extendEnd = JAB.startup + JAB.active;
  while (t < total && !hit) {
    t += DT;
    F._attackPhase = t < JAB.startup ? 'startup' : t < JAB.startup + JAB.active ? 'active' : 'recovery';
    if (F._attackPhase !== 'active') continue;
    const ext = Math.min(1, t / extendEnd);
    const handX = 0.25 + 0.63 * ext;
    const hb = { x: F.root.position.x + handX, y: 1.35, z: 0, r: 0.5 };
    if (overlap(hb, beforeHurtboxes(D))) hit = true;
  }
  return hit;
}

console.log('dist | BEFORE (old) | AFTER (tekken-style)');
console.log('-----|--------------|--------------------');
let bHits = 0, aHits = 0, n = 0;
for (let D = 1.5; D <= 3.01; D += 0.25) {
  const b = simBefore(D), a = simAfter(D);
  bHits += b ? 1 : 0; aHits += a ? 1 : 0; n++;
  console.log(`${D.toFixed(2)} | ${b ? 'HIT ' : 'whiff'}        | ${a ? 'HIT' : 'whiff'}`);
}
console.log(`\nJab connect rate across 1.50–3.00 range:`);
console.log(`BEFORE: ${bHits}/${n} = ${(100 * bHits / n).toFixed(0)}%`);
console.log(`AFTER:  ${aHits}/${n} = ${(100 * aHits / n).toFixed(0)}%`);

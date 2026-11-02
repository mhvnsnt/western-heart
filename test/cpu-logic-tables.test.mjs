// Transfer F1-F12: wrestling-sim CPU logic tables, slots, families,
// resources, traits, critical event, one-record fighter file.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import * as L from '../game/js/ai/cpu-logic-tables.js';

let n = 0; const t = (name, f) => { f(); n++; };
const always = () => 0; // rng that always picks the first positive-weight entry
const never = () => 0.999999;

const data = JSON.parse(readFileSync(fileURLToPath(new URL('../game/data/wrestling-sim-example.json', import.meta.url)), 'utf8'));

t('example record validates clean', () => assert.deepEqual(L.validateFighterRecord(data), []));
t('example record has all five sections', () => {
  for (const s of ['profile', 'appearance', 'parameters', 'moveset', 'cpuLogic']) assert.ok(s in data, s);
});

t('phases: thresholds and critical override', () => {
  assert.equal(L.phaseOf(0.1), 'small'); assert.equal(L.phaseOf(0.5), 'medium');
  assert.equal(L.phaseOf(0.9), 'large'); assert.equal(L.phaseOf(0.1, true), 'critical');
});

t('phase escalation is data-driven: critical column picks the finisher', () => {
  const table = data.cpuLogic.table.frontGrappleSmall;
  assert.equal(L.resolveCpuPick(data.cpuLogic.table, 'frontGrappleSmall', 'small', {}, always).move, 'wh-arm-drag');
  assert.equal(L.resolveCpuPick(data.cpuLogic.table, 'frontGrappleSmall', 'critical', {}, always).move, 'wh-finisher-slam');
  assert.ok(table.small['wh-arm-drag'] > (table.large['wh-arm-drag'] || 0));
});

t('weighted pick is deterministic with injected rng', () => {
  assert.equal(L.pickWeighted({ a: 1, b: 1 }, always), 'a');
  assert.equal(L.pickWeighted({ a: 1, b: 1 }, never), 'b');
  assert.equal(L.pickWeighted({ a: 0, b: 0 }), null);
  assert.equal(L.pickWeighted({}), null);
});

t('showmanship scales taunt weight; ukemi returned as tendency', () => {
  const low = L.resolveCpuPick(data.cpuLogic.table, 'groundHead', 'small', { showmanship: 0, ukemi: 0 }, always);
  const high = L.resolveCpuPick(data.cpuLogic.table, 'groundHead', 'small', { showmanship: 100, ukemi: 80 }, always);
  assert.equal(low.ukemi, 0); assert.equal(high.ukemi, 0.8);
  // taunt weight at showmanship 100 is 3x the weight at 0 (0.5 -> 1.5 factor)
  assert.equal(L.normalizeSliders({ showmanship: 100 }).showmanship, 100);
});

t('sliders validate and normalize', () => {
  assert.deepEqual(L.validateSliders(data.cpuLogic.sliders), []);
  assert.ok(L.validateSliders({ showmanship: 101, discretion: 0, flexibility: 0, ukemi: 0 }).length > 0);
  assert.equal(L.normalizeSliders({}).showmanship, 50);
  assert.equal(L.normalizeSliders({ showmanship: 999 }).showmanship, 100);
});

t('priority: 100% chain always follows up, 0% never does', () => {
  const chains = data.cpuLogic.priority;
  assert.equal(L.resolvePriority(chains, 'wh-suplex', 'critical', always), 'wh-ground-stomp');
  assert.equal(L.resolvePriority(chains, 'wh-suplex', 'small', never), null);
  assert.equal(L.resolvePriority(chains, 'wh-other', 'critical', always), null);
  assert.equal(L.resolvePriority(chains, 'wh-suplex', 'small', always), 'wh-ground-stomp'); // 20% > rng 0
  assert.ok(L.validatePriorityChains(chains).length === 0);
  const tooMany = Array.from({ length: 11 }, (_, i) => ({ trigger: `t${i}`, followUp: 'f', perPhase: { small: 10 } }));
  assert.ok(L.validatePriorityChains(tooMany).some((p) => /too many/.test(p)));
});

t('moveset slots: every position filled in the example, lookup works', () => {
  assert.deepEqual(L.validateMovesetSlots(data.moveset), []);
  assert.equal(L.moveForSlot(data.moveset, 'finisher'), 'wh-finisher-slam');
  assert.equal(L.moveForSlot(data.moveset, 'diving'), 'wh-diving-elbow');
  assert.equal(L.moveForSlot({}, 'finisher'), null);
  assert.ok(L.validateMovesetSlots({ nowhere: 'x' }).length > 0);
});

t('family ratings validate; matchup multiplier favours stronger offense', () => {
  assert.deepEqual(L.validateFamilyRatings(data.parameters), []);
  assert.ok(L.familyMultiplier(8, 6) > 1);
  assert.ok(L.familyMultiplier(5, 8) < 1);
  assert.equal(L.familyMultiplier(5, 5), 1);
  assert.ok(L.validateFamilyRatings({ bogus: { offense: 1, defense: 1 } }).length > 0);
});

t('affinity grades stamina cost, A cheapest', () => {
  assert.ok(L.staminaCost(10, 'A') < L.staminaCost(10, 'C'));
  assert.ok(L.staminaCost(10, 'E') > L.staminaCost(10, 'C'));
  assert.equal(L.staminaCost(10, 'C'), 10);
});

t('stamina and spirit are separate resources; parts exhaust independently', () => {
  const res = L.createResources();
  L.applyResourceDelta(res, { stamina: -30 });
  assert.equal(res.stamina, 70); assert.equal(res.spirit, 100);
  L.applyResourceDelta(res, { spirit: -40 });
  assert.equal(res.spirit, 60); assert.equal(res.stamina, 70);
  assert.equal(L.damagePart(res, 'arm', 100), 0);
  assert.equal(L.partExhausted(res, 'arm'), true);
  assert.equal(L.partExhausted(res, 'leg'), false);
});

t('traits validate; cost range enforced', () => {
  assert.deepEqual(L.validateTrait(data.cpuLogic.traits[0]), []);
  assert.ok(L.validateTrait({ id: 'x', trigger: 'low-stamina', effect: 'rise-faster', cost: 5 }).length > 0);
  assert.ok(L.validateTrait({ id: 'x', trigger: 'nope', effect: 'rise-faster', cost: 20 }).length > 0);
});

t('critical: caller-supplied base rate only, multipliers apply, clamped', () => {
  const zero = L.criticalChance(0, {}, always);
  assert.equal(zero.rolled, false); assert.equal(zero.chance, 0);
  const full = L.criticalChance(1, {}, always);
  assert.equal(full.rolled, true);
  const halved = L.criticalChance(0.4, { traits: [{ criticalMultiplier: 0.5 }] }, never);
  assert.equal(halved.chance, 0.2);
  const doubled = L.criticalChance(0.8, { lowStaminaReversal: true }, never);
  assert.equal(doubled.chance, 1); // clamped, not 1.6
});

t('sim-usable: a deterministic CPU-vs-CPU sequence escalates to the finisher', () => {
  // Two resolvers pick from the same table; as damage grows the phase
  // column moves small -> critical, and the critical column's top pick
  // (rng always-first) is the finisher. This is the shape sim-match.js
  // consumes: same resolver, no player input seat.
  const picks = [];
  let damage = 0;
  for (let i = 0; i < 4; i++) {
    const phase = L.phaseOf(damage, damage >= 0.9);
    picks.push(L.resolveCpuPick(data.cpuLogic.table, 'frontGrappleSmall', phase, {}, always).move);
    damage += 0.35;
  }
  assert.equal(picks[picks.length - 1], 'wh-finisher-slam');
});

console.log(`cpu-logic-tables.test: ${n} passed`);

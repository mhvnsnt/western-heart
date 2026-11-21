/* transmigration.test.mjs — Tong-Nou transmigration sequences.
 *
 * Covers game/js/transmigration.js (face-pick, 9-life run, Nameplates,
 * Magatamas, Katana of Five Forces, shrine), plus the cross-checks
 * that tie this module to the working pieces it wires together:
 *  - FACE_ART matches modes.js EM_FACE (read as text, same pattern
 *    as the heartmind stage-key test — no import of modes.js, so
 *    this module stays DOM-free and node-testable).
 *  - Sound slot names exist in game/data/eastern-mind-sfx.json.
 *
 * Run: node --test game/tests/transmigration.test.mjs (from repo root)
 * Local lane mirror: node --test build/game/tests/transmigration.test.mjs
 *   (build/game/js/modes.js + build/game/data/eastern-mind-sfx.json
 *   are verbatim stubs of the EM_FACE block / sfx slots, copied
 *   from main — the real cross-check runs in-repo / CI.)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  FACE_ART, TRANSMIGRATION_SFX, LANDS, LAND_ORDER, MAGATAMA_LANDS,
  CREATURES, CREATURE_IDS, SELF_ID,
  faceToCreature, allFaceCombinations, creatureByVessel, nameOf,
  createRun, die, reincarnate, advanceMission, dieAgain,
  unlockSeal, collectMagatama, forgeKatana, recoverSoul,
  creatureNameplates, livesRemaining, runSummary,
} from '../js/transmigration.js';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');

function playFullRun(t) {
  let run = createRun();
  // Life 1: Rin dies in the left flame, earns the Rin Nameplate.
  let r = die(run);
  assert.strictEqual(r.ok, true);
  run = r.run;
  assert.deepStrictEqual(run.nameplates, ['rin']);
  // Lives 2-9: the 8 creatures, in walkthrough order.
  for (const id of CREATURE_IDS) {
    const c = CREATURES[id];
    r = reincarnate(run, ...c.face);
    assert.strictEqual(r.ok, true, `reincarnate as ${c.name}`);
    run = r.run;
    assert.strictEqual(run.phase, 'mission');
    assert.strictEqual(run.missionCreature, c.vessel);
    for (let i = 0; i < c.steps.length; i++) {
      r = advanceMission(run);
      assert.strictEqual(r.ok, true);
      run = r.run;
      assert.strictEqual(r.done, i === c.steps.length - 1);
    }
    assert.ok(run.nameplates.includes(c.vessel), `${c.name} plate earned`);
    assert.strictEqual(run.phase, 'face-pick-ready');
    r = dieAgain(run);
    assert.strictEqual(r.ok, true);
    run = r.run;
    assert.strictEqual(run.phase, 'face-pick');
  }
  // Ninth life: the self. Any index-2 part calls Rin.
  r = reincarnate(run, 2, 2, 2);
  assert.strictEqual(r.ok, true);
  run = r.run;
  assert.strictEqual(run.phase, 'seal');
  assert.strictEqual(run.lives, 9);
  assert.strictEqual(run.deaths, 9);
  // Seal, Magatamas, Katana, shrine.
  r = unlockSeal(run);
  assert.strictEqual(r.ok, true);
  run = r.run;
  for (const land of ['metal', 'fire', 'earth']) {
    r = collectMagatama(run, land);
    assert.strictEqual(r.ok, true, `collect ${land}`);
    run = r.run;
  }
  assert.deepStrictEqual([...run.magatamas].sort(), [...MAGATAMA_LANDS].sort());
  assert.strictEqual(run.phase, 'katana');
  r = forgeKatana(run);
  assert.strictEqual(r.ok, true);
  run = r.run;
  assert.strictEqual(run.katana, true);
  r = recoverSoul(run);
  assert.strictEqual(r.ok, true);
  run = r.run;
  assert.strictEqual(run.phase, 'done');
  assert.strictEqual(run.soulRecovered, true);
  assert.strictEqual(run.lives, 9);
  return run;
}

test('face map: the 8 verified combos resolve to the right creature', () => {
  const expected = {
    tou: [0, 0, 0], jin_soul: [0, 0, 1], sha: [0, 1, 0], gyou: [0, 1, 1],
    zen: [1, 0, 0], byou: [1, 0, 1], retsu: [1, 1, 0], kai: [1, 1, 1],
  };
  for (const [vessel, face] of Object.entries(expected)) {
    assert.strictEqual(faceToCreature(...face), vessel, face.join(','));
    assert.deepStrictEqual(CREATURES[vessel === 'jin_soul' ? 'jin' : vessel].face, face);
  }
});

test('face map: all 27 combos resolve; index-2 parts call the self', () => {
  const combos = allFaceCombinations();
  assert.strictEqual(combos.length, 27);
  const creatures = combos.filter((c) => c.vessel !== SELF_ID);
  const selves = combos.filter((c) => c.vessel === SELF_ID);
  assert.strictEqual(creatures.length, 8);
  assert.strictEqual(selves.length, 19);
  assert.strictEqual(new Set(creatures.map((c) => c.vessel)).size, 8);
  for (const c of selves) {
    assert.ok(c.eye === 2 || c.nose === 2 || c.mouth === 2);
  }
  assert.strictEqual(faceToCreature(3, 0, 0), null);
  assert.strictEqual(faceToCreature(0, -1, 0), null);
});

test('creature table: 8 creatures, 2 per land, earth holds none; Sha has 4 instruments', () => {
  assert.deepStrictEqual([...CREATURE_IDS].sort(), ['byou', 'gyou', 'jin', 'kai', 'retsu', 'sha', 'tou', 'zen']);
  const perLand = {};
  for (const id of CREATURE_IDS) {
    const c = CREATURES[id];
    assert.ok(c.steps.length >= 2, `${c.name} has mission steps`);
    assert.ok(LANDS[c.land], `${c.name} land exists`);
    assert.ok(c.home && c.mission && c.bornWith, `${c.name} has home/mission/bornWith`);
    perLand[c.land] = (perLand[c.land] || 0) + 1;
  }
  assert.deepStrictEqual(perLand, { wood: 2, metal: 2, fire: 2, water: 2 });
  assert.ok(!Object.values(CREATURES).some((c) => c.land === 'earth'));
  assert.deepStrictEqual(CREATURES.sha.instruments, ['Bell of Gold', 'Drum of Fire', 'Koto of Wood', 'Flute of Water']);
  assert.deepStrictEqual(CREATURES.byou.magatamas, ['water', 'wood']);
  assert.deepStrictEqual(LAND_ORDER, ['wood', 'fire', 'earth', 'metal', 'water']);
  assert.deepStrictEqual([...MAGATAMA_LANDS].sort(), ['earth', 'fire', 'metal', 'water', 'wood']);
});

test('full 9-life run end to end: 9 lives, 9 deaths, soul recovered', () => {
  const run = playFullRun();
  const s = runSummary(run);
  assert.strictEqual(s.lives, 9);
  assert.strictEqual(s.livesRemaining, 0);
  assert.strictEqual(s.deaths, 9);
  assert.strictEqual(s.creatureNameplates, 8);
  assert.strictEqual(s.nameplates.length, 9);
  assert.strictEqual(s.nameplates[0], 'rin');
  assert.strictEqual(s.magatamas.length, 5);
  assert.strictEqual(s.katana, true);
  assert.strictEqual(s.sealUnlocked, true);
  assert.strictEqual(s.soulRecovered, true);
  assert.ok(run.log.length > 20);
});

test('guards: spent vessels refused, self gated, seal/katana/shrine gated', () => {
  let run = createRun();
  // No face-pick before death.
  assert.strictEqual(reincarnate(run, 0, 0, 0).ok, false);
  assert.strictEqual(advanceMission(run).ok, false);
  assert.strictEqual(unlockSeal(run).ok, false);
  assert.strictEqual(collectMagatama(run, 'metal').ok, false);
  assert.strictEqual(forgeKatana(run).ok, false);
  assert.strictEqual(recoverSoul(run).ok, false);
  // Die as Rin, then the self is gated (0 creature plates).
  run = die(run).run;
  assert.strictEqual(reincarnate(run, 2, 0, 0).ok, false);
  assert.strictEqual(reincarnate(run, 0, 2, 0).ok, false);
  // Pick Tou, finish, then Tou is spent.
  run = reincarnate(run, 0, 0, 0).run;
  for (let i = 0; i < CREATURES.tou.steps.length; i++) run = advanceMission(run).run;
  run = dieAgain(run).run;
  assert.strictEqual(reincarnate(run, 0, 0, 0).ok, false);
  assert.match(reincarnate(run, 0, 0, 0).reason, /spent/);
  // Dying mid-mission forfeits the mission but not the vessel.
  run = reincarnate(run, 0, 1, 0).run; // Sha
  run = advanceMission(run).run;
  assert.strictEqual(run.missionStep, 1);
  const d = die(run);
  assert.strictEqual(d.ok, true);
  assert.strictEqual(d.earned, null);
  run = d.run;
  assert.strictEqual(run.missionCreature, null);
  assert.ok(!run.nameplates.includes('sha'));
  const back = reincarnate(run, 0, 1, 0);
  assert.strictEqual(back.ok, true, 'Sha can be picked again after a forfeited mission');
  assert.strictEqual(back.run.missionStep, 0);
});

test('helpers: creatureByVessel, nameOf, livesRemaining', () => {
  assert.strictEqual(creatureByVessel('sha').name, 'SHA');
  assert.strictEqual(creatureByVessel('jin_soul').name, 'JIN');
  assert.strictEqual(creatureByVessel('nope'), null);
  assert.strictEqual(nameOf('rin'), 'RIN');
  assert.strictEqual(nameOf('kai'), 'KAI');
  assert.strictEqual(nameOf('???'), '???');
  const run = createRun();
  assert.strictEqual(livesRemaining(run), 9);
  assert.strictEqual(creatureNameplates(run), 0);
});

test('FACE_ART matches modes.js EM_FACE (read as text, no import)', () => {
  const text = fs.readFileSync(join(ROOT, 'game', 'js', 'modes.js'), 'utf8');
  const block = text.slice(text.indexOf('const EM_FACE = {'), text.indexOf('};', text.indexOf('const EM_FACE = {')));
  for (const part of ['eyes', 'nose', 'mouth']) {
    for (const p of FACE_ART[part]) {
      assert.ok(block.includes(p), `EM_FACE missing ${part} ${p}`);
    }
    assert.strictEqual(FACE_ART[part].length, 3, `${part} has 3 options`);
  }
  // The block must contain exactly the 9 paths (no silent extras).
  const found = [...block.matchAll(/D_FACE_b\d+_\d+x\d+\.png/g)].map((m) => m[0]);
  assert.strictEqual(found.length, 9);
});

test('sound slots exist in game/data/eastern-mind-sfx.json', () => {
  const data = JSON.parse(fs.readFileSync(join(ROOT, 'game', 'data', 'eastern-mind-sfx.json'), 'utf8'));
  for (const slot of Object.values(TRANSMIGRATION_SFX)) {
    assert.ok(data.slots[slot], `slot ${slot} exists`);
    assert.match(data.slots[slot], /\.wav$/, `slot ${slot} points at audio`);
  }
  assert.match(data.slots['reincarn.death'], /R_JIN/);
  assert.match(data.slots['reincarn.rebirth'], /R_SHA/);
  assert.match(data.slots['ui.click'], /D_FACE/);
});

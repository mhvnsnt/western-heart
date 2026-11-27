// Roly-Polys world hub — data integrity + pure game logic.
// Run: node test/rolypolys-hub.test.mjs  (same as every test/*.test.mjs in CI)
import assert from 'node:assert/strict';
import {
  ROLYPOLYS_WORLD,
  ROLYPOLYS_AREAS,
  ROLYPOLYS_ENDINGS,
  ROLYPOLYS_MINIGAMES,
  ROLYPOLYS_GOD_WITHIN,
  ROLYPOLYS_VIGNETTES,
  ROLYPOLYS_NANAKOROBI_GAMES,
} from '../game/data/rolypolys-world.js';
import {
  mulberry32,
  areaById,
  regionById,
  listAreas,
  listRegions,
  listScenes,
  totalScenes,
  totalRegions,
  sceneExists,
  endingForArea,
  vignetteFor,
  createHubState,
  sailTo,
  visitScene,
  areaProgress,
  SHOOTING,
  spawnTargets,
  shootingHit,
  shootingShards,
  COOKING,
  cookingJudge,
  createCooking,
  cookingRound,
  SLOT_SYMBOLS,
  spinSlot,
  slotPayout,
  BULL,
  createBull,
  bullStep,
  bullShards,
} from '../game/js/rolypolys-hub.js';

const W = ROLYPOLYS_WORLD;

// ---- catalog integrity (verbatim disc catalog) ----
assert.equal(listAreas(W).length, 7, '7 world areas');
assert.deepEqual(listAreas(W), ['AFRICA', 'AMERICA', 'ASIA', 'EUROPA', 'JAPAN', 'OCEANIA', 'SOUTHAME']);
assert.equal(totalRegions(W), 40, '40 regions total');
assert.equal(totalScenes(W), 288, '288 scenes total');
for (const area of ROLYPOLYS_AREAS) {
  for (const region of area.regions) {
    assert.ok(region.scenes.length > 0, `${area.id}/${region.id} has scenes`);
    assert.equal(new Set(region.scenes).size, region.scenes.length, `${area.id}/${region.id} no duplicate scenes`);
    for (const s of region.scenes) {
      assert.equal(s, s.toUpperCase(), `${s} is disc 8.3 upper-case`);
      assert.ok(/^[A-Z0-9]+$/.test(s), `${s} is alphanumerics only`);
    }
  }
}
// Every embedded minigame scene exists in the catalog (or the NANKMAP link list).
for (const m of ROLYPOLYS_MINIGAMES) {
  const inAreas = sceneExists(W, m.area, m.region, m.id);
  const inLinks = (W.links || []).some((l) => l.id === m.region && l.scenes.includes(m.id));
  assert.ok(inAreas || inLinks, `minigame ${m.id} exists at ${m.area}/${m.region}`);
}
// Every god-within anchor exists in the catalog.
for (const g of ROLYPOLYS_GOD_WITHIN) {
  assert.ok(sceneExists(W, g.area, g.region, g.scene), `god-within anchor ${g.scene} exists`);
}
// Endings cover all 7 areas; exactly the 4 on-disc continent ENDs + 3 finales.
assert.equal(Object.keys(ROLYPOLYS_ENDINGS).length, 7, 'ending per area');
for (const id of listAreas(W)) assert.ok(endingForArea(W, id), `ending for ${id}`);
const continentEnds = Object.values(ROLYPOLYS_ENDINGS).filter((e) => e.kind === 'continent');
assert.equal(continentEnds.length, 4, '4 per-continent END movies on disc');
assert.deepEqual(continentEnds.map((e) => e.movie).sort(), ['AFEND', 'ASIAEND', 'SAEND', 'USAEND']);
// 26 vignettes, A–Z exactly once.
assert.equal(ROLYPOLYS_VIGNETTES.length, 26, '26 vignettes');
assert.deepEqual(ROLYPOLYS_VIGNETTES.map((v) => v.letter).join(''), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ');
for (const v of ROLYPOLYS_VIGNETTES) {
  assert.ok(v.word && v.text, `${v.letter} has word + text`);
  assert.equal(vignetteFor(W, v.letter.toLowerCase()).word, v.word, 'vignette lookup is case-insensitive');
}
assert.equal(vignetteFor(W, '['), null, 'unknown letter returns null');
// Nanakorobi games: shooting, cooking, slot.
assert.equal(ROLYPOLYS_NANAKOROBI_GAMES.length, 3, '3 Nanakorobi games');
assert.deepEqual(ROLYPOLYS_NANAKOROBI_GAMES.map((g) => g.id), ['SHOOTING', 'MISO_KO', 'SLOT']);

// ---- hub state machine ----
const st = createHubState();
assert.equal(st.area, 'JAPAN', 'hub starts on the home leg');
assert.equal(sailTo(st, W, 'NOWHERE').ok, false, 'unknown area rejected');
assert.equal(sailTo(st, W, 'AFRICA').ok, true, 'sail to Africa');
assert.equal(st.area, 'AFRICA');
assert.deepEqual(areaProgress(st, W, 'AFRICA'), { visited: 0, total: 30 });
let r = visitScene(st, W, 'AFRICA', 'RUINS', 'SHRINE');
assert.equal(r.ok, true);
assert.equal(r.firstVisit, true);
assert.equal(r.item, 'SHRINE', 'first visit collects the scene item');
assert.equal(st.items.length, 1);
r = visitScene(st, W, 'AFRICA', 'RUINS', 'SHRINE');
assert.equal(r.firstVisit, false, 'revisit does not re-collect');
assert.equal(r.item, null);
assert.equal(st.items.length, 1);
assert.equal(visitScene(st, W, 'AFRICA', 'RUINS', 'NOPE').ok, false, 'unknown scene rejected');
// Completing an area unlocks its ending exactly once.
const st2 = createHubState();
let last = null;
for (const region of listRegions(W, 'SOUTHAME')) {
  for (const scene of listScenes(W, 'SOUTHAME', region)) {
    last = visitScene(st2, W, 'SOUTHAME', region, scene);
  }
}
assert.equal(last.ending.movie, 'SAEND', 'South America ending is SAEND');
assert.equal(st2.endings.length, 1, 'ending unlocked once');
assert.deepEqual(areaProgress(st2, W, 'SOUTHAME'), { visited: 7, total: 7 });
// Finale areas close on END.DXR, not a continent END.
const st3 = createHubState();
for (const region of listRegions(W, 'JAPAN')) {
  for (const scene of listScenes(W, 'JAPAN', region)) visitScene(st3, W, 'JAPAN', region, scene);
}
assert.equal(st3.endings[0], 'JAPAN');
assert.equal(endingForArea(W, 'JAPAN').kind, 'finale', 'Japan closes on the finale');

// ---- shooting gallery ----
const rngA = mulberry32(12345);
const rngB = mulberry32(12345);
assert.deepEqual(spawnTargets(rngA, 3, 640, 360), spawnTargets(rngB, 3, 640, 360), 'spawn is seeded');
const targets = [{ x: 100, y: 100, r: 20 }, { x: 300, y: 200, r: 10 }];
assert.equal(shootingHit(targets, 100, 100).x, 100, 'dead-center hit');
assert.equal(targets.length, 1, 'hit target removed');
assert.equal(shootingHit(targets, 0, 0), null, 'clear miss');
assert.equal(shootingHit(targets, 300, 210).x, 300, 'edge hit counts (r=10)');
assert.equal(shootingShards(8), 8 * SHOOTING.shardsPerHit, '10 shards a hit');
assert.equal(shootingShards(0), 0);

// ---- cooking ----
assert.equal(cookingJudge(50).grade, 'perfect');
assert.equal(cookingJudge(55).grade, 'perfect', 'perfect edge ±5');
assert.equal(cookingJudge(56).grade, 'good');
assert.equal(cookingJudge(65).grade, 'good', 'good edge ±15');
assert.equal(cookingJudge(66).grade, 'miss');
assert.equal(cookingJudge(0).grade, 'miss');
const cook = createCooking();
let cr = cookingRound(cook, 50);
assert.equal(cr.judge.grade, 'perfect');
assert.equal(cr.score, COOKING.shardsPerfect);
cr = cookingRound(cook, 60);
assert.equal(cr.judge.grade, 'good');
cr = cookingRound(cook, 0);
assert.equal(cr.judge.grade, 'miss');
assert.equal(cr.done, true, '3 rounds ends the cook');
assert.equal(cook.score, COOKING.shardsPerfect + COOKING.shardsGood);
assert.equal(cookingRound(cook, 50).ok, false, 'no 4th round');

// ---- slot machine ----
assert.equal(SLOT_SYMBOLS.length, 9, '9 reel symbols (8 souls + Trader)');
assert.equal(new Set(SLOT_SYMBOLS).size, 9, 'symbols unique');
const spinA = spinSlot(mulberry32(999));
const spinB = spinSlot(mulberry32(999));
assert.deepEqual(spinA, spinB, 'spin is seeded');
assert.ok(spinA.every((s) => SLOT_SYMBOLS.includes(s)), 'spin symbols come from the set');
assert.deepEqual(slotPayout(['凛', '凛', '凛'], 10), { payout: 100, kind: 'three' });
assert.deepEqual(slotPayout(['凛', '凛', '商'], 10), { payout: 20, kind: 'two' });
assert.deepEqual(slotPayout(['凛', '商', '凛'], 10), { payout: 20, kind: 'two' });
assert.deepEqual(slotPayout(['凛', '闘', '商'], 10), { payout: 0, kind: 'none' });

// ---- bull dodge ----
const bull = createBull(mulberry32(7));
assert.ok(bull.bullLane >= 0 && bull.bullLane < BULL.lanes, 'bull spawns in a lane');
assert.equal(bull.bullY, BULL.startY);
const rngC = mulberry32(3);
const b2 = createBull(mulberry32(3));
// Step the bull to the player row without moving: it either dodges or gores.
let res;
for (let i = 0; i < BULL.startY; i++) res = bullStep(b2, 0, rngC);
assert.ok(res.over === true || res.dodged === true, 'at the player row the ox dodges or gores');
if (res.over) assert.equal(res.gored, true, 'same lane at the player row gores');
if (res.dodged) assert.equal(b2.dodges, 1, 'dodge counted');
assert.equal(bullShards(4), 4 * BULL.shardsPerDodge, '5 shards a dodge');
assert.equal(bullStep(b2, 0, rngC).ok, b2.over ? false : true, 'step after gore is rejected');
// Forced gore: put the player in the bull's lane at the last step.
const b3 = createBull(mulberry32(11));
b3.bullY = 1;
b3.playerLane = b3.bullLane;
const gore = bullStep(b3, 0, mulberry32(1));
assert.equal(gore.over, true, 'same lane at the player row gores');
assert.equal(gore.gored, true);
assert.equal(b3.over, true);

console.log('rolypolys-hub: 7 areas, 40 regions, 288 scenes, 26 vignettes, hub + shooting + cooking + slot + bull ok');

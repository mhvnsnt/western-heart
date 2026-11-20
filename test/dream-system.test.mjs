// Dream system core (Phase 2: LSD dream core, 2026-11-20). Node, no browser, no DOM.
// Run: node test/dream-system.test.mjs
//
// Every number below is grounded in the verified spec
// (klnuno/lsd-decomp docs/engine/dream-system.md, links.md,
// stages-and-places.md) or in the shipped WH data file
// (game/data/dream-stages.json), never invented.

import test from 'node:test';
import assert from 'node:assert/strict';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readFileSync } from 'node:fs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const M = await import(join(ROOT, 'game', 'js', 'dream-system.js'));
const DATA = JSON.parse(readFileSync(join(ROOT, 'game', 'data', 'dream-stages.json'), 'utf8'));

const SEED = 12345;
function makeSys(seed = SEED) {
  return new M.DreamSys(DATA, { seed, dreamer: { id: 'pantera', name: 'Pantera' } });
}

test('PSY-Q LCG: same seed, same stream; int(n) stays in range', () => {
  const a = new M.PsyqRand(42), b = new M.PsyqRand(42);
  for (let i = 0; i < 50; i++) assert.equal(a.next(), b.next());
  const c = new M.PsyqRand(7);
  for (let i = 0; i < 100; i++) {
    const v = c.int(6);
    assert.ok(v >= 0 && v < 6);
  }
});

test('Mood_Resolve: decomp start-square example (8,-4) -> (-9,-5), yellow', () => {
  const acc = new M.MoodAccumulator();
  acc.log(8, -4);
  // sum/count + last/3 per axis: x = 8 + 8/3 = 10 -> wraps past 9 to -9;
  // y = -4 + -4/3 = -5. The decomp names this exact case yellow.
  assert.deepEqual(acc.resolve(), [-9, -5]);
  assert.equal(M.dayColorName([-9, -5]), 'yellow');
});

test('day point: chunk (3,-3) + entity (3,-3) resolve to (4,-4), cyan — the decomp lions case', () => {
  // One log of (3,-3) resolves per axis to 3 + 3/3 = 4 and -3 + -3/3 = -4:
  // the decomp's Natural World example ends the day exactly cyan, (4, -4).
  const chunk = new M.MoodAccumulator(); chunk.log(3, -3);
  const ent = new M.MoodAccumulator(); ent.log(3, -3);
  assert.deepEqual(M.computeDayPoint(chunk, ent), [4, -4]);
  assert.equal(M.dayColorName([4, -4]), 'cyan');
});

test('day point with no touches is the chunk result alone', () => {
  const chunk = new M.MoodAccumulator(); chunk.log(2, 3);
  const ent = new M.MoodAccumulator();
  // chunk resolve: 2 + 0 = 2; 3 + 1 = 4.
  assert.deepEqual(M.computeDayPoint(chunk, ent), [2, 4]);
});

test('colour band table spot checks', () => {
  assert.equal(M.dayColorName([0, 0]), 'white');
  assert.equal(M.dayColorName([-9, -9]), 'yellow');
  assert.equal(M.dayColorName([9, 9]), 'pink');
  assert.equal(M.dayColorName([-9, 9]), 'green');
  assert.equal(M.dayColorName([0, -9]), 'red');
  assert.equal(M.dayColorName([0, 9]), 'blue');
  assert.equal(M.dayColorName([9, -9]), 'cyan');
});

test('chunk/tile keys pack and parse (col | row<<8, x | y<<8)', () => {
  assert.equal(M.chunkKey(3, 5), 3 | (5 << 8));
  assert.deepEqual(M.parseChunkKey(M.chunkKey(3, 5)), { col: 3, row: 5 });
  assert.equal(M.tileKey(19, 10), 19 | (10 << 8));
  assert.deepEqual(M.parseTileKey(M.tileKey(19, 10)), { x: 19, y: 10 });
});

test('Link_Find: exact tile match; null tile matches any tile of the chunk', () => {
  const lists = [[
    { chunk: [0, 0], tile: [19, 10], toStage: 1, toIndex: 0 },
    { chunk: [0, 0], tile: null, toStage: 2, toIndex: 1 },
  ]];
  const hit = M.findLink(lists, 0, { chunkCol: 0, chunkRow: 0, tileX: 19, tileY: 10 });
  assert.equal(hit.entry.toStage, 1);
  const any = M.findLink(lists, 0, { chunkCol: 0, chunkRow: 0, tileX: 3, tileY: 3 });
  assert.equal(any.entry.toStage, 2);
  assert.equal(M.findLink(lists, 0, { chunkCol: 1, chunkRow: 0, tileX: 3, tileY: 3 }), null);
});

test('facing tolerance is +-44 degrees, wrapping through 0/360', () => {
  assert.equal(M.headingWithin(0, 44), true);
  assert.equal(M.headingWithin(0, 45), false);
  assert.equal(M.headingWithin(350, 10), true);
  assert.equal(M.headingWithin(180, 0), false);
});

test('scores: 1,000,000 per nav flag, 50,000,000 for all 30, -11,024 per dynamic link, floor 0', () => {
  const j = new M.Journal();
  assert.equal(j.calcNavScore(), 0);
  j.navFlags[0] = true;
  assert.equal(j.calcNavScore(), 1000000);
  j.dynamicLinkCount = 1;
  assert.equal(j.calcNavScore(), 1000000 - 11024);
  j.dynamicLinkCount = 100;
  assert.equal(j.calcNavScore(), 0);
  j.dynamicLinkCount = 0;
  j.navFlags.fill(true);
  assert.equal(j.calcNavScore(), 50000000);
});

test('flashback unlock needs score above 9,999,999 AND a kept memory', () => {
  const j = new M.Journal();
  j.navFlags.fill(true); // 50,000,000 nav score
  assert.equal(j.canFlashback(), false); // no memory kept yet
  j.addFlashback({ stage: 0, place: null, rotation: 0, length: 16, day: 1 }, 0);
  assert.equal(j.canFlashback(), true);
  const poor = new M.Journal();
  poor.addFlashback({ stage: 0, place: null, rotation: 0, length: 16, day: 1 }, 0);
  assert.equal(poor.canFlashback(), false); // score 0
});

test('flashback store: max 10, overflow overwrites entry timer % 9', () => {
  const j = new M.Journal();
  for (let i = 0; i < 10; i++) j.addFlashback({ stage: i, place: null, rotation: 0, length: 16, day: 1 }, i);
  assert.equal(j.flashbacks.length, 10);
  j.addFlashback({ stage: 99, place: null, rotation: 0, length: 16, day: 1 }, 9);
  assert.equal(j.flashbacks.length, 10);
  assert.equal(j.flashbacks[0].stage, 99); // 9 % 9 == 0
});

test('journal save round-trips (magic, day, year, graph, flags)', () => {
  const j = new M.Journal();
  j.dayNumber = 40; j.yearNumber = 1; j.navFlags[5] = true;
  j.graph[0] = [4, -4]; j.dynamicLinkCount = 3; j.instanceScore = 25000;
  const back = M.Journal.fromJSON(j.toJSON());
  assert.equal(back.dayNumber, 40);
  assert.equal(back.yearNumber, 1);
  assert.equal(back.navFlags[5], true);
  assert.deepEqual(back.graph[0], [4, -4]);
  assert.equal(back.dynamicLinkCount, 3);
  assert.equal(back.instanceScore, 25000);
  assert.deepEqual(M.Journal.fromJSON({ magic: 'nope' }).dayNumber, 1);
});

test('chooseStart: first day (0,0) finds the Palace (0,0) override chunk', () => {
  const sys = makeSys();
  const start = sys.chooseStart();
  assert.equal(start.stageIndex, 0);
  assert.deepEqual([start.place.chunkCol, start.place.chunkRow], [0, 0]);
});

test('texture sets cycle on the 40-day clock: 1, 2, 3, 4 sets', () => {
  const sets = ['clear', 'ink', 'ember', 'prism'];
  const rng = new M.PsyqRand(1);
  assert.equal(M.textureSetForDay(1, sets, rng), 'clear');
  assert.ok(['clear', 'ink'].includes(M.textureSetForDay(15, sets, rng)));
  assert.ok(['clear', 'ink', 'ember'].includes(M.textureSetForDay(25, sets, rng)));
  assert.ok(sets.includes(M.textureSetForDay(35, sets, rng)));
});

test('special days: day 9 is the Festival; day 1 is ordinary', () => {
  assert.equal(M.specialDayFor(DATA, 9).title, 'Festival of the First Dream');
  assert.equal(M.specialDayFor(DATA, 1), null);
  assert.equal(M.specialDayFor(DATA, 365).title, "Year's End — the Dreaming Closes");
});

test('wall links arm only on timer % 16 == 0', () => {
  const sys = makeSys();
  sys.startDay();
  sys.timerTicks = 15;
  assert.equal(sys.dynamicLinkOn, false);
  sys.timerTicks = 16;
  assert.equal(sys.dynamicLinkOn, true);
});

test('random link: rand()%6 among stages 0..5, counts a dynamic link', () => {
  const sys = makeSys();
  sys.startDay();
  const before = sys.journal.dynamicLinkCount;
  const res = sys.linkRandom();
  assert.equal(res.kind, 'random');
  assert.ok(res.toStage >= 0 && res.toStage <= 5);
  assert.equal(sys.journal.dynamicLinkCount, before + 1);
});

test('extra link on the Tree: same-place move, limit becomes elapsed + 10s', () => {
  const sys = makeSys();
  sys.startDay();
  sys.stageIndex = 3; // Tree of Life, extraListOn
  sys.extraListOn = true;
  sys.place = { chunkCol: 8, chunkRow: 8, tileX: 12, tileY: 12, yawDeg: 0 };
  sys.timerTicks = 100;
  sys.timeLimitTicks = 1000;
  const res = sys.tryExtraLink();
  assert.equal(res.kind, 'extra');
  assert.equal(sys.timeLimitTicks, 100 + 10 * M.TICKS_PER_SECOND);
});

test('fall: allowed from a fall stage (ends the day), refused elsewhere', () => {
  const sys = makeSys();
  sys.startDay();
  sys.stageIndex = 1; // Marketplace is a fall stage in the data
  const fell = sys.linkFall();
  assert.equal(fell.ended, true);
  assert.equal(fell.reason, 'fall');
  const sys2 = makeSys();
  sys2.startDay();
  sys2.stageIndex = 0; // Palace is not a fall stage
  assert.equal(sys2.linkFall(), null);
  assert.equal(sys2.inDream, true);
});

test('full day: start, walk chunks, touch an entity, time up, day advances', () => {
  const sys = makeSys();
  const start = sys.startDay();
  assert.equal(sys.dayNumber, 1);
  assert.equal(start.stageIndex, 0);
  assert.equal(sys.timeLimitTicks, 240 * M.TICKS_PER_SECOND);
  // Walk the start chunk, then a neighbouring chunk, logging moods.
  sys.place = { chunkCol: 0, chunkRow: 0, tileX: 10, tileY: 10, yawDeg: 0 };
  sys.logCurrentChunk();
  sys.place = { chunkCol: 0, chunkRow: 1, tileX: 10, tileY: 10, yawDeg: 0 };
  sys.logCurrentChunk();
  const touched = sys.touchEntity('koi');
  assert.equal(touched.kind, 'touch');
  assert.ok(sys.journal.instanceScore > 0);
  // Run the clock to the limit: not ended at the limit, ended past it.
  sys.timerTicks = sys.timeLimitTicks - 1;
  assert.equal(sys.tick().ended, false);
  const end = sys.tick();
  assert.equal(end.ended, true);
  assert.equal(end.reason, 'time-up');
  assert.ok(Array.isArray(end.dayPoint) && end.dayPoint.length === 2);
  assert.equal(sys.journal.dayNumber, 2);
  assert.deepEqual(sys.journal.graph[0], end.dayPoint);
  // Tomorrow starts from yesterday's point: a real stage, a real place.
  const next = sys.startDay();
  assert.ok(next.stageIndex >= 0 && next.stageIndex < DATA.stages.length);
  assert.ok(next.place);
});

test('shipped data file: 8 WH stages, 6 link kinds present, every target valid', () => {
  assert.equal(DATA.stages.length, 8);
  for (const kind of ['fixed', 'facing', 'extra', 'scripted']) {
    assert.ok(Array.isArray(DATA.links[kind]), kind + ' list missing');
    assert.equal(DATA.links[kind].length, 8);
  }
  for (const kind of ['fixed', 'facing', 'extra', 'scripted']) {
    DATA.links[kind].forEach((list, si) => {
      (list || []).forEach((e) => {
        assert.ok(e.toStage < DATA.stages.length, kind + ' bad toStage');
        assert.ok(e.toIndex < DATA.stages[e.toStage].arrivalPoints.length, kind + ' bad toIndex');
        assert.ok(e.chunk[0] < DATA.stages[si].cols && e.chunk[1] < DATA.stages[si].rows, kind + ' chunk out of grid');
      });
    });
  }
  const flags = new Set();
  DATA.stages.forEach((s) => s.arrivalPoints.forEach((a) => {
    if (typeof a.navFlag === 'number') flags.add(a.navFlag);
  }));
  // 29 flags assigned; 13 deliberately unassigned (the decomp's goal 13).
  assert.equal(flags.size, 29);
  assert.equal(flags.has(13), false);
  assert.equal(DATA.entities.length, 7);
  assert.equal(Object.keys(DATA.specialDays).length, 6);
});

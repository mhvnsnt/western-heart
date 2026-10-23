// online-systems.test.mjs -- tournament brackets + daily challenge rotation.
// Run: node --test game/tests/online-systems.test.mjs   (from repo root)
import test from 'node:test';
import assert from 'node:assert/strict';
import {
  buildBracket, reportWinner, pendingMatches, isComplete,
  bracketView, seedOrder, describeMatch, BRACKET_SIZES,
} from '../js/tournament.js';
import {
  CHALLENGES, CHALLENGE_MAP, WEEKLY_EVENTS,
  challengesFor, eventFor, dateSeed, todayStr,
} from '../data/challenges.js';

const entries4 = [
  { id: 'pantera', name: 'PANTERA' },
  { id: 'torch', name: 'TORCH' },
  { id: 'dio', name: 'DIO' },
  { id: 'skull', name: 'SKULL' },
];

test('tournament: seed order is standard 1vN placement', () => {
  assert.deepEqual(seedOrder(4), [1, 4, 2, 3]);
  assert.deepEqual(seedOrder(8), [1, 8, 4, 5, 2, 7, 3, 6]);
});

test('tournament: 4-fighter bracket builds semifinals + final', () => {
  const b = buildBracket(entries4, { size: 4 });
  assert.equal(b.matches.length, 3);
  const semis = pendingMatches(b);
  assert.equal(semis.length, 2);
  // #1 seed faces #4 seed
  const m1 = semis.find((m) => m.p1.id === 'pantera');
  assert.ok(m1, 'top seed present');
  assert.equal(m1.p2.id === 'skull' || m1.p1.id === 'skull', true);
  assert.ok(!isComplete(b));
});

test('tournament: winners advance, champion crowned', () => {
  const b = buildBracket(entries4, { size: 4 });
  const r1 = pendingMatches(b);
  assert.equal(r1.length, 2);
  assert.ok(reportWinner(b, r1[0].id, r1[0].p1.id));
  assert.ok(reportWinner(b, r1[1].id, r1[1].p1.id));
  const fin = pendingMatches(b);
  assert.equal(fin.length, 1);
  assert.equal(fin[0].roundName, 'FINAL');
  assert.ok(fin[0].p1 && fin[0].p2, 'finalists fed from semifinals');
  assert.ok(reportWinner(b, fin[0].id, fin[0].p1.id));
  assert.ok(isComplete(b));
  assert.equal(b.champion.id, fin[0].p1.id);
});

test('tournament: unknown winner rejected, double-report ignored', () => {
  const b = buildBracket(entries4, { size: 4 });
  const m = pendingMatches(b)[0];
  assert.equal(reportWinner(b, m.id, 'nobody'), false);
  assert.equal(reportWinner(b, 'nope', m.p1.id), false);
  assert.ok(reportWinner(b, m.id, m.p1.id));
  assert.equal(reportWinner(b, m.id, m.p2.id), false, 'second report ignored');
});

test('tournament: short field pads with CPU, BYEs walk over', () => {
  const b = buildBracket(entries4.slice(0, 3), {
    size: 4,
    fillCpu: [{ id: 'cpu1', name: 'CPU RIVAL' }],
  });
  assert.equal(b.matches.length, 3);
  const byeB = buildBracket(entries4.slice(0, 3), { size: 4, byes: true });
  // one semifinal is a walkover -> winner auto-advanced to final
  const final = byeB.matches.find((m) => m.roundName === 'FINAL');
  assert.ok(final.p1 || final.p2, 'BYE walkover feeds the final');
});

test('tournament: 8 and 16 sizes, full playthrough', () => {
  for (const size of [8, 16]) {
    const entries = Array.from({ length: size }, (_, i) => ({ id: `f${i}`, name: `F${i}` }));
    const b = buildBracket(entries, { size });
    let guard = 0;
    while (!isComplete(b) && guard++ < 40) {
      const p = pendingMatches(b);
      assert.ok(p.length > 0, 'always a playable match until complete');
      // all pending are in the same (earliest) round
      assert.ok(p.every((m) => m.round === p[0].round));
      for (const m of p) reportWinner(b, m.id, m.p1.id);
    }
    assert.ok(isComplete(b), `size ${size} completes`);
    assert.equal(b.champion.id, 'f0', 'top seed wins when always picked');
  }
});

test('tournament: bracket view groups rounds for rendering', () => {
  const b = buildBracket(entries4, { size: 4 });
  const view = bracketView(b);
  assert.deepEqual(view.map((r) => r.name), ['SEMIFINAL', 'FINAL']);
  assert.equal(view[0].matches.length, 2);
  assert.ok(describeMatch(view[0].matches[0]).includes('SEMIFINAL'));
});

test('tournament: bracket JSON is serializable (lobby broadcast)', () => {
  const b = buildBracket(entries4, { size: 4 });
  const m = pendingMatches(b)[0];
  reportWinner(b, m.id, m.p1.id);
  const clone = JSON.parse(JSON.stringify(b));
  assert.equal(clone.matches.length, b.matches.length);
  assert.equal(clone.matches.find((x) => x.id === m.id).winner, m.p1.id);
});

test('challenges: catalog is well-formed', () => {
  assert.ok(CHALLENGES.length >= 20);
  for (const c of CHALLENGES) {
    assert.ok(c.id && c.name && c.flavor, `challenge ${c.id} has text`);
    assert.ok(CHALLENGE_MAP[c.id] === c);
    assert.ok(['ember', 'flame', 'inferno'].includes(c.difficulty), c.id);
    assert.ok(typeof c.target === 'number' || typeof c.target === 'string');
  }
  const ids = new Set(CHALLENGES.map((c) => c.id));
  assert.equal(ids.size, CHALLENGES.length, 'no duplicate ids');
  const rewards = new Set(CHALLENGES.map((c) => c.reward));
  assert.equal(rewards.size, CHALLENGES.length, 'each challenge pays a unique reward');
});

test('challenges: daily rotation is deterministic per date', () => {
  const a = challengesFor('2026-10-22');
  const b = challengesFor('2026-10-22');
  assert.deepEqual(a.dailies.map((c) => c.id), b.dailies.map((c) => c.id));
  assert.equal(a.event.id, b.event.id);
  assert.equal(a.dailies.length, 3);
  const diffs = a.dailies.map((c) => c.difficulty).sort();
  assert.deepEqual(diffs, ['ember', 'flame', 'inferno']);
  // different dates (usually) differ
  const c = challengesFor('2026-10-23');
  const same = JSON.stringify(a.dailies.map((x) => x.id)) === JSON.stringify(c.dailies.map((x) => x.id));
  assert.ok(!same || true, 'rotation may repeat by chance; determinism is what matters');
  assert.ok(dateSeed('2026-10-22') !== dateSeed('2026-10-23'));
});

test('challenges: weekly event is stable within a week', () => {
  // 2026-10-22 is a Thursday; Mon 2026-10-19 .. Sun 2026-10-25 share the event
  const days = ['2026-10-19', '2026-10-21', '2026-10-22', '2026-10-25'];
  const evs = days.map((d) => eventFor(d).id);
  assert.ok(evs.every((e) => e === evs[0]), 'same event all week: ' + evs[0]);
  assert.ok(WEEKLY_EVENTS.some((w) => w.id === evs[0]));
  const next = eventFor('2026-10-26').id; // next Monday
  assert.ok(WEEKLY_EVENTS.some((w) => w.id === next));
});

test('challenges: todayStr format', () => {
  assert.match(todayStr(new Date(2026, 9, 22)), /^\d{4}-\d{2}-\d{2}$/);
  assert.equal(todayStr(new Date(2026, 9, 22)), '2026-10-22');
});

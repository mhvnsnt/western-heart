/* ui-gaps.test.mjs — Lane 3 UI gaps (2026-10-24) pure-core guards.
 *
 * WHAT THIS GUARDS: game/js/ui-gaps.js is the pure core behind the
 * Gap 12/13/14/15/20/21 screens. A regression here silently corrupts
 * favorites, chest loot, replay stores, or VS meta lines — all
 * localStorage-persisted, all user-facing.
 *
 * Run: node --test game/tests/ui-gaps.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {
  loadFavorites, saveFavorite, MAX_FAVORITES,
  recordLastAttire, getLastAttire,
  vsMetaLines, vsDisplayName, readVersusWL,
  rollChest, readTreasureCoins,
  jukeboxTracks, getJukeboxSoundtrack, setJukeboxSoundtrack,
  loadReplays, saveReplay, deleteReplay, exportReplayJson, replayTimeline,
  frameLine, readUiSettings,
} from '../js/ui-gaps.js';

const store = () => {
  const m = new Map();
  return { getItem: (k) => (m.has(k) ? m.get(k) : null), setItem: (k, v) => m.set(k, v) };
};

test('favorites: save, overwrite slot, cap at MAX_FAVORITES', () => {
  const s = store();
  assert.deepEqual(loadFavorites(s), []);
  saveFavorite(s, 0, 'pantera', 'Attire 1');
  assert.equal(loadFavorites(s)[0].fighterId, 'pantera');
  assert.equal(loadFavorites(s)[0].attireLabel, 'Attire 1');
  saveFavorite(s, 0, 'torch', null);
  assert.equal(loadFavorites(s)[0].fighterId, 'torch');
  saveFavorite(s, 1, 'a', null);
  saveFavorite(s, 2, 'b', null);
  saveFavorite(s, 3, 'c', null);
  assert.ok(loadFavorites(s).length <= MAX_FAVORITES);
});

test('last-attire session memory round-trips per fighter', () => {
  const s = store();
  assert.equal(getLastAttire(s, 'pantera'), null);
  recordLastAttire(s, 'pantera', 'Attire 2');
  assert.equal(getLastAttire(s, 'pantera').attireLabel, 'Attire 2');
  assert.equal(getLastAttire(s, 'torch'), null);
});

test('VS meta: rank + W-L + local bout; bars only when measured', () => {
  assert.deepEqual(
    vsMetaLines({ rankName: 'War God', wins: 12, losses: 3, connection: null }),
    ['RANK · WAR GOD', 'W-L · 12-3', 'LOCAL BOUT'],
  );
  assert.ok(vsMetaLines({ connection: 4 })[0].includes('▮▮▮▮▯'));
  assert.deepEqual(vsMetaLines({}), ['LOCAL BOUT']);
  assert.equal(vsDisplayName('PLAYER1', 'Pantera', true), 'Pantera');
  assert.deepEqual(readVersusWL({ versusWL: { w: 2, l: 1 } }), { w: 2, l: 1 });
  assert.equal(readVersusWL({}), null);
});

test('treasure chest: coins always pay, prize only from the locked pool', () => {
  const roll = rollChest({ coins: 100, pool: ['title_ladder', 'frame_ember'], rng: () => 0.5 });
  assert.equal(roll.coins, 130);
  assert.equal(roll.prize, 'frame_ember');
  assert.equal(rollChest({ coins: 0, pool: [] }).prize, null);
  const s = store();
  assert.equal(readTreasureCoins(s), 0);
});

test('jukebox: only available tracks listed; choice round-trips per mode', () => {
  const lib = { tracks: [
    { title: 'A', modes: ['battle'], file: 'a.mp3' },
    { title: 'B', modes: ['menu'], remote: 'x' },
    { title: 'C', modes: ['battle'] },
  ] };
  assert.equal(jukeboxTracks(lib, 'battle').length, 1);
  const s = store();
  assert.equal(getJukeboxSoundtrack(s, 'arcade'), null);
  setJukeboxSoundtrack(s, 'arcade', 'Track A');
  assert.equal(getJukeboxSoundtrack(s, 'arcade'), 'Track A');
  assert.equal(getJukeboxSoundtrack(s, 'versus'), null);
});

test('replay theater: save / timeline / export / delete', () => {
  const s = store();
  const events = [
    { type: 'hit', by: 'p1', move: 'LP1', dmg: 7 },
    { type: 'block', by: 'p2', move: 'RP2', chip: 1 },
    { type: 'round', winner: 'p1', timeLeft: 42 },
  ];
  saveReplay(s, { title: 'T', p1: 'a', p2: 'b', events });
  const [r] = loadReplays(s);
  assert.equal(r.events.length, 3);
  assert.ok(replayTimeline(events)[0].includes('HIT LP1 7 dmg'));
  assert.ok(replayTimeline(events)[2].includes('ROUND'));
  assert.ok(exportReplayJson(r).includes('wh-replay'));
  deleteReplay(s, r.id);
  assert.deepEqual(loadReplays(s), []);
});

test('frame line: numbers only when numeric, never invented', () => {
  assert.equal(
    frameLine('Jab', { startup: 10, active: 2, recovery: 7, onBlock: -2, onHit: 5 }),
    'Jab · STARTUP 10 · ACTIVE 2 · RECOVERY 7 · ON BLOCK -2 · ON HIT +5',
  );
  assert.equal(frameLine('Mystery', {}), 'Mystery · frames n/a');
  assert.equal(frameLine(null, null), '— · frames n/a');
});

test('UI settings: plain-object and store shapes both read', () => {
  assert.equal(readUiSettings({ frameOverlay: true }).frameOverlay, true);
  assert.equal(readUiSettings({}).tournamentLock, false);
  const s = store();
  s.setItem('wh_settings_v1', JSON.stringify({ streamingMode: true }));
  assert.equal(readUiSettings(s).streamingMode, true);
});

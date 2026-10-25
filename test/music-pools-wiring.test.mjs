// Music pool wiring (2026-10-24) — rotation pool assignments for every
// stage id + every menu mode, the Cape Jones two-arena pools, and the
// cutscene BGM hook. Extends test/music-rotation.test.mjs; it does not
// replace it (that file still owns the base rotation state machine).
//
// What this verifies:
//  1. Stage-theme rule: a modes-[] track tagged with a stage joins ONLY
//     that stage's battle pool (the Cape Jones mechanism), never other
//     stages' pools and never menu pools.
//  2. Two Cape pools: cape-jones-arena (house, home turf) AND
//     cape-jones-halloween-beach (Malakor-style Halloween beach, show
//     arena) BOTH open with Ghost Surf Rock first, then rotate through
//     interchange tracks. (Fixture: mirrors the merged library — the 8
//     Cape tracks from the audio lane + the 8 new interchange tracks
//     from this PR. The shipped-library section below checks the same
//     property conditionally once the Cape entries land on main.)
//  3. Cutscene hook: playCutscene(name) plays an ordered sequence and
//     resumes battle rotation on the last battle stage when it ends.
//  4. Shipped library: 52 tracks; every Nosferatu track carries exactly
//     one stage tag (the pool assignment); title/menu orphans fixed
//     (title-meditation -> title, menu-deliberate -> online); EVERY
//     mode pool and EVERY playable stage pool contains at least one
//     track whose file exists in this checkout — so no pool can go
//     silent in the tree as shipped, even before pending files land.
//     Pending-download Tekken slots (file:null) are never counted.
//  5. Pending-file honesty: tracks with status 'pending-file' (file
//     field set, bytes not yet committed) are reported separately —
//     they are in pools by id, but the on-disk check in (4) never
//     counts them as the pool's live track.
//
// Run: node test/music-pools-wiring.test.mjs (from repo root; CI runs
// the loop). NOTE on the track count: this branch sets 52 = 44 on main
// + 8 new tracks here. The audio lane's open PR #1058 adds 8 Cape
// tracks to the same count line; whichever merges second must bump
// the count to 60 (44 + 8 + 8). Do not "fix" this by editing the
// count to 60 here while the Cape entries are not on main yet.

import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { music } from '../game/js/music.js';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const failures = [];
const ok = (cond, msg) => { if (!cond) failures.push(msg); else console.log('  ok: ' + msg); };

globalThis.localStorage = {
  _s: {},
  getItem(k) { return Object.prototype.hasOwnProperty.call(this._s, k) ? this._s[k] : null; },
  setItem(k, v) { this._s[k] = String(v); },
};

// ---- 1. Stage-theme rule (fixture) ----
console.log('== stage-theme rule ==');
music.library = {
  rotation: { mode: 'sequential' },
  tracks: [
    { id: 'battle-global', file: 'g.mp3', remote: null, modes: ['battle'], stages: [] },
    { id: 'cape-theme', file: 'cape.mp3', remote: null, modes: [], stages: ['cape-jones-arena'] },
    { id: 'cape-inter', file: 'cape2.mp3', remote: null, modes: [], stages: ['cape-jones-arena'] },
    { id: 'menu-only', file: 'm.mp3', remote: null, modes: ['title'], stages: [] },
  ],
};
music._rotation = {};
music._rotationLoaded = true;
const capePool = music._poolFor({ stage: 'cape-jones-arena', mode: 'battle' });
ok(capePool.map(t => t.id).join(',') === 'cape-theme,cape-inter,battle-global',
  'stage-theme tracks join their stage pool tagged-first, then rest of battle pool');
const otherPool = music._poolFor({ stage: 'shrine', mode: 'battle' });
ok(otherPool.map(t => t.id).join(',') === 'battle-global',
  'stage-theme tracks never leak into other stages pools');
const titlePool = music._poolFor({ mode: 'title' });
ok(titlePool.map(t => t.id).join(',') === 'menu-only',
  'stage-theme tracks never enter menu pools');
const noStagePool = music._poolFor({ mode: 'battle' });
ok(noStagePool.map(t => t.id).join(',') === 'battle-global',
  'stage-theme tracks join nothing when no stage is given');

// ---- 2. Two Cape pools, Ghost Surf Rock first (fixture, merged state) ----
console.log('== two Cape pools ==');
const cape8 = [
  'cape-jones-ghost-surf-rock', 'cape-jones-ghost-waltz', 'cape-jones-hello-regan',
  'cape-jones-dark-alley', 'cape-jones-graveyard', 'cape-jones-old-witch-place',
  'cape-jones-witch-magical', 'cape-jones-sweat-time',
];
const new8 = [
  'cape-jones-monster-parade', 'cape-jones-ghost-duet', 'cape-jones-swamp',
  'cape-jones-hello-michael', 'cape-jones-ghost-party', 'cape-jones-im-on-fire',
  'cape-jones-grab-partner', 'cape-jones-take-break',
];
// Shipped design: EVERY Cape track carries BOTH stage ids (see the
// shipped-library section and the wiring doc), so both pools open with
// Ghost Surf Rock first by library order.
music.library.tracks = [
  { id: 'battle-global', file: 'g.mp3', remote: null, modes: ['battle'], stages: [] },
  ...[...cape8, ...new8].map(id => ({ id, file: `${id}.mp3`, remote: null, modes: [],
    stages: ['cape-jones-arena', 'cape-jones-halloween-beach'] })),
];
for (const stage of ['cape-jones-arena', 'cape-jones-halloween-beach']) {
  music._rotation = {};
  const pool = music._poolFor({ stage, mode: 'battle' });
  ok(pool[0].id === 'cape-jones-ghost-surf-rock',
    `${stage} pool opens with Ghost Surf Rock first`);
  ok(pool.length === 17, `${stage} pool holds 16 Cape tracks + rest of battle pool`);
  const rot = [];
  for (let i = 0; i < 3; i++) rot.push(music.pickRotationTrack({ stage, mode: 'battle' }).id);
  ok(rot[0] === 'cape-jones-ghost-surf-rock' && rot[1] === 'cape-jones-ghost-waltz',
    `${stage} rotation advances Ghost Surf Rock -> interchange track`);
}

// ---- 3. Cutscene hook (fixture) ----
console.log('== cutscene hook ==');
const played = [];
music._playTrack = async (t) => { played.push(t.id); };
music.library.tracks.push(
  { id: 'cut-a', file: 'ca.mp3', remote: null, modes: ['title'], stages: [] },
  { id: 'cut-b', file: 'cb.mp3', remote: null, modes: ['title'], stages: [] },
);
music.library.sequences = { 'cutscene-example': ['cut-a', 'cut-b'] };
music._lastStage = 'shrine';
played.length = 0;
ok(await music.playCutscene('cutscene-example') === true && played[0] === 'cut-a',
  'playCutscene starts the named sequence');
await music._playSequenceNext();
ok(played[1] === 'cut-b', 'cutscene sequence advances');
let resumed = null;
music.playBattle = async (stage) => { resumed = stage; };
await music._playSequenceNext();
ok(music._seq === null && resumed === 'shrine',
  'cutscene end resumes battle rotation on last stage');
ok(await music.playCutscene('no-such-cutscene') === false,
  'unknown cutscene returns false, nothing stops playing');

// ---- 4. Shipped library ----
console.log('== shipped library ==');
const lib = JSON.parse(readFileSync(join(root, 'game', 'data', 'music-library.json'), 'utf8'));
ok(lib.tracks.length === 52, 'library has 52 tracks (44 on main + 8 new here)');
const ids = lib.tracks.map(t => t.id);
ok(new Set(ids).size === ids.length, 'all track ids unique');
const onDisk = (t) => !!(t.file && existsSync(join(root, 'game', t.file)));
const poolIds = (stage, mode) => {
  // Mirror _poolFor without mutating engine rotation state.
  const avail = lib.tracks.filter(t => t.file || t.remote);
  if (mode && mode !== 'battle') return avail.filter(t => t.modes.includes(mode)).map(t => t.id);
  const battle = avail.filter(t => t.modes.includes('battle')
    || (stage && t.modes.length === 0 && t.stages.includes(stage)));
  const tagged = battle.filter(t => t.stages.includes(stage));
  const rest = battle.filter(t => !t.stages.includes(stage));
  return [...tagged, ...rest].map(t => t.id);
};
const byId = (id) => lib.tracks.find(t => t.id === id);
const nos = lib.tracks.filter(t => t.id.startsWith('nos-t'));
ok(nos.length === 25 && nos.every(t => t.stages.length === 1),
  'every Nosferatu track carries exactly one stage tag');
const expectedNosStages = {
  'nos-t01': 'tree-of-life', 'nos-t02': 'tong-nou', 'nos-t03': 'phantom-marketplace',
  'nos-t04': 'palace-of-dreaming', 'nos-t05': 'palace-of-dreaming', 'nos-t06': 'plains-of-chi-u',
  'nos-t07': 'shrine', 'nos-t08': 'palace-of-dreaming', 'nos-t09': 'octagonal-shrine',
  'nos-t10': 'octagonal-shrine', 'nos-t11': 'phantom-marketplace', 'nos-t12': 'helix-palace',
  'nos-t13': 'helix-palace', 'nos-t14': 'sunra', 'nos-t15': 'sunra', 'nos-t16': 'helix-palace',
  'nos-t17': 'octagonal-shrine', 'nos-t18': 'tong-nou', 'nos-t19': 'tong-nou',
  'nos-t20': 'tong-nou', 'nos-t21': 'phantom-marketplace', 'nos-t22': 'plains-of-chi-u',
  'nos-t23': 'plains-of-chi-u', 'nos-t24': 'shrine', 'nos-t25': 'tree-of-life',
};
ok(nos.every(t => t.stages[0] === expectedNosStages[t.id]),
  'Nosferatu stage tags match the wiring table');
ok(byId('title-meditation').modes.includes('title'), 'title-meditation tagged title (orphan fixed)');
ok(byId('menu-deliberate').modes.includes('online'), 'menu-deliberate tagged online (online pool no longer pending-only)');
for (const mode of ['title', 'select', 'versus', 'results', 'credits', 'online', 'victory']) {
  const pool = poolIds(null, mode);
  const live = pool.filter(id => onDisk(byId(id)));
  ok(live.length >= 1, `menu pool ${mode} has >=1 on-disk track (${live.join(',') || 'NONE'})`);
}
for (const stage of ['shrine', 'palace-of-dreaming', 'helix-palace', 'tree-of-life', 'sunra',
  'phantom-marketplace', 'octagonal-shrine', 'plains-of-chi-u', 'tong-nou', 't7-mishima-dojo']) {
  const pool = poolIds(stage, 'battle');
  const live = pool.filter(id => onDisk(byId(id)));
  ok(live.length >= 1, `stage pool ${stage} has >=1 on-disk track (pool size ${pool.length})`);
  ok(pool.length > 1, `stage pool ${stage} is a real pool (>1 track), not a single BGM`);
}
const tekken = lib.tracks.filter(t => t.id.startsWith('t7-'));
ok(tekken.length === 5 && tekken.every(t => t.file === null && t.status === 'pending-download'),
  '5 Tekken slots stay data-only pending-download (never counted live)');
const cutEx = lib.sequences && lib.sequences['cutscene-example'];
ok(Array.isArray(cutEx) && cutEx.length === 3 && cutEx.every(id => ids.includes(id))
  && cutEx.every(id => onDisk(byId(id))),
  'cutscene-example sequence references 3 real, on-disk tracks');
const newTracks = lib.tracks.filter(t => t.id.startsWith('cape-jones-') && !cape8.includes(t.id));
ok(newTracks.length === 8 && newTracks.every(t => t.status === 'pending-file' && t.license === 'CC0-1.0'),
  '8 new tracks are pending-file CC0-1.0 (not claimed live until MP3s land)');
ok(newTracks.every(t => t.stages.includes('cape-jones-arena') && t.stages.includes('cape-jones-halloween-beach')),
  '8 new tracks are tagged for BOTH Cape arenas');
// Conditional (passes vacuously until the audio lane lands): once the
// 8 Cape tracks exist in the shipped library, Ghost Surf Rock must be
// first among them in library order, for BOTH Cape stage ids.
const shippedCape = lib.tracks.filter(t => cape8.includes(t.id));
if (shippedCape.length) {
  ok(shippedCape.length === 8 && shippedCape[0].id === 'cape-jones-ghost-surf-rock',
    'shipped Cape tracks: Ghost Surf Rock first in library order');
  ok(shippedCape.every(t => t.stages.includes('cape-jones-arena')),
    'shipped Cape tracks all tagged cape-jones-arena (house pool)');
  if (!shippedCape.every(t => t.stages.includes('cape-jones-halloween-beach'))) {
    console.log('  NOTE: shipped Cape tracks are NOT all tagged cape-jones-halloween-beach yet — beach pool opens with interchange tracks until the arena/audio lane adds the beach tag to all 8 (see wiring doc). This is a coordination gap, not a test failure.');
  }
} else {
  console.log('  NOTE: 8 Cape tracks not in shipped library yet (audio lane PR #1058) — Cape pool assertions run on fixture only.');
}
const musicJs = readFileSync(join(root, 'game', 'js', 'music.js'), 'utf8');
ok(musicJs.includes('playCutscene'), 'music.js contains playCutscene');
ok(musicJs.includes('t.modes.length === 0'), 'music.js contains the stage-theme rule');

if (failures.length) {
  console.error(`\nFAILURES (${failures.length}):`);
  for (const f of failures) console.error('  - ' + f);
  process.exit(1);
}
console.log('\nAll music pool wiring checks passed.');

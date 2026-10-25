// Music rotation + Nosferatu multi-track wiring (2026-10-24).
// User report: the game soundtrack + stage BGM must rotate like Tekken's
// jukebox (not one track per stage forever), the correct Nosferatu VHS
// synth score must be cut into MANY standalone tracks (not one long
// score), and everything must be wired 100% — engine + library + call
// sites — not pieces.
// This test verifies:
//  1. Rotation pools: stage-tagged tracks first, then the rest of the
//     battle pool; pending entries (file:null, remote:null) never picked;
//     sequential advance + wrap; mode pools for menus.
//  2. T7 match-point rule: playFinalRound swaps to the current track's
//     finalRound variant only when it exists and is available.
//  3. Sequence state machine: playSequence plays in order, then resumes
//     battle rotation on the last battle stage.
//  4. The shipped game/data/music-library.json: 25 Nosferatu tracks with
//     contiguous 0-5067s coverage, Tekken slots marked pending-download,
//     ep01-fight sequence referencing real tracks, helix-palace tag fix.
// Run: node test/music-rotation.test.mjs (from repo root; CI runs the loop).

import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { music } from '../game/js/music.js';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const failures = [];
const ok = (cond, msg) => { if (!cond) failures.push(msg); else console.log('  ok: ' + msg); };

// Polyfill localStorage for the node run (engine guards it anyway).
globalThis.localStorage = {
  _s: {},
  getItem(k) { return Object.prototype.hasOwnProperty.call(this._s, k) ? this._s[k] : null; },
  setItem(k, v) { this._s[k] = String(v); },
};

// ---- 1. Rotation pools (fixture library) ----
console.log('== rotation pools ==');
music.library = {
  rotation: { mode: 'sequential' },
  tracks: [
    { id: 'stage-a', file: 'a.mp3', remote: null, modes: ['battle'], stages: ['shrine'] },
    { id: 'global-1', file: 'g1.mp3', remote: null, modes: ['battle'], stages: [] },
    { id: 'pending-tekken', file: null, remote: null, modes: ['battle'], stages: ['shrine'] },
    { id: 'global-2', file: 'g2.mp3', remote: null, modes: ['battle'], stages: [] },
    { id: 'title-1', file: 't1.mp3', remote: null, modes: ['title'], stages: [] },
    { id: 'title-2', file: 't2.mp3', remote: null, modes: ['title'], stages: [] },
  ],
};
music._rotation = {};
music._rotationLoaded = true;
const pool = music._poolFor({ stage: 'shrine', mode: 'battle' });
ok(pool.map(t => t.id).join(',') === 'stage-a,global-1,global-2', 'battle pool: stage-tagged first, pending excluded, rest in order');
const seq = [];
for (let i = 0; i < 4; i++) seq.push(music.pickRotationTrack({ stage: 'shrine', mode: 'battle' }).id);
ok(seq.join(',') === 'stage-a,global-1,global-2,stage-a', 'sequential rotation advances and wraps');
const menuSeq = [];
for (let i = 0; i < 3; i++) menuSeq.push(music.pickRotationTrack({ mode: 'title' }).id);
ok(menuSeq.join(',') === 'title-1,title-2,title-1', 'menu pool rotates by mode');
const legacy = music.pickTrack({ stage: 'shrine', mode: 'battle' });
ok(legacy && legacy.id === 'stage-a', 'pickTrack unchanged: first stage match wins');

// ---- 2. Final-round variant ----
console.log('== final-round variant ==');
const played = [];
music._playTrack = async (t) => { played.push(t.id); };
music.current = { track: { id: 't7-dojo-1st', finalRound: 't7-dojo-final' } };
music.library.tracks.push(
  { id: 't7-dojo-final', file: 'dojo-final.mp3', remote: null, modes: ['battle'], stages: [] },
);
ok(await music.playFinalRound() === true && played[0] === 't7-dojo-final', 'playFinalRound swaps to available variant');
music.current = { track: { id: 'nos-t01' } };
ok(await music.playFinalRound() === false, 'playFinalRound no-ops when no variant assigned');
music.current = { track: { id: 't7-dojo-1st', finalRound: 'missing-variant' } };
ok(await music.playFinalRound() === false, 'playFinalRound no-ops when variant unavailable');

// ---- 3. Sequence state machine ----
console.log('== sequence state machine ==');
music.library.tracks.push(
  { id: 's1', file: 's1.mp3', remote: null, modes: ['battle'], stages: [] },
  { id: 's2', file: 's2.mp3', remote: null, modes: ['battle'], stages: [] },
);
music.library.sequences = { 'test-seq': ['s1', 's2'] };
music._lastStage = 'shrine';
played.length = 0;
ok(await music.playSequence('test-seq') === true && played[0] === 's1', 'playSequence starts with first track');
await music._playSequenceNext();
ok(played[1] === 's2', 'sequence advances to second track');
let battleResumed = null;
music.playBattle = async (stage) => { battleResumed = stage; };
await music._playSequenceNext();
ok(music._seq === null && battleResumed === 'shrine', 'sequence end resumes battle rotation on last stage');
ok(await music.playSequence('no-such-seq') === false, 'unknown sequence returns false');

// ---- 4. Shipped library data ----
console.log('== shipped library ==');
const lib = JSON.parse(readFileSync(join(root, 'game', 'data', 'music-library.json'), 'utf8'));
ok(Array.isArray(lib.tracks) && lib.tracks.length === 52, 'library has 52 tracks (14 existing + 25 nos + 5 tekken pending + 8 new here)');
const ids = lib.tracks.map(t => t.id);
ok(new Set(ids).size === ids.length, 'all track ids unique');
const nos = lib.tracks.filter(t => t.id.startsWith('nos-t'));
ok(nos.length === 25, '25 Nosferatu game tracks');
let cur = 0;
let contiguous = true;
for (const t of nos) {
  const [a, b] = t.source.range_sec;
  if (a !== cur) contiguous = false;
  cur = b;
}
ok(contiguous && cur === 5067, 'nos tracks contiguous 0-5067s, no gaps or overlaps');
ok(nos.every(t => t.file && t.file.startsWith('assets/music/nosferatu-') && t.modes.includes('battle')),
  'every nos track has a game file path and battle mode');
ok(nos.every(t => t.title.includes('Nosferatu1922VHS') && !t.title.includes('Bernard') && !t.title.includes('Schirmann')),
  'nos titles use the VHS-synth scheme name, never Bernard/Schirmann names');
const tekken = lib.tracks.filter(t => t.id.startsWith('t7-'));
ok(tekken.length === 5 && tekken.every(t => t.file === null && t.remote === null && t.status === 'pending-download'),
  '5 Tekken slots, all data-only pending-download (engine skips them)');
ok(lib.tracks.find(t => t.id === 't7-dojo-1st').finalRound === 't7-dojo-final',
  'dojo Round 1 names its Final Round variant');
const implosion = lib.tracks.find(t => t.id === 'battle-implosion');
ok(implosion && implosion.stages.join(',') === 'helix-palace', 'battle-implosion tag fixed to stages.js id helix-palace');
ok(!JSON.stringify(lib.tracks).includes('helios-palace'), 'no stale helios-palace tag remains');
const ep01 = lib.sequences && lib.sequences['ep01-fight'];
ok(Array.isArray(ep01) && ep01.length === 9 && ep01.every(id => ids.includes(id)),
  'ep01-fight sequence references 9 real tracks');
ok(lib.rotation && lib.rotation.mode === 'sequential', 'rotation mode sequential');
ok(lib.tracks.every(t => t.id && t.title && t.license && t.credit && Array.isArray(t.moods) && Array.isArray(t.modes)),
  'every track carries id/title/license/credit/moods/modes');

// ---- 5. Engine file carries the new methods ----
console.log('== engine methods present ==');
const musicJs = readFileSync(join(root, 'game', 'js', 'music.js'), 'utf8');
for (const m of ['pickRotationTrack', 'playFinalRound', 'playSequence', '_playSequenceNext', '_poolFor']) {
  ok(musicJs.includes(m), `music.js contains ${m}`);
}

if (failures.length) {
  console.error(`\nFAILURES (${failures.length}):`);
  for (const f of failures) console.error('  - ' + f);
  process.exit(1);
}
console.log('\nAll music rotation checks passed.');

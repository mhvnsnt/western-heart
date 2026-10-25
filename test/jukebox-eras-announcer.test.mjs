// Jukebox era browse + announcer events + RTPC helpers (Lane 4 audio,
// 2026-10-24). Verifies, against the SHIPPED library and the new pure
// modules (no DOM, no fetch, no audio bytes needed):
//  1. Era browse: 4 eras, WH content only; Cape Jones main first;
//     Tekken data-only era lists but never resolves to a track.
//  2. Engine pending rule: music.js pickTrack / pools NEVER return
//     a status pending-download track, even as first stage/mode
//     match (the latent pickTrack gap this PR closes).
//  3. Announcer events: all 8 fight events resolve to real manifest
//     clips; character-select is explicitly needs-recording (no
//     invented line, no fake clip).
//  4. Pools consistency guard catches the PR #1046 cape mismatch
//     (mainTrack id/file vs canonical library entry) on synthetic
//     input, and passes on consistent input.
//  5. RTPC/jitter/no-repeat numbers match the research sketch.
// Run: node test/jukebox-eras-announcer.test.mjs (from repo root;
// CI runs the loop over test/*.test.mjs).

import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { music } from '../game/js/music.js';
import {
  listEras, browseEraTracks, playableEraQueue, resolveEraTrack,
  checkPoolsConsistency, isPlayableTrack,
} from '../game/js/jukebox-eras.js';
import { resolveAnnouncerClip, announcerEventNames } from '../game/js/announcer-events.js';
import {
  computeIntensity, jitterRate, pickNoRepeat, masterCompressorSettings,
  ENGINE_STATES, BUSES,
} from '../game/js/audio/rtpc.js';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const failures = [];
const ok = (cond, msg) => { if (!cond) failures.push(msg); else console.log('  ok: ' + msg); };

globalThis.localStorage = {
  _s: {},
  getItem(k) { return Object.prototype.hasOwnProperty.call(this._s, k) ? this._s[k] : null; },
  setItem(k, v) { this._s[k] = String(v); },
};

const lib = JSON.parse(readFileSync(join(root, 'game', 'data', 'music-library.json'), 'utf8'));
const eras = JSON.parse(readFileSync(join(root, 'game', 'data', 'jukebox-eras.json'), 'utf8'));
const ann = JSON.parse(readFileSync(join(root, 'game', 'data', 'announcer-events.json'), 'utf8'));
const manifest = JSON.parse(readFileSync(join(root, 'game', 'data', 'audio-download-manifest.json'), 'utf8'));
const tracks = lib.tracks;

// ---- 1. Era browse ----
console.log('== era browse ==');
const listed = listEras(eras);
ok(listed.map((e) => e.id).join(',') === 'wh-originals,nosferatu,cape-jones,tekken-data-only',
  '4 eras listed in order');
ok(listed.find((e) => e.id === 'tekken-data-only').playable === false,
  'tekken-data-only era is listed but not playable');
ok(listed.find((e) => e.id === 'cape-jones').mainTrackId === 'cape-jones-ghost-surf-rock',
  'cape era main track is Ghost Surf Rock (canonical id)');
const capeBrowse = browseEraTracks(eras, tracks, 'cape-jones');
ok(capeBrowse.map((t) => t.id).join(',') ===
  'cape-jones-ghost-surf-rock,cape-jones-ghost-waltz,cape-jones-hello-regan,cape-jones-dark-alley,cape-jones-graveyard,cape-jones-old-witch-place,cape-jones-witch-magical,cape-jones-sweat-time',
  'cape browse: 8 tracks, Ghost Surf Rock first, exact task filenames underneath');
ok(capeBrowse.every((t) => t.file && t.file.startsWith('assets/music/cape-jones-') && t.file.endsWith('.mp3')),
  'every cape track file is an exact cape-jones-*.mp3 path');
ok(capeBrowse.every((t) => t.artist === 'Loyalty Freak Music' && t.license === 'CC0-1.0'),
  'every cape track is Loyalty Freak Music, CC0 1.0');
ok(!capeBrowse.some((t) => t.title === 'A ghost Waltz' && t.id === 'cape-jones-ghost-surf-rock'),
  'Ghost Surf Rock is the theme; A ghost Waltz is interchanging only (never the theme id)');
const capeQueue = playableEraQueue(eras, tracks, 'cape-jones');
ok(capeQueue[0].id === 'cape-jones-ghost-surf-rock' && capeQueue.length === 8,
  'cape play queue leads with Ghost Surf Rock, all 8');
const st = {};
const cycle = [];
for (let i = 0; i < 9; i++) cycle.push(resolveEraTrack({ erasDoc: eras, libraryTracks: tracks, eraId: 'cape-jones', state: st }).id);
ok(cycle[0] === 'cape-jones-ghost-surf-rock' && cycle[8] === 'cape-jones-ghost-surf-rock',
  'cape cycle repeats with Ghost Surf Rock leading every cycle (wrap)');
ok(resolveEraTrack({ erasDoc: eras, libraryTracks: tracks, eraId: 'tekken-data-only', state: {} }) === null,
  'tekken-data-only era resolves to null — never a track');
ok(resolveEraTrack({ erasDoc: eras, libraryTracks: tracks, eraId: 'no-such-era', state: {} }) === null,
  'unknown era resolves to null');
const nosQueue = playableEraQueue(eras, tracks, 'nosferatu');
ok(nosQueue.length === 25 && nosQueue[0].id === 'nos-t01' && nosQueue[24].id === 'nos-t25',
  'nosferatu era queue: 25 tracks in order');
ok(playableEraQueue(eras, tracks, 'wh-originals').length === 14,
  'wh-originals era queue: 14 tracks');
ok(!JSON.stringify(eras).includes('tekken-7-ost') && !eras.eras.some((e) => (e.trackIds || []).some((id) => !tracks.some((t) => t.id === id))),
  'every era track id resolves to a real library track; no Tekken audio file claimed');

// ---- 2. Engine pending rule ----
console.log('== engine pending rule ==');
music.library = {
  rotation: { mode: 'sequential' },
  tracks: [
    { id: 't7-dojo-1st', file: null, remote: null, modes: ['battle'], stages: ['t7-mishima-dojo'], status: 'pending-download' },
    { id: 'stage-a', file: 'a.mp3', remote: null, modes: ['battle'], stages: ['t7-mishima-dojo'] },
    { id: 't7-select', file: null, remote: null, modes: ['select'], stages: [], status: 'pending-download' },
    { id: 'select-1', file: 's1.mp3', remote: null, modes: ['select'], stages: [] },
  ],
};
music._rotation = {};
music._rotationLoaded = true;
ok(music.pickTrack({ stage: 't7-mishima-dojo', mode: 'battle' }).id === 'stage-a',
  'pickTrack skips pending-download first stage match (was a latent pick)');
ok(music.pickTrack({ mode: 'select' }).id === 'select-1',
  'pickTrack skips pending-download first mode match');
ok(music._poolFor({ stage: 't7-mishima-dojo', mode: 'battle' }).every((t) => t.status !== 'pending-download'),
  'rotation pool contains no pending-download track');
ok(isPlayableTrack({ file: 'x.mp3', status: 'pending-download' }) === false &&
  isPlayableTrack({ file: 'x.mp3', status: 'pending-file' }) === true &&
  isPlayableTrack({ file: null, remote: null }) === false,
  'playability: pending-download excluded, pending-file listed, fileless excluded');
// Shipped library: pending slots still data-only, cape tracks present.
const shippedPending = tracks.filter((t) => t.status === 'pending-download');
ok(shippedPending.length === 5 && shippedPending.every((t) => t.file === null && t.remote === null),
  'shipped library: exactly 5 pending-download slots, all fileless');
ok(tracks.length === 52, 'shipped library: 52 tracks after cape 8');

// ---- 3. Announcer events ----
console.log('== announcer events ==');
ok(announcerEventNames(ann).join(',') ===
  'round-start,fight,ko,double-ko,perfect,time-up,draw,win,character-select',
  '9 announcer events: 8 fight events + character-select');
ok(resolveAnnouncerClip(ann, 'round-start', { round: 1 }).clipId === 'round-1', 'round-start round 1');
ok(resolveAnnouncerClip(ann, 'round-start', { round: 2 }).clipId === 'round-2', 'round-start round 2');
ok(resolveAnnouncerClip(ann, 'round-start', { round: 3 }).clipId === 'round-3', 'round-start round 3');
ok(resolveAnnouncerClip(ann, 'round-start', { finalRound: true }).clipId === 'final-round', 'round-start final round');
ok(resolveAnnouncerClip(ann, 'fight').clipId === 'fight-01', 'fight resolves');
ok(resolveAnnouncerClip(ann, 'ko').clipId === 'ko-01', 'KO resolves');
ok(resolveAnnouncerClip(ann, 'win').clipId === 'you-win-01', 'win resolves');
const sel = resolveAnnouncerClip(ann, 'character-select');
ok(sel && sel.clipId === null && sel.status === 'needs-recording',
  'character-select is needs-recording: no clip invented, no fake line');
ok(resolveAnnouncerClip(ann, 'no-such-event') === null, 'unknown announcer event resolves to null');
ok(!JSON.stringify(ann).includes('.opus') && !JSON.stringify(ann).includes('stage_'),
  'announcer table presents no stage sounds/music/SFX as dialogue');

// ---- 4. Pools consistency guard ----
console.log('== pools consistency guard ==');
const mismatch = checkPoolsConsistency({
  libraryTracks: tracks,
  pools: { pools: [{ id: 'cape-jones', mainTrack: { id: 'ghost-surf-rock', file: 'assets/music/ghost-surf-rock.mp3' } }] },
});
ok(mismatch.length === 2, 'guard catches the PR #1046 cape mismatch (bad id + unmatched file): ' + mismatch.join(' | '));
const clean = checkPoolsConsistency({
  libraryTracks: tracks,
  pools: { pools: [{ id: 'cape-jones', mainTrack: { id: 'cape-jones-ghost-surf-rock', file: 'assets/music/cape-jones-ghost-surf-rock.mp3' } }] },
});
ok(clean.length === 0, 'guard passes on the canonical cape mainTrack id + file');

// ---- 5. RTPC / jitter / no-repeat ----
console.log('== rtpc helpers ==');
ok(Math.abs(computeIntensity({ comboHeat: 1, healthDeficit: 1, roundTimerPressure: 1 }) - 1) < 1e-9,
  'intensity all-ones = 1');
ok(Math.abs(computeIntensity({ comboHeat: 1, healthDeficit: 0, roundTimerPressure: 0 }) - 0.35) < 1e-9,
  'intensity weights: comboHeat alone = 0.35');
ok(Math.abs(computeIntensity({ comboHeat: 0, healthDeficit: 1, roundTimerPressure: 0 }) - 0.35) < 1e-9,
  'intensity weights: healthDeficit alone = 0.35');
ok(Math.abs(computeIntensity({ comboHeat: 0, healthDeficit: 0, roundTimerPressure: 1 }) - 0.30) < 1e-9,
  'intensity weights: roundTimerPressure alone = 0.30');
ok(computeIntensity({ comboHeat: 2, healthDeficit: -1, roundTimerPressure: 0.5 }) <= 1 &&
  computeIntensity({ comboHeat: 2, healthDeficit: -1, roundTimerPressure: 0.5 }) >= 0,
  'intensity clamps inputs and output to [0,1]');
ok(jitterRate(() => 0) === 0.94 && jitterRate(() => 1) === 1.06 && jitterRate(() => 0.5) === 1.0,
  'playbackRate jitter spans exactly 0.94–1.06');
ok(pickNoRepeat(1, 0) === 0, 'no-repeat with one variation returns 0');
let noRepeatOk = true;
for (let i = 0; i < 50; i++) { if (pickNoRepeat(4, 2, () => 0.5) === 2) noRepeatOk = false; }
ok(noRepeatOk, 'no-repeat never returns the previous index');
const comp = masterCompressorSettings();
ok(comp.threshold === -12 && comp.ratio === 8, 'master compressor: threshold -12, ratio 8');
ok(ENGINE_STATES.join(',') === 'Menu,Fight,KO,Pause' && BUSES.join(',') === 'music,sfx,voice,ui,ambience',
  'engine states and buses match the research sketch');

// ---- 6. Download manifest integrity ----
console.log('== download manifest ==');
ok(manifest.groups['nosferatu-25'].tracks.length === 25, 'manifest: 25 nosferatu cuts');
ok(manifest.groups['cape-jones-8'].tracks.length === 8, 'manifest: 8 cape downloads');
ok(manifest.groups['cape-jones-8'].tracks.map((t) => t.file).join(',') ===
  'cape-jones-ghost-surf-rock.mp3,cape-jones-ghost-waltz.mp3,cape-jones-hello-regan.mp3,cape-jones-dark-alley.mp3,cape-jones-graveyard.mp3,cape-jones-old-witch-place.mp3,cape-jones-witch-magical.mp3,cape-jones-sweat-time.mp3',
  'manifest cape filenames match the task exactly');
ok(manifest.groups['cape-jones-8'].tracks.every((t) => t.license === 'CC0-1.0' && t.fmaPage),
  'manifest cape tracks: CC0 1.0 + FMA page each');
ok(manifest.groups['tekken-data-only-5'].tracks.length === 5 &&
  manifest.groups['tekken-data-only-5'].tracks.every((t) => t.file === null),
  'manifest tekken group: 5 data-only slots, no file, no invented URL');
ok(manifest.signInRule.includes('mhvnsnt') && manifest.signInRule.includes('fmmg.mars@gmail.com'),
  'manifest carries the standing GitHub/Google sign-in rule');

// ---- 7. Jukebox UI choices (PR #1056 contract, engine side) ----
console.log('== jukebox ui choices ==');
const playedJuke = [];
music._playTrack = async (t) => { playedJuke.push(t.id); };
music._rotation = {};
music._rotationLoaded = true;
music.library = {
  rotation: { mode: 'sequential' },
  tracks: [
    { id: 'menu-song', title: 'Menu Song', file: 'menu.mp3', remote: null, modes: ['title', 'select'], stages: [] },
    { id: 'battle-song', title: 'Battle Song', file: 'battle.mp3', remote: null, modes: ['battle'], stages: ['shrine'] },
    { id: 'versus-song', title: 'Versus Song', file: 'versus.mp3', remote: null, modes: ['battle'], stages: [] },
    { id: 't7-select', title: 'Blood, Sweat, and Fists', file: null, remote: null, modes: ['select'], stages: [], status: 'pending-download' },
    { id: 'ending-song', title: 'Ending Song', file: 'end.mp3', remote: null, modes: ['results'], stages: [] },
  ],
};
const setJukeboxStore = (obj) => { globalThis.localStorage.setItem('wh_jukebox_v1', JSON.stringify(obj)); };
const clearJukeboxStore = () => { globalThis.localStorage.setItem('wh_jukebox_v1', JSON.stringify({})); };
clearJukeboxStore();
playedJuke.length = 0;
await music.playMenu('title');
ok(playedJuke[0] === 'menu-song', 'no stored choice: menu plays rotation (no behavior change)');
setJukeboxStore({ menu: 'Menu Song' });
playedJuke.length = 0;
await music.playMenu('title');
ok(playedJuke[0] === 'menu-song', 'menu choice resolves by TITLE (UI stores title-or-id)');
setJukeboxStore({ menu: 'menu-song' });
playedJuke.length = 0;
await music.playMenu('select');
ok(playedJuke[0] === 'menu-song', 'menu choice resolves by ID on select screen too');
setJukeboxStore({ menu: 'Blood, Sweat, and Fists' });
playedJuke.length = 0;
await music.playMenu('select');
ok(playedJuke[0] === 'menu-song', 'pending-download choice NEVER plays: falls back to rotation, not silence');
setJukeboxStore({ menu: 'No Such Track' });
playedJuke.length = 0;
await music.playMenu('title');
ok(playedJuke[0] === 'menu-song', 'unknown choice degrades to rotation, not silence');
setJukeboxStore({ menu: 'Menu Song' });
playedJuke.length = 0;
await music.playMenu('results');
ok(playedJuke[0] === 'ending-song', 'results has no owning UI mode: stays on rotation, menu choice does not hijack it');
setJukeboxStore({ arcade: 'Battle Song' });
playedJuke.length = 0;
await music.playBattle('shrine', { uiMode: 'arcade' });
ok(playedJuke[0] === 'battle-song', 'battle with explicit arcade uiMode plays the arcade choice');
setJukeboxStore({ versus: 'Versus Song' });
playedJuke.length = 0;
await music.playBattle('shrine', { uiMode: 'versus' });
ok(playedJuke[0] === 'versus-song', 'battle with explicit versus uiMode plays the versus choice');
setJukeboxStore({ arcade: 'Battle Song', versus: 'Versus Song' });
playedJuke.length = 0;
await music.playBattle('shrine');
ok(playedJuke[0] === 'battle-song', 'battle with no uiMode prefers arcade choice (documented default)');
setJukeboxStore({ versus: 'Versus Song' });
playedJuke.length = 0;
await music.playBattle('shrine');
ok(playedJuke[0] === 'versus-song', 'battle with no uiMode falls back to versus choice when no arcade choice exists');
setJukeboxStore({ versus: 'Versus Song' });
playedJuke.length = 0;
await music.playMenu('versus');
ok(playedJuke[0] === 'versus-song', 'versus SCREEN menu uses the versus choice');
clearJukeboxStore();
playedJuke.length = 0;
await music.playBattle('shrine', { uiMode: 'treasure' });
ok(playedJuke[0] === 'battle-song', 'treasure uiMode with no stored treasure choice falls back to rotation (not faked)');

if (failures.length) {
  console.error(`\nFAILURES (${failures.length}):`);
  for (const f of failures) console.error('  - ' + f);
  process.exit(1);
}
console.log('\nAll jukebox era + announcer + RTPC checks passed.');

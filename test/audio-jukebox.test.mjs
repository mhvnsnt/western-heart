// Audio split + jukebox + streaming + tap-for-audio removal (2026-10-24).
// Verifies, from files only (no invented offsets, labels or lines):
//  1. Pantera Set B sampler cue table: 26 cues, manifest order/durations,
//     exactly 0.6 s of silence between clips, total matching the ffprobe
//     sampler duration (64.210045 s) within MP3 padding (0.001 s).
//     Cue entries carry position/bankSlot/start/duration ONLY — no content
//     label is assigned to any clip (the bank carries slot IDs, not names).
//  2. WHAudio postEvent slices cue ranges and no-ops on missing banks.
//  3. Jukebox pools: Cape Jones cycle [main, ...battle pool], Nosferatu
//     id order, default delegates (null), pending flags present.
//  4. Announcer manifest covers all 11 round/fight calls, all
//     subtitle-only placeholders (NEEDS RECORDING — no audio invented).
//  5. Text checks on the surgical edits: SOUND toggle + JUKEBOX row +
//     announcer wrap in menus.js, tap banner gone from main.js/index.html,
//     voiceBus in audio.js, cue slicing in voice.js, preload note in
//     load-progress.js.
//  6. lazy.preloadNextFight maps roster objects to MODEL_URLS ids only
//     (unknown ids are skipped, never fetched) and preloadLowFirst
//     without a low-LOD URL is just a prefetch.
// Run: node test/audio-jukebox.test.mjs (from repo root; CI runs the loop).
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { resolveJukeboxTrack, getJukeboxPoolId, setJukeboxPoolId } from '../game/js/jukebox.js';
import { WHAudio } from '../game/js/wh-audio.js';
import { preloadNextFight, preloadLowFirst } from '../game/js/lazy.js';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const failures = [];
const ok = (cond, msg) => { if (!cond) failures.push(msg); else console.log('  ok: ' + msg); };
const read = (p) => readFileSync(join(root, p), 'utf8');
const json = (p) => JSON.parse(read(p));

globalThis.localStorage = {
  _s: {},
  getItem(k) { return Object.prototype.hasOwnProperty.call(this._s, k) ? this._s[k] : null; },
  setItem(k, v) { this._s[k] = String(v); },
};

// ---- 1. Pantera cue table ----
console.log('== pantera sampler cues ==');
const events = json('game/data/audio-events.json');
const cues = events.panteraSamplerCues.cues;
const setB = [
  ['1003837159', 0.801088], ['1036113453', 6.266667], ['1038614577', 1.123265], ['1041454593', 0.526000],
  ['235945735', 0.640000], ['279611602', 2.189932], ['328585857', 1.338000], ['366622006', 1.509297],
  ['37512952', 5.162000], ['378194677', 2.470023], ['402346307', 3.741333], ['427436342', 0.744490],
  ['453627518', 2.136000], ['460445785', 3.166667], ['463573614', 1.782132], ['46466028', 3.874667],
  ['479375596', 0.218000], ['496614466', 3.568000], ['68450745', 2.950667], ['703890652', 0.439728],
  ['718397289', 0.635646], ['741838950', 0.216000], ['786104316', 0.683537], ['812504634', 0.439728],
  ['853156273', 0.863492], ['926471152', 1.123265],
];
ok(cues.length === 26, '26 Set B cues');
ok(cues.every((c, i) => c.position === i + 1), 'positions 1..26 in order');
ok(cues.every((c, i) => c.bankSlot === setB[i][0] && Math.abs(c.duration - setB[i][1]) < 1e-9),
  'bank slots + durations match pantera-sounds-manifest.md Set B');
ok(cues.every((c) => Object.keys(c).sort().join(',') === 'bankSlot,duration,position,start'),
  'cue entries carry position/bankSlot/start/duration only — no content label');
ok(Math.abs(cues[0].start) < 1e-9, 'first cue starts at 0');
ok(cues.slice(1).every((c, i) => Math.abs(c.start - (cues[i].start + cues[i].duration) - 0.6) < 1e-6),
  'exactly 0.6 s silence between consecutive clips');
const lastEnd = cues[25].start + cues[25].duration;
ok(Math.abs((lastEnd + 0.6) - 64.210045) < 0.001,
  `computed sampler total ${lastEnd + 0.6} vs ffprobe 64.210045 (MP3 padding)`);
const cued = events.events.pantera_grunt_cued.variations;
ok(cued.length === 26 && cued.every((v, i) => v.cue[0] === cues[i].start && v.cue[1] === cues[i].duration),
  'pantera_grunt_cued variations match the cue table exactly');
ok(events.panteraSplitFiles.primary.length === 26 && events.panteraSplitFiles.alternate.length === 26,
  'split-file lists reference the PR #1028 OGG sets (26 + 26), no second copy shipped here');

// ---- 2. WHAudio cue slicing ----
console.log('== wh-audio engine ==');
const fakeGain = () => ({ gain: { value: 0, setValueAtTime() {}, setTargetAtTime() {}, linearRampToValueAtTime() {}, cancelScheduledValues() {} }, connect() {} });
const fakeCtx = {
  currentTime: 0,
  createBufferSource() {
    const s = { buffer: null, playbackRate: { value: 1 }, connect() {}, start(t, off, dur) { s.startArgs = [t, off, dur]; } };
    return s;
  },
  createGain: fakeGain,
  createBiquadFilter() { return { type: '', frequency: { value: 20000, setTargetAtTime() {} }, connect() {} }; },
  createDynamicsCompressor() { return { threshold: { value: 0 }, ratio: { value: 0 }, connect() {} }; },
  destination: {},
};
const wh = new WHAudio();
ok(wh.manifestUrl === 'data/audio-events.json', 'wh-audio manifest path is game-relative (data/...)');
wh.ctx = fakeCtx;
wh.manifest = events;
wh.buffers.set('pantera-sounds-from-king-t2-grunts-sampler.mp3', { duration: 64.21 });
wh.buses = { music: fakeGain(), sfx: fakeGain(), voice: fakeGain(), ui: fakeGain(), ambience: fakeGain() };
wh.musicFilter = fakeCtx.createBiquadFilter();
const src = wh.postEvent('pantera_grunt_cued');
ok(src && Array.isArray(src.startArgs) && cues.some((c) => src.startArgs[1] === c.start && src.startArgs[2] === c.duration),
  'postEvent(pantera_grunt_cued) starts at a real cue [start, dur]');
ok(wh.postEvent('ko') === null, 'postEvent with an unloaded bank is a silent no-op, never a throw');
ok(wh.postEvent('no-such-event') === null, 'postEvent with an unknown event is a silent no-op');
const seq = [wh._pick(events.events.throw_chain, 'throw_chain'), wh._pick(events.events.throw_chain, 'throw_chain')];
ok(seq[0] !== seq[1] || events.events.throw_chain.variations.length === 1, 'sequence container advances per call');
try { wh.setState(Object.keys(events.states)[0]); ok(true, 'setState runs on a manifest state'); } catch (e) { ok(false, 'setState threw: ' + e.message); }
wh.music = { layers: [{ name: 'drums', gain: fakeGain() }] };
try { wh.setRTPC('intensity', 0.8); ok(true, 'setRTPC(intensity) runs'); } catch (e) { ok(false, 'setRTPC threw: ' + e.message); }

// ---- 3. Jukebox pools ----
console.log('== jukebox pools ==');
const pools = json('game/data/jukebox-pools.json');
const cape = pools.pools.find((p) => p.id === 'cape-jones');
const nos = pools.pools.find((p) => p.id === 'nosferatu');
ok(cape && cape.mainTrack.id === 'ghost-surf-rock', 'cape-jones main track is Ghost Surf Rock');
ok(cape.mainTrack.license === 'CC0-1.0' && cape.mainTrack.durationSeconds === 247, 'ghost track: CC0, 247 s (04:07, Free Music Archive)');
ok(cape.stage === 'cape-jones-arena' && /pending-stage/.test(cape.stageStatus), 'cape arena stage flagged pending-stage (no such stage on main)');
ok(/pending-file/.test(cape.mainTrack.status), 'ghost track file flagged pending-file (bytes not in repo)');
ok(nos && nos.trackIds.length === 25 && nos.trackIds[0] === 'nos-t01' && nos.trackIds[24] === 'nos-t25',
  'nosferatu pool references nos-t01..nos-t25 (PR #1030), nothing duplicated');
const lib = [
  { id: 'battle-volatile', file: 'v.mp3', modes: ['battle'], stages: [] },
  { id: 'global-1', file: 'g.mp3', modes: ['battle'], stages: [] },
  { id: 'nos-t01', file: 'n1.mp3', modes: ['battle'], stages: [] },
  { id: 'nos-t02', file: 'n2.mp3', modes: ['battle'], stages: [] },
];
let st = {};
const cycle = [];
for (let i = 0; i < 6; i++) cycle.push(resolveJukeboxTrack({ poolId: 'cape-jones', stage: 'cape-jones-arena', libraryTracks: lib, pools, state: st }).id);
ok(cycle.join(',') === 'ghost-surf-rock,battle-volatile,global-1,nos-t01,nos-t02,ghost-surf-rock',
  'cape cycle = [main, ...battle pool] repeating: ' + cycle.join(','));
st = {};
const nosSeq = [];
for (let i = 0; i < 3; i++) nosSeq.push(resolveJukeboxTrack({ poolId: 'nosferatu', libraryTracks: lib, pools, state: st }).id);
ok(nosSeq.join(',') === 'nos-t01,nos-t02,nos-t01', 'nosferatu pool rotates its own ids in order');
ok(resolveJukeboxTrack({ poolId: 'default', libraryTracks: lib, pools, state: {} }) === null, 'default pool delegates to music.js');
ok(resolveJukeboxTrack({ poolId: 'nosferatu', libraryTracks: [], pools, state: {} }) === null,
  'nosferatu pool with no library tracks delegates (pre-#1030 safe)');
ok(getJukeboxPoolId() === 'default', 'jukebox pool defaults to stage rotation');
setJukeboxPoolId('cape-jones');
ok(getJukeboxPoolId() === 'cape-jones', 'jukebox pool persists in wh_settings_v1');
setJukeboxPoolId('default');

// ---- 4. Announcer coverage ----
console.log('== announcer ==');
const ann = json('game/data/voices/announcer.json');
const want = ['round-1', 'round-2', 'round-3', 'final-round', 'fight', 'ko', 'double-ko', 'perfect', 'time-up', 'draw', 'you-win'];
const have = new Set(ann.clips.map((c) => c.trigger));
ok(want.every((t) => have.has(t)), 'announcer manifest covers all 11 calls: ' + want.join(', '));
ok(ann.clips.every((c) => c.status === 'placeholder' && !c.file),
  'all announcer clips are subtitle-only placeholders — NEEDS RECORDING, no audio invented');

// ---- 5. Surgical-edit text checks ----
console.log('== surgical edits ==');
const menus = read('game/js/menus.js');
ok(menus.includes("toggleRow('SOUND', 'soundOn')"), 'menus: SOUND toggle in Settings');
ok(menus.includes("segRow('JUKEBOX', 'jukebox'"), 'menus: JUKEBOX row in Settings');
ok(menus.includes('function hookAnnouncer(g)'), 'menus: announcer round-flow wrap');
ok(menus.includes('preloadNextFight([pChar, eChar])'), 'menus: VS-screen rematch preload');
ok(menus.includes("import('./jukebox.js')"), 'menus: jukebox install at boot');
ok(!read('game/js/main.js').includes('tap-to-start'), 'main.js: tap-to-start references gone');
// NOTE: game-unit-tests runs on a sparse checkout (see
// .github/workflows/game-checks.yml) that includes test/, game/js and
// game/data but NOT game/index.html or game/_redirects. Those two checks
// therefore assert when the files are present (full checkout) and log a
// skip when they are absent (sparse checkout) — they must never throw.
// The banner removal is additionally proven by the main.js check above,
// which IS in the sparse scope.
const indexHtml = (() => { try { return read('game/index.html'); } catch (e) { return null; } })();
if (indexHtml === null) console.log('  skip: game/index.html absent (sparse checkout); banner check runs in full checkouts');
else ok(!indexHtml.includes('TAP TO ENABLE SOUND'), 'index.html: TAP TO ENABLE SOUND banner gone');
ok(read('game/js/audio.js').includes('voiceBus()'), 'audio.js: voiceBus() for announcer/voice');
ok(read('game/js/voice.js').includes('clip.cue'), 'voice.js: cue slicing for sampler clips');
ok(read('game/js/load-progress.js').includes('__whPreloadNote'), 'load-progress.js: preload status note');
const redirects = (() => { try { return read('game/_redirects'); } catch (e) { return null; } })();
if (redirects === null) console.log('  skip: game/_redirects absent (sparse checkout); proxy check runs in full checkouts');
else ok(['/roster/*', '/customization/*', '/packages/*', '/game/*'].every((r) => redirects.includes(r)),
  'netlify proxy rules intact (all four 200 rewrites present)');
ok(read('game/js/lazy.js').includes('preloadLowFirst'), 'lazy.js: progressive-LOD preload pattern');

// ---- 6. lazy preload mapping ----
console.log('== lazy preload ==');
const called = [];
const fakeAssets = {
  MODEL_URLS: { pantera: 'assets/models/pantera.glb', demonio: 'x.glb' },
  assets: { prefetch(id) { called.push(id); } },
};
const ids = await preloadNextFight([{ id: 'pantera' }, { id: 'no-such-fighter' }, 'demonio'], { assetsModule: fakeAssets });
ok(JSON.stringify(ids) === JSON.stringify(['pantera', 'demonio']), 'preload maps only MODEL_URLS ids, skips unknown: ' + ids.join(','));
ok(JSON.stringify(called) === JSON.stringify(['pantera', 'demonio']), 'prefetch called once per mapped id');
const lowIds = await preloadLowFirst('pantera', null, { assetsModule: fakeAssets });
ok(lowIds.join(',') === 'pantera', 'preloadLowFirst without a low-LOD URL is just a prefetch');

console.log(failures.length ? `\nFAILED (${failures.length}):\n- ${failures.join('\n- ')}` : '\nALL AUDIO/JUKEBOX CHECKS PASSED');
process.exitCode = failures.length ? 1 : 0;

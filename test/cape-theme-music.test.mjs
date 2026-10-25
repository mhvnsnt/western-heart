// Cape Jones theme + tap-for-audio removal — verification test.
// Run from repo root: node test/cape-theme-music.test.mjs
// CI sparse-checkout includes /test + /game (music mp3s excluded — this
// test checks JSON structure + code text only, never file existence).
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import assert from 'node:assert/strict';

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const read = (p) => readFileSync(path.join(root, p), 'utf8');

let n = 0;
const ok = (cond, msg) => { n++; assert.ok(cond, msg); console.log(`ok ${n} - ${msg}`); };

// ---- Music library: Cape Jones theme + interchanging tracks ----
const lib = JSON.parse(read('game/data/music-library.json'));
const T = lib.tracks;
const cape = T.filter((t) => (t.stages || []).includes('cape-jones-arena'));
ok(cape.length === 8, `cape-jones-arena pool has 8 tracks (got ${cape.length})`);
ok(cape[0].id === 'cape-jones-ghost-surf-rock', 'first cape-jones-arena track is Ghost Surf Rock (main theme)');
const gsr = T.find((t) => t.id === 'cape-jones-ghost-surf-rock');
ok(!!gsr, 'Ghost Surf Rock entry exists');
ok(gsr.artist === 'Loyalty Freak Music', 'Ghost Surf Rock artist is Loyalty Freak Music');
ok(gsr.license === 'CC0-1.0', 'Ghost Surf Rock license is CC0-1.0');
ok(gsr.title === 'Ghost Surf Rock', 'Ghost Surf Rock title exact');
ok((gsr.moods || []).includes('surf') && (gsr.moods || []).includes('spooky'), 'Ghost Surf Rock moods include surf + spooky');
ok((gsr.moods || []).includes('halloween') && (gsr.moods || []).includes('ghost'), 'Ghost Surf Rock moods include halloween + ghost');
for (const t of cape) {
  ok(t.license === 'CC0-1.0', `${t.id} is CC0-1.0`);
  ok((t.file || '').startsWith('assets/music/'), `${t.id} file under assets/music/`);
  ok(Array.isArray(t.modes) && t.modes.length === 0, `${t.id} has no modes (cannot hijack menu/mode picks)`);
  ok(t.loop === true, `${t.id} loops`);
}
// pickTrack simulation (stage > mode > mood, first match — game/js/music.js)
const pick = ({ stage, mode, mood } = {}) => {
  if (stage) { const h = T.find((t) => (t.stages || []).includes(stage)); if (h) return h.id; }
  if (mode) { const h = T.find((t) => (t.modes || []).includes(mode)); if (h) return h.id; }
  if (mood) { const h = T.find((t) => (t.moods || []).includes(mood)); if (h) return h.id; }
  return null;
};
ok(pick({ stage: 'cape-jones-arena' }) === 'cape-jones-ghost-surf-rock', 'arena pick is Ghost Surf Rock');
ok(pick({ stage: 'shrine', mode: 'battle' }) === 'battle-volatile', 'existing shrine pick unchanged');
ok(pick({ stage: 'palace-of-dreaming', mode: 'battle' }) === 'battle-cannery', 'existing palace pick unchanged');
ok(pick({ stage: 'helix-palace', mode: 'battle' }) === 'battle-implosion', 'existing helix pick unchanged');
ok(pick({ stage: 'tong-nou', mode: 'battle' }) === 'tong-nou-theme', 'existing tong-nou pick unchanged');
ok(pick({ mood: 'spooky' }) === 'cape-jones-ghost-surf-rock', 'spooky mood pick is Ghost Surf Rock');

// ---- Tap-for-audio removal ----
const html = read('game/index.html');
ok(!html.includes('tap-to-start'), 'index.html has no tap-to-start element');
ok(!html.includes('tap-hint'), 'index.html has no tap-hint class');
const mainJs = read('game/js/main.js');
ok(!mainJs.includes('tap-to-start'), 'main.js has no tap-to-start reference');
ok(mainJs.includes('function unlockAudio()'), 'main.js still defines unlockAudio()');
ok(mainJs.includes("document.body.addEventListener('pointerdown', unlockAudio"), 'main.js keeps silent first-interaction unlock listener');
const css = read('game/styles.css');
ok(!css.includes('tap-hint'), 'styles.css has no tap-hint rules');
const menusJs = read('game/js/menus.js');
ok(menusJs.includes("toggleRow('SOUND', 'soundOn')"), 'OPTIONS builds a SOUND row on the soundOn key (shipped settings design)');
ok(menusJs.includes('soundOn: true'), 'default settings keep audio ON (soundOn: true)');
ok(menusJs.includes("segRow('JUKEBOX'"), 'OPTIONS builds a JUKEBOX row alongside SOUND');
ok(menusJs.includes('muted: false'), 'default settings keep audio ON (muted: false)');

console.log(`\nPASS: ${n} checks, cape-theme-music`);

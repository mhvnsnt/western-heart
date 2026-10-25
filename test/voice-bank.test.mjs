// Pantera voice-bank wiring verification (2026-10-24, integration one-pass).
// Pantera's voice (King bank clips, owner ear-checked 2026-10-24, T2 set
// preferred) was pulled to ~/workspace/king-mods/ but NOT wired into the
// game: no game/assets/audio dir existed, audio.js was fully procedural,
// and fighter grunts played the same synth grunt for everyone.
// This test verifies the wiring, in the batch-strings test style:
//   1. audio.js gains voice-bank loading + voice grunt with procedural
//      fallback (never silence, never a wrong fighter).
//   2. game.js passes the victim fighter id at all 4 grunt call sites.
//   3. The voice manifest (when present in the checkout) is well-formed:
//      format, preferred set, 26+26+1 clips, grunt-sized preferred clips.
// NOTE on CI sparse checkout: game-unit-tests checks out test + game/js
// but NOT game/assets/audio, so the manifest file is absent there. The
// manifest checks below SKIP (not fail) when the file is absent; they run
// fully on a full checkout. The code-wiring checks always run.
// Run: node test/voice-bank.test.mjs (from repo root).

import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const failures = [];
const ok = (cond, msg) => { if (!cond) failures.push(msg); else console.log('  ok: ' + msg); };

// ---- 1. audio.js voice wiring ----
console.log('== audio.js voice wiring ==');
const audioJs = readFileSync(join(root, 'game', 'js', 'audio.js'), 'utf8');
ok(audioJs.includes('loadVoiceBank(fighterId)'), 'audio.js has loadVoiceBank(fighterId)');
ok(audioJs.includes('voiceGrunt(fighterId)'), 'audio.js has voiceGrunt(fighterId)');
ok(audioJs.includes('grunt(pitch = 1, fighterId = null)'), 'audio.js grunt takes fighterId');
ok(audioJs.includes('this._osc(\'triangle\', 150 * pitch'), 'audio.js keeps procedural grunt fallback');
ok(audioJs.includes('assets/audio/voice/'), 'audio.js loads banks from assets/audio/voice/');
ok(audioJs.includes('duration_s > 2.0'), 'audio.js restricts grunts to grunt-sized clips');

// ---- 2. game.js passes fighter id at grunt sites ----
console.log('== game.js grunt call sites ==');
const gameJs = readFileSync(join(root, 'game', 'js', 'game.js'), 'utf8');
const defSites = (gameJs.match(/audio\.grunt\([^;]*def\.char && def\.char\.id\)/g) || []).length;
const defenderSites = (gameJs.match(/audio\.grunt\([^;]*defender\.char && defender\.char\.id\)/g) || []).length;
ok(defSites === 2, `game.js passes def fighter id at 2 throw sites (found ${defSites})`);
ok(defenderSites === 2, `game.js passes defender fighter id at 2 hit/KO sites (found ${defenderSites})`);

// ---- 3. Manifest integrity (skipped on sparse CI checkout) ----
console.log('== voice manifest ==');
const manifestPath = join(root, 'game', 'assets', 'audio', 'voice', 'pantera', 'manifest.json');
if (!existsSync(manifestPath)) {
  console.log('  skip: manifest not in this checkout (sparse CI checkout excludes game/assets/audio); code checks above still ran');
} else {
  const man = JSON.parse(readFileSync(manifestPath, 'utf8'));
  ok(man.format === 'wh-voice-bank/1', 'manifest format is wh-voice-bank/1');
  ok(man.fighter === 'pantera', 'manifest fighter is pantera');
  ok(man.preferred_set === 't2grunts', 'manifest preferred set is t2grunts (owner ear-check: better quality)');
  ok(man.sets.classic.clips.length === 26, 'manifest classic set has 26 clips');
  ok(man.sets.t2grunts.clips.length === 26, 'manifest t2grunts set has 26 clips');
  ok(man.sets.t8death.clips.length === 1, 'manifest t8death set has 1 clip');
  const all = [...man.sets.classic.clips, ...man.sets.t2grunts.clips, ...man.sets.t8death.clips];
  ok(all.every((c) => c.position && c.wem_id && c.duration_s && c.file), 'every clip has position, wem_id, duration_s, file');
  ok(all.every((c) => c.file.startsWith('assets/audio/voice/pantera/') && c.file.endsWith('.wav')), 'every clip file is under assets/audio/voice/pantera/ and is a .wav');
  const gruntSized = man.sets.t2grunts.clips.filter((c) => c.duration_s <= 2.0);
  ok(gruntSized.length === 16, `preferred set has 16 grunt-sized clips <=2s (found ${gruntSized.length})`);
}

if (failures.length) {
  console.error('FAILURES:');
  for (const f of failures) console.error('  - ' + f);
  process.exit(1);
}
console.log('voice-bank test: ALL PASS');

// Pantera voice trigger wiring verification (2026-10-24, integration one-pass).
// The voice bank (PR #1028: 52 OGG clips + game/data/voices/pantera.json)
// and the voice engine (game/js/voice.js) were wired, but NOTHING in the
// game called voice.play() during fights — the engine was loaded data with
// no trigger. This test verifies the trigger hookup:
//   1. game.js imports the voice engine.
//   2. game.js fires voice.play() with the victim fighter id at all 4
//      grunt sites: KO sites use trigger 'ko', hit/throw sites use 'hit'.
//   3. Every trigger game.js fires exists in the Pantera manifest's clip
//      pool (game/data/voices/pantera.json is in the CI sparse checkout,
//      so this check runs in CI too).
//   4. The existing procedural grunt calls are preserved (fighters without
//      a voice bank must not go silent).
// Run: node test/voice-triggers.test.mjs (from repo root).

import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const failures = [];
const ok = (cond, msg) => { if (!cond) failures.push(msg); else console.log('  ok: ' + msg); };

console.log('== game.js voice trigger hookup ==');
const gameJs = readFileSync(join(root, 'game', 'js', 'game.js'), 'utf8');
ok(gameJs.includes("import { voice } from './voice.js';"), 'game.js imports the voice engine');
const koSites = (gameJs.match(/voice\.play\([^;]*, 'ko'\)/g) || []).length;
const hitSites = (gameJs.match(/voice\.play\([^;]*, 'hit'\)/g) || []).length;
ok(koSites === 2, `game.js fires voice.play with 'ko' at 2 KO sites (found ${koSites})`);
ok(hitSites === 2, `game.js fires voice.play with 'hit' at 2 hit/throw sites (found ${hitSites})`);
ok(gameJs.includes('def.char && def.char.id'), 'game.js passes the throw-victim fighter id');
ok(gameJs.includes('defender.char && defender.char.id'), 'game.js passes the hit-victim fighter id');
ok((gameJs.match(/audio\.grunt\(/g) || []).length >= 4, 'procedural grunt calls preserved (no silence for fighters without banks)');

console.log('== voice engine ==');
const voiceJs = readFileSync(join(root, 'game', 'js', 'voice.js'), 'utf8');
ok(voiceJs.includes('export const voice = new VoiceEngine();'), 'voice.js exports the voice engine');
ok(voiceJs.includes('play(fighterId, trigger'), 'voice engine has play(fighterId, trigger)');

console.log('== Pantera manifest triggers ==');
const man = JSON.parse(readFileSync(join(root, 'game', 'data', 'voices', 'pantera.json'), 'utf8'));
const triggers = new Set(man.clips.map((c) => c.trigger));
ok(triggers.has('hit'), 'Pantera manifest has hit clips');
ok(triggers.has('ko'), 'Pantera manifest has ko clips');
ok(man.clips.filter((c) => c.trigger === 'hit').length >= 1, 'Pantera hit pool is non-empty');
ok(man.clips.filter((c) => c.trigger === 'ko').length >= 1, 'Pantera ko pool is non-empty');

if (failures.length) {
  console.error('FAILURES:');
  for (const f of failures) console.error('  - ' + f);
  process.exit(1);
}
console.log('voice-triggers test: ALL PASS');

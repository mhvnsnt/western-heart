// Shrine体系 — shrine terminal wiring test (2026-10-24).
// Owner directive: TempleOS-inspired mode renamed Shrine + the
// kanji for system (体系, owner-locked 2026-10-24), wired three
// ways: Heart and Mind Within story segment, Eastern Mind
// canon, and a playable side-games mode. TempleOS attribution
// lives in technical files only, never in canon writing.
// This test runs under Node (CI game-unit-tests loop). It only
// touches files CI's sparse checkout includes: game/js/*.
// Run: node test/shrine-os.test.mjs (from repo root).

import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  SHRINE_OS, VGA16, ORACLE_WORDS, oracleDraw, parseCommand,
  createSlopeGame, createSpriteGrid, MUSIC_PATTERNS, COMMANDS,
  SHRINE_CREDITS_LINES,
} from '../game/js/shrine-os.js';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const failures = [];
const ok = (cond, msg) => { if (!cond) failures.push(msg); else console.log('  ok: ' + msg); };

// ---- 1. Identity: name locked, kanji locked ----
console.log('== identity ==');
ok(SHRINE_OS.name === 'Shrine体系', 'name is Shrine体系');
ok(SHRINE_OS.kanji === '体系', 'kanji is 体系');
ok(SHRINE_OS.kanjiReading === 'taikei', 'reading is taikei');
ok(SHRINE_OS.kanjiMeaning === 'system', 'meaning is system');
ok(SHRINE_OS.stage === 'octagonal-shrine', 'stage is octagonal-shrine');
ok(!SHRINE_OS.name.includes('Temple'), 'in-game name never uses the source name');

// ---- 2. Sixteen colors ----
console.log('== palette ==');
ok(VGA16.length === 16, 'palette has exactly 16 colors');
ok(VGA16.every((c, k) => c.i === k && /^#[0-9A-F]{6}$/.test(c.hex)),
  'palette indices 0-15, every hex valid');
ok(VGA16[0].hex === '#000000' && VGA16[15].hex === '#FFFFFF',
  'palette runs black to white');

// ---- 3. Oracle draws canon words only ----
console.log('== oracle ==');
ok(ORACLE_WORDS.includes('凛 RIN') && ORACLE_WORDS.includes('闘 TOU') &&
  ORACLE_WORDS.includes('FIGHT') && ORACLE_WORDS.includes('PAR-FANG'),
  'oracle pool holds soul kanji, trial words, lands');
let seq = 0;
const det = () => { const v = [0.0, 0.5, 0.99][seq % 3]; seq += 1; return v; };
const words = oracleDraw(det);
ok(words.length === 3, 'oracle draws exactly three words');
ok(words.every((w) => ORACLE_WORDS.includes(w)), 'every drawn word is a canon word');
ok(new Set(words).size === 3, 'the three words are distinct');

// ---- 4. Command parser ----
console.log('== commands ==');
ok(parseCommand('oracle').command === 'ORACLE' && parseCommand('oracle').known,
  'lowercase input parses to a known command');
ok(parseCommand('  HELP  ').command === 'HELP', 'extra spaces ignored');
ok(!parseCommand('TEMPLE').known, 'unknown command rejected');
ok(parseCommand('').empty, 'empty input flagged empty');
ok(COMMANDS.map((c) => c.cmd).join(',').includes('ORACLE,SPRITE,MUSIC,GAME'),
  'command list covers oracle, sprite, music, game');
ok(parseCommand('credits').known && parseCommand('credits').command === 'CREDITS',
  'CREDITS parses to a known command');
ok(COMMANDS.some((c) => c.cmd === 'CREDITS'),
  'command list includes CREDITS (credits button + typed command)');

// ---- 5. Sprite board ----
console.log('== sprite ==');
const grid = createSpriteGrid(16, 16);
ok(grid.paint(0, 0, 14) && grid.get(0, 0) === 14, 'paint + read a cell');
ok(!grid.paint(16, 0, 14) && !grid.paint(0, 0, 16), 'out-of-bounds paint rejected');
ok(grid.serialize().length === 256, 'serialized board is 256 hex chars');
ok(grid.serialize()[0] === 'E', 'first cell serializes as hex E (14)');
const grid2 = createSpriteGrid(16, 16);
ok(grid2.deserialize(grid.serialize()) && grid2.get(0, 0) === 14,
  'deserialize round-trips the board');
ok(!grid2.deserialize('ZZZ'), 'bad serialization rejected');

// ---- 6. Single-voice hymns ----
console.log('== music ==');
ok(Object.keys(MUSIC_PATTERNS).length >= 3, 'at least three hymn patterns');
ok(Object.values(MUSIC_PATTERNS).every((p) => p.length > 0 &&
  p.every((n) => typeof n.f === 'number' && n.f > 0 && typeof n.b === 'number' && n.b > 0)),
  'every pattern is a flat single-voice note list (no chords)');

// ---- 7. Slope descent ----
console.log('== slope game ==');
const g = createSlopeGame({ rand: () => 0.99 }); // never spawns
let snap = g.step(0);
ok(snap.alive && snap.score > 0, 'game advances and scores with no obstacles');
ok(g.step(-1).playerLane === 3, 'left move shifts one lane');
g.reset();
for (let k = 0; k < 5; k++) g.step(-1);
ok(g.snapshot().playerLane === 0, 'lane clamps at the left edge');
g.reset();
g.state.obstacles.push({ lane: 4, row: g.state.playerRow - 1, width: 1 });
snap = g.step(0);
ok(!snap.alive && snap.crashed, 'obstacle reaching the player row crashes the run');
g.reset();
g.state.obstacles.push({ lane: 0, row: g.state.playerRow - 1, width: 1 });
snap = g.step(0);
ok(snap.alive, 'obstacle in another lane does not crash the run');

// ---- 8. Story wiring: heartmind.js carries the shrine segment ----
console.log('== heartmind wiring ==');
const hm = readFileSync(join(root, 'game/js/heartmind.js'), 'utf8');
ok(hm.includes('SHRINE_OS_SEGMENT'), 'heartmind exports the shrine segment');
ok(hm.includes('Shrine体系'), 'heartmind names the segment Shrine体系');
ok(hm.includes('stillpoint') && hm.includes('shrineOsBeat'),
  'stillpoint stage plays a shrine beat');

// ---- 9. End credits (owner standing requirement 2026-10-24) ----
// Reachable two ways in the terminal: CREDITS command, and the
// EXIT path (which prints the same lines before it sleeps).
// The dedication line is verbatim; no source-name branding in
// any rendered credits line.
console.log('== end credits ==');
ok(Array.isArray(SHRINE_CREDITS_LINES) && SHRINE_CREDITS_LINES.length >= 3,
  'credits lines exported');
ok(SHRINE_CREDITS_LINES.includes('In memory of Terry Davis, RIP'),
  'credits carry the dedication verbatim: In memory of Terry Davis, RIP');
ok(SHRINE_CREDITS_LINES.some((l) => l.includes('Shrine体系')),
  'credits name the mode Shrine体系');
ok(!SHRINE_CREDITS_LINES.some((l) => l.includes('Temple')),
  'no source-name branding in any rendered credits line');

// ---- Verdict ----
if (failures.length > 0) {
  console.error('FAILURES:');
  failures.forEach((f) => console.error('  FAIL: ' + f));
  process.exitCode = 1;
} else {
  console.log('shrine-os: all checks pass');
}

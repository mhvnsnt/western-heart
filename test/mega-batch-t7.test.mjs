// Mega-batch T7 verification (2026-10-24, one pass).
// User directives: T7 work done in one pass, no guesses, T8 never for T7
// Pantera, MOD damage wins, no tap-for-audio friction (sound in SETTINGS).
// This test verifies, from the repo files themselves:
//  1. The 8 MOD fighters' movesets carry ZERO T8 animation refs in playable
//     moves (T8 anims were quarantined, not deleted: t8_quarantine_20261024).
//  2. Body damage equals MOD (TheBigTuna) damage where the t7 block is wired
//     and numeric-single — the game reads body damage, so MOD was not live
//     until this sync.
//  3. No string maps to a chord row (string steps never fire chord clips).
//  4. Pantera LP1 (jab) body damage is 9 (MOD), not the old T3-scaled 11.
//  5. Tap-for-audio is gone: no TAP TO ENABLE SOUND hint, and a SETTINGS
//     audio toggle exists (audio.js setMuted + main.js wiring + howto button).
// Run: node test/mega-batch-t7.test.mjs (from repo root; CI runs the loop).
// NOTE (CI sparse checkout): game/index.html and docs/ are NOT in the
// game-unit-tests sparse checkout, so those two checks SKIP (not fail)
// when the files are absent; they assert fully on a full checkout.

import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const FIGHTERS = ['pantera', 'burger', 'demonio', 'diablo', 'kinpo', 'phantom', 'scimitar', 'skull'];
let failures = 0;
const check = (cond, msg) => { if (!cond) { failures++; console.log('FAIL:', msg); } };

for (const f of FIGHTERS) {
  const p = join(root, 'game', 'assets', 'movesets', `${f}.json`);
  check(existsSync(p), `${f} moveset file exists`);
  const d = JSON.parse(readFileSync(p, 'utf8'));
  const moves = d.moves;
  const t8 = Object.entries(moves).filter(([, v]) => typeof v.anim_ref === 'string' && v.anim_ref.startsWith('t8:'));
  check(t8.length === 0, `${f}: ${t8.length} T8 anim refs remain in playable moves`);
  check(d.t8_quarantine_20261024 && Object.keys(d.t8_quarantine_20261024).length > 0,
    `${f}: quarantine section present with entries`);
  let mism = 0;
  for (const [, v] of Object.entries(moves)) {
    if (v.t7 && v.t7.wired && !v.throw) {
      const td = v.t7.damage;
      const single = (typeof td === 'number' || (typeof td === 'string' && /^-?\d+(\.\d+)?$/.test(td)));
      if (single && Number(td) !== Number(v.damage)) mism++;
    }
  }
  check(mism === 0, `${f}: ${mism} body-vs-MOD damage mismatches remain`);
  const chordRows = new Set();
  for (const [k, v] of Object.entries(moves)) {
    if (/^[1234]\+[1234]$/.test(k) && v.t3_row != null) chordRows.add(v.t3_row);
  }
  let strChord = 0;
  for (const s of (d.strings || [])) {
    if (s && typeof s === 'object' && s.t3_rows && s.t3_rows.some((r) => chordRows.has(r))) strChord++;
  }
  check(strChord === 0, `${f}: ${strChord} strings map to chord rows`);
}
const pantera = JSON.parse(readFileSync(join(root, 'game', 'assets', 'movesets', 'pantera.json'), 'utf8'));
check(pantera.moves['1'].damage === 9, `pantera LP1 body damage is ${pantera.moves['1'].damage}, expected 9 (MOD)`);

const mainJs = readFileSync(join(root, 'game', 'js', 'main.js'), 'utf8');
const audioJs = readFileSync(join(root, 'game', 'js', 'audio.js'), 'utf8');
check(!mainJs.includes('tap-to-start'), 'tap-to-start references removed from main.js');
check(audioJs.includes('setMuted'), 'audio.js has setMuted');
check(mainJs.includes('audio-toggle'), 'main.js wires the audio toggle');

const indexPath = join(root, 'game', 'index.html');
if (existsSync(indexPath)) {
  const indexHtml = readFileSync(indexPath, 'utf8');
  check(!indexHtml.includes('TAP TO ENABLE SOUND'), 'tap-to-enable-sound hint removed from index.html');
  check(indexHtml.includes('id="audio-toggle"'), 'howto screen has the audio toggle button');
} else {
  console.log('SKIP: game/index.html not in this checkout (CI sparse checkout) — index.html checks skipped');
}

const idxPath = join(root, 'docs', 'research', 't7-unified-index-2026-10-24.json');
if (existsSync(idxPath)) {
  const idx = JSON.parse(readFileSync(idxPath, 'utf8'));
  check(Object.keys(idx).length >= 38, `unified index covers ${Object.keys(idx).length} fighters (expected >= 38)`);
} else {
  console.log('SKIP: unified T7 index doc not in this checkout (CI sparse checkout) — index check skipped');
}

console.log(failures === 0 ? 'MEGA-BATCH-T7 PASS' : `MEGA-BATCH-T7 FAIL (${failures})`);
process.exit(failures === 0 ? 0 : 1);

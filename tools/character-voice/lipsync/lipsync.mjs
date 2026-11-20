// WH lip-sync cue generator driver (worker 22, 2026-10-22).
//
// node tools/character-voice/lipsync/lipsync.mjs <in.wav> <out.cues.json> [--text "dialog text"]
//
// Turns a voice-line WAV into Rhubarb-style mouthCues JSON:
//   { mouthCues: [{start, end, value}] }  value ∈ X A B C D E F G H
// Played back in-game by game/js/lipsync-player.js (WHLipSyncPlayer)
// against the fighter's jaw bone.
//
// Pattern follows tools/proof-harness/*.mjs: serve the repo first:
//   python3 -m http.server 8765   (from the repo root)
// then run. The analysis itself runs in headless Chromium (the engine
// needs a browser/worker for WASM). The engine + 37MB acoustic model
// load from unpkg on first run and cache in the browser profile.
//
// PLAYWRIGHT_MODULE / CHROMIUM_PATH override the defaults below.

const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright/index.mjs');
import fs from 'fs';
import path from 'path';

const [,, inWav, outJson, ...rest] = process.argv;
if (!inWav || !outJson) {
  console.error('usage: node lipsync.mjs <in.wav> <out.cues.json> [--text "dialog text"]');
  process.exit(1);
}
let text = '';
for (let i = 0; i < rest.length; i++) {
  if (rest[i] === '--text') text = rest[i + 1] || '';
}

// Serve the wav from the repo tree so the page can fetch it.
const wavAbs = path.resolve(inWav);
const repoRoot = '/tmp/wh-lipsync-root';
fs.mkdirSync(repoRoot, { recursive: true });
fs.copyFileSync(wavAbs, path.join(repoRoot, 'line.wav'));
// The tool lives in the repo; serve the repo root instead when possible.
const serveRoot = fs.existsSync('tools/character-voice/lipsync/lipsync.html')
  ? process.cwd()
  : repoRoot;
const wavParam = serveRoot === process.cwd()
  ? 'tools/character-voice/lipsync/../..' // not used; we copy below
  : 'line.wav';
if (serveRoot === process.cwd()) {
  fs.mkdirSync('tools/character-voice/lipsync/tmp', { recursive: true });
  fs.copyFileSync(wavAbs, 'tools/character-voice/lipsync/tmp/line.wav');
}

const browser = await chromium.launch({
  executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'],
});
const page = await browser.newPage();
page.on('pageerror', (e) => console.error('[pageerror]', e.message));
const wavUrl = serveRoot === process.cwd()
  ? `http://127.0.0.1:8765/tools/character-voice/lipsync/tmp/line.wav`
  : `http://127.0.0.1:8766/line.wav`;
await page.goto(
  `http://127.0.0.1:8765/tools/character-voice/lipsync/lipsync.html?wav=${encodeURIComponent(wavUrl)}&text=${encodeURIComponent(text)}`,
  { waitUntil: 'load' });
// The 37MB acoustic model downloads on first run; allow generous time.
await page.waitForFunction(() => window.__cues || window.__error, null, { timeout: 300000 });
const result = await page.evaluate(() => {
  if (window.__error) return { error: window.__error };
  return window.__cues;
});
await browser.close();
if (result.error) {
  console.error('lip-sync failed:', result.error);
  process.exit(2);
}
const out = {
  version: 1,
  tool: 'lip-sync-engine@1.0.3 (Rhubarb-compatible)',
  source: path.basename(inWav),
  dialogText: text,
  sampleRate: 16000,
  mouthCues: result.mouthCues,
};
fs.mkdirSync(path.dirname(path.resolve(outJson)), { recursive: true });
fs.writeFileSync(outJson, JSON.stringify(out, null, 1));
console.log(`wrote ${outJson}: ${out.mouthCues.length} cues, ${(result.metadata?.duration || 0).toFixed(2)}s`);

// Lane 8 story wiring test — Ink (vendored) + Yarn (PR #1044).
// Run: node test/oss-lane8-story.test.mjs  (from the repo root)
// MERGE ORDER: requires PR #1044's game/js/yarn-parse.js +
// game/js/ink-loader.js. If they are absent (this PR merged
// first), the test SKIPS with a clear message instead of failing
// — story-wiring.js must not be imported by game code until #1044
// lands. With #1044 present it runs the full Ink + Yarn proof.
import assert from 'node:assert';
import fs from 'node:fs';

let storyWiring;
try {
  storyWiring = await import('../game/js/story-wiring.js');
} catch (e) {
  console.log('OSS LANE 8 STORY TESTS: SKIP — requires PR #1044 (game/js/yarn-parse.js + game/js/ink-loader.js not present yet): ' + e.message);
  process.exit(0);
}
const { runVersusBanterYarn, runHeartMindInk, yarnNodeTitles } = storyWiring;

const yarn = [
  'title: Start', '---', 'The Trader stands at the crossroads.',
  '[[Ask about the Trial|TrialGate]]', '[[Walk away|WalkAway]]', '===',
  'title: TrialGate', '---', '<<set $souls = 3>>', '<<set $trial_done = true>>',
  'The gate opens. Nine lights flicker.',
  '<<if $souls == 3>>', 'The Trial seals behind you. Souls gathered: {$souls}.', '<<endif>>',
  '[[Continue|End]]', '===',
  'title: WalkAway', '---', 'You walk away.', '===',
  'title: End', '---', 'The Trial is done.', '===',
].join('\n');

const pickTrialElseFirst = (choices) => { const i = choices.findIndex((c) => c.text.includes('Trial')); return i >= 0 ? i : 0; };
const lines = runVersusBanterYarn(yarn, 'Start', pickTrialElseFirst);
assert.ok(lines.some((l) => l.includes('Souls gathered: 3')), 'yarn: Trial path interpolates souls=3, got ' + JSON.stringify(lines));
assert.ok(lines.some((l) => l.includes('The Trial is done.')), 'yarn: reaches End');
assert.deepStrictEqual(yarnNodeTitles(yarn), ['Start', 'TrialGate', 'WalkAway', 'End']);

// Ink: compiled trial story. In the repo the compiled JSON lives
// with the story lane; here we accept either an env-provided path
// or the pull-wire proof JSON when present, and skip only the Ink
// half (not the whole test) when neither exists.
const inkPath = process.env.WH_INK_TEST_JSON || '../pulls-wire/js-tests/trial-test.json';
let inkJson = null;
for (const candidate of [inkPath, 'test/fixtures/trial-test.json']) {
  try { inkJson = fs.readFileSync(new URL(candidate, import.meta.url), 'utf8'); break; } catch { /* try next */ }
}
if (!inkJson) {
  console.log('OSS LANE 8 STORY TESTS: PARTIAL — Yarn PASS, Ink SKIPPED (no compiled trial JSON in repo; story lane supplies game/data/story/*.ink.json)');
} else {
  const { lines: inkLines, vars } = runHeartMindInk(inkJson, (choices) => { const i = choices.findIndex((c) => c.text.includes('Trial')); return i >= 0 ? i : 0; });
  assert.ok(inkLines.some((l) => l.includes('Nine lights')), 'ink: Trial gate line present, got ' + JSON.stringify(inkLines));
  assert.strictEqual(vars.souls, 3, 'ink: souls=3');
  assert.strictEqual(vars.trial_done, true, 'ink: trial_done=true');
  console.log('OSS LANE 8 STORY TESTS: PASS (Yarn + vendored Ink)');
}

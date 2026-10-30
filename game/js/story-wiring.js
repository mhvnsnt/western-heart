/* ============================================================
   WESTERN HEART — Story-engine wiring (Ink + Yarn adapters)
   Builds on PR #1044 (game/js/yarn-parse.js + game/js/ink-loader.js),
   which this module imports — it does NOT re-implement either
   parser. Division locked in PR #1044's doc and kept here:
     • Ink  -> heavily branching story (Heart and Mind Within)
     • Yarn -> writer-authored dialogue (versus banter, story NPCs)
   MERGE ORDER: this file lands AFTER #1044. Until #1044 merges,
   these imports are unresolvable and this module must not be
   imported by versus-banter.js / heartmind.js — the call sites
   below are the 3-line seams for the story lane to add then.

   Ink runtime vendoring (this lane): game/vendor/inkjs/ink.mjs is
   the inkjs 2.4.0 runtime (MIT, Inkle) copied verbatim from npm,
   NOT a CDN load. createInkStory() in ink-loader.js takes the
   Story constructor as a caller-passed argument; here it is
   passed the vendored constructor, so compiled Ink JSON stories
   actually run in game with no network dependency. The BOM-strip
   gotcha (inkjs-compiler emits a UTF-8 BOM that inkjs's JSON.parse
   chokes on) is handled inside ink-loader.js's parseInkJson().

   Call sites (story lane, after #1044 merges):
     versus-banter.js: runVersusBanterYarn(text, 'Start', pick)
     heartmind.js:     runHeartMindInk(compiledJsonText, pick)
   ============================================================ */
import { parseYarn, YarnRunner } from './yarn-parse.js';
import { createInkStory, runInkStory } from './ink-loader.js';
import { Story as VendoredInkStory } from '../vendor/inkjs/ink.mjs';

export { VendoredInkStory };

// Run a Yarn dialogue file (versus banter). Returns the spoken
// lines in order; pickFn(choices) -> index selects choices.
export function runVersusBanterYarn(yarnText, startNode, pickFn) {
  const parsed = parseYarn(yarnText);
  const runner = new YarnRunner(parsed, startNode);
  return runner.run(pickFn);
}

// Run a compiled Ink JSON story (Heart and Mind Within branching
// story) with the VENDORED runtime. Returns { lines, vars }.
export function runHeartMindInk(compiledJsonText, pickFn) {
  const story = createInkStory(VendoredInkStory, compiledJsonText);
  return runInkStory(story, pickFn);
}

// Convenience: list Yarn node titles (banter editor / debug UI).
export function yarnNodeTitles(yarnText) {
  return parseYarn(yarnText).order;
}

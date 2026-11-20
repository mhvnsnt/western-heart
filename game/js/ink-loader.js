/* ============================================================
   WESTERN HEART — Ink story loader (Inkle Ink, MIT)
   Dependency-free loader for compiled Ink JSON (.ink.json) as produced
   by inkjs-compiler / the Ink compiler. The inkjs Story runtime itself
   is NOT vendored here — pass it in (see createInkStory) so the game
   keeps no CDN dependency and the loader stays testable in Node.

   GOTCHA (measured 2026-10-24, trial-test.ink -> trial-test.json):
   inkjs-compiler emits a UTF-8 BOM prefix. inkjs `new Story(json)`
   chokes on it (SyntaxError: Unexpected token '﻿'). ALWAYS strip the
   BOM on load — that is what stripBOM() is for, and it is the only
   reason this file exists alongside a stock inkjs import.

   Proven path (workspace proof, ~/workspace/pulls-wire/js-tests/):
   trial-test.ink (Trader crossroads, Trial gate, Nine Souls, souls
   variable, trial_done flag) -> inkjs-compiler -> 1,842-byte JSON
   (inkVersion 21) -> Story run: Trial gate picked, souls=3,
   trial_done=true. Same story beats as the Yarn sample in
   game/js/yarn-parse.js — the two engines are interchangeable for
   WH dialogue; Ink is the pick for Heart and Mind Within branching
   (variables + knots), Yarn for versus banter (visual authoring).
   ============================================================ */

export function stripBOM(text) {
  const s = String(text);
  return s.charCodeAt(0) === 0xfeff ? s.slice(1) : s;
}

// Parse + validate compiled Ink JSON. Throws on bad JSON, on a missing
// inkVersion, or on a missing main content block — never returns a
// half-loaded story.
export function parseInkJson(jsonText) {
  const clean = stripBOM(jsonText);
  let obj;
  try {
    obj = JSON.parse(clean);
  } catch (e) {
    throw new Error('ink-loader: compiled Ink JSON does not parse: ' + e.message);
  }
  if (typeof obj.inkVersion !== 'number') {
    throw new Error('ink-loader: missing inkVersion — not compiled Ink JSON');
  }
  if (!obj.root && !obj.mainContent) {
    throw new Error('ink-loader: no root/mainContent — empty Ink story');
  }
  return obj;
}

// Create a runnable story. StoryClass is the inkjs Story constructor
// (imported by the caller from its vendored inkjs copy). jsonText may
// carry the compiler BOM; it is stripped before the Story sees it.
export function createInkStory(StoryClass, jsonText) {
  if (typeof StoryClass !== 'function') {
    throw new Error('ink-loader: StoryClass (inkjs Story) is required');
  }
  const obj = parseInkJson(jsonText);
  // inkjs Story accepts a JSON string; pass the cleaned string, not the
  // re-serialized object, so no compiler metadata is lost in transit.
  return new StoryClass(stripBOM(jsonText));
}

// Minimal headless driver (used by tests + story tooling): step through
// a story object that exposes canContinue / Continue() / currentChoices
// / ChooseChoiceIndex() — the inkjs Story surface — picking choices via
// pickFn(choices) -> index. Returns { lines, vars } where vars is the
// story's variablesState when present.
export function runInkStory(story, pickFn) {
  const lines = [];
  let guard = 0;
  while (story.canContinue) {
    if (++guard > 10000) throw new Error('ink-loader: runaway story');
    lines.push(String(story.Continue()).trim());
    if (story.currentChoices && story.currentChoices.length > 0) {
      const idx = pickFn ? pickFn(story.currentChoices) : 0;
      story.ChooseChoiceIndex(idx);
    }
  }
  return {
    lines,
    vars: story.variablesState ? { ...story.variablesState } : {},
  };
}

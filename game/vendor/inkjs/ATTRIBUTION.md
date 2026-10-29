# inkjs — attribution & wiring

- **Upstream:** https://github.com/yousefed/inkjs (JS port of inkle/ink,
  https://github.com/inkle/ink)
- **Version vendored:** 2.4.0 (2026-10-23)
- **License:** MIT (see LICENSE.md in this dir)
- **File:** `ink.mjs` — the package's ESM runtime build, unmodified.
  Exports `Story`, `InkList`. No dependencies.

## Why
Owner directive 2026-10-23 (Track 7): visual-scripting-grade narrative
branches, event flags, dialogue prompts for the cinematic director.
ink is the industry-standard interactive-narrative language
(80 Days, Heaven's Vault); inkjs is its official JS runtime —
variables, conditional branches, choices, diverts — exactly the
branching-dialogue machinery story mode needs, with zero weight
(128 KB).

## What uses it
- `game/js/story/cinematic-director.js` — WHCinematicDirector.loadStory
  (lazy dynamic import; game runs fine if the vendor file is absent).
- `game/story/demo/demo-banter.ink` — demo story source (writer-authored).
- `game/story/demo/demo-banter.ink.json` — compiled with inkjs 2.4.0's
  compiler (ink-full.mjs, dev-time only, NOT vendored); runtime-tested
  in game/tests/story-track7.test.mjs.
- Writer tool: Inky (https://github.com/inkle/inky, MIT).

## License note (user override 2026-10-23)
License firewall is OFF per user directive — pulled regardless.
Documented for transparency: MIT, no copyleft.

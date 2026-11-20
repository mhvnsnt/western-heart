# Vendored inkjs runtime

- Package: inkjs 2.4.0 (inkle's ink scripting language,
  JavaScript port). License: MIT (see LICENSE.md in this
  directory — Copyright (c) 2017 inkle Ltd. and inkjs
  contributors).
- File: `ink.mjs` — the ESM runtime build (exports
  `Story`, `InkList`). Source: the npm `inkjs` package
  (already present in the workspace's pulls-wire test
  install, `node_modules/inkjs/dist/ink.mjs`).
- Why vendored: PR #1044's `game/js/ink-loader.js` needs a
  `Story` constructor passed in, and the game keeps no CDN
  dependency. This file is that constructor's home.
- What it is NOT: the Ink compiler. Compiled stories
  (`game/story/*.ink.json`) are produced offline with the
  inkjs compiler (inkjs-compiler) from `*.ink` sources;
  the compiler is not vendored here.
- Usage: `game/js/heartmind-campaign.js`
  `loadInkDialogue(jsonText)` dynamic-imports this file
  (`../vendor/inkjs/ink.mjs`) plus PR #1044's
  `game/js/ink-loader.js`, which strips the compiler BOM
  and validates (`inkVersion`, `root`) before constructing
  the Story. If either file is absent, the adapter returns
  null and callers keep heartmind.js's built-in beats.
